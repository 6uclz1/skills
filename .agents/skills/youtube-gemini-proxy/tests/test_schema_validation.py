import importlib.util
import json
import pathlib
import unittest
from argparse import Namespace


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "youtube_gemini_proxy.py"
VALIDATOR = ROOT / "scripts" / "validate_output.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SchemaValidationTests(unittest.TestCase):
    def setUp(self):
        self.proxy = load_module("youtube_gemini_proxy", SCRIPT)
        self.validator = load_module("validate_output", VALIDATOR)
        self.video = self.proxy.parse_youtube_url("https://youtu.be/jNQXAC9IVRw")

    def load_fixture(self, name):
        with open(ROOT / "tests" / "fixtures" / name, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def test_normalizes_summary_response(self):
        payload = self.proxy.normalize_result(
            video=self.video,
            provider="gemini-cli",
            mode="summary",
            model_payload=self.load_fixture("summary_response.json"),
            retrieved_at="2026-05-05T00:00:00+00:00",
        )

        self.validator.validate_output(payload)
        self.assertEqual(payload["source"]["provider"], "gemini-cli")
        self.assertFalse(payload["source"]["is_official_caption"])
        self.assertEqual(payload["result"]["key_points"][0], "The speaker is at a zoo.")

    def test_transcript_is_never_marked_official_for_cli_path(self):
        fixture = self.load_fixture("transcript_response.json")
        fixture["is_official_caption"] = True

        payload = self.proxy.normalize_result(
            video=self.video,
            provider="gemini-cli",
            mode="transcript",
            model_payload=fixture,
            retrieved_at="2026-05-05T00:00:00+00:00",
        )

        self.validator.validate_output(payload)
        self.assertFalse(payload["source"]["is_official_caption"])
        self.assertEqual(payload["result"]["transcript_type"], "model_generated")
        self.assertIn("model-generated transcript; not official captions", payload["warnings"])

    def test_parses_json_from_gemini_markdown_fence_once(self):
        parsed = self.proxy.parse_model_json('```json\\n{"summary": "ok", "warnings": []}\\n```')

        self.assertEqual(parsed["summary"], "ok")

    def test_invalid_payload_fails_validation(self):
        with self.assertRaises(self.validator.ValidationError):
            self.validator.validate_output({"video": {}})

    def test_invalid_url_returns_normalized_error_payload(self):
        payload = self.proxy.run_proxy(
            Namespace(
                url="https://example.com/watch?v=jNQXAC9IVRw",
                mode="summary",
                lang="ja",
                model=None,
                timeout=1,
                gemini_bin="gemini",
                enable_api_fallback=False,
            )
        )

        self.validator.validate_output(payload)
        self.assertEqual(payload["video"]["url"], "https://example.com/watch?v=jNQXAC9IVRw")
        self.assertEqual(payload["video"]["video_id"], "unknown")
        self.assertTrue(payload["warnings"][0].startswith("unsupported_domain:"))


if __name__ == "__main__":
    unittest.main()
