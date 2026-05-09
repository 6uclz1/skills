#!/usr/bin/env python3
"""Small subprocess wrapper for Gemini CLI headless JSON calls."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from typing import Any, NamedTuple


class GeminiCliError(RuntimeError):
    """Raised when Gemini CLI cannot be executed or returns unusable output."""


class GeminiCliResult(NamedTuple):
    response: str
    raw: dict[str, Any]
    command: list[str]


def run_gemini_prompt(
    prompt: str,
    *,
    model: str | None = None,
    timeout: int = 120,
    gemini_bin: str = "gemini",
    approval_mode: str | None = None,
) -> GeminiCliResult:
    resolved = shutil.which(gemini_bin)
    if not resolved:
        raise GeminiCliError(f"gemini CLI not found: {gemini_bin}")

    command = [resolved, "-p", prompt, "--output-format", "json"]
    if model:
        command.extend(["--model", model])
    if approval_mode:
        command.extend(["--approval-mode", approval_mode])

    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise GeminiCliError(f"gemini CLI timed out after {timeout}s") from exc
    except OSError as exc:
        raise GeminiCliError(f"failed to execute gemini CLI: {exc}") from exc

    if completed.returncode != 0:
        stderr = _summarize_cli_error(completed.stderr, completed.stdout)
        raise GeminiCliError(f"gemini CLI exited with {completed.returncode}: {stderr}")

    stdout = completed.stdout.strip()
    try:
        raw = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise GeminiCliError("gemini CLI did not return JSON output") from exc

    error = raw.get("error")
    if error:
        raise GeminiCliError(f"gemini CLI returned error: {_summarize_cli_error(str(error), '')}")

    response = raw.get("response")
    if not isinstance(response, str) or not response.strip():
        raise GeminiCliError("gemini CLI JSON did not include a non-empty response")

    return GeminiCliResult(response=response, raw=raw, command=command)


def _redact(value: str) -> str:
    redacted = value
    redacted = re.sub(r"https://accounts\.google\.com/\S+", "[redacted-google-validation-url]", redacted)
    redacted = re.sub(r"/(?:var|tmp|Users)/\S+", "[redacted-local-path]", redacted)
    for marker in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "OAUTH", "TOKEN", "SECRET"):
        redacted = redacted.replace(marker, "[redacted]")
    return redacted


def _summarize_cli_error(stderr: str, stdout: str) -> str:
    combined = _redact("\n".join(part for part in (stderr.strip(), stdout.strip()) if part))
    if "Verify your account to continue" in combined:
        return "Verify your account to continue (Gemini CLI authentication/account validation required)"
    if "API key" in combined or "GOOGLE_API_KEY" in combined or "GEMINI_API_KEY" in combined:
        return "Gemini API key or CLI authentication is missing or invalid"

    useful_lines = []
    for line in combined.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("Warning:") or stripped.startswith("at "):
            continue
        useful_lines.append(stripped)
        if len(" ".join(useful_lines)) > 400:
            break
    summary = " ".join(useful_lines)[:500].strip()
    return summary or "Gemini CLI failed without a usable error message"
