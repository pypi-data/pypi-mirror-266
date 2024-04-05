from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import timedelta
from email.message import Message
from functools import cached_property
from http.client import HTTPResponse
from mimetypes import types_map
from pathlib import Path
from ssl import create_default_context
from typing import IO, Annotated, Literal, NoReturn, Optional
from urllib.error import HTTPError
from urllib.parse import urljoin
from urllib.request import (
    AbstractHTTPHandler,
    BaseHandler,
    HTTPDefaultErrorHandler,
    HTTPSHandler,
    Request,
    build_opener,
)

from pydantic import BeforeValidator, ConfigDict, TypeAdapter
from pydantic.dataclasses import dataclass
from typing_extensions import override

from ._get_endpoint_path import get_endpoint_path
from ._server_versions import ServerVersions
from .create_camel_case_alias_generator import create_camel_case_alias_generator
from .fetch_json import JsonResponse, JsonResponseBodyT, fetch_json
from .frozen_collections import FrozenSequence
from .get_type_adapter import get_type_adapter
from .http_method import HttpMethod
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
class _ErrorChainItem:
    message: str
    type: str


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class _ActiveViamHttpErrorBody:
    error_chain: FrozenSequence[_ErrorChainItem]
    stack_trace: str


def _normalize_http_error_body(value: object, /) -> object:
    return (
        value.get("error")  # Atoti Server < 6.0.0-M1.
        if isinstance(value, dict) and value.get("status") == "error"
        else value
    )


class ActiveViamHttpError(HTTPError):
    def __init__(
        self,
        *,
        body: _ActiveViamHttpErrorBody,
        code: int,
        hdrs: Message,  # spell-checker: disable-line
        url: str,
    ) -> None:
        super().__init__(
            url,
            code,
            body.stack_trace,
            hdrs,  # spell-checker: disable-line
            None,
        )

        self.error_chain: Sequence[_ErrorChainItem] = body.error_chain


class _ActiveViamJsonHttpErrorHandler(HTTPDefaultErrorHandler):
    @override
    def http_error_default(  # pylint: disable=too-many-positional-parameters
        self,
        req: Request,
        fp: Optional[IO[bytes]],
        code: int,
        msg: str,
        hdrs: Message,  # spell-checker: disable-line
    ) -> NoReturn:
        error = HTTPError(
            req.full_url,
            code,
            msg,
            hdrs,  # spell-checker: disable-line
            fp,
        )

        if fp is None or (
            hdrs.get_content_type() != types_map[".json"]  # spell-checker: disable-line
        ):
            raise error

        adapter: TypeAdapter[_ActiveViamHttpErrorBody] = get_type_adapter(
            Annotated[  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
                _ActiveViamHttpErrorBody,
                BeforeValidator(_normalize_http_error_body),
            ]
        )
        body_json = fp.read()
        body = adapter.validate_json(body_json)

        raise ActiveViamHttpError(
            body=body,
            code=code,
            hdrs=hdrs,  # spell-checker: disable-line
            url=req.full_url,
        ) from error


_Auth = Callable[[str], Mapping[str, str]]


class _AuthHandler(AbstractHTTPHandler):
    def __init__(self, auth: _Auth, /) -> None:
        super().__init__()

        self._auth = auth

    def _handle_request(self, request: Request) -> Request:
        headers = self._auth(request.full_url)
        request.headers.update(headers)
        return request

    http_request = _handle_request
    https_request = _handle_request


def _normalize_json_response_body(value: object, /) -> object:
    return (
        value.get("data")  # Atoti Server < 6.0.0-M1.
        if isinstance(value, dict) and value.get("status") == "success"
        else value
    )


class ActiveViamClient:
    """Used to communicate with ActiveViam servers such as Atoti Server or the Content Server.

    This class uses a custom HTTP error handler to enrich the raised errors with the server stack trace.
    """

    def __init__(
        self,
        url: str,
        /,
        *,
        auth: Optional[_Auth] = None,
        certificate_authority: Optional[Path] = None,
        client_certificate: Optional[Path] = None,
        client_certificate_keyfile: Optional[Path] = None,
        client_certificate_password: Optional[str] = None,
    ) -> None:
        self._url = url.strip("/")

        handlers: list[BaseHandler] = [_ActiveViamJsonHttpErrorHandler()]

        if auth:
            handlers.append(_AuthHandler(auth))

        if certificate_authority or client_certificate:
            context = create_default_context()
            if certificate_authority:
                context.load_verify_locations(cafile=certificate_authority)
            if client_certificate:
                context.load_cert_chain(
                    certfile=client_certificate,
                    keyfile=client_certificate_keyfile,
                    password=client_certificate_password,
                )
            handlers.append(HTTPSHandler(context=context))

        self._opener_director = build_opener(*handlers)

    @property
    def url(self) -> str:
        return self._url

    def fetch(
        self, request: Request, /, *, timeout: Optional[timedelta] = None
    ) -> HTTPResponse:
        response = self._opener_director.open(
            request, timeout=timeout.total_seconds() if timeout else None
        )
        assert isinstance(response, HTTPResponse)
        return response

    def fetch_json(
        self,
        *,
        body: object = None,
        check_response_content_type: bool = True,
        method: Optional[HttpMethod] = None,
        namespace: str,
        query: str = "",
        response_body_type: type[JsonResponseBodyT] = object,  # type: ignore[assignment]
        route: str,
    ) -> JsonResponse[JsonResponseBodyT]:
        url = self.get_endpoint_url(namespace=namespace, route=route)

        if query:
            url = f"{url}?{query}"

        return fetch_json(
            url,
            body=body,
            check_response_content_type=check_response_content_type,
            method=method,
            opener_director=self._opener_director,
            response_body_type=Annotated[  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
                response_body_type, BeforeValidator(_normalize_json_response_body)
            ],
        )

    def ping(self) -> str:
        url = self.get_endpoint_url(namespace="activeviam/pivot", route="ping")
        response = self._opener_director.open(url)
        body = response.read().decode("utf8")
        assert isinstance(body, str)
        expected_body = "pong"
        if body != expected_body:
            raise RuntimeError(
                f"Expected `ping()`'s response body to be `{expected_body}` but got `{body}`."
            )
        return body

    def _get_endpoint_path(
        self,
        *,
        attribute_name: Literal["restPath", "wsPath"] = "restPath",
        namespace: str,
        route: str,
    ) -> str:
        return get_endpoint_path(
            attribute_name=attribute_name,
            namespace=namespace,
            route=route,
            server_versions=self.server_versions,
        )

    def _get_url(self, path: str, /) -> str:
        return urljoin(f"{self.url}/", path.lstrip("/"))

    def get_endpoint_url(
        self,
        *,
        attribute_name: Literal["restPath", "wsPath"] = "restPath",
        namespace: str,
        route: str,
    ) -> str:
        path = self._get_endpoint_path(
            attribute_name=attribute_name, namespace=namespace, route=route
        )
        return self._get_url(path)

    @cached_property
    def server_versions(self) -> ServerVersions:
        url = self._get_url("versions/rest")
        response = fetch_json(
            url,
            opener_director=self._opener_director,
            response_body_type=ServerVersions,
        )
        return response.body

    @property
    def has_atoti_python_api_endpoints(self) -> bool:
        return "atoti" in self.server_versions.apis
