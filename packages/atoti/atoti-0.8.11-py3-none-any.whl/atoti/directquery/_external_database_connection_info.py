from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Generic, Optional

from atoti_core import Duration, frozendict

from .._java_api import JavaApi
from ._external_database_connection import ExternalDatabaseConnectionT
from ._external_database_connection_info_options import LookupMode
from ._external_table import ExternalTableT_co
from .auto_multi_column_array_conversion import AutoMultiColumnArrayConversion


class ExternalDatabaseConnectionInfo(
    Generic[ExternalDatabaseConnectionT, ExternalTableT_co], ABC
):
    def __init__(
        self,
        *,
        auto_multi_column_array_conversion: Optional[AutoMultiColumnArrayConversion],
        database_key: str,
        extra_options: Mapping[str, Optional[str]] = frozendict(),
        lookup_mode: LookupMode,
        max_sub_queries: int,
        password: Optional[str],
        query_timeout: Duration,
        url: Optional[str],
    ) -> None:
        super().__init__()

        options: dict[str, str] = {
            key: value for key, value in extra_options.items() if value is not None
        }

        if auto_multi_column_array_conversion:
            options["USE_AUTO_VECTORIZER"] = str(True)
            options["AUTO_VECTORIZER_DELIMITER"] = (
                auto_multi_column_array_conversion.separator
            )
            options["MIN_THRESHOLD_FOR_AUTO_VECTORIZER"] = str(
                auto_multi_column_array_conversion.threshold
            )

        options["GET_BY_KEY_QUERY_BEHAVIOR"] = lookup_mode.upper()
        options["MAX_SUB_QUERIES_ALLOWED_IN_MULTI_STEPS_QUERY"] = str(max_sub_queries)
        options["EXTERNAL_DATABASE_QUERY_TIMEOUT"] = str(
            int(query_timeout.total_seconds())
        )

        self._database_key = database_key
        self._options = options
        self._password = password
        self._url = url

    @abstractmethod
    def _get_database_connection(
        self, java_api: JavaApi
    ) -> ExternalDatabaseConnectionT: ...
