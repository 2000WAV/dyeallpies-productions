# Push-up analysis — IMG_6107.MOV (shot 2026-09-08, analysed 2026-09-09/10)

One iPhone 14 standing on its edge on the floor at the head end, lens 13 cm up, looking along the
body 7.8° upward; 116.9 s, 1080×1920 after the rotation tag, 30 fps, 3505 frames, 10-bit HLG
tone-mapped to an SDR master (libplacebo BT.2390). Dennis (188 cm, 79 kg), bare feet, hands
placed under the chest. The first push-up in this format; the pull-up sets' method
(`pullup/REPORT-3.md`) carries over where the camera allows, and this report says where it does
not. The research archive is `references/pushup-science/` (five files, ~90 papers).

## Headline

**30 push-ups, every one past parallel, every one locked out, 29 of 30 with a straight body.**
At the bottom of every rep the shoulder landmarks sit 16 cm above the floor and the nose touches
it (−1 ± 2 cm); the elbow angle there is 69° on average (58–99°), well under the 90° the USMC
standard means by "upper arms parallel to the deck", and the shoulder sits below the elbow (22
cm) on every rep, i.e. past parallel by 14° on average. The arms lock at the top on every rep
(157° by the geometry, 167° by MediaPipe, both within the measurement of a locked arm). The body
line stays at 173–178° for the first twenty reps; the hips sag 1 cm at the start and 7 cm by the
last five, and rep 30 dips to 143° for a moment (the one line that fails, at the end).

The set was not taken to failure but it ended near it: peak push speed 0.84 m/s at rep 8, −26 %
by rep 30; the descents lengthen from 0.6 s to 2–3 s after rep 22, the pauses at the top from 0.5 s
to 3–5 s, and the hips sag. The model's fatigued pool for the pectoralis ends at 75 %, the
triceps' at 43 %.

## What this camera can see, and what it infers

| | |
|---|---|
| **The hips** | Visible in every frame, 1.3 m from the lens. Their landmark width (19.0 cm, measured on Dennis in pull-up set #3's rectified plane) gives their distance; their ray gives their position. Hidden behind the head at the bottom of every rep (the hip dots then land on the skull): those frames are bridged from the shoulders and the toes with the trunk and leg lengths. |
| **The shoulders** | On their rays at the trunk length (58.7 cm) from the hip midpoint where the hips are seen; where the hips are hidden, at the depth that makes their picture width the set's 29.2 cm. Checked two ways: the width comes out the same at the top and the bottom, and at the bottom the shoulders sit 16 cm up while the nose (its own scale, the ear width) touches the floor. |
| **The camera height** | The one free scale: the wrists' rays meet the floor at a distance proportional to it. Chosen (13.0 cm) so the wrist-to-shoulder distance at the locked tops equals the arm (53.1 cm, forearm + upper arm from set #3). The lens of an iPhone 14 standing on its edge is at 12.5 cm; YOLO's ankle row agrees within 16 px. **A tape on the hand spacing (38 cm reconstructed) would replace all three.** |
| **The elbow angle** | The law of cosines over the wrist-to-shoulder distance: no elbow landmark needed (the elbows leave the frame at the bottom). Near lock-out 2 cm of arm is 20°, so lock-out is judged at 140° (94 % of the arm) with MediaPipe's 3D angle printed beside it. |
| **The elbow position** | The circle the two arm lengths allow, placed by the flare read where the elbows are in frame (26 / 35°) and interpolated across the bottoms. It gives the levers, the elbow height and the upper-arm tilt. |
| **The toes** | Hips + 0.95 m along the body line (hip-to-ankle 80.5 cm standing, set #3, plus the foot); YOLO's ankles sit within a degree of the horizon and cannot be ranged from this camera. |
| **Cross-check** | YOLOv8m-pose finds 30 bottoms on its hip track; MediaPipe on 3481 of 3505 frames. |

## The set

| | |
|---|---|
| Hands on the floor | 0.8 – 110.6 s; rep 1 starts at 6.0 s |
| Working set | 106 s, 16.9 reps/min |
| Tempo (mean) | 0.90 s down · 0.30 s at the bottom · 0.79 s up · 1.3 s at the top (0.5 s for the first twenty reps, 3–5 s late) |
| Shoulder height | 53 cm at the top, 16 cm at the bottom: 37 cm of travel |
| Hands | 38 cm apart, 1.3 × the landmark shoulder width; flare ~40° |
| Peak push speed | 0.84 m/s (rep 8); 0.62 m/s at rep 30 |

## Judge's card — USMC PFT push-up standard

The standard (MCO 6100.13A, via two secondary compilations; the .mil pages returned 403 to every
fetch, `03-pushup-norms-and-standards.md` §1): from the front-leaning rest, lower the body as a
unit until the upper arms are at least parallel to the ground, then raise it until the arms are
fully extended, keeping a generally straight body line; a rep that misses any of the three does
not count. For a 21–25-year-old man 40 reps is the minimum and 87 the maximum (70 points; the
push-up is capped, only the pull-up reaches 100).

| line | verdict | number |
|---|---|---|
| upper arms parallel at the bottom | 30 / 30 | elbow 69° (58–99); the shoulder 6 cm below the elbow; nose at the floor |
| arms fully extended at the top | 30 / 30 | 157° by the geometry, 167° by MediaPipe |
| body straight | 29 / 30 | body line 173° mean; hip sag −1 → −7 cm; rep 30 dips to 143° |
| pace | 30 reps in 106 s | the test allows 2 minutes; 40 is the minimum at 21–25 |

## Work, power, energy

| | |
|---|---|
| Hand force | 72 % of body weight at the top, 77 % at the bottom (Eckel et al. 2017, force plate, men); the moment balance on his own geometry says 76 / 82 %. Peak 1.32 BW with the acceleration. |
| Work per rep | 163 J (the centre of mass rises 21 cm) |
| Peak power | 532 W |
| Energy | 0.77 kcal a rep measured by indirect calorimetry (Nakagata, Yamada & Naito 2022) → 23 kcal for the set, 110 kJ of heat with the plank holds. The mechanical-efficiency model gives 0.48 kcal a rep; the measurement wins. |
| Joint moments (per arm) | elbow 34 N·m median through the push (Donkers et al. 1993 measured 23 N·m = 56 % of MVIC in a push-up; here 55 % of the 62 N·m capacity); shoulder 96 N·m median (no measurement exists); wrist 10 N·m against a 14 N·m norm |

## The muscle model

`pushup/PUSHUP-MODEL.md`: the pull-up model's chain on the push-up's levers, validated by the
ordering test (triceps / pec 1.25 against the literature's 0.58–1.17, anterior deltoid / pec 0.91
against 0.89–0.93, serratus / pec 0.82 against 0.77, upper trapezius / pec 0.20 against 0.20), the
capacity test (the one measured push-up joint load, Donkers 1993, reproduced) and the fatigue
test (the pools climb monotonically and clear only after the hands leave the floor). Two
calibrations are disclosed and ranked: the shoulder strength factor (2.0, so a 30-rep set at
−26 % speed is not predicted to fail) and the anterior deltoid's moment arm (3.6 cm, to the EMG
ratio). The colour on the body is the non-resting share of each muscle's pool on set #1's
blue → red scale: a model, not a thermal camera.

## Per rep

| rep | bottom (s) | shoulder (cm) | nose (cm) | elbow L/R (°) | top (°) | body line | sag (cm) | down / bottom / up (s) | peak (m/s) | vs fastest |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6.7 | 16 | 0 | 82 / 58 | 169 | 170 | −1 | 2.2 / 0.3 / 0.8 | 0.72 | −14 % |
| 5 | 15.6 | 17 | −1 | 70 / 65 | 150 | 173 | −1 | 0.6 / 0.3 / 0.6 | 0.74 | −12 % |
| 8 | 21.9 | 17 | −1 | 89 / 79 | 155 | 175 | −1 | 0.6 / 0.3 / 0.5 | 0.84 | 0 |
| 10 | 25.9 | 17 | −1 | 99 / 72 | 149 | 173 | −2 | 1.0 / 0.2 / 0.5 | 0.82 | −2 % |
| 15 | 35.7 | 17 | −2 | 68 / 65 | 168 | 174 | −1 | 0.7 / 0.2 / 0.7 | 0.63 | −25 % |
| 20 | 48.6 | 17 | −1 | 77 / 69 | 156 | 175 | −2 | 0.7 / 0.2 / 0.7 | 0.67 | −20 % |
| 22 | 57.4 | 17 | 0 | 71 / 72 | 151 | 174 | −4 | 1.0 / 0.3 / 1.5 | 0.55 | −35 % |
| 25 | 76.9 | 16 | −2 | 66 / 71 | 151 | 174 | −4 | 2.8 / 0.3 / 0.8 | 0.65 | −23 % |
| 28 | 96.8 | 16 | −2 | 63 / 70 | 152 | 170 | −7 | 1.4 / 0.3 / 1.1 | 0.54 | −36 % |
| 30 | 107.8 | 16 | −2 | 71 / 65 | 182 | 143 | −7 | 2.5 / 0.3 / 2.6 | 0.62 | −26 % |

The full table is `pushup/work/analysis.log`; every number is in `analysis.json`.

## What to change, in order of size

1. **A second phone at hip height, 3 m to the side.** The hand position relative to the
   shoulders (the largest assumption, and the one that sets the shoulder moment), the elbow through
   the bottom, the chest's distance to the floor directly, and the hip sag in its own plane.
2. **A tape on the hand spacing and on a plank of the floor**, before the next set: the scale
   then rests on a measurement instead of three agreeing estimates.
3. The hips sag from rep 25: the core gives before the arms do; the model's core drive keys off
   it (0.22 + 0.10 per cm).
4. The hands are placed under the chest (the shoulders 17–23 cm ahead of the wrists at the top):
   a real style, and it loads the shoulder flexors even at lock-out. Hands under the shoulders
   would unload them at the top and let the pools recover between reps.

## Caveats

- Centimetres are estimates: everything scales with the camera height (rank 1 in the model's
  list). Three independent numbers agree on 12.5–13 cm; a tape would end the question.
- The hips at the bottom are inferred (hidden behind the head); the shoulders and the head are
  measured there. The judge's "chest to the deck" is therefore read off the shoulders (16 cm up)
  and the nose (on the floor), not the sternum.
- The elbow angle near lock-out is ill-conditioned by geometry (2 cm of arm = 20°): "locked"
  means within 6 % of the arm's length, and MediaPipe's own angle is reported beside it.
- The muscle model's shoulder side rests on a calibrated strength factor and assumed moment arms
  (no push-up shoulder moment has been measured); the elbow side reproduces the one measured
  push-up joint load. The colour is a model.
- The energy figure is a measured per-rep constant from another population (Nakagata 2022, 20-
  year-olds), not Dennis's own oxygen uptake.

## Files

`pushup/out/pushup-reel-60.mp4` (the 58 s cut), `pushup/out/pushup-analysis.mp4` (the full set),
their 720p copies, `pushup/out/pushup-dashboard.png`, `pushup/out/pushup-report.html`,
`pushup/PUSHUP-MODEL.md`, `pushup/CAPTION.md`, `pushup/work/analysis.json`, the scripts
`tools/scripts/pushup_recon.py`, `analyze_pushups.py`, `pushup_thermal.py`, `pushup_atlas.py`,
`render_pushup_overlay.py`, `render_pushup_dashboard.py`, `build_pushup_page.py`.
