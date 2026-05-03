# Remix Project Schema Notes

Use these notes when inspecting or updating `remix_project.json`. The manifest is the source of truth before any Ableton Live mutation.

## Required Fields to Check

- `source`: absolute path to the user-provided local source file.
- `project_dir`: directory that owns reports, renders, and intermediate files.
- `rights_status`: one of `private_test`, `cleared`, or `original`.
- `assets`: registered local files with role, path, and optional analysis notes.
- `analysis`: BPM, key, downbeat, beat grid, loudness, and reference notes when available.
- `sections`: ordered section names with bar or time ranges.
- `target`: remix BPM, key, style, and optional reference intent.
- `arrangement_plan`: generated plan to inspect before apply.
- `apply_history`: dry-run and apply command summaries.
- `qa`: pass/fail notes, warnings, render path, mastering checks, and export readiness.

## Rights Status Values

- `private_test`: private listening, private production practice, or household-only verification.
- `cleared`: material has user-confirmed rights clearance outside this skill.
- `original`: source and generated material are user-created original material.

This skill does not grant permissions. Do not convert `private_test` to `cleared` without an explicit user statement.

## Manifest Review Before Apply

- Source and assets exist locally.
- Stem roles are correct and not swapped.
- BPM/key/downbeat are checked against the source.
- Sections are ordered and bar ranges do not overlap.
- Target style matches one of the supported arrangement forms.
- Export filename includes rights status.
- Dry-run steps contain no unexpected destructive operations.
