from dataclasses import dataclass
from itertools import chain
from typing import Optional

from atoti_core import (
    Identifier,
    IdentifierT_co,
    Operand,
    Operation,
    keyword_only_dataclass,
)
from typing_extensions import override


@keyword_only_dataclass
@dataclass(eq=False, frozen=True)
class FunctionOperation(Operation[IdentifierT_co]):
    function_key: str
    operands: tuple[Optional[Operand[IdentifierT_co]], ...] = ()

    @property
    @override
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        return frozenset(
            chain(*(self._get_identifier_types(operand) for operand in self.operands))
        )
