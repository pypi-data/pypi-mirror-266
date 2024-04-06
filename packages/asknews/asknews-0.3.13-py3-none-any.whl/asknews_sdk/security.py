from datetime import datetime, timedelta, timezone
from typing_extensions import TypedDict
from httpx import Request

class TokenInfo(TypedDict):
    access_token: str
    refresh_token: str
    id_token: int
    scope: str
    token_type: str
    expires_in: int


class OAuthToken:
    def __init__(self, token_info: TokenInfo = {}) -> None:  # type: ignore
        self.set_token(token_info)

    def set_token(self, token_info: TokenInfo) -> None:
        self.token_info = token_info
        self._expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=token_info.get("expires_in", 0)
        )

    def reset_token(self):
        self.token_info = TokenInfo()

    def is_expired(self) -> bool:
        if not self.token_info:
            return True
        return datetime.now(timezone.utc) > self._expires_at

    @property
    def access_token(self) -> str:
        if not self.token_info:
            return ""
        return self.token_info["access_token"]


class InjectToken:
    def __init__(self, token: OAuthToken) -> None:
        self.token = token

    def __call__(self, request: Request) -> Request:
        request.headers["Authorization"] = f"Bearer {self.token.access_token}"
        return request
