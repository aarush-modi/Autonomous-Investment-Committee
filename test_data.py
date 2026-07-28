from datetime import date, datetime

import pandas as pd
import pytest

from src.data.models import Quote, OHLCV, FinancialStatements, Filing
from src.data.cache import Cache
from src.data.providers.yahoo import YahooFinanceProvider


class TestModels:
    def test_quote_fields(self):
        quote = Quote(
            ticker="AAPL", price=185.50, volume=50000000, market_cap=2.8e12,
            day_change=1.25, day_change_percent=0.68, timestamp=datetime.now(),
        )
        assert quote.ticker == "AAPL"
        assert quote.price == 185.50

    def test_ohlcv_fields(self):
        ohlcv = OHLCV(date=date(2025, 1, 2), open=180.0, high=186.0, low=179.0, close=185.0, volume=40000000)
        assert ohlcv.close == 185.0

    def test_financial_statements_fields(self):
        fs = FinancialStatements(
            ticker="AAPL", income_statement={"revenue": 100000}, balance_sheet={"total_assets": 500000},
            cash_flow={"free_cash_flow": 30000}, period="annual",
        )
        assert fs.period == "annual"

    def test_filing_fields(self):
        filing = Filing(ticker="AAPL", filing_type="10-K", filed_date=date(2024, 11, 1), url="https://example.com")
        assert filing.filing_type == "10-K"


@pytest.fixture
def cache(tmp_path):
    c = Cache(db_path=str(tmp_path / "test_cache.db"), default_ttl=3600)
    yield c
    c.conn.close()


class TestCache:
    def test_set_then_get_round_trips(self, cache):
        cache.set("test_key", {"price": 185.50})
        assert cache.get("test_key") == {"price": 185.50}

    def test_get_missing_key_returns_none(self, cache):
        assert cache.get("nonexistent") is None

    def test_clear_removes_all_entries(self, cache):
        cache.set("test_key", {"price": 185.50})
        cache.clear()
        assert cache.get("test_key") is None

    def test_expired_entry_returns_none(self, cache):
        cache.set("test_key", {"price": 185.50}, ttl=-1)
        assert cache.get("test_key") is None


@pytest.fixture
def yahoo():
    return YahooFinanceProvider()


class FakeTicker:
    def __init__(self, info=None, history_df=None):
        self.info = info or {}
        self._history_df = history_df

    def history(self, start=None, end=None):
        return self._history_df


class TestYahooFinanceProvider:
    def test_get_quote_maps_fields(self, yahoo, monkeypatch):
        fake_ticker = FakeTicker(info={
            "currentPrice": 185.50,
            "previousClose": 183.00,
            "volume": 50000000,
            "marketCap": 2.8e12,
        })
        monkeypatch.setattr("src.data.providers.yahoo.yf.Ticker", lambda ticker: fake_ticker)

        quote = yahoo.get_quote("AAPL")

        assert quote.ticker == "AAPL"
        assert quote.price == 185.50
        assert quote.day_change == pytest.approx(2.50)

    def test_get_historical_maps_bars(self, yahoo, monkeypatch):
        df = pd.DataFrame(
            {
                "Open": [180.0, 182.0],
                "High": [186.0, 187.0],
                "Low": [179.0, 181.0],
                "Close": [185.0, 186.5],
                "Volume": [40000000, 41000000],
            },
            index=pd.to_datetime(["2025-01-02", "2025-01-03"]),
        )
        fake_ticker = FakeTicker(history_df=df)
        monkeypatch.setattr("src.data.providers.yahoo.yf.Ticker", lambda ticker: fake_ticker)

        bars = yahoo.get_historical("AAPL", date(2025, 1, 1), date(2025, 1, 31))

        assert len(bars) == 2
        assert isinstance(bars[0], OHLCV)
        assert bars[0].close == 185.0
        assert bars[1].volume == 41000000
