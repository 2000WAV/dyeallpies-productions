# Item 10 — Rendering routes and mannequin assets for a compelling CG marionette on the RTX 2060

Dennis wants the ragdoll's graphics to become "really compelling," ahead of a plan being
written. This item does not redo item 5 (camera/light/compositing — pinhole model, the
hand-shadow light estimate, the shadow-catcher *concept*, bloom/light-wrap numbers, hand
matting) or item 6 (MuJoCo's own renderer limits and exact XML defaults, the Windows
`MUJOCO_GL`/GLFW story, the fresnel/matcap/bloom-filter numbers for the existing solid-red
capsule-and-ellipsoid look, and a first Sketchfab asset search) or item 9 (colour salience).
It asks a different, narrower question: **is there a rendering route better than the current
plan (MuJoCo depth+segmentation → NumPy/OpenCV deferred shading) for a "really compelling"
look, and is there a mannequin/marionette mesh asset worth using instead of hand-built
primitives?** Sections 1–3 cover three concrete routes (Blender/EEVEE+Cycles, moderngl/raw
OpenGL, pyrender/trimesh); Sections 4–5 cover mesh and texture assets and how a real wooden
mannequin is built, as modelling reference either way; Section 6 ranks the routes.

Every number below is attributed to a file saved in `references/marionette/papers/` (or, for
the de Leva 1996 anthropometry table, a file item 2 already archived there) or to a fact
extracted directly from a downloaded file this session (the Mannequiny `.glb`'s own glTF JSON,
and a `curl -I` HEAD request against a real Blender download). Where the only source found was
a WebSearch summary of a page that could not itself be fetched (blocked by a bot checkpoint),
that is flagged explicitly, following the precedent set in `downloads-01.md`. Where nothing
citable was found, it says **NOT FOUND**.

## 1. Blender headless on Windows with the GPU

### 1.1 Current version, LTS status, install size

Blender's own download page lists **Blender 5.2 LTS** (current release **5.2.1**) and
**Blender 4.5 LTS** under "LTS Releases Currently Maintained"; the previously-current
**Blender 4.2 LTS** (released 2024-07-14) is listed as a "Previous LTS Release" but "Last
updated to 4.2.23 on July 2026" (`papers/blender-lts-download.txt`) — i.e. it is still being
patched two years after release, which is normal for Blender's 2-year LTS support window. All
manual pages fetched for this item resolved against `/manual/en/latest/`, which currently
serves the 5.2 LTS manual (confirmed by the page footer "Blender 5.2 LTS Manual" appearing on
every fetched page, e.g. `papers/blender-eevee-raytracing-manual.txt` line 1).

Install size: a direct `curl -I` HEAD request against the real installer this session returned
**`Content-Length: 365113344`** bytes (~348.2 MB) for
`blender-5.2.1-windows-x64.msi` — independently matching a third-party estimate of "348 MB"
found via WebSearch (not saved as a file; the HEAD request is the primary source here, listed
in `data/10-rendering-numbers.csv`). The portable `.zip` is reported as somewhat larger
(~386 MB per the same WebSearch result) — **NOT FOUND** as a directly HEAD-verified number for
the zip specifically, so treated as a secondary figure only.

### 1.2 `pip install bpy` (Blender as a Python module)

`pypi.org/project/bpy/` returned a Fastly "Client Challenge" bot-block page to a direct `curl`
fetch (saved for the record as `papers/pypi-bpy-project.html`, 3038 bytes, title "Client
Challenge") — the numbers below instead come from a **WebFetch** read of the same URL, which
got past the block:

- Latest version **bpy 5.2.1** (released 2026-08-25).
- **"Python ==3.13.*"** — bpy ships one wheel per Blender release and it only installs against
  that exact Python minor version. **This machine's `.venv-hand` already runs CPython 3.13.7**
  (confirmed separately, `python3 --version` in this session) — an exact match, so `pip install
  bpy` would not require a second Python environment on this box, only whatever disk space the
  wheel itself needs.
- Wheel sizes: Windows x86-64 **338.6 MB**, Windows ARM64 210.6 MB, Linux x86-64 (glibc 2.28+)
  401.7 MB, macOS ARM64 245.2 MB.
- A caveat surfaced by the same WebFetch pass, not independently re-verified: "the direct `pip
  install bpy` method is no longer the recommended way to install the bpy module, as the
  Blender Foundation is taking over official support" — the practical implication for this
  project, if `bpy` is ever actually installed (this task was told not to install anything, so
  it was not tested), is to pin the exact bpy version rather than assume `pip install bpy` pulls
  the newest one cleanly.

The task brief does not ask this agent to install anything, and this constraint was honoured —
none of the above was actually installed or run.

### 1.3 Running Blender headless and driving it with a Python script

Confirmed directly from Blender's own command-line manual pages (not summarized):

- **`-b`** / `--background` — render without a UI (`papers/blender-cli-render-manual.txt`).
- **`-P <filepath>`** / `--python <filepath>` — run a given Python script file
  (`papers/blender-cli-arguments-manual.txt`, lines 2711–2715). Related flags on the same page:
  `--python-text`, `--python-expr`, `--python-console`, `--python-exit-code`.
- Single-image example, reproduced verbatim: `blender -b file.blend -f 10` (render only frame
  10); `blender -b file.blend -o /project/renders/frame_##### -F OPEN_EXR -f -2` (negative frame
  index = from the end; `-F OPEN_EXR` overrides the blend-file's own output format).
- Animation example, reproduced verbatim: `blender -b file.blend -E CYCLES -s 10 -e 500 -t 2 -a`
  (`-E CYCLES` selects the render engine, `-s`/`-e` set start/end frame, `-t 2` limits to two
  CPU threads, `-a` renders the whole animation using the blend-file's own settings).
  (`papers/blender-cli-render-manual.txt`, lines 2440–2560.) A documented gotcha on the same
  page: **arguments execute in the order given** — `-o` and `-F` must be set *before* `-a`/`-f`,
  or they are silently ignored.
- Putting the two together for this project's pipeline: `blender -b marionette.blend --python
  render_from_poses.py -- --poses poses.npy -o out/frame_#####  -F OPEN_EXR -a` (the `--`
  separator before script-specific arguments is standard Blender CLI convention, confirmed via
  WebSearch of community write-ups — not independently found stated in the two manual pages
  fetched, flagged as WebSearch-sourced for that one detail only).

### 1.4 EEVEE Next (Blender 4.2+) features that matter here

EEVEE was substantially rewritten as "EEVEE Next" starting Blender 4.2; the raytracing panel
(**Render ‣ Raytracing**) is EEVEE Next's headline addition
(`papers/blender-eevee-raytracing-manual.txt`):

- **Raytracing toggle**: "The ray-tracing pipeline goal is to increase the accuracy of surface
  indirect lighting... When disabled, it is replaced by a faster pipeline that uses
  pre-filtered light-probes."
- **Method**: **Light Probe** (lowest cost, relies on manually-placed probes) or **Screen-Trace**
  (traces against the screen depth buffer, falls back to light-probes if a ray exits the view),
  each with its own **Resolution** setting (lower = faster/blurrier).
- **Denoising** (of the raw ray-traced signal, separate from Cycles' final-frame denoiser in
  §1.5): **Spatial Reuse** (reuse neighbour-pixel rays, can leak light across surfaces),
  **Temporal Accumulation** (re-project last frame's result, removes fireflies but adds bias —
  useful for making an animated render converge faster), **Bilateral Filter** (blur the resolved
  output).
- **Fast GI Approximation**: a screen-space fallback for high-roughness BSDFs, itself split into
  an "Ambient Occlusion" mode ("use scene intersections to shadow the distant lighting from
  light-probes... the fastest option") and a "Global Illumination" mode (with its own
  Resolution/Rays/Steps knobs, "higher values will reduce noise").
- **Jittered soft shadows** and **Virtual Shadow Maps**: per `papers/blender-eevee-lightsettings-manual.txt`
  and corroborated by WebSearch of the 4.2 release notes, EEVEE Next computes light visibility
  via shadow-map ray tracing for "plausible soft shadows without needing shadow jittering" by
  default, with an optional jittered mode for higher precision at a "high performance impact."
  Virtual shadow maps "greatly increase the maximum resolution, reduce biases and simplify the
  setup" versus the old fixed shadow-map system.
- **Depth of field**: two distinct methods co-exist
  (`papers/blender-eevee-depth-of-field-manual.txt`) — a fast **post-process filter** (a general
  blur pass, plus a second sprite-based pass restricted to "very bright isolated parts of the
  image" for bokeh highlights, gated by a Sprite Threshold/Neighbor Rejection to avoid the cost
  of running the expensive bokeh pass everywhere), and a slower, more accurate **sample-based**
  method that jitters the camera position per sample (needs many samples to converge cleanly).
- **Bloom**: covered exhaustively by item 6 already (`06-neon-rendering-and-assets.md` §2.5,
  `bloom_threshold`/`bloom_knee`/`bloom_radius`/`bloom_intensity`/`bloom_clamp` defaults) — not
  repeated here.
- **Shadow catcher / holdout in EEVEE Next**: **EEVEE has no native shadow-catcher toggle.**
  Confirmed two ways: (a) EEVEE's **Film** panel (Render ‣ Film) exposes only **Filter Size**
  (anti-aliasing blur amount), **Transparent** (render background alpha for compositing), and
  **Overscan** (extra internal render-buffer margin to fix edge glitches) —
  `papers/blender-eevee-shadow-catcher-manual.txt` (this file's URL, `.../film.html`, turned out
  to be the Film page, not a catcher-specific page; the finding itself — that EEVEE's film
  settings don't include a catcher option — is the useful negative result). (b) A WebSearch of
  the Blender Artists community forum states plainly "there is no native shadow catcher for
  Eevee in Blender... a shadow catcher can be faked using the Shader to RGB node" (WebSearch
  summary only, not an independently saved primary source — flagged per house convention).
  **Holdout** *does* exist as a shader node in EEVEE (it is a generic Shader node,
  `papers/blender-eevee-shadow-catcher-manual.txt` line ~1806 lists "Holdout" among the shader
  node types), but that is the general-purpose "make this object invisible but occlude/shadow
  others" node, not a purpose-built catcher — the workaround is the same Shader-to-RGB trick.

### 1.5 Cycles with OptiX on a Turing card (RTX 2060): realistic render times

- **Requirements** (`papers/blender-cycles-gpu-rendering-manual.txt`): OptiX requires a
  Windows/Linux NVIDIA GPU with **compute capability 5.0+** and a **driver version of at least
  575**; it "takes advantage of hardware ray-tracing acceleration in RTX graphics cards, for
  improved performance." GPU-accelerated **OpenImageDenoise** (as distinct from the OptiX AI
  denoiser) needs **compute capability 7.0+**, which "includes all NVIDIA RTX cards" — the RTX
  2060 (Turing, compute capability 7.5) qualifies for both.
- **RTX 2060 spec recap** (`papers/renderjuice-rtx2060-blender.txt`): 6 GB VRAM, 1920 CUDA
  cores, 30 RT cores, 240 Tensor cores, 336 GB/s memory bandwidth, 160 W TDP, Turing
  architecture, released 2019.
- **Blender Open Data benchmark score**: **1,653** for the RTX 2060, described by the same page
  as "entry-level speed — fine for learning and lighter scenes." This number could not be
  independently re-derived from `opendata.blender.org` itself: its device page is fully
  client-rendered (confirmed this session — both `curl` and `WebFetch` returned only a JS shell/
  403, no static score), so the 1,653 figure and the per-scene times below are a **third-party
  derivation** of the same underlying public dataset, not a first-party number.
- **Per-frame render-time estimates, RTX 2060, standard Blender benchmark scenes** (from the
  same page, "single-frame estimates derived from Blender Open Data benchmark medians at the
  scene sample counts"):

  | scene | OptiX | CUDA |
  |---|---|---|
  | Junkshop | 38.09 s | 63.85 s |
  | Monster | 23.69 s | 32.47 s |
  | Classroom | 49.58 s | 89.18 s |

  **These are full, complex production-quality benchmark scenes at their fixed benchmark sample
  counts and resolution — not the marionette scene, and not 1080×1920.** A specific,
  citable seconds-per-frame number for "an ~18 cm figure of 11 capsule/ellipsoid-derived
  primitives, one HDRI, one shadow catcher, at 1080×1920 with modest samples and OIDN/OptiX
  denoising" is **NOT FOUND** anywhere in the sources checked — no one publishes benchmarks for
  scenes this simple. The reasoned estimate for §6 is built from these numbers by scaling down
  for scene complexity and resolution, and flagged there as this project's own extrapolation,
  not a sourced figure.
- **Denoising**: OptiX's AI denoiser runs on the GPU's Tensor cores (fast, RTX-specific);
  OpenImageDenoise (OIDN) can run on the GPU (compute capability 7.0+, as above) or fall back to
  CPU. A commonly repeated (WebSearch-only, not independently verified against a primary
  benchmark) rule of thumb: AI denoising lets a scene render at roughly a quarter of the samples
  for a similar apparent quality, cutting render time by "50–70%" — treated as a rough
  order-of-magnitude claim, not a number to plan a render budget around.

### 1.6 Importing glTF and building a rigged doll from primitives

The exact current signature of `bpy.ops.import_scene.gltf`, reproduced verbatim from Blender's
own Python API reference (`papers/blender-python-import-gltf-api.txt`, lines 2505–2536):

```
bpy.ops.import_scene.gltf(
    *, filepath='', export_import_convert_lighting_mode='SPEC', filter_glob='*.glb;*.gltf',
    directory='', files=None, loglevel=0, import_pack_images=True, merge_vertices=False,
    import_shading='NORMALS', bone_heuristic='BLENDER', disable_bone_shape=False,
    bone_shape_scale_factor=1.0, guess_original_bind_pose=True, import_webp_texture=False,
    import_unused_materials=False, import_select_created_objects=True, import_scene_extras=True,
    import_scene_as_collection=True, import_merge_material_slots=True,
    import_point_as_pointcloud=False)
```

Two parameters matter directly for driving a rigged asset like Mannequiny (§4) from this
project's sim: `bone_heuristic='BLENDER'` ("best for import/export round trip... bone tips are
placed on their local +Y axis in glTF space" — the default, and the one that keeps bone
orientations predictable for scripted posing) and `guess_original_bind_pose=True` (attempts to
recover the rest pose the rig was authored in, relevant since the sim's own rigid-body rest pose
should be used as the bind pose, not whatever pose the glTF happened to ship in).

Building a doll from bpy primitives (capsules, spheres, cylinders) rather than importing a mesh
is the same operation as the current MuJoCo-primitive plan, just re-created in Blender's own
mesh-primitive operators (`bpy.ops.mesh.primitive_*_add`); no Blender-specific gotcha for this
was found beyond the general glTF-import notes above — this path is mechanically simple, the
open question is purely the render-time cost (§1.5) and pipeline-integration effort (§6), not
feasibility.

### 1.7 Driving object transforms per frame from a NumPy array (the sim's body poses)

The standard, stable Blender Python pattern — `bpy_struct.keyframe_insert` is confirmed present
in the current API index (`papers/blender-python-keyframe-api.txt`; the specific page fetched
for this citation, `bpy.types.Keyframe`, documents the *keyframe data type* rather than the
*insertion method* itself — a mismatch caught and flagged here rather than papered over,
**NOT FOUND** as an ideal citation for the exact call signature of `keyframe_insert`, though its
existence and general behaviour — insert a keyframe on an object/bone property at a given frame
— is uncontroversial, long-stable Blender API and not disputed by any source checked):

```python
for frame_idx, (pos, quat) in enumerate(zip(positions, quaternions)):  # from the sim's NumPy arrays
    obj.location = pos                      # or pose_bone.location for an armature bone
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = quat           # MuJoCo's own quaternion convention: (w, x, y, z)
    obj.keyframe_insert(data_path="location", frame=frame_idx)
    obj.keyframe_insert(data_path="rotation_quaternion", frame=frame_idx)
```

For a single skinned mesh + armature asset like Mannequiny (§4), the same loop targets
`armature.pose.bones["thigh.l"]` etc. instead of a separate object per rigid body — the mapping
from this project's 11 rigid bodies to Mannequiny's skeleton is given in §5.3. MuJoCo's own
quaternion convention (`w, x, y, z`, scalar-first) needs converting to Blender's own convention
before assignment; Blender's `rotation_quaternion` is also `(w, x, y, z)` scalar-first
(long-standing, uncontroversial Blender convention, not separately re-verified by a fetched
source this session since it was not in dispute).

### 1.8 Output: EXR/PNG with alpha, shadow catcher, colour management

- **EXR/PNG with alpha**: confirmed via `-F OPEN_EXR` (§1.3) and the Output Properties panel
  (`papers/blender-output-fileformats-manual.txt`); both EEVEE and Cycles support a
  **Transparent** film/background option (§1.4) that writes a real alpha channel rather than a
  background colour, which is what a bake-once compositing pipeline needs.
- **Shadow catcher**: Cycles has a **true, purpose-built shadow catcher** — Object Properties ‣
  Visibility ‣ Mask ‣ **Shadow Catcher** (`is_shadow_catcher` in the Python API), described
  verbatim as enabling "the object to only receive shadow rays... shadow catcher objects will
  interact with other CG objects via indirect light interaction. This simplifies compositing CGI
  elements into real-world footage" (`papers/blender-cycles-object-data-manual.txt`, lines
  2442–2462). A documented subtlety: results differ depending on whether the "Shadow Catcher"
  render pass is enabled (full indirect-light capture) or not (a simpler approximation is used
  — always the case in viewport preview). **EEVEE Next has no equivalent built-in** (§1.4) — only
  the Shader-to-RGB fake.
- **Colour management**: Blender's default view transform changed from **Filmic** to **AgX**
  starting **Blender 4.0** (`papers/blender-4.0-colormanagement-release.txt`, quoted verbatim:
  "The AgX view transform has been added, and replaces Filmic as the default in new files...
  provides better color handling in over-exposed areas compared to Filmic. In particular bright
  colors go towards white, similar to real cameras"). Both Filmic and AgX are explicitly SDR-only
  tools per the same release notes: "Filmic and AgX do not [support HDR display] as they were
  designed to bring values into the 0..1 range for SDR displays." **This matters directly for
  this project**: the phone plate is already a tone-mapped BT.709 sRGB (SDR) video (item 5's own
  framing). Rendering the doll with AgX or Filmic applies a *second* filmic-style contrast/
  desaturation curve on top of a render that will then be composited onto footage that already
  went through the iPhone's own tone-mapping — a mismatch risk not called out in Blender's own
  docs (this is this project's own synthesis, not a sourced claim). The safer default for a
  bake-once composite onto already-tone-mapped SDR footage is the **Standard** view transform
  (a plain linear-to-sRGB transform, no additional filmic curve) on the CG render, matching the
  plate's own colour space more directly — or exporting linear-light EXR from Blender (Standard/
  raw) and doing any further tone-mapping once, in the same compositing pass that already
  handles the plate.

### 1.9 Film grain and motion blur

- **Film Grain compositor node** (`papers/blender-filmgrain-node-manual.txt`): "simulates the
  appearance of photographic film by adding realistic grain and subtle optical characteristics."
  Controls: **Strength** (0 disables, 1 = full effect), **Film Profile** (named presets for
  different film gauges/stocks), **Gauge** (smaller = larger/more visible grain), **Animated**
  (a different grain pattern every frame vs. a fixed pattern for the whole sequence — for
  matching a phone camera's per-frame sensor noise rather than a static texture), **Saturation**
  (colourfulness of the grain).
- **Cycles motion blur** (`papers/blender-cycles-motion-blur-manual.txt`): **Position** sets
  where the virtual shutter opens relative to the current frame (Start/Center/End on Frame);
  **Shutter** is the open-to-closed duration in frames (e.g. shutter=1.0 blurs over one full
  frame's worth of motion); **Rolling Shutter** simulates a sensor read-out delay; **Shutter
  Curve** is a custom open/close falloff curve (default: instant open/close). This maps directly
  onto item 5's own iPhone 14 rolling-shutter and shutter-angle findings if the CG doll's motion
  blur needs to match the plate's — not re-derived here, just noted as the Blender-side control
  surface that would consume item 5's numbers.

## 2. moderngl / raw OpenGL deferred PBR

### 2.1 What a small, compelling deferred PBR object needs, and its canonical references

For a small (~18 cm on-screen) rigid object, a physically-plausible deferred PBR pipeline
combines: a **Cook-Torrance microfacet BRDF** (GGX distribution + Schlick-GGX geometry +
Fresnel-Schlick), **image-based lighting** from a prefiltered HDRI (split into a diffuse
irradiance map and a roughness-mipped specular map, per Epic's split-sum approximation),
**ambient occlusion** (SSAO/HBAO), **soft shadows** (PCSS or an equivalent penumbra-widening
shadow-map technique), and **temporal or multi-sample anti-aliasing**. The canonical references
named in the brief were all located and (except Filament's landing redirect, fixed) fully
archived:

- LearnOpenGL's **PBR/Theory**, **PBR/Lighting**, **PBR/IBL/Diffuse-irradiance**, **PBR/IBL/
  Specular-IBL** chapters (`papers/learnopengl-pbr-*.html/.txt`).
- Google **Filament**'s `Filament.md.html` (full rendering-pipeline paper) and `Materials.md.html`
  (material model, reflectance tables) (`papers/filament-doc.html/.txt`,
  `papers/filament-materials-doc.html/.txt`) — note both URLs 301-redirect from the `.html`
  landing page to `.md.html`; the plain `.html` URL only serves a redirect stub.
- Fernando (2005), **"Percentage-Closer Soft Shadows"** — already archived by an earlier item
  (`papers/fernando2005-percentage-closer-soft-shadows.pdf/.txt`), re-read here for its numbers.
- Bavoil, Sainz & Dimitrov (2008), **"Image-Space Horizon-Based Ambient Occlusion"** (HBAO) —
  the full 47-slide NVIDIA SIGGRAPH deck, downloaded this session
  (`papers/bavoil2008-hbao-siggraph.pdf/.txt`).
- Mittring (2007), **"Finding Next Gen: CryEngine 2"** — the full 25-page SIGGRAPH course-notes
  chapter containing the original Crysis SSAO description, downloaded this session
  (`papers/mittring2007-finding-nextgen-cryengine2.pdf/.txt`).

### 2.2 Cook-Torrance GGX (LearnOpenGL's exact formulas)

From `papers/learnopengl-pbr-theory.txt` and `papers/learnopengl-pbr-lighting.txt`:

- **Normal distribution (Trowbridge-Reitz GGX)**: `NDF_GGXTR(n,h,α) = α² / (π·((n·h)²·(α²−1)+1)²)`.
- **Geometry (Schlick-GGX + Smith's method)**: `G_SchlickGGX(n,v,k) = (n·v) / ((n·v)(1−k)+k)`,
  combined as `G(n,v,l,k) = G_sub(n,v,k)·G_sub(n,l,k)`, with `k_direct = (α+1)²/8` for direct
  lighting (a different remapping is used for IBL — not itself quoted in the saved excerpt,
  **NOT FOUND** for the exact IBL-`k` formula in this pass, though it is a well-known
  `k_IBL = α²/2` in the wider PBR literature — flagged as not independently re-verified here).
- **Fresnel (Schlick's approximation)**: `F(θ) ≈ F0 + (1−F0)(1−cosθ)⁵`, and the **dielectric
  default `F0 = vec3(0.04)`** — "a base reflectivity that is approximated for most dielectric
  surfaces... holds for most dielectrics and produces physically plausible results without
  having to author an additional surface parameter." Metals use the surface's own albedo as
  `F0` instead.
- **Cross-check against Filament**: Filament's `reflectance` material property defaults to
  **0.5, which the docs state maps to exactly 4% reflectance** (`papers/filament-materials-doc.txt`,
  "the default value of 0.5 corresponds to a reflectance of 4%") — the same `F0=0.04` constant,
  arrived at independently by a completely different renderer's material model. Filament's own
  reflectance table gives **plastics/glass a reflectance of 4–5% (IOR 1.5–1.58)** — directly
  usable for this project's matte-plastic doll material — and, as a bonus worked example, a
  representative **"Wood" dielectric base colour of sRGB (0.53, 0.36, 0.24)**
  (`papers/filament-materials-doc.txt`).

### 2.3 Image-based lighting: the split-sum approximation and its actual buffer sizes

From `papers/learnopengl-pbr-ibl-diffuse-irradiance.txt` and
`papers/learnopengl-pbr-ibl-specular-ibl.txt`:

- **HDR environment capture**: the equirectangular HDRI is rendered into a cubemap at
  **512×512 per face**.
- **Diffuse irradiance map**: convolved from that cubemap at only **32×32 per face** (irradiance
  varies slowly over the hemisphere, so a very low resolution suffices) using a discrete
  numerical integration over spherical coordinates with a **`sampleDelta = 0.025`** radian step
  ("decreasing or increasing the sample delta will increase or decrease the accuracy").
- **Specular IBL (Epic's split-sum approximation)**: splits the specular integral into (a) a
  **prefiltered environment map**, stored at **128×128 per face at its base mip**, with
  successively rougher reflections stored in successive mip levels (the worked example uses
  **5 mip levels** for 5 roughness bands) using GGX-importance-sampled Monte Carlo convolution
  (Hammersley low-discrepancy sequence), and (b) a **2D BRDF integration LUT**, stored at
  **512×512** (`GL_RG16F`), pre-computed once and reused for every material/every frame.
- All of the above scales down trivially for a project this size: a *single* small HDRI, applied
  to *one* small rigid-body-driven doll rather than an open scene, meaning the entire IBL
  precompute (irradiance + prefiltered specular + BRDF LUT) is a **one-time bake**, not a
  per-frame cost — directly compatible with this project's "bake-once" pipeline requirement
  (memory: `render-iteration-cache`).

### 2.4 SSAO / HBAO

- **Mittring (2007)**, the original Crysis SSAO: a full-screen pass sampling the existing
  z-buffer, applying "simple depth comparisons... to compute a darkening factor to get
  silhouettes around objects," restricted to nearby receivers only, and explicitly applied to
  **ambient shading only** (not diffuse/specular) because "it changed the look away from being
  realistic" when applied more broadly (`papers/mittring2007-finding-nextgen-cryengine2.txt`,
  section 8.5.4.3) — the method's own author frames it as look-driven, not physically exact,
  which matches this project's already-established artistic-license approach to occlusion in
  item 6 (Section 1 item 5).
- **Bavoil, Sainz & Dimitrov (2008), HBAO**: samples multiple 2D "directions" per pixel (worked
  example: 6 directions × 6 steps/direction = 36 samples/pixel), estimates the horizon angle
  along each direction with an **angle bias** (their own before/after figures show a 30°
  angle-bias example removing self-occlusion banding artifacts) and per-sample attenuation by
  distance, then blurs. Measured costs, **on a GeForce GTX 280 (2008 hardware, not the 2060, and
  at 800×600/1600×1200, not 1080×1920 — an order-of-magnitude reference only)**:

  | configuration | cost |
  |---|---|
  | Half-resolution AO, 6×6=36 samples/px, no blur, 800×600 | 3.5 ms |
  | Half-resolution AO + 15×15 blur (blur at 1600×1200) | 3.5 ms (AO) + 2.5 ms (blur) |
  | Full-resolution AO, 6×6=36 samples/px, no blur, 800×600 | 30 ms |

  HBAO also documents a **half-resolution AO trick**: compute the occlusion buffer from a
  half-resolution depth source and only do the blur pass at full resolution — the AO cost above
  drops by roughly 8-9× (3.5 ms vs 30 ms) for a resolution difference of 4× the pixel count,
  consistent with occlusion sampling being the dominant cost, not the blur.
- **Neither source gives a number at a 2060-class GPU or at 1080×1920.** For this project's
  purposes, the relevant scaling factor is not GPU generation but **screen coverage**: an
  ~18 cm figure at typical hand-drop framing covers a small fraction of a 1080×1920 frame, so
  even a naively-ported 2008-era full-screen-cost algorithm, restricted to a bounding box around
  the doll (not the whole frame), would cost a small fraction of the numbers above — this is
  this project's own reasoning, not a sourced claim, and is carried into §6's cost ranking as an
  estimate, not a citation.

### 2.5 PCSS (percentage-closer soft shadows)

From `papers/fernando2005-percentage-closer-soft-shadows.txt` (already archived; NVIDIA, GDC/
SIGGRAPH-era paper): penumbra size is estimated per-pixel from (blocker depth, light size,
receiver depth) via similar-triangles, requiring a **blocker search** (over a search region
sized by light size and blocker-to-receiver distance) followed by a **variable-radius PCF**
using the estimated penumbra size as the filter radius. Two published quality/performance
points at 640×480 on 2005-era NVIDIA hardware (an order-of-magnitude reference only, like §2.4):

| quality target | blocker-search samples | PCF samples | measured rate |
|---|---|---|---|
| "Great results (see image), especially with a texture" | 64 | 144 | ~20 fps |
| "For high-quality screenshots" | 144 | 256 | ~8 fps |

The paper's own "Improvements" slide flags its PCF as "currently very wasteful (256 samples
always!)" with "no profiling/tuning done" — i.e. even the paper's authors consider these
sample counts an unoptimized starting point, not a target to match exactly.

### 2.6 TAA / MSAA / screen-space depth of field

Not covered in depth by any single saved source this pass; these are standard, well-documented
real-time techniques (temporal jitter + history reprojection for TAA; multi-sample coverage
buffers for MSAA; a circle-of-confusion-driven blur, often itself using a lens-shaped bokeh
kernel, for screen-space DoF) but a specific *numeric* cost or parameter table for any of the
three was **NOT FOUND** in this pass's source set — MuJoCo's own `offsamples` MSAA default (4,
already documented by item 6) is the only concrete antialiasing number this project has
archived anywhere. Given the small on-screen size of the doll, a simple 2× or 4× supersample-
and-downsample (already implied by item 6's "2× internal render resolution" recommendation) is
a defensible substitute for either TAA or MSAA without needing new machinery.

### 2.7 Estimated cost on the RTX 2060 at 1080×1920

No source in this pass or item 6 publishes a 2060-specific, 1080×1920-specific cost for any of
GGX shading, IBL, HBAO, or PCSS. §6 gives this project's own reasoned estimate (screen-coverage-
scaled from the numbers in §2.4/§2.5, explicitly flagged as an estimate) rather than repeating
that reasoning here.

## 3. pyrender / trimesh / other Python paths (brief)

- **trimesh**: "a pure Python library for loading and using triangular meshes, with an emphasis
  on watertight surfaces." Ships only an optional Pyglet-based viewer "for debugging and
  inspecting" (not a PBR renderer), plus a Jupyter-notebook three.js inline preview. It is a
  geometry/IO/processing library, not a rendering path — useful for loading/validating a
  downloaded mannequin mesh (§4) before handing it to something else, not for producing the
  final beauty pass. (WebSearch-derived summary; not independently re-verified against
  trimesh's own docs this session — flagged as such.)
- **pyrender**: already covered by item 6 in some depth (Pyglet backend needs an active display
  manager — fine on this machine's normal desktop session — vs. `PYOPENGL_PLATFORM`-selected
  OSMesa/EGL for a truly headless server, which are Linux-first;
  `papers/pyrender-offscreen.html/.txt`). Additional detail this pass (WebSearch-derived,
  cross-checked against pyrender's own GitHub README title/description, "Easy-to-use glTF
  2.0-compliant OpenGL renderer for visualization of 3D scenes"): pyrender implements real
  **metallic-roughness PBR materials** (glTF 2.0's material model, the same one Mannequiny's
  `.glb` uses natively, §4) plus **shadow mapping for directional and spot lights**, and is
  designed to interoperate directly with trimesh scenes/meshes. Item 6's verdict stands: a real
  PBR renderer fights against, rather than helps build, a *stylised* look, but for a
  *photoreal wooden-mannequin* look (as opposed to the existing neon-crystal look) pyrender's
  built-in glTF PBR + shadow mapping is a much closer match to what's actually wanted, at much
  less implementation effort than hand-rolling the same GGX/IBL/shadow-map math in moderngl.
- **Other Python paths**: no other renderer (Panda3D, Open3D's own renderer, Kaolin, etc.) was
  searched in this pass — out of scope given the brief's "briefly" instruction for this section
  and the strength of the pyrender/moderngl/Blender comparison already assembled.

## 4. Mannequin and marionette mesh assets

### 4.1 Meshes found, with licence, polygon count, and rig/segmentation status

| asset | source | licence | polys | rigged/segmented | downloaded? |
|---|---|---|---|---|---|
| **Mannequiny — GDQuest / Luciano Muñoz** | github.com/gdquest-demos/godot-3d-mannequin, mirrored (glTF export) on OpenGameArt | **CC-BY 4.0** (model+animations only; the Godot demo code is separately MIT) | **~10,282 vertices / ~13,932 triangles** — parsed directly from the downloaded `.glb`'s own glTF JSON this session, not a page claim | **Rigged**: 1 skinned mesh + 1 armature with **47 skeleton nodes** and **11 baked animations** (idle/walk/run/jump/fight moves) — **not pre-segmented into separate meshes per body part**; it is one continuous skinned mesh deformed by named bones (`pelvis`, `spine_01`, `spine_02`, `neck_01`, `head`, `clavicle.l/r`, `upperarm.l/r`, `lowerarm.l/r`, `hand.l/r` + individually-jointed fingers, `thigh.l/r`, `calf.l/r`, `foot.l/r`, `ball.l/r`) | **Yes** — `assets/mannequiny-gdquest/` |
| **"Mannequin(CC0)" — WuYin** (item 6's find, cross-referenced) | Sketchfab | **CC0** | 5.3k triangles / 2.7k vertices | Not confirmed rigged/segmented by item 6's pass | No (auth wall) |
| **"Marionette" — animator12** (item 6's find) | Sketchfab | **CC-BY** | Not recorded by item 6 | Not confirmed | No (auth wall) |
| Ball Joint Doll Basemesh — ChamberSu | Sketchfab | **CC-BY** (confirmed on-page text) | Renders client-side only — **NOT FOUND** in static HTML | Page badge says "Rigged" | No (auth wall) |
| Ball Joint Doll Rigged Basemesh (Male) — ChamberSu | Sketchfab | **CC-BY** | Same — **NOT FOUND** | "Rigged" badge | No (auth wall) |
| Ball Joint Doll Rigged — Drothari | Sketchfab | **CC-BY** | Same — **NOT FOUND** | "Rigged" badge, described as a "ballerina...double jointed" | No (auth wall) |
| Ball-Joint-Doll (Low Poly Character) — rjducats | Sketchfab | **CC-BY** | **3,000 triangles** (this one *is* static page text) | Not confirmed | No (auth wall) |
| "Mannequin Male" — OpenGameArt | OpenGameArt | **CC0** | Not obtained (page-only check) | Not confirmed | No |
| "Mannequin Model" — OpenGameArt | OpenGameArt | **CC0** | N/A — turned out to be a **32×32 pixel-art reference image**, not a 3D mesh | N/A | No, excluded on inspection |

**Mannequiny is the strongest candidate found.** It is genuinely, unambiguously CC-BY (the
licence question was raised and resolved in the OpenGameArt comment thread itself — a commenter
initially worried it was MIT-only, and the uploader quoted the GitHub release notes directly:
"Mannequiny by GDQuest, Luciano Muñoz, and contributors licensed CC-BY 4.0" — the code is
MIT, the 3D asset is CC-BY, and only the 3D asset was used here). It is small (1.56 MB
uncompressed `.glb`, well under the 30 MB limit), already in glTF 2.0 format (importable
directly via `bpy.ops.import_scene.gltf`, §1.6, or via pyrender, §3), and already rigged with a
humanoid skeleton whose bone set maps closely onto this project's 11 rigid bodies — but *not*
pre-segmented into 11 separate meshes the way MuJoCo's own geoms are. Driving it means either
(a) posing the existing armature's bones per frame from the sim's per-body quaternions (§1.7,
§5.3) — treating the skinned mesh as a single deforming surface, which looks *smoother* at the
joints than 11 independent rigid capsules (skin deformation blends geometry across a joint
instead of showing a hard seam) but means MuJoCo's per-body segmentation ID (item 6, §6.2)
no longer corresponds 1:1 to a paintable region without extra bookkeeping; or (b) treating each
bone's mesh region as effectively rigid (freezing the skin weights to a nearest-bone
assignment) to get back something closer to 11 independently-transformable rigid parts. Neither
was tested this pass — the point of this research item was verifying the asset is a real,
usable, correctly-licensed match, which it is.

### 4.2 CC0 PBR textures for painted wood, lacquered wood, matte plastic

All three downloaded this session, all genuinely CC0, all well under 30 MB:

| texture | source | licence | maps | size |
|---|---|---|---|---|
| **Lacquered Cherry Wood** | Poly Haven | **CC0** | diffuse, normal (GL), roughness, AO — 1k JPGs | 1.6 MB total |
| **Painted Wood 003** | ambientCG | **CC0 / Public Domain** | Color, Displacement, NormalDX, NormalGL, Roughness (+ .blend/.usdc/.mtlx) — 1k | 7.9 MB zip |
| **Plastic 001** | ambientCG | **CC0 / Public Domain** | same map set as above — 1k | 6.6 MB zip |

Poly Haven's own public API (`api.polyhaven.com/files/<slug>`) was used to get exact, verified
download URLs and byte sizes rather than scraping the page — every downloaded file's size
matched the API's own reported size exactly. ambientCG's texture is not explicitly tagged
"matte" (the site organizes by material family — Plastic, Wood, Metal — and by a numeric
roughness map, not by a matte/glossy keyword), so Plastic001 is used here as a representative
mid-roughness sample to be tuned toward "matte" via its own roughness map rather than a
confirmed "matte" label — **NOT FOUND** for an exact matte/glossy taxonomy on ambientCG.

## 5. How artist mannequins and marionettes are built

### 5.1 Construction: joints, wood, and the internal armature

The Metropolitan Museum of Art's own article on artist's lay-figure mannequins
("Mannequins: A Tool of the Artist's Workshop") returned **HTTP 429 ("Vercel Security
Checkpoint")** to both a direct `curl` fetch and a `WebFetch` call this session — the page could
not be independently saved or re-verified (`papers/metmuseum-mannequins-artist-workshop.html`
kept as evidence of the block). The construction facts below are therefore from the
**WebSearch tool's own extracted summary of that page**, not a re-verified primary source —
flagged per the project's existing convention for WebSearch-only findings:

- Some 19th-century French artist's mannequins were handcrafted from **beechwood**.
- Articulation used **wood ball-and-socket joints**, "numerous dowels," and an internal
  **wood-and-metal armature ("skeleton")** that holds the parts in place.
- Articulated joints: **shoulders, arms, hips, legs, wrists, and ankles**, plus (on finer
  figures) **individually-jointed fingers**.
- Function: figures range from life-size down to small scale, mostly used for studying the fall
  of clothing on a posed human figure without a live model.

This is broadly consistent with, and cross-checked against, this project's already-archived
marionette-construction sources from item 1 (`papers/wepa-string-puppet.txt`,
`papers/takey-how-to-make-operate-marionettes.txt`, `papers/marionettescz-3dprint-basics.txt`) —
traditional string marionettes use the same ball-and-socket-at-shoulder-and-hip, hinge-at-elbow-
and-knee joint layout, since both crafts solve the same problem (a small number of rigid links
that must swing believably under gravity/manipulation) with the same mechanism. **No numeric
seam-line or exact joint-diameter figures were found in either the Met's summary or the item-1
sources** — **NOT FOUND** for anything more specific than "ball-and-socket at the wide joints,
hinge or dowel at the narrow ones."

### 5.2 Proportions of a classic 12-inch artist's mannequin (scaled from measured human data)

No retailer or manufacturer page found (Amazon, eBay, Etsy, JustKraft, WoodArtSupply — all
checked via WebSearch) publishes an actual segment-length table for a 12-inch wooden mannequin;
every page instead says some version of "made according to the proportions of the human body."
**NOT FOUND** as a directly-sourced dimension table (see `downloads-10.md`'s "searched, not
found" section for the exhaustive list of pages checked).

In place of that missing table, the segment-length fractions already archived by item 2 from de
Leva's (1996) re-analysis of Zatsiorsky-Seluyanov cadaver data
(`papers/deleva1996-adjustments-zatsiorsky-seluyanov.txt`, `data/02-segment-parameters.csv`) —
measured on live human subjects, expressed as a fraction of standing stature — are scaled here
to a 12 in (**304.8 mm**) total figure height, using the **male** fractions (de Leva reports
separate male/female tables; male is used as the more commonly modelled "artist's mannequin"
default). This is this project's own computation, clearly not itself a published number:

| segment | male fraction of stature (de Leva 1996) | scaled to a 304.8 mm (12 in) figure |
|---|---|---|
| Head (VERT–MIDH) | 11.68% | ≈35.6 mm (1.40 in) |
| Trunk (CERV–MIDH, neck-to-hip) | 34.65% | ≈105.6 mm (4.16 in) |
| Upper arm (SK–KJC) | 16.18% | ≈49.3 mm (1.94 in) |
| Forearm (ETC–TTIP) | 15.44% | ≈47.1 mm (1.85 in) |
| Hand (WJC–fingertip) | 4.95% | ≈15.1 mm (0.59 in) |
| Thigh (HJC–knee) | 24.25% | ≈73.9 mm (2.91 in) |
| Shank (KJC–ankle) | 24.93% | ≈76.0 mm (2.99 in) |
| Foot (heel–toe) | 14.82% | ≈45.2 mm (1.78 in) |

(Fractions don't sum to 100% of stature because trunk/head/leg segments overlap at their shared
joints in this landmark scheme — de Leva's own table is a set of independently-measured
segment lengths, not a partition of total height; see item 2's own notes on this in
`data/02-segment-parameters.csv` for the alternative-endpoint rows.) These numbers are offered
as a **starting point for hand-modelling proportions from primitives**, not as a claim about
what any specific commercial 12-inch mannequin actually measures.

### 5.3 Mapping a modelled/imported doll's parts onto this project's 11 rigid bodies

This project's marionette is already defined (per the brief) as **11 rigid bodies**: pelvis,
chest, head, 2× upper arm, 2× forearm, 2× thigh, 2× shank (1+1+1+2+2+2+2 = 11). Both an
artist's mannequin (§5.1) and Mannequiny's skeleton (§4.1) use a *finer* joint set than this —
notably separate hands/fingers and feet, which this project's 11-body scheme does not model as
independent rigid bodies. The mapping used for either a hand-modelled or an imported/rigged
asset is therefore:

| this project's rigid body | artist-mannequin equivalent | Mannequiny bone name(s) |
|---|---|---|
| pelvis | hip block | `pelvis` |
| chest | torso block | `spine_01` + `spine_02` (collapse to one rigid transform) |
| head | head block (ball-jointed at neck) | `neck_01` + `head` (collapse to one) |
| upper arm (×2) | upper-arm segment, ball-jointed at shoulder | `clavicle.l/r` + `upperarm.l/r` (collapse clavicle into the shoulder joint origin) |
| forearm (×2) | forearm segment, hinge-jointed at elbow | `lowerarm.l/r` |
| thigh (×2) | thigh segment, ball-jointed at hip | `thigh.l/r` |
| shank (×2) | shank segment, hinge-jointed at knee | `calf.l/r` |

Hands and feet exist on both the artist-mannequin and Mannequiny sides but have no rigid body of
their own in this project's 11-body scheme — the simplest treatment is to parent the hand/foot
mesh rigidly to its parent bone's own transform (forearm → hand, shank → foot) rather than
animate them independently, since the sim itself does not simulate them.

## 6. Recommendation

Ranked for **this** project — a 9-second bake-once composite of an ~18 cm figure, 267 frames at
1080×1920, on a 6 GB RTX 2060, Windows, from a NumPy pose array — by visual ceiling, per-frame
cost, integration effort, and Windows risk. Every number repeated here is sourced above; where a
cell has no source it says so rather than guessing a false precision.

| route | (a) visual ceiling | (b) cost/frame @ 1080×1920, 267 frames | (c) integration effort | (d) Windows risk |
|---|---|---|---|---|
| **MuJoCo depth+seg → NumPy/OpenCV deferred (current plan, item 6's recommendation)** | High for the existing *stylised* neon-crystal look (full authorial control of every layer, item 6 §1); **lower** for a *photoreal wooden-mannequin* look, since PBR/IBL/AO/soft-shadow math would all have to be hand-rolled in NumPy from scratch, and NumPy is not GPU-parallel the way a shader is | Already working, CPU-bound; exact seconds/frame **NOT FOUND** in either this item or item 6 (no benchmark was run) | **Lowest** — already the working pipeline, already reads MuJoCo's own poses directly, no import step | **Lowest** — confirmed working via GLFW/WGL fallback (item 6 §6.3), zero new installs |
| **Blender headless (`bpy`, EEVEE Next or Cycles+OptiX)** | **Highest** for either look — real ray-traced soft shadows, SSGI, a true Cycles shadow catcher, AgX/Standard colour pipelines, built-in film grain/motion blur, and (via glTF import) direct use of Mannequiny's rig for a photoreal wooden-doll look | Cycles+OptiX: **NOT FOUND** for this exact scene; anchored against real RTX 2060 numbers for full production scenes (23.7–49.6 s/frame, §1.5) — a scene this much simpler (one small object, one HDRI, one shadow catcher, no complex materials) should render far faster, plausibly low seconds or even sub-second per frame at modest samples with OptiX+OIDN denoising, but this is this project's own extrapolation, not a citation, and 267 frames at even 5 s/frame is ~22 minutes, a real cost against the "iteration must cost minutes" render-cache discipline (memory: `render-iteration-cache`) unless a cache/preview loop is built around it | **Highest** — a second DCC/dependency (`bpy`, 338.6 MB Windows wheel, exact-Python-3.13-match confirmed §1.2) or a Blender subprocess call, a scene-construction step from the sim's own geometry/poses, and a new colour-management decision (§1.8) to avoid double-tonemapping against the plate | **Medium** — no Windows-specific EEVEE-headless pitfall was found in this pass (an open question flagged, not resolved), but `bpy`'s "no longer the recommended install method" caveat (§1.2) and the general added-dependency surface (driver ≥575 for OptiX, §1.5) are real, non-zero new risk versus the zero-install current plan |
| **moderngl / raw OpenGL deferred PBR** | High for a *photoreal* look if every stage in §2 is actually implemented (GGX+IBL+HBAO+PCSS+TAA); no ceiling advantage over Blender, but full control if a specific non-standard look is wanted later | **NOT FOUND** at 2060/1080×1920 for any of the four core passes (§2.7); order-of-magnitude anchors from 2005-2008-era GPUs at much lower resolution (§2.4-2.5) suggest each full-screen pass costs single-digit milliseconds on period hardware, and this project's coverage is a small fraction of the frame, so a bounding-box-restricted implementation should be fast, but this is reasoning, not a benchmark | **High** — every technique in §2 must be hand-written in GLSL from the ground up (no engine gives them for free); item 6 already confirms moderngl runs headless on Windows without a window, so the plumbing exists, but none of the shading code does | **Low-medium** — moderngl's headless story on Windows is already confirmed working (item 6); the risk is entirely in getting the GLSL correct, not in the platform |
| **pyrender (glTF PBR + shadow mapping)** | **Medium-high for a photoreal Mannequiny-based look specifically** — real metallic-roughness PBR and directional/spot shadow mapping "for free" (§3), directly consuming Mannequiny's own glTF materials; no IBL/AO/PCSS quality knobs beyond what the library ships | **NOT FOUND**; a lighter-weight renderer than either Blender or a hand-written moderngl pipeline, so plausibly the fastest of the three GPU-based options for a like-for-like scene, but not benchmarked here | **Medium** — smallest amount of new code of any GPU-based option (load Mannequiny's glTF, set bone poses per frame, call the offscreen renderer), but still a new dependency and, per item 6, a display-manager requirement (fine on this desktop, a real constraint if the pipeline ever needs to run on a true headless server) | **Low-medium** — same Pyglet-needs-a-display caveat as item 6 found; not osmesa/EGL-first like its Linux-oriented docs assume, but workable on this machine's normal desktop session |

**Recommendation**: for the *existing* stylised neon-crystal look, item 6's conclusion still
holds — keep the MuJoCo→NumPy/OpenCV pipeline, since a general PBR renderer actively fights a
non-physical look. But if "really compelling" specifically means moving toward a **more
photoreal wooden-marionette or ball-jointed-doll look** (which the mannequin/texture asset
search in §4 was clearly aimed at), the balance shifts: **pyrender loading the Mannequiny glTF
asset (§4.1) with the CC0 wood/plastic textures (§4.2)** is the least-effort path to a real PBR
result, since it reuses an already-rigged, correctly-licensed mesh and needs the least new code
of any GPU-based option; **Blender/Cycles+OptiX** is the higher-ceiling but higher-effort and
higher-risk option, worth a small timed test render (a handful of frames, not the whole 267) to
replace this section's "NOT FOUND" cost estimate with a real number before committing the
pipeline to it, given the render-iteration-cache discipline this project already holds itself
to; hand-rolling the full moderngl PBR/IBL/AO/PCSS stack (§2) is the most control for the least
justified effort here, since pyrender already gives most of the same visual result off the
shelf.
