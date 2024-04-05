from pydantic.dataclasses import dataclass
from typing_extensions import override

from .identifier import Identifier
from .pydantic_config import PYDANTIC_CONFIG


@dataclass(config=PYDANTIC_CONFIG, frozen=True)
class TableIdentifier(Identifier):  # pylint: disable=keyword-only-dataclass
    table_name: str

    @override
    def __repr__(self) -> str:
        return f"""t["{self.table_name}"]"""
