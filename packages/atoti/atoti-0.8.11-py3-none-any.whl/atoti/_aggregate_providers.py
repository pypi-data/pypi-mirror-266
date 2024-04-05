from collections.abc import Mapping, Set as AbstractSet

from atoti_core import DelegateMutableMapping
from typing_extensions import override

from ._java_api import JavaApi
from .aggregate_provider import AggregateProvider


class AggregateProviders(DelegateMutableMapping[str, AggregateProvider]):
    def __init__(
        self,
        *,
        cube_name: str,
        java_api: JavaApi,
    ):
        self._cube_name = cube_name
        self._java_api = java_api

    @override
    def _delete_keys(self, keys: AbstractSet[str], /) -> None:
        self._java_api.remove_aggregate_providers(keys, cube_name=self._cube_name)
        self._java_api.refresh()

    @override
    def _update(self, other: Mapping[str, AggregateProvider], /) -> None:
        self._java_api.add_aggregate_providers(other, cube_name=self._cube_name)
        self._java_api.refresh()

    @override
    def _get_underlying(self) -> dict[str, AggregateProvider]:
        return self._java_api.get_aggregate_providers_attributes(self._cube_name)
