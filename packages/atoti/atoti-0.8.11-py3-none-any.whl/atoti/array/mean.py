from __future__ import annotations

from typing import Union, cast, overload

from .._column_convertible import (
    ColumnOperation,
    NonConstantColumnConvertible,
    is_non_constant_column_convertible,
)
from .._measure_convertible import NonConstantMeasureConvertible
from .._measure_description import MeasureDescription, convert_to_measure_description
from .._measures.calculated_measure import CalculatedMeasure, Operator
from ._create_function_operation import create_function_operation
from ._utils import check_array_type


@overload
def mean(value: NonConstantColumnConvertible, /) -> ColumnOperation: ...


@overload
def mean(value: NonConstantMeasureConvertible, /) -> MeasureDescription: ...


def mean(
    value: Union[NonConstantColumnConvertible, NonConstantMeasureConvertible], /
) -> Union[ColumnOperation, MeasureDescription]:
    """Return a measure equal to the mean of all the elements of the passed array measure.

    Example:
        >>> pnl_table = session.read_csv(
        ...     f"{RESOURCES}/pnl.csv",
        ...     array_separator=";",
        ...     keys=["Continent", "Country"],
        ...     table_name="PnL",
        ... )
        >>> cube = session.create_cube(pnl_table)
        >>> l, m = cube.levels, cube.measures
        >>> m["Mean"] = tt.array.mean(m["PnL.SUM"])
        >>> m["Empty mean"] = tt.array.mean(m["PnL.SUM"][0:0])
        >>> cube.query(m["PnL.SUM"], m["Mean"], m["Empty mean"])
                                  PnL.SUM    Mean Empty mean
        0  doubleVector[10]{-20.163, ...}  -30.83        .00

    """
    if is_non_constant_column_convertible(value):
        create_function_operation(value, function_key="array_mean")

    value = cast(NonConstantMeasureConvertible, value)
    check_array_type(value)
    return CalculatedMeasure(
        Operator("mean_vector", [convert_to_measure_description(value)])
    )
