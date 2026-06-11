import asyncio
from google.adk.agents import LlmAgent, LoopAgent
from google.adk.tools import AgentTool

from agent.callbacks.ContentGenerator.after_agent_callabacks import save_to_file
from agent.callbacks.CampaignMaker.after_agent_callbacks import check_loop_exit
from agent.callbacks.RootAgent.before_agent_callback import initialize_state
from agent.tools.CampaignMaker import exit_loop
from agent.tools.RootAgent import save_state

# Prompts
from agent.prompts.root_agent import prompt_root_agent
from agent.prompts.CampaignMaker import prompt_campaign_outline_generator,prompt_campaign_outline_reviewer
from agent.prompts.ContentGenerator.twitter import prompt_twitter_content_generator,prompt_twitter_post_text_generator
from agent.prompts.media_generation_tools import prompt_svg_graphic_generator 

# Schemas
from agent.schemas.CampaignMaker.CampaignMaker import CampaignStrategy
from agent.schemas.CampaignMaker.StrategyReviewer import StrategyReview
from agent.schemas.ContentGenerator.ContentGenerator import PostContent,BasePost

from agent.agents.content_generator import ContentGenerator


# Instantiate the agents
campaign_outline_generator = LlmAgent(
    name="campaign_outline_generator",
    model="gemini-3.1-flash-lite",
    instruction=prompt_campaign_outline_generator,
    description="Generates an outline for a new campaign.",
    output_key = "campaign_outline",
    output_schema = CampaignStrategy
)

campaign_outline_reviewer = LlmAgent(
    name="campaign_outline_reviewer",
    model="gemini-3.1-flash-lite",
    instruction=prompt_campaign_outline_reviewer,
    description="Reviews and refines campaign outlines.",
    tools = [exit_loop],
    output_key = "review",
    output_schema = StrategyReview,
    after_agent_callback = [check_loop_exit]
)

# Campaign Maker (Loop non-LLM agent)
campaign_maker = LoopAgent(
    name="campaign_maker",
    sub_agents=[campaign_outline_generator, campaign_outline_reviewer],
    description="Creates a campaign outline and reviews it sequentially.",
    max_iterations = 3,
)

svg_graphic_generator = LlmAgent(
    name="svg_graphic_generator",
    model="gemini-3.1-flash-lite",
    instruction=prompt_svg_graphic_generator,
    description="Generates an SVG illustration for a post.",
    output_key = "post_content",
    output_schema = PostContent,
    after_agent_callback = [save_to_file]
)

twitter_post_text_generator = LlmAgent(
    name="post_text_generator",
    model="gemini-3.1-flash-lite",
    instruction=prompt_twitter_post_text_generator,
    description="Generates the text content for a post.",
    output_key = "twitter_posts_text"
)

twitter_content_generator = LlmAgent(
    name="twitter_content_generator",
    model = "gemini-3.1-flash-lite",
    instruction = prompt_twitter_content_generator,
    description = "Generates outline for twitter posts and orchestrates text and svg generation.",
    output_key = "twitter_posts",
    output_schema = BasePost
)

linkedin_content_generator = LlmAgent(
    name="linkedin_content_generator",
    model = "gemini-3.1-flash-lite",
    instruction = prompt_twitter_content_generator,
    description = "Generates outline for linkedin posts and orchestrates text and svg generation.",
    output_key = "linkedin_posts",
    output_schema = BasePost
)

instagram_content_generator = LlmAgent(
    name="instagram_content_generator",
    model = "gemini-3.1-flash-lite",
    instruction = prompt_twitter_content_generator,
    description = "Generates outline for instagram posts and orchestrates text and svg generation.",
    sub_agents=[twitter_post_text_generator, svg_graphic_generator],
    output_key = "instagram_posts",
    output_schema = BasePost
)


content_generator_agent = ContentGenerator(
    name="content_generator_agent",
    twitter_content_generator=twitter_content_generator,
    linkedin_content_generator=linkedin_content_generator, # Placeholder for now
    instagram_content_generator=instagram_content_generator # Placeholder for now
)

root_agent = LlmAgent(
    name="root_agent",
    model="gemini-3.1-flash-lite",
    instruction=prompt_root_agent,
    description="Main orchestrator that coordinates campaign strategy and content creation",
    tools=[
        AgentTool(agent=content_generator_agent),
        save_state
    ],
    sub_agents=[campaign_maker],
    before_agent_callback=[initialize_state],
)

