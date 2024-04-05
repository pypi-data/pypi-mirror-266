from __future__ import annotations

from collections.abc import Callable, Collection
from typing import Optional

from atoti_core import ActiveViamClient, DataType, IdentifierT_co, LevelIdentifier
from atoti_query import QueryHierarchy, QueryLevel, QuerySession
from typing_extensions import override

from ..._hierarchy_arguments import HierarchyArguments
from ..._java_api import JavaApi
from ..._local_cube import LocalCube
from ...aggregates_cache import AggregatesCache
from .hierarchies import DistributedHierarchies
from .levels import DistributedLevels
from .measures import DistributedMeasures


class DistributedCube(
    LocalCube[DistributedHierarchies, DistributedLevels, DistributedMeasures]
):
    """Cube of a distributed session."""

    def __init__(
        self,
        name: str,
        /,
        *,
        client: ActiveViamClient,
        create_query_session: Callable[[], QuerySession],
        java_api: JavaApi,
        session_name: Optional[str],
    ):
        super().__init__(
            name,
            client=client,
            aggregates_cache=AggregatesCache(
                cube_name=name,
                get_capacity=java_api.get_aggregates_cache_capacity,
                set_capacity=java_api.set_aggregates_cache_capacity,
            ),
            create_query_session=create_query_session,
            hierarchies=DistributedHierarchies(
                create_hierarchy_from_arguments=self._create_hierarchy_from_arguments,
                cube_name=name,
                java_api=java_api,
            ),
            java_api=java_api,
            level_function=lambda hierarchies: DistributedLevels(
                hierarchies=hierarchies
            ),
            measures=DistributedMeasures(cube_name=name, java_api=java_api),
            session_name=session_name,
        )

    @override
    def _get_data_types(
        self, identifiers: Collection[IdentifierT_co], /
    ) -> dict[IdentifierT_co, DataType]:
        return {identifier: "Object" for identifier in identifiers}

    @override
    def _create_hierarchy_from_arguments(
        self, arguments: HierarchyArguments
    ) -> QueryHierarchy:
        return QueryHierarchy(
            arguments.identifier,
            levels={
                level_name: QueryLevel(
                    LevelIdentifier(arguments.identifier, level_name)
                )
                for level_name in arguments.levels_arguments
                if level_name != "ALL"
            },
            slicing=arguments.slicing,
        )
