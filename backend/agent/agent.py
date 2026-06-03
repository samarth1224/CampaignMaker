import asyncio
from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.tools import AgentTool

from agent.tools.ContentGenerator import save_svg_file
from agent.callbacks.ContentGenerator.afteragentcallabacks import save_to_file
from agent.tools.CampaignMaker import exit_loop

# Prompts
from agent.prompts.root_agent import prompt_root_agent
from agent.prompts.CampaignMaker import prompt_campaign_outline_generator,prompt_campaign_outline_reviewer
from agent.prompts.ContentGenerator import prompt_twitter_post_generator,prompt_twitter_post_text_generator,prompt_twitter_post_svg_generator
from agent.prompts.media_generator_tools import prompt_svg_graphic_generator 

# Schemas
from agent.schemas.CampaignMaker import CampaignStrategy
from agent.schemas.StrategyReviewer import StrategyReview
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
    output_schema = StrategyReview

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
    instruction=prompt_twitter_post_svg_generator,
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

twitter_post_generator = LlmAgent(
    name="twitter_post_generator",
    model = "gemini-3.1-flash-lite",
    instruction = prompt_twitter_post_generator,
    description = "Generates outline for twitter posts and orchestrates text and svg generation.",
    sub_agents=[twitter_post_text_generator, svg_graphic_generator],
    output_key = "twitter_posts",
    output_schema = BasePost
)




root_agent = LlmAgent(
    name="root_agent",
    model="gemini-3.1-flash-lite",
    instruction=prompt_root_agent,
    description="Main orchestrator that coordinates campaign strategy and content creation",
    tools=[
        AgentTool(agent=ContentGenerator)
    ],
    sub_agents=[campaign_maker],
)

