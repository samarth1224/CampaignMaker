from google.adk.agents.callback_context import CallbackContext
from agent.schemas.state.content_generator import ContentForPlatform
from app.services.knowledge_base import knowledge_base


def initialize_state(callback_context: CallbackContext):
  
    state_ref = callback_context.state

    state_ref["MAX_POSTS"] = 3
    invocation_context = getattr(callback_context, "_invocation_context", None)
    user_id = getattr(invocation_context, "user_id", None)
    if user_id:
        # The user namespace survives across sessions and lets the retrieval
        # tool enforce ownership without accepting a user ID from the model.
        state_ref["user:rag_user_id"] = str(user_id)
        state_ref["user_uploaded_documents"] = knowledge_base.has_documents(
            user_id=str(user_id)
        )
    elif state_ref.get("user_uploaded_documents") is None:
        state_ref["user_uploaded_documents"] = False
    if state_ref.get("content_for_platform") is None:
        state_ref["content_for_platform"] = ContentForPlatform(
                                                                twitter=True,
                                                                linkedin=False,
                                                                instagram=False
                                                            ).model_dump()
    if state_ref.get("campaign_summary") is None:
        state_ref["campaign_summary"] = None
    if state_ref.get("user_intent_summary") is None:
        state_ref["user_intent_summary"] = None
    if state_ref.get("content_output_summary") is None:
        state_ref["content_output_summary"] = None
    
    
    
#  Two issues 1) agent engine
# 2) frontend not displaying all the events
