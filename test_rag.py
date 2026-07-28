import pytest

from src.rag.chunking import chunk_sec_filing, recursive_chunk

SAMPLE_FILING = """
Item 1. Business
Apple Inc. designs and manufactures consumer electronics.

Item 7. Management Discussion and Analysis
Revenue increased 10% year over year driven by iPhone sales.
Services revenue reached an all-time high.

Item 8. Financial Statements
Total revenue was $394 billion for fiscal year 2024.
"""


class TestChunkSecFiling:
    def test_splits_on_item_sections(self):
        chunks = chunk_sec_filing(SAMPLE_FILING)
        assert len(chunks) >= 3
        assert any("Business" in c["text"] for c in chunks)


class TestRecursiveChunk:
    def test_splits_long_text_within_size_budget(self):
        long_text = "Sentence one. " * 200
        chunks = recursive_chunk(long_text, max_chunk_size=500)
        # allow small overflow from overlap
        assert all(len(c["text"]) <= 600 for c in chunks)

    def test_short_text_returns_single_chunk(self):
        chunks = recursive_chunk("short text", max_chunk_size=500)
        assert len(chunks) == 1
        assert chunks[0]["text"] == "short text"


# The tests below exercise sentence-transformers and ChromaDB, which download
# and load a real embedding model on first run. Skip with `pytest -m "not integration"`
# in environments without network access or model weights cached.
@pytest.mark.integration
class TestEmbeddings:
    def test_embed_returns_a_float_vector(self):
        from src.rag.embeddings import EmbeddingGenerator

        embedder = EmbeddingGenerator()
        vec = embedder.embed("Apple reported strong revenue growth")

        assert len(vec) > 0
        assert isinstance(vec[0], float)

    def test_embed_batch_returns_one_vector_per_text(self):
        from src.rag.embeddings import EmbeddingGenerator

        embedder = EmbeddingGenerator()
        batch = embedder.embed_batch(["revenue increased", "debt decreased"])

        assert len(batch) == 2


@pytest.mark.integration
class TestVectorStore:
    @pytest.fixture
    def store(self, tmp_path):
        from src.rag.store import VectorStore

        return VectorStore(persist_dir=str(tmp_path / "vectorstore"), collection_name="test")

    def test_add_and_count(self, store):
        store.add("doc1", "Apple revenue grew 10% last quarter", {"ticker": "AAPL"})
        store.add("doc2", "Google cloud revenue surpassed expectations", {"ticker": "GOOG"})
        store.add("doc3", "Apple services reached all time high", {"ticker": "AAPL"})

        assert store.count() == 3

    def test_search_filters_by_metadata(self, store):
        store.add("doc1", "Apple revenue grew 10% last quarter", {"ticker": "AAPL"})
        store.add("doc2", "Google cloud revenue surpassed expectations", {"ticker": "GOOG"})
        store.add("doc3", "Apple services reached all time high", {"ticker": "AAPL"})

        results = store.search("Apple revenue growth", n_results=2, where={"ticker": "AAPL"})

        assert len(results) == 2
        assert all(r["metadata"]["ticker"] == "AAPL" for r in results)


@pytest.mark.integration
class TestIngestionPipeline:
    def test_ingest_chunks_and_stores_them(self, tmp_path):
        from src.rag.store import VectorStore
        from src.rag.ingest import IngestionPipeline

        store = VectorStore(persist_dir=str(tmp_path / "vectorstore"), collection_name="test")
        pipeline = IngestionPipeline(store=store)

        num_chunks = pipeline.ingest(
            text=SAMPLE_FILING,
            ticker="AAPL",
            filing_type="10-K",
            filed_date="2024-11-01",
        )

        assert num_chunks > 0
        assert store.count() == num_chunks
