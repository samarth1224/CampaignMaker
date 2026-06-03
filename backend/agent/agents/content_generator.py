from typing import AsyncGenerator
from typing import override
from pydantic import ValidationError   

from google.adk.agents import BaseAgent,LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from agent.schemas.state.content_generator import ContentForPlatform


class ContentGenerator(BaseAgent):

    twitter_content_generator: LlmAgent
    linkdin_content_generator: LlmAgent
    instragram_content_generator: LlmAgent
    
    def __init__(self,
                name: str,
                twitter_content_generator:LlmAgent,
                linkdin_content_generator:LlmAgent,
                instragram_content_generator:LlmAgent
                ):

        sub_agent_list = [
            twitter_content_generator,
            linkdin_content_generator,
            instragram_content_generator
            ]

        super().__init__(name =name,
            twitter_content_generator = twitter_content_generator,
            linkdin_content_generator = linkdin_content_generator,
            instragram_content_generator = instragram_content_generator,
            sub_agents=sub_agent_list
            )
        
    @override
    async def _run_async_impl(self,ctx: InvocationContext) -> AsyncGenerator[Event,None]:
        if (not ctx.session.state.get("content_direction")):
            if ctx.session.state.get("campaign_outline"):
                ctx.session.state["content_direction"] = ctx.session.state.get("campaign_outline").content_direction
        
        if (not ctx.session.state.get("context_summary")):
            if ctx.session.state.get("campaign_outline"):
                ctx.session.state["context_summary"] = ctx.session.state.get("campaign_outline").summary
        

        if (content_for_platform := ctx.session.state.get("content_for_platform")):
            try:
                content_for_platform = ContentForPlatform.model_validate(content_for_platform)
            except ValidationError:
                content_for_platform = ContentForPlatform(twitter=False,linkdin=False,instagram=False)  
        
            if content_for_platform.twitter:
                async for event in self.twitter_content_generator.run_async(ctx):
                    yield event
            if content_for_platform.linkdin:
                async for event in self.linkdin_content_generator.run_async(ctx):
                    yield event
            if content_for_platform.instagram:
                async for event in self.instragram_content_generator.run_async(ctx):
                    yield event
        
                
            
    