"""
Dashboard for a pull-up set, version 2 (analysis.json from analyze_pullups2.py).

    python render_pullup_dashboard2.py <analysis.json> <out.png>

Nine panels: height trace with the failed attempt marked; chin clearance against the bar
with its uncertainty band; per-rep peak speed; tempo; left/right asymmetry (shoulder tilt,
ear-to-shoulder, elbow 2D vs 3D); bar-path drift; modelled muscle temperature per muscle;
and the technique card. Palette and rules from the dataviz skill: one idea per panel, no
dual axes, direct labels rather than legends where it fits.
"""
import sys, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pullup_thermal as TH

BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = \
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"
SURF, TXT, TXT2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
VCOL = {"above": AQUA, "at": YELLOW, "short": ORANGE}
RED_C = "#c2352a"


def main():
    A = json.load(open(sys.argv[1])); out = sys.argv[2]
    REDN = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else None
    S, atts, sig = A["summary"], A["reps"], A["signals"]
    reps = [r for r in atts if r.get("rep")]
    fails = [r for r in atts if not r.get("rep")]
    AS = S["asymmetry"]; TC = S["technique"]
    t = np.array(sig["t"]); n = len(reps); x = np.arange(1, n + 1)
    Tm = TH.integrate(A); tsum = TH.summarise(A, Tm)

    for f in ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/segoeuib.ttf"):
        fm.fontManager.addfont(f)
    plt.rcParams["font.family"] = "Segoe UI"
    plt.rcParams.update({"axes.edgecolor": GRID, "axes.labelcolor": TXT2, "xtick.color": TXT2,
                         "ytick.color": TXT2, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titleweight": "bold", "axes.titlecolor": TXT, "axes.titlesize": 13,
                         "axes.titlelocation": "left", "figure.facecolor": SURF, "axes.facecolor": SURF,
                         "grid.color": GRID, "axes.grid": True, "axes.axisbelow": True,
                         "xtick.labelsize": 10, "ytick.labelsize": 10})

    fig = plt.figure(figsize=(16, 22.5), dpi=110)
    gs = fig.add_gridspec(6, 3, height_ratios=[1.15, 1, 1, 1, 1, 1], hspace=0.62, wspace=0.32,
                          left=0.055, right=0.985, top=0.935, bottom=0.035)
    fig.text(0.055, 0.972, f"Pull-up set · {S['reps']} reps + 1 failed attempt · judged to the USMC standard",
             fontsize=22, fontweight="bold", color=TXT)
    fig.text(0.055, 0.952,
             f"MediaPipe Pose heavy (33 landmarks) on {S['tracked_frames']}/{S['frames']} frames · YOLOv8m-pose "
             f"cross-check: {S.get('yolo_attempts', '-')} attempts, shoulder-track r = {S.get('yolo_mp_shoulder_corr', 0):.3f} · footage de-rolled "
             f"{S['camera_roll_corrected_deg']:.1f}° · {S['px_per_m']:.0f} px/m from the standing stature · "
             f"cm and °C are estimates", fontsize=11, color=TXT2)

    # 1 ---- height trace ----------------------------------------------------------------
    ax = fig.add_subplot(gs[0, :])
    hp = np.array(sig["height_pct"])
    h0, h1 = sig["hang0"], sig["hang1"]
    ax.plot(t[h0:h1], hp[h0:h1], color=TXT, lw=1.6)
    ax.axhline(0, color=GRID, lw=1)
    cbp = 100 + (-S["mean_chin_cm"]) / S["mean_rom_cm"] * 100
    ax.axhline(cbp, color=BLUE, lw=1.4, ls="--")
    ax.text(t[h1] - 0.4, cbp + 2, "chin would clear the bar here", color=BLUE, fontsize=10, ha="right")
    for r in atts:
        c = ORANGE if not r.get("rep") else VCOL[r["chin_verdict"]]
        ax.plot(r["t_top"], hp[r["f_top"]], "o", ms=9, color=c, mec="white", mew=1.5, zorder=5)
        ax.annotate(str(r["rep"]) if r.get("rep") else "X", (r["t_top"], hp[r["f_top"]]),
                    textcoords="offset points", xytext=(0, 11), ha="center", fontsize=9, color=TXT2)
    ax.axvspan(t[sig["grab0"]], t[sig["load0"]], color=GRID, alpha=0.6)
    ax.text(t[sig["grab0"]] + 0.2, 104, "standing, hands on the bar", color=TXT2, fontsize=9)
    ax.set_title("Shoulder height through the set  (0 % = loaded dead hang, 100 % = best rep)")
    ax.set_xlabel("seconds"); ax.set_ylabel("% of best rep"); ax.set_ylim(-8, 118)

    # 2 ---- chin clearance --------------------------------------------------------------
    ax = fig.add_subplot(gs[1, 0])
    ch = [r["chin_cm"] for r in reps]
    ax.bar(x, ch, color=[VCOL[r["chin_verdict"]] for r in reps], width=0.72)
    ax.errorbar(x, ch, yerr=S["chin_sigma_cm"], fmt="none", ecolor=TXT2, elinewidth=1.2, capsize=3)
    ax.plot(x, [r["chin_cm_from_shoulder"] for r in reps], "D", ms=5, color=VIOLET, zorder=6)
    ax.axhline(0, color=TXT, lw=1.4)
    ax.text(0.02, 0.35, "the bar", color=TXT, fontsize=10, transform=ax.get_yaxis_transform(), va="bottom")
    ax.text(n + 0.4, min(ch) - 0.4, "diamonds = shoulder-anchored\nsecond estimate", color=VIOLET, fontsize=9, ha="right")
    ax.set_title("Chin vs the bar — every rep came up short")
    ax.set_xlabel("rep"); ax.set_ylabel("cm above the bar"); ax.set_xticks(x)

    # 3 ---- peak speed ------------------------------------------------------------------
    ax = fig.add_subplot(gs[1, 1])
    pv = [r["peak_conc_v"] for r in reps]
    ax.plot(x, pv, "-o", color=BLUE, lw=2, ms=6)
    ax.plot([n + 1], [atts[-1]["peak_conc_v"]], "X", ms=11, color=ORANGE)
    ax.annotate("failed attempt", (n + 1, atts[-1]["peak_conc_v"]), textcoords="offset points",
                xytext=(-6, 10), ha="right", fontsize=9, color=ORANGE)
    ax.axhline(max(pv) * 0.8, color=TXT2, lw=1, ls=":")
    ax.text(1, max(pv) * 0.8 + 0.01, "20 % velocity loss — the usual 'stop the set' line", fontsize=9, color=TXT2)
    ax.set_title(f"Peak pull speed falls {S['velocity_loss_pct']:.0f} %")
    ax.set_xlabel("rep"); ax.set_ylabel("m/s"); ax.set_xticks(list(x) + [n + 1])

    # 4 ---- tempo -----------------------------------------------------------------------
    ax = fig.add_subplot(gs[1, 2])
    ax.bar(x - 0.22, [r["t_concentric"] for r in reps], width=0.2, color=AQUA, label="up")
    ax.bar(x, [r["t_top_hold"] for r in reps], width=0.2, color=YELLOW, label="hold")
    ax.bar(x + 0.22, [r["t_eccentric"] for r in reps], width=0.2, color=BLUE, label="down")
    ax.set_title("Tempo — the pull slows, the pause stays")
    ax.set_xlabel("rep"); ax.set_ylabel("seconds"); ax.set_xticks(x)
    ax.legend(frameon=False, fontsize=9, ncol=3, loc="upper left")

    # 5 ---- shoulder tilt ---------------------------------------------------------------
    ax = fig.add_subplot(gs[2, 0])
    st = [r["sh_tilt_top"] for r in reps]
    sb = [r["sh_tilt_bottom"] for r in reps]
    ax.plot(x, st, "-o", color=ORANGE, lw=2, ms=6)
    ax.plot(x, sb, "-o", color=BLUE, lw=1.6, ms=5)
    ax.axhline(AS["sh_tilt_standing_deg"], color=TXT2, ls="--", lw=1.2)
    ax.text(n, AS["sh_tilt_standing_deg"] + 0.15, "standing on the floor", fontsize=9, color=TXT2, ha="right")
    ax.text(1, max(st) + 0.2, "at the top", color=ORANGE, fontsize=10)
    ax.text(1, min(sb) - 0.5, "at the hang", color=BLUE, fontsize=10)
    ax.set_title("Shoulder line tilt  (+ = the person's LEFT shoulder is lower)")
    ax.set_xlabel("rep"); ax.set_ylabel("degrees"); ax.set_xticks(x)

    # 6 ---- ear-to-shoulder L vs R ------------------------------------------------------
    ax = fig.add_subplot(gs[2, 1])
    w = 0.36
    ax.bar(x - w / 2, [r["ear_sh_top_l"] for r in reps], width=w, color=BLUE, label="left")
    ax.bar(x + w / 2, [r["ear_sh_top_r"] for r in reps], width=w, color=ORANGE, label="right")
    ax.axhline(AS["ear_sh_stand_l"], color=BLUE, ls="--", lw=1.2)
    ax.axhline(AS["ear_sh_stand_r"], color=ORANGE, ls="--", lw=1.2)
    ax.set_title(f"Ear to shoulder at the top — {AS['ear_sh_top_index_pct']:.0f} % apart\n"
                 f"(dashed = the same distance standing)")
    ax.set_xlabel("rep"); ax.set_ylabel("cm"); ax.set_xticks(x)
    ax.legend(frameon=False, fontsize=9, ncol=2, loc="lower left")

    # 7 ---- elbow 2D vs 3D --------------------------------------------------------------
    ax = fig.add_subplot(gs[2, 2])
    ax.plot(x, [r["elbow_top_l"] for r in reps], "-o", color=BLUE, lw=2, ms=5)
    ax.plot(x, [r["elbow_top_r"] for r in reps], "-o", color=ORANGE, lw=2, ms=5)
    ax.plot(x, [r["elbow2d_top_l"] for r in reps], "--s", color=BLUE, lw=1.2, ms=4, alpha=0.75)
    ax.plot(x, [r["elbow2d_top_r"] for r in reps], "--s", color=ORANGE, lw=1.2, ms=4, alpha=0.75)
    ax.set_title("Elbow angle at the top — the 3D model says 20° apart,\nthe image plane says 2°. Unresolved.")
    ax.set_xlabel("rep"); ax.set_ylabel("degrees"); ax.set_xticks(x)
    ax.text(0.02, 0.52, "solid = 3D model estimate\ndashed = measured in the image",
            transform=ax.transAxes, fontsize=9, color=TXT2)

    # 8 ---- bar-path drift --------------------------------------------------------------
    ax = fig.add_subplot(gs[3, 0])
    ax.bar(x - w / 2, [r["hip_off_top_cm"] for r in reps], width=w, color=VIOLET, label="hips")
    ax.bar(x + w / 2, [r["sh_off_top_cm"] for r in reps], width=w, color=GREEN, label="shoulders")
    ax.axhline(0, color=TXT, lw=1.2)
    ax.set_title("Body offset from the middle of the grip, at the top\n(+ = toward the person's left)")
    ax.set_xlabel("rep"); ax.set_ylabel("cm"); ax.set_xticks(x)
    ax.legend(frameon=False, fontsize=9, ncol=2, loc="lower left")

    # 9 ---- hip sway --------------------------------------------------------------------
    ax = fig.add_subplot(gs[3, 1])
    ax.bar(x, [r["hip_sway_cm"] for r in reps], color=[AQUA if r["hip_sway_cm"] <= 6 else YELLOW for r in reps], width=0.72)
    ax.axhline(6, color=TXT2, ls=":", lw=1.2)
    ax.text(0.4, 6.2, "6 cm — still 'strict' by eye", fontsize=9, color=TXT2)
    ax.set_title(f"Hip travel during the rep — mean {S['mean_hip_sway_cm']:.1f} cm: no swing kip")
    ax.set_xlabel("rep"); ax.set_ylabel("cm"); ax.set_xticks(x)

    # 10 ---- modelled muscle temperature ------------------------------------------------
    ax = fig.add_subplot(gs[3, 2])
    ms = sorted([(m, v["delta_T_C"], v["painted"]) for m, v in tsum["muscles"].items()], key=lambda z: z[1])
    ax.barh([m[0] for m in ms], [m[1] for m in ms],
            color=[RED if m[2] else GRID for m in ms])
    ax.set_title(f"Modelled muscle temperature rise over the set\n"
                 f"({tsum['total_heat_kj']:.0f} kJ of heat — a model, not a camera)")
    ax.set_xlabel("°C above the start"); ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", labelsize=9)

    # 11 ---- temperature over time ------------------------------------------------------
    ax = fig.add_subplot(gs[4, :2])
    series = [("forearm flexors", ORANGE), ("latissimus dorsi", RED), ("biceps brachii", YELLOW),
              ("trapezius", BLUE), ("pectoralis major", VIOLET), ("rectus abdominis", GREEN)]
    lab_y = []
    for m, col in series:
        ax.plot(t[h0:h1], Tm[m][h0:h1], color=col, lw=2)
        y = Tm[m][h1 - 1]
        while any(abs(y - z) < 0.09 for z in lab_y):
            y -= 0.09
        lab_y.append(y)
        ax.annotate(f"{m}  +{Tm[m][h1-1]:.2f}", (t[h1 - 1], Tm[m][h1 - 1]), xytext=(t[h1] + 1.2, y),
                    color=col, fontsize=9, va="center",
                    arrowprops=dict(arrowstyle="-", color=col, lw=0.8, shrinkA=0, shrinkB=2))
    for r in atts:
        ax.axvline(r["t_top"], color=GRID, lw=0.8, zorder=0)
    ax.set_title("Modelled temperature climbs through the set and never falls\n"
                 "(perfusion carries off far less than the muscles make in 53 s)")
    ax.set_xlabel("seconds"); ax.set_ylabel("°C above the start"); ax.set_xlim(t[h0], t[h1] + 12)

    # 12 ---- the judge's card -----------------------------------------------------------
    ax = fig.add_subplot(gs[4, 2]); ax.axis("off")
    lines = [
        ("Reps counted", f"{S['reps']}  (+1 failed)"),
        ("Chin above / at / short", f"{TC['chin_above']} / {TC['chin_at']} / {TC['chin_short']}"),
        ("Mean chin vs bar", f"{S['mean_chin_cm']:+.1f} cm"),
        ("Full lock-out", f"{TC['lockouts']} / {S['reps']}"),
        ("Kipping (swing)", f"none — hips travel {TC['hip_sway_mean_cm']:.1f} cm"),
        ("Legs", f"knees tuck {TC['leg_tuck_deg']:.0f}° each pull"),
        ("Grip width", f"{TC['grip_ratio']:.2f} × shoulders"),
        ("Shoulders shrugged at top", f"L {TC['shrug_top_vs_standing_l']:+.1f} / R {TC['shrug_top_vs_standing_r']:+.1f} cm"),
        ("Neck craned at top", f"{TC['neck_crane_cm']:+.1f} cm"),
        ("Velocity loss", f"{TC['velocity_loss_pct']:.0f} %"),
        ("Set taken to failure", "yes"),
    ]
    ax.text(0, 1.0, "JUDGE'S CARD", fontsize=13, fontweight="bold", color=TXT, va="top")
    ax.text(0, 0.95, "USMC PFT pull-up standard", fontsize=9.5, color=TXT2, va="top")
    for i, (k, v) in enumerate(lines):
        y = 0.87 - i * 0.070
        ax.text(0, y, k, fontsize=10, color=TXT2, va="top")
        ax.text(1.0, y, v, fontsize=10, color=TXT, va="top", ha="right", fontweight="bold")

    # 13 ---- measured chest flush vs the modelled temperature ---------------------------
    if REDN:
        ax = fig.add_subplot(gs[5, :2])
        good = [p for p in REDN["per_rep"] if p.get("valid", True)]
        xr = [p["t"] for p in good]; yr = [p["corrected"] for p in good]
        ax.plot([REDN["per_rep"][0]["t"] - 6], [REDN["baseline"]["corrected"]], "s", ms=9,
                color=TXT2, zorder=6)
        ax.annotate("standing,\nbefore the set", (REDN["per_rep"][0]["t"] - 6, REDN["baseline"]["corrected"]),
                    textcoords="offset points", xytext=(6, -26), fontsize=9, color=TXT2)
        ax.plot(xr, yr, "-o", color=RED_C, lw=2.5, ms=7, zorder=5)
        ax.plot([p["t"] for p in good], [p["wall"] for p in good], "-o", color=TXT2, lw=1.4, ms=4)
        ax.annotate("wall control, same frame", (xr[len(xr) // 2], good[len(xr) // 2]["wall"]),
                    textcoords="offset points", xytext=(0, 12), fontsize=9, color=TXT2, ha="center")
        ax2 = ax.twiny(); ax2.axis("off")
        ax.set_title("Measured chest flush rises and then plateaus\n"
                     f"(r = {REDN.get('r_with_modelled_temp', 0):.2f} against the modelled muscle temperature; "
                     f"the wall control moves the other way)")
        ax.set_xlabel("seconds"); ax.set_ylabel("redness index  (R−G)/(R+G) × 1000")
        for p in REDN["per_rep"]:
            if not p.get("valid", True):
                ax.annotate("dropped: he crosses\nthe control patch", (p["t"], p["corrected"]),
                            textcoords="offset points", xytext=(-6, -30), fontsize=8.5,
                            color=ORANGE, ha="right")
                ax.plot([p["t"]], [p["corrected"]], "x", ms=9, color=ORANGE)
        ax = fig.add_subplot(gs[5, 2]); ax.axis("off")
        ax.text(0, 1.0, "MEASURED, NOT MODELLED", fontsize=13, fontweight="bold", color=TXT, va="top")
        txt = ("The one signal here that comes from the pixels rather than from the literature. "
               "Skin over working muscle reddens as blood is routed to it. Each point is the "
               "dead hang after a rep, where pose and lighting repeat; the index is "
               "(R−G)/(R+G), which ignores brightness; and the same index on a fixed patch of "
               "wall in the same frame is subtracted, so an exposure or white-balance shift "
               "cancels.\n\nIt is still exploratory: the chest is partly hair, he moves into "
               "the lintel's shadow at the top of every rep, and one sample had to be dropped "
               "because he passes in front of the control patch as he drops off the bar.")
        ax.text(0, 0.90, txt, fontsize=10, color=TXT2, va="top", wrap=True, linespacing=1.5)
    fig.savefig(out, facecolor=SURF)
    print("wrote", out)


if __name__ == "__main__":
    main()
