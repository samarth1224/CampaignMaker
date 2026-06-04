from google.adk.tools.tool_context import ToolContext

def save_state(
    tool_context: ToolContext,
    campaign_summary: str | None = None,
    user_intent_summary: str | None = None,
    content_output_summary: str | None = None,
) -> str:
    """
    Tool to save the states campaign_summary, user_intent_summary, and content_output_summary.
    You can update one, multiple, or all of these states in a single call.
    
    Args:
        campaign_summary: The new summary string for the overall campaign (optional).
        user_intent_summary: The new summary string of user intentions/queries (optional).
        content_output_summary: The new summary string of generated content output (optional).
    """
    state_ref = tool_context.state
    
    updated = []
    if campaign_summary is not None:
        state_ref["campaign_summary"] = campaign_summary
        updated.append("campaign_summary")
    if user_intent_summary is not None:
        state_ref["user_intent_summary"] = user_intent_summary
        updated.append("user_intent_summary")
    if content_output_summary is not None:
        state_ref["content_output_summary"] = content_output_summary
        updated.append("content_output_summary")
        
    if not updated:
        return "No state updates were provided."
        
    return f"Successfully updated states: {', '.join(updated)}"
