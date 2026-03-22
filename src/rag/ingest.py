from src.rag.store import VectorStore
from src.rag.chunking import chunk_sec_filing


class IngestionPipeline:
    def __init__(self, store: VectorStore = None):
        self.store = store or VectorStore()

    def ingest(self, text: str, ticker: str, filing_type: str, filed_date: str):
        chunks = chunk_sec_filing(text)

        doc_ids = []
        texts = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            doc_id = f"{ticker}_{filing_type}_{filed_date}_{i}"
            doc_ids.append(doc_id)
            texts.append(chunk["text"])
            metadatas.append({
                "ticker": ticker,
                "filing_type": filing_type,
                "filed_date": filed_date,
                "chunk_index": i,
                "chunk_type": chunk["type"],
            })

        self.store.add_batch(doc_ids, texts, metadatas)
        return len(chunks)
