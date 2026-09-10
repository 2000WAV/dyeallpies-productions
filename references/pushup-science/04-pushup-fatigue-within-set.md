# References — push-up fatigue within a set and rep-to-rep changes

Literature sweep collected 2026-09-09, companion to `02-pushup-hand-force-and-joint-moments.md` and
`03-pushup-norms-and-standards.md`. Abstracts in `abstracts/`, extracted numbers in
`data/pushup-fatigue.csv`, logged in `DOWNLOADS.md`.

**Headline finding, stated honestly up front**: despite a thorough search (PubMed E-utilities and
Europe PMC, both by keyword and by restricting to the TITLE field for "push-up" combined with
"fatigue," "failure," "exhaustion," "median frequency," "velocity loss," "repeated," "set," and
"repetitions"), **no push-up-specific study measuring rep-by-rep kinematic or EMG changes across a
set performed to failure was located this session.** This is a genuine literature gap, not an
oversight — the closest push-up-specific kinetics/EMG papers found (García-Massó 2011, Dhahbi 2017,
Zalleg/Dhahbi 2020) all measure single-trial kinetics, not progression across a fatiguing set. This
file documents what *is* available: reps-to-failure counts, cadence-dependent force redistribution,
one fatigue-adjacent between-exercise design, and the already-archived generic (joint-based, not
exercise-specific) fatigue/recovery model that the pull-up pipeline already uses.

## 1. Reps-to-failure (the closest available proxy for "how long a set lasts")

**Eckel, Watkins, Archer, Wong, Arevalo, Lin, Coburn, Galpin & Brown (2017)**, *International
Journal of Sports Science & Coaching* 12(5):647-652, doi:10.1177/1747954117733879. **Not
PubMed-indexed** (IJSSC/SAGE is not consistently MEDLINE-indexed; searched under several
author/title combinations, 0 hits) — full PDF obtained directly from a Cal State Fullerton
institutional lab-page mirror, saved in `papers/eckel2017-pushup-benchpress-failure.pdf` with a full
extract in the companion `-extract.txt`.

25 recreationally trained subjects (16 men, 9 women) performed push-up and bench-press repetitions
to failure at a fixed 60 beats/min (30 reps/min) metronome cadence, with the bench-press load
individually equated to each subject's own isometric push-up force (average of up+down %BM).

| metric | value |
|---|---|
| push-up reps-to-failure — men | 24.06 ± 10.35 |
| push-up reps-to-failure — women | 30.18 ± 19.15 (very high individual variability) |
| bench-press reps-to-failure — men | 16.38 ± 6.05 |
| bench-press reps-to-failure — women | 11.00 ± 9.25 |
| push-up vs. bench-press reps-to-failure correlation (combined sexes) | r = 0.82 |

More reps were completed in the push-up than the equated-load bench press for both sexes
(P < 0.001), and the two exercises' endurance capacities correlate strongly (r = 0.82) despite the
very different absolute rep counts — i.e. someone who fatigues quickly on the bench also tends to
fatigue quickly on the push-up, even though the push-up "lasts longer" in raw rep terms at a matched
relative load. This paper does **not** report any within-set kinematic or force trajectory —
only the final rep count.

## 2. Cadence and force redistribution (fatigue-adjacent, not fatigue-tracking)

**Rozenek, Byrne, Crussemeyer & Garhammer (2022)**, *J Strength Cond Res* 36(12):3324-3329, PMID
34265814. 44 healthy men and women, standard push-up at 3 fixed cadences (30/45/60 reps/min) plus a
self-selected cadence, vGRF measured under **both** the hands and the feet.

- Self-selected cadence: men 49.9 ± 11.4 reps/min, women 42.8 ± 8.4 reps/min (men significantly
  faster).
- Maximum reps completed at either the self-selected cadence or 60 reps/min, with little difference
  between the two — i.e. subjects' own chosen pace was already near the fastest sustainable rate.
- **Sum of vGRF (hands + feet) at the 60 reps/min cadence: 1.58 ± 0.14× BM (men), 1.33 ± 0.08× BM
  (women)** — a genuine above-bodyweight total system load, driven by the acceleration term at the
  fast cadence (see `02-pushup-hand-force-and-joint-moments.md` §3).
- **As cadence increased, men shifted proportionally more of the total force onto the hands**
  specifically, compared to women (P ≤ 0.05) — a sex difference in how the extra dynamic load at a
  faster pace gets distributed between the hand and foot contact points.

This is a **cadence-manipulation** design, not a fatigue-accumulation design — the study does not
track how force distribution changes across a *single* set as the subject tires, only how it differs
*between* sets performed at different fixed paces. It is included here because it is the closest
available quantitative evidence for how push-up loading redistributes dynamically, which is directly
relevant to what a fatiguing set is likely to do even though it was not measured that way directly.

## 3. One indirect (between-exercise) fatigue design

**Collins, Bradley, Christensen, Waldera, Klawitter, Ogren & Salatto (2024)**, *Int J Exerc Sci*
17(1):38-53, PMID 38665164, **PMCID PMC11042900, open access**. 18 men, post-activation-performance-
enhancement (PAPE) design: bench-press conditioning set (80% 1RM to 10% velocity loss, full vs.
partial range of motion) followed by repeated ballistic-push-up (BPU) tests over the next 2–12
minutes.

Partial-ROM bench conditioning produced **greater** post-test BPU flight time, impulse, and peak
power at several time points than full-ROM conditioning — interpreted by the authors as reflecting
**less fatigue accumulation** from the partial-ROM conditioning set. This is fatigue-*adjacent*
evidence (a conditioning exercise's fatigue carrying over to affect subsequent push-up performance),
not a direct measurement of fatigue developing *within* a push-up set itself.

## 4. Cross-referenced: the generic joint-based fatigue/recovery model (already archived)

**Frey-Law, Looft & Heitsman (2012)**, PMID 22579269 — **already fully archived** in
`references/pullup-science/data/fatigue-recovery-rates.csv` and
`references/pullup-science/papers/freylawlooft2012-3cc-endurance-times.xml`. **Not re-downloaded
this session**, per the task brief's explicit instruction to cross-reference rather than duplicate.

This is a **joint-generic** (not pull-up-specific, not exercise-specific) three-compartment-controller
(3CC) fatigue/recovery model, fit to sustained isometric MVC-normalized tasks at the elbow, shoulder,
trunk, hand/grip, knee and ankle. Because the model's compartments are indexed by *joint*, not by
*exercise*, its shoulder, elbow and trunk fatigue-rate (F) and recovery-rate (R) constants apply
equally well to a push-up muscle-heat-map model as they already do to the pull-up pipeline — a
push-up loads the elbow extensors, shoulder horizontal adductors/flexors, and trunk stabilizers
rather than the pull-up's elbow flexors and shoulder adductors, but the *rate constants themselves*
are joint properties, not movement-direction properties, in this model's own formulation.

Key values (full table, including the Looft, Herkert & Frey-Law 2018 rest-multiplier extension, is
in `references/pullup-science/data/fatigue-recovery-rates.csv` — not duplicated here):

| joint | fatigue rate F (1/s) | recovery rate R (1/s, during contraction) |
|---|---|---|
| shoulder | 0.01820 | 0.00168 |
| elbow | 0.00912 | 0.00094 |
| trunk | 0.00755 | 0.00075 |

**Recommendation for the push-up model**: reuse these three rows directly (shoulder highest
fatigue rate of the three, matching the general expectation that the shoulder is the "weak link" in
a sustained pressing task), and reuse the same 3CC-r rest-multiplier logic (recovery ≈15× faster
during a rest interval than during ongoing contraction) that the pull-up pipeline already applies —
there is no push-up-specific reason to expect this general result to differ by exercise.

## 5. What the model should use, given the gap

1. **There is no sourced rep-by-rep degradation curve for push-up-specific kinematics or EMG** — do
   not invent a "hip sag increases by X° per rep" or "elbow angle at the bottom shrinks by Y° per
   rep" constant. If the pipeline needs *some* within-set degradation signal, the two closest sourced
   proxies are (a) Eckel 2017's reps-to-failure counts (a single endpoint number, not a curve) and
   (b) the generic Frey-Law/Looft joint-fatigue-rate model in §4, which *does* produce a continuous
   time-course, just not one derived from push-up motion capture specifically.
2. **Rozenek 2022's cadence-dependent force-redistribution finding (§2)** is worth reporting as
   context for why a fatiguing set might show handshift/technique changes, but should be labeled
   explicitly as a *between-cadence* finding, not a *within-set-fatigue* finding, if used in the
   report copy.
3. **A future session's most promising next search targets**, not yet tried: (a) a push-up-specific
   Zhang-2022-style ultra-endurance case study (the pull-up archive found exactly this shape of paper
   for pull-ups, PMID 36618336 — no push-up equivalent was searched for by that specific pattern this
   session); (b) rate of perceived exertion (RPE) progression across a push-up set, which Nakagata
   2022's own Table 3 (see `02-pushup-hand-force-and-joint-moments.md` and
   `papers/nakagata2022-energy-cost-bwre-extract.txt`) shows rising with cadence within a single bout
   (RPE 8→15 across 1→6 reps/min) — not the same as within-a-set-to-failure fatigue, but a real,
   sourced RPE-vs-intensity data point that could be adapted; (c) a direct search of Google
   Scholar/ResearchGate for unpublished theses on push-up EMG fatigue, since Eckel et al. 2017 itself
   was only found via an institutional lab-page PDF mirror rather than a standard database.
