from app.core.gemini_client import get_gemini_client
from app.core.utils import safe_json_loads, ensure_list_len

def analyze_transcript(context, transcript: str):
    client = get_gemini_client()
    if not client:
        return {
            "ai_used": False,
            "result": {
                "transcript": transcript,
                "overall_score": 0,
                "pronunciation_score": 0,
                "fluency_score": 0,
                "accuracy_score": 0,
                "phonics_issues": [],
                "speaking_issues": [],
                "suggestions": [],
                "practice_plan": [],
                "confidence": {},
                "raw_text": None,
                "warnings": ["Missing GEMINI_API_KEY"]
            }
        }

    prompt = f"""
Bạn là giáo viên KidzGo chấm Speaking/Phonics.
Dựa trên transcript (và target words/expected text nếu có), hãy:
- Chấm điểm phát âm, độ trôi chảy, độ chính xác (0-10)
- Liệt kê lỗi phonics (nếu mode=phonics) hoặc lỗi speaking (nếu mode=speaking)
- Gợi ý luyện tập cụ thể (drill, shadowing, minimal pairs, đọc âm cuối...)
Không bịa dữ liệu không có.

Trả về DUY NHẤT 1 JSON object:
{{
  "transcript": "string",
  "overall_score": number,
  "pronunciation_score": number,
  "fluency_score": number,
  "accuracy_score": number,
  "phonics_issues": ["..."],
  "speaking_issues": ["..."],
  "suggestions": ["..."],
  "practice_plan": ["..."],
  "confidence": {{"transcript": 0.0, "scoring": 0.0}},
  "warnings": ["..."]
}}

Context:
- Mode: {context.mode}
- Target words: {context.target_words}
- Expected text: {context.expected_text or "N/A"}
- Instructions: {context.instructions or "N/A"}

Transcript:
{transcript}

Ngôn ngữ phản hồi: {context.language}
"""

    try:
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        obj = safe_json_loads(resp.text or "")

        suggestions = ensure_list_len(obj.get("suggestions"), 3, "Luyện tập 5–10 phút mỗi ngày theo hướng dẫn.")
        practice_plan = ensure_list_len(obj.get("practice_plan"), 3, "Shadowing 3–5 phút/ngày với câu ngắn.")

        return {
            "ai_used": True,
            "result": {
                "transcript": (obj.get("transcript") or transcript).strip(),
                "overall_score": float(obj.get("overall_score", 0)),
                "pronunciation_score": float(obj.get("pronunciation_score", 0)),
                "fluency_score": float(obj.get("fluency_score", 0)),
                "accuracy_score": float(obj.get("accuracy_score", 0)),
                "phonics_issues": (obj.get("phonics_issues") or [])[:8],
                "speaking_issues": (obj.get("speaking_issues") or [])[:8],
                "suggestions": suggestions,
                "practice_plan": practice_plan,
                "confidence": obj.get("confidence") or {},
                "raw_text": resp.text,
                "warnings": obj.get("warnings") or []
            }
        }
    except Exception as e:
        return {
            "ai_used": False,
            "result": {
                "transcript": transcript,
                "overall_score": 0,
                "pronunciation_score": 0,
                "fluency_score": 0,
                "accuracy_score": 0,
                "phonics_issues": [],
                "speaking_issues": [],
                "suggestions": ["AI lỗi, vui lòng thử lại."],
                "practice_plan": [],
                "confidence": {},
                "raw_text": None,
                "warnings": [f"AI failed: {type(e).__name__}: {str(e)}"]
            }
        }

def analyze_media_bytes(context, media_bytes: bytes, mime_type: str):
    """
    Demo nhanh: gửi thẳng audio/video cho Gemini để vừa transcript vừa chấm.
    Nếu model không hỗ trợ mime_type này, sẽ fallback ai_used=false.
    """
    client = get_gemini_client()
    if not client:
        return {
            "ai_used": False,
            "result": {
                "transcript": "",
                "overall_score": 0,
                "pronunciation_score": 0,
                "fluency_score": 0,
                "accuracy_score": 0,
                "phonics_issues": [],
                "speaking_issues": [],
                "suggestions": [],
                "practice_plan": [],
                "confidence": {},
                "raw_text": None,
                "warnings": ["Missing GEMINI_API_KEY"]
            }
        }

    prompt = f"""
Bạn là giáo viên KidzGo. File đính kèm là audio/video học sinh luyện nói/phonics.
Hãy:
1) Tạo transcript ngắn gọn (tiếng Anh nếu học sinh nói tiếng Anh)
2) Chấm và feedback theo context

Trả về DUY NHẤT 1 JSON object theo schema giống analyze_transcript.

Context:
- Mode: {context.mode}
- Target words: {context.target_words}
- Expected text: {context.expected_text or "N/A"}
- Instructions: {context.instructions or "N/A"}
Ngôn ngữ phản hồi: {context.language}
"""

    try:
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                {"inline_data": {"mime_type": mime_type or "video/mp4", "data": media_bytes}},
            ],
        )
        obj = safe_json_loads(resp.text or "")
        # reuse normalize
        return analyze_transcript(context, obj.get("transcript") or "")
    except Exception as e:
        return {
            "ai_used": False,
            "result": {
                "transcript": "",
                "overall_score": 0,
                "pronunciation_score": 0,
                "fluency_score": 0,
                "accuracy_score": 0,
                "phonics_issues": [],
                "speaking_issues": [],
                "suggestions": ["Model có thể không hỗ trợ audio/video trực tiếp. Hãy dùng endpoint analyze-transcript (ASR trước)."],
                "practice_plan": [],
                "confidence": {},
                "raw_text": None,
                "warnings": [f"AI media failed: {type(e).__name__}: {str(e)}"]
            }
        }
