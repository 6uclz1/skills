import importlib.util
import json
import pathlib
import textwrap
import unittest
from datetime import datetime, timezone


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "scan_tech_feeds.py"


def load_module():
    spec = importlib.util.spec_from_file_location("scan_tech_feeds", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RSS_FEED = textwrap.dedent(
    """\
    <?xml version="1.0"?>
    <rss version="2.0">
      <channel>
        <title>Example RSS</title>
        <item>
          <title>Postgres 19 adds adaptive indexing</title>
          <link>https://example.com/postgres-adaptive-indexing</link>
          <pubDate>Sun, 26 Apr 2026 08:00:00 +0000</pubDate>
          <description><![CDATA[Deep database internals with benchmarks and production notes.]]></description>
        </item>
      </channel>
    </rss>
    """
)


ATOM_FEED = textwrap.dedent(
    """\
    <?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <title>Kubernetes security release changes defaults</title>
        <link rel="alternate" href="https://example.com/kubernetes-security"/>
        <updated>2026-04-25T12:30:00+00:00</updated>
        <summary>Security, infra, and upgrade notes for cluster operators.</summary>
      </entry>
    </feed>
    """
)


RDF_FEED = textwrap.dedent(
    """\
    <?xml version="1.0" encoding="UTF-8"?>
    <rdf:RDF
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns="http://purl.org/rss/1.0/"
      xmlns:dc="http://purl.org/dc/elements/1.1/">
      <item rdf:about="https://example.com/rdf-ai">
        <title>Browser AI APIs reach stable</title>
        <link>https://example.com/rdf-ai</link>
        <dc:date>2026-04-24T09:00:00+00:00</dc:date>
        <description>Web platform and AI API coverage from a Japanese source.</description>
      </item>
    </rdf:RDF>
    """
)


class ScanTechFeedsTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()
        self.now = datetime(2026, 4, 26, 12, 0, tzinfo=timezone.utc)

    def test_parses_rss_atom_and_rdf_items(self):
        sources = [
            {
                "id": "rss",
                "name": "RSS Source",
                "language": "en",
                "url": "https://feeds.example.com/rss.xml",
                "weight": 1.0,
                "tags": ["database"],
            },
            {
                "id": "atom",
                "name": "Atom Source",
                "language": "en",
                "url": "https://feeds.example.com/atom.xml",
                "weight": 1.0,
                "tags": ["infra"],
            },
            {
                "id": "rdf",
                "name": "RDF Source",
                "language": "ja",
                "url": "https://feeds.example.com/rdf.xml",
                "weight": 1.0,
                "tags": ["web"],
            },
        ]
        feed_by_url = {
            sources[0]["url"]: RSS_FEED,
            sources[1]["url"]: ATOM_FEED,
            sources[2]["url"]: RDF_FEED,
        }

        result = self.mod.scan_sources(
            sources,
            fetcher=lambda url: feed_by_url[url],
            now=self.now,
            days=7,
            top=10,
            detail_candidates=2,
        )

        titles = {item["title"] for item in result["items"]}
        self.assertEqual(result["sources_checked"], 3)
        self.assertIn("Postgres 19 adds adaptive indexing", titles)
        self.assertIn("Kubernetes security release changes defaults", titles)
        self.assertIn("Browser AI APIs reach stable", titles)

    def test_fetches_feed_urls_only_not_article_pages(self):
        source = {
            "id": "rss",
            "name": "RSS Source",
            "language": "en",
            "url": "https://feeds.example.com/rss.xml",
            "weight": 1.0,
            "tags": [],
        }
        calls = []

        def fetcher(url):
            calls.append(url)
            if url != source["url"]:
                raise AssertionError(f"unexpected article fetch: {url}")
            return RSS_FEED

        result = self.mod.scan_sources(
            [source],
            fetcher=fetcher,
            now=self.now,
            days=7,
            top=5,
            detail_candidates=1,
        )

        self.assertEqual(calls, [source["url"]])
        self.assertEqual(result["items"][0]["url"], "https://example.com/postgres-adaptive-indexing")

    def test_deduplicates_by_url_and_records_multiple_sources(self):
        duplicate_feed = RSS_FEED.replace(
            "Postgres 19 adds adaptive indexing",
            "Postgres 19 adds adaptive indexing - discussion",
        )
        sources = [
            {
                "id": "a",
                "name": "A",
                "language": "en",
                "url": "https://feeds.example.com/a.xml",
                "weight": 1.0,
                "tags": [],
            },
            {
                "id": "b",
                "name": "B",
                "language": "en",
                "url": "https://feeds.example.com/b.xml",
                "weight": 1.4,
                "tags": [],
            },
        ]
        feeds = {sources[0]["url"]: RSS_FEED, sources[1]["url"]: duplicate_feed}

        result = self.mod.scan_sources(
            sources,
            fetcher=lambda url: feeds[url],
            now=self.now,
            days=7,
            top=10,
            detail_candidates=1,
        )

        self.assertEqual(len(result["items"]), 1)
        item = result["items"][0]
        self.assertEqual(item["source_id"], "b")
        self.assertIn("seen in 2 sources", item["reasons"])

    def test_scores_keywords_filters_old_and_excluded_items(self):
        source = {
            "id": "rss",
            "name": "RSS Source",
            "language": "en",
            "url": "https://feeds.example.com/rss.xml",
            "weight": 1.0,
            "tags": [],
        }
        feed = textwrap.dedent(
            """\
            <rss version="2.0"><channel>
              <item>
                <title>Rust compiler security audit lands</title>
                <link>https://example.com/rust-security</link>
                <pubDate>Sun, 26 Apr 2026 09:00:00 +0000</pubDate>
                <description>Compiler, security, and tooling details.</description>
              </item>
              <item>
                <title>Old machine learning paper notes</title>
                <link>https://example.com/old-ml</link>
                <pubDate>Mon, 20 Apr 2026 09:00:00 +0000</pubDate>
                <description>Too old for the window.</description>
              </item>
              <item>
                <title>Sponsored cloud benchmark</title>
                <link>https://example.com/sponsored-cloud</link>
                <pubDate>Sun, 26 Apr 2026 09:00:00 +0000</pubDate>
                <description>Advertisement.</description>
              </item>
            </channel></rss>
            """
        )

        result = self.mod.scan_sources(
            [source],
            fetcher=lambda url: feed,
            now=self.now,
            days=3,
            top=10,
            detail_candidates=1,
            include_keywords=["rust", "security"],
            exclude_keywords=["sponsored"],
        )

        self.assertEqual([item["title"] for item in result["items"]], ["Rust compiler security audit lands"])
        self.assertIn("keyword: rust", result["items"][0]["reasons"])
        self.assertIn("keyword: security", result["items"][0]["reasons"])
        self.assertTrue(result["items"][0]["detail_candidate"])

    def test_continues_after_broken_feed(self):
        sources = [
            {
                "id": "broken",
                "name": "Broken",
                "language": "en",
                "url": "https://feeds.example.com/broken.xml",
                "weight": 1.0,
                "tags": [],
            },
            {
                "id": "ok",
                "name": "OK",
                "language": "en",
                "url": "https://feeds.example.com/ok.xml",
                "weight": 1.0,
                "tags": [],
            },
        ]

        def fetcher(url):
            if url.endswith("broken.xml"):
                raise RuntimeError("network failure")
            return RSS_FEED

        result = self.mod.scan_sources(
            sources,
            fetcher=fetcher,
            now=self.now,
            days=7,
            top=10,
            detail_candidates=1,
        )

        self.assertEqual(result["sources_checked"], 2)
        self.assertEqual(result["sources_succeeded"], 1)
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(result["errors"][0]["source_id"], "broken")
        self.assertEqual(len(result["items"]), 1)

    def test_json_output_contract_is_stable(self):
        source = {
            "id": "rss",
            "name": "RSS Source",
            "language": "en",
            "url": "https://feeds.example.com/rss.xml",
            "weight": 1.0,
            "tags": [],
        }
        result = self.mod.scan_sources(
            [source],
            fetcher=lambda url: RSS_FEED,
            now=self.now,
            days=7,
            top=10,
            detail_candidates=1,
        )
        encoded = self.mod.render_json(result)
        decoded = json.loads(encoded)
        item = decoded["items"][0]

        self.assertEqual(
            set(item),
            {
                "rank",
                "score",
                "title",
                "url",
                "source_id",
                "source_name",
                "language",
                "published",
                "summary",
                "reasons",
                "detail_candidate",
            },
        )


if __name__ == "__main__":
    unittest.main()
