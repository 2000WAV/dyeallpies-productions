# Reel virality notes for the hand/CG-marionette video (item 7, 2026-09-11)

Scope: viral-mechanics research for the 9-second tattooed-hand / neon CG-marionette Reel —
hand closes into a fist, opens, a glowing five-string marionette tumbles out and is
puppeteered for ~7s, fist closes, ~1s logo sting + a hold on the GitHub URL. Method:
WebSearch + WebFetch this session (2026-09-11), plus `curl -sS -L -A "Mozilla/5.0"` saves
(the Python certificate store on this box is expired, per `machine-local`). Every saved page
is listed in `virality/SOURCES.md`; the download log is `downloads-07.md`.
`references/pushup-science/05-reel-virality-pushup.md` was read (read-only, not edited) for
house conventions on confidence labelling — it already established that most
"algorithm"/skip-rate numbers found by any agent are creator-analytics blog consensus, not
named platform datasets, and that convention is carried forward here: every specific number
is labelled **(blog consensus)** unless it traces to an official platform page or a
peer-reviewed source, and **NOT FOUND** is used rather than guessing where nothing surfaced.

## 1. How hand-based VFX/"AR magic" shorts actually perform

- **Zach King, "Zach Kings Magic Broomstick"** (posted 2019-12-09): reached **2.2 billion
  views on TikTok**, confirmed as the most-viewed TikTok video by Guinness World Records as
  of 2022-03-15 (`virality/guinness-zachking.html`, official Guinness page, directly read).
  King's whole format — "digital sleight of hand," a practical action that resolves into an
  impossible compositing payoff — is the closest verified, dated, numbered precedent for
  "a hand does something ordinary, then something impossible happens." It is **not** a
  hand-tracked-CG-puppet-on-strings precedent specifically.
- **NOT FOUND**: no independently verifiable, dated, numbered example of a hand-tracked CG
  puppet/marionette/creature emerging from a closed fist was located this session. Searches
  for "hand tracking AR filter creature," "CGI creature emerges from palm," "glowing spell
  hand CGI viral," and a specific VFX-artist lead (`@sybervisions_`, surfaced via WebSearch
  as a ~1.2M-follower TikTok "AI filmmaker" doing POV VFX) all either returned generic
  TikTok discovery pages, unrelated content, or — for `@sybervisions_` — a JS loading shell
  on direct fetch with no video or view count that could be independently tied to the
  creator (see `virality/SOURCES.md`). This is a real gap: there is no confirmed direct
  precedent for or against this specific format, the same shape of gap the pull-up and
  push-up sessions already flagged for their own formats (muscle heat map, EMG overlay).
- **Instagram's own official guidance material with static, fetchable hook-specific numbers
  could not be located this session** — every "Instagram Reels best practices" result was a
  third-party marketing blog (quso.ai, cloudcampaign.com, brandghost.ai, and similar); a
  direct fetch of the Instagram Help Center reel-size page returned a client-rendered shell
  with no static text (`virality/instagram-help-hashtag-clientrendered.html`, same limitation
  already logged for a different Instagram Help Center page in `downloads-08.md`). The one
  **official, primary** Instagram-owned source that did yield real static content this
  session is the @creators Threads hashtag post (§3 below) — it is not about hooks, but it
  confirms Instagram does publish binding creator guidance through that channel.
- **YouTube's own official guidance**, by contrast, did yield real content:
  `virality/youtube-shorts-help.html` (support.google.com/youtube/answer/10059070, official)
  confirms YouTube's in-app "Get feedback" tool on a Short returns "an analysis of your
  video's hook, pacing, and more" — i.e., YouTube's own tooling treats "hook" as a named,
  measured property, not just a creator-blog concept.
- **Blog-consensus retention numbers** (repeating the same caveat as the push-up/pull-up
  sessions, not independently verified against a named platform dataset): skip rate under
  ~20% in the first 3 seconds is treated as a healthy hook, 20–35% typical, over ~40% weak
  (carried over from `05-reel-virality-pushup.md`, not re-verified this session).
  `virality/creatorhouse-hookrate.html` (CreatorHouse blog) independently states Instagram
  reach gets capped below a **~50% hook rate** (3-second plays ÷ impressions) and frames the
  swipe decision as happening in **"the first 1.5 seconds"** — a tighter number than the
  "1.7-second scroll decision" figure the push-up session flagged as unverified-Meta-research;
  neither figure traces to a named Instagram dataset, both are **(blog consensus)**.

## 2. Is a 1.4s reveal early enough, or should the video open ON the drop and loop back?

- Every source found this session — the two saved editing/structure blogs and the pull-up/
  push-up sessions' carried-over findings — converges on the same shape of advice: **move the
  payoff toward the front, not the back.** `virality/socialync-structure.html` states the
  hook's job is to have "something visually interesting...on screen before you say a word,"
  and frames a "cold-open"/payoff-first structure as one of a handful of reliable patterns —
  consistent with, not contradicting, the push-up session's same finding.
- Against the **1.5-second swipe-decision window** reported by `creatorhouse-hookrate.html`
  (blog consensus, not platform-confirmed), a reveal at **1.4 seconds** is inside that window
  by only a tenth of a second — i.e., on the numbers this one blog gives, the fist-open/
  marionette-tumble payoff would land essentially at the edge of, not comfortably before, the
  point some fraction of viewers have already decided to swipe. This is not a controlled
  finding that 1.4s is too late — no source measured this specific reveal-timing question —
  but it is close enough to the reported decision window that opening a beat or two earlier,
  or moving some sign of motion (the fist itself starting to flex, or a first glint of neon
  light at the knuckles) into frame 1, costs nothing and buys margin against a number this
  session cannot verify precisely.
- **Loop-back structure**: `virality/socialync-structure.html` names this explicitly — "The
  payoff connects back to the opening, creating a satisfying circle that encourages
  rewatches" — as a named pattern ("The Loop Back"), separate from and complementary to
  "open on the payoff." For this video, the fist closing again at the end (mirroring the fist
  at the start) already gives a natural loop point *before* the logo sting; whether to also
  make the visual loop seamless (last frame ≈ first frame, no sting in between on the looped
  cut) is a real trade-off against wanting the branded outro to play at least once per view.
- **Does a seamless loop measurably raise replays — yes, mechanically, via view-counting
  policy, not via a measured retention study.** `virality/youtube-shorts-help.html` (official
  YouTube Help, directly read) states that as of **2025-03-31**, YouTube counts every time a
  Short "starts to play or replay, with no minimum watch time requirement" as a view — the
  older continued-watching metric was renamed "Engaged views" and is what YPP/ad-revenue
  eligibility is actually based on. `virality/virvid-loop.html` (a second, independent
  source) states the same date and mechanism ("YouTube counts every loop and replay as an
  additional view, making seamless loops directly inflate your view count and algorithmic
  signals simultaneously") and adds that YouTube's own documentation acknowledges "the
  absolute views for a segment can exceed your video's overall view count" when viewers
  rewatch a portion. **Net: a seamless loop provably inflates the raw view count on YouTube
  Shorts by policy since 2025-03-31; no source found this session measured whether a loop
  raises actual audience retention/completion as opposed to the view-count mechanic itself**
  — flag that distinction rather than conflating "more views counted" with "more people
  watched longer."
- No equivalent official Instagram statement on how replays are counted was found this
  session (**NOT FOUND**); Instagram-specific loop claims are blog consensus only.

## 3. Caption style, hashtags, AI/tool credit, and the branded end-sting

- **Instagram's 5-hashtag limit is confirmed from an official, primary source.**
  `virality/instagram-creators-hashtag-threads.html` — Instagram's own @creators account on
  Threads — states verbatim: "New hashtag guidance: Starting today, Instagram will allow up
  to 5 hashtags in a reel or post." This matches the CLAUDE.md house rule already in force
  ("At most 5 hashtags"). The post is reported by search-result metadata as dated
  2025-12-18; that date is not independently confirmed inside the saved page itself, but the
  5-tag figure is directly confirmed text, not a paraphrase.
- **Caption style for a VFX reel**: no source found this session studied caption wording for
  VFX/illusion content specifically (**NOT FOUND**). The general hook-body-payoff structure
  in `virality/socialync-structure.html` still applies to on-screen text/caption framing —
  lead with the visual promise ("a hand. a fist. then this.") rather than an explanation of
  method, consistent with the same "don't explain the trick, show it" instinct that made
  Zach King's format work without narration.
- **Crediting the tool/AI: found peer-reviewed evidence this disclosure has a real,
  measurable, negative effect on engagement — though the underlying page could not be
  archived.** Carney, Riveros & Tully (2026 forthcoming), "Made With AI," *Journal of
  Consumer Research*, DOI 10.1093/jcr/ucag013 (read once via WebFetch; a `curl` save was
  blocked by a Cloudflare interstitial, see `virality/SOURCES.md` — **peer-reviewed venue,
  not independently re-verified against a saved copy**): an archival study of **1,135,817
  TikTok posts from 8,650 creators** found AI-disclosed posts got **roughly 7–8% fewer
  likes** and 7% less combined engagement, controlling for views, across creator sizes; a
  290-participant controlled experiment found a marginal reduction (Cohen's d=.21) rising to
  **d=.45** among participants who actually noticed the disclosure; a 385-participant
  follow-up traced the mechanism to disclosure reducing *perceived creator effort*, which
  reduces parasocial connection, which reduces engagement — not to AI aversion or quality
  concerns per se. **Applied here**: this video already credits "DyeAllPies Productions" as
  the maker via the end sting, not "made with AI"/tool-name in the caption — the paper's
  finding argues specifically against adding a software/AI-tool credit line to the caption,
  since it would cost measurable engagement for no requirement this project is otherwise
  bound by (Instagram/TikTok AI-disclosure requirements target realistic synthetic
  media/deepfake-adjacent content, not stylized neon CG puppetry, per general
  industry-guidance pages surveyed via WebSearch — not saved, background reading only).
- **Does a 1–2.5s branded end-sting hurt completion? Say honestly what exists: no source
  measured this directly (NOT FOUND).** The one directly relevant number found is
  `virality/socialync-structure.html`'s claim that a viewer allows "about 1-2 seconds after
  the payoff before...scroll[ing]" — i.e., *some* post-payoff runway exists before a typical
  viewer leaves, on this one blog's framing. A sting of "about 1s of animation plus a hold
  for the GitHub URL" sits at or just past the edge of that reported runway depending on how
  long the URL hold runs; there is no measured completion-rate cost quoted anywhere, and no
  source distinguishes a *branded* outro from any other post-payoff content in its effect on
  completion. This is the same gap `references/marionette/08-brand-sting.md` already
  documents from the branding-research side (that file's own scope note); this file does not
  repeat 08's citations, only flags that the virality-side search this session did not close
  the gap either.

## 4. Music sync: should the drop land on a beat?

- `virality/beverlyboy-beatdrop.html` (Beverly Boy Productions, a working production-company
  blog — industry-practice source, not a controlled study) states the convention plainly:
  "By aligning the beat drop with a plot twist, an explosive action beat, or a revealing
  shot, editors can make these moments truly unforgettable," and "When you synchronize a beat
  drop with a cut, transition, or dramatic movement, you fuse sound and imagery into a
  unified moment of impact." Applied here: the fist-opening/marionette-tumble reveal is
  exactly the kind of "revealing shot" this convention says a beat drop should land on.
- Caveat, stated plainly because it matters for this project's actual workflow: **the song is
  added after the real-time recording**, per the brief. That means the reveal's timing is
  fixed by the physical performance, and the editor's job is choosing/nudging a track so its
  drop lands on the *already-shot* reveal frame (trimming song-in point, or minor speed
  ramping of the edit if the puppeteering section has slack) — not the reverse. No source
  found this session addresses that specific "picture-locked, audio added after" workflow
  directly (**NOT FOUND** for that exact scenario); the general convention above is the
  closest applicable guidance, and it argues for spending edit time finding/trimming a track
  whose drop aligns with the existing 1.4s cut rather than treating the drop's placement as
  fixed and cutting picture to match it.

## Recommendations

1. **Hook**: keep visible motion in frame 1 — the fist itself should already be mid-flex or
   show a first hint of neon light at 0.0s, not a static plain-wall shot before anything
   moves. Basis: the 1.5s swipe-decision figure in `creatorhouse-hookrate.html` (blog
   consensus) and the "something visually interesting on screen before you say a word" rule
   in `socialync-structure.html`.
2. **Opening frame / reveal timing**: the planned 1.4s reveal is close to, not comfortably
   ahead of, the reported 1.5s decision window (blog consensus, unverified against a named
   platform dataset) — if the edit has any slack, pull the first visible glow earlier than
   1.4s rather than later; do not push it back.
3. **Loop**: make the fist-closes-at-the-end frame visually rhyme with the fist-closes-at-
   the-start opening frame (same hand position/framing) so the cut back to a rewatch feels
   intentional — named "Loop Back" pattern in `socialync-structure.html`. On YouTube
   specifically this also mechanically raises the counted view total, since every replay has
   counted as a new Short view since 2025-03-31 (`youtube-shorts-help.html`,
   `virvid-loop.html`) — real for the view-count metric, not a proven retention effect.
4. **Caption skeleton**: lead with the visual promise, not an explanation — one line stating
   what's about to happen visually (fist → puppet), no method/tool explanation, blank line,
   then the hashtag line. Basis: `socialync-structure.html`'s hook-body-payoff template and
   the general "don't explain the trick" pattern behind Zach King's format
   (`guinness-zachking.html`).
5. **Hashtags**: 5 maximum, one line at the end — confirmed by Instagram's own @creators
   account, not a blog (`instagram-creators-hashtag-threads.html`); matches the existing
   CLAUDE.md rule, so no change needed, just confirmation it is current as of this session.
6. **Tool/AI credit**: do not add a "made with AI"/software-credit line to the caption text.
   Basis: Carney, Riveros & Tully (2026), ~7-8% fewer likes on disclosed posts in a
   1.1M-post archival study, rising to d=.45 among viewers who notice the disclosure — read
   via WebFetch, not independently re-saved (flagged accordingly). The "DyeAllPies
   Productions" end-sting is a brand credit, not an AI-tool disclosure, and is not the same
   category the paper studied.
7. **End sting length**: keep the sting at the brief's own ~1s animation, and keep the
   GitHub-URL hold short — no source this session quantified a safe maximum, but
   `socialync-structure.html`'s "1-2 seconds after the payoff" runway figure (blog consensus)
   is the only number found that bears on it at all, and it argues against letting the URL
   hold run long. This is the same open question `08-brand-sting.md` already flags from the
   branding side; nothing found here closes it either — treat any total post-payoff runtime
   past ~2s as untested, not pre-approved.
8. **Music sync**: since audio is added after the real-time recording, treat the picture as
   locked and choose/trim the track so its drop lands on the existing ~1.4s reveal cut,
   rather than editing the reveal to match a track chosen first. Basis:
   `beverlyboy-beatdrop.html`'s convention that beat drops are placed on reveals/reversals;
   no source addressed the "audio added after" ordering directly, so this is the general
   convention applied to this project's actual workflow, not a study of that workflow.
