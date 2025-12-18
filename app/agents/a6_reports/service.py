from typing import List, Dict, Any
from app.core.gemini_client import get_gemini_client
from app.core.utils import safe_json_loads, ensure_list_len

POSITIVE = ["tiến bộ", "tốt", "tích cực", "tự tin", "chăm", "nhanh", "đúng", "cải thiện"]
NEGATIVE = ["chậm", "thiếu", "chưa", "sai", "yếu", "quên", "rụt rè", "lẫn", "khó"]

def _rule_based_sections(texts: List[str]) -> Dict[str, Any]:
    strengths, improvements, highlights = [], [], []
    for t in texts:
        tl = t.lower()
        if len(highlights) < 3:
            highlights.append(t.strip())
        if any(k in tl for k in POSITIVE) and len(strengths) < 3:
            strengths.append(t.strip())
        if any(k in tl for k in NEGATIVE) and len(improvements) < 3:
            improvements.append(t.strip())

    if not strengths:
        strengths = ["Học viên duy trì tham gia học đều và có thái độ hợp tác trong lớp."]
    if not improvements:
        improvements = ["Cần tiếp tục luyện tập đều đặn để củng cố kỹ năng và tăng tốc độ phản xạ."]

    return {
        "overview": "",
        "strengths": strengths[:3],
        "improvements": improvements[:3],
        "highlights": highlights[:3] if highlights else ["Có ghi nhận tiến bộ trong tháng."],
        "goals_next_month": [
            "Duy trì thói quen luyện tập ngắn mỗi ngày (5–10 phút) theo hướng dẫn của giáo viên.",
            "Tập trung 1–2 mục tiêu cụ thể (ví dụ: phát âm âm cuối / tốc độ đọc / từ vựng theo chủ đề).",
            "Hoàn thành bài tập đúng hạn và chủ động hỏi khi chưa hiểu."
        ]
    }

def generate_monthly_report(req) -> Dict[str, Any]:
    name = req.student.name
    program = req.student.program or ""
    from_d, to_d = req.range.from_date, req.range.to_date
    texts = [x.text.strip() for x in req.session_feedbacks if x.text and x.text.strip()]
    total = len(texts)

    overview_fallback = (
        f"Trong giai đoạn {from_d} đến {to_d}, hiện chưa có đủ nhận xét sau buổi học để tổng hợp báo cáo."
        if total == 0 else
        f"Trong giai đoạn {from_d} đến {to_d}, {name} ({program}) có {total} ghi nhận sau buổi học. "
        f"Báo cáo này tổng hợp các điểm nổi bật và đề xuất cải thiện dựa trên nhận xét của giáo viên."
    )

    rb = _rule_based_sections(texts)
    rb["overview"] = overview_fallback

    draft_rule = f"""1) Tổng quan:
{rb["overview"]}

2) Điểm mạnh:
- """ + "\n- ".join(rb["strengths"]) + """

3) Cần cải thiện:
- """ + "\n- ".join(rb["improvements"]) + """

4) Nhận xét tiêu biểu:
- """ + "\n- ".join(rb["highlights"]) + """

5) Mục tiêu tháng tới:
- """ + "\n- ".join(rb["goals_next_month"]) + f"""

6) Thống kê nguồn dữ liệu:
- Số feedback được tổng hợp: {total}
- Số ngày có ghi nhận: {total}
"""

    # Gemini attempt
    client = get_gemini_client()
    if not client or total == 0:
        return {
            "ai_used": False,
            "draft_text": draft_rule,
            "sections": {
                "overview": rb["overview"],
                "strengths": rb["strengths"],
                "improvements": rb["improvements"],
                "highlights": rb["highlights"],
                "goals_next_month": rb["goals_next_month"],
                "source_summary": {"total_feedbacks": total, "days_covered": total}
            }
        }

    prompt = f"""
Bạn là giáo viên trung tâm tiếng Anh KidzGo.
Hãy tổng hợp báo cáo tháng dựa CHỈ trên feedback sau buổi học (không bịa).
Nếu thiếu dữ liệu phần nào, ghi rõ "Chưa đủ dữ liệu để kết luận".

Trả về DUY NHẤT 1 JSON object (không markdown, không giải thích):
{{
  "overview": "string",
  "strengths": ["...", "...", "..."],
  "improvements": ["...", "...", "..."],
  "highlights": ["...", "..."],
  "goals_next_month": ["...", "...", "..."]
}}

Học viên: {name}
Chương trình: {program}
Thời gian: {from_d} đến {to_d}

Feedback:
{chr(10).join([f"- {t}" for t in texts])}
"""

    try:
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        sec = safe_json_loads(resp.text or "")

        overview = (sec.get("overview") or rb["overview"]).strip()
        strengths = ensure_list_len(sec.get("strengths"), 3, "Học viên có thái độ học tập tích cực.")
        improvements = ensure_list_len(sec.get("improvements"), 3, "Cần luyện tập thêm theo hướng dẫn của giáo viên (5–10 phút/ngày).")
        highlights = ensure_list_len(sec.get("highlights"), 2, "Có ghi nhận tiến bộ trong tháng.")
        goals = ensure_list_len(sec.get("goals_next_month"), 3, "Duy trì luyện tập đều đặn theo kế hoạch.")

        draft_ai = f"""1) Tổng quan:
{overview}

2) Điểm mạnh:
- """ + "\n- ".join(strengths) + """

3) Cần cải thiện:
- """ + "\n- ".join(improvements) + """

4) Nhận xét tiêu biểu:
- """ + "\n- ".join(highlights) + """

5) Mục tiêu tháng tới:
- """ + "\n- ".join(goals) + f"""

6) Thống kê nguồn dữ liệu:
- Số feedback được tổng hợp: {total}
- Số ngày có ghi nhận: {total}
"""

        return {
            "ai_used": True,
            "draft_text": draft_ai,
            "sections": {
                "overview": overview,
                "strengths": strengths,
                "improvements": improvements,
                "highlights": highlights,
                "goals_next_month": goals,
                "source_summary": {"total_feedbacks": total, "days_covered": total}
            }
        }
    except Exception as e:
        # fallback if AI fails
        return {
            "ai_used": False,
            "draft_text": draft_rule,
            "sections": {
                "overview": rb["overview"],
                "strengths": rb["strengths"],
                "improvements": rb["improvements"],
                "highlights": rb["highlights"],
                "goals_next_month": rb["goals_next_month"],
                "source_summary": {"total_feedbacks": total, "days_covered": total}
            }
        }
