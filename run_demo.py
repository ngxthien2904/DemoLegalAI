"""
Script khởi chạy Demo Legal AI Chatbot.
Chạy: python run_demo.py
"""
import subprocess, sys, os, io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def check_deps():
    """Kiểm tra dependencies."""
    required = ["flask", "chromadb", "sentence_transformers", "flask_cors"]
    missing = []
    for mod in required:
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)
    if missing:
        print(f"[!] Thiếu thư viện: {missing}")
        print("[*] Đang cài đặt từ requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def main():
    print("=" * 55)
    print("  ⚖️  LEGAL AI CHATBOT DEMO - Luật Chứng khoán VN")
    print("=" * 55)

    # Step 1: Check dependencies
    print("\n[1/4] Kiểm tra dependencies...")
    check_deps()
    print("  ✅ Dependencies OK")

    # Step 2 & 3: (Đã bỏ qua vì chúng ta đã nạp dữ liệu thật bằng raw_ingester.py)
    # print("\n[2/4] Tạo dữ liệu mẫu...")
    # from sample_data import generate_sample_data
    # generate_sample_data()
    # print("\n[3/4] Xây dựng vector index (có thể mất 1-2 phút lần đầu)...")
    # from processing.indexer import build_index
    # build_index()

    # Step 4: Start server
    print("\n[4/4] Khởi động server...")
    from config import GEMINI_API_KEY
    if not GEMINI_API_KEY:
        print("  ⚠️  GEMINI_API_KEY chưa được set!")
        print("  → Chạy: set GEMINI_API_KEY=your_key_here")
        print("  → Demo sẽ chạy ở chế độ offline (chỉ search, không dùng LLM)\n")
    else:
        print("  ✅ Gemini API Key đã cấu hình\n")

    from backend.app import start_server
    start_server()

if __name__ == "__main__":
    main()
