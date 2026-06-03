from typing import Dict, List, Literal
from pydantic import BaseModel, Field




# Created a type alias for days of the week to keep code clean
Weekday = Literal[
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


class Timeline(BaseModel):
    duration_in_weeks: int = 2


class TargetAudience(BaseModel):
    age_range: str = "18-35"
    gender: Literal["All", "Male", "Female", "Non-binary"] = "All"
    interests: List[str] = Field(default_factory=list)
    demographics: List[str] = Field(default_factory=list)
    income: Literal["Low", "Medium", "High"] = "Medium"


class Goal(BaseModel):
    goal: str | None = None 
    success_metrics: Dict[str, str] = Field(
        default_factory=lambda: {"KPI": "Impressions"}
    )


class PostingStrategy(BaseModel):
    frequency_per_week: int = 3
    posting_hours: List[str] = Field(
        default_factory=lambda: ["09:00", "17:00"]
    )
    posting_days: List[Weekday] = Field(
        default_factory=lambda: ["Monday", "Wednesday", "Friday"]
    )


class ContentDirection(BaseModel):
    tone: str | None = None
    style: List[str] | None = None
    visual_theme: List[str] | None = None
    posting_strategy: PostingStrategy | None = None


class CampaignStrategy(BaseModel):
    name: str | None = None
    summary: str | None = None
    timeline: Timeline = Field(default_factory=Timeline)
    target_audience: TargetAudience = Field(default_factory=TargetAudience)
    key_messages: List[str] = Field(default_factory=list)
    goal: Goal = Field(default_factory=Goal)
    content_direction: ContentDirection = Field(
        default_factory=ContentDirection
    )

