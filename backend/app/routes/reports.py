from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.ai.agents.report_agent import ReportAgent
from app.utils.pdf_gen import generate_inventory_pdf
from app.auth.dependencies import get_current_user
import json

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/generate")
async def generate_report(user: dict = Depends(get_current_user)):
    agent = ReportAgent()
    report_json = await agent.generate()
    return report_json

@router.get("/download/pdf")
async def download_pdf(user: dict = Depends(get_current_user)):
    agent = ReportAgent()
    report_json = await agent.generate()
    pdf_buffer = generate_inventory_pdf(report_json)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=inventory_report.pdf"}
    )
