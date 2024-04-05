from collections.abc import Mapping
from datetime import timedelta
from http.client import HTTPResponse
from mimetypes import types_map
from typing import Generic, Optional, TypeVar
from urllib.request import OpenerDirector, Request, urlopen

from pydantic.dataclasses import dataclass

from .frozen_collections import FrozenMapping
from .frozendict import frozendict
from .get_type_adapter import get_type_adapter
from .http_method import HttpMethod
from .keyword_only_dataclass import keyword_only_dataclass
from .pydantic_config import PYDANTIC_CONFIG

_CONTENT_TYPE_HEADER_NAME = "content-type"
_JSON_CONTENT_TYPE = types_map[".json"]


JsonResponseBodyT = TypeVar("JsonResponseBodyT", bound=object)


@keyword_only_dataclass
@dataclass(config=PYDANTIC_CONFIG, frozen=True)
class JsonResponse(Generic[JsonResponseBodyT]):
    body: JsonResponseBodyT
    headers: FrozenMapping[str, str]
    status_code: int


def fetch_json(
    url: str,
    /,
    *,
    body: object = None,
    check_response_content_type: bool = True,
    headers: Mapping[str, str] = frozendict(),
    method: Optional[HttpMethod] = None,
    opener_director: Optional[OpenerDirector] = None,
    response_body_type: type[JsonResponseBodyT] = object,  # type: ignore[assignment]
    timeout: Optional[timedelta] = None,
) -> JsonResponse[JsonResponseBodyT]:
    request_body_json: Optional[bytes] = None

    if body is not None:
        request_body_adapter = get_type_adapter(type(body))
        request_body_json = request_body_adapter.dump_json(body, by_alias=True)

    headers = {_CONTENT_TYPE_HEADER_NAME: _JSON_CONTENT_TYPE, **headers}
    request = Request(url, data=request_body_json, headers=headers, method=method)  # noqa: S310
    timeout_in_seconds = timeout.total_seconds() if timeout else None

    response: HTTPResponse = (
        opener_director.open(request, timeout=timeout_in_seconds)
        if opener_director
        else urlopen(request, timeout=timeout_in_seconds)  # noqa: S310
    )

    with response:
        if (
            check_response_content_type
            and response.headers.get_content_type() != _JSON_CONTENT_TYPE
        ):
            raise RuntimeError(
                f"Expected response's `{_CONTENT_TYPE_HEADER_NAME}` to be `{_JSON_CONTENT_TYPE}` but got `{response.headers.get_content_type()}`."
            )

        response_body_json = response.read() or "null"
        response_body_adapter = get_type_adapter(response_body_type)
        response_body = response_body_adapter.validate_json(response_body_json)

        return JsonResponse(
            body=response_body,
            headers=dict(response.headers),  # pyright: ignore[reportArgumentType]
            status_code=response.status,
        )
