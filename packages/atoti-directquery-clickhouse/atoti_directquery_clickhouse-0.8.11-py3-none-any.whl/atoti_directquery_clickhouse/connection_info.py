from typing import Optional

from atoti._docs_utils import (
    EXTERNAL_DATABASE_CONNECTION_INFO_KWARGS as _EXTERNAL_DATABASE_CONNECTION_INFO_KWARGS,
)
from atoti._java_api import JavaApi
from atoti.directquery._external_database_connection_info import (
    ExternalDatabaseConnectionInfo,
)
from atoti.directquery._external_database_connection_info_options import (
    DEFAULT_LOOKUP_MODE as _DEFAULT_LOOKUP_MODE,
    DEFAULT_MAX_SUB_QUERIES as _DEFAULT_MAX_SUB_QUERIES,
    DEFAULT_QUERY_TIMEOUT as _DEFAULT_QUERY_TIMEOUT,
    LookupMode,
)
from atoti_core import Duration, doc
from typing_extensions import override

from .connection import ClickhouseConnection
from .table import ClickhouseTable


class ClickhouseConnectionInfo(
    ExternalDatabaseConnectionInfo[ClickhouseConnection, ClickhouseTable]
):
    """Information needed to connect to a ClickHouse database."""

    @doc(**_EXTERNAL_DATABASE_CONNECTION_INFO_KWARGS)
    def __init__(
        self,
        url: str,
        /,
        *,
        lookup_mode: LookupMode = _DEFAULT_LOOKUP_MODE,
        max_sub_queries: int = _DEFAULT_MAX_SUB_QUERIES,
        password: Optional[str] = None,
        query_timeout: Duration = _DEFAULT_QUERY_TIMEOUT,
    ):
        """Create a ClickHouse connection info.

        Args:
            url: The connection string.
                The pattern is: ``(clickhouse|ch):(https|http|...)://login:password@host:port/database?prop=value``.
                For example: ``"clickhouse:https://user:password@localhost:8123/mydb"``.
                When a parameter is missing, the default value will be used.
            {lookup_mode}
            {max_sub_queries}
            {password}
            {query_timeout}

        See Also:
            :class:`atoti_directquery_snowflake.SnowflakeConnectionInfo` for an example.
        """
        super().__init__(
            auto_multi_column_array_conversion=None,
            database_key="CLICKHOUSE",
            lookup_mode=lookup_mode,
            max_sub_queries=max_sub_queries,
            password=password,
            query_timeout=query_timeout,
            url=url,
        )

    @override
    def _get_database_connection(self, java_api: JavaApi) -> ClickhouseConnection:
        return ClickhouseConnection(
            database_key=self._database_key,
            java_api=java_api,
        )
