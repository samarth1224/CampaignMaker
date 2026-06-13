"""
Agent runner and session management for the Interactive Story engine.

Provides:
- A pre-configured class `Runner` instance wired to the root agent.
- :func:`create_session` for initialising per-story ADK sessions.
- :func:`call_agent_async` for invoking the agent pipeline and
  extracting the structured node response along with the updated session.
"""

from typing import AsyncGenerator
from dotenv import load_dotenv
import os

load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService, Session
from google.adk.events import Event
from google.genai import types


from .agent import root_agent


APP_NAME = "agents"

session_service = DatabaseSessionService(
    db_url=os.getenv("DATABASE_URL")
)

runner = Runner(
    app_name=APP_NAME,
    session_service=session_service,
    agent=root_agent,
)


async def create_session(user_id, campaign_id) -> Session:
    """Create a new ADK session for a story generation run.

    Each session is scoped to one story and stores the agent's
    intermediate state (master plotline, graph-level counters, etc.)
    across multiple invocations.

    Args:
        user_id: The public UUID of the requesting user.
        campaign_id: A unique UUID for the new campaign.

    Returns:
        The newly created :class:`Session` instance.
    """
    return await session_service.create_session(
        app_name=APP_NAME,
        user_id=str(user_id),
        session_id=str(campaign_id),
    )


async def call_agent_async(
    prompt: str,
    runner: Runner,
    user_id,
    campaign_id,
) -> AsyncGenerator[Event, None]:
    """Invoke the agent pipeline and return the generated story node.

    Sends *prompt* to the runner, iterates over events, and yields events.

    Args:
        prompt: The user-facing or internal prompt string to send.
        runner: The :class:`Runner` instance to execute with.
        user_id: The user's public UUID.
        campaign_id: The campaign's public UUID / session ID.

    Returns:
        The :class:`Event`.

    Raises:
        RuntimeError: If the agent escalates with an error.
    """
    content = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(
        user_id=str(user_id),
        session_id=str(campaign_id),
        new_message=content,
    ):
        if event.actions and event.actions.escalate:
            error_msg = (
                event.error_message or "No specific message provided."
            )
            raise RuntimeError(
                f"Agent escalated with error: {error_msg}"
            )

        yield event
       
