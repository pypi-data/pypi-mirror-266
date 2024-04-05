from __future__ import annotations

from collections.abc import Callable, Collection, Mapping
from dataclasses import field, replace
from typing import Generic, Optional, cast

from atoti_core import (
    PYDANTIC_CONFIG as _PYDANTIC_CONFIG,
    ReprJson,
    ReprJsonable,
    keyword_only_dataclass,
)
from pydantic.dataclasses import dataclass
from typing_extensions import override

from .._external_table_identifier import ExternalTableIdentifier
from ._external_table import ExternalTableT_co
from ._external_table_key import ExternalTableKey


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, repr=False)
class ExternalTables(Generic[ExternalTableT_co], ReprJsonable):
    """Tables of an external database.

    Example:
        .. doctest:: ExternalTables
            :hide:

            >>> from atoti.directquery._external_table import ExternalTable
            >>> from atoti._external_table_identifier import ExternalTableIdentifier
            >>> all_identifiers = [ExternalTableIdentifier("my_db", "my_schema", "my_table")]
            >>> key = "EXAMPLE"
            >>> tables = tt.ExternalTables._from_list(
            ...     all_identifiers,
            ...     key,
            ...     create_table_method=lambda identifier: ExternalTable(
            ...         identifier, database_key=key, types={}
            ...     ),
            ... )

        .. doctest:: ExternalTables

            >>> # Individual tables can be accessed with their name only if it is unique:
            >>> my_table = tables["my_table"]
            >>> # Or with a tuple with the schema name to differentiate the tables:
            >>> my_table = tables["my_schema", "my_table"]
            >>> # Or even a tuple starting with the database name:
            >>> my_table = tables["my_db", "my_schema", "my_table"]

    """

    _tables: Mapping[str, Mapping[str, Collection[ExternalTableIdentifier]]]
    _create_table: Callable[[ExternalTableIdentifier], ExternalTableT_co] = field(
        compare=False, hash=False
    )
    _database_key: str = field(compare=False, hash=False)

    @override
    def _repr_json_(self) -> ReprJson:
        data = {
            catalog: {
                schema: [t.table_name for t in tables]
                for schema, tables in schemas.items()
            }
            for catalog, schemas in self._tables.items()
        }
        return data, {"expanded": False, "root": self._database_key}

    def _filter(
        self,
        *,
        database_pattern: Optional[str] = None,
        schema_pattern: Optional[str] = None,
        table_pattern: Optional[str] = None,
    ) -> ExternalTables[ExternalTableT_co]:
        """Filter the tables in the database to retain only the tables matching the given patterns.

        Note that this does not affect the external database.
        It only returns a copy of the instance with the matching tables.

        Args:
            database_pattern: pattern to apply on the database name
            schema_pattern: pattern to apply on the schema name
            table_pattern: pattern to apply on the table name

        """
        selected_tables = {
            database: {
                schema: tables
                if table_pattern is None
                else [t for t in tables if t.table_name == table_pattern]
                for schema, tables in schemas.items()
                if schema_pattern is None or schema == schema_pattern
            }
            for database, schemas in self._tables.items()
            if database_pattern is None or database == database_pattern
        }
        for database, schemas in list(selected_tables.items()):
            for schema, tables in list(schemas.items()):
                if len(tables) == 0:
                    del schemas[schema]
            if len(schemas) == 0:
                del selected_tables[database]

        # See https://github.com/pydantic/pydantic/issues/7075.
        return replace(self, _tables=selected_tables)  # type: ignore[misc]

    def __getitem__(self, table_key: ExternalTableKey, /) -> ExternalTableT_co:
        identifier = self._resolve_table(table_key)
        return self._create_table(identifier)

    def _resolve_table(self, table_key: ExternalTableKey) -> ExternalTableIdentifier:
        tables = [
            t
            for schema in self._tables.values()
            for tables in schema.values()
            for t in tables
        ]

        database_name, schema_name, table_name = _fill_with_none(table_key)

        # Filter with the provided elements
        tables = [t for t in tables if t.table_name == table_name]
        if schema_name is not None:
            tables = [t for t in tables if t.schema_name == schema_name]
        if database_name is not None:
            tables = [t for t in tables if t.database_name == database_name]

        # check invalid result
        schema_message = "" if schema_name is None else f" in schema {schema_name}"
        database_message = (
            "" if database_name is None else f" in database {database_name}"
        )
        if len(tables) == 0:
            raise KeyError(
                f"No table named {table_name}{schema_message}{database_message}"
            )
        if len(tables) > 1:
            raise KeyError(
                f"Too many tables named {table_name}{schema_message}{database_message}: {tables}"
            )
        return tables[0]

    @staticmethod
    def _from_list(
        tables: list[ExternalTableIdentifier],
        database_key: str,
        *,
        create_table_method: Callable[[ExternalTableIdentifier], ExternalTableT_co],
    ) -> ExternalTables[ExternalTableT_co]:
        database_tables: dict[str, dict[str, list[ExternalTableIdentifier]]] = {}
        for table in tables:
            schema = database_tables.get(table.database_name)
            if schema is None:
                schema = {}
                database_tables[table.database_name] = schema
            table_list = schema.get(table.schema_name)
            if table_list is None:
                table_list = []
                schema[table.schema_name] = table_list
            table_list.append(table)
        return ExternalTables(
            _tables=database_tables,
            _create_table=create_table_method,
            _database_key=database_key,
        )


def _fill_with_none(
    table_key: ExternalTableKey,
) -> tuple[Optional[str], Optional[str], str]:
    if isinstance(table_key, str):
        return (None, None, table_key)
    if len(table_key) == 2:  # noqa: PLR2004
        return (None, table_key[0], table_key[1])

    # Pyright narrows the type after the previous checks but mypy does not so casting is required.
    # See https://github.com/python/mypy/issues/1178.
    return cast(tuple[str, str, str], table_key)  # pyright: ignore[reportUnnecessaryCast]
