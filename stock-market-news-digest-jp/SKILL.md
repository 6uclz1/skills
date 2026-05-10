---
name: stock-market-news-digest-jp
description: Create Japanese equity-centered stock market news digests from current news, timely disclosures, company IR, market data, US market spillover context, and crowd trends. Use when Codex should summarize Japan stock market news, individual Japanese stock catalysts, earnings or TDnet disclosures, market themes, Nikkei/TOPIX context, S&P 500/Nasdaq/Dow or major US equity spillovers, or X/Twitter-driven crowd reaction while avoiding investment recommendations.
---

# Stock Market News Digest JP

## Operating Principles

- Treat this as news organization and market context, not investment advice.
- Prioritize Japanese equities. Include US markets only when they can affect Japanese equities through indexes, rates, FX, semiconductors, AI, large tech, or risk sentiment.
- Always separate four layers: primary facts, media interpretation, crowd reaction, and unverified information.
- Reduce reader cognitive load. Prefer summary tables, compact matrices, and one Mermaid diagram for complex relationships instead of long prose or flat bullet lists.
- Use current browsing or available live data for market news. Market facts, prices, schedules, and disclosures are time-sensitive.
- Cite sources used. Do not bypass paywalls or reproduce restricted articles.
- Do not make buy/sell recommendations, price targets, or certainty claims about causal links.

## Inputs To Resolve

Infer missing inputs conservatively:

- `date_range`: default `last_24h`; also accept `today`, `last_3d`, `last_7d`, or explicit dates.
- `market_scope`: default `japan_equities`, `sp500`, `major_us_equities`.
- `tickers`: Japanese codes such as `7974`, `7203`, `9984`; US tickers such as `NVDA`, `AAPL`.
- `watch_keywords`: company names, themes, macro terms, or Japanese phrases such as `半導体`, `AI`, `日銀`, `円安`, `S&P500`.
- `output_depth`: `brief`, `standard`, or `deep`; default `standard`.
- `include_crowd_trend`: default true.
- `include_us_market_context`: default true.

## Workflow

1. Resolve scope.
   - Normalize Japanese stock codes, company names, abbreviations, English names, US tickers, and theme keywords.
   - Expand obvious related terms, but keep the final digest focused on the user request.

2. Collect Japanese market and equity news.
   - Check Japan market context: Nikkei 225, TOPIX, Growth Market, sectors, futures, FX, rates, Bank of Japan, SQ, and overseas investor flow when relevant.
   - Use Japanese equity media for market stories, hot stocks, earnings flashes, PTS materials, and individual stock catalysts.
   - Verify important catalysts through TDnet, JPX, company IR, filings, earnings releases, or official press releases whenever possible.

3. Collect US spillover context when enabled.
   - Check S&P 500, Nasdaq, Dow, US 10-year yield, USD/JPY, FOMC, CPI, PCE, payrolls, and major US equities.
   - Prioritize Nvidia, Apple, Microsoft, Alphabet, Amazon, Meta, Tesla, AMD, Broadcom, semiconductors, AI, and large tech when they map to Japanese themes.

4. Collect crowd trends when enabled.
   - Use the existing X/Twitter research skill rather than implementing X/Twitter scraping here.
   - Pass tickers, company names, resolved keywords, hashtags, and theme terms.
   - Treat returned X/Twitter material as market participant reaction, not as fact.

5. Cluster and deduplicate.
   - Merge duplicate articles about the same catalyst.
   - Keep primary source, media reporting, and social reaction as separate evidence types inside each cluster.

6. Rank importance.
   - Score higher for primary-source confirmation, multiple credible sources, large price/volume reaction, high crowd attention, Japan market relevance, and US-to-Japan spillover.
   - Prefer earnings, guidance revisions, dividends, buybacks, M&A, equity offerings, splits, delistings, scandals, regulation, litigation, and PTS-moving materials.

7. Generate the digest.
   - Lead with conclusions and the few most actionable news clusters.
   - Put the executive summary in a table before detailed commentary.
   - Use tables for index moves, individual stock catalysts, US spillover factors, and unverified items.
   - Use Mermaid when it helps explain information flow, such as `US tech -> Japan semiconductors -> individual stocks`, or `primary disclosure -> media interpretation -> crowd reaction`.
   - Include caveats where causality is uncertain or social claims are unverified.
   - Keep output compact for `brief`, full but scannable for `standard`, and source-rich with more evidence for `deep`.

## Source Priority

Use this priority when evidence conflicts:

1. Primary sources: TDnet, JPX, company IR, earnings releases, securities reports, official press releases.
2. Global market news: Reuters, Bloomberg, exchange or index pages available without bypassing access controls.
3. Japan equity media: Kabutan, Minkabu, Kabushiki Shimbun, and similar market news services.
4. Crowd signals: X/Twitter research output, popular-news rankings, page-view rankings, and social trend summaries.

Never use tier 4 sources to establish factual claims.

## Output Shape

Use the template in [references/report-template.md](references/report-template.md) for standard and deep reports. For brief reports, condense to:

- Conclusion table
- Market snapshot table
- Top Japanese market themes table
- Top individual stocks table
- US spillover table
- Crowd trend and unverified information table
- Sources checked

Read [references/market-taxonomy.md](references/market-taxonomy.md) when the task needs detailed category coverage, scoring, or example handling such as a high-attention Nintendo move.

## Cognitive Load Rules

- Start with a 3-5 row conclusion table. Each row should answer "what happened", "why it matters", and "confidence/caveat".
- Prefer one screen of dense but readable tables over long paragraphs. Use prose only to explain nuance that does not fit a table.
- Use these table columns by default:
  - Market snapshot: `Asset/Index`, `Move`, `Driver or interpretation`, `Japan equity implication`, `Source`.
  - Individual stocks: `Ticker`, `Company`, `Catalyst`, `Price/volume reaction`, `Evidence layer`, `Caveat`, `Importance`.
  - Themes: `Theme`, `Related stocks`, `Primary facts`, `Media interpretation`, `Crowd reaction`, `Durability`.
  - Unverified items: `Claim`, `Where it appeared`, `Primary-source status`, `How to treat it`.
- Use a Mermaid flowchart when there are three or more linked drivers or when US-to-Japan spillover is central. Keep diagrams small: 5-9 nodes, no decorative styling, labels short.
- Keep each table cell concise. If a cell needs more than two short clauses, move the detail below the table.
- Mark evidence layers visibly with labels such as `primary`, `media`, `crowd`, and `unverified`.
- Avoid repeating the same source link in every row when a grouped source list is clearer.

## X/Twitter Adapter

Call an existing X/Twitter skill when crowd trends are requested. Prefer `$x-twitter-research` if it is available in the current environment.

Pass:

- `date_range`
- `tickers`
- company names and aliases
- `watch_keywords`
- resolved theme keywords and hashtags
- market context: `japan_equities_and_us_major_stocks`

Request:

- topic volume
- representative post summary
- sentiment summary
- trending keywords
- rumor or unverified flags

Integrate the result only as crowd reaction.
