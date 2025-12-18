import os
from google import genai

def gemini_key_present() -> bool:
    return bool(os.getenv("GEMINI_API_KEY"))

def get_gemini_client():
    """
    Returns: genai.Client or None if missing key
    """
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return None
    return genai.Client(api_key=key)