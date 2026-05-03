# Ableton Composition Bridge

Use this reference when turning a composition plan into Ableton-ready instructions. Use `$ableton-cli` for exact commands and current CLI syntax.

## Table of Contents

- Division of responsibility
- Track plan
- Clip and scene plan
- MIDI note JSON strategy
- Arrangement strategy
- Browser and device selection
- Handoff checklist

## Division of Responsibility

`compose-music` decides:

- Genre, BPM, key, mode, scale degrees.
- Drum, bass, chord, and melody patterns.
- Section lengths and active parts.
- Musical constraints and finish criteria.

`$ableton-cli` executes:

- Connectivity checks.
- Track creation and naming.
- Browser search and device loading.
- Clip creation.
- MIDI note insertion.
- Scene and arrangement operations.
- Playback, saving, and export.

## Track Plan

Default track order:

1. `Drums`
2. `Bass`
3. `Chords`
4. `Lead`
5. `Texture` or `FX`

For dense arrangements, split `Drums` into `Kick`, `Snare/Clap`, `Hats`, and `Percussion` only when separate mixing or muting is required.

## Clip and Scene Plan

Default clip lengths:

- Drum loop: `1`, `2`, or `4` bars.
- Bass loop: `2`, `4`, or `8` bars.
- Chord loop: `4` or `8` bars.
- Melody loop: `4` or `8` bars.

Default scene names:

```text
Intro
Groove
Build
Drop
Break
Drop Variation
Outro
```

When producing an Ableton plan, include each scene's duration in bars and which clips are active.

For Ableton handoff mode, include enough information to create clips without guessing:

- Track index and track name.
- Scene or clip slot intent.
- Clip length in bars and beats.
- Notes inline as Ableton note JSON, or a path to a generated notes JSON file.
- Scene names, start bars, section lengths, density, and active tracks.

## MIDI Note JSON Strategy

Use beat positions. In 4/4:

- 1 bar = `4.0` beats.
- 1 sixteenth note = `0.25` beats.
- Step `01` starts at `0.0`.
- Step `05` starts at `1.0`.
- Step `09` starts at `2.0`.
- Step `13` starts at `3.0`.

Note object shape:

```json
{"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 100, "mute": false}
```

Velocity defaults:

- Kick: `110`
- Snare or clap: `100`
- Closed hat: `70-90`
- Open hat: `75-95`
- Bass: `90-110`
- Chords: `65-90`
- Lead: `80-105`

Keep bass notes short around kick hits unless a sustained sub is intentional.

Use bundled deterministic helpers when useful:

- `scripts/grid_to_notes.py` for 16-step or 32-step drum grids.
- `scripts/chords_to_notes.py` for roman-numeral chord progressions.
- `scripts/validate_composition_spec.py` before executing a structured handoff.

## Arrangement Strategy

When the user needs a complete track:

1. Create the maximum-density section first.
2. Copy it across the full arrangement.
3. Remove parts to shape intro, build, break, and outro.
4. Add fills only at section boundaries.
5. Commit MIDI or sound-design decisions once the section works.

Default 64-bar form:

```text
Intro 8 | Groove 8 | Build 8 | Drop 16 | Break 8 | Drop Variation 12 | Outro 4
```

For a 32-bar sketch:

```text
Intro 4 | Groove 4 | Build 4 | Drop 8 | Break 4 | Drop Variation 6 | Outro 2
```

## Browser and Device Selection

Never hard-code browser targets. In Ableton plans, instruct the executor to:

1. Wait until Ableton is ready.
2. Search the active browser catalog for the needed rack, instrument, effect, or kit.
3. Select exact returned paths or URIs.
4. Load those targets.

Use placeholder names like `Drum Rack kit selected from browser search`, not fake paths.

Browser handoff should name search intent, not a command sequence:

- Drums: `Drum Rack`, `Kit`, or a genre-specific kit query.
- Bass: `Operator bass`, `Drift bass`, `Analog bass`, or `808 bass`.
- Chords: `Wavetable pad`, `Analog keys`, `Electric keys`, or `Chord stab`.
- Lead: `Wavetable lead`, `Analog lead`, `Pluck`, or `Vocal chop`.
- Texture/FX: `Noise`, `Atmosphere`, `Riser`, `Impact`, or `Reverb`.

## Handoff Checklist

Before using `$ableton-cli`, the composition plan should include:

- BPM and meter.
- Key, mode, and pitch palette.
- Track list and role of each track.
- Clip lengths in beats or bars.
- MIDI note strategy for each part.
- Scene names and durations.
- Arrangement target length.
- Any browser searches required.
- Finish criteria and export target if requested.

If the plan includes `composition_spec`, validate that:

- Section lengths sum to `brief.length_bars`.
- Track names are unique and match section `active_tracks`.
- Notes stay inside each clip length.
- Browser queries do not look like local paths or invented browser paths.
