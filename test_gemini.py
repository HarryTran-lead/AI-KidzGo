import os
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
resp = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Trả lời đúng 1 câu: Xin chào KidzGo"
)
print(resp.text)
