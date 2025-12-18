from fastapi import APIRouter
from app.agents.a6_reports.schemas import MonthlyReportRequest, MonthlyReportResponse
from app.agents.a6_reports.service import generate_monthly_report

router = APIRouter()

@router.post("/generate-monthly-report", response_model=MonthlyReportResponse)
def generate(req: MonthlyReportRequest):
    return generate_monthly_report(req)
