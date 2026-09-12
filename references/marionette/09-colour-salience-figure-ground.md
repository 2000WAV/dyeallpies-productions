# Item 9 — colour salience and figure-ground on a light background

Context: a 9-second Reel, a real tattooed hand from the back in front of a plain
off-white wall (sRGB #F2F0EA, linear luminance ~0.85, L* ~94), a 15 cm CG marionette
hanging on thin strings from the fingertips. Current render: neon cyan, white-hot rim,
bloom. Complaint: too bright, "loses focus" against the white wall. Wanted: (a) the
most attention-grabbing/"viral"/saturated colour, with research behind it, and (b) a
figure that reads opaque, sharp and solidly 3-D against a light wall, with research
behind that too.

All numbers below are attributed to a saved file in `abstracts/` or `papers/`, or
marked **NOT FOUND**. Full numeric detail (every luminance/L*/contrast value computed)
is in `data/09-colour-numbers.csv`, not retyped in full here.

## 1. What makes a colour attention-grabbing at all

**Salience is local contrast against the surround, not an absolute colour property.**
Itti, Koch & Niebur's 1998 saliency model (`abstracts/itti-koch-niebur1998-saliency-based-visual-attention.txt`,
full text `papers/itti1998-saliency-based-visual-attention.pdf`) computes visual
salience as centre-surround feature contrast (intensity, colour-opponent, orientation)
combined into one map; nothing in the model is salient in isolation, only relative to
what surrounds it. This directly grounds the brief's own framing: "a colour is salient
relative to its surround" — there is no context-free "most salient hue," only the hue
that maximises contrast against THIS wall.

Frey, Honey & König 2008 (`abstracts/frey-honey-konig2008-color-attention-categories.txt`,
abstract only, PMID 19146307) measured real eye movements and found colour features
(including colour/saturation contrast) pull fixations beyond what a pure luminance-
saliency model predicts, but by how much depends on the scene: in visually "busy",
already-colourful scenes, colour is not particularly salient; in low-clutter scenes, it
is. This project's wall is uniform and nearly achromatic — a strongly saturated colour
against it should punch well above what it would in a cluttered frame.

Nothdurft 2000 (`abstracts/nothdurft2000-salience-feature-contrast-additivity.txt`,
abstract only, PMID 10788635) quantifies how different salience channels combine:
colour-contrast and orientation-contrast salience overlap heavily (~90% gain reduction
when combined — they compete for the same resource), but **luminance-contrast salience
combines with the others largely independently (<30% overlap)**. Practically: a
saturated colour (colour-channel salience) AND strong luminance contrast (dark-on-light,
luminance-channel salience) are close to additive, not redundant — worth having both,
which is exactly what the recommendation below does.

**The "red advantage."** Elliot & Maier's 2014 Annual Review of Psychology review
(`abstracts/elliot-maier2014-color-psychology-review.txt`, abstract only, PMID
23808916, PDF paywalled — see `downloads-09.md`) is the standard citation for red's
outsized effect on human affect, arousal and attention across achievement and
attraction contexts; red is processed preferentially as a signal worth attending to.
**NOT FOUND**: a specific numeric effect size from the review's own abstract — that
level of detail lives in the primary studies it cites, not fetched separately in this
compact pass.

**Real-world engagement evidence (Instagram-adjacent).** Bakhshi et al. 2015, "Why We
Filter Our Photos" (`abstracts/bakhshi2015-why-we-filter-our-photos.txt`, full text
`papers/bakhshi2015-why-we-filter-our-photos.pdf`; 7.6M Flickr photos): filtered photos
were **21% more likely to be viewed** and **45% more likely to be commented on** than
unfiltered ones, and specifically "filters that increase **warmth, exposure and
contrast** boost engagement the most." This converges with the red-advantage literature
on WARM, high-contrast, saturated imagery — and the brief's own wall (#F2F0EA) is
itself warm-leaning (R=242 > G=240 > B=234), so a warm hue sits with, not against, the
wall's own cast while still contrasting it in luminance (see §3).
A dedicated academic YouTube-thumbnail-colour/CTR study was searched for; only
marketing-blog claims (e.g. "+23% CTR for red thumbnails") turned up, none tied to a
citable peer-reviewed source or a reproducible dataset — **NOT FOUND** as a source
worth saving; not used as evidence below.

## 2. Figure-ground: why chromatic contrast alone gives weak shape/edges

Livingstone & Hubel 1988, "Segregation of Form, Color, Movement, and Depth"
(`abstracts/livingstone-hubel1988-segregation-form-color-movement-depth.txt`, full text
`papers/livingstone-hubel1988-segregation-form-color-movement-depth.pdf`): the primate
visual system splits into a colour+fine-form (parvocellular) pathway and a
motion+depth+coarse-form (magnocellular) pathway that is essentially colour-blind but
carries most of the contrast sensitivity and 3-D/depth cues. Their own isoluminant
demonstration (yellow/grey shapes matched in luminance) looks FLAT until viewed through
a blue filter that reveals a real (previously colour-camouflaged) luminance difference —
at that point the same shapes spring into 3-D relief. **Chromatic contrast with no
luminance contrast reads as flat; luminance contrast is what carries solidity/depth.**
This is the direct research basis for the brief's "chromatic contrast alone gives weak
shape" claim.

Kleffner & Ramachandran 1992 (`abstracts/kleffner-ramachandran1992-perception-shape-from-shading.txt`,
full text `papers/kleffner-ramachandran1992-perception-shape-from-shading.pdf`, the
peer-reviewed full study following Ramachandran's 1988 Sci Am piece, which was not
locatable as an open PDF — **NOT FOUND**): shape-from-shading is a fast, pre-attentive,
"pop-out"-capable process, built on two assumptions the visual system applies
automatically — a SINGLE light source for the whole scene, and that it shines from
ABOVE (in retinal coordinates). A smoothly shaded object under one consistent,
primarily-overhead key light reads as solid almost instantly; conflicting or absent
shading does not.

Gloss/specular cues: Fleming, Dror & Adelson 2003
(`abstracts/fleming-dror-adelson2003-real-world-illumination-reflectance.txt`, abstract
only, PMID 12875632, PDF blocked — see `downloads-09.md`) and the related open paper
Adams, Kucukoglu, Landy & Mantiuk 2018/2019, "Naturally glossy"
(`abstracts/adams-kucukoglu-landy-mantiuk2018-naturally-glossy.txt`, read via PMC
mirror PMC6279370): glossiness/solidity reads from a small number of bright, SHARP
specular highlights consistent with one plausible light source, not from uniform
brightness. An object that emits light uniformly from every surface (an unlit neon
glow) does not read as a solid lit object for exactly this reason — it lacks the
highlight/shading pattern a real illuminated solid would have.

**Why a bright rim on a bright wall fails.** The Schorsch lighting glossary's glare
entry (`abstracts/schorsch-glare-veiling-luminance.txt`, full page
`papers/schorsch-glare-glossary.html`) names the general mechanism: a bright light
source scatters ("veiling luminance") onto its surroundings, reducing local retinal
contrast right where an edge needs to be read. Bloom is exactly this: it spreads some
of the puppet's brightness onto the neighbouring wall pixels. On a DARK background this
is invisible (background luminance stays near zero either way) — which is why standard
3-point-lighting "rim light for separation" advice is built around dark/neutral
backgrounds. On a BRIGHT background, the same spread pushes the wall pixels next to the
puppet even brighter, i.e. toward the puppet's own brightness, which **collapses** the
local contrast instead of creating it. Quantified in `data/09-colour-numbers.csv`: the
current neon-cyan-on-white look computes to a Weber contrast of only about **-6.4%**
(Michelson 0.033) against the wall — this is the numeric form of "loses focus." A dark,
saturated colour against the same wall computes to Weber contrast around **-73% to
-92%** (Michelson 0.5-0.85) depending on hue (see §3/CSV) — one to two orders of
magnitude more contrast. The fix is not "brighter rim," it is the opposite: darken the
object relative to the wall, and if any rim/edge treatment is used at all, it should be
a dark, crisp edge (or none — let the shaded body's own silhouette do the work), never
a light-scattering bloom on this side of the shot.

## 3. The numbers: hue, target luminance, and gamut

Formulas: sRGB EOTF and BT.709 relative luminance, and the CIE L* lightness formula
(`abstracts/wikipedia-cielab-srgb-formulas.txt`, full pages `papers/wikipedia-srgb.html`,
`papers/wikipedia-cielab.html`); Weber and Michelson contrast definitions
(`abstracts/wikipedia-contrast-vision-michelson-weber.txt`, full page
`papers/wikipedia-contrast-vision.html`). All computed values below and the full
candidate-hue table are in `data/09-colour-numbers.csv`; only the load-bearing ones are
repeated here.

- Wall #F2F0EA recomputed: linear Y = 0.8714, L* = 94.8 (brief's ~0.85 / ~94 — matches).
- Target contrast band from the brief, L* 40-55, inverts to relative luminance
  Y ≈ 0.1125-0.2293.
- **Pure red, #FF0000 — HSV S=100%, V=100%, the maximum possible saturation in sRGB for
  this hue — computes to Y=0.2126, L*=53.2.** That lands inside the target 40-55 band
  with NO darkening needed: the single most saturated red in the sRGB gamut already
  sits almost exactly where the figure-ground contrast argument says the puppet should
  sit. Weber contrast vs. the wall: -75.6%. Michelson: 0.608.
- Crimson, #DC143C (HSV S=91%) sits more centrally in the band: L*=47.0, Michelson
  0.689 — marginally higher contrast, marginally less saturated; a reasonable
  alternative if pure red reads too much like a warning-light red for the brand.
- Checked and rejected against the same band: orangered #FF4500 (L*=57.6, just outside,
  Michelson 0.547), magenta #FF00FF (L*=60.3, lightest of the set, Michelson 0.507,
  least contrast), pure orange #FF8000 (L*=67.1, far too light at full
  saturation/value, Michelson 0.407 — weakest of all candidates checked), pure blue
  #0000FF (L*=32.3, darker than the band, HIGHEST raw contrast of the set at Michelson
  0.847, but a cool hue — works against the red-advantage/warm-wall-warmth argument in
  §1, and blue read against a warm off-white can look muddy/cold rather than "viral").
- The current neon-cyan-with-white-rim approach (approximated as #66FFFF, a light,
  near-wall-luminance colour) computes to Michelson 0.033 — about 18x LESS contrast
  than pure red. This is the numeric confirmation of "loses focus."

**Recommendation basis:** pure, fully-saturated red is simultaneously (a) the hue with
the strongest literature-backed attention/arousal association (§1), (b) warm, aligning
with both the wall's own warm cast and the warm-colour engagement finding in Bakhshi et
al. 2015, and (c) — this is the useful coincidence this research turned up — at its own
maximum possible sRGB saturation, its luminance already lands inside the exact
contrast band (L* 40-55) that the figure-ground literature calls for, with no need to
mix in black or otherwise desaturate it to darken it. Crimson is the fallback if a
slightly less "warning-light" red is wanted, at the cost of a hair less saturation for
a hair more contrast.

## 4. String visibility (the thin lines)

Standard resolution (two-point) visual acuity: 1 arcminute
(`abstracts/pmc8523788-vernier-acuity-clinical-use.txt`, full page
`papers/pmc8523788-vernier-acuity-clinical-use.html`). But a taut string is a
LINE-detection target, not a two-point-resolution target — the relevant regime is
vernier/hyperacuity, **2-5 arcseconds** (untrained observers ~10 arcsec) in the same
source, some 12-30x finer than the resolution limit, finer even than the ~30-arcsec
spacing between foveal cone photoreceptors (explained by cortical pooling, not raw
optics).

Geometry (computed, not directly sourced — see CSV): at a typical one-hand phone
viewing distance of 30 cm, on a 6-inch, 1080x1920 screen (pixel pitch ≈0.069 mm, ≈367
ppi), **one arcminute subtends about 1.26 pixels** — i.e. a single delivered pixel is
about 0.79 arcmin (≈47 arcsec) wide on-screen at that distance. That is comfortably
above the 1-arcmin resolution limit (a 1px feature is resolvable) and 10-20x WIDER than
the 2-5 arcsec hyperacuity/line-detection threshold. **Conclusion: human line-detection
sensitivity is not the bottleneck for a 1-2px string at this viewing distance** — the
existing item-6 recommendation of a 1-2px core half-width (`../06-neon-rendering-and-assets.md`,
`data/06-render-numbers.csv`) is more than wide enough to be seen; the real constraints
are (a) the renderer's anti-aliasing quality (sub-pixel lines flicker/alias under
motion — already gated by this project's flicker checks) and (b) CONTRAST, not width.

By the same logic as §2/§3: a bright/glowing string against the bright wall repeats the
low-Weber-contrast problem (bloom spreads onto the wall right where the thin line's
edge needs definition, and a 1-2px line has very little area to begin with, so it is
disproportionately vulnerable to being washed out by its own bloom). **The strings
should be dark** (a thin, crisp, near-black or dark-warm-grey line, matched in darkness
to the puppet body rather than lit as glowing neon), 1-2px core width as already
planned, no bloom pass on the string layer.

## 5. Recommendation for the puppet

- **Hue: pure saturated red.** sRGB #FF0000, linear RGB (1.0, 0.0, 0.0) — the single
  most saturated colour available in the sRGB gamut for this hue (HSV S=100%, V=100%).
  Source: red-advantage literature (Elliot & Maier 2014), warm-colour engagement
  finding (Bakhshi et al. 2015), and the wall's own warm cast (#F2F0EA, computed from
  the given hex). If a less "alarm-red" look is wanted for the brand, the fallback is
  crimson #DC143C (HSV S=91%), which trades a little saturation for a little more
  contrast (Michelson 0.689 vs. 0.608).
- **Target luminance / lightness: L* ≈ 53 (pure red's own natural value at full
  saturation) or L* ≈ 47 (crimson)** — both inside the requested L* 40-55 band, both
  computed directly from the CIE L*/sRGB formulas (`abstracts/wikipedia-cielab-srgb-formulas.txt`)
  against the recomputed wall L* of 94.8. Source for why this band matters:
  Livingstone & Hubel 1988 (luminance, not chromatic, contrast carries form/depth) and
  the Weber/Michelson contrast formulas (`abstracts/wikipedia-contrast-vision-michelson-weber.txt`)
  quantifying it as ~61-69% Michelson contrast, an order of magnitude above the current
  neon-cyan look's 3.3%.
- **Rim: DARK, not bright — or no separate rim pass at all.** Source:
  Schorsch glare glossary (`abstracts/schorsch-glare-veiling-luminance.txt`) for the
  veiling-luminance mechanism by which a bright rim's bloom raises the adjacent wall
  luminance and collapses contrast on a light background (this reverses the usual dark-
  background rim-light convention); Fleming/Dror/Adelson 2003 and Adams et al.
  2018/2019 for why solidity should instead come from a small number of sharp,
  single-direction specular highlights and body shading, not an emissive glow; Kleffner
  & Ramachandran 1992 for shading with one consistent, primarily-overhead key light as
  the fast, pre-attentive route to reading as solid 3-D.
- **String width: keep the existing 1-2px core half-width plan, coloured dark (not
  glowing).** Source: PMC8523788 (vernier/hyperacuity thresholds of 2-5 arcsec are
  10-20x finer than the ≈47 arcsec/px this geometry produces at a 30 cm phone-viewing
  distance, so width is not the limiting factor — contrast polarity is), applying the
  same dark-on-light contrast argument as the puppet body itself.
