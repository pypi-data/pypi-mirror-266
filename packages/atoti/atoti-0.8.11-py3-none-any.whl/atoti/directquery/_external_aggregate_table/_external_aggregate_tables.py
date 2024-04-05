from collections.abc import Mapping, Set as AbstractSet

from atoti_core import DelegateMutableMapping
from typing_extensions import override

from ..._java_api import JavaApi
from .external_aggregate_table import ExternalAggregateTable


class ExternalAggregateTables(DelegateMutableMapping[str, ExternalAggregateTable]):
    def __init__(
        self,
        *,
        java_api: JavaApi,
    ):
        self._java_api = java_api

    @override
    def _delete_keys(self, keys: AbstractSet[str], /) -> None:
        self._java_api.remove_external_aggregate_tables(keys)
        self._java_api.refresh()

    @override
    def _update(self, other: Mapping[str, ExternalAggregateTable]) -> None:
        new_mapping: dict[str, ExternalAggregateTable] = self._get_underlying()
        new_mapping.update(other)
        self._java_api.set_external_aggregate_tables(new_mapping)
        self._java_api.refresh()

    @override
    def _get_underlying(self) -> dict[str, ExternalAggregateTable]:
        return self._java_api.get_external_aggregate_tables()
