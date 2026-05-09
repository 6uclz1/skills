#!/usr/bin/env python3
"""Convert cut-up slice motif patterns into Ableton note JSON."""

import argparse
import json
import re
import sys


REST_TOKENS = {".", "rest", "REST", "-", "_", ""}
STEP_UNIT_BEATS = {
    "1/16": 0.25,
    "1/32": 0.125,
    "1/8T": 1.0 / 3.0,
    "1/16T": 1.0 / 6.0,
}
TOKEN_RE = re.compile(r"^(?P<slice>S\d{1,3})(?:\*(?P<repeat>[1-9]\d*))?(?P<offset>[+-]\d+)?$")


def _round_time(value):
    return round(float(value), 6)


def _validate_pitch(value, path):
    if not isinstance(value, int):
        raise ValueError(f"{path} must be an integer MIDI pitch")
    if not 0 <= value <= 127:
        raise ValueError(f"{path} must be within MIDI range 0-127")
    return value


def _validate_velocity(value):
    if not isinstance(value, int):
        raise ValueError("velocity must be an integer")
    if not 1 <= value <= 127:
        raise ValueError("velocity must be 1-127")
    return value


def _velocity_at(payload, position, default_velocity):
    velocities = payload.get("velocity")
    if velocities is None:
        return _validate_velocity(default_velocity)
    if isinstance(velocities, list):
        if not velocities:
            raise ValueError("velocity array must not be empty")
        return _validate_velocity(velocities[position % len(velocities)])
    return _validate_velocity(velocities)


def _parse_token(token):
    if isinstance(token, str):
        text = token.strip()
        if text in REST_TOKENS:
            return None
        match = TOKEN_RE.match(text)
        if not match:
            raise ValueError(f"unsupported pattern token {token!r}")
        repeat = int(match.group("repeat") or 1)
        offset = int(match.group("offset") or 0)
        return match.group("slice"), repeat, offset
    if isinstance(token, dict):
        slice_id = token.get("slice")
        if slice_id in REST_TOKENS or token.get("rest") is True:
            return None
        if not isinstance(slice_id, str):
            raise ValueError("pattern object slice must be a string")
        repeat = int(token.get("repeat", 1))
        offset = int(token.get("pitch_offset", 0))
        if repeat <= 0:
            raise ValueError("pattern object repeat must be positive")
        return slice_id, repeat, offset
    raise ValueError("pattern entries must be strings or objects")


def _pattern_from_payload(payload):
    pattern = payload.get("pattern", payload.get("motif"))
    if not isinstance(pattern, list) or not pattern:
        raise ValueError("pattern must be a non-empty array")
    return pattern


def cutup_pattern_to_notes(payload):
    """Return Ableton trigger notes for a symbolic cut-up slice pattern."""
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")

    clip_length_bars = payload.get("clip_length_bars", payload.get("bars", 1))
    if not isinstance(clip_length_bars, (int, float)) or clip_length_bars <= 0:
        raise ValueError("clip_length_bars must be positive")

    step_unit = payload.get("step_unit", payload.get("unit", "1/16"))
    if step_unit not in STEP_UNIT_BEATS:
        raise ValueError(f"step_unit must be one of {sorted(STEP_UNIT_BEATS)}")
    step_beats = STEP_UNIT_BEATS[step_unit]

    slice_map = payload.get("slice_map")
    if not isinstance(slice_map, dict) or not slice_map:
        raise ValueError("slice_map must be a non-empty object")
    normalized_slice_map = {
        str(slice_id): _validate_pitch(pitch, f"slice_map.{slice_id}")
        for slice_id, pitch in slice_map.items()
    }

    pattern = _pattern_from_payload(payload)
    default_duration = payload.get("default_duration")
    if default_duration is None:
        default_duration = step_beats
    if not isinstance(default_duration, (int, float)) or default_duration <= 0:
        raise ValueError("default_duration must be positive")

    default_velocity = payload.get("default_velocity", 96)
    mute = bool(payload.get("mute", False))
    global_pitch_offset = int(payload.get("pitch_offset", 0))
    clip_end = float(clip_length_bars) * 4.0

    notes = []
    for position, raw_token in enumerate(pattern):
        parsed = _parse_token(raw_token)
        if parsed is None:
            continue
        slice_id, repeat, token_pitch_offset = parsed
        if slice_id not in normalized_slice_map:
            raise ValueError(f"unknown slice {slice_id!r}")
        pitch = normalized_slice_map[slice_id] + token_pitch_offset + global_pitch_offset
        _validate_pitch(pitch, f"pattern[{position}].pitch")
        start = position * step_beats
        repeat_duration = min(float(default_duration), step_beats) / repeat
        for repeat_index in range(repeat):
            note_start = start + repeat_index * repeat_duration
            note_end = note_start + repeat_duration
            if note_end > clip_end + 1e-9:
                raise ValueError("generated note extends beyond clip length")
            notes.append(
                {
                    "pitch": pitch,
                    "start_time": _round_time(note_start),
                    "duration": _round_time(repeat_duration),
                    "velocity": _velocity_at(payload, position, default_velocity),
                    "mute": mute,
                }
            )
    return notes


def main(argv=None):
    parser = argparse.ArgumentParser(description="Convert cut-up slice patterns to Ableton note JSON.")
    parser.add_argument("input", nargs="?", help="Path to a pattern JSON file, or '-' for stdin.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args(argv)

    try:
        if args.input == "-":
            payload = json.load(sys.stdin)
        elif args.input:
            with open(args.input, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        else:
            raise ValueError("provide an input JSON file or '-' for stdin")
        notes = cutup_pattern_to_notes(payload)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(notes, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
