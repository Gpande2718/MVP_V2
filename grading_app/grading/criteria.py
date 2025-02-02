from typing import Dict, List, Union
from dataclasses import dataclass

@dataclass
class GradingCriterion:
    """Represents a single grading criterion."""
    name: str
    description: str
    max_points: float
    rubric: Dict[str, str]  # Maps point values to descriptions
    
class GradingSchema:
    """Defines the complete grading schema for an assignment."""
    
    def __init__(self, name: str, total_points: float):
        self.name = name
        self.total_points = total_points
        self.criteria: List[GradingCriterion] = []
        
    def add_criterion(self, criterion: GradingCriterion) -> None:
        """Add a grading criterion to the schema."""
        current_total = sum(c.max_points for c in self.criteria)
        if current_total + criterion.max_points > self.total_points:
            raise ValueError("Total points would exceed maximum")
        self.criteria.append(criterion)
        
    def validate(self) -> bool:
        """
        Validate that the grading schema is complete and consistent.
        Returns True if valid, raises ValueError if not.
        """
        total = sum(c.max_points for c in self.criteria)
        if total != self.total_points:
            raise ValueError(
                f"Total points ({total}) don't match expected total ({self.total_points})"
            )
        return True 