from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import Question, Assessment, QuestionResponse
from app.schemas.schemas import SubmitResponse, QuestionResponseResult, CodeExecutionRequest
from app.services.auth_service import get_current_user, get_current_candidate
from app.services.code_executor import execute_code, validate_code_syntax
from app.services.scoring_service import (
    score_mcq_response, score_coding_response, 
    score_text_response, score_slider_response
)

router = APIRouter(prefix="/assessment", tags=["Assessment"])

@router.post("/submit-response", response_model=QuestionResponseResult)
async def submit_question_response(
    data: SubmitResponse,
    current_user = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """Submit a response to a question"""
    # Get question
    question = db.query(Question).filter(Question.id == data.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if already answered
    existing = db.query(QuestionResponse).filter(
        QuestionResponse.assessment_id == data.assessment_id,
        QuestionResponse.question_id == data.question_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Question already answered")
    
    # Score based on question type
    score_result = {"is_correct": False, "score": 0}
    code_output = None
    
    if question.question_type == "mcq":
        score_result = score_mcq_response(question, data.selected_option)
    
    elif question.question_type == "coding":
        # Execute code
        exec_result = execute_code(
            data.response_text,
            "python",
            question.test_cases
        )
        score_result = score_coding_response(question, exec_result)
        code_output = exec_result.get("output", "") + (exec_result.get("error") or "")
    
    elif question.question_type == "text":
        score_result = score_text_response(question, data.response_text)
    
    elif question.question_type == "slider":
        score_result = score_slider_response(question, data.slider_value)
    
    # Save response
    response = QuestionResponse(
        assessment_id=data.assessment_id,
        question_id=data.question_id,
        response_text=data.response_text,
        selected_option=data.selected_option,
        slider_value=data.slider_value,
        code_output=code_output,
        is_correct=score_result.get("is_correct"),
        score=score_result.get("score", 0),
        time_taken_seconds=data.time_taken_seconds
    )
    db.add(response)
    db.commit()
    db.refresh(response)
    
    return response

@router.post("/execute-code")
async def execute_code_endpoint(
    data: CodeExecutionRequest,
    current_user = Depends(get_current_candidate)
):
    """Execute code in sandbox (for practice/testing)"""
    # Validate syntax first
    syntax_check = validate_code_syntax(data.code, data.language)
    if not syntax_check.get("valid"):
        return {
            "success": False,
            "output": "",
            "error": syntax_check.get("error"),
            "test_results": [],
            "execution_time_ms": 0
        }
    
    result = execute_code(data.code, data.language, data.test_cases)
    return result

@router.get("/question/{question_id}")
async def get_question(
    question_id: int,
    current_user = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """Get a specific question (without correct answer)"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return {
        "id": question.id,
        "question_type": question.question_type,
        "category": question.category,
        "difficulty": question.difficulty,
        "question_text": question.question_text,
        "options": question.options,
        "max_score": question.max_score,
        "time_limit_seconds": question.time_limit_seconds,
        "skill_tags": question.skill_tags
    }
