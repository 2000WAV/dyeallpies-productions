# Pull-up analysis — IMG_6041.MOV (shot 2026-09-05, analysed 2026-09-05, revised the same day)

Source: 55.2 s iPhone clip, 1080×1920 after rotation, 30 fps, 1655 frames. Phone low in
front of a doorway bar; Dennis (188 cm, 79 kg) in shorts, facing the camera.

## How it was measured

- **Tracker:** MediaPipe Pose Landmarker *heavy* (33 landmarks, image + metric 3D world
  coordinates), VIDEO mode, pose found on 1651/1655 frames. A second pass with the
  segmentation mask gave the torso silhouette and a perspective-normalised torso patch.
- **Cross-check:** YOLOv8m-pose (17 COCO keypoints) run independently on every frame.
  Shoulder-midpoint tracks agree with r = 0.998, median gap 7.8 px, and its peak
  detector finds the same 10 reps within 0.3 s of each MediaPipe top.
- **Height signal = shoulder midpoint**, not the chin. At the top of every rep the head
  passes behind the bar and the doorway lintel; MediaPipe still reports face landmarks
  there with visibility 1.0, i.e. hallucinated. YOLO is honest about it: its eye
  confidence drops from 0.95 in the hang to 0.1–0.2 at the top of reps 1–9.
- **Hang onset is detected from load, not from grip.** Hands on the bar is not hanging.
  When the body weight goes onto the bar the shoulder-to-wrist distance grows (arms
  straighten and the shoulders distract) and the shoulder line sinks. Both settle to new
  plateaus; the loading phase is the ramp between the standing plateau and the loaded one.
- **Joint angles are 3D** (world landmarks). The 2D elbow angle collapses to ~10° at the
  top because the forearm points straight at the camera.
- **Centimetre scale is anchored on the arm.** With the stature known, the straight arm
  at the loaded hang (shoulder joint to wrist = 0.332 × 188 cm = 62.4 cm, Drillis &
  Contini) gives 1014 px/m. It is the one segment aligned with the motion and at the
  depth of the motion. The two alternatives (trunk length at the bottom, MediaPipe's
  own world fit) give ~1320–1340 px/m, but the trunk sits lower, closer to the camera
  and is foreshortened from below, so they under-read the shoulder travel. Hip-level
  sway uses the trunk scale; the standing neck length uses the local world fit.
- **Chin-at-bar rule:** shoulder-to-chin length measured while standing at the start
  (13.1 cm) plus a 3 cm perspective allowance — the chin hangs 15–20 cm behind the bar
  plane, so a chin *level* with the bar projects a few cm *below* the bar line. The
  head vanishing behind the lintel on 8 of 10 reps is the ground truth for the rule.

## Timeline

| | |
|---|---|
| Hands on the bar, standing | 4.8 – 9.8 s (5.0 s) |
| Loading: weight goes onto the bar | 9.8 – 11.6 s (1.8 s). Arms lengthen 8.6 %, shoulders sink 6.6 cm |
| Loaded dead hang before rep 1 | 1.1 s (first pull at 12.7 s) |
| Working set | 12.7 – 50.2 s: 37.5 s, 16 reps/min |
| Off the bar | 51.5 s |

The earlier version of this report called 4.8–12.7 s a "7.9 s dead hang". That was
wrong: the feet were on the floor until ~9.8 s. The moment Dennis felt his left arm
stretch (~12 s) is exactly where the arm-length signal reaches its loaded plateau.

## The set

| | |
|---|---|
| Reps | **10** (both trackers) |
| Chin vs bar | **4 above** (reps 1–4, +1.4 to +2.5 cm), **5 at the bar** (reps 5–9, within ±1 cm), **1 short** (rep 10, −3.3 cm). With ±3 cm of uncertainty, "at the bar" is the honest label for the middle five |
| Full lock-out at the bottom | 10 of 10 (3D elbow 161–165°) |
| Range of motion | 56 cm of shoulder travel per rep (53–58); alternative calibrations say 42–43 cm |
| Tempo | 1.5 s up / 0.3 s hold / 1.4 s down on average; up-phase slows from 1.2 s to 2.0 s |
| Peak pull speed | 0.93 m/s best (reps 3–4) → 0.50 m/s last, a 46 % velocity loss |
| Hip sway | 3–5 cm per rep, 4.3 cm average — strict, no kip |
| Lateral bend | shoulder line vs hip line moves through 13° per rep, −3° at the top |
| Elbow at the top | left 65°, right 81° on average (3D estimate). The camera is not square to the body, so part of this gap is viewing angle; treat it as "probably some asymmetry", not 16° |
| Knees | tucked to ~70° throughout (legs crossed behind); hip angle 143° at the top |
| Grip | 40 cm, 1.37 × shoulder-joint width |
| Mean efficiency | **92 / 100** — nine A reps, one B |

## Work, power and a rough energy cost (188 cm, 79 kg)

Lifted mass ≈ 75.5 kg (body mass minus hands and forearms, which stay at the bar).

| | |
|---|---|
| Work per rep | 414 J (75.5 kg × g × 0.56 m) — 4.1 kJ for the set |
| Mean pull power | 299 W on rep 1, 350 W best (rep 3), 207 W on rep 10 |
| Peak pull power | ≈ 850 W |
| Peak force on the bar | ≈ 1.18 × body weight at the start of the fastest pull |
| Energy, rough | ≈ 0.9 kcal per rep, **≈ 9 kcal for the set** (plus 0.1 kcal of hang) |
| Equivalent weighted 1RM | ≈ +25 kg extra load for one rep (Epley on the lifted mass) |
| BMI | 22.4 |

**Energy model** (deliberately rough): concentric work ÷ 22 % muscle efficiency, the
lowering at 35 % of that, plus an isometric "holding on" cost of 3.5 METs (0.08 kcal/s)
for every second between the start of the pull and the start of the next. Nothing in
the model is fitted to this set. The mechanical part is the same every rep; what grows
is the time under tension, so the last reps cost ~10 % more than the first ones.

**Difficulty per rep** comes from the force–velocity relationship: same load, slower
pull = closer to maximum effort. Effort multiplier = fastest rep's mean pull speed ÷ this
rep's. Reps in reserve (RIR) are estimated from the peak-velocity loss, roughly one rep
per 9 % lost.

## Per rep

| rep | top (s) | chin vs bar (cm) | elbow top L/R | up / hold / down (s) | rest (s) | peak v (m/s) | work (J) | mean power (W) | kcal | effort | RIR | score |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 14.3 | +1.7 | 59 / 81 | 1.40 / 0.23 / 1.33 | 0.4 | 0.82 | 418 | 299 | 0.89 | ×1.17 | 4 | 93 A |
| 2 | 17.7 | +1.7 | 66 / 81 | 1.50 / 0.20 / 1.33 | 0.4 | 0.90 | 418 | 279 | 0.89 | ×1.25 | 5 | 95 A |
| 3 | 20.8 | +2.5 | 58 / 82 | 1.20 / 0.37 / 1.57 | 0.4 | 0.93 | 419 | 350 | 0.90 | ×1.00 | 5 | 97 A |
| 4 | 24.4 | +1.4 | 64 / 81 | 1.27 / 0.37 / 1.27 | 0.8 | 0.93 | 417 | 329 | 0.91 | ×1.06 | 5 | 94 A |
| 5 | 28.5 | +0.1 | 74 / 84 | 1.50 / 0.27 / 1.23 | 0.4 | 0.83 | 428 | 285 | 0.90 | ×1.22 | 4 | 92 A |
| 6 | 32.0 | +0.5 | 68 / 80 | 1.43 / 0.50 / 1.43 | 0.5 | 0.89 | 414 | 289 | 0.92 | ×1.21 | 4 | 97 A |
| 7 | 35.9 | +0.7 | 63 / 76 | 1.73 / 0.27 / 1.40 | 0.5 | 0.72 | 411 | 237 | 0.92 | ×1.48 | 2 | 93 A |
| 8 | 39.7 | +0.4 | 71 / 80 | 1.63 / 0.30 / 1.40 | 0.5 | 0.63 | 412 | 252 | 0.91 | ×1.39 | 1 | 92 A |
| 9 | 43.8 | −0.7 | 67 / 81 | 1.73 / 0.33 / 1.53 | 1.4 | 0.54 | 393 | 227 | 0.98 | ×1.54 | 0 | 90 A |
| 10 | 49.1 | −3.3 | 57 / 81 | 2.00 / 0.27 / 1.13 | 0.0 | 0.50 | 414 | 207 | 0.88 | ×1.69 | 0 | 78 B |

Chin figures include the 3 cm perspective allowance. Rest = bottom of this rep to the
start of the next pull.

### Efficiency score (per rep, max 100)

| component | max | rule |
|---|---|---|
| range of motion | 25 | full if chin at/over bar, −2.5 per cm short |
| eccentric control | 20 | full at a 1.5 s lowering, linear below |
| lock-out | 15 | full at 155°+ elbow at the bottom, 0 at 120° |
| low sway | 15 | full at ≤4 cm hip sway, 0 at 20 cm |
| pull speed | 15 | peak concentric speed relative to the best rep of the set |
| L/R symmetry | 10 | full at ≤5° mean elbow-angle gap, 0 at 25° |

## Core, chest and lats — what one front camera can and cannot see

Figure: `pullup/out/pullup-torso.png`.

- **Trunk control is good.** The shoulder line and hip line stay within 13° of each
  other through a rep and the hips move 4 cm sideways. Nothing here suggests a
  one-sided pull, even though the elbows are asymmetric.
- **Hip angle at the top is 143°** with the knees tucked to 70°: a mild hollow-body
  position, legs held behind, which is the right shape for a strict pull-up.
- **Rotation:** the 3D estimate of shoulder-line rotation about the vertical axis swings
  15–27° per rep. That coordinate is MediaPipe's weakest; treat it as "some rotation",
  not a measurement.
- **Lats from the front:** the silhouette width just under the armpits, relative to the
  waist (the V-taper), is 1.15 in the hang and 1.10 in the early pull, i.e. no
  measurable lat flare is visible from this angle; the profile is dominated by
  perspective and by the upper arms entering the silhouette as the elbows come down.
  A side or rear camera is what lats need.
- **Abs / chest shading:** the abdominal band's edge-contrast-to-brightness index goes
  11 (hang) → 16 (early pull) → 28 (mid pull) → 51 (top) → 24 (lowering). The rise is
  real in the pictures — the phase-averaged patches show the ribcage and oblique lines
  come out at the top — but the torso also moves up into the lintel's shadow (brightness
  108 → 67), and a darker, side-lit surface has higher relative contrast whether or not
  the muscle is working. Read it as "the lighting shows the bracing at the top", not as
  a measurement of it. The waist width does not change at the start of the pull (−1 %).
- **Chest:** the pectoral region shows no measurable change across phases; pull-ups
  load the pecs very little and the front camera adds nothing here.

## The "muscle heat" overlay (pullup-analysis-heat.mp4)

The second video export paints a red-to-blue heat map on the body from the neck to the
hips. The camera cannot see contraction, so the map is built from two things that are
known: **where a pull-up works, from surface-EMG studies**, and **how hard each rep was,
from the measured pull**.

- Activation values are Youdas et al. (2010), average %MVIC over the rep, pull-up end of
  the ranges because the grip is pronated: latissimus dorsi 124, biceps brachii 78,
  infraspinatus 75, trapezius 52, pectoralis major 44, external oblique 33. Dickie et al.
  (2017) supplies the phase ordering: concentric activation of biceps, brachioradialis
  and pectoralis is significantly higher than eccentric, so the map runs pull 1.0 >
  top hold 0.85 > lowering 0.65 > hang 0.35, and the pull is scaled by the measured
  speed of that rep. Full citations, numbers and the region-to-muscle table are in
  `references/pullup-emg/README.md`.
- Regions are mapped **on the silhouette itself**: every painted pixel is assigned to the
  nearest skeleton segment (torso axis, upper arms, forearms), and torso pixels are then
  banded by how far out toward the outline they sit — lats are the outer band from the
  armpit to the waist, obliques the outer band lower down, pecs the central upper chest,
  trapezius just under the shoulder line, deltoid caps around the shoulder points. So the
  map follows your actual outline rather than fixed-width blobs. Erector spinae is on the
  back and not drawn. The rectus abdominis was not measured in either study, so the
  abdomen only carries the image-evidence term.
- A quarter of the colour comes from the image itself: local skin contrast, where the
  light shows lines, kept away from the silhouette edge.
- The face and the legs stay natural; the body is covered at ~82 % opacity with the
  frame's own shading kept, so the shape reads but the skin does not.
- **The outline** comes from a dedicated matting pass, not the pose model's coarse mask:
  Robust Video Matting (Lin et al., WACV 2022) gives a full-resolution, temporally
  consistent alpha of the person, and MediaPipe's multiclass selfie segmenter labels
  body-skin separately from face-skin, hair and clothes. The paint region is
  alpha × body-skin, so the head, hair, shorts and background are excluded by
  construction and the neck and upper chest are covered.

- **The whole body warms up through the set.** A base level rises with the measured
  peak-velocity loss of the latest completed rep (65 % weight) and with the share of the
  set's energy already spent (35 %), and never falls within the set. The justification is
  Sánchez-Medina & González-Badillo (2011): within-set velocity loss correlates with
  post-exercise lactate at r = 0.93–0.97, i.e. it is a valid proxy for accumulated
  metabolic fatigue, and that fatigue does not clear in the half-second rests between
  reps. Muscle temperature itself also climbs by about a degree over minutes of work
  (Saltin, Gagge & Stolwijk 1968), but the reel's colour is fatigue, not temperature.
  The metrics box shows the measured number behind it: FATIGUE = speed loss in %.
- **Opacity** is 96 % with only a hint of the frame's shading, so the colour reads as a
  solid surface rather than a tint.
- **Backdrop.** The kitchen is replaced by a jungle plate: a 9:16 crop of "Palawan,
  Tropical jungle rainforest" by Vyacheslav Argenberg, CC BY 4.0, via Wikimedia Commons
  (`pullup/assets/ATTRIBUTION.md`; the post must carry the credit line). The person is
  composited with the RVM alpha; the bar is kept from the real footage by a static dark
  mask around the bar row, so the hands grip something. The plate has a 6 % push-in over
  the clip.
- **Dropped-pose frames.** MediaPipe returned no pose on four frames (14.90, 16.73,
  21.83, 23.80 s); the first heat export skipped the paint there and the bare body
  flashed for one frame each. The renderer now holds the last good landmarks, and
  `tools/scripts/check_flicker.py` gates every export: it measures frame-to-frame change
  inside the person region and in the background and reports single-frame spikes.
- **Look pass** (`tools/scripts/pullup_look.py`), all driven by the same matte: with the
  jungle plate the background keeps its colour and is only softened and darkened a
  little; with the real room it is desaturated, darkened and softened (a shallow depth-of-field illusion that
  hides the kitchen), the subject is unsharp-masked with a little added contrast, a thin
  rim glow in the current heat colour separates the body from the wall, fine monochrome
  grain covers compression artefacts, and a soft vignette keeps the eye centred. None of
  it touches the measurements; it is purely presentation.

It is a literature prior on your body, warmed by your effort and by your accumulated
fatigue, and it is labelled that way in the video and here.

## What it says about the pull-ups

1. **Strict and full-range.** Four reps clearly above the bar, five at the bar within a
   centimetre, one short; a full hang at the bottom every time and ~4 cm of hip movement.
   Nothing is kipped. The video says exactly that per rep ("chin above bar" / "chin at
   bar" / "chin N cm short") rather than a letter grade, because the efficiency letter
   was reading as a form verdict it is not.
2. **The set ended on velocity, not on form.** Peak pull speed fell 46 % from rep 3 to
   rep 10, mean power from 350 W to 207 W, and the up-phase stretched from 1.2 s to
   2.0 s. Velocity-based guidelines treat a 20–30 % loss as "stop the set for quality";
   that point was rep 7 (RIR 2). Reps 9 and 10 were grinders at ×1.5–1.7 the effort of
   the best rep for the same 414 J of work, and rep 10 is the only one clearly short.
3. **Lowering is the faster half** (1.4 s vs 1.5 s). A deliberate 2–3 s eccentric is the
   cheapest upgrade in this set; eccentric control is the one score component never at
   full marks.
4. **A left/right difference shows up on every rep — but the camera is off-axis.** The
   3D elbow estimate reads ~65° left and ~81° right at the top, consistently. The phone
   was not square to the body (the shoulder line sits at a slight yaw to the lens), and
   MediaPipe's 3D angles are less reliable for the arm nearer the camera, so part of the
   gap is perspective. Worth a mirror check or a straight-on camera before calling it
   an asymmetry; the video now shows a single elbow value to avoid over-reading it.
5. **The standing time on the bar is free.** 5 s of hands-on-bar standing plus a 1.8 s
   load-in costs nothing, but it is not "hang time" and the earlier report was wrong to
   count it.

## Caveats

- Single low camera in front. All heights are image-plane measurements corrected by a
  fixed perspective allowance; the chin verdicts on reps 9 and 10 are the least certain
  numbers here.
- **The centimetre scale carries ±10–15 % systematic uncertainty**, and every m/s, J,
  W and kcal figure inherits it. Three defensible calibrations put the range of motion
  between 42 and 56 cm; the arm-anchored 56 cm is the most direct and is used throughout.
- The kcal numbers are a model with textbook constants, not a measurement. They are
  good for "about 1 kcal per rep, about 9 for the set", nothing finer.
- Leg landmarks leave the frame at the bottom of the hang; knee and hip angles come from
  MediaPipe's extrapolation there and are only trusted where both knees are visible.
- Lighting-based torso indices are exploratory; see the core section.

## Files

- `pullup/out/pullup-analysis.mp4` — the Reels-format overlay video (1080×1920, NVENC,
  original audio, 3 s frozen summary at the end).
- `pullup/out/pullup-dashboard.png` — the ten-panel dashboard.
- `pullup/out/pullup-torso.png` — core / chest / lats figure.
- `pullup/out/pullup-report.html` — interactive report (also published as an Artifact).
- `pullup/work/analysis.json`, `torso.json` — every per-frame signal and per-rep number.
- `pullup/work/pose_mp.npz`, `pose_yolo.npz`, `torso.npz` — raw tracks and masks.
