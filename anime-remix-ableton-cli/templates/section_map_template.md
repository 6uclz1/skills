# Section Map Template

Use this worksheet before running `audio sections import`.

## Source Notes

- Source file:
- Rights status: `private_test`
- Original BPM:
- Target BPM:
- Original key:
- Target key:
- Downbeat note:
- Pickup or count-in:

## Section Map

| Section | Bars | Timecode | Musical cue | Remix role |
| --- | --- | --- | --- | --- |
| intro | 1-8 | 00:00-00:15 | | DJ intro or texture setup |
| verse | 9-24 | | | vocal or chop source |
| pre | 25-32 | | | build tension |
| chorus | 33-48 | | | hook or drop source |
| bridge | 49-64 | | | breakdown or contrast |
| final_chorus | 65-80 | | | final drop |
| outro | 81-88 | | | private-practice exit |

## Import Command

```bash
uv run ableton-cli --output json audio sections import \
  --project ./proj/remix_project.json \
  --sections "intro:1-8,verse:9-24,pre:25-32,chorus:33-48,bridge:49-64,final_chorus:65-80,outro:81-88"
```

## Checks

- Bar ranges are inclusive and do not overlap.
- Chorus or hook section is identified.
- Build section has enough length for risers or snare movement.
- Vocal chop source section is marked.
- Any pickup before bar 1 is noted separately.
