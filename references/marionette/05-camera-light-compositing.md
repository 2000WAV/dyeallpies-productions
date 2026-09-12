# Item 5 — Camera, light and compositing

Shot: iPhone 14 (base model, main 12 MP camera, 26 mm equivalent), 1080p 30 fps
HDR (HLG, 10-bit), handheld, 9 s, man's right hand from the back seen from
~0.3–0.4 m, fingers pointing down, plain off-white wall behind, soft shadow
lower-left (window light). A CG "neon" marionette (~18 cm) will be rendered
offscreen (MuJoCo depth + segmentation, shaded in NumPy) and composited into the
tone-mapped SDR 1080×1920 plate, hanging from the fingertips.

All files referenced below live in `references/marionette/papers/` (full text or
saved page) and `references/marionette/abstracts/` (summaries of the academic
papers); see `downloads-05.md` for the URL/licence/date of every download.

---

## 1. Camera: sensor, focal length, field of view, distortion, rolling shutter, shutter, HDR pipeline

### 1.1 What Apple actually publishes

Apple's own iPhone 14 tech-specs page (`apple-iphone14-techspecs.txt`) and the
Wikipedia iPhone 14 spec table (`wikipedia-iphone14.txt`, itself sourced from
Apple) agree:

- Main (wide) camera: **12 MP, 26 mm (35 mm-equivalent), f/1.5**, sensor-shift
  optical image stabilization, 100% Focus Pixels (dual-pixel autofocus).
- Ultra-wide: 12 MP, 13 mm equivalent, f/2.4, 120° FOV (not used in this shot).
- Video: 1080p HD at 25/30/60 fps; 4K Dolby Vision at 24/25/30/60 fps; **"Lens
  correction"** is listed only for the Ultra Wide camera, implying Apple does
  not consider the main lens's native geometric distortion significant enough
  to need software correction for normal (non-ultra-wide) shooting.
- Cinematic video stabilization applies at 4K, 1080p and 720p; GSMArena's
  review (`gsmarena-iphone14-review-video.txt`) confirms the main camera has
  both EIS and OIS, and that the iPhone 14 was the first generation to expose a
  toggle to disable EIS in Camera settings — i.e. EIS-with-crop is the
  **default** state for ordinary video capture, which is what we assume Dennis
  shot in.

Apple does **not** publish sensor physical size, pixel pitch, actual (non-
equivalent) focal length, or fx/fy in pixels for any capture mode. Those have
to come from teardown/measurement sources and be derived.

### 1.2 Sensor size and pixel pitch (teardown sources; NOT from Apple)

- `4sense-iphone14-sensors.txt` (teardown-based technical write-up): the
  iPhone 14/Plus main rear camera uses a sensor with **1.9 µm pixel pitch**,
  up from 1.7 µm on the iPhone 13 base model, and appears to be a reuse of the
  iPhone 13 Pro/Max's main sensor design (both are 12 MP with masked PDAF).
- `howtogeek-iphone-photo-resolution.txt`: standard iPhone photo output is
  **4032×3024 px** (12 MP, 4:3) — this has been the iPhone's native still
  resolution across many generations and matches the 12 MP main camera here.
- DXOMARK's own iPhone 14 test page (`dxomark-iphone14-camera-test.txt`)
  states "12MP **1/1.9-inch** sensor, **24mm equivalent** f/1.5 lens" — this
  **conflicts** with Apple's 26 mm and with the 1.9 µm/1/1.65"-class pixel
  pitch reported by the teardown source. Looking at the same DXOMARK overview
  panel, its Ultra-wide line *also* says "24mm equivalent," which is wrong
  (Apple states 13 mm) — the panel is internally inconsistent, so it is
  **discounted** here in favour of Apple's own 26 mm spec plus the independent
  teardown's pixel-pitch figure.
- `techinsights-iphone14-image-sensor.txt` is a real teardown report but only
  covers the **iPhone 14 Pro/Max** (Ultrawide 1.4 µm, Telephoto 1.0 µm,
  LiDAR); it does not cover the base iPhone 14's main sensor, so it is used
  only as generation/methodology context, not as a source of the base-model
  number.
- NOT FOUND: an iFixit- or TechInsights-grade teardown report that states the
  base iPhone 14 main sensor's *physical size* (e.g. "1/1.65 inch") in so many
  words in a file we could save. The 1/1.65" figure recurs across many
  secondary sources (not archived here because they were Cloudflare-blocked or
  bot-blocked — see `downloads-05.md`), and is consistent with computing the
  format from the pixel pitch and native resolution below, so it is used as a
  **derived**, not directly cited, number.

### 1.3 Pinhole model: deriving focal length in mm and pixels (derived by this project)

Using only the two numbers above that come from independent, saved sources
(26 mm-equivalent from Apple; 1.9 µm pixel pitch and 4032×3024 px from the
teardown/resolution sources):

```
sensor width  = 4032 px * 1.9 µm = 7.661 mm
sensor height = 3024 px * 1.9 µm = 5.746 mm
sensor diag   = sqrt(7.661² + 5.746²) = 9.576 mm

crop factor   = 43.27 mm (full-frame diagonal) / 9.576 mm = 4.52x
actual focal length = 26 mm / 4.52 = 5.75 mm

fx (native, 4032 px wide) = 5.75 mm / 1.9 µm = 3026 px
```

This 4.52x crop factor and ~5.75 mm actual focal length are **not themselves
confirmed in any single saved source** — they are this project's own
computation from the two Apple/teardown numbers above. As an informal sanity
check (not a citation), unrelated secondary write-ups about the iPhone 13
Pro/14-class main camera describe "5.7 mm actual, 26 mm equivalent, ~4.5x crop
factor," which is consistent with the derivation to within rounding.

**At 1920×1080 (1080p) output**, two more steps are needed, both flagged as
assumptions because Apple does not publish the exact sensor readout window per
video mode:

1. **Video crop to 16:9.** Assume the video pipeline keeps the sensor's full
   *width* and crops only the *height* to 16:9 before downscaling to 1920 px
   wide (a common assumption for phone sensors, since it maximizes horizontal
   FOV, matching how Apple frames photo vs. video previews in the Camera app).
   Scale factor to 1920 px: 1920/4032 = 0.4762.
   `fx (1920 px, no stabilization) = 3026 * 0.4762 ≈ 1441 px`

2. **Stabilization crop.** `iphonelife-disable-stabilization.txt` documents
   (with paired framegrabs, IS-on vs IS-off, on an earlier iPhone) that
   enabling image stabilization **reserves the outer 10% of pixels of the
   sensor in both dimensions** — i.e., stabilized video only uses the inner
   90% of what would otherwise be captured. This 10%-both-dimensions figure
   is widely repeated in iPhone videography commentary through the iPhone 14
   era; GSMArena's review confirms the iPhone 14 has EIS enabled by default
   with an explicit toggle to turn it off. Applying this as a further ~1/0.9
   effective zoom:
   `fx (1920 px, with ~10% stabilization crop) ≈ 1441 / 0.9 ≈ 1601 px`

**Field of view**, from the same numbers (`FOV = 2*atan((dimension/2)/f)`):

| mode | horizontal FOV | vertical FOV | diagonal FOV |
|---|---|---|---|
| photo, full sensor (4032×3024) | 60.6° | — | 79.6° |
| 1080p video, full width, no stabilization | 67.4° | 41.2° | — |
| 1080p video, with ~10% stabilization crop (**recommended**) | **61.7°** | **36.9°** | — |

The 79.6° diagonal figure for photo mode happens to be close to an unconfirmed
79.52° figure that turned up in a paywalled Medium article
(`rjallain-iphone13-fov-medium.html` — only the metadata/teaser could be
retrieved, the body is member-locked) about the iPhone 13's angular FOV; that
article is **not** used as a citation for any number in this document, it is
mentioned only as an informal cross-check that the derivation is in the right
ballpark.

**Recommended pinhole intrinsics for the plate (1920×1080, stabilized video):**
`fx ≈ fy ≈ 1600 px`, principal point at the image center `(960, 540)` (no
measured decentring available — see §1.4), zero-to-negligible distortion (see
below).

### 1.4 Distortion

Apple's spec sheet applies "Lens correction" only to the Ultra Wide camera,
not the main lens — the main lens's native barrel/pincushion distortion is
implicitly small enough that Apple doesn't correct it in software for normal
photos. Combined with DXOMARK's and GSMArena's photo-quality write-ups
reporting no significant geometric distortion complaints for the main
camera, this project treats the main lens as **effectively distortion-free (k1,
k2, p1, p2 ≈ 0)** for a plain pinhole model at this focal length. NOT FOUND: a
numeric distortion coefficient (k1/k2) for the iPhone 14 main camera from an
actual checkerboard calibration — the one calibration paper we found that
targets an iPhone 14 (`isprs2025-smartphone-camera-calibration-iphone14.txt`)
reports only the *uncertainty* of the recovered parameters (see §1.5), not
their absolute values, likely due to a table/figure that didn't OCR cleanly
out of the two-column PDF.

### 1.5 What an actual iPhone 14 calibration paper reports

`isprs2025-smartphone-camera-calibration-iphone14.txt` (Copernicus/ISPRS 2025,
open access) calibrates a real iPhone 14 (their "iP14"; note the extracted
text mis-OCRs this as "iP10" / "iPhone 10" in places — a two-column PDF
extraction artifact, not a different phone) at **1920×1080, 30 fps**, using
Kalibr against four grid types (small/large AprilGrid, small/large
checkerboard) and two distortion models (radial-tangential, equidistant),
yielding 24 calibration configurations. Headline findings:

- The **standard deviation (uncertainty)** of the recovered focal length and
  principal point across configurations is roughly **1–2 px**.
- Different combinations of grid size/type and distortion model can shift the
  **recovered focal length by 50+ px** and the **principal point by 35+ px**
  between configurations — i.e., "the" fx of a phone camera is itself only
  known to within tens of pixels unless the exact calibration recipe is fixed.
- Grid *size* affects focal-length stability more than grid *type* or
  distortion *model* choice.

This is useful as an **error bar**: our analytically-derived `fx ≈ 1600 px`
(§1.3) should be treated as good to roughly ±50 px, not to single-pixel
precision, unless Dennis actually shoots a checkerboard with this phone and
calibrates it — which, given the ~1–2 px repeatability the paper reports for
a *fixed* calibration recipe, would settle the question far better than any
spec-sheet derivation.

### 1.6 Rolling shutter

NOT FOUND: a direct, measured rolling-shutter (full-sensor readout time)
number for the base iPhone 14. The best available analog is CineD's lab test
of the (newer, larger-sensor) **iPhone 15 Pro** (`cined-iphone15pro-rolling-
shutter.txt`), measured with a 300 Hz strobe:

| camera | readout time |
|---|---|
| main (24 mm) | 5.3 ms |
| ultra-wide (13 mm) | 4.7 ms |
| telephoto | 5.0 ms |
| front (selfie) | 9.3 ms |

CineD's own framing: "the rolling shutter is exceptionally good on the
iPhone 15 Pro... with around 5 ms for all cameras," better than most
mirrorless/cinema cameras except the Sony Venice 2. This is a **different
sensor generation** from the base iPhone 14, so it is used only as an
order-of-magnitude estimate (**~5–10 ms** full-sensor readout is a reasonable
assumption for the iPhone 14 main camera) rather than a hard number. For a
9 s handheld shot of a slow-moving hand, rolling shutter skew will be
essentially invisible regardless of whether the true value is 5 ms or 15 ms —
it only matters for fast horizontal motion or panning, neither of which
applies here.

General rolling-shutter mechanics (row-by-row staggered reset/read, skew
proportional to full-sensor readout time, worse for fast horizontal motion)
are documented in `horshack-rollingshutter-readme.md` (a compiled measurement
methodology and dataset covering mirrorless/cinema cameras, no phones) and
`medium-karlstarnaud-rolling-back-in-time.txt` (a mirror-and-clock measurement
of ~17 ms rolling shutter on an iPad, illustrating the classic measurement
technique).

### 1.7 Shutter speed / motion blur

The iPhone camera has no mechanical shutter or shutter-angle control;
exposure time is chosen automatically by the auto-exposure algorithm subject
to a hard ceiling of one frame interval. At 30 fps that ceiling is **1/30 s**
(33.3 ms); in a reasonably lit indoor room the auto-exposure algorithm will
typically sit somewhere between that ceiling and roughly **1/60 s**, per the
task brief's own framing of "auto exposure at 30 fps: 1/30–1/60 s." (NOT
FOUND: a saved source with a directly measured shutter speed for this
specific shot/lighting; the 1/30–1/60 s range is standard indoor-auto-
exposure behaviour, not degree-of-freedom-controlled by the shooter here, and
is retained from the task brief as the working assumption.) The general
non-applicability of the 180°-shutter-angle convention to phones (no
mechanical shutter disk to describe an "angle" of) is discussed in
`diyphotography-180-degree-shutter-rule.html`. For the CG motion-blur match
(§4), 1/30 s exposure at 30 fps corresponds to a **180° shutter angle
equivalent** — full-frame-time exposure, i.e. maximal (for this frame rate)
motion blur; 1/60 s corresponds to a 90° equivalent shutter, half as much
blur. Given the hand and shadow move very little over the 9 s clip, this
mostly affects fine sub-pixel softness, not visible smear.

### 1.8 HLG / Dolby Vision HDR pipeline

Apple's own developer documentation (`apple-hdr-dolby-vision-avfoundation.txt`,
*Incorporating HDR video with Dolby Vision into your apps*) states plainly:

> "The HDR video recorded with Dolby Vision is in **Dolby Vision Profile 8,
> Cross-compatibility ID 4 (HLG) format**... designed to be backwards
> compatible with HLG, as it allows existing HEVC decoders to decode as HLG.
> The codec type is **HEVC (10-bit)**."

`blackburnapps-iphone-sdr-hdr-video.txt` fills in the transfer-function and
color-space detail: Apple's Dolby Vision HDR recording (introduced on the
iPhone 12 Pro, carried forward to iPhone 14) encodes with the **Hybrid Log-
Gamma (HLG)** transfer function in the **BT.2020** color space at 10-bit,
supporting an encodable contrast ratio of roughly **3,145,000:1**, versus
985:1 for default 8-bit BT.709 SDR video. 10-bit encoding is specifically
needed to avoid visible banding in HLG's much wider range. This matches the
task's description of the plate as "1080p 30 fps HDR (HLG, 10-bit)" — i.e.
the phone captured the extended-range HLG/BT.2020 signal that this project
then tone-maps down to the SDR 1080×1920 plate before compositing.

**Practical implication for compositing:** since the plate is delivered/used
as tone-mapped SDR, the marionette render should be shaded and tone-mapped to
match the *already-tone-mapped* plate's gamma/contrast curve (§4), not to
HLG's own OETF — by the time compositing happens, the "HDR" nature of the
source only matters insofar as it gave the tone-mapping step more highlight
detail to preserve than an SDR-only capture would have.

---

## 2. Estimating the light from the hand's shadow on the wall

### 2.1 The theory: shadows encode light direction, angular size and object distance

- **Sato, Sato & Ikeuchi 2003, "Illumination from Shadows"**
  (`sato2003-illumination-from-shadows.txt`) is the foundational reference for
  recovering a scene's illumination *distribution* from brightness measured
  **inside** a shadow cast by an object of known shape: because the object
  occludes different incident-light directions at different shadow pixels,
  the pattern of residual brightness inside the shadow is a linear system in
  the unknown per-direction radiances. This is more machinery than our single
  soft edge needs (we only need light direction + angular size, and the
  hand's shape is already known from the shot), but it is the rigorous basis
  for "read the light from its shadow."
- **Panagopoulos et al. 2009 / 2011**
  (`panagopoulos2009-shadow-illumination-mixture-model.txt`,
  `panagopoulos2011-illumination-shadow-higher-order.txt`) extend this to a
  single ordinary photo with only *coarse* 3D geometry, using a graphical
  model (a mixture of von Mises–Fisher lobes for the illumination, tied to
  shadow evidence via an MRF). Useful background for "no calibration target,
  no precisely known occluder," which is closer to a real production
  scenario, but again heavier machinery than this shot needs.
- **Lalonde, Efros & Narasimhan 2009 (conference) / 2012 (journal)**
  (`lalonde2009-natural-illumination-outdoor-iccv.txt` — the IJCV 2012 journal
  version is paywalled at Springer and its listed alternate host had moved to
  a different site by the time of this research; the ICCV 2009 conference
  version, freely mirrored by CMU, was archived instead and covers the same
  method) combine several weak shadow/shading cues plus a data-driven prior
  over millions of photos to estimate sun position from a single outdoor
  image, and demonstrate consistent synthetic-object insertion. Same
  "read the light back out of one photo" idea, at outdoor/sun scale.

### 2.2 The practical relation actually used here: PCSS penumbra geometry

For a single, known, soft light source (the window) casting a single object's
(the hand's) shadow onto a single flat receiver (the wall), the classical
real-time-graphics relation is simpler and directly invertible.
**Fernando 2005, "Percentage-Closer Soft Shadows"**
(`fernando2005-percentage-closer-soft-shadows.txt`) gives it via similar
triangles (assuming occluder/receiver/light are roughly parallel, and the
light is a disk of angular size `w_light`):

```
w_penumbra = w_light * (d_receiver - d_blocker) / d_blocker
```

where distances are measured from the light to the receiver (wall) and to the
blocker (hand) respectively. **Inverted for this shot:** measure the
penumbra width in the plate (the soft edge of the hand's shadow on the wall,
in pixels, converted to real-world mm via the pinhole model + known hand-to-
wall distance), and:

- If the **hand-to-wall distance** is known (it should be, roughly, from the
  shot setup: the task brief gives ~0.3–0.4 m from the lens to the hand, and
  the wall is a few tens of cm further back — measure this from the footage
  by comparing the hand's known real width, e.g. ~8 cm palm width, against its
  pixel width, then using the pinhole model to get absolute depth), solve for
  the window's **angular size** `w_light`.
- Conversely, if the light's angular size can be estimated independently
  (e.g. from the window's real size and its distance from the wall, if that's
  known or guessable), solve instead for the **hand-to-wall distance**.

These two are **degenerate from a single frame** unless one of the two is
pinned down some other way — flagged explicitly here so the recipe in §5
states which one to fix.

**Light direction** itself is read directly off the shadow's offset (the
vector from the hand's ground-contact point, or its nearest point to the
wall, to the darkest part of the umbra): the shadow points away from the
light, so its 2D offset direction on the wall plane, combined with the known
hand-to-wall distance, gives the 3D direction to the (window) light source,
consistent with the brief's "lit from the lower left, a window."

### 2.3 Shadow-catcher / shadow-matte compositing for the CG object

For the CG marionette to (optionally) cast a consistent secondary shadow onto
the same wall — or, more simply, to receive occlusion from the real hand
correctly — the standard VFX technique is a **shadow catcher / shadow matte**:
a proxy plane (the real wall, at its measured position and orientation)
receives the CG object's shadow in an otherwise-invisible "matte" render pass,
which is then **multiplied over the plate** rather than composited normally.
This is documented across current production tools (V-Ray's Shadow Catcher
material/wrapper, Redshift's/Houdini's/Maya's/Unreal Composure's matte-shadow
tooling) with the common recipe of two renders — one with the CG object
present, one without — whose ratio (or, equivalently, a dedicated shadow-only
AOV) is multiplied onto the plate so the plate's own floor/wall texture shows
through, darkened only where the CG object would cast a shadow. For this
shot, where the marionette *hangs from the fingertips in front of* the wall
rather than sitting on it, this matters only if the neon marionette is meant
to visibly darken the wall (e.g. by blocking ambient light) — which is a much
smaller effect than the marionette's own emissive glow (§3) adding light to
the wall, so the shadow-catcher pass is a nice-to-have, not the primary
compositing concern here.

---

## 3. Emissive / neon lighting spill and bloom

### 3.1 Light spill onto the real plate ("light wrap" and additive glow)

Two related but distinct compositing conventions, both catalogued in the
standard VFX-compositing textbooks:

- **Light wrap**: takes a blurred/dilated version of the *background* plate
  and additively blends a thin rim of it around the composited foreground
  element's edge, simulating the way a bright background's light physically
  wraps a few millimetres around a real foreground object's silhouette (an
  effect a hard-edged digital composite never has by default). For a
  *self-emissive* object like the neon marionette, the effect runs the other
  way as well: a thin rim of the marionette's own glow color should wrap onto
  the nearest real-world surfaces (the fingers holding it, the wall behind
  it) at falloff proportional to inverse-square-ish distance, which is what
  makes the neon object look like it's actually leaking light into the room
  rather than sitting on top of the footage.
- **Additive glow with distance falloff**: the emissive object's own bloom
  halo (see §3.2) is composited with an **additive** (not "over") blend, and
  a secondary, larger, softer, dimmer additive pass — its "spill" —
  contributes a subtle color cast and lift to nearby real pixels (the
  fingers, the wall patch nearest the marionette), falling off with distance.
- Both conventions are named and described in Ron Brinkmann's **"The Art and
  Science of Digital Compositing"** and Steve Wright's **"Digital Compositing
  for Film and Video"** — the two standard VFX-compositing references named
  in the brief. **NOT FOUND**: legally obtainable full text of either book
  online (ScienceDirect's book page returned a server error, O'Reilly's
  redirected to a login-only page, and no open PDF exists); both are cited
  bibliographically only, via their publisher listings
  (`googlebooks-wright-digital-compositing.html`) and via publisher/second-
  hand-bookseller marketing copy that confirms the relevant section titles
  exist in each edition — Brinkmann's book is confirmed (by its own marketing
  copy) to include dedicated sections titled "Light Wrapping," "Shadows,"
  "Digital Color Matching," and "Spill Suppression"; Wright's 2nd edition is
  confirmed to include "the add-mix composite, light wrap," and "Premultiply
  vs. Unpremultiply." Practical technique write-ups covering the same ground
  in the open literature are archived instead:
  `therookies-integrating-cgi-live-action-plate.txt` and
  `creativebloq-integrate-cg-live-action.txt`, both of which describe light
  wrap, edge treatment, grain, and lens-quality matching for exactly this
  kind of CG-into-live-action integration.

### 3.2 Bloom implementation

- **Kawase's bloom filter** (Masaki Kawase, GDC 2003, *DOUBLE-S.T.E.A.L.*):
  documented in detail, including the exact 3×3 downsample kernel weights
  (a binomial `1/16, 2/16, 4/16` pattern) and HLSL source, in Chris Oat's
  contemporary GDC Europe 2003 talk (`oat2003-realtime-3d-scene-
  postprocessing.txt`). The technique: repeatedly downsample-and-blur with
  this small kernel, "ping-ponging" between two render targets, so that a few
  cheap small-kernel passes at progressively coarser resolutions approximate
  a very wide, expensive single-pass blur.
- **Dual filtering** (Marius Bjørge, ARM, SIGGRAPH 2015,
  `bjorge2015-bandwidth-efficient-rendering-dual-filter.txt`): a bandwidth-
  optimized reformulation for tile-based (mobile) GPUs — a small
  downsample-blur kernel while progressively halving resolution, then a
  small upsample-blur kernel while doubling back up. The talk's own
  performance chart (Mali-T760 MP8) shows dual filtering running at roughly
  2–3 ms per 1080p frame versus 20–40+ ms for naive box or 5×5-Gaussian
  iterative approaches (exact bar-to-label mapping in the source chart is
  approximate, since it was extracted from a figure rather than a table).
  This downsample/upsample-chain approach is the one recommended for an
  offline NumPy compositor too: a handful of successive 2× box-downsamples
  each followed by a small blur, then successive 2× bilinear upsamples summed
  back together, gives a smooth wide glow far more cheaply than a literal
  large-radius kernel.
- **Physically-based bloom** (`learnopengl-physically-based-bloom.txt`,
  crediting Jorge Jimenez's SIGGRAPH 2014 "Next Generation Post Processing in
  Call of Duty: Advanced Warfare" talk): the modern recommendation is to
  **skip the brightness threshold** and instead downsample/blur the *entire*
  HDR image, then blend the blurred "bloom buffer" back with the sharp buffer
  using a **linear interpolation strongly biased toward the sharp image**
  (Jimenez's own quoted bias value is **~0.04** toward the blurred layer).
  Thresholding is explicitly called out as producing "washed-out," low-
  contrast results with visible banding at the cutoff and doesn't reflect how
  real lenses/eyes bloom (which affects *everything*, just more visibly on
  bright objects). For the neon marionette — which is emissive/HDR by
  construction, unlike the SDR-tone-mapped plate around it — this threshold-
  free approach is directly applicable: render the marionette (plus a little
  of its immediate surroundings) at HDR, blur without thresholding, and blend
  back with a small bias, before compositing that combined result onto the
  SDR plate.

### 3.3 Reading as solid and 3D, not a flat glowing blob

A glowing CG object reads as *lit and three-dimensional* rather than a flat
emissive cutout when the render includes, layered under the bloom:

- **An internal gradient** — brighter toward the object's core/thicker
  sections, dimmer toward thin extremities — so the glow itself has volume,
  not a uniform flat color.
- **Rim/fresnel lighting** — a brighter edge where the surface normal grazes
  the view direction (the classic Schlick's-approximation-style fresnel
  falloff), which is what most strongly sells silhouette/volume for a glowing
  object, since it's often the *only* shading cue visible on an otherwise
  self-lit surface.
- **A specular highlight** (even on an "emissive" material, a small hard
  specular hint keyed to the real scene's light direction — here, the
  lower-left window — ties the CG object into the same lighting environment
  as the real hand and wall, which is otherwise all diffuse/ambient for a
  pure-emissive shader).
- **Self-occlusion / ambient occlusion** in the crevices and joints of the
  marionette (string attachment points, joint sockets) — without any
  darkening in concave areas, an emissive object looks like a paper cutout
  rather than a solid volume; occlusion (from the MuJoCo depth pass this
  project already renders) is exactly what supplies this.

These four items (gradient, rim/fresnel, specular, occlusion) are the
standard checklist named in the compositing literature; specifics of fresnel
and rim-light shader math are covered by the item-6 (rendering/shading)
reference set already archived in this shared folder rather than duplicated
here (see e.g. `wikipedia-schlicks-approximation.html`, `lettier-fresnel-
factor.html` already present in `papers/`).

---

## 4. Matching CG to the phone footage

Checklist, synthesized from `therookies-integrating-cgi-live-action-plate.txt`,
`creativebloq-integrate-cg-live-action.txt`, and the alpha-compositing
fundamentals in `wikipedia-alpha-compositing.txt`, cross-referenced against
the camera/HDR facts established in §1:

1. **Color / gamma.** The plate is delivered tone-mapped from HLG/BT.2020
   10-bit down to an SDR curve (§1.8). The marionette render must be tone-
   mapped through the **same** curve, not rendered "flat" sRGB/Rec.709 and
   merely eyeballed to match — otherwise the neon's highlight rolloff will
   look mathematically different from the plate's rolloff even if the colors
   are picked to match in the midtones.
2. **Grain / noise.** Real sensor noise is **signal-dependent (heteroscedastic)
   and varies per color channel**, not flat Gaussian —
   `cao2023-physics-guided-iso-noise-modeling.pdf` (CVPR 2023) models it as a
   physically-motivated mixture (photon shot noise + read noise + banding +
   quantization) with parameters that vary by ISO and by Bayer/CFA channel.
   Even though this shot is well-lit rather than extreme-low-light, adding
   *flat* Gaussian grain to the CG render will look subtly wrong under close
   inspection; matched grain should (a) scale with the local brightness of
   the composited pixel and (b) differ slightly per channel (blue channels
   are typically noisiest). Practically: measure the plate's own noise
   per-channel in a flat region (e.g. the wall) at a few brightness levels,
   fit a simple `variance ≈ a + b*signal` model per channel, and synthesize
   matching noise on the CG layer before the final "over."
3. **Softness (lens MTF).** The real lens has some maximum resolvable detail
   set by its MTF; a raw MuJoCo/NumPy render will typically be sharper than
   what the phone's lens+sensor+HEVC pipeline actually resolves. A small
   match-blur (even a 1-pixel-radius Gaussian at 1080p) on the CG layer
   before compositing is the standard fix, called out explicitly in the
   practical integration write-ups (`therookies-integrating-cgi-live-action-
   plate.txt`: "renders that look too sharp and clean often give away that
   something is CG").
4. **Motion blur.** Per §1.7, the plate's effective exposure is
   1/30–1/60 s at 30 fps (a 90°–180° shutter-angle equivalent). The
   marionette render should carry matching per-frame motion blur (MuJoCo can
   supply sub-frame poses to accumulate/average, or a cheap per-frame
   velocity-buffer blur can approximate it) — although given the hand and
   marionette move slowly in this shot, this is a secondary-priority match
   compared to color/grain/softness.
5. **Chromatic aberration.** Real phone lenses show a small amount of
   lateral CA (color fringing) toward the frame edges; since the marionette
   sits near frame-center in a fingertip-hanging shot, this is a low-priority
   item here, but if it's added, it should be applied consistently with
   whatever (small, likely negligible per §1.4) CA the real plate shows near
   frame edges — not invented independently.
6. **Standard checklist items** (from the alpha-compositing and integration
   references): work in **linear light**, not display-gamma-encoded values,
   when applying the "over" operator (`C_out = alpha*F_linear + (1-alpha)*
   B_linear`, per the Porter–Duff formulation documented in
   `wikipedia-alpha-compositing.txt`); keep the CG layer's RGB **premultiplied**
   by its own alpha before any blur/resize operation (blurring straight/
   unassociated alpha independently from color produces dark or bright
   fringing at the edges — "no halo"); match **black levels** (a CG render's
   truest black is usually darker than a real camera's noise-floor black);
   and treat **edge treatment** (§5) as inseparable from the matte quality
   (§5) — a technically correct color/grain/blur match is undone by a bad
   edge.

**Recommended compositing order** (bringing §§2–4 together):
`(pinhole-projected + lit/shaded CG render, premultiplied) → additive glow/
bloom (threshold-free, biased blend, §3.2) → light-wrap/spill onto plate
pixels near the object (§3.1) → grain match (§4.2) → softness/MTF match
(§4.3) → motion blur match (§4.4) → premultiplied "over" onto the plate in
linear light (§4.6) → final tone curve already shared with the plate (§1.8/
§4.1), so no further grade needed on the composited region alone.`

---

## 5. Hand matting on the plain wall

### 5.1 Classical techniques

- **Smith & Blinn 1996, "Blue Screen Matting"**
  (`smithblinn1996-blue-screen-matting.txt`) formalizes the compositing
  equation `C = alpha*F + (1-alpha)*B` and the classical (Vlahos-style)
  single-backing-color solutions, and is explicit about why a single known
  backing color under-constrains the problem (3 known channel equations vs. 4
  unknowns — alpha plus premultiplied F's 3 channels — per pixel), requiring
  either a second known backing color or an assumption restricting F's
  chrominance. **Vlahos's own historical technique**
  (`wikipedia-chroma-key.txt`) exploits the fact that most real-world subject
  colors have similar blue and green channel intensities, unlike a blue or
  green backing — for our off-white wall (not a saturated backing color),
  this exact assumption doesn't directly apply, but the underlying idea —
  **difference/luminance keying against a known, nearly-uniform background
  color** — carries over directly: the off-white wall is nearly constant in
  hue and lightness, so a per-pixel difference from a measured/modeled clean
  wall-color plate (ideally an empty-wall reference frame, or a per-frame
  median/background estimate since the wall is static) gives a first-pass
  alpha, exactly analogous to a (very desaturated) chroma key.
- **Levin, Lischinski & Weiss 2008, "Closed-Form Solution to Natural Image
  Matting"** (`levin2008-closed-form-matting.txt`) derives the "matting
  Laplacian": under a local color-line assumption in small windows, the alpha
  matte linear in image colors can be solved for the *whole image at once*,
  in closed form, from only a sparse trimap or a few scribbles — no explicit
  foreground/background color sampling. This gives the highest-quality edges
  (fine finger silhouettes, any stray hair) of the classical (non-learned)
  methods, at the cost of a global sparse linear solve per frame.
- **Guided filter** (He, Sun & Tang 2010/2013,
  `he2010-guided-image-filter.txt` / `he2013-guided-image-filter-pami.txt`;
  fast variant He & Sun 2015, `he2015-fast-guided-filter.txt`) is a *local*,
  O(N)-time (or O(N/s²) subsampled) approximation to the same color-line
  idea: use the plate's sharp luma channel to "guide" the smoothing of a
  coarse/noisy alpha channel, snapping it back onto true edges without a
  halo, far more cheaply than the full matting Laplacian solve — the
  practical choice for refining a coarse matte across all ~270 frames of a
  9 s clip.

### 5.2 Learned mattes (trimap-free or trimap-guided)

- **Robust Video Matting (RVM)** — Lin et al. 2021/2022
  (`lin2022-robust-video-matting.txt`) — a recurrent (temporal) network that
  estimates alpha + foreground per frame **without** a trimap or known
  background, exploiting inter-frame temporal state for both speed (4K @
  76 fps / HD @ 104 fps on a GTX 1080 Ti) and **flicker reduction** — directly
  useful here since the hand is nearly static, so a naive per-frame matte
  would show visible frame-to-frame alpha jitter that RVM's recurrent state
  specifically suppresses.
- **MODNet** — Ke et al. 2020/2022 (`ke2020-modnet.txt`) — also trimap-free,
  decomposes the problem into semantic / boundary-detail / fusion
  sub-objectives with explicit per-branch supervision; runs at 67 fps
  (1080 Ti); its "detail branch" specifically targets clean matting of thin
  structures near boundaries, matching the down-pointing-fingers geometry of
  this shot.
- **ViTMatte** — Yao et al. 2023 (`yao2023-vitmatte.txt`) — a Vision-
  Transformer matting backbone with a lightweight convolutional detail-
  capture module, state-of-the-art on standard matting benchmarks at
  publication time, but (unlike RVM/MODNet) still **trimap-guided**, not
  fully automatic. It is included as an optional backend in the popular
  `rembg` background-removal tool.

### 5.3 What actually gives a sharp, halo-free edge on the fingers here

Given the specific geometry — a static, nearly-uniform off-white wall behind
a mostly-static hand, well inside a single 9 s clip — the recommended recipe
(spelled out fully in §6) is a **hybrid**: a coarse, fast, per-frame
difference-key/learned matte (RVM or MODNet — trimap-free, so no manual
rotoscoping) for the bulk of the silhouette, **refined with a guided filter**
against the plate's own luma channel to tighten the alpha onto the true
finger edges without introducing halos, rather than reaching for the full
matting-Laplacian solve (accurate, but the most expensive of the options, and
not obviously necessary once a guided-filter refinement is in the pipeline)
or a manual trimap-based classical key (unnecessary manual labor given how
uniform the background is).

---

## 6. Numbers for the pipeline

See `data/05-camera-numbers.csv` for the full machine-readable table (every
row cites its source file and flags derived/assumed values). Headline
figures:

| Quantity | Value | Status |
|---|---|---|
| Main camera, 35mm-equiv focal length | 26 mm | Apple spec (`apple-iphone14-techspecs.txt`) |
| Main camera aperture | f/1.5 | Apple spec |
| Sensor pixel pitch | 1.9 µm | teardown (`4sense-iphone14-sensors.txt`) |
| Native photo resolution | 4032×3024 px | `howtogeek-iphone-photo-resolution.txt` |
| Sensor size (derived) | 7.66×5.75 mm (9.58 mm diag) | derived |
| Crop factor (derived) | 4.52x | derived |
| Actual focal length (derived) | 5.75 mm | derived |
| **fx/fy at 1920×1080, stabilized (recommended)** | **≈1600 px** | derived; ±~50 px per ISPRS 2025 calibration spread |
| Horizontal / vertical FOV, 1080p stabilized | 61.7° / 36.9° | derived |
| Stabilization crop | 10% per dimension | `iphonelife-disable-stabilization.txt` |
| Distortion | negligible (main lens; no software correction applied by Apple) | inferred from Apple spec |
| Rolling shutter | ~5 ms order-of-magnitude (iPhone 15 Pro analog; NOT FOUND for base 14) | `cined-iphone15pro-rolling-shutter.txt` |
| Shutter / exposure | 1/30–1/60 s (30 fps auto-exposure ceiling = 1/30 s) | task brief + `diyphotography-180-degree-shutter-rule.html` |
| HDR pipeline | HLG, BT.2020, HEVC 10-bit (Dolby Vision Profile 8, CCid4) | `apple-hdr-dolby-vision-avfoundation.txt` |
| Penumbra-width relation | `w_p = w_light * (d_r - d_b) / d_b` | `fernando2005-percentage-closer-soft-shadows.txt` |
| Bloom kernel (Kawase) | 3×3 binomial, 1/16-2/16-4/16, iterated | `oat2003-realtime-3d-scene-postprocessing.txt` |
| Physically-based bloom blend bias | ~0.04 toward blur | `learnopengl-physically-based-bloom.txt` (Jimenez, SIGGRAPH 2014) |
| RVM matting throughput | HD 104 fps / 4K 76 fps (GTX 1080 Ti) | `lin2022-robust-video-matting.txt` |

---

## 7. Recommended recipe

### (a) The pinhole camera

- `fx = fy ≈ 1600 px`, principal point `(960, 540)` (image center; no
  measured decentring available), for the 1920×1080 stabilized plate.
- Zero distortion coefficients (main lens, not ultra-wide).
- Treat this fx as accurate to only **±~50 px** (§1.5) — if a sharper number
  matters later, shoot and Kalibr-calibrate a real checkerboard with the same
  phone/app/stabilization settings rather than trusting the spec-sheet
  derivation further.

### (b) The light and shadow estimate from the hand's shadow

1. From the plate, locate the hand's ground-shadow (or nearest-point-to-wall
   shadow) and measure its **offset** (gives light direction on the wall
   plane) and **penumbra width** (the soft-to-hard transition band at the
   shadow's edge).
2. Using the pinhole model (a) and an assumed/measured hand-to-wall distance
   (from the task's ~0.3–0.4 m hand-to-lens distance plus an estimate of
   wall setback), convert the penumbra's pixel width to real-world mm.
3. Solve Fernando's PCSS relation `w_penumbra = w_light*(d_receiver -
   d_blocker)/d_blocker` for the window's **angular size** `w_light` (fixing
   hand-to-wall distance as the known quantity, since that's the one this
   shoot's geometry pins down more directly than "how big is the window
   opening as seen from the hand").
4. Use the shadow-offset direction (already measured in step 1) plus the
   hand-to-wall distance to get the **3D direction vector** to the window
   light, consistent with "lit from the lower left."
5. Model the window as a soft area light of that direction and angular size
   for shading the CG marionette, so its own shading and cast shadow (if any,
   via a shadow-catcher pass, §2.3) are lit consistently with the real hand's
   shadow already visible in the plate.

### (c) The neon compositing order

`premultiplied CG render (linear light) → additive threshold-free bloom
(bias ~0.04 toward sharp, §3.2) → light-wrap / additive spill onto nearby
plate pixels (§3.1) → per-channel signal-dependent grain match (§4.2) →
lens-softness match-blur (§4.3) → motion-blur match (§4.4) → premultiplied
"over" onto the plate, composited in linear light → (no separate final grade
needed on the composited region, since both layers already share the plate's
tone curve from step 1).`

### (d) The hand matte

1. Run a trimap-free learned matte (RVM, for its temporal/flicker-reduction
   properties on this near-static hand) on the full clip.
2. Refine the resulting alpha per frame with a **guided filter**, guided by
   the plate's own luma channel, to snap the matte tightly onto the true
   finger silhouette without a halo.
3. Spot-check a handful of frames against a simple difference-key baseline
   (plate minus a modeled clean-wall reference) as a sanity check, since the
   wall is nearly uniform enough that a classical Vlahos-style difference key
   should agree closely with the learned matte almost everywhere except at
   the fine finger edges — large disagreements would flag a learned-matte
   failure worth inspecting.
