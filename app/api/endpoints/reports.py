from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models import Report, Interview
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import func
from collections import Counter
from app.db.database import get_db

router = APIRouter()

class ReportResponse(BaseModel):
    id: int
    interview_id: int
    overall_score: int
    strengths: List[str]
    weaknesses: List[str]
    detailed_analysis: str
    recommendations: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/interview/{interview_id}", response_model=ReportResponse)
async def get_interview_report(
    interview_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get the report for a specific interview
    """
    report = db.query(Report).filter(Report.interview_id == interview_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report

@router.get("/", response_model=List[ReportResponse])
async def list_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[ReportResponse]:
    """
    List all reports
    """
    reports = db.query(Report).offset(skip).limit(limit).all()
    return reports

@router.get("/candidate/{candidate_id}", response_model=List[ReportResponse])
async def get_candidate_reports(
    candidate_id: int,
    db: Session = Depends(get_db)
) -> List[ReportResponse]:
    """
    Get all reports for a specific candidate
    """
    # Get all interviews for the candidate
    interviews = db.query(Interview).filter(Interview.candidate_id == candidate_id).all()
    interview_ids = [interview.id for interview in interviews]
    
    # Get all reports for these interviews
    reports = db.query(Report).filter(Report.interview_id.in_(interview_ids)).all()
    return reports

@router.get("/summary")
async def get_reports_summary(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a summary of all reports
    """
    total_reports = db.query(Report).count()
    total_interviews = db.query(Interview).count()
    
    # Calculate average score
    avg_score = db.query(func.avg(Report.overall_score)).scalar() or 0
    
    # Get most common strengths and weaknesses
    all_strengths = []
    all_weaknesses = []
    reports = db.query(Report).all()
    
    for report in reports:
        all_strengths.extend(report.strengths)
        all_weaknesses.extend(report.weaknesses)
    
    common_strengths = Counter(all_strengths).most_common(5)
    common_weaknesses = Counter(all_weaknesses).most_common(5)
    
    return {
        "total_reports": total_reports,
        "total_interviews": total_interviews,
        "average_score": round(avg_score, 2),
        "common_strengths": common_strengths,
        "common_weaknesses": common_weaknesses
    } 