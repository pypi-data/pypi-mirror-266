from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable, Collection
from typing import Any, Literal, Optional, TypeVar

import pandas as pd
from atoti_core import (
    BASE_SCENARIO_NAME,
    DEFAULT_QUERY_TIMEOUT,
    QUERY_DOC,
    ActiveViamClient,
    BaseCube,
    BaseHierarchyBound,
    BaseLevel,
    BaseMeasure,
    Context,
    DataType,
    Duration,
    IdentifierT_co,
    LevelsT_co,
    QueryFilter,
    SequenceOrDeprecatedSet,
    doc,
    frozendict,
    get_query_args_doc,
)
from atoti_query import QuerySession
from atoti_query._internal import generate_mdx, stringify_mdx
from typing_extensions import override

from ._docs_utils import EXPLAIN_QUERY_DOC
from ._hierarchy_arguments import HierarchyArguments
from ._java_api import JavaApi
from ._local_hierarchies import LocalHierarchies
from ._local_measures import LocalMeasures
from ._query_plan import QueryAnalysis
from .aggregates_cache import AggregatesCache

_LocalMeasures = TypeVar("_LocalMeasures", bound=LocalMeasures[Any])
_LocalHierarchies = TypeVar("_LocalHierarchies", bound=LocalHierarchies[Any])


class LocalCube(BaseCube[_LocalHierarchies, LevelsT_co, _LocalMeasures]):
    """Local cube class."""

    def __init__(
        self,
        name: str,
        /,
        *,
        aggregates_cache: AggregatesCache,
        client: ActiveViamClient,
        create_query_session: Callable[[], QuerySession],
        hierarchies: _LocalHierarchies,
        java_api: JavaApi,
        level_function: Callable[[_LocalHierarchies], LevelsT_co],
        measures: _LocalMeasures,
        session_name: Optional[str],
    ):
        super().__init__(name, hierarchies=hierarchies, measures=measures)

        self._aggregates_cache = aggregates_cache
        self._client = client
        self._create_query_session = create_query_session
        self._java_api = java_api
        self._levels: LevelsT_co = level_function(self._hierarchies)
        self._session_name = session_name

    @property
    @override
    def name(self) -> str:
        """Name of the cube."""
        return self._name

    @property
    @override
    def hierarchies(self) -> _LocalHierarchies:
        """Hierarchies of the cube."""
        return self._hierarchies

    @property
    @override
    def levels(self) -> LevelsT_co:
        """Levels of the cube."""
        return self._levels

    @property
    @override
    def measures(self) -> _LocalMeasures:
        """Measures of the cube."""
        return self._measures

    @property
    def aggregates_cache(self) -> AggregatesCache:
        """Aggregates cache of the cube."""
        return self._aggregates_cache

    @abstractmethod
    def _get_data_types(
        self, identifiers: Collection[IdentifierT_co], /
    ) -> dict[IdentifierT_co, DataType]: ...

    @doc(QUERY_DOC, args=get_query_args_doc(is_query_session=False))
    @override
    def query(
        self,
        *measures: BaseMeasure,
        context: Context = frozendict(),
        filter: Optional[QueryFilter] = None,  # noqa: A002
        include_empty_rows: bool = False,
        include_totals: bool = False,
        levels: SequenceOrDeprecatedSet[BaseLevel] = (),
        mode: Literal["pretty", "raw"] = "pretty",
        scenario: str = BASE_SCENARIO_NAME,
        timeout: Duration = DEFAULT_QUERY_TIMEOUT,
        **kwargs: Any,
    ) -> pd.DataFrame:
        query_session = self._create_query_session()

        def get_data_types(
            identifiers: Collection[IdentifierT_co], /, *, cube_name: str
        ) -> dict[IdentifierT_co, DataType]:
            assert cube_name == self.name
            return self._get_data_types(identifiers)

        return query_session.cubes[self.name].query(
            *measures,
            context=context,
            filter=filter,
            get_data_types=get_data_types,
            include_empty_rows=include_empty_rows,
            include_totals=include_totals,
            levels=levels,
            mode=mode,
            scenario=scenario,
            timeout=timeout,
            **kwargs,
        )

    @doc(EXPLAIN_QUERY_DOC, corresponding_method="query")
    def explain_query(
        self,
        *measures: BaseMeasure,
        filter: Optional[QueryFilter] = None,  # noqa: A002
        include_empty_rows: bool = False,
        include_totals: bool = False,
        levels: SequenceOrDeprecatedSet[BaseLevel] = (),
        scenario: str = BASE_SCENARIO_NAME,
        timeout: Duration = DEFAULT_QUERY_TIMEOUT,
    ) -> QueryAnalysis:
        query_session = self._create_query_session()
        cube = query_session._cube_discovery.get_cube(self.name)

        mdx_ast = generate_mdx(
            cube=cube,
            filter=filter,
            include_empty_rows=include_empty_rows,
            include_totals=include_totals,
            level_identifiers=[level._identifier for level in levels],
            measure_identifiers=[measure._identifier for measure in measures],
            scenario=scenario,
        )
        mdx = stringify_mdx(mdx_ast)
        return self._java_api.analyze_mdx(mdx, timeout=timeout)

    @abstractmethod
    def _create_hierarchy_from_arguments(
        self, arguments: HierarchyArguments
    ) -> BaseHierarchyBound: ...
