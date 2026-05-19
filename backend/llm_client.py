"""
LLM Client: Gọi Google Gemini API để tổng hợp câu trả lời.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GEMINI_API_KEY, GEMINI_MODEL

SYSTEM_PROMPT = """Bạn là trợ lý pháp lý AI chuyên về luật chứng khoán Việt Nam.
Quy tắc:
1. CHỈ trả lời dựa trên ngữ cảnh được cung cấp. Không bịa thông tin.
2. Luôn trích dẫn nguồn (số hiệu văn bản, điều khoản cụ thể).
3. Nếu không tìm thấy thông tin, hãy nói rõ.
4. Trả lời bằng tiếng Việt, ngắn gọn, dễ hiểu.
5. Nếu thông tin có thể đã thay đổi, cảnh báo người dùng kiểm tra lại."""


def ask_llm(query, context_chunks, graph_context=""):
    """Gửi câu hỏi + context tới Gemini API."""
    context_parts = []
    for i, chunk in enumerate(context_chunks, 1):
        meta = chunk["metadata"]
        context_parts.append(
            f"[Nguồn {i}] {meta.get('ten', '')} ({meta.get('so_hieu', '')})\n"
            f"Hiệu lực: {meta.get('tinh_trang', 'N/A')}\n"
            f"Nội dung:\n{chunk['text']}\n"
        )
    context = "\n---\n".join(context_parts)

    prompt = f"""Ngữ cảnh pháp lý:
{context}
{graph_context}

Câu hỏi của người dùng: {query}

Hãy trả lời dựa trên ngữ cảnh trên, trích dẫn nguồn rõ ràng."""

    if not GEMINI_API_KEY:
        return _fallback_response(query, context_chunks)

    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
        )
        return {
            "answer": response.text,
            "sources": _extract_sources(context_chunks),
            "mode": "gemini"
        }
    except Exception as e:
        print(f"[!] Gemini API error: {e}")
        return _fallback_response(query, context_chunks)


def _fallback_response(query, chunks):
    """Fallback khi không có API key hoặc lỗi."""
    parts = ["**Kết quả tìm kiếm** (chế độ offline - không sử dụng LLM):\n"]
    for i, chunk in enumerate(chunks, 1):
        meta = chunk["metadata"]
        parts.append(
            f"**{i}. {meta.get('ten', '')}** ({meta.get('so_hieu', '')})\n"
            f"- Hiệu lực: {meta.get('tinh_trang', 'N/A')}\n"
            f"- Nội dung: {chunk['text']}\n"
        )
    return {
        "answer": "\n".join(parts),
        "sources": _extract_sources(chunks),
        "mode": "fallback"
    }


def _extract_sources(chunks):
    """Trích xuất danh sách nguồn."""
    seen = set()
    sources = []
    for c in chunks:
        meta = c["metadata"]
        key = meta.get("doc_id", "")
        if key not in seen:
            seen.add(key)
            sources.append({
                "so_hieu": meta.get("so_hieu", ""),
                "ten": meta.get("ten", ""),
                "tinh_trang": meta.get("tinh_trang", ""),
            })
    return sources
