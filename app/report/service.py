import os
import json
from typing import List, Dict
from datetime import datetime
from google import genai

from app.schemas import MonthlyReportRequest, MonthlyReportResponse, ReportSections

POSITIVE_KEYWORDS = ["tiến bộ", "tốt", "tích cực", "tự tin", "chăm", "nhanh", "đúng", "cải thiện"]
NEGATIVE_KEYWORDS = ["chậm", "thiếu", "chưa", "sai", "yếu", "quên", "rụt rè", "lẫn", "mất", "khó"]

def _get_gemini_client():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return None
    return genai.Client(api_key=key)

def _days_covered(feedbacks: List[dict]) -> int:
    dates = set()
    for f in feedbacks:
        try:
            dates.add(datetime.strptime(f["date"], "%Y-%m-%d").date())
        except:
            pass
    return len(dates)

def _pick_bullets(feedback_texts: List[str]) -> Dict[str, List[str]]:
    strengths, improvements, highlights = [], [], []

    for t in feedback_texts:
        tl = t.lower()

        if len(highlights) < 3:
            highlights.append(t.strip())

        if any(k in tl for k in POSITIVE_KEYWORDS) and len(strengths) < 5:
            strengths.append(t.strip())

        if any(k in tl for k in NEGATIVE_KEYWORDS) and len(improvements) < 5:
            improvements.append(t.strip())

    if not strengths:
        strengths = ["Học viên duy trì tham gia học đều và có thái độ hợp tác trong lớp."]
    if not improvements:
        improvements = ["Cần tiếp tục luyện tập đều đặn để củng cố kỹ năng và tăng tốc độ phản xạ."]

    return {
        "strengths": strengths[:3],
        "improvements": improvements[:3],
        "highlights": highlights[:3] if highlights else ["Học viên có ghi nhận tích cực trong tháng."]
    }

def _ensure_len(items: List[str], n: int, filler: str) -> List[str]:
    items = [x for x in (items or []) if isinstance(x, str) and x.strip()]
    while len(items) < n:
        items.append(filler)
    return items[:n]

def _extract_json_block(text: str) -> str:
    text = (text or "").strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Gemini did not return JSON.")
    return text[start:end+1]

def _generate_sections_with_gemini(client, name: str, program: str, from_d: str, to_d: str, texts: List[str]) -> dict:
    feedback_block = "\n".join([f"- {t}" for t in texts])

    prompt = f"""
Bạn là giáo viên trung tâm tiếng Anh KidzGo.
Hãy viết báo cáo tháng dựa CHỈ trên các feedback sau buổi học (không bịa thêm).
Nếu thiếu dữ liệu phần nào, ghi rõ: "Chưa đủ dữ liệu để kết luận".

Học viên: {name}
Chương trình: {program}
Khoảng thời gian: {from_d} đến {to_d}

Feedback:
{feedback_block}

Yêu cầu: Trả về DUY NHẤT 1 JSON object theo schema sau (không markdown, không giải thích):
{{
  "overview": "string",
  "strengths": ["...", "...", "..."],
  "improvements": ["...", "...", "..."],
  "highlights": ["...", "..."],
  "goals_next_month": ["...", "...", "..."]
}}

Quy tắc:
- strengths: đúng 3 ý
- improvements: đúng 3 ý (mỗi ý kèm gợi ý luyện tập cụ thể)
- highlights: 2-3 ý
- goals_next_month: đúng 3 ý
"""

    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    raw = (resp.text or "").strip()
    json_str = _extract_json_block(raw)
    return json.loads(json_str)

def generate_monthly_report(req: MonthlyReportRequest) -> MonthlyReportResponse:
    name = req.student.name
    program = req.student.program or ""
    from_d, to_d = req.range.from_date, req.range.to_date

    feedbacks = [{"date": f.date, "text": f.text} for f in req.session_feedbacks]
    texts = [f["text"].strip() for f in feedbacks if f.get("text") and f["text"].strip()]

    total = len(texts)
    covered = _days_covered(feedbacks)
    bullets = _pick_bullets(texts)

    # Base overview/goals (fallback)
    if total == 0:
        overview = f"Trong giai đoạn {from_d} đến {to_d}, hiện chưa có đủ nhận xét sau buổi học để tổng hợp báo cáo."
    else:
        overview = (
            f"Trong giai đoạn {from_d} đến {to_d}, {name} {f'({program})' if program else ''} "
            f"có {total} ghi nhận sau buổi học. Báo cáo này tổng hợp các điểm nổi bật và đề xuất cải thiện "
            f"dựa trên nhận xét của giáo viên."
        )

    goals_next_month = [
        "Duy trì thói quen luyện tập ngắn mỗi ngày (5–10 phút) theo hướng dẫn của giáo viên.",
        "Tập trung 1–2 mục tiêu cụ thể (ví dụ: phát âm âm cuối / tốc độ đọc / từ vựng theo chủ đề).",
        "Hoàn thành bài tập đúng hạn và chủ động hỏi khi chưa hiểu."
    ]

    # ===== Rule-based draft (fallback) =====
    draft_rule = f"""1) Tổng quan:
{overview}

2) Điểm mạnh (tổng hợp từ nhận xét sau buổi học):
- """ + "\n- ".join(bullets["strengths"]) + """

3) Cần cải thiện (gợi ý dựa trên ghi nhận của giáo viên):
- """ + "\n- ".join(bullets["improvements"]) + """

4) Nhận xét tiêu biểu (trích một số ghi nhận):
- """ + "\n- ".join(bullets["highlights"]) + f"""

5) Mục tiêu tháng tới:
- {goals_next_month[0]}
- {goals_next_month[1]}
- {goals_next_month[2]}

6) Thống kê nguồn dữ liệu:
- Số feedback được tổng hợp: {total}
- Số ngày có ghi nhận: {covered}
"""

    sections = ReportSections(
        overview=overview,
        strengths=bullets["strengths"],
        improvements=bullets["improvements"],
        highlights=bullets["highlights"],
        goals_next_month=goals_next_month,
        source_summary={"total_feedbacks": total, "days_covered": covered}
    )

    # ===== Gemini attempt =====
    draft_text = None
    client = _get_gemini_client()

    if total > 0 and client is not None:
        try:
            sec = _generate_sections_with_gemini(client, name, program, from_d, to_d, texts)

            overview_ai = (sec.get("overview") or overview).strip()

            strengths_ai = _ensure_len(sec.get("strengths"), 3, "Học viên có thái độ học tập tích cực.")
            improvements_ai = _ensure_len(sec.get("improvements"), 3, "Cần luyện tập thêm theo hướng dẫn của giáo viên (5–10 phút/ngày).")
            highlights_ai = _ensure_len(sec.get("highlights"), 2, "Có ghi nhận tiến bộ trong tháng.")
            goals_ai = _ensure_len(sec.get("goals_next_month"), 3, "Duy trì luyện tập đều đặn theo kế hoạch.")

            draft_text = f"""1) Tổng quan:
{overview_ai}

2) Điểm mạnh:
- """ + "\n- ".join(strengths_ai) + """

3) Cần cải thiện:
- """ + "\n- ".join(improvements_ai) + """

4) Nhận xét tiêu biểu:
- """ + "\n- ".join(highlights_ai) + f"""

5) Mục tiêu tháng tới:
- {goals_ai[0]}
- {goals_ai[1]}
- {goals_ai[2]}

6) Thống kê nguồn dữ liệu:
- Số feedback được tổng hợp: {total}
- Số ngày có ghi nhận: {covered}
"""

            sections = ReportSections(
                overview=overview_ai,
                strengths=strengths_ai,
                improvements=improvements_ai,
                highlights=highlights_ai,
                goals_next_month=goals_ai,
                source_summary={"total_feedbacks": total, "days_covered": covered}
            )
        except Exception as e:
            import traceback
            print("GEMINI_ERROR:", e)
            print(traceback.format_exc())
            draft_text = None


    if draft_text is None:
        draft_text = draft_rule

    return MonthlyReportResponse(draft_text=draft_text, sections=sections)
