# Anime Club Private Test Example

Use this example for a private, non-public anime-club remix sketch from user-provided local files.

## Assumptions

- Rights status: `private_test`
- Source: `/abs/source/opening_theme_private_test.wav`
- Vocal stem: `/abs/stems/opening_theme_vocal_private_test.wav`
- Instrumental stem: `/abs/stems/opening_theme_instrumental_private_test.wav`
- Source policy: preserve the full mix as the main continuous track.
- Verified harmony: record section-level chord notes before adding bass, pads, or supersaws.
- Target style: `anime-club`
- Target BPM: `140`
- Target key: `A minor`
- Export target: `/abs/out/opening_theme_private_test_anime_club_remix.wav`

## Command Flow

```bash
uv run ableton-cli --timeout-ms 15000 --output json wait-ready
uv run ableton-cli --timeout-ms 15000 --output json doctor
uv run ableton-cli --timeout-ms 15000 --output json ping
uv run ableton-cli --timeout-ms 15000 --output json song info
uv run ableton-cli --timeout-ms 15000 --output json tracks list

uv run ableton-cli --output json remix init \
  --source /abs/source/opening_theme_private_test.wav \
  --project ./opening_theme_club_proj \
  --rights-status private_test

uv run ableton-cli --output json audio asset add \
  --project ./opening_theme_club_proj/remix_project.json \
  --role full_mix \
  --path /abs/source/opening_theme_private_test.wav

uv run ableton-cli --output json audio asset add \
  --project ./opening_theme_club_proj/remix_project.json \
  --role vocal \
  --path /abs/stems/opening_theme_vocal_private_test.wav

uv run ableton-cli --output json audio asset add \
  --project ./opening_theme_club_proj/remix_project.json \
  --role instrumental \
  --path /abs/stems/opening_theme_instrumental_private_test.wav

uv run ableton-cli --output json audio analyze \
  --project ./opening_theme_club_proj/remix_project.json

uv run ableton-cli --output json audio sections import \
  --project ./opening_theme_club_proj/remix_project.json \
  --sections "intro:1-8,verse:9-24,pre:25-32,chorus:33-48,breakdown:49-64,final_chorus:65-80,outro:81-88"

uv run ableton-cli --output json remix set-target \
  --project ./opening_theme_club_proj/remix_project.json \
  --bpm 140 \
  --key "A minor"

uv run ableton-cli --output json remix plan \
  --project ./opening_theme_club_proj/remix_project.json \
  --style anime-club \
  --dynamics section-profiles

uv run ableton-cli --output json remix apply \
  --project ./opening_theme_club_proj/remix_project.json \
  --dry-run

uv run ableton-cli --output json remix apply \
  --project ./opening_theme_club_proj/remix_project.json \
  --yes

uv run ableton-cli --output json remix vocal-chop \
  --project ./opening_theme_club_proj/remix_project.json \
  --source vocal \
  --section chorus \
  --slice 1/8 \
  --create-trigger

uv run ableton-cli --output json remix qa \
  --project ./opening_theme_club_proj/remix_project.json \
  --include-mastering \
  --render ./renders/opening_theme_private_test_anime_club_remix.wav

uv run ableton-cli --output json remix export-plan \
  --project ./opening_theme_club_proj/remix_project.json \
  --target /abs/out/opening_theme_private_test_anime_club_remix.wav
```

## Arrangement Intent

- intro: energy 2, drum_policy `light`; DJ-safe light groove, filtered hook texture, no full vocal reveal.
- verse_chop: energy 2, drum_policy `off_or_light`; short call-and-response edits from the verse tail.
- build: energy 3, drum_policy `build_only`; snare roll, riser, filtered instrumental, one vocal pickup, no full groove.
- chorus_drop: energy 4, drum_policy `full`; four-on-floor kick, sidechain bass, supersaw hook, vocal chop.
- breakdown: energy 1, drum_policy `off`; no added drums, foreground the original melody or pad texture.
- final_drop: energy 5, drum_policy `full_with_variation`; full-density chorus with added ad-libs or chop variation.
- outro: energy 2, drum_policy `reduced`; reduced drums and bass for private practice mixing.

## Dry-run Inspection

- Confirm every generated section profile has `energy`, `drum_policy`, and layer policies where applicable.
- Confirm full mix remains one continuous source track or every edit has documented source offsets.
- Confirm `breakdown` creates no added drum clips because its `drum_policy` is `off`.
- Confirm `chorus_drop` uses `full` drums and `final_drop` uses `full_with_variation`.
- Confirm added bass, pads, supersaws, and chop triggers follow the verified chord map.
- Confirm each dry-run step has `section` and `role`.
- Confirm no destructive operations are present before running `remix apply --yes`.
