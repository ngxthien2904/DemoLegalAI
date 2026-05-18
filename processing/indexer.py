"""
Indexer: Pipeline đọc dữ liệu -> chunk -> embed -> lưu ChromaDB.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CHROMA_DIR, CHROMA_COLLECTION, SAMPLE_DIR, EMBEDDING_MODEL
from processing.chunker import process_documents


def build_index():
    """Xây dựng index từ dữ liệu mẫu."""
    import chromadb
    from sentence_transformers import SentenceTransformer

    # 1. Đọc dữ liệu
    doc_path = os.path.join(SAMPLE_DIR, "documents.json")
    if not os.path.exists(doc_path):
        print("[!] Chưa có dữ liệu mẫu. Chạy sample_data.py trước.")
        return False

    with open(doc_path, "r", encoding="utf-8") as f:
        documents = json.load(f)
    print(f"[*] Đọc được {len(documents)} văn bản.")

    # 2. Chunking
    print("[*] Đang chia nhỏ văn bản (chunking)...")
    chunks = process_documents(documents)

    # 3. Embedding
    print(f"[*] Đang tải model embedding: {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    texts = [c["text"] for c in chunks]
    print(f"[*] Đang tạo embeddings cho {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=16)

    # 4. Lưu vào ChromaDB
    os.makedirs(CHROMA_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Xóa collection cũ nếu có
    try:
        client.delete_collection(CHROMA_COLLECTION)
    except Exception:
        pass

    collection = client.create_collection(
        name=CHROMA_COLLECTION,
        metadata={"description": "Legal documents - Vietnam Securities Law"}
    )

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [c["metadata"] for c in chunks]

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
    )

    print(f"[+] Đã index {len(chunks)} chunks vào ChromaDB tại {CHROMA_DIR}")
    return True


if __name__ == "__main__":
    build_index()
