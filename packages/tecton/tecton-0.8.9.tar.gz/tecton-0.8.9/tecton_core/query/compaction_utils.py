import datetime
from collections import defaultdict
from typing import Optional
from typing import Tuple

import attrs
import pendulum

from tecton_core import feature_definition_wrapper
from tecton_core import schema
from tecton_core.specs import LifetimeWindowSpec
from tecton_core.specs import TimeWindowSpec
from tecton_core.specs import create_time_window_spec_from_data_proto
from tecton_proto.data import feature_view_pb2 as feature_view__data_pb2


@attrs.frozen
class AggregationGroup:
    """AggregationGroup represents a group of aggregate features to compute with a corresponding start/end.

    The typical usage of this will be in compaction jobs, where we will use the start/end time to determine
    eligible rows for each individual aggregate.
    """

    window_index: int
    inclusive_start_time: Optional[datetime.datetime]
    exclusive_end_time: datetime.datetime
    aggregate_features: Tuple[feature_view__data_pb2.AggregateFeature, ...]
    schema: schema.Schema


def _get_inclusive_start_time_for_window(
    exclusive_end_time: datetime.datetime, window: TimeWindowSpec
) -> Optional[datetime.datetime]:
    if isinstance(window, LifetimeWindowSpec):
        return None
    return exclusive_end_time + window.window_start


def _get_exclusive_end_time_for_window(
    exclusive_end_time: datetime.datetime, window: TimeWindowSpec
) -> datetime.datetime:
    if isinstance(window, LifetimeWindowSpec):
        return exclusive_end_time
    return exclusive_end_time + window.window_end


def aggregation_groups(
    fdw: feature_definition_wrapper.FeatureDefinitionWrapper, exclusive_end_time: datetime.datetime
) -> Tuple[AggregationGroup, ...]:
    aggregation_map = defaultdict(list)
    for aggregation in fdw.trailing_time_window_aggregation.features:
        aggregation_map[create_time_window_spec_from_data_proto(aggregation.time_window)].append(aggregation)

    agg_groups = fdw.fv_spec.online_batch_table_format.online_batch_table_parts

    if len(agg_groups) != len(aggregation_map):
        msg = "unexpected difference in length of the spec's online_batch_table_format and trailing_time_window_aggregation"
        raise ValueError(msg)

    return tuple(
        AggregationGroup(
            window_index=group.window_index,
            inclusive_start_time=_get_inclusive_start_time_for_window(exclusive_end_time, group.time_window),
            exclusive_end_time=_get_exclusive_end_time_for_window(exclusive_end_time, group.time_window),
            aggregate_features=tuple(aggregation_map[group.time_window]),
            schema=group.schema,
        )
        for group in agg_groups
    )


def _get_largest_agg_window_time_limits(
    fdw: feature_definition_wrapper.FeatureDefinitionWrapper,
    compaction_job_end_time: datetime.datetime,
) -> Optional[pendulum.Period]:
    agg_groups = aggregation_groups(fdw=fdw, exclusive_end_time=compaction_job_end_time)

    window_start_times = []
    for group in agg_groups:
        if group.inclusive_start_time is None:
            return None
        window_start_times.append(group.inclusive_start_time)

    start_time = min(window_start_times)
    end_time = max(agg_groups, key=lambda x: x.exclusive_end_time).exclusive_end_time
    return pendulum.Period(pendulum.instance(start_time), pendulum.instance(end_time))


def get_data_time_limits_for_compaction(
    fdw: feature_definition_wrapper.FeatureDefinitionWrapper, compaction_job_end_time: datetime.datetime
) -> Optional[pendulum.Period]:
    """Compute the time filter to be used for online compaction jobs.

    This determines how much data to read from the offline store.
    For aggregate fvs,
        start_time=earliest agg window
        end_time=latest agg window end
    For non agg fvs,
        start_time=max(feature start time, compaction_job_end_time - ttl)
        end_time=compaction_job_end_time"""

    if fdw.materialization_start_timestamp is None:
        return None
    default_time_limits = pendulum.Period(
        fdw.materialization_start_timestamp, pendulum.instance(compaction_job_end_time)
    )

    if fdw.is_temporal_aggregate:
        largest_agg_window_period = _get_largest_agg_window_time_limits(
            fdw=fdw, compaction_job_end_time=compaction_job_end_time
        )
        if largest_agg_window_period is None:
            return default_time_limits
        return largest_agg_window_period

    if fdw.is_temporal:
        compaction_job_end_time = pendulum.instance(compaction_job_end_time)
        if fdw.serving_ttl is not None and fdw.feature_start_timestamp is not None:
            job_time_minus_ttl = compaction_job_end_time - fdw.serving_ttl
            start_time = max(fdw.feature_start_timestamp, job_time_minus_ttl)
        elif fdw.serving_ttl is not None:
            start_time = compaction_job_end_time - fdw.serving_ttl
        elif fdw.feature_start_timestamp is not None:
            start_time = fdw.feature_start_timestamp
        else:
            return default_time_limits

        return pendulum.Period(start_time, compaction_job_end_time)

    return default_time_limits
