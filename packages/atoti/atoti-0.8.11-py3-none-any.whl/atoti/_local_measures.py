from typing import TypeVar

from atoti_core import BaseMeasures, DelegateMutableMapping
from atoti_query import QueryMeasure

from ._java_api import JavaApi
from .measure import Measure

_Measure = TypeVar("_Measure", Measure, QueryMeasure)


class LocalMeasures(DelegateMutableMapping[str, _Measure], BaseMeasures[_Measure]):
    def __init__(self, *, java_api: JavaApi) -> None:
        super().__init__()

        self._java_api = java_api
