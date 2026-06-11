"""Utility for translating ADK Event objects into frontend-friendly dicts.

The route layer should never leak raw ADK internals to the client.  This
module provides a single entry-point — :func:`parse_event` — that
inspects an :class:`google.adk.events.Event` and returns a plain
dictionary ready to be serialised as JSON inside an SSE ``data:`` line.

Keeping this logic in a dedicated module gives us:
* **Testability** — the function is pure and can be unit-tested with
  mock ``Event`` objects.
* **Reusability** — the same parser can serve SSE, WebSocket, or REST
  polling endpoints.
* **Stability** — when the ADK upgrades its event schema, only this
  file needs to change, not every route handler.
"""

from __future__ import annotations

from typing import Any

from google.adk.events import Event


# ─── Public API ──────────────────────────────────────────────────────────────


def parse_event(event: Event) -> dict[str, Any] | None:
    """Convert an ADK *Event* into a frontend-ready dictionary.

    Returns ``None`` for events that carry no user-visible information
    (e.g. internal state deltas, transfer signals).  The caller should
    simply skip those.

    The returned dict always contains:

    * ``type``   — one of ``"text"``, ``"text_chunk"``, ``"tool_call"``,
      ``"tool_result"``, ``"state_update"``, ``"agent_transfer"``,
      ``"final_response"``, ``"error"``.
    * ``author`` — the agent name (or ``"user"``).
    * ``data``   — type-specific payload.

    Args:
        event: The raw ADK :class:`Event`.

    Returns:
        A JSON-serialisable ``dict``, or ``None`` if the event should
        be silently skipped.
    """
    author = getattr(event, "author", "unknown")

    # ── Error events ──────────────────────────────────────────────────
    if _has_error(event):
        return _build(
            "error",
            author,
            {
                "error_code": getattr(event, "error_code", None),
                "error_message": getattr(event, "error_message", None),
            },
        )

    # ── Tool call requests ────────────────────────────────────────────
    function_calls = event.get_function_calls()
    if function_calls:
        return _build(
            "tool_call",
            author,
            {
                "calls": [
                    {"name": fc.name, "args": dict(fc.args) if fc.args else {}}
                    for fc in function_calls
                ]
            },
        )

    # ── Tool results (function responses) ─────────────────────────────
    function_responses = event.get_function_responses()
    if function_responses:
        return _build(
            "tool_result",
            author,
            {
                "results": [
                    {
                        "name": fr.name,
                        "response": dict(fr.response) if fr.response else {},
                    }
                    for fr in function_responses
                ]
            },
        )

    # ── Agent transfer signal ─────────────────────────────────────────
    if event.actions and getattr(event.actions, "transfer_to_agent", None):
        return _build(
            "agent_transfer",
            author,
            {"target_agent": event.actions.transfer_to_agent},
        )

    # ── State / artifact delta (informational) ────────────────────────
    has_state = event.actions and getattr(event.actions, "state_delta", None)
    has_artifact = event.actions and getattr(event.actions, "artifact_delta", None)
    if has_state or has_artifact:
        payload: dict[str, Any] = {}
        if has_state:
            payload["state_delta"] = dict(event.actions.state_delta)
        if has_artifact:
            payload["artifact_delta"] = dict(event.actions.artifact_delta)
        return _build("state_update", author, payload)

    # ── Text content (streaming or complete) ──────────────────────────
    if event.content and event.content.parts:
        text = _extract_text(event)
        if text is not None:
            is_partial = getattr(event, "partial", False) or False
            is_final = (
                hasattr(event, "is_final_response")
                and callable(event.is_final_response)
                and event.is_final_response()
            )

            if is_final:
                event_type = "final_response"
            elif is_partial:
                event_type = "text_chunk"
            else:
                event_type = "text"

            return _build(
                event_type,
                author,
                {"text": text, "partial": is_partial},
            )

    # Event doesn't carry anything the frontend needs to see.
    return None


# ─── Private helpers ─────────────────────────────────────────────────────────


def _build(
    event_type: str, author: str, data: dict[str, Any]
) -> dict[str, Any]:
    return {"type": event_type, "author": author, "data": data}


def _extract_text(event: Event) -> str | None:
    """Return concatenated text from all text parts, or ``None``."""
    if not event.content or not event.content.parts:
        return None
    texts = [
        part.text for part in event.content.parts if getattr(part, "text", None)
    ]
    return "".join(texts) if texts else None


def _has_error(event: Event) -> bool:
    """Return ``True`` if the event represents an error."""
    return bool(
        getattr(event, "error_code", None)
        or getattr(event, "error_message", None)
    )
