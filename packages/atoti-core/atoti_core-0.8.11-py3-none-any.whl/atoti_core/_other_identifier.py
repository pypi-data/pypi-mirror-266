from typing import TypeVar

from .identifier import Identifier

OtherIdentifierT_co = TypeVar("OtherIdentifierT_co", bound=Identifier, covariant=True)
