from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime

from app.database import get_db
from app.models import (
    User, CandidateProfile, JobDescription, Assessment, 
    Question, QuestionResponse, FinalEvaluation
)
from app.schemas.schemas import (
    AssessmentCreate, AssessmentResponse, CandidateProfileResponse,
    CandidateDashboard, ParsedResume, ResumeMatchResult, FinalEvaluationResponse
)
from app.services.auth_service import get_current_user, get_current_candidate
from app.services.resume_service import parse_resume, parse_resume_from_bytes, match_resume_to_job
from app.services.scoring_service import (
    calculate_assessment_scores, calculate_integrity_score, generate_evaluation
)

router = APIRouter(prefix="/candidate", tags=["Candidate"])

UPLOAD_DIR = "uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Test endpoint - no auth required for testing
@router.post("/resume/parse-test")
async def parse_resume_test(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Parse resume without authentication (for testing)"""
    print(f"=== UPLOAD RECEIVED ===")
    print(f"Filename: {file.filename}")
    print(f"Content-Type: {file.content_type}")
    
    # Validate file type
    allowed_extensions = ['.pdf', '.docx', '.doc']
    file_ext = os.path.splitext(file.filename)[1].lower()
    print(f"Extension: {file_ext}")
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {allowed_extensions}"
        )
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"test_{file.filename}")
    try:
        content = await file.read()
        print(f"File size: {len(content)} bytes")
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        print(f"Saved to: {file_path}")
    except Exception as e:
        print(f"Save error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Parse resume
    try:
        print("Parsing resume...")
        parsed_data = parse_resume(file_path)
        print(f"Skills found: {len(parsed_data.get('skills', []))}")
        print(f"Skills: {parsed_data.get('skills', [])[:10]}")
        return {
            "message": "Resume parsed successfully",
            "parsed_data": parsed_data
        }
    except Exception as e:
        print(f"Parse error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")

@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """Get candidate dashboard with profile, assessments, and evaluation"""
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        # Create profile if it doesn't exist
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    assessments = db.query(Assessment).filter(
        Assessment.candidate_id == profile.id
    ).all()
    
    evaluation = db.query(FinalEvaluation).filter(
        FinalEvaluation.candidate_id == profile.id
    ).first()
    
    return {
        "profile": profile,
        "user": current_user,
        "assessments": assessments,
        "final_evaluation": evaluation
    }

@router.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """Upload and parse resume"""
    # Validate file type
    allowed_extensions = ['.pdf', '.docx', '.doc']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {allowed_extensions}"
        )
    
    # Read file content into memory
    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")
    
    # Parse resume from bytes (works on serverless)
    try:
        parsed_data = parse_resume_from_bytes(file_content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")
    
    # Update candidate profile
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        # Create profile if it doesn't exist
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    profile.resume_path = f"memory://{file.filename}"  # Mark as in-memory
    profile.parsed_resume = parsed_data
    db.commit()
    db.refresh(profile)
    
    return {
        "message": "Resume uploaded and parsed successfully",
        "parsed_data": parsed_data
    }

@router.get("/jobs", response_model=List[dict])
async def get_available_jobs(
    current_user: User = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """Get list of available job positions"""
    jobs = db.query(JobDescription).filter(JobDescription.is_active == True).all()
    
    # Get candidate's parsed resume for matching
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()
    
    result = []
    for job in jobs:
        job_dict = {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "required_skills": job.required_skills,
            "preferred_skills": job.preferred_skills,
            "min_experience_years": job.min_experience_years,
            "created_at": job.created_at
        }
        
        # Add match score if resume is available
        if profile and profile.parsed_resume:
            match_result = match_resume_to_job(profile.parsed_resume, {
                "required_skills": job.required_skills or [],
                "preferred_skills": job.preferred_skills or [],
                "min_experience_years": job.min_experience_years,
                "education_requirements": job.education_requirements or []
            })
            job_dict["match_score"] = match_result["match_score"]
            job_dict["ranking"] = match_result["ranking"]
        
        result.append(job_dict)
    
    return result

@router.post("/assessment/start")
async def start_assessment(
    data: AssessmentCreate,
    current_user: User = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """Start an assessment for a job"""
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Check if already has active assessment for this job
    existing = db.query(Assessment).filter(
        Assessment.candidate_id == profile.id,
        Assessment.job_id == data.job_id,
        Assessment.status != "completed"
    ).first()
    
    if existing:
        return {"assessment_id": existing.id, "message": "Continuing existing assessment"}
    
    # Create new assessment
    assessment = Assessment(
        candidate_id=profile.id,
        job_id=data.job_id,
        status="in_progress",
        started_at=datetime.utcnow()
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    # Update profile status
    profile.status = "in_progress"
    db.commit()
    
    return {"assessment_id": assessment.id, "message": "Assessment started"}

@router.get("/assessment/{assessment_id}/questions")
async def get_assessment_questions(
    assessment_id: int,
    current_user: User = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """Get questions for an assessment"""
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()
    
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.candidate_id == profile.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Get questions for this job
    questions = db.query(Question).filter(
        (Question.job_id == assessment.job_id) | (Question.job_id == None)
    ).all()
    
    # Get already answered question IDs
    answered_ids = {r.question_id for r in db.query(QuestionResponse).filter(
        QuestionResponse.assessment_id == assessment_id
    ).all()}
    
    # Format questions (hide correct answers)
    formatted_questions = []
    for q in questions:
        formatted_questions.append({
            "id": q.id,
            "question_type": q.question_type,
            "category": q.category,
            "difficulty": q.difficulty,
            "question_text": q.question_text,
            "options": q.options,
            "max_score": q.max_score,
            "time_limit_seconds": q.time_limit_seconds,
            "skill_tags": q.skill_tags,
            "is_answered": q.id in answered_ids
        })
    
    return {
        "assessment_id": assessment_id,
        "status": assessment.status,
        "questions": formatted_questions,
        "total_questions": len(questions),
        "answered_questions": len(answered_ids)
    }

@router.get("/assessment/{assessment_id}/status")
async def get_assessment_status(
    assessment_id: int,
    current_user: User = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """Get assessment status and scores"""
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()
    
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.candidate_id == profile.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    return {
        "id": assessment.id,
        "status": assessment.status,
        "technical_score": assessment.technical_score,
        "psychometric_score": assessment.psychometric_score,
        "total_score": assessment.total_score,
        "started_at": assessment.started_at,
        "completed_at": assessment.completed_at
    }

@router.post("/assessment/{assessment_id}/complete")
async def complete_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """Complete an assessment and generate final evaluation"""
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()
    
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.candidate_id == profile.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Calculate scores
    scores = calculate_assessment_scores(db, assessment_id)
    integrity = calculate_integrity_score(db, profile.id, assessment_id)
    
    # Update assessment
    assessment.status = "completed"
    assessment.completed_at = datetime.utcnow()
    assessment.technical_score = scores["technical_score"]
    assessment.psychometric_score = scores["psychometric_score"]
    assessment.total_score = scores["total_score"]
    
    # Get job for resume matching
    job = db.query(JobDescription).filter(
        JobDescription.id == assessment.job_id
    ).first()
    
    # Calculate resume match
    resume_match = {}
    if profile.parsed_resume and job:
        resume_match = match_resume_to_job(profile.parsed_resume, {
            "required_skills": job.required_skills or [],
            "preferred_skills": job.preferred_skills or [],
            "min_experience_years": job.min_experience_years,
            "education_requirements": job.education_requirements or []
        })
    
    # Generate final evaluation
    evaluation_data = generate_evaluation(
        db, profile.id, assessment.job_id, resume_match, scores, integrity
    )
    
    # Save or update final evaluation
    existing_eval = db.query(FinalEvaluation).filter(
        FinalEvaluation.candidate_id == profile.id
    ).first()
    
    if existing_eval:
        for key, value in evaluation_data.items():
            setattr(existing_eval, key, value)
        existing_eval.job_id = assessment.job_id
    else:
        final_eval = FinalEvaluation(
            candidate_id=profile.id,
            job_id=assessment.job_id,
            **evaluation_data
        )
        db.add(final_eval)
    
    # Update profile status and ranking
    profile.status = "completed"
    profile.ranking = resume_match.get("ranking", "potential")
    
    db.commit()
    
    return {
        "message": "Assessment completed",
        "scores": scores,
        "integrity_score": integrity,
        "evaluation": evaluation_data
    }

@router.get("/evaluation")
async def get_my_evaluation(
    current_user: User = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """Get candidate's final evaluation"""
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()
    
    evaluation = db.query(FinalEvaluation).filter(
        FinalEvaluation.candidate_id == profile.id
    ).first()
    
    if not evaluation:
        raise HTTPException(status_code=404, detail="No evaluation found")
    
    return evaluation
