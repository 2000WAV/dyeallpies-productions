# Phonetics reel, beat-synced trend format

Reel 4, "English is easy" (Sep 2026): the panel format's measurement machinery cut to a
trending song's beat grid. Acting shots up front, one word per beat at the drop, 26 words
across p/b/h consonant frames covering the RP vowel inventory, multilingual titles, and a
"waterfall" ridgeline spectrum instead of a heatmap. Graded against **Deterding (1997)**,
RP / British English, because the Hillenbrand reference is American: it has no /ɒ/ and its
NURSE vowel is r-coloured.

Build notes with every measured number and the three alignment bugs that had to be
fixed: [NOTES.md](NOTES.md). Plan: [PLAN.md](PLAN.md). Reshoot spec: [RESHOOT.md](RESHOOT.md).
Caption: [CAPTION.md](CAPTION.md).

## Scripts

Shared, in `tools/scripts/`: `beat_grid.py` (tempo and downbeat grid from a track),
`track_face.py` (head anchor for punch-ins), `walk_fx.py` (locked-subject walking shot),
`blur_whip.py` (zoom-blur whip transitions), `render_ridge_panel.py` (the waterfall
ridgeline panel), plus the panel format's transcription, cutting and measurement scripts.

Per-reel, in this folder: `select_takes.py` → `build_cut.py` → `build_text.py`. They
assume the reel's working tree at `reel-english-is-easy/` next to `tools/`, with
`originals/`, `work/` and `out/` inside it.

## Rules learned the hard way

- **Identify the word before grading the vowel.** Nearest-vowel matching on formants
  cannot tell a mislabelled word from a mispronounced one, and using it for both produced
  a confident wrong verdict that nearly threw away two thirds of the footage. Transcribe
  each word group in isolation (one wav per group, VAD off) and take the word identity
  from that; formants then answer only "how well was it said". The ASR was right and the
  written word list was wrong four times in one session.
- **Quantise a beat-locked timeline into whole frames once.** One beat at 109.94 BPM is
  16.37 frames at 30 fps; letting `fps=30` round each segment put the captions a full
  word ahead of the audio by word 26. Write the frame numbers to one `timeline.json` and
  have every layer read them. Two layers computing "the same" times independently will
  disagree, and the disagreement grows.
- **Render overlay PNG sequences for the whole video** and composite at offset 0.
  Time-shifting a partial sequence with `setpts` landed 5 frames early.
- **Long takes: splice the middle of the vowel**, a whole number of pitch periods from
  the take's measured F0, rather than clipping the final consonant. 8–149 ms removed,
  inaudible.
- **The panel is a ridgeline, not a heatmap.** Non-specialists read a heatmap spectrogram
  as noise. ~30 spectral slices drawn as glowing polylines stacked receding in fake 3-D,
  painter's algorithm back to front with an opaque fill under each ridge so the nearer
  ones occlude. Colour by elevation, calibrate the ramp to the p95 of the measured
  amplitude (not 1.0, or the whole panel is one flat blue), highlight only the vowel
  nucleus, dot the spectral peaks nearest F1/F2 on each highlighted ridge, glow only the
  near ridges. Recompute the nucleus from the FINAL audio so splices are accounted for.
- **Two different meaning emoji, one either side of the word.** A pair reads faster than
  one image repeated and disambiguates ("hoard" = money bag + gem, not "horde").
- **Derive the consonant-frame label from the IPA** (first and last phoneme), not a fixed
  per-group string; after word corrections "hat" is `h _ t`, not `h _ d`.
- **Deterding's between-speaker SDs (n = 5) need a floor** before they are used as
  tolerances.
- **Tempo: autocorrelation alone is ambiguous** (it offered 55/110/220 and 74/148
  families for one track). Settle it with a comb-filter test of how much onset energy a
  candidate grid catches, per 20 s window. Locate the drops from low-band (< 200 Hz)
  energy: bass re-entries land on exact downbeats.
- **`alimiter` auto-levels by default** and silently undoes `limit=`. This shipped
  clipping at +0.4 dBFS across three exports. Pass `level=disabled` and verify with both
  `ebur128` (true peak) and `astats` (sample peak). Target about -14 LUFS / -1.5 dBTP.
- **Speech vs a loud track: check spectral overlap, not just level.** 85 % of the speech
  energy sat in 80–800 Hz where the song had 15 %, so the vowels survive and the /p/
  bursts are what get masked. Carve the pocket: high-pass 95 Hz, presence lift, compression.

## Delivery

- `reel-upload.mp4`: the voice, no music. This is what gets uploaded; the track is added
  inside Instagram, where the original-audio slider keeps the words audible. Burning a
  commercial track in is what gets Reels muted or suppressed.
- `reel-preview.mp4`: voice + music, for checking sync locally. Never uploaded.
- The music file is a timing reference only: extract the beat grid, then delete it.
- Note the exact second to start the track in-app (8.6827 s for this reel).
