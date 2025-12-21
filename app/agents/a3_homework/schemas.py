from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class HomeworkContext(BaseModel):
    homework_id: str
    student_id: str
    subject: str = "english"
    skill: str = "writing"  # writing / reading / vocab / grammar / mixed
    instructions: Optional[str] = None
    rubric: Optional[str] = None  # rubric text if you have

class GradeTextRequest(BaseModel):
    context: HomeworkContext
    student_answer_text: str
    expected_answer_text: Optional[str] = None  # if teacher provides
    language: str = "vi"

class GradeLinkRequest(BaseModel):
    context: HomeworkContext
    link_url: str
    extracted_text: Optional[str] = None  # IMPORTANT: .NET should download/parse then send text here
    expected_answer_text: Optional[str] = None
    language: str = "vi"

class GradingResult(BaseModel):
    score: float
    max_score: float = 10.0
    summary: str
    strengths: List[str] = Field(default_factory=list)
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    extracted_student_answer: Optional[str] = None
    confidence: Dict[str, float] = Field(default_factory=dict)
    raw_text: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)

class GradeResponse(BaseModel):
    ai_used: bool
    result: GradingResult
