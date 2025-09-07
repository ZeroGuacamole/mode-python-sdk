from datetime import datetime, timezone
import importlib.util

import pytest
from pydantic import ValidationError

from mode_sdk.models import (
    Asset,
    AssetType,
    StockDetails,
    Quote,
    QuoteResponse,
    HistoricalDataPoint,
    HistoricalDataResponse,
)


def test_asset_normalization_and_details_parsing():
    payload = {
        "symbol": "aapl",
        "assetType": "STOCK",
        "name": "Apple Inc.",
        "lastUpdated": "2023-10-27T10:00:00",  # naive timestamp
        "details": {"sector": "Technology", "industry": "Consumer Electronics"},
    }

    asset = Asset.model_validate(payload)
    assert asset.symbol == "AAPL"
    assert asset.asset_type == AssetType.STOCK
    assert isinstance(asset.details, StockDetails)
    assert asset.last_updated.tzinfo is not None
    assert asset.last_updated.tzinfo == timezone.utc


def test_quote_validations_and_convenience():
    q = Quote.model_validate(
        {
            "symbol": "msft",
            "price": 10.25,
            "timestamp": datetime(2024, 1, 1, 12, 0, 0),  # naive
            "bid": 10.0,
            "ask": 10.5,
        }
    )
    assert (
        q.symbol == "msft"
    )  # Quote.symbol isn't normalized to upper; key matching handles mapping
    assert q.mid_price == pytest.approx(10.25)
    assert q.spread == pytest.approx(0.5)
    assert q.timestamp.tzinfo == timezone.utc

    with pytest.raises(ValidationError):
        Quote.model_validate(
            {
                "symbol": "MSFT",
                "price": -1.0,
                "timestamp": datetime.now(timezone.utc),
            }
        )

    with pytest.raises(ValidationError):
        Quote.model_validate(
            {
                "symbol": "MSFT",
                "price": 10.0,
                "bid": 10.5,
                "ask": 10.0,
                "timestamp": datetime.now(timezone.utc),
            }
        )


def test_quote_response_key_symbol_mismatch():
    with pytest.raises(ValidationError):
        QuoteResponse.model_validate(
            {
                "quotes": {
                    "AAPL": {
                        "symbol": "MSFT",
                        "price": 1.0,
                        "timestamp": "2024-01-01T00:00:00Z",
                    }
                },
                "errors": {},
            }
        )


def test_historical_datapoint_validators_and_normalization():
    ok = HistoricalDataPoint.model_validate(
        {
            "timestamp": datetime(2024, 1, 1, 0, 0, 0),
            "open": 100.0,
            "high": 110.0,
            "low": 90.0,
            "close": 105.0,
            "volume": 100,
        }
    )
    assert ok.timestamp.tzinfo == timezone.utc

    with pytest.raises(ValidationError):
        HistoricalDataPoint.model_validate(
            {
                "timestamp": "2024-01-01T00:00:00Z",
                "open": 100.0,
                "high": 100.0,
                "low": 90.0,
                "close": 101.0,
            }
        )

    with pytest.raises(ValidationError):
        HistoricalDataPoint.model_validate(
            {
                "timestamp": "2024-01-01T00:00:00Z",
                "open": 100.0,
                "high": 110.0,
                "low": 101.0,
                "close": 105.0,
            }
        )

    with pytest.raises(ValidationError):
        HistoricalDataPoint.model_validate(
            {
                "timestamp": "2024-01-01T00:00:00Z",
                "open": 100.0,
                "high": 110.0,
                "low": 90.0,
                "close": 105.0,
                "volume": -1,
            }
        )


def test_historical_data_response_exports():
    resp = HistoricalDataResponse.model_validate(
        {
            "symbol": "spy",
            "dataPoints": [
                {
                    "timestamp": "2024-01-01T00:00:00Z",
                    "open": 100.0,
                    "high": 110.0,
                    "low": 90.0,
                    "close": 105.0,
                    "volume": 1000,
                },
                {
                    "timestamp": "2024-01-02T00:00:00Z",
                    "open": 106.0,
                    "high": 112.0,
                    "low": 101.0,
                    "close": 110.0,
                    "volume": 1500,
                },
            ],
        }
    )

    recs = resp.to_records()
    assert isinstance(recs, list) and len(recs) == 2
    assert set(recs[0].keys()) == {
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
    }

    # to_dataframe: pass in both environments (with/without pandas)
    if importlib.util.find_spec("pandas") is not None:
        df = resp.to_dataframe()
        assert list(df.columns) == ["open", "high", "low", "close", "volume"]
        assert df.index.tz is not None
    else:
        with pytest.raises(ImportError):
            resp.to_dataframe()

    # to_numpy: pass in both environments (with/without numpy)
    if importlib.util.find_spec("numpy") is not None:
        ts, o, h, low, c, v = resp.to_numpy()
        assert len(ts) == len(o) == len(h) == len(low) == len(c) == len(v) == 2
    else:
        with pytest.raises(ImportError):
            resp.to_numpy()
