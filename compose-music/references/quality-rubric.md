# Quality Rubric

Use this reference when evaluating a compose-music output or writing regression checks.

## Acceptance Checks

Rubric outputs used by CI/evals should conform to `evals/rubric-output.schema.json` and contain:

- `prompt_id`: evaluation prompt id.
- `score`: 0.0-1.0 pass ratio.
- `checks[]`: deterministic and rubric checks with `id`, `ok`, and `message`.
- `failures[]`: failed check ids.

- Narrow requests return only relevant sections.
- Full song sketches include Composition Brief, Pattern Grid, Harmony Map, Section Plan, Ableton Execution Notes, and Finish Checklist.
- Ableton-ready requests include `composition_spec` or an equivalent structured handoff.
- Browser targets are search queries or placeholders, not fake paths.
- MIDI note JSON validates with `scripts/validate_composition_spec.py` when included in `composition_spec`.
- Section lengths sum to the requested arrangement length.
- Harmony tasks include both roman numerals and concrete chords.
- Kick/bass relationship is explicitly described.
- Finish checklist includes concrete commit/export criteria.

## Common Failures

- Producing a full template for a one-part request.
- Giving an Ableton command catalog instead of a composition handoff.
- Naming exact browser paths or Drum Rack kits that were not discovered.
- Writing only vibes, adjectives, or mix advice without notes, rhythms, or section decisions.
- Forgetting density and transition events in arrangement plans.
- Letting bass sustain through every kick hit without stating that it is intentional.

## Evaluation Prompts

Keep representative prompts in `tests/compose-music/prompts.md` and expected checks in `tests/compose-music/expected-checks.md`.

Executable eval definitions live in:

- `evals/compose-music.prompts.csv`
- `evals/compose-music.checks.json`
- `evals/run-compose-music-evals.mjs`

Use `node evals/run-compose-music-evals.mjs --run-codex` when `codex exec --json` is available. The runner stores `*.trace.jsonl`, `*.final.txt`, `*.rubric.json`, and `summary.json` under `evals/artifacts/`.
