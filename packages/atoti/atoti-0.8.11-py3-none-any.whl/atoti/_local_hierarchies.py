from collections.abc import Mapping
from typing import Protocol, TypeVar, Union

from atoti_core import (
    BaseHierarchies,
    BaseHierarchyBound,
    DelegateMutableMapping,
    HierarchyKey,
)
from typing_extensions import override

from ._hierarchy_arguments import HierarchyArguments
from ._java_api import JavaApi
from .column import Column
from .level import Level

LevelOrColumn = Union[Level, Column]

_HierarchyT_co = TypeVar("_HierarchyT_co", bound=BaseHierarchyBound, covariant=True)


class CreateHierarchyFromArguments(Protocol[_HierarchyT_co]):
    def __call__(self, arguments: HierarchyArguments, /) -> _HierarchyT_co: ...


class LocalHierarchies(  # type: ignore[type-var]
    DelegateMutableMapping[
        HierarchyKey,
        _HierarchyT_co,  # pyright: ignore[reportInvalidTypeArguments]
    ],
    BaseHierarchies[_HierarchyT_co],
):
    def __init__(
        self,
        *,
        create_hierarchy_from_arguments: CreateHierarchyFromArguments[_HierarchyT_co],
        java_api: JavaApi,
    ) -> None:
        super().__init__()

        self._create_hierarchy_from_arguments = create_hierarchy_from_arguments
        self._java_api = java_api

    @override
    def _update(
        self,
        other: Mapping[HierarchyKey, _HierarchyT_co],
        /,
    ) -> None:
        raise RuntimeError(f"{self._get_name()} cube hierarchies cannot be changed.")

    def _get_name(self) -> str:
        return self.__class__.__name__.replace("Hierarchies", "")
