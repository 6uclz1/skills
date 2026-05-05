import importlib.util
import contextlib
import csv
import io
import json
import pathlib
import tempfile
import unittest
import unittest.mock


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_script(name):
    script = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GridToNotesTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_script("grid_to_notes")

    def test_converts_16_step_grid_to_beat_positions(self):
        notes = self.mod.grid_to_notes(
            {
                "bars": 1,
                "resolution": 16,
                "tracks": {
                    "Kick": {"pitch": 36, "steps": "X...X...X...X..."},
                    "Clap": {"pitch": 39, "steps": "....X.......X..."},
                },
            }
        )

        self.assertEqual(
            notes,
            [
                {"pitch": 36, "start_time": 0.0, "duration": 0.25, "velocity": 110, "mute": False},
                {"pitch": 36, "start_time": 1.0, "duration": 0.25, "velocity": 110, "mute": False},
                {"pitch": 36, "start_time": 2.0, "duration": 0.25, "velocity": 110, "mute": False},
                {"pitch": 36, "start_time": 3.0, "duration": 0.25, "velocity": 110, "mute": False},
                {"pitch": 39, "start_time": 1.0, "duration": 0.25, "velocity": 100, "mute": False},
                {"pitch": 39, "start_time": 3.0, "duration": 0.25, "velocity": 100, "mute": False},
            ],
        )

    def test_accepts_grid_alias_from_skill_contract(self):
        notes = self.mod.grid_to_notes(
            {
                "bars": 1,
                "resolution": 16,
                "tracks": {
                    "Kick": {"pitch": 36, "grid": "X...X...X...X..."},
                },
            }
        )

        self.assertEqual([note["start_time"] for note in notes], [0.0, 1.0, 2.0, 3.0])

    def test_rejects_conflicting_steps_and_grid_alias(self):
        with self.assertRaisesRegex(ValueError, "steps and .*grid must match"):
            self.mod.grid_to_notes(
                {
                    "bars": 1,
                    "resolution": 16,
                    "tracks": {
                        "Kick": {
                            "pitch": 36,
                            "steps": "X...X...X...X...",
                            "grid": "X.......X.......",
                        },
                    },
                }
            )

    def test_rejects_unsupported_grid_symbols(self):
        with self.assertRaisesRegex(ValueError, "unsupported step symbol"):
            self.mod.grid_to_notes(
                {
                    "bars": 1,
                    "resolution": 16,
                    "tracks": {"Kick": {"pitch": 36, "steps": "X...?...X...X..."}},
                }
            )

    def test_preserves_timing_feel_metadata_in_payload(self):
        payload = self.mod.grid_to_note_payload(
            {
                "bars": 1,
                "resolution": 16,
                "timing_feel": "garage shuffle",
                "swing_amount": 0.58,
                "humanization": {"timing_ms": 7, "velocity": 5},
                "tracks": {"Closed Hat": {"pitch": 42, "steps": "X.X.X.X.X.X.X.X."}},
            }
        )

        self.assertEqual(payload["metadata"]["timing_feel"], "garage shuffle")
        self.assertEqual(payload["metadata"]["swing_amount"], 0.58)
        self.assertEqual(payload["metadata"]["humanization"], {"timing_ms": 7, "velocity": 5})
        self.assertEqual(len(payload["notes"]), 8)


class ChordsToNotesTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_script("chords_to_notes")

    def test_generates_dorian_triads_from_roman_progression(self):
        notes = self.mod.chords_to_notes(
            {
                "tonic": "D",
                "mode": "dorian",
                "roman": ["i", "IV"],
                "chord_type": "triad",
                "voicing": "close",
                "octave": 4,
                "bars_per_chord": 1,
            }
        )

        pitches_by_start = {}
        for note in notes:
            pitches_by_start.setdefault(note["start_time"], []).append(note["pitch"])

        self.assertEqual(pitches_by_start[0.0], [62, 65, 69])
        self.assertEqual(pitches_by_start[4.0], [67, 71, 74])
        self.assertTrue(all(note["duration"] == 4.0 for note in notes))

    def test_smooth_voice_leading_limits_large_jumps(self):
        notes = self.mod.chords_to_notes(
            {
                "tonic": "A",
                "mode": "minor",
                "roman": ["i", "VI", "III", "VII"],
                "chord_type": "triad",
                "voicing": "smooth-voice-leading",
                "octave": 4,
                "bars_per_chord": 1,
            }
        )

        chords = [sorted(note["pitch"] for note in notes[i : i + 3]) for i in range(0, len(notes), 3)]
        pitch_classes = [sorted(pitch % 12 for pitch in chord) for chord in chords]
        self.assertEqual(pitch_classes, [[0, 4, 9], [0, 5, 9], [0, 4, 7], [2, 7, 11]])
        for previous, current in zip(chords, chords[1:]):
            self.assertLessEqual(max(abs(a - b) for a, b in zip(previous, current)), 5)

    def test_accepts_pentatonic_power_voicings(self):
        notes = self.mod.chords_to_notes(
            {
                "tonic": "C",
                "mode": "pentatonic",
                "roman": ["I", "bVII"],
                "chord_type": "triad",
                "voicing": "close",
                "octave": 4,
            }
        )

        self.assertEqual([note["pitch"] for note in notes[:3]], [60, 64, 67])
        self.assertEqual([note["pitch"] for note in notes[3:]], [70, 74, 77])

    def test_supports_compact_and_spread_voicing_names(self):
        compact = self.mod.chords_to_notes(
            {
                "tonic": "C",
                "mode": "major",
                "roman": ["I"],
                "voicing": "compact",
                "octave": 4,
            }
        )
        spread = self.mod.chords_to_notes(
            {
                "tonic": "C",
                "mode": "major",
                "roman": ["I"],
                "voicing": "spread",
                "octave": 4,
            }
        )

        self.assertEqual([note["pitch"] for note in compact], [60, 64, 67])
        self.assertEqual([note["pitch"] for note in spread], [60, 67, 76])

    def test_supports_borrowed_major_flat_chords(self):
        notes = self.mod.chords_to_notes(
            {
                "tonic": "C",
                "mode": "major",
                "roman": [
                    {"roman": "bIII", "quality": "major"},
                    {"roman": "bVI", "quality": "major"},
                    {"roman": "bVII", "quality": "major"},
                ],
                "octave": 4,
            }
        )

        chords = [[note["pitch"] for note in notes[i : i + 3]] for i in range(0, len(notes), 3)]
        self.assertEqual(chords, [[63, 67, 70], [68, 72, 75], [70, 74, 77]])

    def test_supports_first_inversion_seventh_and_slash_bass(self):
        notes = self.mod.chords_to_notes(
            {
                "tonic": "C",
                "mode": "major",
                "roman": [
                    {"roman": "I", "quality": "major", "extensions": ["7"], "inversion": 1},
                    {"roman": "V", "quality": "dominant", "extensions": ["7"], "slash": "B"},
                ],
                "octave": 4,
            }
        )

        first = [note["pitch"] for note in notes[:4]]
        second = [note["pitch"] for note in notes[4:]]
        self.assertEqual(first, [64, 67, 71, 72])
        self.assertEqual(second[0], 59)
        self.assertEqual(sorted(pitch % 12 for pitch in second[1:]), [2, 5, 7, 11])

    def test_supports_explicit_chord_quality_without_roman_case_guessing(self):
        notes = self.mod.chords_to_notes(
            {
                "tonic": "A",
                "mode": "minor",
                "roman": [
                    {"roman": "i", "quality": "minor", "extensions": ["7"]},
                    {"roman": "IV", "quality": "major"},
                ],
                "octave": 3,
            }
        )

        self.assertEqual([note["pitch"] for note in notes[:4]], [57, 60, 64, 67])
        self.assertEqual([note["pitch"] for note in notes[4:]], [62, 66, 69])


class CompositionSchemaTests(unittest.TestCase):
    def test_skill_declares_required_output_modes_and_handoff_contract(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")

        for phrase in (
            "Idea Mode",
            "Pattern Mode",
            "Song Sketch Mode",
            "Ableton Handoff Mode",
            "Repair Mode",
            "fenced JSON block named `composition_spec`",
            "No hard-coded browser paths",
        ):
            self.assertIn(phrase, skill_text)

    def test_schema_file_defines_required_contract_fields(self):
        schema_path = ROOT / "references" / "composition_spec.schema.json"
        with schema_path.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)

        self.assertEqual(schema["$id"], "https://codex.local/compose-music/composition_spec.schema.json")
        self.assertEqual(
            schema["required"],
            ["version", "brief", "tracks", "sections", "handoff", "finish_criteria"],
        )
        self.assertIn("browser_query", schema["$defs"]["track"]["required"])
        self.assertIn("sound_intent", schema["$defs"]["track"]["properties"])
        self.assertIn("kick_relationship", schema["$defs"]["track"]["properties"])
        self.assertIn("identity_carrier", schema["$defs"]["section"]["properties"])
        self.assertIn("browser_queries", schema["$defs"]["handoff"]["required"])

    def test_python_validator_required_fields_match_schema(self):
        validator = load_script("validate_composition_spec")
        schema_path = ROOT / "references" / "composition_spec.schema.json"
        with schema_path.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)

        self.assertEqual(list(validator.TOP_LEVEL_REQUIRED_FIELDS), schema["required"])
        self.assertEqual(list(validator.REQUIRED_BRIEF_FIELDS), schema["$defs"]["brief"]["required"])
        self.assertEqual(list(validator.REQUIRED_TRACK_FIELDS), schema["$defs"]["track"]["required"])
        self.assertEqual(list(validator.REQUIRED_SECTION_FIELDS), schema["$defs"]["section"]["required"])
        self.assertEqual(list(validator.REQUIRED_HANDOFF_FIELDS), schema["$defs"]["handoff"]["required"])

    def test_reference_files_cover_backlog_contracts(self):
        expected = {
            "composition-spec-schema.md": ("sections[*].length_bars", "browser_query"),
            "eval-cases.md": ("E01", "Pass threshold"),
            "arrangement-energy-curves.md": ("32-bar sketch", "128-bar"),
            "sound-design-intent.md": ("Search query", "avoid preset names"),
        }

        for filename, phrases in expected.items():
            text = (ROOT / "references" / filename).read_text(encoding="utf-8")
            for phrase in phrases:
                self.assertIn(phrase, text)


class ValidateCompositionSpecTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_script("validate_composition_spec")

    def valid_spec(self):
        return {
            "version": "1.0",
            "brief": {
                "genre": "melodic techno",
                "bpm": 124,
                "meter": "4/4",
                "key": "D",
                "mode": "dorian",
                "length_bars": 8,
                "creative_constraint": "identity comes from bass rhythm",
            },
            "tracks": [
                {
                    "name": "Drums",
                    "role": "rhythm",
                    "clip_length_bars": 1,
                    "browser_query": "Drum Rack dry electronic kit",
                    "notes": [
                        {"pitch": 36, "start_time": 0.0, "duration": 0.25, "velocity": 110, "mute": False}
                    ],
                },
                {
                    "name": "Bass",
                    "role": "low-end identity",
                    "clip_length_bars": 4,
                    "browser_query": "Operator bass",
                    "notes": [
                        {"pitch": 38, "start_time": 0.5, "duration": 0.5, "velocity": 100, "mute": False}
                    ],
                },
            ],
            "sections": [
                {
                    "name": "Intro",
                    "start_bar": 1,
                    "length_bars": 4,
                    "density": 1,
                    "active_tracks": ["Drums"],
                },
                {
                    "name": "Drop",
                    "start_bar": 5,
                    "length_bars": 4,
                    "density": 4,
                    "active_tracks": ["Drums", "Bass"],
                },
            ],
            "handoff": {
                "requires_browser_search": True,
                "browser_queries": ["Drum Rack dry electronic kit", "Operator bass"],
                "export_target": "rough arrangement render",
            },
            "finish_criteria": [
                "8-bar arrangement exists",
                "kick and bass do not mask each other",
                "one bounce/export target is named",
            ],
        }

    def amen_spec(self, source_type="sliced_audio"):
        track = {
            "name": "Amen Slices" if source_type == "sliced_audio" else "Amen Loop",
            "role": "foreground rhythm",
            "source_type": source_type,
            "sample_ref": "amen_break",
            "clip_length_bars": 4,
            "browser_query": "Drum Rack for sliced break playback"
            if source_type == "sliced_audio"
            else "No browser search: user-provided audio sample",
            "notes": [],
        }
        if source_type == "audio_loop":
            track["audio_clip"] = {
                "warp": True,
                "warp_mode": "beats",
                "loop": True,
                "gain_db": -6.0,
                "transpose_semitones": 0,
            }
        if source_type == "sliced_audio":
            track["slice_plan"] = {
                "mode": "fixed_grid",
                "slice_count": 16,
                "start_pad": 36,
                "create_trigger_clip": True,
            }
            track["notes"] = [
                {"pitch": 36, "start_time": 0.0, "duration": 0.25, "velocity": 115, "mute": False}
            ]

        return {
            "version": "1.0",
            "brief": {
                "genre": "jungle breakbeat",
                "bpm": 170,
                "meter": "4/4",
                "key": "D",
                "mode": "minor",
                "length_bars": 8,
                "creative_constraint": "foreground rhythm comes from one user-provided Amen-style break sample",
            },
            "sample_assets": [
                {
                    "id": "amen_break",
                    "source": "user_sample_library",
                    "path_ref": "AMEN_BREAK_WAV",
                    "original_bpm": 136.0,
                    "bars": 4,
                    "trim": "downbeat_aligned",
                    "rights_status": "user_provided",
                }
            ],
            "tracks": [track],
            "sections": [
                {
                    "name": "Intro",
                    "start_bar": 1,
                    "length_bars": 4,
                    "density": 2,
                    "active_tracks": [track["name"]],
                    "foreground": [track["name"]],
                    "midground": [],
                    "background": [],
                    "identity_carrier": track["name"],
                    "move": "filtered sparse break",
                    "transition_event": "last-half-bar slice repeat into Drop",
                },
                {
                    "name": "Drop",
                    "start_bar": 5,
                    "length_bars": 4,
                    "density": 5,
                    "active_tracks": [track["name"]],
                    "foreground": [track["name"]],
                    "midground": [],
                    "background": [],
                    "identity_carrier": track["name"],
                    "move": "full chopped break",
                    "transition_event": "mute final sixteenth for loop return",
                },
            ],
            "handoff": {
                "requires_browser_search": source_type == "sliced_audio",
                "browser_queries": ["Drum Rack"] if source_type == "sliced_audio" else ["No browser search"],
                "sample_asset_refs": ["amen_break"],
                "export_target": "8-bar jungle Amen break rough loop",
            },
            "finish_criteria": [
                "8-bar breakbeat sketch exists",
                "Amen source is referenced through sample_assets, not browser_query",
            ],
        }

    def test_validates_complete_spec(self):
        result = self.mod.validate_spec(self.valid_spec())

        self.assertTrue(result["ok"])
        self.assertEqual(result["errors"], [])

    def test_rejects_path_like_browser_targets_and_bad_note_values(self):
        spec = self.valid_spec()
        spec["tracks"][0]["browser_query"] = "drums/Kits/Fake Kit.adg"
        spec["tracks"][0]["notes"][0]["pitch"] = 128
        spec["tracks"][0]["drum_rows"] = {"Kick": "X...?...X...X..."}
        spec["sections"][1]["length_bars"] = 8

        result = self.mod.validate_spec(spec)

        self.assertFalse(result["ok"])
        self.assertIn("tracks[0].browser_query must be a search query or placeholder, not a path", result["errors"])
        self.assertIn("tracks[0].notes[0].pitch must be 0-127", result["errors"])
        self.assertIn("tracks[0].drum_rows.Kick includes unsupported step symbol '?'", result["errors"])
        self.assertIn("section lengths sum to 12, expected 8", result["errors"])

    def test_rejects_missing_handoff(self):
        spec = self.valid_spec()
        del spec["handoff"]

        result = self.mod.validate_spec(spec)

        self.assertFalse(result["ok"])
        self.assertIn("handoff is required", result["errors"])
        self.assertIn("handoff.requires_browser_search is required", result["errors"])

    def test_validates_sound_intent_and_kick_relationship_fields(self):
        spec = self.valid_spec()
        spec["tracks"][1]["sound_intent"] = "short mono bass with clear gaps after kick hits"
        spec["tracks"][1]["shape_intent"] = "fast decay, low-pass movement, centered sub"
        spec["tracks"][1]["kick_relationship"] = "answer"

        result = self.mod.validate_spec(spec)

        self.assertTrue(result["ok"])

        spec["tracks"][1]["kick_relationship"] = "crowd"
        result = self.mod.validate_spec(spec)
        self.assertFalse(result["ok"])
        self.assertTrue(any("kick_relationship" in error for error in result["errors"]))

    def test_rejects_unknown_section_role_tracks(self):
        spec = self.valid_spec()
        spec["sections"][0]["foreground"] = ["Lead"]

        result = self.mod.validate_spec(spec)

        self.assertFalse(result["ok"])
        self.assertIn("sections[0].foreground includes unknown track 'Lead'", result["errors"])

    def test_rejects_invalid_timing_metadata(self):
        spec = self.valid_spec()
        spec["tracks"][0]["timing_feel"] = "shuffle"
        spec["tracks"][0]["swing_amount"] = 1.2

        result = self.mod.validate_spec(spec)

        self.assertFalse(result["ok"])
        self.assertIn("tracks[0].swing_amount must be 0.0-1.0", result["errors"])

    def test_rejects_path_like_handoff_browser_queries(self):
        spec = self.valid_spec()
        spec["handoff"]["browser_queries"] = ["drums/Kits/Fake Kit.adg"]

        result = self.mod.validate_spec(spec)

        self.assertFalse(result["ok"])
        self.assertIn("handoff.browser_queries[0] must be a search query or placeholder, not a path", result["errors"])

    def test_accepts_user_sample_assets(self):
        result = self.mod.validate_spec(self.amen_spec("audio_loop"))

        self.assertTrue(result["ok"], result["errors"])

    def test_rejects_path_like_browser_query_even_with_sample_assets(self):
        spec = self.amen_spec("audio_loop")
        spec["tracks"][0]["browser_query"] = "/Users/alice/Music/Samples/amen.wav"
        spec["handoff"]["browser_queries"] = ["file:///Users/alice/Music/Samples/amen.wav"]

        result = self.mod.validate_spec(spec)

        self.assertFalse(result["ok"])
        self.assertIn("tracks[0].browser_query must be a search query or placeholder, not a path", result["errors"])
        self.assertIn("handoff.browser_queries[0] must be a search query or placeholder, not a path", result["errors"])

    def test_rejects_invalid_sample_ref(self):
        spec = self.amen_spec("audio_loop")
        spec["tracks"][0]["sample_ref"] = "missing_break"

        result = self.mod.validate_spec(spec)

        self.assertFalse(result["ok"])
        self.assertIn("tracks[0].sample_ref references unknown sample asset 'missing_break'", result["errors"])

    def test_rejects_invalid_slice_plan(self):
        spec = self.amen_spec("sliced_audio")
        spec["tracks"][0]["slice_plan"]["slice_count"] = 200
        spec["tracks"][0]["slice_plan"]["start_pad"] = 120

        result = self.mod.validate_spec(spec)

        self.assertFalse(result["ok"])
        self.assertIn("tracks[0].slice_plan.slice_count must keep generated pitches in MIDI range", result["errors"])

    def test_cli_returns_nonzero_for_invalid_spec_file(self):
        spec = self.valid_spec()
        spec["tracks"][0]["notes"][0]["duration"] = 0
        with tempfile.NamedTemporaryFile("w", suffix=".json") as handle:
            json.dump(spec, handle)
            handle.flush()

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = self.mod.main([handle.name])

        self.assertEqual(exit_code, 1)


class HandoffPlanTests(unittest.TestCase):
    def setUp(self):
        self.validator = load_script("validate_composition_spec")
        self.mod = load_script("composition_spec_to_handoff_plan")

    def valid_spec(self):
        return ValidateCompositionSpecTests().valid_spec()

    def amen_spec(self, source_type="sliced_audio"):
        return ValidateCompositionSpecTests().amen_spec(source_type)

    def test_builds_ableton_handoff_plan_from_valid_spec(self):
        spec = self.valid_spec()
        spec["tracks"][0]["timing_feel"] = "garage shuffle"
        spec["tracks"][0]["swing_amount"] = 0.58

        plan = self.mod.build_handoff_plan(spec)

        self.assertEqual(plan["preflight_intent"], ["wait-ready", "doctor-if-needed", "tracks-list"])
        self.assertEqual(plan["set_tempo"], 124)
        self.assertEqual(plan["set_meter"], "4/4")
        self.assertEqual(plan["browser_searches"][0]["query"], "Drum Rack dry electronic kit")
        self.assertEqual(plan["track_plan"][1]["name"], "Bass")
        self.assertEqual(plan["clip_plan"][0]["length_beats"], 4.0)
        self.assertEqual(plan["clip_plan"][0]["timing"]["swing_amount"], 0.58)
        self.assertEqual(plan["arrangement_sections"][1]["active_tracks"], ["Drums", "Bass"])
        self.assertIn("do not invent browser paths", plan["handoff_notes"][1])

    def test_rejects_invalid_spec_before_handoff(self):
        spec = self.valid_spec()
        spec["tracks"][0]["browser_query"] = "drums/Kits/Fake Kit.adg"

        with self.assertRaisesRegex(ValueError, "browser_query"):
            self.mod.build_handoff_plan(spec)

    def test_preserves_sample_assets(self):
        plan = self.mod.build_handoff_plan(self.amen_spec("audio_loop"))

        self.assertEqual(plan["sample_assets"][0]["id"], "amen_break")
        self.assertEqual(plan["sample_assets"][0]["path_ref"], "AMEN_BREAK_WAV")

    def test_builds_audio_clip_plan_for_audio_loop(self):
        plan = self.mod.build_handoff_plan(self.amen_spec("audio_loop"))

        self.assertEqual(plan["browser_searches"], [])
        self.assertEqual(plan["audio_clip_plan"][0]["track_name"], "Amen Loop")
        self.assertEqual(plan["audio_clip_plan"][0]["source_asset_id"], "amen_break")
        self.assertEqual(plan["audio_clip_plan"][0]["warp"]["mode"], "beats")
        self.assertEqual(plan["audio_clip_plan"][0]["warp"]["target_bpm"], 170)
        self.assertEqual(plan["audio_clip_plan"][0]["gain_db"], -6.0)

    def test_builds_slice_plan_for_sliced_audio(self):
        plan = self.mod.build_handoff_plan(self.amen_spec("sliced_audio"))

        self.assertEqual(plan["browser_searches"][0]["query"], "Drum Rack for sliced break playback")
        self.assertEqual(plan["slice_plan"][0]["track_name"], "Amen Slices")
        self.assertEqual(plan["slice_plan"][0]["source_asset_id"], "amen_break")
        self.assertEqual(plan["slice_plan"][0]["slice_count"], 16)
        self.assertEqual(plan["slice_plan"][0]["trigger_note_source"]["type"], "inline")
        self.assertEqual(plan["clip_plan"][0]["note_source"]["notes"][0]["pitch"], 36)


class BreakbeatPatternToNotesTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_script("breakbeat_pattern_to_notes")

    def test_generates_trigger_notes_inside_clip(self):
        notes = self.mod.breakbeat_pattern_to_notes(
            {
                "bars": 1,
                "resolution": 16,
                "start_pad": 36,
                "slice_count": 16,
                "pattern": [0, 1, 2, 3],
                "velocity": [116, 92, 98, 84],
                "duration_steps": 1,
            }
        )

        self.assertEqual(
            notes[:2],
            [
                {"pitch": 36, "start_time": 0.0, "duration": 0.25, "velocity": 116, "mute": False},
                {"pitch": 37, "start_time": 0.25, "duration": 0.25, "velocity": 92, "mute": False},
            ],
        )
        self.assertLessEqual(notes[-1]["start_time"] + notes[-1]["duration"], 4.0)

    def test_rejects_slice_index_out_of_range(self):
        with self.assertRaisesRegex(ValueError, "slice index"):
            self.mod.breakbeat_pattern_to_notes(
                {
                    "bars": 1,
                    "resolution": 16,
                    "start_pad": 36,
                    "slice_count": 16,
                    "pattern": [16],
                }
            )


class ResolveSampleAssetsTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_script("resolve_sample_assets")

    def test_resolves_path_ref_without_checking_file_by_default(self):
        with unittest.mock.patch.dict("os.environ", {"AMEN_BREAK_WAV": "/tmp/amen.wav"}):
            asset = self.mod.resolve_asset({"id": "amen_break", "path_ref": "AMEN_BREAK_WAV"})

        self.assertEqual(asset["id"], "amen_break")
        self.assertEqual(asset["absolute_path"], str(pathlib.Path("/tmp/amen.wav").resolve(strict=False)))

    def test_rejects_url_and_file_uri_sources(self):
        for value in ("https://example.com/amen.wav", "file:///tmp/amen.wav"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "URI"):
                    self.mod.resolve_asset({"id": "amen_break", "path": value})


class RepositoryFixtureTests(unittest.TestCase):
    def setUp(self):
        self.validator = load_script("validate_composition_spec")
        self.handoff = load_script("composition_spec_to_handoff_plan")

    def test_composition_spec_examples_validate(self):
        for path in sorted((ROOT / "examples").glob("*.composition_spec.json")):
            with self.subTest(path=path.name):
                spec = json.loads(path.read_text(encoding="utf-8"))
                result = self.validator.validate_spec(spec)
                self.assertTrue(result["ok"], result["errors"])

    def test_handoff_plan_example_matches_schema_shape(self):
        path = ROOT / "examples" / "ableton_handoff_plan.example.json"
        plan = json.loads(path.read_text(encoding="utf-8"))
        expected_fields = {
            "preflight_intent",
            "set_tempo",
            "set_meter",
            "browser_searches",
            "track_plan",
            "clip_plan",
            "arrangement_sections",
            "handoff_notes",
            "export_target",
        }

        self.assertTrue(expected_fields.issubset(plan.keys()))

    def test_eval_prompt_set_has_30_cases_and_threshold(self):
        prompts_path = ROOT.parent / "evals" / "compose-music.prompts.csv"
        with prompts_path.open("r", encoding="utf-8") as handle:
            prompts = list(csv.DictReader(handle))

        self.assertEqual(len(prompts), 30)
        runner_text = (ROOT.parent / "evals" / "run-compose-music-evals.mjs").read_text(encoding="utf-8")
        self.assertIn("minScore: 0.9", runner_text)


if __name__ == "__main__":
    unittest.main()
