from abc import ABC, abstractmethod
from datetime import date
from src.data.models import Quote, OHLCV, FinancialStatements, Filing


class MarketDataProvider(ABC):
    @abstractmethod
    def get_quote(self, ticker: str) -> Quote:
        pass

    @abstractmethod
    def get_historical(self, ticker: str, start: date, end: date) -> list[OHLCV]:
        pass


class EconomicDataProvider(ABC):
    @abstractmethod
    def get_series(self, series_id: str, start: date, end: date) -> dict:
        pass


class FilingsProvider(ABC):
    @abstractmethod
    def get_filings(self, ticker: str, filing_type: str, limit: int = 5) -> list[Filing]:
        pass

    @abstractmethod
    def get_financial_statements(self, ticker: str, period: str = "annual") -> FinancialStatements:
        pass
