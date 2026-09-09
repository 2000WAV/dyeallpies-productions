# Worked example — the STRUT /ʌ/ reel (2026-09-01)

The second phonetics reel made with this skill, and the one that shaped most of its
current behavior. Read this before building another reel: the *decisions* here are
reusable even though the words aren't. The rules distilled from it live in
the [README](README.md); this file keeps the reasoning and the numbers.

**Input:** `WhatsApp Video 2026-09-01 at 18.46.52.mp4`, 81.6 s, 848x480 landscape with
rotation metadata (the master comes out true portrait 480x848 — probe the MASTER).
Dennis reads ~34 takes: a deliberately wrong "culture", "no", then British/American
pairs of R-ending words, then a long list of /ʌ/ words.

**Output:** `phonetics-reels-3.mp4` — 26.5 s, 1080x1920, 23 words / 28 takes kept —
plus `vowel_space4.png`. Artifacts: `final_takes4.json`, `cuts4.json`,
`removed_takes4.json`, `phonetics4.ass`, `panels4/`, `master4_clean.mp4`.

## What the video says

Cold open: Dennis says "culture" wrong on purpose, says "no", then the American and
British versions. Then 21 more /ʌ/ words, five of them in US/UK pairs.

## The decisions that mattered

### 1. Find the real focus before building anything

Whisper's transcript said "culture, no, culture, culture, cultural, cult, cultivate,
custom, customer, …". The theme is **not** the R-endings that jump out visually — it is
the **STRUT vowel /ʌ/**, which every single word shares. The R-endings are one
sub-theme inside it. Getting this backwards cost a full rebuild: the first cut graded
UK/US takes on their *ending* F3, which meant the video's grades were answering a
question the video wasn't asking. **The studied vowel owns the grades; everything else
is a side note.**

### 2. Verify the accent labels acoustically, never from memory

F3 is the r-coloring cue. Men's steady-state F3, computed from the raw Hillenbrand
`.dat` (col 6, zeros excluded — see `tools/scripts/hillenbrand_means.py` for the
parsing pattern):

| | F3 mean ± SD | n |
|---|---|---|
| /ɝ/ ("heard") — r-colored | 1711 ± 108 Hz | 40 |
| /ʌ/ ("hud") — plain | 2548 ± 142 Hz | 45 |

Every pair came out unambiguous (US 1644–1899 Hz vs UK 2455–2731 Hz), which confirmed
take 1 = British, take 2 = American in the source. Threshold used:
`RHOTIC_F3_MAX = 2000`.

### 3. Transcribe what was *said*, not what was meant

Dennis asked for the real transcription of the two opening takes rather than the
intended one. From the formant tracks:

- The gag "culture": nucleus F1 ≈ 320 / F2 ≈ 800 — a genuinely **back [uː]**, not a
  /ʌ/, in mock falsetto (F0 ≈ 240 Hz vs his usual ~90), ending in a plain [ə]
  (F3 ≈ 2050, not r-colored) → **[ˈkuːltʃə]**.
- "no": a ~100 ms monophthong, F1 477 / F2 1179 once the /n/ murmur is excluded from
  the measurement span — mid-back, centralized, **no /oʊ/ offglide** → **[no]**.
  Nearest reference is /oʊ/ (498, 910) at ~2 SD, so it is graded against /oʊ/ and
  earns a C.

Convention adopted: **narrow [brackets] = what was said, /slashes/ = the target.**
A gag take's wrong vowel is highlighted red; the tag line names the error
("that [uː] should be /ʌ/…").

Measurement gotcha this exposed: a nasal murmur or approximant inside the word drags
the nucleus median (the first "no" measured F1 346 before the span was tightened).
When a measured vowel looks wrong for what you hear, narrow `m0`/`m1` first.

### 4. Grade every vowel, but keep one primary

Dennis: *"let's put grades for EACH vowel pronounced, tho our focus is always strut.
Put the grades lined vertically."* Implemented as a stack: the strut stamp big at
mid-right, then smaller rows under it. Only Hillenbrand-referenced vowels qualify —
unstressed word-internal schwa (custom, hundred, sudden) has no reference and honestly
gets nothing.

Three different distance bases, each footnoted where it appears:

| vowel | basis | why |
|---|---|---|
| the studied vowel, and any full extra vowel (`"vowels"` spans) | 2-D over (F1, F2) | the normal case |
| stressed /ʌ/ before dark /l/ (`DARK_L`) | **F1 only, tolerance ×2** | dark /l/ drags F2 ~400 Hz down; a 2-D grade would be a lie |
| a UK/US ending ə ~ ɚ | **1-D over F3** | tail F1/F2 frames are too weak/short to trust |

The dark-/l/ rule is what finally gave culture / cultural / cult / cultivate grades at
all — they had been ungraded, which read as a bug from the outside.

### 5. Cull takes; don't ship everything

Dennis records extras deliberately: *"you are allowed to remove bad samples, that's why
I said too many."* Five takes removed, each with an acoustic reason, all ×-marked on
the chart via `removed_takes4.json`:

| take | why |
|---|---|
| lunch | F — vowel 4+ SD off, far too close/front |
| subject | creaky voice, formants unmeasurable |
| bus | D |
| customary ×2 | the "-ary" came out open and r-dominated ([ɐɹ]-ish, F1 570–655 with F3 dipping to ~1650), neither UK /ˈkʌstəməri/ nor US /ˈkʌstəmɛri/ |

The customary removal came from Dennis's own suspicion — he asked to check the ending
before keeping it. **Check the part of the word you're claiming to teach.**

### 6. Legibility beats completeness

- **One spectrogram per word.** A single full-timeline strip squeezed each word into
  ~30 px of an 876 px panel — unreadable. The panel's time axis now spans only the
  current word's display window.
- **Windows must tile, and must not overlap.** "cup/cut/butt" sit close enough that
  their padded segments merge into one; both takes then displayed for the whole shared
  window, stacking two words' subtitles, grade stamps and emoji on top of each other.
  Fix: split a merged segment's display windows at the word midpoints.
- Type sizes ended at word 104 px / IPA 78 px / tag 50 px / panel readout 36 px, emoji
  128 px — Dennis asked for "bigger" twice; err large.

### 7. Color carries meaning, so give the star a color

Once the ending was teal, the studied vowel being merely *bold* made the ending look
like the subject. The strut vowel now gets its own blue (#4db5ff, the same blue as its
dots on the chart). Colors in play: blue = studied vowel / F1, teal = ending, red =
wrong vowel, purple = F3 over an R-ending, orange = F2, green = F0.

### 8. Order for the audience, not for the tape

American take before British — more widespread. `final_takes.json` rows are simply
reordered; `build_clean_cut.py` merges only **forward**-overlapping pads so an
out-of-source-order pair can't merge into the wrong segment.

## Final grades (for reference)

A+ cup 95 %, cut 90 %, summer·UK 100 % · A cult, customer·US 75 %, fun 85 %, jump 82 %,
such 78 %, number·US 79 %, number·UK 73 %, under·UK 81 %, supper·US 70 % ·
B culture·UK, custom 48 %, customer·UK 47 %, much 53 %, sudden 58 % ·
C culture·US, cultural, cultivate, no 38 %, butt 38 %, run 39 %, under·US 36 %,
hundred 39 %, Sunday 27 %, supper·UK 44 % · F the gag "culture" (0 %).

Dark-/l/ words (culture family) are F1-only grades; UK/US rows also carry an ending
grade (ə/ɚ, all A/A+).

## The Instagram description that shipped

> Culture? ❌ [ˈkuːltʃə] — that [uː] should be a /ʌ/. 🎭
>
> One vowel, 23 words: the English STRUT vowel /ʌ/ — cup, cut, fun, run, under… Each
> word gets its own live spectrogram, formants measured in real time, and a report
> card: every vowel graded A+ to F against the published American English reference
> (Hillenbrand et al. 1995, J. Acoust. Soc. Am., measured with Praat). Yes, my first
> "culture" earned that F 💀
>
> Side quest: some words come in American 🇺🇸 and British 🇬🇧 — watch the purple F3 line
> drop whenever the American R appears. That's the physics of an R.
>
> 🔬 Blue vowel = the star /ʌ/ · teal = the ending · purple = F3, the R detector ·
> grades = distance from the reference in standard deviations.
>
> How's YOUR /ʌ/? Say "cup" and tell me honestly 👇
>
> #phonetics #pronunciation #vowels #ipa #linguistics #accent #americanaccent
> #britishaccent #languagelearning #learnenglish #spectrogram #english

Pattern worth reusing: hook on the mistake, one line of what the video is, one line of
academic backing, a legend, a question to drive comments.

## Commands, in order

```bash
PY=.venv-subtitles/Scripts/python.exe
ffmpeg -y -i "WhatsApp Video 2026-09-01 at 18.46.52.mp4" -vn -acodec pcm_s16le \
  -ar 44100 -ac 1 clip2_audio_44k.wav
$PY tools/scripts/transcribe_audio.py clip2_audio_44k.wav segments2.json   # background
$PY tools/scripts/find_speech_runs.py clip2_audio_44k.wav 50 0.10 0.12
# hand-write final_takes4.json from the runs (+ variants, r0/r1, extra vowels),
# after dumping per-run F0/F1/F2/F3 tracks to label and verify each take
$PY tools/scripts/build_clean_cut.py "WhatsApp Video 2026-09-01 at 18.46.52.mp4" \
  clip2_audio_44k.wav final_takes4.json master4_clean.mp4 cuts4.json
$PY tools/scripts/build_phonetics_ass.py cuts4.json phonetics4.ass 1080 1920
ffmpeg -y -i master4_clean.mp4 -vn -acodec pcm_s16le -ar 44100 -ac 1 clean4_audio.wav
$PY tools/scripts/render_freq_panel.py clean4_audio.wav cuts4.json panels4 876 370 30
$PY tools/scripts/compose_reels.py master4_clean.mp4 panels4 phonetics4.ass \
  phonetics-reels-3.mp4 cuts4.json
ffmpeg -v error -i phonetics-reels-3.mp4 -f null -
$PY tools/scripts/render_vowel_chart.py cuts4.json removed_takes4.json \
  references/hillenbrand1995-means.csv vowel_space4.png
```

**Re-render everything downstream of a re-cut.** `panels4/` keeps stale frames past the
new (shorter) duration — clear the directory rather than letting `panel_%05d.png` mix
two runs.
