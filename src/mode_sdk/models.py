from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


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
