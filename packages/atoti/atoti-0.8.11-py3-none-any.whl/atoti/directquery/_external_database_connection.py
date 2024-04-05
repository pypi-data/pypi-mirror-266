from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Generic, Literal, TypeVar

from atoti_core import DataType

from .._external_table_identifier import ExternalTableIdentifier
from .._java_api import JavaApi
from ..aggregate_provider import AggregateProvider
from ..directquery import ExternalAggregateTable, ExternalTables
from ._external_table import ExternalTable, ExternalTableT_co
from ._table_update import TableUpdate


class ExternalDatabaseConnection(Generic[ExternalTableT_co], ABC):
    def __init__(self, *, database_key: str, java_api: JavaApi) -> None:
        super().__init__()

        self._database_key = database_key
        self._java_api = java_api

    @property
    def tables(self) -> ExternalTables[ExternalTableT_co]:
        """Tables of the external database."""
        table_descriptions = self._java_api.get_external_tables(self._database_key)
        return ExternalTables(
            _tables=table_descriptions,
            _create_table=lambda identifier: self._discover_and_create_table(
                identifier
            ),
            _database_key=self._database_key,
        )

    def _derive_aggregate_table(
        self,
        provider: AggregateProvider,
        /,
        table_identifier: ExternalTableIdentifier,
        *,
        cube_name: str,
    ) -> ExternalAggregateTable:
        """Return the description of an external aggregate table that can be used to feed the passed aggregate provider.

        Args:
            provider: The description of the provider to convert.
                For best performance, this provider should be added to the cube after adding the returned aggregate table to the session.
            table_identifier: The identifier of the external table that will be used as the aggregate table.
            cube_name: The name of the cube which will contain the provider.
        """
        return self._java_api.derive_external_aggregate_table(
            provider,
            cube_name=cube_name,
            key=self._database_key,
            table_identifier=table_identifier,
        )

    def _generate_sql(
        self,
        aggregate_table: ExternalAggregateTable,
        /,
        *,
        mode: Literal["create", "insert"],
    ) -> str:
        """Generates an SQL query to interact with the passed aggregate table.

        Args:
            aggregate_table: The aggregate table to interact with.
            mode: The type of SQL query to generate.
        """
        queries = self._java_api.generate_external_aggregate_table_sql(
            aggregate_table, key=self._database_key
        )
        if mode == "create":
            return queries.create
        assert mode == "insert"
        return queries.insert

    @abstractmethod
    def _create_table(
        self,
        identifier: ExternalTableIdentifier,
        /,
        *,
        types: Mapping[str, DataType],
    ) -> ExternalTableT_co: ...

    def _discover_and_create_table(
        self,
        identifier: ExternalTableIdentifier,
    ) -> ExternalTableT_co:
        columns = self._java_api.get_external_table_schema(
            self._database_key, identifier=identifier
        )
        return self._create_table(identifier, types=columns)

    def _refresh(self, *updates: TableUpdate) -> None:
        self._java_api.incremental_refresh(*updates)


ExternalDatabaseConnectionT = TypeVar(
    "ExternalDatabaseConnectionT",
    bound=ExternalDatabaseConnection[ExternalTable],
)
