import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "gemini_cli_runner.py"


def load_module():
    spec = importlib.util.spec_from_file_location("gemini_cli_runner", RUNNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GeminiCliRunnerTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()

    def test_summarizes_account_validation_without_paths_or_urls(self):
        stderr = (
            "Full report available at: /var/folders/example/report.json\n"
            "ValidationRequiredError: Verify your account to continue.\n"
            "validationLink: 'https://accounts.google.com/signin/continue?secret=abc'\n"
        )

        summary = self.mod._summarize_cli_error(stderr, "")

        self.assertEqual(
            summary,
            "Verify your account to continue (Gemini CLI authentication/account validation required)",
        )
        self.assertNotIn("/var/folders", summary)
        self.assertNotIn("accounts.google.com", summary)


if __name__ == "__main__":
    unittest.main()
