from pydantic import BaseModel, Field
from typing import List

class StrategyReview(BaseModel):
    is_approved: bool = Field(description="True if the strategy is approved, False otherwise.")
    score: int = Field(description="Score out of 100 for the strategy.")
    critical_flaws: List[str] = Field(description="List of critical flaws in the strategy.", default_factory=list)
    optimization_ideas: List[str] = Field(description="List of optimization ideas.", default_factory=list)
