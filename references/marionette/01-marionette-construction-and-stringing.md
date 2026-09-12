# Item 1 — Marionette construction and stringing

For the 9-second hand shot: a CG "neon" marionette (~30 cm artist-mannequin figure) hangs from
five strings, one per fingertip pad of a right hand seen from the back, fingers pointing down,
thumb on the left of frame, middle finger longest. This note gathers the traditions' string
counts and attachment logic, figure size/mass/weight-distribution numbers, thread properties,
and control-to-puppet geometry, then recommends a finger-to-string mapping.

Every number below is attributed to a file saved in `references/marionette/papers/` or
`abstracts/`. Where no source was found, it says **NOT FOUND** rather than guessing.

## 1. String counts and attachment points by tradition

### The minimum and the standard Western set

The puppeteer-ethnographer Jacques Pimpaneau's rule, quoted in WEPA's *String Puppet* article:
"The minimum is five: one for each shoulder, one for each hand and one from the top of the
head." Adding one per temple gives 8; a 14-string figure adds one for the back, one per elbow,
one per wrist, one per group of four fingers, and one per calf; 16–22 strings do "almost all the
movements of an actor"; riding a horse needs up to 28
(`papers/wepa-string-puppet.txt`).

Chen, Tay, Xing & Yeo's engineering survey of marionette history (Nanyang Technological
University) converges on the same anatomy independently: a minimum of 8 strings for full-body
motion — two shoulders (support), and one each for the two arms, two legs and the head — with a
9th back string added for bowing. They call 8–9 "only a rule of thumb"; typical Western human
marionettes use 8–12 strings, traditional Chinese marionettes 16–24 (sometimes up to 50 — one
named 50-plus-string figure, "Drunken Zhong Kui" by Quanzhou puppet master Huang Yique, can pick
up a wine cup and pull a sword) (`papers/icdst-marionette-robotic-manipulation.txt`, section
2.2–2.3). Marionettes.cz's professional maker "Petr Puppeteer" gives an identical standard
stringing recipe for a modern 3D-printed figure: 2 head + 2 shoulders + 2 palms + 2 legs + 1 back
= 9 (`papers/marionettescz-3dprint-basics.txt`).

### What each string does, and why the weight sits on the head/shoulders

Every source agrees on a two-tier functional split:

- **Support/reference strings** — the two shoulder strings in Western marionettes, or a single
  "backbone" string in the traditional Chinese figure — "hold most of the weight of the puppet
  figure and are usually kept stationary during the performance. ... All remaining strings will
  take reference from this string" (`papers/icdst-marionette-robotic-manipulation.txt`, Fig. 2
  caption and body text, section 2.2). WEPA's *String Puppet* article states it the same way:
  "the shoulder strings can hold up the entire puppet" while "pelvis strings prop up the back,"
  "knee strings are indispensable for walking," and head/temple/neck strings give "nuanced head
  movements" (`papers/wepa-string-puppet.txt`).
- **Motion-control strings** — head, arm, hand, leg, knee strings — drive gesture and have a
  "manipulation range... very large depending on the gesture," but they do not need to bear the
  static load (`papers/icdst-marionette-robotic-manipulation.txt`, section 2.2).

The mechanical reason the weight rides on the head/shoulder yoke rather than the hands: the
shoulder pair (or the Chinese backbone string) forms a fixed, symmetric, two- or one-point
suspension that sets the whole figure's centre of gravity and keeps it upright with the strings
*stationary* — exactly the property you want from a load path. Hands and other limbs are driven
by strings whose job is to move continuously and asymmetrically; if the load path ran through
them, every gesture would also have to renegotiate the figure's balance. WEPA's *Control* article
makes the same point about the physics generally: "the task of creating a control involves
addressing problems of applied physics, taking into account the force exerted vertically by
gravity proportional to the mass of the puppet to be manipulated" — which is why "ballasting of
certain parts with lead" and the leverage of the control bar are both there to manage that one
load path, not the gesture strings (`papers/wepa-control.txt`).

### Order of attachment

French puppeteer Jacques Chesnais's own account of stringing a Lorraine-cross vertical control,
quoted in full in WEPA's *Control* article, gives the traditional sequence explicitly: hook the
puppet first at wrists, knees, lower back and both sides of the head with small closed hooks;
**then** join both sides of the head to the control bracket with strings ("Your puppet will stay
standing and upright" — i.e., the reference geometry is locked in first); **only then** attach
the remaining motion strings — back to the bottom of the cross, both knees to the bracket ends,
hands to the centre (`papers/wepa-control.txt`). The support/reference strings go on before the
motion strings in every account found.

### Czech tradition (vertical / "Skupa" cross)

The vertical control is credited to Josef Skupa (1892–1957), creator of the Czech marionettes
Spejbl & Hurvínek, and Marionettes.cz still calls the vertical cross a "Skupa cross" for this
reason (`papers/marionettescz-3dprint-basics.txt`). The ICDST survey confirms the vertical
control became the European/British/German standard in the late 19th century, superseding the
horizontal bar, and consists of "a vertical grip, with a horizontal bar at the bottom to take
head strings, hand strings, and other special ones, and a rocking bar at the top for operation of
the legs" (`papers/icdst-marionette-robotic-manipulation.txt`, section 2.3.1, Fig. 4–5a). Small
Czech controllers sold today are built for up to 9 strings; larger "semi-professional" units
handle 9+ (`papers/marionettescz-3dprint-basics.txt` product listing text, corroborating the
8–9-string rule of thumb).

### Sicilian / Opera dei Pupi

Opera dei Pupi is a **rod-and-string hybrid**, not a pure string marionette, and its weight-path
logic is the rod analogue of the head/shoulder principle above: a rigid main iron rod runs
through the head and connects it to the torso, bearing the puppet's weight and letting it hang
from a hook at the rod's upper end; the sword arm gets a second rod, while the other arm (and, in
Palermo, the knees) move on wires/strings (`papers/wikipedia-opera-dei-pupi.txt`,
`papers/wepa-pupi.txt`). Sizes and masses vary sharply by school and by source:

| school | height | mass | legs | source |
|---|---|---|---|---|
| Catania | 110–130 cm (Wikipedia) | ~30 kg (Wikipedia) / "16 kg and more" (WEPA) | rigid, no knee joint — weight rests on the floor between steps | `papers/wikipedia-opera-dei-pupi.txt`, `papers/wepa-pupi.txt` |
| Palermo | 90 cm (Wikipedia) / 80–100 cm (WEPA) | 5–10 kg (Wikipedia) / ~8 kg (WEPA) | articulated knees; a wire through the fist draws the sword | `papers/wikipedia-opera-dei-pupi.txt`, `papers/wepa-pupi.txt` |
| Syracuse | 110 cm | ~20 kg | semi-articulated | `papers/wikipedia-opera-dei-pupi.txt` |
| Naples (WEPA) | 110 cm | not given | flexible legs; one head rod, strings for both arms | `papers/wepa-pupi.txt` |

The two sources disagree on exact numbers (Wikipedia vs. WEPA's older UNIMA text), which is
itself informative: at this scale and tradition, quoted dimensions vary by a factor of ~2 in
weight depending on informant, so treat any single Opera dei Pupi figure as illustrative of
order-of-magnitude, not a precise spec.

### Burmese yoke thé

Burmese marionettes use 18 wires for male characters and 19 for female characters, each worked
by a single puppeteer (`papers/wikipedia-yoke-the.txt`). WEPA's *Control* article describes the
actual control geometry in detail: an H- (or T-) shaped horizontal control bar only about 10 cm
long. The puppet's back-suspension (support) strings attach to the two bottom extremities of the
H; the head strings attach to the two top extremities. Every other string — elbow-to-elbow,
hand-to-hand, knee-to-knee, heel-to-heel — is simply looped directly across the control bar
itself, and "the manipulator chooses one string out of the five possible, takes it in his hand
and moves it in the direction of the movement he desires" (`papers/wepa-control.txt`). This is
the clearest documented case of support strings (back/head, fixed to the control frame) versus
motion strings (limb pairs, picked up individually by hand) being architecturally separated.
Chen et al. corroborate: "a palm-sized cross type control tightened with eight to ten strings,"
operable one-handed; a more sophisticated figure with over 10 strings uses two such controllers
(`papers/icdst-marionette-robotic-manipulation.txt`, section 2.3.3).

### Airplane / horizontal control

European marionette control by horizontal strings predates the vertical control (medieval
tabletop puppets, and "à la Planchette"/fantoccini figures controlled by a single string through
a jointed body). The cross-shaped horizontal "airplane control" proper took shape in Europe in
the late 18th century and later acquired that nickname in the US because "their shapes resemble
that of aircrafts" (`papers/icdst-marionette-robotic-manipulation.txt`, section 2.3, Fig. 5b). A
notable variant is F. H. Bross's *Angle controller*: a central rod held tilted by the puppeteer,
with head strings joined at an additional bar on top and shoulder strings at a tail pivoted to
the central rod, producing a swinging/rocking motion (same section, Fig. 5c). WEPA's *Control*
article adds concrete examples: the Compagnie Blin and the Salzburger Marionettentheater both use
horizontal controls; Albrecht Roser's horizontal control is over 60 cm long and can run three
puppets at once (`papers/wepa-control.txt`).

### Vertical / "paddle" control

Invented by W. A. Dwiggins, the paddle controller is "a little over 6 inches" (≈15 cm) — tiny
compared to the airplane/vertical crosses above — and was built specifically for **12-inch
(~30 cm) puppets**, i.e. very close to our figure's size. Head, forearm and hand strings attach
along the wing; forehead, shoulder and back strings attach to the main bar; the legs are worked
by a small pivoting piece of wood the puppeteer rocks with one finger, so the whole rig — support,
head, arms and legs — is operable one-handed
(`papers/icdst-marionette-robotic-manipulation.txt`, section 2.3.1, Fig. 5d and following page).
Because it is the only source found that specifies a *controller* size against a puppet height in
our exact size class, it is the closest documented ratio available: controller ≈ half the
puppet's height (15 cm : 30 cm).

## 2. Figure size and mass in the 25–35 cm class

The clearest data at our scale come from an actual engineering build, not a craft guide: Chen et
al.'s three "Robotic Marionette System" (ROMS) prototypes at Nanyang Technological University,
built specifically in the 30 cm range and weighed on a bench:

| version | height | mass | strings | motors |
|---|---|---|---|---|
| ROMS-I | 31.2 cm | **314 g** | 8 | 8 |
| ROMS-II | 30.5 cm | **214 g** | 14 (of 16 motors) | 16 |
| ROMS-III | 29.5 cm | **259 g** | 16 | 16 |

(`papers/icdst-marionette-robotic-manipulation.txt`, Table 1, page 9). ROMS-I's figure was "a
small wooden human dummy" strung with fishing wire; ROMS-II/III used "toy soldiers" bodies with
full clothes and standard embroidery thread as the control strings (same source, section IV).
Read together, this says a ~30 cm articulated humanoid figure, dressed, comes in around
**200–320 g** — two to three orders of magnitude lighter than the 70–140 cm stage marionettes
discussed below, and light enough that even quite delicate string material (embroidery thread,
light fishing line) easily carries the static load.

For commercial corroboration at the same size: Pelham Puppets' most common "SS" (Standard
Stringed) and "LS" ranges were built at 12 inches (30.5 cm) tall on a standard cross-box control
(`papers/brightontoymuseum-pelham.txt`) — i.e. mass-produced 20th-century marionettes cluster at
almost exactly our target height. Dwiggins's own "Experimental Theatre in Miniature" figures were
about 25 cm (`papers/wepa-string-puppet.txt`).

For contrast, larger stage marionettes: Czech/German professional stage figures run 45–75 cm
(`papers/icdst-marionette-robotic-manipulation.txt`, section 2.1); the 19th-century rod-string
hybrid European marionette stood 70–90 cm and could weigh "well over 10 kg" dressed and armed
(same source, section 2.3.1); Opera dei Pupi figures run 80–140 cm and 5–30 kg (section 1 table
above). None of these larger figures are close to our 30 cm case, but they establish that mass
scales far faster than height for these puppets (padded wooden/iron-armoured skeletons at
1–1.4 m reach 16–30 kg — roughly 100× a 30 cm ROMS figure's mass for ~4× the height).

### Weight distribution and lead ballasting

Marionettes.cz's professional-maker guide (from an 18-puppet commission for a Cairo stage show,
figures 70–100 cm) gives an explicit mass-distribution rule: **head : palm : feet mass ratio ≈
1 : 0.75 : 1**, deliberately mirroring human proportion, "to get the best animation results you
need to make the head, palms, hips, and feet much heavier than the rest of the body." The
maker's own 3D-print infill settings make the same point quantitatively: 5–10% infill (with 2
perimeters) for the neck/upper body/arms/thighs/calves, versus 20–30% infill for the head, palms,
feet and lower body — roughly 2–4× the shell/fill density concentrated at the extremities and
head relative to the limbs (`papers/marionettescz-3dprint-basics.txt`). The same source gives a
marionette head-to-body height ratio of 1:5 to 1:3 (versus a real human's 1:8, or 1:6 for a
child) — heads are built deliberately oversized so the face reads at stage distance.

Lead ballasting is attested repeatedly but never with a gram figure. Pelham Puppets' "Lead
Closed Hands" and "Early Flat Lead Hands" ranges (used roughly late 1940s–early 1950s) were cast
from lead specifically for the hands (`papers/brightontoymuseum-pelham.txt`). Clive
Hicks-Jenkins's puppetry guide states plainly that "makers often add lead weights into the feet
of marionettes, to keep them in contact with the ground," and that lightweight body materials
(papier-mâché, Fimo) need embedded "bits of metal junk" for ballast
(`papers/clivehicksjenkins-marionette-part2.txt`). WEPA's *Control* article extends this to
moving mechanisms: jaw and eye levers are "ballasted... with lead pellets" so gravity, not a
spring, returns them to rest (`papers/wepa-control.txt`). **No source gives an actual mass in
grams for any of this lead — that number is NOT FOUND.**

## 3. Thread

**Material.** The one point every puppetmaking source agrees on is to avoid plain monofilament:
"I've heard to avoid fishing line as the elasticity makes it lose its proportions," to which
puppeteers on the Puppets And Stuff forum reply that they use **braided** nylon instead — "It
doesn't seem to distort under stage lights" — precisely because braided line stretches far less
than monofilament under load (`papers/puppetsandstuff-topic-5585.txt`). Clive Hicks-Jenkins uses
Coats **black linen thread** (`papers/clivehicksjenkins-marionette-part2.txt`). WEPA's *String
Puppet* article recommends "plastic strings (nylon, polypropylene) preferably multi-stranded,
which are more flexible and also call less attention to themselves"
(`papers/wepa-string-puppet.txt`). Puppetbuildingworld.com's working guide names specific
braided deep-sea fishing-line brands (Hercules, Dacron) as the most common modern choice, glued
at the knot with Duco cement, and states the obvious visibility rule: black to disappear, bright
colours only for internal mechanism strings you want to be able to see while working
(`papers/puppetbuildingworld-string.txt`).

**Strength/diameter actually used.** For light puppets, puppeteers report using far less breaking
strength than a first guess would suggest: "5–10 lb should be more than enough"
(`papers/puppetsandstuff-best-marionette-strings.txt`); "I use anywhere from 10 lb on up
depending on how heavy the puppet is" and one maker prefers "braided nylon ice fishing line,
25 lb test" for its resistance to distortion under stage light
(`papers/puppetsandstuff-topic-5585.txt`). Puppetbuildingworld.com calls 30 lb test "thin" and
sufficient for most figures, reserving up to 100 lb test for heavier puppets
(`papers/puppetbuildingworld-string.txt`).

**Diameter for a given strength (measured, from fishing-line manufacturer charts).** A
diameter/breaking-strength chart (`papers/norrik-fishing-line-strength-charts.txt`), cross-checked
against a specific product listing (Bullbuster 30 lb braided = 0.28 mm,
`papers/bullbuster-30lb-0.28mm.html`), gives braided-line diameters of:

| lb test | diameter (mm) |
|---|---|
| 8 | 0.13 |
| 10 | 0.15 |
| 15 | 0.18 |
| 20 | 0.23 |
| 30 | 0.28 |

At our figure's scale (~200–300 g, i.e. ~2–3 N of weight split across up to 5 strings), even the
lightest puppeteer-recommended line (5–10 lb ≈ 22–45 N breaking strength) has roughly an order of
magnitude safety margin per string — string choice at this scale is driven by *visibility and
handling*, not load capacity, which matches every maker's stated reasoning (thin, black,
non-stretch, easy to knot) rather than any load calculation.

**Mass per metre.** No source gives a manufacturer mass-per-metre spec for sewing/fishing thread
(spools are sold by length or by weight of the whole spool, not by linear density). A **derived,
not measured** approximate figure, computed as a solid cylinder (nylon density 1.15 g/cm³,
`papers/wikipedia-nylon.html`, × cross-sectional area from the diameter table above) gives about
**0.02 g/m at 0.15 mm (≈10 lb braided-equivalent)** and **≈0.07 g/m at 0.28 mm (≈30 lb
braided-equivalent)**. Real braided line is hollow/porous rather than a solid rod, so true mass
per metre is likely somewhat below this estimate; treat it as an upper bound, not a measurement.

**Elastic modulus / stretch.** No marionette-specific stretch or modulus measurement was found.
The closest attested numbers are for nylon monofilament fishing line generally: real
under-load ("operational") stretch is **2–9%**, distinct from the 25–35% "stretch to break"
number printed on packaging, which is measured only at the instant the line fails
(`papers/masterfishingmag-monofilament-stretch.txt`) — and this is exactly why puppeteers reject
monofilament for stringing (see above) in favour of braided line, which stretches far less. A
2014 *Science* paper on "artificial muscles from fishing line and sewing thread" confirms nylon
monofilament and sewing thread are "inexpensive high-strength polymer fibers," but its abstract
(the only part accessible — the full text is paywalled and no open-access mirror could be
retrieved) does not itself give a modulus figure
(`abstracts/haines2014-artificial-muscles-fishing-line-sewing-thread.txt`). **A specific elastic
modulus (GPa) for marionette string is NOT FOUND** — do not use the "3.3 GPa" style figures that
circulate in secondary summaries of unrelated artificial-muscle papers; they could not be traced
to a retrievable primary source in this pass.

**Measured string tension in performance.** **NOT FOUND.** No engineering or biomechanics study
measuring in-performance marionette string tension turned up in PubMed/Europe PMC/arXiv/general
search. The only figures available are the puppet's static weight (200–320 g at our scale, from
the ROMS table) and the fact that puppeteers do not report needing especially strong string —
consistent with a static per-string tension on the order of 0.5–1 N for a 30 cm figure, but that
number is a back-of-envelope inference from the mass and string-count data above, not a measured
value, and is not included in the CSV as a sourced figure.

## 4. Control-bar-to-puppet string length

No source gives a clean "string length = N × puppet height" rule. What the sources describe
instead is that string length is set by the *staging geometry* — the height of the stage/booth
floor and the puppeteer's arm position above it — not by a fixed proportion of the figure:
"After [the puppet's fabrication], there is the fabrication of the puppet, and then of the
control... [the booth's play-stage height] determines the length of the strings"
(`papers/wepa-string-puppet.txt`). Chesnais's own instructions hang the control "about a metre
from the ground" for his figure (`papers/wepa-control.txt`) — a stage-clearance number, not a
puppet-height ratio.

The one concrete size-to-size datum in our class is the **Dwiggins paddle control**: ≈15 cm
controller for a ≈30 cm puppet, i.e. controller height ≈ 0.5 × figure height
(`papers/icdst-marionette-robotic-manipulation.txt`). This is a controller-body size, not a
string length, but it is the only documented number that relates a control device's scale to a
~30 cm figure, so it is offered as the nearest analogue. **A specific string-length-to-figure-height
ratio is NOT FOUND** and should not be invented; for this shot the string length is a production
decision fixed by the real hand-to-mannequin distance visible in the frame, not by puppetry
convention.

## 5. Numbers for the model

| quantity | value | source file |
|---|---|---|
| minimum functional marionette strings | 5 (2 shoulder + 2 hand + 1 head) | `papers/wepa-string-puppet.txt` |
| our case: strings available | 5 (one per fingertip) | — (given) |
| 30 cm figure mass (built, weighed) | 214–314 g | `papers/icdst-marionette-robotic-manipulation.txt` (Table 1) |
| head : palm : feet mass ratio | 1 : 0.75 : 1 | `papers/marionettescz-3dprint-basics.txt` |
| head-to-body height ratio | 1:5 to 1:3 | `papers/marionettescz-3dprint-basics.txt` |
| controller size vs. figure height (only same-scale datum) | ≈0.5× (15 cm control : 30 cm figure) | `papers/icdst-marionette-robotic-manipulation.txt` |
| recommended string material | braided nylon (not monofilament) | `papers/puppetsandstuff-topic-5585.txt`, `papers/puppetbuildingworld-string.txt` |
| recommended line strength for a light (~250 g) figure | 5–10 lb braided | `papers/puppetsandstuff-best-marionette-strings.txt` |
| corresponding line diameter | 0.15–0.18 mm | `papers/norrik-fishing-line-strength-charts.txt` |
| derived thread mass/metre at that diameter | ≈0.02–0.03 g/m (derived, upper bound) | computed from `papers/wikipedia-nylon.html` density × diameter above |
| nylon monofilament operational stretch | 2–9% (not representative of braided line, which is lower) | `papers/masterfishingmag-monofilament-stretch.txt` |
| string tension in performance | NOT FOUND | — |
| string-length : figure-height ratio | NOT FOUND | — |
| lead ballast mass (hands/feet) | NOT FOUND (only that lead is used, attested) | `papers/brightontoymuseum-pelham.txt`, `papers/clivehicksjenkins-marionette-part2.txt` |

### Recommended five-finger → attachment mapping

Given: right hand, back view, fingers pointing down, thumb on the left of frame, middle finger
longest.

The five-string minimum documented across sources maps onto exactly two shoulder/support
strings, two hand/motion strings, and one head/reference string. Recommended assignment:

- **Middle finger (longest, most central) → head string.** In every tradition surveyed, the
  head/reference string is the one attached first and the one the rest of the rig is squared
  against (Chesnais: head strings go on before anything else, "your puppet will stay standing and
  upright"; the Chinese backbone string is likewise the reference all other strings take their
  cue from). Placing it on the longest, most central, most steady finger — which also reaches
  furthest from the hand, i.e. is physically highest on the puppet's suspension in this
  hand-above/puppet-below setup — gives the reference axis the least jitter and the correct
  "topmost attachment" role it has in every documented control.
- **Index and ring fingers (flanking the middle, next-longest, near-symmetric) → the two
  shoulder/support strings.** The shoulder pair is, in every Western source, the fixed, level,
  symmetric, weight-bearing pair that must stay stationary and must not introduce unwanted
  rotation. Index and ring are the flanking pair closest in length and position to the middle
  finger, giving the most level, most nearly-symmetric pair of anchor points available on the
  hand for the strings that are supposed to hold the figure's centre of gravity steady.
- **Thumb and pinky (shortest, most independently mobile digits) → the two hand/motion
  strings.** Hand strings are, in every source, the ones that see the most asymmetric,
  independent, gestural movement — exactly what the thumb (opposable, most independently
  actuated digit) and pinky (also commonly moved independently, e.g. in spreading/pinching)
  supply as the hand opens, closes and spreads during the shot.

**Alternative mapping:** put the two strongest, most independently controllable digits — thumb
and index — on the two shoulder/support strings instead (on the reasoning that, unlike a fixed
control-bar hook, a live hand actually has to *hold* those support strings steady against its own
tremor, so the steadiest-to-hold digits should get the steadiness-critical job), keep the middle
finger on the head string as before, and move the two hand/motion strings to ring and pinky
(reasoning that hand-string motion is traditionally the smallest-amplitude of the motion strings,
matching ring and pinky's more limited independent range). This trades slightly worse geometric
symmetry of the shoulder pair (thumb and index are not a mirror-symmetric pair the way index/ring
flank the middle finger) for putting the most controllable digits on the load-bearing strings —
a trade that matters more if the simulated figure ends up heavier than the ~200–300 g documented
for real 30 cm marionettes, and matters less if it stays in that range, since the whole puppet's
weight is only a few grams per string either way.

Both mappings are this report's own synthesis from the sourced support-vs-motion, symmetric-pair,
and reference-string-first principles above — no source discusses a five-fingered hand-held
marionette rig directly, so treat the mapping itself (not the underlying principles) as a
recommendation rather than a finding.
