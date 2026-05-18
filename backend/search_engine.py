"""
Search Engine: Hybrid search kết hợp semantic + keyword.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CHROMA_DIR, CHROMA_COLLECTION, SEARCH_TOP_K, EMBEDDING_MODEL


class SearchEngine:
    def __init__(self):
        import chromadb
        from sentence_transformers import SentenceTransformer
        self.client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.collection = self.client.get_collection(CHROMA_COLLECTION)
        self.model = SentenceTransformer(EMBEDDING_MODEL)

    def search(self, query, top_k=None):
        """Hybrid search: semantic + metadata filtering."""
        if top_k is None:
            top_k = SEARCH_TOP_K

        # Semantic search
        query_embedding = self.model.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k * 2,  # lấy nhiều hơn để rerank
            include=["documents", "metadatas", "distances"]
        )

        if not results["documents"] or not results["documents"][0]:
            return []

        # Rerank: ưu tiên văn bản còn hiệu lực
        ranked = []
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            distance = results["distances"][0][i]
            score = 1.0 / (1.0 + distance)

            # Boost nếu còn hiệu lực
            if "Còn hiệu lực" in meta.get("tinh_trang", ""):
                score *= 1.2

            # Keyword matching bonus
            query_lower = query.lower()
            if any(kw in doc.lower() for kw in query_lower.split()):
                score *= 1.1

            ranked.append({
                "text": doc,
                "metadata": meta,
                "score": round(score, 4),
            })

        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked[:top_k]
