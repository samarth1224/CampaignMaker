"""Campaign Beanie document — single collection, embedded sub-documents.

The ``Campaign`` document is the aggregate root for everything related
to a single campaign run.  Agent-produced schemas (like
``CampaignStrategy``) are embedded directly so there is zero field
duplication between the agent layer and the persistence layer.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Literal, Optional

from beanie import Document
from pydantic import BaseModel, Field

# ── Re-use agent schemas as embedded sub-documents ───────────────────────────
from agent.schemas.CampaignMaker.CampaignMaker import CampaignStrategy
from agent.schemas.ContentGenerator.ContentGenerator import PostContent, BasePost


# ─── Chat history ────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    """A single message in the campaign conversation."""

    role: Literal["user", "assistant"] = "user"
    content: str = ""
    author: str | None = None
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ─── Generated content per platform ─────────────────────────────────────────

class PlatformContent(BaseModel):
    """Content generated for a single platform (e.g. Twitter)."""

    platform: str = ""
    posts: List[BasePost] = Field(default_factory=list)
    media: List[PostContent] = Field(default_factory=list)


# ─── Campaign document (MongoDB collection: "campaigns") ────────────────────

class Campaign(Document):
    """Top-level Beanie document — one doc per campaign run."""

    campaign_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    title: str = "Untitled Campaign"
    status: Literal["draft", "generating", "completed", "failed"] = "draft"

    # Strategy produced by the campaign_maker loop agent
    strategy: Optional[CampaignStrategy] = None

    # Generated content, grouped by platform
    content: List[PlatformContent] = Field(default_factory=list)

    # Full chat history for the session
    messages: List[ChatMessage] = Field(default_factory=list)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        name = "campaigns"
        use_state_management = True


# ─── API-facing response model ──────────────────────────────────────────────

class CampaignPublic(BaseModel):
    """Subset of Campaign fields exposed via the REST API."""

    campaign_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    status: str
    strategy: Optional[CampaignStrategy] = None
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
