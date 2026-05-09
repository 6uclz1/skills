#!/usr/bin/env python3
"""Optional Gemini API video fallback.

The MVP keeps this provider isolated from the CLI path. It only runs when the
Google GenAI SDK and an API key are available; otherwise it returns a clear
unsupported classification to the main script.
"""

from __future__ import annotations

import json
import os
from typing import Any


class GeminiApiFallbackUnavailable(RuntimeError):
    pass


def generate_with_api_fallback(
    *,
    url: str,
    prompt: str,
    model: str,
) -> dict[str, Any]:
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        raise GeminiApiFallbackUnavailable("Gemini API fallback requires GEMINI_API_KEY or GOOGLE_API_KEY")

    try:
        from google import genai  # type: ignore
        from google.genai import types  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on optional SDK
        raise GeminiApiFallbackUnavailable("google-genai SDK is not installed") from exc

    client = genai.Client()
    contents = [
        types.Part.from_uri(file_uri=url, mime_type="video/mp4"),
        prompt,
    ]
    response = client.models.generate_content(model=model, contents=contents)
    text = getattr(response, "text", None)
    if not text:
        raise GeminiApiFallbackUnavailable("Gemini API fallback returned an empty response")

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise GeminiApiFallbackUnavailable("Gemini API fallback did not return strict JSON") from exc
