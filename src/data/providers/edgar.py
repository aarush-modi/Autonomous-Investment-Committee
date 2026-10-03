import edgar
edgar.set_identity("AutonomousInvestmentCommittee research@example.com")

from edgar import Company
from datetime import date
from src.data.providers.base import FilingsProvider
from src.data.models import Filing, FinancialStatements
from src.data.cache import cached


class EdgarProvider(FilingsProvider):
    @cached("filings", ttl=86400, model_name=list[Filing])
    def get_filings(self, ticker: str, filing_type: str, limit: int = 5) -> list[Filing]:
        company = Company(ticker)
        filings = company.get_filings(form=filing_type)

        # latest(1) returns a single object, latest(n>1) returns a collection
        if limit == 1:
            latest = [filings.latest(1)]
        else:
            latest = list(filings.latest(limit))

        results = []
        for filing in latest:
            results.append(Filing(
                ticker=ticker,
                filing_type=filing_type,
                filed_date=date.fromisoformat(str(filing.filing_date)),
                url=filing.homepage_url,
                description=f"{filing.company} {filing.form}",
            ))
        return results

    @cached("financials", ttl=86400, model_name=FinancialStatements)
    def get_financial_statements(self, ticker: str, period: str = "annual") -> FinancialStatements:
        company = Company(ticker)
        form = "10-K" if period == "annual" else "10-Q"
        filing = company.get_filings(form=form).latest(1)
        obj = filing.data_object()

        return FinancialStatements(
            ticker=ticker,
            income_statement=self._extract_statement(obj, "income"),
            balance_sheet=self._extract_statement(obj, "balance"),
            cash_flow=self._extract_statement(obj, "cash"),
            period=period,
        )

    @cached("filing_text", ttl=604800, model_name=str)
    def get_filing_text(self, ticker: str, filing_type: str) -> str:
        company = Company(ticker)
        filing = company.get_filings(form=filing_type).latest(1)
        doc = filing.document
        return doc.text() if doc else ""

    def _extract_statement(self, obj, statement_type: str) -> dict:
        try:
            if statement_type == "income":
                return obj.income_statement.to_dict()
            elif statement_type == "balance":
                return obj.balance_sheet.to_dict()
            elif statement_type == "cash":
                return obj.cash_flow_statement.to_dict()
        except (AttributeError, Exception):
            return {}
        return {}
