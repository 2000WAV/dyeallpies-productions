# dyeallpies-productions

How every DyeAllPies video is made. Each format below turns a phone or screen recording
into a posted Reel, Short or clip, and most of them measure something on the way: vowel
formants against published references, joint angles from two independent pose trackers,
rep counts, an EMG-informed muscle map. This repository holds the methods, the scripts
and the reference data. It holds **no recordings, no finished videos, no model weights
and no paper PDFs.**

The videos were built with [Claude Code](https://claude.com/claude-code) driving the
scripts. The Claude skill files themselves are not included; every rule they contain is
written out in the format READMEs, most of them learned from a mistake that shipped or
nearly shipped.

## Formats

| Format | What it makes | The measurement / ML part |
|---|---|---|
| [phonetics-panel](formats/phonetics-panel/) | A pronunciation-practice recording, cleaned and annotated: IPA subtitles with a letter grade per vowel, a live spectrogram / F1-F2 / pitch panel, a vowel-space chart. Reels 1–3, including the STRUT /ʌ/ "culture" video with its UK/US minimal pairs. | Praat formant tracking (parselmouth), Mahalanobis grading against Hillenbrand et al. (1995), faster-whisper for word identity |
| [phonetics-trend](formats/phonetics-trend/) | The same measurements cut to a song's beat grid: acting shots, one word per beat at the drop, a waterfall ridgeline spectrum. Reel 4, "English is easy". | Beat grid from onset comb filtering, Deterding (1997) RP reference, MediaPipe face anchor for punch-ins |
| [pullup-analysis](formats/pullup-analysis/) | A pull-up set counted and graded rep by rep: tempo, range of motion, chin-vs-bar verdict, lock-out, sway, velocity loss, work / power / kcal, an efficiency score, and a muscle-heat overlay on a matted body against a replaced backdrop. Plus a dashboard, a written report and an interactive page. | MediaPipe Pose heavy (33 landmarks, 3D) cross-checked by YOLOv8-pose, Robust Video Matting, MediaPipe multiclass segmentation, surface-EMG literature (Youdas 2010, Dickie 2017), velocity-loss fatigue (Sánchez-Medina 2011) |
| [phoneme-breakdown](formats/phoneme-breakdown/) | A talking-head clip with every phoneme graded and mapped onto the spectrogram: phone boundaries, grade colours per symbol, an accent flag per phoneme, a hand skeleton, and the promoted videos appearing where the finger points. The GitHub promo reel. | wav2vec2 phoneme recogniser + CTC forced alignment, Goodness of Pronunciation (Witt & Young 2000), formants vs Deterding 1997 and Hillenbrand 1995, VOT vs Lisker & Abramson 1964, sibilant centre of gravity vs Haley 2010, MediaPipe Hand Landmarker |
| [pushup-cat](formats/pushup-cat/) | A push-up set with a live rep counter, plus a live count of the cats that wander through the frame, with a ding per rep and a meow per cat. | MediaPipe Pose elbow-angle signal, YOLOv8n cat detection with colour-histogram identity, Haar cascade fallback |
| [captions](formats/captions/) | Word-highlighted "viral" captions burned into a clip, timed against the real audio but worded from a reference transcript. | faster-whisper word timestamps aligned to the transcript with a sequence matcher |
| [clip-cutting](formats/clip-cutting/) | A time range cut out of a screen / OBS recording as a landscape MP4 for YouTube and a 9:16 vertical for Reels and Shorts. | none, ffmpeg only |
| [deck-walkthrough](formats/deck-walkthrough/) | A silent captioned MP4 that walks through already-rendered figures, one slide each, as the quick preview of a report. | none, PIL and an ffmpeg xfade chain |

## Layout

```
formats/<name>/         one folder per format: README with the method and the rules,
                        worked examples, captions, plans, per-reel build scripts
tools/scripts/          the shared Python pipeline behind every format (Python 3.11+, ffmpeg)
tools/assets/emoji/     Twemoji PNGs overlaid next to each word (meaning for non-English viewers)
references/             formant reference data, pull-up EMG literature, phoneme grading references, Reels layout research
```

## Rules every format follows

- **Verify every export** with `ffmpeg -v error -i out.mp4 -f null -`. Any output means
  a problem; silence plus exit 0 means clean. Exit code and file size prove nothing.
- **One ffmpeg encode at a time.** Two at once on one GPU produce corrupt or slow output.
- **Encode with NVENC** where there is an NVIDIA GPU:
  `-c:v h264_nvenc -preset p5 -tune hq -rc vbr -cq 19 -b:v 0 -spatial-aq 1 -temporal-aq 1`.
  Swap in `-c:v libx264 -preset medium -crf 18` otherwise. Never trade quality for file size.
- **Long encodes must run detached** so nothing kills them mid-write; a truncated
  `+faststart` trailer produces a file that looks complete and is corrupt.
- **Measure every burned-in line to its box**, never assume it fits, and eyeball the first
  frame, the last frame and one card of every export before posting. That is where the
  overflow lives.
- **Gate every composited export with `tools/scripts/check_flicker.py`.** A frame sheet
  does not catch one-frame flashes; the flicker gate does.
- **Never burn commercial music in.** Upload the voice-only file, add the track inside
  Instagram, and note the exact second to start it. The music file is a timing reference
  only and is deleted once the cut is locked.
- **Reels are full-bleed 1080x1920.** The talking video fills the frame; overlays sit on
  top of it, never in a box.
- **Captions paste as written.** One paragraph per line, LF endings, at most 5 hashtags
  (Instagram's current limit); a hard-wrapped caption shows every wrap as a line break.
- **Check the source file exists before queueing work from it.** Sources get deleted to
  free disk, sometimes mid-session.

## Requirements

- Python 3.11+ and `pip install -r requirements.txt`. The pose formats need the CPU
  builds of torch, ultralytics and mediapipe; nothing here needs CUDA.
- ffmpeg with libass built with harfbuzz + fribidi (the multilingual titles: Arabic,
  Devanagari, IPA). The scripts default to NVENC; swap in `libx264` without an NVIDIA GPU.
- Fonts referenced by the ASS styles and the renderers: Segoe UI (+ Semibold, Black,
  Symbol), Nirmala UI, Impact, i.e. a Windows box. Several renderers load
  `C:/Windows/Fonts/...` directly; point them at another sans on other systems.
- Model weights, all gitignored under `tools/models/`; each format README says where its
  files come from: `pose_landmarker_lite.task` and `pose_landmarker_heavy.task` (MediaPipe
  model card), `selfie_multiclass_256x256.tflite` (MediaPipe image segmenter),
  `yolov8n.pt` and `yolov8m-pose.pt` (ultralytics assets release), `hand_landmarker.task`
  (MediaPipe model card), OpenCV's
  `haarcascade_frontalcatface_extended.xml`, and the Robust Video Matting weights that
  torch.hub downloads on first use.

## Data and asset licences

- **Hillenbrand et al. (1995)** raw vowel data (`references/hillenbrand-vowdata.dat`) was
  distributed freely by the author at `homepages.wmich.edu/~hillenbr/` (site now dead,
  Wayback Machine copies are cited in [references/README.md](references/README.md)).
  The derived means CSV is computed from it.
- **Deterding (1997)** tables were transcribed by hand from the paper's appendix; the
  script that rebuilds the means asserts that the transcription reproduces the paper's
  own Table 2. The paper PDFs themselves are not redistributed.
- **Phoneme grading references** (Witt & Young 2000, Ferragne & Pellegrino 2010, Lisker &
  Abramson 1964, Haley et al. 2010, Jongman 2024) are cited with the numbers used in
  [references/phonemes/README.md](references/phonemes/README.md); the PDFs are not redistributed.
- **Pull-up EMG values** come from the PubMed abstracts of Youdas et al. (2010) and
  Dickie et al. (2017), kept with their PMIDs in
  [references/pullup-emg/](references/pullup-emg/README.md).
- **Jungle backdrop** (`formats/pullup-analysis/assets/jungle_plate.jpg`) is a crop of
  a CC BY 4.0 photo by Vyacheslav Argenberg via Wikimedia Commons; the required credit
  line is in the folder's `ATTRIBUTION.md` and in the posted caption.
- **Twemoji** graphics (`tools/assets/emoji/`) are CC-BY 4.0, © Twitter, Inc. and
  contributors, via the maintained `jdecked/twemoji` fork.
- Code: MIT, see [LICENSE](LICENSE).
