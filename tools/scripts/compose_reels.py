"""Compose the final Instagram-Reels phonetics video on a 1080x1920 canvas.

Usage: compose_reels.py <master_clean.mp4> <panels_dir> <subs.ass> <out.mp4> [cuts.json] [layout] [fps=30]

layout = "fullbleed" (DEFAULT — the speaker's preference since 2026-08-24) or "boxed".

fullbleed: the talking video fills the whole 1080x1920 frame (scaled to cover, center-
cropped the few px a phone portrait source is off from 9:16); subtitles, emoji, and the
frequency panel are overlaid ON TOP of the footage. Render the panel PNGs with a lower
background alpha (~200, 7th arg of render_freq_panel.py) so the video shows through.
boxed: the earlier look — dark #1a1a19 canvas, video shrunk into the safe box.

Overlay positions (both layouts) per references/instagram-reels-format.md (UI chrome:
top 220, bottom 420, left 60, right 144 px; safe box x 60-936, y 220-1500):
  - word/IPA subtitles + grade stamps: burned by the .ass (word block y~230-500,
    grade stamp mid-right ~y 600)
  - meaning emoji (128 px, Twemoji from tools/assets/emoji/, map in
    vowel_map.WORD_EMOJI): fixed slot right of the word line (x=780, y=232), shown
    for the word's segment — illustrates the word's meaning for non-English-speaking
    viewers. Needs cuts.json; words without a mapped emoji simply get none.
  - variant flag (128 px, vowel_map.VARIANT_EMOJI): fixed slot LEFT of the word
    (x=112, y=232) — UK/US flag for R-ending variant takes, red X for a "XX" take.
  - frequency panel (876 x 370 PNG sequence): x=60, y=1120 (ends at 1490, above the
    bottom chrome)

The .ass must have PlayResX/Y = 1080/1920 (build_phonetics_ass.py does this when called
with 1080 1920). Panel PNGs must be rendered 876x370 at the same fps as the master.
Verify decode after: ffmpeg -v error -i out.mp4 -f null -
"""
import sys, json, os, subprocess
from vowel_map import WORD_EMOJI, VARIANT_EMOJI

master, panels, ass, out = sys.argv[1:5]
cuts_path = sys.argv[5] if len(sys.argv) > 5 else None
layout = sys.argv[6] if len(sys.argv) > 6 else "fullbleed"
fps = int(sys.argv[7]) if len(sys.argv) > 7 else 30
EMOJI_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "emoji")

dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", master],
                           capture_output=True, text=True, check=True).stdout.strip())

cmd = ["ffmpeg", "-y", "-v", "error"]
if layout == "boxed":
    cmd += ["-f", "lavfi", "-i", f"color=c=0x1a1a19:s=1080x1920:r={fps}",
            "-i", master,
            "-framerate", str(fps), "-start_number", "0", "-i", f"{panels}/panel_%05d.png"]
    parts = ["[1:v]scale=-2:700[vid]",
             "[0:v][vid]overlay=x='60+(876-w)/2':y=410:shortest=1[c1]",
             "[c1][2:v]overlay=60:1120:eof_action=repeat[c2]"]
    audio_in, n_in = "1", 3
else:
    cmd += ["-i", master,
            "-framerate", str(fps), "-start_number", "0", "-i", f"{panels}/panel_%05d.png"]
    # scale to cover 1080x1920, center-crop the overshoot (a 480x848 phone source is
    # ~6 px off true 9:16); fps normalized in case a future master isn't CFR 30
    parts = ["[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
             f"crop=1080:1920,fps={fps}[base]",
             "[base][1:v]overlay=60:1120:eof_action=repeat[c2]"]
    audio_in, n_in = "0", 2

cur = "c2"
if cuts_path:
    for c in json.load(open(cuts_path, encoding="utf-8")):
        slots = [(WORD_EMOJI.get(c["word"]), 780),
                 (VARIANT_EMOJI.get(c.get("variant")), 112)]
        for code, x in slots:
            if not code:
                continue
            png = os.path.join(EMOJI_DIR, f"{code}.png")
            if not os.path.exists(png):
                print(f"warning: missing emoji asset {png} for '{c['word']}'")
                continue
            # bound the looped still to the master's duration — an unbounded -loop 1
            # stream keeps the filtergraph pulling frames forever, ffmpeg never ends
            cmd += ["-loop", "1", "-t", f"{dur:.3f}", "-i", png]
            parts.append(f"[{n_in}:v]scale=128:128[e{n_in}]")
            parts.append(f"[{cur}][e{n_in}]overlay={x}:232:"
                         f"enable='between(t,{c['seg_start']},{c['seg_end']})'[c{n_in}]")
            cur, n_in = f"c{n_in}", n_in + 1
parts.append(f"[{cur}]ass={ass}[v]")

cmd += ["-filter_complex", ";".join(parts), "-map", "[v]", "-map", f"{audio_in}:a",
        "-shortest",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
subprocess.run(cmd, check=True)
print("wrote", out)
