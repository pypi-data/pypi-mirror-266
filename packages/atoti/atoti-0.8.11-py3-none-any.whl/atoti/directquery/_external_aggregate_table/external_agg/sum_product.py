from __future__ import annotations

from collections.abc import Collection

from ....column import Column
from ..._external_column import ExternalColumn
from .._external_measure import ExternalMeasure


def sum_product(
    granular_columns: Collection[Column], /, *, aggregate_column: ExternalColumn
) -> ExternalMeasure:
    return ExternalMeasure(
        aggregation_key="ATOTI_SUM_PRODUCT",
        granular_columns=[col._identifier for col in granular_columns],
        aggregate_columns=[aggregate_column._identifier],
    )
