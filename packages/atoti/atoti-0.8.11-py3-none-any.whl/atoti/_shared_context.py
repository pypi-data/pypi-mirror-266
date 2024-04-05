from __future__ import annotations

from collections.abc import Mapping, Set as AbstractSet

from atoti_core import DelegateMutableMapping, ReprJson, ReprJsonable
from typing_extensions import override

from ._java_api import JavaApi


class SharedContext(DelegateMutableMapping[str, str], ReprJsonable):
    def __init__(self, *, cube_name: str, java_api: JavaApi) -> None:
        super().__init__()

        self._cube_name = cube_name
        self._java_api = java_api

    @override
    def _get_underlying(self) -> dict[str, str]:
        return self._java_api.get_shared_context_values(self._cube_name)

    @override
    def _update(self, other: Mapping[str, str], /) -> None:
        for key, value in other.items():
            self._java_api.set_shared_context_value(
                key,
                str(value),
                cube_name=self._cube_name,
            )
        self._java_api.refresh()

    @override
    def _delete_keys(self, keys: AbstractSet[str], /) -> None:
        raise NotImplementedError("Cannot delete context value.")

    @override
    def _repr_json_(self) -> ReprJson:
        return (
            dict(self),
            {"expanded": True, "root": "Context Values"},
        )
