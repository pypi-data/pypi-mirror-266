from dataclasses import dataclass
from enum import StrEnum
import json
from urllib.parse import urljoin
import base64
import typing
import requests
from uncountable.types.base import JsonValue
from uncountable.types.client_base import APIRequest, ClientMethods
from pkgs.argument_parser import CachedParser
from pkgs.serialization_util import serialize_for_api


DT = typing.TypeVar("DT")


class EndpointMethod(StrEnum):
    POST = "POST"
    GET = "GET"


@dataclass(kw_only=True)
class HTTPRequestBase:
    method: EndpointMethod
    url: str
    headers: dict[str, str]
    body: typing.Optional[str] = None
    query_params: typing.Optional[dict[str, str]]


@dataclass(kw_only=True)
class HTTPGetRequest(HTTPRequestBase):
    method: typing.Literal[EndpointMethod.GET]
    query_params: dict[str, str]


@dataclass(kw_only=True)
class HTTPPostRequest(HTTPRequestBase):
    method: typing.Literal[EndpointMethod.POST]


HTTPRequest = HTTPPostRequest | HTTPGetRequest


@dataclass(kw_only=True)
class AuthDetailsApiKey:
    api_id: str
    api_secret_key: str


AuthDetails = AuthDetailsApiKey


class Client(ClientMethods):
    _parser_map: dict[type, CachedParser] = {}
    _auth_details: AuthDetails
    _base_url: str

    def __init__(self, *, base_url: str, auth_details: AuthDetails):
        self._auth_details = auth_details
        self._base_url = base_url

    def do_request(self, *, api_request: APIRequest, return_type: type[DT]) -> DT:
        http_request = self._build_http_request(api_request=api_request)
        match http_request:
            case HTTPGetRequest():
                response = requests.get(
                    http_request.url,
                    headers=http_request.headers,
                    params=http_request.query_params,
                )
            case HTTPPostRequest():
                response = requests.post(
                    http_request.url,
                    headers=http_request.headers,
                    data=http_request.body,
                    params=http_request.query_params,
                )
            case _:
                typing.assert_never(http_request)
        if response.status_code < 200 or response.status_code > 299:
            # TODO: handle_error
            pass
        cached_parser = self._get_cached_parser(return_type)
        try:
            data = response.json()["data"]
            return cached_parser.parse_api(data)
        except ValueError as err:
            # TODO: handle parse error
            raise err

    def _get_cached_parser(self, data_type: type[DT]) -> CachedParser[DT]:
        if data_type not in self._parser_map:
            self._parser_map[data_type] = CachedParser(data_type)
        return self._parser_map[data_type]

    def _build_auth_headers(self) -> dict[str, str]:
        match self._auth_details:
            case AuthDetailsApiKey():
                encoded = base64.standard_b64encode(
                    f"{self._auth_details.api_id}:{self._auth_details.api_secret_key}".encode(
                        "utf-8"
                    )
                ).decode("utf-8")
                return {"Authorization": f"Basic {encoded}"}
        typing.assert_never(self._auth_details)

    def _build_http_request(self, *, api_request: APIRequest) -> HTTPRequest:
        headers = self._build_auth_headers()
        method = api_request.method.lower()
        query_params = {"data": json.dumps(serialize_for_api(api_request.args))}
        match method:
            case "get":
                return HTTPGetRequest(
                    method=EndpointMethod.GET,
                    url=urljoin(self._base_url, api_request.endpoint),
                    query_params=query_params,
                    headers=headers,
                )
            case "post":
                return HTTPPostRequest(
                    method=EndpointMethod.POST,
                    url=urljoin(self._base_url, api_request.endpoint),
                    headers=headers,
                    query_params=query_params
                )
            case _:
                raise ValueError(f"unsupported request method: {method}")
