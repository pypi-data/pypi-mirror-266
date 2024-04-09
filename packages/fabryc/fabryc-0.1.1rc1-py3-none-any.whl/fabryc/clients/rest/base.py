import requests

from fabryc.auth import get_token


class BaseRestClient:
    """
    Base class for REST API clients.
    """

    base_url: str
    timeout: int = 60

    def __init__(self, token: str | None = None):
        self.headers = {
            "authorization": f"Bearer {token or get_token()}",
            "Accept": "application/json",
        }

    def request(
        self, method: str, endpoint: str, params: dict | None = None, *args, **kwargs
    ):
        """
        Request to the given endpoint REST API.
        """
        url = f"{self.base_url}{endpoint}"

        return requests.request(
            method,
            url=url,
            headers=self.headers,
            timeout=self.timeout,
            params=params,
            *args,
            **kwargs,
        )

    def get(self, endpoint: str, params: dict | None = None):
        """
        POST request to the given endpoint REST API.
        """
        return self.request("GET", endpoint, params=params)

    def post(self, endpoint: str, payload: dict):
        """
        POST request to the given endpoint REST API.
        """
        return self.request("POST", endpoint, json=payload)
