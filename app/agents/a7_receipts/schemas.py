from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class PaymentProofExtractResponse(BaseModel):
    ai_used: bool
    fields: Dict[str, Any]
    confidence: Dict[str, float]
    raw_text: Optional[str] = None
    warnings: List[str] = []
