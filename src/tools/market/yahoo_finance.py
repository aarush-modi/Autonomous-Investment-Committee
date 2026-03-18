from src.core.tool import tool
from src.data.providers.yahoo import YahooFinanceProvider
from datetime import date, timedelta

provider = YahooFinanceProvider()


@tool("Gets the current stock quote including price, volume, market cap, and daily change")
def get_stock_price(ticker: str) -> str:
    quote = provider.get_quote(ticker)
    return (
        f"Ticker: {quote.ticker}\n"
        f"Price: ${quote.price:.2f}\n"
        f"Volume: {quote.volume:,}\n"
        f"Market Cap: ${quote.market_cap:,.0f}\n"
        f"Day Change: ${quote.day_change:.2f} ({quote.day_change_percent:.2f}%)"
    )


@tool("Gets historical daily OHLCV data for a stock. Use YYYY-MM-DD format for dates.")
def get_historical_ohlcv(ticker: str, start_date: str, end_date: str) -> str:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    bars = provider.get_historical(ticker, start, end)

    if not bars:
        return f"No historical data found for {ticker} between {start_date} and {end_date}"

    lines = [f"Historical data for {ticker} ({start_date} to {end_date}):"]
    for bar in bars:
        lines.append(
            f"  {bar.date} | O: ${bar.open:.2f} H: ${bar.high:.2f} "
            f"L: ${bar.low:.2f} C: ${bar.close:.2f} V: {bar.volume:,}"
        )
    return "\n".join(lines)


@tool("Gets current quotes for major market indices: S&P 500, NASDAQ, and Dow Jones")
def get_market_indices() -> str:
    indices = {"S&P 500": "^GSPC", "NASDAQ": "^IXIC", "Dow Jones": "^DJI"}
    lines = []
    for name, symbol in indices.items():
        quote = provider.get_quote(symbol)
        lines.append(
            f"{name}: {quote.price:,.2f} ({quote.day_change_percent:+.2f}%)"
        )
    return "\n".join(lines)
