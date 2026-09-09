# References — pull-up biomechanics, kinetics and velocity-based training

Literature sweep collected 2026-09-08 for the pullup-video format's RIR (reps-in-reserve) and
effort-multiplier replacement. Companion files: `../pullup-emg/README.md` (surface EMG %MVIC,
Sánchez-Medina velocity-loss/fatigue) and `../pullup-thermal/README.md` (scapula kinematics,
strict-vs-kipping EMG, technique standards, asymmetry). Abstracts fetched via PubMed E-utilities;
full text via Europe PMC for the open-access papers — see `abstracts/` and `papers/` in this
directory, logged in `DOWNLOADS.md`. Extracted numbers are also in `data/*.csv`.

17 primary/secondary sources below (9 abstract-only/closed access, 8 with full text saved).
Anything not traceable to one of these is marked **ESTIMATE**.

## 1. Velocity-effort relationships (the RIR/effort core)

| relationship | value | population / method | source |
|---|---|---|---|
| MPV vs %1RM, pull-up | r = -.96 | 52 trained men, linear velocity transducer | Sánchez-Moreno 2017 |
| velocity at 1RM (V1RM), pull-up | 0.20 ± 0.05 m/s | 52 trained men | Sánchez-Moreno 2017 |
| % velocity-loss vs % of max reps completed, within a set | R² = .88, stable after 12 wk of training (+15% max reps) | 52 trained men | Sánchez-Moreno 2017 |
| VL25 vs VL50 8-wk pull-up training | VL25 > VL50 for strength/velocity gains; equal max-rep endurance gains; "further reps beyond 25% loss did not elicit additional gains" | 29 strength-trained men, RCT | Sánchez-Moreno 2020 |
| pull-up load-/force-/power-velocity fit (individual) | R² = .975 / .954 / .966 | 82 resistance-trained men, linear transducer, 70–100%1RM added-load | Muñoz-López 2017 |
| load at peak power | 71.0 ± 6.6 %1RM | 82 resistance-trained men | Muñoz-López 2017 |
| first-rep (isolated) MCV vs max reps to failure | R = 0.841, prediction error ≈ 2.07 reps | 49 general trained subjects, linear position transducer | Beckham 2018 |
| velocity at fixed RIR (2/4/6/8) — generalises across 65/75/85 %1RM and across 4 multijoint exercises | between-session CV 4.4–8.0%, no effect of training level | 30 men, varying training levels | Morán-Navarro 2019 |
| RTF(reps-to-failure)–velocity relationship class | "robust" goodness of fit; acceptable–high reliability for the velocity at each of 1–15 RTF; accuracy degrades under fatigue (short rest) except in lifters with >2 y training-to-failure experience | systematic review, 6 pooled studies, non-pull-up | Miras-Moreno/Weakley/García-Ramos 2025 |
| one universal %VL threshold does not reproduce the same rep count session-to-session | "agreement... was not acceptable"; sex, training history and emotional stability all shift where a set actually terminates at a nominal %VL | 46 resistance-trained (15 F/31 M), back squat | Jukic 2023a |
| chronic effect of VL threshold on adaptation | strength/endurance unaffected by VL threshold chosen; higher VL favours hypertrophy (b=0.006/unit VL); lower VL favours CMJ, sprint, submax-velocity outcomes | meta-analysis, 18 acute + 19 longitudinal studies | Jukic 2023b |
| MPV, bodyweight pull-up, large hold vs small edges | large hold 0.84±0.16, 20mm 0.75±0.16, 15mm 0.73±0.16, 10mm 0.52±0.15 m/s | 10 male climbers, linear position transducer | Sordo-Vacas 2024 |
| MPV reliability, pull-up | ICC 0.84–0.99 intra-session, 0.73–0.96 inter-session | 10 male climbers | Sordo-Vacas 2024 |
| Vmean/Vmax vs isometric strength, pure-concentric (dead-hang start) pull-up | strong positive correlation | 50 male collegiate athletes | Hayashi 2026 |
| Vmean/Vmax vs isometric strength, countermovement (bounced) pull-up | weaker correlation than pure-concentric — SSC contribution decouples velocity from underlying strength | 50 male collegiate athletes | Hayashi 2026 |

No pull-up-specific study in this sweep publishes the literal regression coefficients (slope,
intercept) behind the R²=.88 velocity-loss/%-reps-completed curve or the R=0.841 first-rep-velocity
regression — both are reported only as goodness-of-fit statistics in the abstracts available (both
papers are closed access; see `DOWNLOADS.md`). Treat any specific slope/intercept used in the pipeline
as a **fitted approximation to these shapes**, not a literal published constant, until full text or a
personal calibration set is available.

## 2. Kinetics (force, power, EMG-based effort)

| metric | value | population / method | source |
|---|---|---|---|
| pull-up 1RM normalised | 1.5 ± 0.34 × bodyweight | 82 resistance-trained men | Muñoz-López 2017 |
| hand-force (bar) asymmetry, regular practitioners | SD < 5% BW | 11 practitioners, force plate/bar instrumentation | Prinold & Bull 2016 (`../pullup-thermal/`) |
| inter-limb asymmetry "flag" convention | 10% (range 10–15%) | systematic review | Bishop 2018 (`../pullup-thermal/`) |
| rectus abdominis activation, kip vs strict | +28.7 ± 4.7 %MVIC (p<.001) | 11 athletes, surface EMG | Dinunzio 2019 |
| external oblique activation, kip vs strict | +21.8 ± 4.1 %MVIC (p<.001) | 11 athletes, surface EMG | Dinunzio 2019 |
| biceps brachii activation, kip vs strict | significantly lower in kip | 11 athletes, surface EMG | Dinunzio 2019 |
| hip/knee joint angle excursion, kip vs strict | significantly greater in kip (this is the *kinematic* kip signature, not just EMG) | 11 athletes, 3D motion capture | Dinunzio 2019 |
| total muscle work, plyometric-trained group vs control | +21.9 ± 16.6% (p=.015) | 30 experienced climbers, 5-wk training study | Vigouroux & Devise 2024 |
| muscle work / max reps correlated with climbing level; fatigue resistance flagged as the key determinant (more than peak force/velocity) | qualitative | 28 climbers | Devise 2023 |
| rotator-cuff force (modelled) | elevated in reverse (supinated/chin-up-like) grip vs front/wide | 11 male practitioners, musculoskeletal model driven by mocap | Urbanczyk 2020 |
| latissimus dorsi relative activity | higher in wide grip (P<.01) | 11 male practitioners | Urbanczyk 2020 |
| %MVIC by muscle (lat 117–130, biceps 78–96, infraspinatus 71–79, lower trap 45–56, pec major 44–57) | see `../pullup-emg/README.md` | 21M+4F, surface EMG | Youdas 2010 |
| concentric > eccentric activation (brachioradialis, biceps, pec major, P<.01) | see `../pullup-emg/README.md` | 19 men, surface EMG | Dickie 2017 |
| within-set velocity loss vs lactate / CMJ loss | r=.93–.97 / r=.91–.97 (general resistance training, not pull-up-specific) | see `../pullup-emg/README.md` | Sánchez-Medina & González-Badillo 2011 |

No force-plate or instrumented-bar study specifically reporting **peak force × bodyweight** or
**impulse** for the bodyweight pull-up (as opposed to modelled/EMG-inferred force) turned up in this
sweep — Muñoz-López 2017's "force" is the mean *propulsive* force at each %1RM of an *added-load*
pull-up, derived from the transducer's velocity/acceleration trace, not a direct bar/floor force-plate
reading. The pipeline's own `peak_force_bw = m_lift × (g + peak_acc) / (mass × g)` (in
`tools/scripts/analyze_pullups.py`) is a **kinematics-derived** force estimate (Newton's second law
applied to the pose-tracked centre of mass), not validated against any force-plate ground truth found
in this literature — flag as **ESTIMATE** in the report copy.

## 3. Kinematics (ROM, joint angles, durations, sticking point)

| metric | value | population / method | source |
|---|---|---|---|
| elbow ROM, pull-up (pronated) | 93.4 ± 14.6° | 21M+4F | Youdas 2010 (`../pullup-emg/`) |
| elbow ROM, chin-up (supinated) | 100.6 ± 14.5° | 21M+4F | Youdas 2010 |
| scapular protraction/retraction ROM, front grip | 22° (largest of the three grips studied) | 11 practitioners, 3D mocap | Prinold & Bull 2016 (`../pullup-thermal/`) |
| shoulder abduction / external rotation at end-range, wide grip (impingement-risk variant) | 90° / 45° | 11 practitioners | Prinold & Bull 2016 |
| hip/knee angle excursion | significantly greater with a kip | 11 athletes, 3D mocap | Dinunzio 2019 |
| sticking region location | commonly described as roughly mid-pull, "chin ~6–12 in below the bar," attributed to a poor force-length position of the prime movers at that joint angle | secondary/practitioner sources, **not a primary biomechanics study** | **ESTIMATE** (no primary pull-up sticking-point study found this session) |
| chin-travel distance vs. body height (anthropometric ratio) | not found as a primary study this session; the pipeline already uses arm length = 0.332 × stature (its own calibration constant) as the working proxy for vertical travel | — | **ESTIMATE / gap** — no dedicated primary source found |

Concentric/eccentric *durations* specific to a max-effort bodyweight pull-up set (as opposed to the
EMG-magnitude concentric>eccentric finding above) were not reported numerically in any abstract
retrieved this session; the pipeline's own per-rep `t_concentric`/`t_eccentric` timings are the working
data source, with no external validated normative range found to compare against — flag as a gap, not
as ESTIMATE (no claim is being made, just an absence of a comparison point).

## 4. Reliability of video/phone velocity measurement

No pull-up-specific validation of smartphone or markerless pose-based velocity measurement was found.
Closest available evidence, all on **barbell** exercises (bench press / squat / hip thrust), not
bodyweight pulling, and all tracking a **rigid bar marker**, not a full-body pose:

| system | validity vs. linear transducer | reliability | population | source |
|---|---|---|---|---|
| PowerLift iPhone app (mean velocity, bench press) | r = 0.94, SEE 0.028 m/s | ICC = 0.965 | 10 powerlifters | Balsalobre-Fernández 2018 |
| PowerLift 1RM estimate | r = 0.98 (mean diff 5.5±9.6 kg) | — | 10 powerlifters | Balsalobre-Fernández 2018 |
| wearables (wrist/barbell) + PowerLift app, 3 lifts | r = 0.94–0.98, SEE 0.03–0.07 m/s | ICC 0.910–0.990 | 10 elite powerlifters | Balsalobre-Fernández 2017 |
| pull-up MPV, linear position transducer (not video/phone) | — | ICC 0.84–0.99 intra-session, 0.73–0.96 inter-session | 10 male climbers | Sordo-Vacas 2024 |

**Explicit gap and caveat for the report:** these smartphone-app numbers are the best available proxy
for "how much to trust a camera-derived velocity," but they come from a fixed camera tracking a single
rigid, high-contrast bar marker under controlled lighting — a materially easier tracking problem than
full-body markerless pose estimation (MediaPipe/YOLOv8-pose) of a moving person, which is subject to
self-occlusion, landmark jitter at the wrist/shoulder, and camera-plane parallax that a bar-marker
tracker does not face. Independent re-validations of the same MyLift/PowerLift app line on other lifts
have been mixed (some report the app missing large fractions of reps — see WebSearch notes; not a
citable primary source, omitted from the table). **No published validity/reliability figure exists yet
for this pipeline's own pose-based velocity output; treat it as directionally reliable rep-to-rep within
one clip, not validated to transducer-level absolute accuracy.**

## 5. Full citations

- Sánchez-Moreno M, Rodríguez-Rosell D, Pareja-Blanco F, Mora-Custodio R, González-Badillo JJ (2017).
  Movement Velocity as Indicator of Relative Intensity and Level of Effort Attained During the Set in
  Pull-Up Exercise. *Int J Sports Physiol Perform* 12(10):1378-1384. doi:10.1123/ijspp.2016-0791.
  PMID 28338365. Closed access.
- Sánchez-Moreno M, Cornejo-Daza PJ, González-Badillo JJ, Pareja-Blanco F (2020). Effects of Velocity
  Loss During Body Mass Prone-Grip Pull-up Training on Strength and Endurance Performance. *J Strength
  Cond Res* 34(4):911-917. doi:10.1519/JSC.0000000000003500. PMID 32213783. Closed access.
- Sánchez-Moreno M, Pareja-Blanco F, Díaz-Cueli D, González-Badillo JJ (2016). Determinant factors of
  pull-up performance in trained athletes. *J Sports Med Phys Fitness* 56(7-8):825-833. PMID 26176615.
  Closed access.
- Muñoz-López M, Marchante D, Cano-Ruiz MA, Chicharro JL, Balsalobre-Fernández C (2017). Load-, Force-,
  and Power-Velocity Relationships in the Prone Pull-Up Exercise. *Int J Sports Physiol Perform*
  12(9):1249-1255. doi:10.1123/ijspp.2016-0657. PMID 28253041. Closed access.
- Beckham GK, Olmeda JJ, Flores AJ, Echeverry JA, Campos AF, Kim SB (2018). The Relationship between
  Maximum Pull-up Repetitions and First Repetition Mean Concentric Velocity. *J Strength Cond Res*
  32(7):1831-1837. doi:10.1519/JSC.0000000000002431. PMID 29351165. Closed access.
- Dinunzio C, Porter N, Van Scoy J, Cordice D, McCulloch RS (2019). Alterations in kinematics and muscle
  activation patterns with the addition of a kipping action during a pull-up activity. *Sports Biomech*
  18(6):622-635. doi:10.1080/14763141.2018.1452971. PMID 29768093. Closed access.
- Urbanczyk CA, Prinold JAI, Reilly P, Bull AMJ (2020). Avoiding high-risk rotator cuff loading: Muscle
  force during three pull-up techniques. *Scand J Med Sci Sports* 30(11):2205-2214.
  doi:10.1111/sms.13780. PMID 32715526. Closed access.
- Sordo-Vacas C, Garcia-Ramos A, Colomer-Poveda D (2024). Intra and Inter-Session Reliability of
  Movement Velocity During Pull-Ups Performed at Small Climbing Holds. *J Musculoskelet Neuronal
  Interact* 24(4):370-376. PMID 39616506. PMCID PMC11609558. Open access.
- Vigouroux L, Devise M (2024). Pull-Up Performance Is Affected Differently by the Muscle Contraction
  Regimens Practiced during Training among Climbers. *Bioengineering (Basel)* 11(1):85.
  doi:10.3390/bioengineering11010085. PMID 38247962. PMCID PMC10813506. Open access, CC-BY.
- Devise M, Quaine F, Vigouroux L (2023). Assessing climbers' pull-up capabilities by differentiating
  the parameters involved in power production. *PeerJ* 11:e15886. doi:10.7717/peerj.15886.
  PMID 37780381. PMCID PMC10540777. Open access, CC-BY.
- Hayashi K, Yasuda J, Aruga S (2026). Relationship Between Mechanical Variables and Maximum Strength in
  Countermovement and Pure Concentric Pull-Ups Among Male Collegiate Athletes. *Int J Exerc Sci*
  19(4):4001. PMID 41798105. PMCID PMC12965800. Open access.
- Miras-Moreno S, Pérez-Castilla A, Weakley J, Rojas-Ruiz FJ, García-Ramos A (2025). Improving the Use
  of Lifting Velocity to Predict Repetitions to Failure: A Systematic Review. *Int J Sports Physiol
  Perform* 20(3):335-344. PMID 39837320. Closed access.
- Jukic I, Prnjak K, McGuigan MR, Helms ER (2023). One Velocity Loss Threshold Does Not Fit All. *Sports
  Med Open* 9(1):80. doi:10.1186/s40798-023-00626-z. PMID 37668949. PMCID PMC10480128. Open access,
  CC-BY.
- Jukic I, Castilla AP, Ramos AG, Van Hooren B, McGuigan MR, Helms ER (2023). The Acute and Chronic
  Effects of Implementing Velocity Loss Thresholds During Resistance Training. *Sports Med*
  53(1):177-214. doi:10.1007/s40279-022-01754-4. PMID 36178597. PMCID PMC9807551. Open access.
- Morán-Navarro R, Martínez-Cava A, Sánchez-Medina L, Mora-Rodríguez R, González-Badillo JJ, Pallarés JG
  (2019). Movement Velocity as a Measure of Level of Effort During Resistance Exercise. *J Strength
  Cond Res* 33(6):1496-1504. doi:10.1519/JSC.0000000000002017. PMID 29944141. Closed access.
- Balsalobre-Fernández C, Marchante D, Baz-Valle E, Alonso-Molero I, Jiménez SL, Muñoz-López M (2017).
  Analysis of Wearable and Smartphone-Based Technologies for the Measurement of Barbell Velocity in
  Different Resistance Training Exercises. *Front Physiol* 8:649. PMID 28894425. Open access, CC-BY (no
  PMC mirror located this session).
- Balsalobre-Fernández C, Marchante D, Muñoz-López M, Jiménez SL (2018). Validity and reliability of a
  novel iPhone app for the measurement of barbell velocity and 1RM on the bench-press exercise. *J
  Sports Sci* 36(1):64-70. PMID 28097928. Closed access.

Already cited in `../pullup-emg/README.md` and `../pullup-thermal/README.md` and used again above:
Youdas et al. 2010 (PMID 21068680), Dickie et al. 2017 (PMID 28011412), Sánchez-Medina &
González-Badillo 2011 (PMID 21311352), Prinold & Bull 2016 (PMID 26383875), Williamson & Price 2021,
Ronai & Scibek 2014, Bishop et al. 2018.

## 6. How to use in the pipeline

Current code (`tools/scripts/analyze_pullups.py`, ~line 325-353):

```python
v_ref = max(r["mean_conc_v"] for r in reps)          # fastest rep's MEAN velocity in this set
...
r["effort_x"] = float(v_ref / r["mean_conc_v"])       # >1 = slower than the set's fastest rep
peak_ref = max(r["peak_conc_v"] for r in reps)        # fastest rep's PEAK velocity in this set
vl = 1 - r["peak_conc_v"] / peak_ref                  # cumulative peak-velocity loss vs fastest rep
r["est_rir"] = int(np.clip(round(5 - vl / 0.09), 0, 5))   # flat 9%-loss-per-RIR slope, capped 0-5
```

Two problems the literature identifies with this: (1) `v_ref`/`peak_ref` are **the fastest rep actually
observed in this one set**, which is a moving, set-dependent baseline — if the set was already fatigued
before frame one, or if a warm-up effect makes rep 2 or 3 faster than rep 1, every downstream number is
relative to the wrong anchor; (2) a **flat, universal %-loss-per-RIR slope** is exactly what Jukic 2023a
and 2023b show does not hold across individuals (sex, training history and psychological trait all shift
where a set actually terminates at a given %VL) — and Sánchez-Moreno 2020 shows the pull-up-specific
"still worth it" ceiling is a fixed **25% velocity loss**, not a smooth 5-step RIR ladder.

Concrete replacement, ordered by what is and is not literature-backed:

1. **Anchor velocity: prefer the first rep, not the fastest rep.** Beckham 2018 validates *first-rep*
   mean concentric velocity (ideally a single isolated calibration rep, R=0.841 vs. total reps to
   failure) as the reference; using `reps[0]["mean_conc_v"]` instead of `max(...)` matches this
   evidence and is not set-dependent. **Concrete change:** `v_ref = reps[0]["mean_conc_v"]`,
   `peak_ref = reps[0]["peak_conc_v"]`. Caveat: Beckham's subjects performed one *isolated* rep before
   resting, not the first rep of a continuous set — if Dennis's protocol allows it, a genuine single
   calibration rep before the working set (a few seconds' pause, then the set) would match the validated
   protocol more closely than reusing rep 1 of the set itself.
2. **Effort multiplier:** keep the shape `effort_x = v_ref / r["mean_conc_v"]` (it is a legitimate
   velocity-ratio, consistent with the r=-.96 MPV–%1RM relationship in Sánchez-Moreno 2017 — lower
   velocity at the same bodyweight load implies working closer to maximum), just change what `v_ref`
   means per point 1. Report it explicitly as "relative to rep 1," not as an absolute %1RM (no added-load
   1RM is known for a bodyweight set) — do not claim it converts to %1RM the way Muñoz-López 2017's
   added-load curve does.
3. **RIR: replace the flat 9%/rep slope with a two-part report, not a single fabricated number.**
   - Report cumulative `vl_pct` (already computed) directly against the two literature-anchored
     landmarks from Sánchez-Moreno 2020: **below 25% cumulative loss = "still in the strength/velocity-
     productive zone"; above 25% = "past the point where more reps still build strength/speed for this
     exercise"** (their finding was specifically about training adaptation, being reused here as a
     descriptive effort marker, which is an extrapolation — mark it as such in the report copy).
   - Do **not** report a specific "RIR N" integer as fact. The literature (Morán-Navarro 2019) shows a
     velocity-at-fixed-RIR value *can* be stable (CV 4.4-8%) — but only when derived from that person's
     own repeated testing, not a universal constant; with a single untested video, present the number as
     an estimated range (e.g. "roughly 1-2 reps left" derived from where vl_pct sits between 0% and the
     25%/50% pull-up-specific landmarks) and label it **ESTIMATE**.
4. **Kip check:** Dinunzio 2019 gives a machine-checkable kinematic signature (significant hip/knee
   angle excursion during the concentric phase) to flag alongside the existing trunk-sway/EMG-based
   technique verdict — the pipeline already tracks hip/knee angles (`hp3_l`, `hp3_r`, `kn3_l`, `kn3_r`);
   a rep whose hip or knee angle range during `t_concentric` exceeds roughly the strict-form range seen
   in Youdas 2010 (elbow ROM 93±15° is the closest available strict-form comparator; no numeric hip/knee
   ROM threshold was published) is a candidate kip flag — mark the specific angle cutoff **ESTIMATE**
   until a strict-form hip/knee ROM baseline is found.
5. **Caveats to print alongside any new number:** (a) all pull-up-specific velocity numbers above come
   from bodyweight prone/pronated-grip sets in trained men aged ~20-30 — grip variant (Urbanczyk 2020,
   Prinold & Bull 2016) and population (sex, training age) both shift the underlying %MVIC/force/ROM
   values used elsewhere in this pipeline's reports; (b) mean propulsive velocity (MPV, velocity
   averaged only while the bar/body is accelerating faster than gravity would alone) is not the same
   signal as peak velocity or the pipeline's `mean_conc_v`/`peak_conc_v` (which appear from the code to
   be plain mean/peak velocity over the whole concentric phase, not MPV) — do not present pipeline
   numbers as directly equal to a published MPV figure; (c) all the %1RM/load-velocity literature
   (Muñoz-López 2017) is from an *added-load* pull-up machine setup — the pipeline's bodyweight-only set
   has no "load" axis to place on that curve, only a velocity-relative-to-self axis.
