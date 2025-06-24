from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form, status
from sqlalchemy.orm import Session
from app.services.interview import InterviewService
from app.db.models import Interview, Candidate, Report, InterviewResponse
from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel
from app.db.database import get_db
import json
from app.core.config import settings

router = APIRouter()

class InterviewCreate(BaseModel):
    candidate_id: int
    job_description: str
    scheduled_at: datetime

class ResponseData(BaseModel):
    response: str

@router.post("/schedule")
async def schedule_interview(
    interview_data: InterviewCreate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Schedule a new interview
    """
    service = InterviewService(db)
    result = await service.schedule_interview(
        interview_data.candidate_id,
        interview_data.job_description,
        interview_data.scheduled_at
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/{interview_id}/start")
async def start_interview(
    interview_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Start an interview
    """
    service = InterviewService(db)
    result = await service.start_interview(interview_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

def safe_twiml_response(twiml: str):
    return Response(content=twiml, media_type="application/xml", status_code=status.HTTP_200_OK)

@router.post("/{interview_id}/twiml")
async def interview_twiml(interview_id: int, db: Session = Depends(get_db)):
    print(f"DEBUG: TwiML endpoint called for interview {interview_id}")
    try:
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            print(f"DEBUG: Interview {interview_id} not found")
            raise Exception("Interview not found")
            
        candidate = db.query(Candidate).filter(Candidate.id == interview.candidate_id).first()
        if not candidate:
            print(f"DEBUG: Candidate not found for interview {interview_id}")
            raise Exception("Candidate not found")
            
        candidate_name = candidate.name if candidate else "Candidate"
        job_role = interview.job_description[:60] + ("..." if len(interview.job_description) > 60 else "")
        
        print(f"DEBUG: Generating questions for job: {job_role}")
        from app.services.groq_service import GroqService
        groq_service = GroqService()
        questions = await groq_service.generate_interview_questions(interview.job_description)
        
        print(f"DEBUG: Generated {len(questions)} questions")
        
        twiml = f"""
<Response>
    <Say voice="alice">Hello {candidate_name}, this is an automated interview for the job role you have applied for: {job_role}. Let's begin your interview.</Say>
    <Pause length="1"/>
    <Gather input="speech dtmf" timeout="8" numDigits="1" action="{settings.PUBLIC_BASE_URL}/api/v1/interviews/{interview_id}/response/0" method="POST" language="en-IN">
        <Say voice="alice">Question 1: {questions[0]['question']}</Say>
    </Gather>
    <Say voice="alice">We did not receive your response. Let's move to the next question.</Say>
</Response>
"""
        print(f"DEBUG: Returning TwiML for interview {interview_id}")
        return safe_twiml_response(twiml)
    except Exception as e:
        print(f"Error in /twiml: {e}")
        fallback = """
<Response>
    <Say voice="alice">Sorry, an application error occurred. Please try again later.</Say>
    <Hangup/>
</Response>
"""
        return safe_twiml_response(fallback)

@router.post("/{interview_id}/response/{question_index}")
async def process_response(
    interview_id: int,
    question_index: int,
    SpeechResult: str = Form(None),
    Digits: str = Form(None),
    db: Session = Depends(get_db)
):
    try:
        from app.services.groq_service import GroqService
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            print(f"DEBUG: Interview {interview_id} not found in /response")
            fallback = """
<Response>
    <Say voice="alice">Sorry, this interview does not exist.</Say>
    <Hangup/>
</Response>
"""
            return safe_twiml_response(fallback)
        if interview.status == "completed":
            print(f"DEBUG: Interview {interview_id} already completed in /response")
            fallback = """
<Response>
    <Say voice="alice">Thank you, your interview is already complete. Have a great day!</Say>
    <Hangup/>
</Response>
"""
            return safe_twiml_response(fallback)
        groq_service = GroqService()
        questions = await groq_service.generate_interview_questions(interview.job_description)
        if question_index >= len(questions):
            print(f"DEBUG: Question index {question_index} out of range for interview {interview_id}")
            fallback = """
<Response>
    <Say voice="alice">Thank you, your interview is already complete. Have a great day!</Say>
    <Hangup/>
</Response>
"""
            return safe_twiml_response(fallback)
        next_index = question_index + 1

        user_response = SpeechResult or Digits or ""
        db.add(InterviewResponse(
            interview_id=interview_id,
            question_index=question_index,
            question=questions[question_index]['question'],
            response=user_response
        ))
        db.commit()

        if next_index < len(questions):
            twiml = f"""
<Response>
    <Pause length="7"/>
    <Gather input="speech dtmf" timeout="8" numDigits="1" action="{settings.PUBLIC_BASE_URL}/api/v1/interviews/{interview_id}/response/{next_index}" method="POST" language="en-IN">
        <Say voice="alice">Question {next_index+1}: {questions[next_index]['question']}</Say>
    </Gather>
    <Say voice="alice">We did not receive your response. Let's move to the next question.</Say>
</Response>
"""
        else:
            service = InterviewService(db)
            await service.complete_interview(interview_id)
            twiml = """
<Response>
    <Pause length="2"/>
    <Say voice="alice">Thank you for your time. Have a great day!</Say>
</Response>
"""
        return safe_twiml_response(twiml)
    except Exception as e:
        print(f"Error in /response/{{question_index}}: {e}")
        fallback = """
<Response>
    <Say voice="alice">Sorry, an application error occurred. Please try again later.</Say>
    <Hangup/>
</Response>
"""
        return safe_twiml_response(fallback)

@router.post("/{interview_id}/complete")
async def complete_interview(
    interview_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Complete an interview and generate the final report
    """
    service = InterviewService(db)
    result = await service.complete_interview(interview_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.get("/{interview_id}/status")
async def get_interview_status(
    interview_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get the current status of an interview
    """
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    return {
        "interview_id": interview.id,
        "status": interview.status,
        "scheduled_at": interview.scheduled_at,
        "started_at": interview.started_at,
        "completed_at": interview.completed_at
    }

@router.post("/{interview_id}/status")
async def interview_status(interview_id: int):
    # Log or process the status callback here
    return {"message": "Status received"}

@router.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint working", "status": "ok"}

@router.post("/test")
async def test_post_endpoint():
    return {"message": "Test POST endpoint working", "status": "ok"} 