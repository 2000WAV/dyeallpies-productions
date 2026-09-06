"""
Static dashboard for a pull-up set (analysis.json from analyze_pullups.py).

    python render_pullup_dashboard.py <analysis.json> <out.png>

Six panels, one system: height trace with phases; per-rep peak speed and tempo
(small multiples, one axis each - never dual-axis); chin clearance; efficiency
score stacked by component; hip sway; elbow angle L vs R at the top.
"""
import sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = \
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"
SURF, TXT, TXT2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
GRADE = {"A": AQUA, "B": YELLOW, "C": ORANGE, "D": RED}


def main():
    A = json.load(open(sys.argv[1])); out = sys.argv[2]
    S, reps, sig = A["summary"], A["reps"], A["signals"]
    t = np.array(sig["t"]); n = len(reps); x = np.arange(1, n + 1)
    fp = "C:/Windows/Fonts/segoeui.ttf"
    if fp:
        fm.fontManager.addfont(fp); fm.fontManager.addfont("C:/Windows/Fonts/segoeuib.ttf")
        plt.rcParams["font.family"] = "Segoe UI"
    plt.rcParams.update({"axes.edgecolor": GRID, "axes.labelcolor": TXT2, "xtick.color": TXT2, "ytick.color": TXT2,
                         "axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold",
                         "axes.titlecolor": TXT, "axes.titlesize": 13, "axes.titlelocation": "left",
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "grid.color": GRID, "axes.grid": True,
                         "axes.axisbelow": True, "xtick.labelsize": 10, "ytick.labelsize": 10})

    fig = plt.figure(figsize=(16, 15), dpi=110)
    gs = fig.add_gridspec(4, 3, height_ratios=[1.15, 1, 1, 1], hspace=0.55, wspace=0.32,
                          left=0.05, right=0.985, top=0.9, bottom=0.05)
    fig.text(0.05, 0.965, f"Pull-up set · {S['reps']} reps · mean efficiency {S['mean_efficiency']:.0f}/100",
             fontsize=22, fontweight="bold", color=TXT)
    fig.text(0.05, 0.94, f"MediaPipe Pose heavy (33 landmarks, 3D world angles) on {S['tracked_frames']}/{S['frames']} frames · "
             f"YOLOv8m-pose cross-check: {S.get('yolo_reps', '–')} reps, shoulder-track r = {S.get('yolo_mp_shoulder_corr', 0):.3f} · "
             f"cm values are estimates (≈{S['px_per_m']:.0f} px/m)", fontsize=11, color=TXT2)

    # 1. height trace, full width
    ax = fig.add_subplot(gs[0, :])
    h0 = sig["hang0"]; h1 = sig["hang1"]; g0 = sig["grab0"]; l0 = sig["load0"]
    hang_ref, top_ref = S["hang_ref_y"], S["top_ref_y"]
    pct = np.array(sig["height_pct"])
    ax.plot(t[g0:h1], pct[g0:h1], color=TXT2, lw=1.2, alpha=0.6, label="shoulder height")
    for r in reps:
        c, e = slice(r["f_start"], r["f_conc_end"] + 1), slice(r["f_ecc_start"], r["f_end"] + 1)
        ax.plot(t[c], pct[c], color=AQUA, lw=2.2); ax.plot(t[e], pct[e], color=BLUE, lw=2.2)
        ax.plot(t[r["f_top"]], pct[r["f_top"]], "o", ms=9, mfc=GRADE[r["grade"]], mec=SURF, mew=1.5)
        ax.annotate(f"{r['n']}", (t[r["f_top"]], pct[r["f_top"]]), xytext=(0, 9), textcoords="offset points",
                    ha="center", fontsize=9, color=TXT)
    chin_pct = (hang_ref - (S["bar_y"] + (S["neck_cm"] + S["perspective_cm"]) / 100 * S["px_per_m"])) / (hang_ref - top_ref) * 100
    ax.axhline(chin_pct, color=TXT2, lw=1, ls="--"); ax.text(t[g0] + 0.2, chin_pct + 2, "chin at bar", fontsize=9, color=TXT2)
    ax.axvspan(t[g0], t[l0], color=GRID, alpha=0.6); ax.axvspan(t[l0], t[h0], color=YELLOW, alpha=0.18)
    ax.text((t[g0] + t[l0]) / 2, 60, f"standing,\nhands on bar\n{S['standing_on_bar']:.1f} s", ha="center", fontsize=9.5, color=TXT2)
    ax.text((t[l0] + t[h0]) / 2, 60, f"loading\n{S['loading_duration']:.1f} s", ha="center", fontsize=9.5, color=TXT2)
    ax.plot([], [], color=AQUA, lw=2.2, label="pull (concentric)"); ax.plot([], [], color=BLUE, lw=2.2, label="lower (eccentric)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), frameon=False, ncol=3, fontsize=10)
    ax.set_ylabel("height, % of best rep"); ax.set_xlabel("time (s)"); ax.set_ylim(-8, 118)
    ax.set_title("Shoulder height through the set — marker colour = rep grade (A aqua, B yellow)")

    # 2. peak concentric speed per rep
    ax = fig.add_subplot(gs[1, 0])
    v = [r["peak_conc_v"] for r in reps]
    ax.bar(x, v, color=BLUE, width=0.62)
    ax.plot(x, np.polyval(np.polyfit(x, v, 1), x), color=TXT2, lw=1, ls="--")
    for i, val in enumerate(v):
        if i in (0, int(np.argmax(v)), n - 1):
            ax.text(x[i], val + 0.015, f"{val:.2f}", ha="center", fontsize=9, color=TXT)
    ax.set_title("Peak pull speed (m/s)"); ax.set_xticks(x); ax.set_xlabel("rep")
    ax.text(0.98, 0.95, f"−{S['velocity_loss_pct']:.0f} % best→last", transform=ax.transAxes, ha="right", fontsize=10, color=TXT2)

    # 3. tempo per rep (stacked up / hold / down)
    ax = fig.add_subplot(gs[1, 1])
    up = np.array([r["t_concentric"] for r in reps]); hold = np.array([r["t_top_hold"] for r in reps]); dn = np.array([r["t_eccentric"] for r in reps])
    ax.bar(x, up, color=AQUA, width=0.62, label="pull")
    ax.bar(x, hold, bottom=up, color=YELLOW, width=0.62, label="hold", edgecolor=SURF, linewidth=1)
    ax.bar(x, dn, bottom=up + hold, color=BLUE, width=0.62, label="lower", edgecolor=SURF, linewidth=1)
    ax.set_title("Tempo per rep (s)"); ax.set_xticks(x); ax.set_xlabel("rep"); ax.legend(frameon=False, fontsize=9, loc="upper left", ncol=3)
    ax.set_ylim(0, max(up + hold + dn) * 1.25)

    # 4. chin vs bar per rep
    ax = fig.add_subplot(gs[1, 2])
    chin = np.array([r["chin_est_cm"] + S["perspective_cm"] for r in reps])
    ax.bar(x, chin, color=[AQUA if c >= 1 else YELLOW if c >= -1 else ORANGE for c in chin], width=0.62)
    ax.axhline(0, color=TXT, lw=1)
    ax.set_title("Chin vs bar line (cm, est.)"); ax.set_xticks(x); ax.set_xlabel("rep")
    ax.axhline(1, color=TXT2, lw=0.8, ls=":"); ax.axhline(-1, color=TXT2, lw=0.8, ls=":")
    ax.text(0.02, 0.05, f"{S.get('chin_above', 0)} above (≥1 cm) · {S.get('chin_marginal', 0)} at bar (±1 cm) · {S.get('chin_short', 0)} short", transform=ax.transAxes, fontsize=9, color=TXT2)

    # 5. efficiency score, stacked by component
    ax = fig.add_subplot(gs[2, :2])
    comps = [("rom", "range of motion", BLUE), ("control", "eccentric control", AQUA), ("lockout", "lock-out", YELLOW),
             ("sway", "low sway", MAGENTA), ("power", "pull speed", VIOLET), ("symmetry", "L/R symmetry", ORANGE)]
    bottom = np.zeros(n)
    for key, lab, col in comps:
        vals = np.array([r["score"][key] for r in reps])
        ax.bar(x, vals, bottom=bottom, color=col, width=0.62, label=lab, edgecolor=SURF, linewidth=1)
        bottom += vals
    for i, r in enumerate(reps):
        ax.text(x[i], bottom[i] + 1.5, f"{r['efficiency']:.0f} {r['grade']}", ha="center", fontsize=10, color=TXT, fontweight="bold")
    ax.set_ylim(0, 112); ax.set_xticks(x); ax.set_xlabel("rep"); ax.set_title("Efficiency score by component (max 25 / 20 / 15 / 15 / 15 / 10)")
    ax.legend(frameon=False, fontsize=9, ncol=6, loc="lower center", bbox_to_anchor=(0.5, -0.36))

    # 6. hip sway
    ax = fig.add_subplot(gs[2, 2])
    sway = [r["hip_sway_cm"] for r in reps]
    ax.bar(x, sway, color=MAGENTA, width=0.62); ax.axhline(4, color=TXT2, lw=1, ls="--")
    ax.text(n + 0.4, 4.3, "≤4 cm ideal", ha="right", fontsize=9, color=TXT2)
    ax.set_title("Hip sway (cm, est.)"); ax.set_xticks(x); ax.set_xlabel("rep")

    # 7. elbow angle at top, L vs R (dot pair)
    ax = fig.add_subplot(gs[3, 0])
    el = [r["elbow_top_l"] for r in reps]; er = [r["elbow_top_r"] for r in reps]
    for i in range(n):
        ax.plot([x[i], x[i]], [el[i], er[i]], color=GRID, lw=3)
    ax.plot(x, el, "o", color=BLUE, ms=8, label="left", mec=SURF); ax.plot(x, er, "o", color=ORANGE, ms=8, label="right", mec=SURF)
    ax.set_title("Elbow angle at the top (°, 3D)"); ax.set_xticks(x); ax.set_xlabel("rep")
    ax.legend(frameon=False, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2)
    ax.set_ylim(min(el) - 8, max(er) + 6)
    ax.text(0.02, 0.04, f"right arm bends {S['mean_elbow_top_r'] - S['mean_elbow_top_l']:.0f}° less", transform=ax.transAxes, fontsize=9, color=TXT2)

    # 8. energy per rep (rough) and effort
    ax = fig.add_subplot(gs[3, 1])
    if "kcal" in reps[0]:
        kc = np.array([r["kcal_conc"] for r in reps]); ke = np.array([r["kcal_ecc"] for r in reps]); ki = np.array([r["kcal_iso"] for r in reps])
        ax.bar(x, kc, color=AQUA, width=0.62, label="pull (work / 22 %)")
        ax.bar(x, ke, bottom=kc, color=BLUE, width=0.62, label="lower", edgecolor=SURF, linewidth=1)
        ax.bar(x, ki, bottom=kc + ke, color=YELLOW, width=0.62, label="holding on (time)", edgecolor=SURF, linewidth=1)
        for i, r in enumerate(reps):
            ax.text(x[i], r["kcal"] + 0.02, f"{r['kcal']:.2f}", ha="center", fontsize=8.5, color=TXT)
        ax.set_ylim(0, max(r["kcal"] for r in reps) * 1.35); ax.legend(frameon=False, fontsize=8, loc="upper left", ncol=1)
        ax.set_title(f"Energy per rep (kcal, rough) - set = {S['set_kcal_total']:.0f} kcal"); ax.set_xticks(x); ax.set_xlabel("rep")

    ax = fig.add_subplot(gs[3, 2])
    if "effort_x" in reps[0]:
        ef = [r["effort_x"] for r in reps]
        ax.bar(x, ef, color=[ORANGE if e >= 1.4 else YELLOW if e >= 1.2 else AQUA for e in ef], width=0.62)
        for i, r in enumerate(reps):
            ax.text(x[i], r["effort_x"] + 0.03, f"RIR {r['est_rir']}", ha="center", fontsize=8.5, color=TXT2)
        ax.axhline(1, color=TXT2, lw=1, ls="--")
        ax.set_ylim(0, max(ef) * 1.3); ax.set_title("Effort vs fastest rep (× slower, same work)")
        ax.set_xticks(x); ax.set_xlabel("rep")
        ax.text(0.02, 0.9, "RIR = estimated reps in reserve from velocity loss", transform=ax.transAxes, fontsize=9, color=TXT2)

    fig.savefig(out, facecolor=SURF)
    print("saved", out)


if __name__ == "__main__":
    main()
