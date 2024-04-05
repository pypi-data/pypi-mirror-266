from abc import ABC, abstractmethod


class DiscoveryProtocol(ABC):
    @property
    @abstractmethod
    def _xml(self) -> str: ...
