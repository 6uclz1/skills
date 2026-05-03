# Sound Design Intent

Use this reference to describe sounds by role, behavior, and search intent. Do not name fixed presets as if they exist in the user's Ableton catalog.

## Contract

- Search query values are broad intent, such as `Drum Rack dry electronic kit` or `Operator bass`.
- Always avoid preset names, local paths, pack-specific paths, rack names presented as resolved choices, and fake URIs.
- State what the sound must do musically before suggesting any browser query.
- Let `$ableton-cli` browser search resolve exact paths or URIs from the active catalog.

## Drums

- Role intent: transient structure, groove identity, section contrast.
- Search query examples: `Drum Rack`, `dry electronic kit`, `909 kit`, `breakbeat kit`.
- Shape intent: kick decay, clap/snare length, hat brightness, velocity range, swing.
- Handoff note: exact rack or kit must come from active browser search results.

## Bass

- Role intent: low-end identity, root clarity, kick relationship.
- Search query examples: `Operator bass`, `Drift bass`, `Analog bass`, `Wavetable bass`, `808 bass`.
- Shape intent: mono low end, envelope decay, filter cutoff, saturation, sidechain space.
- Handoff note: define whether bass avoids, doubles, or answers kick hits.

## Chords

- Role intent: harmonic color, midground motion, emotional frame.
- Search query examples: `Wavetable pad`, `Analog keys`, `Electric keys`, `Chord stab`.
- Shape intent: attack, release, filter, voice count, chorus or width.
- Handoff note: keep low chord tones sparse because bass owns root weight.

## Lead

- Role intent: foreground motif, call-and-response, peak identity.
- Search query examples: `Wavetable lead`, `Analog lead`, `Pluck`, `Mono lead`, `Vocal chop`.
- Shape intent: portamento, filter envelope, delay send, octave, modulation.
- Handoff note: motif should be short enough to vary by rhythm or final note.

## Texture/FX

- Role intent: transition markers, background motion, width, scene contrast.
- Search query examples: `Noise`, `Atmosphere`, `Field recording`, `Riser`, `Impact`, `Reverb`.
- Shape intent: filtering, volume automation, reverb time, sidechain movement.
- Handoff note: texture should clarify arrangement changes, not hide weak writing.
