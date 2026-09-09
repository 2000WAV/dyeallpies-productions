# Pull-up video #3 (IMG_6108.MOV) — critical assessment of #1 and #2, and the plan

Written by Fable, 2026-09-08 (evening). Dennis's brief: set #1 passed 140k views; do the next
one seriously — more research, more anatomy in the visualisation, more heat, more calculation,
a jungle with high-definition monkeys, everything downloaded and documented ("the best
documented pull-up video"). Same treatment for the push-ups (`sources/IMG_6107.MOV`) afterwards.

Research archive built tonight: `references/pullup-science/` (01 EMG and anatomy, 02
biomechanics and velocity, 03 norms and energy, 04 thermal skin and anatomy assets, 05 ML
tooling, 06 Reel virality; `abstracts/`, `papers/`, `data/`, `DOWNLOADS.md`). Everything below
that changes a number cites one of those files.

## 1. What the two previous videos did right and wrong

### Set #1 (2026-09-05, the 140k one)

Right: the full 55 s set at real speed with a rising counter — the viewer watches to see the
count; a heat map on the body that makes the effort visible; rep cards with numbers; the jungle
backdrop; the "by Fable and DyeAllPies" credit. It was watchable because it did not cut.

Wrong, in order of how much it matters:
1. **The heat was fatigue dressed as heat.** The colour was a velocity-loss tint labelled heat.
   Set #2 fixed the physics (°C from a heat budget) but not the look.
2. **Chin verdicts were inferred**, with a fixed 3 cm "perspective allowance" that was really a
   guess about how far the chin hangs behind the bar plane. This video measures the allowance
   from the camera geometry instead (see 3.2).
3. **The 3D elbow asymmetry (65° vs 81°)** was published in the caption from MediaPipe's world
   coordinates, which set #2 showed disagree with the image plane. It was probably wrong.
4. Scale carried ±10–15 % from a floor camera with no calibration object.

### Set #2 (2026-09-07, the 19.7 s cut, "none of them are legal")

Right: the de-roll, the bar as a fitted line, the judge's card against a named standard, the
thermal model in °C, the measured chest flush (r = 0.83 with the model), the asymmetry suite
that refused to claim what the image plane could not confirm, the cold open on the failure.

Wrong, seen frame by frame tonight (`pullup/out/pullup2-reel.mp4`):
1. **The body reads as a blue mannequin, not as muscles.** One flat colour over the whole
   torso, arms and legs, hard edges, the skeleton drawn on top hiding the body. There is no
   anatomy in it: no lat outline, no biceps, no fibre direction, no boundaries. The scale runs
   0 → +2.5 °C, so for most of the set everything is blue and the map only "happens" in the
   last reps. That is the single biggest thing to fix, and it is what Dennis is asking for.
2. **Too much text for 20 s.** Six-row metrics box at ~30 px, grid labels at ~18 px, a 14-line
   judge's card held for 3.3 s. On a phone nothing below ~44 px is read (the format notes),
   and a card that dense needs 8–10 s. The format that got views was the long one.
3. **The cut.** ×6 through reps 2–11 threw away the thing that worked in #1: watching the reps
   happen. Keep the full-length version as the post; a short cut is a second export, not the
   main one.
4. **The jungle.** Low-resolution plate with a grey haze, monkeys as small blurry cut-outs,
   a red rim glow around the body that reads as a cut-out. The bar floats as a white dash.
5. The 10-bit HLG footage was decoded flat (no tone mapping), which is why the skin looked
   grey; the master for this set is tone-mapped on the GPU (libplacebo, bt.2390) and looks
   like the phone's own playback.
6. The 3.3 s summary card mixed 14 numbers; the two that matter (11 reps, 0 with the chin over
   the bar) were the same size as "chest flush 18 → 44".

## 2. The new clip (IMG_6108.MOV, 63.6 s, iPhone 14, 30 fps, HLG)

Floor camera 2.8 m from the doorway, looking up 6.5°, almost no roll (0.3°), yaw 5.8°. Whole
body in frame including the feet; **the whole head disappears behind the lintel at the top of
every rep**, so chin-over-bar is visually unambiguous and is witnessed by occlusion rather
than measured by a landmark model. A black cat sits in the bottom centre of the frame for the
whole set. 11 reps, 15.6 reps/min, a 3.9 s dead hang before the first pull, 42 s working set.

First-pass numbers (`pullup/work3/analysis.log`, `analyze_pullups3.py`): in-plane ROM 55–58 cm,
lock-outs 11/11 (160–167° 3D), hip sway 5–7 cm, top holds 0.6–0.9 s, lowering 0.9–1.3 s,
peak speed rep 5 0.91 m/s → rep 11 0.43 m/s (−53 % vs the fastest, −40 % vs rep 1), shoulder
line −3° at every top with the wrist line at −1° as the control, right ear-to-shoulder 2.3 cm
longer than the left even standing. Head hidden behind the lintel for 0.3–0.8 s on reps 1–8;
reps 9–11 need the silhouette witness (YOLO's nose confidence stays high there while the
frames show the head gone), which is `pullup_chin_silhouette.py`.

## 3. What is new in the method (each item is a rule for the skill once it works)

### 3.1 Measure in a rectified plane, render on the original frame
Vertical and horizontal vanishing points from LSD segments (RANSAC, 100 and 149 inliers), f
from their orthogonality (1950 px, consistent with an iPhone 14 main camera in stabilised
video), H = K Rᵀ K⁻¹, then a residual rotation so the fitted bar is exactly level (the bar is
the judge's line; the lintel tilts the same way, so the residual was the model, not the bar).
Every landmark goes through H before it is measured; the render never does. Scale from the
standing stature under the bar (708 px/m) and confirmed by the shoulder-to-bar distance at the
dead hang: 62.7 cm, against 0.332 × 188 = 62.4 cm from the anthropometric tables.

### 3.2 Depth is the allowance, and it is computed, not assumed
Elevation angle from the camera to the bar 23.4°, so a point d cm behind the bar plane projects
0.43 d cm lower than it is. In-plane shoulder height at the top (−17 cm) and the chin bound from
the lintel (≥ +13.5 cm) together imply the shoulders sit ~25–30 cm behind the bar plane at the
top, which is what a pull-up looks like from the side. Every in-plane number is labelled as such
and the true vertical ROM is quoted as a range (in-plane + 0.43 × depth change).

### 3.3 Chin witness, three layers
1. Silhouette (RVM alpha): neck-wide under the lintel → head fully above it → chin ≥ 13.5 cm
   above the bar at any depth. Where the head is partly visible, the jaw flare in the width
   profile is the chin, measured in the rectified plane.
2. YOLO nose confidence collapsing (works on reps 1–8, fails 9–11: hallucinated).
3. Face-axis chin from MediaPipe, only while the face is really seen.
Time with the chin above the bar per rep is a new metric (the pause at the top, measured).

### 3.4 Velocity, effort and RIR from the pull-up literature (02)
Reference = rep 1 (Beckham 2018), fastest rep beside it; velocity loss against the 25 % / 50 %
landmarks Sánchez-Moreno 2020 used for pull-up training; RIR reported as an ESTIMATE range from
those landmarks, never an integer fact. Rep 1 here was a slow, deliberate start, so both
references are printed.

### 3.5 Anatomy (01) and heat (04)
Atlas v3 adds serratus anterior (Tucker 2011: 25.5 %MVIC), upper trapezius (61.6 %MVIC), middle
deltoid (ESTIMATE), forearm extensors; the lat/lower-trap share shifts toward the trapezius at
the top of the rep (Park & Yoo 2013); core heat keys off measured hip motion (Dinunzio 2018),
not pull speed; Snarr 2017 at 1.5 × biacromial pronated grip corroborates the Youdas prior.
Each muscle is drawn with fibre direction (striations along the fibre line from the anatomy
plates), a boundary, shading from the frame's own luminance, colour = modelled temperature on
an ironbow scale that reads as thermal at a glance, brightness = activation. Muscle names appear
once, when a muscle first passes 1 °C. A skin layer (Pennes bioheat through fat and skin, from
04) gives the "what an infrared camera would see" view, shown once as a contrast.

### 3.6 Norms (03)
The judge's card places the set on the USMC PFT table and on adult-male percentiles, with the
allometric (body-mass) adjustment named.

## 4. Deliverables

- `pullup/out/pullup3-analysis.mp4` — the full set at real speed (the post), ≤ 60 s including
  the intro and the card, with the reps at 1:1 and the dead hang trimmed to 1.5 s.
- `pullup/out/pullup3-reel-30.mp4` — a ≤ 30 s cut for Reels/Shorts, by frame schedule.
- Dashboard, HTML report (Artifact), `pullup/REPORT-3.md`, `pullup/CAPTION-3.md` with every
  credit line (`pullup/assets/commons/CREDITS.json`, 17 files: CC BY 2.0/3.0/4.0 and CC0).
- Skill update + third worked example; public mirror copy; handoff.

## 5. Open questions for Dennis (none blocks the work; assumptions in brackets)

1. Doorway opening width, bar height above the floor and the bar's length between the mounts,
   with a tape measure. One known length in the bar plane pins the scale to <2 % instead of the
   stature's ~5 %. [assume the stature anchor]
2. Keep the cat? It sits still for the whole set and can be matted in as the judge at the
   bottom of the jungle. [yes]
3. Music, or room tone only. [room tone under the reps, silent card]
4. Height and mass still 188 cm / 79 kg? [yes]
5. Next shoot: a second phone from the side at hip height settles the elbow asymmetry and the
   depth question for good; and a 1 m stick held at the bar before the set.
