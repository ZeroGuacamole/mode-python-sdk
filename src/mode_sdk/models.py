from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class Quote(BaseModel):
    """Represents a real-time quote for a symbol."""

    symbol: str
    price: float
    timestamp: datetime


class QuoteResponse(BaseModel):
    """Represents the structure of the quotes API response."""

    quotes: List[Quote]
    errors: dict


class OHLCV(BaseModel):
    """Represents a single OHLCV data point."""

    timestamp: datetime = Field(..., alias="time")
    open: float
    high: float
    low: float
    close: float
    volume: int


class HistoricalDataResponse(BaseModel):
    """Represents the structure of the historical data API response."""

    symbol: str
    data_points: List[OHLCV] = Field(..., alias="dataPoints")
