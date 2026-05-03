# Anime DnB Private Test Example

Use this example for a private, non-public anime drum and bass remix sketch from user-provided local files.

## Assumptions

- Rights status: `private_test`
- Source: `/abs/source/ending_theme_private_test.wav`
- Vocal stem: `/abs/stems/ending_theme_vocal_private_test.wav`
- Instrumental stem: `/abs/stems/ending_theme_instrumental_private_test.wav`
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
  --role vocal \
  --path /abs/stems/ending_theme_vocal_private_test.wav

uv run ableton-cli --output json audio asset add \
  --project ./ending_theme_dnb_proj/remix_project.json \
  --role instrumental \
  --path /abs/stems/ending_theme_instrumental_private_test.wav

uv run ableton-cli --output json audio sections import \
  --project ./ending_theme_dnb_proj/remix_project.json \
  --sections "intro:1-16,pre_drop_vocal:17-32,drop:33-64,bridge:65-80,second_drop:81-112,outro:113-128"

uv run ableton-cli --output json remix set-target \
  --project ./ending_theme_dnb_proj/remix_project.json \
  --bpm 174 \
  --key "F minor"

uv run ableton-cli --output json remix plan \
  --project ./ending_theme_dnb_proj/remix_project.json \
  --style anime-dnb

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

- Intro: atmospheric pads, filtered breakbeat, short vocal teaser.
- Pre-drop vocal: preserve the strongest melodic phrase before the drop.
- Drop: breakbeat, reese or sub bass, chop response, impact on bar starts.
- Bridge: half-time drums or pad-only reset.
- Second drop: variation in bass rhythm and chop order, not only more layers.
- Outro: private-practice DJ exit with drums and reduced bass.
