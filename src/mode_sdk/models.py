from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, ValidationInfo


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


class QuoteResponse(BaseModel):
    """Represents the structure of the quotes API response."""

    quotes: Dict[str, Quote]
    errors: Dict[str, str]


class HistoricalDataPoint(BaseModel):
    """Represents a single OHLCV data point."""

    timestamp: datetime
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None


class HistoricalDataResponse(BaseModel):
    """Represents the structure of the historical data API response."""

    symbol: str
    data_points: List[HistoricalDataPoint] = Field(..., alias="dataPoints")
