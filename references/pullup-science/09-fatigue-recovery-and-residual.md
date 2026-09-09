# Fatigue that carries over between reps, and what happens in the 5 s after release

Collected to answer: what is the correct scientific term for the state that makes rep 8 of a
~45 s set hotter than rep 1, what are the right joint-specific fatigue (F) and recovery (R)
rates for the three-compartment model already in `tools/scripts/pullup_thermal4.py`, what
recovery rate applies during the ~5 s after Dennis lets go of the bar (rest, not work), and
what stays warm for longer than that. Every number is in
`data/fatigue-recovery-rates.csv` (columns: quantity, joint_or_muscle, value, unit, condition,
source, pmid_or_doi, table_or_figure, note). Abstracts in `abstracts/*.txt`, full text where
obtained in `papers/*`, download log in `DOWNLOADS.md`.

Two of the user's remembered citations turned out to have the wrong year or wrong first
author; both are corrected below and the correction is called out where it matters:
- "Frey-Law, Looft & Heitsenrether 2012" is actually **Frey-Law, Looft & Heitsman 2012**
  (J Biomech 45:1803-8, PMID 22579269) — third author's name is Heitsman, not Heitsenrether.
- "Sahlin, Harris & Hultman 1979" is actually **Harris, Edwards, Hultman, Nordesjö, Nylind &
  Sahlin 1976** (Pflügers Arch 367:137-42, PMID 1034909) — Sahlin is the *last* author, not
  first, and the year is 1976.
- "Edwards 1977" is actually **Edwards RH 1981** (Ciba Found Symp 82:1-18, PMID 6117420).

## The name for the carried-over state

**The modelling literature's own name for it is the fatigued compartment, M_F** — Xia & Frey
Law (2008), Frey-Law et al. (2012), Sonne & Potvin (2016) and Looft et al. (2018) all use
exactly this: motor units sit in one of three states, resting (M_R), active (M_A) or fatigued
(M_F), and M_F is what does not go back to zero between contractions. None of these four
papers uses the phrase "residual fatigue," "cumulative fatigue" or "incomplete recovery" for
it — they simply call it "fatigue" and "recovery" of the compartment. A PubMed title search for
`"residual fatigue"` returns 23 hits, but essentially all of them are either day-to-day
training-load fatigue (fatigue that lingers between *sessions*, e.g. PMID 41994354's
"prolonged residual fatigue" after repeated-sprint training, measured in days) or, confusingly,
materials-engineering "residual fatigue life" (unrelated field, matched on the words only). So
**"residual fatigue" is a real term but the wrong timescale** for what happens between reps 45 s
apart — do not cite it for that.

The right off-the-shelf phrase for the sub-minute mechanism *is* used, just not with the word
"residual": Carroll, Taylor & Gandevia's 2017 review (PMID 27932676) describes exactly this
regime as **peripheral fatigue with incomplete recovery** — their own words are "complete
recovery of muscle function may be incomplete for some hours" and "recovery of peripheral
fatigue... is typically incomplete for at least 20-30 min" after brief high-intensity exercise.
That is the citable term to put in the report/caption if a term is needed: *the model tracks
peripheral fatigue with incomplete recovery, carried in the fatigued motor-unit pool M_F*.

Three named, sourced mechanisms sit underneath that one label, all active during Dennis's set
and all clearing at different rates once he lets go:

1. **Phosphocreatine (PCr) depletion with incomplete resynthesis between reps.** Each pull
   draws down PCr; the fast recovery component has a half-time of 21-22 s at rest with normal
   blood flow (Harris et al. 1976, PMID 1034909) to 56.6 s after a maximal 30 s sprint-type
   effort (Bogdanis et al. 1995, PMID 7714837). Dennis's inter-rep rest is under 1 s — nowhere
   near even the fast half-time — so PCr free-falls across the set exactly as M_F assumes with
   no built-in per-rep recovery term.
2. **Inorganic phosphate (Pi) and H+ accumulation reducing cross-bridge force and Ca2+
   sensitivity.** This is the mechanistic explanation in Allen, Lamb & Westerblad's 2008
   Physiol Rev review (PMID 18195089, open-access status: closed, abstract only obtained) for
   *why* force drops as the set goes on beyond "the motor units ran out" — it is a direct
   biochemical brake on the contractile machinery, and it is also the biochemical substrate
   of low-frequency fatigue (below).
3. **Intramuscular blood-flow occlusion above roughly 50-64% MVC.** Sadamoto, Bonde-Petersen &
   Suzuki (1983, PMID 6685038) measured the %MVC at which rising intramuscular tissue pressure
   stops measured muscle blood flow directly (Xenon clearance) in elbow flexors, knee extensors
   and plantar flexors: **50-64% MVC**, muscle-dependent. Sjøgaard, Savard & Juel (1988, PMID
   3371342) confirm blood flow is adequate only below about 10% MVC for sustained contraction.
   Barcroft & Millen (1939, PMID 16995147) is the foundational demonstration that blood flow
   through a working muscle falls as sustained tension rises (pre-abstract-era record, no
   numeric threshold recoverable from PubMed, but it is the paper the later quantitative work
   builds on). Bigland-Ritchie et al. (1986, PMID 3560001) show directly that recovery of
   motoneurone firing rate needs the blood supply restored, not just elapsed time: "near full
   recovery 3 min after the blood supply was restored" but "no recovery... if the fatigued
   muscle was kept ischaemic." **This is why the grip and the lats, never fully relaxed inside
   the set (a strict dead-hang pull-up keeps the shoulder adductors and the forearm flexors
   working well above the occlusion threshold through most of the cycle), cannot clear PCr,
   Pi or H+ until Dennis actually lets go** — release removes the mechanical occlusion and
   starts reactive hyperaemia, which is the physiological trigger for the ~5 s cool.

## 1. Xia & Frey Law 2008 — the model's own equations

*A theoretical approach for modeling peripheral muscle fatigue and recovery.* J Biomech
41(14):3046-52. PMID 18789445, doi:10.1016/j.jbiomech.2008.07.013. Closed access (Elsevier,
confirmed via Unpaywall) — abstract only obtained.

Confirms the model structure already in the code: three states resting M_R, active M_A,
fatigued M_F; a bounded proportional controller handles the M_R <-> M_A transfer
(activation/deactivation); F and R govern the M_A <-> M_F transfer. The abstract explicitly
frames this as reproducing "Rohmert's curves" (the classic empirical intensity-endurance-time
relationship) and extends to a three-fibre-type, last-in-first-out recruitment stack for more
complex/dynamic loading — a refinement not currently used in `pullup_thermal4.py` but available
if per-fibre-type recruitment order ever matters for the heat map.

## 2. Frey-Law, Looft & Heitsman 2012 — the actual joint-specific F, R table

*A three-compartment muscle fatigue model accurately predicts joint-specific maximum endurance
times for sustained isometric tasks.* J Biomech 45(10):1803-8. PMID 22579269,
doi:10.1016/j.jbiomech.2012.04.018, PMCID PMC3397684. **Open access** — full text XML fetched
(`papers/freylawlooft2012-3cc-endurance-times.xml`).

Table 1 (over 1 million F/R permutations fit by grid search against 9 intensities x 6 joint
regions):

| Joint region | F (1/s) | R (1/s) | F:R ratio | Predicted intensity asymptote (%MVC) |
|---|---|---|---|---|
| Ankle | 0.00589 | 0.00058 | 10.2 | 8.96 |
| Knee | 0.01500 | 0.00149 | 10.1 | 9.04 |
| Trunk | 0.00755 | 0.00075 | 10.1 | 9.04 |
| **Shoulder** | **0.01820** | **0.00168** | 10.8 | 8.45 |
| **Elbow** | **0.00912** | **0.00094** | 9.7 | 9.34 |
| **Hand/Grip** | **0.00980** | **0.00064** | 15.3 | 6.13 |
| General (pooled) | 0.00970 | 0.00091 | 10.7 | 8.57 |

**This is the actual source table for the code's `FATIGUE` dict, and it does not match what
the code has**, beyond the elbow row (see "What the model should do" below for the specific
corrections). The paper's per-joint RMS errors on maximum endurance time were small: shoulder
2.7 s, hand/grip 5.6 s, knee 6.7 s, trunk 9.3 s, elbow 9.9 s, ankle 11.2 s — the model is
well-validated for isometric endurance, which is the closest single-rep analogue to a pull-up's
concentric/isometric-hold phase.

## 3. Looft, Herkert & Frey-Law 2018 — R during rest vs. work

*Modification of a three-compartment muscle fatigue model to predict peak torque decline during
intermittent tasks.* J Biomech 77:16-25. PMID 29960732, doi:10.1016/j.jbiomech.2018.06.005,
PMCID PMC6092960. **Open access** — full text XML fetched
(`papers/looft2018-3cc-r-intermittent.xml`).

This is the key paper for the user's actual question. The original 3CC model (Xia & Frey Law
2008 / Frey-Law et al. 2012) uses a single recovery rate R at all times. Applied to
*intermittent* contractions — any task with rest periods, which a pull-up set is, both the
sub-second gap between reps and the long release at the end — the original model
**over-predicts fatigue by 19-29% torque decline** against a 63-study meta-analysis, because it
has no way to represent that a resting muscle re-perfuses and clears metabolites faster than a
working one. The fix, the **modified 3CC-r model**:

    while producing force (TL > 0):  dM_R/dt = -C(t) + R · M_F            (unchanged)
    at rest (TL = 0):                dM_R/dt = -C(t) + (R · r) · M_F      (recovery boosted by r)

r = 1 recovers the original model exactly. A grid search over r = 2 to 100 against the same
63-study meta-analysis found:

| Joint region | r (candidate range) | **Final r used** | R x r during rest (1/s) |
|---|---|---|---|
| Ankle | 15 [12-19] | 15 | 0.0087 |
| Knee | 12-13 [7-21] | 15 | 0.02235 |
| Elbow | 8-10 [5-17] (AIC not different at r=15) | **15** | 0.0141 |
| Hand/Grip | 27-37 [14-69] | **30** | 0.0192 |
| General (all) | 15 [8-29] | 15 | 0.01365 |

With this correction, the model's error on intermittent tasks drops to 6-10% torque decline.
**The elbow, knee and ankle all converge on the same r = 15 once rounded for consistency; grip
is genuinely different at r = 30** — the paper attributes this to grip/forearm muscle having
disproportionately fast reactive vasodilation and post-contraction hyperaemia, which matches
Sjøgaard et al. 1988 and Sadamoto et al. 1983 above. **The shoulder was not one of the four
joint regions in Looft 2018's 63-study meta-analysis** (only ankle, knee, elbow and hand/grip
had enough intermittent literature) — there is no shoulder-specific r; the paper's own
"General (all)" value (r = 15) is the best available stand-in and should be flagged as
extrapolated if used for the shoulder/lats.

Controller gains: confirmed L_D = L_R = 10 /s (Table 4 footnote), matching the code exactly.

## 4. Liu, Brown & Yue 2002 — the original two-parameter model and its terminology

*A dynamical model of muscle activation, fatigue, and recovery.* Biophys J 82(5):2344-59. PMID
11964225, PMCID PMC1302027 (publisher blocks XML download from PMC; abstract only obtained).

Predates Xia & Frey Law 2008 and uses the same two-parameter (F, R) idea in a slightly
different equation form, validated against a 3-min sustained maximal handgrip contraction —
the single most pull-up-relevant validation task in this whole set of papers, since it is
isometric grip, not knee or elbow. Notable finding: the model implies **only 97% of true
maximal force is achievable under maximal voluntary effort** even with full motor-unit
recruitment — a ceiling effect worth knowing if the heat map's `a_eff = a/(1-M_F)` term is ever
allowed to approach 1. Terminology: the paper calls the two parameters simply "fatigue" and
"recovery" and does not use "residual" or "cumulative" fatigue language either.

## 5. Sonne & Potvin 2016 — a second, physiologically-motivated variant

*A modified version of the three-compartment model to predict fatigue during submaximal tasks
with complex force-time histories.* Ergonomics 59(1):85-98. PMID 26018327 (closed access,
confirmed via Unpaywall — abstract only).

A different modification from Looft 2018 (graded motor-unit recruitment order, "3CM(GMU)"
rather than a rest multiplier), validated against submaximal force *plateaus* rather than
intermittent rest — it explicitly says the model "performed poorly for endurance tasks," i.e.
it is not a substitute for Frey-Law 2012's endurance-time-fit F/R values or for Looft 2018's
rest multiplier; it is a complementary model for graded submaximal force profiles. Not used for
any number in this deliverable beyond confirming the "3CC family" naming convention.

## 6. Phosphocreatine resynthesis kinetics — the ~5-60 s scale for the release

- **Harris, Edwards, Hultman, Nordesjö, Nylind & Sahlin 1976** (Pflügers Arch 367:137-42, PMID
  1034909, closed access, abstract only): quadriceps PCr falls to 15-16% of resting content
  after exhaustive dynamic or isometric-to-fatigue exercise; resynthesis is **biphasic**, fast
  component half-time **21-22 s**, slow component half-time **>170 s**; resynthesis is
  **completely abolished under circulatory occlusion** and resumes only on cuff release — this
  last point is the direct physiological reason the model should not let any muscle cool while
  it is still under load, only after release.
- **Bogdanis, Nevill, Boobis, Lakomy & Nevill 1995** (J Physiol 482:467-80, PMID 7714837,
  PMCID PMC1157744, closed to XML/PDF download — abstract only): after 30 s of *maximal sprint*
  effort (more depleting than isometric-to-fatigue: PCr falls to 19.7% of rest), the
  single-exponential half-time for PCr resynthesis is **56.6 ± 7.3 s** — slower than Harris
  1976's fast component because of the added glycolytic acidosis (muscle pH 6.72 at end of
  sprint). PCr reaches 65.0% of rest at 1.5 min, only 85.5% at 6 min. Power output recovery
  tracks PCr resynthesis closely (r = 0.71-0.86) and *not* pH.
- **Bogdanis, Nevill, Boobis & Lakomy 1996** (J Appl Physiol 80(3):876-84, PMID 8964751, closed
  access, abstract only): confirms 78.7% PCr resynthesis at 3.8 min; also shows a **second**
  30 s sprint after 4 min of rest still has 41% less anaerobic ATP turnover than the first
  (235 -> 139 mmol/kg dry muscle) despite total work falling by only ~18%, because aerobic
  metabolism compensates ~49% of the second bout's energy. Relevant if the model is ever
  extended to a second *set*, not just this set's 8 reps.
- **Sahlin & Ren 1989** (J Appl Physiol 67(2):648-54, PMID 2793665, closed access, abstract
  only): the cleanest number for "how fast does force itself come back" — after a fatiguing
  knee-extension contraction at 66% MVC, **force half-time recovery is under 15 s**, essentially
  full recovery by 2 min, while **endurance (time-to-fatigue) recovers much more slowly**
  (half-time ~1.2 min, still significantly depressed at 4 min). This is the paper that best
  supports letting the model's *visible force/heat* cool quickly toward a floor while a slower
  "capacity" variable (closer to what M_F should represent) stays depressed longer.

## 7. Low-frequency fatigue / PLFFD — the part that does not clear in 5 s

- **Edwards RH 1981** (not 1977 — Ciba Found Symp 82:1-18, PMID 6117420, closed access,
  abstract only): the original distinction between **high-frequency fatigue** (impaired muscle
  membrane excitation, "recovers rapidly") and **low-frequency fatigue** (impaired
  excitation-contraction coupling, "long-lasting").
- **Jones 1996** (Acta Physiol Scand 156(3):265-70, PMID 8729686, closed access, abstract
  only), "High- and low-frequency fatigue revisited": high-frequency fatigue is tied to K+
  accumulation in t-tubules and interfibre spaces and is "rapidly reversed" even under
  ischaemic conditions if the muscle is re-extended; low-frequency fatigue is tied to reduced
  Ca2+ release and recovers "over the course of **hours or even days**."
- **Allen, Lamb & Westerblad 2008** (Physiol Rev 88(1):287-332, PMID 18195089, closed access,
  abstract only), the standard modern mechanism review: reduced SR Ca2+ release and reactive
  oxygen species effects, not lactate/H+ directly, are now considered the dominant mechanisms
  in mammalian muscle — this is the citation for *why* some fraction of contractile capacity
  stays down long after PCr and even after M_F itself would predict recovery.
- **Carroll, Taylor & Gandevia 2017** (J Appl Physiol 122(5):1068-76, PMID 27932676, closed
  access, abstract only): ties the timescales together explicitly — central fatigue recovers
  in ~2 min, peripheral fatigue tied to excitation-contraction coupling and reperfusion in
  ~3-5 min, but "complete recovery of muscle function may be incomplete for some hours" due to
  prolonged Ca2+-release impairment. **This is the floor**: nothing in this literature supports
  the whole body cooling to baseline in 5 s: at best the fast (PCr, reperfusion) component
  starts clearing; the slow (Ca2+-release) component has not even begun.

## 8. Repeated-bout carry-over

- **Bigland-Ritchie, Dawson, Johansson & Lippold 1986** (J Physiol 379:451-9, PMID 3560001,
  PMCID PMC1182907, publisher blocks XML/PDF — abstract only): the requested "recovery of MVC
  after fatiguing contractions" angle is better covered by Sahlin & Ren 1989 above; this 1986
  paper's actual finding is that motoneurone firing-rate recovery needs **restored blood
  flow**, not just elapsed time — "near full recovery 3 min after the blood supply was
  restored" vs. no recovery at all if kept ischaemic. Used here as direct evidence for the
  occlusion mechanism (item 3 under "The name for the carried-over state") rather than as an
  MVC-recovery-curve source. Sánchez-Medina & González-Badillo 2011 is already covered
  elsewhere in this repo per the brief and was not re-fetched.

## What the model should do

**(a) The term.** Call it **peripheral fatigue with incomplete recovery** if a term is needed
in prose (Carroll, Taylor & Gandevia 2017, PMID 27932676); mechanically, it is carried in
**the fatigued motor-unit compartment M_F** of the Xia & Frey-Law (2008) three-compartment
model already in the code — that is the term the governing papers themselves use, and it is
the right one to keep in comments/reports. Do **not** call it "residual fatigue": that phrase
is real in the literature but denotes fatigue carried across days/sessions, a different
mechanism at a different timescale.

**(b) F and R corrections.** Against `references/pullup-science/data/fatigue-recovery-rates.csv`
and Frey-Law, Looft & Heitsman (2012) Table 1:

| Joint | Code has (F, R) | Confirmed value | Verdict |
|---|---|---|---|
| Elbow | (0.00912, 0.00094) | (0.00912, 0.00094) | **CONFIRMED**, exact match |
| Shoulder | (0.00589, 0.00058) | **(0.01820, 0.00168)** | **WRONG** — code's numbers are Table 1's *ankle* row, not shoulder's. Shoulder fatigues ~2x faster than elbow (not slower, as the current code comments claim) |
| Grip | (0.00980, 0.00091) | F confirmed (0.00980); **R should be 0.00064** | R **WRONG** — code used the *General* pooled R, not grip's own row |
| Trunk | (0.00589, 0.00058), copy of shoulder's | **(0.00755, 0.00075)** | **WRONG** — trunk has its own row in the same table and was never given it |
| Leg | (0.00589, 0.00058), copy of shoulder's | ankle (0.00589, 0.00058) if "leg" = ankle/lower-leg; knee (0.01500, 0.00149) if "leg" should track the knee/thigh | Coincidentally now correct **if** "leg" was meant to mean ankle; mislabelled either way and should be assigned deliberately, not inherited from "shoulder" |

This also means the existing narrative in `pullup/MUSCLE-MODEL.md` ("the elbow's fatigue rate
is 1.5x the shoulder's") is backwards: with the corrected shoulder row, the **shoulder's F
(0.0182) is exactly 2.0x the elbow's F (0.00912)** — the shoulder should empty its active pool
*faster* than the elbow, not slower, everything else being equal. That narrative line needs to
be rewritten if these corrected numbers are adopted (out of scope for this note — flagged for
whoever edits `pullup_thermal4.py` next).

**(c) R during rest vs. work.** Use Looft, Herkert & Frey-Law's (2018) 3CC-r modification: keep
R unchanged while a joint is under load (TL > 0); multiply R by **r = 15** for every joint
except grip whenever that joint is at rest (TL = 0, no force being produced — the sub-second
gap between reps counts, and so does the final release). **Grip gets its own multiplier,
r = 30** — twice the other joints' — matching its distinctly faster reactive hyperaemia in
Sjøgaard 1988 and Sadamoto 1983. There is no shoulder-specific r (Looft 2018's meta-analysis
did not include the shoulder); use the shared r = 15 as the best available estimate and flag it
as extrapolated, not fitted.

**(d) PCr-scale recovery constant for the ~5 s after release.** Use the **fast component's
half-time, 21-22 s** (Harris et al. 1976) as the ceiling — the "generous" end, since Dennis's
set is closer to isometric-to-fatigue than to a 30 s maximal sprint (Bogdanis 1995's 56.6 s
half-time is for a more depleting effort). At the fast half-time, 5 s of recovery moves the
fast PCr pool only **1 − 2^(−5/21.5) ≈ 15%** of the way back — i.e., **only a small, visible
dip is physiologically justified in the last 5 s**, consistent with what Dennis asked for
("only slightly cools"). Do not use a faster time constant than this to make the cool-down
more dramatic — 15% in 5 s is already close to what the literature supports as the *fastest*
plausible component; combined with r = 15-30 applied to M_F specifically (which is a
different, model-internal quantity, not literally PCr), the two together set the pace at which
the colour should relax once TL = 0.

**(e) The slow component that stays.** Low-frequency fatigue / prolonged low-frequency force
depression (Edwards 1981; Jones 1996; Allen, Lamb & Westerblad 2008) recovers over **hours to
days**, not seconds — functionally infinite on the timescale of a video. The model should keep
a slowly-clearing floor (a small fraction of M_F, or a separate slow state, that essentially
does not move in the 5 s of release shown on screen) on top of the fast-clearing component
described in (d). Carroll et al. (2017)'s time-banding — central ~2 min, peripheral
excitation-contraction-coupling/reperfusion ~3-5 min, Ca2+-release impairment "some hours" — is
the citable structure for a three-tier (fast/medium/slow) cooling curve if the model is ever
extended past a single 5 s release.

**Summary of what was confirmed vs. corrected vs. unverifiable, against the code's
from-memory numbers (`tools/scripts/pullup_thermal4.py` line 187):**
- **Confirmed exactly**: elbow F & R (0.00912, 0.00094); grip F (0.00980); controller gains
  L_D = L_R = 10/s.
- **Corrected**: shoulder F & R (were the ankle row; should be 0.01820, 0.00168); grip R (was
  the general-pooled row; should be 0.00064); trunk F & R (was a copy of the wrong ankle row;
  should be 0.00755, 0.00075).
- **New, not previously in the code at all**: the rest-recovery multiplier r (15 general, 30
  grip, Looft et al. 2018) — the code's `FATIGUE` dict currently has no rest-vs-work
  distinction at all, so every rep's inter-rep micro-recovery and the final release are
  presumably using the same (work-rate) R throughout, which both over-predicts fatigue by
  Looft 2018's own 19-29% figure and gives no basis for "only slightly cools" after release.
- **Could not be verified / no data exists**: a shoulder-specific rest multiplier (not in
  Looft 2018's meta-analysis; use the general r = 15 as an explicitly-flagged estimate); an
  exact numeric occlusion threshold from Barcroft & Millen 1939 (title-only PubMed record,
  pre-dates abstracting; Sadamoto 1983's 50-64% MVC is the modern number used instead).
