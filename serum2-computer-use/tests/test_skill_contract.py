import json
import re
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]


class Serum2ComputerUseSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill_md = (SKILL_DIR / "SKILL.md").read_text()
        cls.parameter_map = json.loads((SKILL_DIR / "references" / "parameter_map.json").read_text())
        cls.operations = json.loads((SKILL_DIR / "references" / "operation_contract.json").read_text())
        cls.policy = (SKILL_DIR / "references" / "operation_policy.md").read_text()
        cls.openai_yaml = (SKILL_DIR / "agents" / "openai.yaml").read_text()

    def test_skill_frontmatter_targets_serum2_ableton_and_computer_use(self):
        self.assertRegex(self.skill_md, r"^---\n", "SKILL.md must start with YAML frontmatter")
        self.assertIn("name: serum2-computer-use", self.skill_md)
        self.assertRegex(self.skill_md, r"description: .*Serum 2", re.DOTALL)
        self.assertRegex(self.skill_md, r"description: .*Ableton Live", re.DOTALL)
        self.assertRegex(self.skill_md, r"description: .*Computer Use", re.DOTALL)

    def test_skill_documents_layering_safety_and_mvp_flow(self):
        required_sections = [
            "## Core Workflow",
            "## Control Priority",
            "## Computer Use Loop",
            "## Safety Stops",
            "## MVP Checklist",
            "## Verification",
        ]
        for section in required_sections:
            self.assertIn(section, self.skill_md)

        for phrase in [
            "Rack Macro",
            "Configure Mode",
            "post-action screenshot",
            "do not save, export, overwrite, delete, upload, purchase, log in, or change licenses",
            "SERUM_AGENT",
            "ComputerUse_Serum_Template.als",
        ]:
            self.assertIn(phrase, self.skill_md)

    def test_parameter_map_contains_initial_macro_and_core_parameters(self):
        expected_macros = {
            "Brightness",
            "Bite",
            "Movement",
            "Attack",
            "Decay",
            "Release",
            "Space",
            "Width",
        }
        self.assertEqual(set(self.parameter_map["rack_macros"].keys()), expected_macros)

        expected_parameters = {
            "osc_a_level",
            "osc_a_wt_pos",
            "osc_b_level",
            "noise_level",
            "sub_level",
            "filter_cutoff",
            "filter_resonance",
            "filter_drive",
            "filter_mix",
            "env1_attack",
            "env1_decay",
            "env1_sustain",
            "env1_release",
            "lfo1_rate",
            "lfo1_amount_to_cutoff",
            "lfo1_amount_to_wt_pos",
            "distortion_drive",
            "hyper_dimension_mix",
            "chorus_mix",
            "delay_mix",
            "reverb_mix",
            "eq_low",
            "eq_high",
            "compressor_mix",
        }
        self.assertEqual(set(self.parameter_map["parameters"].keys()), expected_parameters)

        for name, spec in self.parameter_map["parameters"].items():
            with self.subTest(parameter=name):
                self.assertIn(spec["preferred_method"], {"rack_macro", "live_panel", "max_for_live"})
                self.assertIn("fallback_method", spec)
                self.assertIn("ui_hint", spec)

    def test_operation_contract_has_primitives_mvp_and_failure_recovery(self):
        primitive_names = {primitive["name"] for primitive in self.operations["operations"]}
        for name in [
            "open_serum_window",
            "select_serum_preset",
            "set_macro",
            "set_live_panel_parameter",
            "set_serum_gui_knob",
            "create_midi_test_clip",
            "render_audio_preview",
        ]:
            self.assertIn(name, primitive_names)

        self.assertEqual(
            [mvp["id"] for mvp in self.operations["mvp"]],
            ["mvp_1_open_set", "mvp_2_select_preset", "mvp_3_macro_edit", "mvp_4_sound_intent"],
        )

        for failure_class in [
            "ui_not_found",
            "wrong_window",
            "drag_inaccurate",
            "parameter_not_exposed",
            "audio_silent",
            "modal_dialog",
        ]:
            self.assertIn(failure_class, self.operations["failure_classes"])

    def test_policy_and_openai_yaml_are_agent_ready(self):
        for rule in [
            "Prefer Live panel, Rack Macro, Max for Live, Remote Script, or keyboard shortcuts before Serum GUI.",
            "Only use Serum GUI when the target UI is visible in the screenshot.",
            "Stop on destructive/account/license/payment dialogs",
        ]:
            self.assertIn(rule, self.policy)

        self.assertIn('display_name: "Serum 2 Computer Use"', self.openai_yaml)
        self.assertIn("$serum2-computer-use", self.openai_yaml)


if __name__ == "__main__":
    unittest.main()
