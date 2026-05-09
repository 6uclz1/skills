#!/usr/bin/env python3
"""Validate compose-music composition_spec JSON."""

import argparse
import json
import pathlib
import re
import sys


SUPPORTED_METERS = {"4/4"}
TOP_LEVEL_REQUIRED_FIELDS = ("version", "brief", "tracks", "sections", "handoff", "finish_criteria")
REQUIRED_BRIEF_FIELDS = ("genre", "bpm", "meter", "key", "mode", "length_bars", "creative_constraint")
REQUIRED_TRACK_FIELDS = ("name", "role", "clip_length_bars", "browser_query", "notes")
REQUIRED_SECTION_FIELDS = ("name", "start_bar", "length_bars", "density", "active_tracks")
REQUIRED_HANDOFF_FIELDS = ("requires_browser_search", "browser_queries", "export_target")
NOTE_FIELDS = ("pitch", "start_time", "duration", "velocity", "mute")
KICK_RELATIONSHIPS = {"avoid", "double", "answer", "intentional_overlap"}
SOURCE_TYPES = {"midi", "audio_loop", "sliced_audio"}
WARP_MODES = {"beats", "tones", "texture", "re-pitch", "complex", "complex_pro"}
RIGHTS_STATUSES = {"original", "cleared", "royalty_free", "private_test", "unknown"}
SOURCE_MATERIAL_KINDS = {"user_audio_file", "browser_audio", "recorded_audio", "placeholder"}
SOURCE_MATERIAL_ROLES = {
    "vocal",
    "melodic_loop",
    "drum_break",
    "texture",
    "field_recording",
    "unknown",
    "vocal_or_melodic_sample",
    "drum_loop_or_break",
    "texture_sample",
}
SLICE_METHODS = {"transient", "beat", "region", "manual", "slice_count"}
GRID_ACTIVE_SYMBOLS = {"x", "X", "1"}
GRID_REST_SYMBOLS = {".", "-", "_", "0"}
SCHEMA_PATH = pathlib.Path(__file__).resolve().parents[1] / "references" / "composition_spec.schema.json"


def _validate_with_jsonschema(spec):
    try:
        import jsonschema
    except Exception:
        return []
    try:
        with SCHEMA_PATH.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)
        validator = jsonschema.Draft202012Validator(schema)
        return [f"schema: {error.message}" for error in sorted(validator.iter_errors(spec), key=lambda item: item.path)]
    except Exception as exc:
        return [f"schema validation unavailable: {exc}"]


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


def _is_uri(value):
    return isinstance(value, str) and re.match(r"^[a-z][a-z0-9+.-]*://", value, re.IGNORECASE) is not None


def _is_placeholder(value):
    return isinstance(value, str) and value.startswith("<") and value.endswith(">")


def _is_env_name(value):
    return isinstance(value, str) and re.fullmatch(r"[A-Z_][A-Z0-9_]*", value) is not None


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


def _validate_rights_status(value, path, errors):
    if value is None:
        errors.append(f"{path} is required")
    elif value not in RIGHTS_STATUSES:
        errors.append(f"{path} must be one of {sorted(RIGHTS_STATUSES)}")


def _validate_sample_assets(sample_assets, errors):
    if sample_assets is None:
        return {}
    if not isinstance(sample_assets, list):
        errors.append("sample_assets must be an array")
        return {}

    asset_ids = {}
    for index, asset in enumerate(sample_assets):
        path = f"sample_assets[{index}]"
        if not isinstance(asset, dict):
            errors.append(f"{path} must be an object")
            continue
        asset_id = asset.get("id")
        if not isinstance(asset_id, str) or not asset_id:
            errors.append(f"{path}.id is required")
        elif asset_id in asset_ids:
            errors.append(f"{path}.id must be unique")
        else:
            asset_ids[asset_id] = asset

        if "path_ref" in asset and not _is_env_name(asset["path_ref"]):
            errors.append(f"{path}.path_ref must be an environment variable name")
        if "root_env" in asset and not _is_env_name(asset["root_env"]):
            errors.append(f"{path}.root_env must be an environment variable name")
        if "relative_path" in asset:
            relative_path = asset["relative_path"]
            if not isinstance(relative_path, str) or not relative_path:
                errors.append(f"{path}.relative_path must be a non-empty string")
            elif (
                pathlib.PurePosixPath(relative_path).is_absolute()
                or "\x00" in relative_path
                or any(ord(char) < 32 for char in relative_path)
                or re.match(r"^[a-z]+://", relative_path, re.IGNORECASE)
            ):
                errors.append(f"{path}.relative_path must be relative and URI-free")
        if "rights_status" not in asset:
            errors.append(f"{path}.rights_status is required")
        else:
            _validate_rights_status(asset["rights_status"], f"{path}.rights_status", errors)
        for field in ("source", "trim"):
            if field in asset and not isinstance(asset[field], str):
                errors.append(f"{path}.{field} must be a string")
        for field in ("original_bpm", "bars"):
            if field in asset:
                value = asset[field]
                if not isinstance(value, (int, float)):
                    errors.append(f"{path}.{field} must be numeric")
                elif value <= 0:
                    errors.append(f"{path}.{field} must be positive")
    return asset_ids


def _validate_audio_clip(audio_clip, path, errors):
    if not isinstance(audio_clip, dict):
        errors.append(f"{path} must be an object")
        return
    for field in ("warp", "loop"):
        if field in audio_clip and not isinstance(audio_clip[field], bool):
            errors.append(f"{path}.{field} must be boolean")
    if "warp_mode" in audio_clip and audio_clip["warp_mode"] not in WARP_MODES:
        errors.append(f"{path}.warp_mode must be one of {sorted(WARP_MODES)}")
    for field in ("gain_db", "transpose_semitones"):
        if field in audio_clip and not isinstance(audio_clip[field], (int, float)):
            errors.append(f"{path}.{field} must be numeric")


def _validate_legacy_slice_plan(slice_plan, path, errors):
    if not isinstance(slice_plan, dict):
        errors.append(f"{path} must be an object")
        return
    if slice_plan.get("mode") != "fixed_grid":
        errors.append(f"{path}.mode must be fixed_grid")
    slice_count = slice_plan.get("slice_count")
    start_pad = slice_plan.get("start_pad")
    if not isinstance(slice_count, int):
        errors.append(f"{path}.slice_count must be an integer")
    elif slice_count <= 0:
        errors.append(f"{path}.slice_count must be positive")
    if not isinstance(start_pad, int):
        errors.append(f"{path}.start_pad must be an integer")
    elif not 0 <= start_pad <= 127:
        errors.append(f"{path}.start_pad must be 0-127")
    if isinstance(slice_count, int) and isinstance(start_pad, int) and start_pad + slice_count - 1 > 127:
        errors.append(f"{path}.slice_count must keep generated pitches in MIDI range")
    if "create_trigger_clip" in slice_plan and not isinstance(slice_plan["create_trigger_clip"], bool):
        errors.append(f"{path}.create_trigger_clip must be boolean")


def _validate_cutup_slice_plan(slice_plan, path, errors):
    if not isinstance(slice_plan, dict):
        errors.append(f"{path} must be an object")
        return
    method = slice_plan.get("method")
    if method not in SLICE_METHODS:
        errors.append(f"{path}.method must be one of {sorted(SLICE_METHODS)}")
    max_slices = slice_plan.get("max_slices")
    start_pad = slice_plan.get("start_pad_midi")
    if not isinstance(max_slices, int):
        errors.append(f"{path}.max_slices must be an integer")
    elif not 1 <= max_slices <= 128:
        errors.append(f"{path}.max_slices must be 1-128")
    if not isinstance(start_pad, int):
        errors.append(f"{path}.start_pad_midi must be an integer")
    elif not 0 <= start_pad <= 127:
        errors.append(f"{path}.start_pad_midi must be 0-127")
    if isinstance(max_slices, int) and isinstance(start_pad, int) and start_pad + max_slices - 1 > 127:
        errors.append(f"{path}.max_slices must keep generated pitches in MIDI range")
    if "create_trigger_clip" in slice_plan and not isinstance(slice_plan["create_trigger_clip"], bool):
        errors.append(f"{path}.create_trigger_clip must be boolean")
    if "trigger_clip_slot" in slice_plan:
        value = slice_plan["trigger_clip_slot"]
        if not isinstance(value, int) or value < 0:
            errors.append(f"{path}.trigger_clip_slot must be a non-negative integer")
    if "preserve_timing" in slice_plan and not isinstance(slice_plan["preserve_timing"], bool):
        errors.append(f"{path}.preserve_timing must be boolean")


def _validate_slice_plan(slice_plan, path, errors):
    if not isinstance(slice_plan, dict):
        errors.append(f"{path} must be an object")
        return
    if "method" in slice_plan or "max_slices" in slice_plan or "start_pad_midi" in slice_plan:
        _validate_cutup_slice_plan(slice_plan, path, errors)
    else:
        _validate_legacy_slice_plan(slice_plan, path, errors)


def _validate_source_material(source_material, path, errors, warnings):
    if not isinstance(source_material, dict):
        errors.append(f"{path} must be an object")
        return
    for field in ("kind", "role", "rights_status"):
        if field not in source_material:
            errors.append(f"{path}.{field} is required")
    kind = source_material.get("kind")
    if kind in SOURCE_MATERIAL_KINDS:
        if kind == "user_audio_file":
            source_path = source_material.get("path")
            if not isinstance(source_path, str) or not source_path:
                warnings.append(f"{path}.path is required before Ableton audio import execution")
            elif _is_uri(source_path):
                errors.append(f"{path}.path must be a placeholder or deferred user path, not a URI")
            elif _is_placeholder(source_path):
                warnings.append(f"{path}.path is a placeholder; Ableton execution requires a user-provided audio file")
    elif kind is not None:
        errors.append(f"{path}.kind must be one of {sorted(SOURCE_MATERIAL_KINDS)}")
    role = source_material.get("role")
    if role is not None and role not in SOURCE_MATERIAL_ROLES:
        errors.append(f"{path}.role must be one of {sorted(SOURCE_MATERIAL_ROLES)}")
    _validate_rights_status(source_material.get("rights_status"), f"{path}.rights_status", errors)
    for field in ("source_bpm", "source_key"):
        if field in source_material and source_material[field] is not None:
            expected = (int, float) if field == "source_bpm" else str
            if not isinstance(source_material[field], expected):
                errors.append(f"{path}.{field} has an invalid type")


def _validate_cutup_pattern(pattern, path, errors):
    if not isinstance(pattern, dict):
        errors.append(f"{path} must be an object")
        return
    unit = pattern.get("unit", pattern.get("step_unit"))
    if unit is not None and unit not in {"1/16", "1/32", "1/8T", "1/16T"}:
        errors.append(f"{path}.unit must be one of ['1/16', '1/32', '1/8T', '1/16T']")
    slice_map = pattern.get("slice_map")
    if not isinstance(slice_map, dict) or not slice_map:
        errors.append(f"{path}.slice_map must be a non-empty object")
    else:
        for slice_id, pitch in slice_map.items():
            if not isinstance(slice_id, str) or not slice_id:
                errors.append(f"{path}.slice_map keys must be non-empty strings")
            if not isinstance(pitch, int) or not 0 <= pitch <= 127:
                errors.append(f"{path}.slice_map.{slice_id} must be a MIDI pitch 0-127")
    for field in ("motif", "pattern"):
        if field in pattern and not isinstance(pattern[field], list):
            errors.append(f"{path}.{field} must be an array")
    if "variation_strategy" in pattern and not isinstance(pattern["variation_strategy"], str):
        errors.append(f"{path}.variation_strategy must be a string")


def _commercial_or_public_export(export_target):
    if not isinstance(export_target, str):
        return False
    return re.search(r"\b(commercial|public|release|distribution|distribute|master)\b", export_target, re.IGNORECASE) is not None


def _collect_rights(spec):
    statuses = []
    for asset in spec.get("sample_assets", []) if isinstance(spec.get("sample_assets"), list) else []:
        if isinstance(asset, dict) and "rights_status" in asset:
            statuses.append(asset["rights_status"])
    for track in spec.get("tracks", []) if isinstance(spec.get("tracks"), list) else []:
        if isinstance(track, dict) and isinstance(track.get("source_material"), dict):
            statuses.append(track["source_material"].get("rights_status"))
    handoff = spec.get("handoff", {})
    if isinstance(handoff, dict):
        for asset in handoff.get("sample_assets", []) if isinstance(handoff.get("sample_assets"), list) else []:
            if isinstance(asset, dict) and "rights_status" in asset:
                statuses.append(asset["rights_status"])
    return statuses


def _validate_track_refs(values, path, track_names, errors):
    if not isinstance(values, list):
        errors.append(f"{path} must be an array")
        return
    for track_name in values:
        if track_name not in track_names:
            errors.append(f"{path} includes unknown track {track_name!r}")


def validate_spec(spec):
    errors = _validate_with_jsonschema(spec)
    warnings = []
    if not isinstance(spec, dict):
        return {"ok": False, "errors": ["composition_spec must be an object"]}

    for field in TOP_LEVEL_REQUIRED_FIELDS:
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

    sample_assets = _validate_sample_assets(spec.get("sample_assets"), errors)

    tracks = spec.get("tracks", [])
    if not isinstance(tracks, list) or not tracks:
        errors.append("tracks must be a non-empty array")
    else:
        names = []
        for index, track in enumerate(tracks):
            path = f"tracks[{index}]"
            _check_required(track, path, REQUIRED_TRACK_FIELDS, errors)
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
            source_type = track.get("source_type", "midi")
            if source_type not in SOURCE_TYPES:
                errors.append(f"{path}.source_type must be one of {sorted(SOURCE_TYPES)}")
                source_type = "midi"
            if "source_material" in track:
                _validate_source_material(track["source_material"], f"{path}.source_material", errors, warnings)
            if source_type in {"audio_loop", "sliced_audio"} and "source_material" not in track:
                sample_ref = track.get("sample_ref")
                if not isinstance(sample_ref, str) or not sample_ref:
                    errors.append(f"{path}.sample_ref is required for {source_type}")
                elif sample_ref not in sample_assets:
                    errors.append(f"{path}.sample_ref references unknown sample asset {sample_ref!r}")
            if source_type == "audio_loop" and "audio_clip" in track:
                _validate_audio_clip(track["audio_clip"], f"{path}.audio_clip", errors)
            if source_type == "sliced_audio":
                if "slice_plan" not in track:
                    errors.append(f"{path}.slice_plan is required for sliced_audio")
                else:
                    _validate_slice_plan(track["slice_plan"], f"{path}.slice_plan", errors)
            elif "slice_plan" in track:
                _validate_slice_plan(track["slice_plan"], f"{path}.slice_plan", errors)
            if "cutup_pattern" in track:
                _validate_cutup_pattern(track["cutup_pattern"], f"{path}.cutup_pattern", errors)
            for field in ("sound_intent", "shape_intent"):
                if field in track and not isinstance(track[field], str):
                    errors.append(f"{path}.{field} must be a string")
            if "kick_relationship" in track and track["kick_relationship"] not in KICK_RELATIONSHIPS:
                errors.append(f"{path}.kick_relationship must be one of {sorted(KICK_RELATIONSHIPS)}")
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
            _check_required(section, path, REQUIRED_SECTION_FIELDS, errors)
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

    handoff = spec.get("handoff", {})
    _check_required(handoff, "handoff", REQUIRED_HANDOFF_FIELDS, errors)
    if isinstance(handoff, dict):
        if "requires_browser_search" in handoff and not isinstance(handoff["requires_browser_search"], bool):
            errors.append("handoff.requires_browser_search must be boolean")
        browser_queries = handoff.get("browser_queries", [])
        if not isinstance(browser_queries, list) or not browser_queries:
            errors.append("handoff.browser_queries must be a non-empty array")
        else:
            for index, query in enumerate(browser_queries):
                if not isinstance(query, str) or not query.strip():
                    errors.append(f"handoff.browser_queries[{index}] must be a non-empty string")
                elif _is_path_like(query):
                    errors.append(f"handoff.browser_queries[{index}] must be a search query or placeholder, not a path")
        if "export_target" in handoff and not isinstance(handoff["export_target"], str):
            errors.append("handoff.export_target must be a string")
        if "sample_assets" in handoff:
            assets = handoff["sample_assets"]
            if not isinstance(assets, list):
                errors.append("handoff.sample_assets must be an array")
            else:
                for index, asset in enumerate(assets):
                    asset_path = f"handoff.sample_assets[{index}]"
                    if not isinstance(asset, dict):
                        errors.append(f"{asset_path} must be an object")
                        continue
                    _validate_rights_status(asset.get("rights_status"), f"{asset_path}.rights_status", errors)
        if "cut_to_drum_rack_requests" in handoff:
            requests = handoff["cut_to_drum_rack_requests"]
            if not isinstance(requests, list):
                errors.append("handoff.cut_to_drum_rack_requests must be an array")
            else:
                for index, request in enumerate(requests):
                    request_path = f"handoff.cut_to_drum_rack_requests[{index}]"
                    if not isinstance(request, dict):
                        errors.append(f"{request_path} must be an object")
                        continue
                    source_file = request.get("source_file")
                    if source_file is not None and _is_uri(source_file):
                        errors.append(f"{request_path}.source_file must be a placeholder or deferred user path, not a URI")
        if "sample_asset_refs" in handoff:
            refs = handoff["sample_asset_refs"]
            if not isinstance(refs, list):
                errors.append("handoff.sample_asset_refs must be an array")
            else:
                for index, asset_id in enumerate(refs):
                    if asset_id not in sample_assets:
                        errors.append(f"handoff.sample_asset_refs[{index}] references unknown sample asset {asset_id!r}")

    finish_criteria = spec.get("finish_criteria", [])
    if not isinstance(finish_criteria, list) or not finish_criteria:
        errors.append("finish_criteria must be a non-empty array")

    if isinstance(handoff, dict) and _commercial_or_public_export(handoff.get("export_target")):
        if "unknown" in _collect_rights(spec):
            errors.append("rights_status unknown cannot be used for commercial or public export targets")

    return {"ok": not errors, "errors": errors, "warnings": warnings}


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
