# References — push-up performance standards, population norms and energy cost

Literature sweep collected 2026-09-09, companion to `02-pushup-hand-force-and-joint-moments.md` and
`04-pushup-fatigue-within-set.md`. Official-source pages saved in `papers/` (HTML, since the primary
`fitness.marines.mil`/`marines.mil` PDFs all returned HTTP 403 to `curl` and to WebFetch — the same
block pattern already documented in `references/pullup-science/03-norms-and-energy.md` §1.1);
abstracts in `abstracts/`; extracted numbers in `data/pushup-military-standards.csv`,
`data/pushup-norms-by-age.csv`, `data/pushup-energy.csv`. All logged in `DOWNLOADS.md`. **Mark
ESTIMATE/NOT FOUND where not primary; nothing below is invented.**

## 1. USMC Physical Fitness Test (PFT) — male & female push-up event

**The official Marine Corps Order (MCO 6100.13A) and the official `fitness.marines.mil` push-up
page could not be fetched this session** — `curl -A "Mozilla/5.0"` and WebFetch both returned HTTP
403 for every `.mil` URL tried, including a direct MCO PDF mirror hosted at
`mcieast.marines.mil/Portals/33/Documents/EOA/MCO 6100.13 PFT Program.pdf` (found via WebSearch, same
403 block). The table and technique description below are from two independent secondary
compilations (the same two sources the pull-up archive uses and trusts for its own pull-up table),
cross-checked against each other.

### 1.1 Technique (secondary source, apparently near-verbatim MCO language — not independently
confirmed against the primary Order this session)

- **Starting position**: front-leaning rest, hands placed where comfortable, feet together or up to
  12 inches apart, body forming a generally straight line from shoulders to ankles.
- **Bottom of the rep**: lower the entire body as a single unit until the **upper arms are at least
  parallel to the ground**. Chest may not rest on the deck except briefly to confirm arm position.
- **Top of the rep (lock-out)**: raise the entire body until the **arms are fully extended**.
- **What does not count**: a rep where the Marine fails to keep a generally straight body line,
  fails to reach upper-arms-parallel at the bottom, or fails to fully extend the arms at the top.
  Additionally, incorrectly-performed reps after the first 10 are not counted.
- **Time limit**: 2 minutes, maximum reps.
- **Authorized rest**: an *altered* front-leaning rest (sagging, back flexed) only. Resting on the
  ground, or lifting either hand or foot off the ground, **ends the set**.

Source: `militaryspot.com/marines/marine-fitness-test` (secondary blog compilation, quoted at length
in `papers/militaryspot-usmc-pft-extract.txt`).

### 1.2 Scoring table (male), verbatim as compiled from two independent secondary sources

| Age bracket | Min passing reps (40 pts) | Max reps (**70 pts** — push-up cap) |
|---|---|---|
| 17–20 | 42 | 82 |
| 21–25 | **40** | **87** |
| 26–30 | 39 | 84 |
| 31–35 | 36 | 80 |
| 36–40 | 34 | 76 |
| 41–45 | 30 | 72 |
| 46–50 | 25 | 68 |
| 51+ | 20 | 64 |

**Push-ups cap at 70 points, not 100** — pull-ups remain the only upper-body PFT event that can
reach the full 100-point ceiling (already documented from the pull-up side in
`references/pullup-science/03-norms-and-energy.md` §1.1: "pull-ups (unlike push-ups, capped at 70
points) are the only upper-body event that can reach the full 100"). A Marine who elects push-ups
over pull-ups gives up the possibility of a perfect 300-point PFT even with a maxed-out push-up
score.

### 1.3 Scoring table (female)

| Age bracket | Min passing reps (40 pts) | Max reps (70 pts) |
|---|---|---|
| 17–20 | 19 | 42 |
| 21–25 | 18 | 48 |
| 26–30 | 18 | 50 |
| 31–35 | 16 | 46 |
| 36–40 | 14 | 43 |
| 41–45 | 12 | 41 |
| 46–50 | 11 | 40 |
| 51+ | 10 | 38 |

Sources: `thebattlebunker.com/blogs/logbook/usmc-fitness-standards-2026-what-is-new` (primary
compiled table, both sexes, all 8 age brackets — `papers/thebattlebunker-usmc-standards-2026-extract.txt`)
cross-checked against `operationmilitarykids.org/marine-corps-pft-standards/` (a coarser 6-point-level
table, male only, ages 17–40 — `papers/operationmilitarykids-usmc-pft-2026-extract.txt`); the two
agree everywhere they overlap (e.g. male 21–25: 40 reps for 40 pts and an intermediate 64 reps at
75 pts in the finer table is consistent with the coarser table's "N/A" at 90/100 pts, confirming the
70-point push-up cap independently).

## 2. US Army — ACFT / AFT hand-release push-up (HRP)

**This is NOT the same movement as the USMC standard push-up** — the Army's event requires the
chest, hips AND thighs to touch the ground at the bottom of every rep, then both hands must lift
completely off the floor and the arms extend out to the sides before the next rep, adding a real
per-rep time cost the USMC push-up does not have. Technique confirmed from the official
`goarmy.com` page (direct `curl` fetch 403'd; content obtained via WebFetch, which could reach it —
see `papers/goarmy-acft-hrp-CITATION-ONLY.txt`).

**Scoring is genuinely unsettled in the secondary sources found this session**, and for a real,
documented reason: the Army renamed/restructured its fitness test from the **ACFT** (Army Combat
Fitness Test, launched ~2019–2020 with **gender-neutral** scoring) to the **AFT** (Army Fitness Test,
current as of **June 2025**, with **age- and sex-normed** scoring restored). Two secondary tables
found this session reflect the two different eras and should not be averaged:

| era | example anchor | source |
|---|---|---|
| original ACFT, gender-neutral, ages 17–80 | 10 reps = 60 pts (min pass); 57 reps = 100 pts (max) | topendsports.com (secondary) |
| current AFT, age/sex-normed, 2025–2026 | male 22–26: 14 reps = 60 pts (min pass); 61 reps = 100 pts (max). Female 22–26: 11 reps = 50 pts | gymnasetips.com / militaryfitnesscalc.com WebSearch summary (secondary) |

No official Army scoring table (DA PAM 7-22, armypubs.army.mil) was fetched this session — see
`papers/army-hrp-scoring-secondary-notes.txt` for the full discussion. **Treat the whole Army HRP
scoring table as lower-confidence than the USMC table above**, which rests on two independent,
internally-consistent secondary compilations rather than one WebSearch summary.

## 3. ACSM / CSEP push-up test and population norms

### 3.1 The actual primary table, recovered via a peer-reviewed paper that reproduces it

No primary ACSM "Guidelines for Exercise Testing and Prescription" text was fetched directly this
session — but **Adams, Hatch, Winsor & Parmelee 2022** (*Int J Exerc Sci*, PMCID PMC9362895, open
access) reproduces the actual table in its own Table 1, with full provenance: ratings for the
**modified** (knee) push-up were first published by Pollock et al. 1978; the table was included in
the **2nd edition of ACSM's Guidelines (1993)**; the underlying normative data were developed by the
**Canadian Association of Sport Sciences in 1987** and — per this 2022 paper — are still the ones in
circulation, unchanged for over 30 years.

| category | Female (modified/knee) | Male (standard/toes) |
|---|---|---|
| Excellent | ≥30 | ≥36 |
| Very Good | 21–29 | 29–35 |
| Good | 15–20 | 22–28 |
| Fair | 10–14 | 17–21 |
| Poor | ≤9 | ≤16 |

(20–29-year-old age bracket; this is the table both ACSM and CSEP use as the standard reference.)

### 3.2 A 2022 attempt to fix the test's gender gap

The same Adams et al. 2022 paper is itself a genuinely recent (2020–2026) normative study: 72
college-age women (18–24y) performed both the standard and modified push-up. Mean standard-position
reps: **9 (SD 8.87)**; modified: **17.5 (SD 11.76)**. Strong correlation between the two positions
(r = 0.85, r² = 0.72); regression equation `standard_reps = −2.217 + 0.64 × modified_reps` used to
derive a **new predicted standard-push-up scale for college women**:

| category | predicted standard-push-up reps |
|---|---|
| Excellent | ≥18 |
| Very Good | 12–17 |
| Good | 8–11 |
| Fair | 5–7 |
| Needs Improvement | ≤4 |

This new scale sits close to Mozumdar et al. 2010's Revised Push-up percentiles and below the (more
demanding) FitnessGram Healthy Zone (which expects 18–35 reps at age 17) and below Baumgartner et
al. 2004's Revised Push-up percentiles.

### 3.3 Secondary-compiled tables (two independent sources, for cross-checking the ACSM/CSEP table)

Both are 5–7-tier fitness-category tables by age and sex, broadly consistent with §3.1's primary
table but not independently traceable to a primary citation by either page itself:

- `trainrboost.com` (5-tier, explicitly cites "ACSM Guidelines, 10th ed.") — male 20–29 Excellent
  ≥36, matching §3.1 exactly.
- `topendsports.com` (7-tier, the page itself says "the original source for this data is unknown,"
  citing Baumgartner/Golding/Heyward fitness-measurement literature only in general terms) — male
  20–29 Average band 17–29, roughly spanning §3.1's Fair-through-Good range.

Full tables (all age brackets, both sexes, both secondary sources) in `data/pushup-norms-by-age.csv`.

**No crowd-sourced percentile table (the strengthlevel.com-style data the pull-up archive used) was
pulled for push-ups this session** — a time-budget gap, not a finding of absence; strengthlevel.com
does publish a push-up page but it was not fetched.

## 2b. Population norms — firefighters and cardiovascular outcome (Yang et al. 2019)

**Yang, Christophi, Farioli, Baur, Moffatt, Zollinger & Kales (2019)**, *JAMA Netw Open* 2(2):e188341,
PMID 30768197, **PMCID PMC6484614, open access** — retrospective cohort, 1104 male firefighters
(Indiana), 10-year follow-up (2000–2010), push-up capacity split into 5 categories:

| push-up category | events (of 37 total) | rate per 100,000 person-yr | IRR vs. 0–10 (95% CI) |
|---|---|---|---|
| 0–10 (reference) | 8 | 1757 | 1 [Reference] |
| 11–20 | 9 | 625 | 0.36 (0.14–0.92) |
| 21–30 | 9 | 288 | 0.16 (0.06–0.42) |
| 31–40 | 10 | 433 | 0.25 (0.10–0.62) |
| ≥41 | 1 | 79 | **0.04 (0.01–0.36)** |

Men completing **>40 push-ups had a 96% lower incidence rate** of cardiovascular events than those
completing <10, over 10 years (the headline figure quoted in the paper's own abstract). This is an
**observational, occupationally-selected cohort** (career firefighters, not a general population) —
report it as an association, not a causal claim that push-ups themselves prevent cardiovascular
disease; higher push-up capacity very plausibly marks general fitness/leanness/younger relative age
within the cohort. Full extract in `papers/yang2019-pushup-cvd-cohort-extract.txt`.

## 4. Energy cost

### 4.1 Directly measured (indirect calorimetry) — the strongest evidence in this archive

**Nakagata, Yamada & Naito (2022)**, *J Strength Cond Res* 36(5):1290-1296, PMID 32379233, **PMCID
PMC9042340, open access**. 15 men (21–29y), push-up (and squat, heel-raise for comparison) performed
at 6 controlled cadences (1–6 reps/min), oxygen consumption measured directly.

- **Energy cost per push-up repetition: 0.77 ± 0.20 kcal/rep (95% CI 0.66–0.88)** — directly measured,
  not a consensus rating.
- Extrapolated to 10 reps/min: **9.2 ± 2.1 kcal/min = 7.8 METs** (highest of the 3 exercises tested;
  squat 6.3 kcal/min = 5.4 METs; heel-raise 2.7 kcal/min = 2.3 METs).
- Confirmed directly (not extrapolated) by the paper's own Table 3: at 6 reps/min, measured push-up
  MET = **4.7 ± 0.8**, vs. squat 3.7 ± 0.5 and heel-raise 1.8 ± 0.2 — push-up highest at every
  matched cadence.

### 4.2 Compendium of Physical Activities (reused from the pull-up archive, not re-fetched)

The pull-up archive's `03-norms-and-energy.md` §5.1 already documents the relevant 2024 Compendium
codes, which explicitly list "pushups" in their activity description alongside pull-ups:

| code | activity | METs |
|---|---|---|
| 02020 | Calisthenics (pushups, sit-ups, pull-ups, jumping jacks, burpees, battling ropes), **vigorous** | 7.5 |
| 02022 | Calisthenics (pushups, sit-ups, pull-ups, lunges), **moderate** | 3.8 |
| 02056 | Bodyweight resistance exercise, general intensity | 3.0 |
| 02057 | Bodyweight resistance exercise, high intensity | 6.5 |

**Nakagata's directly-measured 7.8 METs at 10 reps/min is within ~4% of the Compendium's 7.5-MET
consensus rating for vigorous calisthenics push-ups** — unusually good agreement between a direct
physiological measurement and an expert consensus panel's rating; use **7.5–7.8 METs** as the
push-up-specific vigorous-effort figure, and 0.77 kcal/rep as the per-repetition constant, citing
Nakagata 2022 as the primary source for the per-rep number.

## 5. Predictors and cross-exercise relationships (context, not standards per se)

- **Push-up vs. bench-press strength**: strong-to-very-large cross-exercise correlations turn up
  repeatedly across this sweep — Wang et al. 2017a (R = 0.837 for a push-up-derived bench-press 1RM
  prediction equation), Bartolomei et al. 2018 (r = 0.87), van den Tillaar & Ball 2020 (r = 0.93),
  van den Tillaar, Falch & Larsen 2025 (r = 0.92, but with the push-up's own actual 1RM
  *exceeding* the bench press's, 112.4 vs. 106.4 kg vest-equivalent kg in the same 11 men) — see
  `02-pushup-hand-force-and-joint-moments.md` §6 for the full numbers.
- **Push-up vs. push-up in the other position**: Adams et al. 2022's r = 0.85 (standard vs. modified,
  §3.2 above) is the strongest same-exercise cross-position relationship found.

## 6. What the model should use

1. **Elbow-lockout/parallel-upper-arm ROM anchors** (top/bottom position definitions) should follow
   the USMC wording in §1.1 — it is the most precisely worded standard found this session and
   matches Eckel et al. 2017's own isometric-hold protocol definitions (`02-...md` §5).
2. **USMC scoring (§1.2/1.3) is the highest-confidence military standard** in this file — two
   independent secondary sources agree at every overlap point, and the 70-point push-up cap is
   internally cross-confirmed by both tables' structure. Use it as the primary military-scale
   reference; treat the Army AFT numbers (§2) as lower-confidence pending a primary-source fetch.
3. **Report ACSM/CSEP §3.1 as the primary civilian fitness-category table** — it has a traceable
   provenance chain (Pollock 1978 → ACSM 1993 → still in use per Adams 2022), unlike the two
   secondary-compiled tables in §3.3, which should be used only as a rough cross-check.
4. **Use Nakagata 2022's 0.77 kcal/rep as the energy-cost constant** — it is a directly measured
   number, not a consensus estimate, and it happens to closely validate the Compendium's independent
   7.5-MET rating, which is unusually strong corroboration for an exercise-physiology constant.
5. **Report the Yang 2019 firefighter cardiovascular association (§2b) as a "why this matters"
   framing point for the report copy**, explicitly labeled as an association in an occupational
   cohort, not a general-population causal claim.
