# Pull-up analysis

A phone clip of one pull-up set, camera static, whole torso and arms in frame, becomes a
rep-counted, biomechanics-annotated Reel plus a dashboard, a written report and an
interactive page. First set analysed 2026-09-05: 10 reps, mean efficiency 92/100.

- The worked example, with the timeline of the session and every mistake on the way:
  [pullups-2026-09-05.md](pullups-2026-09-05.md)
- The written report (method, timeline, per-rep table, physics, core section, caveats):
  [REPORT.md](REPORT.md)
- The posted caption: [CAPTION.md](CAPTION.md)
- The dashboard: [pullup-dashboard.png](pullup-dashboard.png)
- The EMG literature behind the muscle heat map: [references/pullup-emg/](../../references/pullup-emg/README.md)
- The backdrop plate and its required credit line: [assets/ATTRIBUTION.md](assets/ATTRIBUTION.md)

## Outputs

1. `pullup-analysis.mp4` (plain) and `pullup-analysis-heat.mp4` (muscle heat on a
   matted body against a replaced backdrop): full-bleed 1080x1920 Reels exports with the
   tracked skeleton, rep counter, phase pill (DEAD HANG / PULL / HOLD / LOWER / HANG),
   live 3D elbow angle, speed and height %, a height gauge with a "chin at bar" tick, a
   progressive shoulder-height chart with verdict chips, a rep card after every rep and
   a 3 s frozen set summary.
2. `pullup-dashboard.png`: 8-panel figure.
3. `pullup-torso.png`: core / chest / lats figure from the segmentation pass (not
   published here; it shows the bare torso).
4. `pullup-report.html`: interactive report built from the analysis JSON.
5. `REPORT.md` and `CAPTION.md`.

**Ask for height and body mass up front.** Height calibrates the centimetre scale (arm
length = 0.332 × stature, Drillis & Contini); mass turns the kinematics into work, power,
force, a rough kcal per rep and an effort / reps-in-reserve estimate.

## Pipeline

All CPU, no CUDA torch. For a 55 s clip the three heavy passes take about 3.5 min
(MediaPipe heavy), 7 min (YOLO) and 12 min (matte); run them detached in parallel.

```bash
ffprobe -v error -show_entries stream=width,height,r_frame_rate,nb_frames:stream_side_data=rotation IMG.MOV
mkdir -p pullup/work pullup/out
# 1. trackers
python tools/scripts/extract_pose_mp.py IMG.MOV tools/models/pose_landmarker_heavy.task pullup/work/pose_mp.npz
python tools/scripts/extract_pose_yolo.py IMG.MOV tools/models/yolov8m-pose.pt pullup/work/pose_yolo.npz 640
python tools/scripts/extract_torso.py IMG.MOV tools/models/pose_landmarker_heavy.task pullup/work/torso.npz
# 2. analysis (prints the per-rep table; iterate here until the count and the hang onset are right)
python tools/scripts/analyze_pullups.py IMG.MOV pullup/work/pose_mp.npz pullup/work/analysis.json pullup/work/pose_yolo.npz height=1.88 mass=79
# 3. renders
python tools/scripts/render_pullup_overlay.py IMG.MOV pullup/work/pose_mp.npz pullup/work/analysis.json pullup/out/pullup-analysis.mp4 3.0
python tools/scripts/extract_matte.py IMG.MOV pullup/work/matte3.npy 2      # RVM alpha + clothes + head channels, 2.6 GB memmap
#    preview a handful of frames first; the full heat render takes ~12 min
python tools/scripts/render_pullup_overlay.py IMG.MOV pullup/work/pose_mp.npz pullup/work/analysis.json pullup/out/pullup-analysis-heat.mp4 3.0 heat=pullup/work/matte3.npy look=1 bg=formats/pullup-analysis/assets/jungle_plate.jpg preview=60,447,780,1400,1700
python tools/scripts/render_pullup_overlay.py IMG.MOV pullup/work/pose_mp.npz pullup/work/analysis.json pullup/out/pullup-analysis-heat.mp4 3.0 heat=pullup/work/matte3.npy look=1 bg=formats/pullup-analysis/assets/jungle_plate.jpg
ffmpeg -v error -i pullup/out/pullup-analysis-heat.mp4 -f null -
python tools/scripts/check_flicker.py pullup/out/pullup-analysis-heat.mp4 pullup/work/matte3.npy pullup/work/sheet/flicker_report.png
#    the only acceptable flicker event is the intro-card swap at the grab frame
python tools/scripts/render_pullup_dashboard.py pullup/work/analysis.json pullup/out/pullup-dashboard.png
python tools/scripts/render_pullup_torso.py pullup/work/analysis.json pullup/work/torso.npz pullup/out/pullup-torso.png pullup/work/torso.json
python tools/scripts/build_pullup_page.py pullup/work/analysis.json pullup/out/pullup-report.html pullup/work/torso.json
```

| script | does |
|---|---|
| `extract_pose_mp.py` | MediaPipe Pose Landmarker heavy, VIDEO mode: 33 image landmarks + metric 3D world landmarks per frame |
| `extract_pose_yolo.py` | YOLOv8m-pose, 17 COCO keypoints with confidences: the independent count and the occlusion witness |
| `extract_torso.py` | the pose model's segmentation mask, torso silhouette and a perspective-normalised torso patch per frame |
| `extract_matte.py` | Robust Video Matting alpha × MediaPipe multiclass segmentation, stored as alpha / clothes / head channels |
| `analyze_pullups.py` | hang onset, rep detection, phases, 3D joint angles, cm calibration, chin verdicts, physics, efficiency score → `analysis.json` |
| `pullup_heat.py` | the EMG-informed muscle map on the silhouette, warmed by measured effort and the fatigue base |
| `pullup_look.py` | matte-driven look pass: background treatment, subject unsharp, rim glow, grain, vignette |
| `render_pullup_overlay.py` | the Reels export: skeleton, UI, cards, heat, look, backdrop; raw frames piped to NVENC |
| `check_flicker.py` | single-frame spikes of frame-to-frame change inside the person region and in a UI-free background window |
| `render_pullup_dashboard.py`, `render_pullup_torso.py`, `build_pullup_page.py` | the dashboard, the torso figure, the interactive page |

Models: `pose_landmarker_heavy.task` (Google storage bucket,
`mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/`),
`selfie_multiclass_256x256.tflite` (MediaPipe image segmenter model card), `yolov8m-pose.pt`
(ultralytics assets release v8.3.0), Robust Video Matting mobilenetv3 via
`torch.hub PeterL1n/RobustVideoMatting` (Lin et al. 2022). OpenCV applies the MOV rotation
tag itself, so frames arrive upright.

## Efficiency score (per rep, /100)

ROM 25 (chin at or over the bar, −2.5 per cm short) · eccentric control 20 (full at
1.5 s) · lock-out 15 (155°+ full, 0 at 120°) · low sway 15 (≤ 4 cm hip sway full, 0 at
20 cm) · pull speed 15 (peak concentric velocity ÷ the best rep of the set) · L/R
symmetry 10 (≤ 5° mean elbow gap full, 0 at 25°). A ≥ 85, B ≥ 70, C ≥ 55. The letter is
a footnote; the rep card and the chart chips carry the chin verdict.

## Rules that came out of the first set

**Counting and measuring**

- **Count and measure height from the shoulder midpoint, never the face or chin.** At the
  top of a rep the head passes behind the bar and the door lintel. MediaPipe keeps
  emitting face landmarks there with visibility 1.0, hallucinated, and a chin-based
  counter lost the first half of the set.
- **Use YOLO as the occlusion witness.** Its keypoint confidence really drops when a
  part is hidden (eyes 0.95 in the hang → 0.1–0.2 at the top). "Head hidden behind the
  lintel" is the ground truth for chin-over-bar.
- **Joint angles from the 3D world landmarks.** With the phone on the floor the forearm
  points at the camera at the top and the 2D elbow angle collapses to ~10°; 3D gives a
  sane 60–85°. Bottom lock-out reads 160–165° in 3D; use ≥ 150° as the test.
- **Merge hands-above-shoulders runs with gaps under 0.5 s** before picking the hang
  window; the mask flickers at rep tops where wrists and shoulders are level.
- **Chin rule = personal shoulder-to-chin length** (measured standing in the first 2 s)
  **plus a 3 cm perspective allowance.** The chin hangs 15–20 cm behind the bar plane; from
  a floor camera a chin level with the bar projects a few cm below the bar line.
- **The phase walker walks forward** from the bottom and from the top, never backward
  from the next bottom (velocity there is ~0 and the walk exits immediately, giving zero
  rest times). Rest = next rep's pull start − this rep's lowering end.
- **Hands on the bar is not hanging.** Five seconds of standing while holding the bar was
  first called a dead hang. Detect load onset from the shoulder-to-wrist distance (arms
  lengthen ~9 % when the weight goes on) and the shoulder line sinking (~6 cm): standing
  plateau, loading ramp, loaded plateau. Reference the standing plateau after the reach
  settles, never the first second after the grab.
- Bar row = darkest horizontal band in the top half of frame 0 over the middle 60 % of
  the width, sanity-checked against the median wrist line.

**Scale and what a front camera cannot see**

- **Scale from the arm, not the trunk.** From a low front camera the trunk is closer and
  foreshortened; trunk- or world-fit-anchored px/m under-read the shoulder travel by
  ~25 % (42 vs 56 cm). Anchor vertical px/m on shoulder-to-wrist at the loaded hang.
  Use the trunk scale for hip-level horizontal measures. Always print the alternative
  calibrations into the report; the spread is the honest error bar (±10–15 %).
- **MediaPipe world z is not a measurement.** Trunk lean and "compression" from world
  coordinates were pure foreshortening artefacts; yaw is qualitative at best. Lateral bend
  in the image plane is fine.
- **Lighting-based torso indices are exploratory.** The abdominal-band edge-contrast index
  does rise at the top, but the torso also moves into the lintel's shadow. Say so. Lats
  need a side or rear camera; the front silhouette shows no flare.
- **kcal is a model, not a measurement**: work / 22 % efficiency + lowering at 35 % of
  that + 3.5 MET isometric cost × time under tension. Say "about 1 kcal per rep" and stop.
  The progressive-difficulty story is carried by the effort multiplier (fastest mean pull
  speed ÷ this rep's) and the RIR estimate (one rep per ~9 % peak-velocity loss).

**The muscle heat overlay**

- **It is an EMG-informed prior, not a measurement, and the screen says so** ("EMG
  studies × your effort"). Youdas 2010 %MVIC per muscle (pull-up end of each range for a
  pronated grip), Dickie 2017 concentric > eccentric phase factors, scaled by the measured
  pull speed. Image contrast alone lit up the silhouette edge and was flat inside; it is
  kept to a 25 % share and masked away from the outline. The literature layer is what
  gives the map its structure.
- **Map muscles on the silhouette, not with landmark blobs.** Assign each painted pixel
  to the nearest skeleton segment; band torso pixels by distance-to-edge vs
  distance-to-axis. Fixed-thickness lines left arms half-painted and put "lats" where
  the outline was not.
- **The paint region must come from a matting pass, not the pose model's mask.** The
  256-px pose mask leaked onto the head and the wall. Robust Video Matting alpha ×
  multiclass body-skin excludes head, hair, shorts and background by construction.
- **Segmentation classes flicker when the face is out of view.** With the head behind
  the bar the segmenter labelled the chest as face-skin for a few frames at each rep top,
  and a chest tattoo as clothes. Never subtract a class directly: gate the head class to
  above the shoulders near the ear landmarks, gate the clothes class to around and below
  the hips, close pinholes, build the region from alpha minus the gated classes.
- **Fatigue base:** the whole body warms through the set from the measured velocity loss
  (Sánchez-Medina 2011) and energy spent, and never cools within the set. Opacity 0.96.
- **The look pass** (`look=1`) is the honest version of "make it look better quality than
  it is": matte-driven background desaturate / darken / soften, subject unsharp, rim glow
  in the heat colour, grain, vignette. Applied after the heat and before the UI, so the
  cards stay crisp. No speed ramps, no fake sharpness on the data.
- **Backdrop replacement** (`bg=plate.jpg`): composite with the RVM alpha, keep the real
  bar with a static dark-pixel mask around the bar row, slow push-in. Only free-licence
  plates (Wikimedia Commons CC BY / CC0); write the credit into `ATTRIBUTION.md` and the
  caption.

**Export hygiene**

- **Hold landmarks across dropped-pose frames.** MediaPipe returns no pose on a few
  frames per clip; skipping the paint there flashes the bare body for one frame. The
  renderer keeps the last good landmarks. **Gate every composited export with
  `check_flicker.py`**; the first heat export had four such flashes that a frame-sheet
  check did not catch.
- **Text must be measured, never assumed.** Two exports went out with the intro subtitle
  and the summary footnote running past their boxes. Every one-line text goes through a
  `fit()` that shrinks the face until the line fits, and box widths are sized for the
  longest value that can occur. Check the first frame, the last frame and one rep card
  of every export.
- **Say the verdict, not a letter.** Rep cards and chart chips carry "chin above bar /
  at bar / N cm short" with ✓ / ~ / ✗ from Segoe UI Symbol (Segoe UI itself has no
  ✓/✗; they render as boxes in PIL).
- Layout: shoulder-height chart at the very bottom (knowingly inside the Reels bottom UI
  band), full-width rep card above it, one-line legend "MUSCLE HEAT" + gradient, one
  ELBOW value rather than L/R (an off-axis camera makes L and R read differently),
  SPEED, ENERGY.
- Use the `preview=` mode before any full render; the heat render takes twice as long.

## Next time

- Film from further back or higher so the head never leaves the frame at the top; then
  the chin can be measured directly instead of inferred.
- A side-on second angle makes sway, kip and lat work far more trustworthy.
- Skip the long dead hang if the set is a max-rep test.

## Caption

Hook on the number (reps + efficiency), one line on the method ("33-point pose model,
two independent trackers agree"), the two coaching findings, a question, the credit line
for the backdrop. See [CAPTION.md](CAPTION.md).
