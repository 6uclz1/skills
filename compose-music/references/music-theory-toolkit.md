# Music Theory Toolkit

Use theory to make decisions faster. Do not over-explain theory unless the user asks for teaching.

## Table of Contents

- Pitch palettes
- Diatonic chords
- Roman numerals
- Voicing and inversion
- Seventh chords and extensions
- Bass and harmony
- Advanced color

## Pitch Palettes

Default palette choices:

- `minor`: reliable for dark, direct electronic music.
- `dorian`: minor feel with more lift.
- `aeolian`: natural minor, stable and familiar.
- `phrygian`: dark, close semitone pull.
- `mixolydian`: groove-oriented major with a flat seventh.
- `pentatonic`: simple, hook-friendly, avoids half-step clashes.
- `whole tone`: floating and unresolved.
- `octatonic`: tense, symmetrical, cinematic or techno-friendly.

State the tonic and the scale degrees available. If using outside notes, name their job: passing tone, borrowed color, leading tone, chromatic approach, or tension note.

## Diatonic Chords

Build diatonic triads by stacking scale tones in thirds. In major:

```text
I major | ii minor | iii minor | IV major | V major | vi minor | vii diminished
```

In natural minor:

```text
i minor | ii diminished | III major | iv minor | v minor | VI major | VII major
```

For electronic music, repeated two-chord and four-chord loops often work better than long functional progressions.

## Roman Numerals

Always include roman numerals when giving a chord progression. They make transposition and Ableton implementation safer.

Examples:

- `I-V-vi-IV`: broad pop lift.
- `i-VI-III-VII`: minor anthem loop.
- `i-iv-v`: darker minor loop.
- `i-bVII-bVI-bVII`: modal descent and return.
- `i-IV`: dorian vamp when the raised sixth is present.

For modal loops, avoid strong dominant resolution unless the user wants tonal pull.

## Melody Motifs

Describe motifs as a small contract instead of a loose sentence:

- `rhythm_cell`: the repeatable rhythm, such as `eighth, eighth-rest, sixteenth pickup`.
- `pitch_cell`: the scale degrees or named pitches that define identity.
- `variation_strategy`: one controlled edit, such as final-note change, octave answer, rhythmic displacement, call-and-response, or subtraction.

Keep the first motif short enough to repeat, then vary one property at a time.

## Voicing and Inversion

Use inversions to smooth movement between chords. Choose voicing based on track role:

- Pad: wider spacing, shared tones, slow movement.
- Stab: compact voicing, rhythmic placement, clear attack.
- Pluck: fewer notes, avoid muddy low thirds.
- Lead harmony: upper triads, sevenths, and suspensions.

Keep low chord tones sparse. Put bass roots below the chord track instead of duplicating full chords in the low register.

## Seventh Chords and Extensions

Use seventh chords when the track needs depth, softness, or jazz/R&B color:

- `maj7`: smooth, bright, suspended.
- `min7`: deep, stable, house-friendly.
- `dom7`: forward motion or blues/funk color.
- `m7b5`: unstable, useful as a passing chord.

Add ninths or suspensions only after the triad/seventh function is clear.

## Bass and Harmony

Bass decides perceived harmony more strongly than upper voicings. For slash chords and inversions, be explicit:

```text
C/E = C major with E in the bass
Am/G = A minor with G in the bass
```

Use non-root bass notes for transitions, not as the default. If the mix is dense, prefer root and octave patterns.

For harmony maps, name:

- `tension_bar`: where the progression, voicing, or outside note increases pressure.
- `resolution_bar`: where the loop lands or releases.
- `outside_notes`: non-diatonic notes with their job, such as borrowed color, chromatic approach, or passing tone.

For basslines, state `kick_relationship` as `avoid`, `double`, `answer`, or `intentional_overlap`.

## Advanced Color

Use these only when they solve a musical problem:

- Borrowed chord: one chord from parallel major/minor for contrast.
- Secondary dominant: brief dominant pull into a target chord.
- Pedal: hold tonic or dominant in bass while upper chords move.
- Planing: move a voicing shape in parallel for color over function.
- Chromatic approach: one-step motion into a target pitch.

When in doubt, simplify the harmony and make rhythm, register, and arrangement do more work.
