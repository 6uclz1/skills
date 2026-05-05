---
name: anime-remix-ableton-cli
description: Create private-use anime song remix arrangements in Ableton Live using ableton-cli. Use for manifest-first remix planning, stem registration, source-preserving section mapping, harmonic/chord analysis, anime-club/anime-dnb/anime-future-bass arrangement layers, vocal chops on separate tracks, mix setup, mastering QA, and export planning.
---

# Anime Remix Production with ableton-cli

## Scope

Use this skill as a remix-production layer above `$ableton-cli`. It helps plan and execute private-use anime-style remixes in Ableton Live from user-provided local sources, stems, BPM/key notes, section maps, and reference intent.

Use only with:

- original material;
- cleared material;
- private test material;
- user-provided local files.

Do not:

- publish, upload, stream, distribute, sell, DJ publicly, or perform generated remixes;
- imply that this skill grants copyright, arrangement, master-use, neighboring-rights, synchronization, publishing, or distribution permission;
- download or retrieve copyrighted songs automatically;
- bypass DRM or copy protection;
- use illegal uploads as source material.

When initializing a remix manifest, default to `--rights-status private_test` unless the user explicitly provides a more precise cleared or original status. Record rights status in `remix_project.json`, QA notes, and export filenames such as `song_private_test_remix.wav`.

## Core Rules

- Run all commands as `uv run ableton-cli ...`.
- Prefer `--output json` for machine-readable results.
- Use `--timeout-ms 15000` for connection and inspection commands.
- Use manifest-first flow: `plan -> inspect -> dry-run -> apply -> qa`.
- Do not write to Ableton Live until the manifest, assets, sections, target, and dry-run result have been inspected.
- Run `remix apply --dry-run` before `remix apply --yes`.
- Run `remix mastering apply --dry-run` before `remix mastering apply --yes`.
- Do not run destructive operations such as track, clip, device, or file deletion without explicit user confirmation.
- Do not hard-code Ableton Browser URIs, paths, kit names, or device locations. Search the active browser catalog first and use only returned `uri` or `path` values.

## Dynamic Arrangement Rules

When planning anime remixes, assign an energy and layer policy to every section.

Default energy scale:

- `0`: silence, texture, or transition tail
- `1`: pad, vocal, or melody-only reset; drums off
- `2`: light groove; no full drums
- `3`: build tension; snare/riser allowed, full drums off
- `4`: drop/hook; full drums and bass allowed
- `5`: final drop; full drums, bass, fills, and variation

Default drum policy:

- `intro`: `light` or `filtered`
- `verse` / `vocal_verse`: `off` or `light`
- `pre` / `pre_drop_vocal`: `off` except pickup/fill
- `build`: `build_only`, no full groove
- `chorus` / `chorus_drop` / `drop`: `full`
- `bridge` / `interlude` / `breakdown` / `intro_pad`: `off`
- `final_chorus` / `final_drop` / `second_drop`: `full`
- `outro`: `reduced` or DJ-exit only

Layer policy expectations:

- `drum_policy: off`: no `role: drums` arrangement steps.
- `drum_policy: build_only`: risers, snare rolls, impacts, or filtered percussion only; no full groove.
- `drum_policy: light`: filtered break, low-velocity percussion, or a short teaser only.
- `drum_policy: reduced`: limited exit or pickup rhythm only.
- `drum_policy: full`: full drum groove allowed.
- `drum_policy: full_with_variation`: full drum groove plus fills or variation.

If the source arrangement clearly contradicts these defaults, record the override in the manifest and in QA. Do not turn `bridge`, `interlude`, `breakdown`, `intro_pad`, or other reset sections into full drum sections unless the user or verified source arrangement explicitly calls for it. If only a `full_mix` or drum-baked `instrumental` asset is available, record that drums cannot be guaranteed off even when the plan avoids new drum steps.

## Source and Harmony Rules

- Preserve the user-provided full mix as the main source track by default. Place it once as a continuous arrangement reference unless the user explicitly asks for a reconstructed edit.
- Do not create a remix by repeating the same full-mix file from the beginning across multiple section clips. If `remix apply --dry-run` shows repeated full-mix `arrangement_clip_create` steps without source offsets, warp markers, or a documented musical reason, stop and revise the plan.
- Register a full mix as `full_mix` or `reference`. Do not silently register the same full mix as `vocal` to satisfy a workflow requirement.
- If stems are missing, keep stem-dependent actions optional. Use added drums, bass, chords, risers, impacts, and texture tracks around the preserved full mix instead of pretending the full mix is a clean vocal or instrumental stem.
- Run or document harmonic analysis before writing bass, chord, pad, supersaw, or chop-trigger MIDI. Record original key, section-level chord progression, modulation notes, and confidence in the manifest or production notes.
- Do not invent generic progressions such as `E,B,C#m,A` unless analysis, user notes, or manual listening supports them.
- Vocal chops must be created on separate tracks. Never cut, replace, or destructively edit the main full-mix track for chops.

## Required Preflight

Run before any mutation:

```bash
uv run ableton-cli --timeout-ms 15000 --output json wait-ready
uv run ableton-cli --timeout-ms 15000 --output json doctor
uv run ableton-cli --timeout-ms 15000 --output json ping
uv run ableton-cli --timeout-ms 15000 --output json song info
uv run ableton-cli --timeout-ms 15000 --output json tracks list
```

Stop if any command returns `ok: false` or a non-zero exit code. Summarize the failing command, exit code, and `error` field before attempting setup repair.

## Remix Capability Gate

Before using the remix workflow on an unknown `ableton-cli` installation, confirm that the local CLI build exposes the required command groups:

```bash
uv run ableton-cli remix --help
uv run ableton-cli audio --help
```

If either command group is missing, stop and tell the user that the installed `ableton-cli` build does not include the remix/audio layer required by this skill. Do not simulate manifest, section, remix, vocal-chop, mastering, or QA commands with unrelated primitive commands.

## Minimal Remix Workflow

### 1. Initialize Manifest

```bash
uv run ableton-cli --output json remix init \
  --source /abs/source/anime_song_private_test.wav \
  --project ./proj \
  --rights-status private_test
```

Use an absolute path for source audio. Keep the generated `remix_project.json` as the single source of truth for assets, analysis notes, section maps, arrangement plans, QA, and export targets.

### 2. Register Assets

Register the original full mix first. Register stems by role only when the files are actually stems. Typical roles are `full_mix`, `reference`, `vocal`, `instrumental`, `drums`, and `bass`.

```bash
uv run ableton-cli --output json audio asset add \
  --project ./proj/remix_project.json \
  --role full_mix \
  --path /abs/source/anime_song_private_test.wav
```

```bash
uv run ableton-cli --output json audio asset add \
  --project ./proj/remix_project.json \
  --role vocal \
  --path /abs/stems/vocal_private_test.wav

uv run ableton-cli --output json audio asset add \
  --project ./proj/remix_project.json \
  --role instrumental \
  --path /abs/stems/instrumental_private_test.wav
```

### 3. Analyze Structure and Harmony

Before choosing target material or writing MIDI layers, identify:

- original BPM, downbeat, and pickup/count-in;
- original key and target key;
- section boundaries with timecode, bars, musical cue, and energy;
- section-level chord progression, bass roots, cadences, and modulation notes;
- which sections should keep the original song foregrounded and which sections can support remix layers.

Use available deterministic analysis commands first, then manual listening notes where the CLI cannot infer structure or harmony:

```bash
uv run ableton-cli --output json audio analyze \
  --project ./proj/remix_project.json
```

If chord analysis is external or manual, record the result in the section worksheet or manifest notes before arranging. Stop if the chord progression is unknown and the next step would create harmonic content.

### 4. Import Section Map

Prefer a manually checked section map over guessed structure. Use bar ranges and anime-song labels such as `intro`, `verse`, `pre`, `chorus`, `bridge`, `final_chorus`, and `outro`.

```bash
uv run ableton-cli --output json audio sections import \
  --project ./proj/remix_project.json \
  --sections "intro:1-8,verse:9-24,pre:25-32,chorus:33-48,bridge:49-64,final_chorus:65-80,outro:81-88"
```

Use `templates/section_map_template.md` when the user has only timestamps, lyrics cues, rough section names, or incomplete chord notes. Do not import a guessed section map as final if it would cause source loops that ignore the song structure.

### 5. Set Target

Choose a target BPM, key, and style from the material and user brief. Supported style anchors:

- `anime-club`: 128-150 BPM, four-on-floor, sidechain bass, supersaw hook, vocal chop.
- `anime-dnb`: 168-178 BPM, breakbeat, reese/sub bass, vocal chop, impact risers.
- `anime-future-bass`: 140-160 BPM, wide chords, pitched chops, sub bass, snare build.

```bash
uv run ableton-cli --output json remix set-target \
  --project ./proj/remix_project.json \
  --bpm 174 \
  --key "F minor"
```

### 6. Plan Arrangement

Default arrangement policy: preserve the full mix and add remix layers that follow the verified section map and chord progression. Use `remix plan` only after deciding whether the CLI's generated plan preserves the source correctly for the current assets.

```bash
uv run ableton-cli --output json remix plan \
  --project ./proj/remix_project.json \
  --style anime-dnb \
  --dynamics section-profiles
```

Read `examples/arrangement_forms.json` when choosing a form or adapting the section sequence. Use `--dynamics section-profiles` so the plan records section dynamics. Keep the planned `section-profiles` compatible with the imported section map, and inspect each section for `energy`, `drum_policy`, `bass_policy`, and per-step `section` / `role` before dry-run apply.

### 7. Dry Run, Inspect, Apply

```bash
uv run ableton-cli --output json remix apply \
  --project ./proj/remix_project.json \
  --dry-run
```

Inspect the returned batch steps, target tracks, clip placements, tempo/key changes, and any destructive operations. Required checks:

- full mix is preserved as one continuous main source, or any edits have explicit source offsets and musical rationale;
- no repeated full-mix clips start at the beginning only to fake sections;
- added MIDI clips follow the chord map and section roles;
- vocal chops are routed to separate tracks;
- no destructive operations appear.

Required dry-run inspection:

- section energy values are present and stay within `0-5`;
- section `drum_policy` matches the planned role, especially `off` for reset sections and `full` or `full_with_variation` for drops;
- section `bass_policy`, `vocal_policy`, and `instrumental_policy` are present where they affect layer decisions;
- every arrangement step has machine-readable `section` and `role`;
- no `off` drum policy section creates new drum clips or drum devices;
- drop sections named `drop`, `chorus_drop`, `second_drop`, or `final_drop` use `full` or `full_with_variation`;
- if only full-mix or drum-baked instrumental assets exist, the plan warns that drums cannot be guaranteed off;
- no unexpected destructive operations appear.

Only then apply:

```bash
uv run ableton-cli --output json remix apply \
  --project ./proj/remix_project.json \
  --yes
```

### 8. Vocal Chop

Use vocal chops as private production practice unless the source is cleared or original. Chops must live on separate audio/MIDI tracks. Prefer a real `vocal` stem; if only a full mix exists, mark the chop as `full_mix_texture` or similar in QA because drums, bass, and accompaniment may bleed into the chop.

```bash
uv run ableton-cli --output json remix vocal-chop \
  --project ./proj/remix_project.json \
  --source vocal \
  --section chorus \
  --slice 1/8 \
  --create-trigger
```

Read `examples/vocal_chop_recipe.json` when a user asks for chop timing, trigger mapping, or motif intent.

### 9. QA

Run QA before export or mastering decisions:

```bash
uv run ableton-cli --output json remix qa \
  --project ./proj/remix_project.json \
  --include-mastering \
  --render ./renders/song_private_test_remix.wav
```

Use `templates/qa_checklist.md` to summarize pass/fail results, rights status, missing assets, section alignment, headroom, loudness, and export readiness.

## Sound and Mix Setup

Before loading devices, search the active Ableton Browser:

```bash
uv run ableton-cli --timeout-ms 15000 --output json browser categories all
uv run ableton-cli --timeout-ms 15000 --output json browser search "Drum Rack" --path drums --item-type loadable --limit 10
uv run ableton-cli --timeout-ms 15000 --output json browser search "Kit" --path drums --item-type loadable --limit 10
uv run ableton-cli --timeout-ms 15000 --output json browser search "Operator" --path instruments --item-type loadable --limit 10
```

Use explicit returned values only:

```bash
uv run ableton-cli --output json remix setup-mix \
  --project ./proj/remix_project.json

uv run ableton-cli --output json remix setup-returns \
  --project ./proj/remix_project.json

uv run ableton-cli --output json remix setup-sidechain \
  --project ./proj/remix_project.json
```

## Mastering and Export Planning

Keep mastering conservative for private demos. Always dry-run first.

```bash
uv run ableton-cli --output json remix mastering profile list
uv run ableton-cli --output json remix mastering target set \
  --project ./proj/remix_project.json \
  --profile anime-club-demo \
  --true-peak-dbtp-max -1.0
uv run ableton-cli --output json remix mastering analyze \
  --project ./proj/remix_project.json \
  --render ./renders/song_private_test_remix.wav \
  --report-dir ./proj/reports
uv run ableton-cli --output json remix mastering plan \
  --project ./proj/remix_project.json \
  --target anime-club-demo \
  --chain utility,eq8,compressor,limiter
uv run ableton-cli --output json remix mastering apply \
  --project ./proj/remix_project.json \
  --dry-run
uv run ableton-cli --output json remix mastering apply \
  --project ./proj/remix_project.json \
  --yes
```

Export planning should preserve the rights boundary in the target name:

```bash
uv run ableton-cli --output json remix export-plan \
  --project ./proj/remix_project.json \
  --target /abs/out/song_private_test_remix.wav
```

## References in This Skill

- `examples/anime_club_private_test.md`: private-test club remix walkthrough.
- `examples/anime_dnb_private_test.md`: private-test drum and bass remix walkthrough.
- `examples/arrangement_forms.json`: anime-club, anime-dnb, and anime-future-bass form defaults.
- `examples/vocal_chop_recipe.json`: example chop-grid and trigger intent.
- `templates/remix_project_schema_notes.md`: manifest fields to inspect and keep current.
- `templates/section_map_template.md`: manual section-map worksheet.
- `templates/qa_checklist.md`: final QA and export-readiness checklist.
