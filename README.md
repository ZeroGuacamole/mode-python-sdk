# Mode API Python SDK

A Python SDK for interacting with the Mode API.

## Installation

You can install it directly from the GitHub repository.

### Using `pip`

```bash
pip install git+https://github.com/ZeroGuacamole/mode-python-sdk.git
```

Install with backtesting helpers (pandas/numpy) via extras:

```bash
pip install "git+https://github.com/ZeroGuacamole/mode-python-sdk.git#egg=mode-sdk[backtest]"
```

## Quickstart

Here's a quick example of how to use the client to fetch historical data.

### 1. Configuration

The client can be configured via environment variables. Create a `.env` file in your project root:

```
MODE_API_BASE_URL="http://localhost:8080" # Optional, defaults to this
MODE_API_EMAIL="your_email@example.com"
MODE_API_PASSWORD="your_secret_password"
```

### 2. Example Usage

```python
import os
from dotenv import load_dotenv
from mode_sdk.client import ModeAPIClient
from mode_sdk.exceptions import ModeAPIError

# Load environment variables from .env
load_dotenv()

try:
    # Initialize the client. It will automatically use environment variables.
    client = ModeAPIClient()

    # Fetch historical data for a symbol
    symbol = "AAPL"
    historical_data = client.market_data.get_historical_data(
        symbol=symbol,
        start_time="2023-01-01",
        end_time="2023-12-31",
        interval="daily"
    )

    print(f"Successfully fetched {len(historical_data.data_points)} data points for {symbol}.")

    for point in historical_data.data_points:
        print(f"Date: {point.timestamp.date()}, Close: {point.close}")

except ModeAPIError as e:
    print(f"An API error occurred: {e}")

```

### Helpers

The models include utilities commonly used in research/backtesting pipelines.

1. Convert historical data to a pandas DataFrame (UTC index):

```python
from mode_sdk.client import ModeAPIClient

client = ModeAPIClient()
hist = client.market_data.get_historical_data("AAPL", "2024-01-01", "2024-01-31", "daily")

# Requires: pip install pandas
df = hist.to_dataframe()
print(df.head())
```

2. Convert historical data to NumPy arrays for vectorized processing:

```python
# Requires: pip install numpy
ts, open_, high, low, close, volume = hist.to_numpy()
```

3. Quote convenience properties:

```python
quotes = client.market_data.get_quotes(["AAPL"]).quotes
q = quotes["AAPL"]
print(q.mid_price, q.spread)
```

### Data validation and normalization

- Symbols are normalized to uppercase in `Asset` and `HistoricalDataResponse`.
- Timestamps are normalized to UTC in all models that include time fields.
- OHLCV values are validated (non-negative; high/low consistency) for `HistoricalDataPoint`.
- `Quote` validation ensures non-negative prices and `ask >= bid` when both are present.

## Development

1.  Clone the repository.
2.  Create a virtual environment:
    ```bash
    uv venv
    ```
3.  Activate the virtual environment:
    ```bash
    source .venv/bin/activate
    ```
4.  Install dependencies:
    ```bash
    uv pip install -e ".[dev]"
    ```
5.  Run tests:
    ```bash
    pytest
    ```
