import os
from fastapi import FastAPI
from app.schemas import MonthlyReportRequest, MonthlyReportResponse
from app.report.service import generate_monthly_report

app = FastAPI(title="KidzGo AI Service - Monthly Report")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/debug/ai")
def debug_ai():
    # KHÔNG in key ra, chỉ báo có/không
    return {"gemini_key_present": bool(os.getenv("GEMINI_API_KEY"))}

@app.post("/generate-monthly-report", response_model=MonthlyReportResponse)
def generate_report(req: MonthlyReportRequest):
    return generate_monthly_report(req)
