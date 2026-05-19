"""
Raw Ingester: Đọc file PDF/DOCX từ thư mục Luật chứng khoán, dùng Gemini để trích xuất metadata,
lưu metadata vào PostgreSQL và vector vào ChromaDB.
"""
import os
import sys
import re
import json
import time
import fitz  # PyMuPDF
from docx import Document as DocxDocument
import chromadb
from sentence_transformers import SentenceTransformer

# Cấu hình encoding cho stdout trên Windows để tránh lỗi Unicode
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CHROMA_DIR, CHROMA_COLLECTION, EMBEDDING_MODEL, BASE_DIR, GEMINI_API_KEY, GEMINI_MODEL
from backend.database import SessionLocal, engine, Base
from backend.models import Document
from processing.chunker import chunk_by_article

# Khởi tạo DB tables
Base.metadata.create_all(bind=engine)

DATA_PATH = os.path.join(BASE_DIR, "Luật chứng khoán")

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
    except Exception as e:
        print(f"Lỗi đọc PDF {pdf_path}: {e}")
    return text

def extract_text_from_docx(docx_path):
    text = ""
    try:
        doc = DocxDocument(docx_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Lỗi đọc DOCX {docx_path}: {e}")
    return text

def parse_metadata_from_filename(filename):
    """Trích xuất sơ bộ số hiệu và loại văn bản từ tên file bằng Regex."""
    loai = "Văn bản"
    so_hieu = "Unknown"
    
    filename_lower = filename.lower()
    
    if "nq" in filename_lower or "nghị quyết" in filename_lower:
        loai = "Nghị quyết"
    elif "nd" in filename_lower or "nđ" in filename_lower or "nghị định" in filename_lower:
        loai = "Nghị định"
    elif "luật" in filename_lower:
        loai = "Luật"
    elif "tt" in filename_lower or "thông tư" in filename_lower:
        loai = "Thông tư"
        
    # Tìm kiếm các mẫu số hiệu như 69.2025 hoặc 155/2020...
    match = re.search(r'(\d+[\./]\d+)', filename)
    if match:
        so_hieu = match.group(1)
        
    return loai, so_hieu

def extract_metadata_with_llm(text_content, filename):
    """Sử dụng Gemini API để trích xuất các cột thông tin bị thiếu từ nội dung văn bản."""
    if not GEMINI_API_KEY:
        print("  [!] Không tìm thấy GEMINI_API_KEY. Bỏ qua bước bóc tách bằng LLM.")
        return "Đang cập nhật", "Đang cập nhật", "Còn hiệu lực"
        
    # Trích xuất 2000 ký tự đầu tiên
    preamble = text_content[:2000]
    
    prompt = f"""Bạn là một chuyên gia phân tích văn bản pháp luật. Hãy phân tích đoạn trích sau từ đầu một văn bản pháp luật Việt Nam (tên file gốc là '{filename}') và trích xuất các thông tin sau dưới dạng JSON cực kỳ ngắn gọn:
1. "co_quan": Tên cơ quan ban hành (ví dụ: "Chính phủ", "Bộ Tài chính", "Quốc hội", "Ủy ban Thường vụ Quốc hội").
2. "ngay_hieu_luc": Ngày có hiệu lực của văn bản (định dạng YYYY-MM-DD, ví dụ: "2021-01-01"). Nếu không tìm thấy ngày hiệu lực cụ thể, hãy cố gắng đoán dựa vào ngày ký hoặc ngày ban hành, nếu không thể đoán được hãy ghi "Đang cập nhật".
3. "tinh_trang": Tình trạng hiệu lực hiện tại của văn bản này. Mặc định ghi "Còn hiệu lực" trừ khi văn bản ghi rõ đã bị thay thế hoặc hết hiệu lực.

Đoạn trích văn bản:
\"\"\"
{preamble}
\"\"\"

Trả về kết quả dưới dạng JSON thuần túy, không có thẻ ```json hay bất kỳ chữ giải thích nào khác. Định dạng bắt buộc:
{{
  "co_quan": "...",
  "ngay_hieu_luc": "...",
  "tinh_trang": "..."
}}
"""
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        
        clean_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)
        
        co_quan = data.get("co_quan", "Đang cập nhật")
        ngay_hieu_luc = data.get("ngay_hieu_luc", "Đang cập nhật")
        tinh_trang = data.get("tinh_trang", "Còn hiệu lực")
        
        return co_quan, ngay_hieu_luc, tinh_trang
    except Exception as e:
        print(f"  [!] Lỗi LLM trích xuất metadata cho {filename}: {e}")
        return "Đang cập nhật", "Đang cập nhật", "Còn hiệu lực"

def ingest_data():
    print("[*] Đang khởi tạo kết nối DB và ChromaDB...")
    db = SessionLocal()
    
    os.makedirs(CHROMA_DIR, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    
    try:
        chroma_client.delete_collection(CHROMA_COLLECTION)
    except Exception:
        pass
    
    collection = chroma_client.create_collection(
        name=CHROMA_COLLECTION,
        metadata={"description": "Legal documents - Vietnam Securities Law"}
    )
    
    print(f"[*] Đang tải model embedding: {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    
    all_chunks = []
    
    # 1. Quét thư mục
    if not os.path.exists(DATA_PATH):
        print(f"[!] Không tìm thấy thư mục {DATA_PATH}")
        return
        
    folders = [f for f in os.listdir(DATA_PATH) if os.path.isdir(os.path.join(DATA_PATH, f))]
    print(f"[*] Tìm thấy {len(folders)} thư mục tài liệu.")
    
    doc_counter = 0
    for folder in folders:
        folder_path = os.path.join(DATA_PATH, folder)
        files = os.listdir(folder_path)
        
        # Ưu tiên PDF, nếu không có thì tìm DOCX
        target_file = None
        for f in files:
            if f.lower().endswith('.pdf'):
                target_file = f
                break
        
        if not target_file:
            for f in files:
                if f.lower().endswith('.docx'):
                    target_file = f
                    break
                    
        if not target_file:
            print(f"  [!] Bỏ qua {folder} vì không tìm thấy file PDF hay DOCX.")
            continue
            
        file_path = os.path.join(folder_path, target_file)
        
        # 2. Đọc nội dung
        if target_file.lower().endswith('.pdf'):
            text_content = extract_text_from_pdf(file_path)
        else:
            text_content = extract_text_from_docx(file_path)
            
        if not text_content.strip():
            print(f"  [!] Cảnh báo: Không trích xuất được text từ {target_file}")
            continue
            
        # 3. Trích xuất metadata bằng Regex và LLM
        loai, so_hieu = parse_metadata_from_filename(target_file)
        doc_id = f"doc_{folder}_{so_hieu}".replace(".", "_").replace("/", "_")
        
        print(f"  [*] Đang xử lý tài liệu: {target_file}...")
        print("      → Đang gọi Gemini bóc tách cơ quan ban hành, ngày hiệu lực...")
        co_quan, ngay_hieu_luc, tinh_trang = extract_metadata_with_llm(text_content, target_file)
        print(f"      ✓ Kết quả: CQ: {co_quan} | Ngày HL: {ngay_hieu_luc} | TT: {tinh_trang}")
        
        # Lệnh Delay: Chờ 4 giây đối với tài khoản Gemini miễn phí để không bị lỗi 429 (Tối đa 15 yêu cầu/phút)
        if GEMINI_API_KEY:
            print("      [Delay] Đang tạm dừng 4 giây để tránh lỗi quá tải API (429 Rate Limit)...")
            time.sleep(4)
        
        # Lưu vào PostgreSQL (Nếu đã có thì cập nhật, chưa có thì tạo mới)
        existing_doc = db.query(Document).filter(Document.doc_id == doc_id).first()
        if not existing_doc:
            new_doc = Document(
                doc_id=doc_id,
                so_hieu=so_hieu,
                ten=target_file,
                loai=loai,
                co_quan=co_quan,
                ngay_hieu_luc=ngay_hieu_luc,
                tinh_trang=tinh_trang,
                file_path=file_path
            )
            db.add(new_doc)
            db.commit()
            db.refresh(new_doc)
            pg_doc_id = new_doc.id
        else:
            existing_doc.co_quan = co_quan
            existing_doc.ngay_hieu_luc = ngay_hieu_luc
            existing_doc.tinh_trang = tinh_trang
            db.commit()
            pg_doc_id = existing_doc.id
            
        # 4. Chunking
        doc_metadata = {
            "doc_id": doc_id,
            "pg_doc_id": pg_doc_id,
            "so_hieu": so_hieu,
            "ten": target_file,
            "loai": loai,
            "co_quan": co_quan,
            "ngay_hieu_luc": ngay_hieu_luc,
            "tinh_trang": tinh_trang,
            "file_path": file_path
        }
        
        chunks = chunk_by_article(text_content, doc_metadata)
        all_chunks.extend(chunks)
        
        doc_counter += 1
        print(f"      ✓ Hoàn tất: {len(chunks)} chunks")
        
    # 5. Embedding và đưa vào ChromaDB
    if not all_chunks:
        print("[!] Không có chunk nào được tạo ra.")
        return
        
    texts = [c["text"] for c in all_chunks]
    metadatas = [c["metadata"] for c in all_chunks]
    ids = [f"{c['metadata']['doc_id']}_chunk_{i}" for i, c in enumerate(all_chunks)]
    
    print(f"\n[*] Đang tạo embeddings cho {len(texts)} chunks (quá trình này có thể mất chút thời gian)...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=16)
    
    print(f"[*] Đang lưu {len(texts)} chunks vào ChromaDB...")
    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
    )
    
    print(f"\n[+] HOÀN THÀNH! Đã nạp thành công {doc_counter} tài liệu.")
    print("[+] Đã tự động cập nhật đầy đủ Metadata vào PostgreSQL và ChromaDB bằng AI.")
    db.close()

if __name__ == "__main__":
    ingest_data()
