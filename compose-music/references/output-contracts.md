# Output Contracts

Use this reference when the user asks for Ableton-ready implementation, MIDI JSON, or a structured handoff. Human-readable sections are still useful, but implementation work should pass through `composition_spec`.

## composition_spec v1

Emit `composition_spec` only when requested, when the user asks for Ableton implementation, or when a structured handoff would reduce ambiguity.

Readable schema guide: `references/composition-spec-schema.md`.
Machine schema: `references/composition_spec.schema.json`.

Required top-level fields:

- `version`: currently `"1.0"`.
- `brief`: genre, BPM, meter, key, mode, length, and creative constraint.
- `tracks`: ordered track plan with roles, clip lengths, browser queries, and notes.
- `sections`: arrangement sections with bar counts, density, and active tracks.
- `handoff`: Ableton browser search intent and export target.
- `finish_criteria`: concrete completion checks.

Example:

```json
{
  "version": "1.0",
  "brief": {
    "genre": "melodic techno",
    "bpm": 124,
    "meter": "4/4",
    "key": "D",
    "mode": "dorian",
    "length_bars": 64,
    "creative_constraint": "no supersaw; identity comes from bass rhythm"
  },
  "tracks": [
    {
      "name": "Drums",
      "role": "rhythm",
      "clip_length_bars": 2,
      "browser_query": "Drum Rack dry electronic kit",
      "timing_feel": "straight",
      "notes": [
        {"pitch": 36, "start_time": 0.0, "duration": 0.25, "velocity": 110, "mute": false}
      ]
    },
    {
      "name": "Bass",
      "role": "low-end identity",
      "clip_length_bars": 4,
      "browser_query": "Operator bass",
      "notes": []
    }
  ],
  "sections": [
    {
      "name": "Intro",
      "start_bar": 1,
      "length_bars": 8,
      "density": 1,
      "active_tracks": ["Drums", "Texture/FX"],
      "foreground": [],
      "midground": ["Texture/FX"],
      "background": ["Drums"],
      "identity_carrier": "Texture/FX",
      "move": "add filtered hats in bar 7",
      "transition_event": "short noise rise into Groove"
    }
  ],
  "handoff": {
    "requires_browser_search": true,
    "browser_queries": ["Drum Rack dry electronic kit", "Operator bass", "Wavetable pad"],
    "export_target": "rough arrangement render"
  },
  "finish_criteria": [
    "64-bar arrangement exists",
    "kick and bass do not mask each other",
    "one bounce/export target is named"
  ]
}
```

## Track Fields

- `name`: stable track label used in section `active_tracks`.
- `role`: musical job, not a mix setting.
- `clip_length_bars`: positive number; multiply by 4.0 for beats in 4/4.
- `browser_query`: search query or placeholder, never a fake path.
- `notes`: Ableton note JSON objects with `pitch`, `start_time`, `duration`, `velocity`, and `mute`.
- Optional timing fields: `timing_feel`, `swing_amount`, `shuffle_amount`, `humanization`, and `polymeter_reset_bar`.

Use `scripts/grid_to_notes.py` for drum rows and `scripts/chords_to_notes.py` for chord tracks when exact MIDI notes matter. Use `grid_to_notes.py --payload` when timing feel metadata should be preserved alongside note JSON.

## Section Fields

- `name`: scene or arrangement section name.
- `start_bar`: 1-based bar number.
- `length_bars`: section duration.
- `density`: 0-5, as defined in `arrangement-energy-curves.md`.
- `active_tracks`: track names active in the section.
- `foreground`, `midground`, `background`: role allocation for complete song plans.
- `identity_carrier`: track name carrying the section identity.
- `move`: primary add/mute/subtraction decision.
- `transition_event`: fill, riser, silence, pickup, or automation event into the next section.

## Handoff Fields

- `requires_browser_search`: usually `true`; exact Ableton browser paths and URIs must come from the active catalog.
- `browser_queries`: deduplicated search intent collected from track `browser_query` values.
- `export_target`: short description of the expected save, render, or rough bounce.

## Validation

Before handing off:

1. Save JSON to a temporary file if needed.
2. Run `python3 compose-music/scripts/validate_composition_spec.py <file> --pretty`.
3. Fix errors before using `$ableton-cli`.

Do not expose raw validation mechanics to the user unless they asked for implementation details.

## ableton_handoff_plan v1

Use `scripts/composition_spec_to_handoff_plan.py` to turn a valid `composition_spec` into an intermediate `ableton_handoff_plan` before asking `$ableton-cli` to operate on Live.

The plan separates:

- `preflight_intent`: readiness checks such as wait-ready, doctor-if-needed, and tracks-list.
- `browser_searches`: role-based search queries for the active Ableton browser catalog.
- `track_plan`: ordered track names and musical roles.
- `clip_plan`: clip lengths, note source, and timing metadata.
- `arrangement_sections`: section bars, density, active tracks, role layers, identity carrier, moves, and transition events.
- `finish_criteria`: completion checks from the source spec.
