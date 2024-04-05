from __future__ import annotations

import multiprocessing
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from operator import attrgetter
from typing import Any, Union

from atoti_core import ReprJson, ReprJsonable, keyword_only_dataclass
from typing_extensions import override


@keyword_only_dataclass
@dataclass(frozen=True)
class BaseRetrieval(ReprJsonable):
    id: int
    retrieval_type: str
    start_times: Sequence[int]
    elapsed_times: Sequence[int]
    result_sizes: Sequence[int]

    @property
    def title(self) -> str:
        return f"Retrieval #{self.id}: {self.retrieval_type}"

    @property
    def elapsed_time_per_core(self) -> float:
        """Return the average elapsed time per core."""
        if not self.elapsed_times:
            return 0

        parallelism = min(len(self.elapsed_times), multiprocessing.cpu_count())
        return sum(self.elapsed_times) / parallelism

    @override
    def _repr_json_(self) -> ReprJson:
        data: dict[str, Any] = {}
        data["Start time   (in ms)"] = (
            f"[{', '.join([str(t) for t in self.start_times])}]"
        )
        data["Elapsed time (in ms)"] = (
            f"[{', '.join([str(t) for t in self.elapsed_times])}]"
        )
        data["Elapsed time per core (in ms)"] = self.elapsed_time_per_core
        data["Result sizes"] = self.result_sizes
        additional_infos: dict[str, Any] = {"expanded": False, "root": self.title}
        return data, additional_infos


@keyword_only_dataclass
@dataclass(frozen=True)
class PivotRetrieval(BaseRetrieval):
    """Data associated with a cube retrieval."""

    location: str
    filter_id: int
    measures: Sequence[str]
    retrieval_filter: str
    partitioning: str
    measures_provider: str

    @override
    def _repr_json_(self) -> ReprJson:
        if self.retrieval_type == "NoOpPrimitiveAggregatesRetrieval":
            return (
                {},
                {"expanded": False, "root": self.title},
            )
        representation: ReprJson = super()._repr_json_()
        data = representation[0]
        data["Location"] = self.location
        data["Filter ID"] = self.filter_id
        data["Measures"] = f"[{', '.join(self.measures)}]"
        data["Partitioning"] = self.partitioning
        data["Measures provider"] = self.measures_provider
        return representation


@keyword_only_dataclass
@dataclass(frozen=True)
class ExternalRetrieval(BaseRetrieval):
    """Data associated with a database retrieval."""

    store: str
    fields: Sequence[str]
    joined_measures: Sequence[str]
    condition: str

    @override
    def _repr_json_(self) -> ReprJson:
        representation: ReprJson = super()._repr_json_()
        data = representation[0]
        data["Store"] = self.store
        data["Fields"] = f"[{', '.join(self.fields)}]"
        data["Joined Measures"] = f"[{', '.join(self.joined_measures)}]"
        data["Condition"] = self.condition
        return representation


class QueryPlan(ReprJsonable):
    def __init__(
        self,
        *,
        infos: Mapping[str, Any],
        retrievals: Sequence[PivotRetrieval],
        external_retrievals: Sequence[ExternalRetrieval],
        dependencies: Mapping[int, Sequence[int]],
        external_dependencies: Mapping[int, Sequence[int]],
    ):
        self.retrievals: Mapping[int, PivotRetrieval] = {
            retrieval.id: retrieval for retrieval in retrievals
        }
        self.external_retrievals: Mapping[int, ExternalRetrieval] = {
            retrieval.id: retrieval for retrieval in external_retrievals
        }
        self.infos: Mapping[str, Any] = infos
        self.dependencies: Mapping[int, Sequence[int]] = dependencies
        self.external_dependencies: Mapping[int, Sequence[int]] = external_dependencies

    def _analyze_retrievals(self) -> QueryPlanRetrievalsAnalyzer:
        """Return an object used to analyze this query plan's retrievals."""
        return QueryPlanRetrievalsAnalyzer(
            infos=self.infos,
            retrievals=self.retrievals,
            dependencies=self.dependencies,
            analyzed_retrievals=self.retrievals,
            external_retrievals=self.external_retrievals,
            external_dependencies=self.external_dependencies,
        )

    @staticmethod
    def _enrich_repr_json(
        *,
        retrieval_id: int,
        retrievals: Mapping[int, PivotRetrieval],
        dependencies: Mapping[int, Sequence[int]],
        external_retrievals: Mapping[int, ExternalRetrieval],
        external_dependencies: Mapping[int, Sequence[int]],
    ) -> dict[str, Any]:
        """Add the dependencies to the JSON of the retrieval."""
        retrieval = retrievals[retrieval_id]
        json_representable_retrieval = retrieval._repr_json_()
        if retrieval_id not in dependencies:
            # leaf
            return json_representable_retrieval[0]  # type: ignore[no-any-return]

        retrieval_dependencies = {
            retrievals[dependency_id].title: QueryPlan._enrich_repr_json(
                retrieval_id=dependency_id,
                retrievals=retrievals,
                dependencies=dependencies,
                external_retrievals=external_retrievals,
                external_dependencies=external_dependencies,
            )
            for dependency_id in dependencies[retrieval_id]
        }
        external_retrieval_dependencies = (
            {
                # External retrievals don't have dependencies: no recursive call.
                external_retrievals[external_dependency_id].title: external_retrievals[
                    external_dependency_id
                ]._repr_json_()[0]
                for external_dependency_id in external_dependencies[retrieval_id]
            }
            if retrieval_id in external_dependencies
            else {}
        )
        return {
            **json_representable_retrieval[0],
            "Dependencies": {
                **retrieval_dependencies,
                **external_retrieval_dependencies,
            },
        }

    @override
    def _repr_json_(self) -> ReprJson:
        retrievals = {
            retrieval.title: QueryPlan._enrich_repr_json(
                retrieval_id=id,
                retrievals=self.retrievals,
                dependencies=self.dependencies,
                external_retrievals=self.external_retrievals,
                external_dependencies=self.external_dependencies,
            )
            for id, retrieval in self.retrievals.items()  # noqa: A001
            if id in self.dependencies[-1]
        }
        data = {
            "Info": self.infos,
            "Retrievals": retrievals,
        }
        return data, {"expanded": True, "root": "QueryPlan"}


class QueryPlanRetrievalsAnalyzer(ReprJsonable):
    """Analyzer for query plan retrievals."""

    def __init__(
        self,
        *,
        infos: Mapping[str, Any],
        retrievals: Mapping[int, PivotRetrieval],
        dependencies: Mapping[int, Sequence[int]],
        external_retrievals: Mapping[int, ExternalRetrieval],
        external_dependencies: Mapping[int, Sequence[int]],
        analyzed_retrievals: Mapping[int, PivotRetrieval],
    ):
        self.retrievals = retrievals
        self.external_retrievals = external_retrievals
        self.infos = infos
        self.dependencies = dependencies
        self.external_dependencies = external_dependencies
        self.analyzed_retrievals = analyzed_retrievals

    def sort(
        self,
        *,
        key: Callable[[PivotRetrieval], Any] = attrgetter("elapsed_time_per_core"),
        reverse: bool = False,
    ) -> QueryPlanRetrievalsAnalyzer:
        """Sort the retrievals based on the given attribute.

        Args:
            key: A function of one argument that is used to extract
                a comparison key from each RetrievalData.
            reverse: Whether the result should be sorted in descending order or not.
        """
        return QueryPlanRetrievalsAnalyzer(
            infos=self.infos,
            retrievals=self.retrievals,
            dependencies=self.dependencies,
            external_retrievals=self.external_retrievals,
            external_dependencies=self.external_dependencies,
            analyzed_retrievals={
                retrieval.id: retrieval
                for retrieval in sorted(
                    self.analyzed_retrievals.values(), key=key, reverse=reverse
                )
            },
        )

    def filter(
        self, callback: Callable[[PivotRetrieval], bool]
    ) -> QueryPlanRetrievalsAnalyzer:
        """Filter the retrievals using the provided callback method."""
        return QueryPlanRetrievalsAnalyzer(
            infos=self.infos,
            retrievals=self.retrievals,
            dependencies=self.dependencies,
            external_retrievals=self.external_retrievals,
            external_dependencies=self.external_dependencies,
            analyzed_retrievals={
                retrieval.id: retrieval
                for retrieval in self.analyzed_retrievals.values()
                if callback(retrieval)
            },
        )

    def __getitem__(self, key: Union[int, slice], /) -> QueryPlanRetrievalsAnalyzer:
        """Return the retrieval with the target key, or a subset of the retrievals.

        Args:
            key: The ID of a retrieval, or a slice of the retrievals.
        """
        slice_idx = key if isinstance(key, slice) else slice(key, key + 1)
        return QueryPlanRetrievalsAnalyzer(
            infos=self.infos,
            retrievals=self.retrievals,
            dependencies=self.dependencies,
            external_retrievals=self.external_retrievals,
            external_dependencies=self.external_dependencies,
            analyzed_retrievals={
                retrieval.id: retrieval
                for retrieval in list(self.analyzed_retrievals.values())[slice_idx]
            },
        )

    @override
    def _repr_json_(self) -> ReprJson:
        retrievals = {
            retrieval.title: QueryPlan._enrich_repr_json(
                retrieval_id=id,
                retrievals=self.retrievals,
                dependencies=self.dependencies,
                external_retrievals=self.external_retrievals,
                external_dependencies=self.external_dependencies,
            )
            for id, retrieval in self.analyzed_retrievals.items()  # noqa: A001
        }
        return retrievals, {"expanded": False, "root": "Retrievals"}


@keyword_only_dataclass
@dataclass(frozen=True)
class QueryAnalysis(ReprJsonable):
    """Query Analysis."""

    query_plans: Sequence[QueryPlan]

    @override
    def _repr_json_(self) -> ReprJson:
        return {"Query plans": [plan._repr_json_()[0] for plan in self.query_plans]}, {
            "expanded": True,
            "root": "Query analysis",
        }
