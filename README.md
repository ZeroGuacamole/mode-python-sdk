# Mode API Python SDK

A Python SDK for interacting with the Mode API.

## Installation

You can install it directly from the GitHub repository.

### Using `uv` or `pip`

```bash
pip install git+https://github.com/ZeroGuacamole/mode-python-sdk.git
```

Or with `uv`:

```bash
uv pip install git+https://github.com/ZeroGuacamole/mode-python-sdk.git
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
    historical_data = client.get_historical_data(
        symbol=symbol,
        start_time="2023-01-01",
        end_time="2023-12-31",
        interval="daily"
    )

    print(f"Successfully fetched {len(historical_data.data_points)} data points for {symbol}.")

    # The data is a Pydantic model, so you can access it with autocomplete
    for point in historical_data.data_points:
        print(f"Date: {point.timestamp.date()}, Close: {point.close}")

except ModeAPIError as e:
    print(f"An API error occurred: {e}")

```

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
