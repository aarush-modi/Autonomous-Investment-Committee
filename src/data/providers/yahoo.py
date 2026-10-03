import yfinance as yf
from datetime import date, datetime
from src.data.providers.base import MarketDataProvider
from src.data.models import Quote, OHLCV
from src.data.cache import cached


class YahooFinanceProvider(MarketDataProvider):
    @cached("quote", ttl=300, model_name=Quote)
    def get_quote(self, ticker: str) -> Quote:
        stock = yf.Ticker(ticker)
        info = stock.info
        price = info.get("currentPrice", info.get("regularMarketPrice", 0.0))
        previous_close = info.get("previousClose", price)
        day_change = price - previous_close

        return Quote(
            ticker=ticker,
            price=price,
            volume=info.get("volume", 0),
            market_cap=info.get("marketCap", 0.0),
            day_change=day_change,
            day_change_percent=(day_change / previous_close * 100) if previous_close else 0.0,
            timestamp=datetime.now(),
        )

    @cached("historical", ttl=3600, model_name=list[OHLCV])
    def get_historical(self, ticker: str, start: date, end: date) -> list[OHLCV]:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start.isoformat(), end=end.isoformat())

        return [
            OHLCV(
                date=row.Index.date(),
                open=row.Open,
                high=row.High,
                low=row.Low,
                close=row.Close,
                volume=int(row.Volume),
            )
            for row in df.itertuples()
        ]
