from typing import Dict
from .criteria import GradingSchema, GradingCriterion

def load_grading_schema(assignment_id: str) -> GradingSchema:
    """
    Load grading schema for an assignment (temporary mock implementation).
    In production, this would load from a database.
    """
    # Mock schema for testing
    schema = GradingSchema(name=f"Assignment {assignment_id}", total_points=100)
    
    # Add some sample criteria
    criteria = [
        GradingCriterion(
            name="Understanding",
            description="Demonstrates understanding of core concepts",
            max_points=40,
            rubric={
                "40": "Excellent understanding",
                "30": "Good understanding",
                "20": "Fair understanding",
                "10": "Limited understanding",
                "0": "No understanding shown"
            }
        ),
        GradingCriterion(
            name="Implementation",
            description="Quality of implementation",
            max_points=60,
            rubric={
                "60": "Excellent implementation",
                "45": "Good implementation",
                "30": "Fair implementation",
                "15": "Poor implementation",
                "0": "No implementation"
            }
        )
    ]
    
    for criterion in criteria:
        schema.add_criterion(criterion)
        
    return schema 