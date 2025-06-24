from app.services.groq_service import GroqService
from app.services.twilio_service import TwilioService
from app.db.models import Interview, Report, Candidate, InterviewResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime
import json

class InterviewService:
    def __init__(self, db: Session):
        self.db = db
        self.groq_service = GroqService()
        self.twilio_service = TwilioService()

    async def schedule_interview(self, candidate_id: int, job_description: str, scheduled_at: datetime) -> Dict[str, Any]:
        """
        Schedule a new interview
        """
        try:
            # Create interview record
            interview = Interview(
                candidate_id=candidate_id,
                job_description=job_description,
                status="scheduled",
                scheduled_at=scheduled_at
            )
            self.db.add(interview)
            self.db.commit()
            self.db.refresh(interview)

            # Generate questions
            questions = await self.groq_service.generate_interview_questions(job_description)
            
            return {
                "success": True,
                "interview_id": interview.id,
                "questions": questions
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "error": str(e)
            }

    async def start_interview(self, interview_id: int) -> Dict[str, Any]:
        """
        Start the interview process
        """
        try:
            interview = self.db.query(Interview).filter(Interview.id == interview_id).first()
            if not interview:
                return {"success": False, "error": "Interview not found"}

            candidate = self.db.query(Candidate).filter(Candidate.id == interview.candidate_id).first()
            if not candidate:
                return {"success": False, "error": "Candidate not found"}

            # Generate questions if not already generated
            questions = await self.groq_service.generate_interview_questions(interview.job_description)
            
            # Initiate call
            call_result = self.twilio_service.initiate_call(candidate.phone, str(interview_id))
            
            if call_result["success"]:
                interview.status = "in_progress"
                interview.started_at = datetime.utcnow()
                self.db.commit()
                
                return {
                    "success": True,
                    "call_sid": call_result["call_sid"],
                    "questions": questions
                }
            else:
                return call_result

        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "error": str(e)
            }

    async def process_response(self, interview_id: int, question_index: int, response: str) -> Dict[str, Any]:
        """
        Process candidate's response to a question
        """
        try:
            interview = self.db.query(Interview).filter(Interview.id == interview_id).first()
            if not interview:
                return {"success": False, "error": "Interview not found"}

            # Get the question
            questions = await self.groq_service.generate_interview_questions(interview.job_description)
            if question_index >= len(questions):
                return {"success": False, "error": "Invalid question index"}

            question = questions[question_index]

            # Store response only (no analysis or marks)
            interview_data = {
                "question": question["question"],
                "response": response
            }

            return {
                "success": True,
                "next_question": question_index + 1 < len(questions)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def complete_interview(self, interview_id: int) -> Dict[str, Any]:
        """
        Complete the interview and generate final report
        """
        try:
            interview = self.db.query(Interview).filter(Interview.id == interview_id).first()
            if not interview:
                return {"success": False, "error": "Interview not found"}

            # Get all responses
            responses = self.db.query(InterviewResponse).filter(InterviewResponse.interview_id == interview_id).all()
            interview_data = {
                "job_description": interview.job_description,
                "responses": [
                    {"question_index": r.question_index, "response": r.response}
                    for r in responses
                ]
            }

            # Generate final report without a quantitative score
            report_data = await self.groq_service.generate_final_report(interview_data)

            # Create report record
            report = Report(
                interview_id=interview_id,
                overall_score=0,  # Set score to 0 as it's not used
                strengths=report_data.get("strengths", ""),
                weaknesses=report_data.get("weaknesses", ""),
                detailed_analysis=report_data.get("detailed_analysis", ""),
                recommendations=report_data.get("recommendations", "")
            )
            self.db.add(report)

            # Update interview status
            interview.status = "completed"
            interview.completed_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(report)

            return {
                "success": True,
                "report": report_data
            }

        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "error": str(e)
            } 