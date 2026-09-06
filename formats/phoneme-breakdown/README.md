# Phoneme breakdown (the GitHub promo reel)

A 17 s selfie clip becomes a 14.8 s Reel in which **every phoneme is graded against
published references and mapped onto the spectrogram**, the hand gets a 21-point
skeleton, the Instagram thumbnails and live clips appear where the finger points, and a
GitHub card appears on the word "GitHub". Built 2026-09-06 to announce this repository.

- Build notes, findings and the rules learned: [NOTES.md](NOTES.md)
- The checklist that drove the session, round by round: [CHECKLIST.md](CHECKLIST.md)
- The references behind every grade: [references/phonemes/README.md](../../references/phonemes/README.md)
- Caption: [CAPTION.md](CAPTION.md)

## The band at the bottom

Left chip: the phoneme being spoken and its grade. Middle: the waterfall ridgeline
spectrogram of the last 0.42 s, every ridge tinted by its phoneme's grade colour, with
consecutive phonemes alternating texture (solid, checker, lines) so the runs separate,
a divider ridge at every phoneme onset with the symbol at both ends. Right chip: the
accent that phoneme was said in, British, American, or a half-and-half flag when the
sound is the same in both. Above it, the English line and the RP IPA line with every
symbol in its grade colour.

## Pipeline

```bash
# 0. cut the pauses on whole frames; the timeline in cut.json is read by every layer
#    (see build_promo.py's header for the one-pass trim/concat), then the analysis audio:
ffmpeg -y -i work/cut_master.mov -vn -acodec pcm_s16le -ar 44100 -ac 1 work/cut_voice_44k.wav
# 1. words and IPA: transcribe, write timeline.json (English, RP IPA, two meaning emoji per line)
python tools/scripts/transcribe_audio.py work/voice_16k.wav work/segments.json
# 2. phone boundaries + Goodness of Pronunciation
python align_phones.py work/cut_voice_44k.wav work/timeline.json work/phones.json
# 3. grade every phone and decide its accent
python phone_grades.py work/cut_voice_44k.wav work/phones.json work/timeline.json references/deterding1997-means.csv work/phones_graded.json
# 4. hands: MediaPipe Hand Landmarker, then a rescue pass on a padded frame, then filter
python tools/scripts/extract_hands_mp.py IMG.MOV tools/models/hand_landmarker.task work/hands_mp.npz 2
python hands_retry.py IMG.MOV tools/models/hand_landmarker.task work/hands_mp.npz work/hands_mp2.npz 0.3
# 5. the most intense window of each promoted video (mean absolute frame difference)
python motion_windows.py work/motion.json video1.mp4 video2.mp4 video3.mp4
# 6. the band (phone runs, dividers, chips), then the composite
python render_promo_panel.py work/cut_voice_44k.wav 444 work/band work/phones_graded.json
python build_promo.py work/cut_master.mov work/cut.json work/timeline.json work/hands_mp4.npz work/band out/promo_video.mp4
# 7. level the voice (alimiter level=disabled!), mux, verify
ffmpeg -v error -i out/reel-upload.mp4 -f null -
```

| script | does |
|---|---|
| `align_phones.py` | wav2vec2-lv-60-espeak-cv-ft phoneme posteriors (20 ms) + `torchaudio.functional.forced_align` on our own RP transcription mapped to its tokens; GOP per phone (Witt & Young 2000); saves the posteriors for the accent test |
| `phone_grades.py` | monophthongs by F1/F2 vs Deterding 1997, diphthongs by onset/offset vs monophthong anchors, word-initial stops by VOT vs Lisker & Abramson 1964, sibilants by centre of gravity vs Haley 2010, the rest by GOP; accent per phone (RP vs Hillenbrand distance, or the recogniser asked which variant it heard) |
| `render_promo_panel.py` | the ridgeline band with phoneme runs, textures, dividers, symbols, grade chip and accent flag |
| `build_promo.py` | the composite: hand skeleton, top row (Instagram tiles, live clips, repo card), subtitles with per-phoneme IPA colours, all on transparent layers |
| `hands_retry.py`, `hands_retry_roi.py` | second and third detection passes for frames the tracker missed |
| `motion_windows.py` | the 2.5 s window of maximum pixel change per video |
| `tools/scripts/extract_hands_mp.py` | MediaPipe Hand Landmarker over a whole clip → npz |

Models: `hand_landmarker.task` (MediaPipe model card, float16), `facebook/wav2vec2-lv-60-espeak-cv-ft`
(Hugging Face, downloaded on first run; the phonemizer-based tokenizer is bypassed by
reading `vocab.json` directly, so espeak-ng is not needed).

## Rules learned

- **CTC alignment is peaky.** A token owns a few frames; give each phone the blank
  frames up to the next onset or durations are nonsense.
- **Whitelist the recogniser's tokens.** The 392-token vocabulary holds `th`, `ts`, `eɑ`
  from other languages and greedy matching swallowed "t h" as one token.
- **The transcription is a claim the recogniser can dispute.** GOP flagged exactly the
  places where the RP line did not match what was said (American /oʊ/ and /ɑ/), and
  that is what the accent flag is built on.
- **Say what is approximate.** No open RP diphthong table in Hz exists; the diphthong
  grade uses monophthong anchors and the notes say so.
- **Draw with alpha on a transparent layer**, never straight onto the opaque frame: PIL
  writes the alpha value instead of blending, and the fades silently did nothing.
- **A hand cut by the frame edge is a fragment.** Padding the canvas rescued frames, a
  crop rescued none, and low thresholds invented hands on a hoodie collar; filter by
  position, size and score, and leave the frames with no palm empty rather than stale.
- **Real tiles first, then your own.** The Instagram tiles with their own view counts
  read as legitimate; the live clips with drawn pills read as yours. Show them in that order.
- **Publishers block PDF fetches.** Save what is open into `references/` immediately and
  record every number with its source.
