# Reel virality notes for pull-up video #3 (2026-09-08)

Scope: what makes fitness form-analysis Reels perform, for a follow-up to the 140k-view
skeleton-tracking/heat-map pull-up Reel (55 s) and its 19.7 s USMC-standard cut. Read
`references/instagram-reels-format.md` first (safe zones, text sizing — not repeated here).
Method: WebSearch + a handful of WebFetch pulls this session (2026-09-08). No account was
logged into; nothing here came from Meta's internal Creator Portal.

**Confidence warning, read before trusting any bullet below:** almost every "Instagram
algorithm 2026" hit is a creator-tool marketing blog (Buffer, Hootsuite, dataslayer.ai,
creatorflow.so, socialpilot, dozens more) restating the same handful of claims from each
other, not from Instagram directly. Where a claim traces only to that blog-echo-chamber it
is marked **(blog consensus, primary source not independently confirmed this session)**.
Two things this session *did* reach closer to primary: an actual about.instagram.com post,
and a named creator-economy podcast (Colin and Samir) where Mosseri is a recurring guest.
Nothing below is invented — where a specific account/video name could not be verified it is
either omitted or flagged **unverified**.

## 1. Reels ranking signals (Instagram / Mosseri statements)

- **Official Instagram source (primary, confirmed by direct fetch):** about.instagram.com's
  "Control Your Instagram Reels Algorithm" / "Your Algorithm" post — announced 2025-12-10,
  expanded to Explore 2026-04-15, rolled out globally to Feed/Reels/Explore 2026-06-10. It
  describes a user-facing "why am I seeing this" / topic-steering control layer, not the
  ranking weights themselves — it does **not** mention watch time, sends, or likes by name.
  (about.instagram.com/blog/announcements/reels-algorithm-control)
- **Sends per reach as the top unconnected-reach signal**: repeatedly attributed to Mosseri
  in an appearance on *The Colin and Samir Show* (a real, recurring podcast slot for him),
  cited as "send rates matter more for reach than watch time, likes, and comments" — reported
  secondhand by multiple marketing blogs, e.g. smk.co ("Instagram Chief Confirms Sends Drive
  Algorithm Rankings"). The 3–5x "one send ≈ 3-5 likes" figure is a blog estimate layered on
  top of that, not a Mosseri number **(blog consensus)**.
- **Watch time / total watch time + replay rate** is the most consistently repeated #1
  signal across every source found, said to have displaced a pure "3-second view" count as
  the headline metric **(blog consensus, widely repeated, no single primary citation with a
  date pinned down this session)**.
- **Likes weighted more for connected (follower) reach; sends weighted more for unconnected
  (stranger/Explore) reach** — repeated consistently enough across independent blogs that it
  is likely a real distinction Mosseri has drawn, but no exact quote+date was retrieved
  **(blog consensus)**.
- **Skip rate** (percentage who exit within the first 3 seconds) is described as a newer
  ranking input and is also the metric now surfaced to creators directly — see retention
  section below.
- **Originality / no watermarks**: reposted, watermarked, or near-duplicate content is
  described as demoted; multiple sources agree Instagram rewards "original, niche-consistent"
  content **(blog consensus)** — directly relevant since your Reel is original tracking
  overlay work, not a repost.
- **Trial Reels** — this one is well corroborated across many independent creator-tool blogs
  describing the same mechanic consistently, and matches a real Meta feature name: launched
  December 2024, available to public accounts with 1,000+ followers, the Reel is shown only
  to non-followers first (not on your grid/followers' feeds), Instagram can auto-promote it
  to your followers if it performs well, and after ~24h you get view/like/comment/share
  numbers to decide whether to publish normally. Useful for A/B-testing a hook or cut before
  committing it to your grid.
- **Reels length ceiling and discovery cutoff**: technical upload ceiling reported at up to
  15–20 minutes for eligible accounts in 2026, but **Reels over 3 minutes are described as
  opting out of non-follower discovery** (Explore/Reels tab push) — repeated across sources
  as a hard behavioral cutoff, not just a soft preference **(blog consensus, not confirmed
  against an Instagram primary source this session)**.
- **Length vs. engagement data** — the one dataset with an actual named publisher and stated
  sample: Socialinsider, "6M Instagram Reels from brands with an active presence, Jan–Jun
  2026" (fetched directly this session, socialinsider.io/blog/instagram-reels-length):

  | Length bracket | Engagement rate | Median views |
  |---|---|---|
  | 0–30 s | 0.28% | 4,700 |
  | 30–45 s | 0.30% | 8,564 |
  | 45–60 s | **0.35% (highest)** | **10,374 (highest)** |
  | 60–90 s | 0.30% | 9,790 |
  | 90–120 s | 0.30% | 8,000 |
  | 120–180 s | 0.33% | 9,000 |
  | 180+ s | 0.15% | 4,428 |

  Note: this sample is brand accounts, not solo creators, and Socialinsider's own
  methodology (attribution model, what counts as "engagement") was not independently
  re-derived — treat the shape (45–60 s and 120–180 s are two local peaks, 180+ s falls off a
  cliff) as more trustworthy than the exact decimal engagement-rate values.

## 2. Hook conventions

- **The scroll decision happens fast**: one source states users decide continue-or-scroll
  within ~1.7 seconds; the more broadly repeated number is the first 3 seconds
  **(blog consensus for both; the 1.7s figure appeared in a single source this session and
  should be treated as an unverified specific number, not a confirmed industry figure)**.
- **Up to 50% of viewers reportedly drop off in the first 3 seconds** on an unremarkable
  open — repeated across multiple retention-focused blog posts **(blog consensus)**.
- One source claims "pattern interrupt" hooks average 72–84% 3-second retention vs. 65–78%
  for "curiosity gap" hooks vs. under 40% for a weak hook — **this specific percentage
  breakdown could not be traced to a named study or dataset and should be treated as
  unverified marketing-copy precision, not measured data.**
- **Text hook matters because most viewing is muted**: consistently cited that 70–80%+ of
  Reels are watched without sound, so the on-screen text in the first 1–3 seconds has to
  carry the hook independent of narration **(blog consensus, directionally very plausible
  and consistent with why your muscle-heat-map/skeleton overlay already reads without
  sound)**.
- **Cold-open on the payoff** (show the result/verdict first, then rewind to the mechanism)
  is standard short-form advice everywhere but was not found tied to a specific fitness/pose-
  estimation dataset this session — treat as **opinion, well-supported by general short-form
  practice**.
- **Ending on a loop** (last frame flows into first frame) is universally recommended
  because watch time now explicitly includes replays — a seamless loop converts a rewatch
  into more counted watch time. Directly actionable for a rep-counter format: end on the same
  framing/pose the video opened on.

## 3. Viral "AI analyzes my form" / pose-estimation / muscle-map content

- **Named professional-grade tools** actually built for this (verified as real, currently
  marketed products, not verified as "went viral" specifically):
  - **OnForm** — skeleton/joint-angle overlay on video replay, slow-motion, side-by-side and
    overlay comparison, voice-over annotation; ~$499/yr tier reported; recently reported to
    have acquired Hudl Technique.
  - **Ochy** — AI running/gait-analysis app, phone-camera posture tracking.
  - **Kinovea** — free, open-source, long-standing manual/semi-automated biomechanics
    video-annotation tool (angle measurement, tracking); widely used by coaches, predates the
    AI-hype cycle.
  - **Sportsbox AI** and **Uplift** were searched for directly this session; no substantive,
    independently-confirmed detail on either came back — **not enough was found to describe
    what they do with confidence; do not treat prior assumptions about them as verified.**
- **"Muscle activation" 3D-anatomy-render style videos** (a 3D animated body with muscles
  lighting up red as they fire, exercise labelled, rep-counted) are described by search
  results as an active, popular TikTok fitness-education subgenre; two account names surfaced
  in search snippets — **SynerMuscle** and **Easy Anatomy** — but neither was independently
  visited/verified this session, so treat both as **unverified leads, not confirmed accounts**
  before citing them anywhere public.
- **A "skeleton overlay" trend** was reported by one blog (vuela.ai) as starting on TikTok
  with an account given as "@theoretico5" around early March 2026 and spreading to Shorts and
  Reels — **this is a single-source claim from a marketing blog and could not be
  cross-verified this session; treat the account name and date as unverified, not fact.**
- **What comments criticize, per general (not video-specific) search results**: the
  recurring friction points in fitness-form-check content are (a) whether a rep "counted"
  under a stricter or looser range-of-motion definition, (b) kipping vs. strict/dead-hang as
  fundamentally different movements being compared unfairly, and (c) skepticism of AI/pose-
  estimation accuracy itself (occlusion, camera angle, "the app doesn't know your actual
  joint angle"). This matches general fitness-content-debate patterns rather than a specific
  quoted comment thread on a specific viral video — **no specific comment text is quoted here
  because none was found and verified this session.**
- Nothing found this session confirms or denies that a "muscle heat map" visualization format
  matching your video's specific style (a heat-map-colored overlay directly on the tracked
  body, vs. a separate 3D anatomical figure) has its own named viral precedent — the closest
  verified adjacent formats are the skeleton-overlay trend and the 3D-anatomy-render genre
  above, both distinct from a direct on-body heat map. This may mean the format is
  differentiated rather than derivative — noted as **opinion**, not evidence of novelty.

## 4. Pull-up niche: what's viral and why

- **Guinness World Records, both independently verifiable and dated:**
  - Heaviest weighted pull-up (male): **Liu Weiqiang, 146.64 kg (323.28 lb), Zhangjiakou,
    Hebei, China, 2025-02-01** — beat his own prior record by ~40 kg (guinnessworldrecords.com).
  - Most pull-ups in 24 hours: **Oh Yohan (South Korea), 11,707 pull-ups, Incheon** — reported
    across multiple sources as having gone viral; exact 2025/2026 date not independently
    re-confirmed this session.
  - A TikTok claim of Andrei Smaev doing a +171 kg weighted pull-up at 130 kg bodyweight
    ("300 kg total") surfaced in search results — **not Guinness-verified, treat as an
    unverified TikTok/creator claim, not a record.**
- **Dead-hang challenge**: a "hang from a bar for 100 seconds straight" dead-hang challenge is
  described as having spread across social media — corroborates that bar-hang content travels
  even without reps involved, relevant background for why a chin-over-bar/ROM debate draws
  engagement (it's litigating what "counts," which is inherently comment-bait).
- **Kipping vs. dead-hang/strict is a live, ongoing fitness-community debate** (not proven to
  be Reel-specific, but the underlying tension is well documented): the core argument is
  whether kipping "is a different exercise that happens to get your chin over the bar" rather
  than a lesser version of a strict pull-up, and that neither is "wrong" outside its own
  stated goal (rep count under fatigue vs. maximal strength). This maps directly onto likely
  comment fodder for a USMC-standard video, since the USMC standard is explicitly a
  **dead-hang, chin-over-bar, controlled** standard — a stricter definition than many casual
  gym pull-ups, which is exactly the kind of gap that generates "well ACTUALLY" comments.
- **No specific named 2025–2026 viral pull-up Reel/TikTok (creator handle + video) could be
  confirmed this session** beyond the two Guinness records above. Searches for "are your
  pull-ups legal," chin-over-bar debate Reels, and "half rep"/"quarter rep" argument threads
  returned only general fitness-advice content, not a traceable specific viral post — **this
  is a gap, not a claim that no such videos exist.**

## 5. Practical recommendations with sourcing

- **Length**: 45–60 s tracks the best engagement-rate and median-views bracket in the
  Socialinsider 6M-Reels sample above; 120–180 s is a secondary peak; anything past 180 s
  drops sharply *and* (per the separate discovery-cutoff claim above) may stop being pushed
  to non-followers at all. Your 55 s original sits exactly in the top bracket; the 19.7 s cut
  sits in the lowest-performing bracket by this dataset, though it may still work as a
  hook-heavy teaser/trailer format that data of this shape wasn't designed to measure.
- **Music**: using a "Trending" audio (tappable in the Reels composer under the music icon,
  or via Professional Dashboard → Tips and resources → Trending audio) is described as
  boosting Explore-page surfacing because Instagram treats audio choice itself as a ranking
  signal and gives the Reel a shot at that sound's own audio page; original/self-made audio
  is described as giving you sole ownership of that audio page instead. Only use audio
  labeled "Original audio" or explicitly commercial-cleared if monetization/brand use is a
  concern **(blog consensus on mechanism; consistent enough across sources to act on)**.
- **On-screen text**: matches your existing `references/instagram-reels-format.md` sizing
  guidance (60–75 px optimal, don't go under 48 px) — nothing new found that contradicts it;
  additionally, cover-frame text specifically is recommended at 3–5 words, 48–60 pt, centered
  in the safe 1080×1080 square so it survives the 4:5/3:4 crops.
- **Cover frame**: pick a manually-set frame (don't let Instagram auto-select — auto-select
  risks a mid-motion blur), keep the focal subject and any text inside the central 1080×1080
  square, high contrast since covers shrink to grid-tile size.
- **Caption first line**: no source gave a fitness-specific first-line formula; general
  short-form advice (repeated, not fitness-specific) is that the first line should work
  as its own hook since Instagram truncates captions in-feed — **opinion, not
  fitness-content-specific data.**
- **Hashtags**: confirmed consistent with your CLAUDE.md note — Instagram rolled out a
  **hard 5-hashtag cap starting December 2025**, and current guidance converges on 3–5
  highly relevant tags rather than a long list; several sources note Reels specifically may
  benefit from using the full 5 (vs. fewer for static posts) given broader distribution
  surface. `#Fable` stays per your existing rule when the model is credited.
- **Crediting the AI model/tool in the caption**: no fitness-Reel-specific data found on
  whether naming the tool (MediaPipe, YOLOv8, "tracked with machine learning," etc.) helps or
  hurts views. The only related research surfaced was a *Journal of Consumer Research* paper
  finding that AI-disclosure framing has a measurable, non-trivial effect on "like" likelihood
  (an interaction between platform-level and self-disclosure framing) — but that study is
  about AI-generated *images/content* being labeled as such, not about a creator naming a
  legitimate analysis tool used on real footage, so it's only loosely analogous. Net: **no
  usable data either way; treat "credit the model" as a style/trust choice, not a growth
  lever, per this session's research.**

## 6. Retention curve data for 15–60 s Reels

- Instagram shipped a dedicated **Retention chart** inside Reels Insights in 2025 (reported
  around August 2025 by storyy.com) that visualizes drop-off during playback, plus a
  **Skip Rate** metric specifically measuring exits within the first 3 seconds — meaning
  creators can now pull their own actual retention curve per-video rather than relying on
  aggregate claims. Recommend checking this in-app for the 140k-view video directly; it will
  beat any external benchmark below.
- Aggregate claims found this session (all **blog consensus, no underlying dataset named or
  inspected**):
  - Up to ~50% drop-off within the first 3 seconds is commonly cited as typical for an
    unremarkable open.
  - A retention curve is described as falling sharply in the first 1–2 s, then flattening
    once the remaining audience has committed, then tailing off toward the end.
  - For 15–30 s content, retention is described as commonly dropping to a 40–60% range by
    the end.
  - For anything over ~45 s, retention "rarely" stays above 30% "unless exceptionally
    compelling" — no threshold definition of "compelling" was given, and no source tied this
    specifically to educational/technical (vs. entertainment) content.
- **No public, source-named second-by-second retention curve specific to fitness/technical
  form-analysis content was found this session.** The general shape above (steep early drop,
  flatten, tail off) is standard across all short-form video and not fitness-specific;
  treat it as a shape prior, not a number to design exact cut points against.

## Concrete recommendations for pull-up video #3

1. Keep the primary cut in the 45–60 s band — it is the single best-attested bracket in the
   Socialinsider 6M-Reels sample (§1, §5); treat the 19.7 s length as a secondary
   teaser/trailer cut, not the version you expect to carry reach.
2. Put the verdict/payoff (pass/fail against the named standard, or the single most
   striking number) in the first 3 seconds as on-screen text, since roughly half of viewers
   are reported to drop off in that window and most watch muted (§2, §6) — cold open on the
   result, then show the mechanism.
3. End the cut on a frame/pose that visually continues into the opening frame so a rewatch
   reads as a loop — watch time (the most repeated #1 ranking signal, §1) explicitly counts
   replays.
4. Set the cover frame manually to a clear, high-contrast moment of the overlay in action
   (skeleton or heat map clearly visible on the body), subject and any text centered in the
   1080×1080 safe square (§5).
5. Use "Original audio" or a Trending-labeled, commercially-clear sound rather than an
   unlabeled trending song, since audio choice is described as its own ranking input and you
   don't want a licensing flag on a Reel you want pushed to strangers (§5) — opinion-backed
   (unverified music-licensing enforcement specifics), but low-cost to follow.
6. Keep hashtags at exactly 5, one line, matching your existing CLAUDE.md rule — this is now
   a platform-enforced cap (December 2025), not just best practice (§1, §5).
7. Consider posting the technical/USMC-standard cut as a **Trial Reel** first (needs
   1,000+ followers, confirm eligibility) to get a stranger-only performance read within 24h
   before deciding which cut becomes your main grid post (§1) — this directly answers "which
   length wins" with your own audience instead of a brand-account dataset.
8. Lean into the ROM/chin-over-bar strictness angle in the caption or on-screen text
   deliberately, since the kipping-vs-strict and "does this rep count" debate is a genuine,
   recurring fitness-community friction point (§4) likely to drive comments — opinion, but
   grounded in a real, well-documented debate rather than invented.
9. Do not over-invest in a specific "credit the AI model" caption strategy expecting a growth
   effect — no fitness-Reel-specific evidence either way was found this session (§5); pick
   the phrasing that's honest and move on rather than treating it as a lever.
10. Pull the in-app Retention chart and Skip Rate for the existing 140k-view Reel before
    cutting video #3 — it is first-party, video-specific data you already have access to and
    will beat every external benchmark cited in §6.

## Sources

- https://about.instagram.com/blog/announcements/reels-algorithm-control
- https://www.socialinsider.io/blog/instagram-reels-length/
- https://smk.co/instagram-chief-confirms-sends-drive-algorithm-rankings/
- https://buffer.com/resources/instagram-algorithms/
- https://blog.hootsuite.com/instagram-algorithm/
- https://metricool.com/instagram-trial-reels/
- https://later.com/blog/ultimate-guide-to-using-instagram-hashtags/
- https://www.guinnessworldrecords.com/world-records/heaviest-weighted-pull-up
- https://physicalliving.com/kipping-pullups-vs-deadhang-pullups-where-do-we-draw-the-line-between-strict-deadhang-pullups-and-kipping-pullups/
- https://bullbarfit.com/blogs/updates/the-kipping-paradox-why-crossfits-most-controversial-pull-up-might-actually-be-misunderstood
- https://academic.oup.com/jcr/advance-article/doi/10.1093/jcr/ucag013/8672493
- https://storyy.com/2025/08/24/instagram-adds-retention-metrics-for-reels-creators/
- https://vuela.ai/blog/ai-skeleton-exercise-videos (single-source, unverified account/date claim — see §3)
- https://www.infoq.com/articles/human-pose-estimation-ai-powered-fitness-apps/
- https://www.ochy.io/
