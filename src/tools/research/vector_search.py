from src.core.tool import tool
from src.rag.store import VectorStore

store = None

def get_store() -> VectorStore:
    global store
    if store is None:
        store = VectorStore()
    return store


@tool("Searches the knowledge base of ingested SEC filings for relevant information")
def search_knowledge_base(query: str, ticker: str) -> str:
    results = get_store.search(query, n_results=5, where={"ticker": ticker})

    if not results:
        return f"No results found for '{query}' related to {ticker}"

    lines = [f"Knowledge base results for '{query}' ({ticker}):"]
    for r in results:
        meta = r["metadata"]
        lines.append(
            f"\n[{meta.get('filing_type', '?')} — {meta.get('filed_date', '?')}]\n"
            f"{r['text'][:500]}"
        )
    return "\n".join(lines)
