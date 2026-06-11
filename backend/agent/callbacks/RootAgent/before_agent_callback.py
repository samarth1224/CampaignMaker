from google.adk.agents.callback_context import CallbackContext
from agent.schemas.state.content_generator import ContentForPlatform


def initialize_state(callback_context: CallbackContext):
  
    state_ref = callback_context.state

    state_ref["MAX_POSTS"] = 3
    if state_ref.get("user_uploaded_documents") is None:
        state_ref["user_uploaded_documents"] = False
    if state_ref.get("content_for_platform") is None:
        state_ref["content_for_platform"] = ContentForPlatform(
                                                                twitter=True,
                                                                linkedin=False,
                                                                instagram=False
                                                            ).model_dump()
    state_ref["campaign_summary"] = None
    state_ref["user_intent_summary"] = None
    state_ref["content_output_summary"] = None
    
    
    
#  Two issues 1) agent engine
# 2) frontend not displaying all the events
