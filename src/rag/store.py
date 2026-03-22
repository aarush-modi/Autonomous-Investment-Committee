import chromadb
from src.rag.embeddings import EmbeddingGenerator


class VectorStore:
    def __init__(self, persist_dir: str = "data/vectorstore", collection_name: str = "filings"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.embedder = EmbeddingGenerator()

    def add(self, doc_id: str, text: str, metadata: dict = None):
        embedding = self.embedder.embed(text)
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata or {}],
        )

    def add_batch(self, doc_ids: list[str], texts: list[str], metadatas: list[dict] = None):
        embeddings = self.embedder.embed_batch(texts)
        self.collection.add(
            ids=doc_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas or [{} for _ in doc_ids],
        )

    def search(self, query: str, n_results: int = 5, where: dict = None) -> list[dict]:
        query_embedding = self.embedder.embed(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
        )

        return [
            {
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            }
            for i in range(len(results["ids"][0]))
        ]

    def count(self) -> int:
        return self.collection.count()
