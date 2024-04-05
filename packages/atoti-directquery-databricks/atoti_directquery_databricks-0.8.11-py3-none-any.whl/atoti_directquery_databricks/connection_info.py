from typing import Literal, Optional

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

from .connection import DatabricksConnection
from .table import DatabricksTable


class DatabricksConnectionInfo(
    ExternalDatabaseConnectionInfo[DatabricksConnection, DatabricksTable]
):
    """Information needed to connect to a Databricks database."""

    @doc(**_EXTERNAL_DATABASE_CONNECTION_INFO_KWARGS)
    def __init__(
        self,
        url: str,
        /,
        *,
        auto_multi_column_array_conversion: Optional[
            AutoMultiColumnArrayConversion
        ] = None,
        heavy_load_url: Optional[str] = None,
        lookup_mode: LookupMode = _DEFAULT_LOOKUP_MODE,
        max_sub_queries: int = _DEFAULT_MAX_SUB_QUERIES,
        password: Optional[str] = None,
        query_timeout: Duration = _DEFAULT_QUERY_TIMEOUT,
        time_travel: Literal[False, "lax", "strict"] = "strict",
    ):
        """Create a Databricks connection info.

        `To aggregate native Databrick arrays, UDAFs (User Defined Aggregation Functions) provided by ActiveViam must be registered on the cluster <https://docs.activeviam.com/products/atoti/server/6.0-next/docs/directquery/databases/databricks/#vectors-support>`__.
        Native array aggregation is not supported on SQL warehouses.

        Args:
            url: The JDBC connection string.
            {auto_multi_column_array_conversion}
            heavy_load_url: When not ``None``, this JDBC connection string will be used instead of *url* for the heavy load phases (e.g. startup and refresh).
            {lookup_mode}
            {max_sub_queries}
            {password}
            {query_timeout}
            time_travel: How to use Databricks' time travel feature.

                Databricks does not support time travel with views, so the options are:

                * ``False``: tables and views are queried on the latest state of the database.
                * ``"lax"``: tables are queried with time travel but views are queried without it.
                * ``"strict"``: tables are queried with time travel and querying a view raises an error.

        Example:
            >>> import os
            >>> from atoti_directquery_databricks import DatabricksConnectionInfo
            >>> connection_info = DatabricksConnectionInfo(
            ...     "jdbc:databricks://"
            ...     + os.environ["DATABRICKS_SERVER_HOSTNAME"]
            ...     + "/default;"
            ...     + "transportMode=http;"
            ...     + "ssl=1;"
            ...     + "httpPath="
            ...     + os.environ["DATABRICKS_HTTP_PATH"]
            ...     + ";"
            ...     + "AuthMech=3;"
            ...     + "UID=token;",
            ...     password=os.environ["DATABRICKS_AUTH_TOKEN"],
            ... )
            >>> external_database = session.connect_to_external_database(connection_info)

        """
        super().__init__(
            auto_multi_column_array_conversion=auto_multi_column_array_conversion,
            database_key="DATABRICKS",
            extra_options={
                "HEAVY_LOAD_CONNECTION_STRING": heavy_load_url,
                "TIME_TRAVEL": time_travel.upper() if time_travel else "DISABLED",
            },
            lookup_mode=lookup_mode,
            max_sub_queries=max_sub_queries,
            password=password,
            query_timeout=query_timeout,
            url=url,
        )

    @override
    def _get_database_connection(self, java_api: JavaApi) -> DatabricksConnection:
        return DatabricksConnection(
            database_key=self._database_key,
            java_api=java_api,
        )
