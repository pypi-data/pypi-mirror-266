from collections.abc import Mapping

import atoti as tt
from atoti._external_table_identifier import ExternalTableIdentifier
from atoti.directquery._external_database_with_cache_connection import (
    ExternalDatabaseWithCacheConnection,
)
from typing_extensions import override

from .table import SnowflakeTable


class SnowflakeConnection(ExternalDatabaseWithCacheConnection[SnowflakeTable]):
    """Connection to an external Snowflake database.

    See Also:
        :class:`~atoti_directquery_snowflake.SnowflakeConnectionInfo`.
    """

    @override
    def _create_table(
        self,
        identifier: ExternalTableIdentifier,
        /,
        *,
        types: Mapping[str, tt.DataType],
    ) -> SnowflakeTable:
        return SnowflakeTable(identifier, database_key=self._database_key, types=types)
