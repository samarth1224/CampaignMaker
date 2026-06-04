from google.adk.tools.tool_context import ToolContext


def exit_loop(tool_context: ToolContext):
    """Call this function ONLY when campaign_outline_reviewer agent approves the Strategy"""
    print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    return {}