from typing import Annotated

from pydantic import AfterValidator
from pydantic.dataclasses import dataclass
from typing_extensions import override

from .identifier import Identifier
from .pydantic_config import PYDANTIC_CONFIG


def _validate_measure_name(name: str, /) -> str:
    if "," in name:
        raise ValueError(f"`,` is not allowed, got `{name}`.")

    if name != name.strip():
        raise ValueError(
            f"Leading or trailing whitespaces are not allowed, got `{name}`."
        )

    return name


@dataclass(config=PYDANTIC_CONFIG, frozen=True)
class MeasureIdentifier(Identifier):  # pylint: disable=keyword-only-dataclass
    measure_name: Annotated[str, AfterValidator(_validate_measure_name)]

    @override
    def __repr__(self) -> str:
        return f"""m["{self.measure_name}"]"""
