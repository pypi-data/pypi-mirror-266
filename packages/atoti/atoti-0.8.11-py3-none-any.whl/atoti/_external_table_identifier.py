from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, Identifier
from pydantic.dataclasses import dataclass
from typing_extensions import override


@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class ExternalTableIdentifier(Identifier):  # pylint: disable=keyword-only-dataclass
    database_name: str
    schema_name: str
    table_name: str

    @override
    def __repr__(self) -> str:
        return f"""t[{self.database_name, self.schema_name, self.table_name}]"""
