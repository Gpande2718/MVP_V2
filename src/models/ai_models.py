from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import os
from ..grading.criteria import GradingCriterion, GradingSchema

class GradingResult(BaseModel):
    points: float = Field(description="Points awarded for this criterion")
    explanation: str = Field(description="Detailed explanation for the points awarded")
    confidence: float = Field(description="Confidence score between 0 and 1")

class AIGrader:
    """Handles the AI-based grading using multiple LLM models."""
    
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.0):
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature
        )
        self.output_parser = PydanticOutputParser(pydantic_object=GradingResult)
        
    def grade_submission(
        self,
        submission_text: str,
        criterion: GradingCriterion,
    ) -> GradingResult:
        """
        Grade a single submission against a specific criterion.
        
        Args:
            submission_text: The text content to grade
            criterion: The grading criterion to apply
            
        Returns:
            GradingResult containing points, explanation, and confidence
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert grader. Grade the following submission according 
            to the provided criterion. Be objective and thorough in your assessment."""),
            ("user", """
            Criterion: {criterion_name}
            Description: {criterion_description}
            Maximum Points: {max_points}
            
            Rubric:
            {rubric}
            
            Submission:
            {submission}
            
            Grade this submission and provide:
            1. Points awarded (between 0 and {max_points})
            2. Detailed explanation
            3. Confidence score (between 0 and 1)
            
            {format_instructions}
            """)
        ])
        
        rubric_text = "\n".join([f"- {points}: {desc}" 
                                for points, desc in criterion.rubric.items()])
        
        formatted_prompt = prompt.format_messages(
            criterion_name=criterion.name,
            criterion_description=criterion.description,
            max_points=criterion.max_points,
            rubric=rubric_text,
            submission=submission_text,
            format_instructions=self.output_parser.get_format_instructions()
        )
        
        response = self.llm.invoke(formatted_prompt)
        return self.output_parser.parse(response.content)

class ConsensusGrader:
    """Manages multiple AI models and determines consensus grades."""
    
    def __init__(self, models: List[AIGrader]):
        self.models = models
        
    def grade_with_consensus(
        self,
        submission_text: str,
        criterion: GradingCriterion,
        min_confidence: float = 0.7
    ) -> Optional[GradingResult]:
        """
        Grade submission using multiple models and determine consensus.
        
        Args:
            submission_text: Text to grade
            criterion: Grading criterion to apply
            min_confidence: Minimum confidence threshold
            
        Returns:
            Consensus GradingResult or None if no consensus reached
        """
        results = []
        for model in self.models:
            result = model.grade_submission(submission_text, criterion)
            if result.confidence >= min_confidence:
                results.append(result)
                
        if not results:
            return None
            
        # Calculate weighted average based on confidence
        total_weight = sum(r.confidence for r in results)
        weighted_points = sum(r.points * r.confidence for r in results) / total_weight
        
        # Combine explanations
        combined_explanation = "\n".join([
            f"Model {i+1} ({r.confidence:.2f} confidence): {r.explanation}"
            for i, r in enumerate(results)
        ])
        
        # Calculate overall confidence
        avg_confidence = sum(r.confidence for r in results) / len(results)
        
        return GradingResult(
            points=round(weighted_points, 2),
            explanation=combined_explanation,
            confidence=avg_confidence
        ) 