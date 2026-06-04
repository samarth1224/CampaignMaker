from google.adk.agents.callback_context import CallbackContext
from agent.schemas.ContentGenerator.ContentGenerator import PostContent


def save_to_file(callback_context: CallbackContext):
    """
    Callback function executed after an agent generates post media.
    Validates the media object and saves it as an SVG file.
    """
    post_content = callback_context.state.get('post_content')
    try:
        post_content = PostContent.model_validate(post_content)
    except: 
        return 
    
    with open(f"{post_content.media_name}.svg", 'w') as svg_file:
        svg_file.write(post_content.svg_code)


    