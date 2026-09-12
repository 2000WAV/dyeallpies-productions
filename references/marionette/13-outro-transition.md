# 13 — the outro transition into the sting (2026-09-12)

Dennis, after the neon-on-black export: the hand and the doll must not vanish on a hard cut into the
brand sting; add a camera transition, "look up a viral one". This note records what was looked up, what
was chosen and the numbers in `render_puppet.py::outro_frame`.

## What short-form editors ship as the default transition

The transition every phone editor's template library leads with is the **zoom / pull-in**: the outgoing
clip scales up about a point of interest, a zoom (radial) blur streaks it, and the incoming clip lands
already scaled in (or, when it starts dark, from black). The same effect is sold under several names:

| name | where | what it does | figures found |
|---|---|---|---|
| Pull In / Pull Out | CapCut (mobile and PC) | the outgoing clip zooms toward the cut, the incoming clip starts zoomed in, "as if the camera is moving closer" | mobile lets the duration go 0.3–1 s; the PC build locks it at 0.1 s (a known bug thread) |
| Zoom transition (manual) | Premiere Pro, CapCut's own guide | scale keyframes 100 % → 120 % or more at the clip's end, the ease from the keyframes | 120 % is the guide's starting number |
| Zoom Blur Impacts | Film Impact (Premiere pack) | "pulls viewers in with fast, dynamic movement": a zoom with a directional blur, direction and speed adjustable | none published |
| Dip to Black | every NLE | fade the outgoing clip to black, fade the incoming up; "signals the beginning or end of a scene" | a 2 s dip = 1 s down + 1 s up |

The trend pages for 2026 ("viral reel transitions") list in-camera match cuts (a hand or a leg sweeping
across the frame, cut at the same point of the motion) and POV reveal moves; none of them applies to a
static shot ending on a hanging doll. The pull-in is the one that fits a subject the camera can move toward.

## What was built

The outgoing half of the pull-in, plus a dip to black, over the shot's last 18 frames (0.6 s: inside the
0.3–1 s range the mobile editors allow; Premiere's default transition length is 1 s, too slow for a
9 s reel):

- **push-in**: scale 1 → 1.45 about the doll's alpha-weighted centre, on t² (accelerating, the camera
  starting to move); the hand leaves the top of the frame, the doll grows;
- **zoom blur**: the mean of 8 copies of the frame scaled between s and s·(1 + 0.18 t): radial streaks
  from the doll outward that grow with the speed, the blur a stand-in for the motion blur a real dolly
  would produce at that speed;
- **dip to black**: a smoothstep from t = 0.5 to 1 multiplies the frame to zero; the last of the shot is
  the boots' red glow fading;
- **the incoming half** is the sting itself: its ground is now `#000000` for this video (the `ground=`
  option of `render_brand_sting.py`; the brand main `#231F20` would step up from the shot's black), and
  its first beat is five strings dropping from the top, the same motif the shot ends on, so the sting
  reads as the continuation.

Judged on `hand/work/prev_r5_sheet.png` (frames 248, 252, 256, 260, 263, 266) and the export's flicker
gate (the outro frames are large frame-to-frame changes by design; the gate's report on 249–266 is
expected).

## Sources (search summaries; the underlying pages are commercial guides, see DOWNLOADS.md item 13)

- CapCut, "How to do Zoom Transition in Premiere Pro: Total Guide": https://www.capcut.com/resource/zoom-transition-in-premiere-pro
- capeditcut.com, "Pull In and Pull Out transitions in CapCut, guide": https://www.capeditcut.com/pull-in-and-pull-out-transitions-in-capcut-guide/ (the host did not resolve on 2026-09-12; the description comes from the search result's summary)
- capeditcut.com community, "CapCut PC transition bug" (Pull In locked at 0.1 s on PC): https://www.capeditcut.com/community/capcut/capcut-pc-transition-bug/
- Film Impact, "Zoom Blur Impacts": https://www.filmimpact.com/premiere-pro-transitions/lights-and-blurs/zoom-blur-impacts
- Adobe community, "Dip to Black transition": https://community.adobe.com/questions-725/dip-to-black-transition-1324801
- Later, "Top Instagram Reels Trends to Try in 2026": https://later.com/blog/instagram-reels-trends/
- New Engen, "Instagram Trends: September 2026": https://newengen.com/insights/instagram-trends/
