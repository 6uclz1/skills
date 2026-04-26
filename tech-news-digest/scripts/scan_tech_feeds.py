#!/usr/bin/env python3
"""Scan RSS/Atom/RDF feeds and rank tech-news candidates.

This script intentionally fetches feed documents only. It never downloads the
article URLs found inside feeds; Codex should inspect only selected candidates.
"""

from __future__ import annotations

import argparse
import email.utils
import html
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path


DEFAULT_KEYWORDS = [
    "ai",
    "api",
    "architecture",
    "browser",
    "cloud",
    "compiler",
    "database",
    "developer",
    "devops",
    "infrastructure",
    "javascript",
    "kubernetes",
    "language",
    "llm",
    "machine learning",
    "open source",
    "performance",
    "programming",
    "python",
    "release",
    "rust",
    "security",
    "software",
    "typescript",
    "web",
    "生成ai",
    "開発",
    "機械学習",
    "セキュリティ",
]


TRACKING_PARAMS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "ref",
    "utm_campaign",
    "utm_content",
    "utm_medium",
    "utm_source",
    "utm_term",
}


def default_sources_path() -> Path:
    return Path(__file__).resolve().parents[1] / "references" / "default_sources.json"


def fetch_url(url: str, timeout: int = 20) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.1",
            "User-Agent": "tech-news-digest/1.0 (+https://github.com/)",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def load_sources(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        sources = json.load(handle)
    if not isinstance(sources, list):
        raise ValueError("sources file must contain a JSON array")
    for source in sources:
        missing = {"id", "name", "language", "url", "weight", "tags"} - set(source)
        if missing:
            raise ValueError(f"source is missing required keys: {', '.join(sorted(missing))}")
    return sources


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def child_text(element: ET.Element, names: tuple[str, ...]) -> str:
    wanted = {name.lower() for name in names}
    for child in list(element):
        if local_name(child.tag) in wanted:
            text = "".join(child.itertext()).strip()
            if text:
                return text
    return ""


def atom_link(entry: ET.Element) -> str:
    fallback = ""
    for child in list(entry):
        if local_name(child.tag) != "link":
            continue
        href = child.attrib.get("href", "").strip()
        rel = child.attrib.get("rel", "alternate").strip().lower()
        if href and rel == "alternate":
            return href
        if href and not fallback:
            fallback = href
        text = "".join(child.itertext()).strip()
        if text and not fallback:
            fallback = text
    return fallback


def clean_summary(value: str, limit: int = 360) -> str:
    text = html.unescape(value or "")
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def parse_datetime(value: str) -> datetime | None:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        parsed = email.utils.parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        parsed = None
    if parsed is None:
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def canonical_url(url: str) -> str:
    parsed = urllib.parse.urlsplit((url or "").strip())
    if not parsed.scheme or not parsed.netloc:
        return (url or "").strip().lower()
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    kept_query = [(key, value) for key, value in query if key.lower() not in TRACKING_PARAMS]
    path = parsed.path.rstrip("/") or "/"
    normalized = urllib.parse.urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            urllib.parse.urlencode(kept_query, doseq=True),
            "",
        )
    )
    return normalized.rstrip("/")


def canonical_title(title: str) -> str:
    return re.sub(r"\W+", "", title or "", flags=re.UNICODE).lower()


def item_key(item: dict) -> str:
    if item["url"]:
        return "url:" + canonical_url(item["url"])
    return "title:" + canonical_title(item["title"])


def parse_feed(feed_xml: str, source: dict) -> list[dict]:
    root = ET.fromstring(feed_xml)
    if local_name(root.tag) == "feed":
        entries = [element for element in root.iter() if local_name(element.tag) == "entry"]
        return [parse_atom_entry(entry, source) for entry in entries]
    items = [element for element in root.iter() if local_name(element.tag) == "item"]
    return [parse_rss_item(item, source) for item in items]


def parse_atom_entry(entry: ET.Element, source: dict) -> dict:
    title = child_text(entry, ("title",))
    summary = child_text(entry, ("summary", "content"))
    published = child_text(entry, ("published", "updated"))
    return normalize_item(
        {
            "title": title,
            "url": atom_link(entry),
            "published_dt": parse_datetime(published),
            "summary": clean_summary(summary),
        },
        source,
    )


def parse_rss_item(item: ET.Element, source: dict) -> dict:
    title = child_text(item, ("title",))
    summary = child_text(item, ("description", "encoded", "summary"))
    published = child_text(item, ("pubdate", "published", "updated", "date"))
    return normalize_item(
        {
            "title": title,
            "url": child_text(item, ("link",)) or item.attrib.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", ""),
            "published_dt": parse_datetime(published),
            "summary": clean_summary(summary),
        },
        source,
    )


def normalize_item(raw: dict, source: dict) -> dict:
    return {
        "title": clean_summary(raw.get("title", ""), limit=180),
        "url": (raw.get("url") or "").strip(),
        "published_dt": raw.get("published_dt"),
        "summary": raw.get("summary", ""),
        "source_id": source["id"],
        "source_name": source["name"],
        "language": source["language"],
        "source_weight": float(source.get("weight", 1.0)),
        "source_ids": {source["id"]},
        "source_names": {source["name"]},
        "source_tags": set(source.get("tags") or []),
    }


def contains_keyword(text: str, keyword: str) -> bool:
    keyword_lower = keyword.lower()
    text_lower = text.lower()
    if re.search(r"\w", keyword_lower, flags=re.ASCII):
        return bool(re.search(rf"(?<!\w){re.escape(keyword_lower)}(?!\w)", text_lower))
    return keyword_lower in text_lower


def item_text(item: dict) -> str:
    return " ".join([item.get("title", ""), item.get("summary", "")])


def should_exclude(item: dict, exclude_keywords: list[str]) -> bool:
    text = item_text(item)
    return any(contains_keyword(text, keyword) for keyword in exclude_keywords)


def score_item(item: dict, now: datetime, days: int, include_keywords: list[str]) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    source_score = max(0.0, item["source_weight"]) * 2.0
    score += source_score
    reasons.append(f"source weight {item['source_weight']:.1f}")

    published_dt = item.get("published_dt")
    if published_dt is not None:
        age_days = max(0.0, (now - published_dt).total_seconds() / 86400)
        freshness = max(0.0, 1.0 - (age_days / max(days, 1))) * 3.0
        score += freshness
        reasons.append("fresh")
    else:
        score += 0.2
        reasons.append("undated")

    summary_len = len(item.get("summary", ""))
    if summary_len >= 120:
        score += 0.8
        reasons.append("substantial summary")
    elif summary_len >= 40:
        score += 0.4
        reasons.append("has summary")

    text = item_text(item)
    matched_keywords = []
    for keyword in include_keywords:
        if contains_keyword(text, keyword):
            matched_keywords.append(keyword)
    for keyword in matched_keywords[:6]:
        score += 0.8
        reasons.append(f"keyword: {keyword}")
    if len(matched_keywords) > 6:
        score += 0.2 * (len(matched_keywords) - 6)

    source_count = len(item["source_ids"])
    if source_count > 1:
        multi_source_score = 1.25 * (source_count - 1)
        score += multi_source_score
        reasons.append(f"seen in {source_count} sources")

    return round(score, 3), reasons


def merge_duplicate(existing: dict, candidate: dict) -> dict:
    existing["source_ids"].update(candidate["source_ids"])
    existing["source_names"].update(candidate["source_names"])
    existing["source_tags"].update(candidate["source_tags"])

    if candidate["source_weight"] > existing["source_weight"]:
        existing["source_weight"] = candidate["source_weight"]
        existing["source_id"] = candidate["source_id"]
        existing["source_name"] = candidate["source_name"]
        existing["language"] = candidate["language"]

    if len(candidate.get("summary", "")) > len(existing.get("summary", "")):
        existing["summary"] = candidate["summary"]

    candidate_dt = candidate.get("published_dt")
    existing_dt = existing.get("published_dt")
    if candidate_dt and (existing_dt is None or candidate_dt > existing_dt):
        existing["published_dt"] = candidate_dt
        existing["title"] = candidate["title"] or existing["title"]
        existing["url"] = candidate["url"] or existing["url"]

    return existing


def public_item(item: dict, rank: int, score: float, reasons: list[str], detail_candidate: bool) -> dict:
    published_dt = item.get("published_dt")
    published = published_dt.isoformat().replace("+00:00", "Z") if published_dt else None
    return {
        "rank": rank,
        "score": score,
        "title": item["title"],
        "url": item["url"],
        "source_id": item["source_id"],
        "source_name": item["source_name"],
        "language": item["language"],
        "published": published,
        "summary": item["summary"],
        "reasons": reasons,
        "detail_candidate": detail_candidate,
    }


def scan_sources(
    sources: list[dict],
    fetcher=fetch_url,
    now: datetime | None = None,
    days: int = 3,
    top: int = 20,
    detail_candidates: int = 5,
    include_keywords: list[str] | None = None,
    exclude_keywords: list[str] | None = None,
) -> dict:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    include_keywords = normalize_keywords(include_keywords) or DEFAULT_KEYWORDS
    exclude_keywords = normalize_keywords(exclude_keywords)
    cutoff = now - timedelta(days=days)
    grouped: dict[str, dict] = {}
    errors: list[dict] = []
    sources_checked = len(sources)
    sources_succeeded = 0

    for source in sources:
        try:
            feed_xml = fetcher(source["url"])
            parsed_items = parse_feed(feed_xml, source)
            sources_succeeded += 1
        except Exception as exc:  # Keep one bad feed from killing the digest.
            errors.append({"source_id": source.get("id", ""), "source_name": source.get("name", ""), "error": str(exc)})
            continue

        for item in parsed_items:
            if not item["title"] and not item["url"]:
                continue
            published_dt = item.get("published_dt")
            if published_dt is not None and published_dt < cutoff:
                continue
            if should_exclude(item, exclude_keywords):
                continue
            key = item_key(item)
            if key in grouped:
                grouped[key] = merge_duplicate(grouped[key], item)
            else:
                grouped[key] = item

    scored_items = []
    for item in grouped.values():
        score, reasons = score_item(item, now, days, include_keywords)
        scored_items.append((score, item, reasons))
    scored_items.sort(key=lambda value: (value[0], value[1].get("published_dt") or datetime.min.replace(tzinfo=timezone.utc)), reverse=True)

    public_items = []
    for index, (score, item, reasons) in enumerate(scored_items[:top], start=1):
        public_items.append(public_item(item, index, score, reasons, index <= detail_candidates))

    return {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "window_days": days,
        "sources_checked": sources_checked,
        "sources_succeeded": sources_succeeded,
        "errors": errors,
        "items": public_items,
    }


def normalize_keywords(values: list[str] | None) -> list[str]:
    keywords: list[str] = []
    for value in values or []:
        for part in value.split(","):
            keyword = part.strip()
            if keyword:
                keywords.append(keyword)
    return keywords


def render_json(result: dict) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_markdown(result: dict) -> str:
    lines = [
        "# Tech News Feed Scan",
        "",
        f"- Generated: {result['generated_at']}",
        f"- Window: {result['window_days']} days",
        f"- Sources checked: {result['sources_checked']}",
    ]
    if result.get("errors"):
        lines.append(f"- Sources succeeded: {result['sources_succeeded']}")
        lines.append(f"- Feed errors: {len(result['errors'])}")
    lines.extend(["", "## Ranked Candidates", ""])

    if not result["items"]:
        lines.append("No matching items found.")
        return "\n".join(lines) + "\n"

    for item in result["items"]:
        marker = " [detail candidate]" if item["detail_candidate"] else ""
        published = item["published"] or "unknown date"
        reasons = ", ".join(item["reasons"])
        lines.extend(
            [
                f"{item['rank']}. [{item['title']}]({item['url']}){marker}",
                f"   - Score: {item['score']} | Source: {item['source_name']} | Language: {item['language']} | Published: {published}",
                f"   - Reasons: {reasons}",
            ]
        )
        if item["summary"]:
            lines.append(f"   - Summary: {item['summary']}")
    if result.get("errors"):
        lines.extend(["", "## Feed Errors", ""])
        for error in result["errors"]:
            lines.append(f"- {error['source_name'] or error['source_id']}: {error['error']}")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan RSS/Atom/RDF tech feeds and rank digest candidates.")
    parser.add_argument("--sources", type=Path, default=default_sources_path(), help="JSON source list path")
    parser.add_argument("--days", type=int, default=3, help="Lookback window in days")
    parser.add_argument("--top", type=int, default=20, help="Number of ranked items to return")
    parser.add_argument("--detail-candidates", type=int, default=5, help="Number of items to mark for deeper reading")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format")
    parser.add_argument("--include-keyword", action="append", default=[], help="Boost matching keyword; repeat or comma-separate")
    parser.add_argument("--exclude-keyword", action="append", default=[], help="Drop matching keyword; repeat or comma-separate")
    parser.add_argument("--timeout", type=int, default=12, help="Per-feed network timeout in seconds")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    sources = load_sources(args.sources)
    result = scan_sources(
        sources,
        fetcher=lambda url: fetch_url(url, timeout=args.timeout),
        days=args.days,
        top=args.top,
        detail_candidates=args.detail_candidates,
        include_keywords=args.include_keyword,
        exclude_keywords=args.exclude_keyword,
    )
    if args.format == "json":
        sys.stdout.write(render_json(result))
    else:
        sys.stdout.write(render_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
