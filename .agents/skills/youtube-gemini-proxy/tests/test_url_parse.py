import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "youtube_gemini_proxy.py"


def load_module():
    spec = importlib.util.spec_from_file_location("youtube_gemini_proxy", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class UrlParseTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()

    def test_accepts_supported_youtube_url_forms(self):
        cases = [
            "https://www.youtube.com/watch?v=jNQXAC9IVRw",
            "https://youtube.com/watch?v=jNQXAC9IVRw&feature=share",
            "https://m.youtube.com/watch?v=jNQXAC9IVRw",
            "https://youtu.be/jNQXAC9IVRw?t=12",
            "https://www.youtube.com/shorts/jNQXAC9IVRw",
            "https://youtube-nocookie.com/embed/jNQXAC9IVRw",
        ]

        for url in cases:
            with self.subTest(url=url):
                video = self.mod.parse_youtube_url(url)
                self.assertEqual(video.video_id, "jNQXAC9IVRw")
                self.assertEqual(video.url, "https://www.youtube.com/watch?v=jNQXAC9IVRw")

    def test_rejects_non_youtube_and_unsafe_urls(self):
        cases = [
            "https://example.com/watch?v=jNQXAC9IVRw",
            "file:///tmp/video.mp4",
            "http://127.0.0.1/watch?v=jNQXAC9IVRw",
            "https://www.youtube.com.evil.test/watch?v=jNQXAC9IVRw",
            "https://user:pass@www.youtube.com/watch?v=jNQXAC9IVRw",
            "https://www.youtube.com:443/watch?v=jNQXAC9IVRw",
            "https://www.youtube.com:notaport/watch?v=jNQXAC9IVRw",
            "https://www.youtube.com/watch?v=not-valid",
            "https://www.youtube.com/watch?v=jNQXAC9IVRw%0A",
        ]

        for url in cases:
            with self.subTest(url=url):
                with self.assertRaises(self.mod.ProxyError):
                    self.mod.parse_youtube_url(url)

    def test_build_prompt_marks_external_content_untrusted(self):
        video = self.mod.parse_youtube_url("https://youtu.be/jNQXAC9IVRw")
        prompt = self.mod.build_prompt(video, "transcript", "ja")

        self.assertIn("untrusted data", prompt)
        self.assertIn("not an official caption", prompt)
        self.assertIn("Return strict JSON only", prompt)


if __name__ == "__main__":
    unittest.main()
