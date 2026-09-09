# References — performance standards, norms, predictors and energy cost of pull-ups

Literature sweep collected 2026-09-08 for placing Dennis's max-rep set (188 cm, 79 kg, 11 strict
reps, pronated grip) against published standards, and for a sourced energy-cost model. Companion
files: `01-emg-and-anatomy.md`, `02-biomechanics-and-velocity.md` (velocity/effort, already covers
Sánchez-Moreno 2016), `../pullup-thermal/README.md` (USMC PFT rule *wording*, no scoring table — the
table is added here), `../pullup-emg/README.md`. Abstracts fetched via PubMed E-utilities, saved
verbatim in `abstracts/`; de Leva (1996) full text found as an open university-hosted PDF mirror,
saved in `papers/`; extracted numbers in `data/pullup-military-standards.csv`,
`data/pullup-percentiles-and-predictors.csv`, `data/pullup-energy-and-segments.csv`; all logged in
`DOWNLOADS.md` under this date's heading. **Mark ESTIMATE where not primary; nothing below is
invented.**

Two official .mil PDFs (`fitness.marines.mil` and `marines.mil` mirrors of MCO 6100.13A CH-2) refused
both `curl` and `WebFetch` with HTTP 403 this session — the USMC table below is from two independent
secondary compilations that agree on ages 17–40; the 41+ rows come from only one of the two and are
flagged. Re-attempt the official PDF in a future session if a verbatim primary table is needed.

## 1. Military, police and fire pull-up standards

### 1.1 USMC Physical Fitness Test (PFT) — male pull-up event, verbatim as compiled

| Age bracket | Min passing reps (40 pts) | Max reps (100 pts) |
|---|---|---|
| 17–20 | 4 | 20 |
| 21–25 | 5 | 23 |
| 26–30 | 5 | 23 |
| 31–35 | 5 | 23 |
| 36–40 | 5 | 21 |
| 41–45† | 5 | 20 |
| 46–50† | 5 | 19 |
| 51+† | 3 | 18 |

† Ages 41+ are from `thebattlebunker.com` only, not cross-checked against a second source — treat
these three rows with lower confidence than 17–40.

Rules (from `../pullup-thermal/README.md`, already collected): dead-hang start, arms fully extended;
one rep = chin above the bar, then return to full elbow extension; no kipping/kicking/swinging; sleeves
off so the judge can see lock-out. Score is 0–100 points per event; 40 points/event is the bare
passing minimum; pull-ups (unlike push-ups, capped at 70 points) are the only upper-body event that
can reach the full 100. Sources: `operationmilitarykids.org/marine-corps-pft-standards`,
`thebattlebunker.com/blogs/logbook/usmc-fitness-standards-2026-what-is-new` (both secondary; the
primary MCO 6100.13A CH-2 could not be fetched this session, see above). A sex-neutral 210-point
combat-arms MOS requirement exists per MARADMIN 613/25 but its component pull-up table was not
retrieved.

### 1.2 US Army — no current pull-up/leg-tuck event

The Army Combat Fitness Test (ACFT) dropped the leg tuck in favor of the plank; there is **no pull-up
event** in the current ACFT. Historically (legacy leg tuck, hanging knee-to-elbow raise, not a strict
pull-up): 1 leg tuck = minimum passing, 5+ = "moderate," 15+ = "excellent" core/upper-body endurance
descriptor (no fixed numeric max found). Sources: `taskandpurpose.com`, `topendsports.com/testing/
tests/leg-tuck.htm`, `dummies.com` (all secondary).

### 1.3 US Navy — no pull-up event in the standard PRT

The Physical Readiness Test (push-ups/curl-ups/plank + 1.5-mile run or swim) has no pull-up event.
Navy special-warfare (SEAL/SWCC) screening tests include pull-ups alongside push-ups/sit-ups/swim/run
under strictly monitored technique, but no numeric standard table was retrieved this session. Sources:
`military.com/military-fitness/navy-fitness-requirements`, `navycs.com` (secondary).

### 1.4 US Air Force — no pull-up event

The Air Force fitness assessment tests the 1.5-mile run, push-ups, sit-ups and waist circumference;
total score ≥75/100 to pass. No pull-up event. Source: `militaryonesource.mil` (secondary).

### 1.5 Royal Marines

- **Pre-Joining Fitness Test (PJFT), entry to the Candidate Preparation Course:** minimum 4 pull-ups
  (plus 30 press-ups, 40 sit-ups).
- **Potential Royal Marine Course (PRMC) / Commando course:** minimum 3 pull-ups to continue, 8
  encouraged as a target, 16 for maximum points. Strict overhand dead-hang pull-ups on a wooden beam,
  timed to a cadence bleep, no swinging.

Sources: `royalnavy.mod.uk/careers/royal-marines`, `bestronger.co.uk`, `force-fit.co.uk/blogs/
fitness-tests-of-the-worlds-elite-forces`, `contactcoffee.com` (all secondary; no official Royal
Navy/Royal Marines PDF fetched this session).

### 1.6 Police / fire

- **FBI Physical Fitness Test:** 1-minute timed max pull-ups, minimum 4 for men (1 for women).
- **SF Fire Department Baseline Fitness Assessment:** "as many pull-ups as possible in 2 minutes"
  described informally, not a fixed pass/fail rep count in the source found.
- Local police/sheriff department standards vary widely (some timed sets, some max-rep, some none at
  all) — no single national standard exists; secondary sources say kipping is almost universally
  disallowed where a pull-up event exists.

Sources: `bullbarfit.com` (secondary, not the official FBI PDF), `sf-fire.org/our-organization/
training/recruit-training/baseline-fitness-assessment` (secondary). **Neither is a primary/official
document fetched directly this session — treat both as indicative, not verbatim.**

## 2. Percentile norms, adult men

No primary Cooper Institute / ACSM raw percentile table for adult-male pull-ups was fetched directly
this session (only secondary compilations of it) — the ACSM full "Guidelines for Exercise Testing and
Prescription" table exists but was not retrieved. What was found:

| source | rating | reps | population | note |
|---|---|---|---|---|
| ACSM/YMCA-derived (secondary) | average | 7–9 | adult men 18–35 | secondary compilation, not the primary ACSM table |
| ACSM/YMCA-derived (secondary) | good | 10–15 | adult men 18–35 | as above |
| ACSM/YMCA-derived (secondary) | excellent | 16+ | adult men 18–35 | as above |
| strengthlevel.com | beginner | <1 | adult male, ~79 kg bodyweight bracket | crowd-sourced gym-log data, 1,220,115 qualifying male results, Dec 2016–Mar 2026 — **not a probability-sampled population survey**, skews toward people who log lifts in a training app |
| strengthlevel.com | novice | 7 | as above | as above |
| strengthlevel.com | intermediate ("stronger than 50% of lifters," ≥2 y training) | 13 | as above | as above |
| strengthlevel.com | advanced | 21 | as above | as above |
| strengthlevel.com | elite | 29 | as above | as above |
| fitness-media compilations | untrained adult male | 1–3 | general population | **ESTIMATE-grade**: repeated across multiple fitness-media articles with no traceable primary dataset cited by any of them |
| fitness-media compilation | "<5% of general population can do 10 strict pull-ups" | — | general population | **ESTIMATE-grade**, same caveat — flag as an unverified claim, not a sourced statistic |
| National Physical Fitness Award (secondary mention) | 50th-percentile youth boys 13–17 | 3–8 | youth, not adult men | not the population of interest here; included only because the task asked about youth Presidential/national-award data — no adult table found alongside it |

**Honest read:** there is a real, well-sourced adult-male military scoring table (§1.1) and a much
softer, crowd-sourced or unsourced set of "general population" pull-up numbers. The two disagree
sharply at the low end (strengthlevel.com "novice" = 7 reps vs. "untrained adult male" media claims of
1–3 reps) because they measure different populations — gym-app users who log a pull-up number are
self-selected toward people who can already do at least one. Report both, and say so.

## 3. Allometric scaling of pull-up performance with body mass

No PubMed-indexed **pull-up-specific** "Vanderburgh & Flanagan (2000)" allometric paper was located
this session (searched under several term combinations, 0 hits). The general allometric-scaling method
this task refers to is documented via:

- **Theoretical basis (geometric similarity):** strength is a cross-sectional-area property (∝ length²)
  while body mass is a volume property (∝ length³), so strength should scale with body mass to the
  **2/3 power**: `S ∝ M^(2/3)`.
- **Vanderburgh's simplified index** (asep.org/asep/asep/Vander.html, his own plain-language summary of
  his allometric-scaling program): mass-adjusted score `S_adj = S × I`, where the index
  `I = M_ref^(2/3) × M^(-2/3)`, with reference body mass **M_ref = 73.0 kg for men** (the same 73.0 kg
  appears, coincidentally or not, as de Leva's 1996 male reference body — see §6). Equivalently
  `S_adj = S × (M_ref / M) ^ (2/3)`.
- **Corroborating, PubMed-confirmed Vanderburgh papers** (none pull-up-specific, but the same author and
  method): Vanderburgh & Dooman 2000 (women's powerlifting, PMID 10647549) and Vanderburgh & Batterham
  1999 (validating the Wilks powerlifting formula against the allometric model, PMID 10613442) both
  show the **2/3-power allometric model has some bias against very light and very heavy lifters** even
  though it out-performs raw (unadjusted) scores; a second-order-polynomial model fit their powerlifting
  data with less bias than allometric scaling for deadlift/squat/total (bench press was a tie). This is
  a caution for pull-ups too: the 2/3-power model is a reasonable default, not an exact fit at the
  extremes of body mass.
- **JSCR 2000 "Allometric Modeling of the Bench Press and Squat" (Vanderburgh & Flanagan, by title)**
  is the paper that best matches the task's description, but its abstract page (`journals.lww.com`)
  returned HTTP 402 (paywalled) this session and it was not PubMed-indexed under that title in the
  searches run — its specific empirical exponent for bench/squat was **not confirmed**; only the
  general 2/3 theoretical exponent above is sourced.
- Earlier grip-strength allometric work by the same author group: Vanderburgh, Mahar & Chou (1995,
  PMID 7777699, "Allometric scaling of grip strength by body mass in college-age men and women" —
  title/citation confirmed, abstract text not on PubMed record).
- **How height/arm length affect pull-ups:** no dedicated primary study on stature/arm-length effects
  on pull-up rep count was found this session (a gap, not an ESTIMATE — no claim is made). The nearest
  related datum already in this reference set (`02-biomechanics-and-velocity.md`) is the pipeline's own
  working assumption `arm length = 0.332 × stature`, itself flagged there as ESTIMATE/no dedicated
  source. Longer arms increase the vertical distance the body must travel per rep (more concentric
  work per rep for the same body mass) — a mechanical inference, not a cited finding.

## 4. Predictors of pull-up performance

| predictor | relationship | population | source |
|---|---|---|---|
| body mass vs. max free-hanging pull-ups | r = −0.48 | 28 elite NCAA D2 women swimmers | Halet, Mayhew, Murphy & Fanthorpe 2009, PMID 19620915 |
| lean body mass (skinfold-estimated) vs. pull-ups | r = −0.43 | as above | Halet 2009 |
| % body fat (skinfold) vs. pull-ups | r = −0.32 | as above | Halet 2009 |
| 1RM lat-pull vs. pull-ups | r = 0.34 (p = .08, not significant) | as above | Halet 2009 |
| lat-pull reps-to-fatigue (80% 1RM) vs. pull-ups | r = 0.07 (n.s.) | as above | Halet 2009 — pull-ups and lat-pulls are **not** interchangeable training proxies |
| pull-ups × body mass (PU·BM) vs. 1RM lat-pull | r = 0.86 (SEE 4.4 kg) | as above | Halet 2009 |
| adding %fat to PU·BM (stepwise) vs. 1RM lat-pull | R = 0.90 (SEE 3.9 kg) | as above | Halet 2009 |
| 1RM lat-pull vs. 1RM pull-up (men) | r = 0.78, p < .01 | 35 college men | Johnson, Lynch, Nash, Cygan & Mayhew 2009, PMID 19387371 |
| 1RM lat-pull vs. 1RM pull-up (women) | r = 0.44, p > .05 | 23 college women | Johnson 2009 |
| 1RM pull-up relative to body mass (men) | 1.16 ± 0.15 × BW | 35 college men | Johnson 2009 |
| 1RM pull-up relative to body mass (women) | 0.73 ± 0.09 × BW | 23 college women | Johnson 2009 |
| pull-up reps at 80% 1RM (men) | 8.1 ± 1.9 | 35 college men | Johnson 2009 |
| pull-up reps at 80% 1RM (women) | 10.5 ± 2.2 (sig. > men) | 23 college women | Johnson 2009 |
| % body fat + strength/fat-free-mass ratio → predicts who completes a pull-up | 2-variable model, no numeric coefficients given in the abstract | college-age women, before/after an 8-wk combined strength+aerobic program | Flanagan, Vanderburgh, Borchers & Kohstall 2003, PMID 12659476 |
| upper-body field tests (incl. pull-ups) vs. criterion strength, raw scores | non-significant | 94 children, 9–10 y (38 boys, 56 girls) | Pate, Burgess, Woods, Ross & Baumgartner 1993, PMID 8451529 |
| same field tests, criterion strength expressed **per kg body weight** | significant, p < .01 for every field test | as above | Pate 1993 — i.e. pull-ups (a body-mass-relative test by construction) track *relative* strength, not absolute strength, even in children |

**Gap, honestly reported:** Ricci (1988) and Chandler (1988), named in the task as expected sources,
returned **zero PubMed hits** under several search-term combinations this session (author+year+topic,
author+"pull-up", etc.) — not included as primary citations here. This may reflect a citation from a
secondary/textbook source not itself PubMed-indexed, or a slightly different author-name/year than
searched. Flag as a gap for a future session with journal-name-specific searching (e.g. *Res Q Exerc
Sport*, *Pediatric Exercise Science* pre-1996 issues, which PubMed indexes unevenly).

## 5. Energy cost

### 5.1 Compendium of Physical Activities — MET values

| code (2024 edition) | activity | METs |
|---|---|---|
| 02020 | Calisthenics (pushups, sit-ups, **pull-ups**, jumping jacks, burpees, battling ropes), vigorous effort | 7.5 |
| 02022 | Calisthenics (pushups, sit-ups, **pull-ups**, lunges), moderate effort | 3.8 |
| 02024 | Calisthenics (curl-ups, crunches, plank), light effort | 2.8 |
| 02030 | Calisthenics, light or moderate effort, general | 3.5 |
| 02056 | Bodyweight resistance exercise, general intensity | 3.0 |
| 02057 | Bodyweight resistance exercise, high intensity | 6.5 |

Source: `pacompendium.com`, 2024 Adult Compendium of Physical Activities (consensus expert ratings, not
directly measured VO2 for pull-ups specifically — the Compendium's numbers are activity-class
estimates, not per-exercise calorimetry). An older/2011-era predecessor code **02050 = 8.0 METs**
("calisthenics, vigorous, pull-ups/push-ups") appears in some still-circulating secondary summaries;
the 2024 edition's 02020 (7.5 METs) supersedes it — use 7.5, note the version history if the pipeline
ever cites a MET number by code.

### 5.2 Mechanical/mechanochemical efficiency

- **Ryschon, Fowler, Wysong, Anthony & Balaban (1997)**, PMID 9292475, *J Appl Physiol* 83(3):867-74.
  Human tibialis anterior / extensor digitorum longus in vivo, ³¹P-NMR + dynamometer. Mechanochemical
  efficiency (ATP production rate ÷ work, both J/s): **concentric 15.0 ± 1.3%**, **eccentric
  34.7 ± 6.1%**. Metabolic efficiency ranking: isometric > eccentric > concentric. This is a *lower*
  concentric efficiency than the pipeline's current 22% assumption — the 22% falls inside the broader
  "20–25%" range often quoted in exercise-physiology texts (whole-body cycling/rowing efficiency
  estimates), but this single in-vivo isolated-muscle NMR study measured a lower figure for a
  non-pulling muscle group (ankle dorsiflexors, not the lats/biceps used in a pull-up). Report both
  numbers; do not claim 22% is directly validated by Ryschon 1997 — it is a plausible whole-body-motion
  value bracketed by, not equal to, this isolated-muscle datum.
- **Bigland-Ritchie & Woods (1976)**, PMID 978517, *J Physiol* 260(2):267-77, open access (PMCID
  PMC1309091). Motorized bicycle ergometer, vastus lateralis. Ratio of slopes (mean torque vs.
  integrated EMG, and vs. steady-state VO2), positive/negative work: **EMG ratio 1.96 ± 0.12**, **VO2
  ratio 6.34 ± 0.82**. I.e., for the same mean torque, negative (eccentric) work needs about half the
  muscle-fibre activity but only about **1/6.34 ≈ 16%** of the oxygen cost of positive (concentric)
  work — a substantially bigger eccentric discount than the EMG alone would suggest.
- **Abbott, Bigland & Ritchie (1952)**, *J Physiol*, "The physiological cost of negative work" — the
  foundational two-bicycles-and-a-chain experiment. **Not retrieved as a primary abstract this
  session** (PubMed esearch returned 0 hits under several term combinations, likely a pre-1953/pre-deep
  PubMed-indexing gap). Its commonly cited "6–7× lower metabolic cost for negative vs. positive work at
  equal mechanical magnitude" figure is carried here only via a secondary description (a 2014 J Exp
  Biol review, "Revisiting the positive aspects of negative work") — **ESTIMATE-grade citation of the
  original**, but note it is closely consistent with Bigland-Ritchie & Woods's later, primary-sourced
  6.34× VO2 ratio above.
- **Net read for the pipeline's "eccentric = 35% of concentric" constant:** the primary data above
  (16–43% eccentric/concentric cost ratio, depending on whether you use the VO2 ratio 1/6.34≈16% or the
  Ryschon efficiency ratio 0.15/0.347≈43%) **brackets** the pipeline's 35% assumption on both sides —
  35% is a defensible mid-range estimate, not a number lifted verbatim from any single cited study.

### 5.3 Isometric holding (grip/hang) cost

No study specifically measuring the VO2/kcal cost of an isometric dead-hang or bar-hold was found this
session. The pipeline's 3.5 MET assumption for "isometric cost while on the bar" happens to equal
Compendium code 02030 ("calisthenics, light or moderate effort, general," 3.5 METs exactly) — this is a
**coincidental match, not a direct citation**: 02030 is a general light/moderate calisthenics class,
not an isometric-hang-specific code. Flag the 3.5 MET isometric constant as **ESTIMATE**, bracketed
loosely by the Compendium's calisthenics range (2.8–7.5 METs depending on effort) but not independently
validated for a static hang.

### 5.4 EPOC (afterburn)

General (non-pull-up-specific) resistance-training/HIIT literature: EPOC typically adds **6–15% on top
of** a workout's net exercise-time energy cost (e.g., ~30-75 kcal of "afterburn" on a ~500 kcal
workout). Source: narrative synthesis via `marathonhandbook.com`/`acefitness.org` (secondary, no single
primary study extracted this session — this is consistent with, but not sourced from, the pipeline's
already-cited Sánchez-Medina & González-Badillo 2011 velocity-loss/fatigue work in `../pullup-emg/`).
For an ~11-rep, well under one minute set, EPOC is a small, second-order correction (a few kcal at
most) — worth a one-line caveat in the report, not a term in the per-rep equation.

## 6. Segment mass fractions and centre of mass (de Leva 1996)

**de Leva P (1996).** Adjustments to Zatsiorsky-Seluyanov's segment inertia parameters. *J Biomech*
29(9):1223-30. PMID 8872282. Full text obtained (open PDF mirror, `papers/
deleva1996-segment-inertia-parameters.pdf`, extracted table in the `-extract.txt` companion). Reference
bodies: **male 73.0 kg / 1.741 m stature**; **female 61.9 kg / 1.735 m stature** (adjusted
Zatsiorsky-Seluyanov gamma-ray-scanning dataset, college-aged Caucasian adults).

### Table 4 (de Leva 1996) — segment mass as % of total body mass

| segment | male % | female % |
|---|---|---|
| hand | 0.61 | 0.56 |
| forearm | 1.62 | 1.38 |
| upper arm | 2.71 | 2.55 |
| **hand + forearm, one arm** | **2.23** (derived) | 1.94 (derived) |
| **hand + forearm, both arms** | **4.46** (derived) | 3.88 (derived) |
| hand + forearm + upper arm, one arm | 4.94 (derived) | 4.49 (derived) |

Segment CM position (male; % of segment length from the proximal/cranial endpoint): upper arm (acromion
to elbow) 57.72%; forearm (elbow-joint-centre to wrist, "EJCS→STYL" definition) 46.08%; hand (wrist to
3rd metacarpale, "WJCS" definition) 79.00% (i.e., the hand's CM sits close to its far/finger end because
Zatsiorsky's "hand" segment already excludes the palm-proximal wrist bones).

**This is the primary source for the pipeline's "lifted mass = body mass minus hands + forearms"
convention.** Both hands+forearms together are ~4.46% of a male's total body mass (de Leva, male
reference) — for Dennis at 79 kg, that is **≈3.5 kg** of hand+forearm mass, essentially fixed to the bar
during a pull-up and not part of the vertically-displaced mass. Using the exact de Leva fraction (4.46%,
not a round number) is the sourced version of that constant; the upper arms (a further 2.71% × 2 =
5.42% of body mass) **do** travel with the torso and should stay in the lifted-mass term — the current
convention of excluding only hands+forearms, not upper arms, is consistent with de Leva's segment
boundaries (the upper arm's proximal end, the shoulder, is where the "lifted body" begins).

**Whole-body CM position relative to the shoulder while hanging: not found as a primary measurement.**
No study measuring the specific position of a hanging person's whole-body centre of mass relative to
the shoulder/glenohumeral joint was located this session. De Leva/Winter/Dempster all report the
*standing, arms-at-sides* whole-body CM at roughly 55–57% of stature above the sole of the foot (i.e.
near the umbilicus) — not directly transferable to a dead-hang position where the arms are raised
overhead and the torso hangs free. Computing the hang-position CM from de Leva's segment fractions and
lengths is possible in principle (sum of segment-mass × segment-CM-position over all segments,
re-referenced to the shoulder) but **was not done this session** — flag as a follow-up task, not as an
ESTIMATE number invented here.

## 7. World records and elite benchmarks

| record | value | holder | source |
|---|---|---|---|
| most pull-ups in 1 minute (male, unweighted) | 90 | Yutaro Matsuta (Japan), 10 Apr 2026 | Guinness World Records |
| most pull-ups in 1 minute with 40 lb (18.1 kg) pack | 46 | Adam Sandel (USA), 30 May 2025 | Guinness World Records |
| most pull-ups in 1 minute with 60 lb (27.2 kg) pack | 35 | Li Zechuan (China), 22 Mar 2025 | Guinness World Records |
| most pull-ups in 1 minute with 100 lb (45.4 kg) pack | 25 | Liu Weiqiang (China), 12 Mar 2023 | Guinness World Records |

Source: `guinnessworldrecords.com` (official record pages, one WebSearch summary per record — not
independently re-verified against the GWR site's raw video/adjudication pages this session).

## 8. How to use in the pipeline

### 8.1 Placing 11 strict reps, ~30 y, 79 kg man

- **USMC PFT table (§1.1):** 79 kg (174 lb) man, assume age bracket 26–35 (matches "30-ish"): min
  passing (40 pts) = 5 reps, max (100 pts) = 23 reps. **11 reps sits inside that range but well below
  the midpoint** — linear interpolation between the two known anchor points (5 reps = 40 pts, 23 reps
  = 100 pts, i.e. 60 points over 18 reps ≈ 3.33 pts/rep) gives an **approximate 40 + (11−5)×3.33 ≈ 60
  points** — **mark this interpolation as ESTIMATE**: the real USMC scoring curve is not published here
  as a full 3-to-23 rep-by-rep table (only the two milestone anchors were retrieved), and military
  scoring tables are not always linear between milestones. State the number as "roughly 60/100 on a
  linearly-interpolated USMC scale, unverified against the actual non-linear table" rather than as fact.
- **strengthlevel.com crowd-sourced levels (§2):** 11 reps sits **between "novice" (7) and
  "intermediate" (13)** for a ~79 kg man — closer to intermediate. Caveat clearly: this is a
  convenience-sample gym-app population, not a probability sample of adult men.
- **ACSM/YMCA-derived secondary bands (§2):** 11 reps sits at the top of "average" (7–9) / bottom of
  "good" (10–15) for adult men 18–35 — again, secondary compilation, not the primary ACSM table.
- **Royal Marines PRMC (§1.5):** 11 reps clears the 8-rep "encouraged" target and is well above the
  3-rep minimum, short of the 16-rep max-points mark.
- **Combined honest verdict for the reel:** "well above the minimum passing standard on every military
  scale checked, comfortably inside the trained/intermediate band on both a crowd-sourced strength
  database and a secondary ACSM-derived scale, short of the ~20+ rep territory that any of these scales
  treat as elite" — report the range across sources rather than a single invented percentile number.

### 8.2 The energy model — every constant sourced or flagged

Current model: `kcal_per_rep ≈ [W_concentric / 0.22] + [0.35 × (W_concentric / 0.22)] + isometric_kcal`,
isometric term via 3.5 MET while gripping the bar; lifted mass = body mass − (hands + forearms).

| constant | current value | status | source |
|---|---|---|---|
| concentric mechanical efficiency | 22% | inside the literature range but not a direct measurement of pulling muscles | Ryschon 1997 measured 15.0 ± 1.3% (isolated tibialis anterior/EDL, in vivo, ³¹P-NMR) — a different, non-pulling muscle group; 20-25% is a commonly quoted whole-body-exercise range in secondary sources. **Recommendation: report 22% as "within the 15-25% range found in the literature for different muscles/methods," not as a single validated number.** |
| eccentric cost, as fraction of equivalent concentric cost | 35% | bracketed by two primary ratios, not identical to either | Bigland-Ritchie & Woods 1976 (VO2 ratio 6.34× → eccentric ≈ 1/6.34 ≈ **16%** of concentric for equal torque); Ryschon 1997 efficiency ratio (0.15/0.347 → eccentric ≈ **43%** of concentric cost for equal work). 35% sits inside this 16-43% bracket — reasonable, not verbatim from a single source. |
| isometric holding cost | 3.5 MET | ESTIMATE — no dead-hang-specific measurement found | Coincides with Compendium code 02030 (general light/moderate calisthenics, 3.5 METs) but that code is not hang-specific; bracket is roughly 2.8-7.5 METs across the Compendium's calisthenics codes (§5.1). |
| EPOC | not currently in the model | correctly omitted for a ~30-50 s set (per §5.4, a few-kcal, second-order effect) — if added, +6-15% is the general (non-pull-up) literature range | secondary synthesis, §5.4 |
| lifted mass = body mass − hands − forearms | − 4.46% of body mass (both hands+forearms, de Leva male reference) | **sourced number available now**: use −4.46%, i.e. for a 79 kg man, lifted mass ≈ 79 × (1 − 0.0446) ≈ **75.5 kg**, rather than a round guessed percentage | de Leva 1996, Table 4, §6 |
| ~1 kcal/rep (overall pipeline output) | plausible order-of-magnitude check | Using the Compendium's own stated approximation (1 MET ≈ 1 kcal·kg⁻¹·h⁻¹): vigorous calisthenics (code 02020, 7.5 MET) for a 79 kg man over an assumed 2-4 s/rep (assumption, not measured from this set) gives 7.5 × 79 ÷ 3600 × (2 to 4 s) ≈ **0.33-0.66 kcal/rep** from the MET table alone. The pipeline's biomechanically-derived ≈1 kcal/rep is roughly **1.5-3× higher**, same order of magnitude, not a large discrepancy — consistent with a single max-effort pull-up being more locally intense than the Compendium's broad "vigorous calisthenics" class (which also covers jumping jacks and burpees). | this session's own arithmetic comparison (Compendium §5.1 MET value + its own kcal·kg⁻¹·h⁻¹ definition), not a discrepancy worth flagging as a problem |

**Bottom line for the pipeline:** the mass-fraction constant (§6) can be tightened immediately to the
sourced −4.46%. The 22% and 35% constants are defensible midpoints inside literature-bracketed ranges,
not single validated numbers — report them that way. The 3.5 MET isometric term is the weakest-sourced
constant in the whole model (no direct hang-specific measurement exists in the literature found this
session) — say so on screen or in the report copy if the isometric term meaningfully changes the total.
The ≈1 kcal/rep headline number is plausible given the eccentric/concentric/isometric decomposition, and
is also in the right ballpark (same order of magnitude, roughly 1.5-3x higher) as a naive "vigorous
calisthenics" Compendium-MET estimate for a 2-4 s rep — a reasonable cross-check, not a contradiction,
though the Compendium comparison itself rests on an assumed, unmeasured rep duration and should be
labeled as such if used in the report.
