import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_script(name):
    script = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CutupPatternToNotesTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_script("cutup_pattern_to_notes")

    def test_converts_16_step_slice_pattern_to_notes(self):
        notes = self.mod.cutup_pattern_to_notes(
            {
                "clip_length_bars": 1,
                "step_unit": "1/16",
                "slice_map": {"S01": 36, "S02": 37},
                "pattern": ["S01", ".", "S02", "."],
                "default_duration": 0.25,
                "default_velocity": 96,
            }
        )

        self.assertEqual(
            notes,
            [
                {"pitch": 36, "start_time": 0.0, "duration": 0.25, "velocity": 96, "mute": False},
                {"pitch": 37, "start_time": 0.5, "duration": 0.25, "velocity": 96, "mute": False},
            ],
        )

    def test_expands_stutter_inside_one_step(self):
        notes = self.mod.cutup_pattern_to_notes(
            {
                "clip_length_bars": 1,
                "step_unit": "1/16",
                "slice_map": {"S03": 38},
                "pattern": ["S03*4"],
                "default_velocity": 88,
            }
        )

        self.assertEqual([note["start_time"] for note in notes], [0.0, 0.0625, 0.125, 0.1875])
        self.assertTrue(all(note["duration"] == 0.0625 for note in notes))
        self.assertTrue(all(note["pitch"] == 38 for note in notes))

    def test_supports_triplet_step_units(self):
        notes = self.mod.cutup_pattern_to_notes(
            {
                "clip_length_bars": 1,
                "step_unit": "1/8T",
                "slice_map": {"S01": 36, "S02": 37},
                "pattern": ["S01", "S02"],
            }
        )

        self.assertEqual([note["start_time"] for note in notes], [0.0, 0.333333])

    def test_rejects_unknown_slice_and_out_of_range_pitch(self):
        with self.assertRaisesRegex(ValueError, "unknown slice"):
            self.mod.cutup_pattern_to_notes(
                {
                    "clip_length_bars": 1,
                    "step_unit": "1/16",
                    "slice_map": {"S01": 36},
                    "pattern": ["S02"],
                }
            )

        with self.assertRaisesRegex(ValueError, "MIDI range"):
            self.mod.cutup_pattern_to_notes(
                {
                    "clip_length_bars": 1,
                    "step_unit": "1/16",
                    "slice_map": {"S01": 128},
                    "pattern": ["S01"],
                }
            )


if __name__ == "__main__":
    unittest.main()
