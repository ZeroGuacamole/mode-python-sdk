# Mode API Python SDK

A Python SDK for interacting with the Mode API.

## Installation

This SDK is intended for use in a private repository and is not published on PyPI. You can install it directly from your private GitHub repository.

### Using `uv` or `pip`

You will need a GitHub Personal Access Token (PAT) with the `repo` scope to install from a private repository.

```bash
# Replace <YOUR_GITHUB_PAT>, <USERNAME>, and <REPO_NAME> with your details.
pip install git+https://<YOUR_GITHUB_PAT>@github.com/<USERNAME>/<REPO_NAME>.git
```

Or with `uv`:

```bash
uv pip install git+https://<YOUR_GITHUB_PAT>@github.com/<USERNAME>/<REPO_NAME>.git
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

To set up a development environment:

1.  Clone the repository.
2.  Create a virtual environment: `python -m venv .venv`
3.  Activate it: `source .venv/bin/activate`
4.  Install `uv`: `pip install uv`
5.  Install dependencies: `uv pip install -e ".[dev]"`
6.  Run tests: `pytest`
