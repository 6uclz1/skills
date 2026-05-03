# compose-music Expected Checks

Use these checks against the prompts in `prompts.md`.

## Global Checks

- Narrow requests return only relevant sections.
- Full sketch requests include Composition Brief, Pattern Grid, Harmony Map, Section Plan, Ableton Execution Notes, and Finish Checklist.
- Ableton-ready or implementation requests include `composition_spec` or an equivalent structured handoff.
- No fake browser paths, fixed Drum Rack kit paths, or hard-coded device targets appear.
- MIDI note JSON validates when included.
- Section lengths sum to the requested arrangement length.
- Harmony tasks include both roman numerals and concrete chords.
- Kick and bass relationship is explicitly described when both are present.
- Finish checklist contains concrete commit/export criteria for completion-oriented prompts.

## Prompt-Specific Checks

1. Dark techno loop: includes D dorian pitch palette, 8 bars, drum grid, bass/kick composite plan, and Ableton handoff fields.
2. Grid conversion: returns note JSON only, with 4/4 beat positions where step 1 is `0.0` and step 5 is `1.0`.
3. Loop expansion: includes 64 total bars, density per section, add/mute decisions, and transition events.
4. Bassline only: avoids full template, names chord roots and rhythm, and explains kick relationship if drums are assumed.
5. Ableton implementation: delegates command execution to `$ableton-cli`, includes browser search queries, and does not duplicate the full command catalog.
6. Finish plan: diagnoses over-editing, names commit decisions, render/export target, and one intentional revision path.
7. Garage pattern: includes swing handling and pattern details only, not a full section plan.
8. Melodic techno spec: emits valid `composition_spec` fields and notes that can be checked by `validate_composition_spec.py`.
9. Kick/bass diagnosis: treats low end as one composite line and proposes concrete edits to timing, duration, or register.
10. Ambient arrangement: uses density even without a strong beat and defines foreground/midground/background roles.
