from collections.abc import Set as AbstractSet
from typing import Union

from atoti_core import HierarchyKey
from atoti_query import QueryHierarchy
from py4j.protocol import Py4JError
from typing_extensions import override

from ..._java_api import JavaApi
from ..._local_hierarchies import CreateHierarchyFromArguments, LocalHierarchies
from ...column import Column
from ...level import Level

LevelOrColumn = Union[Level, Column]


class DistributedHierarchies(
    LocalHierarchies[QueryHierarchy],
):
    def __init__(
        self,
        *,
        create_hierarchy_from_arguments: CreateHierarchyFromArguments[QueryHierarchy],
        cube_name: str,
        java_api: JavaApi,
    ) -> None:
        super().__init__(
            create_hierarchy_from_arguments=create_hierarchy_from_arguments,
            java_api=java_api,
        )

        self._cube_name = cube_name

    @override
    def _get_underlying(self) -> dict[HierarchyKey, QueryHierarchy]:
        hierarchies = {
            identifier: self._create_hierarchy_from_arguments(description)
            for identifier, description in self._java_api.get_hierarchies(
                self._cube_name
            ).items()
        }
        return {  # pyright: ignore[reportReturnType]
            hierarchy_identifier: hierarchies[hierarchy_identifier]  # type: ignore[misc]
            for hierarchy_identifier in hierarchies
        }

    @override
    def __getitem__(self, key: HierarchyKey, /) -> QueryHierarchy:
        (dimension_name, hierarchy_name) = self._convert_key(key)
        try:
            hierarchy_argument = self._java_api.get_hierarchy(
                hierarchy_name,
                cube_name=self._cube_name,
                dimension_name=dimension_name,
            )
        except Py4JError as error:
            raise KeyError(str(error)) from None
        return self._create_hierarchy_from_arguments(hierarchy_argument)

    @override
    def _delete_keys(
        self,
        keys: AbstractSet[HierarchyKey],
        /,
    ) -> None:
        raise RuntimeError("Distributed cube hierarchies cannot be changed.")
