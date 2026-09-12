# Item 11 — what makes a small CG object read as real in phone footage, ranked by what it buys

Context: the marionette (11 rigid bodies, capsules and ellipsoids, currently a solid-red
shader with a dark silhouette edge and no wall shadow) composited into the 9 s handheld
iPhone 14 shot (item 05: 1080x1920, 30 fps, tone-mapped from HLG/BT.2020 to SDR BT.709,
main camera 26 mm-equivalent/f1.5, derived actual focal length 5.75 mm) of a hand from the
back in front of an off-white wall (item 09: sRGB #F2F0EA, L*=94.8) lit from a window on the
left, the figure hanging ~30 cm off the wall on five strings. Dennis wants it "really
compelling"; this is the research pass before the graphics plan (HANDOFF.md follow-up 3) is
written. This item does NOT redo item 05 (camera intrinsics, light-from-shadow geometry, the
PCSS penumbra relation, shadow-catcher basics, grain matching) or item 09 (colour and
figure-ground) — both are read and cited below wherever they already answer part of the
question, not repeated.

All files referenced live in `references/marionette/papers/` (full text or saved page) and
`references/marionette/abstracts/` (summaries); see `downloads-11.md` for the URL/licence/
date of every file fetched this pass, and `data/11-realism-numbers.csv` for every number.
"**NOT FOUND**" marks a claim in the task brief that could not be sourced to a citable file.

---

## 1. Perception of realism: what cues actually make a rendered object read as real

### 1.1 Shadow softness and surface smoothness (Rademacher et al. 2001)

The direct, purpose-built answer to "which visual factors make a CG image read as real":
Rademacher, Lengyel, Cutrell & Whitted, *Measuring the Perception of Visual Realism in
Images* (`papers/rademacher2001-visual-realism.pdf/.txt`), EGWR 2001, ran forced-choice
("real"/"not real") experiments on photographs and matched CG renders, varying one factor at
a time.

- **Shadow softness.** Five penumbra levels were measured directly in the images: **0.39,
  1.5, 2.5, 5.2 and 10.3 degrees**. Shadow softness was a statistically significant predictor
  of realism overall (chi^2=4.31, df=1, p=.0379). Pairwise tests found the jump to
  significance happens at the **5.21-degree** level versus the sharpest (0.39 deg) shadows
  (chi^2=5.39, df=1, p=.0203) — and there is **no** significant difference between the two
  softest levels, 5.2 vs 10.3 degrees (chi^2=2.64, p=.1043). In plain terms: sharp shadows
  read as fake, softening buys realism steeply up to roughly 5 degrees of penumbra, and
  softening further than that has diminishing returns. This is a numeric target for section 3
  below and for item 05's own PCSS penumbra relation (`w_penumbra = w_light*(d_r-d_b)/d_b`).
- **Surface smoothness.** Counter to a naive "smoother renders more real" assumption: smooth
  (spray-painted) blocks were rated real at **tau=.39**, while rough (visibly brush-painted)
  blocks were rated real at **tau=.71** — a large effect in the opposite direction. A
  perfectly smooth CG surface (which is exactly what a flat-shaded capsule/ellipsoid is) reads
  as *less* real than one with visible surface imperfection. Directly relevant to section 4:
  the puppet's current perfectly smooth solid-red shading is fighting this finding.

### 1.2 Cast shadows dominate spatial/depth judgement (Wanger et al. 1992; Kersten et al. 1997)

Two classic psychophysics results establish that a cast shadow is disproportionately
load-bearing for "the object is really there, at that distance from that surface" — well
beyond what its rendering cost would suggest.

- **Wanger, Ferwerda & Greenberg 1992**, *Perceiving Spatial Relationships in
  Computer-Generated Images* (`papers/wanger1992-perceiving-spatial-relationships.pdf`; IEEE
  CG&A 12(3), 44-58) ran three experiments on how accurately subjects match an object's
  position/orientation/size to a standard, under different combinations of shadows, motion
  parallax, texture and perspective. The saved PDF is a 1992 scan with no OCR text layer (no
  OCR tool is available on this machine — see `downloads-11.md`), so the exact accuracy
  numbers per cue are **NOT FOUND** here; the well-established qualitative result (from the
  paper's own widely-cited description, not independently re-verified against this PDF) is
  that texture had only a small effect, **shadows had a major effect** on relative-position
  judgments, and motion parallax's effect was inconsistent/task-dependent.
- **Kersten, Mamassian & Knill 1997**, *Moving Cast Shadows Induce Apparent Motion in Depth*
  (abstract only, `abstracts/kersten1997-moving-cast-shadows-apparent-motion-depth.txt`,
  PMID 9274752; Perception 26(2):171-192) is the "ball-in-a-box" demonstration: a ball on a
  fixed on-screen path appears to slide along a floor or rise off it *purely as a function of
  how its cast shadow moves*, overriding other strong cues (constant object size, generic
  viewpoint). The visual system assumes a stationary light source and misattributes shadow
  motion caused by a moving light to the object moving instead.

Together with item 05's own shadow-direction-from-the-hand's-shadow recipe, these two papers
are the reason a plausible cast/contact shadow for the marionette (section 3) is worth more
attention than its modest rendering cost would suggest — the wall shadow is one of the
single strongest cues that the figure hangs 30 cm off the wall rather than floating pasted on
top of the footage.

### 1.3 Visual equivalence, not pixel accuracy (Ramanarayanan et al. 2007)

Ramanarayanan, Ferwerda, Walter & Bala, *Visual Equivalence: Towards a New Standard for Image
Fidelity* (`papers/ramanarayanan2007-visual-equivalence.pdf/.txt`, ACM TOG/SIGGRAPH 2007)
propose that two renderings are "visually equivalent" if observers cannot reliably tell they
convey *different* scene appearance, even if the pixels differ — a **75%-correct-detection**
threshold is used to define "reliably different." Applying a looser, visual-equivalence-tuned
error threshold in a real renderer (Lightcuts) cut render time by roughly **50%** with no
perceptible fidelity loss versus a stricter threshold. This reframes several of section 7's
ranked items: screen-space AO vs ray-traced AO, or an approximate vs physically exact contact
shadow, are visual-equivalence bets — the question is not "is it physically correct" but "can
anyone tell," which is a much lower and cheaper bar for a 9-second phone clip.

### 1.4 Color compatibility as an independent realism signal (Lalonde & Efros 2007)

Lalonde & Efros, *Using Color Compatibility for Assessing Image Realism*
(`papers/lalonde2007-color-compatibility-realism.pdf/.txt`, ICCV 2007) classify composite
images as realistic vs. not using *only* the pasted object's color-distribution compatibility
with its new background — no geometry, shading or matte-quality signal at all. Their best
classifier (joint color histogram + texture-matched nearest neighbour) reaches **ROC AUC
0.78-0.79** (texture alone: 0.59; chance = 0.5). This is an independent line of evidence for
item 09's pure-red recommendation: getting the puppet's hue/warmth relationship to the
off-white wall right is not only a salience trick, it measurably predicts perceived realism
in the compositing literature on its own terms.

### 1.5 Real-vs-CG discrimination (Fan et al. 2012; "Kalantari" — **NOT FOUND**)

Fan, Ng, Herberg, Koenig & Xin, *Real or Fake?: Human Judgments about Photographs and
Computer-Generated Images of Faces* (SIGGRAPH Asia 2012 Technical Briefs) is widely cited as
establishing that ordinary viewers can reliably tell CG face renders from photographs above
chance, with later work in the same group identifying the eyes as the most influential region
for the judgement — but no fetchable copy of the paper or its abstract could be located this
pass (see `downloads-11.md`; `abstracts/11-fan2012-real-or-fake.txt` documents the attempt and
what is cited via secondary description only). Its direct applicability is limited here in
any case: it is a face-realism study, and this marionette is a stylized, non-photoreal
humanoid figure, not an attempt at a photoreal face.

A citable "Kalantari" paper specifically on real-vs-CG discrimination, as named in the task
brief, is **NOT FOUND** — every search surfaced either Nima Khademi Kalantari's unrelated
HDR/denoising work or other authors' discrimination studies (Fan et al. above; Mader, Banks &
Farid 2017's "Identifying Computer-Generated Portraits"). Treated as a likely
mis-specification in the brief; not used as a citation below.

### 1.6 The uncanny valley, and why it matters for a stylized marionette

The brief asks for this literature "since this is a humanoid figure" — but the key finding
across all three sources below is that a **stylized, uniformly non-photoreal figure like this
marionette is exactly the safe zone**, not a figure to worry about crossing into the valley.

- **Mori 1970, translated 2012** (`papers/mori1970-2012-uncanny-valley.pdf/.txt`, IEEE
  Robotics & Automation Magazine): the founding essay. Affinity for a humanlike figure rises
  with human-likeness, then plunges sharply ("the uncanny valley") just short of true
  likeness, before recovering at true likeness. Mori's own prescriptive conclusion, easy to
  miss: since climbing all the way out of the valley is hard, a designer should consider
  **"deliberately pursuing a nonhuman design"** to achieve "a safe level of affinity" — his
  own example is a toy robot, sitting well before the valley on the strength of being clearly,
  charmingly non-human, not despite it.
- **Mathur & Reichling 2016** (abstract only,
  `abstracts/mathur-reichling2016-uncanny-valley-cartography.txt`, PMID 26402646; Cognition
  146:22-32) is the first study to demonstrate a real uncanny-valley effect using 80
  *objectively chosen real-world robot faces* rather than only artificially blended/morphed
  images (which had produced inconsistent results before this paper) — confirming the effect
  is real, not an artifact of earlier studies' image-blending methodology, and that it
  penetrates to implicit trust judgements, not just stated likability.
- **Chattopadhyay & MacDorman 2016**, *Familiar Faces Rendered Strange*
  (`papers/chattopadhyay-macdorman2016-familiar-faces-rendered-strange.pdf/.txt`, Journal of
  Vision 16(11):7) is the single most load-bearing citation for this project's checklist: in a
  study of **365 participants**, reducing realism *consistency* across an image's features (a
  photoreal face on a cartoonish body, or vice versa) did **not** make objects-in-general
  appear less familiar — but for animals and humans specifically it did, and specifically
  triggered the cold, eerie affect associated with the uncanny valley. **Uniformly low
  realism does not trigger it; inconsistent realism does.**

**Synthesis for this project:** the marionette's smooth capsules/ellipsoids, single solid-red
material and uniform shading are, per this literature, the *safe* choice — Mori's own "toy
robot" analogue. The graphics-plan follow-up in HANDOFF.md should be read with this in mind:
adding a highly detailed, differently-shaded face or hands while the rest of the body stays
primitive-shaped would risk the exact inconsistency Chattopadhyay & MacDorman show triggers
eeriness — a uniform upgrade (e.g. all-over lacquered wood, section 4) stays safe; a
partial one (a realistic face bolted onto capsule limbs) does not.

---

## 2. Illumination estimation from a single frame — and what this shot already has for free

### 2.1 What single-image learned illumination estimation actually achieves

Three papers the brief names, all read for their reported ERROR, not just their existence,
to calibrate how much a learned approach would actually buy over item 05's simpler
single-key-plus-ambient model:

- **Gardner et al. 2017**, *Learning to Predict Indoor Illumination from a Single Image*
  (`papers/gardner2017-indoor-illumination-arxiv.pdf/.txt`, SIGGRAPH Asia 2017/ACM TOG)
  regresses a single LDR indoor photo directly to HDR omnidirectional illumination. Their own
  **perceptual user study** (105 participants, 1080 pairwise comparisons) found their best
  (HDR) network's relit composites were judged as-or-more-realistic than the *ground-truth*-lit
  reference in only **41.85%** of comparisons — beating prior methods (Khan et al. 2006:
  27.78%; Karsch et al. 2014: 16.76%) but still losing to ground truth more than half the
  time. Reported failure modes: sharp small lights get blurred into larger, softer ones (no
  crisp cast shadows), and the network is much better at light *position* than light
  *intensity*.
- **LeGendre et al. 2019, DeepLight** (`papers/legendre2019-deeplight.pdf/.txt`, CVPR 2019) is
  the closest of the three to this project's actual hardware: it infers HDR lighting from a
  single **ordinary mobile-phone photo**. Its best configuration's own reported error on a
  rendered diffuse test sphere is an **RGB angular error of about 9.8-10.8 degrees**
  (n=450, indoor/outdoor unseen locations) — i.e. even state-of-the-art phone-photo lighting
  inference is typically off by roughly 10 degrees of light direction.
- **Hold-Geoffroy et al. 2017**, *Deep Outdoor Illumination Estimation*
  (`papers/holdgeoffroy2017-deep-outdoor-illumination.pdf/.txt`, CVPR 2017) and **Hold-Geoffroy
  et al. 2019**, *Deep Sky Modeling for Single Image Outdoor Lighting Estimation*
  (`papers/holdgeoffroy2019-deep-sky-modeling.pdf/.txt`, CVPR 2019) fit/learn a sky-dome model
  from a single outdoor photo — not directly applicable to this indoor, window-lit shot, but
  useful as the *easiest possible case* (one dominant, extremely bright, well-modeled source):
  even here, **80% of test images have combined sun-position error under 45 degrees**, sun
  elevation error under **7 degrees** for 80% of images, and camera FOV error under **11
  degrees** for 80% of images. If the easiest single-light case still carries several degrees
  of unavoidable error, a general learned estimator is not obviously better than a
  scene-specific measurement for this shot.

### 2.2 What this specific shot already has, essentially for free

The punchline of section 2.1's numbers: **this shot does not need a learned illumination
estimator.** Item 05 already has something better than any of the above for this exact frame
— a single, dominant, already-visible light source (the window) whose direction and
approximate angular size can be read directly off the **hand's own cast shadow already in the
plate** (item 05 section 2, the PCSS-inversion recipe), which uses this frame's own
ground-truth shadow evidence rather than a population prior fit to millions of other rooms.
That beats DeepLight's ~10-degree error bar in principle, because it is not a *guess* informed
by similar-looking rooms, it is a *measurement* of this room. The window key plus a bright
ambient/bounce term from the light off-white walls (a large, soft area light from the left,
consistent with item 05's own framing) is exactly the "single-key-plus-ambient" model that
this evidence says is sufficient — a full spherical-harmonics environment map would model
indirect bounce more completely, but for a single dominant window key in a small room, the
marginal gain is unlikely to be visible at this figure's scale (~15 cm) against the ~10-degree
error floor these learned methods themselves report.

---

## 3. Contact and cast shadows, and ambient occlusion

### 3.1 The shadow-catcher's origin, and why it needs only an approximate wall BRDF

**Debevec 1998**, *Rendering Synthetic Objects into Real Scenes*
(`papers/debevec1998-rendering-synthetic-objects.pdf/.txt`, SIGGRAPH 1998) is the paper item
05 already cites qualitatively for the shadow-catcher technique; read in full here for the
mechanism: split the scene into the distant scene (an HDR light probe supplying incident
illumination), the local scene (the real surfaces nearest the inserted object — here, the
wall), and the synthetic object. **Differential rendering**: render the local scene twice with
a global-illumination solver, once with the object present and once without; the *difference*
is exactly the object's lighting contribution (new shadows, bounced light), which can be added
onto the real photograph. The key practical point for this shot: because it is a *difference*
of two renders, errors in the assumed wall BRDF mostly cancel — the wall's reflectance only
needs to be approximately right (matte, off-white, item 09's #F2F0EA), not precisely measured,
for the added shadow to look correct.

### 3.2 Shadow softness for THIS geometry (marionette 30 cm off a window-lit wall)

Combining Rademacher's target (~5 degrees of penumbra reads as maximally real, section 1.1)
with item 05's own penumbra relation `w_penumbra = w_light * (d_receiver - d_blocker) /
d_blocker`: for a marionette 30 cm off the wall (`d_receiver - d_blocker = 0.30 m`), reaching a
5-degree penumbra implies solving for the effective window angular size `w_light` at the
puppet's distance from it — the same inversion item 05 already sets up for the hand's own
shadow, applied to the puppet instead of the hand. Since the puppet is small (~15 cm) and its
blocker distance from the window is not itself separately measured in this project, the
practical recipe is: **reuse the window direction and angular size already solved from the
hand's shadow (item 05 section 2.2)** rather than re-deriving it independently for the puppet
— it is the same light, and consistency between the two shadows (hand's and puppet's) is
itself a stronger realism cue than either shadow's individual softness (an inconsistent
shadow direction between the hand and the puppet would be a dead giveaway, per the same logic
as Chattopadhyay & MacDorman's inconsistency finding, applied to lighting rather than
material). Expect an **offset toward the lower-right** of the puppet's ground-plane projection
(shadow points away from the lower-left window) and a **soft, not sharp**, penumbra, since a
window is a large-angular-size source at this distance, consistent with item 05's own "lit
from the lower left, soft shadow" framing of the plate.

### 3.3 Screen-space AO vs ray-traced AO for the joints

Item 06 already establishes that MuJoCo's own renderer computes no AO (section 6.4 of that
document) and recommends synthesizing occlusion at the joints from the segmentation+depth
buffers. For THIS shot specifically: given the visual-equivalence argument (section 1.3
above) and the small on-screen scale of each joint crevice (a handful of pixels at most, on a
~15 cm figure filling a fraction of a 1080x1920 frame), a cheap screen-space proxy (e.g.
distance-to-nearest-different-segid, already recommended in item 06 section 7 step 7) is very
unlikely to be visually distinguishable from a full ray-traced AO pass at this scale and
viewing distance — ray-traced AO is the "big build" end of section 7's ranking, not
recommended for this shot's return on effort.

### 3.4 Rademacher's shadow-softness evidence, restated for this section

Already covered in full in section 1.1; restated here only as the numeric anchor for this
section's shadow-softness target: **~5.2 degrees of penumbra** is where realism gains from
softening a shadow saturate (Rademacher et al. 2001).

---

## 4. Materials on a light wall: matte wood, lacquered wood, matte plastic, the current solid red

### 4.1 Measured reference data exists for exactly these material categories

**Matusik, Pfister, Brand & McMillan 2003**, *A Data-Driven Reflectance Model*
(`papers/matusik2003-data-driven-reflectance-model.pdf/.txt`, ACM TOG/SIGGRAPH 2003) is the
paper behind the MERL BRDF database: **100 real, densely-measured materials**
(`papers/merl-brdf-database.html`, `papers/merl-mit-brdf-database.html`). The actual file
list (`papers/merl-brdf-filelist.html`, a fetched directory listing) confirms real samples in
every category this section needs:

- **Finished/lacquered wood**: `cherry-235`, `colonial-maple-223`, `fruitwood-241`,
  `ipswich-pine-221`, `natural-209`, `pickled-oak-260`, `special-walnut-224` — names
  consistent with a furniture-finish reference set (i.e. these are lacquered/varnished wood
  finishes, not raw unfinished wood grain — MERL measures smooth BRDF spheres, so an
  unfinished, highly non-uniform raw-wood-grain look is not represented in this dataset).
- **Paint** (a good analogue for "matte painted wood"): `white-paint`, `dark-blue-paint`,
  `dark-red-paint`, `orange-paint`, `yellow-paint`, plus glossier metallic variants
  (`gold-metallic-paint`, `silver-metallic-paint`, `pearl-paint`).
- **Plastic**: `gray-plastic`, `red-plastic`, `pvc`, `delrin`, `teflon`,
  `yellow-matte-plastic` — spanning both glossy and explicitly matte plastic.

**NOT FOUND**: a simple, directly-quotable scalar roughness value per material from this
paper itself — Matusik et al.'s model represents each material as PCA weights over measured
BRDF lobes ("traits" like metallic-like, plastic-like, roughness, silverness, gold-like,
fabric-like), not a single number.

### 4.2 What an analytic-model fit says about wood/paint/plastic (Ngan et al. 2005)

**Ngan, Durand & Matusik 2005**, *Experimental Analysis of BRDF Models*
(`papers/ngan2005-experimental-analysis-brdf-models.pdf/.txt`, EGSR 2005) fit standard
analytic microfacet models (Cook-Torrance, Ward, Blinn-Phong, etc.) to all 100 MERL materials
and report which model class fits which material class. The qualitative finding, quoted
directly: a **single** microfacet lobe fits "fabrics, rubber and paints" well, while **highly
specular** materials — explicitly named: "brushed metals" and "highly specular plastics" —
need a **two-lobe** fit (a broad coarse lobe plus a narrow fine one) to capture both a wide
soft sheen and a sharp hard highlight; a single lobe under- or over-blurs one of the two.
**NOT FOUND**: the paper's own numeric per-material roughness/exponent table, which lives in a
supplemental spreadsheet not fetched this pass (see `downloads-11.md`).

**Implication for the puppet's material choice:** a *matte painted* look (wood or plastic)
needs only one soft specular lobe — cheap, and matches the "paints" category directly. A
*lacquered* look needs the two-lobe construction: keep the body's diffuse/soft-specular
response (the paint colour and a broad soft sheen) and layer a second, much narrower, much
sharper highlight on top for the lacquer coat — not a single glossier version of the same
lobe.

### 4.3 Filament's own clear-coat model: lacquered wood is two layers, not one

**Google's Filament Materials Guide** (`papers/filament-materials-guide.html`), a widely-used
open PBR renderer's documentation, has a dedicated clear-coat layer explicitly named for **"car
paint, soda cans, lacquered wood, and coated metals"** — i.e. the renderer's own authors treat
lacquered wood as inherently two-layer: a rougher, coloured base coat (the wood/paint) plus a
separate, near-perfectly-smooth (very low roughness) clear coat on top, each with its own
roughness parameter. This corroborates Ngan et al.'s two-lobe finding independently, from a
production-renderer perspective rather than a measured-BRDF-fitting one. **NOT FOUND**: a
single numeric roughness value per material name in the fetched guide (it teaches the model
qualitatively with example-image sweeps, not a lookup table).

### 4.4 Fresnel on a lacquered surface; subsurface for painted wood is negligible

Item 06 already covers Schlick's approximation in full (`papers/lettier-fresnel-factor.html`,
Schlick exponent default 5, stylised-wide-rim convention ~2-3) — the same fresnel term applies
directly to a lacquered clear coat: at grazing angles even a matte-looking lacquered surface
brightens toward white/specular, because the clear coat itself is a smooth dielectric
regardless of how rough the coloured layer underneath is. This is exactly the mechanism
Filament's two-layer model captures (section 4.3) and is already in this project's shader
plan (item 06 section 3). Subsurface scattering for painted wood is negligible: opaque paint
and lacquer are both optically thick within a millimetre or two, so light does not travel
meaningfully through the material and re-emerge elsewhere — no source in this pass modeled a
subsurface term for a painted/lacquered surface, consistent with treating it as zero (not a
"NOT FOUND," simply not a real effect at this material's optical density).

### 4.5 The dark-edge contrast rule (item 09) still wins over a glossy read

Item 09's contrast rule (a dark, saturated body against the bright wall, a dark or no rim, no
bloom on this side of the shot) is about **figure-ground contrast at the object's silhouette**
and is orthogonal to, not overridden by, the specular/glossy read discussed here, which is
about **within-body shading** (does the puppet look like a solid lit volume). A lacquered
look's fresnel/specular highlights are small, local, bright points or thin curved bands *well
inside* the puppet's dark silhouette — they do not push the silhouette edge itself toward the
wall's brightness the way a full-body bloom did in the old neon look. The two recommendations
compose: keep the body dark/saturated red at the edge (item 09), add a glossy two-lobe
specular/fresnel read for volume (this section) — they operate at different spatial scales of
the same image.

---

## 5. Lens, motion and edge integration

### 5.1 Depth of field at 0.4-0.6 m: the phone's DoF is deeper than intuition suggests

Using item 05's own derived numbers (actual focal length 5.75 mm, f/1.5, sensor diagonal
9.576 mm) and the standard thin-lens formulas (`papers/wikipedia-depth-of-field.html`,
`papers/wikipedia-circle-of-confusion.html`: hyperfocal distance `H = f^2/(N*c) + f`, near/far
limits `Dn = H*s/(H+(s-f))`, `Df = H*s/(H-(s-f))`), computed for two circle-of-confusion
conventions (the conservative "diagonal/1500" print criterion, c=6.38 micron; and a tighter
"2 pixels" on-screen criterion, c=3.8 micron, using item 05's 1.9 micron pixel pitch):

| focus distance | DoF span (diag/1500, looser) | DoF span (2px, tighter) |
|---|---|---|
| 0.4 m (near item 05's hand distance) | 359-452 mm (**92 mm** span) | 375-429 mm (**55 mm** span) |
| 0.6 m (plausible puppet distance, wall-setback-dependent) | 512-725 mm (**213 mm** span) | 544-668 mm (**124 mm** span) |

(Full working in `data/11-realism-numbers.csv`.) The counterintuitive takeaway: despite the
fast f/1.5 aperture, the iPhone 14's small sensor gives a genuinely **deep** depth of field at
these near-macro distances — tens of millimetres to over 20 cm of acceptable focus even at
0.6 m. Since the hand is at ~0.3-0.4 m and the puppet is somewhat farther back (30 cm off a
wall whose own distance from the camera is not separately pinned down in this project), the
puppet likely sits at or just past the far edge of the hand's own critical-focus zone at these
DoF spans — meaning it could plausibly be captured with **very little or no optical
defocus** in the real plate. Practical recommendation: check the plate itself for any visible
softening between the hand and the wall plane before adding synthetic defocus blur to the CG
puppet; a "shallow portrait DoF" assumption would be *wrong* for this phone/distance
combination and would make the CG puppet look artificially separated from its surroundings by
an effect the real lens likely does not actually produce here.

### 5.2 Light wrap, edge blending, and the sub-pixel edge

Already covered in depth by item 05 section 3.1 (light wrap and additive glow) and section 4.6
(premultiplied alpha, linear-light "over," black-level matching) — both citing Wright's
*Digital Compositing for Film and Video* and Brinkmann's *The Art and Science of Digital
Compositing* bibliographically only (no legally obtainable full text found by item 05; not
re-attempted here, same **NOT FOUND** status carries over). Nothing to add beyond noting that
the light-wrap direction now runs from a *dark* saturated puppet against a *bright* wall
(post-item-09), which is the reverse of the original neon-glow light-wrap case item 05 wrote
up — a light wrap here should pull a thin sliver of the bright *wall's* colour onto the
puppet's edge (simulating the wall's ambient light grazing the puppet's silhouette), not the
puppet's colour bleeding onto the wall, since there is no longer an emissive glow to spill.

MuJoCo's own `offsamples` MSAA control (item 06 section 6.1: default 4x, only active for
offscreen rendering) plus the existing 2x internal render resolution (item 06 section 10) are
already the project's sub-pixel edge quality controls; no new number to add here.

### 5.3 Chromatic aberration and lens softness on a phone: **largely NOT FOUND, low priority**

Item 05 section 1.4 already establishes, from Apple's own spec sheet (lens correction listed
only for the ultra-wide camera, not main) and DXOMARK/GSMArena's photo-quality write-ups
(`papers/dxomark-iphone14-camera-test.html`, `papers/gsmarena-iphone14-review-video.html`, no
significant geometric-distortion complaints for the main camera), that the main lens is
treated as effectively distortion-free. A dedicated search this pass for a numeric
iPhone-14-specific chromatic-aberration or MTF measurement turned up only generic
lens-testing methodology pages (MTF test-bench descriptions, not iPhone-14-specific numbers)
— **NOT FOUND** for a citable CA or MTF number for this exact camera. Given the marionette
sits near frame-center (item 05 section 4.5 already makes this same point for CA), and the
phone's own JPEG/video pipeline already applies whatever correction it applies before the
footage ever reaches this project, this remains a low-priority item: match whatever small
softening the real footage shows (a 1-pixel-radius match-blur, per item 05 section 4.3) rather
than modeling CA or MTF from first principles.

### 5.4 Noise/grain: nothing to add beyond item 05

Item 05 section 4.2 already covers signal-dependent, per-channel sensor noise
(`papers/cao2023-physics-guided-iso-noise-modeling.pdf`) in full, including the practical
recipe (measure the plate's own noise on the flat wall region, fit `variance ~ a + b*signal`
per channel). Nothing in this pass's sources adds to that; restated here only so section 7's
checklist can reference it as an existing, already-specified item.

---

## 6. Reference looks: how films make marionettes and wooden puppets convincing

Short, per the brief, since the deep dive here is items 1/2 (construction/stringing/dynamics)
and this document's sections 1-5 (rendering/perception), not film history.

- **Team America: World Police (2004)** — "The World on a String"
  (`papers/theasc-team-america-world-on-a-string.html`, American Cinematographer) confirms the
  strings were left genuinely **visible throughout**, a deliberate choice, not a compositing
  failure the crew tried to hide — shots were timed so wires would not upstage a scene's own
  joke, rather than removed. This is the clearest counter-evidence to any assumption that
  strings must be invisible to read as convincing; it is the puppet's **weight, motion physics
  and timing** that sell it, not string invisibility — directly consistent with this project's
  own choice (item 09) of dark, non-glowing strings rather than trying to erase them.
- **Thunderbirds / Supermarionation** (`papers/gerryanderson-supermarionation-without-strings.html`)
  — Gerry Anderson's puppets used very fine wires that did double duty as suspension/control
  lines *and* electrical conductors to solenoid mouth-motors (the first puppet production with
  electronic lip-sync at scale). The wire's fineness was a functional requirement as much as a
  visibility choice — another data point that a successful, iconic marionette look does not
  depend on eliminating visible rigging.
- **Czech marionette film — Jiri Trnka** (`papers/wepa-jiri-trnka.html`, World Encyclopedia of
  Puppetry Arts): Trnka's puppets typically have simplified, near-expressionless carved faces;
  the illusion of life comes from **body language, staging, and lighting**, not facial detail
  — a strong precedent for this project's own simplified capsule/ellipsoid figure, and
  consistent with Kleffner & Ramachandran 1992's finding (already cited in item 09) that one
  consistent, plausible key light reads as "solid" almost pre-attentively, independent of
  surface detail.
- **The Dark Crystal** (`papers/creatureshop-dark-crystal-age-of-resistance.html`, Jim Henson's
  Creature Shop) sits at the opposite end of the spectrum: 170+ puppets and 125+ artists (2019
  series) invested heavily in skin texture, hair and materials specifically because those
  characters are meant to read as near-photoreal creatures — useful calibration for how much
  material investment the graphics-plan follow-up would need if it aimed for that register
  instead of a stylized one (per section 1.6's uncanny-valley argument, not recommended).
- **Pinocchio (del Toro, 2022)** (`papers/beforesandafters-pinocchio-puppet-head.html`,
  befores & afters): for a character meant to visibly read as **carved wood**, the production
  used a **replacement** technique (discrete, individually fabricated parts per pose/
  expression, some metal-3D-printed) rather than deforming one continuous material — because
  wood does not deform smoothly like flesh; a believable "wood" read depends on hard edges and
  discrete parts at every joint. Directly actionable if the graphics-plan pursues a
  "matte painted wood" material (section 4): keep visible seams/hard edges at each
  capsule-to-capsule joint rather than blending them smooth.
- **Kubo and the Two Strings** (`papers/inverse-kubo-3d-printed-puppets.html`, LAIKA)
  reinforces the same point at industrial scale (one character: 850 3D-printed exterior pieces
  over a 250-part armature) — a cast of many rigid, purpose-built parts is an established,
  successful way to build a convincing puppet, not a compromise forced by using rigid MuJoCo
  primitives.
- **What a typical "AR object in hand" reel gets wrong**
  (`papers/renderahouse-why-renders-look-fake.html`, a working archviz practitioner's
  checklist, cited for its checklist only, not as peer-reviewed evidence): the single most
  common, most fixable failure named is a **weak or missing contact shadow**, making an
  inserted object look like it floats rather than rests/hangs in the scene — the same failure
  mode item 05 flags as a "nice-to-have" for this shot (section 2.3) and this document
  upgrades to a real recommendation in section 7. The same source recommends a **two-part**
  shadow (a broad soft ambient shadow plus a tighter, darker occlusion shadow right at the
  actual contact/attachment point) rather than one uniform soft shadow — a concrete, cheap
  structure for the marionette's five string-attachment points at the fingertips and for the
  wall shadow.

---

## 7. Ranked checklist for THIS shot (light wall, window key from the left, handheld phone, 15 cm figure, 30 cm off the wall)

Ordered by realism bought per hour of work, cheapest/highest-leverage first. "Evidence" cites
the section above; "cost" flags cheap test vs. big build.

1. **Consistency of shading style across every body part — keep it uniform.** *Cost: free
   (a discipline, not a build).* Evidence: section 1.6 (Chattopadhyay & MacDorman 2016 — 365
   participants; inconsistent realism, not low realism, drives eeriness) and Mori's own
   "deliberately pursuing a nonhuman design" prescription. This is rank 1 because it costs
   nothing but restraint, and getting it wrong (e.g. bolting a detailed face onto primitive
   limbs in the graphics-plan follow-up) actively *hurts* realism rather than merely failing
   to help it.
2. **A contact/cast shadow on the wall, using the SAME light direction already solved from the
   hand's shadow (item 05).** *Cost: cheap-to-moderate — a shadow-catcher differential render
   (Debevec 1998, section 3.1), reusing item 05's already-derived window direction.* Evidence:
   sections 1.2 (Wanger 1992, Kersten 1997 — cast shadows dominate depth judgement) and 3.2
   (Rademacher's ~5-degree penumbra target); also the single most commonly cited generic
   compositing failure (section 6, renderahouse.com: "floating object, no contact shadow").
   High leverage because item 05 already did the hard part (measuring the light); this is
   mostly reuse, not new work.
3. **A small amount of surface roughness/imperfection instead of a perfectly smooth render.**
   *Cost: cheap — a noise/roughness texture on the existing shader, no new render pipeline.*
   Evidence: section 1.1 (Rademacher: rough tau=.71 vs smooth tau=.39 — nearly double the
   "real" rating). Directly contradicts the intuition that a cleaner render is a better one;
   worth doing before any bigger material overhaul.
4. **A soft (~5-degree penumbra) shadow, not a sharp one, if/when the cast shadow above is
   built.** *Cost: folded into item 2 above — a rendering parameter, not separate work.*
   Evidence: section 1.1/3.2/3.4 (Rademacher's own threshold).
5. **Grain/noise match and a 1-pixel softness match-blur on the CG layer.** *Cost: cheap —
   already specified in item 05 section 4.2-4.3; not new work, just execution.* Evidence:
   section 5.3-5.4. Ranked mid-list because it is cheap and already-designed, but its
   perceptual payoff (subtle "this was actually shot on the same camera" cue) is smaller than
   shadow/consistency/material fixes above.
6. **A two-lobe (broad soft + narrow sharp) specular/fresnel read, if the material moves
   toward lacquered wood.** *Cost: moderate — a real shader change (section 4.2-4.4), not a
   parameter tweak; depends on the graphics-plan follow-up's direction.* Evidence: Ngan et al.
   2005 (section 4.2) and Filament's own clear-coat model (section 4.3). Only worth it if
   Dennis wants the glossier "lacquered" look specifically; a matte painted-wood or
   matte-plastic material (single soft lobe) is cheaper and, per item 09, does not fight the
   dark-edge contrast rule at all.
7. **Screen-space (not ray-traced) AO at the joints.** *Cost: cheap — a depth/segid proxy,
   already planned in item 06.* Evidence: section 3.3 (Ramanarayanan's visual-equivalence
   argument: at this figure's on-screen scale, a cheap proxy is very unlikely to be
   perceptibly different from a ray-traced pass). Ranked below the shadow/material items
   because item 06 already scoped this as the plan; nothing new to decide.
8. **Checking the plate for real optical defocus before adding synthetic DoF blur to the CG
   puppet.** *Cost: free — a look, not a build.* Evidence: section 5.1 (the phone's DoF at
   0.4-0.6 m is deeper than intuition suggests, tens of mm to 20+ cm) — a "big build" (a full
   synthetic defocus pipeline) is very likely *not* needed for this shot, which is itself a
   time-saving finding worth checking before spending effort on it.
9. **A full learned single-image illumination estimator (Gardner/DeepLight/Hold-Geoffroy) in
   place of the existing single-key-plus-ambient model.** *Cost: big build — training data,
   inference pipeline, integration.* Evidence: section 2 — these methods' own reported errors
   (Gardner: chosen over ground truth only 41.85% of the time; DeepLight: ~10-degree angular
   error) show they do not clearly beat a scene-specific measurement from this frame's own
   visible hand-shadow. **Not recommended for this shot** — the one item on this list actively
   ranked *last* because the evidence argues against building it, not merely that it is
   expensive.
10. **A full mesh-based, PBR-lit, ray-traced-AO renderer swap (Blender/EEVEE, moderngl PBR) as
    a wholesale replacement for the NumPy deferred pipeline.** *Cost: big build — a second
    renderer/DCC dependency, per item 06 section 7's own comparison table.* Evidence: nothing
    in this pass changes item 06's own conclusion that the current MuJoCo-depth-plus-custom-
    shading pipeline is the right fit for a small, few-primitive figure with a stylized (not
    physically-accurate) target look; a full renderer swap would buy PBR correctness this
    project's uncanny-valley evidence (item 1) argues is not what is actually needed.

**Cheap tests vs. big builds, restated:** items 1, 3, 4, 8 cost nothing more than a look and a
parameter change and should happen first. Items 2, 5, 7 are moderate, mostly-already-specified
builds. Item 6 is a real but scoped shader change, worth doing only if the material direction
changes. Items 9 and 10 are the big builds this evidence argues are not the highest-leverage
next step for this particular 15 cm figure in this particular shot.
