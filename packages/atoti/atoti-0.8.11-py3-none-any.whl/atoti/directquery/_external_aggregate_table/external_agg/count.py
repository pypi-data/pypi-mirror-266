from __future__ import annotations

from ..._external_column import ExternalColumn
from .._external_measure import ExternalMeasure


def count(*, aggregate_column: ExternalColumn) -> ExternalMeasure:
    return ExternalMeasure(
        aggregation_key="COUNT",
        granular_columns=[],
        aggregate_columns=[aggregate_column._identifier],
    )
