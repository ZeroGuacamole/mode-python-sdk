from datetime import datetime, timezone
import importlib
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, ValidationInfo, model_validator


class AssetType(str, Enum):
    """Defines the different kinds of financial instruments."""

    STOCK = "STOCK"
    ETF = "ETF"
    OPTION = "OPTION"
    FUTURE = "FUTURE"
    INDEX = "INDEX"
    FOREX = "FOREX"
    CRYPTO = "CRYPTO"
    UNKNOWN = "UNKNOWN"


class StockDetails(BaseModel):
    """Holds information specific to stock assets."""

    sector: Optional[str] = None
    industry: Optional[str] = None


class Asset(BaseModel):
    """Represents the reference data for any financial instrument."""

    symbol: str
    asset_type: AssetType = Field(..., alias="assetType")
    name: str
    exchange: Optional[str] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    identifiers: Optional[Dict[str, str]] = None
    details: Optional[Any] = None
    last_updated: datetime = Field(..., alias="lastUpdated")

    @field_validator("details", mode="after")
    @classmethod
    def validate_details(cls, v: Any, info: ValidationInfo) -> Any:
        """Parse the details field into a specific model based on assetType."""
        if v is None:
            return None

        asset_type = info.data.get("asset_type")

        if asset_type == AssetType.STOCK and isinstance(v, dict):
            return StockDetails.model_validate(v)

        return v

    @field_validator("symbol", mode="after")
    @classmethod
    def normalize_symbol(cls, v: str) -> str:
        """Normalize symbols to uppercase for consistency across models."""
        return v.upper()

    @field_validator("last_updated", mode="after")
    @classmethod
    def normalize_last_updated(cls, v: datetime) -> datetime:
        """Ensure timestamps are timezone-aware and normalized to UTC."""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)


class Quote(BaseModel):
    """Represents a real-time quote for a symbol."""

    symbol: str
    price: float
    timestamp: datetime
    bid: Optional[float] = None
    ask: Optional[float] = None
    volume: Optional[int] = None
    change: Optional[float] = None
    change_percent: Optional[float] = Field(default=None, alias="changePercent")
    day_high: Optional[float] = Field(default=None, alias="dayHigh")
    day_low: Optional[float] = Field(default=None, alias="dayLow")
    previous_close: Optional[float] = Field(default=None, alias="previousClose")
    open: Optional[float] = None

    @field_validator("timestamp", mode="after")
    @classmethod
    def normalize_timestamp(cls, v: datetime) -> datetime:
        """Ensure quote timestamps are timezone-aware (UTC)."""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)

    @model_validator(mode="after")
    def validate_prices(self) -> "Quote":
        """Basic sanity checks for price fields used in backtesting."""
        if self.price is not None and self.price < 0:
            raise ValueError("price must be non-negative")
        if self.bid is not None and self.bid < 0:
            raise ValueError("bid must be non-negative")
        if self.ask is not None and self.ask < 0:
            raise ValueError("ask must be non-negative")
        if self.bid is not None and self.ask is not None and self.ask < self.bid:
            raise ValueError("ask must be greater than or equal to bid")
        return self

    @property
    def mid_price(self) -> float:
        """Return mid price if bid/ask present, otherwise fall back to last price."""
        if self.bid is not None and self.ask is not None:
            return (self.bid + self.ask) / 2.0
        return self.price

    @property
    def spread(self) -> Optional[float]:
        """Return bid/ask spread if available."""
        if self.bid is not None and self.ask is not None:
            return self.ask - self.bid
        return None


class QuoteResponse(BaseModel):
    """Represents the structure of the quotes API response."""

    quotes: Dict[str, Quote]
    errors: Dict[str, str]

    @model_validator(mode="after")
    def validate_quote_keys(self) -> "QuoteResponse":
        """Ensure the mapping keys align with each nested quote's symbol when present."""
        for key, quote in self.quotes.items():
            # Only validate when symbol is present; API may return partials
            if quote.symbol and key.upper() != quote.symbol.upper():
                raise ValueError(
                    f"quotes key '{key}' does not match nested symbol '{quote.symbol}'"
                )
        return self


class HistoricalDataPoint(BaseModel):
    """Represents a single OHLCV data point."""

    timestamp: datetime
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None

    @field_validator("timestamp", mode="after")
    @classmethod
    def normalize_timestamp(cls, v: datetime) -> datetime:
        """Ensure bar timestamps are timezone-aware (UTC)."""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)

    @model_validator(mode="after")
    def validate_ohlcv(self) -> "HistoricalDataPoint":
        """Sanity checks for OHLCV used in backtesting pipelines."""
        # Non-negativity
        for name in ("open", "high", "low", "close"):
            value = getattr(self, name)
            if value is not None and value < 0:
                raise ValueError(f"{name} must be non-negative")
        if self.volume is not None and self.volume < 0:
            raise ValueError("volume must be non-negative")

        # High/low consistency with other provided fields
        candidates_for_high: List[float] = [
            v for v in [self.open, self.close, self.low] if v is not None
        ]
        if (
            self.high is not None
            and candidates_for_high
            and self.high < max(candidates_for_high)
        ):
            raise ValueError("high must be >= max(open, close, low) when provided")
        candidates_for_low: List[float] = [
            v for v in [self.open, self.close, self.high] if v is not None
        ]
        if (
            self.low is not None
            and candidates_for_low
            and self.low > min(candidates_for_low)
        ):
            raise ValueError("low must be <= min(open, close, high) when provided")

        return self


class HistoricalDataResponse(BaseModel):
    """Represents the structure of the historical data API response."""

    symbol: str
    data_points: List[HistoricalDataPoint] = Field(..., alias="dataPoints")

    @field_validator("symbol", mode="after")
    @classmethod
    def normalize_symbol(cls, v: str) -> str:
        return v.upper()

    def to_records(self) -> List[Dict[str, Any]]:
        """Return the historical data as a list of dictionaries."""
        return [
            {
                "timestamp": point.timestamp,
                "open": point.open,
                "high": point.high,
                "low": point.low,
                "close": point.close,
                "volume": point.volume,
            }
            for point in self.data_points
        ]

    def to_dataframe(self):  # type: ignore[override]
        """Convert the historical data to a pandas DataFrame (if pandas is installed).

        Returns a DataFrame indexed by UTC timestamps with columns: open, high, low,
        close, volume. The frame is sorted by index and duplicate timestamps are
        collapsed keeping the last occurrence.
        """
        try:
            pd = importlib.import_module("pandas")
        except Exception as exc:
            raise ImportError(
                "pandas is required for to_dataframe(); install with 'pip install pandas'"
            ) from exc

        records = self.to_records()
        if not records:
            return pd.DataFrame(
                columns=["open", "high", "low", "close", "volume"]
            ).astype(
                {
                    "open": "float64",
                    "high": "float64",
                    "low": "float64",
                    "close": "float64",
                    "volume": "float64",
                }
            )

        frame = pd.DataFrame.from_records(records)
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        frame.set_index("timestamp", inplace=True)
        frame.sort_index(inplace=True)
        frame = frame[~frame.index.duplicated(keep="last")]
        return frame

    def to_numpy(self):  # type: ignore[override]
        """Return numpy arrays (timestamps, open, high, low, close, volume).

        Arrays are suitable for fast vectorized backtests. Requires numpy.
        """
        try:
            np = importlib.import_module("numpy")
        except Exception as exc:
            raise ImportError(
                "numpy is required for to_numpy(); install with 'pip install numpy'"
            ) from exc

        points = self.data_points
        n = len(points)
        ts = np.empty(n, dtype="datetime64[ns]")
        open_ = np.full(n, np.nan)
        high = np.full(n, np.nan)
        low = np.full(n, np.nan)
        close = np.full(n, np.nan)
        vol = np.full(n, np.nan)

        for i, p in enumerate(points):
            dt_utc = p.timestamp.astimezone(timezone.utc).replace(tzinfo=None)
            ts[i] = np.datetime64(dt_utc, "ns")
            if p.open is not None:
                open_[i] = p.open
            if p.high is not None:
                high[i] = p.high
            if p.low is not None:
                low[i] = p.low
            if p.close is not None:
                close[i] = p.close
            if p.volume is not None:
                vol[i] = p.volume

        return ts, open_, high, low, close, vol
