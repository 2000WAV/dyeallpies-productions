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
| **Anatomy** | 14 painted regions from a landmark-warped atlas with fibre directions, boundaries and belly shading (`pullup_atlas3.py`), 23 muscles in the heat budget (`pullup_thermal3.py`): serratus anterior, upper trapezius, middle deltoid, triceps and forearm extensors added from 01-emg-and-anatomy.md; the lat share shifts toward the trapezius at the top (Park & Yoo 2013); core heat keys off measured hip motion (Dinunzio 2018). |

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

## Modelled muscle temperature

Same heat budget as set #2, per muscle: C dT/dt = share × P_heat − k(t) dT, 3.6 kJ/kg/K,
removal ramping with a 90 s time constant to 42 W/K/kg (González-Alonso 2000). 23 muscles;
the painted ones and their end-of-set rise:

| muscle | %MVIC | ΔT at the end |
|---|---|---|
| latissimus dorsi | 124 | **+1.38 °C** |
| brachioradialis / forearm flexors (grip) | 62 / 60 | +1.36 / +1.34 °C |
| forearm extensors (estimate) | 35 | +1.06 °C |
| biceps, brachialis | 78 | +0.87 °C |
| infraspinatus | 75 | +0.83 °C |
| upper trapezius (Tucker 2011) | 62 | +0.69 °C |
| posterior / middle deltoid | 60 / 45 | +0.67 / +0.50 °C |
| trapezius, middle and lower | 52 | +0.58 °C |
| pectoralis major | 44 | +0.49 °C |
| external oblique | 33 | +0.37 °C |
| serratus anterior (Tucker 2011) | 26 | +0.29 °C |
| rectus abdominis | 20 | +0.22 °C |
| triceps (estimate) | 15 | +0.17 °C |
| hip flexors, quadriceps, calves | 18 / 8 / 4 | +0.17 / +0.08 / +0.04 °C |

The colour is on an ironbow scale, 0 to +1.5 °C, with the muscle names shown once each the
first time they pass +0.3 °C. Brightness pulses with modelled activation. The legend says it
on every frame: a model, not a thermal camera.

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
- The temperature map is a model on a literature prior: five of 23 activations are
  estimates, most lower-body volumes are estimates.
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
