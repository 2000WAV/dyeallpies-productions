# Instagram Reels format reference (researched 2026-08-24)

Used by the phonetics-video skill to lay out the Reels export. Re-verify yearly — UI
chrome changes.

## Canvas

- **1080 × 1920 px, 9:16, 30 fps** is the standard Reels canvas.
- Feed preview crops to 4:5 and profile grid to 3:4 — the truly critical content should
  survive a center crop too.

## Safe zone (avoid Instagram UI chrome)

Consensus across 2026 guides (sources below; numbers vary a little between them — these
are the conservative picks we use):

| Edge | Avoid | Why |
|---|---|---|
| Top | **220 px** | username, camera icon, "Reels" header |
| Bottom | **420 px** | caption, audio row, action bar |
| Right | **144 px** | like/comment/share/save button stack |
| Left | **60 px** | breathing room, feed-crop tolerance |

→ usable content box: x 60–936 (876 wide), y 220–1500 (1280 tall).

## Text / caption sizing (at 1080 × 1920)

- Optimal caption size: **60–75 px** (~3.1–3.9 % of frame height).
- Minimum readable: ~**44–48 px**; below 48 px muted-audio viewers stop reading.
- Body/secondary text floor: ~28 px, but avoid <45 px for anything that must be read.
- Above ~100 px text starts blocking the video.
- Bold sans-serif, high contrast; avoid thin weights.

## Layout used by phonetics-video (compose_reels.py)

Dark #1a1a19 canvas 1080×1920:
- word + IPA subtitles: top of safe area (MarginV ≈ 230), word ~72 px, IPA ~56 px
- source video (portrait 480×848 scaled ~×0.83 → 396×700): centered in the safe box
- frequency panel 876×370: bottom of safe area, ends above y=1500

## Sources

- https://www.outfy.com/blog/instagram-safe-zone/
- https://campaignswift.com/blog/instagram-safe-zone-sizes
- https://kreatli.com/guides/instagram-reels-safe-zone
- https://www.trymypost.com/blog/instagram-reels-safe-zones-text-placement-2026
- https://blitzcutai.com/blog/best-caption-size-instagram-reels-2026
- https://www.itnavideo.com/blog/caption-font-size-guide-reels
- https://www.screensnap.pro/blog/instagram-reels-size-guide
