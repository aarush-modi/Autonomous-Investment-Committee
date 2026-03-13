from pydantic import BaseModel
from datetime import datetime,date

class Quote(BaseModel):
    ticker: str
    price: float
    volume: int
    market_cap: float
    day_change: float
    day_change_percent: float
    timestamp: datetime


class OHLCV(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


class FinancialStatements(BaseModel):
    ticker: str
    income_statement: dict
    balance_sheet: dict
    cash_flow: dict
    period: str  # "annual" or "quarterly"


class Filing(BaseModel):
    ticker: str
    filing_type: str  # "10-K", "10-Q", "8-K", etc.
    filed_date: date
    url: str
    description: str = ""
