import numpy as np
from scipy import stats
from src.core.tool import tool
from src.data.providers.yahoo import YahooFinanceProvider
from datetime import date, timedelta

provider = YahooFinanceProvider()


def _get_returns(ticker: str, period_days: int) -> np.ndarray:
    end = date.today()
    start = end - timedelta(days=period_days)
    bars = provider.get_historical(ticker, start, end)
    closes = np.array([b.close for b in bars])
    return np.diff(closes) / closes[:-1]


@tool("Calculates Value at Risk for a stock. Confidence level as decimal (e.g. 0.95)")
def calculate_var(ticker: str, period_days: int, confidence: float) -> str:
    returns = _get_returns(ticker, period_days)

    if len(returns) < 2:
        return f"Not enough data for {ticker}"

    # Historical VaR
    historical_var = np.percentile(returns, (1 - confidence) * 100)

    # Parametric VaR
    mean = np.mean(returns)
    std = np.std(returns)
    z_score = stats.norm.ppf(1 - confidence)
    parametric_var = mean + z_score * std

    return (
        f"Value at Risk for {ticker} (last {period_days} days, {confidence:.0%} confidence):\n"
        f"  Historical VaR: {historical_var:.4%} daily\n"
        f"  Parametric VaR: {parametric_var:.4%} daily\n"
        f"  Interpretation: On a bad day, you could lose at least {abs(historical_var):.2%} of your position"
    )


@tool("Calculates the Sharpe ratio for a stock. Uses risk-free rate as decimal (e.g. 0.05 for 5%)")
def calculate_sharpe_ratio(ticker: str, period_days: int, risk_free_rate: float) -> str:
    returns = _get_returns(ticker, period_days)

    if len(returns) < 2:
        return f"Not enough data for {ticker}"

    daily_rf = risk_free_rate / 252
    excess_returns = returns - daily_rf
    sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)

    if sharpe > 2:
        quality = "Excellent"
    elif sharpe > 1:
        quality = "Good"
    elif sharpe > 0:
        quality = "Below average"
    else:
        quality = "Poor"

    return (
        f"Sharpe Ratio for {ticker} (last {period_days} days):\n"
        f"  Sharpe Ratio: {sharpe:.4f}\n"
        f"  Risk-Free Rate: {risk_free_rate:.2%}\n"
        f"  Quality: {quality}"
    )


@tool("Calculates the maximum drawdown for a stock over a given period in days")
def calculate_max_drawdown(ticker: str, period_days: int) -> str:
    end = date.today()
    start = end - timedelta(days=period_days)
    bars = provider.get_historical(ticker, start, end)

    if len(bars) < 2:
        return f"Not enough data for {ticker}"

    closes = np.array([b.close for b in bars])
    dates = [b.date for b in bars]
    peak = np.maximum.accumulate(closes)
    drawdown = (closes - peak) / peak

    max_dd = np.min(drawdown)
    max_dd_idx = np.argmin(drawdown)
    peak_idx = np.argmax(closes[:max_dd_idx + 1]) if max_dd_idx > 0 else 0

    return (
        f"Max Drawdown for {ticker} (last {period_days} days):\n"
        f"  Max Drawdown: {max_dd:.2%}\n"
        f"  Peak: ${closes[peak_idx]:.2f} ({dates[peak_idx]})\n"
        f"  Trough: ${closes[max_dd_idx]:.2f} ({dates[max_dd_idx]})\n"
        f"  Recovery needed: {abs(max_dd) / (1 + max_dd):.2%}"
    )
