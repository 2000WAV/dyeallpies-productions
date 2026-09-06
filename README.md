# phonetics-reels

How I make my pronunciation-analysis Instagram Reels: record myself saying a word list,
measure every vowel with Praat, grade it against a published formant reference, and burn
the measurements into the video. Two formats so far:

1. **The panel format** (reels 1–3, Aug–Sep 2026). The raw practice recording is cleaned
   (silences and flubbed takes cut out), every word gets a subtitle with its IPA and a
   letter grade, and a live spectrogram / F1-F2 / pitch panel runs along the bottom.
   Vowel targets from **Hillenbrand et al. (1995)**, American English.
   Worked example with every decision and number: [docs/strut-reel-2026-09-01.md](docs/strut-reel-2026-09-01.md).
2. **The beat-synced "trend" format** (reel 4, "English is easy", Sep 2026). The same
   measurement machinery cut to a song's beat grid, acting shots up front, one word per
   beat at the drop, and a "waterfall" ridgeline spectrum instead of a heatmap. Graded
   against **Deterding (1997)**, RP / British English.
   Build notes: [reel-english-is-easy/NOTES.md](reel-english-is-easy/NOTES.md),
   plan: [PLAN.md](reel-english-is-easy/PLAN.md), caption: [CAPTION.md](reel-english-is-easy/CAPTION.md).

The videos were built with [Claude Code](https://claude.com/claude-code) driving the
scripts below. **Not included:** the Claude Code skill files themselves, my recordings,
and the finished videos. Everything that explains *how* it was done is here.

## Layout

```
tools/scripts/          the pipeline (Python 3.11+, ffmpeg)
tools/assets/emoji/     Twemoji PNGs overlaid next to each word (meaning for non-English viewers)
references/             formant reference data + Instagram Reels layout research
reel-english-is-easy/   the trend reel: notes, plan, reshoot spec, caption, per-reel build scripts
docs/                   worked example of a panel-format reel (the STRUT /ʌ/ video)
```

## Format 1 — the panel reel

```bash
# 0. analysis audio (44.1 kHz mono for Praat)
ffmpeg -y -i in.mp4 -vn -acodec pcm_s16le -ar 44100 -ac 1 clip_audio_44k.wav
# 1. transcribe (words + probabilities; CPU whisper is slow, run it in the background)
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
| `find_speech_runs.py` | intensity runs above a dB threshold, with voiced fraction and median F0/F1/F2 per run — the take boundaries |
| `build_clean_cut.py` | single-pass `trim/atrim + concat` cut, measures each take's nucleus (median F1/F2 over voiced frames within 15 dB of the peak), writes the exact timeline to `cuts.json` |
| `build_phonetics_ass.py` | word + IPA + grade subtitles (libass), one per padded segment |
| `render_freq_panel.py` | per-frame PNGs: wideband spectrogram, F1/F2 dots, target bands, pitch strip, one window per word |
| `compose_reels.py` | overlays subtitles, panel and meaning emoji on the Reels canvas |
| `render_vowel_chart.py` | F1×F2 chart vs the reference means ±1 SD, plus an ending-F3 "R test" subplot when UK/US pairs are present |
| `vowel_map.py` | word→vowel, word→IPA, word→emoji, the reference targets, the match % and the A+…F grade bands |
| `hillenbrand_means.py`, `deterding_means.py` | rebuild the reference CSVs from the raw data |

## Format 2 — the beat-synced trend reel

Scripts: `beat_grid.py` (tempo + downbeat grid from a track), `track_face.py`
(head anchor for punch-ins), `walk_fx.py` (locked-subject walking shot),
`blur_whip.py` (zoom-blur whip transitions), `render_ridge_panel.py` (the waterfall
ridgeline panel), and the per-reel `select_takes.py` → `build_cut.py` → `build_text.py`
in `reel-english-is-easy/`. The exact order, the measured numbers and the three
alignment bugs that had to be fixed are in
[reel-english-is-easy/NOTES.md](reel-english-is-easy/NOTES.md).

## The rules these videos taught me

Every one of these came from a mistake that shipped or nearly shipped.

- **Identify the word before grading the vowel.** Nearest-vowel matching on formants
  cannot tell a mislabelled word from a mispronounced one. Transcribe each word group in
  isolation; the ASR was right and my own word list was wrong four times in one session.
- **Find the real focus before building.** Grade the vowel every word shares, not the
  feature that happens to be visually obvious (an R-ending). Getting this backwards cost
  a full rebuild.
- **Never cut or measure on whisper timestamps.** They are loose; derive spans from
  intensity runs. Whisper also hallucinates polite outros over trailing silence.
- **Never concatenate per-segment AAC files.** Each decode loses a ~23 ms priming frame;
  ten segments drift 0.2 s. Cut everything in one filter pass.
- **Quantise a beat-locked timeline into whole frames once** and let every layer read
  those frame numbers. One beat at 109.94 BPM is 16.37 frames; letting `fps=30` round
  each segment put the captions a full word ahead by word 26.
- **Render overlay PNG sequences for the whole video** and composite at offset 0.
  Time-shifting a partial sequence with `setpts` landed 5 frames early.
- **Long takes: splice the middle of the vowel**, a whole number of pitch periods, rather
  than clipping the final consonant.
- **`alimiter` auto-levels by default** and silently undoes `limit=`. Pass
  `level=disabled` and verify with both `ebur128` and `astats`.
- **Verify accent labels acoustically.** Ending F3 below ~2000 Hz means an r-coloured
  vowel (men /ɝ/ F3 1711 ± 108 vs plain ≈ 2548 ± 142, from the Hillenbrand raw data).
- **Dark /l/ drags F2 down ~400 Hz**: grade /ʌl/, /ʊl/, /uːl/ words on F1 only, with a
  wider tolerance, and say so on screen.
- **Use the right reference for the accent.** Hillenbrand is American: it has no /ɒ/ and
  its NURSE vowel is r-coloured. British word lists are graded against Deterding, whose
  between-speaker SDs (n = 5) need a floor before they are used as tolerances.
- **One spectrogram per word.** A full-timeline strip squeezes each word into ~30 px.
- **A heatmap reads as noise to non-specialists.** The ridgeline panel is the same data
  drawn the pre-heatmap way; colour by elevation, calibrate the ramp to the p95 of the
  measured amplitude, highlight only the vowel nucleus, glow only the near ridges.
- **Never burn the music in.** Upload the voice-only file, add the track inside
  Instagram, and note the exact second to start it.
- **Every `-loop 1` still input in ffmpeg needs `-t <duration>`**, or the filtergraph
  never ends.
- Measure with a 5000 Hz formant ceiling for a male voice (5500 for female); pitch floor
  75 Hz. Type sizes ended at word ~100 px, IPA ~75 px, emoji 128 px; err large.
- Verify every export with `ffmpeg -v error -i out.mp4 -f null -`, and eyeball the first
  frame, the last frame and one word card before posting.

## Requirements

- Python 3.11+ and `pip install -r requirements.txt`.
- ffmpeg with libass built with harfbuzz + fribidi (the multilingual titles: Arabic,
  Devanagari, IPA). The scripts default to NVIDIA NVENC (`h264_nvenc`); swap in
  `libx264` if you have no NVIDIA GPU.
- Fonts referenced by the ASS styles and the panel renderer: Segoe UI (+ Semibold, Black)
  and Nirmala UI, i.e. a Windows box. `render_freq_panel.py` loads
  `C:/Windows/Fonts/seguisb.ttf` directly; point it at another bold sans on other systems.
- `track_face.py` needs MediaPipe's `pose_landmarker_lite.task` in `tools/models/`
  (download from the MediaPipe model card; gitignored here).

## Data and asset licences

- **Hillenbrand et al. (1995)** raw vowel data (`references/hillenbrand-vowdata.dat`) was
  distributed freely by the author at `homepages.wmich.edu/~hillenbr/` (site now dead,
  Wayback Machine copies are cited in [references/README.md](references/README.md)).
  The derived means CSV is computed from it.
- **Deterding (1997)** tables were transcribed by hand from the paper's appendix; the
  script that rebuilds the means asserts that the transcription reproduces the paper's
  own Table 2. The paper PDFs themselves are not redistributed.
- **Twemoji** graphics (`tools/assets/emoji/`) are CC-BY 4.0, © Twitter, Inc. and
  contributors, via the maintained `jdecked/twemoji` fork.
- Code: MIT, see [LICENSE](LICENSE).
