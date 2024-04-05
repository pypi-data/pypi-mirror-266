from __future__ import annotations

from typing import Union, cast, overload

from .._column_convertible import (
    NonConstantColumnConvertible,
    is_non_constant_column_convertible,
)
from .._measure_convertible import NonConstantMeasureConvertible
from .._measure_description import MeasureDescription, convert_to_measure_description
from .._measures.calculated_measure import CalculatedMeasure, Operator
from .._operation import JavaFunctionOperation
from ._create_function_operation import create_function_operation
from ._utils import check_array_type


@overload
def sum(  # noqa: A001
    value: NonConstantColumnConvertible,
    /,
) -> JavaFunctionOperation: ...


@overload
def sum(  # noqa: A001
    value: NonConstantMeasureConvertible,
    /,
) -> MeasureDescription: ...


def sum(  # noqa: A001
    value: Union[NonConstantColumnConvertible, NonConstantMeasureConvertible],
    /,
) -> Union[JavaFunctionOperation, MeasureDescription]:
    """Return a measure equal to the sum of all the elements of the passed array measure.

    Example:
        >>> pnl_table = session.read_csv(
        ...     f"{RESOURCES}/pnl.csv",
        ...     array_separator=";",
        ...     keys=["Continent", "Country"],
        ...     table_name="PnL",
        ... )
        >>> cube = session.create_cube(pnl_table)
        >>> l, m = cube.levels, cube.measures
        >>> m["Sum"] = tt.array.sum(m["PnL.SUM"])
        >>> m["Empty sum"] = tt.array.sum(m["PnL.SUM"][0:0])
        >>> cube.query(m["PnL.SUM"], m["Sum"], m["Empty sum"])
                                  PnL.SUM      Sum Empty sum
        0  doubleVector[10]{-20.163, ...}  -308.29       .00

    """
    if is_non_constant_column_convertible(value):
        create_function_operation(value, function_key="array_sum")

    value = cast(NonConstantMeasureConvertible, value)
    check_array_type(value)
    return CalculatedMeasure(
        Operator("sum_vector", [convert_to_measure_description(value)])
    )
