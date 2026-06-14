import json
from google.adk.agents.callback_context import CallbackContext
from agent.schemas.ContentGenerator.ContentGenerator import PostContent


def save_to_file(callback_context: CallbackContext):
    """
    Callback function executed after an agent generates post media.
    Validates the media object. We no longer save to the local disk or S3,
    as the SVG code is stored directly in MongoDB and rendered by the frontend.
    """
    post_content = callback_context.state.get('post_content')
    if not post_content:
        return
        
    parsed_content = None
    if isinstance(post_content, str):
        try:
            cleaned = post_content.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            data = json.loads(cleaned.strip())
            parsed_content = PostContent(**data)
        except Exception as e:
            # Fallback if the agent just generated the raw SVG
            if "<svg" in post_content:
                parsed_content = PostContent(svg_code=post_content, media_name="auto_graphic")
            else:
                return
    elif isinstance(post_content, dict):
        parsed_content = PostContent(**post_content)
    else:
        try:
            parsed_content = PostContent.model_validate(post_content)
        except Exception:
            return 
            
    if not parsed_content:
        return
    
    # We optionally update the state with the cleaned/validated object
    callback_context.state['post_content'] = parsed_content