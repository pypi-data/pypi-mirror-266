import contextlib
import logging
import threading
import typing
from datetime import datetime
from functools import partial
from typing import Optional

from tecton_core.query.errors import UserDefinedTransformationError
from tecton_materialization.common.job_metadata import update_job_exec
from tecton_proto.materialization.job_metadata_pb2 import JobMetadata
from tecton_proto.materialization.job_metadata_pb2 import TectonManagedStage
from tecton_proto.materialization.params_pb2 import MaterializationTaskParams


logger = logging.getLogger(__name__)


def create_stage(
    stage_type: TectonManagedStage.StageType, description: str, task_params: MaterializationTaskParams
) -> int:
    """
    Returns created stage index
    """

    def _update(job_metadata: JobMetadata) -> JobMetadata:
        new_proto = JobMetadata()
        new_proto.CopyFrom(job_metadata)

        new_stage = TectonManagedStage(
            description=description,
            stage_type=stage_type,
            state=TectonManagedStage.State.PENDING,
        )
        new_proto.tecton_managed_info.stages.append(new_stage)
        return new_proto

    return len(update_job_exec(task_params, _update).tecton_managed_info.stages) - 1


def set_query(stage_idx, sql: str, task_params: MaterializationTaskParams):
    def _update(job_metadata: JobMetadata) -> JobMetadata:
        new_proto = JobMetadata()
        new_proto.CopyFrom(job_metadata)

        stage = new_proto.tecton_managed_info.stages[stage_idx]
        if not stage.compiled_sql_query:
            stage.compiled_sql_query = sql

        return new_proto

    update_job_exec(task_params, _update)


def set_running(stage_idx: int, task_params: MaterializationTaskParams):
    def _update(job_metadata: JobMetadata) -> JobMetadata:
        new_proto = JobMetadata()
        new_proto.CopyFrom(job_metadata)

        stage = new_proto.tecton_managed_info.stages[stage_idx]
        stage.state = TectonManagedStage.State.RUNNING
        stage.start_time.GetCurrentTime()

        return new_proto

    update_job_exec(task_params, _update)


def update_progress(stage_idx: int, progress: float, task_params: MaterializationTaskParams):
    def _update(job_metadata: JobMetadata) -> JobMetadata:
        new_proto = JobMetadata()
        new_proto.CopyFrom(job_metadata)

        stage = new_proto.tecton_managed_info.stages[stage_idx]
        stage.progress = progress
        stage.duration.FromSeconds(int((datetime.now() - stage.start_time.ToDatetime()).total_seconds()))

        return new_proto

    update_job_exec(task_params, _update)


def set_completed(stage_idx: int, task_params: MaterializationTaskParams):
    def _update(job_metadata: JobMetadata) -> JobMetadata:
        new_proto = JobMetadata()
        new_proto.CopyFrom(job_metadata)

        stage = new_proto.tecton_managed_info.stages[stage_idx]
        stage.state = TectonManagedStage.State.SUCCESS

        return new_proto

    update_job_exec(task_params, _update)


def set_failed(
    stage_idx: int, error_type: TectonManagedStage.ErrorType, error_detail: str, task_params: MaterializationTaskParams
):
    def _update(job_metadata: JobMetadata) -> JobMetadata:
        new_proto = JobMetadata()
        new_proto.CopyFrom(job_metadata)

        stage = new_proto.tecton_managed_info.stages[stage_idx]
        stage.error_type = error_type
        stage.error_detail = error_detail
        stage.state = TectonManagedStage.State.ERROR

        return new_proto

    update_job_exec(task_params, _update)


def set_current_stage_failed(
    error_type: TectonManagedStage.ErrorType, error_detail: str, task_params: MaterializationTaskParams
):
    def _update(job_metadata: JobMetadata) -> JobMetadata:
        new_proto = JobMetadata()
        new_proto.CopyFrom(job_metadata)

        current_stage = None
        for stage in new_proto.tecton_managed_info.stages:
            if stage.state == TectonManagedStage.State.ERROR:
                return new_proto

            # Select first RUNNING or PENDING stage
            # Or if all stages are complete - just the last one
            current_stage = stage
            if stage.state in (TectonManagedStage.State.RUNNING, TectonManagedStage.State.PENDING):
                break

        if not current_stage:
            # if there are no stages - we will create a dummy one
            current_stage = TectonManagedStage(
                description="Setting up materialization job",
                state=TectonManagedStage.State.ERROR,
            )
            new_proto.tecton_managed_info.stages.append(current_stage)

        current_stage.error_type = error_type
        current_stage.error_detail = error_detail
        current_stage.state = TectonManagedStage.State.ERROR

        return new_proto

    update_job_exec(task_params, _update)


ProgressLogger = typing.Callable[[float], None]
SQLParam = typing.Optional[str]
MonitoringContextProvider = typing.Callable[[SQLParam], typing.ContextManager[ProgressLogger]]

UserErrors = (UserDefinedTransformationError,)


_monitor_state = threading.local()


def dummy_progress_logger(p: float):
    pass


def create_stage_monitor(
    stage_type: TectonManagedStage.StageType, description: str, materialization_task_params: MaterializationTaskParams
) -> MonitoringContextProvider:
    stage_idx = create_stage(stage_type, description, materialization_task_params)

    @contextlib.contextmanager
    def monitor(sql: Optional[str] = None):
        if sql:
            set_query(stage_idx, sql, materialization_task_params)

        if hasattr(_monitor_state, "active_ctx") and _monitor_state.active_ctx:
            # we're already inside monitoring ctx
            yield dummy_progress_logger
            return

        set_running(stage_idx, materialization_task_params)

        progress_logger = partial(update_progress, stage_idx, task_params=materialization_task_params)

        _monitor_state.active_ctx = stage_idx
        try:
            yield progress_logger
        except UserErrors as err:
            set_failed(stage_idx, TectonManagedStage.ErrorType.USER_ERROR, err.args[0], materialization_task_params)
            raise
        except Exception as err:
            set_failed(
                stage_idx, TectonManagedStage.ErrorType.UNEXPECTED_ERROR, err.args[0], materialization_task_params
            )
            raise
        else:
            set_completed(stage_idx, materialization_task_params)
        finally:
            _monitor_state.active_ctx = None

    return monitor
