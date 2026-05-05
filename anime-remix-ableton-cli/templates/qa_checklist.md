# QA Checklist

Use this checklist after `remix qa` and before export planning.

## Rights and Scope

- [ ] `rights_status` is recorded in `remix_project.json`.
- [ ] Export filename includes rights status, for example `_private_test_`.
- [ ] Output is not described as publishable, distributable, cleared, or licensed unless the user explicitly confirmed clearance.
- [ ] No command downloaded copyrighted material or bypassed copy protection.

## Manifest and Assets

- [ ] Source path is absolute and exists.
- [ ] Registered stems exist and roles are correct.
- [ ] Full mix is registered as `full_mix` or `reference`, not silently reused as `vocal`.
- [ ] BPM, key, and downbeat are present or marked as unknown.
- [ ] Section map is ordered, non-overlapping, and musically plausible.
- [ ] Section-level chord progression or harmonic notes are recorded before writing harmonic MIDI.
- [ ] Target BPM, key, and style are present.

## Arrangement

- [ ] `remix plan` completed with `ok: true`.
- [ ] `remix apply --dry-run` was inspected before `--yes`.
- [ ] Main full mix is preserved as one continuous source track unless a reconstructed edit was explicitly requested.
- [ ] Dry-run does not repeat the same full mix from the beginning across multiple section clips.
- [ ] Any full-mix edit has source offset, warp marker, or documented musical rationale.
- [ ] Added bass, chords, pads, supersaws, and chop triggers follow the verified chord map.
- [ ] No unexpected destructive operations appeared in dry-run steps.
- [ ] Chops are created on separate tracks and do not destructively alter the main full-mix track.
- [ ] Hook/drop sections contain the intended vocal, chop, or lead identity.
- [ ] Transitions have pickups, fills, risers, or contrast where needed.

## Arrangement Dynamics

- [ ] `remix plan --dynamics section-profiles` was used or equivalent section profiles were recorded in the manifest.
- [ ] Every section has an energy value or an intentional fallback.
- [ ] Bridge, interlude, and breakdown sections do not contain full drum grooves.
- [ ] Drum-off sections have no `drums` layer steps in the dry-run plan.
- [ ] Build sections use only build elements such as risers, snare rolls, impacts, or filtered percussion.
- [ ] Drop, chorus_drop, final_drop, and second_drop restore full rhythmic density.
- [ ] At least one clear contrast section exists before the final drop.
- [ ] If only full_mix or drum-baked instrumental assets are available, the plan warns that drums cannot be guaranteed off.

## Mix and Mastering

- [ ] Kick and bass do not mask each other.
- [ ] Vocal or vocal chop is audible in hook sections.
- [ ] Master channel has headroom before limiting.
- [ ] True peak target is no higher than `-1.0 dBTP` for private demo renders.
- [ ] Mastering apply was dry-run before `--yes`.

## Export Readiness

- [ ] `remix qa --include-mastering` completed.
- [ ] Render path exists or export plan names the intended target.
- [ ] Export target is local and private-use named.
- [ ] Any warnings are either fixed or explicitly accepted.
