---
name: compose-music
description: Design complete song sketches and Ableton-ready composition plans with rhythm, pitch palettes, chord progressions, basslines, melodies, arrangement structure, and finishing prompts. Use when Codex should help compose electronic music, generate drum patterns, write chord progressions, build bass or melody parts, turn loops into songs, or prepare musical material for implementation with ableton-cli.
---

# Compose Music

## Core Workflow

Use this skill as the composition layer above `$ableton-cli`. First decide the music, then translate it into Ableton operations.

Default assumptions when the user gives no constraints:
- Meter: `4/4`
- Tempo: `120 BPM`
- Tonality: `minor` or `dorian`
- Loop target: `8 bars`
- Arrangement target: `32` or `64 bars`

Follow this sequence:

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

For narrow requests, return only the relevant sections.

## Reference Selection

- Read `references/learning-music-system.md` when starting from scratch, teaching the user, or structuring the work from rhythm through song form.
- Read `references/music-theory-toolkit.md` when choosing keys, scales, modes, chords, voicings, seventh chords, or harmonic functions.
- Read `references/creative-strategies.md` when the user is blocked, over-editing, stuck in loops, or needs a finish plan.
- Read `references/pattern-recipes.md` when generating concrete drum, harmony, bass, or melody patterns.
- Read `references/ableton-composition-bridge.md` when the output should be executable or easily translated with `$ableton-cli`.

## Ableton CLI Boundary

Do not duplicate the `$ableton-cli` command catalog. When asked to implement in Ableton, use this skill to decide musical content and use `$ableton-cli` for deterministic DAW operations.

Always avoid hard-coding browser item paths, Drum Rack kits, or device targets. Ask `$ableton-cli` workflows to search the active Ableton browser catalog first, then use returned paths or URIs.

## Composition Rules

- Separate generation from editing: create several options before judging them.
- Prefer simple, playable material before advanced theory.
- Keep kick and bass clear by treating the low end as one composite part.
- Use foreground, middle ground, and background roles while composing, not only while mixing.
- Build the maximal-density section first when arrangement is unclear.
- Finish imperfect sketches instead of abandoning them.
