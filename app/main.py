from fastapi import FastAPI
from dotenv import load_dotenv
from app.core.gemini_client import gemini_key_present

# Load environment variables from .env file
load_dotenv()

from app.agents.a6_reports.router import router as a6_router
from app.agents.a7_receipts.router import router as a7_router
from app.agents.a3_homework.router import router as a3_router
from app.agents.a8_speaking.router import router as a8_router

app = FastAPI(title="KidzGo AI Service")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/debug/ai")
def debug_ai():
    return {"gemini_key_present": gemini_key_present()}

app.include_router(a6_router, prefix="/a6", tags=["A6 Reports"])
app.include_router(a7_router, prefix="/a7", tags=["A7 Receipts"])
app.include_router(a3_router, prefix="/a3", tags=["A3 Homework"])
app.include_router(a8_router, prefix="/a8", tags=["A8 Speaking/Phonics"])

if __name__ == "__main__":
    import uvicorn
    # Use import string to enable reload feature
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)