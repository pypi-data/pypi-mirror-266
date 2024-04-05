from pydantic.dataclasses import dataclass

from .data_type import DataType
from .keyword_only_dataclass import keyword_only_dataclass
from .pydantic_config import PYDANTIC_CONFIG


@keyword_only_dataclass
@dataclass(config=PYDANTIC_CONFIG, frozen=True)
class ColumnDescription:
    name: str
    data_type: DataType
    nullable: bool = False
