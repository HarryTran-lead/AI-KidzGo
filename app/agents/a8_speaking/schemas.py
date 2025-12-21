from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SpeakingContext(BaseModel):
    homework_id: str
    student_id: str
    mode: str = "phonics"  # phonics / speaking
    target_words: List[str] = Field(default_factory=list)   # danh sách từ/âm cần đọc
    expected_text: Optional[str] = None                     # nếu là đọc đoạn/câu
    instructions: Optional[str] = None
    language: str = "vi"

class AnalyzeTranscriptRequest(BaseModel):
    context: SpeakingContext
    transcript: str

class SpeakingResult(BaseModel):
    transcript: str
    overall_score: float
    pronunciation_score: float
    fluency_score: float
    accuracy_score: float
    phonics_issues: List[str] = Field(default_factory=list)
    speaking_issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    practice_plan: List[str] = Field(default_factory=list)
    confidence: Dict[str, float] = Field(default_factory=dict)
    raw_text: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)

class AnalyzeSpeakingResponse(BaseModel):
    ai_used: bool
    result: SpeakingResult
