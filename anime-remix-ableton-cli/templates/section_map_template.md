# Section Map Template

Use this worksheet before running `audio sections import` and `remix plan --dynamics section-profiles`.

## Source Notes

- Source file:
- Rights status: `private_test`
- Original BPM:
- Target BPM:
- Original key:
- Target key:
- Downbeat note:
- Pickup or count-in:
- Source treatment: preserve full mix / reconstructed edit / stem-only
- Harmonic analysis source: CLI / external tool / manual listening / user notes

## Section Map

| Section | Bars | Timecode | Musical cue | Chord progression | Source treatment | Remix role | Energy | Drum policy | Notes |
| --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- |
| intro | 1-8 | 00:00-00:15 | | | preserve full mix | texture setup | 2 | light | DJ intro or texture setup |
| verse | 9-24 | | | | preserve full mix | vocal source | 2 | off_or_light | vocal or chop source |
| pre | 25-32 | | | | preserve full mix + build layers | build tension | 3 | build_only | tension ramp |
| chorus | 33-48 | | | | preserve full mix + drop layers | hook/drop | 4 | full | hook or drop source |
| bridge | 49-64 | | | | preserve full mix | contrast/reset | 1 | off | no drums |
| final_chorus | 65-80 | | | | preserve full mix + final layers | final drop | 5 | full_with_variation | final drop |
| outro | 81-88 | | | | preserve full mix or drums-only tail | exit | 2 | reduced | private-practice exit |

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
- Chord progression is known for any section that receives bass, chord, pad, supersaw, or chop-trigger MIDI.
- Source treatment says whether the original full mix is preserved or intentionally edited.
- Vocal chop source section is marked.
- Vocal chop target is a separate track.
- Full-mix clips are not repeated from the beginning as a substitute for real section placement.
- Energy is an integer from `0` to `5`.
- Drum policy is one of `off`, `off_or_light`, `light`, `filtered_break`, `build_only`, `reduced`, `full`, or `full_with_variation`.
- `off` drum policy sections are reset sections and do not add drum clips.
- Any pickup before bar 1 is noted separately.
