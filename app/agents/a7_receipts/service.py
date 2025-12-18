import json
from typing import Any, Dict, Optional
from app.core.gemini_client import get_gemini_client
from app.core.utils import safe_json_loads, normalize_amount_to_number, normalize_account

def extract_payment_proof(
    image_bytes: bytes,
    mime_type: str,
    direction: str,
    branch_id: str
) -> Dict[str, Any]:
    client = get_gemini_client()
    if not client:
        return {
            "ai_used": False,
            "fields": {"direction": direction, "branch_id": branch_id},
            "confidence": {},
            "raw_text": None,
            "warnings": ["Missing GEMINI_API_KEY on server process"]
        }

    prompt = f"""
Bạn là trợ lý kế toán của trung tâm Anh ngữ KidzGo.
Trích xuất dữ liệu từ ảnh biên lai/chứng từ chuyển khoản. Chỉ lấy những gì nhìn thấy rõ; không chắc thì null.
Trả về DUY NHẤT 1 JSON object (không markdown, không giải thích) theo schema:

{{
  "fields": {{
    "direction": "{direction}",
    "branch_id": "{branch_id}",
    "transaction_datetime": "YYYY-MM-DD HH:mm:ss" | null,
    "amount": number | string | null,
    "currency": "VND" | null,
    "bank_name": string | null,
    "transaction_id": string | null,
    "content": string | null,
    "sender_name": string | null,
    "sender_account": string | null,
    "receiver_name": string | null,
    "receiver_account": string | null
  }},
  "confidence": {{
    "transaction_datetime": 0.0,
    "amount": 0.0,
    "transaction_id": 0.0,
    "content": 0.0,
    "sender_account": 0.0,
    "receiver_account": 0.0
  }},
  "raw_text": string | null,
  "warnings": [string]
}}

Quy tắc:
- amount phải chuẩn hóa về số (VND), bỏ dấu phẩy/chấm phân tách nghìn.
- Ưu tiên lấy: Số tiền, Ngày giờ, Mã GD/Trace/Ref, Nội dung.
"""

    try:
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                {"inline_data": {"mime_type": mime_type or "image/jpeg", "data": image_bytes}},
            ],
        )
        obj = safe_json_loads(resp.text or "")

        fields = obj.get("fields") or {}
        confidence = obj.get("confidence") or {}
        raw_text = obj.get("raw_text")
        warnings = obj.get("warnings") or []

        # Normalize
        fields["direction"] = direction
        fields["branch_id"] = branch_id
        fields["amount"] = normalize_amount_to_number(fields.get("amount"))
        fields["sender_account"] = normalize_account(fields.get("sender_account"))
        fields["receiver_account"] = normalize_account(fields.get("receiver_account"))

        return {
            "ai_used": True,
            "fields": fields,
            "confidence": {k: float(v) for k, v in confidence.items() if v is not None},
            "raw_text": raw_text,
            "warnings": warnings
        }
    except Exception as e:
        return {
            "ai_used": False,
            "fields": {"direction": direction, "branch_id": branch_id},
            "confidence": {},
            "raw_text": None,
            "warnings": [f"AI extract failed: {type(e).__name__}: {str(e)}"]
        }
