from __future__ import annotations

from abc import abstractmethod
from collections.abc import Collection, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from atoti_core import ColumnIdentifier, Constant, DataType, keyword_only_dataclass
from typing_extensions import override

if TYPE_CHECKING:
    from ._udaf_utils import (  # pylint: disable=nested-import
        JavaFunction,
        JavaOperationElement,
        OperationVisitor,
    )


def _get_new_columns(
    operation: Operation, column_names: Collection[ColumnIdentifier]
) -> list[ColumnIdentifier]:
    return [column for column in operation.columns if column not in column_names]


class Operation:
    """An operation between table columns."""

    @abstractmethod
    def accept(self, operation_visitor: OperationVisitor) -> JavaOperationElement:
        """Contribute this operation to the visitor."""

    @property
    @abstractmethod
    def columns(self) -> Sequence[ColumnIdentifier]:
        """Columns involved in this operation."""


class JavaFunctionOperation(Operation):
    @property
    @abstractmethod
    def underlyings(self) -> Sequence[Operation]: ...

    @property
    @abstractmethod
    def java_function(self) -> JavaFunction: ...

    @override
    def accept(self, operation_visitor: OperationVisitor) -> JavaOperationElement:
        return operation_visitor.visit_java_function_operation(self)

    @property
    @override
    def columns(self) -> Sequence[ColumnIdentifier]:
        columns: list[ColumnIdentifier] = []
        for underlying in self.underlyings:
            columns += _get_new_columns(underlying, columns)
        return columns


@dataclass(eq=False, frozen=True)
class ColumnOperation(Operation):  # pylint: disable=keyword-only-dataclass
    """Column of a table in an operation."""

    _column_identifier: ColumnIdentifier
    _column_data_type: DataType

    @override
    def accept(self, operation_visitor: OperationVisitor) -> JavaOperationElement:
        return operation_visitor.visit_column_operation(operation=self)

    @property
    @override
    def columns(self) -> Sequence[ColumnIdentifier]:
        return [self._column_identifier]


@dataclass(eq=False, frozen=True)
class ConstantOperation(Operation):  # pylint: disable=keyword-only-dataclass
    """Constant leaf of an operation."""

    _value: Constant

    @override
    def accept(self, operation_visitor: OperationVisitor) -> JavaOperationElement:
        return operation_visitor.visit_constant_operation(self)

    @property
    @override
    def columns(self) -> Sequence[ColumnIdentifier]:
        return []


@dataclass(eq=False, frozen=True)
class LeftRightOperation(JavaFunctionOperation):  # pylint: disable=keyword-only-dataclass
    """Operation with left and right member."""

    _left: Operation
    _right: Operation

    @property
    @override
    def underlyings(self) -> Sequence[Operation]:
        return [self._left, self._right]


class MultiplicationOperation(LeftRightOperation):
    """Multiplication operation."""

    @property
    @override
    def java_function(self) -> JavaFunction:
        from ._udaf_utils import MUL_FUNCTION  # pylint: disable=nested-import

        return MUL_FUNCTION


class AdditionOperation(LeftRightOperation):
    """Addition operation."""

    @property
    @override
    def java_function(self) -> JavaFunction:
        from ._udaf_utils import ADD_FUNCTION  # pylint: disable=nested-import

        return ADD_FUNCTION


class SubtractionOperation(LeftRightOperation):
    """Subtraction operation."""

    @property
    @override
    def java_function(self) -> JavaFunction:
        from ._udaf_utils import SUB_FUNCTION  # pylint: disable=nested-import

        return SUB_FUNCTION


class DivisionOperation(LeftRightOperation):
    """Division operation."""

    @property
    @override
    def java_function(self) -> JavaFunction:
        from ._udaf_utils import TRUEDIV_FUNCTION  # pylint: disable=nested-import

        return TRUEDIV_FUNCTION


@keyword_only_dataclass
@dataclass(eq=False, frozen=True)
class TernaryOperation(Operation):
    condition: Operation
    true_operation: Operation
    false_operation: Optional[Operation]

    @override
    def accept(self, operation_visitor: OperationVisitor) -> JavaOperationElement:
        return operation_visitor.visit_ternary_operation(self)

    @property
    @override
    def columns(self) -> Sequence[ColumnIdentifier]:
        columns: list[ColumnIdentifier] = []
        columns += self.condition.columns
        columns += _get_new_columns(self.true_operation, columns)
        if self.false_operation is not None:
            columns += _get_new_columns(self.false_operation, columns)
        return columns


class ConditionOperation(LeftRightOperation):
    """Operations which can be used as conditions."""


class EqualOperation(ConditionOperation):
    """== operation."""

    @property
    @override
    def java_function(self) -> JavaFunction:
        from ._udaf_utils import EQ_FUNCTION  # pylint: disable=nested-import

        return EQ_FUNCTION


class NotEqualOperation(ConditionOperation):
    """!= operation."""

    @property
    @override
    def java_function(self) -> JavaFunction:
        from ._udaf_utils import NEQ_FUNCTION  # pylint: disable=nested-import

        return NEQ_FUNCTION


class GreaterThanOperation(ConditionOperation):
    """> operation."""

    @property
    @override
    def java_function(self) -> JavaFunction:
        from ._udaf_utils import GT_FUNCTION  # pylint: disable=nested-import

        return GT_FUNCTION


class GreaterThanOrEqualOperation(ConditionOperation):
    """>= operation."""

    @property
    @override
    def java_function(self) -> JavaFunction:
        from ._udaf_utils import GTE_FUNCTION  # pylint: disable=nested-import

        return GTE_FUNCTION


class LowerThanOperation(ConditionOperation):
    """< operation."""

    @property
    @override
    def java_function(self) -> JavaFunction:
        from ._udaf_utils import LT_FUNCTION  # pylint: disable=nested-import

        return LT_FUNCTION


class LowerThanOrEqualOperation(ConditionOperation):
    """<= operation."""

    @property
    @override
    def java_function(self) -> JavaFunction:
        from ._udaf_utils import LTE_FUNCTION  # pylint: disable=nested-import

        return LTE_FUNCTION
