import os
import requests
from typing import Optional

from .exceptions import APIError, AuthenticationError
from .resources import AssetsResource, MarketDataResource


class ModeAPIClient:
    """
    A Python client for the Mode Trading API.

    This client handles authentication and provides methods to access
    market data endpoints for quotes and historical data.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """
        Initializes the API client.

        Args:
            base_url: The base URL of the Mode API. Can be set via MODE_API_BASE_URL env var.
                      Defaults to 'http://localhost:8080'.
            email: User's email for authentication. Can be set via MODE_API_EMAIL env var.
            password: User's password for authentication. Can be set via MODE_API_PASSWORD env var.

        Raises:
            AuthenticationError: If email or password are not configured.
        """
        self.base_url = (
            base_url or os.getenv("MODE_API_BASE_URL") or "http://localhost:8080"
        ).rstrip("/")

        self.email = email or os.getenv("MODE_API_EMAIL")
        self.password = password or os.getenv("MODE_API_PASSWORD")

        if not self.email or not self.password:
            raise AuthenticationError(
                "Email and password must be provided or set as environment variables."
            )

        self.session = requests.Session()
        self._authenticate()

        # Initialize resource groups
        self.market_data = MarketDataResource(self.session, self.base_url)
        self.assets = AssetsResource(self.session, self.base_url)

    def _authenticate(self) -> None:
        """
        Authenticates with the API to get a JWT access token.

        The token is stored and used for subsequent requests.

        Raises:
            AuthenticationError: If authentication fails due to invalid credentials,
                                 network issues, or an unexpected response.
        """
        auth_url = f"{self.base_url}/api/v1/auth/login"
        payload = {
            "email": self.email,
            "password": self.password,
        }

        try:
            response = self.session.post(auth_url, json=payload)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)

            data = response.json()
            access_token = data.get("accessToken")
            if not access_token:
                raise AuthenticationError(
                    "Authentication failed: accessToken not found in response."
                )

            self.session.headers.update({"Authorization": f"Bearer {access_token}"})

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError(
                    "Authentication failed: Invalid credentials."
                ) from e
            raise APIError(
                status_code=e.response.status_code, message=e.response.text
            ) from e

        except requests.exceptions.RequestException as e:
            raise AuthenticationError(
                f"An error occurred during authentication: {e}"
            ) from e
