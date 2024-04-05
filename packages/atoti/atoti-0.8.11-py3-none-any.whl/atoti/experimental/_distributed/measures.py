from collections.abc import Mapping, Set as AbstractSet

from atoti_core import MeasureIdentifier
from atoti_query import QueryMeasure
from typing_extensions import override

from ..._java_api import JavaApi
from ..._local_measures import LocalMeasures


class DistributedMeasures(LocalMeasures[QueryMeasure]):
    def __init__(self, *, cube_name: str, java_api: JavaApi) -> None:
        super().__init__(java_api=java_api)

        self._cube_name = cube_name

    @override
    def _get_underlying(self) -> dict[str, QueryMeasure]:
        """Fetch the measures from the JVM each time they are needed."""
        measures = self._java_api.get_measures(self._cube_name)
        return {
            identifier.measure_name: QueryMeasure(
                identifier,
                description=measure.description,
                folder=measure.folder,
                formatter=measure.formatter,
                visible=measure.visible,
            )
            for identifier, measure in measures.items()
        }

    @override
    def __getitem__(self, key: str, /) -> QueryMeasure:
        identifier = MeasureIdentifier(key)
        measure = self._java_api.get_measure(identifier, cube_name=self._cube_name)
        return QueryMeasure(
            identifier,
            formatter=measure.formatter,
            folder=measure.folder,
            description=measure.description,
            visible=measure.visible,
        )

    @override
    def _update(
        self,
        other: Mapping[str, QueryMeasure],
        /,
    ) -> None:
        raise RuntimeError("Distributed cube measures cannot be changed.")

    @override
    def _delete_keys(
        self,
        keys: AbstractSet[str],
        /,
    ) -> None:
        raise RuntimeError("Distributed cube measures cannot be changed.")
