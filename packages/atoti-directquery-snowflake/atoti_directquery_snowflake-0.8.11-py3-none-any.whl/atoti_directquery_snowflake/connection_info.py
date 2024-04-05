from typing import Optional

from atoti._docs_utils import (
    EXTERNAL_DATABASE_CONNECTION_INFO_KWARGS as _EXTERNAL_DATABASE_CONNECTION_INFO_KWARGS,
)
from atoti._java_api import JavaApi
from atoti.directquery import AutoMultiColumnArrayConversion
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

from .connection import SnowflakeConnection
from .table import SnowflakeTable


class SnowflakeConnectionInfo(
    ExternalDatabaseConnectionInfo[SnowflakeConnection, SnowflakeTable]
):
    """Information needed to connect to a Snowflake database."""

    @doc(**_EXTERNAL_DATABASE_CONNECTION_INFO_KWARGS)
    def __init__(
        self,
        url: str,
        /,
        *,
        array_agg_wrapper_function_name: Optional[str] = None,
        auto_multi_column_array_conversion: Optional[
            AutoMultiColumnArrayConversion
        ] = None,
        feeding_warehouse_name: Optional[str] = None,
        lookup_mode: LookupMode = _DEFAULT_LOOKUP_MODE,
        max_sub_queries: int = _DEFAULT_MAX_SUB_QUERIES,
        password: Optional[str] = None,
        query_timeout: Duration = _DEFAULT_QUERY_TIMEOUT,
        time_travel: bool = True,
    ):
        """Create a Snowflake connection info.

        Args:
            url: The JDBC connection string.
                See https://docs.snowflake.com/en/user-guide/jdbc-configure.html#jdbc-driver-connection-string for more information.
            array_agg_wrapper_function_name: The name of the User Defined Function to use to wrap the aggregations on arrays to improve performance.
                This function must be defined in Snowflake and accessible to the role running the queries.
            {auto_multi_column_array_conversion}
            feeding_warehouse_name: The name of the warehouse to use for the initial feeding.
                If ``None``, the main warehouse will be used.
            {lookup_mode}
            {max_sub_queries}
            {password}
            {query_timeout}
            {time_travel}

        Example:
            >>> import os
            >>> from atoti_directquery_snowflake import SnowflakeConnectionInfo
            >>> connection_info = SnowflakeConnectionInfo(
            ...     "jdbc:snowflake://"
            ...     + os.environ["SNOWFLAKE_ACCOUNT_IDENTIFIER"]
            ...     + ".snowflakecomputing.com/?user="
            ...     + os.environ["SNOWFLAKE_USERNAME"],
            ...     password=os.environ["SNOWFLAKE_PASSWORD"],
            ... )
            >>> external_database = session.connect_to_external_database(connection_info)

        """
        super().__init__(
            auto_multi_column_array_conversion=auto_multi_column_array_conversion,
            database_key="SNOWFLAKE",
            extra_options={
                "ARRAY_AGG_WRAPPER_FUNCTION_NAME": array_agg_wrapper_function_name,
                "ENABLE_TIME_TRAVEL": str(time_travel).lower(),
                "FEEDING_WAREHOUSE_NAME": feeding_warehouse_name,
            },
            lookup_mode=lookup_mode,
            max_sub_queries=max_sub_queries,
            password=password,
            query_timeout=query_timeout,
            url=url,
        )

    @override
    def _get_database_connection(self, java_api: JavaApi) -> SnowflakeConnection:
        return SnowflakeConnection(
            database_key=self._database_key,
            java_api=java_api,
        )
