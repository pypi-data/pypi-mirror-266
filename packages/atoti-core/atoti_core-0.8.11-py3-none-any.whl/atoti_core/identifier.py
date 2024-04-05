from abc import ABC, abstractmethod

from typing_extensions import override


class Identifier(ABC):  # pylint: disable=keyword-only-dataclass
    @abstractmethod
    @override
    def __repr__(self) -> str: ...

    @override
    def __str__(self) -> str:
        return repr(self)
