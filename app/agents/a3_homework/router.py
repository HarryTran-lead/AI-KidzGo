from fastapi import APIRouter, UploadFile, File
from app.agents.a3_homework.schemas import GradeTextRequest, GradeLinkRequest, GradeResponse
from app.agents.a3_homework.service import grade_text, grade_image

router = APIRouter()

@router.post("/grade-text", response_model=GradeResponse)
def grade_text_api(req: GradeTextRequest):
    return grade_text(req.context, req.student_answer_text, req.expected_answer_text, req.language)

@router.post("/grade-image", response_model=GradeResponse)
async def grade_image_api(
    homework_id: str,
    student_id: str,
    skill: str = "writing",
    instructions: str = "",
    expected_answer_text: str = "",
    language: str = "vi",
    file: UploadFile = File(...)
):
    # build context inline (để test nhanh)
    class Ctx:
        def __init__(self):
            self.homework_id = homework_id
            self.student_id = student_id
            self.skill = skill
            self.instructions = instructions
            self.rubric = None

    img = await file.read()
    return grade_image(Ctx(), img, file.content_type or "image/jpeg", expected_answer_text or None, language)

@router.post("/grade-link", response_model=GradeResponse)
def grade_link_api(req: GradeLinkRequest):
    # Demo chuẩn: .NET download + parse nội dung rồi gửi extracted_text vào
    text = req.extracted_text or f"(LINK ONLY) {req.link_url}\nChưa có extracted_text."
    return grade_text(req.context, text, req.expected_answer_text, req.language)
