# Pull-up analysis #3 — IMG_6108.MOV (shot 2026-09-08 11:35, analysed the same evening)

Third set, third camera position: iPhone 14 on the floor 2.8 m from the doorway, looking up
6.5°, 63.6 s, 1080×1920 after the rotation tag, 30 fps, 1909 frames, 10-bit HLG. Dennis
(188 cm, 79 kg), pronated grip, legs crossed and tucked. A black cat sits in the bottom of
the frame from about 15 s. The two earlier reports (`REPORT.md`, `REPORT-2.md`) stand for
their own clips; this one supersedes their methods where they differ, and it is the first
built on the literature archive in `references/pullup-science/` (six files, 60-odd papers).

## Headline

**11 reps, chin at the bar on every one, never clearly over it.** Every rep locked out at
the bottom (160–167°), none kipped (hips travel 5 cm), and every rep held the top for
0.6–0.9 s with the head behind the bar for 0.9–1.4 s. In the doorway plane the chin finishes
1.7 to 5.0 cm below the top edge of the bar; the floor camera hides about 3.4 cm of that
(0.43 cm per cm of depth, for a chin 8 cm behind the bar). Adjusted, the eleven reps sit
between −1.6 and +1.7 cm: at the bar, within the ±3 cm this camera can resolve. It is the
same finding as set #2 from a different camera and a different method: his mouth clears the
bar, his chin reaches it, and a strict judge would want 3 more centimetres.

The set was not taken to failure this time. Peak speed fell 40 % from rep 1 and 53 % from
the fastest rep (rep 5); the pull-up training cut-off of 25 % loss (Sánchez-Moreno 2020) was
crossed at rep 10.

## What changed in the method

| | |
|---|---|
| **Tone-mapped master** | The phone records 10-bit HLG. Sets #1 and #2 were decoded flat (grey skin, no contrast); this one is tone-mapped on the GPU (libplacebo, BT.2390) to an SDR master before anything reads a pixel. |
| **Measure in a rectified plane, render on the frame** | Vertical and horizontal vanishing points from long edges (RANSAC, 100 and 149 inliers), f = 1950 px from their orthogonality, H = K Rᵀ K⁻¹, then a residual 0.72° rotation so the fitted bar is exactly level (the lintel tilts identically, so the residual was the model). Every landmark goes through H before it is measured. px/m is then uniform over the doorway plane. |
| **Scale** | 708 px/m from the standing stature under the bar (eye-to-ankle 1193 px = 168.6 cm). Confirmed independently: shoulder-to-bar at the dead hang = 62.7 cm, against 0.332 × 188 = 62.4 cm from the anthropometric tables. The arm anchor (617 px/m) under-reads because the wrist joint sits 8 cm below the bar. |
| **Depth allowance is computed, not assumed** | Elevation of the camera to the bar 23.4°, so a point d cm behind the bar plane projects 0.43 d cm lower. Set #1's "3 cm perspective allowance" was this quantity, guessed. |
| **The chin, by witness** | The bar is mounted at the back edge of the lintel's underside, so at the top of a legal rep the whole head is hidden by the bar and the underside together, with the neck visible up to the bar. YOLO's nose confidence collapses on reps 1–8 and stays high (hallucinated) on 9–11; MediaPipe's visibility stays 1.0 throughout. So the chin is extrapolated from the last frame the face is genuinely seen on the way up (eyes ≥ 4 cm below the bar's underside and nose confidence > 0.35) plus the shoulder rise after it, and the head-hidden time is reported as its own number. The silhouette (RVM alpha) was tried as a witness too: it confirms the neck reaches the bar's underside on every top, and nothing more. |
| **Phase walker from the local base** | A passive dead hang sits 2–3 cm lower than the active hang he pulls from; walking back to the deep base swallowed the whole dead hang into rep 1's concentric (3.2 s). Each concentric now starts from the highest shoulder position in the second before the pull. |
| **Velocity references** | Rep 1 (Beckham 2018) and the fastest rep, both printed. Velocity loss against the 25 % / 50 % landmarks; RIR as an estimate range, never an integer. |
| **Anatomy** | 14 painted regions from a landmark-warped atlas with fibre directions, boundaries and belly shading (`pullup_atlas3.py`), 23 muscles in the heat budget (`pullup_thermal4.py`: inverse dynamics → force sharing → force–velocity → activation dynamics → fatigue; `MUSCLE-MODEL.md`): serratus anterior, upper trapezius, middle deltoid, triceps and forearm extensors added from 01-emg-and-anatomy.md; the lat share shifts toward the trapezius at the top (Park & Yoo 2013); core heat keys off measured hip motion (Dinunzio 2018). |

**Cross-check.** YOLOv8m-pose finds the same 11 tops; shoulder tracks correlate at r = 0.998.
MediaPipe found a pose on 1897 of 1909 frames.

## Timeline

| | |
|---|---|
| Walks in, stands under the bar | 6.4 – 9.3 s |
| Hands on the bar, feet leave the floor | 9.4 s (he steps up; no standing-on-the-bar phase) |
| Dead hang before rep 1 | 3.9 s (passive at first, then he sets the shoulders and rises 2–3 cm) |
| Working set | 13.6 – 55.9 s: 42.3 s, 15.6 reps/min |
| Off the bar | 56.6 s |

## The set

| | |
|---|---|
| Reps | **11**, no failed attempt |
| Chin vs the bar top, in the doorway plane | −1.7 to −5.0 cm, mean **−3.5 cm** |
| Chin, adjusted for the camera (chin 8 cm behind the bar plane) | −1.6 to +1.7 cm, mean **−0.1 cm**: at the bar, 11/11 |
| Head behind the bar | 11/11 reps, 0.9–1.4 s each |
| Full lock-out at the bottom | **11 / 11** (3D elbow 160–167°) |
| Range of motion | 47–51 cm of shoulder travel in the plane; ≈ 55 cm true vertical once the body's depth change is allowed for |
| Tempo | 1.1 s up / 0.7 s hold / 1.1 s down, 0.7 s at the bottom |
| Peak pull speed | rep 1 0.62 → rep 5 0.79 → rep 11 0.38 m/s: −40 % vs rep 1, −53 % vs the fastest |
| Hip travel during a rep | 5 cm — no swing |
| Grip | 1.3 × shoulder width |
| Shoulder line at the top | −3.1° (right shoulder lower), vs −1.2° standing; the wrist line reads −1.0° as the control |
| Mean efficiency | 79 / 100 (a composite, not a form verdict) |

## Judge's card — USMC PFT pull-up standard

| check | result | verdict |
|---|---|---|
| Dead hang, arms extended | 160–167° at every bottom, 3.9 s hang before rep 1 | **pass, 11/11** |
| Chin above the bar | at the bar on all 11 (−3.5 cm in plane, ≈ 0 adjusted, ±3) | **borderline on all 11** — a lenient judge counts them, a strict one wants 3 cm more |
| Lower to full extension | 11/11 | **pass** |
| No kipping | hips travel 5 cm | **pass** |
| Leg movement | knees tucked and crossed throughout; the hip angle changes as the torso rises | **borderline**, as in set #2 |
| Set honesty | stopped at 11 with 40 % velocity loss, not to failure | — |

On the chin, in one paragraph. Three witnesses agree: the extrapolated chin (−1.7 to −5.0 cm
in plane), the neck visible right up to the bar's underside on every top (which puts the chin
at or above the underside's sight line, i.e. ≥ −3.7 cm + 0.43 × depth), and the shoulders
sitting 14–17 cm below the bar in plane against a shoulder-to-chin length of 16 cm. All three
say the chin arrives at the bar's height and no further. What the camera cannot resolve is
the last 3 cm, because the chin's depth behind the bar is not measured; a side camera would.

## Left vs right

| measure | standing | at the top | reading |
|---|---|---|---|
| Shoulder line tilt | −1.2° | −3.1° (right lower by 1.4 cm) | Real: the wrist line, on a level bar, reads −1.0° at the same moment. The right shoulder rides low under load. |
| Ear to shoulder | L 25.2 / R 27.5 cm | — | The right side is longer standing too: part build, part habit. |
| Elbow angle at the top, 3D | — | L 50–59° / R 68–79° | **Unresolved for the third time.** The image plane says 12–17° on both sides. Same disagreement as set #2, so it is systematic to the model or the man; a side camera settles it. |
| Grip | — | symmetric about the grip centre | — |
| Lead arm | — | no consistent lead | — |

## Work, power, energy (188 cm, 79 kg, lifted mass 75.5 kg)

| | |
|---|---|
| Work per rep | 360 J in the plane (≈ 400 J true) — 4.0 kJ for the set |
| Mean pull power | 387 W best (rep 2) → 250 W (rep 11) |
| Peak power | ≈ 680 W |
| Energy, rough | ≈ 0.8 kcal per rep, **≈ 10 kcal for the set** |
| Heat produced | **≈ 36 kJ** (21 kJ from muscle work, 16 kJ isometric) |

Energy model as before (concentric work ÷ 22 %, lowering at 35 % of that, 3.5 MET while on
the bar). 03-norms-and-energy.md brackets the constants with measured values: concentric
efficiency 15 % (Ryschon 1997) to 25 %, the eccentric at one sixth of the concentric cost
(Bigland-Ritchie & Woods 1976); the Compendium's 7.5 MET for vigorous calisthenics gives
0.3–0.7 kcal per rep, the same order. Segment fractions are now de Leva 1996 (hand 0.61 %,
forearm 1.62 %: 4.46 % for both arms, so the lifted mass is 75.5 kg). "About 1 kcal a rep"
stands.

## Where this set sits

USMC PFT, male, 27–30: 5 reps to pass, 23 for the maximum score; 11 strict reps is a passing
score in the lower-middle of the table (03-norms-and-energy.md; the official table was
recovered from two secondary sources, the .mil PDFs refuse fetches). Crowd-sourced strength
norms put 13 at "intermediate" for 79 kg. Allometric adjustment (2/3 power, 73 kg reference)
moves 11 reps at 79 kg to 11.6.

## Modelled muscle temperature (v4: driven by the mechanics of the rep)

The heat budget is the one from set #2 - C dT/dt = q - k(t) dT, 3.6 kJ/kg/K, removal ramping
with a 90 s time constant to 42 W/K/kg (González-Alonso 2000), 26.9 kJ deposited in the
muscles - but *where and when* the heat lands is no longer a fixed share read from an EMG
table. `pullup_thermal4.py` (formulation in `MUSCLE-MODEL.md`) runs the standard chain:
the hand force from the body's weight and acceleration, each joint's moment from that force
and its lever measured in the rectified plane (the forearm's foreshortening gives the elbow's
lever; the shoulder's depth behind the bar is assumed, 4 → 20 cm), Crowninshield & Brand 1981
force sharing between the muscles that cross the joint, Hill force–velocity (which is why the
pull costs more than the lowering), Thelen 2003 activation dynamics, and the three-compartment
fatigue model of Xia & Frey-Law 2008 so that a late rep draws on a smaller pool of able motor
units. Peak elbow moment 79 N·m, peak shoulder moment 76 N·m; the biceps reaches its limit in
the middle of every pull; the lats work at or above their isometric capacity through the pull,
the top and the lowering (whole-rep 1.19, against Youdas' 124 %MVIC) and relax only in the hang.
The fatigued pool ends at 41 % for the lats, 23 % for the grip, 20 % for the biceps (v4.3, with
Frey-Law, Looft & Heitsman 2012's Table 1 read from the archived full text: the shoulder's
fatigue rate is twice the elbow's. v4.2 had the biceps ahead, 22 / 26 / 19, because the
shoulder's rates had been entered from memory and were the table's ankle row). Nothing
recovers between reps: a contracting muscle occludes its own blood flow above 50–64 %MVC
(Sadamoto 1983), the forearm's above ~25 % (Byström & Kilbom 1990), and the hang keeps the grip
and the lats loaded, so each rep starts with the previous rep's fatigue in the pool, which is
peripheral fatigue with incomplete recovery (Carroll, Taylor & Gandevia 2017). Recovery starts
when the hands open, at 15× (grip 30×) the under-load rate (Looft, Herkert & Frey-Law 2018),
and clears 6–11 % of the pool in five seconds, in line with phosphocreatine's 21–22 s
half-time (Harris 1976). Before the feet leave the floor (14.2 s in the source, read from the
knee angle) the hands carry only the fraction of the weight the shoulders' sinking implies, so
the first seconds paint blue and the pill says HANDS ON BAR. End-of-set rise, painted muscles
(v4.2):

| muscle | Youdas %MVIC | ΔT at the end |
|---|---|---|
| latissimus dorsi | 124 | **+1.21 °C** |
| infraspinatus | 75 | +0.93 °C |
| forearm flexors (grip) | 60 | +0.92 °C |
| biceps brachii | 78 | +0.89 °C |
| upper trapezius (Tucker 2011) | 62 | +0.84 °C |
| trapezius, middle and lower | 52 | +0.80 °C |
| brachialis | 78 | +0.75 °C |
| teres major | 99 | +0.73 °C |
| brachioradialis | 62 | +0.68 °C |
| pectoralis major | 44 | +0.61 °C |
| middle / posterior deltoid | 45 / 60 | +0.59 / +0.43 °C |
| forearm extensors (estimate) | 35 | +0.54 °C |
| external oblique | 33 | +0.53 °C |
| rectus abdominis | 20 | +0.40 °C |
| serratus anterior (Tucker 2011) | 26 | +0.35 °C |
| hip flexors, quadriceps, calves | 18 / 8 / 4 | +0.28 / +0.13 / +0.06 °C |
| triceps | 15 | +0.11 °C |

**The review (v4.2).** Dennis saw the biceps' fatigue above the lats' and asked whether the model
was a chin-up's. It was validated against Youdas' pronated pull-up column all along, but its lats
sat barely above its biceps (whole-rep ratio 1.08) where the EMG has 1.6 (Youdas) to 1.8 (Snarr
2017). Two causes, both fixed: the shoulder's depth behind the bar had been assumed at 20 cm and
is now computed from the elbow angle and the measured segment lengths (26–31 cm at the tops,
34–39 mid-pull), which raises the shoulder moment to 100–150 N·m; and the biceps carried a
supinated-grip moment arm, now × 0.75 for the pronated grip (Murray 1995 direction, Kohn 2018
magnitude). Capacities come from the Holzbaur 2007 strength norms with one athlete factor of 1.2
at both joints; the pec's and the triceps' shoulder roles are calibrated to Youdas' ratios because
Ackland 2008's moment arms are behind a paywall. Result: whole-rep lats / biceps 1.67. The whole
argument, every constant with its source and the ranked assumptions, is in `MUSCLE-MODEL.md`
and in the comments of `tools/scripts/pullup_thermal4.py`.

**What the colour is (v4.1, 2026-09-09).** The first cut coloured the body by this temperature,
and because a muscle's temperature never falls inside a set the map only ever got hotter, even
though the model underneath was contracting and relaxing. The colour is now the *effort index*,
0.9 × the share of the muscle's motor units that are not resting (active + fatigued, v4.3;
v4.1–4.2 used the effective activation a / (1 − fatigued), which returned to the same hang
colour between reps and hid the carry-over) plus 0.2 × the temperature over 1.5 °C, clipped at
1, on a blue → red scale. The active share contracts and relaxes inside the rep; the fatigued
share is the heat one rep leaves in the next: the lats' hang colour climbs 37 → 82 % from rep
1 to rep 11, the grip's 57 → 89 %, and at the release the active share drops at once (lats
100 → 54 % in five seconds) while the fatigued share only begins to clear. Per rep the v4.1
model gave (mean effort, PULL / HOLD / LOWER /
the hang after): biceps 0.66 / 0.42 / 0.56 / 0.26 at rep 5 (peak ≈ 1.0 mid-pull), lats 0.53 /
0.78 / 0.62 / 0.35, grip 0.59 / 0.57 / 0.62 / 0.63, trapezius 0.35 / 0.49 / 0.28 / 0.15,
hip flexors 0.16 throughout. So the biceps go red at the sticking point and cyan at the hang,
the lats peak at the top and settle to green in the active hang, the grip stays orange, the legs
stay blue, and rep 11's top is red where rep 5's was yellow-orange. The elbow flexors carry a
×1.25 strength factor over the generic OpenSim strengths (otherwise their demand clipped at 1
and the pull and the lowering both painted as max); the trapezius has its own drive at the start
of the pull (scapular depression before the elbow bends); the legs scale with g + a_y. Muscle
names appear the first time a muscle's effort passes 0.55. Where the model and the EMG
literature disagree (Youdas has the lats above the biceps over the whole rep; the model has
them below) the cause is the shoulder depth the front camera cannot see. The legend says it on
every frame: a model, not a thermal camera.

**What an infrared camera would show (04-thermal-skin-and-anatomy-assets.md):** less, and
later. Skin over a working muscle *drops* in the first minute of a bout (Merla 2010,
Formenti 2016, Chudecka 2015) and warms after it; the effective conductivity through skin
and fat is 0.3–0.7 W/m/K (Ducharme & Tikuisis 1991), so a 42 s set barely reaches the
surface.

## The chest flush, measured — and re-interpreted

The index from set #2, (R−G)/(R+G) × 1000 over the chest skin at the dead hang after each
rep, minus the same index on a fixed patch of tile wall left of the doorway:

| | index |
|---|---|
| After rep 1 | 122.7 |
| After rep 5 | 133.1 |
| After rep 8 | 140.2 |
| After rep 10 / 11 | 153.5 / 149.6 |
| Wall control | 2.2–2.5 throughout (flat) |

It rises 27 units over the set, r = 0.93 with time and r = 0.92 with the modelled lat
temperature. The standing baseline (137.6) is not comparable: he stood closer to the camera
with the arms up, and the camera's white balance moved with him.

The interpretation has to change from set #2. Tonight's sweep of the vasodilation literature
(Kellogg 1991, Taylor 1990, Charkoudian 2010, Demachi 2013) says skin blood flow *falls* in
the first minute of exercise and the thermoregulatory flush needs a core-temperature rise
that takes many minutes. A 42 s set cannot be that. Plausible mechanisms for a chest that
visibly reddens within reps are venous engorgement under the Valsalva strain and a local
histamine response, neither confirmed for the chest specifically. So: the flush is real,
measured, and it tracks effort; it is not evidence of muscle temperature reaching the skin,
and the caption must not say it is.

## Per rep

| rep | top (s) | chin in plane (cm) | chin adj. (cm) | head hidden (s) | ROM (cm) | up/hold/down (s) | peak v (m/s) | loss vs rep 1 | sh tilt | sway (cm) | eff |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 16.9 | −2.8 | +0.6 | 0.9 | 50 | 1.20/0.60/1.13 | 0.62 | 0 % | −3.2° | 5.7 | 82 |
| 2 | 20.2 | −1.7 | +1.7 | 1.1 | 49 | 0.93/0.67/1.23 | 0.73 | — | −4.1° | 4.6 | 88 |
| 3 | 24.3 | −1.8 | +1.6 | 1.1 | 49 | 1.17/0.73/1.07 | 0.58 | 7 % | −3.3° | 4.8 | 83 |
| 4 | 27.7 | −2.8 | +0.6 | 1.0 | 48 | 0.90/0.70/1.00 | 0.78 | — | −3.0° | 5.6 | 83 |
| 5 | 30.9 | −4.3 | −0.9 | 1.0 | 48 | 0.87/0.70/1.17 | 0.79 | — | −2.0° | 4.9 | 84 |
| 6 | 34.5 | −3.7 | −0.3 | 1.0 | 49 | 0.90/0.67/1.13 | 0.79 | — | −2.2° | 5.5 | 84 |
| 7 | 38.0 | −3.4 | 0.0 | 1.2 | 48 | 0.97/0.83/1.10 | 0.70 | — | −3.8° | 5.7 | 80 |
| 8 | 41.9 | −5.0 | −1.6 | 1.1 | 47 | 1.07/0.70/1.07 | 0.63 | — | −3.1° | 4.7 | 77 |
| 9 | 45.1 | −4.8 | −1.4 | 1.2 | 47 | 1.07/0.83/1.07 | 0.63 | — | −2.4° | 6.0 | 77 |
| 10 | 49.3 | −4.1 | −0.7 | 1.4 | 51 | 1.30/0.87/1.33 | 0.48 | 23 % | −3.7° | 5.3 | 79 |
| 11 | 54.4 | −4.5 | −1.1 | 1.1 | 49 | 1.70/0.57/0.93 | 0.38 | 40 % | −3.2° | 4.2 | 72 |

A dash in the loss column means the rep was faster than rep 1 (reps 2 and 4–7 were): rep 1
was a deliberate start, which is why the fastest rep is reported beside it. The adjusted
chin carries ±3 cm.

## What to change, in order of size

1. **Three more centimetres at the top**, again. The pause is there and the head is behind
   the bar on every rep; the chin stops at the bar's height. Aim the collarbones at the bar.
2. **Keep the right shoulder down.** The shoulder line tilts 3° at the top with the wrists
   level on the bar, and the right ear-to-shoulder distance is the longer one even standing.
3. **Stop at 25 % velocity loss if the goal is strength**: that was rep 10. Reps 10 and 11
   cost 1.5–1.7× the effort of rep 5 for the same work.
4. **For the next shoot:** a second phone from the side at hip height settles the chin depth,
   the elbow asymmetry and the true range of motion in one go; a 1 m stick held at the bar
   pins the scale; lock the exposure so the flush measurement gets a baseline.

## Caveats

- One camera, low and in front. Every centimetre is measured in the doorway plane; the
  depth of the chin behind the bar is assumed (8 cm) and the allowance (3.4 cm) scales with it.
- The chin verdict band is ±3 cm for this camera; "at the bar" means exactly that.
- The 3D elbow angles are MediaPipe's estimate and disagree with the image plane; no claim.
- The scale carries about ±5 % (two anchors agree within 0.5 %; the third is explained).
- The temperature map is a model: the joint moments come from the video, the muscle
  forces are shared by an optimisation criterion, the shoulder's depth behind the bar is
  assumed, the fatigue and recovery rates are published per joint region, not per muscle
  (Frey-Law 2012, Looft 2018; the shoulder's rest recovery extrapolated), most lower-body
  volumes are estimates (`MUSCLE-MODEL.md` §5).
- The flush index is eleven points on one person with a moving white balance and no valid
  baseline; the wall control is the only thing keeping it honest.

## Files

- `pullup/out/pullup3-analysis.mp4` — the full set at real speed on the jungle plate (the post).
- `pullup/out/pullup3-dashboard.png` — 13 panels.
- `pullup/out/pullup3-report.html` — the interactive report.
- `pullup/work3/analysis.json`, `redness.json`, `chin_sil.json` — every number.
- `pullup/work3/master.mp4` — the tone-mapped master everything was measured on.
- `pullup/assets/jungle3_plate.jpg`, `pullup/assets/commons/CREDITS.json` — the backdrop and every credit.
- `pullup/PLAN-3.md` — the assessment of sets #1 and #2 and the plan this was built from.
- `references/pullup-science/` — the archive: 01 EMG and anatomy, 02 biomechanics and
  velocity, 03 norms and energy, 04 thermal skin and anatomy assets, 05 ML tooling, 06 Reel
  virality; abstracts, open-access PDFs, CSV tables, `DOWNLOADS.md`.
