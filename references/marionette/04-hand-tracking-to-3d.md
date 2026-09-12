# Item 4 — Hand tracking to 3D

For the 9-second, 1080x1920/30fps iPhone 14 shot of a right hand seen from the back
(fingers down, ~0.3 m from the lens): what MediaPipe Hand Landmarker's landmarks actually
are and how accurate they are, how depth-from-known-size works and where it breaks down,
where the anatomical fingertip pad sits relative to the tracked tip landmark, male hand-size
norms with means and SDs, and the evidence behind the smoothing/gap-bridging pipeline
(5-frame median + Savitzky-Golay 7/2, cubic Hermite spline over the frames 28-40 closed-fist
gap). Every number below is attributed to a saved file in `references/marionette/`
(papers/, abstracts/, data/); anything not found is marked **NOT FOUND** rather than guessed.

Full source list with URLs/licences/dates: `downloads-04.md`. Raw numbers in
`data/04-hand-norms.csv` and `data/04-tracking-numbers.csv`.

---

## 1. What MediaPipe Hand Landmarker's landmarks are

MediaPipe Hands (Zhang, Bazarevsky, Vakunov, Tkachenka, Sung, Chang & Grundmann, 2020,
`papers/arxiv-2006.10214-mediapipe-hands.pdf`/`.txt`) is a two-stage pipeline: a BlazePalm
detector locates an oriented palm bounding box, then a landmark regression model runs on the
cropped hand region and outputs "21 hand landmarks consisting of x, y, and relative depth"
(Section 2.2). Two facts from the original paper matter a lot for this build:

- The z channel ("relative depth w.r.t. the wrist point") was, in this 2020 model, "learned
  only from synthetic images" — there was no real-photograph depth ground truth at all
  (Section 2.2, `arxiv-2006.10214-mediapipe-hands.txt`).
- Quality is reported as MSE normalized by palm size: 13.4% for the model trained on
  combined real+synthetic data (Table 2), and palm-detector average precision 95.7% (Table 1)
  — not a millimeter or pixel accuracy figure.

The **metric "world landmarks"** the build actually consumes are a later addition, documented
in the official model card (`papers/mediapipe-model-card-hand-tracking-fairness-2021.pdf`/
`.txt`) rather than the 2020 paper: "21 3-dimensional metric scale world landmarks. Predictions
are based on the GHUM hand model," and "Landmark screen z-value and 3D metric x, y, z
coordinate values estimate is provided using synthetic data, obtained via the GHUM model
(articulated 3D human shape model) fitted to 2D point projections." In plain terms: the world
landmarks are not a depth-sensor measurement or a triangulation — they are a learned fit of a
parametric hand shape model to the 2D image, and only that model's synthetic training data
ever supplied ground-truth depth. This is also confirmed, independently, by the GitHub docs
mirror (`papers/mediapipe-github-hands-solution.md`, Apache-2.0): "we take Z-value from image
depth map, if it exists per corresponding coordinate" for real photos — i.e. most real training
images have no real z at all.

**Coordinate conventions** (`mediapipe-github-hands-solution.md`, matching the developer-docs
page fetched separately):
- Image-space landmarks: x, y normalized to [0,1] by image width/height; "z represents the
  landmark depth with the depth at the wrist being the origin, and the smaller the value the
  closer the landmark is to the camera. The magnitude of z uses roughly the same scale as x."
- World landmarks: "real-world 3D coordinates in meters with the origin at the hand's
  approximate geometric center."
- The 21-landmark indexing (WRIST = 0, tip landmarks at indices 4/8/12/16/20 for
  thumb/index/middle/ring/pinky) is the standard `HandLandmark` enum used throughout Google's
  own sample code (`mp_hands.HandLandmark.INDEX_FINGER_TIP`, `HandLandmark.WRIST` both appear
  verbatim in `mediapipe-github-hands-solution.md`); the complete verbatim 0-20 name list
  itself was **NOT FOUND** in any saved source (only a diagram is linked, not transcribed) —
  the mapping above is the well-known public convention, not independently re-derived here.

**Accuracy and failure modes.** The 2021 model card's headline metric is MNAE (Mean of
Normalized Absolute Error by palm size, where "palm size = distance between wrist and MCP of
middle finger"): full model 10.09% ± 1.73% stdev (range 6.10-13.00%) across 14 geographic
regions, lite model 12.02% ± 1.6% (range 8.43-13.42%) (`mediapipe-model-card-hand-tracking-
fairness-2021.txt`). For context, human-vs-human re-annotation MNAE was only 6.0% — so model
error is well above the noise floor of the labels themselves. Most importantly for this
project: **"per-joint MNAE is the smallest at the base of each finger, and gets larger toward
the fingertip"** — the fingertip landmarks (the ones this build hangs marionette strings from)
are explicitly the least accurate landmarks in the model. The card's out-of-scope list names
gloves, occlusions, and jewelry/tattoo/henna as invalidating conditions, and warns the model
"has not been tested in 'in-the-wild' smartphone camera conditions, including low-end devices,
low light, motion blur." **Neither a closed fist nor a dorsal (back-of-hand) camera view is
named anywhere in the model card as a specific failure mode — NOT FOUND as an explicit,
documented limitation.**

The best available *independent* check is Maggioni, Azevedo-Coste, Durand & Bailly (2025,
Sensors, open access, `papers/maggioni2025-markerless-vs-markerbased-hand-mocap.html`/`.txt`),
which validated MediaPipe Hands (v0.10.15, 30 Hz, 4 cameras) against an Optitrack marker-based
rig on 15 participants. Findings directly relevant here:
- Mean joint-angle RMSE 10.9° ± 7.8° (vs. 14.7° ± 8.6° for a Leap Motion Controller); the
  paper's own translation: **"considering the length of a finger segment between two joints,
  this range of error (10° to 15°) is equivalent to a distal spatial error of a few (around
  two to three) millimeters."**
- On depth specifically: **"preliminary testing revealed that this third depth coordinate was
  unreliable, frequently causing the estimated hand to adopt impossible poses."**
- On occlusion: **"the landmarks of occluded fingers were not concurrent with the actual
  position of said fingers,"** and their "flexion" task (fingertips folded under the palm — the
  closest analog in that study to a closed fist) showed marker/landmark occlusion rates
  reaching 16.6% ± 18.8% of frames.
- This study never tested a dorsal (back-of-hand) camera angle — all recordings were palm-down
  toward the camera rig — so it does **not** directly confirm or deny a dorsal-view failure
  mode either. **NOT FOUND** across every source checked.

**Verdict on "holds the hand's depth constant" instead of trusting MediaPipe's own depth/z:**
correct call, and independently corroborated twice over — by MediaPipe's own documentation
(world-landmark z comes from a model fit to 2D, not measured depth) and by Maggioni's
explicit finding that the depth channel produces "impossible poses" in practice.

---

## 2. Depth from the image: hand length / palm width vs. metric norms

No single paper in this pass gives a dedicated "hand-length-in-pixels to depth" study, so this
section is the standard pinhole-camera relation plus the norms found for it, not a lifted
formula. For an object of known real size `S` filling `p` pixels in an image, at focal length
`fx` (pixels): `depth Z = fx * S / p`. Item 5's already-archived iPhone 14 camera work
(`data/05-camera-numbers.csv`, not re-fetched here, only read) gives `fx` for the 1080p-wide
video crop as roughly 1441-1601 px (depending on how much of the sensor width the video mode
actually reads out — flagged there as an assumption, not a confirmed Apple spec). Plugging in
this project's own numbers as an order-of-magnitude check: a 19.3 cm hand held ~0.3 m from the
lens, imaged nearly fronto-parallel, would occupy roughly `1441 px * 0.193 m / 0.30 m` =~ 930 px
of a 1080 px-wide frame — i.e. filling most of the frame width, consistent with "~0.3 m from
the lens" in the brief. This is arithmetic on already-archived numbers, not a new source.

**Where this breaks down — foreshortening.** The depth formula above assumes the measured
hand-length/palm-width axis lies in a plane parallel to the sensor. Two of this project's own
named conditions violate that assumption:
- **Finger curl**: a curling finger's tip-to-MCP projected length shrinks below its true 3D
  length as the distal segments rotate out of the image plane — the projected pixel length no
  longer represents the true 19.3 cm/2.84 cm (etc.) reference length, so a depth computed from
  it would be systematically wrong (too far, since the apparent size shrinks as if the hand had
  moved away). No paper found quantifies this error in millimeters directly; the closest
  corroborating evidence is geometric/indirect: the model card's finding that per-joint error
  grows toward the fingertip, and Maggioni's finding that occluded/folded fingers are
  "not concurrent with the actual position" — both consistent with, but not a direct
  measurement of, a foreshortening-driven depth error. **NOT FOUND** as a directly quantified
  curl-vs-depth-error study.
- **Palm tilt**: rotating the palm normal away from the optical axis has the same effect on
  the palm-width measurement (and, by the MediaPipe model card's own admission, GHUM-model
  world landmarks are a *fit*, not a triangulation, so an unmodeled tilt biases the fit itself,
  not just a downstream measurement). Same **NOT FOUND** caveat: no source directly quantifies
  a tilt-angle-to-depth-error curve for this specific pipeline.

**Verdict:** the depth-from-known-size formula itself is uncontroversial optics, but the task
brief's framing ("the error when fingers curl or the palm tilts") is **not answerable with a
specific number from any source found in this pass** — only qualitative, converging evidence
that both conditions degrade accuracy, concentrated at the fingertips. Since the build "holds
the hand's depth constant" rather than re-deriving depth every frame from pixel size, it
sidesteps this failure mode almost entirely for depth — but the *pose* (PnP) solve still
depends on 2D landmark positions that degrade under curl/tilt in the same way.

---

## 3. Where the tip landmark sits, and the source for the 7 mm pad offset

The MediaPipe tip landmarks (indices 4/8/12/16/20) are trained to sit at the visible tip of
each digit as annotated in 2D images and the synthetic GHUM-fitted 3D data — i.e.
approximately on the skin surface at the fingertip, not at any specific anatomical depth
(bone axis vs. palmar pad surface is not distinguished by the annotation scheme as documented;
**NOT FOUND** as an explicit statement either way in the model card or the architecture
paper). Greiner (1991) locates the analogous anthropometric landmark, "point 35," at "the tip
of digit 3" for the DIGIT 3 TIP TO WRIST CREASE LENGTH and DISTAL PHALANX LINK LENGTH
measurements (`greiner1991-hand-anthropometry-of-us-army-personnel.txt`, items 24 and 31) —
consistent with a skin-surface landmark, but Greiner's photometric system measures in a single
projected plane and does not distinguish dorsal-side skin from palmar-side skin at the tip
either.

Critically, **Greiner's report has no fingertip depth/thickness measurement at all.** Checking
its full table of contents (items 1-86, Chapter II), every distal-digit dimension is a length,
a mediolateral breadth, or a circumference — never a dorsal-palmar depth or thickness. So the
Army hand-anthropometry survey used throughout this project cannot supply a source for "how
far palmar from the surface landmark does the actual pad sit."

The best source found for that specific question is Hauck, Camp, Ehrlich, Saggers, Banducci &
Graham (2004), "Pulp Nonfiction: Microscopic Anatomy of the Digital Pulp Space" (*Plastic and
Reconstructive Surgery*), which reports an **"averaged maximal thickness of soft tissues of
the fingertip pulp [of] 6.4 ± 0.8 mm"** (bone/periosteum of the distal phalanx to the palmar
skin surface), alongside a 4 ± 1 mm phalanx-bone height in the same cross-section. This figure
could only be confirmed via secondary citation and the paper's Europe PMC abstract
(`papers/europepmc-hauck2004.json`) — the primary full text sits behind an Ovid/LWW paywall
and was **not independently read**; flagged accordingly in `abstracts/hauck2004-pulp-
nonfiction.txt` and `data/04-hand-norms.csv`.

**Verdict:** the build's 7 mm palmar-normal pad offset lands inside 1 SD of Hauck et al.'s
6.4 ± 0.8 mm bone-to-palmar-skin pulp thickness — plausible and well-grounded in order of
magnitude, though ~0.6-1.4 mm on the high side of that range, and the source itself is a
secondary citation of a paywalled paper, not a directly-read primary result. No source in this
project's own anthropometric backbone (Greiner, ANSUR II) can corroborate or refute it, since
none of them measured fingertip depth/thickness at all.

---

## 4. Male hand norms — three independent sources, and they agree

| Quantity | Greiner 1991 (n=1003 men) | ANSUR II 2012 (n=4082 men) | NASA-STD-3000 (50th %ile, American male) |
|---|---|---|---|
| Hand length | 19.41 cm ± 0.99 cm (tip-to-stylion) / 19.45 cm ± 1.03 cm (tip-to-wrist-crease) | 19.33 cm ± 0.995 cm | 19.3 cm (5th/95th: 17.9/20.6 cm) |
| Hand breadth | 9.04 cm ± 0.42 cm | 8.83 cm ± 0.439 cm | 8.9 cm (5th/95th: 8.2/9.6 cm) |
| Palm length | 11.05 cm ± 0.60 cm | 11.65 cm ± 0.623 cm | NOT FOUND |
| Hand circumference | NOT tabulated here (report has it, not transcribed) | 21.23 cm ± 1.024 cm | 21.8 cm (5th/95th: 20.3/23.4 cm) |

Full transcription with page/column citations: `data/04-hand-norms.csv`. ANSUR II's mean/SD
were computed directly from the raw public CSV (`papers/ansur-ii-male-public.csv`, 4082 rows)
with Python (`statistics.mean` / `statistics.pstdev`), not read off a pre-published summary
table.

**Verdict on the build's "19.3 cm, entered from memory, to be confirmed":** confirmed, and
unusually well. Three independent surveys spanning 1991-2012, with sample sizes from 1,003 to
4,082 men and two different measurement technologies (photometric digitizer/caliper vs.
whatever ANSUR II's own protocol used), all land within 0.15 cm of 19.3 cm for male hand
length. This is one of the stronger corroborations found across this whole research pass —
the number from memory happened to be correct.

**Verdict on scaling world landmarks to the population median hand length:** reasonable as a
population-level default given the above, but note the three sources above don't share
exactly the same landmark definition (stylion vs. wrist-crease vs. an MCP-based "palm size"
used elsewhere in MediaPipe's own MNAE metric) — the ~0.1-0.15 cm spread between definitions is
small relative to the ~1 cm population SD, so this doesn't materially change the scaling, but
it means "the median wrist-to-middle-tip length" in the build's own code is not necessarily
measuring the identical landmark pair as any single cited source, only something close to it.

---

## 5. Smoothing and gap-bridging

**One Euro filter** (Casiez, Roussel & Vogel, 2012, CHI, `papers/casiez2012-one-euro-
filter.pdf`/`.txt`) is named in the task brief as a smoothing reference, but **the build does
not use it** — it uses a 5-frame median + Savitzky-Golay (7, 2) cascade instead. For the
record, the paper's own worked example (tuned for a 60 Hz, 1440x900 px mouse cursor against an
Optitrack/Gametrak reference) settles on `mincutoff = 1.0 Hz`, `beta = 0.007`, with a fixed
`1.0 Hz` cutoff on the internal speed-derivative low-pass stage. The paper is explicit that
these two parameters must be *re-tuned per device and task* using its own two-step procedure
(hold still to set `mincutoff`, then move fast to set `beta`) — there is no universal "30 fps
hand landmark" preset in this source, so even if the build switched to One Euro, transplanting
1.0/0.007 verbatim would not be justified by this paper.

**Savitzky-Golay, window 7 / order 2**: a dedicated optimality analysis (arXiv:1808.10489,
"Optimum window length of Savitzky-Golay filters with arbitrary order,"
`papers/arxiv-1808.10489-optimum-savgol-window.pdf`/`.txt`) shows the optimal window length is
not a fixed constant — it is a function of the signal's local smoothness and the noise level
("the lower the SNR, the larger the optimal window length will be"), and that for
smooth-ish signals **"there is not much difference between order 2 and higher"** — i.e. order 2
is a defensible, low-complexity choice, but window length 7 is not derived from this
project's actual landmark-jitter statistics anywhere in the source material — it is a common
off-the-shelf default.

**Cubic Hermite spline bridging the frames 28-40 closed-fist gap**: a small motion-capture
gap-filling report (Schuddeboom, "Automatic Processing of Motion Capture Data," a Utrecht
student project hosted at `perso.liris.cnrs.fr`, `papers/schuddeboom-automatic-processing-
mocap-data.pdf`/`.txt`) tested exactly this technique under the name "pchip" (piecewise cubic
Hermite interpolating polynomial): **"fills a gap using position and velocity at both ends of
the gap to create a C2 continuous spline."** This matches the build's situation precisely —
landmark tracks exist on both sides of the 13-frame gap, which is the precondition the report
states for using interpolation over extrapolation at all ("interpolation requires both data
before and after the gap"). However, the report's own accuracy comparison (Table 5, gap sizes
5-30 frames, which brackets this project's 13-frame gap) found **extrapolation from before the
gap alone (normalized deviation 1.095) outperformed Hermite/pchip interpolation using both
sides (normalized deviation 1.558)** on their specific mocap dataset — with the caveat, per the
same report, that "spline interpolation can be expected to be more accurate toward the end of
the gap, since it will converge to the point at which data reappears." This is one dataset,
not a general result, but it is a mild caution rather than a clean endorsement.

**Verdict on median+SG+spline overall:** methodologically standard and internally consistent
(median kills single-frame outlier spikes, SG smooths remaining high-frequency jitter while
preserving curvature, Hermite spline is the textbook choice for a gap with known data on both
sides) — but two of the three numeric choices (SG window=7, and interpolation-over-
extrapolation for the gap) are defaults/reasonable engineering picks rather than values derived
from this footage's own noise/gap statistics, per the sources above. Neither choice is wrong;
neither is uniquely justified by what was found either.

---

## Numbers for the model

| Quantity | Value | Source |
|---|---|---|
| Male hand length (mean) | 19.3-19.45 cm (converges across 3 sources) | Greiner 1991, ANSUR II 2012, NASA-STD-3000 — see Section 4 table |
| Male hand length SD | ~0.99-1.03 cm | Greiner 1991 / ANSUR II 2012 |
| Male hand breadth (mean) | 8.83-9.04 cm | Greiner 1991, ANSUR II 2012, NASA-STD-3000 |
| Male palm length (mean) | 11.05-11.65 cm | Greiner 1991, ANSUR II 2012 |
| Fingertip pulp thickness (bone to palmar skin) | 6.4 ± 0.8 mm | Hauck et al. 2004 (secondary-cited, full text unverified) |
| MediaPipe world landmark units/origin | meters, hand's approximate geometric center | MediaPipe GitHub docs / model card |
| MediaPipe image z convention | wrist-relative origin, smaller = closer to camera, scaled like x | MediaPipe GitHub docs |
| MediaPipe full-model landmark error (MNAE) | 10.09% ± 1.73% of palm size | Model card 2021 |
| MediaPipe fingertip-region error pattern | largest of any joint region | Model card 2021 |
| Independent (Optitrack-validated) fingertip spatial error | ~2-3 mm | Maggioni et al. 2025 |
| MediaPipe relative-depth (z) reliability | documented as unreliable / "impossible poses" | Maggioni et al. 2025 |
| Curl/tilt-specific depth error | NOT FOUND (no directly quantified source) | — |
| Dorsal (back-of-hand) view failure mode | NOT FOUND (untested in every source checked) | — |
| Closed-fist failure mode (explicit) | NOT FOUND in MediaPipe's own docs; occlusion generally documented as out-of-scope | Model card 2021, Maggioni et al. 2025 (proxy: folded-finger task) |
| One Euro default params (not used by this build) | mincutoff=1.0 Hz, beta=0.007, derivative cutoff=1.0 Hz | Casiez et al. 2012 (tuned for a different task; not re-derived for 30fps) |
| SG window/order optimality | order 2 defensible; window 7 not derived from this footage | arXiv:1808.10489 |
| Cubic Hermite (pchip) gap fill | matches build's method; one dataset found extrapolation more accurate at comparable gap sizes | Schuddeboom mocap report |

## One-line verdicts on the build's choices

1. **19.3 cm male hand-length norm (from memory):** confirmed by three independent surveys
   (Greiner 1991, ANSUR II 2012, NASA-STD-3000) within 0.15 cm — correct.
2. **Scaling world landmarks to that median:** reasonable; landmark-definition differences
   between the three sources (~0.1-0.15 cm) are small relative to the ~1 cm population SD.
3. **PnP pose solve:** standard, well-supported method family (EPnP-class algorithms); the
   specific solver/flags used in the build's code were not checked against literature in this
   pass.
4. **Holding depth constant instead of trusting MediaPipe's z/world-depth:** correct and
   independently corroborated — MediaPipe's own docs describe world-z as a GHUM model fit, not
   measured depth, and Maggioni et al. found it produces "impossible poses" in practice.
5. **7 mm palmar-normal pad offset:** plausible, inside 1 SD of the closest anatomical figure
   found (Hauck et al., 6.4 ± 0.8 mm pulp thickness), but that figure is a secondary citation
   of a paywalled source, and the project's own anthropometric backbone (Greiner, ANSUR II)
   has no depth/thickness measurement to check it against.
6. **Cubic Hermite spline over the 13-frame closed-fist gap:** methodologically the right tool
   for data known on both sides of a gap, per the one gap-filling study found — though that
   same study found plain extrapolation more accurate at comparable gap sizes on its own
   dataset, a mild caution rather than a contradiction.
7. **5-frame median + Savitzky-Golay (7, 2):** order 2 is defensible per a dedicated
   optimality analysis; window 7 is a common default, not derived from this footage's own
   landmark-noise statistics — nothing found says it's wrong, nothing found says it's optimal.
8. **One Euro filter (named in the task brief):** not actually used by the build; if it were
   adopted, its published default parameters (mincutoff=1.0 Hz, beta=0.007) are tuned for an
   unrelated 60 Hz pointing task and would need re-tuning per the paper's own procedure before
   use on 30 fps hand landmarks.
