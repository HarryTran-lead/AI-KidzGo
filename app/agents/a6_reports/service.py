from typing import List, Dict, Any, Optional
from app.core.gemini_client import get_gemini_client
from app.core.utils import safe_json_loads, ensure_list_len
from app.agents.a6_reports.schemas import (
    MonthlyReportRequest, AttendanceData, HomeworkData, TestData,
    MissionData, TopicsData, SkillAssessment
)

POSITIVE = ["tiến bộ", "tốt", "tích cực", "tự tin", "chăm", "nhanh", "đúng", "cải thiện"]
NEGATIVE = ["chậm", "thiếu", "chưa", "sai", "yếu", "quên", "rụt rè", "lẫn", "khó"]

def _rule_based_sections(req) -> Dict[str, Any]:
    """Fallback when AI is not available"""
    name = req.student.name
    
    # Get data from request
    attendance = req.attendance
    homework = req.homework
    mission = req.mission
    topics = req.topics
    texts = [x.text.strip() for x in req.session_feedbacks if x.text and x.text.strip()]
    
    # Default values
    attendance_rate = f"{attendance.percentage:.0f}%" if attendance and attendance.percentage else "N/A"
    homework_completion = f"{homework.completion_rate:.0f}%" if homework and homework.completion_rate else "N/A"
    progress_level = mission.current_level if mission else "N/A"
    progress_topics = topics.topics if topics and topics.topics else []
    
    # Extract from session feedbacks
    strengths, improvements = [], []
    for t in texts:
        tl = t.lower()
        if any(k in tl for k in POSITIVE) and len(strengths) < 3:
            strengths.append(t.strip())
        if any(k in tl for k in NEGATIVE) and len(improvements) < 3:
            improvements.append(t.strip())

    if not strengths:
        strengths = [f"{name} duy trì tham gia học đều và có thái độ hợp tác trong lớp."]
    if not improvements:
        improvements = ["Cần tiếp tục luyện tập đều đặn để củng cố kỹ năng."]

    # Default study attitude from feedbacks
    study_attitude = texts[0] if texts else f"{name} có thái độ học tập tích cực trong tháng."
    
    # Default skills assessment
    skills = SkillAssessment(
        phonics="Chưa đủ dữ liệu để đánh giá.",
        speaking="Chưa đủ dữ liệu để đánh giá.",
        listening="Chưa đủ dữ liệu để đánh giá.",
        writing="Chưa đủ dữ liệu để đánh giá."
    )
    
    # Default parent support
    parent_support = [
        "Nhắc con làm và nộp bài tập về nhà đầy đủ.",
        "Khuyến khích con luyện tập tiếng Anh mỗi ngày."
    ]

    return {
        "attendance_rate": attendance_rate,
        "study_attitude": study_attitude,
        "progress_level": progress_level,
        "progress_topics": progress_topics,
        "skills": skills.model_dump() if isinstance(skills, SkillAssessment) else skills,
        "strengths": strengths[:3],
        "improvements": improvements[:3],
        "homework_completion": homework_completion,
        "parent_support": parent_support
    }

def _format_recent_reports(recent_reports: List[Any]) -> str:
    if not recent_reports:
        return "Không có dữ liệu báo cáo 3 tháng gần nhất."

    lines = []
    for report in recent_reports:
        lines.append(f"- Tháng: {report.month}")
        if hasattr(report, 'overview') and report.overview:
            lines.append(f"  Tổng quan: {report.overview}")
        if hasattr(report, 'strengths') and report.strengths:
            lines.append("  Điểm mạnh: " + "; ".join(report.strengths))
        if hasattr(report, 'improvements') and report.improvements:
            lines.append("  Cần cải thiện: " + "; ".join(report.improvements))
    return "\n".join(lines)

def _build_source_summary(req) -> Dict[str, Any]:
    """Build source summary from available data"""
    texts = [x.text.strip() for x in req.session_feedbacks if x.text and x.text.strip()]
    
    summary = {
        "total_feedbacks": len(texts),
        "has_attendance": req.attendance is not None,
        "has_homework": req.homework is not None,
        "has_test": req.test is not None and req.test.total > 0,
        "has_mission": req.mission is not None,
        "has_topics": req.topics is not None and req.topics.total > 0
    }
    
    if req.attendance:
        summary["attendance"] = {
            "total": req.attendance.total,
            "present": req.attendance.present,
            "percentage": req.attendance.percentage
        }
    
    if req.homework:
        summary["homework"] = {
            "total": req.homework.total,
            "completion_rate": req.homework.completion_rate
        }
    
    if req.test and req.test.tests:
        summary["test"] = {
            "total": req.test.total,
            "tests": [{"type": t.type, "score": t.score, "max_score": t.max_score} for t in req.test.tests]
        }
    
    return summary

def _format_draft_text(sections: Dict[str, Any], name: str) -> str:
    """Format the draft text for display"""
    skills = sections.get("skills", {})
    
    lines = [
        f"✔ Tỉ lệ chuyên cần: {sections.get('attendance_rate', 'N/A')}",
        f"✔ Về thái độ học tập: {sections.get('study_attitude', '')}",
        f"✔ Tiến độ: level {sections.get('progress_level', 'N/A')}: {', '.join(sections.get('progress_topics', []))}",
        "",
        f"✔ Về kỹ năng học tập:",
        f"Phần Phonics: {skills.get('phonics', 'Chưa đủ dữ liệu.')}",
        f"Phần Speaking: {skills.get('speaking', 'Chưa đủ dữ liệu.')}",
        f"Phần Listening: {skills.get('listening', 'Chưa đủ dữ liệu.')}",
        f"Phần Writing: {skills.get('writing', 'Chưa đủ dữ liệu.')}",
        "",
        "✔ Điểm mạnh: " + "; ".join(sections.get("strengths", [])),
        "",
        "✔ Điểm cần cải thiện: " + "; ".join(sections.get("improvements", [])),
        "",
        f"✔ Bài tập về nhà: {sections.get('homework_completion', 'N/A')}",
        "",
        "✔ Hướng hỗ trợ từ cô và ba mẹ:",
    ]
    
    for support in sections.get("parent_support", []):
        lines.append(support)
    
    return "\n".join(lines)

def generate_monthly_report(req: MonthlyReportRequest) -> Dict[str, Any]:
    name = req.student.name
    program = req.student.program or ""
    from_d, to_d = req.range.from_date, req.range.to_date
    texts = [x.text.strip() for x in req.session_feedbacks if x.text and x.text.strip()]
    total = len(texts)
    
    recent_reports_summary = _format_recent_reports(req.recent_reports)
    teacher_notes = (req.teacher_notes or "").strip() or "Không có ghi chú bổ sung."
    
    # Get aggregated data
    attendance = req.attendance
    homework = req.homework
    test = req.test
    mission = req.mission
    topics = req.topics

    # Build source summary
    source_summary = _build_source_summary(req)

    # Try AI first
    client = get_gemini_client()
    if not client:
        # Fallback to rule-based
        rb = _rule_based_sections(req)
        draft_text = _format_draft_text(rb, name)
        
        return {
            "ai_used": False,
            "draft_text": draft_text,
            "sections": {
                **rb,
                "source_summary": source_summary
            }
        }

    # Build prompt with all available data
    prompt_parts = [
        f"Bạn là giáo viên trung tâm tiếng Anh KidzGo.",
        f"Hãy tổng hợp báo cáo tháng cho học viên {name}.",
        "Dựa trên dữ liệu thực tế dưới đây, viết nhận xét bằng tiếng Việt.",
        "",
        f"Thời gian: {from_d} đến {to_d}",
        f"Chương trình: {program}",
        ""
    ]

    # Attendance data
    if attendance:
        prompt_parts.extend([
            "--- DỮ LIỆU CHUYÊN CẦN ---",
            f"Tổng số buổi: {attendance.total}",
            f"Số buổi có mặt: {attendance.present}",
            f"Tỷ lệ chuyên cần: {attendance.percentage:.1f}%",
            ""
        ])

    # Homework data
    if homework:
        prompt_parts.extend([
            "--- DỮ LIỆU BÀI TẬP VỀ NHÀ ---",
            f"Tổng bài tập: {homework.total}",
            f"Hoàn thành: {homework.completed}",
            f"Đã nộp: {homework.submitted}",
            f"Tỷ lệ hoàn thành: {homework.completion_rate:.1f}%",
            f"Điểm trung bình: {homework.average:.1f}/100",
            ""
        ])

    # Test data
    if test and test.tests:
        test_info = "\n".join([
            f"- {t.type}: {t.score}/{t.maxScore} ({t.date})" 
            for t in test.tests
        ])
        prompt_parts.extend([
            "--- DỮ LIỆU BÀI TEST ---",
            test_info,
            ""
        ])

    # Mission/Level data
    if mission:
        prompt_parts.extend([
            "--- DỮ LIỆU LEVEL & XP ---",
            f"Level hiện tại: {mission.current_level}",
            f"XP hiện tại: {mission.current_xp}",
            f"Stars tích lũy: {mission.stars}",
            f"Nhiệm vụ hoàn thành: {mission.completed}/{mission.total}",
            ""
        ])

    # Topics covered
    if topics and topics.topics:
        prompt_parts.extend([
            "--- CÁC CHỦ ĐIỂM ĐÃ HỌC ---",
            ", ".join(topics.topics),
            ""
        ])

    # Session feedbacks
    if texts:
        prompt_parts.extend([
            "--- FEEDBACK SAU BUỔI HỌC ---",
            "\n".join([f"- {t}" for t in texts]),
            ""
        ])
    
    # Recent reports
    if req.recent_reports:
        prompt_parts.extend([
            "--- BÁO CÁO 3 THÁNG GẦN NHẤT ---",
            recent_reports_summary,
            ""
        ])

    # Teacher notes
    if teacher_notes and teacher_notes != "Không có ghi chú bổ sung.":
        prompt_parts.extend([
            "--- GHI CHÚ THÊM TỪ GIÁO VIÊN ---",
            teacher_notes,
            ""
        ])

    prompt = "\n".join(prompt_parts) + """

Hãy trả về DUY NHẤT 1 JSON object (không markdown, không giải thích):
{
  "attendance_rate": "VD: 85%",
  "study_attitude": "Mô tả thái độ học tập của học viên trong tháng",
  "progress_level": "VD: Get Ready for Flyers",
  "progress_topics": ["Chủ điểm 1", "Chủ điểm 2"],
  "skills": {
    "phonics": "Đánh giá kỹ năng Phonics",
    "speaking": "Đánh giá kỹ năng Speaking",
    "listening": "Đánh giá kỹ năng Listening", 
    "writing": "Đánh giá kỹ năng Writing"
  },
  "strengths": ["Điểm mạnh 1", "Điểm mạnh 2", "Điểm mạnh 3"],
  "improvements": ["Điểm cần cải thiện 1", "Điểm cần cải thiện 2"],
  "homework_completion": "VD: 90%",
  "parent_support": ["Hướng hỗ trợ 1", "Hướng hỗ trợ 2", "Hướng hỗ trợ 3"]
}
"""

    try:
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        sec = safe_json_loads(resp.text or "")

        # Validate and fill in missing values
        attendance_rate = sec.get("attendance_rate") or (f"{attendance.percentage:.0f}%" if attendance else "N/A")
        study_attitude = sec.get("study_attitude") or texts[0] if texts else f"{name} có thái độ học tập tích cực."
        progress_level = sec.get("progress_level") or (mission.current_level if mission else "N/A")
        progress_topics = sec.get("progress_topics") or (topics.topics if topics else [])
        
        skills_data = sec.get("skills") or {}
        skills = SkillAssessment(
            phonics=skills_data.get("phonics") or "Chưa đủ dữ liệu để đánh giá.",
            speaking=skills_data.get("speaking") or "Chưa đủ dữ liệu để đánh giá.",
            listening=skills_data.get("listening") or "Chưa đủ dữ liệu để đánh giá.",
            writing=skills_data.get("writing") or "Chưa đủ dữ liệu để đánh giá."
        )
        
        strengths = ensure_list_len(sec.get("strengths"), 3, f"{name} có thái độ học tập tích cực.")
        improvements = ensure_list_len(sec.get("improvements"), 2, "Cần luyện tập thêm theo hướng dẫn của giáo viên.")
        homework_completion = sec.get("homework_completion") or (f"{homework.completion_rate:.0f}%" if homework else "N/A")
        parent_support = ensure_list_len(sec.get("parent_support"), 3, "Nhắc con làm và nộp bài tập về nhà đầy đủ.")

        sections = {
            "attendance_rate": attendance_rate,
            "study_attitude": study_attitude,
            "progress_level": progress_level,
            "progress_topics": progress_topics,
            "skills": skills.model_dump(),
            "strengths": strengths,
            "improvements": improvements,
            "homework_completion": homework_completion,
            "parent_support": parent_support,
            "source_summary": source_summary
        }

        draft_text = _format_draft_text(sections, name)

        return {
            "ai_used": True,
            "draft_text": draft_text,
            "sections": sections
        }

    except Exception as e:
        # Fallback if AI fails
        rb = _rule_based_sections(req)
        rb["source_summary"] = source_summary
        draft_text = _format_draft_text(rb, name)
        
        return {
            "ai_used": False,
            "draft_text": draft_text,
            "sections": rb
        }
