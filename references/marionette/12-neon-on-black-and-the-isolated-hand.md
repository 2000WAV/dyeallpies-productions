# Item 12 — neon on black: the emissive figure on a black plate, the isolated hand, and the light between them

Context: the marionette (11 rigid MuJoCo bodies, rendered depth+ID -> deferred shader, per
item 6) moves from a solid-red figure on the off-white wall (item 9) to a NEON, emissive,
"crystal/lighting"-style figure composited onto a PITCH-BLACK plate, with the real hand
isolated from the wall and placed on that same black. Dennis has since specified: several
neon hues across the figure's body parts, GREEN excluded, and VIOLET ("electromagnetic
violet", ~400-420 nm) as the dominant hue. This item builds directly on item 6 (bloom
filter shapes/numbers, fresnel/matcap shading, MuJoCo renderer limits — NOT repeated here)
and reads item 9 (colour salience on a LIGHT ground) and item 11 (light wrap, realism cues,
day-for-night is new to this item) as background without redoing their numbers.

All numbers are attributed to a file in `papers/`, `abstracts/`, or `data/12-neon-black-
numbers.csv`; **NOT FOUND** marks a number the brief asked for that could not be sourced
this pass. See `downloads-12.md` for every URL/licence fetched this session.

## 1. The neon look on a dark ground

**The physically-based bloom argument, restated for black.** Item 6 already established
the modern "no hard threshold" bloom pipeline (Jimenez 2014's blend weight ~0.04, the
physically-based mip-chain, Section 2 of that item) — none of that changes on a black
plate. What DOES change is item 9's finding about bloom on a LIGHT wall: there, bloom
scattering onto the wall raised the background luminance and collapsed Weber contrast
(item 9 Section 2, the "veiling luminance" mechanism, `abstracts/schorsch-glare-veiling-
luminance.txt`). On a plate whose background luminance is already ~0, that mechanism runs
in reverse: any light the bloom scatters onto the surrounding black can ONLY increase local
contrast (from 0 up), never collapse it. This is precisely why "rim light for separation"
and bloom read as natural and "neon" specifically on dark backgrounds — the standard advice
item 9 found itself fighting against on a light wall is the correct advice here.

**The point-spread-function behind a believable glow.** Spencer, Shirley, Zimmerman &
Greenberg 1995, "Physically-Based Glare Effects for Digital Images"
(`papers/spencer1995-physically-based-glare.pdf/.txt`, fetched via a Wayback Machine
mirror after Cornell's own pubs URL 301-redirected away — see `downloads-12.md`) is the
direct source for how a real bright source's halo actually falls off in the human eye, and
therefore what a rendered glow should mimic to read as "real light" rather than "a blurred
sprite":

- Vos's ocular point-spread function has three terms: a narrow **central Gaussian** (the
  unscattered image of the source), a term proportional to **1/theta^3** that **dominates
  for visual angle theta < 1-2 degrees**, and a term proportional to **1/theta^2** that
  dominates beyond about 1 degree. There is **no single "core:halo ratio" number** given
  anywhere in the source — glare is a continuous multi-term falloff, not a two-zone split
  (flagged **NOT FOUND** for a citable ratio; item 6's "core + halo" construction should be
  understood as an artistic two-band APPROXIMATION of this continuous curve, which is fine,
  but should not be dialled to a single fixed ratio and left alone).
- **Simpson's finding**: a glare source subtending **more than 20 arcminutes** of visual
  angle does not produce significant ciliary-corona flare lines — the fine radial rays blur
  together into bloom once the source is that large. The marionette's individual glowing
  limbs, at typical delivery framing, are almost certainly well above 20 arcmin, so the
  relevant regime is bloom/veiling glare, not corona flare lines — consistent with item 6's
  plan (Section 2 of that item; no separate corona-flare-line pass is needed).
- **The veiling-luminance relation**: `Lv(theta) = k * f(theta) * E_eye`, where `Lv` is the
  equivalent veiling luminance added to nearby objects (cd/m^2), `E_eye` is illuminance at
  the eye from the glare source (lux), `theta` is the angle from the source (degrees), and
  `k`/`f` are empirically fit, not universal constants. This is the textbook basis for
  "the object's own glow lights its surroundings" — see Section 4 below for applying it to
  the hand.
- **Perceived vs. physical scatter**: normal viewers PERCEIVE only ~10% of light as
  scattered, but physical measurement shows ~40% actually is — explained by the
  Crawford-Stiles effect (directional cone sensitivity). **Age dependence**: total scattered
  fraction rises from **0.36 at age 20 to 0.45 at age 60** (roughly doubling again by 70).
  Not directly actionable for this render (there is no "viewer age" parameter to tune), but
  useful calibration: even a "clean" 20-year-old eye scatters over a third of the light from
  a bright source — a render with NO veiling glare at all around its brightest points will
  under-sell the glow relative to real vision.
- **Converting the halo geometry to this project's pixels**: item 9 already computed **1
  arcminute is approximately 1.26 px** at 1080x1920 delivery and a 30 cm phone-viewing
  distance (`data/09-colour-numbers.csv`). That makes **1 degree of visual angle roughly
  75.6 px** at the same viewing geometry. Combined with Spencer's 1-2 degree PSF dominance
  crossover: most of the perceptually-important glow energy (the 1/theta^3 term) should sit
  within roughly a **~75 px radius** of each emissive core at delivery resolution, with a
  much lower-amplitude 1/theta^2 tail extending well beyond that — a concrete target for
  tuning the bloom mip-chain's outer radius (item 6 Section 2.4's `filter radius`
  parameter), rather than eyeballing it with no anchor at all.

**Saturation clipping and the "shoulder" toward white.** This is the same mechanism item 6
already used for the string cores (item 6 Section 5: "core whiter than the halo... exactly
where full saturation is lost to white first") and for the fresnel rim (item 6 Section 3):
the brightest, most concentrated part of any HDR-bloomed light source clips hardest, so its
hue desaturates toward white before dimmer surrounding pixels do. On a black plate this
reads as a genuine "hot core, coloured halo" tube look (real neon signage photography shows
exactly this: a near-white or pastel core line with a saturated coloured glow around it,
not a flat single-colour tube) — no new number beyond item 6's existing fresnel/bloom
recipe is needed; the halo's colour desaturation toward white IS the bloom pass's natural
behaviour once any tone-mapping/clipping is applied, not a separate effect to author.

**Reference looks, briefly (per the brief's own "short, with sources" instruction for this
sub-point).** Tron: Legacy's practical-suit breakdown is already fully covered in item 6
Section 2.6 (`papers/fxguide-tron-legacy-faceoff.html/.txt`) and is not repeated here beyond
its headline point: even genuinely light-emitting practical sources needed glow-falloff and
colour-consistency work added in post, and a director-requested flicker — both directly
relevant to a violet figure that should look "alive," not static (see Ritschel 2009 below).
Neon signage photography and "cyberpunk" grading were searched for a citable technical
breakdown with numbers (rather than mood-board pages); none were found beyond what the
gas-colour and glare sources below already establish — flagged **NOT FOUND** for a
dedicated cyberpunk-grading technical source, not pursued further given item 6 and this
item's own colour-science sources cover the same ground with better numbers.

**Temporal glare — the "it's actually glowing" cue.** Ritschel, Ihrke, Frisvad, Coppens,
Myszkowski & Seidel 2009, "Temporal Glare" (Computer Graphics Forum 28(2), 183-192;
abstract-only in this archive — `papers/ritschel2009-orbit-dtu.html`, the DTU institutional
record; the author's own project-page PDF link and ResearchGate/Semantic Scholar mirrors
all returned 403/404 to curl, see `downloads-12.md`) argues, with a validated psychophysical
study, that ocular glare's TEMPORAL fluctuation (not just its static shape) is itself a
perceptual cue: dynamic glare renderings were judged as more attractive and increased
perceived brightness versus an identical static glare pattern. No numeric halo-size or
flicker-rate figure is available from the abstract alone, but the qualitative
recommendation is directly actionable and cheap: **give the bloom/glow a very subtle
temporal variation (a slow, low-amplitude flicker or breathing)** rather than a perfectly
static glow — consistent with Tron: Legacy's own director-requested flicker (item 6 Section
2.6) and free to combine with the render's existing per-frame bloom pass.

## 2. Colour on black

### 2.1 Which hues read strongest as emissive on black (general)

**The Helmholtz-Kohlrausch (H-K) effect.** Wikipedia, "Helmholtz-Kohlrausch effect"
(`papers/wikipedia-helmholtz-kohlrausch.html`, CC BY-SA 4.0): saturated colour is perceived
as BRIGHTER than an achromatic patch of the same measured luminance, growing with
saturation and strongest for spectral/near-monochromatic colours, and working BEST in dark
viewing environments — the article names darkened theatres specifically. This is the
single most load-bearing perceptual fact for this whole item: on a black plate, the H-K
effect is running at its strongest, which is exactly why a saturated neon figure on black
reads as "glowing" even before any bloom is added.

The article states plainly which hues show the effect **least**: "green and yellow" — which
independently corroborates Dennis's own decision to exclude green (a hue that would look
comparatively DULL/flat for a given luminance budget, on top of any other reasons for
excluding it). By elimination/implication, red, blue/violet and magenta-leaning hues show
the STRONGER effect; stage-lighting practice (cited in the article's own "Entertainment"
section) explicitly favours reds, pinks and blues for exactly this reason. One concrete
numeric example is given (aviation section): a white-reference incandescent runway lamp
needs **roughly TWICE the luminance** of a red LED lamp to be perceived as equally bright —
the only citable H-K magnitude found this pass. A closed-form H-K model exists in the
literature (Nayatani 1997; Fairchild & Pirrotta 1991) but both are paywalled and were
**NOT FOUND** as fetchable full texts this session (see `abstracts/12-helmholtz-kohlrausch-
effect.txt`).

**Bloom of one hue against black desaturates toward white at the core.** Already covered
mechanically in Section 1 above (the same clipping/shoulder logic as item 6's string
cores/fresnel rim) — restated here because it interacts directly with hue choice: a
strongly-bloomed violet or blue core will show a WHITE or pale-lavender hot centre with the
saturated hue only fully visible in the surrounding halo, not at the brightest point. This
is real neon-tube behaviour (photographed neon signage consistently shows this), not a
render artifact to fight.

### 2.2 Violet as the dominant hue: sRGB approximation, luminance, and the halo

**Spectral violet cannot be displayed; three named approximations exist.** Wikipedia,
"Violet (color)" and "Shades of violet" (`papers/wikipedia-violet-color.html`,
`papers/wikipedia-shades-of-violet.html`, both CC BY-SA 4.0) state directly that violet
light (~380-435 nm per the Violet (color) infobox) lies outside the sRGB gamut — a display
cannot emit true spectral violet, only fake it by mixing blue at high intensity with red at
lower intensity. "Shades of violet" uses a narrower 380-420 nm band for "violet proper"
(treating 420-450 nm as a separate "indigo" band) and gives three named sRGB stand-ins, all
HSV S=100%/V=100%, increasing in "redness":

| name | hex | sRGB | approximates | note |
|---|---|---|---|---|
| colour-wheel violet | `#8000FF` | (128,0,255) | ~417 nm | Wikipedia's own infobox colour, sourced to the W3C CSS Color Module Level 3 keyword list; sits at the violet/indigo boundary |
| **electric violet** | **`#8F00FF`** | **(143,0,255)** | **~400 nm** | called "the closest approximation to middle spectrum violet that can be made on a computer screen, given the limitations of the sRGB colour gamut"; this is the ~400-420 nm "electromagnetic violet" match the brief asks for |
| vivid/extreme violet | `#9F00FF` | (159,0,255) | ~380 nm | approximates the extreme short-wavelength edge |

The "electric violet" hex itself traces to a third-party "HTML Color Chart" page that
Wikipedia's own editors have flagged **"failed verification"** — treat `#8F00FF` as a
widely-used, reasonable CONVENTION for "the violet you get on a screen," not a
standards-body-certified number. **Two traps to avoid**: the X11/CSS colour literally named
`"violet"` (`#EE82EE`) is actually a pale tint of MAGENTA (equal red/blue plus some green),
not a violet approximation at all; and `"darkviolet"` (`#9400D3`) is the desaturated
"artist's pigment" analogue, not the electric/emissive look wanted here.

**Violet's low luminance for its saturation — why the H-K effect matters most here.**
Computed this session using the same sRGB-EOTF + BT.709 luminance-weight formulas item 9
already archived (`abstracts/wikipedia-cielab-srgb-formulas.txt`), cross-checked against
item 9's own saved red/blue/magenta values (exact match — see `data/12-neon-black-
numbers.csv`):

| colour | hex | relative luminance Y | CIE L* |
|---|---|---|---|
| electric violet | `#8F00FF` | 0.131 | **42.9** |
| colour-wheel violet | `#8000FF` | 0.118 | 40.9 |
| vivid/extreme violet | `#9F00FF` | 0.146 | 45.1 |
| dark/pigment violet | `#9400D3` | 0.110 | 39.6 |
| pure red (item 9) | `#FF0000` | 0.213 | 53.2 |
| pure blue (item 9) | `#0000FF` | 0.072 | 32.3 |
| magenta (item 9) | `#FF00FF` | 0.285 | 60.3 |
| cyan | `#00FFFF` | 0.787 | 91.1 |
| amber/orange | `#FFA500` | 0.482 | 74.9 |

Electric violet's L* (42.9) sits **~10 units below pure red's (53.2)** despite matching HSV
saturation and value exactly — violet is the second-darkest of every fully-saturated hue
checked (only pure blue is darker). Wikipedia's "Violet (color)" article gives the
mechanism directly: violet appears dark because the **S-cones contribute very little to the
luminance (lightness) channel** at all, even though they respond strongly to violet
wavelengths (this is also why violet reads slightly reddish compared to spectral blue —
the S-cone leaks a little "red" into the red-green opponent channel). **This is exactly why
the Helmholtz-Kohlrausch effect matters most for violet of all the candidate hues**: violet
is colorimetrically the darkest fully-saturated colour available (after blue), yet the H-K
literature places blue/red/violet-leaning hues among the STRONGEST beneficiaries of the
brightness-from-saturation boost — meaning a violet figure needs that perceptual boost
just to read as "as bright as it looks saturated," and will look flat/muddy rather than
glowing if the render's saturation is allowed to drift down even slightly (a small drop in
saturation costs violet proportionally more perceived brightness than it would cost red).
Practical implication: **keep the violet body panels at or very near maximum sRGB
saturation** (do not desaturate them "for realism" the way a matte material might elsewhere
in the render) and rely on the fresnel rim / internal gradient (item 6 Section 1) rather
than desaturation to add shading variation.

**The halo desaturates toward white — for violet specifically, watch the white point.**
Per Section 1's general clipping mechanism, a bloomed violet core will wash toward white
fastest along whichever channel clips first — since sRGB `#8F00FF` already has its blue
and red channels both high (0/143/255), the bloom's white "shoulder" will pass through a
warm lavender/pink-white on the way to pure white, NOT a cool blue-white the way a pure-blue
bloom would. This is a good thing for a dominant-violet figure: the halo's transitional hue
(lavender-white) still reads as part of the violet "family" rather than jumping to a
different colour identity as brightness increases, which helps the whole figure read as one
consistent light source even where several body parts differ in base hue (Section 2.3).

### 2.3 Secondary hues that pair with a dominant violet, green excluded

Using the real neon-gas colours as the reference set, per the brief (Wikipedia, "Neon
lighting" and "Argon", `papers/wikipedia-neon-lighting.html`, `papers/wikipedia-argon.html`,
both CC BY-SA 4.0):

| gas / mechanism | real colour | sRGB-family pairing with violet |
|---|---|---|
| **pure argon** | **lilac/violet** ("Gas-discharge lamps filled with pure argon provide lilac/violet light"; the Argon infobox image is captioned "a violet glow") | this IS the dominant hue — the real-world anchor for "electromagnetic violet" as an actual neon-tube colour, not just a screen convention |
| argon + mercury, or mercury vapour alone | **blue** | strongest, most natural secondary — same family as violet (both short-wavelength/cool), corroborated by two independent Wikipedia pages |
| neon (the element) | **orange-red** (the "popular orange" glow the whole technology is named for) | the classic warm complement to violet; use sparingly as an accent (e.g. a joint highlight or a single limb) since it is the hue family FARTHEST from violet on the wheel and will read as the most visually "loud" contrast |
| hydrogen | **purple-red** | a rose/magenta-leaning red that sits naturally BETWEEN violet and orange-red — a good intermediate accent that won't fight the violet the way a pure warm orange-red might |
| helium | yellow **or pink** | use the **pink** variant only — yellow is excluded by the same green/yellow-weak-H-K logic that excludes green (Section 2.1); pink pairs cleanly with violet as a lighter, less saturated relative |
| phosphor-coated tubes (argon/mercury-vapour + UV-excited phosphor) | ~100 additional colours since the 1950s, including **magenta and cyan** | these are NOT raw single-gas glows — they are the phosphor-conversion mechanism that also produced fluorescent lighting; magenta and cyan are legitimate "classic neon sign" colours by this route, and both sit adjacent to violet on the wheel (magenta = violet+red, cyan = violet's near-complement through blue) |

**Recommended palette for the multi-hue figure**: dominant **violet** (`#8F00FF` family,
kept near-maximum saturation per Section 2.2) for the torso/core mass; **blue**
(argon+mercury/mercury-vapour family) as the primary secondary for adjoining limbs — same
cool family, lowest risk of looking like a different light source; **magenta** as a second
secondary (phosphor-tube-legitimate, sits between violet and red, will not clip toward a
different white-point than violet does); **orange/amber or a hydrogen-style purple-red** as
a single warm accent (a hand, a head, or the string-attachment glow) for contrast, used
sparingly since it is the most "different" hue in the set; **cyan** only in small/thin
elements (string cores, small joint highlights) given its very high L* (91.1) — a cyan body
PANEL would be the single lightest, least "jewel-like" element on the figure and risks
looking washed out rather than glowing. **Green is excluded** per the brief and independently
supported by the H-K literature's own "green and yellow show the weakest effect" finding
(Section 2.1) — a green panel would need MORE luminance than every other hue on the figure
to look equally bright, working against the whole point of an emissive-on-black look.

## 3. Isolating the hand and putting it on black

### 3.1 The decontamination relation (already archived, reused unchanged)

Smith & Blinn 1996, "Blue Screen Matting" (`papers/smithblinn1996-blue-screen-matting.pdf`,
already archived under item 5) gives the standard unpremultiply-against-a-known-backing-
colour relation:

```
F = (C - (1-a)*B) / a
```

where `F` is the true (decontaminated) foreground colour, `C` is the composited/contaminated
pixel as it exists in the source plate, `a` is the alpha/coverage value, and `B` is the
KNOWN backing colour. This project's plate has exactly the condition this formula assumes:
a uniform, known backing colour (`#F2F0EA`, item 9) rather than an arbitrary or
spatially-varying background — so the decontamination step is well-posed and should recover
a clean, backing-colour-free hand before any recomposite onto black.

**Why this matters specifically for a move TO BLACK.** Item 11 Section 5.2 already notes
that a soft edge/light-wrap direction reverses when moving from a bright wall to a dark
background — the same logic applies here at the matte level: any residual wall colour
(`#F2F0EA`, a warm off-white) left in the hand's edge pixels by an imperfect matte will show
up as a visible WARM HALO/FRINGE against pure black, where it would have been nearly
invisible blended into the wall itself. This is the single most likely "the matte looks
wrong" failure once the background changes (see Section 6's ranked risk list) — the fix is
exactly the Smith & Blinn unpremultiply above, run with the actual measured backing colour,
not skipped because "it looked fine on the wall."

### 3.2 Edge treatment: core+edge mattes, and removing the light-wrap-in-reverse halo

The guided-filter edge band already in this project's pipeline
(`papers/he2013-guided-image-filter-pami.pdf`, `papers/he2010-guided-image-filter.pdf`,
`papers/he2015-fast-guided-filter.pdf`, all already archived under item 5) is the right tool
for exactly this: a **"core + edge"** matte splits the alpha into a solid, high-confidence
interior region (hard-edged, unambiguous hand pixels) and a narrow band at the true
silhouette where alpha and colour both need care. Levin, Lischinski & Weiss 2008,
"Closed-Form Solution to Natural Image Matting" (`papers/levin2008-closed-form-matting.pdf`,
already archived under item 5) is the standard reference for solving that edge band's alpha
from local colour statistics rather than a fixed threshold — already available in this
project's archive, cited here rather than re-summarised.

**The halo a soft matte leaves on black, and how compositors remove it.** Because rembg's
matte was pulled against the off-white wall, its soft edge necessarily contains a
BLEND of hand colour and wall colour at every partially-transparent pixel — exactly what the
Smith & Blinn formula (Section 3.1) exists to remove. If any wall contamination survives
into the final composite, the standard compositing fix (per Wright/Brinkmann's despill and
edge-treatment chapters — bibliographic reference only, no legally obtainable full text was
found by items 5/11 either, so this is unchanged **NOT FOUND** status, carried forward
rather than re-attempted) is a combination of: **edge erosion** (shrink the alpha matte by a
pixel or two before recompositing, sacrificing a sliver of true hand edge to guarantee no
contaminated pixels survive), and a **light wrap in reverse** — item 11 Section 5.2 already
identifies that on this new black background, a light wrap should pull a thin sliver of
whatever IS behind the hand (here: the emissive figure's own bloom colour, where it passes
close to the hand, or otherwise near-black) onto the hand's edge, not the old wall-ambient
wrap direction used on the light-wall version.

### 3.3 Matte quality at motion-blurred fingers, and rembg's soft alpha

The brief specifies the matte was cut from a plate with **1/60 s** shutter (item 05's stated
shutter speed), i.e. real motion blur on fast-moving fingers is physically present in the
source photography. Yao et al. 2023, ViTMatte (`papers/yao2023-vitmatte.pdf`, already
archived under item 5, CC BY 4.0/arXiv) and the guided-filter papers above are both built
around exactly this case: a soft, gradual alpha transition at a blurred edge is the CORRECT
matte, not an error to sharpen away. **Recommendation: keep rembg's soft alpha as-is at
motion-blurred edges (fast finger frames) and only harden/erode the matte at edges that are
NOT motion-blurred** (a still or slow-moving frame where a soft edge would look like a
mistake rather than real blur) — a single global "harden the matte" pass would make blurred
frames look wrong by removing real blur, and a single global "keep it maximally soft" pass
would leave still frames looking mushy/ill-defined. This distinction is this project's own
synthesis from the two facts above (soft mattes are correct for real blur; soft mattes read
as errors when the underlying edge is sharp), not a single source's explicit recommendation.

## 4. The lighting of a hand in a dark room next to an emissive object

### 4.1 How much light a small emissive figure actually throws on nearby skin

The inverse-square law is the whole mechanism: illuminance falls as **1/d^2** from a source
small relative to the working distance (scantips.com, `papers/scantips-inverse-square-law.html`;
PetaPixel, `papers/petapixel-black-backgrounds-macro.html`, which restates it in
photographic terms — "each time you double the distance your light travels, the power is
reduced by two stops, or 75%"). **No citable manufacturer or measured luminance figure for
this project's own rendered emissive surface exists** (flagged **NOT FOUND** — this is a
render/grade choice, not a physical measurement), so the useful number here is the
GEOMETRIC ratio, not an absolute one:

- Figure-to-fingertip distance (brief): **~6.5 cm** (midpoint of the stated 5-8 cm range).
- An illustrative across-the-room window distance: **~1.5 m** (an assumption for scale only
  — item 05's archive has no measured window distance for this plate, only a solved light
  DIRECTION from the hand's own cast shadow, item 05 Section 2 / item 11 Section 2.2).
- Geometric illuminance ratio if figure and window had EQUAL luminous intensity toward the
  hand: `(1.5 / 0.065)^2 ≈ 530`, i.e. **~9.1 stops** of pure proximity advantage for the
  figure. In plain terms: the figure does not need to be anywhere near as luminous as the
  window in absolute terms to show a visible interactive glow on skin a few centimetres
  away — it only needs a small fraction of the window's effective output, because it is
  roughly 23x closer.
- Illustrative worked target (Wikipedia, "Lux", `papers/wikipedia-lux.html` — "family living
  room lighting" is given as **50 lux**, a clearly-visible-but-not-overpowering indoor
  light level): to deliver 50 lux at 6.5 cm, the figure needs a luminous intensity toward
  the hand of only `I = E * d^2 = 50 * 0.065^2 ≈ 0.21 candela` — a genuinely small light
  source's worth of output. This is a back-of-envelope illustration of the CALCULATION
  SHAPE, not a specified brightness for the render (which stays a grading/tuning choice).

### 4.2 Compositing practice: "the CG object lights the real actor"

Item 6 Section 2.6 already covers the Tron: Legacy practical-suit account in full
(`papers/fxguide-tron-legacy-faceoff.html/.txt`): the suits WERE genuinely light-emitting on
set and did light the actors for real, but even so almost every shot needed glow-falloff and
colour-consistency correction in post — i.e. even a real practical light source needs the
same compositing discipline (light wrap, spill, edge treatment) as a purely synthetic one
composited afterward. Item 11 Section 5.2 already covers light wrap as the cheap version of
"the CG object lights the real actor" for THIS project (citing Wright/Brinkmann
bibliographically only, full text **NOT FOUND** by either item 05, item 11, or this pass —
status unchanged, not re-attempted): a thin, colour-matched sliver of the figure's own bloom
hue wrapped onto the nearest real edges of the hand, strongest where the hand is closest to
the figure and falling off with the same geometry as Section 4.1's inverse-square argument.

### 4.3 Relighting a real object from a single image — why the cheap version is right here

Two sources establish what the "real," fully physically-grounded version of this problem
costs, specifically so this item can justify NOT building it:

- Nestmeyer, Lalonde, Matthews & Lehrmann 2020, "Learning Physics-guided Face Relighting
  under Directional Light" (`papers/nestmeyer2020-face-relighting-arxiv.pdf/.txt`, CVPR
  2020/arXiv, CC BY-style arXiv preprint) de-lights and re-lights a face via an end-to-end
  network trained on **21 subjects captured in a light-stage rig with 32 individual light
  sources** — real single-image relighting of a real subject is a rig-and-data-hungry deep
  learning problem, not a lightweight per-frame filter.
- Einabadi, Guillemaut & Hilton 2021, "Deep Neural Models for Illumination Estimation and
  Relighting: A Survey" (Computer Graphics Forum 40, 315-331; abstract fetched via the
  Semantic Scholar API, `papers/einabadi2021-illumination-relighting-survey-abstract.json`
  — the paper's own claimed hybrid-open-access PDF returned an HTML interstitial to a
  scripted fetch and was not saved) surveys this entire field in three categories
  (illumination estimation / reflectance-aware relighting / image-to-image relighting),
  cited once per the brief's instruction, confirming this is an active, non-trivial research
  area rather than a solved, pluggable step.

**Conclusion for this shot**: do not build a learned relighting model for the hand (same
verdict item 11 Section 2/7 already reached for the whole plate's illumination — the
learned methods' own reported error bars there were larger than what a direct geometric
measurement gives). Use the cheap per-pixel light-wrap shortcut (Section 4.2) instead,
scaled by the inverse-square geometry (Section 4.1) and the figure's own bloom colour
(Section 2), which is consistent with, not a downgrade from, this project's existing
practice.

### 4.4 The hand's own exposure in a dark room: day-for-night, without inventing numbers

Wikipedia, "Day for night" (`papers/wikipedia-day-for-night.html`, CC BY-SA 4.0, citing Van
Hurkman 2013 and Malkiewicz & Mullen 2009): the classic film-era recipe is to **underexpose
by about two f-stops**, often via a neutral-density filter so the aperture itself need not
change, combined with a **3200K-vs-5000K** tungsten/daylight white-balance shift so that
practical lights render white while ambient/unlit areas render "moonlight blue," plus
increased contrast and a deliberate slight under-lighting of shadow areas to match the
higher-contrast look associated with night vision. The modern digital exception, named
explicitly on the same page: **Mad Max: Fury Road (2015)** shot these scenes deliberately
OVER-exposed on set (exploiting sensor dynamic range), then pulled the exposure back down
and graded blue in post — avoiding the shadow clipping that classic in-camera underexposure
risks.

**This shot's own situation is different from either case**, and the difference matters:
this is a SINGLE existing 9-second plate, already captured at a fixed exposure — there is no
"underexpose on set" option left to take, only a post-production grading choice. The
applicable piece of the day-for-night practice is therefore the GRADING half only: **pull
the hand's exposure down somewhat and add contrast/a cool-leaning shift when the background
goes from a lit off-white wall to pitch black**, consistent with the eye's own expectation
that a dark room means a darker, more contrasty subject — but the exact number of stops to
pull is a grading judgement call for this specific plate's existing exposure latitude, not a
value this item will invent. **NOT FOUND**: an ASC or ARRI technical-standard document
giving a specific stops/Kelvin recommendation for grading (as opposed to shooting) day-for-
night from an already-captured plate — the sourced numbers above are all for the SHOOTING
side of the technique; applying them in the grade is this item's own reasoned extrapolation,
flagged as such rather than presented as a sourced number.

## 5. Reference looks for "a real hand holding a glowing thing on black"

Short, per the brief:

- **Product/macro photography's black-background practice.** PetaPixel's black-background
  macro guide (`papers/petapixel-black-backgrounds-macro.html`) and the general product-
  photography convention it describes (a subject lit close and bright, a background far
  enough or unlit enough that the same flash/key falls off to nothing by the time it would
  reach it) is exactly this shot's own physics: item 4.1's inverse-square argument is the
  reason a close, modest emissive figure and a pitch-black room can coexist believably in
  one frame, the same way a product shot gets a black background "for free" from distance
  rather than from a painted backdrop.
- **Held-object product photography rim-lighting convention**: lighting a small held object
  from behind/the side so a thin rim defines its silhouette against black — directly
  analogous to keeping the figure's own fresnel rim (item 6 Section 3) doing double duty as
  both "reads as 3-D" (item 6's original purpose) and "reads as separated from the now-black
  background" (this item's purpose) with no new technique required, just confirmation the
  same rim serves both jobs once the background changes.
- **Tron: Legacy and the puppet/glowing-marionette reel precedent**: already fully covered
  in item 6 Section 2.6 (Tron) and item 11 Section 6 (Team America, Thunderbirds, Trnka,
  Dark Crystal, Pinocchio, Kubo, and the "why renders look fake" checklist) — a dedicated
  search this pass for OTHER glowing-marionette reels specifically (as opposed to this
  project's own prior puppet-video work) surfaced no additional citable technical source
  beyond what those two items already archived; **NOT FOUND** for anything to add here.

## 6. A ranked recipe for THIS shot

15 cm figure, 5-8 cm below the fingertips, hand lit from a window at the left (item 05),
handheld, 30 fps, 1/60 s shutter, moving to a pitch-black plate.

**Composite order** (each stage citing the section above it draws from):

1. **Black plate** as the base layer (a genuine, near-zero-luminance background; item 9's
   veiling-luminance mechanism, Section 1 above, means bloom scattered onto this layer can
   only ADD visible contrast, never collapse it — the opposite risk from the old light wall).
2. **Decontaminated hand** (Section 3.1's `F = (C-(1-a)B)/a` unpremultiply against the
   measured `#F2F0EA` backing colour, run BEFORE recompositing onto black, not after) with
   its edge treated per Section 3.2 (core+edge split, erosion only where the source edge is
   genuinely sharp, soft alpha preserved at real motion-blurred finger edges per Section 3.3)
   and its own exposure pulled down slightly per Section 4.4's grading-only interpretation of
   day-for-night practice.
3. **The emissive figure**, composited BEHIND the hand where it passes behind fingers
   (unchanged from the prior red-on-wall geometry — only the shading/hue/background change
   in this item, not the depth ordering).
4. **Bloom** on the figure only (item 6 Sections 2-9 for the filter shapes/numbers; this
   item's Section 1 for the ~75 px/1-2-degree halo-radius target and the optional subtle
   temporal flicker per Ritschel 2009).
5. **Spill/light-wrap onto the hand** (Section 4.2), coloured and intensity-scaled per the
   figure's own dominant hue and the inverse-square falloff from Section 4.1, strongest
   where the hand is nearest the figure (the fingertips, the palm-side edge as it passes the
   torso/limbs).
6. **Grain** matched to the plate's own noise characteristics (item 05 Section 4.2-4.3,
   unchanged by this item — the sensor noise model does not depend on the background colour).

**Parameters to expose** (for iteration, per the render-iteration-cache lesson): the
per-body-part hue assignment (violet dominant + the Section 2.3 secondary palette), each
hue's saturation floor (Section 2.2's "do not desaturate violet" rule applies most strongly
to the dominant hue, less so to secondaries), the bloom blend weight (item 6's existing
0.03-0.15 range, COD:AW's 0.04 as the default starting point, unchanged by moving to black),
the light-wrap intensity/colour-temperature on the hand (Section 4.2), and the hand's own
grade pull (Section 4.4, a judgement call not a fixed number).

**The three things most likely to look fake, and the fix for each**:

1. **A warm halo/fringe around the hand from residual wall colour in the matte edge.** This
   is the single highest-risk item precisely BECAUSE the matte was built for a light wall
   and is now seen against black, where any surviving `#F2F0EA` contamination becomes
   visible instead of blending in (Section 3.1). **Fix**: always run the Smith & Blinn
   decontamination against the actual measured backing colour before compositing onto
   black, never composite the raw rembg alpha directly; verify by eye at 100% on a still
   frame with the hand held over pure black in a viewer, specifically looking for a warm
   fringe.
2. **The hand looking pasted-on because it is still lit like the bright room it was shot
   in, next to a plate that is now supposed to read as dark.** The real photography's
   exposure and colour temperature do not automatically change just because the background
   pixels were replaced with black. **Fix**: the Section 4.4 grading pull (a modest exposure
   reduction and contrast increase on the hand layer only, informed by but not slavishly
   copying the classic ~2-stop day-for-night convention) plus the Section 4.2 light-wrap,
   which together sell "this hand is actually in a dark room lit mainly by the object it's
   holding" rather than "a bright-room hand pasted over a black rectangle."
3. **The bloom clipping fully to white and losing the violet identity.** Because violet is
   the DARKEST fully-saturated hue checked (Section 2.2) and the H-K effect is doing more
   of the perceptual "brightness" work for it than for a hue like red or orange, an
   over-aggressive bloom or tone-map can push the core (and even a wide halo) to flat white
   faster than expected, leaving a figure that reads as "a white glowing blob" rather than
   "a violet neon figure." **Fix**: keep the bloom blend weight in item 6's existing
   0.03-0.15 range rather than pushing it higher "to make it glow more," rely on the
   fresnel rim and internal gradient (item 6 Section 1) for the 3-D read instead of raw
   brightness, and specifically eyeball a still frame of the torso (the dominant-violet
   mass) to confirm its CENTRE still reads as violet-white, not pure white, before
   finalising the grade.

## Files written by this research pass

- `references/marionette/12-neon-on-black-and-the-isolated-hand.md` (this file)
- `references/marionette/abstracts/12-spencer1995-physically-based-glare.txt`
- `references/marionette/abstracts/12-ritschel2009-temporal-glare.txt`
- `references/marionette/abstracts/12-helmholtz-kohlrausch-effect.txt`
- `references/marionette/abstracts/12-electric-violet-srgb-approximation.txt`
- `references/marionette/abstracts/12-neon-gas-colours.txt`
- `references/marionette/abstracts/12-day-for-night.txt`
- `references/marionette/abstracts/12-nestmeyer2020-face-relighting.txt`
- `references/marionette/abstracts/12-einabadi2021-relighting-survey.txt`
- `references/marionette/abstracts/12-lux-illuminance-examples.txt`
- `references/marionette/abstracts/12-inverse-square-law-photography.txt`
- `references/marionette/data/12-neon-black-numbers.csv`
- `references/marionette/downloads-12.md`
- `references/marionette/papers/spencer1995-physically-based-glare.pdf/.txt`
- `references/marionette/papers/ritschel2009-orbit-dtu.html`
- `references/marionette/papers/wikipedia-helmholtz-kohlrausch.html`
- `references/marionette/papers/wikipedia-violet-color.html`
- `references/marionette/papers/wikipedia-shades-of-violet.html`
- `references/marionette/papers/wikipedia-argon.html`
- `references/marionette/papers/wikipedia-neon-lighting.html`
- `references/marionette/papers/wikipedia-day-for-night.html`
- `references/marionette/papers/wikipedia-lux.html`
- `references/marionette/papers/nestmeyer2020-face-relighting-arxiv.pdf/.txt`
- `references/marionette/papers/einabadi2021-illumination-relighting-survey-abstract.json`
- `references/marionette/papers/petapixel-black-backgrounds-macro.html`
- `references/marionette/papers/scantips-inverse-square-law.html`
- `references/marionette/papers/ucsb-spectra-three-gases-8816.html` (background only)
- `references/marionette/papers/huevaluechroma-dimensions-of-colour-121.html`,
  `huevaluechroma-brightness-saturation-091.html` (background only, low yield — see
  `downloads-12.md`)
- `references/marionette/papers/adobe-light-falloff-vignetting.html`,
  `toolsforfilm-day-for-night.html` (fetched, not directly quoted — see `downloads-12.md`)

Also updated: `references/marionette/DOWNLOADS.md` (new "Item 12" heading appended).
No other file in the repo was modified.
