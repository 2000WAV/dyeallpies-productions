# DyeAllPies Productions — brand foundation (v1, 2026-09-12)

The label's branding, built for the hand-puppet reel's end sting and appended to every later export
by `tools/scripts/render_brand_sting.py`. The palette and the fonts live in code in
`tools/studio/brand.py` (the sting reads them from there; `python -m studio.brand` prints the contrast
table below); this file carries the reasoning. Every number comes from
`references/marionette/08-brand-sting.md` (item 8 of the marionette research) unless marked as a
choice; the research file carries the sources.

## The mark

- **Wordmark, no symbol.** `DyeAllPies` in Space Grotesk Bold, tight tracking; `PRODUCTIONS` in
  Inter Semibold, letter-spaced, half the wordmark's cap height, under the wordmark's right half.
  A wordmark is enough for a one-person technical label; a symbol can grow out of the strings later.
- **The motion signature: the five-string drop.** Five vertical strings fall from the top of the
  frame, snap taut with a bounce (the marionette's own physics, the thing the label's first format
  was about) and their lower ends light the wordmark letter by letter as they land. Every sting opens
  with the drop; formats that have no puppet still get the five strings.
- **The handle vs the URL.** `DyeAllPies` (10 characters) is readable inside a one-second sting;
  the full URL `github.com/DyeAllPies/dyeallpies-productions` (44 characters) needs 2.2–3.7 s at the
  cited reading speeds (Netflix 20 cps, BBC 160–180 wpm), so the URL gets its own hold after the
  animation. The total appended tail is 2.5 s: 1.0 s of animation, 1.5 s of hold with the URL.

## Palette (decided by Dennis, 2026-09-12: main and secondary; the neutral is a choice)

| role | hex | contrast on the main `#231F20` | contrast on the off-white wall `#F2F0EA` |
|---|---|---|---|
| **main** (a warm near-black): the ground of every sting and card | `#231F20` | – | 14.30 : 1 (AA) |
| **secondary** (orange): the wordmark, the strings, the tick | `#D75413` | 4.01 : 1 (AA large, ≥ 24 px) | 3.57 : 1 (AA large) |
| neutral (off-white): `PRODUCTIONS`, the URL, the strings' core | `#F2F0EA` | 14.30 : 1 (AA) | – |
| white: one flash beat only | `#FFFFFF` | 16.30 : 1 | – |

Contrast ratios computed with the WCAG 2.2 relative-luminance formula (`studio.colour.wcag_contrast`;
the formula and the AA thresholds 4.5 : 1 normal / 3 : 1 large are in item 08's `brand/` files). The
orange passes only as large text (WCAG's 18 pt / 24 px), which the 150 px wordmark and the 44 px
`PRODUCTIONS` are; and a logo's own text has no requirement at all. Body text on the dark ground is
set in the neutral; brand text over the light-wall footage is set in the main near-black (14.3 : 1),
never in the orange alone. v0's neon cyan `#3DE8F2` and blue `#4D7FFF` were provisional from the
puppet's first look and are retired; the puppet's red is a per-video look decision (item 09), not
the brand.

## Type (all SIL Open Font License 1.1; files and licences in `tools/brand/fonts/`)

- Space Grotesk (variable, weight axis) — the wordmark, at Bold (700).
- Inter (variable) — subheads and body, Semibold (600) for `PRODUCTIONS`.
- JetBrains Mono (variable) — the URL and handles, Medium (500).
- Minimum text height at 1080×1920: 58 px for body text (legibility.info's worked example);
  the URL is set at 52 px in the mono, the wordmark at 150 px.

## Motion rules

- Entrance easing `cubic-bezier(0, 0, 0, 1)` (Fluent "fast out, slow in"); exits
  `cubic-bezier(1, 0, 1, 1)`. Three to four beats inside the second, 150–400 ms each.
- The sting's beats at 30 fps: frames 0–8 the strings fall (gravity, real: 0.27 s for the frame's
  height at the puppet's scale), 8–12 the snap and bounce, 10–22 the wordmark lights left to right
  as the strings land, 22–30 `PRODUCTIONS` tracks in and the orange tick draws under the wordmark;
  then the hold: the URL fades in over 6 frames and stays 39 more.
- Safe area: everything between y = 270 and y = 1250 px, horizontally centred, inside x = 65–1015
  (the intersection of the Instagram and YouTube Shorts template safe zones; the platforms
  publish no figures of their own, see item 8).
- The glow around the lit elements stays (three Gaussians, 0.30 / 0.18 / 0.10): on the dark ground it
  is the "lit thread" read, and item 09's objection to bloom (veiling luminance) applies to a bright
  ground only.

## The ground when the video ends on black (2026-09-12)

The main #231F20 is the sting's default ground. A video that ends on pitch black (the neon-on-black
puppet, whose outro dips to #000000) gets the sting on `ground=#000000` (an option of
`render_brand_sting.py`): the warm near-black would read as a step up at the join. Dennis's call
for that video; the brand's own ground is unchanged.

## The brand is not fixed yet: a video's look may carry into its logo (Dennis, 2026-09-12)

"We don't have a fixed brand yet, so let's make this video have a common visual thread that extends
into the logo." So v1 above is provisional, and `render_brand_sting.py look=neon` renders the sting
in the neon puppet video's own look: the wordmark and the falling strings in the doll's electric
violet #8F00FF with a pale tube core #CCA1FF (the strings' colour in the video), `PRODUCTIONS` and
the URL in that pale violet, the tick under the wordmark in the boots' pure red #FF0000 with the
boots' 3.5x glow, and the glow itself computed as the video's composite computes it (`studio.glow`:
the emission at 1.5 in linear light, the 3/9/27/81 px bloom, the sigma 60 + 180 pool on the wall at
0.8, the shoulder). The colours are options (`accent=`, `core=`, `tick=`, `gain=`, `wall=`), so the
next video's look can carry the same way. Sheets: `hand/work/sting_neon_sheet.png`,
`sting_neon_logo_1to1.png`. Whether the neon violet becomes the brand is his call once a few videos
exist; the orange v1 stays the default of the script.

## Appending the sting (2026-09-12)

`render_brand_sting.py <out> append=<shot>` encodes the sting with the shot's own stream parameters
(codec, profile, level, size, frame rate, pixel format, a silent AAC track at the shot's sample rate
and channel count: `studio.encode.sting_encode_args`) and joins the two with the concat demuxer and
`-c copy` (`studio.encode.concat_copy`), so the shot's frames are bit-identical in the export and the
join costs seconds. The hand-puppet export: 22 s for the sting's render + join, against a full
NVENC re-encode of the shot before.

## What is not decided yet

- Whether the tail costs completion: no study isolates a branded end-sting on short-form
  (item 8, NOT FOUND). The first reel with it is the measurement.
- A symbol, a sound (the "ta-dum" beat exists only as the white flash for now).
- The neutral's exact value: `#F2F0EA` is the wall reference reused as the light neutral; a warmer
  or cooler paper tone is one edit in `studio/brand.py`.
