# Item 6 — Neon / emissive rendering and assets

For the ~18 cm CG marionette (capsules and ellipsoids simulated in MuJoCo), rendered as an
opaque "crystal / lighting"-style neon figure in blue/cyan/orange with glowing strings, then
composited onto the 9-second phone plate. This note covers what makes an emissive render read
as solid and three-dimensional rather than a flat glow, the concrete numbers used by real
bloom/fresnel/matcap pipelines, what MuJoCo's own renderer can and cannot do, the Windows
offscreen-rendering backends, alternatives for the beauty pass, and a short asset search.

Every number below is attributed to a file saved in `references/marionette/papers/` (or, for
two items already fetched by another research pass for this project, a file that already
existed there — `bjorge2015-bandwidth-efficient-rendering-dual-filter.pdf/.txt`). Where no
source was found, it says **NOT FOUND**.

## 1. What makes an emissive object read as solid and 3D, not a flat glowing blob

No single source states this as one list, but it is the consistent takeaway from combining the
VFX/bloom literature (below) with the matcap/fresnel shading literature (below): a convincing
"glowing but solid" object separates into layers that a flat blob only has one of.

1. **A saturated emissive core** — the object's own base colour, unlit, fully saturated. This is
   the "it glows" signal but by itself reads as a flat cut-out, because a flat card glows exactly
   the same way (own observation, consistent with the matcap literature's core caveat below).
2. **A brighter, whiter rim/fresnel term** — grazing angles (surface normal near-perpendicular to
   the view vector) are pushed towards white, following Schlick's approximation (Section 3). This
   is what tells the eye the surface is curving away from camera at the silhouette — it is the
   single strongest 3D cue for a smooth emissive object, because it is the one part of the shading
   that is a *function of the surface normal*, not just of material colour.
3. **A specular highlight** — a small, sharp, near-white hot spot from an implied key light,
   independent of the fresnel rim (fresnel is silhouette-wide; specular is a point). This adds a
   second, different normal-dependent cue and reads as "polished/crystal" rather than "diffuse
   glow" (`papers/lettier-fresnel-factor.txt`, `papers/digitalrune-matcap-shaders.txt`).
4. **An internal gradient (thicker = brighter, a fake subsurface/volumetric read)** — cheap
   "crystal" shading fakes refraction/subsurface by darkening or color-shifting toward the
   silhouette edge and brightening toward the visual center of a rounded volume (the opposite
   sense from the fresnel rim, which is why the two combine instead of cancelling): fresnel
   brightens the very edge pixels, the internal gradient brightens the perceived-thick middle,
   and together they read as a lit, extruded volume instead of a flat disc with a bright edge.
   This is the standard "crystal" shader recipe described qualitatively in matcap/toon-shading
   write-ups (`papers/digitalrune-matcap-shaders.txt`) — no numeric falloff is given by that
   source; NOT FOUND for a citable exponent, so the renderer should treat this term as an
   artistic gradient tuned by eye, not a physical constant.
5. **Ambient occlusion in the creases** — joints (where capsule meets capsule, e.g. elbow, knee,
   the string attachment points) need to visibly darken/desaturate, or the puppet reads as a set
   of glowing tubes floating past each other rather than a single connected body. MuJoCo's own
   renderer does not compute AO (Section 6); this has to be faked in the deferred/NumPy pass,
   e.g. from local curvature or a distance-to-neighbor-body term on the depth buffer.
6. **Bloom that falls off with distance from the source** — see Section 2 for the concrete
   filter shapes and numbers. Bloom is what sells "this is actually emitting light into a dark
   room," and doing it as a proper multi-scale blur (not a single blur radius) gives the
   "brighter parts bloom further" cue that a flat single-blur glow does not.
7. **Colour bleeding into the surroundings / onto the wall** — a large-radius, low-opacity
   version of the bloom colour screened onto the plate near the puppet and strings sells contact
   in the actual filmed environment; this is compositing, not shading, but is the step that
   convinces the eye the glow is really lighting the off-white wall rather than being pasted on
   top of the footage (synthesis from the Tron: Legacy VFX breakdown, Section 2.4, and from the
   physically-based-bloom argument in Section 2.2 that bloom is fundamentally light scattering
   into neighbouring pixels).

## 2. Bloom: history, filter shapes, and the numbers each source actually uses

### 2.1 Kawase's original filter (GDC 2003) — the historical root of "Kawase blur"

Masaki Kawase (Bunkasha Games) presented "Frame Buffer Postprocessing Effects in
DOUBLE-S.T.E.A.L (Wreckless)" at GDC 2003. The talk itself was not directly recoverable, but
Chris Oat (ATI Research) reproduced Kawase's method with attribution and working HLSL in his own
GDC Europe 2003 talk "Real-Time 3D Scene Post-processing," saved here in full
(`papers/oat2003-realtime-3d-scene-postprocessing.pdf/.txt`, 49 slides). Oat's slides show:

- Kawase's method **downsamples first** (quarter × quarter resolution, i.e. 1/16 area), then
  applies a small blur filter repeatedly, with **more iterations giving more blurriness**; each
  iteration ping-pongs between two render targets (`papers/oat2003-realtime-3d-scene-postprocessing.txt`,
  lines 179–198).
- The per-iteration filter samples the **four diagonal corner texels** around the destination
  pixel at an offset that grows with the iteration index (`iteration` parameter multiplies the
  pixel-size step), and **averages the four samples equally (×0.25)** — the actual HLSL is
  reproduced verbatim: `SiWrecklessBloomFilterRGB(sampler tSource, float2 texCoord, float2
  pixelSize, int iteration)`, sampling top-left/top-right/bottom-right/bottom-left and returning
  `cOut *= 0.25f` (`papers/oat2003-realtime-3d-scene-postprocessing.txt`, lines 210–218).
- A companion **3×3 separable-looking single-pass kernel** shown just before the iterative
  version uses weights `1/16, 2/16, 1/16 / 2/16, 4/16, 2/16 / 1/16, 2/16, 1/16` (a standard
  binomial/tent 3×3, i.e. the same shape LearnOpenGL later uses for bloom upsampling — Section
  2.2) (`papers/oat2003-realtime-3d-scene-postprocessing.txt`, lines 185–193).
- Oat's own slides (lines 30–75) show the classical **bright-pass + separable Gaussian** bloom
  used alongside Kawase's filter at the time: a 25-tap separable Gaussian (1 center + 6 inner +
  6 outer taps per direction, run horizontal then vertical) feeding into tone mapping.

### 2.2 "Dual Kawase" / dual-filtering (Marius Bjørge, ARM, 2015)

Marius Bjørge's "Bandwidth-Efficient Rendering" (ARM, SIGGRAPH 2015 course) extends Kawase's
filter into a **downsample+upsample pyramid** ("dual filtering") for mobile GPUs
(`papers/bjorge2015-bandwidth-efficient-rendering-dual-filter.pdf/.txt`, already present in this
folder from earlier research). Key figures from the deck:

- The **downsample filter** samples the center plus 4 diagonal corners (5 taps); the **upsample
  filter** samples the 4 edge midpoints plus 4 diagonal corners (8 taps) — reproduced as the
  diagram "Downsample filter / Upsample filter: 1/8, 1/8, 1/2, 1/8, 1/8" weighting
  (`papers/bjorge2015-bandwidth-efficient-rendering-dual-filter.txt`; confirmed independently by
  a second write-up of the same slide deck, `papers/frostkiwi-dual-kawase.txt`, which gives the
  GLSL: downsample = center + 4 diagonal corners, upsample = 4 edge centers + 4 diagonal
  corners).
- Bjørge's comparison: **first downsample to 1/16 resolution**, then compares Gaussian
  (reference) vs "Dual filtering" vs Kawase at **0,1,2,3,4,4,5,6,7 distances/passes**, "Dual
  filtering" using **8 passes**. PSNR against the Gaussian reference: **Kawase 50.02 dB, Dual
  49.78 dB** — both visually indistinguishable from the reference in the stability comparison.
- Performance on a Mali-T760 MP8 at 1080p (ms per frame, illustrative of the *relative* cost,
  not portable to a desktop GPU): Gaussian ≈41.9, 5×5 Gaussian ≈19.2–23.5, Kawase ≈7.0, Dual
  ≈2.8–4.5 (`papers/bjorge2015-bandwidth-efficient-rendering-dual-filter.txt`).

### 2.3 "Next Generation Post Processing in Call of Duty: Advanced Warfare" (Jorge Jimenez, SIGGRAPH 2014)

Slides and — importantly — the author's own comment-thread clarifications are saved from
`papers/iryoku-cod-postprocessing.html/.txt` (the 407 MB .pptx itself was not fetched; the
article page embeds the same numbers and Jimenez answers implementation questions directly in
the comments, which is the most precise numeric source found for this technique):

- **No hard brightness threshold.** Jimenez, replying to a reader: "When using PBR the dynamic
  range is usually very high, so you don't need to threshold. The blurred bloom layer is set to
  a low value (say **0.04**), which means that only very bright pixels will bloom noticeably.
  That said, the whole image will receive some softness" — i.e. the *blend weight* between the
  bloom buffer and the scene, not a cutoff, is the tuning knob, and **0.04** is the value he
  quotes for COD:AW.
- **Mip-chain / pyramidal filter** with a **3×3 tent filter on upsample**, iterated "a few
  iterations" per mip so the tent converges toward a Gaussian; a **custom per-mip radius** is
  used, and "by default it uses the same radius in UV space for each level (as opposed to same
  radius in pixels)."
- **Firefly suppression**: a Karis-style weighted average during the mip0→mip1 downsample,
  `weight = 1 / (1 + luma)`.
- The downsample-then-blur-then-upsample structure follows the Unreal Engine 4 "Elemental Demo"
  bloom (McGuire/Karis-style mip chain, labelled A through E, lowest-resolution mip blurred
  first then added into the next mip up).

### 2.4 LearnOpenGL — classic threshold bloom and the "physically based" mip-chain bloom

Two tutorials, both fetched in full (`papers/learnopengl-bloom.html/.txt`,
`papers/learnopengl-physically-based-bloom.html/.txt`):

- **Classic bloom**: bright-pass extracts fragments where luminance
  `dot(color.rgb, vec3(0.2126, 0.7152, 0.0722)) > 1.0`; blurred with a **separable Gaussian, 5
  taps per side** (10 total samples per axis; weights `0.227027, 0.1945946, 0.1216216, 0.054054,
  0.016216`), run for **10 iterations** (5 horizontal + 5 vertical passes, ping-ponged); final
  composite is a straight additive `hdrColor += bloomColor` before tone mapping.
- **Physically based bloom** (2022 guest article, closely follows the Jimenez/Karis mip-chain
  method): **5 or 6 mip levels** (`num_bloom_mips = 5` in the sample code); downsample uses a
  **13-tap kernel sampled with bilinear filtering (effectively 36 texel reads)** — center weight
  **0.125**, the 4 immediate-inner-cross taps **0.125** each, the 4 edge-midpoint taps **0.0625**
  each, the 4 corner taps **0.03125** each; the first downsample applies a **Karis average**,
  `weight = 1 / (1 + luma)` (same formula as Jimenez, luma from sRGB-converted color using
  `0.2126/0.7152/0.0722`); upsample uses the same **3×3 tent** (`1,2,1 / 2,4,2 / 1,2,1`, ÷16) as
  Kawase's single-pass filter and a configurable **filter radius** (example value **0.005** in UV
  space, explicitly said to need per-project tuning); final blend factor between the HDR scene
  and the bloom buffer is quoted as **"a very small value in the range (0.03, 0.15)"** — squarely
  bracketing Jimenez's 0.04. This tutorial's central argument is that a **hard threshold is not
  physically necessary**: natural attenuation from repeated downsampling/blurring already favours
  brighter pixels.

### 2.5 Engine defaults: Unreal Engine and Blender EEVEE

- **Unreal Engine 5** Bloom docs (`papers/epicgames-bloom-ue.html/.txt`): **Intensity** is a
  linear multiplier on the whole bloom contribution (example images shown at 0.0 / 1.0 / 5.0);
  **Threshold** "defines how many luminance units a color needs to have to affect bloom," with a
  **one-unit-wide linear transition** at the threshold edge, and a value of **−1 makes all pixels
  contribute equally** (i.e. the physically-based, no-threshold mode from Section 2.4); the
  engine also exposes 5 named Gaussian mip passes (`#1…#5 Size`/`#1…#5 Tint`) whose exact default
  percentages are not published as text on the current doc page (only as before/after slider
  images) — **NOT FOUND** for the numeric default size-percent-of-screen-width per level. A
  separate **Convolution Bloom** mode does an FFT-accelerated convolution against a user-supplied
  kernel image for "in-game or offline cinematics," with `Convolution Scale` defaulting to **1**
  and `Convolution Center` defaulting to **(0.5, 0.5)**.
- **Blender EEVEE (legacy, pre-4.2)** — the actual shipped Python defaults, read from the
  `bpy.types.SceneEEVEE` API reference (`papers/blender-sceneeevee-api.html/.txt`; the “Add
  Bloom” manual page itself has been superseded by node-based compositing docs for current
  Blender and was **NOT** a usable numeric source — the manual URL now redirects into the
  geometry-nodes reference):
  - `bloom_threshold` — "filters out pixels under this level of brightness" — **default 0.8**,
    range [0, 100000].
  - `bloom_knee` — "gradual transition between under/over-threshold" — **default 0.5**, range
    [0, 1].
  - `bloom_radius` — "bloom spread distance" — **default 6.5**, range [0, 100].
  - `bloom_intensity` — "blend factor" — **default 0.05**, range [0, 10000] (note: same order of
    magnitude as Jimenez's 0.04 and LearnOpenGL's 0.03–0.15 blend weight, despite being a
    completely independent implementation).
  - `bloom_clamp` — max intensity a bloom pixel can have, 0 = disabled — **default 0.0**.
  - `bloom_color` — RGB tint multiplier — **default (1, 1, 1)**.

### 2.6 Tron: Legacy — what the "neon" look actually is on a real production

`papers/fxguide-tron-legacy-faceoff.html/.txt` (fxguide's VFX breakdown, multiple studios). The
practical suit lights were **Polylights** (an elastomer-based electroluminescent flat-light
material); despite being genuinely light-emitting on set, **"there is not a practical suit, I
don't think, in the film that was not augmented"** — nearly every shot was keyed/roto'd to add or
adjust **glow falloff and colour consistency** across shots, plus a director-requested subtle
**flicker** (a noise-driven post filter in Nuke) applied uniformly to all suits. The two concrete
takeaways for this project: (1) even a genuinely emissive practical source is not "neon enough"
straight from camera — the falloff/bloom is added or corrected in post on top of real light, and
(2) consistency of glow width/colour across the whole figure, not raw brightness, is what reads
as a designed "neon" look rather than an accident of exposure.

## 3. Fresnel / rim, matcap, and the "crystal" look

- **Schlick's approximation** (`papers/wikipedia-schlicks-approximation.html.txt`,
  `papers/lettier-fresnel-factor.html/.txt`): `F(θ) ≈ F0 + (1 − F0)(1 − cosθ)^5`, where `F0` is
  reflectance at normal incidence and `θ` the angle between the surface normal and the view (or
  half) vector. Lettier's shader write-up gives the GLSL directly used in the "3D Game Shaders
  for Beginners" reference: `fresnelFactor = pow(max(1.0 - max(dot(normal, eye), 0.0), 0.0),
  fresnelPower)`, and states **"fresnelPower is five, though you can alter this to your
  liking"** — i.e. **5** is the textbook default exponent, and is treated as an artistic dial in
  practice, not a fixed constant. For a stylised neon rim rather than a physically-metallic one,
  a lower exponent (roughly **2–3**) widens the rim band and is the more common choice in toon /
  glow shaders — this specific "2–3 for a wider stylised rim" range is a general shader-authoring
  convention rather than something stated numerically in the saved sources; flagged here as
  **NOT FOUND** for a citable number and left as an artistic starting point to eyeball against
  the plate.
- **Matcap shading** (`papers/digitalrune-matcap-shaders.html/.txt`): a "material capture" is
  made by photographing/rendering a sphere lit the way you want the final material to look, then
  looking up shading per-pixel by the **view-space surface normal's (x, y) direction** into that
  captured texture — "no complicated computations, only a single texture lookup per pixel." This
  is the cheapest way to get a highlight + rim + AO-ish falloff all baked into one 2D texture and
  is explicitly noted as *not* rotation-stable (it looks right mainly when the camera doesn't
  orbit the object) — acceptable here because the marionette does not rotate relative to camera
  by more than the natural swing of a hanging figure in a static 9-second shot.
- **"Crystal" look**: no single named source was found describing a "crystal shader" recipe with
  numbers (**NOT FOUND**); it is a synthesis of the fresnel term above (sharp rim), a matcap- or
  analytic-specular hot spot (Section 1, item 3), and a fake internal gradient (Section 1, item
  4) that brightens the visually "thick" center of each capsule/ellipsoid and darkens toward the
  geometric silhouette *before* the fresnel rim is added on top — the order matters: internal
  gradient first (a radial falloff from the screen-space long-axis of each primitive), fresnel
  rim added on top (Section 7 gives the exact composite order recommended for this project).

## 4. Normals from depth in screen space (deferred shading without a G-buffer normal pass)

Since the plan renders MuJoCo's depth buffer and reconstructs shading in NumPy/OpenCV rather
than getting normals from a real G-buffer, the standard "normal reconstruction from depth"
family of techniques applies directly:

- **Naive method**: reconstruct view-space position from depth at each pixel, take screen-space
  finite differences (`ddx`, `ddy` equivalents — for a NumPy pass, simple pixel-neighbour
  differences), and normal = `cross(normalize(dPosition/dx), normalize(dPosition/dy))`. This is
  the textbook approach but produces visible **artifacts at depth discontinuities** (silhouette
  edges, and anywhere one capsule occludes another) because the finite difference spans the
  discontinuity and blends two unrelated surfaces (`papers/atyuwen-normal-reconstruction.html/.txt`).
- **The standard fix, "improved" method**: at each pixel, take the derivative in *both* signed
  directions (left/right, up/down) and **choose whichever pair has the smaller absolute depth
  difference**, on the logic that the smaller jump is less likely to have crossed a silhouette
  edge. This removes most artifacts but the same source shows two categories of case (their
  labelled cases "b" and "c") where it still fails — thin or steeply-angled silhouettes.
- **The more accurate method** (`papers/atyuwen-normal-reconstruction.html/.txt`, credited to an
  idea by "Humus" called SDAA): sample **5 taps in each direction** (not just the immediate
  neighbour) along each screen-space axis, extrapolate the two nearest valid taps to estimate
  where the true edge crosses between them, and use that extrapolated point instead of the raw
  neighbour when computing the finite difference. The source is explicit that "accurate normal
  reconstruction from depth is impossible in theory but possible in practice" and that even this
  method can still fail on very thin/sub-pixel triangles — not a concern here since the puppet's
  primitives (capsules/ellipsoids at 2× render resolution) are never sub-pixel.
- **Practical recommendation for this project**: given the puppet is a small, fixed set of
  smooth convex primitives (capsules/ellipsoids) rather than an arbitrary mesh, MuJoCo's own
  **segmentation buffer** (Section 6) can be used to gate which depth neighbours are eligible for
  the finite difference — i.e. only difference depth samples that share the same segmentation
  (object) ID, which sidesteps most of the cross-silhouette blending problem cheaply, without
  needing the 5-tap extrapolation method. This is this agent's synthesis, not something a saved
  source states directly.

## 5. Rendering thin glowing lines (the strings) — look only

(Slack/physics of the strings themselves is item 3's topic; this is purely the rendering look.)

- **Constant-pixel-width lines in screen space**: `papers/atyuwen-antialiased-line.html/.txt`
  describes drawing a line as a screen-space quad (via geometry shader) so that width is
  specified in pixels regardless of distance/perspective, storing the **signed distance from the
  line's center axis** in a texture coordinate (`noperspective float2 TexCoord`), then shading
  each fragment by that distance.
- **The anti-aliasing falloff**: the same source found that a plain box/hard cutoff at the line's
  nominal half-width aliases badly, and that an **exponential falloff `2^(−2.7·d·d)`** (`d` =
  normalized distance from the line's center axis) closely approximates the ideal cone/tent
  filter kernel for a line and gives clean anti-aliasing without a supersampling pass.
- **Core + halo, for a glow rather than a flat line**: no saved source gives exact pixel widths
  for a "core" vs "halo" line (**NOT FOUND** for a citable number), but combining the AA falloff
  above with the bloom numbers in Section 2 gives a principled construction: render the string
  as a **narrow, near-white core** (e.g. 1–2 px half-width at the 1080×1920 delivery resolution,
  i.e. roughly 2–4 px at the stated 2× internal render resolution) using the `2^(−2.7·d·d)`
  falloff for its own edge, let the **halo be entirely the bloom pass's response to that thin
  bright core** rather than a second explicit line width — this way the halo automatically
  inherits the same multi-scale falloff as the rest of the puppet's glow (Section 2) instead of
  being a separately-tuned, inconsistent blur. If a distinct halo pass is wanted for stylisation
  independent of the main bloom (e.g. so strings can glow a different colour than the body), a
  **second, wider, low-alpha copy of the same core** (roughly 3–5× the core's pixel width, colour
  desaturated toward white per Section 1 item 2) composited underneath is a reasonable starting
  point — again, an artistic construction rather than a sourced number.
- **Core whiter than the halo**: consistent with Section 1's rim/fresnel logic — the thinnest,
  most "point-like" part of any glowing primitive (a 1–2 px line core, or a fresnel grazing edge)
  is exactly where full saturation is lost to white first in real HDR-bloomed footage, because it
  is the brightest/most concentrated part of the light source and clips hardest.

## 6. MuJoCo's own renderer: capabilities, exact numbers, and Windows backends

### 6.1 Materials, lights, quality (XML reference)

Fetched and parsed directly from the current MuJoCo docs
(`papers/mujoco-xmlreference-visual-asset.html/.txt`; NOTE — an earlier AI-summarized fetch of
the same page returned several **wrong** defaults, e.g. zfar=12, numslices/numstacks/numquads=20,
material rgba="0.5 0.5 0.5 1"; the numbers below come from grepping the raw saved HTML text
directly and are the corrected ones):

`asset/material` attributes:

| attribute | default | meaning |
|---|---|---|
| `rgba` | `1 1 1 1` | color and transparency |
| `emission` | `0` | scalar self-illumination coefficient; "Emission in OpenGL has the RGBA format, however we only provide a scalar setting... the emission vector [is] the RGB components of the material color multiplied by the value specified here" |
| `specular` | `0.5` | specular reflection coefficient (scalar) |
| `shininess` | `0.5` | specular exponent |
| `reflectance` | `0` | environment-map reflectance, range [0,1] |
| `metallic`, `roughness` | present in current schema (PBR-style additions) | not detailed further in the fetched excerpt — **NOT FOUND** for their exact default values/ranges beyond appearing in the attribute list |

`visual/quality` attributes: `shadowsize` default **4096** (shadow map texture size);
`offsamples` default **4** — "the number of multi-samples for offscreen rendering... set this to
0 to disable multi-sampling... this attribute only affects offscreen rendering" (i.e. this *is*
MuJoCo's MSAA control, but only for the offscreen framebuffer — window rendering's MSAA is set
OS-side when the GL context is created); `numslices` default **28**, `numstacks` default **16**,
`numquads` default **4** (mesh density for auto-generated sphere/box/cylinder primitives — these
directly set how smooth the puppet's capsule/ellipsoid silhouettes are before any shading is
applied, so they matter for how clean the fresnel rim and normal reconstruction can look).

`visual/map` attributes: `znear` default **0.01**, `zfar` default **50** (both are multiplied by
`model.stat.extent`, the model's auto-computed spatial scale, not used as raw metres);
`shadowclip` default **1**, `shadowscale` default **0.6**.

Headlight: MuJoCo always renders with a **built-in headlight** (a directional light at the
camera position, pointed along the view direction, only adjustable via the `headlight` element,
never removable), in addition to any explicit lights, and the headlight **never casts shadows**
("It does not cast shadows (which would be invisible anyway)"). Default lighting model is fixed
function **OpenGL Phong** with shadow mapping layered on top.

### 6.2 Segmentation rendering — confirmed from the actual Python source, not just docs

The public docs page for this (`programming/rendering.html`) has moved/been removed (fetched URL
returned a live 404 from Read the Docs, saved as
`papers/mujoco-rendering-doc.html` for the record); the authoritative and precise answer instead
came from reading MuJoCo's own Python `Renderer` class implementation directly off GitHub
(`papers/mujoco-renderer-classic-py-source.txt`, `mujoco/rendering/classic/renderer.py`,
Apache-2.0 licensed source, fetched at the `main` branch HEAD):

- `enable_segmentation_rendering()` sets an internal flag and, at render time, turns on
  **`mjRND_SEGMENT`** and **`mjRND_IDCOLOR`** scene flags (segmented + ID-colour rendering mode);
  antialiasing is implicitly disabled for this mode within the engine (consistent with an
  earlier general-web-search finding that MSAA is skipped during segmentation rendering because
  averaged colours at geom edges would corrupt IDs).
- The raw pixel read is a **3-channel uint8 RGB image encoding a segmentation ID**, decoded as
  `segid = R + G*256 + B*65536` (a base-256 packed 24-bit integer across the three colour
  channels) — verbatim from source: `segimage = image3[:,:,0] + image3[:,:,1]*(2**8) +
  image3[:,:,2]*(2**16)`.
- That raw `segid` is then **remapped through the scene's own per-geom `segid`/`objid`/`objtype`
  arrays** into a final **2-channel output**: channel 0 = **object ID** (`objid` — e.g. the geom
  index), channel 1 = **object type** (`objtype` — MuJoCo's `mjtObj` enum, distinguishing e.g. a
  geom from a site from a tendon). **Background pixels (segid 0) are remapped to `(-1, -1)`.**
  This directly answers the brief's question "geom id or object type": **it is both, as two
  separate output channels**, not one or the other.
- Depth rendering (`enable_depth_rendering()`) reads the **raw float32 buffer directly** via
  `mjr_readPixels`, then **converts OpenGL normalized/reversed-Z depth to true metric distance**
  using the model's `visual/map` `znear`/`zfar` (each multiplied by `model.stat.extent`) via the
  standard perspective-projection inverse, reproduced verbatim from source:
  ```
  c_coef = -(zfar+znear)/(zfar-znear); d_coef = -(2*zfar*znear)/(zfar-znear)
  # reverse-Z transform:
  c_coef = -0.5*c_coef - 0.5;  d_coef = -0.5*d_coef
  metric_depth = d_coef / (ndc_depth + c_coef)     # done in float64, cast back to float32
  ```
  The context is explicitly set to **`mjDEPTH_ZEROFAR`** reversed-Z mode
  (`self._mjr_context.readDepthMap = mujoco.mjtDepthMap.mjDEPTH_ZEROFAR`) for better precision at
  distance — i.e. the raw buffer value is **1.0 at znear and 0.0 at zfar**, the opposite of the
  naive convention, and must be run through the formula above (not treated as raw linear depth)
  to get real distances. This is the precise mechanism behind the mismatch reported in
  `github.com/google-deepmind/mujoco` issue #1121 (edge pixels where segmentation ID and depth
  can disagree because segmentation forces MSAA off while depth's projection math is exact per
  pixel) — issue content summarized via web search, not independently re-verified against the
  live issue thread's later comments.

### 6.3 `MUJOCO_GL` and the Windows offscreen story — confirmed from source, not folklore

Read directly from `mujoco/rendering/classic/gl_context.py`
(`papers/mujoco-gl_context-classic-py-source.txt`, same repository, Apache-2.0):

- The env var accepts `disable/disabled/off/false/0` to turn off GL entirely, otherwise checks
  membership in a platform-specific valid set: **on Linux**, `glx/egl/osmesa` are additionally
  valid (beyond the universal `enable/enabled/on/true/1/glfw/''`); **on Windows**, only **`wgl`**
  is added to the universal set; **on macOS**, only **`cgl`**.
- But the actual `GLContext` class selection logic **only special-cases Linux `osmesa`, Linux
  `egl`, and Darwin** — every other case, **including Windows regardless of whether
  `MUJOCO_GL` is unset, `"enable"`, or explicitly `"wgl"`, falls through to the same
  `mujoco.glfw.GLContext`.** In other words: **on Windows there is no separate WGL-specific
  context class; `MUJOCO_GL=wgl` is accepted as a valid string but is handled identically to
  leaving `MUJOCO_GL` unset — both use GLFW** (a hidden/invisible window under the hood, which
  works for offscreen rendering on Windows because, unlike headless Linux, Windows always has a
  native OpenGL driver available even without a visible desktop session in the normal case).
- **`osmesa` is not available on Windows or macOS at all.** Confirmed both by the source logic
  above and by an open, unresolved GitHub feature request,
  `google-deepmind/mujoco` **issue #2164**, "Add support for `MUJOCO_GL=osmesa` on Windows and
  macOS" (saved: `papers/mujoco-github-issue-2164-osmesa-windows.html/.txt`), opened because CI
  rendering tests "work fine on Linux by setting `MUJOCO_GL=osmesa`" but fail on Windows/macOS,
  and Linux's method of detecting OSMesa (checking process-global symbol tables) does not port
  cleanly to either platform's dynamic-loader model.
- **Practical takeaway for this machine**: do not set `MUJOCO_GL` at all (or set it to `wgl` for
  self-documentation — functionally identical); MuJoCo will use GLFW with a hidden window, which
  is the supported and only path on Windows.

### 6.4 What the built-in renderer cannot do, for this project's purposes

Synthesizing sections 6.1–6.3 against the brief's neon/crystal requirements: MuJoCo's fixed-
function Phong renderer gives flat-shaded materials with a single scalar specular/shininess/
emission per material, one shadow-mapped light budget, and no fresnel, no bloom, no ambient
occlusion, and no per-pixel PBR beyond the newer but sparsely-documented `metallic`/`roughness`
fields (**NOT FOUND** — whether those are actually consumed by the fixed-function OpenGL path at
all, versus only present for USD/external-renderer export, was not resolved from the fetched
docs). This confirms the project's existing plan (MuJoCo for depth + segmentation only, all
shading done as a custom deferred pass in NumPy/OpenCV) is necessary, not just a stylistic
choice — the built-in renderer structurally cannot produce the fresnel/bloom/AO layers in
Section 1.

## 7. Alternatives for the beauty layer

| option | effort | Windows notes | verdict |
|---|---|---|---|
| **MuJoCo depth+segid → custom NumPy/OpenCV deferred shading + bloom** (current plan) | Medium — normal reconstruction and all shading written by hand, but full creative control and every number in this document is directly applicable | Confirmed working via GLFW/WGL fallback (Section 6.3); no extra install | **Recommended** — matches the "crystal/neon" brief exactly since every layer in Section 1 can be authored explicitly, and the puppet's few smooth convex primitives make normal-from-depth reconstruction (Section 4) tractable without exotic edge handling |
| **pyrender** | Low-medium — real glTF/OpenGL PBR renderer, easy Python API | Defaults to the **Pyglet** backend, which "requires an active display manager" and is unsuitable for a truly headless server, but is **fine on a normal Windows desktop session** (which this machine has); `OSMesa`/`EGL` backends (set via `PYOPENGL_PLATFORM`) are the headless-server options and are Linux-first (`papers/pyrender-offscreen.html/.txt`) | Viable fallback, but a real PBR material model fights against, rather than helps build, a stylised non-physical "crystal" look — would need custom emissive/fresnel shaders anyway, at which point moderngl gives more control for the same effort |
| **moderngl** | Medium-high — hand-written GLSL, full control of a custom bloom-in-a-few-passes pipeline | Runs headless on Windows without a visible window (`papers/moderngl-headless-deepwiki.html/.txt`); requires writing the fresnel/bloom/composite shaders described in Sections 2–3 from scratch in GLSL | Strong alternative if the NumPy/OpenCV deferred pass turns out too slow — same shading math as Section 8, just on GPU instead of CPU |
| **Blender EEVEE (headless `bpy`)** | Medium — bloom, emission shaders, and rim/fresnel nodes all built in and artist-tunable live (Section 2.5's exact defaults) | Headless Python (`bpy` without the GUI) is documented and works on Windows, but **no Windows-specific pitfalls were found in the fetched sources** — general EEVEE-headless setup was **NOT FOUND** in the searched material beyond confirming the engine's bloom parameters exist and their defaults (Section 2.5) | Best *visual* quality per hour of tuning (built-in bloom + node-based fresnel), worst *pipeline* fit — introduces a second renderer/DCC dependency and a scene-import step from MuJoCo's own geometry, which the brief's existing NumPy/OpenCV deferred-pass plan avoids entirely |

**Recommendation**: keep the planned MuJoCo depth+segmentation → NumPy/OpenCV deferred shading
→ bloom → composite pipeline. It is the only option with zero extra install, it already has a
confirmed working Windows path (Section 6.3), and — because the look is explicitly "crystal /
lighting"-style rather than physically accurate — hand-authoring every layer in Section 1 is a
feature, not a limitation, of doing it outside a general-purpose PBR renderer.

## 8. Assets (secondary — the puppet is primitive-built, so this is optional)

Searched Sketchfab (CC0 filter), and checked for a direct-download alternative on Poly Haven and
Wikimedia Commons, since the puppet is explicitly built from MuJoCo capsules/ellipsoids and does
not require an external mesh.

- **Poly Haven**: browsed via search; its models library is overwhelmingly HDRIs/textures/props
  and photogrammetry scans, not articulated figures — **no mannequin or marionette model found**.
- **Wikimedia Commons**: `Commons:3D models` confirms `.stl` uploads are supported and searchable
  under a 3D-models category, but **no specific artist's-mannequin or marionette STL was located**
  by search — **NOT FOUND**.
- **Sketchfab**, three candidates checked directly:
  - **"Mannequin(CC0)" by WuYin** (`sketchfab.com/3d-models/mannequincc0-db6ac59387c245d8bae086ce1ee17fec`)
    — page confirms **"CC0, free to use, no rights reserved"** in the model metadata; 5.3k
    triangles / 2.7k vertices (saved: `papers/sketchfab-mannequincc0.html`). **Genuinely CC0.**
  - **"Marionette" by animator12** (`sketchfab.com/3d-models/marionette-2af427c39af44e80a5e4e8ad049e8288`)
    — page metadata shows **"CC Attribution" (CC-BY)**, i.e. usable but requires crediting the
    author (saved: `papers/sketchfab-marionette-animator12.html`).
  - **"Artist's Mannequin" by timcoleman** — checked and **excluded**: the page's own embedded
    JSON shows `"license": null` (raw HTML confirms this, not an AI summary), meaning it is
    either unlicensed or a paid/store item, not usable.
- **No file was downloaded into `assets/`.** Sketchfab's actual model-file download endpoint
  requires an authenticated session — confirmed directly: an anonymous `curl` request to the
  model's download API returned `{"detail":"Authentication credentials were not provided."}`
  — and this task is instructed not to install anything or set up new authentication, so the CC0
  and CC-BY candidates above are listed by URL/licence for Dennis to fetch by hand through the
  browser if an external mesh is ever wanted, rather than downloaded here. Given the puppet is
  built entirely from MuJoCo primitives per the brief, this is treated as **optional and
  currently unnecessary** rather than a gap. See `assets/LICENCES.md`.

## 9. Numbers for the renderer

| stage | parameter | value | unit | source |
|---|---|---|---|---|
| Bloom (COD:AW) | scene/bloom blend weight | 0.04 | unitless (lerp factor) | `papers/iryoku-cod-postprocessing.txt` (Jimenez, comment reply) |
| Bloom (physically-based, LearnOpenGL) | scene/bloom blend weight | 0.03–0.15 | unitless | `papers/learnopengl-physically-based-bloom.txt` |
| Bloom (Blender EEVEE) | `bloom_intensity` (blend factor) | 0.05 default | unitless | `papers/blender-sceneeevee-api.txt` |
| Bloom (Blender EEVEE) | `bloom_threshold` | 0.8 default | luminance units | `papers/blender-sceneeevee-api.txt` |
| Bloom (Blender EEVEE) | `bloom_knee` | 0.5 default | unitless (0–1) | `papers/blender-sceneeevee-api.txt` |
| Bloom (Blender EEVEE) | `bloom_radius` | 6.5 default | unitless (0–100 scale) | `papers/blender-sceneeevee-api.txt` |
| Bloom (Blender EEVEE) | `bloom_clamp` | 0.0 default (disabled) | luminance units | `papers/blender-sceneeevee-api.txt` |
| Bloom (classic, LearnOpenGL) | brightness threshold | 1.0 | luminance (post-tonemap-space) | `papers/learnopengl-bloom.txt` |
| Bloom (classic, LearnOpenGL) | Gaussian taps per side / iterations | 5 taps, 10 passes (5H+5V) | count | `papers/learnopengl-bloom.txt` |
| Bloom (classic, LearnOpenGL) | Gaussian weights | 0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216 | unitless | `papers/learnopengl-bloom.txt` |
| Bloom (physically-based mip chain) | mip count | 5–6 | count | `papers/learnopengl-physically-based-bloom.txt` |
| Bloom (physically-based mip chain) | downsample 13-tap weights | center 0.125; inner-cross 0.125×4; edge 0.0625×4; corner 0.03125×4 | unitless | `papers/learnopengl-physically-based-bloom.txt` |
| Bloom (physically-based mip chain) | upsample tent (also Kawase's single-pass filter) | 1,2,1/2,4,2/1,2,1 ÷16 | unitless | `papers/learnopengl-physically-based-bloom.txt`; matches `papers/oat2003-realtime-3d-scene-postprocessing.txt` (Kawase 3×3) |
| Bloom (physically-based mip chain) | upsample filter radius (example) | 0.005 | UV-space units (needs per-project tuning) | `papers/learnopengl-physically-based-bloom.txt` |
| Bloom (Karis/firefly weight) | weight formula | 1/(1+luma) | unitless | `papers/iryoku-cod-postprocessing.txt`; `papers/learnopengl-physically-based-bloom.txt` |
| Bloom (Kawase, GDC 2003) | downsample before blurring | 1/16 area (¼×¼) | ratio | `papers/oat2003-realtime-3d-scene-postprocessing.txt` |
| Bloom (dual filter, Bjørge 2015) | typical pass count | up to 8 | count | `papers/bjorge2015-bandwidth-efficient-rendering-dual-filter.txt` |
| Bloom (dual filter, Bjørge 2015) | PSNR vs Gaussian reference | Kawase 50.02 dB; Dual 49.78 dB | dB | `papers/bjorge2015-bandwidth-efficient-rendering-dual-filter.txt` |
| Fresnel/rim | Schlick exponent (default/physical) | 5 | unitless | `papers/lettier-fresnel-factor.txt`; `papers/wikipedia-schlicks-approximation.txt` |
| Fresnel/rim | stylised-wide-rim exponent | ~2–3 (artistic convention) | unitless | NOT FOUND in saved sources — general shader-authoring convention, not independently sourced |
| Rim brightness ratio (rim vs core) | not numerically specified anywhere found | — | — | NOT FOUND; tune by eye against the plate |
| Thin line AA falloff | exponential cone approximation | 2^(−2.7·d²) | unitless (d = normalized distance from line axis) | `papers/atyuwen-antialiased-line.txt` |
| Thin line core width (this project's recommendation) | 1–2 px at 1080×1920 (≈2–4 px at stated 2× internal render) | px | synthesis, not directly sourced | — |
| Thin line halo width (this project's recommendation) | 3–5× core width if a distinct halo pass is used; otherwise let bloom generate it | px / ratio | synthesis, not directly sourced | — |
| Normal-from-depth | robust tap count (accurate method) | 5 taps per axis | count | `papers/atyuwen-normal-reconstruction.txt` |
| MuJoCo `visual/quality` | `offsamples` (offscreen MSAA) | 4 default (0 disables) | sample count | `papers/mujoco-xmlreference-visual-asset.txt` |
| MuJoCo `visual/quality` | `shadowsize` | 4096 default | px (square texture) | `papers/mujoco-xmlreference-visual-asset.txt` |
| MuJoCo `visual/quality` | `numslices`/`numstacks`/`numquads` | 28 / 16 / 4 default | count | `papers/mujoco-xmlreference-visual-asset.txt` |
| MuJoCo `visual/map` | `znear` / `zfar` | 0.01 / 50 default (× `model.stat.extent`) | model-extent units | `papers/mujoco-xmlreference-visual-asset.txt` |
| MuJoCo `asset/material` | `emission` / `specular` / `shininess` / `reflectance` defaults | 0 / 0.5 / 0.5 / 0 | scalar coefficients | `papers/mujoco-xmlreference-visual-asset.txt` |
| MuJoCo segmentation | ID packing in raw RGB read | segid = R + G·256 + B·65536 | integer | `papers/mujoco-renderer-classic-py-source.txt` |
| MuJoCo segmentation | decoded output channels | ch0 = object ID (`objid`), ch1 = object type (`objtype`); background → (−1,−1) | — | `papers/mujoco-renderer-classic-py-source.txt` |
| MuJoCo depth | reversed-Z metric conversion | `d_coef/(ndc+c_coef)`, `c_coef=-0.5·(-(zf+zn)/(zf-zn))-0.5`, `d_coef=-0.5·(-2·zf·zn/(zf-zn))` | metres (model-extent-scaled) | `papers/mujoco-renderer-classic-py-source.txt` |
| MuJoCo Windows | GL backend actually used | GLFW (hidden window), regardless of `MUJOCO_GL` unset/`wgl` | — | `papers/mujoco-gl_context-classic-py-source.txt` |

## 10. Recommended pass list for this project

In composite order, each stage's formula spelled out so it can be implemented directly against
the MuJoCo depth + segmentation buffers:

1. **Geometry buffers from MuJoCo** (per Section 6.2): render `segid` (decoded to per-body
   object ID) and metric depth at 2× the 1080×1920 delivery resolution. Use the segmentation ID
   to gate which neighbouring depth pixels are allowed to contribute to normal reconstruction
   (Section 4's recommendation), avoiding cross-body finite-difference artifacts without needing
   the full 5-tap extrapolation method.
2. **Normals from depth**: per-pixel finite difference of reconstructed view-space position
   along each axis, restricted to same-segid neighbours; `normal = normalize(cross(dP/dx,
   dP/dy))`.
3. **Base emissive layer**: each body's assigned neon colour (blue/cyan/orange per the brief) at
   full saturation, unlit — this is Section 1 item 1, the "it glows" signal.
4. **Internal gradient ("volumetric"/subsurface fake)**: per-pixel brightness multiplier as a
   function of the body's local screen-space radius/thickness (e.g. distance from the
   primitive's medial axis, normalized 0–1), brighter toward the perceived-thick center —
   Section 1 item 4, tuned by eye (no sourced falloff exists).
5. **Fresnel rim**: `rim = F0 + (1-F0)*(1-max(dot(N,V),0))^p`, with `p ≈ 5` as the physically
   "correct" starting point (Section 3) or `p ≈ 2–3` for a wider stylised rim; multiply the rim
   term by a whiter/desaturated version of the body's neon colour and additively blend on top of
   step 4's result — this is Section 1 item 2.
6. **Specular highlight**: a small analytic or matcap-sourced hot spot from one implied key
   light per body, near-white, additively blended — Section 1 item 3.
7. **Ambient occlusion in creases**: darken pixels near joints/attachment points using a
   cheap proxy (e.g. distance-to-nearest-different-segid in screen space, or a precomputed
   per-vertex/per-primitive AO term from the known rigid geometry) — Section 1 item 5; MuJoCo's
   renderer does not provide this (Section 6.4), so it must be synthesized here.
8. **String cores**: render each string as a screen-space-constant-width line (Section 5), core
   half-width ≈1–2 px at delivery resolution, edge falloff `2^(-2.7·d²)`, core colour whiter than
   the body's neon hue per Section 1 item 2's logic (thin/point-like = brightest = clips to
   white first).
9. **Bloom** (Sections 2.3/2.4 numbers): build a 5–6 level mip pyramid from the combined
   emissive-plus-rim-plus-specular-plus-string-core buffer of steps 3–8; downsample with the
   13-tap/Karis-weighted kernel (`weight=1/(1+luma)` on the first downsample only); upsample with
   the 3×3 tent (1,2,1/2,4,2/1,2,1 ÷16) accumulating additively mip-to-mip; blend the final bloom
   buffer back onto the sharp (non-blurred) shaded image at a weight in the **0.03–0.15** range
   (COD:AW used 0.04; treat this as the primary "how much does it glow" dial) — this
   automatically produces the string halos (Section 5) and the falloff-with-distance and
   colour-bleeding cues (Section 1 items 6–7) without any separate halo/bleed pass.
10. **Composite onto the phone plate**: screen- or add-blend the bloomed puppet layer onto the
    9-second plate; optionally re-run a second, larger-radius/lower-opacity pass of only the
    bloom buffer (not the sharp layer) directly onto the plate pixels near the puppet/strings to
    reinforce colour bleeding onto the off-white wall (Section 1 item 7) if the primary composite
    reads as pasted-on rather than lighting the room.
