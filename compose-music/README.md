# compose-music

## What It Does

`compose-music` turns electronic music requests into concrete sketches, patterns, arrangements, and Ableton-ready handoff artifacts.

- Electronic music sketching with genre, tempo, key, groove, harmony, bass, melody, and arrangement decisions.
- Pattern generation for drum grids, basslines, chord loops, and melody motifs.
- Loop-to-song arrangement using density, foreground/midground/background roles, moves, and transitions.
- Ableton handoff through validated `composition_spec` and generated `ableton_handoff_plan` JSON.
- User-provided sample workflows for audio loops and fixed-grid sliced break playback without embedding private paths.

## When To Use

Use this skill when the task is about composition, arrangement, MIDI note material, or an implementation plan that should be handed to Ableton later.

Good requests include:

- "Make an 8-bar dark techno loop in Ableton."
- "Turn this drum grid into MIDI note JSON."
- "Expand this 4-bar loop into a 64-bar arrangement."
- "Create a melodic techno `composition_spec`."
- "Make a 170 BPM jungle Amen break using my local sample asset."
- "Diagnose why my kick and bass feel crowded."

## When Not To Use

Do not use this skill for pure Ableton command lookup, Remote Script installation, transport control, browser catalog inspection, or mixing-only advice. Those belong to `$ableton-cli` or a mixing-focused workflow.

## Output Modes

- **Idea Mode**: brainstorming, options, constraints, and high-level direction.
- **Pattern Mode**: one narrow unit such as a grid, bassline, chord loop, motif, or MIDI JSON.
- **Song Sketch Mode**: human-readable loop-to-song arrangements without direct Ableton execution.
- **Ableton Handoff Mode**: validated `composition_spec` plus concise human plan for implementation requests.
- **Repair Mode**: diagnosis and minimal edits for an existing loop, progression, melody, or arrangement.

Narrow requests should stay narrow. Do not emit a full song-sketch template when the user only asked for a bassline, chord options, or a grid conversion.

## composition_spec Example

See `examples/dark-techno-8bar.composition_spec.json` for a complete minimal spec. The top-level contract is:

- `version`
- `brief`
- `sample_assets` when user-owned audio is referenced
- `tracks`
- `sections`
- `handoff`
- `finish_criteria`

Validate a spec before Ableton handoff:

```bash
python3 compose-music/scripts/validate_composition_spec.py compose-music/examples/dark-techno-8bar.composition_spec.json --pretty
```

Convert it into an intermediate handoff plan:

```bash
python3 compose-music/scripts/composition_spec_to_handoff_plan.py compose-music/examples/dark-techno-8bar.composition_spec.json --pretty
```

## Running Helper Scripts

Convert a drum grid to note JSON:

```bash
python3 compose-music/scripts/grid_to_notes.py compose-music/examples/garage-swing-grid.json --payload --pretty
```

Convert a roman-numeral chord loop to note JSON:

```bash
python3 compose-music/scripts/chords_to_notes.py compose-music/examples/chord-loop-i-VI-III-VII.json --pretty
```

Convert an Amen slice trigger grid to note JSON:

```bash
python3 compose-music/scripts/breakbeat_pattern_to_notes.py compose-music/examples/amen-break-trigger-grid.json --pretty
```

Resolve a private sample asset from a user manifest:

```bash
AMEN_BREAK_WAV=/tmp/amen.wav python3 compose-music/scripts/resolve_sample_assets.py --manifest compose-music/examples/sample_assets.example.json --asset-id amen_break --pretty
```

Rows in grid files may use either `steps` or the equivalent `grid` alias. If both are present, the values must match.

## Running Tests

```bash
python3 -m unittest discover compose-music/tests
```

## Running Evals

Dry-run the deterministic eval harness:

```bash
node evals/run-compose-music-evals.mjs --dry-run
```

Grade saved local answers from `evals/artifacts`:

```bash
node evals/run-compose-music-evals.mjs
```

Run Codex-generated answers when `codex exec --json` is available:

```bash
node evals/run-compose-music-evals.mjs --run-codex
```

The merge threshold is `score >= 0.9` for every prompt plus no failed structural checks.

## Safe Ableton Handoff Policy

`composition_spec` and `ableton_handoff_plan` contain musical intent and structured data only. Browser targets must be broad search queries such as `Drum Rack dry electronic kit` or `Operator bass`; exact paths, URIs, racks, kits, presets, and local files must come from active `$ableton-cli` browser search results.

For user-owned audio, use `sample_assets` with `path_ref`, `root_env` plus `relative_path`, or a private manifest. Do not put `/Users/...`, `file://...`, or sample filenames into `browser_query` or `handoff.browser_queries`.

The handoff plan is an intermediate artifact. It does not operate on Ableton Live directly.
