from pydantic import BaseModel


class EnhanceFeedbackRequest(BaseModel):
    draft: str
    language: str = "vi"


class EnhanceFeedbackResponse(BaseModel):
    enhanced: str


def enhance_feedback(draft: str, language: str = "vi") -> str:
    if not draft or not draft.strip():
        return draft

    prompt = f"""Ban la chuyen gia giao duc. Hay chinh sua doan feedback sau theo phong cach formal, ro rang, tich cuc va phu hop de giao vien su dung gui cho hoc sinh/phu huynh. Giup cau truc lai cau tu neu can de feedback de hieu, chuyen nghiep va de ap dung trong thuc te.

Feedback: {draft}

Enhanced:"""

    from app.core.gemini_client import get_gemini_client

    client = get_gemini_client()
    if not client:
        return _simple_enhance(draft)

    try:
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        enhanced = (resp.text or "").strip()
        if enhanced.startswith('"') and enhanced.endswith('"'):
            enhanced = enhanced[1:-1]
        return enhanced if enhanced else draft
    except Exception as e:
        print(f"Error: {e}")
        return _simple_enhance(draft)


def _simple_enhance(draft: str) -> str:
    replacements = {
        "hôm nay": "trong buổi học",
        "em": "học sinh",
        "tốt lắm": "có tiến bộ",
        "lắm": "cao",
        "làm bài": "hoàn thành bài tập",
        "đầy đủ": "đầy đủ các nội dung được giao",
        "chăm chỉ": "thể hiện sự chăm chỉ trong học tập",
        "học tốt": "có kết quả học tập tốt",
        "ngoan": "có thái độ học tập tích cực",
    }

    result = draft
    for old, new in replacements.items():
        result = result.replace(old, new)

    if not result.endswith(".") and not result.endswith("!") and not result.endswith("?"):
        result += "."

    return result


def enhance_feedback_api(req: EnhanceFeedbackRequest) -> EnhanceFeedbackResponse:
    enhanced = enhance_feedback(req.draft, req.language)
    return EnhanceFeedbackResponse(enhanced=enhanced)