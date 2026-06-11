from typing import Dict, List, Literal
from pydantic import BaseModel, Field, ConfigDict

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

class SuccessMetric(BaseModel):
    metric_name: str = Field(description="The KPI name, e.g., 'KPI' or 'Target'")
    metric_value: str = Field(description="The value, e.g., 'Impressions' or '5000'")


class Goal(BaseModel):
    goal: str | None = None 
    success_metrics: List[SuccessMetric] = Field(
        default_factory=lambda: [
            SuccessMetric(metric_name="KPI", metric_value="Impressions")
        ]
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
    summary: str | None = Field(
        None, 
        description=(
            "A comprehensive paragraph summarizing the entire marketing campaign strategy. "
            "This narrative must seamlessly integrate who the target audience is, the primary "
            "campaign goals, and how the content direction/posting strategy will be used to achieve them."
        )
    )
    timeline: Timeline = Field(default_factory=Timeline)
    target_audience: TargetAudience = Field(default_factory=TargetAudience)
    key_messages: List[str] = Field(default_factory=list)
    goal: Goal = Field(default_factory=Goal)
    content_direction: ContentDirection = Field(
        default_factory=ContentDirection
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Summer Launch 2026",
                "summary": "This Q3 product marketing campaign targets urban, tech-savvy young professionals (ages 18-35) to drive user acquisition and secure 5,000 new signups. To achieve this goal, our strategy relies on deploying a high-frequency, modern, and casual content direction across primary channels on Mondays, Wednesdays, and Fridays. By focusing our visual theme on minimalism and emphasizing speed and affordability, the content is systematically designed to engage this specific demographic during peak commuting hours.",
                "timeline": {"duration_in_weeks": 4},
                "target_audience": {
                    "age_range": "18-35",
                    "gender": "All",
                    "interests": ["tech", "fitness"],
                    "demographics": ["urban"],
                    "income": "Medium",
                },
                "key_messages": ["Fast", "Reliable", "Affordable"],
                "success_metrics": [
                        {"metric_name": "KPI", "metric_value": "Signups"},
                        {"metric_name": "Target", "metric_value": "5000"}
                    ],
                "content_direction": {
                    "tone": "Casual",
                    "style": ["Modern"],
                    "visual_theme": ["Minimalist"],
                    "posting_strategy": {
                        "frequency_per_week": 3,
                        "posting_hours": ["09:00", "18:00"],
                        "posting_days": ["Monday", "Wednesday", "Friday"],
                    },
                },
            }
        }
    )
