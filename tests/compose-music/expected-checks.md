# compose-music Expected Checks

Use these checks against the prompts in `prompts.md`. The executable source of truth is `evals/compose-music.checks.json`.

## Global Checks

- Narrow requests return only relevant sections.
- Full song sketch requests include the relevant human-readable sections without forcing Ableton artifacts.
- Ableton-ready or implementation requests include a valid `composition_spec`.
- `ableton_handoff_plan` is used as the intermediate artifact for implementation conversion requests.
- No fake browser paths, fixed Drum Rack kit paths, preset names presented as resolved choices, or hard-coded device targets appear.
- MIDI note JSON validates when included.
- Section lengths sum to the requested arrangement length.
- Harmony tasks include roman numerals and concrete chords.
- Kick and bass relationship is explicitly described when both are present.
- Sound design uses `sound_intent`, `shape_intent`, and broad `browser_query` values.
- Finish checklist contains concrete commit/export criteria for completion-oriented prompts.

## Prompt-Specific Checks

1. Dark techno loop: includes D dorian pitch palette, 8 bars, drum grid, bass/kick composite plan, and Ableton Handoff Mode fields.
2. Grid conversion: returns note JSON only, with 4/4 beat positions where step 1 is `0.0` and step 5 is `1.0`.
3. Loop expansion: includes 64 total bars, density per section, add/mute decisions, and transition events.
4. Bassline only: avoids full template, names chord roots and rhythm, and explains kick relationship if drums are assumed.
5. Ableton implementation: delegates command execution to `$ableton-cli`, includes browser search queries, and does not duplicate the full command catalog.
6. Finish plan: diagnoses over-editing, names commit decisions, render/export target, and one intentional revision path.
7. Garage pattern: includes swing handling and pattern details only, not a full section plan.
8. Melodic techno spec: emits valid `composition_spec` fields and notes that can be checked by `validate_composition_spec.py`.
9. Kick/bass diagnosis: treats low end as one composite line and proposes concrete edits to timing, duration, or register.
10. Ambient arrangement: uses density even without a strong beat and defines foreground/midground/background roles.
11. Melody motif: includes `rhythm_cell`, `pitch_cell`, and `variation_strategy`; no full song template.
12. 7/8 techno: states the current `composition_spec` validator supports `4/4` only and avoids emitting invalid implementation JSON.
13. Hybrid genre: resolves DnB tempo/drop logic with garage swing and bass phrasing.
14. Chord-only request: includes roman numerals and voicing notes without drums or arrangement.
15. Missing genre: chooses a focused default genre and states the assumption before emitting a valid spec.
16. Broken spec repair: adds missing `handoff` fields and replaces path-like browser targets with broad search intent.
17. Ambient texture: uses density for register and texture, not drum count, and does not force a drum kit.
18. UK garage grid: includes swing metadata and payload-preserving handoff guidance.
19. IDM polymeter: includes reset metadata and path-free browser language.
20. Acid techno: uses acoustic sound intent and shape intent instead of preset names; valid spec when emitted.
21. Minimal techno expansion: section lengths total 96 bars with identity carriers and transitions.
22. Borrowed chords: gives borrowed chord, slash chord, and inversion examples without a full template.
23. Bassline relationship: explicitly uses `avoid`, `double`, `answer`, or `intentional_overlap`.
24. Handoff conversion: includes `ableton_handoff_plan`, `preflight_intent`, `browser_searches`, `track_plan`, and `clip_plan`.
25. Progressive house arrangement: section lengths total 128 bars with density, identity carriers, and transitions.
