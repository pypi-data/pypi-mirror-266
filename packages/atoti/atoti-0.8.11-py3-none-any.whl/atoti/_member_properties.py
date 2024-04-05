from collections.abc import Mapping, Set as AbstractSet

from atoti_core import (
    ColumnIdentifier,
    DelegateMutableMapping,
    Identifiable,
    LevelIdentifier,
)
from typing_extensions import override

from ._java_api import JavaApi


class MemberProperties(DelegateMutableMapping[str, Identifiable[ColumnIdentifier]]):
    def __init__(
        self,
        *,
        cube_name: str,
        level_identifier: LevelIdentifier,
        java_api: JavaApi,
    ):
        self._cube_name = cube_name
        self._level_identifier = level_identifier
        self._java_api = java_api

    @override
    def _delete_keys(self, keys: AbstractSet[str], /) -> None:
        new_value = self._get_underlying()
        for key in keys:
            del new_value[key]

        self._java_api.set_member_properties(
            self._level_identifier, new_value, cube_name=self._cube_name
        )
        self._java_api.refresh()

    @override
    def _update(self, other: Mapping[str, Identifiable[ColumnIdentifier]], /) -> None:
        new_value = {**self._get_underlying(), **other}

        self._java_api.set_member_properties(
            self._level_identifier, new_value, cube_name=self._cube_name
        )
        self._java_api.refresh()

    @override
    def _get_underlying(self) -> dict[str, Identifiable[ColumnIdentifier]]:
        return self._java_api.get_member_properties(
            self._level_identifier, cube_name=self._cube_name
        )
