"""
Flask API Backend cho Legal AI Chatbot.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG, FRONTEND_DIR, SAMPLE_DIR
from backend.search_engine import SearchEngine
from backend.llm_client import ask_llm

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)

# Lazy init search engine
_search_engine = None

def get_engine():
    global _search_engine
    if _search_engine is None:
        _search_engine = SearchEngine()
    return _search_engine


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(FRONTEND_DIR, path)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Câu hỏi không được để trống"}), 400

    try:
        engine = get_engine()
        chunks = engine.search(query)
        result = ask_llm(query, chunks)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/documents")
def documents():
    doc_path = os.path.join(SAMPLE_DIR, "documents.json")
    if not os.path.exists(doc_path):
        return jsonify([])
    with open(doc_path, "r", encoding="utf-8") as f:
        docs = json.load(f)
    summary = [{"id": d["id"], "so_hieu": d["so_hieu"], "ten": d["ten"],
                "loai": d["loai"], "tinh_trang": d["tinh_trang"]} for d in docs]
    return jsonify(summary)


@app.route("/api/graph")
def graph():
    rel_path = os.path.join(SAMPLE_DIR, "relations.json")
    doc_path = os.path.join(SAMPLE_DIR, "documents.json")
    if not os.path.exists(rel_path):
        return jsonify({"nodes": [], "edges": []})
    with open(doc_path, "r", encoding="utf-8") as f:
        docs = json.load(f)
    with open(rel_path, "r", encoding="utf-8") as f:
        rels = json.load(f)

    nodes = [{"id": d["id"], "label": d["so_hieu"], "title": d["ten"],
              "group": d["loai"]} for d in docs]
    edges = [{"from": r["from"], "to": r["to"], "label": r["label"],
              "type": r["type"]} for r in rels]
    return jsonify({"nodes": nodes, "edges": edges})


def start_server():
    print(f"\n{'='*50}")
    print(f"  Legal AI Chatbot Demo")
    print(f"  http://localhost:{FLASK_PORT}")
    print(f"{'='*50}\n")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)


if __name__ == "__main__":
    start_server()
