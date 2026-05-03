# Eval Cases

Use these cases after changing `SKILL.md`, scripts, or references. Score the answer, then validate any emitted `composition_spec` with `scripts/validate_composition_spec.py`.

## Rubric

- Score 0-2: trigger correctness.
- Score 0-2: output contract compliance.
- Score 0-2: musical coherence.
- Score 0-2: Ableton handoff completeness.
- Score 0-2: safety and no fake browser paths.

Pass threshold: `score >= 0.9` and no structural validation errors.

## Cases

| ID | Prompt | Pass Conditions |
| --- | --- | --- |
| E01 | Make an 8-bar dark techno loop in Ableton. | Ableton Handoff Mode; 125-138 BPM; minor, phrygian, dorian, or similarly dark palette; drum, bass, chord/stab, lead or texture roles; 8-bar `composition_spec`; validator passes. |
| E02 | Write only a bassline for this kick pattern. | Idea Mode or Pattern Mode behavior; bassline only; kick/bass conflict note; no full arrangement or unrelated tracks. |
| E03 | Turn this 4-bar loop into a 64-bar arrangement. | Section lengths total 64; maximal-density section identified; subtraction, add/mute moves, and transition events included. |
| E04 | Make a D dorian house sketch. | D dorian palette; modal logic such as `i-IV`, `i-v`, or dorian color tone; house tempo and groove assumptions. |
| E05 | Implement in Ableton. | Ableton Handoff Mode; preflight, browser search intent, track plan, clip plan, notes JSON strategy, dry-run or plan-first safety; no fixed browser path. |
| E06 | I am stuck and over-editing. | Repair Mode or Idea Mode; uses generation/editing separation, render commitment, subtraction, and a finish checklist. |
| E07 | Give me only chord options. | Harmony Map only; roman numerals, voicing, tension/release; no drums, full arrangement, or Ableton command plan. |
| E08 | Make jungle / drum and bass. | 160-180 BPM range; breakbeat-oriented drum logic; sub or reese bass role; sparse harmony or atmosphere; clear drop entry. |
| E09 | Repair this loop: kick and bass feel muddy. | Diagnosis first; low-end composite reasoning; edited bass rhythm/register or kick gap strategy; minimal execution notes. |
| E10 | Make a 96-bar ambient techno arrangement. | 96-bar section template; slow density curve; low harmonic density; texture-led transitions; validator passes if `composition_spec` is emitted. |
| E11 | Only give me a melody motif. | Pattern Mode; includes `rhythm_cell`, `pitch_cell`, and `variation_strategy`; no full template. |
| E12 | Make 7/8 techno in Ableton. | Explains `composition_spec` currently validates `4/4`; gives safe plan or asks to convert intent; no invalid spec. |
| E13 | Garage drum and bass hybrid. | Resolves tempo toward DnB and swing toward garage; clear drop entry. |
| E14 | Only chord options. | Pattern Mode; roman numerals, voicings, borrowed color when useful; no drums or full arrangement. |
| E15 | Implement in Ableton with no genre. | Chooses a focused default genre and states assumption; emits valid `composition_spec`. |
| E16 | Repair broken spec with missing handoff and fake path. | Identifies missing `handoff`; rewrites path-like browser target to broad search query. |
| E17 | Beat-light ambient material. | Uses density for texture/register motion; no forced drum kit. |
| E18 | Shuffled UK garage grid. | Preserves `timing_feel`, `swing_amount`, and payload metadata. |
| E19 | Polymeter IDM percussion. | Includes reset metadata and path-free handoff language. |
| E20 | Acid techno sound design. | Uses `sound_intent` and `shape_intent`; avoids preset/path claims; validator passes if spec emitted. |
| E21 | 96-bar minimal techno arrangement. | Section lengths sum to 96; density, identity carrier, move, and transition fields are present. |
| E22 | Borrowed chord options. | Includes borrowed chord, slash chord, or inversion examples; no full template. |
| E23 | Kick/bass relationship enum. | Uses `avoid`, `double`, `answer`, or `intentional_overlap` explicitly. |
| E24 | Convert spec to handoff plan. | Uses `ableton_handoff_plan` as intermediate artifact with preflight, browser searches, track plan, and clip plan. |
| E25 | 128-bar progressive house. | Section lengths sum to 128; identity carriers and transitions are present. |

## Failure Signals

- The skill returns a full song sketch for a narrow request.
- Ableton implementation lacks `composition_spec`.
- Section lengths do not match the requested total.
- Track references in sections do not exist.
- Notes exceed clip length or use invalid MIDI pitch or velocity.
- Browser targets look like local paths, fixed catalog paths, or invented URIs.
