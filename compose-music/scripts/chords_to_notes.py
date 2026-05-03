#!/usr/bin/env python3
"""Generate Ableton chord note JSON from tonic, mode, and roman numerals."""

import argparse
import json
import re
import sys


NOTE_TO_PC = {
    "C": 0,
    "C#": 1,
    "DB": 1,
    "D": 2,
    "D#": 3,
    "EB": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "GB": 6,
    "G": 7,
    "G#": 8,
    "AB": 8,
    "A": 9,
    "A#": 10,
    "BB": 10,
    "B": 11,
}

MODE_INTERVALS = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "aeolian": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    # Roman chord requests in pentatonic contexts still need seven degrees.
    # Use major harmony while the composer keeps melodies and tensions pentatonic.
    "pentatonic": [0, 2, 4, 5, 7, 9, 11],
}

ROMAN_DEGREES = {
    "I": 0,
    "II": 1,
    "III": 2,
    "IV": 3,
    "V": 4,
    "VI": 5,
    "VII": 6,
}

QUALITY_INTERVALS = {
    "major": [0, 4, 7],
    "maj": [0, 4, 7],
    "minor": [0, 3, 7],
    "min": [0, 3, 7],
    "m": [0, 3, 7],
    "diminished": [0, 3, 6],
    "dim": [0, 3, 6],
    "augmented": [0, 4, 8],
    "aug": [0, 4, 8],
    "dominant": [0, 4, 7],
    "dom": [0, 4, 7],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
}


def _note_to_midi(note_name, octave):
    key = note_name.strip().upper()
    if key not in NOTE_TO_PC:
        raise ValueError(f"unsupported tonic {note_name!r}")
    return 12 * (int(octave) + 1) + NOTE_TO_PC[key]


def _parse_roman(symbol):
    match = re.fullmatch(r"([b#]?)([ivIV]+)(.*)?", symbol.strip())
    if not match:
        raise ValueError(f"unsupported roman numeral {symbol!r}")
    accidental, numeral, suffix = match.groups()
    degree_key = numeral.upper()
    if degree_key not in ROMAN_DEGREES:
        raise ValueError(f"unsupported roman degree {symbol!r}")
    accidental_offset = {"b": -1, "#": 1, "": 0}[accidental]
    return ROMAN_DEGREES[degree_key], accidental_offset, suffix or ""


def _scale_pitch_classes(tonic_pc, mode):
    intervals = MODE_INTERVALS.get(mode)
    if intervals is None:
        raise ValueError(f"unsupported mode {mode!r}")
    return [(tonic_pc + interval) % 12 for interval in intervals]


def _pitch_at_or_above(base_midi, target_pc):
    pitch = base_midi + ((target_pc - base_midi) % 12)
    return pitch


def _chord_pcs(scale_pcs, degree, accidental_offset, chord_type):
    root_pc = (scale_pcs[degree] + accidental_offset) % 12
    third_pc = scale_pcs[(degree + 2) % 7]
    fifth_pc = scale_pcs[(degree + 4) % 7]
    pcs = [root_pc, third_pc, fifth_pc]
    if chord_type == "seventh":
        pcs.append(scale_pcs[(degree + 6) % 7])
    elif chord_type != "triad":
        raise ValueError("chord_type must be triad or seventh")
    return pcs


def _quality_intervals(quality, extensions):
    normalized = str(quality).lower()
    if normalized not in QUALITY_INTERVALS:
        raise ValueError(f"unsupported chord quality {quality!r}")
    intervals = list(QUALITY_INTERVALS[normalized])
    normalized_extensions = {str(extension).lower() for extension in extensions}
    if "9" in normalized_extensions:
        normalized_extensions.add("7")
    if "7" in normalized_extensions:
        if normalized in ("major", "maj"):
            intervals.append(11)
        elif normalized in ("diminished", "dim"):
            intervals.append(9)
        else:
            intervals.append(10)
    if "maj7" in normalized_extensions or "major7" in normalized_extensions:
        intervals.append(11)
    if "b7" in normalized_extensions or "dom7" in normalized_extensions:
        intervals.append(10)
    if "9" in normalized_extensions:
        intervals.append(14)
    return sorted(set(intervals), key=intervals.index)


def _explicit_chord_pcs(root_pc, quality, extensions):
    return [(root_pc + interval) % 12 for interval in _quality_intervals(quality, extensions)]


def _normalize_chord_spec(symbol, default_chord_type):
    if isinstance(symbol, dict):
        if "roman" not in symbol:
            raise ValueError("chord spec object requires roman")
        extensions = symbol.get("extensions", [])
        if isinstance(extensions, str):
            extensions = [extensions]
        return {
            "roman": str(symbol["roman"]),
            "quality": symbol.get("quality"),
            "extensions": list(extensions),
            "inversion": symbol.get("inversion"),
            "slash": symbol.get("slash") or symbol.get("bass"),
            "voicing": symbol.get("voicing"),
        }

    text = str(symbol)
    if "/" in text:
        text, slash = text.split("/", 1)
    else:
        slash = None
    degree, accidental_offset, suffix = _parse_roman(text)
    extensions = []
    quality = None
    suffix_lower = suffix.lower()
    if "maj7" in suffix_lower or "major7" in suffix_lower:
        quality = "major"
        extensions.append("maj7")
    elif "m7" in suffix_lower or "min7" in suffix_lower:
        quality = "minor"
        extensions.append("7")
    elif "7" in suffix_lower:
        extensions.append("7")
    elif default_chord_type == "seventh":
        extensions.append("7")
    return {
        "roman": text,
        "quality": quality,
        "extensions": extensions,
        "inversion": None,
        "slash": slash,
        "voicing": None,
        "_parsed": (degree, accidental_offset),
    }


def _apply_inversion(pitches, inversion):
    if inversion in (None, 0, "0", "root", "root-position"):
        return pitches
    aliases = {"first": 1, "first-inversion": 1, "second": 2, "second-inversion": 2, "third": 3}
    count = aliases.get(str(inversion), inversion)
    try:
        count = int(count)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"unsupported inversion {inversion!r}") from exc
    if count < 0 or count >= len(pitches):
        raise ValueError(f"unsupported inversion {inversion!r}")
    inverted = list(pitches)
    for _ in range(count):
        inverted.append(inverted.pop(0) + 12)
    return sorted(inverted)


def _slash_bass_midi(note_name, chord_pitches):
    pitch = _note_to_midi(note_name, 3)
    while pitch >= chord_pitches[0]:
        pitch -= 12
    while pitch < 0:
        pitch += 12
    return pitch


def _close_voicing(base_midi, pcs):
    pitches = [_pitch_at_or_above(base_midi, pcs[0])]
    for pc in pcs[1:]:
        pitches.append(_pitch_at_or_above(pitches[-1], pc))
    return pitches


def _open_voicing(base_midi, pcs):
    pitches = _close_voicing(base_midi, pcs)
    if len(pitches) >= 3:
        pitches[1] += 12
        pitches.sort()
    return pitches


def _move_near(previous, current):
    if previous is None:
        return current
    moved = []
    for index, pitch in enumerate(current):
        target = previous[min(index, len(previous) - 1)]
        candidates = [pitch + shift for shift in (-24, -12, 0, 12, 24)]
        moved.append(min(candidates, key=lambda candidate: (abs(candidate - target), candidate)))
    return sorted(moved)


def _apply_voicing(base_midi, pcs, voicing, previous=None):
    if voicing in ("close", "stab", "pad"):
        pitches = _close_voicing(base_midi, pcs)
        if voicing == "pad":
            pitches = _open_voicing(base_midi - 12, pcs)
        return pitches
    if voicing == "open":
        return _open_voicing(base_midi, pcs)
    if voicing == "root-position":
        return _close_voicing(base_midi, pcs)
    if voicing == "first-inversion":
        pitches = _close_voicing(base_midi, pcs)
        return sorted([pitches[1], pitches[2], pitches[0] + 12] + pitches[3:])
    if voicing == "smooth-voice-leading":
        return _move_near(previous, _close_voicing(base_midi, pcs))
    raise ValueError(f"unsupported voicing {voicing!r}")


def chords_to_notes(spec):
    tonic = spec.get("tonic")
    mode = str(spec.get("mode", "minor")).lower()
    roman = spec.get("roman")
    if not tonic:
        raise ValueError("tonic is required")
    if not isinstance(roman, list) or not roman:
        raise ValueError("roman must be a non-empty list")

    tonic_midi = _note_to_midi(tonic, int(spec.get("octave", 4)))
    scale_pcs = _scale_pitch_classes(tonic_midi % 12, mode)
    bars_per_chord = float(spec.get("bars_per_chord", 1))
    if bars_per_chord <= 0:
        raise ValueError("bars_per_chord must be positive")
    duration = bars_per_chord * 4.0
    chord_type = spec.get("chord_type", "triad")
    voicing = spec.get("voicing", "close")
    velocity = int(spec.get("velocity", 78))
    if velocity < 1 or velocity > 127:
        raise ValueError("velocity must be 1-127")

    notes = []
    previous = None
    for chord_index, symbol in enumerate(roman):
        chord_spec = _normalize_chord_spec(symbol, chord_type)
        if "_parsed" in chord_spec:
            degree, accidental_offset = chord_spec["_parsed"]
        else:
            degree, accidental_offset, _suffix = _parse_roman(chord_spec["roman"])
        root_pc = (scale_pcs[degree] + accidental_offset) % 12
        if chord_spec["quality"]:
            pcs = _explicit_chord_pcs(root_pc, chord_spec["quality"], chord_spec["extensions"])
        else:
            pcs = _chord_pcs(scale_pcs, degree, accidental_offset, chord_type)
        chord_voicing = chord_spec["voicing"] or voicing
        pitches = _apply_voicing(tonic_midi, pcs, chord_voicing, previous)
        pitches = _apply_inversion(pitches, chord_spec["inversion"])
        if chord_spec["slash"]:
            pitches = [_slash_bass_midi(chord_spec["slash"], pitches)] + pitches
        previous = pitches
        start_time = chord_index * duration
        for pitch in pitches:
            notes.append(
                {
                    "pitch": pitch,
                    "start_time": start_time,
                    "duration": duration,
                    "velocity": velocity,
                    "mute": False,
                }
            )
    return notes


def main(argv=None):
    parser = argparse.ArgumentParser(description="Convert roman chord progressions to Ableton note JSON.")
    parser.add_argument("input", help="Path to a chord spec JSON file, or '-' for stdin.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args(argv)

    try:
        if args.input == "-":
            spec = json.load(sys.stdin)
        else:
            with open(args.input, "r", encoding="utf-8") as handle:
                spec = json.load(handle)
        notes = chords_to_notes(spec)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    indent = 2 if args.pretty else None
    print(json.dumps(notes, indent=indent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
