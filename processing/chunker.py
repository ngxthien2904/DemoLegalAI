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
    """Chia text dài thành các phần nhỏ có overlap, bảo vệ ranh giới từ và câu."""
    if len(text) <= max_size:
        return [text.strip()]
        
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        # Nếu phần còn lại nhỏ hơn max_size, lấy toàn bộ
        if start + max_size >= text_len:
            chunks.append(text[start:].strip())
            break
            
        end = start + max_size
        
        # Tìm ranh giới tốt nhất xung quanh điểm cắt mong muốn (end)
        # Ưu tiên ngắt ở dấu xuống dòng hoặc kết thúc câu (. , ? , !) trong phạm vi khoảng 150 ký tự trước 'end'
        best_break = -1
        search_range = text[max(start, end - 150):end]
        
        # Tìm ranh giới dòng mới hoặc câu
        for marker in ['\n', '. ', '? ', '! ']:
            pos = search_range.rfind(marker)
            if pos != -1:
                # Điều chỉnh vị trí tuyệt đối trong text
                abs_pos = max(start, end - 150) + pos + len(marker)
                if abs_pos > best_break:
                    best_break = abs_pos
        
        # Nếu không tìm thấy dấu câu, tìm khoảng trắng gần nhất
        if best_break == -1:
            pos = search_range.rfind(' ')
            if pos != -1:
                best_break = max(start, end - 150) + pos + 1
                
        # Nếu vẫn không tìm thấy, đành cắt tại 'end'
        if best_break == -1 or best_break <= start:
            best_break = end
            
        chunk = text[start:best_break]
        chunks.append(chunk.strip())
        
        # Lùi lại overlap để bắt đầu chunk tiếp theo, nhưng đảm bảo lùi lại đúng từ
        start = best_break - overlap
        # Điều chỉnh start để không cắt giữa chừng một từ
        if start > 0 and start < text_len:
            # Lùi start về khoảng trắng gần nhất để không cắt từ
            while start > 0 and text[start] != ' ' and text[start] != '\n':
                start -= 1
            start = max(0, start)
            
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
