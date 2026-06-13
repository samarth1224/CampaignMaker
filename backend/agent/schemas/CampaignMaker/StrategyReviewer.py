from typing import List
from pydantic import BaseModel, Field


class FeedbackItem(BaseModel):
    field_path: str = Field(
        description="The exact field being critiqued (e.g., 'content_direction.tone')"
    )
    issue: str = Field(
        description="What is wrong or missing in this specific section."
    )
    suggestion: str = Field(
        description="Exact actionable advice on how the generator agent can fix it."
    )


class StrategyReview(BaseModel):
    is_approved: bool = Field(
        description="True if the campaign strategy meets all quality standards and is ready to launch."
    )
    score: int = Field(
        description="Overall campaign quality score from 1 to 100."
    )
    critical_flaws: List[FeedbackItem] = Field(
        default_factory=list,
        description="List of issues that MUST be fixed before approval.",
    )
    optimization_ideas: List[FeedbackItem] = Field(
        default_factory=list,
        description="Minor suggestions to make an already good strategy even better.",
    )
