from src.core.tool import tool
from src.data.providers.edgar import EdgarProvider

provider = EdgarProvider()


@tool("Searches for SEC filings by ticker and type (e.g. 10-K, 10-Q, 8-K)")
def search_sec_filings(ticker: str, filing_type: str) -> str:
    filings = provider.get_filings(ticker, filing_type, limit=5)

    if not filings:
        return f"No {filing_type} filings found for {ticker}"

    lines = [f"Recent {filing_type} filings for {ticker}:"]
    for f in filings:
        lines.append(f"  {f.filed_date} — {f.description or 'No description'} ({f.url})")
    return "\n".join(lines)


@tool("Gets financial statements (income statement, balance sheet, cash flow) for a company")
def get_financial_statements(ticker: str, period: str) -> str:
    statements = provider.get_financial_statements(ticker, period)

    lines = [f"Financial Statements for {ticker} ({period}):"]

    lines.append("\nIncome Statement:")
    for key, val in list(statements.income_statement.items())[:10]:
        lines.append(f"  {key}: {val}")

    lines.append("\nBalance Sheet:")
    for key, val in list(statements.balance_sheet.items())[:10]:
        lines.append(f"  {key}: {val}")

    lines.append("\nCash Flow:")
    for key, val in list(statements.cash_flow.items())[:10]:
        lines.append(f"  {key}: {val}")

    return "\n".join(lines)
