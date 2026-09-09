# Phonetics reel, panel format

Reels 1–3 (Aug–Sep 2026): a raw pronunciation-practice recording, cleaned (silences and
flubbed takes cut out), every word subtitled with its IPA and a letter grade, and a live
spectrogram / F1-F2 / pitch panel running along the bottom. Vowel targets from
**Hillenbrand et al. (1995)**, American English.

Worked example with every decision and number: the STRUT /ʌ/ video, which opens with a
deliberately wrong "culture", then the American and British versions, then 21 more /ʌ/
words with five UK/US minimal pairs: [strut-reel-2026-09-01.md](strut-reel-2026-09-01.md).

## Outputs

1. `phonetics-final.mp4`: the cleaned video with per-word subtitles at the top (word,
   take number, /IPA/ with the studied vowel bold and coloured) and the frequency panel
   at the bottom (wideband spectrogram with measured F1/F2 dots and per-word target
   bands, pitch strip with a live F0 readout, a moving playhead). Full-bleed 1080x1920.
2. `vowel_space.png`: F1×F2 chart of every take, kept and removed, against the
   reference means ±1 SD, plus an ending-F3 "R test" subplot when UK/US pairs are present.
3. The Instagram caption: hook on the mistake, one line on what the video is, one line
   of academic backing, a colour legend, a question to drive comments.

## Pipeline

```bash
# 0. analysis audio (44.1 kHz mono for Praat)
ffmpeg -y -i in.mp4 -vn -acodec pcm_s16le -ar 44100 -ac 1 clip_audio_44k.wav
# 1. transcribe (words + probabilities; CPU whisper is slow, run it detached)
python tools/scripts/transcribe_audio.py clip_audio_44k.wav segments.json
# 2. find the REAL acoustic take boundaries (never cut on whisper timestamps)
python tools/scripts/find_speech_runs.py clip_audio_44k.wav 50 0.10 0.12
# 3. hand-write final_takes.json: map each run to {word, take, t0, t1}, dropping bad takes
# 4. cut + measure + remap the timeline in ONE ffmpeg pass (writes cuts.json)
python tools/scripts/build_clean_cut.py in.mp4 clip_audio_44k.wav final_takes.json master_clean.mp4 cuts.json
# 5. subtitles on the 1080x1920 Reels canvas, and the panel frames (progressive reveal)
ffmpeg -y -i master_clean.mp4 -vn -acodec pcm_s16le -ar 44100 -ac 1 clean_audio.wav
python tools/scripts/build_phonetics_ass.py cuts.json phonetics.ass 1080 1920
python tools/scripts/render_freq_panel.py clean_audio.wav cuts.json panels 876 370 30
# 6. compose full-bleed (video fills the frame, overlays on top) and verify the decode
python tools/scripts/compose_reels.py master_clean.mp4 panels phonetics.ass phonetics-final.mp4 cuts.json
ffmpeg -v error -i phonetics-final.mp4 -f null -
# 7. vowel-space chart, removed takes drawn as x-marks
python tools/scripts/render_vowel_chart.py cuts.json removed_takes.json references/hillenbrand1995-means.csv vowel_space.png
```

| script | does |
|---|---|
| `transcribe_audio.py` | faster-whisper (small, int8) → segments with per-word probabilities |
| `find_speech_runs.py` | intensity runs above a dB threshold, with voiced fraction and median F0/F1/F2 per run: the take boundaries |
| `build_clean_cut.py` | single-pass `trim/atrim + concat` cut, measures each take's nucleus (median F1/F2 over voiced frames within 15 dB of the peak), writes the exact timeline to `cuts.json` |
| `build_phonetics_ass.py` | word + IPA + grade subtitles (libass), one per padded segment; IPA from `eng_to_ipa` with a manual overrides dict |
| `render_freq_panel.py` | per-frame PNGs: wideband spectrogram, F1/F2 dots, target bands, pitch strip, one window per word |
| `compose_reels.py` | overlays subtitles, panel and meaning emoji on the Reels canvas (`fullbleed` default, `boxed` kept) |
| `render_vowel_chart.py` | F1×F2 chart vs the reference means ±1 SD, `adjustText` labels, the "R test" subplot |
| `vowel_map.py` | word→vowel, word→IPA, word→emoji, the reference targets, the match % and the A+…F grade bands |
| `hillenbrand_means.py`, `deterding_means.py` | rebuild the reference CSVs from the raw data |

## How the grading works

- **Measurement.** Median F1/F2 over the vowel nucleus, defined as the voiced frames
  within 15 dB of the word's peak intensity. Praat Burg via parselmouth, 10 ms step,
  formant ceiling 5000 Hz for a male voice (5500 for female), pitch floor 75 Hz.
- **Match %.** A Mahalanobis distance over (F1, F2) in reference SDs, mapped through a
  Gaussian with a 2-SD tolerance. The strict 1-SD percentile flattens to 0 % past 2 SD
  and the feedback ordering disappears; the Michigan reference dialect already sits
  2–3 SD off modern General American.
- **Letter grades.** The same distance mapped to A+…F (A+ ≤ 1 SD … F > 4 SD). Every
  reference vowel in the word gets a grade, stacked: the studied vowel big on top, then
  rows for the others. Unstressed schwa has no reference and no grade.
- **UK/US endings** are graded one-dimensionally on the ending's F3, because the tail
  F1/F2 frames are too weak to trust. Men's /ɝ/ F3 is 1711 ± 108 Hz vs ≈ 2548 ± 142 for a
  plain vowel (computed from the raw Hillenbrand data, column 6, zeros excluded), so
  ending F3 below ~2000 Hz means r-coloured.
- **Dark /l/** drags F2 down ~400 Hz: /ʌl/, /ʊl/, /uːl/ words are graded on F1 only with
  the tolerance doubled, and the footnote says so.
- **Deciding which takes are bad** combines whisper's word probability (below 0.1 is a
  genuine flub), formant distance from the target in SDs, and a reading of the F1/F2
  pattern (F2 collapsed toward 1590 means the vowel backed to /ɑ/, "hat" → "hot").
  Removed takes are reported with reasons and charted as ×-marks. A take that is
  acoustically fine but whose word is ambiguous is removed and flagged, never guessed.

## Layout rules

- Full-bleed 1080x1920: the talking video fills the frame, overlays go on top. The panel
  background alpha stays around 200 so the video shows through.
- The panel is a progressive reveal: spectrogram, formant dots and pitch curve appear at
  the playhead as they are uttered; the static chrome (grids, target bands, labels) shows
  from the start.
- **One spectrogram per word.** A full-timeline strip squeezes each word into ~30 px.
  Windows tile the timeline; words merged into one padded segment get the window split
  at word midpoints in `cuts.json`.
- Each word gets a meaning emoji (Twemoji PNG, 128 px right slot) because the audience
  includes non-English speakers. Variant takes get a second PNG in the left slot (UK/US
  flag, or ❌ for the deliberate mistake). Overlay PNGs; do not rely on libass colour-emoji
  rendering on Windows.
- The studied vowel gets its own colour in the IPA line on top of bold; a highlight on
  the ending must never be the only colour.
- Type sizes ended at word ~96 px, IPA ~72 px, emoji 128 px; err large.
- The American take plays before the British one. Rows in `final_takes.json` are simply
  reordered; the cutter only merges forward-overlapping pads, so an out-of-source-order
  pair never merges wrongly.

## Rules learned the hard way

- **Find the real focus before building anything.** Grade the vowel every word shares,
  not the feature that happens to be visually obvious (an R-ending). Getting this
  backwards cost a full rebuild.
- **Verify accent labels acoustically, never from memory.** Which take was UK and which
  US was decided by the ending F3, and one "-ary" pair turned out to be neither and was
  removed.
- **Whisper hallucinates on trailing silence.** A polite outro appeared over 2 s of
  quiet. Signature: many words with collapsed zero-width timestamps. Re-transcribe the
  slice in isolation with VAD off and cross-check `silencedetect`.
- **Whisper word timestamps are loose. Never cut or measure on them.** Midpoints land
  inside silence, two takes merge into one word, quiet takes get skipped. Derive spans
  from intensity runs and assign words to runs; the per-run formant medians also expose
  mislabelled takes.
- **Never concatenate per-segment AAC files.** Each decode loses a ~23 ms priming frame;
  ten segments drift 0.2 s. Cut everything in one filter pass so the timeline in
  `cuts.json` is exact and the cleaned video never needs re-transcribing.
- **Probe the master, not the source, for width and height.** ffmpeg auto-rotates phone
  video in the filter chain, so the master comes out true-portrait with no rotation tag.
  `PlayResX/Y` in the ASS header and the panel geometry come from the master.
- **Every `-loop 1` still input needs `-t <duration>`** and the output keeps `-shortest`,
  or the filtergraph never ends. This burned minutes of CPU on a 7 s video.
- The panel PNG sequence is rendered at the master's constant frame rate (30) with its
  time axis spanning the master's audio duration; `overlay=...:eof_action=repeat` absorbs
  a ±1 frame count mismatch.
- Segoe UI has no ✗ glyph; use ×.
