from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TypeVar

from atoti_core import DataType, HasIdentifier, ReprJson, ReprJsonable
from typing_extensions import override

from .._external_table_identifier import ExternalTableIdentifier
from ._external_column import ExternalColumn
from ._external_column_identifier import ExternalColumnIdentifier


class ExternalTable(HasIdentifier[ExternalTableIdentifier], ReprJsonable):
    __identifier: ExternalTableIdentifier
    _database_key: str

    types: Mapping[str, DataType]
    """Mapping from the name of each column to their type."""

    def __init__(
        self,
        identifier: ExternalTableIdentifier,
        /,
        *,
        database_key: str,
        types: Mapping[str, DataType],
    ) -> None:
        self.__identifier = identifier
        self._database_key = database_key
        self.types = types

    @override
    def _repr_json_(self) -> ReprJson:
        data = {name: str(datatype) for name, datatype in self.types.items()}
        return data, {"expanded": True, "root": self._identifier.table_name}

    @property
    def name(self) -> str:
        """Name of the table."""
        return self._identifier.table_name

    @property
    @override
    def _identifier(self) -> ExternalTableIdentifier:
        return self.__identifier

    @property
    def columns(self) -> Sequence[str]:
        """Columns of the table."""
        return list(self.types)

    def __getitem__(self, column_name: str, /) -> ExternalColumn:
        return ExternalColumn(ExternalColumnIdentifier(self._identifier, column_name))


ExternalTableT_co = TypeVar("ExternalTableT_co", bound=ExternalTable, covariant=True)
