---
name: compose-music
description: Create structured electronic music sketches and Ableton-ready composition specs with drum grids, chords, basslines, melodies, arrangements, MIDI note JSON, and loop-to-song handoff plans. Use for composition, arrangement, repair, and Ableton implementation planning; not for pure Ableton command lookup or mixing-only advice.
---

# Compose Music

## Scope

Use this skill as the composition layer above `$ableton-cli`: decide the music first, then hand deterministic Ableton operations to `$ableton-cli`.

Do not use this skill for pure Ableton command lookup, installation, transport control, browser inspection, or mixing-only advice. Use `$ableton-cli` directly for DAW operation and a mixing-focused skill or general answer for mix-only work.

## Output Modes

Choose the smallest output mode that satisfies the request:

- **Idea Mode**: for brainstorming, options, constraints, or high-level composition advice. Return only the directly useful ideas.
- **Pattern Mode**: for drum grids, basslines, chord loops, melody motifs, or MIDI JSON for a narrow musical unit. Return only the requested pattern material.
- **Song Sketch Mode**: for loop-to-song expansion, arrangement plans, and complete human-readable sketches that do not need Ableton execution. Return the relevant song sections.
- **Ableton Handoff Mode**: for "make this in Ableton", "implement", "generate clips", "MIDI JSON", or handoff requests. Return a concise human plan plus `composition_spec`.
- **Sample Handoff Mode**: for user-owned audio such as Amen-style break samples. Return `sample_assets`, `audio_loop` or `sliced_audio` tracks, and keep local paths out of browser fields.
- **Repair Mode**: for fixing an existing loop, arrangement, bassline, melody, or chord progression. Return diagnosis, edited material, and minimal execution notes.

Default assumptions when the user gives no constraints:
- Meter: `4/4`
- Tempo: `120 BPM`
- Tonality: `minor` or `dorian`
- Loop target: `8 bars`
- Arrangement target: `32` or `64 bars`
- Genre: choose one focused electronic direction and state it.
- Track count: 5 tracks: `Drums`, `Bass`, `Chords`, `Lead`, `Texture/FX`.

Assume defaults for missing tempo, key, meter, genre, length, and track count. Ask at most one clarifying question only when the missing constraint would materially change the result or create conflicting deliverables.

## Core Workflow

Follow this sequence for song sketches and Ableton handoffs:

1. **Brief**: lock genre, tempo, emotional intent, key/mode, track count, and one creative constraint.
2. **Beat**: create a 16-step or 2-bar drum grid before detailed sound design.
3. **Pitch Palette**: choose tonic, scale or mode, and allowed non-diatonic notes.
4. **Harmony**: choose a chord loop, roman numerals, voicing range, and harmonic rhythm.
5. **Bassline**: reinforce the harmony while relating to or contrasting with the drum pattern.
6. **Melody**: write a short identifiable motif, then create variations.
7. **Structure**: expand the loop into sections using 4, 8, or 16 bar blocks.
8. **Ableton Handoff**: specify tracks, clips, note grids, scene names, and arrangement durations.
9. **Finish**: apply subtraction, commitment, and completion prompts.

## Output Contract

For full song sketches, produce these sections:

- **Composition Brief**: genre, BPM, meter, key/mode, constraint, reference energy.
- **Pattern Grid**: drum grid, bass rhythm, melody motif, and bar lengths.
- **Harmony Map**: chords, roman numerals, voicings, harmonic rhythm, tension/release notes.
- **Section Plan**: Intro, Build, Break, Drop/Hook, Variation, Outro with bar counts and active parts.
- **Ableton Execution Notes**: track names, clip lengths, scene names, MIDI note JSON strategy, and `$ableton-cli` handoff notes.
- **Finish Checklist**: decisions to commit, parts to remove, renders or bounces to make, and completion criteria.

For Ableton Handoff Mode, always include:

- A concise human-readable plan.
- A fenced JSON block named `composition_spec`.
- A validation checklist.
- No hard-coded browser paths, rack names, device presets, local file paths, or fake URIs.
- User samples referenced through `sample_assets`, never through `browser_query`.

Read `references/output-contracts.md` and `references/composition-spec-schema.md`; validate against `references/composition_spec.schema.json` before producing the final handoff.

For narrow requests, return only the relevant sections; do not emit the full song-sketch template.

## Validation Rules

Before finalizing Ableton-ready material, verify:

- Section bar counts sum to the requested length.
- MIDI notes use valid `pitch`, `start_time`, `duration`, `velocity`, and `mute` fields.
- Bass and kick are designed as one composite low-end part.
- Browser targets are search queries or placeholders, not hard-coded paths, rack names, device presets, local file paths, or fake URIs.
- User-owned samples use `sample_assets` with `path_ref`, `root_env` plus `relative_path`, or a private manifest. Do not emit `/Users/...`, `file://...`, or sample filenames in `browser_query` or `handoff.browser_queries`.
- Audio-backed tracks set `source_type` to `audio_loop` or `sliced_audio`, use `sample_ref`, and include `audio_clip` or fixed-grid `slice_plan` as appropriate.
- `composition_spec.handoff.browser_queries` repeats the browser search intent and remains path-free.
- Section plans include density, foreground/midground/background roles, add/mute moves, and transition events when arranging a complete song.
- Narrow requests do not return unrelated full-contract sections.
- Complete arrangements use the section fields from `references/arrangement-energy-curves.md`: `foreground`, `midground`, `background`, `identity_carrier`, `move`, and `transition_event`.
- Melody motifs name `rhythm_cell`, `pitch_cell`, and `variation_strategy` when the user asks for melodic material.
- Harmony maps name tension and release points with `tension_bar`, `resolution_bar`, and any `outside_notes` when those choices are present.
- Basslines state `kick_relationship` as `avoid`, `double`, `answer`, or `intentional_overlap`.
- Track sound choices describe `sound_intent` and `shape_intent`; `browser_query` remains a broad search phrase only.

Use bundled scripts when deterministic conversion or validation is useful:

- `scripts/grid_to_notes.py`: 16-step or 32-step drum grid to Ableton note JSON; each row may use `steps` or the equivalent `grid` alias. Use `--payload` when swing, shuffle, humanization, or polymeter metadata must survive handoff.
- `scripts/breakbeat_pattern_to_notes.py`: fixed-grid Amen/breakbeat slice index patterns to Ableton trigger note JSON.
- `scripts/chords_to_notes.py`: tonic, mode, roman numerals, explicit chord quality, borrowed chords, inversions, slash chords, and extensions to chord note JSON.
- `scripts/validate_composition_spec.py`: validate Ableton-ready `composition_spec`.
- `scripts/resolve_sample_assets.py`: resolve private sample asset manifests or environment variable references outside generated specs.
- `scripts/composition_spec_to_handoff_plan.py`: convert a valid `composition_spec` into `ableton_handoff_plan` JSON for `$ableton-cli` workflows.

## Reference Selection

- Read `references/learning-music-system.md` when starting from scratch, teaching the user, or structuring the work from rhythm through song form.
- Read `references/music-theory-toolkit.md` when choosing keys, scales, modes, chords, voicings, seventh chords, or harmonic functions.
- Read `references/creative-strategies.md` when the user is blocked, over-editing, stuck in loops, or needs a finish plan.
- Read `references/pattern-recipes.md` when generating concrete drum, harmony, bass, or melody patterns.
- Read `references/ableton-composition-bridge.md` when the output should be executable or easily translated with `$ableton-cli`.
- Read `references/output-contracts.md` when the user asks for Ableton-ready implementation, MIDI JSON, or structured handoff.
- Read `references/composition-spec-schema.md` when building or checking `composition_spec` fields and validation rules.
- Read `references/ableton-handoff-plan-schema.md` when converting `composition_spec` into an intermediate `ableton_handoff_plan`.
- Read `references/eval-cases.md` when running regression-style prompt checks.
- Read `references/genre-playbooks.md` when selecting genre defaults or making genre-specific decisions.
- Read `references/arrangement-energy-curves.md` when expanding loops into 32-, 64-, 96-, or 128-bar forms.
- Read `references/sound-design-intent.md` when choosing role-based sound targets without naming fixed presets.
- Read `references/quality-rubric.md` when evaluating a draft or running regression-style checks.

## Ableton Handoff

Do not duplicate the `$ableton-cli` command catalog. Hand off intent and structured data:

- Preflight intent: wait-ready, doctor if needed, then tracks list.
- Browser search intent by role, for example `Drum Rack`, `Kit`, `Operator bass`, `Drift bass`, `Wavetable pad`, `Analog keys`; resolve exact paths or URIs only from active `$ableton-cli` search results.
- Track plan: default order `0 Drums`, `1 Bass`, `2 Chords`, `3 Lead`, `4 Texture/FX`.
- Clip plan: scene clips with lengths in bars and beats.
- Audio clip plan: user sample audio placement, warp, loop, gain, and source asset id.
- Slice plan: fixed-grid slicing, Drum Rack trigger pad range, and trigger note source.
- Notes: inline note JSON or a path to a generated notes file.
- Arrangement: scene names, start bars, durations, density, active tracks.
- Safety: prefer dry-run or plan-first execution, inspect JSON command results, and stop on non-zero `$ableton-cli` exit codes.
- Finish: save/export target if requested.

When the user asks to implement a sketch, produce or use `ableton_handoff_plan` as the intermediate artifact before any DAW operation.

Always avoid hard-coding browser item paths, Drum Rack kits, or device targets. Ask `$ableton-cli` workflows to search the active Ableton browser catalog first, then use returned paths or URIs.

For requests like "make a 170 BPM jungle Amen break using my local sample", do not generate or bundle the Amen audio. Reference the user's sample with `sample_assets`, choose `audio_loop` for warp/loop placement or `sliced_audio` for fixed-grid Drum Rack slicing, and prefer plan/dry-run Ableton execution before modifying Live.

## Composition Rules

- Separate generation from editing: create several options before judging them.
- Prefer simple, playable material before advanced theory.
- Keep kick and bass clear by treating the low end as one composite part.
- Use foreground, middle ground, and background roles while composing, not only while mixing.
- Build the maximal-density section first when arrangement is unclear.
- Finish imperfect sketches instead of abandoning them.
