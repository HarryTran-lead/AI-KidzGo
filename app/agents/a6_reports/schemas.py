from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class StudentInfo(BaseModel):
    student_id: str
    name: str
    age: Optional[int] = None
    program: Optional[str] = None

class AttendanceData(BaseModel):
    total: int = 0
    present: int = 0
    absent: int = 0
    makeup: int = 0
    not_marked: int = 0
    percentage: float = 0

class HomeworkData(BaseModel):
    total: int = 0
    completed: int = 0
    submitted: int = 0
    pending: int = 0
    late: int = 0
    missing: int = 0
    average: float = 0
    completion_rate: float = 0

class TestResult(BaseModel):
    exam_id: str
    type: str
    score: float
    max_score: float
    date: str
    comment: Optional[str] = None

class TestData(BaseModel):
    total: int = 0
    tests: List[TestResult] = Field(default_factory=list)

class MissionData(BaseModel):
    completed: int = 0
    total: int = 0
    in_progress: int = 0
    stars: int = 0
    xp: int = 0
    current_level: str = "0"
    current_xp: int = 0

class TopicsData(BaseModel):
    total: int = 0
    topics: List[str] = Field(default_factory=list)
    lesson_contents: List[str] = Field(default_factory=list)

class SessionFeedback(BaseModel):
    date: str  # YYYY-MM-DD
    text: str

class ReportRange(BaseModel):
    from_date: str  # YYYY-MM-DD
    to_date: str    # YYYY-MM-DD

class RecentMonthlyReport(BaseModel):
    month: str  # YYYY-MM
    overview: Optional[str] = None
    strengths: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    highlights: List[str] = Field(default_factory=list)
    goals_next_month: List[str] = Field(default_factory=list)

class MonthlyReportRequest(BaseModel):
    student: StudentInfo
    range: ReportRange
    attendance: Optional[AttendanceData] = None
    homework: Optional[HomeworkData] = None
    test: Optional[TestData] = None
    mission: Optional[MissionData] = None
    topics: Optional[TopicsData] = None
    session_feedbacks: List[SessionFeedback] = Field(default_factory=list)
    recent_reports: List[RecentMonthlyReport] = Field(default_factory=list)
    teacher_notes: Optional[str] = None
    language: str = "vi"

# New response format for monthly report
class SkillAssessment(BaseModel):
    phonics: Optional[str] = None
    speaking: Optional[str] = None
    listening: Optional[str] = None
    writing: Optional[str] = None

class ReportSections(BaseModel):
    attendance_rate: str  # e.g., "85%"
    study_attitude: str
    progress_level: str
    progress_topics: List[str]
    skills: SkillAssessment
    strengths: List[str]
    improvements: List[str]
    homework_completion: str  # e.g., "90%"
    parent_support: List[str]
    source_summary: Dict[str, Any]

class MonthlyReportResponse(BaseModel):
    ai_used: bool
    draft_text: str
    sections: ReportSections
