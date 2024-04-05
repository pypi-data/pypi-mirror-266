from __future__ import annotations

from collections.abc import Collection

from ....column import Column
from ..._external_column import ExternalColumn
from .._external_measure import ExternalMeasure


def agg(
    *,
    key: str,
    granular_columns: Collection[Column],
    aggregate_columns: Collection[ExternalColumn],
) -> ExternalMeasure:
    return ExternalMeasure(
        aggregation_key=key,
        granular_columns=[col._identifier for col in granular_columns],
        aggregate_columns=[col._identifier for col in aggregate_columns],
    )
