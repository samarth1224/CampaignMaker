"""Normalise generated post media into the shared ``PostContent`` schema."""

from __future__ import annotations

import json
from typing import Any, Mapping

from agent.schemas.ContentGenerator.ContentGenerator import PostContent


def clean_svg_code(value: str) -> str:
    """Remove optional Markdown fences from an SVG payload."""
    cleaned = value.strip()
    if not cleaned.startswith("```"):
        return cleaned

    lines = cleaned.splitlines()
    if lines:
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def parse_post_content(raw_value: Any) -> PostContent | None:
    """Return validated media content when *raw_value* contains an SVG.

    Agent output may be a Pydantic model, mapping, JSON string, or raw SVG.
    Keeping that compatibility boundary in one place prevents callbacks and
    persistence code from gradually drifting apart.
    """
    if not raw_value:
        return None

    if isinstance(raw_value, PostContent):
        return _normalise_post_content(raw_value.model_dump())

    if hasattr(raw_value, "model_dump"):
        return _normalise_post_content(raw_value.model_dump())

    if isinstance(raw_value, Mapping):
        return _normalise_post_content(raw_value)

    if not isinstance(raw_value, str):
        return None

    cleaned = clean_svg_code(raw_value)
    parsed_mapping = _parse_json_mapping(cleaned)
    if parsed_mapping:
        return _normalise_post_content(parsed_mapping)

    if "<svg" in cleaned.lower():
        return PostContent(svg_code=cleaned, media_name="post_graphic")
    return None


def _parse_json_mapping(value: str) -> Mapping[str, Any] | None:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, Mapping) else None


def _normalise_post_content(value: Mapping[str, Any]) -> PostContent | None:
    svg_code = clean_svg_code(str(value.get("svg_code") or value.get("svg") or ""))
    if not svg_code:
        return None

    media_name = str(value.get("media_name") or value.get("name") or "post_graphic")
    return PostContent(svg_code=svg_code, media_name=media_name)
