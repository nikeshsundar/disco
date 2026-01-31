from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    role: str = "candidate"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Job Description Schemas
class JobDescriptionCreate(BaseModel):
    title: str
    description: str
    required_skills: List[str]
    preferred_skills: Optional[List[str]] = []
    min_experience_years: int = 0
    education_requirements: Optional[List[str]] = []

class JobDescriptionResponse(JobDescriptionCreate):
    id: int
    recruiter_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Question Schemas
class QuestionCreate(BaseModel):
    job_id: Optional[int] = None
    question_type: str  # mcq, coding, text, slider
    category: str  # technical, psychometric
    difficulty: str = "medium"
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    test_cases: Optional[List[dict]] = None
    max_score: float = 10.0
    time_limit_seconds: int = 300
    skill_tags: Optional[List[str]] = []

class QuestionResponse(BaseModel):
    id: int
    question_type: str
    category: str
    difficulty: str
    question_text: str
    options: Optional[List[str]]
    max_score: float
    time_limit_seconds: int
    skill_tags: Optional[List[str]]
    
    class Config:
        from_attributes = True

# Assessment Schemas
class AssessmentCreate(BaseModel):
    job_id: int

class AssessmentResponse(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    status: str
    technical_score: float
    psychometric_score: float
    total_score: float
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Question Response Schemas
class SubmitResponseBase(BaseModel):
    question_id: int
    response_text: Optional[str] = None
    selected_option: Optional[int] = None
    slider_value: Optional[float] = None
    time_taken_seconds: int = 0

class SubmitResponse(SubmitResponseBase):
    assessment_id: int

class QuestionResponseResult(BaseModel):
    id: int
    question_id: int
    is_correct: Optional[bool]
    score: float
    code_output: Optional[str]
    
    class Config:
        from_attributes = True

# Resume Schemas
class ParsedResume(BaseModel):
    skills: List[str]
    experience_years: float
    education: List[dict]
    work_experience: List[dict]
    contact_info: dict
    raw_text: str

class ResumeMatchResult(BaseModel):
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    experience_match: bool
    education_match: bool
    ranking: str

# Proctoring Schemas
class ProctoringEventCreate(BaseModel):
    assessment_id: int
    event_type: str
    severity: str
    description: str

class ProctoringEventResponse(BaseModel):
    id: int
    event_type: str
    severity: str
    description: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Final Evaluation Schemas
class FinalEvaluationResponse(BaseModel):
    id: int
    recommendation: str
    rationale: str
    technical_breakdown: dict
    psychometric_breakdown: dict
    strengths: List[str]
    weaknesses: List[str]
    resume_match_score: float
    assessment_score: float
    integrity_score: float
    final_score: float
    created_at: datetime
    
    class Config:
        from_attributes = True

# Candidate Dashboard
class CandidateProfileResponse(BaseModel):
    id: int
    user_id: int
    status: str
    ranking: Optional[str]
    parsed_resume: Optional[dict]
    
    class Config:
        from_attributes = True

class CandidateDashboard(BaseModel):
    profile: CandidateProfileResponse
    user: UserResponse
    assessments: List[AssessmentResponse]
    final_evaluation: Optional[FinalEvaluationResponse]

# Code Execution
class CodeExecutionRequest(BaseModel):
    code: str
    language: str = "python"
    test_cases: Optional[List[dict]] = None

class CodeExecutionResult(BaseModel):
    success: bool
    output: str
    error: Optional[str]
    test_results: Optional[List[dict]]
    execution_time_ms: float
