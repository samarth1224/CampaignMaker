"""Route campaign content generation to the requested social platforms."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from typing import override

from pydantic import ValidationError

from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from agent.schemas.state.content_generator import ContentForPlatform

logger = logging.getLogger(__name__)


class ContentGenerator(BaseAgent):
    """Delegate content work to the platform agents selected in session state."""

    twitter_content_generator: LlmAgent
    linkedin_content_generator: LlmAgent
    instagram_content_generator: LlmAgent

    def __init__(
        self,
        *,
        name: str,
        twitter_content_generator: LlmAgent,
        linkedin_content_generator: LlmAgent,
        instagram_content_generator: LlmAgent,
    ) -> None:
        platform_agents = [
            twitter_content_generator,
            linkedin_content_generator,
            instagram_content_generator,
        ]
        super().__init__(
            name=name,
            twitter_content_generator=twitter_content_generator,
            linkedin_content_generator=linkedin_content_generator,
            instagram_content_generator=instagram_content_generator,
            sub_agents=platform_agents,
        )

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        self._populate_context_from_outline(ctx)
        selected_platforms = self._selected_platforms(ctx)

        for enabled, agent in (
            (selected_platforms.twitter, self.twitter_content_generator),
            (selected_platforms.linkedin, self.linkedin_content_generator),
            (selected_platforms.instagram, self.instagram_content_generator),
        ):
            if enabled:
                async for event in agent.run_async(ctx):
                    yield event

    @staticmethod
    def _populate_context_from_outline(ctx: InvocationContext) -> None:
        outline = ctx.session.state.get("campaign_outline")
        if not isinstance(outline, dict):
            return

        state = ctx.session.state
        for target_key, outline_key in (
            ("content_direction", "content_direction"),
            ("context_summary", "summary"),
        ):
            if state.get(target_key) is None:
                state[target_key] = outline.get(outline_key)

    @staticmethod
    def _selected_platforms(ctx: InvocationContext) -> ContentForPlatform:
        raw_selection = ctx.session.state.get("content_for_platform")
        try:
            return ContentForPlatform.model_validate(raw_selection or {})
        except ValidationError:
            logger.warning("Ignoring invalid content_for_platform state: %r", raw_selection)
            return ContentForPlatform()
