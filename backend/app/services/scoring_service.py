from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.models import (
    Assessment, QuestionResponse, Question, CandidateProfile,
    ProctoringEvent, FinalEvaluation, JobDescription
)

# Psychometric question scoring logic
PSYCHOMETRIC_SCORING = {
    # For scenario-based MCQs (higher = better response)
    "leadership": {
        "weights": [0.2, 0.4, 0.6, 0.8, 1.0],
        "ideal_range": (0.7, 1.0)
    },
    "resilience": {
        "weights": [0.2, 0.4, 0.6, 0.8, 1.0],
        "ideal_range": (0.6, 1.0)
    },
    "teamwork": {
        "weights": [0.2, 0.4, 0.6, 0.8, 1.0],
        "ideal_range": (0.6, 1.0)
    },
    "emotional_intelligence": {
        "weights": [0.2, 0.4, 0.6, 0.8, 1.0],
        "ideal_range": (0.7, 1.0)
    },
    "culture_fit": {
        "weights": [0.2, 0.4, 0.6, 0.8, 1.0],
        "ideal_range": (0.5, 1.0)
    }
}

def score_mcq_response(question: Question, selected_option: int) -> Dict[str, Any]:
    """Score MCQ response"""
    correct_answer = question.correct_answer
    options = question.options or []
    
    try:
        correct_index = int(correct_answer) if correct_answer.isdigit() else options.index(correct_answer)
    except (ValueError, AttributeError):
        correct_index = 0
    
    is_correct = selected_option == correct_index
    score = question.max_score if is_correct else 0
    
    return {
        "is_correct": is_correct,
        "score": score,
        "max_score": question.max_score
    }

def score_coding_response(question: Question, code_result: Dict[str, Any]) -> Dict[str, Any]:
    """Score coding response based on test case results"""
    test_results = code_result.get("test_results", [])
    
    if not test_results:
        # If no test cases, binary scoring based on execution success
        return {
            "is_correct": code_result.get("success", False),
            "score": question.max_score if code_result.get("success") else 0,
            "max_score": question.max_score
        }
    
    # Calculate score based on test cases passed
    passed = sum(1 for t in test_results if t.get("passed", False))
    total = len(test_results)
    
    score_ratio = passed / total if total > 0 else 0
    score = round(question.max_score * score_ratio, 2)
    
    return {
        "is_correct": passed == total,
        "score": score,
        "max_score": question.max_score,
        "tests_passed": passed,
        "tests_total": total
    }

def score_text_response(question: Question, response_text: str) -> Dict[str, Any]:
    """
    Score text response using keyword matching and length analysis.
    In production, this could use NLP/LLM for better evaluation.
    """
    if not response_text:
        return {"is_correct": False, "score": 0, "max_score": question.max_score}
    
    # Basic scoring criteria
    word_count = len(response_text.split())
    
    # Check for relevant keywords from skill tags
    skill_tags = question.skill_tags or []
    keywords_found = sum(1 for tag in skill_tags if tag.lower() in response_text.lower())
    
    # Scoring factors
    length_score = min(1.0, word_count / 100)  # Expect ~100 words for full points
    keyword_score = keywords_found / len(skill_tags) if skill_tags else 0.5
    
    # Combined score
    total_score = (length_score * 0.4 + keyword_score * 0.6) * question.max_score
    
    return {
        "is_correct": total_score >= question.max_score * 0.5,
        "score": round(total_score, 2),
        "max_score": question.max_score,
        "word_count": word_count,
        "keywords_found": keywords_found
    }

def score_slider_response(question: Question, slider_value: float) -> Dict[str, Any]:
    """Score slider response for psychometric assessment"""
    category = question.category
    skill_tags = question.skill_tags or []
    
    # Normalize slider value (assuming 1-5 scale)
    normalized_value = slider_value / 5.0
    
    # For psychometric questions, we're measuring preference/tendency
    # Not strictly "correct", but within ideal range
    score = normalized_value * question.max_score
    
    return {
        "is_correct": None,  # No right/wrong for psychometric
        "score": round(score, 2),
        "max_score": question.max_score,
        "normalized_value": normalized_value
    }

def calculate_assessment_scores(db: Session, assessment_id: int) -> Dict[str, Any]:
    """Calculate overall assessment scores"""
    responses = db.query(QuestionResponse).filter(
        QuestionResponse.assessment_id == assessment_id
    ).all()
    
    technical_scores = []
    psychometric_scores = []
    
    for response in responses:
        question = response.question
        if question.category == "technical":
            technical_scores.append({
                "score": response.score,
                "max_score": question.max_score,
                "type": question.question_type,
                "skills": question.skill_tags
            })
        else:
            psychometric_scores.append({
                "score": response.score,
                "max_score": question.max_score,
                "type": question.question_type,
                "skills": question.skill_tags
            })
    
    # Calculate averages
    tech_total = sum(s["score"] for s in technical_scores)
    tech_max = sum(s["max_score"] for s in technical_scores)
    tech_percentage = (tech_total / tech_max * 100) if tech_max > 0 else 0
    
    psycho_total = sum(s["score"] for s in psychometric_scores)
    psycho_max = sum(s["max_score"] for s in psychometric_scores)
    psycho_percentage = (psycho_total / psycho_max * 100) if psycho_max > 0 else 0
    
    # Overall score (weighted)
    overall = tech_percentage * 0.6 + psycho_percentage * 0.4
    
    return {
        "technical_score": round(tech_percentage, 2),
        "psychometric_score": round(psycho_percentage, 2),
        "total_score": round(overall, 2),
        "technical_breakdown": technical_scores,
        "psychometric_breakdown": psychometric_scores
    }

def calculate_integrity_score(db: Session, candidate_id: int, assessment_id: int) -> float:
    """Calculate integrity score based on proctoring events"""
    events = db.query(ProctoringEvent).filter(
        ProctoringEvent.candidate_id == candidate_id,
        ProctoringEvent.assessment_id == assessment_id
    ).all()
    
    if not events:
        return 100.0
    
    # Deduction rules
    deductions = {
        "multiple_faces": 15,
        "no_face": 10,
        "tab_switch": 5,
        "copy_paste": 8,
        "keyboard_shortcut": 3,
        "window_blur": 5,
        "right_click": 2
    }
    
    severity_multiplier = {
        "low": 0.5,
        "medium": 1.0,
        "high": 2.0
    }
    
    total_deduction = 0
    for event in events:
        base_deduction = deductions.get(event.event_type, 5)
        multiplier = severity_multiplier.get(event.severity, 1.0)
        total_deduction += base_deduction * multiplier
    
    # Cap deduction at 100
    integrity_score = max(0, 100 - total_deduction)
    return round(integrity_score, 2)

def generate_evaluation(
    db: Session,
    candidate_id: int,
    job_id: int,
    resume_match: Dict[str, Any],
    assessment_scores: Dict[str, Any],
    integrity_score: float
) -> Dict[str, Any]:
    """Generate final evaluation with rationale"""
    
    # Calculate final weighted score
    resume_weight = 0.25
    assessment_weight = 0.55
    integrity_weight = 0.20
    
    final_score = (
        resume_match.get("match_score", 0) * resume_weight +
        assessment_scores.get("total_score", 0) * assessment_weight +
        integrity_score * integrity_weight
    )
    
    # Determine recommendation
    if final_score >= 75 and integrity_score >= 70:
        recommendation = "hire"
    elif final_score >= 50 and integrity_score >= 50:
        recommendation = "consider"
    else:
        recommendation = "no_hire"
    
    # Generate rationale
    rationale_parts = []
    
    # Technical assessment analysis
    tech_score = assessment_scores.get("technical_score", 0)
    if tech_score >= 80:
        rationale_parts.append(f"Strong technical performance ({tech_score}%). Candidate demonstrated solid coding and problem-solving skills.")
    elif tech_score >= 60:
        rationale_parts.append(f"Adequate technical skills ({tech_score}%). Shows competency but may need mentoring in some areas.")
    else:
        rationale_parts.append(f"Technical assessment score of {tech_score}% indicates gaps in required skills.")
    
    # Psychometric analysis
    psycho_score = assessment_scores.get("psychometric_score", 0)
    if psycho_score >= 70:
        rationale_parts.append(f"Psychometric assessment ({psycho_score}%) indicates good cultural fit and soft skills.")
    elif psycho_score >= 50:
        rationale_parts.append(f"Psychometric score of {psycho_score}% shows moderate alignment with team values.")
    else:
        rationale_parts.append(f"Low psychometric score ({psycho_score}%) suggests potential challenges with team integration.")
    
    # Resume match analysis
    resume_score = resume_match.get("match_score", 0)
    if resume_match.get("missing_skills"):
        rationale_parts.append(f"Missing skills: {', '.join(resume_match['missing_skills'][:3])}.")
    
    # Integrity analysis
    if integrity_score < 70:
        rationale_parts.append(f"⚠️ Integrity concerns: Score of {integrity_score}% due to proctoring violations.")
    
    # Final recommendation text
    if recommendation == "hire":
        rationale_parts.append("RECOMMENDATION: Proceed with hiring. Candidate meets or exceeds requirements.")
    elif recommendation == "consider":
        rationale_parts.append("RECOMMENDATION: Consider for role. May benefit from additional interview or training.")
    else:
        rationale_parts.append("RECOMMENDATION: Not recommended for this role at this time.")
    
    # Identify strengths and weaknesses
    strengths = []
    weaknesses = []
    
    if tech_score >= 70:
        strengths.append("Strong technical foundation")
    else:
        weaknesses.append("Technical skills need improvement")
    
    if psycho_score >= 70:
        strengths.append("Good cultural fit and soft skills")
    else:
        weaknesses.append("May need soft skills development")
    
    if resume_match.get("experience_match"):
        strengths.append("Meets experience requirements")
    else:
        weaknesses.append("Below required experience level")
    
    if resume_match.get("matched_skills"):
        strengths.append(f"Has key skills: {', '.join(resume_match['matched_skills'][:3])}")
    
    if integrity_score >= 90:
        strengths.append("Excellent test integrity")
    elif integrity_score < 70:
        weaknesses.append("Integrity concerns during assessment")
    
    return {
        "recommendation": recommendation,
        "rationale": " ".join(rationale_parts),
        "final_score": round(final_score, 2),
        "resume_match_score": resume_score,
        "assessment_score": assessment_scores.get("total_score", 0),
        "integrity_score": integrity_score,
        "technical_breakdown": assessment_scores.get("technical_breakdown", {}),
        "psychometric_breakdown": assessment_scores.get("psychometric_breakdown", {}),
        "strengths": strengths,
        "weaknesses": weaknesses
    }
