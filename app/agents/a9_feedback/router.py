from fastapi import APIRouter
from app.agents.a9_feedback.schemas import EnhanceFeedbackRequest, EnhanceFeedbackResponse
from app.agents.a9_feedback.service import enhance_feedback_api

router = APIRouter()

@router.post("/enhance-feedback", response_model=EnhanceFeedbackResponse)
def enhance_feedback_endpoint(req: EnhanceFeedbackRequest):
    return enhance_feedback_api(req)
