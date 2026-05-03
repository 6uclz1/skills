import importlib.util
import contextlib
import io
import json
import pathlib
import tempfile
import unittest


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

    def test_rejects_unsupported_grid_symbols(self):
        with self.assertRaisesRegex(ValueError, "unsupported step symbol"):
            self.mod.grid_to_notes(
                {
                    "bars": 1,
                    "resolution": 16,
                    "tracks": {"Kick": {"pitch": 36, "steps": "X...?...X...X..."}},
                }
            )


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
            "finish_criteria": [
                "8-bar arrangement exists",
                "kick and bass do not mask each other",
                "one bounce/export target is named",
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


if __name__ == "__main__":
    unittest.main()
