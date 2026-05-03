# Anime Club Private Test Example

Use this example for a private, non-public anime-club remix sketch from user-provided local files.

## Assumptions

- Rights status: `private_test`
- Source: `/abs/source/opening_theme_private_test.wav`
- Vocal stem: `/abs/stems/opening_theme_vocal_private_test.wav`
- Instrumental stem: `/abs/stems/opening_theme_instrumental_private_test.wav`
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
  --role vocal \
  --path /abs/stems/opening_theme_vocal_private_test.wav

uv run ableton-cli --output json audio asset add \
  --project ./opening_theme_club_proj/remix_project.json \
  --role instrumental \
  --path /abs/stems/opening_theme_instrumental_private_test.wav

uv run ableton-cli --output json audio sections import \
  --project ./opening_theme_club_proj/remix_project.json \
  --sections "intro:1-8,verse:9-24,pre:25-32,chorus:33-48,breakdown:49-64,final_chorus:65-80,outro:81-88"

uv run ableton-cli --output json remix set-target \
  --project ./opening_theme_club_proj/remix_project.json \
  --bpm 140 \
  --key "A minor"

uv run ableton-cli --output json remix plan \
  --project ./opening_theme_club_proj/remix_project.json \
  --style anime-club

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

- Intro: DJ-safe drums, filtered hook texture, no full vocal reveal.
- Verse chop: short call-and-response edits from the verse tail.
- Build: snare roll, riser, filtered instrumental, one vocal pickup.
- Chorus drop: four-on-floor kick, sidechain bass, supersaw hook, vocal chop.
- Breakdown: reduce drums and foreground the original melody.
- Final drop: full-density chorus with added ad-libs or chop variation.
- Outro: drums and bass only for private practice mixing.
