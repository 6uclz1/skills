# Ableton Handoff Plan Schema

Use `ableton_handoff_plan` as the deterministic intermediate artifact between `composition_spec` and `$ableton-cli` workflows. The machine schema lives in `ableton_handoff_plan.schema.json`.

The plan must describe intent and structured data only. It must not duplicate the `$ableton-cli` command catalog and must not invent browser paths, URIs, rack names, or preset names.

## Required Top-Level Fields

- `version`: string, currently `1.0`.
- `source`: usually `compose-music composition_spec`.
- `preflight_intent`: readiness intents such as `wait-ready`, `doctor-if-needed`, and `tracks-list`.
- `set_tempo`: BPM number copied from the source brief.
- `set_meter`: meter string, currently `4/4`.
- `browser_searches`: role-based search queries to resolve against the active Ableton browser.
- `track_plan`: ordered tracks, roles, search queries, and optional sound/shape intent.
- `clip_plan`: clip slots, lengths, note source, and timing metadata.
- `arrangement_sections`: sections copied from the source spec with density, active tracks, role layers, moves, and transition events.
- `handoff_notes`: short safety notes.
- `export_target`: expected render, save, or rough bounce target.

## Conversion Rules

- Validate `composition_spec` before conversion.
- Copy `brief.bpm` to `set_tempo` and `brief.meter` to `set_meter`.
- Convert each track into one `browser_searches` entry and one `track_plan` entry.
- Preserve `sound_intent`, `shape_intent`, and `kick_relationship` when present.
- Convert `clip_length_bars` to `length_beats` using 4 beats per bar in `4/4`.
- Use inline note JSON when `tracks[*].notes` exists; otherwise use `notes_file` only when the file was actually created.
- Copy section arrangement fields exactly enough for the Ableton operator to create scenes or timeline regions.

## Safety Rules

- Browser searches stay broad and unresolved.
- Exact paths or URIs are allowed only after an active browser search returns them.
- Stop before DAW execution if validation fails.
- Prefer plan-first or dry-run execution before modifying Live.
