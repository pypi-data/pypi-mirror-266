from abc import ABC, abstractmethod

from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic.dataclasses import dataclass

from .._measure_convertible import NonConstantMeasureConvertible
from .._measure_description import MeasureDescription


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
# Do not make this type public unless also renaming it to `Scope` and getting rid of the existing `Scope` `Union`.
class BaseScope(ABC):
    @abstractmethod
    def _create_measure_description(
        self, measure: NonConstantMeasureConvertible, /, *, plugin_key: str
    ) -> MeasureDescription: ...
