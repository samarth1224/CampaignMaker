from google.adk.agents.callback_context import CallbackContext
from agent.schemas.CampaignMaker.StrategyReviewer import StrategyReview

def check_loop_exit(callback_context: CallbackContext):
    """
    Callback function executed after the campaign outline reviewer completes.
    Checks if the strategy review resulted in approval, and if so,
    programmatically escalates to break the LoopAgent execution immediately.
    """
    review = callback_context.state.get("review")
    if not review:
        return
        
    is_approved = False
    try:
        review_obj = StrategyReview.model_validate(review)
        is_approved = review_obj.is_approved
    except Exception:
        # Fallback to direct key/attribute check if validation fails
        if isinstance(review, dict):
            is_approved = review.get("is_approved", False)
        else:
            is_approved = getattr(review, "is_approved", False)

    if is_approved:
        print("[Callback] Strategy approved. Programmatically exiting Campaign Maker loop.")
        callback_context.actions.escalate = True
