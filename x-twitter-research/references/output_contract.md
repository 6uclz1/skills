# Output Contract

Use this contract when returning a structured X/Twitter research report or handing extracted evidence to another task.

## Report Sections

- **Query/source**: The keyword, hashtag, profile, direct tweet URL, or linked article URL checked.
- **Key findings**: A short list of findings grounded in visible tweets or linked articles.
- **Notable posts**: The most relevant visible posts and why each matters.
- **Context/interpretation**: A careful explanation of what the visible discussion suggests.
- **Linked article summary**: Summaries of opened article links, separated from tweet claims.
- **Caveats**: Access, ranking, recency, deleted/protected content, and uncertainty notes.
- **Next search suggestions**: Optional focused searches for follow-up.

## Structured Fields

Use these fields when JSON-like output is helpful:

```text
query_or_url: string
retrieved_at: ISO-8601 timestamp or explicit local time
search_mode: "keyword" | "hashtag" | "top" | "latest" | "direct_tweet_url" | "profile_scoped" | "linked_article"
result_scope: short description of tabs, result modes, and limits checked
key_findings: string[]
notable_posts: NotablePost[]
linked_articles: LinkedArticle[]
caveats: string[]
next_search_suggestions: string[]
```

## Notable Post Fields

```text
author_display_name: string | null
author_handle: string | null
tweet_url: string | null
timestamp: string | null
post_summary: string
quoted_or_reposted_context: string | null
media_or_link_context: string | null
engagement_signals: string | null
relevance_reason: string
uncertainty: string | null
```

## Linked Article Fields

```text
article_url: string
source_name: string | null
title: string | null
summary: string
relationship_to_tweet: string
access_notes: string | null
uncertainty: string | null
```

## Caveats

Always include caveats when any of these apply:

- X/Twitter ranking mode was Top, For you, or otherwise algorithmic.
- Results were limited to visible posts and a small amount of scrolling.
- Posts were deleted, protected, blocked, translated, truncated, or hidden behind login/rate limits.
- Engagement numbers were absent, rounded, stale, or changed during browsing.
- Linked articles were paywalled, blocked, partially loaded, or summarized from visible snippets only.
