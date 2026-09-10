# Push-up surface EMG: muscle activation by variant and phase

Literature sweep for the push-up muscle model's per-muscle "heat" map, built to the same
conventions as `../pullup-science/01-emg-and-anatomy.md` and `07-phase-resolved-emg.md`. Raw
data extracted into `data/pushup-emg-by-study.csv` (whole-rep and variant table) and
`data/pushup-phase-emg.csv` (phase-resolved rows). Abstracts in `abstracts/*.txt`, full text
where it could be fetched in `papers/`, full download log in `DOWNLOADS.md`.

Every number below is attributed to a study. A row that only reports significance/direction (no
recoverable number) says so. Anything not found in a primary source is marked **NOT FOUND** —
none of those are invented. 37 studies are cited; 24 are primary EMG studies of the push-up or a
push-up-plus variant, 5 are systematic reviews/meta-analyses that pool dozens more named studies
(their raw per-study numbers, where recoverable, are folded into the CSV and cited as "via
[review], PMID/table"), and 8 are kinetics/kinematics-only context citations (no EMG) kept
because the brief asked for kinetic/plyometric context around the EMG picture.

**The single biggest caveat for this whole file:** unlike the pull-up literature (which mostly
converges on one MVIC-testing convention), push-up EMG studies normalise to wildly different
references — some to the muscle's own isometric MVIC, some (Alizadeh 2020) to a *different
exercise's* MVIC, some (Intziegianni 2026) to the muscle's own peak activity *within the push-up
itself*, and reported floor-condition pectoralis major ranges from 13% MVIC (Batbayar 2015,
push-up **plus**) to 105% MVIC (Youdas 2010, standard push-up) depending on lab and method. Never
divide a value from one study by a value from another study to build a ratio — every ratio in
§4 below is computed **within one study**, from that study's own muscles measured under its own
MVIC test.

## 1. Master table — %MVIC per muscle per study per variant per phase

Full detail (n, population, normalisation, notes) is in `data/pushup-emg-by-study.csv` (137
rows). Condensed here to the standard (shoulder-width, hands-and-feet-on-floor) push-up baseline
plus the variants named in the brief; "direction only" means the study reported a
significance/direction finding with no recoverable %MVIC number.

### 1a. Standard (shoulder-width) push-up — whole rep

| study | n | muscle | value | unit |
|---|---|---|---|---|
| Youdas et al. 2010 (PMID 20664364) | 20 | triceps brachii | 73-109 %MVIC | whole rep, range across hand positions |
| Youdas et al. 2010 | 20 | pectoralis major | 95-105 %MVIC | whole rep |
| Youdas et al. 2010 | 20 | serratus anterior | 67-87 %MVIC | whole rep |
| Youdas et al. 2010 | 20 | posterior deltoid | 11-21 %MVIC | whole rep (posterior, not anterior, deltoid) |
| Snarr & Esco 2013 (PMID 24511343) | 21 | pectoralis major | 63.62±16.4 %MVC | whole rep |
| Snarr & Esco 2013 | 21 | anterior deltoid | 58.91±20.3 %MVC | whole rep |
| Snarr & Esco 2013 | 21 | triceps brachii | 74.32±16.9 %MVC | whole rep |
| Calatayud et al. 2014 (JSSM, PMID 25177174) | 29 | pectoralis major (clavicular) | 29.60±1.88 (SE) %MVIC | whole rep — **highest** of 5 conditions tested |
| Calatayud et al. 2014 (JSSM) | 29 | anterior deltoid | 26.22±1.46 (SE) %MVIC | whole rep — **highest** of 5 conditions |
| Calatayud et al. 2014 (JSSM) | 29 | triceps brachii | 17.14±1.31 (SE) %MVIC | whole rep — **lowest** of 5 conditions |
| Calatayud et al. 2014 (JSSM) | 29 | upper trapezius | 5.90±0.56 (SE) %MVIC | whole rep — lowest of 5 conditions |
| Calatayud et al. 2014 (JSSM) | 29 | rectus abdominis | 23.85±2.80 (SE) %MVIC | whole rep |
| Calatayud et al. 2014 (JSSM) | 29 | rectus femoris (quadriceps) | 7.45±0.72 (SE) %MVIC | whole rep |
| Calatayud et al. 2014 (JSSM) | 29 | erector spinae (lumbar) | 2.03±0.14 (SE) %MVIC | whole rep |
| Borreani et al. 2015 (JESF, PMID 29541105) | 30 | anterior deltoid | 78.54±4.39 (SE) %MVIC | whole rep |
| Borreani et al. 2015 (JESF) | 30 | serratus anterior | 29.07±3.76 (SE) %MVIC | whole rep — **lowest** of 5 conditions |
| Borreani et al. 2015 (JESF) | 30 | lumbar multifidus | 3.97±0.43 (SE) %MVIC | whole rep |
| Borreani et al. 2015 (JESF) | 30 | rectus femoris (quadriceps) | 20.55±1.69 (SE) %MVIC | whole rep |
| Borreani et al. 2015 (Phys Ther Sport, PMID 25882770) | 29 | triceps brachii (long head) | 17.14±1.31 (SE) %MVIC | whole rep, stable/floor |
| Borreani et al. 2015 (PTS) | 29 | upper trapezius | 5.83±0.58 (SE) %MVIC | whole rep, stable/floor |
| Cogley et al. 2005 (PMID 16095413, via Kowalski et al. 2022) | 40 | triceps brachii | 101.3±85.4 %MVIC | whole rep — huge SD, flagged |
| Freeman et al. 2006 (PMID 16540847, via Kowalski et al. 2022) | 10 | triceps brachii | 66.0±17.6 %MVC | whole rep |
| Freeman et al. 2006 (via Kowalski et al. 2022) | 10 | pectoralis major | 61.2±38.3 %MVC | whole rep |
| Tahani et al. 2026 (PMID 42218292), healthy (WSD) subgroup | 15 | erector spinae | 6.63±4.99 %MVIC | whole rep |
| Tahani et al. 2026, WSD | 15 | multifidus | 5.24±3.2 %MVIC | whole rep |
| Tahani et al. 2026, WSD | 15 | **gluteus medius** | 5.24±2.01 %MVIC | whole rep — only gluteus number found in the entire search |
| Tahani et al. 2026, WSD | 15 | external oblique | 13.84±7.11 %MVIC | whole rep |
| Tahani et al. 2026, WSD | 15 | transversus abdominis/internal oblique | 18.75±8.13 %MVIC | whole rep |
| Tahani et al. 2026, WSD | 15 | rectus abdominis | 21.94±9.67 %MVIC | whole rep |
| Tahani et al. 2026, WSD | 15 | serratus anterior | 24.04±6.12 %MVIC | whole rep |

### 1b. Hand-width variants (narrow / wide / diamond vs shoulder-width)

| study | n | comparison | muscle | finding |
|---|---|---|---|---|
| Cogley et al. 2005 | 40 | narrow vs wide | pectoralis major, triceps brachii | narrow > wide, P<0.05 (no % in abstract) |
| Gouvali & Boudolos 2005 (PMID 15705025) | 8 | posterior-hand vs normal | pectoralis major | posterior > normal |
| Gouvali & Boudolos 2005 | 8 | posterior-hand vs normal | triceps brachii | posterior < normal |
| Marcolin et al. 2015 (PMID 26488636) | 8 | narrow vs wide vs standard | triceps brachii, pectoralis major | narrow-base variant gave the greatest activation of both (no % recoverable) |
| Batbayar et al. 2015 (PMID 26357442), push-up **plus** | 9 | 30% narrower than shoulder-width | serratus anterior | 80.7±32.1 %MVC, significant decrease vs shoulder-width 90.9±40.5, P=0.03 |
| Batbayar et al. 2015, push-up plus | 9 | 20% wider than shoulder-width | latissimus dorsi | 13.0±7.4 %MVC, significant decrease vs SW 16.6±12.1, P=0.04 |
| Intziegianni et al. 2026 (PMID 41892990) | 20 | diamond > standard > wide | pectoralis major, triceps brachii | diamond gave the highest normalized activation of both muscles, wide the lowest, P<0.05 |
| Youdas et al. 2010 | 20 | narrow base | triceps brachii, posterior deltoid | narrow base was most effective for these two of the 4 muscles measured |

### 1c. Instability / suspension variants (vs stable floor, within-study)

| study | n | condition | muscle | value |
|---|---|---|---|---|
| Snarr & Esco 2013 | 21 | suspension push-up | pectoralis major | 69.54±27.6 %MVC (vs 63.62±16.4 traditional, P<0.05) |
| Snarr & Esco 2013 | 21 | suspension push-up | anterior deltoid | 81.13±17.77 %MVC (vs 58.91±20.3 traditional, P<0.05) |
| Snarr & Esco 2013 | 21 | suspension push-up | triceps brachii | 105.83±18.54 %MVC (vs 74.32±16.9 traditional, P<0.05) |
| Borreani et al. 2015 (JESF) | 30 | TRX suspension trainer | serratus anterior | 75.48±9.42 %MVIC, significantly higher than floor's 29.07±3.76, P<0.001 |
| Borreani et al. 2015 (JESF) | 30 | TRX suspension trainer | rectus femoris | 37.86±3.65 %MVIC, TRX only device to raise this above the other 4 conditions |
| Borreani et al. 2015 (JESF) | 30 | 4 unstable devices (wobble/disc/dome/TRX) pooled | anterior deltoid | **no** significant difference vs floor, P=0.130 |
| Borreani et al. 2015 (PTS) | 29 | suspended, 10cm height | triceps brachii | 37.03±1.80 %MVIC (vs 17.14±1.31 stable, P<0.05) |
| Borreani et al. 2015 (PTS) | 29 | suspended, 10cm height | upper trapezius | 14.69±1.91 %MVIC (vs 5.83±0.58 stable, P<0.05) |
| Calatayud et al. 2014 (JSSM) | 29 | AirFit Trainer Pro (pulley) suspension | global mean, 7 muscles | 37.76±2.27 %MVIC (vs floor 16.75±0.67, P<0.001) — floor was the **lowest** of the 5 conditions on this global measure |
| Kang et al. 2019, meta-analysis (PMID 31584855) | 213 pooled | unstable vs stable, push-up plus | serratus anterior | mean difference 0.01% MVIC, 95% CI -4.90 to 4.92 — **no significant difference** |
| Kang et al. 2019, meta-analysis | 213 pooled | unstable vs stable, push-up plus | upper trapezius | mean difference -2.85% MVIC, 95% CI -5.51 to -0.19 — significantly **more** UT on unstable |
| Arghadeh et al. 2023, meta-analysis (PMID 38116582) | 38 studies | unstable vs stable, push-up | upper trapezius | SMD 0.425 (95% CI 0.077-0.773), P=0.017 |
| Arghadeh et al. 2023 | 38 studies | unstable vs stable, push-up plus | middle trapezius | SMD 0.672 (95% CI 0.225-1.119), P=0.003 |
| Arghadeh et al. 2023 | 38 studies | unstable vs stable, push-up plus | serratus anterior | SMD 0.216 (95% CI 0.011-0.420), P=0.039 |
| Arghadeh et al. 2024, meta-analysis (PMID 38840951) | 28 studies | unstable vs stable, push-up | anterior deltoid | SMD **-0.630** (95% CI -1.205 to -0.055), P=0.032 — **decreases** on unstable |
| Arghadeh et al. 2024 | 28 studies | unstable vs stable, push-up | pectoralis major | SMD 0.282 (95% CI 0.079-0.484), P=0.006 |
| Arghadeh et al. 2024 | 28 studies | unstable vs stable, push-up | triceps brachii | SMD 0.813 (95% CI 0.457-1.168), P<0.001 |
| Arghadeh et al. 2024 | 28 studies | unstable vs stable, push-up **plus** | pectoralis major | SMD 0.207 (95% CI -0.194-0.609), **not** significant — only stands out for plain PU/knee PU, not push-up plus |
| Freeman et al. 2006 (via Kowalski et al. 2022) | 10 | unstable (labile ball under hands) | triceps brachii | 68.9±16.2 %MVC (vs standard 66.0±17.6) |
| Freeman et al. 2006 (via Kowalski et al. 2022) | 10 | unstable (labile ball under hands) | pectoralis major | 68.7±39.9 %MVC (vs standard 61.2±38.3) |

**Reconciling the instability picture:** the two 2023/2024 Arghadeh meta-analyses (38 and 28
pooled studies) and the Kang 2019 meta-analysis (11 pooled studies) are the most authoritative
sources here because they pool many primary studies. Their combined picture for a plain
(non-plus) push-up on an unstable surface: **pectoralis major and triceps brachii go up**,
**anterior deltoid goes down**, **upper trapezius goes up**, and **serratus anterior does not
change** on a plain push-up but **does** go up specifically during a push-up **plus** (where the
scapular protraction movement itself, not general instability, is what drives serratus). This
mostly agrees with the single-study numbers above (Snarr, Borreani, Freeman) but the anterior
deltoid finding is the one place a single study (Snarr & Esco, suspension push-up) shows an
*increase* where the pooled meta-analytic evidence shows a *decrease* — Snarr's suspension
device and the Arghadeh reviews' pooled "unstable surface" studies (BOSU, wobble board, stability
disc) are not the same kind of instability, and this file does not average across that
difference.

### 1d. Elevation variants (incline / decline / hands-elevated)

| study | n | variant | muscle | value / finding |
|---|---|---|---|---|
| Escamilla et al. 2010 (PMID 20436242) | 18 | decline push-up (feet on Swiss ball) | latissimus dorsi | 17-25 %MVIC — decline push-up was in the **high** group |
| Escamilla et al. 2010 | 18 | decline push-up | rectus femoris (quadriceps) | 6-10 %MVIC — decline push-up was in the **low** group |
| Escamilla et al. 2010 | 18 | decline push-up | rectus abdominis, external/internal oblique | within a 7-73% MVIC range across 10 exercises; decline-push-up-specific value not separable from the abstract — **NOT FOUND** as an isolated number |
| Kowalski et al. 2022, scoping review (PMID 35599715) | 30 studies pooled | incline on stable surface | global mean, all muscles | 15.8±13.4 %MVIC — **lowest** of the 6 push-up types reviewed |
| Kowalski et al. 2022 | 30 studies pooled | incline on a ball | global mean | 26.1±20.7 %MVIC |
| Kowalski et al. 2022 | 30 studies pooled | incline (either surface) | serratus anterior | one of the two push-up types (with push-up plus) where SA has the **highest** amplitude of any muscle |
| Ebben et al. 2011 (PMID 21873902, kinetics only) | 23 | hands elevated 30/61cm | whole-body peak GRF | **lower** GRF than all other variants tested, P≤0.05 (no EMG) |
| Ebben et al. 2011 | 23 | feet elevated (decline) 30/61cm | whole-body peak GRF | **higher** GRF than all other variants, P≤0.05 (no EMG) |

### 1e. Knee push-up (modified)

| study | n | muscle | value |
|---|---|---|---|
| Lim 2021 (PMID 34946362), knee push-up plus | 40 | pectoralis major | 88.28±11.40 %MVIC |
| Lim 2021 | 40 | lower trapezius | 34.91±6.95 %MVIC |
| Lim 2021 | 40 | serratus anterior | 44.88±3.69 %MVIC |
| Lim 2021 | 40 | upper trapezius | 26.86±5.44 %MVIC |
| Gottschall et al. 2018 (PMID 29809073) | 12 | primary movers, toes vs knees | no significant difference between toes and knees for primary-mover %contribution (direction only, no %) |
| Suprak et al. 2011 (PMID 20179649, kinetics only) | 28 | modified (knee) vs traditional | whole-body %BM supported | modified push-up shows a **greater** top-to-bottom % change in load than traditional (no EMG) |
| San Juan et al. 2015 | 22 | modified (knee) push-up plus vs traditional | serratus anterior | traditional > modified by up to 22 percentage points, P<0.05; SA activity pattern across the rep is also different (see §2) |

### 1f. Plyometric push-up

No EMG study of plyometric/explosive push-ups was found. Dhahbi et al. 2017 (PMID 27193045),
Zalleg et al. 2020 (PMID 30095736) and the Dhahbi et al. 2022 kinetic systematic review (PMID
30284496, 46 variants) all measure **ground-reaction-force kinetics only** — initial/peak GRF,
rate of force development, flight time, impact force — with **no surface EMG**. Dhahbi et al.
2026's pendulum biomechanical model (PMID 42072239) is a pure analytical/computational model of
flight time and power, again with no EMG. **Plyometric push-up %MVIC by muscle is NOT FOUND.**
The kinetic literature is real and is cited in the CSV for context (a plyometric/explosive
push-up clearly raises peak force and rate of force development vs a controlled push-up, per
these sources) but gives no muscle-by-muscle activation number to feed the heat map.

## 2. Phase-resolved section — concentric vs eccentric, and firing order within a rep

Full machine-readable version: `data/pushup-phase-emg.csv` (24 rows: muscle, phase, value, unit,
exercise, n, source, pmid_or_doi, measured_or_estimated, note).

### 2a. The cleanest phase-split finding in the whole literature: push-up phase vs plus phase

**Gioftsos et al. 2016** (PMID 27512278, n=13 men, push-up plus, 3 hand positions × stable/
unstable surface, all pooled by phase) is the only study located that cleanly splits a push-up-
plus rep into its two mechanically distinct phases (elbow extension = "push-up phase"; scapular
protraction at the top = "plus phase") and reports %MVIC for **both** phases on **three**
muscles:

| muscle | push-up phase | plus phase | direction |
|---|---|---|---|
| upper trapezius | 30.2±13.6 %MVIC | 24.1±8.5 %MVIC | **push-up phase higher**, P<0.05, F=8.3 |
| lower trapezius | 9.8±11.1 %MVIC | 4.1±3.8 %MVIC | **push-up phase higher**, P<0.05, F=7.1 |
| serratus anterior | 49.2±17.9 %MVIC | 75.9±16.1 %MVIC | **plus phase higher**, P<0.001, F=72.9 |
| UT/LT ratio | 6.0±4.5 | 8.1±4.3 | ratio also significantly higher in the plus phase, P<0.05 |

This is a real within-rep firing-order result with numbers and significance on both sides: the
trapezius (both upper and lower) does most of its work during the elbow-extension push-up phase,
while serratus anterior's role is concentrated in the scapular-protraction plus phase — and the
serratus effect (F=72.9) is far larger than either trapezius effect (F=7.1-8.3).

### 2b. Serratus anterior's role in a rep WITHOUT an explicit "plus" — traditional vs modified

**San Juan et al. 2015** (PMID 25881172, n=22) measured SA continuously across the elbow-
extension range of motion in both a traditional (full) and a modified (knee) push-up plus, and
found the two exercises put the SA peak in *different* places:

- In the **traditional** push-up plus, SA activity (45-57% MVC, this study's own measurement)
  rises across the concentric phase and **peaks at 55° of elbow extension — inside the
  concentric/push-up phase itself, before the plus movement starts.** The authors' own
  conclusion: "the plus-phase is not necessary" to get high SA activity out of a full (feet-on-
  floor) push-up.
- In the **modified (knee)** push-up plus, SA activity barely changes across the concentric phase
  (~3% change) and instead **peaks during the plus phase**, mirroring the Gioftsos finding above.

Read together, these two studies say the "SA needs a plus phase" assumption is knee-push-up-
specific, not a general push-up property — for a full, standard push-up, the model should let SA
build through the concentric (pushing-away) phase itself, not wait for an explicit protraction
movement that most standard-push-up reps don't even contain.

### 2c. Concentric vs eccentric for the prime movers — two studies, two different pictures

**Marcolin et al. 2015** (PMID 26488636, n=8, 12 muscles, 5 hand-position variants) found the
ascendant (concentric) phase produced **greater EMG than the descendant (eccentric) phase for
every one of the 12 muscles measured** — serratus anterior, anterior deltoid, erector spinae,
latissimus dorsi, rectus abdominis, triceps brachii (long+lateral heads), external oblique,
pectoralis major (sternal+clavicular heads), trapezius, biceps brachii — with the abdominal/
erector-spinae group showing a smaller concentric-to-eccentric drop than the arm/chest prime
movers (consistent with their role as continuous stabilizers rather than phasic movers). No
%MVIC numbers were recoverable from the text (data is in a figure only); this is a direction-only
finding but it is consistent across all 12 muscles and matches the general "concentric > eccentric"
result already established for the pull-up (Dickie et al. 2017, in `../pullup-science/`).

**Intziegianni et al. 2026** (PMID 41892990, n=20, pectoralis major & triceps brachii, standard/
diamond/wide) nuances this: **raw RMS (mV) is higher in concentric than eccentric for both
muscles (P<0.05)** — agreeing with Marcolin — **but once each repetition is normalized to its own
peak RMS within that push-up, the concentric-vs-eccentric difference disappears (P>0.05).** In
other words, absolute muscle output is higher pushing away than lowering down, but the *relative
effort* (how close to that rep's own peak each phase gets) is sustained near-maximally in both
directions. This is an important nuance for the model: a phase factor built from raw-amplitude
studies (like Marcolin) would show a sharp eccentric dip; a phase factor built from effort-
normalized data (like Intziegianni) would show almost no dip at all. **Treat the size of the
concentric>eccentric drop as method-dependent, not settled**, and prefer showing a modest dip
rather than a sharp one if the model needs to pick one behavior.

**Alizadeh et al. 2020** (PMID 32390722, n=20, push-up vs bench press to failure) additionally
found triceps and biceps brachii EMG were **significantly lower during the push-up's concentric
phase than during the bench press's concentric phase** (P=0.002, P=0.018) at a matched relative
load, and anterior deltoid was the one muscle/phase combination where the **push-up's eccentric
phase exceeded the bench press's eccentric phase** (P=0.03). These specific %values were
extracted from the paper's full text via an automated tool this session could not independently
re-verify against the original PDF table (PMC access was blocked by a bot-challenge) — **treat
the numeric magnitudes in this row as provisional**; the qualitative comparison (push-up demands
less peak triceps/biceps EMG than bench press at matched load, which is consistent with push-ups
being performable for far more reps — Alizadeh's own subjects did 53-77% more push-up than bench
press reps at that load) is stated directly in the abstract and is solid.

### 2d. No millisecond-scale onset-latency sequence exists for the push-up

Exactly as with the pull-up, **no study located this session timed which muscle switches on
first** in a push-up rep. The Gioftsos and San Juan findings above are genuine phase-*mean*
comparisons (push-up phase vs plus phase, or "peaks at 55° of elbow extension"), not an EMG-onset
time series. Any "X fires before Y by N milliseconds" claim for the push-up would be invented —
do not build one into the model.

## 3. Fatigue within a set — what exists and what does not

**No study measuring rep-by-rep %MVIC amplitude drift across a dynamic push-up set performed to
failure was found.** PubMed, Europe PMC and targeted searches for "push-up EMG fatigue",
"push-up EMG median frequency", and "push-up repetitions decline EMG" turned up no primary study
that tracks EMG amplitude (or even median/mean power frequency) rep-by-rep through a push-up set
to exhaustion. This specific curve — the one the brief asks for — is **NOT FOUND** and must not
be invented for the model.

The closest adjacent evidence:

- **Borstad et al. 2009** (PMID 19683822, n=28) is the only primary EMG-fatigue study located in
  a push-up-like posture, but it is a **sustained isometric hold** of scapular protraction at the
  top of a push-up (not dynamic reps), used to preferentially fatigue serratus anterior. The
  fatigue task **decreased median power frequency in all 4 shoulder muscles tested** (a classical
  EMG fatigue marker — motor unit firing rate slows as fatigue sets in) and increased subjective
  Borg CR10 fatigue ratings. It also found measurable *kinematic* consequences of that fatigue:
  decreased scapular posterior tilt and increased internal rotation afterward — a plausible
  mechanism linking push-up-position fatigue to subacromial impingement risk, but this is a
  kinematic finding, not an amplitude-vs-rep-number curve.
- **Alizadeh et al. 2020** (PMID 32390722) shows push-ups can be performed for far more
  repetitions than bench press at a matched relative load (men: 25.6±5.2 vs an equivalent bench
  load; women: 15.5±8.0), which is *performance* evidence that push-ups are a lower-intensity,
  more fatigue-resistant task relative to a muscle's ceiling — but this is a repetitions-to-
  failure count, not an EMG-amplitude-per-rep curve.
- **Dhahbi et al. 2017/2022** and **Zalleg et al. 2020** measure kinetic (GRF) reliability across
  trials, not fatigue-driven EMG amplitude change, and are not usable for this section.

**If the model needs a within-set fatigue behaviour for the push-up, it currently has no primary
EMG source to build it from** — any rep-to-rep amplitude curve used in the pipeline should be
marked ESTIMATE, exactly as the pull-up archive already flags its own hang-phase and onset-timing
estimates, and should say so on screen.

## 4. What the model should use — ordering for pec major / triceps / anterior deltoid / serratus

The brief's ordering test: give pec/triceps, deltoid/pec, serratus/pec ratios, each **computed
within one study** (per the incommensurability caveat in the header), for a standard shoulder-
width push-up.

| study (n) | triceps / pec | anterior deltoid / pec | serratus / pec | notes |
|---|---|---|---|---|
| Youdas et al. 2010 (n=20) | ≈0.91 (91/100, using range midpoints 73-109 over 95-105) | not measured (only posterior deltoid: ≈0.16) | ≈0.77 (77/100) | standard push-up, hand positions pooled; the one study with both SA and a prime-mover ratio for a genuinely standard (non-plus) push-up |
| Snarr & Esco 2013 (n=21) | 1.17 (74.32/63.62) | 0.93 (58.91/63.62) | not measured | traditional push-up |
| Calatayud et al. 2014, JSSM (n=29) | 0.58 (17.14/29.60) | 0.89 (26.22/29.60) | not measured | floor condition of a 5-condition suspension-system study |
| Freeman et al. 2006 (n=10, via Kowalski et al. 2022) | 1.08 (66.0/61.2) | not measured | not measured | standard push-up, secondary-cited numbers |
| Batbayar et al. 2015 (n=9) | 3.62 (48.1/13.3) | 3.91 (52.0/13.3) | 6.83 (90.9/13.3) | **push-up PLUS, not standard** — kept for contrast only, do not average with the standard-push-up rows above |

**Reading across the standard-push-up rows (excluding Batbayar's push-up-plus outlier):**

- **Triceps vs pectoralis major are co-dominant, with no consistent winner.** Ratios range 0.58-
  1.17 across 4 independent studies/labs — sometimes triceps edges out pec (Snarr, Freeman),
  sometimes pec edges out triceps (Youdas, Calatayud). The honest ordering statement for the
  model is **"pectoralis major and triceps brachii are the two prime movers of a standard
  push-up, roughly matched in magnitude"** — not a strict pec-first or triceps-first hierarchy.
  This is a genuine difference from the pull-up literature, where latissimus dorsi's dominance
  over biceps brachii is large and consistent across every source in `../pullup-science/`.
- **Anterior deltoid tracks pectoralis major closely and consistently.** The two studies that
  measured both in the same standard-push-up protocol (Snarr 0.93, Calatayud 0.89) land within 4
  percentage points of each other — a genuinely corroborated ratio, unusual for this literature.
  **Anterior deltoid ≈ 85-95% of pectoralis major's activation** is a defensible number for the
  model.
- **Serratus anterior is meaningfully below the two prime movers in a plain standard push-up**
  (Youdas: SA/PM ≈0.77) **but rises sharply once the rep includes an explicit scapular-protraction
  "plus" at the top** — Batbayar's push-up-plus SA/PM ratio of 6.83 is not comparable in
  magnitude (its own PM number is measured in a very different, PM-suppressing exercise) but the
  *direction* — SA climbing well above the prime movers once protraction is added — is
  independently confirmed by Ludewig et al. 2004 (SA "to 123% MVIC" in a standard push-up plus,
  the highest number in this entire file) and by Gioftsos et al. 2016's phase split in §2a. **The
  model should key SA's rise to a detected scapular-protraction motion at the top of the rep, not
  treat SA as uniformly ~75-80% of pec through the whole rep** — San Juan 2015 (§2b) shows that
  even without an exaggerated "plus," SA in a full standard push-up already climbs toward its
  peak by 55° of elbow extension, well before full lockout.

**Recommended whole-rep ordering for a standard shoulder-width push-up:** pectoralis major and
triceps brachii as co-dominant primary movers (magnitude order between them not fixed — pick
either as "first" without contradicting the evidence, or render them visually equal); anterior
deltoid close behind at ~85-95% of pectoralis major; serratus anterior lower through the plain
concentric/eccentric cycle (~75-80% of pectoralis major, Youdas) but rising to meet or exceed the
prime movers specifically around scapular protraction at the top of the rep, if the animation
shows that movement. Upper trapezius is consistently the least-activated shoulder-girdle muscle
of the group measured (Calatayud's 5.90% MVIC is the lowest whole-muscle number in the entire
standard-push-up baseline table, and Kowalski et al. 2022's 30-study synthesis independently
confirms UT is lowest in 4 of 6 push-up types reviewed).

### Other muscles for the model

- **Latissimus dorsi**: only measured for the push-up in the Batbayar push-up-plus dataset
  (16.6±12.1 %MVC at shoulder width) — a minor player relative to PM/triceps/SA in that exercise,
  consistent with the push-up (a horizontal press) not being a lat-dominant movement the way a
  pull-up is. No standard-push-up-specific latissimus dorsi number was found.
- **Biceps brachii**: only measured via Alizadeh et al. 2020's provisional numbers (§2c) — a
  minor, non-prime-mover role, consistent with the push-up being an elbow-extension (triceps),
  not elbow-flexion, movement.
- **Rectus abdominis, external oblique, transversus abdominis/internal oblique**: Tahani et al.
  2026 gives a clean healthy-baseline standard-push-up set (RA 21.94%, EO 13.84%, TrA/IO 18.75%
  MVIC) and Calatayud (JSSM) independently gives RA 23.85% MVIC on the floor — the two numbers
  agree well (21.94 vs 23.85). **Core activation in a standard push-up is real but moderate**,
  well below the prime movers, and rises substantially on unstable/suspended devices (Calatayud's
  suspension conditions reach 87-105% MVIC for RA — see §1c logic; suspension devices are the one
  condition that reliably spikes core demand across multiple studies).
- **Erector spinae**: consistently the lowest-activated muscle measured anywhere in this file —
  2.03% MVIC (Calatayud, floor) and 6.63% MVIC (Tahani, floor) — both under 10% MVIC, agreeing
  with Escamilla's "<10% MVIC for all exercises" finding for lumbar paraspinals. **Should render
  as close to cold/inactive** in a standard push-up.
- **Gluteus**: exactly one number found in the whole search — Tahani et al. 2026's gluteus medius,
  5.24±2.01 %MVIC in a healthy standard push-up. Low, consistent with the glutes being a passive/
  postural stabilizer (keeping the hips extended and in line) rather than a prime mover in a
  standard push-up. **Gluteus maximus specifically, and any push-up gluteus number for men, is
  NOT FOUND.**
- **Quadriceps**: rectus femoris is the only one of the 4 quadriceps muscles with any push-up
  data — 7.45% MVIC (Calatayud, floor), 20.55% MVIC (Borreani JESF, floor — a very different
  number from the same muscle group in a similar population, another instance of the cross-lab
  incommensurability noted in the header), and 6-10% MVIC for the decline push-up (Escamilla).
  **Vastus medialis/lateralis/intermedius push-up EMG is NOT FOUND.** Like the glutes, rectus
  femoris's role in a standard push-up is isometric-postural (keeping the legs straight), not a
  prime mover, and should render as low/moderate rather than hot.

## 5. Full citations

Primary EMG studies of the push-up / push-up plus (abstract in `abstracts/`, full text in
`papers/` where legally available):

- Cogley RM, Archambault TA, Fibeger JF, Koverman MM, Youdas JW, Hollman JH (2005). Comparison of
  muscle activation using various hand positions during the push-up exercise. *J Strength Cond
  Res* 19(3):628-33. doi:10.1519/15094.1. PMID 16095413. Closed access, abstract only.
- Gouvali MK, Boudolos K (2005). Dynamic and electromyographical analysis in variants of push-up
  exercise. *J Strength Cond Res* 19(1):146-51. doi:10.1519/14733.1. PMID 15705025. Closed
  access, abstract only.
- Youdas JW, Budach BD, Ellerbusch JV, Stucky CM, Wait KR, Hollman JH (2010). Comparison of
  muscle-activation patterns during the conventional push-up and Perfect Pushup(TM) exercises. *J
  Strength Cond Res* 24(12):3352-62. doi:10.1519/JSC.0b013e3181cc23b0. PMID 20664364. Closed
  access; abstract contains full %MVIC numbers for triceps, pectoralis major, serratus anterior
  and posterior deltoid.
- Marcolin G, Petrone N, Moro T, Battaglia G, Bianco A, Paoli A (2015). Selective Activation of
  Shoulder, Trunk, and Arm Muscles: A Comparative Analysis of Different Push-Up Variants. *J Athl
  Train* 50(11):1126-32. doi:10.4085/1062-6050-50.9.09. PMID 26488636. PMCID PMC4732391. Open
  access, but full-text fetch failed this session (Europe PMC has no fullTextXML for this PMCID,
  HTTP 404; the NCBI PMC PDF endpoint is gated behind a proof-of-work JS challenge curl cannot
  solve). A WebFetch re-check of the rendered PMC page confirmed its numeric results live only in
  a figure, not extractable text, so no numbers were lost by the failed direct fetch.
- Batbayar Y, Uga D, Nakazawa R, Sakamoto M (2015). Effect of various hand position widths on
  scapular stabilizing muscles during the push-up plus exercise in healthy people. *J Phys Ther
  Sci* 27(8):2573-6. doi:10.1589/jpts.27.2573. PMID 26357442. PMCID PMC4563317. CC BY-NC-ND, full
  text XML fetched.
- Gioftsos G, Arvanitidis M, Tsimouris D, Kanellopoulos A, Paras G, Trigkas P, Sakellari V (2016).
  EMG activity of the serratus anterior and trapezius muscles during the different phases of the
  push-up plus exercise on different support surfaces and different hand positions. *J Phys Ther
  Sci* 28(7):2114-8. doi:10.1589/jpts.28.2114. PMID 27512278. PMCID PMC4968519. Open access, full
  text XML fetched. Note: the brief's source list named this paper "Kim, Kim & Park 2016" -- the
  actual authors on PubMed are Gioftsos et al.; this file cites it under its real authorship.
- Intziegianni K, Katsamis E, Michaelides M, Parpa K (2026). Electromyographic Activation of the
  Pectoralis Major and Triceps Brachii Muscles During Standard, Diamond, and Wide Hand Position
  Push-Ups. *Muscles* 5(1):18. doi:10.3390/muscles5010018. PMID 41892990. PMCID PMC13029269. CC
  BY (MDPI), full text XML fetched.
- Snarr RL, Esco MR (2013). Electromyographic comparison of traditional and suspension push-ups.
  *J Hum Kinet* 39:75-83. doi:10.2478/hukin-2013-0070. PMID 24511343. PMCID PMC3916913. Open
  access, full text XML fetched.
- Ludewig PM, Hoff MS, Osowski EE, Meschke SA, Rundquist PJ (2004). Relative balance of serratus
  anterior and upper trapezius muscle activity during push-up exercises. *Am J Sports Med*
  32(2):484-93. doi:10.1177/0363546503258911. PMID 14977678. Closed access, abstract only.
- Lehman GJ, MacMillan B, MacIntyre I, Chivers M, Fluter M (2006). Shoulder muscle EMG activity
  during push up variations on and off a Swiss ball. *Dyn Med* 5:7. doi:10.1186/1476-5918-5-7.
  PMID 16762080. PMCID PMC1508143. Open access, full text XML fetched; complete numeric Table 1
  extracted (triceps, pectoralis major, rectus abdominis, external oblique x bench/ball x 3
  exercise conditions).
- Lehman GJ, Gilas D, Patel U (2008). An unstable support surface does not increase
  scapulothoracic stabilizing muscle activity during push up and push up plus exercises. *Man
  Ther* 13(6):500-6. doi:10.1016/j.math.2007.05.016. PMID 17643339. Closed access, abstract only.
- San Juan JG, Suprak DN, Roach SM, Lyda M (2015). The effects of exercise type and elbow angle on
  vertical ground reaction force and muscle activity during a push-up plus exercise. *BMC
  Musculoskelet Disord* 16(1):23. doi:10.1186/s12891-015-0486-5. PMID 25881172. PMCID PMC4327800.
  Open access, full text XML fetched.
- Lim H (2021). Comparison of Activity in Scapular Stabilizing Muscles during Knee Push-Up Plus
  and Modified Vojta's 3-Point Support Exercises. *Healthcare (Basel)* 9(12):1636.
  doi:10.3390/healthcare9121636. PMID 34946362. PMCID PMC8701807. Open access (CC BY), full text
  XML fetched; complete numeric Table 2 extracted.
- Borstad JD, Szucs K, Navalgund A (2009). Scapula kinematic alterations following a modified
  push-up plus task. *Hum Mov Sci* 28(6):738-51. doi:10.1016/j.humov.2009.05.002. PMID 19683822.
  Closed access, abstract only. Isometric fatigue task, not dynamic reps -- see Section 3 caveat.
- Freeman S, Karpowicz A, Gray J, McGill S (2006). Quantifying muscle patterns and spine load
  during various forms of the push-up. *Med Sci Sports Exerc* 38(3):570-7.
  doi:10.1249/01.mss.0000189317.08635.1b. PMID 16540847. Closed access, abstract only; standard
  and unstable %MVC numbers used in Section 1a/1c are secondary citations via Kowalski et al. 2022
  Table 1, not independently re-verified against Freeman's own (paywalled) tables.
- Borreani S, Calatayud J, Colado JC, Moya-Najera D, Triplett NT, Martin F (2015). Muscle
  activation during push-ups performed under stable and unstable conditions. *J Exerc Sci Fit*
  13(2):94-8. doi:10.1016/j.jesf.2015.07.002. PMID 29541105. PMCID PMC5812863. Open access, PDF
  fetched (Europe PMC fullTextXML 404'd for this PMCID; PDF render endpoint worked), complete
  numeric Table 1 extracted.
- Borreani S, Calatayud J, Colado JC, Tella V, Moya-Najera D, Martin F, Rogers ME (2015). Shoulder
  muscle activation during stable and suspended push-ups at different heights in healthy
  subjects. *Phys Ther Sport* 16(3):248-54. doi:10.1016/j.ptsp.2014.12.004. PMID 25882770. Closed
  access, abstract only (abstract itself contains 4 full %MVIC numbers, used directly).
- Calatayud J, Borreani S, Colado JC, Martin F, Rogers ME (2014). Muscle activity levels in
  upper-body push exercises with different loads and stability conditions. *Phys Sportsmed*
  42(4):106-19. doi:10.3810/psm.2014.11.2097. PMID 25419894. Closed access, abstract only.
- Calatayud J, Borreani S, Colado JC, Martin FF, Rogers ME, Behm DG, Andersen LL (2014). Muscle
  Activation during Push-Ups with Different Suspension Training Systems. *J Sports Sci Med*
  13(3):502-10. PMID 25177174. PMCID PMC4126284. Open access, PDF fetched (Europe PMC
  fullTextXML 404'd; PDF render endpoint worked, pdftotext -layout extraction), complete numeric
  Table 1 extracted (7 muscles x 5 conditions incl. floor).
- Calatayud J, Borreani S, Colado JC, Martin F, Tella V, Andersen LL (2015). Bench press and
  push-up at comparable levels of muscle activity results in similar strength gains. *J Strength
  Cond Res* 29(1):246-53. doi:10.1519/JSC.0000000000000589. PMID 24983847. Closed access,
  abstract only.
- Gottschall JS, Hastings B, Becker Z (2018). Muscle Activity Patterns do not Differ Between
  Push-Up and Bench Press Exercises. *J Appl Biomech* 34(6):442-7. doi:10.1123/jab.2017-0063.
  PMID 29809073. Closed access, abstract only.
- Alizadeh S, Rayner M, Mahmoud MMI, Behm DG (2020). Push-Ups vs. Bench Press Differences in
  Repetitions and Muscle Activation between Sexes. *J Sports Sci Med* 19(2):289-97. PMID
  32390722. PMCID PMC7196742. Open access, but the full-text fetch was blocked this session
  (Europe PMC fullTextXML 404, NCBI PMC PDF gated behind a proof-of-work JS challenge). A
  WebFetch re-check of the rendered PMC page recovered numeric concentric/eccentric %values --
  these are flagged provisional throughout this file and the CSV, not independently verified
  against the original PDF table.
- Escamilla RF, Lewis C, Bell D, Bramblet G, Daffron J, Lambert S, Pecson A, Imamura R, Paulos L,
  Andrews JR (2010). Core muscle activation during Swiss ball and traditional abdominal
  exercises. *J Orthop Sports Phys Ther* 40(5):265-76. doi:10.2519/jospt.2010.3073. PMID
  20436242. Closed access, abstract only; decline-push-up-specific numbers could not be separated
  from the abstract's pooled ranges across 10 exercises.
- Tahani HS, Minoonejad H, Zandi S, Ebrahimi E (2026). Comparison of endurance and
  electromyographic activity of core muscles in overhead athletes with and without scapular
  dyskinesis. *Sci Rep* 16(1):24808. doi:10.1038/s41598-026-56082-8. PMID 42218292. PMCID
  PMC13457960. Open access (CC BY), full text XML fetched; complete numeric Table 4 (push-up
  task) extracted for both the SD and WSD (healthy) subgroups.
- Jordan SL, Brinkman B, Harris S, Cole T, Ortiz A (2022). Core musculature co-contraction during
  suspension training exercises. *J Bodyw Mov Ther* 30:82-8. doi:10.1016/j.jbmt.2022.02.018. PMID
  35500983. Closed access, abstract only.

Systematic reviews and meta-analyses (used to pool many additional named primary studies and for
the ordering synthesis in Section 4; abstracts fetched, full text where open access):

- Kowalski KL, Connelly DM, Jakobi JM, Sadi J (2022). Shoulder electromyography activity during
  push-up variations: a scoping review. *Shoulder Elbow* 14(3):326-40.
  doi:10.1177/17585732211019373. PMID 35599715. PMCID PMC9121296. Open access, full text XML
  fetched; its Table 1 (30 studies x push-up type x muscle x %MVIC) is the single richest
  secondary-source table in this file and is saved separately as
  `papers/kowalski2022-table1.txt` for citing individual rows. Names 20+ additional primary
  studies not independently re-fetched this session (Ashnagar 2016, Cho 2014, de Araujo 2018/2019,
  Decker 2003, Hwang 2015, Kang 2014, Marshall 2006, McGill 2014, Park 2013/2015, Santos 2018,
  Stoelting 2008, Tucker 2008/2009/2010) -- their numbers as reported in Kowalski's table are
  usable but are one step removed from the primary source, same status as the Freeman/Cogley
  secondary citations above.
- Kang FJ, Ou HL, Lin KY, Lin JJ (2019). Serratus Anterior and Upper Trapezius Electromyographic
  Analysis of the Push-Up Plus Exercise: A Systematic Review and Meta-Analysis. *J Athl Train*
  54(11):1156-64. doi:10.4085/1062-6050-237-18. PMID 31584855. PMCID PMC6863690. Open access, PDF
  fetched (Europe PMC fullTextXML 404'd; PDF render endpoint worked), meta-analytic mean-
  difference numbers for SA and UT extracted.
- Arghadeh R, Alizadeh MH, Minoonejad H, Sheikhhoseini R, Asgari M, Jaitner T (2023).
  Electromyography of scapular stabilizers in people without scapular dyskinesis during push-ups:
  a systematic review and meta-analysis. *Front Physiol* 14:1296279.
  doi:10.3389/fphys.2023.1296279. PMID 38116582. PMCID PMC10728295. Open access, full text XML
  fetched.
- Arghadeh R, Alizadeh MH, Minoonejad H, Sheikhhoseini R, Asgari M, Jaitner T (2024).
  Electromyography of shoulder muscles in individuals without scapular dyskinesis during closed
  kinetic chain exercises on stable and unstable surfaces: a systematic review and meta-analysis.
  *Front Sports Act Living* 6:1385693. doi:10.3389/fspor.2024.1385693. PMID 38840951. PMCID
  PMC11150595. Open access, full text XML fetched. Same author group and PROSPERO registration
  (CRD42021268465) as the 2023 review above but a different, larger set of muscles (pectoralis
  major, anterior deltoid, triceps) rather than the scapular stabilizers.
- Mendez-Rebolledo G, Morales-Verdugo J, Orozco-Chavez I, Habechian FAP, Padilla EL, de la Rosa
  FJB (2021). Optimal activation ratio of the scapular muscles in closed kinetic chain shoulder
  exercises: A systematic review. *J Back Musculoskelet Rehabil* 34(1):3-16.
  doi:10.3233/BMR-191771. PMID 32831190. Closed access, abstract only.
- Karabay D, Emuk Y, Ozer Kaya D (2019). Muscle Activity Ratios of Scapular Stabilizers During
  Closed Kinetic Chain Exercises in Healthy Shoulders: A Systematic Review. *J Sport Rehabil*
  29(7):1001-18. doi:10.1123/jsr.2018-0449. PMID 31860828. Closed access, abstract only. Already
  cited in `../pullup-science/01-emg-and-anatomy.md` for its pull-up-adjacent CKC conclusions;
  cited here for its push-up-specific one (isometric one-hand knee push-up = best UT/LT ratio).

Kinetics/kinematics-only context citations (no EMG; cited for the plyometric/variant loading
context the brief asked for, not used in the %MVIC ordering table):

- Ebben WP, Wurm B, VanderZanden TL, Spadavecchia ML, Durocher JJ, Bickham CT, Petushek EJ (2011).
  Kinetic analysis of several variations of push-ups. *J Strength Cond Res* 25(10):2891-4.
  doi:10.1519/JSC.0b013e31820c8587. PMID 21873902. Closed access, abstract only.
- Dhahbi W, Chaouachi A, Dhahbi AB, Cochrane J, Cheze L, Burnett A, Chamari K (2017). The Effect
  of Variation of Plyometric Push-Ups on Force-Application Kinetics and Perception of Intensity.
  *Int J Sports Physiol Perform* 12(2):190-7. doi:10.1123/ijspp.2016-0063. PMID 27193045. Closed
  access, abstract only.
- Dhahbi W, Chaabene H, Chaouachi A, Padulo J, Behm DG, Cochrane J, Burnett A, Chamari K (2022).
  Kinetic analysis of push-up exercises: a systematic review with practical recommendations.
  *Sports Biomech* 21(1):1-40. doi:10.1080/14763141.2018.1512149. PMID 30284496. Closed access,
  abstract only. 26 studies, 46 push-up variants, kinetics only (no EMG).
- Zalleg D, Ben Dhahbi A, Dhahbi W, Sellami M, Padulo J, Souaifi M, Beslija T, Chamari K (2020).
  Explosive Push-ups: From Popular Simple Exercises to Valid Tests for Upper-Body Power. *J
  Strength Cond Res* 34(10):2877-85. doi:10.1519/JSC.0000000000002774. PMID 30095736. Closed
  access, abstract only.
- Dhahbi W (2026). A Rigid-Body Pendulum Model for Plyometric Push-Up Biomechanics: Analytical
  Derivation and Numerical Quantification of Flight Time, Arc Displacement, Maximum Height, and
  Mechanical Power Output. *Bioengineering (Basel)* 13(4):445.
  doi:10.3390/bioengineering13040445. PMID 42072239. PMCID PMC13113941. Open access (CC BY), pure
  analytical/computational model, no EMG or empirical kinetics.
- Suprak DN, Dawes J, Stephenson MD (2011). The effect of position on the percentage of body mass
  supported during traditional and modified push-up variants. *J Strength Cond Res* 25(2):497-503.
  doi:10.1519/JSC.0b013e3181bde2cf. PMID 20179649. Closed access, abstract only.
- Suprak DN, Bohannon J, Morales G, Stroschein J, San Juan JG (2013). Scapular kinematics and
  shoulder elevation in a traditional push-up. *J Athl Train* 48(6):826-35.
  doi:10.4085/1062-6050-48.5.08. PMID 23952043. PMCID PMC3867095. Open access, kinematics only
  (motion capture), no EMG.

## 6. What could not be found

- A true rep-by-rep EMG-amplitude fatigue curve for a dynamic push-up set to failure (Section 3).
- Plyometric/explosive push-up %MVIC by muscle (Section 1f) -- the plyometric literature located
  is kinetics-only.
- A millisecond-scale EMG-onset firing-order sequence for the push-up (Section 2d).
- Decline-push-up-specific numeric values isolated from Escamilla et al. 2010's pooled
  10-exercise ranges (Section 1d).
- Vastus medialis/lateralis/intermedius, and gluteus maximus, push-up EMG (only rectus femoris and
  gluteus medius have any push-up-specific number at all, both from single studies).
- The brief's cited "Marcolin et al. 2015, PeerJ" -- the real paper is *J Athl Train*, not PeerJ;
  found and used under its correct citation (Section 5).
- The brief's cited "Kim, Kim & Park 2016" -- no such author combination was found for a 2016
  hand-width push-up-plus paper; the paper matching that description (phase-resolved SA/trapezius
  by hand width and surface) is Gioftsos et al. 2016 and is used under its correct authorship
  (Section 5, Section 2a).
- A primary source for Gouvali & Boudolos 2005's own %MVIC magnitudes -- the abstract gives
  direction/significance only; no open-access full text or PMCID was found for this 2005 JSCR
  paper.
