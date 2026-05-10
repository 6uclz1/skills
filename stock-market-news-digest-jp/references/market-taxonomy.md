# Market Taxonomy

Use this reference when a digest needs broad coverage, explicit scoring, or careful handling of crowd-driven stock stories.

## Japan Market Categories

- Nikkei 225
- TOPIX
- Growth Market
- FX
- rates
- Bank of Japan
- sector indexes
- futures
- SQ
- overseas investor flow

## Individual Stock Catalysts

- earnings
- guidance revisions
- dividend increases
- dividend cuts
- buybacks
- shareholder benefits
- M&A
- major shareholders
- ratings
- price targets
- capital increases
- secondary offerings
- public offerings
- stock splits
- delistings
- scandals
- regulation
- litigation
- new products
- supply-demand deterioration
- short selling
- PTS catalysts

## Themes

- semiconductors
- AI
- defense
- games
- banks
- trading companies
- inbound tourism
- yen weakness beneficiaries
- yen strength beneficiaries
- crude oil
- electric power
- data centers
- generative AI
- parent-subsidiary listing unwind
- activists
- Tokyo Stock Exchange reforms

## US Market Spillover Categories

- S&P 500
- Nasdaq
- Dow
- US 10-year yield
- FOMC
- CPI
- PCE
- payrolls
- Nvidia
- Apple
- Microsoft
- Alphabet
- Amazon
- Meta
- Tesla
- AMD
- Broadcom

## Importance Score

Use the score as a ranking aid, not as a precise model:

- `source_count`: 20%
- `source_quality`: 20%
- `price_move`: 20%
- `volume_move`: 10%
- `crowd_trend`: 15%
- `japan_market_relevance`: 10%
- `us_market_spillover`: 5%

Interpretation:

- `80-100`: top news
- `60-79`: important stock or theme item
- `40-59`: notable short-term item or supporting context
- `0-39`: normally omit

## Crowd Trend Signals

Use crowd trend evidence only as market attention:

- Media popularity: Minkabu popular news, Kabutan hot stocks, Kabushiki Shimbun breaking or PTS items.
- Social popularity: X/Twitter topic volume, sentiment, and representative arguments from the existing X/Twitter skill.
- Market reaction: same-day, 3-trading-day, and 5-trading-day returns; volume surge; trading value surge; PTS move; margin balance; short-selling discussion.
- Theme spread: repeated keywords across media, multiple stocks reacting to the same theme, or US and Japanese stocks moving on linked themes.

## High-Attention Stock Handling

For a stock such as Nintendo (`7974`) becoming widely discussed after a price decline, separate:

- Factual layer: when and how much the stock moved, whether volume increased, and whether there is a primary catalyst such as earnings, guidance, product news, FX, rating changes, or disclosure.
- Media layer: what Kabutan, Minkabu, Kabushiki Shimbun, Reuters, Bloomberg, and other sources say; whether multiple sources repeat the same explanation.
- Crowd layer: what X/Twitter users emphasize, such as pessimism, dip buying, product expectations, earnings concerns, FX effects, crowded positioning, or "sell the news" explanations.
- Risk layer: whether social explanations are primary-source based, whether explanations are post-hoc, and whether short-term supply-demand is being confused with long-term fundamentals.

Example summary:

```markdown
### 7974 Nintendo
- Overview: The share-price decline became a major topic among individual investors.
- Main arguments: Earnings outlook, product expectations, sell-the-news reaction, FX impact, and supply-demand deterioration.
- Media check: Related coverage was checked across Japanese equity media and global market sources where accessible.
- Primary sources: Earnings releases, company announcements, and TDnet were checked.
- Crowd reaction: X/Twitter showed multiple interpretations, including pessimism, dip-buying interest, and expectation reset.
- Caveat: Do not state social explanations as the reason for the price decline unless primary facts support them.
```
