# Reasoning Eval Prompts

## Database Decision

Prompt:

> For an early-stage startup, should we use PostgreSQL, DynamoDB, or Firestore? Include decision criteria.

Expected behavior:

- Set assumptions.
- Compare options.
- Give conditional recommendation.
- Browse if current pricing, limits, or managed-service behavior matters.
- Separate facts from recommendations.

## Architecture Trade-Off

Prompt:

> Should this team move from a monolith to microservices this quarter?

Expected behavior:

- Ask or state assumptions about scale, team boundaries, deployment pain, and observability.
- Avoid defaulting to microservices.
- Provide revisit conditions.
