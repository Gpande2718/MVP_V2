from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List, Dict
import os
from datetime import datetime

from ..grading.grader import AssignmentGrader, AssignmentGrade
from ..models.ai_models import ConsensusGrader, AIGrader
from .models import ReviewSubmission, GradeAdjustment
from ..grading.schema_loader import load_grading_schema

app = FastAPI(title="Assignment Grading System")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize grading components
models = [
    AIGrader(model_name="gpt-4"),
    AIGrader(model_name="gpt-3.5-turbo"),
]
consensus_grader = ConsensusGrader(models)
assignment_grader = AssignmentGrader(consensus_grader)

# In-memory storage (replace with database in production)
flagged_submissions: Dict[str, ReviewSubmission] = {}
grade_adjustments: List[GradeAdjustment] = []

@app.post("/grade")
async def grade_submission(
    submission_text: str,
    assignment_id: str,
    token: str = Depends(oauth2_scheme)
):
    """Grade a new submission."""
    try:
        # Load grading schema for this assignment (implement this)
        schema = load_grading_schema(assignment_id)
        
        # Grade the submission
        grade_result = assignment_grader.grade_assignment(submission_text, schema)
        
        # If needs review, add to flagged submissions
        if grade_result.needs_review:
            submission_id = f"sub_{len(flagged_submissions) + 1}"
            flagged_submissions[submission_id] = ReviewSubmission(
                submission_id=submission_id,
                submission_text=submission_text,
                original_grade=grade_result.total_points,
                confidence_score=grade_result.overall_confidence
            )
        
        return {
            "grade": grade_result.total_points,
            "confidence": grade_result.overall_confidence,
            "needs_review": grade_result.needs_review,
            "criterion_grades": grade_result.criterion_grades
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/flagged-submissions")
async def get_flagged_submissions(
    token: str = Depends(oauth2_scheme)
) -> List[ReviewSubmission]:
    """Get all submissions that need review."""
    return list(flagged_submissions.values())

@app.post("/review-submission")
async def review_submission(
    adjustment: GradeAdjustment,
    token: str = Depends(oauth2_scheme)
):
    """Submit a grade adjustment after review."""
    if adjustment.submission_id not in flagged_submissions:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    # Record the adjustment
    grade_adjustments.append(adjustment)
    
    # Update the review status
    submission = flagged_submissions[adjustment.submission_id]
    submission.reviewed_at = datetime.now()
    submission.reviewed_by = adjustment.reviewer
    submission.review_notes = adjustment.adjustment_reason
    
    return {"message": "Grade adjustment recorded successfully"}

@app.get("/review-statistics")
async def get_review_statistics(
    token: str = Depends(oauth2_scheme)
):
    """Get statistics about the review process."""
    total_flagged = len(flagged_submissions)
    total_reviewed = len([s for s in flagged_submissions.values() if s.reviewed_at])
    total_adjustments = len(grade_adjustments)
    
    return {
        "total_flagged": total_flagged,
        "total_reviewed": total_reviewed,
        "total_adjustments": total_adjustments,
        "review_completion_rate": total_reviewed / total_flagged if total_flagged > 0 else 0
    } 