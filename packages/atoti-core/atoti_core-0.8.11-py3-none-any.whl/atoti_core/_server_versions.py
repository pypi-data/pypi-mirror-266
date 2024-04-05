from typing import Optional

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from .create_camel_case_alias_generator import create_camel_case_alias_generator
from .frozen_collections import FrozenMapping, FrozenSequence
from .keyword_only_dataclass import keyword_only_dataclass
from .pydantic_config import PYDANTIC_CONFIG as __PYDANTIC_CONFIG

_PYDANTIC_CONFIG: ConfigDict = {
    **__PYDANTIC_CONFIG,
    "alias_generator": create_camel_case_alias_generator(),
    "arbitrary_types_allowed": False,
    "extra": "ignore",
}


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class ApiVersion:
    id: str
    rest_path: str
    ws_path: Optional[str] = None


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class ServerApi:
    versions: FrozenSequence[ApiVersion]


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class ServerVersions:
    version: int
    server_version: str
    apis: FrozenMapping[str, ServerApi]
