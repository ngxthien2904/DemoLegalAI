"""
Cấu hình tập trung cho hệ thống Demo Legal AI Chatbot.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SAMPLE_DIR = os.path.join(DATA_DIR, "sample")
RAW_DIR = os.path.join(DATA_DIR, "raw")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma_db")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"

EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
CHROMA_COLLECTION = "legal_documents"

SEARCH_TOP_K = 5
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True
