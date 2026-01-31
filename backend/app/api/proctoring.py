from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import ProctoringEvent, CandidateProfile, Assessment
from app.schemas.schemas import ProctoringEventCreate, ProctoringEventResponse
from app.services.auth_service import get_current_user, get_current_candidate

router = APIRouter(prefix="/proctoring", tags=["Proctoring"])

@router.post("/event")
async def log_proctoring_event(
    data: ProctoringEventCreate,
    current_user = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """Log a proctoring event (detected by frontend)"""
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Create proctoring event
    event = ProctoringEvent(
        candidate_id=profile.id,
        assessment_id=data.assessment_id,
        event_type=data.event_type,
        severity=data.severity,
        description=data.description
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return {"message": "Event logged", "event_id": event.id}

@router.get("/events/{assessment_id}", response_model=List[ProctoringEventResponse])
async def get_proctoring_events(
    assessment_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get proctoring events for an assessment (recruiter view)"""
    events = db.query(ProctoringEvent).filter(
        ProctoringEvent.assessment_id == assessment_id
    ).order_by(ProctoringEvent.timestamp.desc()).all()
    
    return events

@router.get("/summary/{assessment_id}")
async def get_proctoring_summary(
    assessment_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summary of proctoring events"""
    events = db.query(ProctoringEvent).filter(
        ProctoringEvent.assessment_id == assessment_id
    ).all()
    
    # Count by type
    event_counts = {}
    severity_counts = {"low": 0, "medium": 0, "high": 0}
    
    for event in events:
        event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
        severity_counts[event.severity] = severity_counts.get(event.severity, 0) + 1
    
    # Calculate risk level
    risk_score = (
        severity_counts["low"] * 1 +
        severity_counts["medium"] * 3 +
        severity_counts["high"] * 5
    )
    
    if risk_score > 20:
        risk_level = "high"
    elif risk_score > 10:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return {
        "total_events": len(events),
        "event_counts": event_counts,
        "severity_counts": severity_counts,
        "risk_score": risk_score,
        "risk_level": risk_level
    }
