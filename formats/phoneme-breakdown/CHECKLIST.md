# GitHub promo reel — checklist (2026-09-06)

Source: `originals/IMG_6082.MOV` (17.2 s, portrait 1080x1920 after rotation, 30 fps) and
`originals/IMG_6070.PNG` (phone screenshot). Aim: show the public repo
`DyeAllPies/dyeallpies-productions` and the top 3 videos it documents, promote phonetics.

## Inputs to understand first
- [x] Watch the clip (contact sheet) and transcribe it word by word with timestamps
- [x] Look at the PNG: Instagram Reels tab; top 3 = pull-up 8,723 · WHO'D 764 · culture 2,609 views (tiles cropped to work/thumbs/)
- [x] Find where Dennis points, when, and in which direction (hand tracking)
- [x] Hand skeleton (MediaPipe Hand Landmarker, 21 points): tools/scripts/extract_hands_mp.py -> work/hands_mp.npz, drawn with glow, index tip ringed
- [x] Find the beats: "thanks for the views", "these videos", "GitHub repo", "phonetics"

## Edit
- [x] Cut long pauses: 17.2 s -> 14.8 s, takes in work/cut.json
- [x] Single-pass trim/concat cut -> work/cut_master.mov (decode clean)
- [x] Verify decode (cut master and final export both clean)

## Overlays (all read the same timeline)
- [x] Thumbnails of the top 3 videos in the top row where the index finger points (3.45 s), Instagram's count strip cropped off
- [x] "thanks for the views" -> thumbnails pop in with drawn eye + count pills (8.723 / 764 / 2.609)
- [x] "these videos" -> tiles crossfade to the live 2.5 s max-pixel-change window of each video (motion_windows.py)
- [x] Repo card at "GitHub repository" (index up): github.com/DyeAllPies / dyeallpies-productions / PUBLIC pill
- [x] Subtitles: English (bold 66) + RP IPA (gold 52) on the band, two meaning emoji flanking, fit() on every line
- [x] Ridgeline band y 1380-1920 (render_promo_panel.py), continuous, subtitles sit on it
- [x] Every burned-in line measured to its box; first / last / card / clip frames eyeballed (work/final_sheet.png)

## Audio
- [x] Voice levelled: -13.3 LUFS, -1.7 dBTP (highpass, compressor, alimiter level=disabled) -> work/voice_final.wav

## Delivery
- [x] `out/reel-upload.mp4` 1080x1920 NVENC, 444 frames, decode clean; flicker check: only the three take joins (frames 144, 263, 395) jump, no one-frame flashes
- [x] Caption draft in `CAPTION.md`
- [x] First pass sent to Dennis 2026-09-06; refine on his notes
- [x] Dennis round 1: real Instagram tiles (count strip kept) first, quick swap to the live clips with pills, clips run until "GitHub" (cut 10.13 s), repo card from "GitHub"
- [x] Dennis round 1: colour each IPA vowel by its grade vs Deterding RP connected-speech means (grade_phonemes.py); consonants / schwa / diphthongs neutral; legend line under the IPA
- [x] Bug: pills and subtitles drawn with alpha onto the opaque frame never blended -> drawn on layers now
- [x] Dennis: hand not recognised 1-3 s. Second pass (hands_retry.py: padded frame, low thresholds, IMAGE mode) recovered 32 frames, 3 of them false (hoodie collar, low score) -> filtered by position/size/score to hands_mp4.npz (29 kept); a third pass on an upscaled left-edge crop recovered none. 1.8-3.1 s: only the back of the hand + index are in frame, wrist and palm outside -> no skeleton there (honest; no stale hold)
- [x] Round 2 rendered, muxed, decode clean, flicker = take joins only, frames checked, sent 2026-09-06
- [x] Dennis round 2: legend line removed (colours stay, unexplained); repo card first line now github.com/DyeAllPies/ with the trailing slash
- [x] Dennis asked whether consonants can be graded: answered (no formant reference; possible via VOT / fricative centroid with published norms, not built)
- [x] Round 3 rendered, decode clean, card + thumbs frames checked, sent 2026-09-06
- [x] Dennis round 3a: research written up in references/phonemes/README.md (Witt & Young 2000 GOP, Ferragne 2010 RP table, Lisker & Abramson 1964 VOT, Haley 2010 sibilant CoG; diphthongs approximated from monophthong anchors, stated); PDFs saved where the publisher allowed
- [x] Dennis round 3b: align_phones.py (wav2vec2 phoneme CTC + forced_align + GOP), phone_grades.py (all 103 phones graded: 52 acoustic, 51 GOP), band shows phone runs / dividers / symbols / current-phone chip, IPA coloured per phone; round 4 rendered, decode clean, sent 2026-09-06
- [x] Dennis round 4: phoneme runs on the spectrogram alternate texture (solid / checker / lines), stronger tint, symbol at both ends of each divider
- [x] Dennis round 4: spectrogram squeezed (x 150-850); left chip = phone + grade, right column = accent flag per phone (British / American / half-and-half for neutral), decided by RP-vs-Hillenbrand distance for vowels and by the recogniser for the GB/US alternations (əʊ/oʊ, ɒ/ɑ, ɑː/æ, ɜː/ɚ, final ə/ɚ, t/flap)
- [x] Round 5 rendered, decode clean, band frames checked, sent 2026-09-06
- [x] Dennis round 5: Instagram tiles from 0.15 s to 4.2 s (the hook), live clips 4.2-10.13, repo card 10.13-13.15, clips back 13.15-end; clip windows re-extracted at 11 s so the second run has footage
- [x] Round 6 = FINAL (Dennis, 2026-09-06): rendered, decode clean, -13.4 LUFS / -1.9 dBTP, flicker = take joins + one cut inside the pull-up miniature, sent
- [x] Dennis round 4: phoneme runs on the spectrogram alternate texture (solid / checker / lines), stronger tint, symbol at both ends of each divider
- [x] Dennis round 4: spectrogram squeezed (x 150-850); left chip = phone + grade, right column = accent flag per phone (British / American / half-and-half for neutral), decided by RP-vs-Hillenbrand distance for vowels and by the recogniser for the GB/US alternations (əʊ/oʊ, ɒ/ɑ, ɑː/æ, ɜː/ɚ, final ə/ɚ, t/flap)
- [x] Round 5 rendered, decode clean, band frames checked, sent 2026-09-06
- [x] Dennis round 5: Instagram tiles from 0.15 s to 4.2 s (the hook), live clips 4.2-10.13, repo card 10.13-13.15, clips back 13.15-end; clip windows re-extracted at 11 s so the second run has footage
- [x] Round 6 = FINAL (Dennis, 2026-09-06): rendered, decode clean, -13.4 LUFS / -1.9 dBTP, flicker = take joins + one cut inside the pull-up miniature, sent
- [x] Added to `dyeallpies-productions` as formats/phoneme-breakdown (README, notes, checklist, caption, scripts; references/phonemes/README.md; no media, no PDFs)
- [x] HANDOFF.md rotated

## Timeline facts (source time)
- 0.27–2.95 "Hey guys, this is DyeAllPies" (wave, right hand frame-left)
- 3.53–4.37 "Thanks for the views" (right hand raised, index up, frame upper-left)
- 5.43–8.73 "Some people have asked me how I make these videos" (hand upper-left, pointing)
- 10.23–13.85 "Check out my GitHub repository, DyeAllPies Productions" (hand left, pointing)
- 15.35–15.99 "Peace"
- Pauses to shorten: 4.37–5.43, 8.73–10.23, 13.85–15.35, tail after 15.99
- Intense windows (2.5 s): pull-up 47.6 s (reps 9–10), english 23.3 s (BAD/BOOK), strut 13.2 s (fun/much)

## Grade caveats (say so if asked)
- Connected speech, not isolated words: vowels are short and reduced, so grades run harsher than the reels.
- Reference: Deterding (1997) men's CONNECTED-speech means, citation SDs floored (F1 >= 45, F2 >= 130 Hz), 2-SD Gaussian bands as in vowel_map.
- Nuclei come from intensity peaks inside whisper's word span (clipped to neighbours); multi-vowel words assign peaks in order, so a wrong peak can grade the wrong vowel ("people" iː probably measured the schwa).
- No reference here for consonants, schwa, diphthongs, happY-i: they stay neutral grey.
