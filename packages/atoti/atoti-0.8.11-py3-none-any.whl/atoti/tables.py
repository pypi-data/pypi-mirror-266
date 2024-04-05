from collections.abc import Mapping, Set as AbstractSet

from atoti_core import (
    ActiveViamClient,
    ColumnDescription,
    DelegateMutableMapping,
    Plugin,
    ReprJson,
    ReprJsonable,
    TableIdentifier,
)
from typing_extensions import override

from ._database_schema import DatabaseSchema, TableDescription
from ._java_api import JavaApi
from .table import Table, _LoadKafka, _LoadSql


class Tables(DelegateMutableMapping[str, Table], ReprJsonable):
    r"""Manage the local :class:`~atoti.Table`\ s of a :class:`~atoti.Session`."""

    def __init__(
        self,
        *,
        client: ActiveViamClient,
        java_api: JavaApi,
        load_kafka: _LoadKafka,
        load_sql: _LoadSql,
        plugins: Mapping[str, Plugin],
    ):
        self._client = client
        self._java_api = java_api
        self._load_kafka = load_kafka
        self._load_sql = load_sql
        self._plugins = plugins

    @override
    def _repr_json_(self) -> ReprJson:
        return (
            dict(
                sorted(
                    {
                        table.name: table._repr_json_()[0] for table in self.values()
                    }.items()
                )
            ),
            {"expanded": False, "root": "Tables"},
        )

    @override
    def _update(
        self,
        other: Mapping[str, Table],
        /,
    ) -> None:
        raise AssertionError(
            "Use `Session.create_table()` or other methods such as `Session.read_pandas()` to create a table."
        )

    @override
    def _get_underlying(self) -> dict[str, Table]:
        return {
            table_name: self._unchecked_getitem(table_name)
            for table_name in self._java_api.get_table_names()
        }

    @override
    def __getitem__(self, key: str, /) -> Table:
        if key not in self._java_api.get_table_names():
            raise KeyError(key)
        return self._unchecked_getitem(key)

    def _unchecked_getitem(self, key: str, /) -> Table:
        return Table(
            TableIdentifier(key),
            client=self._client,
            java_api=self._java_api,
            load_kafka=self._load_kafka,
            load_sql=self._load_sql,
            plugins=self._plugins,
        )

    @override
    def _delete_keys(self, keys: AbstractSet[str], /) -> None:
        for key in keys:
            self._java_api.delete_table(TableIdentifier(key))

    @property
    def schema(self) -> object:
        """Schema of the tables represented as a `Mermaid <https://mermaid.js.org>`__ entity relationship diagram.

        Each table is represented with 3 or 4 columns:

        #. whether the column's :attr:`~atoti.Column.default_value` is ``None`` (denoted with :guilabel:`nullable`) or not
        #. the colum :attr:`~atoti.Column.data_type`
        #. (optional) whether the column is part of the table :attr:`~atoti.Table.keys` (denoted with :guilabel:`PK`) or not
        #. the column :attr:`~atoti.Column.name`

        Example:
            .. raw:: html

                <div class="mermaid">
                erDiagram
                  "Table a" {
                      _ String "foo"
                      nullable int "bar"
                  }
                  "Table b" {
                      _ int PK "bar"
                      _ LocalDate "baz"
                  }
                  "Table c" {
                      _ String PK "foo"
                      _ double PK "xyz"
                  }
                  "Table d" {
                      _ String PK "foo_d"
                      _ double PK "xyz_d"
                      nullable float "abc_d"
                  }
                  "Table a" }o--o| "Table b" : "`bar` == `bar`"
                  "Table a" }o..o{ "Table c" : "`foo` == `foo`"
                  "Table c" }o--|| "Table d" : "(`foo` == `foo_d`) & (`xyz` == `xyz_d`)"
                </div>

        """
        return DatabaseSchema(
            joins=self._java_api.get_joins(),
            tables=[
                TableDescription(
                    name=table.name,
                    columns=[
                        ColumnDescription(
                            name=column_name,
                            data_type=table[column_name].data_type,
                            nullable=table[column_name].default_value is None,
                        )
                        for column_name in table.columns
                    ],
                    keys=set(table.keys),
                )
                for table in self.values()
            ],
        )
