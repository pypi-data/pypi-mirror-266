from __future__ import annotations

from ....column import Column
from ..._external_column import ExternalColumn
from .._external_measure import ExternalMeasure


def mean(
    granular_column: Column,
    /,
    *,
    sum_aggregate_column: ExternalColumn,
    count_aggregate_column: ExternalColumn,
) -> ExternalMeasure:
    return ExternalMeasure(
        aggregation_key="AVG",
        granular_columns=[granular_column._identifier],
        aggregate_columns=[
            sum_aggregate_column._identifier,
            count_aggregate_column._identifier,
        ],
    )
