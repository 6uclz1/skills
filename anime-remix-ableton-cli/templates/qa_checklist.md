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
- [ ] BPM, key, and downbeat are present or marked as unknown.
- [ ] Section map is ordered, non-overlapping, and musically plausible.
- [ ] Target BPM, key, and style are present.

## Arrangement

- [ ] `remix plan` completed with `ok: true`.
- [ ] `remix apply --dry-run` was inspected before `--yes`.
- [ ] No unexpected destructive operations appeared in dry-run steps.
- [ ] Hook/drop sections contain the intended vocal, chop, or lead identity.
- [ ] Transitions have pickups, fills, risers, or contrast where needed.

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
