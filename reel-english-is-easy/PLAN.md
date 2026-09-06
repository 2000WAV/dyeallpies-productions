# Build plan — "English is easy" reel (2026-09-04)

Source facts and measurements: [NOTES.md](NOTES.md). Reference provenance:
[`references/README.md`](../references/README.md).

## The story

Nine words, one consonant frame (/pVt/-ish), nine different vowels. Graded against a
**British** reference (Deterding 1997), eight land within 1.25 SD — and **/ɜː/ "pert"
sits +4.65 SD on F1 with F2 dead on (+0.12 SD)**. So the punchline is not "English is
hard, look at all these vowels", it is sharper:

> Eight A's and one F — and the F is a single millimetre of tongue height.

Grades via the existing `vowel_map.GRADE_BANDS` (A+ <=1 SD ... F >4 SD):

| word | IPA | F1 (RP ref) | F2 (RP ref) | grade |
|---|---|---|---|---|
| pet  | /pɛt/  | 580 (560±40)  | 1693 (1797±218) | A+ |
| pat  | /pæt/  | 831 (732±139) | 1525 (1527±156) | A+ |
| part | /pɑːt/ | 721 (687±70)  | 1021 (1077±80)  | A+ |
| pot  | /pɒt/  | 576 (593±55)  |  832 (866±80)   | A+ |
| putt | /pʌt/  | 643 (695±66)  | 1159 (1224±80)  | A  |
| pert | /pɜːt/ | **699 (513±40) +4.65 SD** | 1394 (1377±141) | **F** |
| port | /pɔːt/ | 432 (453±40)  |  697 (642±92)   | A+ |
| pull | /pʊl/  | 449 (414±40)  |  719 — dark-L, F2 not gradable | A+ |
| pool | /puːl/ | 352 (302±40)  | 1382 — dark-L, F2 not gradable | A+ |

Two secondary findings worth one line of screen time each:
- **pool is fronted** (F2 1382 despite a dark /l/ pulling it back) — the documented
  young-RP GOOSE-fronting, i.e. drifting the way the literature predicts for his
  generation, not an error.
- **pert came out [ɐː]**, an open central vowel, not [ɜː].

## Structure — locked to the song's own grid

The track gives **two bass-marked transitions on exact downbeats** (see NOTES.md):
**27.52 s** and **62.49 s**. Those are the two word slots. Timings below are in the
song's timebase, so the export tells the user where to start the audio in Instagram.

| # | song time | shot | source | content |
|---|---|---|---|---|
| 1 | 10.0-14.4 s | hook   | `01-lookup` | "ENGLISH IS EASY" stacked in 6 languages above him; he looks up, unconvinced |
| 2 | 14.4-18.8 s | claims | `02-walk`   | the easy-English myths, one per bar, cycling languages |
| 3 | 18.8-23.2 s | claims | `02-walk`   | ditto — sway + face-anchored punch-in on the beat |
| 4 | 23.2-27.5 s | doubt  | `04-doubt` / `07-stare-long` | "should I really show you?" -> "let me show you" (`03-invite`) |
| 5 | **27.52 s** | **DROP 1** | `12-words-c` | **9 vowels, one per beat** (4.9 s) — words + IPA + the ridgeline panel. No grades yet: this is the "there are NINE of these" reveal |
| 6 | 33-60 s   | breathe | `05-filler` / `06-stare-short` | the vowel floor fills in, puck trail showing all nine positions |
| 7 | **62.49 s** | **DROP 2** | `12-words-c` | **the verdict** — same nine, now stamped. Eight A's land... and /ɜː/ comes up F |
| 8 | 67-73 s   | punchline | `05-filler` | "your tongue was 1 mm too low" |

Two nine-word slots is what the song affords — **not three**, and in any case the b-
and h-frames are unusable (NOTES.md). Slot 2 re-uses the *same* nine words rather than
a second word set, which is stronger anyway: drop 1 poses the problem, drop 2 delivers
the judgement, and every frame on screen is data we have actually verified.

### Shot 1 — the title, in six languages

All verified to render (libass has harfbuzz + fribidi):
EN "ENGLISH IS EASY" / PT "INGLÊS É FÁCIL" / ES "EL INGLÉS ES FÁCIL" /
TR "İNGİLİZCE KOLAY" / AR "الإنجليزية سهلة" / HI "अंग्रेज़ी आसान है".

### Shots 2-3 — the myths, while walking (user request)

One claim per bar (2.186 s), each in a different language, stacking up as he walks so
the screen crowds with confident wrong opinions. The aim is to set up **pronunciation**
as the thing none of them mention.

| claim | PT | ES | TR | AR | HI |
|---|---|---|---|---|---|
| GRAMMAR IS EASY | A GRAMÁTICA É FÁCIL | LA GRAMÁTICA ES FÁCIL | DİL BİLGİSİ KOLAY | القواعد سهلة | व्याकरण आसान है |
| THE VERBS BARELY CHANGE | OS VERBOS QUASE NÃO MUDAM | LOS VERBOS CASI NO CAMBIAN | FİİLLER NEREDEYSE HİÇ DEĞİŞMEZ | الأفعال لا تتغير تقريبًا | क्रियाएँ लगभग नहीं बदलतीं |
| NO GENDERS, NO CASES | NÃO TEM GÊNERO NEM CASO | NO HAY GÉNEROS NI CASOS | CİNSİYET YOK, HÂL YOK | لا تذكير ولا تأنيث | न लिंग, न कारक |
| ONLY THE SPELLING IS HARD | SÓ A ESCRITA É DIFÍCIL | SOLO LA ESCRITURA ES DIFÍCIL | SADECE YAZIMI ZOR | الإملاء فقط صعب | बस वर्तनी कठिन है |

Every one of these is *true*, which is what makes the turn land: none of them is about
pronunciation. The last card before the drop is the one nobody says —
"NOBODY WARNS YOU ABOUT THE VOWELS".

## The panel redesign (replaces the heatmap spectrogram)

User asked for something friendlier, line-based and lightly 3D. Plan:

1. **Waterfall ridgeline.** Successive spectral slices drawn as glowing polylines,
   stacked receding into fake 3D (each line offset up+right, back lines dimmer and
   thinner, front line brightest). F1 and F2 read as two travelling ridges instead of a
   heat smear. This is the same data as the spectrogram, drawn the classic waterfall
   way — it stays honest, it animates well on a beat, and it is legible at phone size.
2. **Perspective vowel floor.** F1xF2 as a floor grid in perspective, with a glowing
   puck that snaps to each vowel as it is spoken and leaves a fading trail. The RP
   reference zones sit on the floor as soft ellipses, so "inside the ellipse = A" is
   readable without knowing what a formant is.
3. Keep from the current pipeline: per-word windows, progressive reveal, the grade
   stamp, the meaning emoji, the studied-vowel colour highlight.

New renderer, so `render_freq_panel.py` is left alone and a sibling script is added.

## Audio and delivery

Two exports, per the user's decision:
- `out/reel-muted.mp4` — **silent**, for upload. The song is added inside Instagram from
  its licensed library. Burning a commercial track in is what gets Reels muted or
  suppressed, so the upload file carries no audio at all.
- `out/reel-preview.mp4` — same picture, with the song and the word takes audible, for
  the user to check the sync before posting. **Never uploaded.**

The song file is a **local timing reference only**: extract the beat grid, cut to it,
then delete the recording. It is not committed and not redistributed.

## Build order

1. ~~Beat grid~~ **DONE** — 109.78 BPM, first beat 1.281 s, drops at 27.52 s / 62.49 s.
2. Match the trend's motion from a reference video the user supplies — **BLOCKED**.
   (Deliberately not researched by web search: trend/tutorial results are unreliable
   and sometimes malware-bait. A screen recording the user provides is the safe source.)
3. Pick the single best take per word from the 3 available (27 takes -> 9).
4. Add the 9 RP vowels + dark-L rules to `vowel_map.py`; wire `GRADE_BANDS` to the
   Deterding reference with the SD floor.
5. Build the new ridgeline + vowel-floor renderer.
6. Cut shots 1-4 to the grid; face-tracked punch-in (mediapipe/cv2 are in `.venv-pushup`).
7. Compose, verify decode, export both files, write the Instagram caption.

## Open questions for the user

- A **reference video of the trend**, so the sway/punch-in/transition timings are
  measured rather than guessed. This is the only remaining blocker.
- Shot 4 has three candidates (`04-doubt`, `06-stare-short`, `07-stare-long`).
- Confirm the video should start at song 10.0 s (so drop 1 lands ~17 s in). Starting
  later makes a tighter reel; starting at 0 gives a 27 s run-up, which is long.
