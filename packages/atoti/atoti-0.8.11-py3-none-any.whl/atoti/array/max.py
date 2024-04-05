from __future__ import annotations

from .._measure_convertible import NonConstantMeasureConvertible
from .._measure_description import MeasureDescription, convert_to_measure_description
from .._measures.calculated_measure import CalculatedMeasure, Operator
from ._utils import check_array_type


def max(  # noqa: A001
    measure: NonConstantMeasureConvertible,
    /,
) -> MeasureDescription:
    """Return a measure equal to the maximum element of the passed array measure.

    Example:
        >>> pnl_table = session.read_csv(
        ...     f"{RESOURCES}/pnl.csv",
        ...     array_separator=";",
        ...     keys=["Continent", "Country"],
        ...     table_name="PnL",
        ... )
        >>> cube = session.create_cube(pnl_table)
        >>> l, m = cube.levels, cube.measures
        >>> m["Max"] = tt.array.max(m["PnL.SUM"])
        >>> m["Empty max"] = tt.array.max(m["PnL.SUM"][0:0])
        >>> cube.query(m["PnL.SUM"], m["Max"], m["Empty max"])
                                  PnL.SUM   Max Empty max
        0  doubleVector[10]{-20.163, ...}  9.26

    """
    check_array_type(measure)
    return CalculatedMeasure(
        Operator("max_vector", [convert_to_measure_description(measure)])
    )
