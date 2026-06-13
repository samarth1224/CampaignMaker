####  The Live Link for the app will launch soon....
# CampaignMaker AI

Create Social Media Campaigns with single prompt. Fastapi, Next.js, ChromaDB, MongoDB, Google Agent Development Kit.

##  Multi-Agent Orchestration
<img width="529" height="400" alt="image" src="https://github.com/user-attachments/assets/bd33ceb1-d2c5-405f-b2b3-1a9263e1c7a0" />

The core strength of CampaignMaker lies in its multi-agent system, where specialized AI agents collaborate to deliver a cohesive marketing campaign.

- **Root Agent (`root_agent`)**: The primary orchestrator. It interacts with the user, understands the overall goal, initializes the necessary context states, and delegates tasks to the appropriate sub-agents.
- **Campaign Maker (`campaign_maker`)**: A `LoopAgent` responsible for strategy. It loops between generating and reviewing to ensure high quality:
  - **Campaign Outline Generator (`campaign_outline_generator`)**: Drafts the initial campaign strategy and post outlines.
  - **Campaign Outline Reviewer (`campaign_outline_reviewer`)**: Critiques the drafted strategy and refines it. This loop continues until a satisfactory strategy is achieved (up to 3 iterations).
- **Content Generator Agent (`content_generator_agent`)**: A router agent that delegates content creation based on the target social media platform.
  - **Platform Content Generators** (e.g., `twitter_content_generator`, `linkedin_content_generator`, `instagram_content_generator`): Orchestrates text and media generation for specific platforms.
  - **Text Generator (`twitter_post_text_generator`)**: Crafts the actual copy for the posts.
  - **Graphic Generator (`svg_graphic_generator`)**: Produces SVG code to create visual illustrations for the posts.

## State Management & Data Persistence

To ensure seamless collaboration between agents and prevent context loss, CampaignMaker employs a robust state management system. 
- **Context Narrowing**: By breaking down the task, specific agent receives only the specific context (state) it needs rather than the entire conversation history. 
- **Persistence**: Utilizes callbacks (like `initialize_state`) and tools (like `save_state`) tied to the Root Agent. This allows to track various states—such as `campaign_strategy`, `approved_outlines`, and `generated_content`—ensuring data is persisted across agent handoffs and displayed correctly in the frontend UI.

##  Under Construction: RAG with ChromaDB

Actively integrating **Retrieval-Augmented Generation (RAG) using ChromaDB**. 
This feature is currently under construction and will allow the agents to extract content from Documents.

##  Known Deficiencies & Shortcomings

While CampaignMaker is highly capable, there are a few current limitations:
- **SVG Image Realism**: The `svg_graphic_generator` produces vector illustrations. While useful for simple graphics and layouts, SVGs generated purely by LLMs lack the photorealism and complex artistry seen in image-based models (nano-banana). They are functional, but not "worthwhile".
- **Schema Validation Nuances**: Because we rely on strict Pydantic JSON schemas to pass data between agents, occasional validation errors can occur if an agent hallucinates outside the expected JSON format.

## Future Additions

- **Automated Social Media Posting**:To implement direct-to-platform posting using **OAuth 2.0 authorization** for differnt social media platform. This will allow users to securely grant permissions for CampaignMaker to publish directly to Twitter, LinkedIn, and Instagram without leaving the app.
- **Advanced Media Integrations**: Replacing or augmenting the SVG generator with an external image generation API for high-fidelity raster images.
- **Enhanced Analytics UI**: Visualizing the predicted engagement of campaigns based on the strategy reviewed by the agents.
