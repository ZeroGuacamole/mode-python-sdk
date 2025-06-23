import pytest
import requests
import requests_mock

from mode_sdk.client import ModeAPIClient
from mode_sdk.exceptions import AuthenticationError, APIError
from mode_sdk.models import StockDetails

BASE_URL = "http://localhost:8080"
AUTH_URL = f"{BASE_URL}/api/v1/auth/login"


@pytest.fixture
def api_client(requests_mock):
    """Fixture to create an API client with a mocked successful authentication."""
    requests_mock.post(AUTH_URL, json={"accessToken": "test-token"}, status_code=200)
    return ModeAPIClient(
        base_url=BASE_URL, email="test@example.com", password="password"
    )


def test_successful_authentication(requests_mock):
    """Test that the client authenticates successfully and stores the token."""
    requests_mock.post(AUTH_URL, json={"accessToken": "test-token"}, status_code=200)
    client = ModeAPIClient(
        base_url=BASE_URL, email="test@example.com", password="password"
    )
    assert client.session.headers["Authorization"] == "Bearer test-token"


def test_failed_authentication_bad_credentials(requests_mock):
    """Test that AuthenticationError is raised for a 401 Unauthorized status."""
    requests_mock.post(AUTH_URL, status_code=401)
    with pytest.raises(AuthenticationError, match="Invalid credentials"):
        ModeAPIClient(base_url=BASE_URL, email="wrong@example.com", password="wrong")


def test_get_quotes_success(api_client, requests_mock):
    """Test successful fetching of quotes."""
    quotes_url = f"{BASE_URL}/api/v1/market-data/quotes"
    mock_response = {
        "quotes": {
            "AAPL": {
                "symbol": "AAPL",
                "price": 150.0,
                "timestamp": "2023-01-01T12:00:00Z",
                "ask": 150.5,
                "bid": 149.5,
            }
        },
        "errors": {},
    }
    requests_mock.get(quotes_url, json=mock_response, status_code=200)

    response = api_client.market_data.get_quotes(["AAPL"])
    assert response.quotes["AAPL"].symbol == "AAPL"
    assert response.quotes["AAPL"].price == 150.0
    assert response.quotes["AAPL"].ask == 150.5
    assert len(response.errors) == 0


def test_get_quotes_partial_success(api_client, requests_mock):
    """Test fetching quotes where some symbols are found and others return errors."""
    quotes_url = f"{BASE_URL}/api/v1/market-data/quotes"
    mock_response = {
        "quotes": {
            "AAPL": {
                "symbol": "AAPL",
                "price": 150.0,
                "timestamp": "2023-01-01T12:00:00Z",
            }
        },
        "errors": {"GOOG": "Symbol not found"},
    }
    requests_mock.get(quotes_url, json=mock_response, status_code=200)

    response = api_client.market_data.get_quotes(["AAPL", "GOOG"])
    assert response.quotes["AAPL"].symbol == "AAPL"
    assert "GOOG" in response.errors
    assert response.errors["GOOG"] == "Symbol not found"


def test_get_quotes_empty_list(api_client):
    """Test that calling get_quotes with an empty list returns an empty response."""
    response = api_client.market_data.get_quotes([])
    assert response.quotes == {}
    assert response.errors == {}


def test_get_asset_success(api_client, requests_mock):
    """Test successful fetching of asset reference data."""
    symbol = "AAPL"
    asset_url = f"{BASE_URL}/api/v1/assets/{symbol.upper()}"
    mock_response = {
        "symbol": "AAPL",
        "assetType": "STOCK",
        "name": "Apple Inc.",
        "exchange": "NASDAQ",
        "currency": "USD",
        "status": "ACTIVE",
        "lastUpdated": "2023-10-27T10:00:00Z",
        "details": {"sector": "Technology", "industry": "Consumer Electronics"},
    }
    requests_mock.get(asset_url, json=mock_response, status_code=200)

    asset = api_client.assets.get_asset(symbol)

    assert asset.symbol == "AAPL"
    assert asset.asset_type == "STOCK"
    assert asset.name == "Apple Inc."
    assert isinstance(asset.details, StockDetails)
    assert asset.details.sector == "Technology"


def test_get_asset_not_found(api_client, requests_mock):
    """Test that APIError is raised for a 404 Not Found error."""
    symbol = "FAKE"
    asset_url = f"{BASE_URL}/api/v1/assets/{symbol.upper()}"
    requests_mock.get(asset_url, status_code=404, text="Asset not found")

    with pytest.raises(APIError) as excinfo:
        api_client.assets.get_asset(symbol)

    assert excinfo.value.status_code == 404
    assert "Asset not found" in excinfo.value.message


def test_get_historical_data_success(api_client, requests_mock):
    """Test successful fetching of historical data."""
    symbol = "TSLA"
    historical_url = f"{BASE_URL}/api/v1/market-data/historical/{symbol}"
    mock_response = {
        "symbol": "TSLA",
        "dataPoints": [
            {
                "timestamp": "2023-01-01T00:00:00Z",
                "open": 200.0,
                "high": 205.0,
                "low": 199.0,
                "close": 202.0,
                "volume": 1000,
            }
        ],
    }
    requests_mock.get(historical_url, json=mock_response, status_code=200)

    response = api_client.market_data.get_historical_data(
        symbol, "2023-01-01", "2023-01-02", "daily"
    )
    assert response.symbol == "TSLA"
    assert response.data_points[0].open == 200.0
    assert response.data_points[0].timestamp.year == 2023


def test_get_historical_data_with_optional_fields(api_client, requests_mock):
    """Test that historical data with missing optional fields is handled correctly."""
    symbol = "MSFT"
    historical_url = f"{BASE_URL}/api/v1/market-data/historical/{symbol}"
    mock_response = {
        "symbol": "MSFT",
        "dataPoints": [
            {"timestamp": "2023-01-01T00:00:00Z", "close": 300.0, "volume": None}
        ],
    }
    requests_mock.get(historical_url, json=mock_response, status_code=200)

    response = api_client.market_data.get_historical_data(
        symbol, "2023-01-01", "2023-01-02", "daily"
    )
    point = response.data_points[0]
    assert point.close == 300.0
    assert point.open is None
    assert point.high is None
    assert point.volume is None


def test_api_error_on_500(api_client, requests_mock):
    """Test that APIError is raised for a 500 Internal Server Error."""
    quotes_url = f"{BASE_URL}/api/v1/market-data/quotes"
    requests_mock.get(quotes_url, status_code=500, text="Internal Server Error")

    with pytest.raises(APIError) as excinfo:
        api_client.market_data.get_quotes(["AAPL"])

    assert excinfo.value.status_code == 500
    assert "Internal Server Error" in excinfo.value.message


def test_malformed_response_triggers_api_error(api_client, requests_mock):
    """Test that an APIError is raised if the API response is malformed."""
    quotes_url = f"{BASE_URL}/api/v1/market-data/quotes"
    mock_response = {
        "quotes": {
            "AAPL": {
                "symbol": "AAPL",
                "price": "invalid-price",  # Price should be a float
                "timestamp": "2023-01-01T12:00:00Z",
            }
        },
        "errors": {},
    }
    requests_mock.get(quotes_url, json=mock_response, status_code=200)

    with pytest.raises(APIError):
        api_client.market_data.get_quotes(["AAPL"])
