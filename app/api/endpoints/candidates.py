from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models import Candidate
from typing import Dict, Any, List
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.db.database import get_db

router = APIRouter()

class CandidateCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str

class CandidateResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=CandidateResponse)
async def create_candidate(
    candidate_data: CandidateCreate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create a new candidate
    """
    # Check if candidate with email already exists
    existing_candidate = db.query(Candidate).filter(Candidate.email == candidate_data.email).first()
    if existing_candidate:
        raise HTTPException(
            status_code=400,
            detail="A candidate with this email already exists"
        )
    
    # Create new candidate
    candidate = Candidate(
        name=candidate_data.name,
        email=candidate_data.email,
        phone=candidate_data.phone
    )
    
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    
    return candidate

@router.get("/", response_model=List[CandidateResponse])
async def list_candidates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[CandidateResponse]:
    """
    List all candidates
    """
    candidates = db.query(Candidate).offset(skip).limit(limit).all()
    return candidates

@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a specific candidate by ID
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return candidate

@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: int,
    candidate_data: CandidateCreate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update a candidate's information
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Check if email is being changed and if it's already taken
    if candidate_data.email != candidate.email:
        existing_candidate = db.query(Candidate).filter(Candidate.email == candidate_data.email).first()
        if existing_candidate:
            raise HTTPException(
                status_code=400,
                detail="A candidate with this email already exists"
            )
    
    # Update candidate information
    candidate.name = candidate_data.name
    candidate.email = candidate_data.email
    candidate.phone = candidate_data.phone
    
    db.commit()
    db.refresh(candidate)
    
    return candidate

@router.delete("/{candidate_id}")
async def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Delete a candidate
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    db.delete(candidate)
    db.commit()
    
    return {"message": "Candidate deleted successfully"} 