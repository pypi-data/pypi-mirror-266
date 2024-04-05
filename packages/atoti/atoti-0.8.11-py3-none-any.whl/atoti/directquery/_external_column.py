from __future__ import annotations

from typing import Literal, Optional, overload

from atoti_core import (
    Condition,
    Constant,
    ConstantValue,
    IsinCondition,
    OperandConvertibleWithIdentifier,
)
from typing_extensions import override

from ._external_column_identifier import ExternalColumnIdentifier


class ExternalColumn(OperandConvertibleWithIdentifier[ExternalColumnIdentifier]):
    def __init__(
        self,
        identifier: ExternalColumnIdentifier,
        /,
    ) -> None:
        super().__init__()

        self.__identifier = identifier

    @property
    def name(self) -> str:
        """The name of the column."""
        return self._identifier.column_name

    @property
    @override
    def _identifier(self) -> ExternalColumnIdentifier:
        return self.__identifier

    @property
    @override
    def _operation_operand(self) -> ExternalColumnIdentifier:
        return self._identifier

    @overload
    def isin(
        self, *elements: ConstantValue
    ) -> Condition[ExternalColumnIdentifier, Literal["isin"], Constant, None]: ...

    @overload
    def isin(
        self, *elements: Optional[ConstantValue]
    ) -> Condition[
        ExternalColumnIdentifier, Literal["isin"], Optional[Constant], None
    ]: ...

    def isin(
        self, *elements: Optional[ConstantValue]
    ) -> Condition[ExternalColumnIdentifier, Literal["isin"], Optional[Constant], None]:
        """Return a condition evaluating to ``True`` if a column element is among the given elements and ``False`` otherwise.

        ``table["City"].isin("Paris", "New York")`` is equivalent to ``(table["City"] == "Paris") | (table["City"] == "New York")``.

        Args:
            elements: One or more elements on which the column should be.
        """
        return IsinCondition(
            subject=self._operation_operand,
            elements=tuple(
                None if element is None else Constant(element) for element in elements
            ),
        )
