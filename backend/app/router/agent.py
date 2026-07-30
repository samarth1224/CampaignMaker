"""Agent interaction router — streams public ADK events over SSE."""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import AsyncGenerator, Mapping

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agent.runner import APP_NAME, call_agent_async, create_session, runner, session_service
from app.models.usermodel import User
from app.services.campaign_run import (
    AgentRunState,
    CampaignAccessError,
    mark_campaign_failed,
    persist_completed_run,
    prepare_campaign_run,
)
from app.utility.dependencies import verify_user_access_token
from app.utility.event_parser import parse_event

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agent", tags=["Agent"])


class AgentPromptRequest(BaseModel):
    """Body sent by the frontend to start or continue an agent run."""

    prompt: str = Field(..., min_length=1, max_length=5000)
    campaign_id: str | None = None


def _sse_encode(data: dict[str, object]) -> str:
    """Format a dictionary as one SSE data frame."""
    return f"data: {json.dumps(data)}\n\n"


def _sse_error(message: str) -> str:
    return _sse_encode(
        {"type": "error", "author": "system", "data": {"error_message": message}}
    )


def _sse_done(campaign_id: str) -> str:
    return _sse_encode(
        {"type": "done", "author": "system", "data": {"campaign_id": campaign_id}}
    )


async def _load_session_state(
    *, user_id: str, campaign_id: str
) -> Mapping[str, object]:
    """Read final session state once all ADK events have been consumed."""
    try:
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=campaign_id,
        )
        return session.state if session and session.state else {}
    except Exception:
        logger.exception("Unable to read final session state for campaign %s", campaign_id)
        return {}


async def _event_stream(
    *, prompt: str, user_id: str, campaign_id: str
) -> AsyncGenerator[str, None]:
    """Drive the agent and yield only frontend-safe SSE frames."""
    try:
        campaign, conversation = await prepare_campaign_run(
            campaign_id=campaign_id,
            user_id=user_id,
            prompt=prompt,
        )
    except CampaignAccessError as exc:
        logger.warning("Rejected attempt to access campaign %s", campaign_id)
        yield _sse_error(str(exc))
        return
    except Exception:
        logger.exception("Unable to prepare campaign %s", campaign_id)
        yield _sse_error("Unable to start this campaign.")
        return

    try:
        await create_session(user_id=user_id, campaign_id=campaign_id)
    except Exception:
        # Session creation raises when continuing an existing campaign.
        logger.debug("Using existing agent session for campaign %s", campaign_id)

    run_state = AgentRunState()
    try:
        async for event in call_agent_async(
            prompt=prompt,
            runner=runner,
            user_id=user_id,
            campaign_id=campaign_id,
        ):
            parsed_event = parse_event(event)
            run_state.record_event(event, parsed_event)
            if parsed_event is not None:
                yield _sse_encode(parsed_event)
    except RuntimeError as exc:
        logger.error("Agent escalation for campaign %s: %s", campaign_id, exc)
        await mark_campaign_failed(campaign)
        yield _sse_error(str(exc))
        return
    except Exception:
        logger.exception("Unexpected error during agent run for %s", campaign_id)
        await mark_campaign_failed(campaign)
        yield _sse_error("The agent could not complete this campaign.")
        return

    run_state.merge_session_state(
        await _load_session_state(user_id=user_id, campaign_id=campaign_id)
    )
    try:
        await persist_completed_run(
            campaign=campaign,
            conversation=conversation,
            run_state=run_state,
        )
    except Exception:
        logger.exception("Unable to persist completed campaign %s", campaign_id)
        await mark_campaign_failed(campaign)
        yield _sse_error("The campaign finished, but its results could not be saved.")
        return

    yield _sse_done(campaign_id)


@router.post("/run")
async def run_agent(
    body: AgentPromptRequest,
    user: User = Depends(verify_user_access_token),
) -> StreamingResponse:
    """Start or continue a campaign and stream its agent events as SSE."""
    campaign_id = body.campaign_id or str(uuid.uuid4())
    try:
        uuid.UUID(campaign_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="campaign_id must be a valid UUID.",
        ) from exc

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
            "X-Accel-Buffering": "no",
        },
    )
