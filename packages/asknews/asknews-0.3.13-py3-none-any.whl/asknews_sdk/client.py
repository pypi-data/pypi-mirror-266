from __future__ import annotations

import asyncio
from typing import Any
from httpx import AsyncClient, HTTPStatusError
from authlib.integrations.httpx_client import AsyncOAuth2Client
from enum import Enum
from asgiref.typing import ASGIApplication

from asknews_sdk.version import __version__
from asknews_sdk.errors import raise_from_json
from asknews_sdk.security import OAuthToken, InjectToken
from asknews_sdk.utils import (
    serialize,
    deserialize,
    build_accept_header,
    build_url,
    determine_content_type
)


class StreamType(str, Enum):
    bytes = "bytes"
    lines = "lines"
    raw = "raw"


class APIRequest:
    """
    API Request object used by the APIClient.
    """
    def __init__(
        self,
        base_url: str,
        method: str,
        endpoint: str,
        body: Any | None = None,
        query: dict | None = None,
        headers: dict | None = None,
        params: dict | None = None,
        accept: list[tuple[str, float]] | None = None,
    ) -> None:
        self.base_url = base_url
        self.method = method
        self.endpoint = endpoint
        self.query = query
        self.params = params
        self.accept = accept
        self.url = build_url(
            base_url=self.base_url,
            endpoint=self.endpoint,
            query=self.query,
            params=self.params
        )
        self.headers = headers or {}
        self.content_type = self.headers.pop("Content-Type", determine_content_type(body))
        self.body = serialize(body) if body and not isinstance(body, bytes) else None
        self.accept = accept or [
            (self.content_type if "json" in self.content_type else "application/json", 1.0)
        ]
        self.headers["Content-Type"] = self.content_type
        self.headers["Accept"] = build_accept_header(self.accept)


class APIResponse:
    """
    API Response object returned by the APIClient.
    """
    def __init__(
        self,
        request: APIRequest,
        status_code: int,
        headers: dict,
        body: bytes,
        stream: bool = False,
    ) -> None:
        self.request = request
        self.status_code = status_code
        self.headers = headers
        self.body = body
        self.stream = stream
        self.content_type = headers.get("Content-Type", "application/json")
        self.content = self.deserialize_body() if not self.stream else self.body

    def deserialize_body(self) -> Any:
        if self.content_type == "application/octet-stream":
            return self.body
        elif self.content_type == "application/json":
            return deserialize(self.body)
        elif self.content_type == "text/plain":
            return self.body.decode("utf-8")
        else:
            return self.body


class APIClient:
    """
    Base HTTP API Client

    :param client_id: Client ID
    :type client_id: str
    :param client_secret: Client secret
    :type client_secret: str
    :param scopes: OAuth scopes
    :type scopes: set[str]
    :param base_url: Base URL
    :type base_url: str
    :param token_url: Token URL
    :type token_url: str
    :param verify_ssl: Verify SSL certificate
    :type verify_ssl: bool
    :param retries: Default number of retries
    :type retries: int
    :param timeout: Request timeout
    :type timeout: Optional[float]
    :param follow_redirects: Follow redirects
    :type follow_redirects: bool
    """
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scopes: set[str] | None,
        base_url: str,
        token_url: str,
        verify_ssl: bool = True,
        retries: int = 3,
        timeout: float | None = None,
        follow_redirects: bool = True,
        _mock_server: ASGIApplication | None = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        # By default the offline and openid scopes
        # are set even if the user doesn't specify them
        self.scopes = {"offline", "openid", *(scopes or set())}
        self.base_url = base_url
        self.token_url = token_url
        self.verify_ssl = verify_ssl
        self.retries = retries
        self.timeout = timeout

        self._token = OAuthToken()
        # We use a lock to synchronize coroutines to prevent
        # concurrent attempts to refresh the same token
        self._token_lock = asyncio.Lock()
        self._oauth_client = AsyncOAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope=" ".join(self.scopes) if self.scopes else None,
            token_endpoint_auth_method="client_secret_basic",
            token_type="Bearer",
        )

        self._client = AsyncClient(
            base_url=self.base_url,
            verify=self.verify_ssl,
            timeout=self.timeout,
            auth=InjectToken(self._token),
            follow_redirects=follow_redirects,
            headers={
                "User-Agent": f"asknews-sdk-python/{__version__}"
            },
            app=_mock_server,
        )

    async def close(self) -> None:
        """
        Close the Client.
        """
        await self._client.aclose()

    async def __aenter__(self) -> APIClient:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

        if exc:
            raise exc

    async def _refresh_token(self) -> None:
        self._token.set_token(
            await self._oauth_client.fetch_token(
                self.token_url,
                grant_type="client_credentials",
            )
        )

    def reset_token(self) -> None:
        """
        Reset the current token.
        """
        self._token.reset_token()

    async def ensure_valid_token(self, force: bool = False) -> None:
        """
        Ensure a valid access token is available.

        :param force: Force the token to be refreshed
        :type force: bool
        """
        async with self._token_lock:
            if force:
                self.reset_token()

            if self._token.is_expired():
                await self._refresh_token()

    def build_request(
        self,
        method: str,
        endpoint: str,
        body: Any | None = None,
        query: dict | None = None,
        headers: dict | None = None,
        params: dict | None = None,
        accept: list[tuple[str, float]] | None = None,
    ) -> APIRequest:
        """
        Build an APIRequest object.

        :param method: HTTP method
        :type method: str
        :param endpoint: API endpoint
        :type endpoint: str
        :param body: Request body
        :type body: Any | None
        :param query: Query parameters
        :type query: dict | None
        :param headers: Request headers
        :type headers: dict | None
        :param params: Path parameters
        :type params: dict | None
        :param accept: Accept header
        :type accept: list[tuple[str, float]] | None
        :return: APIRequest object
        :rtype: APIRequest
        """
        return APIRequest(
            base_url=self.base_url,
            method=method,
            endpoint=endpoint,
            body=body,
            query=query,
            headers=headers,
            params=params,
            accept=accept,
        )

    async def request(
        self,
        method: str,
        endpoint: str,
        body: Any | None = None,
        query: dict | None = None,
        headers: dict | None = None,
        params: dict | None = None,
        accept: list[tuple[str, float]] | None = None,
        stream: bool = False,
        stream_type: StreamType = StreamType.bytes,
    ) -> APIResponse:
        """
        Send an HTTP request.

        :param method: HTTP method
        :type method: str
        :param endpoint: API endpoint
        :type endpoint: str
        :param body: Request body
        :type body: Any | None
        :param query: Query parameters
        :type query: dict | None
        :param headers: Request headers
        :type headers: dict | None
        :param params: Path parameters
        :type params: dict | None
        :param accept: Accept header
        :type accept: list[tuple[str, float]] | None
        :param stream: Stream response content
        :type stream: bool
        :param stream_type: Stream type
        :type stream_type: StreamType
        :return: APIResponse object
        :rtype: APIResponse
        """
        # TODO: Add logic for getting a new token if
        # a 401 is returned from the API up to one time
        await self.ensure_valid_token()

        request = self.build_request(
            method=method,
            endpoint=endpoint,
            body=body,
            query=query,
            headers=headers,
            params=params,
            accept=accept,
        )

        response = await self._client.request(
            method=request.method,
            url=request.url,
            content=request.body,
            headers=request.headers,
        )
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            raise_from_json(
                e.response.json()
            )

        if stream:
            match stream_type:
                case StreamType.bytes:
                    response_body = response.aiter_bytes()
                case StreamType.lines:
                    response_body = response.aiter_lines()
                case StreamType.raw:
                    response_body = response.aiter_raw()
        else:
            response_body = response.content

        return APIResponse(
            request=request,
            status_code=response.status_code,
            headers=dict(response.headers.items()),
            body=response_body,
            stream=stream,
        )

    async def get(
        self,
        endpoint: str,
        query: dict | None = None,
        headers: dict | None = None,
        params: dict | None = None,
        accept: list[tuple[str, float]] | None = None,
        stream: bool = False,
        stream_type: StreamType = StreamType.bytes,
    ) -> APIResponse:
        """
        Send a GET request.

        :param endpoint: API endpoint
        :type endpoint: str
        :param query: Query parameters
        :type query: dict | None
        :param headers: Request headers
        :type headers: dict | None
        :param params: Path parameters
        :type params: dict | None
        :param accept: Accept header
        :type accept: list[tuple[str, float]] | None
        :param stream: Stream response content
        :type stream: bool
        :param stream_type: Stream type
        :type stream_type: StreamType
        :return: APIResponse object
        :rtype: APIResponse
        """
        return await self.request(
            "GET",
            endpoint,
            query=query,
            headers=headers,
            params=params,
            accept=accept,
            stream=stream,
            stream_type=stream_type,
        )

    async def post(
        self,
        endpoint: str,
        body: Any | None = None,
        query: dict | None = None,
        headers: dict | None = None,
        params: dict | None = None,
        accept: list[tuple[str, float]] | None = None,
        stream: bool = False,
        stream_type: StreamType = StreamType.bytes,
    ) -> APIResponse:
        """
        Send a POST request.

        :param endpoint: API endpoint
        :type endpoint: str
        :param body: Request body
        :type body: Any | None
        :param query: Query parameters
        :type query: dict | None
        :param headers: Request headers
        :type headers: dict | None
        :param params: Path parameters
        :type params: dict | None
        :param accept: Accept header
        :type accept: list[tuple[str, float]] | None
        :param stream: Stream response content
        :type stream: bool
        :param stream_type: Stream type
        :type stream_type: StreamType
        :return: APIResponse object
        :rtype: APIResponse
        """
        return await self.request(
            "POST",
            endpoint,
            body=body,
            query=query,
            headers=headers,
            params=params,
            accept=accept,
            stream=stream,
            stream_type=stream_type,
        )

    async def put(
        self,
        endpoint: str,
        body: Any | None = None,
        query: dict | None = None,
        headers: dict | None = None,
        params: dict | None = None,
        accept: list[tuple[str, float]] | None = None,
        stream: bool = False,
        stream_type: StreamType = StreamType.bytes,
    ) -> APIResponse:
        """
        Send a PUT request.

        :param endpoint: API endpoint
        :type endpoint: str
        :param body: Request body
        :type body: Any | None
        :param query: Query parameters
        :type query: dict | None
        :param headers: Request headers
        :type headers: dict | None
        :param params: Path parameters
        :type params: dict | None
        :param accept: Accept header
        :type accept: list[tuple[str, float]] | None
        :param stream: Stream response content
        :type stream: bool
        :param stream_type: Stream type
        :type stream_type: StreamType
        :return: APIResponse object
        :rtype: APIResponse
        """
        return await self.request(
            "PUT",
            endpoint,
            body=body,
            query=query,
            headers=headers,
            params=params,
            accept=accept,
            stream=stream,
            stream_type=stream_type,
        )

    async def patch(
        self,
        endpoint: str,
        body: Any | None = None,
        query: dict | None = None,
        headers: dict | None = None,
        params: dict | None = None,
        accept: list[tuple[str, float]] | None = None,
        stream: bool = False,
        stream_type: StreamType = StreamType.bytes,
    ) -> APIResponse:
        """
        Send a PATCH request.

        :param endpoint: API endpoint
        :type endpoint: str
        :param body: Request body
        :type body: Any | None
        :param query: Query parameters
        :type query: dict | None
        :param headers: Request headers
        :type headers: dict | None
        :param params: Path parameters
        :type params: dict | None
        :param accept: Accept header
        :type accept: list[tuple[str, float]] | None
        :param stream: Stream response content
        :type stream: bool
        :param stream_type: Stream type
        :type stream_type: StreamType
        :return: APIResponse object
        :rtype: APIResponse
        """
        return await self.request(
            "PATCH",
            endpoint,
            body=body,
            query=query,
            headers=headers,
            params=params,
            accept=accept,
            stream=stream,
            stream_type=stream_type,
        )

    async def delete(
        self,
        endpoint: str,
        body: Any | None = None,
        query: dict | None = None,
        headers: dict | None = None,
        params: dict | None = None,
        accept: list[tuple[str, float]] | None = None,
        stream: bool = False,
        stream_type: StreamType = StreamType.bytes,
    ) -> APIResponse:
        """
        Send a DELETE request.

        :param endpoint: API endpoint
        :type endpoint: str
        :param body: Request body
        :type body: Any | None
        :param query: Query parameters
        :type query: dict | None
        :param headers: Request headers
        :type headers: dict | None
        :param params: Path parameters
        :type params: dict | None
        :param accept: Accept header
        :type accept: list[tuple[str, float]] | None
        :param stream: Stream response content
        :type stream: bool
        :param stream_type: Stream type
        :type stream_type: StreamType
        :return: APIResponse object
        :rtype: APIResponse
        """
        return await self.request(
            "DELETE",
            endpoint,
            body=body,
            query=query,
            headers=headers,
            params=params,
            accept=accept,
            stream=stream,
            stream_type=stream_type,
        )
