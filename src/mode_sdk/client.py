import os
import requests
from typing import List, Optional

from .exceptions import APIError, AuthenticationError
from .models import HistoricalDataResponse, QuoteResponse


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

    def get_quotes(self, symbols: List[str]) -> QuoteResponse:
        """
        Fetches real-time quotes for a list of symbols.

        Args:
            symbols: A list of ticker symbols (e.g., ['AAPL', 'GOOG']).

        Returns:
            A QuoteResponse object containing quotes and any errors.

        Raises:
            APIError: If the API returns an error or the response is malformed.
        """
        if not symbols:
            return QuoteResponse(quotes=[], errors={})

        quotes_url = f"{self.base_url}/api/v1/market-data/quotes"
        params = {"symbols": ",".join(symbols)}

        try:
            response = self.session.get(quotes_url, params=params)
            response.raise_for_status()
            return QuoteResponse.model_validate(response.json())
        except requests.exceptions.HTTPError as e:
            raise APIError(
                status_code=e.response.status_code, message=e.response.text
            ) from e
        except Exception as e:
            raise APIError(
                status_code=500, message=f"An error occurred while fetching quotes: {e}"
            ) from e

    def get_historical_data(
        self, symbol: str, start_time: str, end_time: str, interval: str
    ) -> HistoricalDataResponse:
        """
        Fetches historical OHLCV data for a single symbol.

        Args:
            symbol: The ticker symbol (e.g., 'AAPL').
            start_time: The start date in 'YYYY-MM-DD' format.
            end_time: The end date in 'YYYY-MM-DD' format.
            interval: The data interval (e.g., 'daily', '1min').

        Returns:
            A HistoricalDataResponse object containing the historical data.

        Raises:
            APIError: If the API returns an error or the response is malformed.
        """
        historical_url = (
            f"{self.base_url}/api/v1/market-data/historical/{symbol.upper()}"
        )
        params = {
            "startTime": start_time,
            "endTime": end_time,
            "interval": interval,
        }

        try:
            response = self.session.get(historical_url, params=params)
            response.raise_for_status()
            return HistoricalDataResponse.model_validate(response.json())
        except requests.exceptions.HTTPError as e:
            raise APIError(
                status_code=e.response.status_code, message=e.response.text
            ) from e
        except Exception as e:
            raise APIError(
                status_code=500,
                message=f"An error occurred while fetching historical data: {e}",
            ) from e
