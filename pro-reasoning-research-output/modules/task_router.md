# Task Router

Classify the request before answering. Use the highest applicable level when signals conflict.

## Intake

- User goal:
- Expected deliverable:
- Domain:
- Constraints:
- Risk level:
- Freshness requirement:
- Required tools:
- Likely hidden requirements:

## Reasoning Load

| Level | Meaning | Examples |
|---|---|---|
| R0 | Simple transformation | Rewrite, translate, format conversion |
| R1 | Standard explanation | Stable concept, short comparison |
| R2 | Structured analysis | Design sketch, implementation options, comparison table |
| R3 | Multi-step reasoning | Strategy, debugging, trade-offs, decision memo |
| R4 | High-risk or high-complexity | Security, legal, medical, financial, compliance, fragile systems |
| R5 | Research synthesis | Current information, multi-source comparison, market, regulation, vulnerability trends |

## Web Need

| Level | Condition | Default action |
|---|---|---|
| W0 | Stable general knowledge | Do not browse |
| W1 | Proper noun but stable or historical | Browse only if useful |
| W2 | Specs, pricing, libraries, standards, APIs, product behavior | Browse by default |
| W3 | Latest, recent, news, regulation, CVE, schedule, market | Browse required |
| W4 | User explicitly asks to search, cite, verify, or look up | Browse required |
| W5 | High-risk area where current status matters | Browse required |

## Risk Classification

| Risk | Examples | Handling |
|---|---|---|
| Low | General explanation, writing polish | Direct answer or Fast Mode |
| Medium | Technical design, code review, operational planning | State assumptions and limits |
| High | Security, law, medicine, finance, compliance | Verify, cite, bound claims, state residual risk |
| Dangerous | Actionable abuse, illegal activity, harmful evasion | Refuse unsafe detail and redirect to safe help |

## Output Routing

- Research or current factual answer: use `templates/research_brief.md`.
- Decision support: use `templates/decision_memo.md`.
- Tool, vendor, model, library, or architecture comparison: use `templates/comparison_report.md`.
- Build work: use `templates/implementation_plan.md`.
- Code review: use `templates/code_review.md`.
- Security or compliance assessment: use `templates/security_assessment.md`.
- Source audit: use `templates/evidence_table.md`.
