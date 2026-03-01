from pydantic import BaseModel


class EnhanceFeedbackRequest(BaseModel):
    draft: str
    language: str = 'vi'


class EnhanceFeedbackResponse(BaseModel):
    enhanced: str
