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

from .connection import SynapseConnection
from .table import SynapseTable


class SynapseConnectionInfo(
    ExternalDatabaseConnectionInfo[SynapseConnection, SynapseTable]
):
    """Information needed to connect to a Synapse database."""

    @doc(**_EXTERNAL_DATABASE_CONNECTION_INFO_KWARGS)
    def __init__(
        self,
        url: str,
        /,
        *,
        auto_multi_column_array_conversion: Optional[
            AutoMultiColumnArrayConversion
        ] = None,
        lookup_mode: LookupMode = _DEFAULT_LOOKUP_MODE,
        max_sub_queries: int = _DEFAULT_MAX_SUB_QUERIES,
        password: Optional[str] = None,
        query_timeout: Duration = _DEFAULT_QUERY_TIMEOUT,
    ):
        """Create a Synapse connection info.

        Args:
            url: The JDBC connection string.
                See https://docs.microsoft.com/en-us/azure/synapse-analytics/sql/connection-strings#sample-jdbc-connection-string for more information.
            {auto_multi_column_array_conversion}
            {lookup_mode}
            {max_sub_queries}
            {password}
            {query_timeout}

        Example:
            .. doctest::
                :hide:

                >>> account_identifier = "tck-directquery-ondemand"

            .. doctest::

                >>> import os
                >>> from atoti_directquery_synapse import SynapseConnectionInfo
                >>> connection_info = SynapseConnectionInfo(
                ...     "jdbc:sqlserver://"
                ...     + account_identifier
                ...     + ".sql.azuresynapse.net;authentication="
                ...     + os.environ["SYNAPSE_AUTHENTICATION_METHOD"]
                ...     + ";user="
                ...     + os.environ["SYNAPSE_USERNAME"],
                ...     password=os.environ["SYNAPSE_PASSWORD"],
                ... )
                >>> external_database = session.connect_to_external_database(connection_info)
        """
        super().__init__(
            auto_multi_column_array_conversion=auto_multi_column_array_conversion,
            database_key="SYNAPSE",
            lookup_mode=lookup_mode,
            max_sub_queries=max_sub_queries,
            password=password,
            query_timeout=query_timeout,
            url=url,
        )

    @override
    def _get_database_connection(self, java_api: JavaApi) -> SynapseConnection:
        return SynapseConnection(
            database_key=self._database_key,
            java_api=java_api,
        )
