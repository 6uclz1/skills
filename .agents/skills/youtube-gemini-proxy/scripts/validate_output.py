#!/usr/bin/env python3
"""Validate normalized youtube-gemini-proxy JSON without external dependencies."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


PROVIDERS = {"gemini-cli", "gemini-api-video-fallback", "youtube-data-api-captions"}
MODES = {"summary", "transcript", "chapters", "claims", "captions"}


class ValidationError(ValueError):
    pass


def validate_output(payload: dict[str, Any]) -> None:
    _require_keys(payload, ["video", "source", "result", "warnings"], "$")
    if not isinstance(payload["warnings"], list) or not all(isinstance(x, str) for x in payload["warnings"]):
        raise ValidationError("$.warnings must be an array of strings")

    video = _object(payload["video"], "$.video")
    _require_keys(video, ["url", "video_id"], "$.video")
    for key in ("url", "video_id"):
        if not isinstance(video[key], str) or not video[key]:
            raise ValidationError(f"$.video.{key} must be a non-empty string")
    for key in ("title", "duration", "channel"):
        if key in video and video[key] is not None and not isinstance(video[key], str):
            raise ValidationError(f"$.video.{key} must be string or null")

    source = _object(payload["source"], "$.source")
    _require_keys(source, ["provider", "mode", "retrieved_at", "is_official_caption"], "$.source")
    if source["provider"] not in PROVIDERS:
        raise ValidationError("$.source.provider is not supported")
    if source["mode"] not in MODES:
        raise ValidationError("$.source.mode is not supported")
    if not isinstance(source["retrieved_at"], str) or not source["retrieved_at"]:
        raise ValidationError("$.source.retrieved_at must be a non-empty string")
    if not isinstance(source["is_official_caption"], bool):
        raise ValidationError("$.source.is_official_caption must be boolean")

    result = _object(payload["result"], "$.result")
    _optional_string_or_null(result, "summary", "$.result")
    _optional_string_list(result, "key_points", "$.result")
    _optional_string_list(result, "topics", "$.result")
    _validate_segments(result.get("segments", []))
    _validate_chapters(result.get("chapters", []))
    _validate_claims(result.get("claims", []))


def _object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{path} must be an object")
    return value


def _require_keys(value: dict[str, Any], keys: list[str], path: str) -> None:
    missing = [key for key in keys if key not in value]
    if missing:
        raise ValidationError(f"{path} missing required keys: {', '.join(missing)}")


def _optional_string_or_null(value: dict[str, Any], key: str, path: str) -> None:
    if key in value and value[key] is not None and not isinstance(value[key], str):
        raise ValidationError(f"{path}.{key} must be string or null")


def _optional_string_list(value: dict[str, Any], key: str, path: str) -> None:
    if key not in value:
        return
    if not isinstance(value[key], list) or not all(isinstance(item, str) for item in value[key]):
        raise ValidationError(f"{path}.{key} must be an array of strings")


def _validate_segments(segments: Any) -> None:
    if not isinstance(segments, list):
        raise ValidationError("$.result.segments must be an array")
    for index, segment in enumerate(segments):
        item = _object(segment, f"$.result.segments[{index}]")
        _require_keys(item, ["timestamp", "text"], f"$.result.segments[{index}]")
        if not isinstance(item["timestamp"], str) or not item["timestamp"]:
            raise ValidationError(f"$.result.segments[{index}].timestamp must be a non-empty string")
        if not isinstance(item["text"], str):
            raise ValidationError(f"$.result.segments[{index}].text must be a string")
        _optional_string_or_null(item, "end_timestamp", f"$.result.segments[{index}]")
        _optional_string_or_null(item, "language", f"$.result.segments[{index}]")


def _validate_chapters(chapters: Any) -> None:
    if not isinstance(chapters, list):
        raise ValidationError("$.result.chapters must be an array")
    for index, chapter in enumerate(chapters):
        item = _object(chapter, f"$.result.chapters[{index}]")
        _require_keys(item, ["timestamp", "title"], f"$.result.chapters[{index}]")
        if not isinstance(item["timestamp"], str) or not isinstance(item["title"], str):
            raise ValidationError(f"$.result.chapters[{index}] timestamp and title must be strings")
        _optional_string_or_null(item, "summary", f"$.result.chapters[{index}]")


def _validate_claims(claims: Any) -> None:
    if not isinstance(claims, list):
        raise ValidationError("$.result.claims must be an array")
    for index, claim in enumerate(claims):
        item = _object(claim, f"$.result.claims[{index}]")
        _require_keys(item, ["claim", "timestamp"], f"$.result.claims[{index}]")
        if not isinstance(item["timestamp"], str) or not isinstance(item["claim"], str):
            raise ValidationError(f"$.result.claims[{index}] timestamp and claim must be strings")
        _optional_string_or_null(item, "confidence", f"$.result.claims[{index}]")
        if "needs_verification" in item and not isinstance(item["needs_verification"], bool):
            raise ValidationError(f"$.result.claims[{index}].needs_verification must be boolean")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file")
    args = parser.parse_args(argv)

    with open(args.json_file, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    try:
        validate_output(payload)
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
