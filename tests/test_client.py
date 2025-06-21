import pytest
import requests
import requests_mock

from mode_sdk.client import ModeAPIClient
from mode_sdk.exceptions import AuthenticationError, APIError

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
    """Test that AuthenticationError is raised for 401 status."""
    requests_mock.post(AUTH_URL, status_code=401)
    with pytest.raises(AuthenticationError, match="Invalid credentials"):
        ModeAPIClient(base_url=BASE_URL, email="wrong@example.com", password="wrong")


def test_get_quotes_success(api_client, requests_mock):
    """Test successful fetching of quotes."""
    quotes_url = f"{BASE_URL}/api/v1/market-data/quotes"
    mock_response = {
        "quotes": [
            {"symbol": "AAPL", "price": 150.0, "timestamp": "2023-01-01T12:00:00Z"}
        ],
        "errors": {},
    }
    requests_mock.get(quotes_url, json=mock_response, status_code=200)

    response = api_client.get_quotes(["AAPL"])
    assert response.quotes[0].symbol == "AAPL"
    assert response.quotes[0].price == 150.0
    assert len(response.errors) == 0


def test_get_historical_data_success(api_client, requests_mock):
    """Test successful fetching of historical data."""
    symbol = "TSLA"
    historical_url = f"{BASE_URL}/api/v1/market-data/historical/{symbol}"
    mock_response = {
        "symbol": "TSLA",
        "dataPoints": [
            {
                "time": "2023-01-01T00:00:00Z",
                "open": 200.0,
                "high": 205.0,
                "low": 199.0,
                "close": 202.0,
                "volume": 1000,
            }
        ],
    }
    requests_mock.get(historical_url, json=mock_response, status_code=200)

    response = api_client.get_historical_data(
        symbol, "2023-01-01", "2023-01-02", "daily"
    )
    assert response.symbol == "TSLA"
    assert response.data_points[0].open == 200.0


def test_api_error_on_500(api_client, requests_mock):
    """Test that APIError is raised for a 500 server error."""
    quotes_url = f"{BASE_URL}/api/v1/market-data/quotes"
    requests_mock.get(quotes_url, status_code=500, text="Internal Server Error")

    with pytest.raises(APIError) as excinfo:
        api_client.get_quotes(["AAPL"])

    assert excinfo.value.status_code == 500
    assert "Internal Server Error" in excinfo.value.message


def test_malformed_response_validation_error(api_client, requests_mock):
    """Test that an APIError is raised if the response is malformed."""
    quotes_url = f"{BASE_URL}/api/v1/market-data/quotes"
    # 'price' is a string instead of a float
    mock_response = {"quotes": [{"symbol": "AAPL", "price": "invalid-price"}]}
    requests_mock.get(quotes_url, json=mock_response, status_code=200)

    with pytest.raises(APIError):
        api_client.get_quotes(["AAPL"])
