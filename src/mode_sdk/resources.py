import requests
from typing import List

from .exceptions import APIError
from .models import HistoricalDataResponse, QuoteResponse


class MarketDataResource:
    """
    Handles market data endpoints.
    """

    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url

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
            return QuoteResponse(quotes={}, errors={})

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
