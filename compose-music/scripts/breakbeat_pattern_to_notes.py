#!/usr/bin/env python3
"""Convert sliced breakbeat trigger patterns into Ableton note JSON."""

import argparse
import json
import sys


PRESETS = {
    "amen_loop_straight": {
        "bars": 4,
        "resolution": 16,
        "start_pad": 36,
        "slice_count": 16,
        "pattern": [index % 16 for index in range(64)],
        "velocity": [116, 92, 98, 84, 110, 86, 104, 88, 118, 90, 100, 84, 112, 88, 106, 96] * 4,
        "duration_steps": 1,
    },
    "amen_jungle_chop_170": {
        "bars": 4,
        "resolution": 16,
        "start_pad": 36,
        "slice_count": 16,
        "pattern": [
            0, 1, 4, 5, 8, 9, 10, 11, 4, 5, 14, 15, 8, 9, 6, 7,
            0, 1, 2, 3, 12, 13, 10, 11, 4, 5, 6, 7, 15, 15, 14, 12,
            8, 9, 4, 5, 0, 1, 10, 11, 12, 13, 6, 7, 8, 9, 14, 15,
            0, 1, 4, 5, 8, 8, 9, 10, 11, 12, 15, 15, 14, 10, 8, 6,
        ],
        "velocity": [118, 92, 106, 86, 116, 88, 104, 90] * 8,
        "duration_steps": 1,
    },
    "amen_half_time_switch": {
        "bars": 4,
        "resolution": 16,
        "start_pad": 36,
        "slice_count": 16,
        "pattern": [
            0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
            0, 0, 4, 4, 8, 8, 12, 12, 4, 4, 8, 8, 14, 14, 15, 15,
            0, 1, 2, 3, 12, 13, 10, 11, 4, 5, 6, 7, 15, 15, 14, 12,
            0, 0, 8, 8, 4, 4, 12, 12, 8, 8, 14, 14, 15, 15, 12, 12,
        ],
        "velocity": [116, 88, 104, 84, 112, 86, 100, 90] * 8,
        "duration_steps": 1,
    },
}


def _velocity_at(velocity, index):
    if isinstance(velocity, list):
        if len(velocity) == 0:
            raise ValueError("velocity array must not be empty")
        if len(velocity) != index["pattern_length"]:
            raise ValueError("velocity array length must match pattern length")
        value = velocity[index["position"]]
    else:
        value = velocity
    if not isinstance(value, int):
        raise ValueError("velocity must be an integer or integer array")
    if not 1 <= value <= 127:
        raise ValueError("velocity must be 1-127")
    return value


def breakbeat_pattern_to_notes(payload):
    """Return Ableton trigger notes for fixed-grid break slices."""
    bars = int(payload.get("bars", 4))
    resolution = int(payload.get("resolution", 16))
    start_pad = int(payload.get("start_pad", 36))
    slice_count = int(payload.get("slice_count", 16))
    pattern = payload.get("pattern")
    duration_steps = float(payload.get("duration_steps", 1))
    velocity = payload.get("velocity", 110)

    if bars <= 0:
        raise ValueError("bars must be positive")
    if resolution not in (16, 32):
        raise ValueError("resolution must be 16 or 32")
    if slice_count <= 0:
        raise ValueError("slice_count must be positive")
    if not 0 <= start_pad <= 127:
        raise ValueError("start_pad must be 0-127")
    if start_pad + slice_count - 1 > 127:
        raise ValueError("slice_count must keep generated pitches in MIDI range")
    if not isinstance(pattern, list) or not pattern:
        raise ValueError("pattern must be a non-empty array")
    if len(pattern) > bars * resolution:
        raise ValueError("pattern length must not exceed bars * resolution")
    if duration_steps <= 0:
        raise ValueError("duration_steps must be positive")

    step_duration = 4.0 / resolution
    duration = round(duration_steps * step_duration, 6)
    clip_end = bars * 4.0
    notes = []
    pattern_length = len(pattern)
    for position, slice_index in enumerate(pattern):
        if not isinstance(slice_index, int):
            raise ValueError("slice index must be an integer")
        if not 0 <= slice_index < slice_count:
            raise ValueError("slice index must be within 0 <= index < slice_count")
        start_time = round(position * step_duration, 6)
        if start_time + duration > clip_end + 1e-9:
            raise ValueError("generated note extends beyond clip length")
        notes.append(
            {
                "pitch": start_pad + slice_index,
                "start_time": start_time,
                "duration": duration,
                "velocity": _velocity_at(velocity, {"position": position, "pattern_length": pattern_length}),
                "mute": bool(payload.get("mute", False)),
            }
        )
    return notes


def main(argv=None):
    parser = argparse.ArgumentParser(description="Convert breakbeat slice patterns to Ableton note JSON.")
    parser.add_argument("input", nargs="?", help="Path to a pattern JSON file, or '-' for stdin.")
    parser.add_argument("--preset", choices=sorted(PRESETS), help="Use a bundled Amen trigger pattern preset.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args(argv)

    try:
        if args.preset:
            payload = PRESETS[args.preset]
        elif args.input == "-":
            payload = json.load(sys.stdin)
        elif args.input:
            with open(args.input, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        else:
            raise ValueError("provide an input JSON file, '-' for stdin, or --preset")
        notes = breakbeat_pattern_to_notes(payload)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(notes, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
