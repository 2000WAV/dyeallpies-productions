# Item 8 — Branding and the end sting

The hand-puppet reel (9s, 1080x1920, real time) ends with a 1-second animated logo sting:
`github.com/DyeAllPies/dyeallpies-productions` has to be legible in it, it has to have a motion
signature (not a static card), and the puppet's own strings/glow are the natural hand-over into
the mark. Because there is no branding yet, this sting is also the first page of `tools/brand/
BRAND.md` — every later export appends to what gets decided here. Every number below is
attributed to a file saved in `references/marionette/brand/` (or `papers/` for the one academic
paper), or marked **NOT FOUND**. Numbers computed directly from those sources (character counts,
reading-time divisions, WCAG contrast ratios) say "(computed)" and show the arithmetic, per the
constant-sourcing rule in the repo's CLAUDE.md — nothing here is entered from memory.

## 0. The one finding that shapes everything else: the URL does not fit in 1 second

`github.com/DyeAllPies/dyeallpies-productions` is 44 characters (computed: `len()` of the
literal string). Against every reading-speed figure found in this research —

- Netflix's own subtitle ceiling, 20 characters/second for adult content
  (`brand/netflix-timed-text-style-guide.html`) → 44/20 = **2.2 s** to read once
- the midpoint of BBC's broadcast pace, 160-180 wpm (`brand/bbc-accessibility-subtitles-guide.html`)
  → roughly **2.9 s**
- the older, more conservative "six-second rule" pace (~12 cps, historical d'Ydewalle 1987 figure,
  cited across secondary subtitling sources, no open-access primary located) → **3.7 s**

— a full, once-only reading of the URL needs 2.2 to 3.7 seconds, not 1. This holds even though
Szarkowska & Gerber-Moron (2018, PLOS ONE, `papers/szarkowska2018-viewers-keep-up-fast-subtitles.
txt`) found that modern viewers comfortably keep up with subtitles as fast as 20 cps in eye-tracking
tests — that study is about repeated, in-context reading during a narrative, not a single
unrepeatable 1-second flash of a URL with no second chance.

The honest options, given the brief's own 1-second constraint:
1. **Split the beat**: the 1-second *animated* sting (the wordmark forming, the motion signature)
   is the part that must be 1 second and dynamic; the URL should hold, static, for a further
   1.5-2.5 s after the mark has resolved — still a very short end-card, still well inside a 9 s
   reel, but honestly longer than "1 second" for the part a viewer actually has to read letter by
   letter. This is the recommended path (used in Concepts A and B below).
2. **Abbreviate on-screen**: show only the short handle `DyeAllPies` (10 characters, computed) —
   which clears even the slowest cited pace (12 cps → 0.83 s) inside the 1-second sting — and let
   the full `github.com/.../dyeallpies-productions` live in the pasted caption text (where it is
   already going, per the caption workflow) rather than being read off the screen at all. This is
   the path in Concept C below, and is the one that best survives Instagram/YouTube's own UI
   overlays (Section 2), since a 10-character handle is much easier to park inside whatever safe
   box the platform leaves clear than a 44-character URL is.

Either way: **do not promise a legible full URL inside a literal 1-second on-screen window** — no
source found supports that being readable once, unrepeated, at any of the paces above.

## 1. Logo stings / idents: conventions, timing, and what a 1-second sting can carry

**Terminology.** A short animated logo reveal used as a sign-off or bumper is called a "logo
sting," "logo reveal," "logo animation," or — in the film/broadcast world — a studio "ident" or
"vanity plate" (per the WebSearch synthesis behind `brand/wheelhaus-logo-stings.html` and general
usage confirmed in that saved page). The audio equivalent is a "sonic ID" or "audio logo" —
Wheelhaus's own post name-drops this term directly, citing Netflix's "ba-dum" as the canonical
example (`brand/wheelhaus-logo-stings.html`).

**Duration conventions (industry practice, not a formal standard — no regulatory body sets logo-
sting length).**
- Wheelhaus Media, a working production studio, states outright that *their own* logo stings "tend
  to be around 3-4 seconds" (`brand/wheelhaus-logo-stings.html`, direct quote).
- Broader search of motion-design outlets (Renderforest, Motion Array, autoae.online — summarized
  by WebSearch, individual pages not saved because they were low-value SEO aggregates, see
  `downloads-08.md`) converges on **2 seconds** for ads/Shorts/Reels/end-cards specifically, and
  **3-5 seconds** for YouTube intros/presentation openers. This is the closest thing to a
  convention: a 1-second sting sits right at or just under the *shortest* end of what the industry
  normally attempts, which argues for keeping the sting to one clean beat, not several.
- **Netflix's "ta-dum"** is the standard long reference point the brief itself names. Per
  `brand/20k-netflix-tudum.html` (Twenty Thousand Hertz podcast, featuring Netflix's own VP of
  Product Todd Yellin, Brand Design Lead Tanya Kumar, and sound designers Lon Bender/Charlie
  Campagna of Formosa Group): the sound was developed over roughly a year, debuted in 2015, and
  was deliberately made short and "crisp" because "in a fast-paced world a long sound wouldn't
  work." Secondary sources (not independently saved, see `downloads-08.md`) disagree on the exact
  short-form duration (3 s vs 4 s reported) but agree Netflix also produced a **16-second**
  theatrical/orchestral extension scored by Hans Zimmer for cinema use — i.e. the "long reference"
  the brief names is roughly 4-16x longer than our sting.
- **App splash screens** are the other short-duration precedent: search-derived guidance (appypie.
  com, uxpin.com; not independently saved) puts the *animated* portion at "≤1,000 ms" and the total
  splash hold at under 1.5-2 s before users start wondering if the app has frozen. A 1-second logo
  sting is exactly at this ceiling — consistent with "this is about as long as an animation can run
  before it needs to hand off to something else," which matches Section 0's conclusion that the URL
  itself needs a *separate* hold beat after the sting's own second is spent.

**What a 1-second sting can actually carry.** Given the durations above, and given that Material
Design's own numbers put a *single* UI transition at 195-400 ms (Section 3), a 1-second (30-frame
@ 30fps) sting has room for roughly **3-4 sequential beats** before it starts to feel like more
than "one" motion — e.g. (a) an initiating action (something snaps/collapses/releases), (b) the
mark resolving, (c) one accent flourish (a rim-light pulse or an underline draw), not more. All
three concepts in Section 6 are built to exactly this 3-4-beat budget.

**Motion-design principles / "motion signature."**
- Google's own framing (`brand/design-google-making-motion-meaningful.html`, Google Design):
  Material motion "conveys energy, drawing inspiration from forces like gravity and friction,"
  aims to feel natural "like gaining velocity or easing into a resting state by following an arc
  rather than a straight path," and exists to *guide* the user, not just decorate. Material's
  documented durations and the standard easing curve are in Section 3.
- Fluent's official guidance (`brand/msft-timing-easing.html`, Microsoft Learn) states plainly:
  "Easing is a way to manipulate the velocity of an object as it travels... it's the glue that ties
  together all the Fluent motion experiences" — i.e. a consistent easing curve, reused everywhere,
  *is* the motion signature. Fluent ships exactly two named curves for this purpose (see Section 3
  for the bezier values): one for anything entering, one for anything leaving.
- IBM's design language (`brand/ibm-motion-tips-techniques.html`, `brand/ibm-motion-classic-
  principles.html` — both client-rendered React pages that would not yield static text on repeated
  curl/WebFetch attempts, including a Wayback Machine snapshot attempt; cited here via WebSearch's
  own summary of the pages' stated content, flagged as not independently re-verified against saved
  raw text) frames motion as a duality: "Productive" motion (subtle, efficient, for micro-
  interactions) versus "Expressive" motion (vibrant, more visible, used sparingly) — and states
  that *sparse* compositions can carry more expressive motion, while dense ones need smaller,
  "textural" motion. A single 1-second sting on a plain dark ground is exactly the sparse case IBM
  says can carry the most expressive motion.
- "Motion signature" as a named concept (general branding/motion-design trade usage, WebSearch
  synthesis, no single primary source): a brand's *consistent* way of moving — a shared timing
  rhythm, easing curve, and directional logic reused across everything it publishes — is what
  makes motion recognizable the way a static logo is. The practical implication for `BRAND.md`:
  write down ONE easing curve and ONE small family of durations now (Section 3 gives the concrete
  candidates), and reuse them in every future export's transitions, not just the sting.
- **The 12 classic animation principles** (Thomas & Johnston, *The Illusion of Life*, 1981 — the
  book itself was not fetched, cited via widely-republished secondary summaries, e.g. the
  UI-design write-ups surfaced by WebSearch) supply the two principles most relevant to a hand-over
  moment: **anticipation** (a small pull-back or gather before the main motion, telling the eye
  something is about to happen) and **follow-through/overlapping action** (parts of a moving system
  arriving at rest at slightly different times, not all at once). Concepts B and C below use staggered
  arrival explicitly for this reason.

## 2. Legibility at reel size

**Minimum text height.** `brand/legibility-info-rules-text-video.html` (legibility.info, a
typographic-legibility research project) gives a directly usable, worked figure: for a video shown
full-screen on an average smartphone, **body text needs a minimum of 40-60 px at a 1920x1080
(full-HD) frame**, and **titles should be at least 50% larger than body text**. The page's own
worked example (40 cm reading distance, visual acuity 0.5, an x-height/font-size ratio of 0.51
typical of a typeface like Frutiger) computes to a **58 px** recommended body-text size, derived
from treating the frame's diagonal (2203 px for 1920x1080) as filling an average 6.174-inch phone
screen (357 virtual ppi). Because `sqrt(1080^2+1920^2) = sqrt(1920^2+1080^2)` — the diagonal pixel
count is identical whether the frame is landscape or portrait — this 40-60 px / 58 px figure
carries over directly to the reel's actual 1080x1920 canvas. **For the sting's wordmark, this means
the letterforms should render meaningfully larger than 58 px cap-height** (it is a title/logo
moment, not body text, and per legibility.info's own +50% title rule that argues for ~90 px+ as a
floor, well below the mark's actual on-screen size in any of the three concepts, which use a
wordmark spanning most of the frame width).

**Platform safe areas.** Instagram's own Help Center page for Reel sizing
(`brand/help-instagram-reel-size.html`) and YouTube/Google Ads' own Shorts-ads spec page
(`brand/support-google-shorts-ads-specs.html`) were both fetched directly, and both are
client-rendered pages that returned no static safe-zone pixel numbers — Google's page did confirm
the 9:16 / 1080x1920 recommendation but nothing about UI-overlay margins. The pixel figures below
are therefore **industry-standard ad/template numbers, not the platforms' own published figures**
(the task brief explicitly allows "the platforms' or the standard templates' actual numbers" for
this reason) — flagged here and in the CSV every time:
- **Instagram Reels / Stories (2026 unified 9:16 safe zone, per multiple ad-spec blogs — billo.app,
  firstpier.com, 1clickreport.com, not independently saved, see `downloads-08.md`):** clear the top
  14% (~270 px on 1080x1920), each side 6% (~65 px), and the bottom — sources disagree between 20%
  and 35% (~340-672 px); use the more conservative **35% / 672 px** for anything that must survive
  the caption + like/comment/share/audio stack. This leaves a safe box on the order of 950x978 to
  950x1420 px depending which bottom figure is trusted.
- **YouTube Shorts (per template blogs — flixier.com, poster.ly, youtubetoolkit.com, not
  independently saved):** one template gives a ~900x1160 px safe box; another gives top 380/bottom
  380/left 60/right 120 px; a third gives top 120/bottom 300/right 96 px. These three templates do
  not agree with each other, which is itself the honest finding — there is no single authoritative
  YouTube Shorts safe-zone number in the public record found here, only a family of similar
  third-party templates. **The right-hand action column (like/comment/share/subscribe) is the one
  point of agreement across every source**: keep the wordmark clear of roughly the right-hand 120 px
  and the bottom third of the frame on both platforms.
- **Where the URL/mark survives both:** the intersection of every figure above is a horizontal band
  roughly centered in the frame, above the bottom ~35% and inboard of both the left 65 px and the
  right ~130-200 px (Instagram's action column is the tighter constraint on the right). Placing the
  wordmark and the URL/handle centered in the frame between roughly y=270px and y=1250px (well
  above both platforms' bottom UI, centered horizontally with margin on both sides) clears every
  cited figure simultaneously. All three concepts in Section 6 use this placement.

## 3. Motion-design numbers actually published by real systems

| System | Duration / value | Source |
|---|---|---|
| Material Design v1, mobile baseline | 300 ms | `brand/m1-material-duration-easing.html` |
| Material Design v1, large/full-screen | 375 ms | same |
| Material Design v1, element entering | 225 ms | same |
| Material Design v1, element leaving | 195 ms | same |
| Material Design v1, "feels too slow" past | 400 ms | same |
| Material Design v1, desktop | 150-200 ms | same |
| Material Design v2, opacity transition | 235 ms, `cubic-bezier(.4,0,.2,1)` | `brand/m2-material-speed.html` (live CSS sample) |
| Material Design v2, position transition | 500 ms, same curve | same |
| Material Design 3 duration tokens (short1...long4) | 50-600 ms | third-party token references only — m3.material.io itself returned no static content on two fetch attempts, **not independently verified against a primary saved page** |
| Fluent / WinUI3, `ControlNormalAnimationDuration` | 250 ms | `brand/msft-timing-easing.html` (official Microsoft Learn) |
| Fluent / WinUI3, `ControlFastAnimationDuration` | 167 ms | same |
| Fluent / WinUI3, `ControlFasterAnimationDuration` | 83 ms | same |
| Fluent, entrance easing ("Fast Out, Slow In") | `cubic-bezier(0, 0, 0, 1)` | same |
| Fluent, exit easing ("Slow Out, Fast In") | `cubic-bezier(1, 0, 1, 1)` | same |
| IBM | "Productive" (subtle, fast) vs "Expressive" (vibrant, sparing) motion duality | cited via WebSearch summary of `brand/ibm-motion-tips-techniques.html`; page itself would not statically render, **not independently re-verified** |

**Reading across these**: every system that published real numbers (Material v1/v2, Fluent) puts a
*single* UI transition in the 150-500 ms range, with 400 ms as Material's own stated "starts to
feel slow" ceiling. A 1-second (1000 ms) sting is therefore naturally 2-4 single-transitions long —
which is exactly the 3-4-beat budget used in Section 6's concepts, and confirms the sting should
not be built as one continuous 1000 ms ease (that would read as sluggish by every cited system's
own standard) but as a short sequence of 150-400 ms beats.

## 4. Brand-identity foundations

**Wordmark vs. symbol.** No single source states a hard rule for when a wordmark alone is enough,
but the reasoning that follows from the platform-legibility numbers in Section 2 is directly
applicable: a symbol/icon has to be legible at a much smaller size than a wordmark (it typically
survives down to app-icon or favicon scale), while a wordmark only has to work at the sizes this
specific project actually needs (a full-width reel sting, a channel banner, a caption credit line).
Given DyeAllPies Productions is presently a single creator's channel with no existing mark at all,
and the deliverable's own premise is that the puppet's strings/glow *become the letterforms*
(i.e. the motion IS the distinguishing mark, not a separate static icon) — **a wordmark-only
identity is the right scope for this brand**, with the option to extract a standalone symbol later
if the channel ever needs a small-format mark (e.g. a monogram built from the same string-derived
letterforms) once one exists to extract from.

**Palette derived from the neon look, with WCAG contrast ratios (computed from the official WCAG
2.2 relative-luminance formula, `brand/w3-wcag-glossary-relative-luminance.html`: linear-light
mix `L = 0.2126 R + 0.7152 G + 0.0722 B` after the sRGB gamma transform; contrast ratio
`(L_lighter + 0.05) / (L_darker + 0.05)`):**

| Colour | Hex | Role | Contrast vs dark ground `#0A0E14` | Contrast vs off-white wall `#F2F0EA` |
|---|---|---|---|---|
| Dark ground | `#0A0E14` | sting background, primary UI dark | — | 16.97:1 (as text ink on the wall) |
| Neon cyan | `#3DE8F2` | puppet core / primary wordmark fill | **12.91:1** (AAA normal text) | 1.31:1 (fails outright) |
| Neon blue | `#4D7FFF` | strings / rim / secondary fill | **5.34:1** (AA normal text) | 3.18:1 (fails normal, borderline large) |
| Accent orange | `#FF7A33` | signature tick / underline / CTA, used sparingly | **7.44:1** (AAA normal text) | 2.28:1 (fails outright) |
| White | `#FFFFFF` | single fresnel/flash beat only | 19.34:1 | — |
| Off-white wall | `#F2F0EA` | matches the live plate; background only, not a text colour here | — | — |

Two things fall directly out of the arithmetic, not from taste: (1) **the neon palette only works
as text on the dark ground** — every neon colour fails WCAG AA against the off-white wall, so any
text-bearing frame (the sting, any caption card) must sit on the dark ground, never composited
directly over the off-white-wall footage; (2) **per WCAG 2.2's own Understanding document,
"text that is part of a logo or brand name has no contrast requirement" at all**
(`brand/w3-wcag-relative-luminance.html`, quoted verbatim in Section 4's CSV row) — so the wordmark
itself is technically exempt, but every number above still clears AA/AAA comfortably, which means
the mark reads cleanly for viewers with low vision too, not just decoratively.

**Type — open-licence only, all confirmed SIL OFL 1.1 directly from each font's own licence file**
(fetched and saved as `brand/ofl-<name>.txt`; see `downloads-08.md` for the raw URLs and canonical
GitHub repos of each):

| Font | Best role for this label | Licence file fetched |
|---|---|---|
| **Space Grotesk** | wordmark — geometric, technical, distinctive angular strokes that plausibly read as "made of straight strings" | `brand/ofl-spacegrotesk.txt` |
| **Inter** | body/subhead ("Productions", captions baked into any future video) — huge weight range, the neutral workhorse | `brand/ofl-inter.txt` |
| **JetBrains Mono** | the URL/handle string specifically — monospacing makes per-character width exact (useful for the Section 0 hold-time math) and reads as "technical," matching the channel's format | `brand/ofl-jetbrainsmono.txt` |
| IBM Plex Sans | alternate body option, slightly more "corporate technical" than Inter | `brand/ofl-ibmplexsans.txt` |
| Manrope | alternate wordmark option, rounder/warmer geometric sans | `brand/ofl-manrope.txt` |
| Sora | alternate wordmark option, geometric with a slightly display-forward feel | `brand/ofl-sora.txt` |
| Outfit | alternate body/subhead option | `brand/ofl-outfit.txt` |
| Syne | alternate display option, more experimental/angular than Space Grotesk | `brand/ofl-syne.txt` |
| Unbounded | alternate display option, rounded and bold — good "collapse into a blob" letterform if a future sting wants a softer look | `brand/ofl-unbounded.txt` |

Recommendation for `BRAND.md`: **Space Grotesk Bold** for the wordmark, **Inter** for everything
else set as prose (captions, subheads), **JetBrains Mono** reserved specifically for the URL/handle
string wherever it appears on-screen. All three are downloadable free of charge from Google Fonts
or their canonical GitHub repos (URLs in `downloads-08.md`); none were downloaded as font files in
this pass per the task's own instruction that the build session handles that.

**Credit-line convention.** The channel already credits its AI collaborator as "by Fable" in
videos (per the task's own context) — no separate research was needed or attempted for this, since
it is an existing, working convention. The recommendation is only to keep this exact phrasing
consistent with the new wordmark's own type (Inter, small size, low-emphasis colour — e.g. the
neon blue at reduced opacity) rather than inventing a new format for it.

## 5. Does a branded end-sting cost retention or completion? What actually exists

**Short answer: no rigorous, controlled study was found — this is a genuine gap, not a "yes/no"
that got missed.** A dedicated search for peer-reviewed or platform-published research isolating
*a branded end-sting's* effect on short-form completion/retention (as opposed to general video
length or hook-strength research) returned nothing beyond creator-analytics marketing blogs and
best-practice writeups. Specifically:
- Search located a peer-reviewed paper on YouTube retention *measurement methodology* (Altman &
  Jimenez, "Measuring Audience Retention in YouTube," VALUETOOLS 2019) via its HAL open-archive
  record, but the HAL landing page (`brand/hal-altman-audience-retention.html`) yielded no working
  PDF link on fetch, and the paper's own stated scope is about *how retention is measured*, not
  about outros/end-screens specifically — so it was not used as a citation here even though it was
  chased down.
- The only figures available are **from creator-analytics/marketing blogs, not peer-reviewed
  research** (shortzly.com, kineclip.com, opus.pro, virvid.ai, socialvideoplaza.com,
  humbleandbrag.com — summarized via WebSearch, individual pages not archived because they are
  low-value SEO aggregates repeating similar unsourced numbers; see `downloads-08.md`): short-form
  clips under 30 s reportedly see 55-70% completion; YouTube Shorts average ~73% retention vs ~52%
  for long-form; the last few seconds of a short is a common drop-off point when content is
  "clearly wrapping up"; a generic "thanks for watching / see you next time" outro is specifically
  called out (unsourced) as something that loses viewers, whereas a surprise element or a natural
  loop at the very end is claimed to help.
- **NOT FOUND**: any number quantifying the specific cost (or benefit) of a *branded* 1-second
  sting versus no sting at all, on any platform, from any source (academic or platform-published).

**What this means for the brief, stated honestly rather than guessed:** the blog-level advice
converges on avoiding a *static, expected* "thanks for watching" moment — which argues, if
anything, *for* the brief's own instinct to make this a short, in-motion hand-over (the puppet's
own glow doing something, not a card fading in) rather than a conventional outro card. But there is
no data to say a branded sting measurably helps or hurts completion on this channel specifically;
the one thing Dennis's own memory record confirms empirically for this channel is that the
full-length pull-up reel (no sting at all, as far as this research can tell) hit 140k views, which
is not a controlled comparison and should not be read as evidence either way.

## 6. Three concept directions

All three assume the sting is exactly **30 frames at 30 fps (1.000 s)** of animated motion,
followed by a **separate static hold** carrying the URL/handle (per Section 0's finding), on the
dark ground `#0A0E14`, using the palette and type from Section 4, placed inside the safe band from
Section 2 (roughly y=270-1250 px, centered horizontally with margin from both edges).

### Concept A — "Strings Into Letterforms" (structural hand-over)

The puppet's own control strings — already the most legible glowing element in every shot — are
the thing that survives into the mark, literally re-draping into letter-strokes.

- **Frames 0-5 (0-0.17s, still on the live composite):** the puppet's glow brightens one notch (a
  small anticipation beat, per the classic-animation-principle read in Section 1) as if gathering
  charge, just before cut.
- **Frames 5-6 (hard cut):** cut to the dark ground `#0A0E14`. Only the strings remain on screen,
  disconnected from the hand/puppet, drawn taut.
- **Frames 6-14 (0.27s):** the strings snap straight using Fluent's entrance curve `cubic-
  bezier(0,0,0,1)` ("Fast Out, Slow In," Section 3) — arriving at full velocity, decelerating hard
  into position, the same "traveled a long distance and arrived at speed" read Microsoft's own docs
  describe.
- **Frames 14-22 (0.27s):** the straightened strings kink at new joints, staggered by 1-2 frames
  each (follow-through/overlapping action, Section 1) into the strokes of "DyeAllPies" set in Space
  Grotesk Bold, filled neon cyan `#3DE8F2`.
- **Frames 22-26 (0.13s):** one white `#FFFFFF` fresnel-style rim pulse travels left-to-right along
  the completed wordmark once — a "current running through a wire" beat that keeps reading these as
  the same glowing strings, not a new object.
- **Frames 26-30 (0.13s):** the accent-orange `#FF7A33` tick/underline draws in beneath the mark,
  left to right — this tick is the reusable motion-signature element for every future export's
  outro, independent of whether a puppet is on screen.
- **Hold (additional ~1.5-2.0s after frame 30, outside the "1-second sting" proper):** "Productions"
  sets in beneath in Inter Regular, cyan or white; the full URL sets in JetBrains Mono beneath that,
  static, sized well above the 58 px legibility floor (Section 2) — this is the beat that actually
  gives the URL its required ~2.2-3.7s of total visible time when added to the sting itself.

### Concept B — "Glow Collapse to Core" (particle/energy hand-over)

The puppet's whole volume condenses to a point of light and re-expands as the mark — echoes
"letting go of the strings" rather than the strings themselves transforming.

- **Frames 0-8 (0.27s):** cut to the dark ground; the puppet (now small in frame) implodes toward
  its own centroid, glow pulled inward, eased on Material's own standard curve `cubic-
  bezier(.4,0,.2,1)` (Section 3, `brand/m2-material-speed.html`) since this is a "leaving the
  screen" motion by collapsing away rather than exiting a side.
- **Frames 8-10 (2 frames, ~0.07s):** a single bright white flash frame at full collapse — the
  "ta-dum" beat (Section 1): a short, percussive, single hit at the pivot moment is what the
  Netflix reference makes memorable, and this is the closest visual equivalent.
- **Frames 10-23 (0.43s):** from the flash point, "DyeAllPies" in Space Grotesk Bold, neon cyan,
  expands outward letter by letter, each letter staggered 2 frames behind the last (explicit
  anticipation/follow-through, Section 1), arriving on Fluent's entrance curve.
- **Frames 23-30 (0.23s):** the orange tick draws under the mark, same as Concept A — kept
  identical across concepts so it can be adopted as the fixed motion-signature element regardless
  of which concept ships.
- **Hold:** identical to Concept A's hold beat.

### Concept C — "Hand Releases the Mark" (practical / literal hand-over)

The real tattooed hand — on screen the entire video as the "puppeteer" — is the one that visibly
signs off, tying the brand mark to the fact that this is a single creator's label, not an
anonymous effect. This is also the only one of the three that does not require the CG puppet to be
on screen at all, which matters because most future exports under this brand will not have a
marionette.

- **Frames 0-9 (0.3s, still on the live plate):** the hand's fingers uncurl (can be shot practically
  rather than simulated) and release a single mote of cyan light from the fingertips.
- **Frames 9-12 (0.1s):** quick cut to the dark ground as the mote falls, leaving a short glowing
  motion-blur trail, eased on Fluent's exit curve `cubic-bezier(1,0,1,1)` ("Slow Out, Fast In,"
  Section 3) since this is explicitly an object leaving a scene.
- **Frames 12-24 (0.4s):** the trail whips first into the orange signature-tick stroke (drawn in one
  continuous motion — literally a hand-drawn signature gesture), then the cyan wordmark letters
  snap in above it as one synchronized group arrival (deliberately the *opposite* rhythm from
  Concept B's staggered letters — calmer, more "signed and done"), using Material v1's own 225 ms
  "element entering" figure (Section 3) scaled into this frame budget.
- **Frames 24-30 (0.2s):** "Productions" subhead sets in; hold begins as in the other two concepts,
  but here the short handle `DyeAllPies` (10 characters, clears even the slowest cited reading pace
  inside the sting itself, Section 0) can optionally be set directly into the sting's own last few
  frames instead of only the hold, since it is short enough to fit.

**Recommendation**: Concept C is the strongest foundation for `BRAND.md` specifically because it is
the only one of the three that still makes sense without a marionette in frame — every later
export under this brand can reuse "the hand releases the signature" as the fixed motion signature,
while Concepts A and B are stronger *for this specific puppet video* (the hand-over is more
literally tied to the strings/glow the brief describes) but would need a different opening beat for
a non-puppet video.

## Numbers for BRAND.md

| Category | Value | Source |
|---|---|---|
| Sting animated duration | 30 frames @ 30 fps = 1.000 s | task brief |
| Recommended additional static hold for URL | +1.5 to 2.0 s (total ~2.5-3.0 s on screen incl. sting) | computed, Section 0, against `brand/netflix-timed-text-style-guide.html` (20 cps) and `brand/bbc-accessibility-subtitles-guide.html` (160-180 wpm) |
| Full URL length | 44 characters | computed |
| Short handle length | 10 characters (`DyeAllPies`) | computed |
| Minimum body-text size at reel resolution | 40-60 px (worked example: 58 px) | `brand/legibility-info-rules-text-video.html` |
| Title-text size vs body | +50% minimum | same |
| Instagram Reels/Stories safe zone (industry template, NOT Instagram's own published figure) | top 14% (~270px), sides 6% (~65px), bottom 20-35% (~340-672px) | aggregated ad-spec blogs, see Section 2 + `downloads-08.md` |
| YouTube Shorts safe zone (industry templates, disagree with each other, NOT YouTube's own published figure) | ~900x1160px safe box (one template); or margins top/bottom 380/380, left/right 60/120 (another) | aggregated template blogs, see Section 2 + `downloads-08.md` |
| Recommended sting text placement | y ≈ 270-1250px, horizontally centered | computed intersection of the above |
| Dark ground | `#0A0E14` | chosen; contrast ratios computed Section 4 |
| Neon cyan (wordmark fill) | `#3DE8F2` — 12.91:1 on dark ground | computed, WCAG formula `brand/w3-wcag-glossary-relative-luminance.html` |
| Neon blue (strings/rim) | `#4D7FFF` — 5.34:1 on dark ground | same |
| Accent orange (signature tick) | `#FF7A33` — 7.44:1 on dark ground | same |
| White (single flash beat only) | `#FFFFFF` — 19.34:1 on dark ground | same |
| Off-white wall reference (background only, not text) | `#F2F0EA` | matches the live plate |
| WCAG minimum for any future on-brand text (normal / large) | 4.5:1 / 3:1 | `brand/w3-wcag-contrast-minimum.html` (official W3C) |
| Wordmark typeface | Space Grotesk Bold, SIL OFL 1.1 | `brand/ofl-spacegrotesk.txt` |
| Body/subhead typeface | Inter, SIL OFL 1.1 | `brand/ofl-inter.txt` |
| URL/handle typeface | JetBrains Mono, SIL OFL 1.1 | `brand/ofl-jetbrainsmono.txt` |
| Alternate type options (all confirmed SIL OFL 1.1) | IBM Plex Sans, Manrope, Sora, Outfit, Syne, Unbounded | `brand/ofl-*.txt`, see Section 4 table |
| Motion signature — entrance easing | `cubic-bezier(0, 0, 0, 1)` (Fluent "Fast Out, Slow In") | `brand/msft-timing-easing.html` |
| Motion signature — exit easing | `cubic-bezier(1, 0, 1, 1)` (Fluent "Slow Out, Fast In") | same |
| Motion signature — alternative standard curve | `cubic-bezier(0.4, 0.0, 0.2, 1)` (Material standard) | `brand/m2-material-speed.html` |
| Single-beat duration budget inside the sting | 150-400 ms per beat (3-4 beats total in 1s) | synthesized from Material v1/v2 + Fluent's own published durations, Section 3 |
| Peer-reviewed evidence that a branded end-sting costs/helps short-form completion | **NOT FOUND** | Section 5 |
