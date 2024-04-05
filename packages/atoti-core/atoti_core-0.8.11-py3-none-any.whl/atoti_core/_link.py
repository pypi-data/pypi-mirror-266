from collections.abc import Mapping
from dataclasses import dataclass, replace
from textwrap import dedent
from urllib.parse import urlparse

from typing_extensions import Self, deprecated, override

from .deprecated_warning_category import DEPRECATED_WARNING_CATEGORY
from .keyword_only_dataclass import keyword_only_dataclass
from .mime_type import LINK_MIME_TYPE, MARKDOWN_MIME_TYPE, TEXT_MIME_TYPE


@keyword_only_dataclass
@dataclass(frozen=True)
class Link:
    session_local_url: str
    session_location: Mapping[str, object]
    path: str = ""

    @override
    def __repr__(self) -> str:
        text = self._repr_mimebundle_({}, {})[TEXT_MIME_TYPE]
        assert isinstance(text, str)
        return text

    @deprecated(
        "Calling `Session.link()` is deprecated, just access the `Session.link` property instead. Use `session.link / 'some_path'` to add a path to the linked URL.",
        category=DEPRECATED_WARNING_CATEGORY,
    )
    def __call__(self, *, path: str = "") -> Self:
        return replace(self, path=path.lstrip("/"))

    def __truediv__(self, path: str, /) -> Self:
        assert isinstance(path, str)
        return replace(self, path=f"{self.path}/{path}" if self.path else path)

    def _repr_mimebundle_(
        self,
        include: object,  # noqa: ARG002
        exclude: object,  # noqa: ARG002
    ) -> dict[str, object]:
        url = self.session_local_url

        if self.path:
            url += f"/{self.path}"

        bundle: dict[str, object] = {
            LINK_MIME_TYPE: {
                "path": self.path,
                "sessionLocation": self.session_location,
            }
        }

        is_local = urlparse(url).hostname == "localhost"

        if is_local:
            note = "This is the session's local URL: it may not be reachable if Atoti is running on another machine."

            bundle[MARKDOWN_MIME_TYPE] = dedent(
                f"""\
                {url}

                _Note_: {note}
                """
            ).strip()
            bundle[TEXT_MIME_TYPE] = f"{url} ({note})"
        else:
            bundle[TEXT_MIME_TYPE] = url

        return bundle
