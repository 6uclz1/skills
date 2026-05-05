#!/usr/bin/env python3
"""Build an Ableton handoff plan from a compose-music composition_spec."""

import argparse
import json
import pathlib
import sys

import importlib.util


def _load_validator():
    script = pathlib.Path(__file__).with_name("validate_composition_spec.py")
    spec = importlib.util.spec_from_file_location("validate_composition_spec", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _beats_from_bars(bars, meter="4/4"):
    if meter != "4/4":
        raise ValueError("only 4/4 meter is supported")
    return float(bars) * 4.0


def _note_source(track):
    notes = track.get("notes", [])
    if notes:
        return {"type": "inline", "notes": notes}
    if track.get("notes_file"):
        return {"type": "file", "path": track["notes_file"]}
    return {"type": "empty", "notes": []}


def _sample_asset_summary(asset):
    keep = (
        "id",
        "source",
        "path_ref",
        "root_env",
        "relative_path",
        "original_bpm",
        "bars",
        "trim",
        "rights_status",
    )
    return {key: asset[key] for key in keep if key in asset}


def _asset_by_id(spec):
    return {asset["id"]: asset for asset in spec.get("sample_assets", [])}


def build_handoff_plan(spec):
    validator = _load_validator()
    result = validator.validate_spec(spec)
    if not result["ok"]:
        raise ValueError("; ".join(result["errors"]))

    meter = spec["brief"]["meter"]
    track_plan = []
    browser_searches = []
    clip_plan = []
    audio_clip_plan = []
    slice_plan = []
    sample_assets = [_sample_asset_summary(asset) for asset in spec.get("sample_assets", [])]
    assets = _asset_by_id(spec)
    for index, track in enumerate(spec["tracks"]):
        source_type = track.get("source_type", "midi")
        if source_type != "audio_loop":
            browser_searches.append(
                {
                    "track_index": index,
                    "track_name": track["name"],
                    "role": track["role"],
                    "query": track["browser_query"],
                }
            )
        track_plan.append(
            {
                "index": index,
                "name": track["name"],
                "role": track["role"],
                "source_type": source_type,
                "sample_ref": track.get("sample_ref"),
                "browser_query": track["browser_query"],
                "sound_intent": track.get("sound_intent"),
                "shape_intent": track.get("shape_intent"),
                "kick_relationship": track.get("kick_relationship"),
            }
        )
        timing = {
            key: track[key]
            for key in ("timing_feel", "swing_amount", "shuffle_amount", "humanization", "polymeter_reset_bar")
            if key in track
        }
        if source_type in ("midi", "sliced_audio"):
            clip_plan.append(
                {
                    "track_index": index,
                    "track_name": track["name"],
                    "clip_slot": 0,
                    "clip_name": f"{track['name']} Main",
                    "length_bars": track["clip_length_bars"],
                    "length_beats": _beats_from_bars(track["clip_length_bars"], meter),
                    "note_source": _note_source(track),
                    "timing": timing,
                }
            )
        if source_type == "audio_loop":
            audio_clip = track.get("audio_clip", {})
            asset = assets.get(track["sample_ref"], {})
            audio_clip_plan.append(
                {
                    "track_index": index,
                    "track_name": track["name"],
                    "source_asset_id": track["sample_ref"],
                    "start_bar": 1,
                    "length_bars": track["clip_length_bars"],
                    "length_beats": _beats_from_bars(track["clip_length_bars"], meter),
                    "warp": {
                        "enabled": bool(audio_clip.get("warp", True)),
                        "mode": audio_clip.get("warp_mode", "beats"),
                        "original_bpm": asset.get("original_bpm"),
                        "target_bpm": spec["brief"]["bpm"],
                    },
                    "loop": bool(audio_clip.get("loop", True)),
                    "gain_db": audio_clip.get("gain_db"),
                    "transpose_semitones": audio_clip.get("transpose_semitones", 0),
                }
            )
        if source_type == "sliced_audio":
            plan = track["slice_plan"]
            slice_plan.append(
                {
                    "track_index": index,
                    "track_name": track["name"],
                    "source_asset_id": track["sample_ref"],
                    "slice_count": plan["slice_count"],
                    "start_pad": plan["start_pad"],
                    "mode": plan.get("mode", "fixed_grid"),
                    "create_trigger_clip": bool(plan.get("create_trigger_clip", False)),
                    "trigger_note_source": _note_source(track),
                }
            )

    arrangement_sections = []
    for section in spec["sections"]:
        arrangement_sections.append(
            {
                "name": section["name"],
                "start_bar": section["start_bar"],
                "length_bars": section["length_bars"],
                "density": section["density"],
                "active_tracks": section["active_tracks"],
                "foreground": section.get("foreground", []),
                "midground": section.get("midground", []),
                "background": section.get("background", []),
                "identity_carrier": section.get("identity_carrier"),
                "move": section.get("move"),
                "transition_event": section.get("transition_event"),
            }
        )

    return {
        "version": "1.0",
        "source": "compose-music composition_spec",
        "preflight_intent": ["wait-ready", "doctor-if-needed", "tracks-list"],
        "set_tempo": spec["brief"]["bpm"],
        "set_meter": meter,
        "meter": meter,
        "requires_browser_search": spec["handoff"]["requires_browser_search"],
        "browser_searches": browser_searches,
        "sample_assets": sample_assets,
        "track_plan": track_plan,
        "clip_plan": clip_plan,
        "audio_clip_plan": audio_clip_plan,
        "slice_plan": slice_plan,
        "arrangement_sections": arrangement_sections,
        "export_target": spec["handoff"]["export_target"],
        "finish_criteria": spec["finish_criteria"],
        "handoff_notes": [
            "Search the active Ableton browser catalog before loading devices or kits.",
            "Use returned paths or URIs from ableton-cli browser results; do not invent browser paths.",
            "Create tracks and clips from this plan, then add note_source data to clips.",
            "Resolve sample_assets through path_ref, root_env plus relative_path, or a user manifest before any audio operation.",
            "Prefer ableton-cli plan or dry-run execution before modifying Live.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Convert composition_spec JSON to an Ableton handoff plan JSON.")
    parser.add_argument("input", help="Path to a composition_spec JSON file, or '-' for stdin.")
    parser.add_argument("--output", help="Write handoff plan to this path instead of stdout.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args(argv)

    try:
        if args.input == "-":
            spec = json.load(sys.stdin)
        else:
            with open(args.input, "r", encoding="utf-8") as handle:
                spec = json.load(handle)
        plan = build_handoff_plan(spec)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    indent = 2 if args.pretty else None
    output = json.dumps(plan, indent=indent)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(output)
            handle.write("\n")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
