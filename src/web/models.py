from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class ReviewSubmission(BaseModel):
    """Model for submissions that need review."""
    submission_id: str
    submission_text: str
    original_grade: float
    confidence_score: float
    review_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    
class GradeAdjustment(BaseModel):
    """Model for grade adjustments made during review."""
    submission_id: str
    criterion_name: str
    original_points: float
    adjusted_points: float
    adjustment_reason: str
    reviewer: str 