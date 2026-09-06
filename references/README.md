# References — vowel formant standards

Everything fetched from the internet for the phonetics-video format lives here, so the
format can be reproduced offline.

**Public-repo note:** the two paper PDFs and their extracted `.txt` files are NOT
redistributed here (they are copyrighted articles). The rows below keep their Wayback
Machine URLs so you can fetch them yourself; the raw data tables, transcribed appendix
tables and derived `.csv` files ARE included.

## Hillenbrand et al. (1995) — the academic standard used

Hillenbrand, J., Getty, L. A., Clark, M. J., & Wheeler, K. (1995). *Acoustic
characteristics of American English vowels.* Journal of the Acoustical Society of
America, 97(5), 3099–3111. — The modern replication/extension of Peterson & Barney
(1952): 45 men, 48 women, 46 children; 12 American English vowels in /hVd/ words
("had", "head", "hod", …), with steady-state F0/F1/F2/F3 per token.

| File | What it is | Source |
|---|---|---|
| `hillenbrand1995-acoustic-characteristics.pdf` | The full paper (author's copy) | Wayback Machine capture of `homepages.wmich.edu/~hillenbr/Papers/HillenbrandGettyClarkWheeler.pdf` |
| `hillenbrand1995-acoustic-characteristics.txt` | Text extracted from the PDF (pypdf) | derived locally |
| `hillenbrand-vowdata.dat` | The RAW dataset: 1,668 tokens, one line each (`m01ae …` = man 01, vowel "ae"), duration/F0/F1/F2/F3 at steady state. Zeros = unmeasurable. | Wayback Machine capture of `homepages.wmich.edu/~hillenbr/voweldata/vowdata.dat` |
| `hillenbrand-voweldata-page.html` | The data's original documentation page (column layout, vowel codes) | Wayback capture of `homepages.wmich.edu/~hillenbr/voweldata.html` |
| `hillenbrand1995-means.csv` | Per-group, per-vowel mean ± SD of F0/F1/F2, computed from the raw data by `tools/scripts/hillenbrand_means.py` | derived locally |

Note: `homepages.wmich.edu/~hillenbr/` is dead (redirects to wmich.edu since ~2023-2024);
the Wayback Machine (`web.archive.org/web/<year>id_/<url>`) is the reliable source.

Key men's values used as targets (steady state, mean ± SD, from the raw data):

| vowel | example | F1 | F2 |
|---|---|---|---|
| /æ/ | had | 591 ± 42 | 1930 ± 133 |
| /ɛ/ | head | 588 ± 41 | 1803 ± 117 |

Caveat for comparisons: Hillenbrand's speakers are 1990s Michigan (Northern Cities)
talkers with a notably raised/fronted /æ/ (F2 ~1930). Modern General American /æ/ sits
somewhat lower/backer, so a measured F2 of ~1750–1850 is less alarming than the raw
SD-distance suggests. F1 (openness) is the more diagnostic axis for /æ/ vs /ɛ/.

## Peterson & Barney (1952) — the older classic

Peterson, G. E., & Barney, H. L. (1952). *Control methods used in a study of the
vowels.* JASA, 24(2), 175–184. Not stored here (paywalled); its men's /æ/ mean is
F1 660 / F2 1720 — closer to modern General American than Hillenbrand's Michigan /æ/.

## Deterding (1997) — the RP / British standard, added 2026-09-04

Deterding, D. (1997). *The formants of monophthong vowels in Standard Southern British
English pronunciation.* Journal of the International Phonetic Association, 27, 47–55.
— 5 male + 5 female BBC broadcasters from the MARSEC corpus, 11 SSB monophthongs,
~10 tokens per vowel per speaker, LPC formant tracks over digital spectrograms.

**Why this exists alongside Hillenbrand.** Hillenbrand is *American*. It has no /ɒ/ at
all, and its only NURSE vowel is r-coloured /ɝ/. Grading a British speaker's /ɒ/ and
/ɜː/ against it fails them for having a British accent rather than for mispronouncing
anything. Use Deterding for RP word lists, Hillenbrand for American ones.

| File | What it is | Source |
|---|---|---|
| `deterding1997-ssbe-formants.pdf` | The full paper | Wayback capture of `repository.nie.edu.sg/bitstream/10497/14152/1/JIPA-27-47.pdf` |
| `deterding1997-ssbe-formants.txt` | Text extracted from the PDF (pypdf) | derived locally |
| `deterding1997-perspeaker.dat` | Appendix Tables A1/A2: F1/F2/F3 per vowel **per speaker** (5 men, 5 women), connected speech. The only source of a spread. | transcribed from the PDF appendix |
| `deterding1997-citation.dat` | Tables 3/4 "citation" columns — F1/F2 for **citation forms**, from Deterding (1990). Means only. | transcribed from the PDF |
| `deterding1997-means.csv` | Citation-form means + between-speaker SDs, computed by `tools/scripts/deterding_means.py` | derived locally |

The NIE repository is behind an AWS WAF CAPTCHA on direct `curl`; the Wayback Machine
(`web.archive.org/web/2020id_/<url>`) fetches it fine — same trick as Hillenbrand.

`deterding_means.py` **asserts** that the per-vowel means of the transcribed appendix
reproduce the paper's own published Table 2 (all 11 men's vowels, ±1 Hz). If that
assertion ever fails, the `.dat` transcription is wrong — fix it before trusting output.

Men's citation values used as RP targets (F1 / F2 in Hz, SD from the appendix):

| vowel | keyword | F1 ± SD | F2 ± SD |
|---|---|---|---|
| /ɛ/  | DRESS  | 560 ± 30  | 1797 ± 218 |
| /æ/  | TRAP   | 732 ± 139 | 1527 ± 156 |
| /ɑː/ | START  | 687 ± 70  | 1077 ± 41  |
| /ɒ/  | LOT    | 593 ± 55  | 866 ± 72   |
| /ʌ/  | STRUT  | 695 ± 66  | 1224 ± 71  |
| /ɜː/ | NURSE  | 513 ± 39  | 1377 ± 141 |
| /ɔː/ | THOUGHT| 453 ± 24  | 642 ± 92   |
| /ʊ/  | FOOT   | 414 ± 10  | 1051 ± 146 |
| /uː/ | GOOSE  | 302 ± 21  | 1131 ± 204 |

### Three caveats before grading against this

1. **The SDs are between-speaker over n=5**, not per-token over 45 speakers like
   Hillenbrand's. Some collapse implausibly tight — /ʊ/ F1 ± 10 Hz is an artefact of
   five broadcasters agreeing, not evidence that a 35 Hz deviation is 3.5 SD of error.
   **Floor the SD** before feeding `GRADE_BANDS`, or NURSE and FOOT will fail everybody.
2. **Means are citation forms, SDs are connected speech** — the two columns come from
   different recordings (Deterding 1990 vs MARSEC). Documented in the script's docstring.
   The `f1_connected`/`f2_connected` columns carry the connected-speech means if needed.
3. **Deterding avoided vowels before /l/** because of coarticulation. A dark-L word like
   "pull" or "pool" therefore has no clean counterpart here — the existing dark-L rule
   (grade on F1, tolerance ×2) still applies, and F2 must not be graded at all.

## Age-graded RP: Hawkins & Midgley (2005) — NOT stored, paywalled

Hawkins, S. & Midgley, J. (2005). *Formant frequencies of RP monophthongs in four age
groups of speakers.* JIPA 35(2), 183–199. 20 male RP speakers (5 each aged 20–25,
35–40, 50–55, 65–73 in 2001), 11 monophthongs in **/hVd/ citation frames**. Cambridge
paywalls it and no open copy was found. Its headline finding is worth knowing anyway:
younger speakers have **higher F1 in /ɛ/ and especially /æ/**, and **higher F2 in /uː/
and /ʊ/** (GOOSE-fronting) than Deterding's 1990s broadcasters. So a young British
speaker measuring open-/æ/ and fronted-/uː/ against Deterding is drifting in the
direction the literature predicts for their generation — report that as a generational
shift, not as an error. If access is ever obtained, its 20–25 men's table is the single
best reference for this speaker and should replace Deterding as the default.
