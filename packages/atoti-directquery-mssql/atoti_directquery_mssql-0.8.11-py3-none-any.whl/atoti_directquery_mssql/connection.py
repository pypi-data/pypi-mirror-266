from collections.abc import Mapping

import atoti as tt
from atoti._external_table_identifier import ExternalTableIdentifier
from atoti.directquery._external_database_connection import ExternalDatabaseConnection
from typing_extensions import override

from .table import MsSqlTable


class MsSqlConnection(ExternalDatabaseConnection[MsSqlTable]):
    """Connection to an external Microsoft SQL Server database.

    See Also:
        :class:`~atoti_directquery_mssql.MsSqlConnectionInfo`.
    """

    @override
    def _create_table(
        self,
        identifier: ExternalTableIdentifier,
        /,
        *,
        types: Mapping[str, tt.DataType],
    ) -> MsSqlTable:
        return MsSqlTable(identifier, database_key=self._database_key, types=types)
