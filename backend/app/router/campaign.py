"""Campaign REST router — list, get, and manage campaigns."""

from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from beanie.operators import Eq

from app.models.usermodel import User
from app.models.campaign import Campaign
from app.models.chat_message import Conversation
from app.utility.dependencies import verify_user_access_token


router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


# ─── Response schemas ────────────────────────────────────────────────────────


class CampaignListItem(BaseModel):
    """Lightweight campaign item for sidebar list."""

    campaign_id: str
    title: str
    status: str
    created_at: str
    updated_at: str


class CampaignDetail(BaseModel):
    """Full campaign detail for the Generated Content panel."""

    campaign_id: str
    user_id: str
    title: str
    status: str
    strategy: dict | None = None
    content: list = []
    messages: list = []
    created_at: str
    updated_at: str


# ─── Routes ──────────────────────────────────────────────────────────────────


@router.get("/", response_model=List[CampaignListItem])
async def list_campaigns(
    user: User = Depends(verify_user_access_token),
):
    """List all campaigns for the authenticated user, newest first."""
    campaigns = await Campaign.find(
        Campaign.user_id == user.public_id,
    ).sort("-created_at").to_list()

    return [
        CampaignListItem(
            campaign_id=str(c.campaign_id),
            title=c.title,
            status=c.status,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
        )
        for c in campaigns
    ]


@router.get("/{campaign_id}", response_model=CampaignDetail)
async def get_campaign(
    campaign_id: str,
    user: User = Depends(verify_user_access_token),
):
    """Get full campaign details by ID."""
    try:
        cid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid campaign ID format.",
        )

    campaign = await Campaign.find_one(
        Campaign.campaign_id == cid,
        Campaign.user_id == user.public_id,
    )

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found.",
        )

    conversation = await Conversation.find_one(
        Conversation.campaign_id == cid,
        Conversation.user_id == user.public_id,
    )

    messages = []
    if conversation and conversation.messages:
        messages = [
            {
                "role": msg.role,
                "content": msg.content,
                "author": msg.author,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in conversation.messages
        ]

    return CampaignDetail(
        campaign_id=str(campaign.campaign_id),
        user_id=str(campaign.user_id),
        title=campaign.title,
        status=campaign.status,
        strategy=campaign.strategy.model_dump() if campaign.strategy else None,
        content=[pc.model_dump() for pc in campaign.content] if campaign.content else [],
        messages=messages,
        created_at=campaign.created_at.isoformat(),
        updated_at=campaign.updated_at.isoformat(),
    )
