from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"
    ADMIN = "admin"

class CandidateStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    HIRED = "hired"
    REJECTED = "rejected"

class RankingCategory(str, enum.Enum):
    HIGH_MATCH = "high_match"
    POTENTIAL = "potential"
    REJECT = "reject"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.CANDIDATE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    candidate_profile = relationship("CandidateProfile", back_populates="user", uselist=False)
    job_descriptions = relationship("JobDescription", back_populates="recruiter")

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    resume_path = Column(String(500))
    parsed_resume = Column(JSON)  # Extracted skills, education, experience
    status = Column(String(50), default=CandidateStatus.PENDING)
    ranking = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="candidate_profile")
    assessments = relationship("Assessment", back_populates="candidate")
    proctoring_events = relationship("ProctoringEvent", back_populates="candidate")
    final_evaluation = relationship("FinalEvaluation", back_populates="candidate", uselist=False)

class JobDescription(Base):
    __tablename__ = "job_descriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    required_skills = Column(JSON)  # List of required skills
    preferred_skills = Column(JSON)  # List of preferred skills
    min_experience_years = Column(Integer, default=0)
    education_requirements = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    recruiter = relationship("User", back_populates="job_descriptions")
    assessments = relationship("Assessment", back_populates="job")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=True)
    question_type = Column(String(50))  # mcq, coding, text, slider
    category = Column(String(50))  # technical, psychometric
    difficulty = Column(String(20))  # easy, medium, hard
    question_text = Column(Text, nullable=False)
    options = Column(JSON)  # For MCQ: list of options
    correct_answer = Column(Text)  # For MCQ: correct option index/text
    test_cases = Column(JSON)  # For coding: input/output test cases
    max_score = Column(Float, default=10.0)
    time_limit_seconds = Column(Integer, default=300)
    skill_tags = Column(JSON)  # Skills this question tests
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    responses = relationship("QuestionResponse", back_populates="question")

class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidate_profiles.id"))
    job_id = Column(Integer, ForeignKey("job_descriptions.id"))
    status = Column(String(50), default="not_started")  # not_started, in_progress, completed
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    technical_score = Column(Float, default=0.0)
    psychometric_score = Column(Float, default=0.0)
    total_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate = relationship("CandidateProfile", back_populates="assessments")
    job = relationship("JobDescription", back_populates="assessments")
    responses = relationship("QuestionResponse", back_populates="assessment")

class QuestionResponse(Base):
    __tablename__ = "question_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    response_text = Column(Text)  # For text/coding responses
    selected_option = Column(Integer)  # For MCQ
    slider_value = Column(Float)  # For slider inputs
    code_output = Column(Text)  # For coding: execution output
    is_correct = Column(Boolean)
    score = Column(Float, default=0.0)
    time_taken_seconds = Column(Integer)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    assessment = relationship("Assessment", back_populates="responses")
    question = relationship("Question", back_populates="responses")

class ProctoringEvent(Base):
    __tablename__ = "proctoring_events"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidate_profiles.id"))
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    event_type = Column(String(100))  # multiple_faces, no_face, tab_switch, copy_paste, keyboard_shortcut
    severity = Column(String(20))  # low, medium, high
    description = Column(Text)
    screenshot_path = Column(String(500))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate = relationship("CandidateProfile", back_populates="proctoring_events")

class FinalEvaluation(Base):
    __tablename__ = "final_evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidate_profiles.id"), unique=True)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"))
    recommendation = Column(String(50))  # hire, no_hire, consider
    rationale = Column(Text)  # Explainable AI: text justification
    technical_breakdown = Column(JSON)  # Competency mapping
    psychometric_breakdown = Column(JSON)
    strengths = Column(JSON)
    weaknesses = Column(JSON)
    resume_match_score = Column(Float)
    assessment_score = Column(Float)
    integrity_score = Column(Float)  # Based on proctoring
    final_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate = relationship("CandidateProfile", back_populates="final_evaluation")
