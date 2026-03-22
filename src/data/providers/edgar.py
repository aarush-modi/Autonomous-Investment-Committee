from edgar import Company
from datetime import date
from src.data.providers.base import FilingsProvider
from src.data.models import Filing, FinancialStatements


class EdgarProvider(FilingsProvider):
    def get_filings(self, ticker: str, filing_type: str, limit: int = 5) -> list[Filing]:
        company = Company(ticker)
        filings = company.get_filings(form=filing_type).latest(limit)

        results = []
        for filing in filings:
            results.append(Filing(
                ticker=ticker,
                filing_type=filing_type,
                filed_date=date.fromisoformat(str(filing.filing_date)),
                url=filing.homepage_url,
                description=filing.description or "",
            ))
        return results

    def get_financial_statements(self, ticker: str, period: str = "annual") -> FinancialStatements:
        company = Company(ticker)
        filing = company.get_filings(form="10-K" if period == "annual" else "10-Q").latest(1)[0]
        financials = filing.obj()

        return FinancialStatements(
            ticker=ticker,
            income_statement=self._extract_statement(financials, "income"),
            balance_sheet=self._extract_statement(financials, "balance"),
            cash_flow=self._extract_statement(financials, "cash"),
            period=period,
        )

    def get_filing_text(self, ticker: str, filing_type: str) -> str:
        company = Company(ticker)
        filing = company.get_filings(form=filing_type).latest(1)[0]
        return filing.text()

    def _extract_statement(self, financials, statement_type: str) -> dict:
        try:
            if statement_type == "income":
                return financials.income_statement.to_dict()
            elif statement_type == "balance":
                return financials.balance_sheet.to_dict()
            elif statement_type == "cash":
                return financials.cash_flow_statement.to_dict()
        except (AttributeError, Exception):
            return {}
        return {}
