from fastapi import APIRouter, UploadFile, File, Form
from app.agents.a7_receipts.schemas import PaymentProofExtractResponse
from app.agents.a7_receipts.service import extract_payment_proof

router = APIRouter()

@router.post("/extract-payment-proof", response_model=PaymentProofExtractResponse)
async def extract(
    file: UploadFile = File(...),
    direction: str = Form("IN"),      # IN / OUT
    branch_id: str = Form("UNKNOWN")
):
    img = await file.read()
    return extract_payment_proof(
        image_bytes=img,
        mime_type=file.content_type or "image/jpeg",
        direction=direction,
        branch_id=branch_id
    )
