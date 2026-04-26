---
name: tech-news-digest
description: Gather and summarize recent technology signals from representative English and Japanese developer communities using RSS/Atom/RDF feeds first. Use when Codex should scan tech communities, create a concise tech-news digest, compare English/Japanese trends, monitor software/AI/web/infrastructure/security topics, or identify a small set of articles worth deeper review without bulk scraping article HTML.
license: MIT
---

# Tech News Digest

## Workflow

Use the bundled scanner before browsing individual articles:

```bash
python3 scripts/scan_tech_feeds.py --sources references/default_sources.json --days 3 --top 20 --detail-candidates 5 --format markdown
```

Use `python` instead of `python3` when that is the available interpreter. Add `--format json` when you need structured data for additional processing.

## Source Strategy

- Prefer RSS, Atom, and RDF feeds from `references/default_sources.json`.
- Do not bulk-fetch article pages or scrape HTML directly during the broad scan.
- Read only the feed-provided title, URL, published time, source, language, and short summary/description.
- Inspect full article pages only for the highest-value `detail_candidate` items, and only as needed to answer the user.
- If a feed fails, keep going and mention important gaps in the final digest.

## Interest Tuning

Use keyword flags to adapt the scan without editing the default source file:

```bash
python3 scripts/scan_tech_feeds.py --include-keyword rust --include-keyword security --exclude-keyword sponsored
```

Use repeated flags or comma-separated values. Treat include keywords as score boosts, not hard filters; treat exclude keywords as filters.

If network calls are slow, lower the per-feed timeout:

```bash
python3 scripts/scan_tech_feeds.py --timeout 6 --top 10
```

## Digest Format

After scanning, produce a concise digest with these sections:

- **Top signals**: 3-7 cross-community or high-impact themes with source links.
- **English communities**: notable items from Hacker News, Lobsters, Reddit, DEV, or similar English-language sources.
- **Japanese communities**: notable items from Hatena Bookmark IT, Qiita, Zenn, JSer.info, Publickey, or similar Japanese-language sources.
- **Worth deeper read**: the few articles most worth opening and reading closely, with why they matter.
- **Sources checked**: feeds checked, feed failures, and the time window.

Keep summaries short. Clearly distinguish feed-derived summaries from conclusions made after reading a selected article.
