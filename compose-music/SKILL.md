---
name: compose-music
description: Compose, arrange, and prepare Ableton-ready electronic music sketches with drum grids, pitch palettes, chord progressions, basslines, melodies, section plans, MIDI note specs, and finish checklists. Use for song sketches, loop-to-song expansion, MIDI composition plans, and composition handoff to ableton-cli. Do not use for pure Ableton command lookup, installation, or mixing-only tasks.
---

# Compose Music

## Scope

Use this skill as the composition layer above `$ableton-cli`: decide the music first, then hand deterministic Ableton operations to `$ableton-cli`.

Do not use this skill for pure Ableton command lookup, installation, transport control, browser inspection, or mixing-only advice. Use `$ableton-cli` directly for DAW operation and a mixing-focused skill or general answer for mix-only work.

## Mode Selection

Choose the smallest output mode that satisfies the request:

- **Idea mode**: brief, palette, and 2-3 directions.
- **Pattern mode**: drum, bass, chord, or melody grid only.
- **Song sketch mode**: full human-readable output contract.
- **Ableton handoff mode**: full output plus `composition_spec`.
- **Repair mode**: diagnose an existing loop and propose edits.

Default assumptions when the user gives no constraints:
- Meter: `4/4`
- Tempo: `120 BPM`
- Tonality: `minor` or `dorian`
- Loop target: `8 bars`
- Arrangement target: `32` or `64 bars`
- Genre: choose one focused electronic direction and state it.
- Track count: 5 tracks: `Drums`, `Bass`, `Chords`, `Lead`, `Texture/FX`.

Ask at most one clarifying question only when the missing constraint would materially change the result.

## Core Workflow

Follow this sequence for song sketches and Ableton handoffs:

1. **Brief**: lock genre, tempo, emotional intent, key/mode, track count, and one creative constraint.
2. **Beat**: create a 16-step or 2-bar drum grid before detailed sound design.
3. **Pitch Palette**: choose tonic, scale or mode, and allowed non-diatonic notes.
4. **Harmony**: choose a chord loop, roman numerals, voicing range, and harmonic rhythm.
5. **Bassline**: reinforce the harmony while relating to or contrasting with the drum pattern.
6. **Melody**: write a short identifiable motif, then create variations.
7. **Structure**: expand the loop into sections using 4, 8, or 16 bar blocks.
8. **Ableton Plan**: specify tracks, clips, note grids, scene names, and arrangement durations.
9. **Finish**: apply subtraction, commitment, and completion prompts.

## Output Contract

For full song sketches, produce these sections:

- **Composition Brief**: genre, BPM, meter, key/mode, constraint, reference energy.
- **Pattern Grid**: drum grid, bass rhythm, melody motif, and bar lengths.
- **Harmony Map**: chords, roman numerals, voicings, harmonic rhythm, tension/release notes.
- **Section Plan**: Intro, Build, Break, Drop/Hook, Variation, Outro with bar counts and active parts.
- **Ableton Execution Notes**: track names, clip lengths, scene names, MIDI note JSON strategy, and `$ableton-cli` handoff notes.
- **Finish Checklist**: decisions to commit, parts to remove, renders or bounces to make, and completion criteria.

For Ableton handoff mode, also include a machine-readable `composition_spec` JSON object. Read `references/output-contracts.md` before producing it.

For narrow requests, return only the relevant sections; do not emit the full song-sketch template.

## Validation Rules

Before finalizing Ableton-ready material, verify:

- Section bar counts sum to the requested length.
- MIDI notes use valid `pitch`, `start_time`, `duration`, `velocity`, and `mute` fields.
- Bass and kick are designed as one composite low-end part.
- Browser targets are search queries or placeholders, not hard-coded paths.
- Section plans include density, foreground/midground/background roles, add/mute moves, and transition events when arranging a complete song.
- Narrow requests do not return unrelated full-contract sections.

Use bundled scripts when deterministic conversion or validation is useful:

- `scripts/grid_to_notes.py`: 16-step or 32-step drum grid to Ableton note JSON.
- `scripts/chords_to_notes.py`: tonic, mode, and roman numerals to chord note JSON.
- `scripts/validate_composition_spec.py`: validate Ableton-ready `composition_spec`.

## Reference Selection

- Read `references/learning-music-system.md` when starting from scratch, teaching the user, or structuring the work from rhythm through song form.
- Read `references/music-theory-toolkit.md` when choosing keys, scales, modes, chords, voicings, seventh chords, or harmonic functions.
- Read `references/creative-strategies.md` when the user is blocked, over-editing, stuck in loops, or needs a finish plan.
- Read `references/pattern-recipes.md` when generating concrete drum, harmony, bass, or melody patterns.
- Read `references/ableton-composition-bridge.md` when the output should be executable or easily translated with `$ableton-cli`.
- Read `references/output-contracts.md` when the user asks for Ableton-ready implementation, MIDI JSON, or structured handoff.
- Read `references/genre-playbooks.md` when selecting genre defaults or making genre-specific decisions.
- Read `references/arrangement-energy.md` when expanding loops into 32- or 64-bar forms.
- Read `references/sound-design-palettes.md` when choosing browser search queries or role-based sound targets.
- Read `references/quality-rubric.md` when evaluating a draft or running regression-style checks.

## Ableton Handoff

Do not duplicate the `$ableton-cli` command catalog. Hand off intent and structured data:

- Preflight intent: wait-ready, doctor if needed, then tracks list.
- Browser searches required by role, for example `Drum Rack`, `Kit`, `Operator bass`, `Drift bass`, `Wavetable pad`, `Analog keys`.
- Track plan: default order `0 Drums`, `1 Bass`, `2 Chords`, `3 Lead`, `4 Texture/FX`.
- Clip plan: scene clips with lengths in bars and beats.
- Notes: inline note JSON or a path to a generated notes file.
- Arrangement: scene names, start bars, durations, density, active tracks.
- Finish: save/export target if requested.

Always avoid hard-coding browser item paths, Drum Rack kits, or device targets. Ask `$ableton-cli` workflows to search the active Ableton browser catalog first, then use returned paths or URIs.

## Composition Rules

- Separate generation from editing: create several options before judging them.
- Prefer simple, playable material before advanced theory.
- Keep kick and bass clear by treating the low end as one composite part.
- Use foreground, middle ground, and background roles while composing, not only while mixing.
- Build the maximal-density section first when arrangement is unclear.
- Finish imperfect sketches instead of abandoning them.
