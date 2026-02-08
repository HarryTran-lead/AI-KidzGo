import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env file
script_dir = Path(__file__).parent
env_path = script_dir / ".env"
load_dotenv(dotenv_path=str(env_path), override=True)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY not found in environment variables!")
    print("Make sure .env file exists and contains: GEMINI_API_KEY=your-key")
    exit(1)

client = genai.Client(api_key=api_key)
resp = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Trả lời đúng 1 câu: Xin chào KidzGo"
)
print(resp.text)
