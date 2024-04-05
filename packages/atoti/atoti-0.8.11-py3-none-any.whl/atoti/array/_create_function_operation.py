from __future__ import annotations

from typing import Optional

from atoti_core import convert_to_operand

from .._column_convertible import ColumnConvertible, ColumnOperation
from .._function_operation import FunctionOperation


def create_function_operation(
    *operands: Optional[ColumnConvertible], function_key: str
) -> ColumnOperation:
    return FunctionOperation(
        function_key=function_key,
        operands=tuple(convert_to_operand(operand) for operand in operands),
    )
