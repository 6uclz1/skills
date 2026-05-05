# Anime DnB Private Test Example

Use this example for a private, non-public anime drum and bass remix sketch from user-provided local files.

## Assumptions

- Rights status: `private_test`
- Source: `/abs/source/ending_theme_private_test.wav`
- Vocal stem: `/abs/stems/ending_theme_vocal_private_test.wav`
- Instrumental stem: `/abs/stems/ending_theme_instrumental_private_test.wav`
- Source policy: preserve the full mix as the main continuous track.
- Verified harmony: `F minor: Fm, Db, Ab, Eb` through the drop sections.
- Target style: `anime-dnb`
- Target BPM: `174`
- Target key: `F minor`
- Export target: `/abs/out/ending_theme_private_test_anime_dnb_remix.wav`

## Command Flow

```bash
uv run ableton-cli --timeout-ms 15000 --output json wait-ready
uv run ableton-cli --timeout-ms 15000 --output json doctor
uv run ableton-cli --timeout-ms 15000 --output json ping
uv run ableton-cli --timeout-ms 15000 --output json song info
uv run ableton-cli --timeout-ms 15000 --output json tracks list

uv run ableton-cli --output json remix init \
  --source /abs/source/ending_theme_private_test.wav \
  --project ./ending_theme_dnb_proj \
  --rights-status private_test

uv run ableton-cli --output json audio asset add \
  --project ./ending_theme_dnb_proj/remix_project.json \
  --role full_mix \
  --path /abs/source/ending_theme_private_test.wav

uv run ableton-cli --output json audio asset add \
  --project ./ending_theme_dnb_proj/remix_project.json \
  --role vocal \
  --path /abs/stems/ending_theme_vocal_private_test.wav

uv run ableton-cli --output json audio asset add \
  --project ./ending_theme_dnb_proj/remix_project.json \
  --role instrumental \
  --path /abs/stems/ending_theme_instrumental_private_test.wav

uv run ableton-cli --output json audio analyze \
  --project ./ending_theme_dnb_proj/remix_project.json

uv run ableton-cli --output json audio sections import \
  --project ./ending_theme_dnb_proj/remix_project.json \
  --sections "intro:1-16,pre_drop_vocal:17-32,drop:33-64,bridge:65-80,second_drop:81-112,outro:113-128"

uv run ableton-cli --output json remix set-target \
  --project ./ending_theme_dnb_proj/remix_project.json \
  --bpm 174 \
  --key "F minor"

uv run ableton-cli --output json remix plan \
  --project ./ending_theme_dnb_proj/remix_project.json \
  --style anime-dnb \
  --dynamics section-profiles

uv run ableton-cli --output json remix apply \
  --project ./ending_theme_dnb_proj/remix_project.json \
  --dry-run

uv run ableton-cli --output json remix apply \
  --project ./ending_theme_dnb_proj/remix_project.json \
  --yes

uv run ableton-cli --output json remix vocal-chop \
  --project ./ending_theme_dnb_proj/remix_project.json \
  --source vocal \
  --section pre_drop_vocal \
  --slice 1/8 \
  --create-trigger

uv run ableton-cli --output json remix qa \
  --project ./ending_theme_dnb_proj/remix_project.json \
  --include-mastering \
  --render ./renders/ending_theme_private_test_anime_dnb_remix.wav

uv run ableton-cli --output json remix export-plan \
  --project ./ending_theme_dnb_proj/remix_project.json \
  --target /abs/out/ending_theme_private_test_anime_dnb_remix.wav
```

## Arrangement Intent

- intro: energy 2, drum_policy `filtered_break`; atmospheric pads, filtered breakbeat teaser, short vocal cue.
- pre_drop_vocal: energy 2, drum_policy `off`; preserve the strongest melodic phrase before the drop, allowing only pickup or riser.
- drop: energy 4, drum_policy `full`; breakbeat, reese or sub bass, chop response, impact on bar starts.
- bridge: energy 1, drum_policy `off`; no added drums, use pads or source-only contrast before the second drop.
- second_drop: energy 5, drum_policy `full_with_variation`; variation in bass rhythm and chop order, not only more layers.
- outro: energy 2, drum_policy `reduced`; private-practice DJ exit with reduced breakbeat and bass.

## Dry-run Inspection

- Confirm every generated section profile has `energy`, `drum_policy`, and layer policies where applicable.
- Confirm full mix remains one continuous source track or every edit has documented source offsets.
- Confirm `bridge` creates no added drum clips because its `drum_policy` is `off`.
- Confirm `drop` uses `full` drums and `second_drop` uses `full_with_variation`.
- Confirm drop bass follows the verified Fm, Db, Ab, Eb progression.
- Confirm each dry-run step has `section` and `role`.
- Confirm no destructive operations are present before running `remix apply --yes`.
