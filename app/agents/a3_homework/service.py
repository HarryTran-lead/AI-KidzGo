from app.core.gemini_client import get_gemini_client
from app.core.utils import safe_json_loads, ensure_list_len

def _build_prompt(context, student_answer_text: str, expected_answer_text: str | None, language: str) -> str:
    rubric = context.rubric or """
Chấm theo thang 10:
- Đúng nội dung/đúng yêu cầu (4)
- Ngữ pháp/chính tả (3)
- Từ vựng/diễn đạt (2)
- Trình bày/độ rõ ràng (1)
"""
    return f"""
Bạn là giáo viên KidzGo. Hãy chấm bài dựa trên rubric và hướng dẫn bài. Không bịa.
Trả về DUY NHẤT 1 JSON object (không markdown, không giải thích) theo schema:

{{
  "score": number,
  "max_score": 10,
  "summary": "string",
  "strengths": ["..."],
  "issues": ["..."],
  "suggestions": ["..."],
  "extracted_student_answer": "string|null",
  "confidence": {{"score": 0.0, "extraction": 0.0}},
  "warnings": ["..."]
}}

Bối cảnh:
- HomeworkId: {context.homework_id}
- StudentId: {context.student_id}
- Skill: {context.skill}
- Instructions: {context.instructions or "N/A"}

Rubric:
{rubric}

Đáp án chuẩn (nếu có):
{expected_answer_text or "N/A"}

Bài làm học sinh (text):
{student_answer_text}

Ngôn ngữ phản hồi: {language} (vi là tiếng Việt).
"""

def grade_text(context, student_answer_text: str, expected_answer_text: str | None, language: str):
    client = get_gemini_client()
    if not client:
        return {
            "ai_used": False,
            "result": {
                "score": 0,
                "max_score": 10,
                "summary": "Thiếu GEMINI_API_KEY trong process server.",
                "strengths": [],
                "issues": [],
                "suggestions": [],
                "extracted_student_answer": student_answer_text[:2000],
                "confidence": {},
                "raw_text": None,
                "warnings": ["Missing GEMINI_API_KEY"]
            }
        }

    prompt = _build_prompt(context, student_answer_text, expected_answer_text, language)

    try:
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        obj = safe_json_loads(resp.text or "")

        strengths = ensure_list_len(obj.get("strengths"), 2, "Có cố gắng hoàn thành bài.")
        issues = ensure_list_len(obj.get("issues"), 2, "Cần luyện tập thêm theo hướng dẫn.")
        suggestions = ensure_list_len(obj.get("suggestions"), 3, "Luyện tập thêm 5–10 phút/ngày.")

        result = {
            "score": float(obj.get("score", 0)),
            "max_score": float(obj.get("max_score", 10)),
            "summary": (obj.get("summary") or "").strip(),
            "strengths": strengths,
            "issues": issues,
            "suggestions": suggestions,
            "extracted_student_answer": obj.get("extracted_student_answer") or student_answer_text,
            "confidence": obj.get("confidence") or {},
            "raw_text": resp.text,
            "warnings": obj.get("warnings") or []
        }
        return {"ai_used": True, "result": result}

    except Exception as e:
        return {
            "ai_used": False,
            "result": {
                "score": 0,
                "max_score": 10,
                "summary": "AI chấm bài lỗi, hệ thống đang fallback.",
                "strengths": [],
                "issues": [],
                "suggestions": ["Vui lòng thử lại hoặc giáo viên chấm thủ công."],
                "extracted_student_answer": student_answer_text[:2000],
                "confidence": {},
                "raw_text": None,
                "warnings": [f"AI failed: {type(e).__name__}: {str(e)}"]
            }
        }

def grade_image(context, image_bytes: bytes, mime_type: str, expected_answer_text: str | None, language: str):
    client = get_gemini_client()
    if not client:
        return {
            "ai_used": False,
            "result": {
                "score": 0,
                "max_score": 10,
                "summary": "Thiếu GEMINI_API_KEY trong process server.",
                "strengths": [],
                "issues": [],
                "suggestions": [],
                "extracted_student_answer": None,
                "confidence": {},
                "raw_text": None,
                "warnings": ["Missing GEMINI_API_KEY"]
            }
        }

    rubric = context.rubric or """
Chấm theo thang 10:
- Đúng nội dung/đúng yêu cầu (4)
- Ngữ pháp/chính tả (3)
- Từ vựng/diễn đạt (2)
- Trình bày/độ rõ ràng (1)
"""

    prompt = f"""
Bạn là giáo viên KidzGo. Ảnh là bài làm học sinh.
Hãy: (1) trích nội dung bài làm (OCR) (2) chấm theo rubric.
Không bịa phần không nhìn thấy rõ.

Trả về DUY NHẤT 1 JSON:
{{
  "score": number,
  "max_score": 10,
  "summary": "string",
  "strengths": ["..."],
  "issues": ["..."],
  "suggestions": ["..."],
  "extracted_student_answer": "string|null",
  "confidence": {{"score": 0.0, "extraction": 0.0}},
  "warnings": ["..."]
}}

Bối cảnh:
- Skill: {context.skill}
- Instructions: {context.instructions or "N/A"}

Rubric:
{rubric}

Đáp án chuẩn (nếu có):
{expected_answer_text or "N/A"}

Ngôn ngữ phản hồi: {language}
"""

    try:
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                {"inline_data": {"mime_type": mime_type or "image/jpeg", "data": image_bytes}},
            ],
        )
        obj = safe_json_loads(resp.text or "")

        strengths = ensure_list_len(obj.get("strengths"), 2, "Có cố gắng hoàn thành bài.")
        issues = ensure_list_len(obj.get("issues"), 2, "Cần luyện tập thêm theo hướng dẫn.")
        suggestions = ensure_list_len(obj.get("suggestions"), 3, "Luyện tập thêm 5–10 phút/ngày.")

        result = {
            "score": float(obj.get("score", 0)),
            "max_score": float(obj.get("max_score", 10)),
            "summary": (obj.get("summary") or "").strip(),
            "strengths": strengths,
            "issues": issues,
            "suggestions": suggestions,
            "extracted_student_answer": obj.get("extracted_student_answer"),
            "confidence": obj.get("confidence") or {},
            "raw_text": resp.text,
            "warnings": obj.get("warnings") or []
        }
        return {"ai_used": True, "result": result}

    except Exception as e:
        return {
            "ai_used": False,
            "result": {
                "score": 0,
                "max_score": 10,
                "summary": "AI chấm bài ảnh lỗi, fallback.",
                "strengths": [],
                "issues": [],
                "suggestions": ["Giáo viên chấm thủ công hoặc thử lại với ảnh rõ hơn."],
                "extracted_student_answer": None,
                "confidence": {},
                "raw_text": None,
                "warnings": [f"AI failed: {type(e).__name__}: {str(e)}"]
            }
        }
