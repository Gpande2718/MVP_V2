from typing import Dict, List, Optional
from .criteria import GradingCriterion, GradingSchema
from ..models.ai_models import ConsensusGrader, GradingResult
from dataclasses import dataclass

@dataclass
class AssignmentGrade:
    """Represents the complete grade for an assignment."""
    total_points: float
    criterion_grades: Dict[str, GradingResult]
    overall_confidence: float
    needs_review: bool
    
class AssignmentGrader:
    """Handles the complete grading process for assignments."""
    
    def __init__(
        self,
        consensus_grader: ConsensusGrader,
        confidence_threshold: float = 0.7,
        consistency_threshold: float = 0.2
    ):
        self.consensus_grader = consensus_grader
        self.confidence_threshold = confidence_threshold
        self.consistency_threshold = consistency_threshold
        
    def grade_assignment(
        self,
        submission_text: str,
        schema: GradingSchema
    ) -> AssignmentGrade:
        """
        Grade an assignment according to the provided schema.
        
        Args:
            submission_text: The submission to grade
            schema: The grading schema to apply
            
        Returns:
            AssignmentGrade containing complete grading results
        """
        criterion_grades: Dict[str, GradingResult] = {}
        total_points = 0
        confidences = []
        needs_review = False
        
        for criterion in schema.criteria:
            result = self.consensus_grader.grade_with_consensus(
                submission_text,
                criterion,
                self.confidence_threshold
            )
            
            if result is None:
                needs_review = True
                continue
                
            criterion_grades[criterion.name] = result
            total_points += result.points
            confidences.append(result.confidence)
            
            # Check if the confidence is too low
            if result.confidence < self.confidence_threshold:
                needs_review = True
                
        # Calculate overall confidence
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return AssignmentGrade(
            total_points=total_points,
            criterion_grades=criterion_grades,
            overall_confidence=overall_confidence,
            needs_review=needs_review
        ) 