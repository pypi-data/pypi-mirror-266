from typing import Optional

from ._external_database_connection import ExternalDatabaseConnection
from ._external_table import ExternalTableT_co


class ExternalDatabaseWithCacheConnection(
    ExternalDatabaseConnection[ExternalTableT_co]
):
    @property
    def cache(self) -> Optional[bool]:
        """Whether the external database should cache the query results or not."""
        return self._java_api.get_external_database_cache(self._database_key)

    @cache.setter
    def cache(self, value: bool) -> None:
        self._java_api.set_external_database_cache(self._database_key, cache=value)
