# The muscle model behind the heat map (v4, 2026-09-08)

Written by Fable for Dennis, who asked for the heat map to "integrate contraction and
relaxation of the movement" and for "a more scientific and precise way to formulate the
problem". This is that formulation. It is implemented in `tools/scripts/pullup_thermal4.py`
and drives every export from now on; v3 (`pullup_thermal3.py`, a phase table) is kept for
comparison and can be switched back with `model=3`.

## 1. What was wrong with v3

v3 gave every muscle a fixed share of the set's heat (%MVIC × mass, Youdas 2010) and read the
per-frame "activation" from a table: PULL 1.0, HOLD 0.85, LOWER 0.65, HANG 0.35, scaled a
little by the pull speed. Three consequences:

- a muscle could not contract and relax inside a rep, only brighten with the phase name;
- a late rep cost exactly what an early one did, so nothing compounded except temperature;
- the biceps and the lats had the same time-course, only different amplitudes.

## 2. The formulation

The problem is: given the body's motion in the video, estimate for every muscle *m* and every
frame *t* its activation *a_m(t)*, its fatigue state, its metabolic heat *q_m(t)* and its
temperature rise *ΔT_m(t)*. The standard way to do that in biomechanics is a chain of
inverse dynamics → muscle force sharing → muscle mechanics → energetics, with a fatigue
state that carries over from rep to rep. Each link, with what is measured and what is assumed:

### 2.1 Inverse dynamics (measured)

The hand force is what the body weighs plus what it accelerates:

    F(t) = m_lift · (g + a_y(t))          per arm: F/2

*m_lift* = 75.5 kg (body mass minus the forearms and hands, from the analysis), *a_y* from the
shoulder trace in the rectified bar plane. The force acts vertically through the hand, so a
joint's moment is the force times the **horizontal** distance from the hand to the joint:

    M_elbow(t)    = F/2 · d_elbow(t)
    M_shoulder(t) = F/2 · d_shoulder(t)

`d_elbow` is the trick that makes a front camera enough: the forearm's true length *L* is
measured at the dead hang (it is vertical and in the bar plane there: 28.4 cm left, 27.0 cm
right, against 27.4 cm from the segment tables for 188 cm), and in any later frame

    d_elbow = sqrt(L² − Δy²)

because whatever foreshortening took away from the picture is exactly the horizontal extent
of the forearm. `d_shoulder` has a measured across-the-picture part and a depth of the shoulder
joint behind the bar plane that **v4 assumed** (4 cm at the hang, 20 cm at the top) and **v4.2
computes** (2026-09-09, after Dennis asked why the lats sat under the biceps): the hand-to-
shoulder distance follows from the elbow angle by the law of cosines over the forearm (28.4 /
27.0 cm) and the elbow-to-shoulder-landmark length (26.6 / 25.2 cm), both measured at the plumb
dead hang; subtract what the picture shows across and down, and the remainder is depth:

    L_hs² = L_fore² + L_up² − 2 L_fore L_up cos(180° − θ_elbow)
    d_shoulder = sqrt(L_hs² − Δx² − Δy²)          (floored at 4 cm, the plumb hang)

With the on-screen (mean) 3D elbow angle this gives 4 cm at the hang, 34–39 cm mid-pull and
26–31 cm at the tops. The upper-arm length must be the landmark's own (26 cm), not the
anthropometric 35 cm: the table length put the shoulder 30 cm behind a plumb arm, which is
impossible (tried, rejected). The depth is now a measurement's consequence, with the 3D elbow
angle as its soft spot: ±10° of elbow angle is ±6 cm of depth, ±20 % of shoulder moment.

Result on this set: elbow moment 7 N·m at the hang, 79 N·m peak mid-pull; shoulder moment 24
N·m at the hang, 113 N·m median through the pull, 98 at the top, 150 N·m peak. Elbow-flexion
MVC for healthy young men is 79.5 N·m (Holzbaur et al. 2007), so the elbow flexors work at their
limit mid-pull; shoulder adduction MVC is 93.7 N·m in the same study, so the shoulder extensors
work **above** their isometric capacity through most of the pull, which is exactly what Youdas
measured for the lats (117–130 %MVIC).

### 2.2 Force sharing (literature, closed form)

More muscles cross each joint than there are equations, so the moment is shared by the static
optimisation of Crowninshield & Brand (1981): minimise Σ (F_i / F_max,i)³ subject to
Σ r_i F_i = M. With every agonist pulling the same way this has a closed form for the
activation of each muscle:

    a_i = M · (r_i F_max,i)^(1/2) / Σ_k (r_k F_max,k)^(3/2)

*F_max* = 50 N/cm² × PCSA (biceps 1060 N, brachialis 987 N, brachioradialis 261 N and lats 1253 N
from the CC BY `arm26` / Holzbaur 2005 OpenSim model in the archive; the rest listed with their
source in the module), times one **athlete factor of 1.2** at both joints (a resistance-trained
man over the healthy young adults of the strength norms; v4.1's 1.25 at the elbow alone was a
display fix and is gone). Elbow moment arms: the peaks measured by Murray, Buchanan & Delp 2000
(brachioradialis 7.7, biceps 4.7, brachialis 2.6 cm; `papers/murray2000-*.pdf`) times the
flexion hump of Murray, Delp & Buchanan 1995, and **the biceps' arm × 0.75 for the pronated
grip** (Murray 1995 measured the direction, the magnitude is assumed; Kohn et al. 2018 measured
pronated flexion MVC 42 % below supinated). That factor is the chin-up / pull-up difference in
the EMG: Youdas' biceps 96 %MVIC supinated, 78 pronated, the load moving to the brachialis and
brachioradialis. Shoulder arms: Ackland et al. 2008 measured them, but only their ranking is
readable (`08-moment-arms-and-strength.md`), so the values are assumed within that ranking, and
two of them are **calibrated to the EMG rather than predicted**: the pec (lower sternocostal
fibres only, 450 N at 1.5 cm) and the triceps' long head (shoulder arm zero; co-contraction at
12 % of the flexor drive is all it does). With the whole pec at 2.5 cm and the triceps at 1.5 cm
the sharing gave pec / lats 0.86 and triceps 0.7, where Youdas measures 0.35 and 0.15.

### 2.3 Force–velocity (Hill 1938)

The activation a muscle needs for a force depends on how fast it is changing length:

    u_i = F_i / (F_max,i · f_v(v_i)),   v_i = r_i · ω_joint / (10 · l_opt,i)

with the Hill hyperbola for shortening (a/F₀ = 0.25) and a plateau at 1.6 × isometric for
lengthening. This is why the pull costs more than the lowering; in v3 that was a table entry
(0.65), here it follows from the elbow and shoulder angular velocities that the trackers
measure. Force–length is ignored (stated).

### 2.4 Activation dynamics (Thelen 2003)

    da/dt = (u − a) / τ,   τ = 15 ms when u > a, 50 ms when u < a

Relaxation lags contraction by a few frames. Small at 30 fps, but physically right, and it is
the part that makes the map "breathe" rather than switch.

### 2.5 Fatigue that compounds (Xia & Frey-Law 2008)

Every muscle has three pools of motor units, resting *M_R*, active *M_A* and fatigued *M_F*,
that sum to 1:

    dM_A/dt = C(t) − F · M_A
    dM_F/dt = F · M_A − R · M_F
    dM_R/dt = −C(t) + R · M_F

*C(t)* is a controller that recruits resting units to make *M_A* follow the target *a(t)*
(gains 10 /s, confirmed in Looft 2018 Table 4). *F* and *R* are the fatigue and recovery rates
per joint region, **Frey-Law, Looft & Heitsman 2012, Table 1** (J Biomech 45:1803; the full
text is in the archive since v4.3, `papers/freylawlooft2012-3cc-endurance-times.xml`):

| region | F (1/s) | R (1/s) | rest multiplier r (Looft 2018, Table 4) |
|---|---|---|---|
| elbow | 0.00912 | 0.00094 | 15 |
| shoulder | 0.01820 | 0.00168 | 15, extrapolated (the shoulder was not in Looft's meta-analysis) |
| hand / grip | 0.00980 | 0.00064 | 30 |
| trunk | 0.00755 | 0.00075 | 15 |
| legs (knee row) | 0.01500 | 0.00149 | 15 |

**v4.2 and earlier held these from memory, and the shoulder's were wrong:** 0.00589 / 0.00058
is the table's *ankle* row, the grip's R was the pooled "general" row, and the trunk's was a
copy. With the true rows the shoulder fatigues at twice the elbow's rate, so the lats' pool
empties faster than the biceps', which reverses v4.2's narrative (and its excuse for the card
that showed the biceps ahead). The lesson is the repo rule: a number from memory is marked as
such until the archive confirms it, and this one was marked and was still wrong.

**Recovery is gated by blood flow (v4.3).** Looft, Herkert & Frey-Law 2018 (J Biomech 77:16,
`papers/looft2018-3cc-r-intermittent.xml`) found the original model over-predicts fatigue in
intermittent tasks by 19–29 % of torque decline, because a muscle that stops producing force
re-perfuses (reactive hyperaemia) and clears its metabolites faster than one still working.
Their 3CC-r fix multiplies *R* by *r* only while the target load is zero:

    dM_F/dt = F · M_A − R · r(t) · M_F,   r = 1 under load, r = 15 (grip 30) at rest

Fitted against 63 studies: 15 for the ankle, knee and elbow, 30 for the grip. In this set
nothing is ever at rest before the release: a contracting muscle shuts its own blood flow above
50–64 %MVC (Sadamoto, Bonde-Petersen & Suzuki 1983), the forearm's is already occluded above
~25 %MVC (Byström & Kilbom 1990), and the hang keeps the grip at 0.56 and the lats at 0.32, so
the fatigue of one rep is carried whole into the next. Harris et al. 1976 measured the same
thing chemically: phosphocreatine resynthesis is abolished under occlusion and resumes on
release with a fast half-time of 21–22 s, so five seconds of rest returns about 15 % of it.
The name for this in the physiology is **peripheral fatigue with incomplete recovery**
(Carroll, Taylor & Gandevia 2017); the modelling papers just call the carried state *the
fatigued compartment*. "Residual fatigue" is a real term but means fatigue carried between
training days; it is not used here. Sources and numbers:
`references/pullup-science/09-fatigue-recovery-and-residual.md` and
`data/fatigue-recovery-rates.csv`.

Two views of the fatigued pool are kept: the *effective* activation, the share of the
still-able units in use, drives the brightness nudge,

    a_eff = a / (1 − M_F)

and the **non-resting share** *M_A + M_F = 1 − M_R* drives the colour (§3). On this set the
fatigued pool ends at 41 % for the lats, 23 % for the grip, 20 % for the biceps (v4.2 had
19 / 26 / 22 with the wrong rows). The FATIGUE TEST printed by the module shows the pools at
each rep's top climbing monotonically (lats 6 → 47 %, biceps 2 → 21 %, grip 4 → 25 %), the
colour in the hang before each rep climbing with them (lats 37 → 82 %, grip 57 → 89 %), and the
release clearing 6–11 % of each pool in five seconds, against the 15 % that Harris' fast
component allows as a ceiling. That is the compounding Dennis asked about, twice: the same rep
late in the set is drawn from a smaller pool, and the pool never refills until the hands open.
The measured −40 % peak speed is the consequence; the literature's shape for it is an EMG
amplitude climbing 86 → 124 %MVC from the first rep to the last (Sundstrup 2012) and sets to
failure ending at 40–60 % speed loss (`10-rep-to-rep-fatigue-in-a-set.md`).

### 2.6 Metabolic heat (Umberger 2003 structure, calibrated)

Per muscle, per frame:

    q_i = k · mass_i · a_i · (1 + 1.2 · max(v̂_i, 0) + 0.3 · max(−v̂_i, 0))

activation/maintenance heat plus a shortening term and a small lengthening term. The one
constant *k* is fixed so that the set total equals the energy budget the analysis already
reports (work / 22 % efficiency, eccentric at 35 % of that, the isometric hang cost with the
grip's and the legs' local share): 26.9 kJ deposited in the muscles, the same figure v3 used.
The numbers on the judge's card therefore do not change; only *where* and *when* the heat
lands does.

### 2.7 Temperature (unchanged from v3)

    C · dT_i/dt = q_i − k_blood(t) · ΔT_i,   C = 3.6 kJ/kg/K,  k_blood → 42 W/K/kg with τ = 90 s

González-Alonso 2000, Kenny 2003; temperature never falls inside a set.

## 3. What the map shows now (v4.1, 2026-09-09)

Dennis watched v4 and saw "only a progressive increase in heat". He was right: v4 coloured the
body by *temperature*, which by construction never falls inside a set (§2.7), and put the
activation into brightness, a ±22 % modulation that the frame's own shading swallowed. The
model was contracting and relaxing (biceps 0.9 on the pull, 0.2 at the hang); the picture was
not showing it. v4.1 changes what the colour *is*:

    E_i(t) = min(1, 0.9 · a_eff,i(t) + 0.2 · ΔT_i(t) / 1.5 °C)          (v4.1 – v4.2)
    E_i(t) = min(1, 0.9 · (M_A,i(t) + M_F,i(t)) + 0.2 · ΔT_i(t) / 1.5 °C)  (v4.3)

- **Colour** = the effort index *E*, blue → cyan → green → yellow → orange → red. In v4.3 the
  fast part is the **non-resting share of the motor-unit pool**: the active units *M_A*
  contract and relax inside every rep (the biceps go red in the middle of the pull and drop
  toward blue at the hang, the lats peak red at the top, the grip stays orange because it never
  lets go), and the fatigued units *M_F* are the heat one rep leaves in the next, a floor that
  climbs rep by rep (the lats' hang goes from green at rep 1 to orange at rep 11, the biceps'
  from blue to green) and starts to clear only when the hands open. v4.1–4.2 used the
  effective activation, which returned to the same hang colour between reps and hid the
  carry-over Dennis asked for on 2026-09-09 ("each rep should get hotter, and only when I let
  go should the whole body slightly cool"). At the release the working share drops at once
  (the lats' colour 100 → 54 % over five seconds) while the fatigued share lingers, clearing
  6–11 % in that time; the video ends 2.3 s after the release, while he still stands straight.
  The slow part is the temperature as a floor, unchanged. The ironbow is gone (too dark in the
  purples); `lut=iron` brings it back.
- **Brightness** nudges with activation (±10 %), the rest is anatomy shading.
- **Names** appear the first time a muscle's effort passes 0.55, with its effort in %.
- **The left stack** carries the numbers that compound: chin tally, speed loss, running peak
  power, lats' temperature (still a modelled °C), the biceps' fatigued pool, calories and heat.

Three changes to the mechanics came with it:

1. **Elbow flexor strength ×1.25.** With the generic `arm26` strengths the required biceps
   activation on the pull was 1.1–1.4 and clipped at 1, so the pull and the lowering both
   painted as "max". A man doing 11 strict pull-ups at 79 kg has more than generic elbow
   flexors; ×1.25 puts the peak of the pull at ≈1.0 and the lowering at ≈0.6, which is the
   eccentric / concentric ratio the EMG literature reports (§4.1). Assumed; ranked in §5.
2. **The trapezius and the pec start the pull.** While the phase is PULL and the elbow is
   still under 35° of flexion the lower / middle trapezius gets its own drive (+0.35) and the
   pectoralis major +0.25, because the rep is "initiated by the lower trapezius and pectoralis
   major" and "completed with biceps brachii and latissimus dorsi" (Youdas 2010, full text as
   paraphrased by Di Fonza 2026; scapular depression before the elbow bends, Prinold & Bull
   2016). They no longer only follow the lats. In rep 5 the model now ramps pec 0.44 → 0.61
   and trapezius 0.36 → 0.53 over the first eight frames of the pull while the biceps is still
   at 0.36 → 0.54 and the lats at 0.40 → 0.49; then the biceps overtakes, then the lats.
3. **The legs breathe.** The hip flexors, quadriceps and calves hold the tuck against
   g + a_y, so their drive scales with the measured vertical acceleration (0.5–1.6 ×) instead
   of one constant for the whole set. They stay blue: in a strict pull-up they are passengers.
4. **Hands on the bar is not hanging.** Dennis pointed out that at the start he only holds the
   bar, sinks into the hang with his feet still on the floor, and lifts the legs about five
   seconds later. The moment the feet leave is read from the knee angle (both knees under 120°
   for five frames: 14.2 s in the source), and before it the hand force carries a load fraction
   from how far the shoulders have sunk from the standing hold toward the hanging level (floored
   at 0.2 for the grip). The pill says HANDS ON BAR there and the body paints blue until the
   weight is actually on the hands.
5. **v4.2, the review** (Dennis: "sure you didn't mistake chin-ups and pull-ups?"). The shoulder's
   depth behind the bar is computed, not assumed (§2.1); the biceps carries the pronated grip's
   smaller moment arm; one athlete factor (1.2) at both joints from the Holzbaur 2007 norms; the
   lats' F_max from Holzbaur 2005; the pec's and triceps' shoulder roles calibrated to Youdas' EMG
   ratios (§2.2). Whole-rep lats / biceps went from 1.08 to 1.67 (Youdas 1.59, Snarr 1.82). The
   left stack shows both fatigued pools (lats · biceps), and the closing frame is a references
   card instead of the judge's card, held 0.5 s (the numbers live in the caption and here).

Muscles without a visible lever (rotator cuff, trapezius, serratus, core, legs) otherwise follow
the lat's activation at their published EMG ratio (Youdas 2010, Tucker 2011), the core rising
with measured hip motion (Dinunzio 2018), as in v3.

## 4. Validation against the EMG literature

Mean required activation per phase, this set (v4), against the whole-rep %MVIC of Youdas 2010:

| muscle | PULL | HOLD | LOWER | HANG | fatigued at the end | Youdas %MVIC |
|---|---|---|---|---|---|---|
| latissimus dorsi | 1.17 (peak 1.5) | 1.09 | 1.28 | 0.32 | 19 % | 117–130 |
| biceps brachii | 0.88 (peak 1.3) | 0.54 | 0.67 | 0.19 | 22 % | 78–96 |
| brachialis | 0.73 | 0.45 | 0.55 | 0.15 | 19 % | (78, assumed) |
| brachioradialis | 0.69 | 0.40 | 0.46 | 0.14 | 18 % | 62 (est.) |
| forearm flexors (grip) | 0.60 | 0.55 | 0.61 | 0.56 | 26 % | 60 (est.) |
| infraspinatus | 0.70 | 0.76 | 0.95 | 0.19 | 16 % | 71–79 |
| trapezius, lower / middle | 0.63 | 0.71 | 0.67 | 0.14 | 14 % | 45–56 |
| pectoralis major | 0.52 | 0.44 | 0.51 | 0.11 | 11 % | 44–57 (calibrated) |
| teres major | 0.51 | 0.55 | 0.67 | 0.14 | 12 % | (99, assumed) |
| triceps | 0.11 | 0.07 | 0.08 | 0.02 | 2 % | 15 (calibrated) |

v4.2 numbers. The HANG column includes the seconds before the feet leave the floor, when the
hands carry a reduced load (§3 item 4). **The ordering test** (whole-rep required activation,
printed by the module): lats 1.19, biceps 0.71, brachialis 0.59, trapezius 0.66, pec 0.49;
lats / biceps = **1.67** against Youdas' 1.59 and Snarr's 1.82; pec / lats = 0.42 against
Youdas' 0.35. **The capacity test:** elbow 99 N·m pronated against a peak demand of 79 (norm
79.5 supinated); shoulder 93 N·m against a median pull demand of 113 and a peak of 150 (norm
93.7). The lats therefore sit at or above capacity through the pull, the top and the lowering
and relax only in the hang; on screen they are red for the whole rep and green between reps,
which is what a whole-rep 124 %MVIC looks like.

### 4.1 Phase by phase, against `references/pullup-science/07-phase-resolved-emg.md`

Dennis asked (2026-09-09) which muscles work in each part of the pull-up. A research pass
collected what exists (abstracts, two open-access full texts, a 134-row CSV in `data/`); the
honest headline is that **no study publishes a time-normalised EMG envelope of the pull-up
outside a paywall**, so the comparison is against directions and orderings, not curves:

| what the literature says | source | the model |
|---|---|---|
| The rep is initiated by the lower trapezius and pectoralis major | Youdas 2010 (discussion), Di Fonza 2026 | yes since v4.1: both lead the first ~8 frames of the pull (§3) |
| Biceps and lats build through the pull and complete it | Youdas 2010 | lats yes (0.54 → 0.84 at the top); the **biceps peaks mid-pull** (elbow lever largest near 90°) and is 0.47 at the top: the lever physics disagrees with the description here, and the video's elbow angles decide, not the model |
| Biceps, brachioradialis, pec significantly lower in the eccentric than the concentric (P < 0.01) | Dickie 2017 | yes: 0.56 / 0.81, 0.35 / 0.52, 0.57 / 0.75 |
| Lats do not drop off in the eccentric like the other prime movers | Doma 2013, Williamson & Price 2021 | yes: 0.71 on the lowering against 0.84 at the top (ratio 0.85, the biceps' is 0.69) |
| Triceps nudges up on the eccentric (elbow control) | inferred in 07 | yes: 0.38 lowering, 0.31 pull |
| Core flat and low in a strict rep; rises only with hip motion | Dinunzio 2018 | yes: rectus 0.13–0.25, keyed off the measured hip sway (5 cm here, so no boost) |
| Grip never has an off phase inside a rep | 07 (no pull-up grip EMG exists; reasoning) | yes: 0.55–0.61 in every phase, orange throughout the video |
| Dead hang: no primary EMG exists; an active hang re-engages lats / lower trap / serratus | 07, flagged as unsourced | the model keeps the lats at 0.35 in the hang (their share of the static shoulder moment), which reads as an active hang; that is the mechanics, not a citation |

No millisecond onset timing is claimed anywhere on screen: the initiation window is "the elbow
under 35° of flexion while the shoulder rises", which the tracker measures, and the order
inside it (pec and trapezius before biceps before lats) is the descriptive sequence Youdas
gives, not a latency.

Where it agrees (v4.2): the lats above the biceps over the whole rep at the ratio the EMG gives,
the biceps at its limit mid-pull, the grip flat through the whole set, concentric above eccentric
at the elbow without a table saying so, the lats holding through the lowering (Doma 2013), the
pec and triceps at the EMG's level because they were calibrated to it. Where it does not: the
lats' demand exceeds the model's capacity by up to 50 % at the peaks (the shoulder norms are
adduction at 60°, not extension from overhead, and the moment arms are assumed within Ackland's
ranking), so their within-rep contrast is lost to clipping; the biceps peaks mid-pull where
Youdas describes it completing the rep; and the whole shoulder side rests on the 3D elbow angle
through the depth computation. A side camera measures the depth and the elbow angle directly
and retires both.

## 5. Assumptions, ranked by how much they move the picture

1. The 3D elbow angle (MediaPipe) through the shoulder-depth computation: ±10° is ±6 cm of depth
   and ±20 % of shoulder moment, and the two elbows disagree by 20° where the image plane says
   2°. The depth itself is no longer assumed (v4.2), but it inherits this. A side camera fixes it.
2. Shoulder moment arms at overhead elevation: assumed within Ackland 2008's ranking (lats 4.5,
   teres major 2.5, pec 1.5, posterior deltoid 1.5 cm); the pec's and the triceps' were calibrated
   to Youdas' EMG ratios. Ackland's numbers would replace all of them in one edit.
3. The athlete factor 1.2 at both joints (Holzbaur 2007 norms are for untrained young adults; no
   shoulder-extension-from-overhead norm exists). A dynamometer session replaces it.
4. The biceps' pronated moment-arm factor 0.75 (direction measured by Murray 1995, magnitude
   assumed; Kohn 2018's 42 % strength drop says it could be larger).
5. Fatigue rates F, R: published per joint region (Frey-Law 2012 Table 1, verified v4.3), not
   per muscle; the legs take the knee row (assumed mapping); the shoulder's rest multiplier is
   Looft 2018's general value, extrapolated; the rest threshold (target load under 2 %) is
   assumed. They set how fast each pool empties, and that the lats' pool leads the biceps'.
6. Grip activation at the hang (60 %) and its scaling with the hand force; the hand-load fraction
   before the feet leave the floor (0.2 floor, shoulder-sink ramp).
7. The trapezius' and pec's initiation drives (0.35 / 0.25 while the elbow is under 35°) and the
   stabiliser ratios: literature ratios, not measured on him.
8. Force–length ignored; segment weights of the arm ignored; both arms share the force equally
   (Prinold 2016: < 5 % BW asymmetry in regular practitioners).
9. The heat calibration: the shape per muscle is the model's, the total is the analysis'.
10. The effort index weights (0.9 fast, 0.2 slow, clipped at 1) are a display choice, not
    physiology, and so is weighting the active and the fatigued units equally in the fast part
    (v4.3: the fraction of the pool that is not resting); the legend says "a model" on every
    frame.

## 6. What a side camera would add

Chin depth, shoulder depth, elbow angle in its own plane, the sagittal lever of every joint —
the four assumptions above collapse into measurements. One phone at hip height, 3 m to the
side, is enough.

## References (all in `references/pullup-science/` unless marked)

Crowninshield & Brand 1981 (J Biomech; classic, not in the archive) · Murray, Delp & Buchanan
1995 (J Biomech; classic, not in the archive) · Ackland, Pak, Richardson & Pandy 2008 (J Anat;
not in the archive) · Hill 1938 · Thelen 2003 (J Biomech Eng) · Xia & Frey-Law 2008 (J
Biomech) · Frey-Law, Looft & Heitsman 2012 (J Biomech; `papers/freylawlooft2012-…xml`) ·
Looft, Herkert & Frey-Law 2018 (J Biomech; `papers/looft2018-…xml`) · Sadamoto 1983, Byström &
Kilbom 1990, Harris 1976, Bogdanis 1995, Carroll, Taylor & Gandevia 2017, Allen, Lamb &
Westerblad 2008 (`09-fatigue-recovery-and-residual.md`) · Sundstrup 2012, García-Ramos 2020,
Sánchez-Moreno 2017, Kenny 2003 (`10-rep-to-rep-fatigue-in-a-set.md`) · Umberger, Gerritsen & Martin
2003 (Comput Methods Biomech Biomed Engin) · Youdas 2010, Tucker 2011, Dinunzio 2018, Dickie
2017, Snarr 2017 (`01-emg-and-anatomy.md`) · Holzbaur 2005/2007, Garner & Pandy 2003, An 1981
(`data/anatomy-pcsa-volume.csv`) · González-Alonso 2000, Kenny 2003 (`04-thermal-skin…`) ·
OpenSim `arm26.osim` (`anatomy-assets/opensim-models/`, CC BY 3.0).
