from __future__ import annotations

from asknews_sdk.client import APIClient
from asknews_sdk.api import (
    AnalyticsAPI,
    StoriesAPI,
    NewsAPI,
    ChatAPI,
)


class AskNewsSDK:
    """
    The AskNews SDK client for communicating with the AskNews API.

    Usage:

    ```python
    >>> async with AskNewsSDK(client_id=..., client_secret=...) as sdk:
    >>>    stories_response = await sdk.stories.get_stories(...)
    ```

    :param client_id: The client ID for your AskNews API application.
    :type client_id: str
    :param client_secret: The client secret for your AskNews API application.
    :type client_secret: str
    :param scopes: The scopes to request for your AskNews API application.
    :type scopes: set[str] | None
    :param base_url: The base URL for the AskNews API.
    :type base_url: str
    :param token_url: The token URL for the AskNews API.
    :type token_url: str
    :param verify_ssl: Whether or not to verify SSL certificates.
    :type verify_ssl: bool
    :param retries: The number of retries to attempt on connection errors.
    :type retries: int
    :param timeout: The timeout for requests.
    :type timeout: float | None
    """
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scopes: set[str] | None = None,
        base_url: str = "https://api.asknews.app",
        token_url: str = "https://auth.asknews.app/oauth2/token",
        verify_ssl: bool = True,
        retries: int = 3,
        timeout: float | None = None,
    ) -> None:
        self.client = APIClient(
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes,
            base_url=base_url,
            token_url=token_url,
            verify_ssl=verify_ssl,
            retries=retries,
            timeout=timeout,
        )

        self.analytics = AnalyticsAPI(self.client)
        self.stories = StoriesAPI(self.client)
        self.news = NewsAPI(self.client)
        self.chat = ChatAPI(self.client)

    async def __aenter__(self) -> AskNewsSDK:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.client.__aexit__(exc_type, exc, tb)

    async def close(self) -> None:
        """
        Close the SDK client.
        """
        await self.client.close()

    async def ping(self) -> dict:
        """
        Ping the AskNews API and get the version.
        """
        response = await self.client.get("/")
        return response.content

    async def test(self) -> dict:
        response = await self.client.get("/v1/test")
        return response.content
