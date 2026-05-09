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


def valid_cutup_spec():
    return {
        "version": "1.0",
        "brief": {
            "genre": "cut-up garage",
            "bpm": 134,
            "meter": "4/4",
            "key": "D",
            "mode": "minor",
            "length_bars": 8,
            "creative_constraint": "only 12 vocal slices; no full lyric phrase",
            "sampling_policy": {
                "allowed_sources": ["original", "cleared", "royalty_free", "private_test"],
                "requires_user_provided_audio_for_execution": True,
            },
        },
        "tracks": [
            {
                "name": "Cutup Rack",
                "role": "foreground sample-slice identity",
                "source_type": "sliced_audio",
                "clip_length_bars": 2,
                "browser_query": "Drum Rack slicing preset or empty Drum Rack",
                "source_material": {
                    "kind": "user_audio_file",
                    "role": "vocal",
                    "path": "<user-provided-audio-path>",
                    "rights_status": "private_test",
                    "source_bpm": None,
                    "source_key": None,
                },
                "slice_plan": {
                    "method": "transient",
                    "max_slices": 12,
                    "start_pad_midi": 36,
                    "create_trigger_clip": True,
                    "trigger_clip_slot": 1,
                    "warp_mode": "beats_or_complex_pro",
                    "preserve_timing": True,
                },
                "cutup_pattern": {
                    "unit": "1/16",
                    "slice_map": {"S01": 36, "S02": 37, "S03": 38},
                    "motif": ["S01", ".", "S03", "S02"],
                    "variation_strategy": "change final beat only",
                },
                "notes": [
                    {"pitch": 36, "start_time": 0.0, "duration": 0.25, "velocity": 100, "mute": False},
                    {"pitch": 38, "start_time": 0.5, "duration": 0.25, "velocity": 88, "mute": False},
                ],
            }
        ],
        "sections": [
            {
                "name": "Groove",
                "start_bar": 1,
                "length_bars": 4,
                "density": 3,
                "active_tracks": ["Cutup Rack"],
            },
            {
                "name": "Variation",
                "start_bar": 5,
                "length_bars": 4,
                "density": 4,
                "active_tracks": ["Cutup Rack"],
            },
        ],
        "handoff": {
            "requires_browser_search": True,
            "browser_queries": ["Drum Rack", "Beat Repeat", "Simple Delay"],
            "requires_audio_import": True,
            "sample_assets": [
                {
                    "track": "Cutup Rack",
                    "source": "<user-provided-audio-path>",
                    "rights_status": "private_test",
                    "intended_use": "slice_to_drum_rack",
                }
            ],
            "cut_to_drum_rack_requests": [
                {
                    "track": "Cutup Rack",
                    "source_file": "<user-provided-audio-path>",
                    "method": "transient",
                    "max_slices": 12,
                    "create_trigger_clip": True,
                }
            ],
            "export_target": "rough cut-up arrangement render",
        },
        "finish_criteria": ["cut-up motif is recognizable", "sample execution waits for user-provided audio"],
    }


class ValidateCutupSpecTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_script("validate_composition_spec")

    def test_accepts_valid_cutup_source_material_slice_plan_and_pattern(self):
        result = self.mod.validate_spec(valid_cutup_spec())

        self.assertTrue(result["ok"], result["errors"])

    def test_rejects_slice_plan_that_exceeds_midi_pad_range(self):
        spec = valid_cutup_spec()
        spec["tracks"][0]["slice_plan"]["start_pad_midi"] = 120
        spec["tracks"][0]["slice_plan"]["max_slices"] = 16

        result = self.mod.validate_spec(spec)

        self.assertFalse(result["ok"])
        self.assertIn("tracks[0].slice_plan.max_slices must keep generated pitches in MIDI range", result["errors"])

    def test_rejects_missing_rights_status(self):
        spec = valid_cutup_spec()
        del spec["tracks"][0]["source_material"]["rights_status"]

        result = self.mod.validate_spec(spec)

        self.assertFalse(result["ok"])
        self.assertIn("tracks[0].source_material.rights_status is required", result["errors"])

    def test_rejects_unknown_rights_for_commercial_export(self):
        spec = valid_cutup_spec()
        spec["tracks"][0]["source_material"]["rights_status"] = "unknown"
        spec["handoff"]["sample_assets"][0]["rights_status"] = "unknown"
        spec["handoff"]["export_target"] = "commercial release master"

        result = self.mod.validate_spec(spec)

        self.assertFalse(result["ok"])
        self.assertIn("rights_status unknown cannot be used for commercial or public export targets", result["errors"])

    def test_rejects_fake_uri_in_cut_to_drum_rack_request(self):
        spec = valid_cutup_spec()
        spec["handoff"]["cut_to_drum_rack_requests"][0]["source_file"] = "file:///tmp/fake.wav"

        result = self.mod.validate_spec(spec)

        self.assertFalse(result["ok"])
        self.assertIn("handoff.cut_to_drum_rack_requests[0].source_file must be a placeholder or deferred user path, not a URI", result["errors"])


if __name__ == "__main__":
    unittest.main()
