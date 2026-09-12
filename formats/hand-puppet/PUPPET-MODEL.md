# The hand-puppet model (v1.1, 2026-09-12)

What the video claims physically, where every number comes from, and what is assumed, ranked by
how much it can move the picture. The code is `tools/scripts/hand_to_3d.py` (the hand in 3D),
`puppet_model.py` (the figure), `puppet_sim.py` (the physics and its checks), `render_puppet.py`
(the neon layer and the composite). The research archive is `references/marionette/` (items
01–08, `DOWNLOADS.md`). A reviewer reads the modules top to bottom and rebuilds the argument
without the chat (CLAUDE.md).

## 1. What the camera can and cannot see

The phone looks at the back of a hand in front of a textureless wall. It measures the fingertips'
positions in the picture (MediaPipe, 21 landmarks on 254 of 267 frames; the fist, frames 28–40, has
none) and nothing in metres. So:

- **The one free scale is the hand's length.** The world landmarks' median wrist-to-middle-tip
  length (14.0 cm on their canonical scale) is set to a male hand-length norm of 19.3 cm (entered
  from memory of ANSUR II; item 04 confirms or corrects it). Everything in metres scales with it:
  the hand's depth (0.324 m at f = 1600 px), the puppet's size, the drop height, the string
  lengths. The puppet's size *relative to the hand* does not depend on it, nor on the focal length.
- **The focal length**: 1600 px at 1080×1920 (item 05: Apple's 26 mm-equivalent spec, the 1.9 µm
  pixel pitch, the ~10 % stabilisation crop; 1441 px without the crop; ±50 px per an iPhone 14
  checkerboard calibration). It only sets the depth in metres and the perspective across the
  puppet's 15 cm, which at 0.32 m is a 4 % size change top to bottom.
- **The hand's depth is held constant** at the median PnP depth over the open phases. The PnP
  depth jumped 10 cm whenever the fingers curled (a curled hand looks smaller and MediaPipe's world
  landmarks are not rigid: 5.4–10.4 cm wrist-to-knuckle before scaling), and the arm does not move
  in this shot. Each fingertip keeps its relative depth from the rotated shape (±4 cm, smoothed
  over 15 frames); its lateral position is the tracked pixel back-projected at that depth, so the
  string leaves exactly the tracked tip.
- **The camera is handheld and not compensated.** The wall line at the top drifts 60 px and rolls
  −1.1° to +0.3° over the shot; a seam in it was template-tracked for the pan and jumped 25 px
  frame to frame, so it is measured and printed, not used. A camera translating a few centimetres
  over seconds is a 0.05 m/s² anchor acceleration on a 9.8 m/s² problem, and the wall has no
  texture that a shifted render could disagree with. The roll tilts gravity in the sim.
- **The pads**: the string leaves the palm side of each fingertip, hidden from the camera. Pad =
  tip landmark + 7 mm along the palmar normal (the plane of wrist, index MCP, pinky MCP, signed
  away from the camera on all 254 frames). Cosmetic: it sets where the string emerges behind the
  finger (~35 px behind the landmark at this depth); item 04 gives the fingertip's depth.
- **Smoothing**: the fist gap is bridged with a cubic Hermite in 3D (the puppet is behind the
  fist then and every string is slack, so only continuity matters); a 5-frame median removes
  tracker spikes (none found on this shot), a Savitzky-Golay window 7 order 2 smooths (median
  residual 1.0 mm; 2.6 mm on the snap-open frames 41–44, which stay sharp; a 30 mm residual at
  frame 195 where the index moves fast).

## 2. The figure

An artist's-mannequin marionette, 11 rigid bodies (pelvis, chest, head, upper arms, forearms
with the hands, thighs, shanks with the feet), capsules and ellipsoids, built in
`puppet_model.py` from these numbers:

| quantity | value | source |
|---|---|---|
| height | 15 cm | design choice, rank 1 below |
| mass | 55 g | item 01: three built, weighed 29.5–31.2 cm marionettes at 214–314 g (Chen et al., NTU); by volume 27–39 g at 15 cm, kept heavier for a solid "crystal" figure |
| segment masses | de Leva 1996 Table 4, male (head 6.94 %, trunk 43.46 %, upper arm 2.71, forearm 1.62, hand 0.61, thigh 14.16, shank 4.33, foot 1.37) | `references/marionette/data/02-segment-parameters.csv` |
| segment lengths | Drillis & Contini 1966 fractions of stature (shoulder 0.818, hip 0.530, knee 0.285, ankle 0.039, upper arm 0.186, forearm 0.146, hand 0.108, biacromial 0.259) | from memory; cross-checked in the same CSV against Fromuth 2008 (0.820, 0.528, 0.284, 0.038, 0.193, 0.151) |
| trunk split pelvis / chest | 0.257 / 0.743 of the trunk | de Leva's lower vs middle + upper trunk, from memory |
| joint ranges | hips 70°, shoulders 110°, neck 40°, waist 30° cones; knees, elbows 0–140° | design choice: item 02 found no numeric range for marionette joints anywhere (leather-strap knees, cloth stops at Yamane 2003's shoulders); human ranges are the bound |
| joint damping | 5e-5 N m s/rad, Coulomb 5e-6 N m | item 02: no measured value; start at the critical damping of each joint's own pendulum mode (c = 2√(I m g d) ≈ 5e-5 for the thigh) and tune; air drag alone (0.006–0.01 per swing, measured on pendulum balls) cannot settle a marionette |
| air | ρ 1.2 kg/m³, μ 1.8e-5 Pa s, MuJoCo's inertia-box fluid model | CRC Handbook values |

## 3. The strings

Five spatial tendons from mocap bodies at the pads to sites on the figure, `limited="true"
range="0 L"`, stiffness 0: MuJoCo's documented "cable" behaviour, force only when stretched
(item 02 quotes the doc; Johnson & Murphey 2007 model marionette strings the same way and reject
spring chains). Limit compliance `solreflimit="0.004 1"` (time constant 4 ms ≥ 2 × the 1/1200 s
step, the documented rule; damping ratio 1: a thread with almost no give). Tendon damping
0.002 N s/m, assumed tiny.

**Mapping** (item 01's recommendation, which the plan's default anticipated): middle finger → the
head top (the reference string every tradition attaches first), index and ring → the shoulders
(the weight-bearing pair), thumb and pinky → the hands (the mobile, gestural pair). A different
mapping is one edit in `puppet_model.STRINGS`.

**Lengths** are set at a reference frame where the figure hangs upright with its head-top site
7 cm under the middle pad and every string just taut: frame 120, a typical mid-shot hand ("wide,
drifting down"). With the snap-open's highest, widest hand (48) as the reference every later pose
was slacker and the settled figure hung from one shoulder string. Result: thumb 22.1, index 9.1,
middle 7.0, ring 10.9, pinky 20.5 cm. The hand strings are long because the thumb and pinky sit
far out at the reference; when the fingers close they go slack and the arms hang, when they
spread they pull the arms out (decision 3 in `PLAN.md`).

**The release.** The figure is in the fist until frame 41, the first frame the tracker sees the
open hand (the fist starts opening at 40). It is released upside down, its head-top site at the
middle fingertip pad (1.2 cm behind the finger) and its folded body up behind the fingers: every
string is slack there (3.7–12.5 cm), it tumbles out head first and the head and shoulder strings
right it as it falls. Why not the palm centre: the head string is 7 cm and the middle pad is
8.8 cm below the palm centre, so a figure behind the palm is over-length the moment the hand is
open; released there it was yanked at 75 times its weight instead of falling, and a figure
lowered until slack hung under the fingertips before it ever dropped.

**The slack string on screen** is the catenary for its length between its two endpoints
(closed form: a from 2a·sinh(h/2a) = √(L² − v²) by Brent's method); a taut one is straight.
Item 03 (not yet run) is to confirm the form and the sag's visibility at this thread mass.

## 4. What the physics prints before any frame is rendered (`puppet_sim.py`, run 2026-09-11)

| check | value | expectation |
|---|---|---|
| free fall until the first string goes taut | 0.122 s (middle string, 5.8 cm of slack) | √(2h/g) = 0.109 s; the body unfolds and swings, so slightly longer |
| peak string tension at the snap | 12.9 N at frame 44.7 = 24 × the weight | an inelastic snap along the string (item 02); a real thread's jerk |
| tension minimum over the run | 0.000 N | ≥ 0 always: a string cannot push |
| quietest hang (frame 107) | taut index, ring, pinky; Σ tensions 0.625 N vs weight 0.540 N (1.16) | = 1 at rest; 1.16 because the fingers are still moving it |
| dominant sway of the centre of mass (frames 60–160) | 0.67 s | 2π√(L/g) with L = pads-to-COM 16.0 cm: 0.80 s (driven by the fingers, so within 30 %) |
| worst hinge overshoot past its limit | 3.1° (18° before the joint limits were stiffened) | soft limits |
| fastest body | 1.84 m/s | the snap and the hoist |
| the feet's lowest point in the frame | 1678 px of 1920 (frame 119) | inside the picture, under the caption band |

## 5. The look (item 06's pass list, `render_puppet.py`)

MuJoCo renders depth and a per-body ID at 2× (2160×3840); normals come from the depth by central
differences gated by the body ID; each pixel is shaded in linear light as an emissive body
(colour × (0.22 + 0.45 Lambert + 0.45 thickness gradient)) plus a wide rim ((1 − n·v)³ × 2.0,
item 06: Schlick's exponent 5 is physical, 2–3 the stylised wide rim) and a specular ((n·h)⁸⁰ ×
1.5); the strings are 1.5 px cores; sub-frame samples inside a 1/60 s shutter are averaged (one
per pixel of motion, up to 8); the layer is downsampled to 1080×1920, composited over the plate
behind the hand matte, bloomed (Gaussian σ 3, 9, 27, 81 px, weights 0.22, 0.12, 0.07, 0.04; item
06: 0.03–0.15 for a whole game frame, more here since only the emissive subject is bloomed and
the wide levels are the spill on the wall), soft-shouldered above 0.8, and given the plate's own
grain (linear std 0.0025) on the figure's pixels. Two earlier passes are recorded in the file's
docstring: 0.30 ambient + 0.45 core read as a flat pale blob, 0.12 ambient + 0.55 Lambert as a
dark plastic toy.

## 5b. The second look: solid red (2026-09-12, Dennis: "very bright, loses focus against the white wall")

Item 09 (`references/marionette/09-colour-salience-figure-ground.md`) quantifies the complaint and
sets the fix:

| quantity | value | source |
|---|---|---|
| wall (#F2F0EA) luminance | Y 0.871, L* 94.8 | computed from the plate, sRGB → linear |
| neon cyan with the bright rim vs the wall | Weber −6 %, Michelson 0.03 | item 09: the reason it "loses focus" |
| pure red #FF0000 vs the wall | Y 0.213, L* 53.2; Weber −76 %, Michelson 0.61 | item 09 |
| the hue | saturated red | Elliot & Maier 2014 (attention and arousal); Bakhshi et al. 2015 (warm, high-contrast photos: +21 % views, +45 % comments) |
| the edge | dark or absent, never a bright bloom | bloom is veiling luminance: on a bright wall it lifts the wall toward the figure and collapses the edge (item 09); form comes from luminance contrast, not chroma (Livingstone & Hubel 1988) |
| the 3D read | one directional key light, a few sharp speculars | Kleffner & Ramachandran 1992; Fleming, Dror & Adelson 2003 |
| the strings | 3 px at 1×, saturated (dark against the wall) | 1 px is 0.79 arcmin at 30 cm on a 6-inch phone, far above the line-detection threshold; contrast polarity is what makes a thin line visible (item 09) |

The `solid` style in `render_puppet.py`: E = c × (0.18 + 0.82 Lambert) × (1 − 0.55 edge) + a small
specular, the maximum channel held at 0.72 (nothing clips to white; the rendered red lands near
crimson, L* ≈ 47, item 09's fallback), the near bloom only. The five candidates (red, magenta,
electric blue, green, orange) are on `hand/work/solid_sheet.png`; red and magenta read strongest by
eye and the literature picks red.

## 6. Ranking of the assumptions (what moves the picture most)

1. **The puppet's size (15 cm) and the head string (7 cm)**: pure design choices that set the
   composition; the physics is the same at any size except through air drag.
2. **The hand-length norm (19.3 cm)**: scales every metre; changes nothing on screen (the render
   is in the hand's own scale) but every number quoted in centimetres.
3. **Joint damping and friction**: no measurement exists (item 02); set near the legs' critical
   damping so the figure settles in seconds. More damping = a stiffer, deader puppet.
4. **The release pose and place**: chosen so the drop is a fall, not a yank; the first 0.2 s of
   the puppet's life on screen depend on it.
5. **The string mapping**: item 01's recommendation; the alternative (thumb + index on the
   shoulders) is one edit.
6. **The look constants**: judged on Dennis's screen, not measured; the sources give ranges.
7. **The focal length (1600 vs 1441 px)** and **the pad offset (7 mm)**: a few pixels.
