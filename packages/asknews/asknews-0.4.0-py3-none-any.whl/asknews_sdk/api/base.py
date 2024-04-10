from asknews_sdk.client import APIClient, AsyncAPIClient

class BaseAPI:
    def __init__(self, client: APIClient | AsyncAPIClient) -> None:
        self.client = client
