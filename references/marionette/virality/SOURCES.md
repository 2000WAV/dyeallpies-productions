# Saved sources — item 7, reel virality (2026-09-11)

Fetched 2026-09-11 with `curl -sS -L -A "Mozilla/5.0"` (the Python certificate store is
expired on this box, per `machine-local` skill). WebSearch/WebFetch used for discovery and
for two pages a raw save could not add anything to. Confidence labels follow the convention
set in `references/pushup-science/05-reel-virality-pushup.md`: most "algorithm" numbers below
are creator-analytics blog consensus, not platform-published data, and are labelled
**(blog consensus)** in the main file unless traced to an official platform page or a
peer-reviewed source.

## Saved (real content, confirmed with `file`/`grep`, not a JS shell or paywall page)

- **guinness-zachking.html** — Guinness World Records news page (2022-11),
  "Internet illusionist Zach King breaks record for most viewed video on TikTok."
  https://www.guinnessworldrecords.com/news/2022/11/internet-illusionist-zach-king-breaks-record-for-most-viewed-video-on-tiktok-724834
  Official Guinness page, all rights reserved. Confirms: "Zach Kings Magic Broomstick"
  (posted 2019-12-09) reached 2.2 billion TikTok views as of 2022-03-15, the record for
  most-viewed TikTok video. This is the one independently-verified, dated, numbered example
  found this session of a "digital sleight of hand" hand/object-illusion short going viral —
  not a hand-tracked-CG-puppet precedent specifically (no such video was found and verified,
  see the main file's **NOT FOUND**), but the closest confirmed real-world analog for "a
  practical-looking hand trick with a VFX payoff."
- **youtube-shorts-help.html** — YouTube Help, "Get started creating YouTube Shorts."
  https://support.google.com/youtube/answer/10059070
  Official Google/YouTube documentation. Confirms two facts used in the main file: (1) the
  in-app "Get feedback" button on a Short gives creators "an analysis of your video's hook,
  pacing, and more" — i.e. YouTube's own tooling treats "hook" as a named, measured property
  of a Short; (2) as of **2025-03-31**, "Shorts views" count every time a Short "starts to
  play or replay, with no minimum watch time requirement" — replays are counted as new views
  by policy — while the pre-existing continued-watching metric was renamed "Engaged views"
  and is what YPP eligibility/ad revenue are actually based on.
- **instagram-creators-hashtag-threads.html** — Instagram's own @creators account, Threads
  post. https://www.threads.com/@creators/post/DSalXGPCWM4/new-hashtag-guidance-starting-today-instagram-will-allow-up-to-hashtags-in-a
  Official Instagram-owned account (Threads, Meta), primary source. Verbatim text confirmed
  in the saved page: "New hashtag guidance: Starting today, Instagram will allow up to 5
  hashtags in a reel or post. Swipe to learn more." Search-result metadata (not confirmed
  inside the saved page itself) dates the post to **2025-12-18**; treat the date as
  reported-not-independently-verified, the 5-hashtag figure itself as directly confirmed.
- **creatorhouse-hookrate.html** — CreatorHouse blog, "Hook Rate, Hold Rate, Completion
  Rate: The 3 Reel Metrics That Predict Reach in 2026."
  https://creatorhouse.app/blog/instagram-reel-hook-rate-hold-rate-completion-rate-benchmarks
  Creator-analytics blog, **not** an Instagram/Meta publication — **(blog consensus)**.
  Used for: hook rate defined as 3-second-plays ÷ impressions; the claim that Instagram caps
  distribution below a ~50% hook rate; a stated "first 1.5 seconds" swipe-decision window
  ("If 60%+ of them swipe past in the first 1.5 seconds, the test fails").
- **virvid-loop.html** — Virvid.ai blog, "Looping Structure: The Hidden Retention Trick in
  Viral Shorts." https://virvid.ai/blog/looping-structure-shorts-retention-2026
  Creator-tool blog — **(blog consensus)**, but it independently states the same
  2025-03-31 YouTube replay-counting change as youtube-shorts-help.html above ("As of March
  31, 2025, YouTube counts every loop and replay as an additional view"), which corroborates
  that fact from a second source rather than only the primary one.
- **socialync-structure.html** — Socialync blog, "Short-Form Video Structure: Hook, Body,
  Payoff." https://www.socialync.io/blog/short-form-video-structure-guide-2026
  Creator-editing blog — **(blog consensus)**. Used for the hook-body-payoff template, the
  "Loop Back" pattern (ending reconnects to the opening frame to "encourage rewatches"), and
  the claim that a viewer allows "about 1-2 seconds after the payoff before...scroll[ing]" —
  relevant to how long a branded outro can run before it starts costing completions.
- **beverlyboy-beatdrop.html** — Beverly Boy Productions blog, "Music Cue Momentum: Beat
  Drops Guide the Edit."
  https://beverlyboy.com/film-technology/music-cue-momentum-beat-drops-guide-the-edit/
  Working production-company blog — **(blog consensus/industry practice, not a study)**.
  Used for the editing convention that a beat drop is conventionally placed on a reveal,
  reversal, or dramatic movement to fuse sound and image into "one unified moment of impact."

## Attempted, not saved as usable content

- **instagram-help-hashtag-clientrendered.html** — https://help.instagram.com/1038071743007909
  Instagram Help Center page on hashtags. Fetched (771 KB) but the static HTML has no
  hashtag-count text at all — this is a client-rendered (JS-hydrated) page, same limitation
  already logged for a different Instagram Help Center URL in
  `references/marionette/downloads-08.md`. Kept for the record; not usable as a citable
  source. The 5-hashtag figure is instead cited from the Instagram @creators Threads post
  above, which did return real static text.
- **Carney, S., Riveros, I., Tully, S.M. (2026 forthcoming), "Made With AI,"** *Journal of
  Consumer Research*, DOI 10.1093/jcr/ucag013.
  https://academic.oup.com/jcr/advance-article/doi/10.1093/jcr/ucag013/8672493
  `curl` returned a Cloudflare "Just a moment..." interstitial, not the article — could not
  be saved as a local file. The findings cited in the main file (archival TikTok study of
  1,135,817 posts; AI-disclosed posts get ~7-8% fewer likes; a 290-participant experiment,
  Cohen's d = .21 overall / .45 among those who noticed the disclosure; a 385-participant
  mediation study tying the effect to reduced perceived creator effort, not AI aversion) come
  from a single WebFetch pass over the live page before the block was hit, not from a saved
  file — flagged as **peer-reviewed venue, content read once via WebFetch, not independently
  re-verified against a saved copy.**
- **tiktok-sybervisions_ profile** — https://www.tiktok.com/@sybervisions_
  Returned a JS-only loading shell ("Please wait...") on `curl`; WebSearch's own summary
  (1.2M TikTok followers, "ultra-realistic, mysterious POV videos") could not be tied to any
  specific dated video or view count, so this creator is **not used** as a named example in
  the main file — flag as an unconfirmed lead only, not a citation.
- **Instagram Help Center, Reels size/safe-zone page** (`help.instagram.com/1038071743007909`,
  same page as above) and a general search for an official `business.instagram.com` Reels
  hook/best-practices page: no official Meta business-blog page with static, fetchable hook
  guidance was located this session; every "Instagram Reels best practices" result was a
  third-party marketing blog. This gap is carried into the main file rather than papered
  over with a blog citation dressed as official guidance.
