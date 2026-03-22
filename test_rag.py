from dotenv import load_dotenv
load_dotenv()

import os
import shutil
from src.rag.embeddings import EmbeddingGenerator
from src.rag.chunking import chunk_sec_filing, recursive_chunk
from src.rag.store import VectorStore
from src.rag.ingest import IngestionPipeline

# --- Test Embeddings ---
embedder = EmbeddingGenerator()
vec = embedder.embed("Apple reported strong revenue growth")
assert len(vec) > 0
assert isinstance(vec[0], float)

batch = embedder.embed_batch(["revenue increased", "debt decreased"])
assert len(batch) == 2
print("✓ Embeddings work")

# --- Test Chunking ---
sample_filing = """
Item 1. Business
Apple Inc. designs and manufactures consumer electronics.

Item 7. Management Discussion and Analysis
Revenue increased 10% year over year driven by iPhone sales.
Services revenue reached an all-time high.

Item 8. Financial Statements
Total revenue was $394 billion for fiscal year 2024.
"""

chunks = chunk_sec_filing(sample_filing)
assert len(chunks) >= 3
assert any("Business" in c["text"] for c in chunks)
print(f"✓ Chunking works ({len(chunks)} chunks)")

# --- Test Recursive Chunking ---
long_text = "Sentence one. " * 200
chunks = recursive_chunk(long_text, max_chunk_size=500)
assert all(len(c["text"]) <= 600 for c in chunks)  # allow small overflow from overlap
print(f"✓ Recursive chunking works ({len(chunks)} chunks)")

# --- Test Vector Store ---
test_dir = "data/test_vectorstore"
store = VectorStore(persist_dir=test_dir, collection_name="test")

store.add("doc1", "Apple revenue grew 10% last quarter", {"ticker": "AAPL"})
store.add("doc2", "Google cloud revenue surpassed expectations", {"ticker": "GOOG"})
store.add("doc3", "Apple services reached all time high", {"ticker": "AAPL"})

assert store.count() == 3

results = store.search("Apple revenue growth", n_results=2, where={"ticker": "AAPL"})
assert len(results) == 2
assert all(r["metadata"]["ticker"] == "AAPL" for r in results)
print("✓ Vector store works")

# --- Test Ingestion Pipeline ---
pipeline = IngestionPipeline(store=store)
num_chunks = pipeline.ingest(
    text=sample_filing,
    ticker="AAPL",
    filing_type="10-K",
    filed_date="2024-11-01",
)
assert num_chunks > 0
assert store.count() > 3
print(f"✓ Ingestion pipeline works ({num_chunks} chunks ingested)")

# Cleanup
shutil.rmtree(test_dir)
print("\nAll RAG tests passed!")
