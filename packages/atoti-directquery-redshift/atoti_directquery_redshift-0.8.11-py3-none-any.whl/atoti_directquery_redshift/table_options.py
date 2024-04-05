from atoti.directquery._array_conversion_options import ArrayConversionOptions
from atoti.directquery._external_table_options import ExternalTableOptions
from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic.dataclasses import dataclass

from .table import RedshiftTable


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class RedshiftTableOptions(ExternalTableOptions[RedshiftTable], ArrayConversionOptions):
    """Options passed to :meth:`atoti.Session.add_external_table`."""
