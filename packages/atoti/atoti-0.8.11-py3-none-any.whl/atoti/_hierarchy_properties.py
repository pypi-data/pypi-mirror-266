from collections.abc import Collection, Mapping

from atoti_core import DelegateMutableMapping, HierarchyIdentifier
from pydantic import JsonValue
from typing_extensions import override

from ._java_api import JavaApi


class HierarchyProperties(DelegateMutableMapping[str, JsonValue]):
    def __init__(
        self,
        *,
        cube_name: str,
        hierarchy_identifier: HierarchyIdentifier,
        java_api: JavaApi,
    ):
        self._cube_name = cube_name
        self._hierarchy_identifier = hierarchy_identifier
        self._java_api = java_api

    @override
    def _delete_keys(self, keys: Collection[str], /) -> None:
        new_value = self._get_underlying()
        for key in keys or list(new_value):
            del new_value[key]

        self._java_api.set_hierarchy_properties(
            self._hierarchy_identifier, new_value, cube_name=self._cube_name
        )
        self._java_api.refresh()

    @override
    def _update(self, other: Mapping[str, JsonValue], /) -> None:
        new_value = {**self._get_underlying(), **other}

        self._java_api.set_hierarchy_properties(
            self._hierarchy_identifier, new_value, cube_name=self._cube_name
        )
        self._java_api.refresh()

    @override
    def _get_underlying(self) -> dict[str, JsonValue]:
        return self._java_api.get_hierarchy_properties(
            self._hierarchy_identifier, cube_name=self._cube_name
        )
