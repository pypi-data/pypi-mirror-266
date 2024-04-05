from collections.abc import Mapping

import atoti as tt
from atoti._external_table_identifier import ExternalTableIdentifier
from atoti.directquery._external_database_with_cache_connection import (
    ExternalDatabaseWithCacheConnection,
)
from typing_extensions import override

from .table import RedshiftTable


class RedshiftConnection(ExternalDatabaseWithCacheConnection[RedshiftTable]):
    """Connection to an external Redshift database.

    See Also:
        :class:`~atoti_directquery_redshift.RedshiftConnectionInfo`.
    """

    @override
    def _create_table(
        self,
        identifier: ExternalTableIdentifier,
        /,
        *,
        types: Mapping[str, tt.DataType],
    ) -> RedshiftTable:
        return RedshiftTable(identifier, database_key=self._database_key, types=types)
