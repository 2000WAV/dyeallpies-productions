# Reshoot spec — b-frame and h-frame word sets

## Why (and what NOT to redo)

The p-frame (`12-words-c.MOV`) is **good and ships as-is**. Don't re-record it.

Its audio was measured before recommending anything: **31-33 dB SNR across the whole
formant region** (0.3-5 kHz), no clipping, peaks -9 to -16 dBFS, normal speech spectral
tilt. That is more than Praat needs. A closer mic would gain little. The only weak band
is 80-300 Hz at 22.6 dB SNR — outdoor rumble, which touches F0 tracking but not F1/F2.

**Do not re-record audio separately over the existing video.** The mouth on screen is
making the original words; in the b/h frames those words were wrong, so dubbing correct
audio onto them would visibly break lip sync. Video and audio together, or not at all.

The real defect is **word order**. In `10-words-a` and `11-words-b`, only 3 of 9 words
match their intended vowel; from the third word on, every label lands on a neighbouring
vowel, and each set has a duplicate or a gap. See NOTES.md.

## What to record

Two clips, each 9 words, **video and audio together**, same setup as before.

Use the **/hVd/ frame** for one of them — that is exactly Deterding's and Hawkins &
Midgley's elicitation context, so the comparison stops needing a consonant-context
caveat:

| # | h-frame | b-frame | vowel |
|---|---|---|---|
| 1 | head    | bed     | /ɛ/  |
| 2 | had     | bad     | /æ/  |
| 3 | hard    | bard    | /ɑː/ |
| 4 | hod     | bod     | /ɒ/  |
| 5 | hud     | bud     | /ʌ/  |
| 6 | heard   | bird    | /ɜː/ |
| 7 | hoard   | bored   | /ɔː/ |
| 8 | hood    | book    | /ʊ/  |
| 9 | who'd   | boot    | /uː/ |

## How to record it so the analysis can't go wrong

1. **Keep the list visible while recording** and follow it in order. This is the one
   thing that failed last time — nothing else.
2. **Say each word 3 times**, then **pause ~3 s** before moving to the next word. The
   grouping code splits on gaps > 1.5 s, so keep repetitions under ~1.2 s apart and
   word boundaries clearly over 2 s.
3. **Say nothing else.** No "okay", no counting, no restarts mid-list — a stray sound
   becomes a phantom take.
4. If you fluff a word, **pause, then redo the whole 3-rep block**. Extra blocks are
   fine (extras get culled); a half-block is what creates ambiguity.
5. Natural citation pace. Takes came out 0.24-0.48 s last time, which fits inside the
   545.75 ms beat with room. Don't slow down for the camera.
6. Changing angle per word is good — keep doing it, it gives the cut its rhythm.
7. Same distance and setting as before is fine. If it's easy, record somewhere less
   windy to clean up the 80-300 Hz band, but this is optional.

## After recording

Drop the files in `originals/`. Verification is one command and takes seconds:

```
.venv-subtitles/Scripts/python.exe tools/scripts/find_speech_runs.py <wav> 50 0.10 0.12
```

Expect **27 runs in 9 groups**, and each group's median F1/F2 to sit nearest its
intended vowel in `references/deterding1997-means.csv`. If a group's nearest match is a
neighbouring vowel, the order slipped again — recheck before building.
