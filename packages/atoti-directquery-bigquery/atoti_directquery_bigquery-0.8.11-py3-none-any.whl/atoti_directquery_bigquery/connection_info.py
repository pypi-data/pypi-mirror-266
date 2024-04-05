from pathlib import Path
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

from .connection import BigqueryConnection
from .table import BigqueryTable


class BigqueryConnectionInfo(
    ExternalDatabaseConnectionInfo[BigqueryConnection, BigqueryTable]
):
    """Information needed to connect to a BigQuery database."""

    @doc(**_EXTERNAL_DATABASE_CONNECTION_INFO_KWARGS)
    def __init__(
        self,
        credentials: Optional[Path] = None,
        /,
        *,
        auto_multi_column_array_conversion: Optional[
            AutoMultiColumnArrayConversion
        ] = None,
        lookup_mode: LookupMode = _DEFAULT_LOOKUP_MODE,
        max_sub_queries: int = _DEFAULT_MAX_SUB_QUERIES,
        query_timeout: Duration = _DEFAULT_QUERY_TIMEOUT,
        time_travel: bool = True,
    ):
        """Create a BigQuery connection info.

        Args:
            credentials: The path to the `BigQuery credentials file <https://cloud.google.com/docs/authentication/getting-started#setting_the_environment_variable>`__.
                If ``None``, the `application default credentials <https://cloud.google.com/java/docs/reference/google-auth-library/latest/com.google.auth.oauth2.GoogleCredentials#com_google_auth_oauth2_GoogleCredentials_getApplicationDefault__>`__ will be used.
            {auto_multi_column_array_conversion}
            {lookup_mode}
            {max_sub_queries}
            {query_timeout}
            {time_travel}

        Example:
            >>> from atoti_directquery_bigquery import BigqueryConnectionInfo
            >>> connection_info = BigqueryConnectionInfo()
            >>> external_database = session.connect_to_external_database(connection_info)

        """
        super().__init__(
            auto_multi_column_array_conversion=auto_multi_column_array_conversion,
            database_key="BIGQUERY",
            extra_options={
                "ENABLE_TIME_TRAVEL": str(time_travel).lower(),
            },
            lookup_mode=lookup_mode,
            max_sub_queries=max_sub_queries,
            password=None,
            query_timeout=query_timeout,
            url=None if credentials is None else str(credentials),
        )

    @override
    def _get_database_connection(self, java_api: JavaApi) -> BigqueryConnection:
        return BigqueryConnection(
            database_key=self._database_key,
            java_api=java_api,
        )
