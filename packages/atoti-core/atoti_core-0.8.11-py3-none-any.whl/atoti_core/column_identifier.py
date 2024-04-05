from pydantic.dataclasses import dataclass
from typing_extensions import override

from .identifier import Identifier
from .pydantic_config import PYDANTIC_CONFIG
from .table_identifier import TableIdentifier


@dataclass(config=PYDANTIC_CONFIG, frozen=True)
class ColumnIdentifier(Identifier):  # pylint: disable=keyword-only-dataclass
    table_identifier: TableIdentifier
    column_name: str

    @override
    def __repr__(self) -> str:
        return f"""{self.table_identifier!r}["{self.column_name}"]"""
