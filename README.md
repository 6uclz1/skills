# Codex Skills

Repository-scoped Codex skills maintained by `6uclz1`.

## Skills

- `compose-music`: compose Ableton-ready electronic music sketches, MIDI grids, arrangements, `composition_spec` handoffs, evals, and helper scripts.
- `tech-news-digest`: scan English and Japanese developer community feeds and produce concise technology digests.

Each skill has its own README or `SKILL.md` for detailed usage. `compose-music/README.md` is the entry point for composition specs, helper scripts, examples, and evals.

## Installing A Skill

Use a direct folder install from this repository checkout:

```bash
codex skills install ./compose-music
```

For local development, keep this repository checked out and point Codex at the skill folder. Each skill keeps operational instructions in `SKILL.md`, optional references in `references/`, deterministic helpers in `scripts/`, and tests in `tests/`.

## compose-music Sample Prompts

- `Use $compose-music to create an 8-bar dark techno loop in D dorian, Ableton-ready.`
- `Use $compose-music to turn this 16-step kick/snare/hat grid into MIDI note JSON.`
- `Use $compose-music to expand this 4-bar loop into a 64-bar arrangement.`
- `Use $compose-music to implement this sketch via an Ableton handoff plan.`
- `Use $compose-music to diagnose why my kick and bass feel crowded.`

## compose-music Validation

Run the core script tests:

```bash
python3 -m unittest compose-music/tests/test_composition_scripts.py
```

Run the executable eval harness in dry-run mode:

```bash
node evals/run-compose-music-evals.mjs --dry-run
```

The dry-run checks the 25-prompt rubric configuration and uses `score >= 0.9` as the merge threshold for saved or Codex-generated answers.

When `codex exec --json` is available, capture traces and rubric output:

```bash
node evals/run-compose-music-evals.mjs --run-codex
```

## Known Limitations

- `compose-music` validates `composition_spec` for 4/4 material only.
- The eval runner can grade saved final outputs without Codex, but full trace capture requires `codex exec --json`.
- Ableton browser targets are intentionally role-based search queries until `$ableton-cli` discovers real paths or URIs in the active Live catalog.
- `composition_spec_to_handoff_plan.py` creates an intermediate plan; it does not operate on Ableton Live directly.
