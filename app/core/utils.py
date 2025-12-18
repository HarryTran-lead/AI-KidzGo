import json
import re
from typing import Any, Dict, List, Optional

def extract_json_block(text: str) -> str:
    """
    Extract the first {...} block from a model output.
    """
    if not text:
        raise ValueError("Empty text")
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in text")
    return text[start:end+1]

def safe_json_loads(text: str) -> Dict[str, Any]:
    return json.loads(extract_json_block(text))

def ensure_list_len(items: Optional[List[str]], n: int, filler: str) -> List[str]:
    items = [x.strip() for x in (items or []) if isinstance(x, str) and x.strip()]
    while len(items) < n:
        items.append(filler)
    return items[:n]

def normalize_amount_to_number(x: Any) -> Optional[float]:
    """
    Accepts: "1,200,000", "1.200.000", "1200000", 1200000, etc.
    Returns float or None
    """
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)

    s = str(x).strip()
    if not s:
        return None

    # keep digits and separators only
    s = re.sub(r"[^\d,\.]", "", s)

    # Heuristic:
    # - If string contains both '.' and ',' -> remove thousands separators by dropping ',' then drop '.' if it's thousands
    # - For VN amounts, '.' often thousands; ',' often thousands too. We'll remove both and parse as int.
    digits = re.sub(r"[^\d]", "", s)
    if not digits:
        return None
    try:
        return float(int(digits))
    except:
        return None

def normalize_account(x: Any) -> Optional[str]:
    if x is None:
        return None
    s = str(x).strip()
    if not s:
        return None
    # remove spaces
    s = s.replace(" ", "")
    return s
