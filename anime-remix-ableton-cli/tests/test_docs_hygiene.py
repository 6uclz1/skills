import json
import re
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
FORMS_PATH = SKILL_DIR / "examples" / "arrangement_forms.json"


class AnimeRemixDocsHygieneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill_md = (SKILL_DIR / "SKILL.md").read_text()
        cls.forms = json.loads(FORMS_PATH.read_text())
        cls.section_template = (SKILL_DIR / "templates" / "section_map_template.md").read_text()
        cls.qa_checklist = (SKILL_DIR / "templates" / "qa_checklist.md").read_text()
        cls.examples = {
            path.name: path.read_text()
            for path in (SKILL_DIR / "examples").glob("*_private_test.md")
        }

    def test_skill_documents_dynamic_arrangement_contract(self):
        self.assertIn("## Dynamic Arrangement Rules", self.skill_md)
        self.assertRegex(self.skill_md, r"energy scale")
        self.assertIn("`0`", self.skill_md)
        self.assertIn("`5`", self.skill_md)
        self.assertIn("`--dynamics section-profiles`", self.skill_md)
        for term in ("section energy", "drum_policy", "bass_policy"):
            self.assertIn(term, self.skill_md)
        for policy in ("off", "light", "build_only", "reduced", "full", "full_with_variation"):
            self.assertIn(f"`{policy}`", self.skill_md)

    def test_arrangement_forms_use_section_objects_with_compat_names(self):
        for style, form in self.forms.items():
            self.assertIsInstance(form.get("section_names"), list, style)
            self.assertIsInstance(form.get("sections"), list, style)
            self.assertEqual(
                form["section_names"],
                [section["name"] for section in form["sections"]],
                style,
            )
            for section in form["sections"]:
                with self.subTest(style=style, section=section):
                    self.assertIsInstance(section, dict)
                    self.assertIn("name", section)
                    self.assertIn("default_bars", section)
                    self.assertIn("energy", section)
                    self.assertIn("drum_policy", section)
                    self.assertIsInstance(section["energy"], int)
                    self.assertGreaterEqual(section["energy"], 0)
                    self.assertLessEqual(section["energy"], 5)

    def test_required_section_drum_policies(self):
        by_style = {
            style: {section["name"]: section for section in form["sections"]}
            for style, form in self.forms.items()
        }
        self.assertEqual(by_style["anime-club"]["breakdown"]["drum_policy"], "off")
        self.assertEqual(by_style["anime-dnb"]["bridge"]["drum_policy"], "off")
        self.assertEqual(by_style["anime-future-bass"]["intro_pad"]["drum_policy"], "off")
        self.assertEqual(by_style["anime-future-bass"]["breakdown"]["drum_policy"], "off")

        for style, sections in by_style.items():
            for name in ("drop", "chorus_drop", "final_drop", "second_drop"):
                if name in sections:
                    self.assertIn(
                        sections[name]["drum_policy"],
                        {"full", "full_with_variation"},
                        f"{style}:{name}",
                    )

    def test_templates_include_dynamic_columns_and_qa(self):
        self.assertIn("Energy", self.section_template)
        self.assertIn("Drum policy", self.section_template)
        self.assertIn("Notes", self.section_template)
        self.assertIn("## Arrangement Dynamics", self.qa_checklist)
        for term in ("energy", "Drum-off", "full rhythmic density"):
            self.assertIn(term, self.qa_checklist)

    def test_examples_match_arrangement_form_policies(self):
        by_style = {
            style: {section["name"]: section for section in form["sections"]}
            for style, form in self.forms.items()
        }
        style_by_example = {
            "anime_club_private_test.md": "anime-club",
            "anime_dnb_private_test.md": "anime-dnb",
        }
        for filename, style in style_by_example.items():
            text = self.examples[filename]
            for section_name, section in by_style[style].items():
                policy_line = re.compile(
                    rf"- {re.escape(section_name)}: .*drum_policy `{section['drum_policy']}`",
                    re.IGNORECASE,
                )
                self.assertRegex(text, policy_line, f"{filename}:{section_name}")


if __name__ == "__main__":
    unittest.main()
