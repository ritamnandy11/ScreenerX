from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    interviews = relationship("Interview", back_populates="candidate")

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    job_description = Column(Text)
    status = Column(String)  # scheduled, in_progress, completed, cancelled
    scheduled_at = Column(DateTime)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    candidate = relationship("Candidate", back_populates="interviews")
    report = relationship("Report", back_populates="interview", uselist=False)

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"))
    overall_score = Column(Integer)
    strengths = Column(JSON)
    weaknesses = Column(JSON)
    detailed_analysis = Column(Text)
    recommendations = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    interview = relationship("Interview", back_populates="report")

class InterviewResponse(Base):
    __tablename__ = "interview_responses"
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"))
    question_index = Column(Integer)
    question = Column(Text)
    response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow) 