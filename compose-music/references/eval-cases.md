# Eval Cases

Use these cases after changing `SKILL.md`, scripts, or references. Score the answer, then validate any emitted `composition_spec` with `scripts/validate_composition_spec.py`.

## Rubric

- Score 0-2: trigger correctness.
- Score 0-2: output contract compliance.
- Score 0-2: musical coherence.
- Score 0-2: Ableton handoff completeness.
- Score 0-2: safety and no fake browser paths.

Pass threshold: `>= 8/10` and no structural validation errors.

## Cases

| ID | Prompt | Pass Conditions |
| --- | --- | --- |
| E01 | Make an 8-bar dark techno loop in Ableton. | Ableton Plan Mode; 125-138 BPM; minor, phrygian, dorian, or similarly dark palette; drum, bass, chord/stab, lead or texture roles; 8-bar `composition_spec`; validator passes. |
| E02 | Write only a bassline for this kick pattern. | Sketch Mode or Pattern Mode behavior; bassline only; kick/bass conflict note; no full arrangement or unrelated tracks. |
| E03 | Turn this 4-bar loop into a 64-bar arrangement. | Section lengths total 64; maximal-density section identified; subtraction, add/mute moves, and transition events included. |
| E04 | Make a D dorian house sketch. | D dorian palette; modal logic such as `i-IV`, `i-v`, or dorian color tone; house tempo and groove assumptions. |
| E05 | Implement in Ableton. | Ableton Plan Mode; preflight, browser search intent, track plan, clip plan, notes JSON strategy, dry-run or plan-first safety; no fixed browser path. |
| E06 | I am stuck and over-editing. | Repair or Sketch Mode; uses generation/editing separation, render commitment, subtraction, and a finish checklist. |
| E07 | Give me only chord options. | Harmony Map only; roman numerals, voicing, tension/release; no drums, full arrangement, or Ableton command plan. |
| E08 | Make jungle / drum and bass. | 160-180 BPM range; breakbeat-oriented drum logic; sub or reese bass role; sparse harmony or atmosphere; clear drop entry. |
| E09 | Repair this loop: kick and bass feel muddy. | Diagnosis first; low-end composite reasoning; edited bass rhythm/register or kick gap strategy; minimal execution notes. |
| E10 | Make a 96-bar ambient techno arrangement. | 96-bar section template; slow density curve; low harmonic density; texture-led transitions; validator passes if `composition_spec` is emitted. |

## Failure Signals

- The skill returns a full song sketch for a narrow request.
- Ableton implementation lacks `composition_spec`.
- Section lengths do not match the requested total.
- Track references in sections do not exist.
- Notes exceed clip length or use invalid MIDI pitch or velocity.
- Browser targets look like local paths, fixed catalog paths, or invented URIs.
