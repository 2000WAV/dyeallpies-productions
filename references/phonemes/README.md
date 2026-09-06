# References — grading every phoneme (2026-09-06)

Collected for the GitHub promo reel, where each phoneme of the IPA line is coloured by a
grade and the phone boundaries are drawn on the spectrogram. Everything fetched from the
internet for this lives here so the method can be reproduced offline. Files marked
"text only" could not be downloaded as PDFs (publisher blocks); the numbers used were
read from open pages and are quoted below with their source.

## 1. Phone boundaries and the fallback grade: Goodness of Pronunciation

Witt, S. M., & Young, S. J. (2000). *Phone-level pronunciation scoring and assessment for
interactive language learning.* Speech Communication, 30(2–3), 95–108.
File: `witt-young2000-gop.pdf` (+ `.txt`, author copy from mi.eng.cam.ac.uk).

The GOP score of a phone = the log posterior of the intended phone over its aligned
frames minus the log posterior of the best-scoring phone over the same frames (their
eq. 3 in the free-phone-loop form), so 0 means "the recogniser is certain it heard
exactly that phone" and more negative means it heard something else. It is the standard
phone-level pronunciation-assessment method and works for every phoneme, consonants
included, which is why it is the fallback here for sounds that have no acoustic target
of their own (nasals, approximants, /h/, affricates, schwa) and a second opinion for the
rest.

Recogniser: `facebook/wav2vec2-lv-60-espeak-cv-ft` (Xu et al. 2021, *Simple and
effective zero-shot cross-lingual phoneme recognition*; wav2vec 2.0 large fine-tuned on
Common Voice with espeak-ng IPA phoneme labels, 392 tokens, 20 ms frames). Alignment by
`torchaudio.functional.forced_align` (CTC forced alignment) on our own RP transcription
mapped to its tokens (`e`→`ɛ`, `r`→`ɹ`). Script: `reel-github-promo/align_phones.py`.

## 2. Monophthongs

Deterding (1997), already in `references/` (RP, 5 men, BBC; connected-speech means used
for the promo). Second RP table, younger speakers:

Ferragne, E., & Pellegrino, F. (2010). *Formant frequencies of vowels in 13 accents of the
British Isles.* Journal of the International Phonetic Association, 40(1), 1–34.
File: `ferragne2010-formants-13-accents.pdf` (+ `.txt`, CNRS author copy). Table 3,
median F1/F2 in Hz at the temporal midpoint, Standard Southern English (`sse`, London,
6 men, recorded 2003), Praat Burg, Bark-smoothed then back to Hz:

| word | vowel | F1 | F2 |
|---|---|---|---|
| heed | iː | 273 | 2289 |
| hid | ɪ | 386 | 2038 |
| head | e | 527 | 1801 |
| had | æ | 751 | 1558 |
| hard | ɑː | 655 | 1044 |
| hod | ɒ | 552 | 986 |
| hoard | ɔː | 452 | 793 |
| hood | ʊ | 397 | 1550 |
| who'd | uː | 291 | 1672 |
| Hudd | ʌ | 623 | 1370 |
| heard | ɜː | 527 | 1528 |

Medians, no SDs: use Deterding's floored SDs as the tolerance. Note how far GOOSE and FOOT
have fronted (who'd F2 1672 vs Deterding's 1131) — the reference generation matters.

## 3. Diphthongs (approximation, say so on screen if it matters)

No open source with an RP diphthong table in Hz was found: Ferragne & Pellegrino 2010
plot diphthongs only as z-scored Bark values; Williams & Escudero (2014, JASA 136:2751)
and Bjelaković (2017, English Language & Linguistics, BBC newsreaders: FACE, PRICE,
MOUTH, GOAT) are closed. Used instead: onset and offset targets from the monophthong
anchors that describe RP diphthongs (Wells 1982 §3.2): eɪ = e→ɪ, aɪ = [a]→ɪ with [a]
taken as the mean of æ and ʌ, aʊ = [a]→ʊ, əʊ = ə→ʊ (ə has no reference: GOP only), each
end graded with double tolerance and the two averaged; GOP carries the rest.

## 4. Stops: voice onset time

Lisker, L., & Abramson, A. S. (1964). *A cross-language study of voicing in initial
stops: acoustical measurements.* Word, 20(3), 384–422. doi:10.1080/00437956.1964.11659830.
Text only (publisher PDF blocked). The English means for word-initial stops in isolated
words, as reproduced across the literature: /b/ 1, /d/ 5, /g/ 21 ms (short lag);
/p/ 58, /t/ 70, /k/ 80 ms (long lag). Category ranges quoted by the open SLRF 2017 paper
(`slrf2017-vot-bilingual-korean-english.pdf`): voiced ≈ −90 ms, voiceless unaspirated
≈ +10 ms, voiceless aspirated ≈ +75 ms; it also quotes Yang (1993) word-initial English
means p 77 (47–142), t 95 (54–193), k 88 (45–131) ms.

Grading: measured VOT (burst = onset of high-band energy after the closure, voicing =
first voiced pitch frame after it) vs the Lisker–Abramson mean, tolerance 25 ms, only for
word-initial stops before a vowel; medial and final stops fall back to GOP.

## 5. Fricatives: spectral mean

Jongman, A., Wayland, R., & Wong, S. (2000). *Acoustic characteristics of English
fricatives.* JASA, 108(3), 1252–1263. Text only (publisher PDF blocked); /s/ spectral
mean 6133 Hz is the one value quoted openly.

Haley, K. L., Seelinger, E., Mandulak, K. C., & Zajac, D. J. (2010). *Evaluating the
spectral distinction between sibilant fricatives through a speaker-centered approach.*
Journal of Phonetics, 38(4), 548–554. PMC3027155 (open, text only). Spectral mean at
50 ms into the fricative, American English: men /s/ 6.3 kHz (individuals 6.0–6.4),
/ʃ/ 4.2 kHz (3.9–4.6); women /s/ 7.9, /ʃ/ 5.2 kHz.

Li, F. (2007). *Spectral measures for sibilant fricatives of English, Japanese and
Mandarin Chinese.* ICPhS XVI. File: `li2007-sibilant-spectral-measures.pdf` (+ `.txt`).

Grading: centre of gravity over the middle 50 % of the aligned fricative (pre-emphasised,
above 500 Hz) vs the male means for /s z/ (6.3 kHz) and /ʃ ʒ/ (4.2 kHz), tolerance
700 Hz. Non-sibilants (f v θ ð h) have flat, weak spectra and no usable single target:
GOP only.

Jongman, A. (2024). *Phonetics of fricatives.* Oxford Research Encyclopedia of Linguistics.
File: `jongman2024-phonetics-of-fricatives.pdf` (+ `.txt`), the survey of the cues.

## 6. Everything else

Nasals (m n ŋ), approximants (l ɹ j w), /h/, affricates (tʃ dʒ), schwa, happY-i: GOP only.
The dark-/l/ F2 rule and the ending-F3 r-colouring test from the phonetics reels still
apply where relevant.
