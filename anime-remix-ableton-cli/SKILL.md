---
name: anime-remix-ableton-cli
description: Create private-use anime song remix arrangements in Ableton Live using ableton-cli. Use for manifest-first remix planning, stem registration, section mapping, anime-club/anime-dnb/anime-future-bass arrangement, vocal chops, mix setup, mastering QA, and export planning.
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

Register stems by role. Typical roles are `vocal`, `instrumental`, `drums`, `bass`, `reference`, and `full_mix`.

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

### 3. Import Section Map

Prefer a manually checked section map over guessed structure. Use bar ranges and anime-song labels such as `intro`, `verse`, `pre`, `chorus`, `bridge`, `final_chorus`, and `outro`.

```bash
uv run ableton-cli --output json audio sections import \
  --project ./proj/remix_project.json \
  --sections "intro:1-8,verse:9-24,pre:25-32,chorus:33-48,bridge:49-64,final_chorus:65-80,outro:81-88"
```

Use `templates/section_map_template.md` when the user has only timestamps, lyrics cues, or rough section names.

### 4. Set Target

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

### 5. Plan Arrangement

```bash
uv run ableton-cli --output json remix plan \
  --project ./proj/remix_project.json \
  --style anime-dnb
```

Read `examples/arrangement_forms.json` when choosing a form or adapting the section sequence.

### 6. Dry Run, Inspect, Apply

```bash
uv run ableton-cli --output json remix apply \
  --project ./proj/remix_project.json \
  --dry-run
```

Inspect the returned batch steps, target tracks, clip placements, tempo/key changes, and any destructive operations. Only then apply:

```bash
uv run ableton-cli --output json remix apply \
  --project ./proj/remix_project.json \
  --yes
```

### 7. Vocal Chop

Use vocal chops as private production practice unless the source is cleared or original.

```bash
uv run ableton-cli --output json remix vocal-chop \
  --project ./proj/remix_project.json \
  --source vocal \
  --section chorus \
  --slice 1/8 \
  --create-trigger
```

Read `examples/vocal_chop_recipe.json` when a user asks for chop timing, trigger mapping, or motif intent.

### 8. QA

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
