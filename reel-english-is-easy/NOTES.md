# "English is easy" reel — source notes (2026-09-04)

## Files

**Masters = `originals/` (iPhone HEVC, 1920x1080 + rotation=90 -> native 1080x1920,
30 fps CFR).** Delivered as `Videos-20260904T175823Z-1-001.zip` on 2026-09-04; these
replace the WhatsApp copies entirely (those were 576x1024 / 31.58 fps and are no longer
used — the WhatsApp files themselves remain untouched in the project root).

| file | dur | role |
|---|---|---|
| `originals/01-lookup.MOV`       | 3.4 s  | looking up-left at text — TITLE CARD shot |
| `originals/02-walk.MOV`         | 10.4 s | walking, camera low — the left/right sway section |
| `originals/03-invite.MOV`       | 2.4 s  | inviting gesture at front door — "let me show you" |
| `originals/04-doubt.MOV`        | 6.0 s  | still, skeptical — "should I really show you?" |
| `originals/05-filler.MOV`       | 3.0 s  | thinking, looking up — "ok I'll show you" |
| `originals/06-stare-short.MOV`  | 4.3 s  | NEW — deadpan stare at door, reaction B-roll |
| `originals/07-stare-long.MOV`   | 13.3 s | NEW — deadpan stare, many angle changes |
| `originals/10-words-a.MOV`      | 46.0 s | b-frame word set |
| `originals/11-words-b.MOV`      | 51.4 s | h-frame word set |
| `originals/12-words-c.MOV`      | 63.8 s | p-frame word set — THE ONE WE USE |

## Technical facts

- Masters are **exactly the Reels canvas** (1080x1920) — no upscale, no fps conversion.
- The five acting clips are effectively **silent** (mean -40 to -69 dB, no dialogue) —
  all mimed. Their audio is discardable; the song carries them.
- libass on this box has **harfbuzz + fribidi**: Arabic shaping/RTL, Devanagari
  conjuncts, Turkish dotted-I and the full IPA set all render clean (verified).
  Fonts: `Segoe UI` (Latin/Arabic/IPA), `Nirmala UI` (Devanagari).

## Word sets — measured medians (parselmouth, 5000 Hz ceiling, men)

Target list is **RP/British**: /ɛ æ ɑː ɒ ʌ ɜː ɔː ʊ uː/, 9 monophthongs, one consonant
frame per video. Dennis said extra repetitions were deliberate — pick the best take.

### 12-words-c (p-frame) — 27 runs, 9 groups, 3 takes each. CLEAN, USE THIS ONE.

| word | IPA | F1 | F2 | verdict |
|---|---|---|---|---|
| pet  | /pɛt/  | 581 | 1705 | ✓ |
| pat  | /pæt/  | 824 | 1520 | ✓ strongest low-front token in the whole shoot |
| part | /pɑːt/ | 729 | 1027 | ✓ |
| pot  | /pɒt/  | 576 |  832 | ✓ |
| putt | /pʌt/  | 644 | 1158 | ✓ |
| pert | /pɜːt/ | 698 | 1394 | central ✓ but **open** — came out [ɐː] not [ɜː] |
| port | /pɔːt/ | 432 |  697 | ✓ |
| pull | /pʊl/  | 449 |  719 | ✓ |
| pool | /puːl/ | 352 | 1382 | ✓ but strongly **fronted** — RP GOOSE-fronting [ʉː] |

### 10-words-a (b-frame) — 18 runs, 9 groups, but LABELS DON'T ALIGN

From group 3 on the formants match the *next* vowel along: "bard" measures 548/904
(= /ɒ/ pot), "bod" 617/1142 (= /ʌ/ putt), "bud" 576/1384 (= /ɜː/ pert), "bird"
405/648 (= /ʊ/ pull). **No /ɑː/ token appears.** One take is also corrupt on the WhatsApp copy only; on the master "bad" reads 738/1552, so the
audio is fine — the WORD ORDER is what is off. Not used.

### 11-words-b (h-frame) — 16 runs, only 8 groups for 9 words

One word missing outright; "hot" measures 628/1270 (too front for /ɒ/) and "hurt"
412/714 (too close/back for /ɜː/). Same shift problem. Needs re-check.

### Two things to resolve at build time

1. **F0 looks doubled in b/c.** Memory has Dennis at 85-95 Hz; `10-words-a` medians
   are 89-105 Hz (right), but `12-words-c` runs 99-164 Hz. Suspect octave errors on
   breathy tokens — re-track with a tighter ceiling before drawing any pitch strip.
2. **Hillenbrand is American.** 7 of the 9 vowels map fine (ɛ æ ɑ ʌ ɔ ʊ u), but
   **/ɒ/ has no American counterpart** and **/ɜː/ only exists there as r-coloured
   /ɝ/** — grading Dennis's non-rhotic /ɜː/ against /ɝ/ would fail it on F3 for a
   dialect difference, not an error. Needs an RP reference or an explicit caveat.

## Song reference — beat grid, SUPERSEDED phone capture (see next section)

Source: `WhatsApp Ptt 2026-09-04 at 15.12.45.ogg` (mono Opus 19 kbps, 114 s). A phone
capture of the track, held locally as a **timing reference only** — gitignored, never
redistributed, deleted once the cut is locked. Analysed by
`tools/scripts/beat_grid.py` (spectral-flux onset envelope -> autocorrelation tempo ->
comb-filter phase fit). Low bitrate is fine: percussive onsets survive it.

- **Recording lead-in: song starts at ~1.0 s** (silence to 0.5 s, handling click 0.55 s).
- **Tempo 109.78 BPM** — beat 546.6 ms, bar (4/4) 2.186 s, **first beat at 1.281 s**.
  Tempo was contested: autocorrelation offered 55/110/220 and 74/148 families. A
  comb-filter test (how much onset energy a grid actually catches) picked 110 in every
  20 s window, 3.0-4.7x versus 1.3-2.3x for 147.66. Not a half-time guess.
- **Two structural transitions, both marked by the bass**, both on exact downbeats:

  | | bar | time | kick energy | onset energy |
  |---|---|---|---|---|
  | transition 1 | 12 | **27.52 s** | 0.65 -> **0.84** | 0.23 -> 0.63 |
  | break | 27 | 60.31 s | 0.32 -> 0.66 | 0.60 -> 0.39 |
  | transition 2 | 28 | **62.49 s** | -> **0.87** (track max) | 0.39 -> 0.67 |

  These are the two slots the user identified by ear ("27 secs and 1:02"). Confirmed
  independently here by low-band (<200 Hz) energy — the "slight bass after those
  timestamps" is the kick re-entering.
- Room in each slot: transition 1 runs 8 bars (32 beats, 17.5 s) before the next big
  change at bar 20 / 45.0 s; transition 2 runs 4-5 bars (16-20 beats, 8.7-10.9 s)
  before bar 32 / 71.2 s. At one word per beat, 9 words = 4.9 s; at one per two beats,
  9.8 s. **So the song affords exactly two nine-word slots, not three.**

## Can the b- and h-frames be recovered? No.

Each group's median formants were matched to the nearest RP vowel (Deterding men's
citation values, normalised by 120 Hz F1 / 220 Hz F2):

- **p-frame: 7 of 9 words have their intended vowel as the nearest match.** The two
  that don't are precisely the two already identified as real pronunciation findings
  (`pert` too open, `pull` dark-L). The set is internally consistent.
- **b-frame: only 3 of 9 match** (`bed`, `bad`, `book`). From `bard` onward every label
  lands on a neighbouring vowel — `bard`->/ɒ/, `bud`->/ɜː/, `bird`->/ɔː/, `bored`->/ʊ/ —
  and `book`/`bored` both measure /ʊ/, so there is a duplicate as well as a gap.
- **h-frame: 3 of 9 match** (`head`, `had`, `hard`), only 8 groups for 9 words, and the
  last three are mutually ambiguous between /uː/, /ɜː/ and /ʊ/.

The b/h errors are *wrong-word* errors, not pronunciation errors, and cannot be
resolved from acoustics alone without guessing word identity — which the skill
explicitly forbids. **Both sets are unusable. Only the p-frame ships.**

## Song reference — CLEAN grid (2026-09-04, use this one)

Source: a 129 kbps AAC rip of the official video, `work/song_full.mp3`, 113.55 s.
Supersedes the phone capture above (which had a 1.0 s lead-in and a noisier envelope);
the two agree on tempo to within 0.16 BPM, so the phone analysis was sound — this is
just tighter. Same handling: **timing reference only, gitignored, deleted once the cut
is locked.** `*.mp3` added to .gitignore alongside `*.ogg`/`*.opus`/`*.m4a`.

- **109.94 BPM** — beat **545.75 ms**, bar (4/4) **2.1830 s**.
- **First beat at 0.002 s**: the track starts exactly on a downbeat, so bar N begins at
  `N * 2.1830 s` with no offset to carry around.
- Comb score 3.62x (vs 2.7x on the phone capture) — the grid is well locked.

### THREE bass drops, not two

Structural novelty across onset / low-band (<200 Hz) / mid-band energy. The three big
kick entries share an identical signature (low-band jumping to ~0.96):

| slot | bar | time | kick before -> after | room until next change |
|---|---|---|---|---|
| **1** | 12 | **26.20 s** | 0.35 -> **0.97** | 12 bars / 26.2 s (to bar 24) |
| **2** | 28 | **61.13 s** | 0.43 -> **0.96** | 7-8 bars / 15.3 s (to bar 35) |
| **3** | 40 | **87.32 s** | 0.33 -> **0.96** | 8 bars / 17.5 s (to bar 48) |

Outro at bar 48 / 104.79 s (kick 0.99 -> 0.07).

The user identified slots 1 and 2 by ear ("27 secs and 1:02" — the grid says 26.20 and
61.13). **Slot 3 at 87.32 s was not spotted by ear but has the same signature**, so the
song affords three nine-word slots, each with room for 9 words at one word per beat
(4.91 s) or even at two beats per word (9.82 s).

**But the footage still only affords one trustworthy word set** (p-frame). So three
slots do not mean three consonant frames — see the recommendation in PLAN.md.

## Take selection — the 9 that ship

Chosen from the 27 p-frame takes: longest allowed 0.50 s (leaving headroom inside the
545.75 ms beat), then max voiced fraction, then peak dB. Formants re-measured on the
CHOSEN take (not the group median), nucleus = voiced frames within 15 dB of the take's
peak. Graded against Deterding men's citation values with the SD floor; `pull`/`pool`
graded on F1 only at 2x tolerance per the dark-L rule. Saved to
`work/selected_takes.json`.

| word | IPA | take | t0 (s) | dur | F1 | F2 | dist | grade |
|---|---|---|---|---|---|---|---|---|
| pet  | /pɛt/  | 2 |  4.43 | 0.370 | 562 | 1692 | 0.48 | A+ |
| pat  | /pæt/  | 3 | 10.39 | 0.410 | 757 | 1530 | 0.18 | A+ |
| part | /pɑːt/ | 3 | 15.24 | 0.460 | 726 | 1013 | 0.98 | A+ |
| pot  | /pɒt/  | 3 | 20.51 | 0.240 | 565 |  832 | 0.66 | A+ |
| putt | /pʌt/  | 1 | 28.55 | 0.350 | 652 | 1162 | 1.01 | A  |
| pert | /pɜːt/ | 2 | 39.97 | 0.410 | 740 | 1370 | **5.68** | **F** |
| port | /pɔːt/ | 2 | 48.35 | 0.480 | 437 |  667 | 0.49 | A+ |
| pull | /pʊl/  | 1 | 55.74 | 0.340 | 408 |  678 | 0.08 | A+ |
| pool | /puːl/ | 1 | 60.52 | 0.400 | 382 | 1771 | 1.00 | A+ |

**All nine fit inside one beat** — longest 0.480 s vs 545.75 ms. Mean 0.384 s.

Notes:
- `pull` at 0.08 is the single most accurate vowel in the set.
- `pert` is *worse* on the chosen take than on the group median (5.68 vs 4.65 SD), and
  it is F1 alone — F2 1370 against a reference 1377. One fault, cleanly isolated.
- `pool` F2 1771 on this take (group median 1382) is extreme GOOSE-fronting. It does
  not affect the grade (dark-L rule grades F1 only) but is worth a caption line.

## Word identity — RESOLVED by transcribing each group in isolation (2026-09-04)

The earlier verdict ("b- and h-frames are unusable, labels shifted") was **wrong in
method**: it inferred word identity from nearest-vowel matching, which cannot tell a
mislabelled word from a mispronounced one. Transcribing each group as its own audio
file settles it, and the formants then agree with every label.

- **b-frame**: bed, bad, bod, bud, bird, bored, book, **book**, boot — "book" was said
  twice and **"bard" was never said**. Not a shift: 8 good words plus a duplicate.
- **h-frame**: head, had, **hot**, hut, hurt, hoard, hood, who'd — **"hard" was never
  said** (re-recorded separately afterwards as `originals/13-hard.mp4`).
- **p-frame**: all 9 confirmed.

`hot` is the interesting one. The speaker confirmed saying it, but it measures
F1 693 / F2 1171 against an /ɒ/ target of 593 / 866 — that is /ɑː/ territory, 4.23 SD
out. So it is a genuine production error (said "hot", produced something nearer
"hart"), not a labelling problem. Graded F, and kept: the reel's whole argument is that
nobody's pronunciation is perfect.

**Lesson for the skill: identify the word before grading the vowel.** ASR on an
isolated group answers "which word is this"; formants answer "how well was it said".
Using formants for both conflates the two questions and produced a confident wrong
answer that nearly threw away two thirds of the usable footage.

### F0 anomaly resolved
The outdoor sets measured F0 118-165 Hz, well above this speaker's 85-95 Hz profile.
The indoor `13-hard.mp4` reads **87-91 Hz**, matching the profile exactly. So the
outdoor figures were inflated (octave errors on a poor 80-300 Hz SNR of 22.6 dB), not a
real register change. Do not draw a pitch strip from the outdoor takes without
re-tracking.

## Final grade distribution (26 words)

A+ 9 · A 10 · B 3 · D 1 · E 1 · F 2

The four faults: `pert` /ɜː/ F (5.68 SD), `hot` /ɒ/ F (4.23), `hurt` /ɜː/ E (3.35),
`boot` /uː/ D (2.96). NURSE is the weak spot — but `bird` scored A, so it is
word-specific, not vowel-wide. `boot`'s fronting is the documented young-RP GOOSE shift
rather than an error.

Three takes have no version that fits inside one beat (`bored` 0.570 s, `hurt` 0.550 s,
`who'd` 0.620 s vs a 0.546 s beat); they lose 25-75 ms of final consonant release.

## Three alignment/level bugs found and fixed (2026-09-04, late)

1. **Caption drift — a word ahead by the end.** One beat is 545.75 ms = **16.3725 frames**
   at 30 fps. The build let ffmpeg's `fps` filter round each word segment up to 17 frames
   and silence-pad the audio to match, while the subtitles were timed from exact beat
   arithmetic. Result: every word landed 20.9 ms later than its caption, accumulating to
   **+523 ms by word 26** — the caption for the NEXT word showed while the previous one
   was still being spoken, and the last word lost its caption entirely.
   **Fix:** the whole timeline is built in WHOLE FRAMES (`build_cut.py`), and the text and
   panel layers read those frame numbers instead of recomputing from the beat.
2. **Panel layer 5 frames early.** The panel PNG sequence was rendered only for the word
   range and time-shifted into place with `setpts`. The shift landed ~5 frames early, so
   captions showed one word while the pictures showed the next (`BOOT` with `head`'s
   emoji). Masked at the start because the first word's slot is wide enough to hide it.
   **Fix:** render a panel for EVERY frame of the video, transparent outside the word
   section, and composite at offset 0. No alignment left to get wrong.
3. **Audio clipping across three exports.** `alimiter` has **auto-level on by default**,
   which normalises the output straight back to full scale — so `limit=0.72` was being
   undone every time and true peak sat at +0.4 dBFS. **Fix:** `level=disabled`.
   Now -14.5 LUFS at -1.9 dBTP, verified with `astats` as well as `ebur128`.

Lesson for the skill: when a beat is not a whole number of frames, quantise the timeline
ONCE and let every layer derive from it. Two layers computing "the same" times
independently will disagree, and the disagreement grows.

## Truncated finals fixed by mid-vowel splicing

Nine takes were longer than one beat, so their final consonant was being cut off
("bored", "who'd"). Rather than dropping them, `build_cut.py` removes a slice from the
MIDDLE OF THE VOWEL and rounds that slice to a whole number of pitch periods (from the
take's measured F0) so the waveform stays in phase across the join and does not click.
Removed: part 16 ms, port 8, bad 64, bird 65, bored 94, hurt 74, hoard 58, hood 98,
who'd 149.

## Final layout (2026-09-04)

Walking section simplified to ONE sentence per half, shown in all five languages at
once and held for the whole half so it can be read: "if English is so easy, why do so
many mispronounce it?" then "what if I told you there is a science for pronunciation?"
(EN / PT / TR / AR / FA). The earlier version cycled four different claims and was
unreadable at that pace.

Word section, top to bottom: grade (deliberately above the Instagram safe line -- the
user accepted that), word flanked by two DIFFERENT meaning emoji, IPA with the studied
vowel in blue, the ridgeline graph, then the F1/F2 readout below the graph baseline.

### Showing WHERE the vowel is on the graph

The panel used to show a spectrum without saying which part of it was the vowel being
graded. Two additions fix that:

- **Nucleus highlight.** Ridges inside the vowel nucleus are drawn bright and thick;
  consonant ridges drop to ~20% visibility. The nucleus is defined exactly as the
  measurement uses it -- frames within 15 dB of the word's peak intensity -- so the
  highlight marks precisely the frames that produced the grade. It is recomputed from
  the FINAL audio, so mid-vowel splices are accounted for automatically.
- **Formant markers.** On each highlighted ridge, `peak_bin()` finds the actual spectral
  peak nearest F1 and F2 and dots it (blue / amber). Watching the dots climb the stack
  shows which "mountain" is which formant.
- **Shine.** The near ridges glow while the vowel is being hit, easing out over 160 ms.
  First attempt haloed all 34 stacked slices and the accumulated alpha turned the whole
  panel into grey fog -- restricted to depth > 0.5 and much lower alpha.

## Word corrections (speaker, 2026-09-04 final pass)

- b-frame word 4 is **"but"** /bʌt/, not "bud".
- h-frame word 2 is **"hat"** /hæt/, not "had".

Whisper transcribed both correctly ("But. But. But." / "Hat. Hat.") and I overrode it
with the word list supplied at the start of the session. **The ASR was right twice and
the assumed list was wrong twice.** Trust the transcription of the isolated group over
the intended word list; the speaker does not always say what the list says.

Neither correction changes a vowel (/ʌ/ and /æ/ are unchanged), so no grade moved. The
IPA, both meaning emoji and the consonant-frame label all changed. That label is now
DERIVED from the IPA (first + last phoneme) rather than fixed per group, so "hat" reads
h _ t and "pull" reads p _ l, which a fixed per-group label got wrong.
