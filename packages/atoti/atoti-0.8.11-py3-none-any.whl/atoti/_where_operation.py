from dataclasses import dataclass
from itertools import chain
from typing import Optional

from atoti_core import (
    Identifier,
    IdentifierT_co,
    Operand,
    OperandCondition,
    Operation,
    keyword_only_dataclass,
)
from typing_extensions import override


@keyword_only_dataclass
@dataclass(eq=False, frozen=True)
class WhereOperation(Operation[IdentifierT_co]):
    condition: OperandCondition[IdentifierT_co]
    true_value: Operand[IdentifierT_co]
    false_value: Optional[Operand[IdentifierT_co]]

    @property
    @override
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        operands = [
            self.condition,
            self.true_value,
            self.false_value,
        ]
        return frozenset(
            chain(
                *(
                    self._get_identifier_types(
                        operand,
                    )
                    for operand in operands
                )
            )
        )
