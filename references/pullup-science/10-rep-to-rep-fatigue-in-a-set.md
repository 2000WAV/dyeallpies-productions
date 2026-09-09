# Rep-to-rep fatigue evidence within a single set (for the compounding heat-map colour)

Built for the muscle heat-map video: Dennis wants each rep of an ~8-rep, ~45 s set to look
"hotter" than the last, and the body to cool only slightly in the ~5 s after he lets go of the
bar. This file collects the MEASURED, rep-by-rep (or set-by-set) evidence for (1) fatigue
compounding within one set of resistance exercise, (2) how much recovers during a short rest,
and (3) how fast muscle temperature actually falls once exercise stops. It is the *observable*
half of the argument — another agent is covering the underlying fatigue-model mechanism papers
(Xia & Frey-Law 2008, Frey-Law 2012, Looft 2018, Liu 2002, PCr resynthesis, low-frequency
fatigue reviews); this file does not repeat those, but does report the mechanism-relevant
*measurements* (blood-flow occlusion thresholds, low-frequency-fatigue persistence times) the
mechanism papers would need to be consistent with.

**Headline finding, and its limit:** almost nothing in the literature measures rep-by-rep
velocity or EMG *inside* a single ~8-rep pull-up set to failure — studies either report
whole-set summary statistics (velocity loss at failure, peak power loss across 5 sets) or use a
much longer exercise (leg press/bench press to failure, or a 330-rep pull-up "set" in the one
ultra-endurance case study located). Every specific rep-count or percentage below states its
exercise and whether it is pull-up-specific or transferred from another exercise. No number in
this file is invented; gaps are stated as gaps.

## 0. What "each rep hotter" needs, broken into three measurable claims

1. **Within-set fatigue compounds monotonically (or near-monotonically) as reps accumulate** —
   supported indirectly (pull-up: R²=.88 velocity-loss-vs-%-reps-done relationship) and directly
   (EMG amplitude rises rep-by-rep in non-pull-up sets to failure, with a plateau only in the
   final few reps before failure).
2. **A pull-up's inter-rep "rest" does not fully reset the fatigue clock**, because unlike a
   racked barbell, the hands and lats stay under load in the low-hang or top-hold between reps —
   this is a mechanistic argument built from grip-occlusion physiology (§4) plus what the
   cluster-set literature's "rest" actually consists of (§3), not from a pull-up-specific
   inter-rep-recovery measurement (none was found).
3. **5 s after release is too short to see visible cooling**, because measured post-exercise
   muscle-temperature decay is a many-minutes process, not a few-seconds one (§5).

## 1. Pull-up-specific velocity loss across a set

- **Sánchez-Moreno, Rodríguez-Rosell, Pareja-Blanco, Mora-Custodio & González-Badillo (2017).**
  Movement Velocity as Indicator of Relative Intensity and Level of Effort Attained During the
  Set in Pull-Up Exercise. *Int J Sports Physiol Perform* 12(10):1378-1384.
  doi:10.1123/ijspp.2016-0791. PMID 28338365. Closed access (already archived, `02-biomechanics-
  and-velocity.md`; not re-fetched). **PULL-UP-SPECIFIC.** 52 trained men; sets to failure at
  several relative loads, mean propulsive velocity on every rep via linear velocity transducer.
  **% velocity loss within a set correlates with % of maximum possible reps already completed at
  R²=.88**, stable after a 12-week training program that raised max reps ~15%. This is the best
  pull-up-specific evidence that velocity loss is a *reliable, monotonically-tracking* proxy for
  how far into the set (i.e., how fatigued) the person is — exactly the shape needed to drive a
  rep-by-rep heat ramp. **Gap:** the literal regression slope/intercept behind R²=.88 is in the
  paywalled tables, not the abstract — any slope used in the model is a *fitted approximation to
  this shape*, not this paper's own published constant.
- **Sánchez-Moreno, Cornejo-Daza, González-Badillo & Pareja-Blanco (2020).** Effects of Velocity
  Loss During Body Mass Prone-Grip Pull-up Training on Strength and Endurance Performance.
  *J Strength Cond Res* 34(4):911-917. doi:10.1519/JSC.0000000000003500. PMID 32213783. Closed
  access (already archived). **PULL-UP-SPECIFIC.** 29 strength-trained men, 8-week RCT, VL25 vs
  VL50 (stop the set at 25% vs 50% cumulative velocity loss). VL25 produced strictly greater
  strength/velocity gains; going on to 50% loss bought no extra max-rep endurance. Used here as
  the landmark for "still-productive" vs. "purely fatigue-accumulating" territory within a set —
  a near-failure ~8-rep set (like Dennis's) is, by definition, deep in VL50+ territory by its
  final reps.
- **Sánchez-Medina & González-Badillo (2011).** Velocity loss as an indicator of neuromuscular
  fatigue during resistance training. *Med Sci Sports Exerc* 43(9):1725-1734.
  doi:10.1249/MSS.0b013e318213f880. PMID 21311352. `abstracts/sanchezmedina2011-pmid21311352.txt`
  (re-fetched this session; an older copy already existed at `../pullup-emg/pmid21311352-
  abstract.txt` from 2026-09-05, same text). Closed access. **NOT pull-up-specific** (bench
  press/squat, 18 strength-trained men, 15 rep×set×load protocols, 5-min inter-set rests) —
  **transferred.** Within-set velocity loss correlates with post-exercise lactate at
  **r = 0.93-0.97** and with countermovement-jump-height loss at **r = 0.91-0.97**. Ammonia rises
  only once reps completed exceed roughly half the predicted maximum — i.e. the metabolic
  fatigue signal is **non-linear/accelerating** past the set's midpoint, not flat. This is
  transferable justification for a heat curve that accelerates toward the end of the set rather
  than rising in equal steps per rep.

## 2. EMG amplitude rise and frequency fall rep-by-rep in a set to failure

No pull-up-specific EMG-to-failure study with rep-by-rep numbers was located (the closest
pull-up EMG data, Youdas 2010 and Dickie 2017, are whole-rep or phase-averaged, not tracked
across a set to failure — see `07-phase-resolved-emg.md`). All of the following are **NOT
pull-up-specific — transferred** from other resistance exercises, chosen because they report the
first-to-last-rep (or first-to-failure) EMG amplitude and frequency change explicitly.

- **Sundstrup, Jakobsen, Andersen, Zebis & Mortensen (2012).** Muscle activation strategies
  during strength training with heavy loading vs. repetitions to failure. *J Strength Cond Res*
  26(7):1897-1903. doi:10.1519/JSC.0b013e318239c38e. PMID 21986694. Closed access. 15 untrained
  women; lateral raise with elastic tubing, ~15RM set to failure. **Normalized EMG amplitude rose
  from 86% to 124% MVC (trapezius) across the set, in a curvilinear fashion, reaching a plateau
  in the final 3-5 repetitions before failure (P<0.001).** Median power frequency for all
  examined muscles **decreased linearly** through the set. This is the single cleanest
  first-to-last-rep %MVIC pair found in this sweep, and it directly supports the requested shape:
  amplitude climbs rep-by-rep, but with diminishing returns very close to failure (the last 1-2
  reps of an 8-rep set should not be drawn *dramatically* hotter than the 6th/7th — the literature
  says the increase is already flattening by then), while frequency compression is closer to
  linear throughout.
- **Tsoukos, Brown, Terzis, Wilk, Zajac & Bogdanis (2021).** Changes in EMG and movement velocity
  during a set to failure against different loads in the bench press exercise. *Scand J Med Sci
  Sports* 31(11):2071-2082. doi:10.1111/sms.14027. PMID 34329514. Closed access. 14 men; sets to
  failure at 40/60/80%1RM, sEMG of pectoralis major and triceps brachii, time-under-tension
  matched between loads. **sEMG was significantly higher in the middle AND the last repetitions
  compared with the initial repetitions, at every load (P<0.001)** — i.e. the amplitude rise is
  not just an early-vs-late-rep effect, it keeps climbing past the set's midpoint. **Velocity loss
  at exhaustion and the drop in EMG median frequency were both GREATER at 40% and 60%1RM than at
  80%1RM** — lighter, longer sets produce more frequency compression than short heavy ones, which
  is relevant because an 8-rep bodyweight pull-up set (bodyweight ≈ a submaximal relative load
  for someone who can do 8 reps) sits closer to the moderate-load, moderate-duration end of this
  spectrum than to a 1-3RM set.
- **Izquierdo, Ibañez, Calbet et al. (2009).** Neuromuscular fatigue after resistance training.
  *Int J Sports Med* 30(8):614-623. doi:10.1055/s-0029-1214379. PMID 19382055. Closed access.
  12 trained men; 5×10RM leg press, 2-min inter-set rests, sEMG amplitude and spectral indices
  measured before/after. **Peak power loss reached 58-62% (pre-to-post-training comparison at the
  same relative load)**, versus only **12-17% loss in isometric strength** over the same protocol
  — i.e. dynamic/power fatigue within a multi-set session can be 3-5× larger than the isometric
  strength loss measured afterward, a caution against using isometric MVC intuitions to judge how
  much a dynamic effort (like a pull-up) should visibly fatigue.
- **González-Izal, Rodríguez-Carreño et al. / Izquierdo et al. (2010, 2011)** — companion papers
  from the same Navarre lab, same 5×10 leg-press-to-fatigue protocol (12-15 trained subjects,
  2-min inter-set rest): **peak power loss of 46% pretraining, rising to 61% after a strength-
  training period at the same relative load** (Izquierdo/González-Izal 2011, *Med Sci Sports
  Exerc* 43(2):303-311, doi:10.1249/MSS.0b013e3181edfa96, PMID 20581711); a wavelet-based sEMG
  index explained only **46.6-49.8% of the variance** in power loss (González-Izal et al. 2010,
  *J Electromyogr Kinesiol* 20(6):1097-1106, doi:10.1016/j.jelekin.2010.05.010, PMID 20579906) —
  an explicit caution that **EMG amplitude is an imperfect, not 1:1, proxy for mechanical power
  loss**, relevant if the pipeline ever calibrates the heat map's brightness directly off a
  camera-estimated EMG-like signal rather than off velocity/power.
- **Zhang, Khassetarash, Millet & Aboodarda (2022).** Neuromuscular Fatigability Associated with
  Different Pacing Strategies During an Ultra-Endurance Pull-Up Task: A Case Study. *Int J Exerc
  Sci* 15(3):1514-1527. PMID 36618336. PMCID PMC9797014. **Open access — full PDF and text
  extract archived** (`papers/zhang2022-ultraendurance-pullup.pdf` / `-extract.txt`).
  **PULL-UP-SPECIFIC**, but the "set" here is 330 pull-ups (not ~8) done in preparation for a
  world-record attempt (single 31-year-old male athlete, n=1 case study, three pacing
  strategies). Not directly transferable to an 8-rep set, but it is the **only pull-up-specific
  neuromuscular-fatigue-kinetics data found in either research session**, and its qualitative
  shape matters: **elbow-flexor MVC force declined sharply within the FIRST block of pull-ups in
  every pacing condition (-8.6% to -29.1%), before plateauing or continuing more gradually** —
  i.e. even in this athlete, most of a block's fatigue accrues early, echoing the "accelerating
  then plateauing" pattern seen in the transferred EMG-to-failure studies above. Biceps rmsEMG
  during MVC tests **rose through most of a block before dropping right at the end** in two of
  three pacing conditions — a rise-then-fall pattern, not monotonic rise to task end, a nuance
  worth flagging if the model ever extends past ~8 reps toward genuine failure. Grip strength and
  MVC force recovered slowest in the pacing condition with the LONGEST between-block rest
  (paradoxically) — evidence that resuming after a longer break does not fully reset force
  output, i.e. **fatigue truly compounds block-to-block even across rest periods measured in
  minutes**, let alone the ~5 s of a between-rep pull-up hang.

## 3. Recovery of force/velocity over short (5-30 s) rests — and what kind of "rest" it is

**Coordinator's addition, addressed directly: distinguish rest with the muscle relaxed (blood
flow restored) from "rest" with the muscle still loaded.** Every cluster-set/inter-repetition-
rest study below used **unloaded, relaxed rest** — the barbell is racked (bench press, clean
pull) or returned to the floor (Olympic lifts) during the rest interval, so blood flow to the
working muscle is restored during that gap. **This is NOT what happens between reps of a
pull-up**: between reps of a strict pull-up, the athlete is still hanging from the bar (low-hang
or dead-hang), so the grip, forearm flexors, and to a lesser extent the lats/biceps stay under
substantial load — this is a **loaded** rest, structurally closer to Byström & Kilbom's
"continuous" handgrip condition (§4) than to any cluster-set study's racked-bar rest. This
matters for the model: the recovery percentages below are an **upper bound** on how much a
pull-up's own inter-rep gap should be modelled as restorative, not a direct pull-up number.

- **Haff, Whitley, McCoy et al. (2003).** Effects of different set configurations on barbell
  velocity and displacement during a clean pull. *J Strength Cond Res* 17(1):95-103. PMID
  12580663. Closed access. **NOT pull-up-specific — transferred.** 13 men (track/field + Olympic
  weightlifters); cluster vs. traditional vs. undulating set structures, 5-rep sets at 90%/120%
  1RM clean pull. **Cluster sets produced significantly higher peak velocity than traditional
  continuous sets at both intensities (P<0.016)** — the foundational demonstration that inserting
  rest between reps preserves velocity a continuous set would otherwise lose. Rest here = bar
  returned to the floor between reps (fully unloaded).
- **Latella, Teo, Drinkwater, Kendall & Haff (2019).** The Acute Neuromuscular Responses to
  Cluster Set Resistance Training: A Systematic Review and Meta-Analysis. *Sports Med*
  49(12):1861-1877. doi:10.1007/s40279-019-01172-z. PMID 31506904. PMCID PMC6851217. **Open
  access — full text XML archived** (`papers/latella2019-cluster-sets-review.xml`). **NOT
  pull-up-specific — transferred.** 25 pooled studies. Cluster-set (short unloaded rest) vs.
  traditional (continuous) sets: **peak velocity SMD = 0.815, mean velocity SMD = 0.863, mean
  power SMD = 0.692, peak force SMD = 0.306** (all favoring cluster sets, the smallest and least
  certain effect being on peak force). The **intra-set/inter-repetition rest durations pooled
  across the 25 studies ranged from 6.0 to 45.4 s**, with Haff et al. elsewhere suggesting
  **15-30 s** as long enough to measurably blunt fatigue markers. One individual dataset cited
  inside the review (Lawton et al. 2006, bench press, not independently re-fetched this session)
  found power reduced by 53.8 W with 23 s of inter-repetition rest vs. 66.9 W with 56 s and 57.0 W
  with 109 s of intra-set rest — **not a clean monotonic "more rest = more recovery" relationship
  at these short durations**, a caution against assuming linear dose-response. The review found
  **no significant difference between inter-repetition rest, intra-set rest, and rest-pause
  structures** (Q[3]=2.675, p=0.367) — i.e. it is the presence and total amount of unloaded rest
  that matters, not its exact distribution.
- **Jukic, Ramos, Helms, McGuigan & Tufano (2020).** Acute Effects of Cluster and Rest
  Redistribution Set Structures on Mechanical, Metabolic, and Perceptual Fatigue During and After
  Resistance Training: A Systematic Review and Meta-analysis. *Sports Med* 50(12):2209-2236.
  doi:10.1007/s40279-020-01344-2. PMID 32901442. Closed access (confirmed via Europe PMC, no
  PMCID). **NOT pull-up-specific — transferred.** This is the Tufano-authored review matching the
  brief's "Tufano review" request (32 pooled studies, not the older Tufano 2016/2017 single-author
  pieces, which were not independently re-located this session). **Alternative (cluster/rest-
  redistribution) set structures mitigated the velocity/power DECLINE during a session with SMD
  0.83-1.97** — a substantially larger effect than their effect on absolute velocity/power values
  themselves (SMD 0.33-0.60) — i.e. short rest matters most for **blunting the within-set decline
  curve**, exactly the mechanism the heat map needs to reproduce in reverse (no rest → steeper
  climb). Lactate accumulation was reduced with SMD = 1.61, RPE with SMD = 0.81. **Cluster sets
  (short, evenly-spaced rest) were more effective than rest redistribution (same total rest,
  concentrated differently)** — total rest time is necessary but the distribution also matters.
- **García-Ramos, González-Hernández, Baños-Pelegrín et al. (2020).** Mechanical and Metabolic
  Responses to Traditional and Cluster Set Configurations in the Bench Press Exercise.
  *J Strength Cond Res* 34(3):663-670. doi:10.1519/JSC.0000000000002301. PMID 29076963. Closed
  access. **NOT pull-up-specific — transferred, but the single most useful explicit number set in
  this file for "how much recovers with short rest."** 10 men; five 10RM-load, 30-total-rep
  configurations differing only in intra-set rest: TR1 = 3×10 continuous (0 s), TR2 = 6×5
  continuous (0 s), CL5/CL10/CL15 = 3×10 with 5/10/15 s of rest after every 2 reps. **Velocity
  loss from first to last set: TR1 -39.3%, CL5 -20.2%, CL10 -12.9%, TR2 -10.3%, CL15 -10.0%.**
  Even **5 s** of unloaded rest roughly **halved** the velocity loss relative to no rest at all;
  **10-15 s** reduced it to roughly **a quarter** of the no-rest value. Blood lactate tracked the
  same ordering (TR1 7.9 → CL15 3.4 mmol/L). **Caveat for this model:** this rest is fully
  unloaded (bar racked); a pull-up's ~5 s between-rep hang is loaded, so this halving effect is an
  optimistic ceiling, not a like-for-like pull-up number.
- **Torrejón, Janicijevic, Haff & García-Ramos (2019).** Acute effects of different set
  configurations during a strength-oriented resistance training session on barbell velocity and
  the force-velocity relationship in resistance-trained males and females. *Eur J Appl Physiol*
  119(6):1409-1417. doi:10.1007/s00421-019-04131-8. PMID 30955089. Closed access. **NOT
  pull-up-specific — transferred.** 13 men + 13 women; bench press, 24 reps at 6RM comparing
  traditional (3-min inter-set rest), cluster (15 s intra-set rest), and inter-repetition rest
  (IRR: 39 s rest after every single rep) configurations. Whole-session velocity loss was
  **comparable for men and women (-12.1% vs -11.3%)**; the IRR configuration (most rest per rep)
  produced **higher velocity specifically on the LAST repetition of each mini-set**, even though
  average session velocity did not differ between configurations — short unloaded rest protects
  the *end* of a set more than it raises the *average*. Maximum theoretical force (F0) still fell
  significantly post-session (P=0.001) regardless of configuration — short rest defends velocity
  better than it defends the force ceiling.

## 4. Grip / forearm occlusion mechanism (why a pull-up's own "rest" barely helps)

**Coordinator's addition, addressed directly.** The pull-up hang is a sustained, high-relative-
force grip task — closer to an isometric handgrip held well above the muscle's own blood-flow
occlusion threshold than to a barbell exercise where the hand's grip force is a small fraction of
its maximum.

- **Byström & Kilbom (1990).** Physiological response in the forearm during and after isometric
  intermittent handgrip. *Eur J Appl Physiol Occup Physiol* 60(6):457-466.
  doi:10.1007/BF00705037. PMID 2390985. Closed access. **NOT pull-up-specific — transferred, but
  this is the primary occlusion-mechanism paper the coordinator asked for.** Handgrip dynamometer,
  four contraction-relaxation patterns (10+10, 10+5, 10+2 s, and continuous) at 10/25/40% MVC,
  with venous-occlusion plethysmography of forearm blood flow (BF) and EMG frequency analysis.
  **Forearm BF is insufficient even at 10% MVC isometric contraction** — occlusion-driven fatigue
  is not a high-intensity-only phenomenon. **Maximal BF during the RELAXATION phase itself is
  already reached at 25% MVC (25-30 ml·min⁻¹·100ml⁻¹)** — above roughly a quarter of maximum grip
  force, giving the muscle *more* relaxation time between contractions stops helping, because the
  vasculature is already delivering all the blood flow it is going to during the gap. Only
  10% MVC intermittent, and 25% MVC with the two longest relax windows (10+5 s, 10+10 s), were
  "acceptable" by the paper's own local-fatigue criteria. **Relevance:** a pull-up's grip is
  supporting full bodyweight through the hand — almost certainly well above 25% MVC for most
  people, likely much higher — so by this paper's own finding, the brief release between reps
  cannot meaningfully increase forearm reperfusion; the grip-fatigue clock should be modelled as
  barely resettable between reps, unlike, e.g., a racked barbell.
- **Byström & Kilbom (1991).** Electrical stimulation of human forearm extensor muscles as an
  indicator of handgrip fatigue and recovery. *Eur J Appl Physiol Occup Physiol* 62(5):363-368.
  doi:10.1007/BF00634974. PMID 1874244. Closed access. **NOT pull-up-specific — transferred.**
  Companion study: continuous 25% MVC handgrip to exhaustion vs. intermittent 25% MVC (10+2 s) to
  exhaustion vs. the same intermittent protocol to half-exhaustion-time, followed by electrically-
  evoked force testing up to 24 h later. **Low-frequency fatigue persisted for at least 24 h after
  the CONTINUOUS protocol, but only about 1 h after the INTERMITTENT (10+2 s) protocols** — even a
  brief (2 s) relaxation between grip efforts, at the same total time-under-tension and the same
  relative intensity, dramatically shortens how long fatigue persists afterward compared with one
  unbroken contraction. **Relevance:** this supports modelling a pull-up's brief inter-rep
  releases (whatever fraction of a second the grip is least loaded, e.g. at the top or bottom of
  the rep) as PARTIALLY, not fully, protective — consistent with "each rep hotter" rather than
  either full reset or zero recovery.
- **Nicolay & Walker (2005).** Grip strength and endurance: Influences of anthropometric
  variation, hand dominance, and gender. *Int J Ind Ergon* 35(7):605-618.
  doi:10.1016/j.ergon.2005.01.007. Not PubMed-indexed; confirmed **closed access** via Unpaywall
  and Semantic Scholar (abstract elided by publisher); the ScienceDirect abstract page returned a
  Cloudflare bot-wall to a direct fetch this session (same pattern already logged for other
  publishers in this repo's `DOWNLOADS.md`). **No primary abstract text obtained** —
  `abstracts/nicolaywalker2005-doi-ergon2005.txt` holds a citation plus an explicitly-flagged
  **secondary WebSearch-derived summary**, not a quote. 51 subjects; three protocols including a
  **30-second static maximal handgrip hold** — the closest published protocol duration to
  Dennis's ~45 s set. Qualitatively: relative grip endurance (percent force decline) was **not**
  associated with hand/forearm anthropometry, and the **dominant hand was stronger but fatigued
  MORE rapidly** than the non-dominant hand — consistent with a stronger muscle self-occluding
  more severely at a similar or higher %MVC (Byström & Kilbom's mechanism, applied to a bigger
  muscle). **No literal % force-decline number could be recovered and none should be reported
  from this citation.**
- Two dead-hang EMG papers already archived from the phase-resolved-EMG sweep are relevant here
  and are not re-fetched: **Ferrer-Uris et al. (2023)** (rock-climbing maximal isometric finger
  dead-hangs, PMID 37304875, PMC10249616, CC BY) and **Dykes et al. (2019)** (static crimp hang,
  PMID 30721754, closed access) — both confirm forearm flexors stay substantially active through
  a sustained hang (see `07-phase-resolved-emg.md` §1 Phase 5), consistent with the grip never
  going fully "cold" between reps even where the rest of the body's prime movers do relax.

## 5. Post-exercise muscle temperature decay (why 5 s should look almost unchanged)

- **Kenny, Reardon, Zaleski, Reardon, Haman & Ducharme (2003).** Muscle temperature transients
  before, during, and after exercise measured using an intramuscular multisensor probe.
  *J Appl Physiol* 94(6):2350-2357. doi:10.1152/japplphysiol.01107.2002. PMID 12598487. Closed
  access; confirmed not open access via Unpaywall. **NOT pull-up-specific — transferred, but this
  is the exact "Kenny et al. 2003 muscle-temperature-transients" primary source named in the
  brief.** 7 subjects; intramuscular multisensor thermal probe in vastus medialis at three depths
  (10/25/40 mm from the probe tip), 15 min of bilateral knee extension at 60% VO₂peak, 60 min of
  seated recovery. **Muscle temperature rose 2.00-3.20°C during exercise** (depth-dependent, the
  deepest sensor rising most) while **esophageal (core) temperature rose only 0.55°C** — local
  muscle heating during a working bout is roughly 4-6× the whole-body core-temperature rise, so
  the heat map should be driven by a local/muscle signal, not a core-temperature proxy. **Critical
  number for the model: muscle temperature "decreased GRADUALLY over the course of recovery,"
  remaining significantly elevated by 0.92-1.77°C a full 60 minutes later (P<0.05).** Core
  (esophageal) temperature, by contrast, showed a rapid initial decrease before settling to a
  smaller sustained +0.3°C elevation — a **different, faster** kinetic than the muscle's own slow
  decay, and a specific caution against using "how fast you stop feeling hot" (a core-temperature,
  autonomic sensation) as an intuition for how fast the *muscle itself* cools. **No single-number
  °C/min decay rate is stated in the abstract** (the full text was not obtainable — closed
  access) — the citable, defensible claim from this abstract alone is qualitative-but-quantified:
  "gradual," with roughly half of the peak elevation (of a 2-3°C rise) still present a full hour
  later. Given that the fastest part of any exponential-like decay happens earliest, even the
  paper's own most generous reading implies markedly less than 2-3°C of decay in the first 5-10
  seconds — a change too small to be visually distinguishable on a heat map, which is exactly the
  claim the brief needs justified. **This is an inference from the shape of Kenny 2003's numbers,
  not a number Kenny 2003 states directly for a 5 s window — flag as such on screen or in any
  report copy, do not present "no visible cooling in 5 s" as a literal quoted result.**
- **Flouris, Dinas, Tsitoglou, Patramani, Koutedakis & Kenny (2015).** Non-invasive measurement of
  tibialis anterior muscle temperature during rest, cycling exercise, and post-exercise recovery.
  *Physiol Meas* 36(7):N103-N113. doi:10.1088/0967-3334/36/7/N103. PMID 26012697. Closed access.
  **NOT pull-up-specific — transferred, secondary/methods support for Kenny 2003.** 26 healthy
  males; a non-invasive skin-surface-based method (INDISK) validated against direct intramuscular
  temperature during 20 min rest / 20 min cycling at 60% max HR / 20 min recovery. The best
  prediction model for current muscle temperature used the temperature reading **from 4 minutes
  earlier** as its strongest single input (R²=0.646) — i.e., muscle temperature during recovery
  changes slowly enough that a reading taken 4 minutes prior remains a strong predictor of the
  current one. This corroborates Kenny 2003's "gradual" decay independently, in a different
  muscle (tibialis anterior vs. vastus medialis) and a different exercise mode (cycling vs. knee
  extension).
- **Racinais & Oksa (2010).** Temperature and neuromuscular function. *Scand J Med Sci Sports*
  20 Suppl 3:1-18. doi:10.1111/j.1600-0838.2010.01204.x. PMID 21029186. Closed access. **NOT
  pull-up-specific — transferred; background/context only.** Narrative review: **short-duration
  exercise performance improves 2-5% per 1°C rise in muscle temperature** (a
  performance-vs-temperature relationship, not a decay rate — do not repeat this % as a decay
  number). Confirms the broader physiological framing (working muscle heats up, and that heat
  measurably matters for performance) without adding a numeric decay rate of its own.

## 6. What the model should reproduce (numbers to carry into the heat-map/fatigue module)

**(a) Velocity loss per rep and at failure, for ~8 pull-ups.** No published slope/intercept
exists for the pull-up's own velocity-loss-vs-rep curve (Sánchez-Moreno 2017's R²=.88 relationship
is reported only as a goodness-of-fit statistic, not literal coefficients — closed access). Model
guidance: (i) the curve should be **monotonic and roughly accelerating**, not linear — supported
by Sánchez-Medina 2011's non-linear ammonia-rise-past-the-midpoint finding and by every
transferred EMG-to-failure study's curvilinear-with-late-plateau shape (§2); (ii) Sánchez-Moreno
2020's VL25/VL50 pull-up landmarks say that by the time a near-maximal ~8-rep set reaches its last
1-2 reps, cumulative velocity loss is almost certainly **past 25%, likely well into the 40-60%+
range** typical of "set to failure" data in the transferred literature (Izquierdo 2009/2011's
46-62% peak-power-loss figures, García-Ramos 2020's -39.3% for a 30-rep continuous bench set); a
literal ~8-rep bodyweight set should land somewhere in this territory by the final rep, not at a
mild 10-15% loss — treat this as an ESTIMATE-grade band, not a cited number, since no pull-up
study gives the literal final-rep figure for an 8-rep set specifically.

**(b) EMG amplitude and frequency drift, first→last rep, as the observable of compounding
fatigue.** Use Sundstrup 2012's explicit **86%→124% MVC** trapezius rise (curvilinear, plateauing
in the final 3-5 reps before failure) as the best-attested SHAPE to reproduce — not a pull-up
muscle-specific magnitude, but the closest measured first-to-last-rep %MVIC pair in the whole
sweep. Combine with Tsoukos 2021's finding that amplitude keeps climbing past the set's midpoint
(not just an early-vs-late-rep step) and that frequency compression is proportionally larger in
longer/lighter sets — an 8-rep bodyweight set is a moderate-duration set, so expect meaningful
(not negligible) frequency-domain fatigue by the last rep, alongside the amplitude rise.

**(c) How much recovers in 5-30 s of rest.** García-Ramos 2020 gives the cleanest number: 5 s of
FULLY UNLOADED rest roughly **halves** velocity loss (-39.3%→-20.2%) relative to none; 10-15 s
cuts it to roughly a **quarter** of the no-rest value. **This is an upper bound, not a pull-up
number** — a pull-up's between-rep gap is a LOADED rest (the hands/lats stay under bodyweight
load in the low-hang/top-hold), structurally closer to Byström & Kilbom's continuous or
minimally-relaxed handgrip conditions than to a racked barbell. Byström & Kilbom (1990) show
forearm blood flow during any relaxation phase is already at its ceiling by ~25% MVC — well below
a bodyweight-supporting grip — so the grip specifically should be modelled with **little to no
inter-rep recovery**, while the prime movers (lats/biceps), which do get a brief true unloading
at the bottom of each rep, can be modelled with the partial-recovery shape the cluster-set
literature supports, scaled down from the fully-unloaded-rest numbers above to account for the
much shorter, less-relaxed nature of a pull-up's own inter-rep gap.

**(d) Temperature decay rate after exercise ends.** Kenny 2003: muscle temperature decay is
"gradual" over tens of minutes, with roughly half of a 2-3°C exercise-induced rise still present a
full hour later; core temperature decays on a visibly different (faster, biphasic) timescale and
should not be used as the model's proxy. Justify the "no visible cooling in 5 s" claim as an
inference from this shape (a slow, many-minutes decay curve implies a negligible change in its
first few seconds), not as a number the source states directly — say so explicitly in any report
or on-screen caption that cites this reasoning.

## 7. Sources fetched this session, with open-access status

| citation | PMID/DOI | OA status | files |
|---|---|---|---|
| Sánchez-Moreno et al. 2017 | PMID 28338365 | Closed (reused, not re-fetched) | `abstracts/sanchezmoreno2017-pmid28338365.txt` (already existed) |
| Sánchez-Moreno et al. 2020 | PMID 32213783 | Closed (reused, not re-fetched) | `abstracts/sanchezmoreno2020-pmid32213783.txt` (already existed) |
| Sánchez-Medina & González-Badillo 2011 | PMID 21311352 | Closed | `abstracts/sanchezmedina2011-pmid21311352.txt` (re-fetched fresh copy; older copy also exists at `../pullup-emg/pmid21311352-abstract.txt`) |
| Izquierdo et al. 2009 | PMID 19382055 | Closed | `abstracts/izquierdo2009-pmid19382055.txt` |
| Izquierdo/González-Izal et al. 2011 | PMID 20581711 | Closed | `abstracts/gonzalezizal2011-pmid20581711.txt` |
| González-Izal et al. 2010 | PMID 20579906 | Closed | `abstracts/gonzalezizal2010-pmid20579906.txt` |
| Sundstrup et al. 2012 | PMID 21986694 | Closed | `abstracts/sundstrup2012-pmid21986694.txt` |
| Tsoukos et al. 2021 | PMID 34329514 | Closed | `abstracts/tsoukos2021-pmid34329514.txt` |
| Zhang et al. 2022 | PMID 36618336, PMCID PMC9797014 | **Open access** | `abstracts/zhang2022-pmid36618336.txt`, `papers/zhang2022-ultraendurance-pullup.pdf`, `papers/zhang2022-ultraendurance-pullup-extract.txt` |
| Haff et al. 2003 | PMID 12580663 | Closed | `abstracts/haff2003-pmid12580663.txt` |
| Latella et al. 2019 | PMID 31506904, PMCID PMC6851217 | **Open access** | `abstracts/latella2019-pmid31506904.txt`, `papers/latella2019-cluster-sets-review.xml` |
| Jukic, Ramos, Helms, McGuigan & Tufano 2020 | PMID 32901442 | Closed | `abstracts/jukictufano2020-pmid32901442.txt` |
| García-Ramos et al. 2020 | PMID 29076963 | Closed | `abstracts/garciaramos2020-pmid29076963.txt` |
| Torrejón et al. 2019 | PMID 30955089 | Closed | `abstracts/torrejon2019-pmid30955089.txt` |
| Kenny et al. 2003 | PMID 12598487 | Closed (confirmed via Unpaywall) | `abstracts/kenny2003-pmid12598487.txt` |
| Flouris et al. 2015 | PMID 26012697 | Closed | `abstracts/flouris2015-pmid26012697.txt` |
| Racinais & Oksa 2010 | PMID 21029186 | Closed (confirmed via Unpaywall) | `abstracts/racinaisoksa2010-pmid21029186.txt` |
| Byström & Kilbom 1990 | PMID 2390985 | Closed | `abstracts/bystromkilbom1990-pmid2390985.txt` |
| Byström & Kilbom 1991 | PMID 1874244 | Closed | `abstracts/bystromkilbom1991-pmid1874244.txt` |
| Nicolay & Walker 2005 | DOI 10.1016/j.ergon.2005.01.007, no PMID | Closed (confirmed via Unpaywall + Semantic Scholar; ScienceDirect page bot-walled) | `abstracts/nicolaywalker2005-doi-ergon2005.txt` (citation + flagged secondary summary only, no primary abstract text) |

**Not found this session** (searched via PubMed E-utilities, Europe PMC, Semantic Scholar Graph
API, CrossRef, Unpaywall, and WebSearch): a pull-up-specific rep-by-rep EMG or velocity dataset
for a set in the 6-12 rep range to failure (the closest is Zhang 2022's 330-rep case study, and
the whole-set-summary pull-up VBT papers in §1); the original Tufano 2016 ("Cluster sets:
permitting greater mechanical stress and greater training volume") or Tufano 2017 single/co-first-
authored reviews named in the brief specifically (the Tufano-authored review actually retrieved
and used, Jukic et al. 2020, is a later, larger systematic review with Tufano as last author, not
the exact 2016/2017 papers — flagged as a substitution, not presented as the same paper); Beckham
et al. 2018's reliability-of-pull-up-velocity paper (already archived from the 2026-09-08 sweep,
not re-fetched, no new rep-by-rep numbers in its abstract beyond what `02-biomechanics-and-
velocity.md` already reports); a literal °C-per-minute or °C-per-second decay CONSTANT for
post-exercise muscle temperature (Kenny 2003's abstract reports the shape and two endpoint values
{peak rise, +60 min remaining elevation} but not a fitted decay-rate constant — the full text
was not obtainable, closed access, no PMC/OA mirror found); Muñoz-López et al. 2017's raw
load-velocity data broken out by rep (already archived, whole-relationship R² only, no new
numbers this session); a Nicolay & Walker 2005 primary abstract or full text (closed access,
bot-walled ScienceDirect page — see §4 and `abstracts/nicolaywalker2005-doi-ergon2005.txt` for the
full account of what was and was not obtained).
