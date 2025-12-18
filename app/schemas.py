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

class MonthlyReportRequest(BaseModel):
    student: StudentInfo
    range: ReportRange
    session_feedbacks: List[SessionFeedback] = Field(default_factory=list)
    template: str = "MONTHLY_REPORT_V1"
    language: str = "vi"

class ReportSections(BaseModel):
    overview: str
    strengths: List[str]
    improvements: List[str]
    highlights: List[str]
    goals_next_month: List[str]
    source_summary: Dict[str, int]

class MonthlyReportResponse(BaseModel):
    draft_text: str
    sections: ReportSections

from typing import Optional, Dict, Any, List

class PaymentProofExtractResponse(BaseModel):
    fields: Dict[str, Any]
    confidence: Dict[str, float]
    raw_text: Optional[str] = None
    warnings: List[str] = []