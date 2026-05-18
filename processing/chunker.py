"""
Chunker: Chia văn bản pháp luật thành các chunk theo điều khoản.
"""
import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_by_article(text, doc_metadata):
    """Chia văn bản theo Điều (Article-level chunking)."""
    pattern = r'(Điều\s+\d+[^\.]*\..*?)(?=Điều\s+\d+|$)'
    articles = re.findall(pattern, text, re.DOTALL)

    chunks = []
    if articles:
        for art in articles:
            art = art.strip()
            if len(art) < 20:
                continue
            # Nếu điều quá dài, chia nhỏ thêm
            if len(art) > CHUNK_SIZE:
                sub_chunks = split_long_text(art, CHUNK_SIZE, CHUNK_OVERLAP)
                for i, sc in enumerate(sub_chunks):
                    chunks.append({
                        "text": sc,
                        "metadata": {**doc_metadata, "chunk_type": "article_part", "part": i}
                    })
            else:
                chunks.append({
                    "text": art,
                    "metadata": {**doc_metadata, "chunk_type": "article"}
                })
    else:
        # Không tìm thấy cấu trúc Điều -> chunk theo kích thước
        sub_chunks = split_long_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        for i, sc in enumerate(sub_chunks):
            chunks.append({
                "text": sc,
                "metadata": {**doc_metadata, "chunk_type": "paragraph", "part": i}
            })
    return chunks


def split_long_text(text, max_size, overlap):
    """Chia text dài thành các phần nhỏ có overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
    return [c for c in chunks if c]


def process_documents(documents):
    """Xử lý danh sách documents thành chunks."""
    all_chunks = []
    for doc in documents:
        meta = {
            "doc_id": doc["id"],
            "so_hieu": doc["so_hieu"],
            "ten": doc["ten"],
            "loai": doc["loai"],
            "co_quan": doc["co_quan"],
            "ngay_hieu_luc": doc["ngay_hieu_luc"],
            "tinh_trang": doc["tinh_trang"],
        }
        chunks = chunk_by_article(doc["noi_dung"], meta)
        all_chunks.extend(chunks)
        print(f"  [{doc['id']}] -> {len(chunks)} chunks")
    print(f"[+] Tổng cộng: {len(all_chunks)} chunks từ {len(documents)} văn bản.")
    return all_chunks
