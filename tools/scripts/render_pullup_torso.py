"""
Core / chest / lats figure from the segmentation pass (torso.npz) + the pose analysis.

    python render_pullup_torso.py <analysis.json> <torso.npz> <out.png> <out.json>

Panels: phase-averaged torso patches (what the camera sees on average in each phase),
phase-averaged silhouettes, silhouette width profile (hang vs early pull), abdominal-band
shading index per phase, and per-rep trunk control (lateral bend, yaw, hip angle).
All lighting-based indices are exploratory - the light comes from above and the torso
moves into the lintel's shadow at the top, so shading changes are geometry as much as muscle.
"""
import sys, json
import numpy as np
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

BLUE, ORANGE, AQUA, YELLOW, MAGENTA, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#4a3aa7"
SURF, TXT, TXT2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"


def main():
    A = json.load(open(sys.argv[1])); T = np.load(sys.argv[2]); out_png, out_json = sys.argv[3], sys.argv[4]
    S, reps, sig = A["summary"], A["reps"], A["signals"]
    patch, thumb, width, taxis = T["patch"], T["thumb"], T["width_px"], np.round(T["taxis"], 2)
    P = None
    fps = S["fps"]
    g0, l0, h0 = sig["grab0"], sig["load0"], sig["hang0"]
    phases = {
        "standing, hands on bar": list(range(g0 + int(0.8 * fps), l0)),
        "loaded hang": [r["f_bottom1"] for r in reps] + [reps[0]["f_bottom0"]],
        "early pull": [f for r in reps for f in range(r["f_start"], r["f_start"] + (r["f_top"] - r["f_start"]) // 3)],
        "mid pull": [f for r in reps for f in range(r["f_start"] + (r["f_top"] - r["f_start"]) // 3, r["f_start"] + 2 * (r["f_top"] - r["f_start"]) // 3)],
        "top": [f for r in reps for f in range(r["f_conc_end"], r["f_ecc_start"] + 1)],
        "lowering": [f for r in reps for f in range(r["f_ecc_start"], r["f_end"] + 1)],
    }
    # abdominal-band shading index: gradient magnitude / brightness, central 30 % of the patch,
    # rows 55-85 % (between the ribcage and the waistband), so the arms stay out of it
    def shading(frames):
        band = patch[frames][:, 176:272, 84:156].astype(float)
        vals = [np.sqrt(cv2.Sobel(b, cv2.CV_64F, 1, 0) ** 2 + cv2.Sobel(b, cv2.CV_64F, 0, 1) ** 2).mean() / max(b.mean(), 1) * 100 for b in band]
        return float(np.mean(vals)), float(band.mean())
    res = {"phases": {}}
    for name, fr in phases.items():
        sh, br = shading(fr)
        res["phases"][name] = dict(frames=len(fr), shading_index=sh, brightness=br)
    # per-rep shading at top vs bottom
    for r in reps:
        r_sh_top, _ = shading(list(range(r["f_conc_end"], r["f_ecc_start"] + 1)))
        r_sh_bot, _ = shading([r["f_bottom1"]])
        r["abs_shading_top"] = r_sh_top; r["abs_shading_bottom"] = r_sh_bot
    # silhouette width profile normalised by the shoulder-level width (t=0.05), hang vs early pull
    k = {v: i for i, v in enumerate(taxis)}
    def prof(frames):
        w = width[frames]; w = w / w[:, [k[0.05]]]
        return np.nanmedian(w, axis=0)
    prof_hang = prof(phases["loaded hang"]); prof_early = prof(phases["early pull"]); prof_stand = prof(phases["standing, hands on bar"])
    def vt(frames):
        w = width[frames]; return float(np.nanmedian(w[:, k[0.2]] / w[:, k[0.55]]))
    res["v_taper_upper_over_waist"] = dict(standing=vt(phases["standing, hands on bar"]), hang=vt(phases["loaded hang"]), early_pull=vt(phases["early pull"]))
    res["waist_widening_early_pull_pct"] = float((np.nanmedian(width[phases["early pull"], k[0.55]]) / np.nanmedian(width[phases["loaded hang"], k[0.55]]) - 1) * 100)
    res["core"] = dict(mean_lat_bend_range=S["mean_lat_bend_range"], mean_lat_bend_top=S["mean_lat_bend_top"],
                       mean_yaw_top=S["mean_yaw_top"], mean_hip_angle_top=S["mean_hip_angle_top"],
                       mean_hip_sway_cm=S["mean_hip_sway_cm"], mean_knee_min=S["mean_knee_min"])
    json.dump(res, open(out_json, "w"), indent=1)

    fm.fontManager.addfont("C:/Windows/Fonts/segoeui.ttf"); fm.fontManager.addfont("C:/Windows/Fonts/segoeuib.ttf")
    plt.rcParams.update({"font.family": "Segoe UI", "axes.edgecolor": GRID, "axes.labelcolor": TXT2, "xtick.color": TXT2, "ytick.color": TXT2,
                         "axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold", "axes.titlecolor": TXT,
                         "axes.titlesize": 12, "axes.titlelocation": "left", "figure.facecolor": SURF, "axes.facecolor": SURF,
                         "grid.color": GRID, "axes.grid": True, "axes.axisbelow": True, "xtick.labelsize": 9, "ytick.labelsize": 9})
    fig = plt.figure(figsize=(16, 13), dpi=110)
    gs = fig.add_gridspec(3, 6, height_ratios=[1.35, 0.9, 1.0], hspace=0.5, wspace=0.35, left=0.04, right=0.985, top=0.9, bottom=0.06)
    fig.text(0.04, 0.965, "Core, chest and lats — what one front camera can and cannot see", fontsize=20, fontweight="bold", color=TXT)
    fig.text(0.04, 0.94, "Top row: the torso patch (shoulders→hips, perspective-normalised) averaged over every frame of each phase. "
             "Shading indices are exploratory: the light is overhead and the torso rises into the lintel's shadow at the top.", fontsize=10.5, color=TXT2)
    for j, (name, fr) in enumerate(phases.items()):
        ax = fig.add_subplot(gs[0, j]); ax.grid(False); ax.set_xticks([]); ax.set_yticks([])
        m = np.clip(patch[fr].astype(float).mean(0), 0, 255)
        ax.imshow(m, cmap="gray", vmin=0, vmax=255, aspect="equal")
        ax.set_title(f"{name}\n{len(fr)} frames · brightness {res['phases'][name]['brightness']:.0f}", fontsize=10)
        for sp in ax.spines.values(): sp.set_visible(False)
    # silhouettes
    for j, (name, fr) in enumerate(phases.items()):
        ax = fig.add_subplot(gs[1, j]); ax.grid(False); ax.set_xticks([]); ax.set_yticks([])
        ax.imshow(thumb[fr].astype(float).mean(0), cmap="gray", vmin=0, vmax=255, aspect="equal")
        for sp in ax.spines.values(): sp.set_visible(False)
        if j == 0: ax.set_title("mean silhouette (segmentation mask)", fontsize=10)
    # width profile
    ax = fig.add_subplot(gs[2, 0:2])
    sel = (taxis >= 0.05) & (taxis <= 1.0)
    ax.plot(taxis[sel], prof_stand[sel], color=TXT2, lw=1.5, ls="--", label="standing")
    ax.plot(taxis[sel], prof_hang[sel], color=BLUE, lw=2.2, label="loaded hang")
    ax.plot(taxis[sel], prof_early[sel], color=AQUA, lw=2.2, label="early pull")
    ax.set_xlabel("position along shoulder → hip axis"); ax.set_ylabel("silhouette width ÷ width at shoulders")
    ax.set_title("Silhouette width profile (arms overhead only)"); ax.legend(frameon=False, fontsize=9)
    ax.text(0.98, 0.05, f"V-taper (0.2 ÷ 0.55): hang {res['v_taper_upper_over_waist']['hang']:.2f} · early pull {res['v_taper_upper_over_waist']['early_pull']:.2f}\n"
            f"waist width change as the pull starts: {res['waist_widening_early_pull_pct']:+.0f} %", transform=ax.transAxes, fontsize=9, color=TXT2, ha="right")
    ax.set_ylim(0.7, 1.35)
    # shading index per phase
    ax = fig.add_subplot(gs[2, 2:4])
    names = list(phases.keys()); vals = [res["phases"][n]["shading_index"] for n in names]; brs = [res["phases"][n]["brightness"] for n in names]
    ax.bar(range(len(names)), vals, color=[TXT2, BLUE, AQUA, AQUA, YELLOW, BLUE], width=0.62)
    for i, (v, b) in enumerate(zip(vals, brs)):
        ax.text(i, v + 1, f"{v:.0f}", ha="center", fontsize=9, color=TXT)
    ax.set_xticks(range(len(names))); ax.set_xticklabels([n.replace(", ", ",\n") for n in names], fontsize=8.5)
    ax.set_title("Abdominal-band shading index (edge contrast ÷ brightness)")
    ax.text(0.02, 0.9, "rises with bracing AND with shadow — read together with brightness", transform=ax.transAxes, fontsize=9, color=TXT2)
    # per-rep trunk control
    ax = fig.add_subplot(gs[2, 4:6])
    x = np.arange(1, len(reps) + 1)
    ax.bar(x - 0.2, [r["lat_bend_range"] for r in reps], width=0.38, color=MAGENTA, label="lateral bend range (°)")
    ax.bar(x + 0.2, [r["yaw_range"] for r in reps], width=0.38, color=VIOLET, label="rotation range (°, 3D estimate)")
    ax.set_xticks(x); ax.set_xlabel("rep"); ax.set_title("Trunk control per rep")
    ax.legend(frameon=False, fontsize=9, loc="upper left", ncol=2)
    ax.set_ylim(0, max(max(r["lat_bend_range"] for r in reps), max(r["yaw_range"] for r in reps)) * 1.45)
    ax.set_title(f"Trunk control per rep — hip angle at top {S['mean_hip_angle_top']:.0f}°, knees {S['mean_knee_min']:.0f}°, sway {S['mean_hip_sway_cm']:.0f} cm")
    fig.savefig(out_png, facecolor=SURF)
    print("saved", out_png)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
