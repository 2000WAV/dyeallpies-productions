# The ragdoll's graphics — plan (2026-09-12, before any build)

Dennis: "I would like the ragdoll to be really compelling." Today it is eleven capsules and
ellipsoids in a solid red, Lambert-shaded with a dark silhouette edge and sharp speculars, no shadow
on the wall, no occlusion at the joints, rendered by `tools/scripts/render_puppet.py` on the GPU
(`studio.gl`, 0.04 s a frame, since today). This plan says what "compelling" can mean for THIS shot,
ranks the options by the evidence in research items 10 and 11 (`references/marionette/`), and sets
the order of concept frames that go on Dennis's screen before any renderer is committed to.

What does not change: the sim (`puppet_sim.py`, MuJoCo on cable tendons), the hand pipeline (the
matte, the 3D pads), the bake-once split (`bake_frame()` is the only function that sees the sim and
the look; the composite reads the cache), the string model, the reel's timing.

## 1. What the evidence says "compelling" is made of (item 11, ranked by realism per hour)

1. **One consistent level of stylisation across the whole figure.** Chattopadhyay & MacDorman 2016
   (n = 365): inconsistent realism, not low realism, is what reads as eerie; Mori's own advice is to
   pursue a deliberately non-human design. A wooden doll or a mannequin is the safe target; a face on
   capsule limbs is the trap.
2. **A cast shadow on the wall, consistent with the hand's own.** Wanger 1992 and Kersten 1997: cast
   shadows dominate the depth read. But measured on this plate (frames 120 and 200, the wall's
   gradient removed): the HAND's shadow is a darkening of about 2–5 % of the wall's luminance, to the
   lower right, with a penumbra wider than the fingers. A window is a large source; item 05's relation
   `w_penumbra = w_light (d_receiver − d_blocker) / d_blocker` puts the puppet's penumbra at roughly its
   own size (a 1 m window at 2 m, the figure 0.3 m off the wall: 15 cm). So the puppet's physically
   correct shadow is a faint blob offset by hundreds of pixels, and `hand/work/concept_shadow_f120.png`
   shows it: invisible at 5 % / σ 150 px, barely there as a "film cheat" at 10 % / σ 40 px / 80 px offset.
   A shadow stronger than the hand's own would be the inconsistency of point 1 applied to lighting.
3. **A little surface roughness instead of a perfect surface.** Rademacher 2001: rough-textured
   surfaces were judged real at τ = 0.71 against 0.39 for smooth ones; the cleaner render is not the
   more convincing one.
4. **The penumbra soft, ~5°** (Rademacher's saturation point), folded into 2.
5. **Grain and a 1 px softness match** (item 05; the grain is done, the softness is not).
6. **A two-lobe specular only if the material becomes lacquer** (Ngan 2005, Filament's clear coat).
7. **Screen-space occlusion at the joints**, not ray-traced (Ramanarayanan 2007's visual equivalence:
   at a few pixels per crease nobody can tell).
8. **No synthetic depth of field**: the iPhone 14's DoF at 0.4–0.6 m spans 5–21 cm, deeper than
   intuition; check the plate for defocus before adding any.
9. **Not a learned illumination estimator** (Gardner 2017 is preferred to ground truth 42 % of the
   time; DeepLight's error is ~10°): the plate's own hand shadow already fixes the key.
10. **Not a renderer swap for its own sake**: nothing in the evidence says the stylised target needs
    physical accuracy; item 10 ranks the swap as the most effort for the least justified gain.

And one weakness the current renderer shows that no paper had to tell us: on the drop (frame 48 in
`hand/work/gl_vs_delivered.png`) the motion-blurred limbs read GREY, because a thin fast limb is
mostly "silhouette" to the dark-edge term (n·v small everywhere) and the average of eight dark
sub-samples is a grey smear, not a red streak.

## 2. The options (item 10) against this project

| route | ceiling | cost per frame on the 2060 | effort | verdict |
|---|---|---|---|---|
| **A. Grow `studio.gl`** (the moderngl deferred renderer built today): more passes on the same g-buffer, a mesh instead of capsules, the same bake-once loop | high for a stylised doll; every pass is ours; PBR + IBL + soft shadow + AO are each one shader (LearnOpenGL / Filament formulas in item 10 §2) | 0.04 s now; each full-screen pass on a bounding box adds milliseconds | medium: GLSL we write, but the plumbing, the equality check against the CPU and the cache exist since today | **the path**: it keeps iteration at 2 min and item 11's top items are all cheap here |
| **B. pyrender** loading a glTF (Mannequiny) with its PBR materials and shadow mapping | medium-high for a wooden doll; no IBL/AO/PCSS knobs beyond what ships | not benchmarked; a Pyglet display is needed (fine on this desktop) | smallest new code of the GPU options, but a second renderer beside `studio.gl`, and the strings, the matte and the bake would be re-plumbed | not chosen: it duplicates what A now has, with less control |
| **C. Blender 5.2 headless** (`pip install bpy` needs exactly Python 3.13, which `.venv-hand` is; 339 MB wheel), Cycles + OptiX with a shadow catcher, or EEVEE Next (real soft shadows and AO, but no shadow catcher) | the highest: ray-traced soft shadows, SSGI, a real shadow catcher, film grain and motion blur built in | NOT FOUND for a scene this simple; RTX 2060 numbers exist only for full production scenes (24–50 s a frame); "plausibly seconds" is our extrapolation. At 5 s a frame the 267 frames are 22 min: the 35-minute bake again unless the preview loop is rebuilt around it | highest: a scene builder from `sim.npz`, a colour-management decision (Standard view transform; AgX/Filmic would double-tone-map the BT.709 plate), driver ≥ 575 for OptiX | **only if A's ceiling proves too low on Dennis's screen**; then a timed test of five frames before anything else |
| **D. moderngl PBR from scratch** (item 10's reading of "hand-rolled") | as A | as A | item 10 ranks it highest effort, written before today's renderer existed | it is A |

Item 10 was written against yesterday's NumPy renderer; with the GPU path in place its objection to
"hand-rolling" is already paid for. The decision is A, with C held as the fallback for the ceiling.

## 3. The figure: mesh or primitives, and which material

- **Mannequiny** (GDQuest / Luciano Muñoz, CC-BY 4.0, downloaded and licence-recorded in
  `references/marionette/assets/mannequiny-gdquest/`, 13,932 triangles, 47 bones, glTF 2.0) maps onto
  the eleven bodies (item 10 §5.3: pelvis → `pelvis`, chest → `spine_01`+`spine_02`, head →
  `neck_01`+`head`, upper arms → `clavicle`+`upperarm`, forearms → `lowerarm`, thighs → `thigh`,
  shanks → `calf`; hands and feet ride rigidly on their parent). Two ways to drive it: freeze the skin
  weights to the nearest of the eleven bones and draw eleven rigid parts (keeps the per-body ID the
  shader relies on), or skin it in the vertex shader (smoother joints, the ID by dominant weight).
  It is a smooth humanoid, not a wooden doll: it would need the seams and the ball sockets painted or
  modelled to read as a marionette, and its proportions are not a 15 cm mannequin's.
- **A modelled doll from primitives, in code** (item 10 §5: ball-and-socket at shoulders and hips, hinge
  elbows and knees, seam lines, the 12-inch artist's mannequin scaled from de Leva's segment fractions,
  beech or boxwood): the same eleven bodies we have, each with a socket sphere at the joint and a
  visible seam, generated as meshes in `studio.gl` (a capsule is already one). No licence, exact
  proportions, the ID map for free, and the stylisation stays uniform (point 1 above).
- **Material**, judged by item 09's rule (a dark, saturated silhouette on the light wall, no bloom) and
  item 11 §4.5 (gloss lives inside the silhouette and does not fight the rule): candidates are matte
  painted wood (one soft lobe, the current red as its paint: the cheapest, the rule-safe default),
  lacquered wood (two lobes, clear coat, Poly Haven's `lacquered_cherry_wood_1k`, CC0, downloaded) and
  matte plastic (ambientCG `plastic001_1k`, CC0). Painted wood with the CC0 `paintedwood003_1k` texture
  gives the roughness of point 3 for free.

The recommendation is the modelled doll (primitives with sockets and seams) in matte painted wood,
with Mannequiny kept as the comparison frame; if Dennis wants a smoother humanoid, Mannequiny wins.

## 4. The build, in the order of concept frames on Dennis's screen

Every stage is one shader or one mesh change in `render_puppet.py` / `studio.gl`, previewed with
`preview=48,120,200,266` in seconds and baked in 30 s; each stage stops for a verdict.

1. **Stage A — the cheap wins on the current figure (one afternoon).**
   - The dark-edge term by distance to the silhouette in the g-buffer (pixels within ~2 px of an ID
     change) instead of n·v, so a motion-blurred limb streaks red, not grey.
   - Joint occlusion from the g-buffer: darken by distance to a different body ID (item 06 §7 step 7,
     item 11 §3.3), a few pixels wide.
   - Roughness: a small normal perturbation from a fixed 3D noise (Rademacher's point), and a 1 px
     softness match on the layer (item 05).
   - The cast shadow as a "film cheat" at the hand's own strength (≤ 10 %, σ ≈ 40 px, offset to the
     lower right along the key), multiplied into the plate under the figure, and a frame without it: the
     concept sheet already exists (`concept_shadow_f120.png`); Dennis picks.
   Verdict frames: 48 (the drop), 120 (the hang), 200, 266.
2. **Stage B — the doll (two or three days).** The eleven bodies as a modelled wooden doll: socket
   spheres, seams, a slightly larger head and hands in the mannequin's proportions, the CC0 painted-wood
   texture with a per-body UV; the same sim, the same strings. Three materials on frame 120 side by
   side (matte paint, lacquer with the clear coat, plastic), each with the Stage A passes; and Mannequiny
   posed on the same frame as the fourth tile. Verdict: the figure and the material.
3. **Stage C — light (one day).** Image-based lighting from a small synthetic environment (a bright
   window at the left, the off-white wall as the fill) with the split-sum prefiltered maps (LearnOpenGL,
   item 10 §2.3), replacing the single key + ambient; the specular read then follows the room. Check
   against the plate's hand: the puppet's brightest side must be the hand's brightest side.
4. **Stage D — only if the ceiling is not enough:** the Blender test, five frames of the Stage B doll
   in Cycles + OptiX through `bpy`, timed, with the shadow catcher; the decision then is on a measured
   cost per frame against the 2-minute loop we have.

## 5. What stays out, with the reason

- Bloom, a bright rim, a glossy full-body highlight: item 09 (the light wall).
- A face, fingers, cloth: point 1 (a detailed part on a simple body is the uncanny case).
- Synthetic depth of field: point 8. A learned light estimator: point 9.
- A stronger shadow than the hand's: point 2 (it would contradict the plate).
- A second renderer beside `studio.gl` (pyrender): the bake-once loop, the strings and the matte are
  plumbed once; a second path would have to redo them.

## 6. Sources

`references/marionette/10-rendering-routes-and-mannequin-assets.md` (Blender 5.2 and `bpy`, EEVEE
Next and Cycles + OptiX facts, the LearnOpenGL / Filament formulas and buffer sizes, HBAO Bavoil 2008,
SSAO Mittring 2007, PCSS Fernando 2005, the asset table and licences, the mannequin's construction and
proportions, the body mapping) and `11-cg-realism-in-phone-footage.md` (Rademacher 2001, Wanger 1992,
Kersten 1997, Ramanarayanan 2007, Lalonde & Efros 2007, Chattopadhyay & MacDorman 2016, Mori,
Gardner 2017, LeGendre 2019, Debevec 1998, Ngan 2005, the DoF computation, the reference looks), with
their CSVs in `references/marionette/data/10-*.csv` and `11-*.csv`, plus the plate measurement of the
hand's shadow made for this plan (2026-09-12, frames 120 and 200; the method is in HANDOFF.md's
session note and will move into the renderer as the light check when Stage A is built).
