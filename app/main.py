from fastapi import FastAPI
from app.core.gemini_client import gemini_key_present
from app.agents.a6_reports.router import router as a6_router
from app.agents.a7_receipts.router import router as a7_router

app = FastAPI(title="KidzGo AI Service")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/debug/ai")
def debug_ai():
    return {"gemini_key_present": gemini_key_present()}

# Routes
app.include_router(a6_router, prefix="/a6", tags=["A6 Reports"])
app.include_router(a7_router, prefix="/a7", tags=["A7 Receipts"])
