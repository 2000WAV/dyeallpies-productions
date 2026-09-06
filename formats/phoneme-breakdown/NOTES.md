# GitHub promo reel — build notes (2026-09-06)

Source `originals/IMG_6082.MOV`, 17.2 s selfie talk, 1080x1920 after rotation, 30 fps.
Output `out/reel-upload.mp4`, 14.8 s. The checklist that drove the session is
`CHECKLIST.md`; the grading references are `references/phonemes/README.md`.

## What the video does

1. Pauses cut (17.2 → 14.8 s), four takes, one trim/concat pass, whole-frame timeline
   (`work/cut.json`) read by every layer.
2. Where the index finger points up ("thanks for the views", "GitHub repository") the top
   row shows the three Instagram tiles exactly as the profile renders them, then swaps
   to the live 6 s max-pixel-change window of each video with eye + count pills, until
   the word "GitHub", where the repo card takes over.
3. Hand skeleton: MediaPipe Hand Landmarker (21 points) in VIDEO mode, a rescue pass on
   a padded frame for missed frames, false detections filtered by position / size /
   score. 1.8–3.1 s has no skeleton: only the back of the hand is in frame.
4. Subtitles on the spectrogram band: English + RP IPA, two meaning emoji.
5. **Every phoneme graded and coloured**, and the phone boundaries drawn on the
   waterfall spectrogram (see below).
6. Voice levelled to −13.3 LUFS / −1.7 dBTP.

## The phoneme breakdown

- `align_phones.py`: wav2vec2-lv-60-espeak-cv-ft phoneme posteriors (20 ms frames) +
  CTC forced alignment of our own RP transcription → a start/end for every phone, and a
  Goodness of Pronunciation score per phone (Witt & Young 2000: log p(intended) −
  log p(best), mean over the phone's frames). CTC alignments are peaky, so each phone
  is given the blank frames after it up to the next phone's onset.
- `phone_grades.py`: monophthongs by F1/F2 vs Deterding (1997) connected-speech means;
  diphthongs by onset/offset vs monophthong anchors (approximation, no open RP diphthong
  table in Hz was found); word-initial stops by VOT vs Lisker & Abramson (1964);
  sibilants by spectral centre of gravity vs Haley et al. (2010) men; everything else by
  GOP. A GOP below −3.5 caps an acoustic grade at C.
- `render_promo_panel.py`: every ridge tinted by its phone's grade colour, a bright
  divider ridge with the symbol floating at the onset depth, and the phone being spoken
  big in the left column with its grade.

Findings on this clip that the numbers surfaced: word-initial /p/ with 4–16 ms VOT
(unaspirated, a Portuguese/Danish habit), "videos" said with American /oʊ/ rather than RP
/əʊ/ (GOP −8), "repository" with an American /ɑ/ instead of /ɒ/ (GOP −7), a syllabic /l/
in "people" where the transcription had /əl/, and /s/ centre of gravity around 8 kHz,
sharper than the 6.3 kHz male reference (partly the phone microphone).

## Rules learned

- **CTC alignment is peaky.** Token spans from `merge_tokens` are a few frames; extend
  each to the next onset or the durations are nonsense.
- **Whitelist the model's tokens.** The 392-token vocab holds `th`, `ts`, `eɑ` from other
  languages; greedy matching over the full vocab swallowed "t h" as one token.
- **The transcription is a claim the recogniser can dispute.** GOP flagged exactly the
  places where the RP transcription did not match what was said (American /oʊ/, /ɑ/).
- **Draw with alpha on a transparent layer**, never straight onto the opaque frame; PIL
  writes the alpha value instead of blending, so fades silently do nothing.
- **Hand detectors need the palm.** A hand cut by the frame edge is a fragment; padding
  the canvas rescues some frames, a crop rescues none, and low thresholds invent hands
  on hoodie collars: filter by position, size and score.
- **Publishers block PDF fetches**; save what is open (author copies, PMC) into
  `references/` immediately and record the numbers with their source.
