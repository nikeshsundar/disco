from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import (
    User, JobDescription, Question, CandidateProfile, 
    Assessment, FinalEvaluation, ProctoringEvent
)
from app.schemas.schemas import (
    JobDescriptionCreate, JobDescriptionResponse, 
    QuestionCreate, QuestionResponse
)
from app.services.auth_service import get_current_recruiter
from app.services.resume_service import match_resume_to_job

router = APIRouter(prefix="/recruiter", tags=["Recruiter"])

# ============ JOB MANAGEMENT ============

@router.post("/jobs", response_model=JobDescriptionResponse)
async def create_job(
    job_data: JobDescriptionCreate,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Create a new job description"""
    job = JobDescription(
        recruiter_id=current_user.id,
        **job_data.model_dump()
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.get("/jobs", response_model=List[JobDescriptionResponse])
async def get_my_jobs(
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Get all jobs created by this recruiter"""
    jobs = db.query(JobDescription).filter(
        JobDescription.recruiter_id == current_user.id
    ).all()
    return jobs

@router.get("/jobs/{job_id}")
async def get_job(
    job_id: int,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Get job details with candidate stats"""
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get candidate stats
    assessments = db.query(Assessment).filter(Assessment.job_id == job_id).all()
    
    stats = {
        "total_applications": len(assessments),
        "completed": sum(1 for a in assessments if a.status == "completed"),
        "in_progress": sum(1 for a in assessments if a.status == "in_progress"),
        "not_started": sum(1 for a in assessments if a.status == "not_started")
    }
    
    return {
        "job": job,
        "stats": stats
    }

@router.put("/jobs/{job_id}")
async def update_job(
    job_id: int,
    job_data: JobDescriptionCreate,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Update a job description"""
    job = db.query(JobDescription).filter(
        JobDescription.id == job_id,
        JobDescription.recruiter_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    for key, value in job_data.model_dump().items():
        setattr(job, key, value)
    
    db.commit()
    db.refresh(job)
    return job

@router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Deactivate a job"""
    job = db.query(JobDescription).filter(
        JobDescription.id == job_id,
        JobDescription.recruiter_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job.is_active = False
    db.commit()
    
    return {"message": "Job deactivated"}

# ============ QUESTION MANAGEMENT ============

@router.post("/questions", response_model=QuestionResponse)
async def create_question(
    question_data: QuestionCreate,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Create a new question"""
    question = Question(**question_data.model_dump())
    db.add(question)
    db.commit()
    db.refresh(question)
    return question

@router.get("/questions")
async def get_questions(
    job_id: int = None,
    category: str = None,
    question_type: str = None,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Get questions with optional filters"""
    query = db.query(Question)
    
    if job_id:
        query = query.filter((Question.job_id == job_id) | (Question.job_id == None))
    if category:
        query = query.filter(Question.category == category)
    if question_type:
        query = query.filter(Question.question_type == question_type)
    
    return query.all()

@router.post("/questions/bulk")
async def create_questions_bulk(
    questions: List[QuestionCreate],
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Create multiple questions at once"""
    created = []
    for q_data in questions:
        question = Question(**q_data.model_dump())
        db.add(question)
        created.append(question)
    
    db.commit()
    return {"message": f"Created {len(created)} questions"}

# ============ CANDIDATE MANAGEMENT ============

@router.get("/candidates")
async def get_all_candidates(
    job_id: int = None,
    status: str = None,
    ranking: str = None,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Get all candidates with filters"""
    query = db.query(CandidateProfile).join(User)
    
    if status:
        query = query.filter(CandidateProfile.status == status)
    if ranking:
        query = query.filter(CandidateProfile.ranking == ranking)
    
    candidates = query.all()
    
    result = []
    for candidate in candidates:
        user = candidate.user
        evaluation = db.query(FinalEvaluation).filter(
            FinalEvaluation.candidate_id == candidate.id
        ).first()
        
        # Get assessments
        assessments = db.query(Assessment).filter(
            Assessment.candidate_id == candidate.id
        )
        if job_id:
            assessments = assessments.filter(Assessment.job_id == job_id)
        assessments = assessments.all()
        
        result.append({
            "id": candidate.id,
            "user_id": user.id,
            "name": user.full_name,
            "email": user.email,
            "status": candidate.status,
            "ranking": candidate.ranking,
            "resume_uploaded": candidate.resume_path is not None,
            "skills": candidate.parsed_resume.get("skills", []) if candidate.parsed_resume else [],
            "experience_years": candidate.parsed_resume.get("experience_years", 0) if candidate.parsed_resume else 0,
            "assessments": [{
                "job_id": a.job_id,
                "status": a.status,
                "total_score": a.total_score
            } for a in assessments],
            "evaluation": {
                "recommendation": evaluation.recommendation,
                "final_score": evaluation.final_score,
                "rationale": evaluation.rationale[:200] if evaluation.rationale else None
            } if evaluation else None
        })
    
    return result

@router.get("/candidates/{candidate_id}")
async def get_candidate_detail(
    candidate_id: int,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Get detailed view of a candidate"""
    candidate = db.query(CandidateProfile).filter(
        CandidateProfile.id == candidate_id
    ).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    user = candidate.user
    
    # Get assessments
    assessments = db.query(Assessment).filter(
        Assessment.candidate_id == candidate_id
    ).all()
    
    # Get final evaluation
    evaluation = db.query(FinalEvaluation).filter(
        FinalEvaluation.candidate_id == candidate_id
    ).first()
    
    # Get proctoring events
    proctoring_summary = {}
    if assessments:
        for assessment in assessments:
            events = db.query(ProctoringEvent).filter(
                ProctoringEvent.assessment_id == assessment.id
            ).all()
            proctoring_summary[assessment.id] = {
                "total_events": len(events),
                "events": [{
                    "type": e.event_type,
                    "severity": e.severity,
                    "timestamp": e.timestamp
                } for e in events[:10]]  # Last 10 events
            }
    
    return {
        "candidate": {
            "id": candidate.id,
            "name": user.full_name,
            "email": user.email,
            "status": candidate.status,
            "ranking": candidate.ranking,
            "created_at": candidate.created_at
        },
        "resume": candidate.parsed_resume,
        "assessments": [{
            "id": a.id,
            "job_id": a.job_id,
            "status": a.status,
            "technical_score": a.technical_score,
            "psychometric_score": a.psychometric_score,
            "total_score": a.total_score,
            "started_at": a.started_at,
            "completed_at": a.completed_at,
            "proctoring": proctoring_summary.get(a.id, {})
        } for a in assessments],
        "evaluation": {
            "recommendation": evaluation.recommendation,
            "rationale": evaluation.rationale,
            "final_score": evaluation.final_score,
            "resume_match_score": evaluation.resume_match_score,
            "assessment_score": evaluation.assessment_score,
            "integrity_score": evaluation.integrity_score,
            "strengths": evaluation.strengths,
            "weaknesses": evaluation.weaknesses,
            "technical_breakdown": evaluation.technical_breakdown,
            "psychometric_breakdown": evaluation.psychometric_breakdown
        } if evaluation else None
    }

@router.get("/candidates/job/{job_id}/shortlist")
async def get_shortlisted_candidates(
    job_id: int,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Get candidates sorted by ranking for a specific job"""
    # Get all assessments for this job
    assessments = db.query(Assessment).filter(
        Assessment.job_id == job_id,
        Assessment.status == "completed"
    ).all()
    
    candidates_data = []
    
    for assessment in assessments:
        candidate = assessment.candidate
        user = candidate.user
        evaluation = db.query(FinalEvaluation).filter(
            FinalEvaluation.candidate_id == candidate.id,
            FinalEvaluation.job_id == job_id
        ).first()
        
        candidates_data.append({
            "candidate_id": candidate.id,
            "name": user.full_name,
            "email": user.email,
            "ranking": candidate.ranking,
            "total_score": assessment.total_score,
            "technical_score": assessment.technical_score,
            "psychometric_score": assessment.psychometric_score,
            "recommendation": evaluation.recommendation if evaluation else "pending",
            "final_score": evaluation.final_score if evaluation else 0,
            "integrity_score": evaluation.integrity_score if evaluation else 100
        })
    
    # Sort by ranking and score
    ranking_order = {"high_match": 0, "potential": 1, "reject": 2}
    candidates_data.sort(key=lambda x: (
        ranking_order.get(x["ranking"], 3),
        -x["final_score"]
    ))
    
    # Group by category
    return {
        "high_match": [c for c in candidates_data if c["ranking"] == "high_match"],
        "potential": [c for c in candidates_data if c["ranking"] == "potential"],
        "reject": [c for c in candidates_data if c["ranking"] == "reject"]
    }

# ============ DASHBOARD ============

@router.get("/dashboard")
async def get_recruiter_dashboard(
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Get recruiter dashboard with overview stats"""
    # Get jobs
    jobs = db.query(JobDescription).filter(
        JobDescription.recruiter_id == current_user.id
    ).all()
    
    # Get all candidates
    total_candidates = db.query(CandidateProfile).count()
    
    # Get by status
    status_counts = {
        "pending": db.query(CandidateProfile).filter(CandidateProfile.status == "pending").count(),
        "in_progress": db.query(CandidateProfile).filter(CandidateProfile.status == "in_progress").count(),
        "completed": db.query(CandidateProfile).filter(CandidateProfile.status == "completed").count()
    }
    
    # Get by ranking
    ranking_counts = {
        "high_match": db.query(CandidateProfile).filter(CandidateProfile.ranking == "high_match").count(),
        "potential": db.query(CandidateProfile).filter(CandidateProfile.ranking == "potential").count(),
        "reject": db.query(CandidateProfile).filter(CandidateProfile.ranking == "reject").count()
    }
    
    # Recent evaluations
    recent_evaluations = db.query(FinalEvaluation).order_by(
        FinalEvaluation.created_at.desc()
    ).limit(10).all()
    
    return {
        "jobs_count": len(jobs),
        "active_jobs": sum(1 for j in jobs if j.is_active),
        "total_candidates": total_candidates,
        "status_breakdown": status_counts,
        "ranking_breakdown": ranking_counts,
        "jobs": [{
            "id": j.id,
            "title": j.title,
            "is_active": j.is_active,
            "applications": db.query(Assessment).filter(Assessment.job_id == j.id).count()
        } for j in jobs],
        "recent_evaluations": [{
            "candidate_id": e.candidate_id,
            "recommendation": e.recommendation,
            "final_score": e.final_score,
            "created_at": e.created_at
        } for e in recent_evaluations]
    }
