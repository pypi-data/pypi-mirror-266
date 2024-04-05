from __future__ import annotations

from ....column import Column
from ..._external_column import ExternalColumn
from .._external_measure import ExternalMeasure


def min(  # noqa: A001
    granular_column: Column, /, *, aggregate_column: ExternalColumn
) -> ExternalMeasure:
    return ExternalMeasure(
        aggregation_key="MIN",
        granular_columns=[granular_column._identifier],
        aggregate_columns=[aggregate_column._identifier],
    )
