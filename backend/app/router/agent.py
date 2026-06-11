"""Agent interaction router — SSE endpoint for streaming ADK events."""

from __future__ import annotations

import json
import uuid
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.models.usermodel import User
from app.models.campaign import Campaign, ChatMessage
from app.utility.dependencies import verify_user_access_token
from app.utility.event_parser import parse_event

from agent.runner import create_session, call_agent_async, runner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["Agent"])


# ─── Request / Response schemas ──────────────────────────────────────────────


class AgentPromptRequest(BaseModel):
    """Body sent by the frontend to start an agent run."""

    prompt: str = Field(
        ..., min_length=1, max_length=5000, description="The user prompt."
    )
    campaign_id: str | None = Field(
        default=None,
        description=(
            "Existing campaign / session ID.  "
            "Omit to start a brand-new session."
        ),
    )


# ─── SSE streaming helpers ───────────────────────────────────────────────────


def _sse_encode(data: dict) -> str:
    """Format a dict as a single SSE ``data:`` frame."""
    return f"data: {json.dumps(data)}\n\n"


def _sse_error(message: str) -> str:
    """Format an error as an SSE frame the frontend can handle."""
    return _sse_encode({"type": "error", "author": "system", "data": {"error_message": message}})


def _sse_done(campaign_id: str) -> str:
    """Send a final ``[DONE]`` sentinel with the campaign_id so the client
    knows to close and can reference the campaign later."""
    return _sse_encode({"type": "done", "author": "system", "data": {"campaign_id": campaign_id}})


# ─── Core SSE generator ─────────────────────────────────────────────────────


async def _event_stream(
    prompt: str,
    user_id: str,
    campaign_id: str,
) -> AsyncGenerator[str, None]:
    """Async generator that drives the ADK agent and yields SSE frames.

    1. Creates (or reuses) a session via the runner.
    2. Persists the user message to the Campaign document.
    3. Calls ``call_agent_async`` which yields raw ADK ``Event`` objects.
    4. Each event is passed through ``parse_event`` (the utility layer)
       to produce a clean, frontend-friendly JSON dict.
    5. Final text responses from the agent are also persisted.
    6. A ``done`` event is sent at the end.
    """
    campaign_uuid = uuid.UUID(campaign_id)
    user_uuid = uuid.UUID(user_id)

    # ── 1. Ensure ADK session exists ──────────────────────────────────
    try:
        await create_session(user_id=user_id, campaign_id=campaign_id)
    except Exception as exc:
        logger.warning("Session creation failed (may already exist): %s", exc)

    # ── 2. Ensure Campaign document exists & save user message ────────
    campaign = await Campaign.find_one(Campaign.campaign_id == campaign_uuid)
    if not campaign:
        campaign = Campaign(
            campaign_id=campaign_uuid,
            user_id=user_uuid,
            title=prompt[:80],
            status="generating",
        )
        await campaign.insert()

    # Persist the user's message
    campaign.messages.append(ChatMessage(role="user", content=prompt))
    campaign.status = "generating"
    await campaign.save()

    # ── 3. Stream agent events ────────────────────────────────────────
    assistant_text_parts: list[str] = []
    try:
        async for event in call_agent_async(
            prompt=prompt,
            runner=runner,
            user_id=user_id,
            campaign_id=campaign_id,
        ):
            parsed = parse_event(event)
            if parsed is not None:
                yield _sse_encode(parsed)

                # Accumulate text for the final assistant message
                if parsed["type"] in ("text", "text_chunk", "final_response"):
                    text = parsed["data"].get("text", "")
                    if text:
                        assistant_text_parts.append(text)
    except RuntimeError as exc:
        logger.error("Agent escalation: %s", exc)
        yield _sse_error(str(exc))
        campaign.status = "failed"
        await campaign.save()
    except Exception as exc:
        logger.exception("Unexpected error during agent run")
        yield _sse_error(f"Internal error: {exc}")
        campaign.status = "failed"
        await campaign.save()

    # ── 4. Persist assistant reply & mark complete ────────────────────
    if assistant_text_parts:
        full_reply = "".join(assistant_text_parts)
        campaign.messages.append(
            ChatMessage(role="assistant", content=full_reply)
        )
    campaign.status = "completed"
    await campaign.save()

    # ── 5. Signal completion ──────────────────────────────────────────
    yield _sse_done(campaign_id)


# ─── Route ───────────────────────────────────────────────────────────────────


@router.post("/run")
async def run_agent(
    body: AgentPromptRequest,
    user: User = Depends(verify_user_access_token),
):
    """Stream ADK agent events to the frontend via Server-Sent Events.

    The endpoint accepts a JSON body with the user prompt (and an
    optional ``campaign_id``).  If ``campaign_id`` is not supplied a new
    UUID is generated automatically.

    **Response**: ``text/event-stream`` — each frame is a JSON object
    with ``type``, ``author``, and ``data`` keys.  The stream ends with
    a ``done`` event containing the ``campaign_id``.
    """
    campaign_id = body.campaign_id or str(uuid.uuid4())

    return StreamingResponse(
        _event_stream(
            prompt=body.prompt,
            user_id=str(user.public_id),
            campaign_id=campaign_id,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
