# Web Research Protocol

## Freshness Triggers

Always research when the answer depends on:

- Current product behavior
- Model availability
- APIs
- Security advisories
- CVEs
- Laws and regulations
- Prices
- Schedules
- Market conditions
- Recent news
- Software versions
- Standards under active revision
- Vendor claims
- Public figures or organizations whose status may change

## Avoid Browsing

Avoid web research when:

- The user asks for rewriting, translation, summarization of provided text, or creative writing.
- The task is pure reasoning based only on user-provided premises.
- The user explicitly asks not to browse.
- Current facts are irrelevant to the answer.

Browse anyway when high-risk or freshness requirements override these defaults.

## Pre-Search Reasoning

Before searching, identify:

- What must be established.
- Which information is likely to change.
- Where the primary source should exist.
- Which claims need citations.
- Which facts most affect the user's decision.

## Query Design

Use at least these query classes when the answer is important:

| Query type | Purpose | Example |
|---|---|---|
| Primary query | Find official information | `OpenAI ChatGPT Skills official SKILL.md` |
| Freshness query | Find recent updates | `2026 ChatGPT Skills update` |
| Contradiction query | Find limits or conflicts | `ChatGPT Skills limitations official` |

For technical domains, add targeted searches as relevant:

| Query | Use |
|---|---|
| `site:docs.vendor.com` | Official documentation |
| `site:github.com release notes` | Implementation and releases |
| `site:nvd.nist.gov CVE` | Vulnerabilities |
| `site:ietf.org RFC` | Standards |
| `site:owasp.org` | Security best practices |

## Source Priority

1. Official documentation
2. Standards bodies
3. Government or regulator sources
4. Vendor release notes or security advisories
5. Peer-reviewed papers or preprints, with caution
6. Reputable technical media
7. High-signal community sources
8. Low-trust SEO summaries

## Research Depth

| Depth | Use | Typical evidence |
|---|---|---|
| Light | Quick current confirmation | 1 to 2 sources |
| Standard | Practical answer | 3 to 5 sources |
| Deep | Comparison, decision, research report | 5 to 10 sources |
| Adversarial | Security, regulation, major decisions | Official sources plus contradiction checks |

## Post-Search Process

1. Compare timestamps and version context.
2. Prefer newer official information when credible sources conflict.
3. Capture uncertainty when sources disagree.
4. Map each important claim to a source.
5. Cite claims directly in the final answer.
