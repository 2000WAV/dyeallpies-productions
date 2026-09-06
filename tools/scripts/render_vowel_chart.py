"""Vowel-space (F1 x F2) chart: measured tokens vs Hillenbrand et al. (1995) men reference.

Usage: render_vowel_chart.py <cuts.json> <removed.json> <hillenbrand_means.csv> <out.png>

Phonetics convention: both axes reversed (F2 right-to-left, F1 top-to-bottom) so the chart
reads like the IPA vowel quadrilateral (front-close top-left). Reference vowels are drawn as
IPA glyphs at the men's steady-state means; the vowels under study get a +/-1 SD ellipse.
Axis limits are computed from everything drawn (tokens, reference glyphs, study ellipses)
plus padding, so no data can fall outside the figure. Tokens over a dark /l/
(vowel_map.DARK_L) are hollow — their F2 is coarticulated and ungraded.

If any take carries an R-ending measurement (f3_end in cuts.json), a second panel is added
below: the "R test" — ending F3 per word, UK vs US takes joined dumbbell-style, against the
Hillenbrand /ɝ/ (r-colored) and plain-vowel F3 zones.

Palette/typography: dataviz reference palette, light mode.
"""
import sys, json, csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from vowel_map import WORD_VOWEL, DARK_L, F3_RHOTIC, F3_PLAIN

cuts_path, removed_path, means_path, out_path = sys.argv[1:5]

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID = "#e1e0d9"
BLUE, ORANGE, CRIT, GREEN = "#2a78d6", "#eb6834", "#d03b3b", "#1e9e6a"

matplotlib.rcParams["font.family"] = "Segoe UI"

cuts = json.load(open(cuts_path, encoding="utf-8"))
removed = json.load(open(removed_path, encoding="utf-8")) \
    if removed_path != "none" and os.path.exists(removed_path) else []
ref = {}
for row in csv.DictReader(open(means_path, encoding="utf-8")):
    if row["group"] == "men":
        ref[row["ipa"]] = {k: float(row[k]) for k in
                           ("f1_mean", "f1_sd", "f2_mean", "f2_sd")}

r_takes = [c for c in cuts if c.get("f3_end")]
if r_takes:
    fig, (ax, axr) = plt.subplots(2, 1, figsize=(8, 11.6), dpi=150,
                                  gridspec_kw={"height_ratios": [3.0, 1.15]})
else:
    fig, ax = plt.subplots(figsize=(8, 9), dpi=150)
    axr = None
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

# reference glyphs; emphasize the vowels actually under study, in order of appearance —
# first gets blue, second orange (matches the token colors below)
study = []
for c in cuts:
    v = WORD_VOWEL.get(c["word"])
    if v and v not in study:
        study.append(v)
EMPH = {v: col for v, col in zip(study, (BLUE, ORANGE))}
for ipa, v in ref.items():
    col = EMPH.get(ipa, MUTED)
    if ipa in EMPH:
        ax.add_patch(Ellipse((v["f2_mean"], v["f1_mean"]), 2 * v["f2_sd"], 2 * v["f1_sd"],
                             facecolor=col, alpha=0.10, edgecolor=col, lw=1.0, ls="--"))
    ax.text(v["f2_mean"], v["f1_mean"], ipa, color=col, fontsize=17 if ipa in EMPH else 13,
            fontweight="bold" if ipa in EMPH else "normal", ha="center", va="center",
            zorder=7)  # above token dots: a token ON the mean should show the glyph on top

# kept tokens; labels are auto-placed by adjustText to dodge collisions (the /ʌ/
# cluster packs ~25 tokens into a ~400x250 Hz box — fixed offsets can't survive that)
multi_take = {c["word"] for c in cuts if c["take"] > 1 and not c.get("variant")}
plotted = [c for c in cuts if c.get("f1") and WORD_VOWEL.get(c["word"])]
texts = []
for c in plotted:
    col = EMPH.get(WORD_VOWEL[c["word"]], BLUE)
    dark = c["word"] in DARK_L
    ax.plot(c["f2"], c["f1"], "o", ms=8, zorder=6,
            markerfacecolor="none" if dark else col, color=col,
            markeredgecolor=col if dark else SURFACE, markeredgewidth=1.5)
    name = f"{c['word']}{c['take'] if c['word'] in multi_take else ''}"
    if c.get("variant"):
        name += "·X" if c["variant"] == "XX" else f"·{c['variant']}"
    if c.get("match") is not None and not dark:
        name += f" {c['match']}%"
    if c.get("grade"):
        name += f" {c['grade']}"
    texts.append(ax.text(c["f2"], c["f1"], name, fontsize=7, color=INK2, zorder=6,
                         clip_on=True))

# removed takes
for r in removed:
    ax.plot(r["f2"], r["f1"], "x", color=CRIT, ms=9, markeredgewidth=2.2, zorder=6)
    ax.annotate(r["label"], (r["f2"], r["f1"]), textcoords="offset points",
                xytext=(r.get("dx", 10), r.get("dy", -14)), fontsize=8, color=CRIT,
                ha="left", zorder=6, annotation_clip=True)

# limits from everything drawn (tokens, removed, every ref glyph, study ellipses)
# + padding, so nothing can stick out of the axes
xs, ys = [], []
for c in plotted:
    xs.append(c["f2"]); ys.append(c["f1"])
for r in removed:
    xs.append(r["f2"]); ys.append(r["f1"])
for ipa, v in ref.items():
    pad = 1.0 if ipa in EMPH else 0.0  # ellipse = ±1 SD
    xs += [v["f2_mean"] - pad * v["f2_sd"] - 60, v["f2_mean"] + pad * v["f2_sd"] + 60]
    ys += [v["f1_mean"] - pad * v["f1_sd"] - 25, v["f1_mean"] + pad * v["f1_sd"] + 25]
mx, my = 0.07 * (max(xs) - min(xs)), 0.07 * (max(ys) - min(ys))
ax.set_xlim(max(xs) + 1.5 * mx, min(xs) - 1.5 * mx)
ax.set_ylim(max(ys) + my, min(ys) - my)

# spread the labels after limits are final; clip_on keeps every label inside the axes
from adjustText import adjust_text
adjust_text(texts, ax=ax,
            expand_axes=False, ensure_inside_axes=True,
            arrowprops=dict(arrowstyle="-", color=GRID, lw=0.6, shrinkA=2, shrinkB=4))
ax.grid(True, color=GRID, lw=0.7)
ax.tick_params(colors=MUTED, labelsize=9)
for s in ax.spines.values():
    s.set_color(GRID)
ax.set_xlabel("F2 (Hz)   ← back        front →", color=INK2, fontsize=10)
ax.set_ylabel("F1 (Hz)   ← open        close →", color=INK2, fontsize=10)
ax.xaxis.set_label_position("top")
ax.xaxis.tick_top()

ax.set_title("Your vowels vs. American English reference (adult men)",
             color=INK, fontsize=13, fontweight="bold", pad=34)

handles = [
    plt.Line2D([], [], marker="o", ls="", color=col, ms=8, label=f"your /{v}/ words")
    for v, col in EMPH.items()
] + [
    plt.Line2D([], [], marker="$æ$", ls="", color=MUTED, ms=10,
               label="Hillenbrand men mean (ellipse = ±1 SD)"),
]
if any(c["word"] in DARK_L for c in plotted):
    handles.append(plt.Line2D([], [], marker="o", ls="", markerfacecolor="none",
                              color=next(iter(EMPH.values()), BLUE), ms=8,
                              label="before dark /l/ (graded on F1 only)"))
if removed:
    handles.append(plt.Line2D([], [], marker="x", ls="", color=CRIT, ms=8,
                              markeredgewidth=2, label="removed takes"))
ax.legend(handles=handles, loc="lower left", fontsize=8.5, frameon=False,
          labelcolor=INK2)

# ---- R test panel: ending F3, UK vs US takes, against the rhotic /ɝ/ zone ----
if axr:
    axr.set_facecolor(SURFACE)
    words = list(dict.fromkeys(c["word"] for c in r_takes))
    rows = {w: i for i, w in enumerate(words)}
    for (mean, sd), col, lab in ((F3_RHOTIC, GREEN, "American /ɚ/ zone (r-colored)"),
                                 (F3_PLAIN, MUTED, "British /ə/ zone (no R)")):
        axr.axvspan(mean - sd, mean + sd, color=col, alpha=0.13, zorder=1)
        axr.axvline(mean, color=col, lw=1.0, ls=(0, (3, 2)), alpha=0.8, zorder=2)
        axr.text(mean, len(words) - 0.25, lab, color=col, fontsize=8.5,
                 ha="center", va="bottom", fontweight="bold", zorder=5)
    for w in words:
        pair = [c for c in r_takes if c["word"] == w]
        if len(pair) == 2:
            axr.plot([c["f3_end"] for c in pair], [rows[w]] * 2, "-", color=GRID,
                     lw=1.6, zorder=3)
        for c in pair:
            col = GREEN if c.get("variant") == "US" else BLUE
            axr.plot(c["f3_end"], rows[w], "o", color=col, ms=9, zorder=4,
                     markeredgecolor=SURFACE, markeredgewidth=1.5)
            axr.annotate(c.get("variant", "?"), (c["f3_end"], rows[w]),
                         textcoords="offset points", xytext=(0, 8), fontsize=7,
                         color=INK2, ha="center", zorder=5)
    f3s = [c["f3_end"] for c in r_takes] + \
          [F3_RHOTIC[0] - F3_RHOTIC[1], F3_PLAIN[0] + F3_PLAIN[1]]
    pad = 0.08 * (max(f3s) - min(f3s))
    axr.set_xlim(min(f3s) - pad, max(f3s) + pad)
    axr.set_ylim(-0.6, len(words) + 0.7)
    axr.set_yticks(range(len(words)), words)
    axr.grid(True, axis="x", color=GRID, lw=0.7)
    axr.tick_params(colors=MUTED, labelsize=9)
    axr.tick_params(axis="y", labelcolor=INK2)
    for s in axr.spines.values():
        s.set_color(GRID)
    axr.set_xlabel("ending F3 (Hz) — lower = more r-colored", color=INK2, fontsize=10)
    axr.set_title("The R test: F3 of the word's ending, British vs American take",
                  color=INK, fontsize=11.5, fontweight="bold", pad=8)

fig.text(0.5, 0.012,
         "Reference: Hillenbrand, Getty, Clark & Wheeler (1995), JASA 97(5) — 45 men, "
         "steady-state formants (/hVd/ words).\nYour values: median F1/F2 over the vowel "
         "nucleus (ending F3 over the final schwa), Praat (Burg) via parselmouth, "
         "ceiling 5 kHz.\nmatch % = closeness to the reference mean over (F1, F2), "
         "Gaussian with 2-SD tolerance. Grades: A+ ≤1 SD, A ≤1.75, B ≤2.5, C ≤3.25, "
         "D ≤4, F beyond\n(hollow /ʌl/ tokens graded on F1 only, tolerance ×2 — dark "
         "/l/ coarticulates F2; UK/US endings graded on F3 vs /ɝ/ or plain-vowel).",
         color=MUTED, fontsize=7.5, ha="center")

fig.tight_layout(rect=[0, 0.035, 1, 1])
fig.savefig(out_path, dpi=150, facecolor=SURFACE)
print("wrote", out_path)
