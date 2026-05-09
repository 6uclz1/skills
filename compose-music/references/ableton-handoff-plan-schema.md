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
- `sample_assets`: unresolved user sample references copied from `composition_spec`.
- `audio_asset_plan`: direct cut-up source material copied from `tracks[*].source_material`.
- `track_plan`: ordered tracks, roles, search queries, and optional sound/shape intent.
- `clip_plan`: clip slots, lengths, note source, and timing metadata.
- `audio_clip_plan`: audio loop placement and warp/loop/gain intent for user-provided sample clips.
- `slice_plan`: fixed-grid or cut-up slicing intent for user-provided sliced audio.
- `cutup_trigger_plan`: trigger clip slot, length, note source, inline notes, and symbolic cut-up pattern.
- `cut_to_drum_rack_requests`: preserved intent equivalent to `$ableton-cli clip cut-to-drum-rack`.
- `execution_warnings`: warnings that must be resolved before modifying Ableton or exporting.
- `arrangement_sections`: sections copied from the source spec with density, active tracks, role layers, moves, and transition events.
- `handoff_notes`: short safety notes.
- `export_target`: expected render, save, or rough bounce target.

## Conversion Rules

- Validate `composition_spec` before conversion.
- Copy `brief.bpm` to `set_tempo` and `brief.meter` to `set_meter`.
- Convert each MIDI track into one `browser_searches` entry and one `track_plan` entry.
- Do not add `audio_loop` tracks to `browser_searches`; their source comes from `sample_assets`.
- Convert `audio_loop` tracks into `audio_clip_plan`.
- Convert legacy `sliced_audio` tracks into fixed-grid `slice_plan`; keep trigger notes in `clip_plan.note_source`.
- Convert cut-up `sliced_audio` tracks with `source_material` into `audio_asset_plan`, cut-up `slice_plan`, and `cutup_trigger_plan`.
- Preserve `handoff.cut_to_drum_rack_requests`.
- Preserve `sound_intent`, `shape_intent`, and `kick_relationship` when present.
- Convert `clip_length_bars` to `length_beats` using 4 beats per bar in `4/4`.
- Use inline note JSON when `tracks[*].notes` exists; otherwise use `notes_file` only when the file was actually created.
- Copy section arrangement fields exactly enough for the Ableton operator to create scenes or timeline regions.

## Safety Rules

- Browser searches stay broad and unresolved.
- Local sample paths stay behind `path_ref`, `root_env` plus `relative_path`, or a private manifest until `scripts/resolve_sample_assets.py` resolves them.
- Placeholder source material such as `<user-provided-audio-path>` must be replaced before `$ableton-cli audio transient analyze` or `clip cut-to-drum-rack`.
- Stop public or commercial export when any source material has `rights_status: unknown`.
- Exact paths or URIs are allowed only after an active browser search returns them.
- Stop before DAW execution if validation fails.
- Prefer plan-first or dry-run execution before modifying Live.
