#!/usr/bin/env python3
"""Convert a step grid into Ableton note JSON."""

import argparse
import json
import sys


DEFAULT_VELOCITIES = {
    "kick": 110,
    "snare": 100,
    "clap": 100,
    "chat": 80,
    "closed hat": 80,
    "closed_hat": 80,
    "ohat": 85,
    "open hat": 85,
    "open_hat": 85,
    "bass": 100,
}

ACTIVE_SYMBOLS = {"x", "X", "1"}
REST_SYMBOLS = {".", "-", "_", "0"}
METADATA_FIELDS = ("timing_feel", "swing_amount", "shuffle_amount", "humanization", "polymeter_reset_bar")


def _default_velocity(name):
    key = name.strip().lower()
    return DEFAULT_VELOCITIES.get(key, 90)


def _compact_steps(raw_steps):
    return "".join(str(raw_steps).split())


def grid_to_notes(grid):
    """Return Ableton note dictionaries for a 4/4 16- or 32-step grid."""
    bars = int(grid.get("bars", 1))
    resolution = int(grid.get("resolution", 16))
    if bars <= 0:
        raise ValueError("bars must be positive")
    if resolution not in (16, 32):
        raise ValueError("resolution must be 16 or 32")
    if not isinstance(grid.get("tracks"), dict) or not grid["tracks"]:
        raise ValueError("tracks must be a non-empty object")

    expected_steps = bars * resolution
    step_duration = 4.0 / resolution
    notes = []

    for track_name, row in grid["tracks"].items():
        if "pitch" not in row:
            raise ValueError(f"{track_name}.pitch is required")
        pitch = int(row["pitch"])
        if pitch < 0 or pitch > 127:
            raise ValueError(f"{track_name}.pitch must be 0-127")

        steps = _compact_steps(row.get("steps", ""))
        if len(steps) != expected_steps:
            raise ValueError(f"{track_name}.steps must contain {expected_steps} steps")

        velocity = int(row.get("velocity", _default_velocity(track_name)))
        if velocity < 1 or velocity > 127:
            raise ValueError(f"{track_name}.velocity must be 1-127")
        duration = float(row.get("duration", step_duration))
        if duration <= 0:
            raise ValueError(f"{track_name}.duration must be positive")
        mute = bool(row.get("mute", False))

        for index, symbol in enumerate(steps):
            if symbol in ACTIVE_SYMBOLS:
                notes.append(
                    {
                        "pitch": pitch,
                        "start_time": round(index * step_duration, 6),
                        "duration": duration,
                        "velocity": velocity,
                        "mute": mute,
                    }
                )
            elif symbol in REST_SYMBOLS:
                continue
            else:
                raise ValueError(f"unsupported step symbol {symbol!r} in {track_name}.steps")

    return notes


def grid_to_note_payload(grid):
    """Return notes plus timing metadata that should survive Ableton handoff."""
    metadata = {}
    for field in METADATA_FIELDS:
        if field in grid:
            metadata[field] = grid[field]
    return {"notes": grid_to_notes(grid), "metadata": metadata}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Convert 16/32-step drum grids to Ableton note JSON.")
    parser.add_argument("input", help="Path to a grid JSON file, or '-' for stdin.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--payload", action="store_true", help="Output notes with preserved timing metadata.")
    args = parser.parse_args(argv)

    try:
        if args.input == "-":
            grid = json.load(sys.stdin)
        else:
            with open(args.input, "r", encoding="utf-8") as handle:
                grid = json.load(handle)
        output = grid_to_note_payload(grid) if args.payload else grid_to_notes(grid)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    indent = 2 if args.pretty else None
    print(json.dumps(output, indent=indent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
