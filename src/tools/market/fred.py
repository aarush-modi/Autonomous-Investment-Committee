from src.core.tool import tool
from src.data.providers.fred import FredProvider
from datetime import date, timedelta

provider = FredProvider()

COMMON_SERIES = {
    "inflation": "CPIAUCSL",
    "unemployment": "UNRATE",
    "fed_funds_rate": "FEDFUNDS",
    "gdp": "GDP",
    "consumer_sentiment": "UMCSENT",
    "treasury_10y": "DGS10",
    "treasury_2y": "DGS2",
}


@tool("Gets an economic indicator from FRED. Common indicators: inflation, unemployment, fed_funds_rate, gdp, consumer_sentiment, treasury_10y, treasury_2y")
def get_economic_indicators(indicator: str) -> str:
    series_id = COMMON_SERIES.get(indicator.lower(), indicator)
    end = date.today()
    start = end - timedelta(days=365)

    data = provider.get_series(series_id, start, end)
    values = list(data["data"].items())

    if not values:
        return f"No data found for {indicator}"

    latest_date, latest_val = values[-1]
    first_date, first_val = values[0]
    change = latest_val - first_val

    lines = [
        f"{data['title']} ({series_id}):",
        f"  Latest: {latest_val:.2f} ({latest_date})",
        f"  1Y ago: {first_val:.2f} ({first_date})",
        f"  Change: {change:+.2f}",
        f"\nRecent values:",
    ]
    for d, v in values[-5:]:
        lines.append(f"  {d}: {v:.2f}")

    return "\n".join(lines)


@tool("Gets insider transactions (buys/sells) for a stock from SEC filings")
def get_insider_transactions(ticker: str) -> str:
    import yfinance as yf
    stock = yf.Ticker(ticker)
    transactions = stock.insider_transactions

    if transactions is None or transactions.empty:
        return f"No insider transactions found for {ticker}"

    lines = [f"Recent insider transactions for {ticker}:"]
    for _, row in transactions.head(10).iterrows():
        lines.append(
            f"  {row.get('Start Date', 'N/A')} | {row.get('Insider', 'Unknown')} | "
            f"{row.get('Transaction', 'N/A')} | {row.get('Shares', 'N/A')} shares"
        )
    return "\n".join(lines)
