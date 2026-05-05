# Composition Spec Schema

Use this reference when Ableton implementation, MIDI JSON, generated clips, or a deterministic handoff is requested. The machine schema lives in `composition_spec.schema.json`; this file explains the contract in compact terms.

## Top-Level Object

Required fields:

- `version`: string, currently `1.0`.
- `brief`: composition constraints and musical defaults.
- `sample_assets`: optional user-provided audio references, kept separate from browser search fields.
- `tracks`: ordered track plans and MIDI note material.
- `sections`: arrangement sections.
- `handoff`: Ableton implementation intent.
- `finish_criteria`: completion checks.

## brief

Required fields:

- `genre`: focused genre or hybrid.
- `bpm`: positive number.
- `meter`: currently `4/4`.
- `key`: tonic such as `D`, `F#`, or `Bb`.
- `mode`: scale or mode such as `minor`, `dorian`, `phrygian`, `mixolydian`, or `pentatonic`.
- `length_bars`: positive integer.
- `creative_constraint`: one concrete limitation that gives the sketch identity.

## tracks

Each track requires:

- `name`: unique track label.
- `role`: musical job, such as `rhythm`, `low-end identity`, `harmony`, `foreground motif`, or `texture`.
- `clip_length_bars`: positive number.
- `browser_query`: search query or placeholder, never a local path, preset path, or fake URI.
- `notes`: Ableton note JSON array.

`source_type` defaults to `midi`. Use `audio_loop` for a user sample placed as an audio clip, and `sliced_audio` for a user sample sliced to Drum Rack pads and triggered by MIDI notes.

Each note requires:

- `pitch`: MIDI integer `0..127`.
- `start_time`: beat position, `>= 0`.
- `duration`: positive beat length.
- `velocity`: integer `1..127`.
- `mute`: boolean.

Optional track fields:

- `source_type`: one of `midi`, `audio_loop`, or `sliced_audio`.
- `sample_ref`: `sample_assets[*].id` for audio-backed tracks.
- `audio_clip`: audio loop settings such as `warp`, `warp_mode`, `loop`, `gain_db`, and `transpose_semitones`.
- `slice_plan`: fixed-grid slicing settings: `mode: fixed_grid`, `slice_count`, `start_pad`, and optional `create_trigger_clip`.
- `drum_rows`: named step grids used as source material.
- `timing_feel`, `swing_amount`, `shuffle_amount`, `humanization`, `polymeter_reset_bar`: timing metadata that should survive handoff.
- `sound_intent`: the musical behavior the sound must serve, such as `short mono bass with clear gaps after kick hits`.
- `shape_intent`: envelope, filter, width, transient, or modulation direction to carry into Ableton execution notes.
- `kick_relationship`: one of `avoid`, `double`, `answer`, or `intentional_overlap` for bass and low percussion parts.
- `notes_file`: generated note JSON path, only when the file is local to the current workspace and has actually been created.

## sample_assets

Use `sample_assets` for user-owned samples such as an Amen-style break. Do not put local sample paths in `browser_query` or `handoff.browser_queries`.

Recommended locator priority:

- `path_ref`: environment variable containing the absolute sample path, for example `AMEN_BREAK_WAV`.
- `root_env` plus `relative_path`: sample root environment variable plus a repository-free relative path.
- user-level manifest: resolve `id` through a private manifest such as `~/.config/compose-music/sample_assets.json`.

Common fields:

- `id`: stable asset id used by `tracks[*].sample_ref`.
- `source`: usually `user_sample_library`.
- `path_ref`: environment variable name, not the path itself.
- `root_env` and `relative_path`: path components resolved only by `scripts/resolve_sample_assets.py`.
- `original_bpm`: source tempo used for warp planning.
- `bars`: source loop length in bars.
- `trim`: alignment note such as `downbeat_aligned`.
- `rights_status`: for example `user_provided`.

## sections

Each section requires:

- `name`: scene or arrangement label.
- `start_bar`: 1-based start bar.
- `length_bars`: positive integer.
- `density`: integer `0..5`.
- `active_tracks`: list of existing track names.

Recommended for complete arrangements:

- `foreground`, `midground`, `background`: lists of existing track names.
- `identity_carrier`: existing track name carrying the section identity.
- `move`: add, mute, subtract, vary, filter, or commit action.
- `transition_event`: fill, riser, silence, pickup, crash, or automation event.

## handoff

Required fields:

- `requires_browser_search`: boolean; usually `true`.
- `browser_queries`: deduplicated Ableton browser search intent, usually copied from track `browser_query` values.
- `export_target`: expected save, render, or rough bounce target.

`browser_query` and `handoff.browser_queries` are search intent only. They must not contain hard-coded browser paths, local file paths, rack names presented as resolved items, or fake URIs.

## Validation Rules

- `sections[*].length_bars` must sum to `brief.length_bars`.
- `tracks[*].name` must be unique.
- `sections[*].active_tracks`, `foreground`, `midground`, `background`, and `identity_carrier` must reference existing track names.
- `notes[*].start_time + duration` must be less than or equal to the clip length in beats.
- `pitch` must be MIDI range `0..127`.
- `velocity` must be `1..127`.
- `browser_query` and `handoff.browser_queries` must be search queries or placeholders, not local paths, fake URIs, or fixed browser results.
- `tracks[*].sample_ref` must reference an existing `sample_assets[*].id`.
- `audio_loop` tracks may include `audio_clip`; `sliced_audio` tracks require a valid fixed-grid `slice_plan`.
- `finish_criteria` must contain at least one concrete completion check.

Run `scripts/validate_composition_spec.py` before using a spec for Ableton operations.
