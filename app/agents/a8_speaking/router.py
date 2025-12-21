from fastapi import APIRouter, UploadFile, File
from app.agents.a8_speaking.schemas import AnalyzeTranscriptRequest, AnalyzeSpeakingResponse
from app.agents.a8_speaking.service import analyze_transcript, analyze_media_bytes

router = APIRouter()

@router.post("/analyze-transcript", response_model=AnalyzeSpeakingResponse)
def analyze_transcript_api(req: AnalyzeTranscriptRequest):
    return analyze_transcript(req.context, req.transcript)

@router.post("/analyze-media", response_model=AnalyzeSpeakingResponse)
async def analyze_media_api(
    homework_id: str,
    student_id: str,
    mode: str = "phonics",
    target_words: str = "",   # comma-separated for quick test
    expected_text: str = "",
    instructions: str = "",
    language: str = "vi",
    file: UploadFile = File(...)
):
    # quick context object
    class Ctx:
        def __init__(self):
            self.homework_id = homework_id
            self.student_id = student_id
            self.mode = mode
            self.target_words = [x.strip() for x in target_words.split(",") if x.strip()]
            self.expected_text = expected_text or None
            self.instructions = instructions or None
            self.language = language

    media = await file.read()
    return analyze_media_bytes(Ctx(), media, file.content_type or "video/mp4")
