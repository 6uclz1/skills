# Changelog

## v0.3.0 - 2026-05-03

### Added

- Added `compose-music/README.md`, examples, `VERSION`, and a GitHub Actions workflow for unit tests and eval dry-runs.
- Added `ableton_handoff_plan` documentation and schema as the formal intermediate handoff artifact.
- Expanded compose-music eval prompts from 10 to 25 and set the runner merge threshold to `score >= 0.9`.

### Changed

- Standardized output mode names to Idea Mode, Pattern Mode, Song Sketch Mode, Ableton Handoff Mode, and Repair Mode.
- Tightened `grid_to_notes.py` so `steps` and `grid` aliases must match when both are present.
- Extended `composition_spec` with optional `genre_traits`, `sound_intent`, `shape_intent`, and `kick_relationship` fields.
- Strengthened references for genre constraints, arrangement fields, melody motifs, harmony maps, and sound-design intent.

## v0.2.0 - 2026-05-03

### Added

- Added `compose-music` to the release scope with implementation-oriented references, scripts, tests, and eval definitions.
- Added `references/composition_spec.schema.json` as the schema contract for `composition_spec` v1.
- Added `evals/run-compose-music-evals.mjs`, prompt/check definitions, and rubric output schema for regression-style scoring.
- Added `scripts/composition_spec_to_handoff_plan.py` to convert a validated `composition_spec` into an Ableton handoff plan.
- Expanded `genre-playbooks.md` to 20 genres with tempo, drum identity, bass relation, harmony density, arrangement behavior, and avoid lists.

### Changed

- Shortened the `compose-music` description for clearer implicit invocation.
- Extended `grid_to_notes.py` with payload output for swing, shuffle, humanization, and polymeter metadata.
- Extended `chords_to_notes.py` with explicit chord qualities, borrowed chords, inversions, slash chords, and extensions.
- Strengthened `validate_composition_spec.py` checks for timing metadata, role track references, identity carriers, and version alignment.

### Notes

- `compose-music` remains a composition and handoff skill. It does not replace `$ableton-cli` for deterministic Ableton Live operations.
- Browser targets remain search queries or placeholders until discovered through the active Ableton browser catalog.
