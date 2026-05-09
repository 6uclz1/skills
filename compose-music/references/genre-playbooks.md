# Genre Playbooks

Use these defaults when the user names a genre or omits one. Adapt them to the user's constraints instead of treating them as fixed templates.

## Constraint Set Fields

For every genre below, translate the prose into these output constraints when the request is more than a narrow pattern:

- `must_have`: the few traits that make the genre recognizable.
- `should_have`: useful supporting traits that can be dropped for constraints.
- `avoid`: failure modes to actively prevent.
- `default_density_curve`: the expected density motion across the requested length.
- `typical_clip_lengths`: common loop lengths for drums, bass, harmony, lead, and texture.

When emitting `composition_spec`, summarize the chosen traits in optional `brief.genre_traits`.

## Alias Triggers

- Drum and Bass: `DnB`, `dnb`, `drum & bass`, `jungle`.
- Garage: `ukg`, `UKG`, `2-step`, `two-step`, `future garage`.
- Breakbeat: `breaks`, `nu skool breaks`.
- Acid House: `acid`, `acid techno` when the 303-style line is dominant.
- Minimal Techno: `minimal`.
- Electro: `electro funk`, `machine funk`.
- Synthwave: `retrowave`.
- Downtempo: use Ambient, Lo-fi, or Hip-Hop constraints based on drums and tempo.

## Hybrid Conflict Rules

- Garage drum and bass: keep DnB tempo and break/drop energy; borrow garage swing, shuffled hats, and bouncy bass phrasing.
- Ambient techno: keep techno pulse if present, lower rhythm density, and let texture/FX carry identity.
- Acid techno: use techno tempo and section pressure; make the acid line the hook and keep harmony sparse.
- Breaks house: keep house tempo and harmonic warmth; use breakbeat drum identity instead of straight kick/clap as the main carrier.
- Downtempo garage: keep garage swing and vocal/chord chop identity; lower tempo and reduce kick density.
- Cut-up garage: keep the garage drum swing and bass bounce; make the sliced sample the identity carrier and leave one-beat dropouts before hook returns.

## Default Constraint Matrix

| Genre | must_have | should_have | default_density_curve | typical_clip_lengths |
| --- | --- | --- | --- | --- |
| House | four-on-floor kick, clap/backbeat, bass gaps | seventh color, open-hat lift | 1-2-3-4-1-4-1 | drums 1-2, bass 2-4, chords 4-8 |
| Techno | kick weight, hat motion, restrained harmony | rumble/sub answer, one identity cell | 1-2-3-4-1-4/5-1 | drums 1-2, bass 1-4, stabs 2-4 |
| Melodic Techno | minor/dorian loop, controlled drums, delayed motif | long pad, pluck variation | 1-2-3-4-1-5-1 | drums 2, bass 4, chords 8, lead 4 |
| Trance | driving kick, offbeat/rolling bass, long tension | suspended chords, lead reveal | 1-2-3-4-1-3-5-1 | drums 2, bass 2-4, chords 8, lead 8 |
| Drum and Bass | 160-176 BPM, break/two-step drums, sub/reese | sparse pads, clear drop entry | 1-2-3-4-1-4-1 | drums 2-4, bass 4, atmosphere 8 |
| Garage | swing, shuffled hats, syncopated bass | vocal chop or organ stab | 1-2-3-4-2-4-1 | drums 1-2, bass 2-4, chords 4 |
| Hip-Hop | pocket, swing, vocal space | 808 or root bass, sample-like loop | 1-3-2-4-2-4 | drums 2-4, bass 4, sample 4-8 |
| Ambient | texture identity, slow harmonic motion, density by register | beatless or sparse pulse | 0-1-2-3-1 | pad 8-16, texture 8-16, pulse 4-8 |
| Cut-up / Sample Chop | recognizable slice motif, stable pulse, negative space | 8-16 primary slices, stutter at boundaries | 1-2-3-4-2-5-1 | drums 1-2, cutup 1-2, bass 2-4 |

## House

- Tempo: 120-126 BPM
- Meter: 4/4
- Drum identity: steady kick, clap on 2 and 4, open hat lift, light percussion
- Bass: offbeat or syncopated root/octave pulse with kick-aware gaps
- Harmony: minor, dorian, or major seventh color; 2-4 chord loops
- Melody: short hook, vocal-like stab, or sampled phrase
- Arrangement: 8-bar intro, 8 groove, 8 build, 16 hook, 8 break, 8 hook variation, 8 outro
- Avoid: overcrowding the midrange before the groove is stable

## Techno

- Tempo: 128-138 BPM
- Meter: 4/4
- Drum identity: kick weight, hat motion, restrained clap or rim
- Bass: sub pulse, rumble, or short answer to kick
- Harmony: minimal; use modal pedal tones, one-chord pressure, or sparse stabs
- Melody: motif can be rhythmic noise, filtered stab, or short pitch cell
- Arrangement: additive 8-bar blocks, breakdowns shorter than hooks
- Avoid: too many chord changes unless the user asks for melodic techno

## Melodic Techno

- Tempo: 120-128 BPM
- Meter: 4/4
- Drum identity: steady kick, restrained hats, controlled percussion
- Bass: root/octave pulse, sidechain-aware gaps
- Harmony: minor or dorian, 2-4 chord loop, long voicings
- Melody: short motif with filter or automation variation
- Arrangement: 8 intro, 8 build, 16 hook, 8 break, 16 variation, 8 outro
- Avoid: over-dense supersaw stacks unless requested

## Trance

- Tempo: 132-140 BPM
- Meter: 4/4
- Drum identity: driving kick, offbeat bass, open hats, snare rolls at transitions
- Bass: offbeat octave pulse or rolling sixteenths
- Harmony: minor anthem, suspended chords, longer build tension
- Melody: clear lead motif, call and response, peak octave lift
- Arrangement: intro, groove, long build, breakdown, drop, variation, outro
- Avoid: adding the full lead before the breakdown earns it

## Drum and Bass

- Alias triggers: `DnB`, `dnb`, `jungle`, `drum & bass`
- Tempo: 160-176 BPM
- Meter: 4/4
- Drum identity: breakbeat or two-step kick/snare with ghost notes
- Bass: sub phrase, reese, or call-and-response low line
- Harmony: sparse pads, modal stabs, or minor seventh color
- Melody: short atmospheric motif or vocal chop; leave room for drums
- Arrangement: 16-bar phrases, frequent fills, clear drop entry
- Avoid: sustained low notes masking kick and snare movement

## Garage

- Tempo: 128-138 BPM
- Meter: 4/4 with swing
- Drum identity: shuffled hats, syncopated kick, snare or clap on backbeat variants
- Bass: syncopated, bouncy, often answers the vocal or chord stab
- Harmony: minor, dorian, or soulful seventh chords
- Melody: vocal chop, organ stab, or short pluck response
- Arrangement: 8-bar phrase variation with fills and dropouts
- Avoid: straight quantized hats unless intentionally hybridized

## Hip-Hop

- Tempo: 70-100 BPM or double-time feel
- Meter: 4/4
- Drum identity: kick/snare pocket, swing, ghost hats
- Bass: root support, 808 slide, or sparse sub punctuation
- Harmony: loop-first; minor, pentatonic, jazz color, or sample-like voicing
- Melody: memorable 2-4 bar motif with space for vocal
- Arrangement: hook/verse contrast through subtraction and drum density
- Avoid: busy lead writing that would fight the topline

## Synthwave

- Tempo: 80-115 BPM
- Meter: 4/4
- Drum identity: punchy kick, big snare, gated or roomy ambience
- Bass: octave pulse, arpeggiated root movement, or pedal tone
- Harmony: minor anthem, borrowed major color, lush triads or sevenths
- Melody: simple heroic motif, octave lead, or arpeggio
- Arrangement: 8 intro, 8 verse, 8 build, 16 hook, 8 bridge, 16 hook/outro
- Avoid: making every synth wide and bright at once

## Ambient

- Tempo: 60-100 BPM or beatless
- Meter: 4/4 if grid-based
- Drum identity: optional; use texture, pulse, or sparse transient events
- Bass: drone, pedal, or slow root motion
- Harmony: slow modal shifts, suspended voicings, planing, or static color
- Melody: minimal motif, long notes, generative variation
- Arrangement: density and register changes matter more than drops
- Avoid: too many events that break the intended stillness

## Acid House

- Tempo: 120-128 BPM
- Meter: 4/4
- Drum identity: steady house kick, clap on 2 and 4, hats that leave room for the acid line
- Bass: resonant 303-style pattern with slides, accents, and short rests around the kick
- Harmony: one tonal center or two-chord vamp; tension comes from filter movement, not reharmonization
- Melody: the bassline is usually the hook; add sparse stabs only if they answer it
- Arrangement: 8-bar filter openings, mutes, and accent variations
- Avoid: writing pad-heavy progressions that bury the acid identity

## Electro

- Tempo: 120-135 BPM
- Meter: 4/4 with broken kick placement
- Drum identity: syncopated machine funk, snappy snare/clap, short metallic percussion
- Bass: angular octave jumps, syncopated root movement, or vocoder-like answer phrases
- Harmony: sparse minor, chromatic passing tones, or single-chord pressure
- Melody: robotic lead cell, call-and-response bleeps, or short arpeggio
- Arrangement: emphasize drum/bass edits and 4-bar fills over long breakdowns
- Avoid: default four-on-the-floor unless the user asks for electro-house

## UK Bass

- Tempo: 128-140 BPM
- Meter: 4/4 with syncopated pressure
- Drum identity: broken kicks, sharp claps, shuffled hats, percussion gaps
- Bass: weighty sub phrase with mid-bass answer; leave silence as part of the groove
- Harmony: minimal stabs, minor/dorian color, or sampled chord hits
- Melody: short vocal chop, stab, or percussive synth response
- Arrangement: quick 8-bar switches, dropouts, and bass sound swaps
- Avoid: straight house hat patterns without syncopated low-end movement

## Future Garage

- Tempo: 128-138 BPM
- Meter: 4/4 with swing and implied half-time emotion
- Drum identity: shuffled hats, rim/snare ghosts, off-grid percussion, soft transients
- Bass: warm sub notes that answer vocal chops and leave kick holes
- Harmony: minor seventh, suspended, or bittersweet borrowed color
- Melody: chopped vocal, bell motif, or fragile pluck with space
- Arrangement: texture-led builds, vocal fragment reveals, and sparse drops
- Avoid: overly bright EDM leads or perfectly straight quantization

## Cut-up / Sample Chop

- Alias triggers: `cut-up`, `cutup`, `sample chop`, `vocal chop`, `chopped sample`, `glitch collage`, `break edit`
- Tempo: 90-100 BPM for hip-hop or lo-fi cut-up, 125-140 BPM for breakbeat/garage/club cut-up, 160-176 BPM for jungle/DnB cut-up
- Meter: 4/4
- Must have: recognizable slice motif, stable drum or pulse anchor, clear negative space, one source-identity reveal, one heavily resequenced section
- Should have: 8-16 primary slices, 1-bar identity phrase, 2-bar variation, boundary stutter/repeat, pitch/gate/filter/reverse/delay-throw variation
- Bass: answer the kick and sample gaps; avoid low-mid masking under the sample body
- Arrangement: reveal the source, resequence it, then alternate dense edits with silence or simplified motifs
- Avoid: uncontrolled randomization, too many unrelated samples, continuous slicing without a motif, hard-coded local sample paths, or fake Ableton browser URIs

## Vocal Chop

- Tempo: follows the target genre; 128-138 BPM for garage or future garage, 160-176 BPM for DnB
- Must have: vowel/consonant identity, short gated motifs, silence before hook returns
- Should have: 3-5 slice motif, one pitch-up response slice, delay throws only at phrase boundaries
- Avoid: full lyric phrases when rights or source intent are unclear

## Glitch Cut-up

- Tempo: 90-150 BPM depending on feel
- Must have: one stable anchor under the edits, controlled repeat/stutter grammar, resets after surprise events
- Should have: 1/32 repeats, reverses at boundaries, occasional triplet fragments
- Avoid: edits that sound random before a motif is established

## Break Cut-up

- Tempo: 125-140 BPM for breaks, 160-176 BPM for jungle/DnB
- Must have: break transient identity, strong snare anchor, bar-end rearrangement
- Should have: ghost slices, crash/tail slices as transition material, bass gaps around kick/snare impacts
- Avoid: slicing the break so densely that the groove loses its backbeat

## Cut-up Garage

- Tempo: 128-138 BPM
- Must have: shuffled hats, syncopated kick, vocal or melodic chop identity, bouncy bass answers
- Should have: swung trigger feel, final-beat motif variation, one-beat sample mute before the main return
- Avoid: straight quantized vocal chops that fight the garage pocket

## Cut-up DnB

- Tempo: 160-176 BPM
- Must have: break or two-step drum anchor, sub/reese space, sliced vocal or break identity, clear drop entry
- Should have: 2-bar chop phrase, bar-end 1/16 or 1/32 repeats, one source reveal before or after the drop
- Avoid: sustained bass under every kick and dense chop run

## Lo-fi

- Tempo: 65-90 BPM
- Meter: 4/4
- Drum identity: swung kick/snare pocket, soft hats, vinyl/noise transient glue
- Bass: simple root support, occasional walk-up, short enough to keep drums breathing
- Harmony: jazz color, seventh/ninth voicings, borrowed chords, or sample-like loops
- Melody: dusty keys, guitar-like phrase, or small pentatonic motif
- Arrangement: 8/16-bar loops with subtle mutes, filter changes, and texture variation
- Avoid: too many pristine high-frequency layers

## Trap

- Tempo: 130-160 BPM with half-time feel
- Meter: 4/4
- Drum identity: half-time snare/clap, rolling hats, triplet fills, sparse kick anchors
- Bass: 808 root line with slides, pitch drops, and kick-aware starts
- Harmony: minor, phrygian, harmonic minor, or dark two-chord vamp
- Melody: bell, flute, pluck, or vocal-like minor hook
- Arrangement: hook/verse contrast through drum density and 808 variation
- Avoid: bass notes sustaining through every kick unless the smear is intentional

## IDM

- Tempo: 90-150 BPM depending on feel
- Meter: 4/4 with polymetric or irregular surface rhythm
- Drum identity: edited breaks, displaced accents, micro-fills, glitch percussion
- Bass: concise motif, odd-length loop, or sub punctuation that stabilizes the edits
- Harmony: modal, chromatic, planed chords, or sparse tonal anchors
- Melody: fragmented motif, generative variation, or timbral counterpoint
- Arrangement: controlled surprise; repeat enough for identity before each disruption
- Avoid: random edits without a recognizable carrier motif

## Dub Techno

- Tempo: 118-128 BPM
- Meter: 4/4
- Drum identity: deep kick, soft clap/rim, steady hats, restrained percussion
- Bass: short sub pulse or low chord root that supports long echoes
- Harmony: minor chord stabs, suspended color, tape-like repeats
- Melody: chord echo and filter movement carry the hook
- Arrangement: slow density shifts, send/return gestures, 8-bar mute cycles
- Avoid: busy lead melodies that fight the dub space

## Breakbeat

- Tempo: 125-140 BPM
- Meter: 4/4
- Drum identity: chopped break, syncopated kick/snare, ghost hits, crash or ride punctuation
- Bass: rolling sub or Reese phrase that locks to break accents
- Harmony: sparse stabs, rave chords, or minor pedal
- Melody: short sample, hoover stab, or rhythmic synth phrase
- Arrangement: 8/16-bar break edits, fills, and drop entries
- Avoid: reducing the groove to straight kick/clap house

## Minimal Techno

- Tempo: 124-132 BPM
- Meter: 4/4
- Drum identity: small number of precise drum voices, clicky percussion, evolving hat detail
- Bass: short pulse, tuned percussion, or quiet sub answer
- Harmony: almost none; use one pitch cell or occasional stab
- Melody: micro motif, texture, or automation pattern
- Arrangement: tiny 4/8-bar changes with strong subtraction discipline
- Avoid: adding chords to solve energy problems too early

## Progressive House

- Tempo: 120-126 BPM
- Meter: 4/4
- Drum identity: smooth kick/clap foundation, open hat lift, percussion that grows in layers
- Bass: rolling or offbeat pattern that supports long harmonic arcs
- Harmony: 4-8 chord progression, suspensions, inversions, emotional resolution
- Melody: delayed lead motif, pluck arpeggio, or vocal-like hook
- Arrangement: long builds, 16/32-bar arcs, clear breakdown-to-drop payoff
- Avoid: revealing every hook layer in the first 8 bars

## Output Examples

- Acid House: `I | bVII` vamp, one 2-bar acid bassline, 8-bar filter-open arrangement moves.
- Electro: broken kick/snare grid, angular bass answer, no straight four-on-the-floor unless requested.
- Future Garage: swung hats, vocal chop motif, sub gaps around kick, minor seventh harmony.
- IDM: identity carrier first, then controlled polymeter or glitch edits with reset bars.
- Progressive House: longer chord loop and delayed hook reveal, not a techno one-chord loop.
