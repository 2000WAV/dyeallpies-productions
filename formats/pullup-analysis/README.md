# Pull-up analysis

Three sets so far: `REPORT.md` (2026-09-05, the 140k-view video), `REPORT-2.md` (2026-09-07) and `REPORT-3.md` (2026-09-08, the research-backed one; read `PLAN-3.md` for the critical assessment of the first two). The literature archive behind set #3 is in `../../references/pullup-science/`.

A phone clip of one pull-up set, camera static, whole torso and arms in frame, becomes a
rep-counted, biomechanics-annotated Reel plus a dashboard, a written report and an
interactive page.

**Two sets analysed.** 2026-09-05, camera on the floor: 10 reps. 2026-09-06, camera further
back and level: 11 reps and a failed twelfth attempt, judged against the USMC pull-up
standard — and none of the eleven put the chin over the bar. It also carries a measured
signal beside the modelled one: the chest flush, which doubles over five reps and tracks
the modelled muscle temperature at r = 0.83. The second run is the current
pipeline; the first is kept because its numbers must stay reproducible.

- Second set, the worked example with the timeline and every mistake on the way:
  [pullups-2026-09-06.md](pullups-2026-09-06.md) · report [REPORT-2.md](REPORT-2.md) ·
  caption [CAPTION-2.md](CAPTION-2.md) · dashboard
  [pullup2-dashboard.png](pullup2-dashboard.png) · the physiology and technique references
  behind it: [references/pullup-thermal/](../../references/pullup-thermal/README.md)
- First set, the worked example with the timeline of the session and every mistake on the way:
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

## The second set's scripts

`analyze_pullups2.py`, `render_pullup_overlay2.py`, `render_pullup_dashboard2.py`,
`build_pullup_page2.py`, `pullup_thermal.py` and `pullup_atlas.py` in
[`tools/scripts/`](../../tools/scripts/) are the current pipeline; `straighten.py` and
`vp_fit.py` here measure the camera roll and write the de-rolled master. The unsuffixed
scripts are the first set's and are kept only for reproducibility.

## Pipeline (first set)

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

## The third set's pipeline (2026-09-08, floor camera)

Scripts with the `3` suffix are the current ones; `work3/` holds the geometry helpers.

```bash
PY=.venv-pushup/Scripts/python.exe
# 0. tone-mapped SDR master (the phone records 10-bit HLG)
ffmpeg -y -init_hw_device vulkan -i IMG.MOV -vf "libplacebo=tonemapping=bt.2390:colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv:format=yuv420p" -c:v h264_nvenc -preset p5 -rc vbr -cq 12 -b:v 0 -c:a aac work3/master.mp4
# 1. camera model: vertical + horizontal vanishing points -> f, R, H (the doorway plane)
$PY work3/vp_fit.py work3/master.mp4 work3/vp.npy 135,165,600,1200,1745,1790 690
$PY work3/geom_fit.py work3/master.mp4 1745,1770,1800,1830,1860       # bar, lintel, horizontal VP
$PY work3/rectify.py work3/master.mp4 1770 work3/rect_check.png       # H_rect.npy, K.npy; check the frame
# 2. trackers on the master, in parallel (matte is the long pole, ~26 min)
$PY tools/scripts/extract_pose_mp.py work3/master.mp4 tools/models/pose_landmarker_heavy.task work3/pose_mp.npz
$PY tools/scripts/extract_pose_yolo.py work3/master.mp4 tools/models/yolov8m-pose.pt work3/pose_yolo.npz 640
$PY tools/scripts/extract_matte.py work3/master.mp4 work3/matte.npy 2
# 3. analysis in the rectified plane (stand= the reach under the bar, ref= arms down after the set)
$PY tools/scripts/analyze_pullups3.py work3/master.mp4 work3/pose_mp.npz work3/analysis.json work3/pose_yolo.npz height=1.88 mass=79 stand=7.8,9.2 ref=57.2,58.6
$PY tools/scripts/pullup_thermal3.py work3/analysis.json
$PY tools/scripts/pullup_chin_silhouette.py work3/analysis.json work3/matte.npy work3/chin_sil.json strip=work3/chin_strip.jpg
$PY tools/scripts/measure_redness.py work3/master.mp4 work3/pose_mp.npz work3/analysis.json work3/matte.npy work3/redness.json ref=0.22,0.22,0.35,0.28 base=205,275
# 4. backdrop: Commons search (curl), cut-outs (rembg isnet), plate
$PY work3/commons_search.py "spider monkey" work3/commons/spider_monkey.json 2500 50
$PY work3/commons_download.py && $PY work3/commons_credits.py && $PY work3/build_plate3.py
# 5. renders: preview three frames at 1:1 first (atlas), then the full set, then the reel by schedule
$PY tools/scripts/pullup_atlas3.py work3/master.mp4 work3/pose_mp.npz work3/analysis.json work3/matte.npy 430,506,1478 work3/atlas3
$PY -u tools/scripts/render_pullup_overlay3.py work3/master.mp4 work3/pose_mp.npz work3/analysis.json out/pullup3-analysis.mp4 heat=work3/matte.npy look=1 grid=1 cat=1 lut=iron bg=assets/jungle3_plate.jpg trim=150,1712 hold=4.5 > work3/full_render.log
$PY -u tools/scripts/render_pullup_overlay3.py ... out/pullup3-reel-30.mp4 ... schedule=work3/reel_schedule.json
# 6. gates, dashboard, page
$PY tools/scripts/check_flicker.py out/pullup3-analysis.mp4 work3/matte.npy work3/flicker_full.png offset=150
$PY tools/scripts/render_pullup_dashboard3.py work3/analysis.json out/pullup3-dashboard.png work3/redness.json
$PY tools/scripts/build_pullup_page3.py work3/analysis.json out/pullup3-report.html work3/redness.json
```

## Rules that came out of the third set (2026-09-08, floor camera, anatomy paint) — these supersede

Worked example: `pullups-2026-09-08.md` (in this folder). Scripts:
`analyze_pullups3.py`, `render_pullup_overlay3.py`, `render_pullup_dashboard3.py`,
`build_pullup_page3.py`, `pullup_thermal3.py`, `pullup_atlas3.py`, `pullup_chin_silhouette.py`;
geometry helpers in `pullup/work3/` (`vp_fit.py`, `geom_fit.py`, `rectify.py`, `build_plate3.py`,
`commons_search.py`). Research archive: `references/pullup-science/` (read `01`–`06` before
changing a constant; `DOWNLOADS.md` lists every file).

- **Research before rendering, and archive it.** Every constant in the heat budget, the
  velocity rules and the norms cites a file in `references/pullup-science/`. Agents fetch
  abstracts through PubMed E-utilities and Europe PMC, PDFs with `curl -A "Mozilla/5.0"`;
  the system Python's certificate store is expired, so downloads go through curl.
- **Tone-map HLG before anything reads a pixel.** iPhone clips are 10-bit HLG; the plain
  decode is grey. `libplacebo=tonemapping=bt.2390` on Vulkan (`-init_hw_device vulkan`) into
  an SDR master; zscale hable/mobius are worse by eye.
- **Measure in a rectified plane, render on the frame.** Two vanishing points → f from
  their orthogonality → H = K Rᵀ K⁻¹, then a residual rotation so the fitted bar is exactly
  level (the bar is the judge's line). Verify with the lintel: if it tilts the same way, the
  residual was the model. The plane normal must point away from the camera or the image
  mirrors. Landmarks go through H; the render, the grid (mapped back through H⁻¹) and the
  paint stay in image space.
- **Depth is the allowance, computed.** Elevation to the bar from K and the pitch; a point d
  behind the bar plane projects tan(elevation) × d lower. State the assumed depth (8 cm for
  the chin) and the band it implies (±3 cm) — never a fixed "3 cm".
- **The head hidden at the top is a witness only after you know what hides it.** With a bar
  mounted at the back edge of the lintel's underside, "hidden" means chin ≥ the bar's
  underside sight line, nothing more. Look at a rep top at full resolution with the
  highlights stretched before writing any occlusion bound. YOLO's nose confidence can stay
  high with the head gone; MediaPipe's visibility always does.
- **Chin from the last honest frame.** face_seen = eyes ≥ 4 cm under the bar's underside
  AND nose confidence > 0.35; chin at the top = face-axis chin there + the shoulder rise
  since. Print in-plane, adjusted and the head-hidden time per rep.
- **Phases from the local base.** The passive dead hang sits 2–3 cm below the active hang;
  the concentric starts from the highest shoulder position in the second before the pull.
- **Reference windows:** stature = the reach under the bar (arms up, at the bar plane);
  shoulder-tilt reference = arms down, after the set; ear-to-shoulder reference = the dead
  hang, never the reach (it reads a 10 cm "shrug" on every top).
- **Scale check by physics:** shoulder-to-bar at the dead hang must equal 0.332 × stature
  within a few percent. The wrist-based arm anchor under-reads by ~13 % (the wrist is 8 cm
  below the bar); report it, do not average it in.
- **Velocity: rep 1 is the reference (Beckham 2018), the fastest rep beside it; loss against
  25 % / 50 % (Sánchez-Moreno 2020); RIR is a range, never an integer.**
- **The chest flush is not muscle heat at the skin.** Skin blood flow falls in the first
  minute of exercise; report the index as effort-tracking and say what it is not.
- **Anatomy paint:** regions with fibre-direction fields (fan to the tendon or parallel),
  grooves with an inner highlight, belly shading, irregular thin striations, the frame's own
  luminance kept deep; ironbow scale 0 → +1.5 °C; names shown once when a muscle passes
  +0.3 °C. Preview hang / mid-pull / top at 1:1 before rendering.
- **Layout for a centred, large body:** push in only as far as keeps the bar under the
  Instagram top band; no side panels over the arms — readouts are pills beside the elbow
  and hips; the legend lives in the chart header; the card leads with three numbers.
- **Backdrop:** Commons API with `iiurlwidth` for thumbnails (hand-built thumb URLs 400),
  originals into `pullup/assets/commons/` with `CREDITS.json`; rembg isnet + alpha matting
  for cut-outs, drop any that sat on branches; the cat is pasted from its own mask.
- **Tooling hygiene:** patch scripts from a file with `encoding="utf-8"` (a heredoc here
  mangles `\n` and non-ASCII); run long renders with `python -u` straight to a log.
- Next upgrades, licence-checked in `05-ml-tooling-survey.md`: DWPose via rtmlib (jawline
  keypoints), SAM 2 for person + cat masks, SCHP for body-part parsing.

## Efficiency score (per rep, /100)

ROM 25 (chin at or over the bar, −2.5 per cm short) · eccentric control 20 (full at
1.5 s) · lock-out 15 (155°+ full, 0 at 120°) · low sway 15 (≤ 4 cm hip sway full, 0 at
20 cm) · pull speed 15 (peak concentric velocity ÷ the best rep of the set) · L/R
symmetry 10 (≤ 5° mean elbow gap full, 0 at 25°). A ≥ 85, B ≥ 70, C ≥ 55. The letter is
a footnote; the rep card and the chart chips carry the chin verdict.

## Rules that came out of the second set (2026-09-06, level camera) — these supersede

- **Straighten before measuring, and get the roll from gravity, not from the room.** A
  doorway that leans in the image is not proof of roll: with a low camera you have roll
  AND yaw at once, so verticals converge one way and horizontals the other. Fit the
  vertical vanishing point (RANSAC over long LSD segments) and read the roll as the tilt of
  a true vertical **at the subject's x**, then cross-check it against gravity references
  the body itself provides: the standing ankle→eye line, and the grip→hip and grip→ankle
  plumb lines at a quiet dead hang. On IMG_5990 those four agreed at 2.1–3.5° while the bar
  read level — **the bar looked level only because yaw makes horizontals converge.**
  Rotate with `cv2.warpAffine`, `BORDER_REPLICATE`, scale 1.0: no zoom, no crop, no black
  corners. `getRotationMatrix2D(c, +angle, 1)` turns counter-clockwise — **verify by
  re-measuring the verticals on the output**, the sign is easy to get backwards.
- **The bar is a line, not a row.** With yaw it is tilted in the image (3.0° here) even
  after de-rolling. Fit it on empty frames with sub-pixel edges (1626 points over 14 frames
  gave a 0.25 px residual) and measure every height against the bar line **at that point's
  own x**. Validate the fit independently before publishing any chin claim; everything
  rests on it.
- **Chin from the face axis:** `chin = mouth + 0.60 × (mouth − eye midpoint)`. At the top
  of a rep the head is tilted right back, so a fixed nose-to-chin or shoulder-to-chin drop
  measured standing is far too pessimistic — the first pass called 11 of 12 attempts
  failures. The face-axis construction cancels head pitch and foreshortening together.
  Carry ±1.5 cm on every chin number and print the shoulder-anchored estimate beside it.
  **Crop the head at a rep top at 3× with the bar line and a centimetre ruler drawn on it
  and look, before believing any chin number.**
- **Scale from the standing stature when the feet are in frame** (eye→ankle ÷ 0.897 ×
  stature). Three anchors then agree within 5 %, against 30 % on the floor-camera clip.
- **Hang onset from the feet.** Ankle plateau while the hands are up = standing; the feet
  leaving the floor is the load-off. Keep the arm-length method only as a fallback.
- **Phase boundaries from position, not velocity:** concentric from 5 % to 95 % of that
  rep's own amplitude, eccentric back down. The velocity walker collapsed on one rep and
  reported a 0.03 s lowering.
- **An attempt that stalls is not a rep.** Count reps and failed attempts separately
  everywhere — counter, cards, chart chips, tables, mean efficiency.
- **Judge to a published standard and name it.** USMC PFT pull-up: dead hang with the arms
  fully extended, chin above the bar, lower to full extension, no kipping, kicking or leg
  movement. Report each line as pass / fail / borderline with its number. Never a letter
  grade as a form verdict.
- **A kip is a swing, not a hip angle.** Flagging `hip_angle_range > 15°` called a strict
  set a kip: the hip angle changes 38° simply because the torso rises past tucked legs.
  Use horizontal hip travel (> 8 cm) for the kip flag, report the leg tuck as its own
  line, **and watch a frame strip through two reps before writing either verdict.**
- **Asymmetry in the image plane first.** After de-rolling, image vertical is world
  vertical, so left/right differences in the picture are real. MediaPipe's 3D angles are a
  model estimate: here they said the elbows were 20° apart while the image plane said 2.6°.
  When a model and a measurement disagree, **report both and claim neither.**
- **Muscle heat is a temperature, in °C.** `pullup_thermal.py` integrates
  `C dT/dt = share × P_heat − k(t) × dT` with C = 3.6 kJ/kg/K, share = %MVIC × muscle mass
  (Youdas 2010 × Holzbaur 2007, scaled ×1.4 for a 188 cm man), and k ramping to
  42 W/K/kg with a 90 s time constant — both from González-Alonso 2000, which is also why
  temperature never falls inside a 53 s set. Only the grip's share (22 %) of the isometric
  term is deposited locally; the rest is whole-body. Sanity check: the integral of the heat
  power must match the analysis JSON's own per-rep heat total. Legend on screen reads
  "MODELLED MUSCLE TEMP · a model, not a thermal camera", and say what an infrared camera
  would really show (skin cools first, warms after, < 1 °C — Jung 2021).
- **Muscle regions from a warped polygon atlas** (`pullup_atlas.py`), not nearest-segment
  banding: polygons drawn once in a canonical body frame (trunk coordinates for the torso,
  per-segment for the arms), warped by the frame's landmarks, deliberately overshooting the
  body so the **silhouette** sets every edge. Check the label map over hang / mid-pull / top
  before rendering.
- **The look pass needs the person alpha, not the paint region.** `LookPass` desaturates
  everything outside the mask it is handed; handing it the paint region turned his head,
  legs and shorts grey.
- **Cut the Reel by frame schedule from the source frames** (`schedule=sched.json`), never
  by re-timing a finished render. Every cut lands on a dead hang so the body is in the same
  place across it; the sped-up block is one continuous run with a "×N" pill and the
  per-frame readouts dropped (they are unreadable at ×6) — keep the counter, the
  temperature and the legend. Freeze the summary on the **last frame shown**, not on the
  clip's last frame, or the card lands on whatever the camera saw after the set.
- **Read forward, seek rarely.** `cap.set(POS_FRAMES)` per frame costs a keyframe decode
  each time; step the reader forward for gaps up to a GOP and seek only for backward jumps.
- **Trim the tail.** The last seconds where he walks up to the camera produce garbage
  landmarks and a heat-painted close-up. `trim=f0,f1`.
- Text: `fit()` everything, and check the first frame, the last frame, one rep card, one
  sped-up frame and the summary card of every export.

- **Paint the legs too, and let them be cold.** Dennis asked for it and the physics agrees:
  the legs hold a tucked position rather than lifting, so they take **no share of the work
  heat** - only a slice of the isometric term - and finish a 53 s set at +0.04 to +0.19 °C.
  They read blue, which is the honest picture. Give the work heat only to the muscles that
  move the body (`POSTURAL` in `pullup_thermal.py` is excluded from `heat_shares()`).
- **Colour is temperature, brightness is activation.** Temperature accumulates and never
  falls inside a set, which is correct but static. `TH.activation()` gives a per-frame,
  per-muscle activation from the EMG phase ordering scaled by the measured pull speed;
  multiply the painted colour by `0.82 + 0.42 x activation`. Two quantities, two channels,
  and the legend names both. Do not fold activation into the colour - it would break the
  degrees-C claim.
- **The head gate must not scale with the ear separation.** When he tilts his head back at
  the top the ears close up in the image and an ear-width gate collapses to a dot, letting
  the paint run over his face. Scale it on the shoulder width (`0.62 x sw`).
- **A see-through form grid earns its place** (`grid=1`): rules parallel to the bar every
  10 cm with cm labels, a dashed plumb line through the middle of the grip, and - at full
  strength - the shoulder line drawn against a true horizontal through its own midpoint, so
  the tilt being claimed is visible rather than asserted. Stop the grid above the chart
  panel (`GRID_BOTTOM`).
- **Measure the chest flush; it is the only signal that comes from the pixels.**
  `measure_redness.py`: the index `(R-G)/(R+G) x 1000` over chest skin, sampled at the dead
  hang after each rep (pose and lighting repeat there), minus the same index on a fixed
  patch of wall in the same frame so exposure and white-balance shifts cancel. Reject any
  sample whose wall patch is occluded - he crosses it on the way down. On this set it
  doubled over five reps then plateaued, and correlated **r = 0.83** with the modelled
  muscle temperature while the wall control drifted the other way. Present it as
  exploratory: partly hair, moving shadow, eleven points, one person.
- **Backdrop licences: CC BY or CC0 only, never ShareAlike.** A CC BY-SA element would push
  the whole Reel into ShareAlike. Search Wikimedia Commons through the API with a real
  User-Agent, filter the licence before downloading, cut subjects out with GrabCut from a
  tight rectangle (a loose rectangle leaves a visible box of background), and write every
  credit line into `pullup/assets/ATTRIBUTION.md` and the caption.

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
