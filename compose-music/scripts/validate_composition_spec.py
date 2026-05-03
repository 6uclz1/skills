#!/usr/bin/env python3
"""Validate compose-music composition_spec JSON."""

import argparse
import json
import re
import sys


SUPPORTED_METERS = {"4/4"}
REQUIRED_BRIEF_FIELDS = ("genre", "bpm", "meter", "key", "mode", "length_bars", "creative_constraint")
NOTE_FIELDS = ("pitch", "start_time", "duration", "velocity", "mute")
GRID_ACTIVE_SYMBOLS = {"x", "X", "1"}
GRID_REST_SYMBOLS = {".", "-", "_", "0"}


def _is_path_like(value):
    text = str(value)
    if text.startswith(("file:", "~", "/", "./", "../")):
        return True
    if "\\" in text:
        return True
    if "/" in text and not re.search(r"\s", text):
        return True
    if re.search(r"\.(adg|adv|als|wav|aif|aiff|mp3|midi?|alp)$", text, re.IGNORECASE):
        return True
    return False


def _check_required(obj, path, fields, errors):
    if not isinstance(obj, dict):
        errors.append(f"{path} must be an object")
        return
    for field in fields:
        if field not in obj:
            errors.append(f"{path}.{field} is required")


def _validate_note(note, path, clip_length_beats, errors):
    if not isinstance(note, dict):
        errors.append(f"{path} must be an object")
        return
    for field in NOTE_FIELDS:
        if field not in note:
            errors.append(f"{path}.{field} is required")
    if "pitch" in note and not isinstance(note["pitch"], int):
        errors.append(f"{path}.pitch must be an integer")
    elif "pitch" in note and not 0 <= note["pitch"] <= 127:
        errors.append(f"{path}.pitch must be 0-127")

    for field in ("start_time", "duration"):
        if field in note and not isinstance(note[field], (int, float)):
            errors.append(f"{path}.{field} must be numeric")
    if "start_time" in note and isinstance(note["start_time"], (int, float)) and note["start_time"] < 0:
        errors.append(f"{path}.start_time must be >= 0")
    if "duration" in note and isinstance(note["duration"], (int, float)) and note["duration"] <= 0:
        errors.append(f"{path}.duration must be > 0")
    if "velocity" in note and not isinstance(note["velocity"], int):
        errors.append(f"{path}.velocity must be an integer")
    elif "velocity" in note and not 1 <= note["velocity"] <= 127:
        errors.append(f"{path}.velocity must be 1-127")
    if "mute" in note and not isinstance(note["mute"], bool):
        errors.append(f"{path}.mute must be boolean")

    if (
        "start_time" in note
        and "duration" in note
        and isinstance(note["start_time"], (int, float))
        and isinstance(note["duration"], (int, float))
        and note["start_time"] + note["duration"] > clip_length_beats + 1e-9
    ):
        errors.append(f"{path} extends beyond clip length")


def _validate_drum_rows(rows, path, errors):
    if not isinstance(rows, dict):
        errors.append(f"{path} must be an object")
        return
    for row_name, steps in rows.items():
        compact_steps = "".join(str(steps).split())
        for symbol in compact_steps:
            if symbol not in GRID_ACTIVE_SYMBOLS and symbol not in GRID_REST_SYMBOLS:
                errors.append(f"{path}.{row_name} includes unsupported step symbol {symbol!r}")


def _validate_timing_metadata(obj, path, errors):
    if "timing_feel" in obj and not isinstance(obj["timing_feel"], str):
        errors.append(f"{path}.timing_feel must be a string")
    for field in ("swing_amount", "shuffle_amount"):
        if field in obj:
            value = obj[field]
            if not isinstance(value, (int, float)):
                errors.append(f"{path}.{field} must be numeric")
            elif not 0.0 <= value <= 1.0:
                errors.append(f"{path}.{field} must be 0.0-1.0")
    if "humanization" in obj and not isinstance(obj["humanization"], dict):
        errors.append(f"{path}.humanization must be an object")
    if "polymeter_reset_bar" in obj:
        value = obj["polymeter_reset_bar"]
        if not isinstance(value, int):
            errors.append(f"{path}.polymeter_reset_bar must be an integer")
        elif value <= 0:
            errors.append(f"{path}.polymeter_reset_bar must be positive")


def _validate_track_refs(values, path, track_names, errors):
    if not isinstance(values, list):
        errors.append(f"{path} must be an array")
        return
    for track_name in values:
        if track_name not in track_names:
            errors.append(f"{path} includes unknown track {track_name!r}")


def validate_spec(spec):
    errors = []
    if not isinstance(spec, dict):
        return {"ok": False, "errors": ["composition_spec must be an object"]}

    for field in ("version", "brief", "tracks", "sections", "finish_criteria"):
        if field not in spec:
            errors.append(f"{field} is required")
    if "version" in spec and spec["version"] != "1.0":
        errors.append("version must be '1.0'")

    brief = spec.get("brief", {})
    _check_required(brief, "brief", REQUIRED_BRIEF_FIELDS, errors)
    if "bpm" in brief and not isinstance(brief["bpm"], (int, float)):
        errors.append("brief.bpm must be numeric")
    if "meter" in brief and brief["meter"] not in SUPPORTED_METERS:
        errors.append("brief.meter must be supported: 4/4")
    if "length_bars" in brief:
        if not isinstance(brief["length_bars"], int):
            errors.append("brief.length_bars must be an integer")
        elif brief["length_bars"] <= 0:
            errors.append("brief.length_bars must be positive")

    tracks = spec.get("tracks", [])
    if not isinstance(tracks, list) or not tracks:
        errors.append("tracks must be a non-empty array")
    else:
        names = []
        for index, track in enumerate(tracks):
            path = f"tracks[{index}]"
            _check_required(track, path, ("name", "role", "clip_length_bars", "browser_query", "notes"), errors)
            if not isinstance(track, dict):
                continue
            name = track.get("name")
            if name in names:
                errors.append(f"{path}.name must be unique")
            names.append(name)
            clip_length_bars = track.get("clip_length_bars", 0)
            if not isinstance(clip_length_bars, (int, float)):
                errors.append(f"{path}.clip_length_bars must be numeric")
                clip_length_beats = 0
            elif clip_length_bars <= 0:
                errors.append(f"{path}.clip_length_bars must be positive")
                clip_length_beats = 0
            else:
                clip_length_beats = clip_length_bars * 4.0
            if "browser_query" in track and _is_path_like(track["browser_query"]):
                errors.append(f"{path}.browser_query must be a search query or placeholder, not a path")
            if "drum_rows" in track:
                _validate_drum_rows(track["drum_rows"], f"{path}.drum_rows", errors)
            _validate_timing_metadata(track, path, errors)
            notes = track.get("notes", [])
            if not isinstance(notes, list):
                errors.append(f"{path}.notes must be an array")
            else:
                for note_index, note in enumerate(notes):
                    _validate_note(note, f"{path}.notes[{note_index}]", clip_length_beats, errors)

    sections = spec.get("sections", [])
    if not isinstance(sections, list) or not sections:
        errors.append("sections must be a non-empty array")
    else:
        total = 0
        track_names = {track.get("name") for track in tracks if isinstance(track, dict)}
        for index, section in enumerate(sections):
            path = f"sections[{index}]"
            _check_required(section, path, ("name", "start_bar", "length_bars", "density", "active_tracks"), errors)
            if not isinstance(section, dict):
                continue
            if isinstance(section.get("length_bars"), int):
                total += section["length_bars"]
                if section["length_bars"] <= 0:
                    errors.append(f"{path}.length_bars must be positive")
            else:
                errors.append(f"{path}.length_bars must be an integer")
            density = section.get("density")
            if not isinstance(density, int) or not 0 <= density <= 5:
                errors.append(f"{path}.density must be an integer from 0 to 5")
            active_tracks = section.get("active_tracks", [])
            _validate_track_refs(active_tracks, f"{path}.active_tracks", track_names, errors)
            for role_field in ("foreground", "midground", "background"):
                if role_field in section:
                    _validate_track_refs(section[role_field], f"{path}.{role_field}", track_names, errors)
            if "identity_carrier" in section and section["identity_carrier"] not in track_names:
                errors.append(f"{path}.identity_carrier includes unknown track {section['identity_carrier']!r}")
        if isinstance(brief, dict) and isinstance(brief.get("length_bars"), int) and total != brief["length_bars"]:
            errors.append(f"section lengths sum to {total}, expected {brief['length_bars']}")

    finish_criteria = spec.get("finish_criteria", [])
    if not isinstance(finish_criteria, list) or not finish_criteria:
        errors.append("finish_criteria must be a non-empty array")

    return {"ok": not errors, "errors": errors}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate compose-music composition_spec JSON.")
    parser.add_argument("input", help="Path to a composition_spec JSON file, or '-' for stdin.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print validation result.")
    args = parser.parse_args(argv)

    try:
        if args.input == "-":
            spec = json.load(sys.stdin)
        else:
            with open(args.input, "r", encoding="utf-8") as handle:
                spec = json.load(handle)
        result = validate_spec(spec)
    except Exception as exc:
        result = {"ok": False, "errors": [str(exc)]}

    indent = 2 if args.pretty else None
    print(json.dumps(result, indent=indent))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
