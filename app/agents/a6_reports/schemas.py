from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class StudentInfo(BaseModel):
    student_id: str
    name: str
    age: Optional[int] = None
    program: Optional[str] = None

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
    session_feedbacks: List[SessionFeedback] = Field(default_factory=list)
    recent_reports: List[RecentMonthlyReport] = Field(default_factory=list)
    recent_reports: List[RecentMonthlyReport] = Field(default_factory=list)
    teacher_notes: Optional[str] = None
    language: str = "vi"

class ReportSections(BaseModel):
    overview: str
    strengths: List[str]
    improvements: List[str]
    highlights: List[str]
    goals_next_month: List[str]
    source_summary: Dict[str, int]

class MonthlyReportResponse(BaseModel):
    ai_used: bool
    draft_text: str
    sections: ReportSections
