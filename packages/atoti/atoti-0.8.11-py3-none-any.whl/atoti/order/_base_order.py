from abc import ABC, abstractmethod

from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic.dataclasses import dataclass


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class BaseOrder(ABC):
    """Base class for orders."""

    @property
    @abstractmethod
    def _key(self) -> str: ...
