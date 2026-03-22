import numpy as np
import pandas as pd
from scipy import stats
from src.core.tool import tool
from src.data.providers.yahoo import YahooFinanceProvider
from datetime import date, timedelta

provider = YahooFinanceProvider()


@tool("Calculates daily and annualized returns for a stock over a given period in days")
def calculate_returns(ticker: str, period_days: int) -> str:
    end = date.today()
    start = end - timedelta(days=period_days)
    bars = provider.get_historical(ticker, start, end)

    if len(bars) < 2:
        return f"Not enough data for {ticker}"

    closes = np.array([b.close for b in bars])
    daily_returns = np.diff(closes) / closes[:-1]

    total_return = (closes[-1] - closes[0]) / closes[0]
    avg_daily = np.mean(daily_returns)
    annualized = (1 + avg_daily) ** 252 - 1
    volatility = np.std(daily_returns) * np.sqrt(252)

    return (
        f"Returns for {ticker} (last {period_days} days):\n"
        f"  Total Return: {total_return:.2%}\n"
        f"  Avg Daily Return: {avg_daily:.4%}\n"
        f"  Annualized Return: {annualized:.2%}\n"
        f"  Annualized Volatility: {volatility:.2%}"
    )


@tool("Calculates the correlation between two stocks over a given period in days")
def calculate_correlations(ticker1: str, ticker2: str, period_days: int) -> str:
    end = date.today()
    start = end - timedelta(days=period_days)

    bars1 = provider.get_historical(ticker1, start, end)
    bars2 = provider.get_historical(ticker2, start, end)

    if len(bars1) < 2 or len(bars2) < 2:
        return f"Not enough data to calculate correlation"

    # Align by date
    dates1 = {b.date: b.close for b in bars1}
    dates2 = {b.date: b.close for b in bars2}
    common = sorted(set(dates1.keys()) & set(dates2.keys()))

    if len(common) < 2:
        return "Not enough overlapping dates"

    closes1 = np.array([dates1[d] for d in common])
    closes2 = np.array([dates2[d] for d in common])
    returns1 = np.diff(closes1) / closes1[:-1]
    returns2 = np.diff(closes2) / closes2[:-1]

    corr = np.corrcoef(returns1, returns2)[0, 1]

    return (
        f"Correlation between {ticker1} and {ticker2} (last {period_days} days):\n"
        f"  Pearson Correlation: {corr:.4f}\n"
        f"  Interpretation: {'Strong' if abs(corr) > 0.7 else 'Moderate' if abs(corr) > 0.4 else 'Weak'} "
        f"{'positive' if corr > 0 else 'negative'} correlation"
    )


@tool("Runs a linear regression of one stock's returns against another over a given period in days")
def run_regression(ticker: str, benchmark: str, period_days: int) -> str:
    end = date.today()
    start = end - timedelta(days=period_days)

    bars_stock = provider.get_historical(ticker, start, end)
    bars_bench = provider.get_historical(benchmark, start, end)

    if len(bars_stock) < 2 or len(bars_bench) < 2:
        return "Not enough data to run regression"

    dates_s = {b.date: b.close for b in bars_stock}
    dates_b = {b.date: b.close for b in bars_bench}
    common = sorted(set(dates_s.keys()) & set(dates_b.keys()))

    if len(common) < 2:
        return "Not enough overlapping dates"

    closes_s = np.array([dates_s[d] for d in common])
    closes_b = np.array([dates_b[d] for d in common])
    returns_s = np.diff(closes_s) / closes_s[:-1]
    returns_b = np.diff(closes_b) / closes_b[:-1]

    slope, intercept, r_value, p_value, std_err = stats.linregress(returns_b, returns_s)

    return (
        f"Regression: {ticker} vs {benchmark} (last {period_days} days):\n"
        f"  Beta: {slope:.4f}\n"
        f"  Alpha (daily): {intercept:.6f}\n"
        f"  R-squared: {r_value**2:.4f}\n"
        f"  P-value: {p_value:.6f}\n"
        f"  Std Error: {std_err:.6f}"
    )
