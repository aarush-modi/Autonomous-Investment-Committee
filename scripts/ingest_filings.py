import argparse
from src.data.providers.edgar import EdgarProvider
from src.rag.ingest import IngestionPipeline

provider = EdgarProvider()
pipeline = IngestionPipeline()


def ingest(ticker: str, filing_type: str, limit: int):
    filings = provider.get_filings(ticker, filing_type, limit=limit)
    print(f"Found {len(filings)} {filing_type} filings for {ticker}")

    for filing in filings:
        print(f"  Ingesting {filing.filing_type} filed {filing.filed_date}...")
        text = provider.get_filing_text(ticker, filing_type)
        chunks = pipeline.ingest(
            text=text,
            ticker=ticker,
            filing_type=filing_type,
            filed_date=str(filing.filed_date),
        )
        print(f"    Created {chunks} chunks")

    print(f"Done. Total documents in store: {pipeline.store.count()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest SEC filings into the knowledge base")
    parser.add_argument("--ticker", required=True, help="Stock ticker (e.g. AAPL)")
    parser.add_argument("--filing-type", default="10-K", help="Filing type (default: 10-K)")
    parser.add_argument("--limit", type=int, default=3, help="Number of filings to ingest (default: 3)")
    args = parser.parse_args()

    ingest(args.ticker, args.filing_type, args.limit)
