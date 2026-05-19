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

    def get_graph_context(self, chunks):
        """
        Truy vấn các mối quan hệ liên kết từ Knowledge Graph dựa trên kết quả tìm kiếm ngữ nghĩa.
        Trả về: (graph_context_str, graph_relations_list)
        """
        if not chunks:
            return "", []

        try:
            from sample_data import SAMPLE_DOCS, RELATIONS
            from backend.database import SessionLocal
            from backend.models import Document

            db = SessionLocal()
            
            # Lấy tất cả doc_id đã tìm thấy từ chunks
            retrieved_doc_ids = set()
            for chunk in chunks:
                doc_id = chunk["metadata"].get("doc_id")
                if doc_id:
                    retrieved_doc_ids.add(doc_id)

            if not retrieved_doc_ids:
                db.close()
                return "", []

            # Bản đồ ánh xạ:
            # - ID mẫu (ví dụ: LUAT_CK_2019) -> Số hiệu chuẩn (ví dụ: 54/2019/QH14)
            id_to_sohieu = {d["id"]: d["so_hieu"] for d in SAMPLE_DOCS}
            
            # Lấy tất cả văn bản từ PostgreSQL
            all_docs = db.query(Document).all()
            docid_to_sohieu = {d.doc_id: d.so_hieu for d in all_docs}
            sohieu_to_ten = {d.so_hieu: d.ten for d in all_docs}
            db.close()

            # Quét qua RELATIONS để tìm các liên kết liên quan đến retrieved_doc_ids
            context_lines = []
            relations_list = []
            
            for r in RELATIONS:
                from_sohieu = id_to_sohieu.get(r["from"])
                to_sohieu = id_to_sohieu.get(r["to"])

                if not from_sohieu or not to_sohieu:
                    continue

                # Kiểm tra xem có liên quan tới các văn bản trong chunks tìm được hay không
                from_match = False
                to_match = False
                
                for doc_id in retrieved_doc_ids:
                    doc_sohieu = docid_to_sohieu.get(doc_id)
                    if doc_sohieu:
                        if doc_sohieu.lower() == from_sohieu.lower():
                            from_match = True
                        if doc_sohieu.lower() == to_sohieu.lower():
                            to_match = True

                if from_match or to_match:
                    from_name = sohieu_to_ten.get(from_sohieu, from_sohieu)
                    to_name = sohieu_to_ten.get(to_sohieu, to_sohieu)
                    rel_type = r["label"] # Hướng dẫn, Sửa đổi, Chi tiết hóa...
                    
                    context_lines.append(
                        f"- Văn bản `{from_name}` (Số hiệu: {from_sohieu}) [{rel_type}] cho văn bản `{to_name}` (Số hiệu: {to_sohieu})."
                    )
                    relations_list.append(
                        f"{from_sohieu} [{rel_type}] {to_sohieu}"
                    )

            # Khử trùng lặp
            context_lines = list(set(context_lines))
            relations_list = list(set(relations_list))

            if context_lines:
                graph_context_str = "\nCác mối quan hệ liên kết pháp lý trích xuất từ Đồ thị Kiến thức (Knowledge Graph):\n"
                graph_context_str += "\n".join(context_lines)
                return graph_context_str, relations_list

            return "", []

        except Exception as e:
            print(f"[!] Lỗi truy vấn Graph Query: {e}")
            return "", []
