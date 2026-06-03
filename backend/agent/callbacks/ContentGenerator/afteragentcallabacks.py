from google.adk.agents.callback_context import CallbackContext

from .schemas.ContentGenerator import PostMedia


def save_to_file(ctx: CallbackContext):
    post_media = ctx.state.get('post_media')
    try:
        post_media = PostMedia.modelvalidate(post_media)
    except: 
        return 
    
    with open(f"{post_media.name}.svg", 'w') as svg_file:
        svg_file.write(post_media.content)
    return 

    