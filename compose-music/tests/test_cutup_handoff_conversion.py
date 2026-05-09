import importlib.util
import pathlib
import unittest

from test_validate_cutup_spec import valid_cutup_spec


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_script(name):
    script = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CutupHandoffConversionTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_script("composition_spec_to_handoff_plan")

    def test_preserves_cutup_audio_slice_and_trigger_intent(self):
        plan = self.mod.build_handoff_plan(valid_cutup_spec())

        self.assertEqual(plan["audio_asset_plan"][0]["track"], "Cutup Rack")
        self.assertEqual(plan["audio_asset_plan"][0]["rights_status"], "private_test")
        self.assertEqual(plan["slice_plan"][0]["target_track"], "Cutup Rack")
        self.assertEqual(plan["slice_plan"][0]["method"], "transient")
        self.assertEqual(plan["slice_plan"][0]["max_slices"], 12)
        self.assertEqual(plan["cutup_trigger_plan"][0]["track"], "Cutup Rack")
        self.assertEqual(plan["cutup_trigger_plan"][0]["clip_slot"], 1)
        self.assertEqual(plan["cutup_trigger_plan"][0]["notes_source"], "inline")
        self.assertEqual(plan["cut_to_drum_rack_requests"][0]["track"], "Cutup Rack")

    def test_warns_before_executing_unknown_rights(self):
        spec = valid_cutup_spec()
        spec["tracks"][0]["source_material"]["rights_status"] = "unknown"
        spec["handoff"]["sample_assets"][0]["rights_status"] = "unknown"
        spec["handoff"]["export_target"] = "private test render"

        plan = self.mod.build_handoff_plan(spec)

        self.assertTrue(any("unknown rights_status" in warning for warning in plan["execution_warnings"]))


if __name__ == "__main__":
    unittest.main()
