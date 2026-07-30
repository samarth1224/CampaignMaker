"""Persistence and state handling for a single streamed agent run.

Routes should focus on HTTP/SSE transport. This module owns the campaign and
conversation lifecycle plus the translation of agent session state into the
application's persisted campaign model.
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, Mapping, TypeVar

from pydantic import BaseModel, ValidationError

from agent.schemas.CampaignMaker.CampaignMaker import CampaignStrategy
from agent.schemas.ContentGenerator.ContentGenerator import PostCollection, PostContent
from agent.utility.post_content import parse_post_content
from app.models.campaign import Campaign, PlatformContent
from app.models.chat_message import ChatMessage, Conversation

logger = logging.getLogger(__name__)

PLATFORM_POST_STATE_KEYS = {
    "twitter_posts_text": "twitter",
    "linkedin_posts_text": "linkedin",
    "instagram_posts_text": "instagram",
}
MEDIA_STATE_KEYS = ("generated_media", "post_content")
ModelT = TypeVar("ModelT", bound=BaseModel)


class CampaignAccessError(PermissionError):
    """Raised when a campaign ID belongs to another user."""


@dataclass
class AgentRunState:
    """The pieces of an agent run needed after the event stream completes."""

    assistant_text_parts: list[str] = field(default_factory=list)
    final_response: str | None = None
    session_state: dict[str, Any] = field(default_factory=dict)
    streamed_media: list[PostContent] = field(default_factory=list)

    def record_event(self, event: Any, parsed_event: Mapping[str, Any] | None) -> None:
        """Collect persisted data from one raw ADK event and its public form."""
        state_delta = getattr(getattr(event, "actions", None), "state_delta", None)
        if state_delta:
            self.session_state.update(dict(state_delta))

        if parsed_event:
            self._record_text(parsed_event)

        self.streamed_media.extend(_extract_event_media(event))

    def merge_session_state(self, session_state: Mapping[str, Any] | None) -> None:
        if session_state:
            self.session_state.update(session_state)

    def assistant_reply(self) -> str:
        return self.final_response or "".join(self.assistant_text_parts)

    def _record_text(self, parsed_event: Mapping[str, Any]) -> None:
        event_type = parsed_event.get("type")
        if event_type not in {"text", "text_chunk", "final_response"}:
            return
        data = parsed_event.get("data")
        if isinstance(data, Mapping) and isinstance(data.get("text"), str):
            if event_type == "final_response":
                self.final_response = data["text"]
            else:
                self.assistant_text_parts.append(data["text"])


async def prepare_campaign_run(
    *, campaign_id: str, user_id: str, prompt: str
) -> tuple[Campaign, Conversation]:
    """Find or create the campaign and conversation, then store the prompt."""
    campaign_uuid = uuid.UUID(campaign_id)
    user_uuid = uuid.UUID(user_id)

    campaign = await Campaign.find_one(Campaign.campaign_id == campaign_uuid)
    conversation = await Conversation.find_one(
        Conversation.campaign_id == campaign_uuid
    )

    if campaign and campaign.user_id != user_uuid:
        raise CampaignAccessError("You do not have access to this campaign.")
    if conversation and conversation.user_id != user_uuid:
        raise CampaignAccessError("You do not have access to this conversation.")

    if not campaign:
        campaign = Campaign(
            campaign_id=campaign_uuid,
            user_id=user_uuid,
            title=prompt[:80],
            status="generating",
        )
        await campaign.insert()
    if not conversation:
        conversation = Conversation(
            campaign_id=campaign_uuid,
            user_id=user_uuid,
            title=prompt[:80],
        )
        await conversation.insert()

    conversation.messages.append(ChatMessage(role="user", content=prompt))
    campaign.status = "generating"
    await conversation.save()
    await campaign.save()
    return campaign, conversation


async def mark_campaign_failed(campaign: Campaign) -> None:
    campaign.status = "failed"
    await campaign.save()


async def persist_completed_run(
    *,
    campaign: Campaign,
    conversation: Conversation,
    run_state: AgentRunState,
) -> None:
    """Persist final text, strategy, posts, and media for a successful run."""
    assistant_reply = run_state.assistant_reply()
    if assistant_reply:
        conversation.messages.append(ChatMessage(role="assistant", content=assistant_reply))
        await conversation.save()

    _persist_strategy(campaign, run_state.session_state)
    _persist_platform_posts(campaign, run_state.session_state)
    _persist_media(campaign, run_state.session_state, run_state.streamed_media)

    campaign.status = "completed"
    await campaign.save()


def _extract_event_media(event: Any) -> list[PostContent]:
    content = getattr(event, "content", None)
    parts = getattr(content, "parts", None)
    if not parts:
        return []

    author = getattr(event, "author", "")
    media: list[PostContent] = []
    for part in parts:
        text = getattr(part, "text", None)
        if not isinstance(text, str):
            continue
        if author == "svg_graphic_generator" or "<svg" in text.lower():
            parsed = parse_post_content(text)
            if parsed:
                media.append(parsed)
    return media


def _persist_strategy(campaign: Campaign, state: Mapping[str, Any]) -> None:
    strategy = _parse_model(state.get("campaign_outline"), CampaignStrategy)
    if strategy:
        campaign.strategy = strategy


def _persist_platform_posts(campaign: Campaign, state: Mapping[str, Any]) -> None:
    for state_key, platform in PLATFORM_POST_STATE_KEYS.items():
        posts = _parse_model(state.get(state_key), PostCollection)
        if not posts:
            continue

        platform_content = _get_or_create_platform_content(campaign, platform)
        platform_content.posts = _merge_posts(platform_content.posts, posts)


def _persist_media(
    campaign: Campaign,
    state: Mapping[str, Any],
    streamed_media: list[PostContent],
) -> None:
    media_items = _deduplicate_media(
        [*streamed_media, *_collect_media_from_state(state)]
    )
    if not media_items:
        return

    platforms = [content.platform for content in campaign.content] or ["twitter"]
    for platform in platforms:
        platform_content = _get_or_create_platform_content(campaign, platform)
        existing_svg = {media.svg_code for media in platform_content.media}
        platform_content.media.extend(
            media for media in media_items if media.svg_code not in existing_svg
        )


def _collect_media_from_state(state: Mapping[str, Any]) -> list[PostContent]:
    media: list[PostContent] = []
    for state_key in MEDIA_STATE_KEYS:
        value = state.get(state_key)
        values = value if isinstance(value, list) else [value]
        media.extend(parsed for item in values if (parsed := parse_post_content(item)))

    # Some ADK versions persist output under the agent's output key. Scan other
    # simple values as a backwards-compatible fallback without duplicating known
    # media keys.
    for state_key, value in state.items():
        if state_key in MEDIA_STATE_KEYS or not isinstance(value, (str, Mapping)):
            continue
        if parsed := parse_post_content(value):
            media.append(parsed)
    return media


def _deduplicate_media(media_items: list[PostContent]) -> list[PostContent]:
    unique_media: list[PostContent] = []
    seen_svg: set[str] = set()
    for media in media_items:
        if media.svg_code and media.svg_code not in seen_svg:
            seen_svg.add(media.svg_code)
            unique_media.append(media)
    return unique_media


def _get_or_create_platform_content(
    campaign: Campaign, platform: str
) -> PlatformContent:
    for content in campaign.content:
        if content.platform == platform:
            return content

    content = PlatformContent(platform=platform)
    campaign.content.append(content)
    return content


def _merge_posts(
    existing: PostCollection | None, incoming: PostCollection
) -> PostCollection:
    if existing is None:
        return incoming

    existing_text = {post.post_text for post in existing.posts}
    existing.posts.extend(
        post for post in incoming.posts if post.post_text not in existing_text
    )
    return existing


def _parse_model(value: Any, model_type: type[ModelT]) -> ModelT | None:
    if value is None:
        return None
    if isinstance(value, model_type):
        return value

    try:
        if isinstance(value, str):
            value = json.loads(value)
        return model_type.model_validate(value)
    except (ValidationError, TypeError, json.JSONDecodeError) as exc:
        logger.warning("Unable to parse %s from agent state: %s", model_type.__name__, exc)
        return None
