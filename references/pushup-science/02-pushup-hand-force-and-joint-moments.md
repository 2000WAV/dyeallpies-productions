# References — push-up ground reaction force, joint moments and rep kinetics

Literature sweep collected 2026-09-09 for the push-up-video format's inverse-dynamics muscle model
(companion to `references/pullup-science/` for the pull-up format). Abstracts fetched via PubMed
E-utilities, saved verbatim in `abstracts/`; full text via Europe PMC (fullTextXML or `?pdf=render`)
for the open-access papers, and direct institutional-mirror curl for one non-PubMed-indexed paper —
see `abstracts/` and `papers/` in this directory, logged in `DOWNLOADS.md`. Extracted numbers are
also in `data/pushup-kinetics.csv`.

24 primary/secondary sources below (9 closed-access/abstract-only, 15 with full text or a
verified secondary numeric citation). Anything not traceable to one of these is marked **NOT
FOUND**, never invented from memory.

## 1. Fraction of body weight on the hands — standard push-up, top vs bottom

| position | value | population / method | source |
|---|---|---|---|
| standard, initial/static load | 66.4% BW | 8 healthy men, force plate + EMG | Gouvali & Boudolos 2005 |
| knees (modified), initial/static load | 52.9% BW | 8 healthy men | Gouvali & Boudolos 2005 |
| standard, top (up, elbows locked) | 71.95 ± 3.09% BM (men); 66.26 ± 2.63% BM (women) | 16M+9W, isometric hold on force plate | Eckel et al. 2017 |
| standard, bottom (down, upper arms parallel) | 76.70 ± 2.56% BM (men); 73.14 ± 3.14% BM (women) | 16M+9W, isometric hold | Eckel et al. 2017 |
| standard, average of up+down | 74.33 ± 2.57% BM (men); 69.70 ± 2.63% BM (women) | 16M+9W | Eckel et al. 2017 |
| standard, peak GRF (dynamic) | ~64% BW | 23 (14M/9W), force platform | Ebben et al. 2011 (number cited secondhand via Adams 2022 — **not stated in Ebben's own abstract**) |
| knee (modified), peak GRF (dynamic) | ~49% BW | 23 (14M/9W) | Ebben et al. 2011 (secondhand via Adams 2022); ~18% lower than standard |
| standard, %BM increase up→down | +5.88 percentage points | 28 highly strength-trained men, static holds | Suprak et al. 2011 (secondhand via Adams 2022) |
| modified (knee), %BM increase up→down | +8.24 percentage points | 28 highly strength-trained men | Suprak et al. 2011 (secondhand via Adams 2022) |
| standard, maximal dynamic load — men | 97.7 ± 8.1% BW | 37 M+W, force platform, max effort | Mier et al. 2014 — **primary text not obtained (403 blocked); flagged as an outlier vs. every other study in this table, likely a different measurement definition (max dynamic vs. static/initial)** |
| standard, maximal dynamic load — women | 80.0 ± 3.9% BW | as above | Mier et al. 2014 (same caveat) |
| modified (knee), maximal dynamic load — men | 79.7 ± 7.4% BW | as above | Mier et al. 2014 |
| modified (knee), maximal dynamic load — women | 68.2 ± 3.0% BW | as above | Mier et al. 2014 |

**Honest read.** Every primary/secondary source that measured a simple static or dynamic-peak %BW
agrees on the same order of magnitude and the same direction (bottom loads more than top, standard
loads more than knee) — 66–77% BW at the top and 73–87%-ish at the bottom is the consistent band
across Gouvali 2005, Eckel 2017, and the secondhand Ebben 2011 / Suprak 2011 numbers. **Mier et
al. 2014's ~98%/80% figures are the one outlier**, and its primary text could not be retrieved this
session (digitalcommons.wku.edu returned HTTP 403 to both `curl` and `WebFetch`) to check whether it
used a different definition (e.g. true dynamic peak including an acceleration spike, vs. the
quasi-static holds most other studies used) — see `papers/mier2014-CITATION-ONLY.txt`. **Use the
Gouvali/Eckel range (66–77% BW) as the primary number for a standard push-up**, and treat Mier's
figures as an upper-bound caution, not a contradiction to resolve by averaging.

## 2. Variants — knee, incline (hands elevated), decline (feet elevated)

| variant | GRF vs standard | source |
|---|---|---|
| knee (modified) | 49% BW (Ebben, secondhand) / 52.9% BW (Gouvali, primary) — roughly **12–18% lower** than standard, per Adams et al. 2022's own synthesis of both papers | Ebben 2011 + Gouvali 2005 |
| hands elevated 30.48 cm / 60.96 cm (incline) | **lower** GRF than all other variants tested | Ebben et al. 2011 (ranking only, no absolute number in the abstract) |
| feet elevated 30.48 cm / 60.96 cm (decline) | **higher** GRF than all other variants tested | Ebben et al. 2011 (ranking only) |
| no gender or height effect on GRF | confirmed, except the 60.96 cm hands-elevated condition (r = 0.63 with height) | Ebben et al. 2011 |

Ebben et al. 2011's own abstract (23 recreationally fit subjects, 14M/9W, force platform, 6 push-up
variants) reports only the *ranking* among variants, not absolute %BW values — the widely-quoted
"64%/49%" pair comes from Adams et al. 2022's secondary citation of Ebben's results table, not from
Ebben's own abstract text (closed access, JSCR/LWW, no PMC copy located this session).

## 3. Force-time curves, peak dynamic force (including the acceleration term)

A genuinely static hold cannot exceed ~100% of body weight distributed across all contact points —
any measurement *above* 1× total bodyweight is direct evidence of the acceleration/inertial term
that a purely kinematic (position-only) model would miss.

| metric | value | population / method | source |
|---|---|---|---|
| sum of vGRF (both hands + both feet) at fast (60 reps/min) cadence — men | **1.58 ± 0.14× BM** | 44 (M+F), standard push-up, vGRF under hands AND feet | Rozenek et al. 2022 |
| sum of vGRF at 60 reps/min — women | **1.33 ± 0.08× BM** | as above | Rozenek et al. 2022 |
| self-selected push-up cadence — men | 49.9 ± 11.4 reps/min | as above | Rozenek et al. 2022 |
| self-selected push-up cadence — women | 42.8 ± 8.4 reps/min | as above | Rozenek et al. 2022 |
| ballistic push-up peak force (no external load) | 960 ± 188 N | 60 men (80.8 ± 13.5 kg), force plate under hands | Wang et al. 2017b |
| ballistic push-up peak force (+10% BM vest) | 1017 ± 202 N | as above | Wang et al. 2017b |
| ballistic push-up peak force (+20% BM vest) | 1062 ± 202 N | as above (highest force, but **lowest** power of the 3 loads) | Wang et al. 2017b |
| ballistic push-up peak power (no external load, highest of the 3) | 950 ± 257 W | as above | Wang et al. 2017b |
| whole-body velocity, plyometric push-up (correct 2-force-plate method) | 0.90 ± 0.23 m/s | 34 physically active adults | Sha & Dai 2021 |
| whole-body velocity, plyometric push-up (1-force-plate method — **overestimates**) | 1.39 ± 0.37 m/s (Cohen's d = 1.59 vs. the 2-plate reference) | as above | Sha & Dai 2021 |
| whole-body power, plyometric push-up (2-plate reference) | 1.03 ± 0.29 W/BW | as above | Sha & Dai 2021 |
| landing peak vGRF, box-drop 3.8/7.6/11.4 cm | 0.69 / 0.71 / 0.71 × BW | 21 men, dominant-hand force plate | Moore et al. 2012 |
| landing peak vGRF, clap push-up | **0.78 × BW** (significantly highest of the 4 variants) | 21 men | Moore et al. 2012 |
| free-fall-model overestimation of plyometric flight time vs. the mechanically correct pendulum model | up to **18.82%** | analytical/simulation, no subjects | Dhahbi 2026 (rigid-body pendulum model) |
| free-fall-model overestimation of plyometric max height | up to **28.43%** | as above | Dhahbi 2026 |

**Methodological caution flagged directly by two of the sources above**: Sha & Dai 2021 show that the
common single-force-plate shortcut (measuring only the hands, assuming feet-force stays constant)
substantially *overestimates* velocity and power, because foot-force actually *decreases* through
most of the push-off phase. Dhahbi 2026 shows the companion error on the kinematic side: treating the
body as a free-falling point mass (rather than a rigid pendulum pivoting at the ankle) systematically
overestimates flight time and height, worst at short limb lengths and high launch velocity. **Any
push-up model that infers force/power/height from flight time or from a single force plate should
apply a correction in the direction these two papers describe, not take the naive reading at face
value.**

## 4. Elbow joint moments and forces (inverse dynamics)

The Mayo Clinic group (An, Chao, Morrey, Donkers — three related papers, 1990/1992/1993, all on the
same or an overlapping 9-healthy-men dataset with electromagnetic motion sensors + a piezoelectric
force plate) is the primary source for push-up elbow-joint loading, analogous to Youdas 2010's role
for the pull-up EMG dataset.

| quantity | value | condition | source |
|---|---|---|---|
| peak elbow axial (forearm-long-axis) force | **45% BW** | "normal" hand position; significantly lower for 'apart'/'superior' hand positions | Donkers, An, Chao & Morrey 1993 |
| peak elbow-flexion torque | **2305.9 N·cm** = 56% of MVIC extensor torque | normal hand position; 29%/71% of MVIC for 'apart'/'together' | Donkers et al. 1993 |
| forearm pronation torque (max) | 315.4 N·cm = 35% of MVIC supinator torque | normal hand position | Donkers et al. 1993 |
| peak elbow valgus torque | 1241 N·cm | opposed by the medial (ulnar) collateral ligament | Donkers et al. 1993 |
| peak elbow valgus torque, one-handed push-up (simulated fall) | **+42%** over the two-handed value | simulated-fall loading | Donkers et al. 1993 |
| (companion/duplicate confirmation of the above) | same 45% BW / 2305.9 N·cm / 56% MVIC numbers | same dataset, symposium-proceedings paper | An, Chao, Morrey & Donkers 1992 |
| wrist/elbow/shoulder load factors (qualitative only, no numbers in the abstract) | palm-shoulder relative position, plane of arm movement, foot position, and push-up **speed** (inertial load) all affect intersegmental joint loads | 1990 pilot dataset | An, Korinek, Kilpela & Edis 1990 |

**No numeric shoulder-joint moment** for the push-up was located this session (An 1990's abstract is
qualitative-only on the shoulder; no other push-up-specific shoulder inverse-dynamics paper turned
up in PubMed or Europe PMC searches). This mirrors the pull-up archive's own gap for shoulder-
extension MVC (`08-moment-arms-and-strength.md` in `references/pullup-science/`) — mark any
push-up shoulder-moment number used in the model as an estimate pending a future session's search
(candidates not yet tried: a musculoskeletal-model / OpenSim push-up simulation specifically
computing glenohumeral joint reaction force, which was searched for this session — "push-up OpenSim
simulation," "push-up inverse dynamics shoulder elbow" — and returned 0 hits).

## 5. Elbow angle range (top lock-out, bottom)

No study in this sweep reports a numeric total elbow range-of-motion (degrees, top-to-bottom) for
the *standard* push-up analogous to Youdas 2010's 93.4° pull-up figure in the pull-up archive.
Operational anchors used by the studies here instead of a measured ROM number: Eckel et al. 2017
define the *top* as "triceps perpendicular to the floor" (full extension) and the *bottom* as
"upper arms parallel to the floor" (device-cued with a safety-squat-bar placed on the triceps) — the
same wording used by the official USMC push-up standard (see `03-pushup-norms-and-standards.md`).
Moore et al. 2012's plyometric-push-up landing elbow-flexion-at-ground-contact values (−19.4° to
−29.9°, more flexed for the clap variant and the shallowest box-drop) are a *landing-instant* angle
for a different (plyometric) task, not a top-to-bottom ROM for the standard push-up — **do not
substitute one for the other**. **Elbow ROM in degrees for a standard push-up: NOT FOUND** as a
primary numeric result this session (searched "push-up elbow range of motion degrees goniometry,"
"push-up elbow flexion angle bottom top kinematics," 0 useful hits beyond the qualitative anchors
above).

## 6. Rep velocity and duration

| metric | value | population / method | source |
|---|---|---|---|
| mean concentric velocity, push-up (no vest) | 0.86 ± 0.19 m/s | 20 resistance-trained men, linear encoder | van den Tillaar & Ball 2020 |
| mean concentric velocity, push-up (+30 kg vest) | 0.43 ± 0.15 m/s | as above | van den Tillaar & Ball 2020 |
| %BM supported (+weight vest), 0/10/20/30 kg | 62.6 / 63.7 / 64.4 / 65.1 %BM | as above | van den Tillaar & Ball 2020 |
| velocity at theoretical 1RM (V0, borrowed from barbell-training convention) | 0.18 m/s | applied (not independently derived for push-up) | van den Tillaar & Ball 2020, citing González-Badillo |
| self-selected cadence — men / women | 49.9 ± 11.4 / 42.8 ± 8.4 reps/min | 44 (M+F) | Rozenek et al. 2022 |
| fixed test cadence used in a reps-to-failure protocol | 60 beats/min = 30 reps/min | 25 (16M/9W), metronome-paced | Eckel et al. 2017 |
| predicted push-up 1RM (load-velocity extrapolation, weight-vest equivalent) | 93.1 ± 14.0 kg (vs. bench press 93.5 ± 15.7 kg, r = 0.93 between exercises) | 20 men | van den Tillaar & Ball 2020 |
| **actual** push-up 1RM (directly tested, weight-vest equivalent) | **112.4 ± 18.9 kg — significantly higher than the same subjects' actual bench-press 1RM (106.4 ± 20.4 kg)** | 11 men | van den Tillaar, Falch & Larsen 2025 |

The 2025 finding (actual push-up 1RM > actual bench-press 1RM, despite the two exercises' *predicted*
1RM from load-velocity not differing) is a caution against relying purely on a load-velocity
extrapolation for push-up strength ceiling — the extrapolation method itself may under-capture the
true capacity in this closed-kinetic-chain exercise.

## 7. Plyometric peaks

See section 3 above (Rozenek's cadence data, Wang's ballistic-push-up loaded/unloaded force-power
trade-off, Moore's landing-force table, and the Dhahbi 2026 pendulum-model correction) — the
plyometric numbers are integrated there rather than repeated in a separate section, since they are
directly comparable to (and in several cases methodologically corrected versions of) the standard-
push-up force numbers above. Two further points specific to plyometric variants:

- **Loading a ballistic push-up trades force for power**: peak force rises monotonically with added
  vest load (960 → 1017 → 1062 N across 0/10/20% BM), but peak power is *highest with no external
  load at all* (950 W) and falls as load increases (Wang et al. 2017b) — the classic force-velocity
  power-optimum pattern seen in ballistic barbell training, now confirmed for the push-up.
- **The clap push-up is the most mechanically demanding of the common plyometric variants tested**:
  highest landing force (0.78 BW) combined with the greatest eccentric elbow-flexion displacement
  (Moore et al. 2012) — a specific, sourced ranking for progressing plyometric push-up intensity.

## 8. Gaps and sources named in the task brief but not located this session

- **Suprak, Dawes & Stephenson 2013** (a hand-position/GRF paper distinct from the 2013 scapular-
  kinematics paper that *was* found, `suprak2013-pmid23952043.txt`) — not located under several
  author/title search combinations.
- **Contreras 2012** — no PubMed or Europe PMC record found under any search tried this session
  (Bret Contreras is a well-known strength-and-conditioning author/blogger; if this is a magazine or
  blog piece rather than a peer-reviewed paper, it would not be expected to appear in these
  databases — not independently confirmed either way).
- **Chou et al. 2011 (J Athl Train?, shoulder joint loads in push-up)** — only a *different* Chou
  paper was found (Chou 2001, *Clin Biomech*, "Effect of elbow flexion on upper extremity impact
  forces during a **fall**" — a different topic and a different first-author initial pattern); no
  push-up-specific shoulder-joint-load paper by a first author "Chou" was located.
- **Lou et al. 2001 (Am J Phys Med Rehabil, elbow load)** — 0 PubMed hits under several term
  combinations.
- **Hinshaw 2018 (JSCR, push-up/bench-press 1RM prediction)** — 0 PubMed hits; **Clemons 2019** (JSCR,
  "Construct Validity of Two Different Methods of Scoring and Performing Push-ups") used as the
  closest available substitute — see `abstracts/clemons2019-pmid30363033.txt`.
- **Bartolomei 2022 (push-up load-velocity)** — 0 hits for a 2022 paper; **Bartolomei et al. 2018**
  ("Comparison Between Bench Press Throw and Ballistic Push-up Tests," PMID 29528954) is the real
  Bartolomei push-up paper found this session (confirmed as such by its citation inside the Dhahbi
  2026 pendulum-model paper's own reference list).
- **Dhahbi 2018 (load-velocity)** — the 2018 Dhahbi paper found this session is the *systematic
  review* (`dhahbi2018review-pmid30284496.txt`, "Kinetic analysis of push-up exercises," 26 studies /
  46 variants pooled), not a primary load-velocity study.
- **Wang et al. 2013** (named uncertainly in the task brief) — the real paper is **Wang et al. 2017**
  (two companion papers, PMID 28166187 and 28118312), confirmed via the Dhahbi 2026 paper's citation.
