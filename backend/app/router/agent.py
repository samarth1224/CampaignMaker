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


def _sse_done() -> str:
    """Send a final ``[DONE]`` sentinel so the client knows to close."""
    return "data: [DONE]\n\n"


# ─── Core SSE generator ─────────────────────────────────────────────────────


async def _event_stream(
    prompt: str,
    user_id: str,
    campaign_id: str,
) -> AsyncGenerator[str, None]:
    """Async generator that drives the ADK agent and yields SSE frames.

    1. Creates (or reuses) a session via the runner.
    2. Calls ``call_agent_async`` which yields raw ADK ``Event`` objects.
    3. Each event is passed through ``parse_event`` (the utility layer)
       to produce a clean, frontend-friendly JSON dict.
    4. Events that ``parse_event`` returns ``None`` for are silently
       skipped — the frontend never sees internal ADK bookkeeping.
    5. A ``[DONE]`` sentinel is sent at the end.
    """
    # ── 1. Ensure session exists ──────────────────────────────────────
    try:
        await create_session(user_id=user_id, campaign_id=campaign_id)
    except Exception as exc:
        logger.warning("Session creation failed (may already exist): %s", exc)
        # Swallow — the session might already exist from a prior turn.

    # ── 2. Stream agent events ────────────────────────────────────────
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
    except RuntimeError as exc:
        # call_agent_async raises RuntimeError on escalation.
        logger.error("Agent escalation: %s", exc)
        yield _sse_error(str(exc))
    except Exception as exc:
        logger.exception("Unexpected error during agent run")
        yield _sse_error(f"Internal error: {exc}")

    # ── 3. Signal completion ──────────────────────────────────────────
    yield _sse_done()


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
    a ``data: [DONE]`` sentinel.
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
