"""Conversation Beanie document — stores all chat interactions for a campaign session.

Each Conversation references a Campaign via ``campaign_id`` and the owning
user via ``user_id``. Chat messages are embedded directly as sub-documents
within the Conversation to keep all interaction history together.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Literal

from beanie import Document
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single message in the conversation — embedded sub-document."""

    role: Literal["user", "assistant"] = "user"
    content: str = ""
    author: str | None = None
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class Conversation(Document):
    """Top-level Beanie document — one doc per conversation session."""

    conversation_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    campaign_id: uuid.UUID
    user_id: uuid.UUID
    title: str = "New Conversation"

    messages: List[ChatMessage] = Field(default_factory=list)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        name = "conversations"
        use_state_management = True
