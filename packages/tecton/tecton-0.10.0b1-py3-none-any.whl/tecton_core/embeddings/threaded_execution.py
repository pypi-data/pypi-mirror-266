from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Iterator
from typing import Sequence
from typing import Tuple
from typing import Union

import pyarrow as pa
import pyarrow.parquet

from tecton_core.embeddings import execution_utils
from tecton_core.vendor import queue


QUEUE_TIMEOUT_SECS = 5


def data_coordinator_thread_func(data_iter: pa.RecordBatchReader, output_queue: queue.ClosableQueue) -> None:
    for data in data_iter:
        output_queue.put(data)

    output_queue.close()


def iterator_over_queue(q: queue.ClosableQueue) -> Iterator:
    while True:
        try:
            yield q.get(timeout=QUEUE_TIMEOUT_SECS)
        except queue.Closed as e:
            # NOTE: we are done if our input is closed!
            break
        except queue.Empty:
            continue


@dataclass
class _ThreadContext:
    input_queue: queue.ClosableQueue
    output_queue: queue.ClosableQueue
    func: Union[execution_utils.PreprocessorCallable, execution_utils.ModelCallable]
    func_kwargs: Dict[str, Any]

    @classmethod
    def create(
        cls,
        input_queue: queue.ClosableQueue,
        output_queue: queue.ClosableQueue,
        func: Union[execution_utils.PreprocessorCallable, execution_utils.ModelCallable],
        func_config: execution_utils.FuncConfig,
    ) -> _ThreadContext:
        func_config = func_config.load()
        return _ThreadContext(
            input_queue=input_queue,
            output_queue=output_queue,
            func=func,
            func_kwargs=func_config.kwargs(),
        )


def data_preprocessor_thread_func(thread_context: _ThreadContext) -> None:
    for item in iterator_over_queue(thread_context.input_queue):
        items = execution_utils.data_preprocessor_one_step(item, thread_context.func, thread_context.func_kwargs)

        for batch in items:
            # TODO: should we loop here as well?
            thread_context.output_queue.put(batch)


def model_inference_thread_func(thread_context: _ThreadContext) -> None:
    for item in iterator_over_queue(thread_context.input_queue):
        result = execution_utils.model_inference_one_step(item, thread_context.func, thread_context.func_kwargs)
        thread_context.output_queue.put(result)


@dataclass
class MultithreadedInferenceConfig:
    num_preprocessors: int
    preprocess_info: Tuple[execution_utils.PreprocessorCallable, execution_utils.FuncConfig]
    inference_info: Tuple[execution_utils.ModelCallable, Sequence[execution_utils.FuncConfig]]


def execute_multithreaded(
    data_source: pa.RecordBatchReader, inference_config: MultithreadedInferenceConfig
) -> Iterator[pa.RecordBatch]:
    # NOTE: for now this assumes that all data fits in memory. We will re-evaluate that in the future.
    # NOTE: this artificially limits the queue size to make sure it works
    input_queue = queue.ClosableQueue(maxsize=1)  # Queue between coordinator and preprocessors
    preprocessed_queue = queue.ClosableQueue()  # Queue between preprocessors and model workers
    output_queue = queue.ClosableQueue()  # Queue between preprocessors and model workers

    inference_func, inference_func_configs = inference_config.inference_info

    # Start data coordinator
    coordinator = threading.Thread(target=data_coordinator_thread_func, args=(data_source, input_queue))
    coordinator.start()

    # Start preprocessors
    preprocessors = [
        threading.Thread(
            target=data_preprocessor_thread_func,
            args=(_ThreadContext.create(input_queue, preprocessed_queue, *inference_config.preprocess_info),),
            daemon=True,
        )
        for _ in range(inference_config.num_preprocessors)
    ]
    for preprocessor in preprocessors:
        preprocessor.start()

    # Start model workers
    model_workers = [
        threading.Thread(
            target=model_inference_thread_func,
            args=(_ThreadContext.create(preprocessed_queue, output_queue, inference_func, func_config),),
            daemon=True,
        )
        for func_config in inference_func_configs
    ]
    for worker in model_workers:
        worker.start()

    coordinator.join()
    for preprocessor in preprocessors:
        preprocessor.join()

    # We close this here since pre-processing work was done concurrently.
    preprocessed_queue.close()

    for worker in model_workers:
        worker.join()

    num_items = output_queue.qsize()

    # NOTE: this line means that we cannot work with larger than memory data.
    # We will come back to this later.
    output_batches = [output_queue.get() for _ in range(num_items)]

    for output_item in output_batches:
        if isinstance(output_item, execution_utils.ExceptionWrapper):
            output_item.reraise()

    yield from output_batches


def execute_singlethreaded(
    data_source: pa.RecordBatchReader,
    preprocess_info: Tuple[execution_utils.PreprocessorCallable, execution_utils.FuncConfig],
    inference_info: Tuple[execution_utils.ModelCallable, Sequence[execution_utils.FuncConfig]],
) -> Iterator[pa.RecordBatch]:
    preprocess_func, preprocess_config = preprocess_info
    preprocess_kwargs = preprocess_config.load().kwargs()

    inference_func, inference_config = inference_info
    if len(inference_config) > 1:
        msg = "Single threaded execution only supports one inference configuration"
        raise ValueError(msg)
    inference_kwargs = inference_config[0].load().kwargs()

    for data in data_source:
        for batch in execution_utils.data_preprocessor_one_step(data, preprocess_func, preprocess_kwargs):
            result = execution_utils.model_inference_one_step(batch, inference_func, inference_kwargs)
            if isinstance(result, execution_utils.ExceptionWrapper):
                result.reraise()

            yield result
