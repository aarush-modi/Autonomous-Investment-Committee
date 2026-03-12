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
