from __future__ import annotations

from .._measure_convertible import NonConstantMeasureConvertible
from .._measure_description import MeasureDescription, convert_to_measure_description
from .._measures.calculated_measure import CalculatedMeasure, Operator
from ._utils import check_array_type


def positive_values(measure: NonConstantMeasureConvertible, /) -> MeasureDescription:
    """Return a measure where all the elements < 0 of the passed array measure are replaced by 0."""
    check_array_type(measure)
    return CalculatedMeasure(
        Operator("positive_vector", [convert_to_measure_description(measure)])
    )
