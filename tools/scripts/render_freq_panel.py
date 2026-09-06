"""Render the per-frame frequency panel PNG sequence for the phonetics video.

Usage: render_freq_panel.py <clean.wav> <cuts.json> <out_dir> <panel_w> <panel_h> <fps> [alpha=200]

alpha = opacity (0-255) of the panel background. Default 200 suits the fullbleed layout
(panel overlaid on the talking video — footage stays visible through it); use ~235 for
the boxed layout on a dark canvas.

ONE SPECTROGRAM PER WORD (user request 2026-09-01 — a single full-timeline spectrogram
squeezes each word into ~30 px and is illegible): the panel's time axis spans only the
CURRENT word's display window (seg_start..seg_end from cuts.json, which tile the master's
timeline), so every word gets the full panel width. Layout per window (dark chart
surface, palette = dataviz reference dark mode):
 - Spectrogram strip (top ~56%): wideband spectrogram 0-4 kHz in grayscale, measured
   F1 (blue) / F2 (orange) dots on voiced frames inside the word span, the word's
   Hillenbrand target bands (mean ± 1 SD), and — R-ending side note — purple F3 dots
   + target band over the ending span (r_out) of a UK/US variant take.
 - Pitch strip (bottom ~44%): F0 curve (aqua) on a 60-160 Hz scale.

PROGRESSIVE REVEAL within each word: data appears at the playhead as it is uttered
(two pre-rendered backgrounds per word — full/empty — composited at the playhead x);
static chrome (grid, tick labels, target bands, titles) shows from the window start.
PIL stamps the playhead line and live readouts (F0 Hz; word F1/F2 vs target + textbook
match % + letter grade; ending-F3 verdict line for variant takes).

Fonts/sizes scale with panel width (design reference: 876 px wide panel on a 1080x1920
Reels canvas). Output: out_dir/panel_%05d.png, RGBA, panel_w x panel_h — must be
rendered at the same CFR fps as the master.
"""
import sys, json, os, math, bisect
import numpy as np
import parselmouth
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from vowel_map import WORD_VOWEL, DARK_L, TARGETS_MEN, F3_RHOTIC, F3_PLAIN

wav, cuts_path, out_dir, W, H, FPS = (sys.argv[1], sys.argv[2], sys.argv[3],
                                      int(sys.argv[4]), int(sys.argv[5]), float(sys.argv[6]))
ALPHA = int(sys.argv[7]) if len(sys.argv) > 7 else 200
os.makedirs(out_dir, exist_ok=True)

SURFACE = "#1a1a19"
INK2 = "#c3c2b7"
MUTED = "#898781"
GRID = "#2c2c2a"
BLUE = "#3987e5"    # F1
ORANGE = "#d95926"  # F2
AQUA = "#199e70"    # F0
PURPLE = "#a07be0"  # F3 over R-endings (the r-coloring cue)

FS = W / 876.0  # font scale relative to the Reels design width

cuts = json.load(open(cuts_path, encoding="utf-8"))
snd = parselmouth.Sound(wav)
T = snd.duration

pitch = snd.to_pitch(time_step=0.005, pitch_floor=75, pitch_ceiling=500)
formant = snd.to_formant_burg(time_step=0.005, max_number_of_formants=5,
                              maximum_formant=5000, window_length=0.025)
spec = snd.to_spectrogram(window_length=0.008, maximum_frequency=4000, time_step=0.002,
                          frequency_step=20)
S_all = 10 * np.log10(np.maximum(spec.values, 1e-12))
S_times = spec.xs()
S_LO, S_HI = np.percentile(S_all, 55), S_all.max()  # one norm for every window

SPEC_H = int(H * 0.56)
PITCH_H = H - SPEC_H
FMAX = 4000.0
PITCH_LO, PITCH_HI = 60.0, 160.0

def y_spec(hz):
    return SPEC_H * (1 - hz / FMAX)

def y_pitch(hz):
    hz = min(max(hz, PITCH_LO), PITCH_HI)
    return SPEC_H + PITCH_H * (1 - (hz - PITCH_LO) / (PITCH_HI - PITCH_LO))

SCALE = 2  # matplotlib renders 2x, downsampled for crispness
TICK_FS = 18 * FS
TITLE_FS = 19 * FS

def render_bg(c, with_data):
    """Panel background for ONE word's display window [seg_start, seg_end]."""
    w0, w1 = c["seg_start"], c["seg_end"]

    def x_of(t):
        return (t - w0) / (w1 - w0) * W

    fig = plt.figure(figsize=(W * SCALE / 100, H * SCALE / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")
    fig.patch.set_facecolor(SURFACE)
    ax.add_patch(plt.Rectangle((0, 0), W, H, color=SURFACE, zorder=0))

    if with_data:
        i0 = bisect.bisect_left(S_times, w0)
        i1 = max(bisect.bisect_right(S_times, w1), i0 + 2)
        Snorm = np.clip((np.flipud(S_all[:, i0:i1]) - S_LO) / (S_HI - S_LO), 0, 1)
        ax.imshow(Snorm, extent=[0, W, SPEC_H, 0], aspect="auto", cmap="gray",
                  vmin=0, vmax=1.25, zorder=1, interpolation="bilinear")

    vow = WORD_VOWEL.get(c["word"])
    x0, x1 = x_of(c["word_start"]), x_of(c["word_end"])
    bands = []
    if vow:
        m1, s1, m2, s2 = TARGETS_MEN[vow]
        bands += [(x0, x1, m1, s1, BLUE), (x0, x1, m2, s2, ORANGE)]
    if c.get("r_out"):
        # R-ending side note: /ɝ/ F3 target for a US take, plain-vowel F3 for UK
        m3, s3 = F3_RHOTIC if c.get("variant") == "US" else F3_PLAIN
        bands.append((x_of(c["r_out"][0]), x_of(c["r_out"][1]), m3, s3, PURPLE))
    for b0, b1, mean, sd, col in bands:
        ax.add_patch(plt.Rectangle((b0, y_spec(mean + sd)), b1 - b0,
                                   y_spec(mean - sd) - y_spec(mean + sd),
                                   color=col, alpha=0.18, zorder=2, lw=0))
        ax.plot([b0, b1], [y_spec(mean)] * 2, color=col, lw=0.8 * SCALE,
                ls=(0, (3, 2)), alpha=0.85, zorder=3)

    if with_data:
        t = c["word_start"]
        while t <= c["word_end"]:
            f0 = pitch.get_value_at_time(t)
            if f0 == f0:
                f1 = formant.get_value_at_time(1, t)
                f2 = formant.get_value_at_time(2, t)
                if f1 == f1 and f1 < FMAX:
                    ax.plot(x_of(t), y_spec(f1), ".", color=BLUE, ms=3.4 * SCALE, zorder=4)
                if f2 == f2 and f2 < FMAX:
                    ax.plot(x_of(t), y_spec(f2), ".", color=ORANGE, ms=3.4 * SCALE, zorder=4)
                if c.get("r_out") and c["r_out"][0] <= t <= c["r_out"][1]:
                    f3 = formant.get_value_at_time(3, t)
                    if f3 == f3 and f3 < FMAX:
                        ax.plot(x_of(t), y_spec(f3), ".", color=PURPLE,
                                ms=3.4 * SCALE, zorder=4)
            t += 0.005

    for hz in (1000, 2000, 3000):
        ax.plot([0, W], [y_spec(hz)] * 2, color=GRID, lw=0.5 * SCALE, zorder=1.5)
        ax.text(6, y_spec(hz) - 4, f"{hz//1000}k", color=MUTED, fontsize=TICK_FS,
                va="bottom", ha="left", zorder=5)

    ax.add_patch(plt.Rectangle((0, SPEC_H), W, PITCH_H, color=SURFACE, zorder=6))
    ax.plot([0, W], [SPEC_H] * 2, color="#383835", lw=1 * SCALE, zorder=7)
    for hz in (80, 100, 120, 140):
        ax.plot([0, W], [y_pitch(hz)] * 2, color=GRID, lw=0.5 * SCALE, zorder=7)
        ax.text(6, y_pitch(hz) - 3, f"{hz}", color=MUTED, fontsize=TICK_FS,
                va="bottom", ha="left", zorder=9)

    if with_data:
        ts = np.arange(w0, w1, 0.005)
        f0s = np.array([pitch.get_value_at_time(t) for t in ts])
        ax.plot([x_of(t) for t in ts], [y_pitch(v) if v == v else np.nan for v in f0s],
                color=AQUA, lw=1.6 * SCALE, zorder=8, solid_capstyle="round")

    ax.text(W - 6, 6, "spectrogram · F1 F2 vs target", color=INK2, fontsize=TITLE_FS,
            ha="right", va="top", zorder=9)
    ax.text(W - 6, SPEC_H + 6, "pitch F0 (Hz)", color=INK2, fontsize=TITLE_FS,
            ha="right", va="top", zorder=9)

    path = os.path.join(out_dir, "_bg_tmp.png")
    fig.savefig(path, dpi=100)
    plt.close(fig)
    im = Image.open(path).convert("RGBA").resize((W, H), Image.LANCZOS)
    im.putalpha(im.split()[3].point(lambda a: ALPHA))
    return im

print(f"rendering {len(cuts)} per-word backgrounds…")
bgs = [(render_bg(c, True), render_bg(c, False)) for c in cuts]

try:
    font_b = ImageFont.truetype("C:/Windows/Fonts/seguisb.ttf", round(36 * FS))
except OSError:
    font_b = ImageFont.load_default()

starts = [c["seg_start"] for c in cuts]

def cut_at(t):
    """The word window containing t (windows tile the master timeline)."""
    return min(bisect.bisect_right(starts, t) - 1, len(cuts) - 1) if t >= 0 else 0

def px(v):
    return round(v * FS)

n_frames = int(math.ceil(T * FPS))
for i in range(n_frames):
    t = i / FPS
    ci = cut_at(t)
    c = cuts[ci]
    bg_full, bg_empty = bgs[ci]
    x = int(round((t - c["seg_start"]) / (c["seg_end"] - c["seg_start"]) * W))
    x = max(0, min(x, W))
    im = bg_empty.copy()
    if x > 0:
        im.paste(bg_full.crop((0, 0, x, H)), (0, 0))
    d = ImageDraw.Draw(im)
    d.line([(x, 0), (x, H)], fill=(255, 255, 255, 210), width=max(2, px(2)))
    f0 = pitch.get_value_at_time(t)
    txt = f"F0  {f0:3.0f} Hz" if f0 == f0 else "F0   —"
    d.rectangle([W - px(210), SPEC_H + px(44), W - px(8), SPEC_H + px(92)],
                fill=(26, 26, 25, 220))
    d.text((W - px(200), SPEC_H + px(48)), txt, font=font_b, fill=(255, 255, 255, 255))
    if c.get("f1") and c["word"] in WORD_VOWEL:
        m1, _, m2, _ = TARGETS_MEN[WORD_VOWEL[c["word"]]]
        # top of the spectrogram strip: only ~3.5-4 kHz energy lives there, while the
        # bottom fifth holds F1 and its target band — never cover that
        y0 = px(6)
        d.rectangle([px(4), y0, px(790), y0 + px(50)], fill=(26, 26, 25, 220))
        d.rectangle([px(12), y0 + px(15), px(32), y0 + px(35)], fill=BLUE)
        d.text((px(40), y0 + px(6)), f"F1 {c['f1']} ({m1})", font=font_b,
               fill=(255, 255, 255, 255))
        d.rectangle([px(265), y0 + px(15), px(285), y0 + px(35)], fill=ORANGE)
        d.text((px(293), y0 + px(6)), f"F2 {c['f2']} ({m2})", font=font_b,
               fill=(255, 255, 255, 255))
        # a dark-L word's match % is meaningless (coarticulated F2) — its grade is
        # F1-only, labeled as such; the "XX" gag still flaunts its honest 0%
        if c.get("match") is not None and (c["word"] not in DARK_L
                                           or c.get("variant") == "XX"):
            txt = f"match {c['match']}%"
            if c.get("grade"):
                txt += f" · {c['grade']}"
            d.text((px(545), y0 + px(6)), txt, font=font_b, fill=(255, 255, 255, 255))
        elif c.get("grade"):
            d.text((px(545), y0 + px(6)), f"F1 only · {c['grade']}", font=font_b,
                   fill=(255, 255, 255, 255))
        if c.get("f3_end"):
            # R-ending side note: the F3 verdict, with the ending vowel's own grade
            verdict = "R-colored /ɚ/" if c.get("rhotic") else "no R, plain /ə/"
            txt = f"ending F3 {c['f3_end']} Hz → {verdict}"
            if c.get("ending_grade"):
                txt += f" · {c['ending_grade']}"
            y1 = y0 + px(54)
            d.rectangle([px(4), y1, px(760), y1 + px(50)], fill=(26, 26, 25, 220))
            d.rectangle([px(12), y1 + px(15), px(32), y1 + px(35)], fill=PURPLE)
            d.text((px(40), y1 + px(6)), txt, font=font_b, fill=(255, 255, 255, 255))
    im.save(os.path.join(out_dir, f"panel_{i:05d}.png"))

print(f"{n_frames} frames -> {out_dir}")
