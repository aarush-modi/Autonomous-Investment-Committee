from datetime import date, datetime
from src.data.models import Quote, OHLCV, FinancialStatements, Filing
from src.data.cache import Cache
from src.data.providers.yahoo import YahooFinanceProvider
import os

# --- Test Models ---
quote = Quote(
    ticker="AAPL", price=185.50, volume=50000000, market_cap=2.8e12,
    day_change=1.25, day_change_percent=0.68, timestamp=datetime.now(),
)
assert quote.ticker == "AAPL"
assert quote.price == 185.50

ohlcv = OHLCV(date=date(2025, 1, 2), open=180.0, high=186.0, low=179.0, close=185.0, volume=40000000)
assert ohlcv.close == 185.0

fs = FinancialStatements(
    ticker="AAPL", income_statement={"revenue": 100000}, balance_sheet={"total_assets": 500000},
    cash_flow={"free_cash_flow": 30000}, period="annual",
)
assert fs.period == "annual"

filing = Filing(ticker="AAPL", filing_type="10-K", filed_date=date(2024, 11, 1), url="https://example.com")
assert filing.filing_type == "10-K"
print("✓ Models work")

# --- Test Cache ---
cache = Cache(db_path="test_cache.db", default_ttl=5)
cache.set("test_key", {"price": 185.50})
assert cache.get("test_key") == {"price": 185.50}
assert cache.get("nonexistent") is None
cache.clear()
assert cache.get("test_key") is None
os.remove("test_cache.db")
print("✓ Cache works")

# --- Test Yahoo Provider (hits free API) ---
yahoo = YahooFinanceProvider()

quote = yahoo.get_quote("AAPL")
assert quote.ticker == "AAPL"
assert quote.price > 0
print(f"  AAPL quote: ${quote.price}, volume: {quote.volume}")

history = yahoo.get_historical("AAPL", date(2025, 1, 1), date(2025, 1, 31))
assert len(history) > 0
assert isinstance(history[0], OHLCV)
print(f"  Historical bars: {len(history)}")
print("✓ Yahoo provider works")
