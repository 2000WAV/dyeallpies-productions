"""
Dashboard for a push-up set (analysis.json from analyze_pushups.py, the model from pushup_thermal.py).

    python render_pushup_dashboard.py <analysis.json> <out.png>

Eight panels: the shoulder-height trace; the bottom of every rep (elbow angle against the USMC's
90 deg, shoulder height); peak push speed per rep; tempo; the body line (hip sag) per rep; the
hand force and the two joint moments through one rep; the modelled fatigued pools; the
technique card. Palette and rules from the dataviz skill: one idea per panel, no dual axes,
direct labels rather than legends where it fits.
"""
import sys, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pushup_thermal as TH

BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = \
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"
SURF, TXT, TXT2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"


def main():
    A = json.load(open(sys.argv[1])); out = sys.argv[2]
    S, atts, sig = A["summary"], A["reps"], A["signals"]
    reps = [r for r in atts if r.get("rep")]
    TC = S["technique"]; cam = S["camera"]
    t = np.array(sig["t"]); n = len(reps); x = np.arange(1, n + 1)
    Mo = TH.model(A); fps = S["fps"]
    for f in ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/segoeuib.ttf"):
        fm.fontManager.addfont(f)
    plt.rcParams["font.family"] = "Segoe UI"
    plt.rcParams.update({"axes.edgecolor": GRID, "axes.labelcolor": TXT2, "xtick.color": TXT2,
                         "ytick.color": TXT2, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titleweight": "bold", "axes.titlecolor": TXT, "axes.titlesize": 13,
                         "axes.titlelocation": "left", "figure.facecolor": SURF, "axes.facecolor": SURF,
                         "grid.color": GRID, "axes.grid": True, "axes.axisbelow": True,
                         "xtick.labelsize": 10, "ytick.labelsize": 10})
    fig = plt.figure(figsize=(16, 20), dpi=110)
    gs = fig.add_gridspec(5, 3, height_ratios=[1.15, 1, 1, 1, 1], hspace=0.62, wspace=0.32,
                          left=0.055, right=0.985, top=0.935, bottom=0.035)
    fig.text(0.055, 0.972, f"Push-up set · {S['reps']} reps · judged to the USMC standard · {TC['depth_pass']}/{n} past parallel, {TC['lockouts']}/{n} locked, {TC['straight']}/{n} straight",
             fontsize=22, fontweight="bold", color=TXT)
    fig.text(0.055, 0.952,
             f"MediaPipe Pose heavy on {S['tracked_frames']}/{S['frames']} frames · YOLOv8m-pose hip track r = {S.get('yolo_mp_hip_corr', 0):.2f} against MediaPipe's · "
             f"phone on the floor at the head end (f {cam['f_px']:.0f} px, {cam['pitch_up_deg']:.1f}° up, lens {cam['height_m']*100:.0f} cm) · the shoulders' depth from the hips' width and a rigid 58.7 cm trunk, "
             f"the wrists on the floor, the elbow angle by the law of cosines · cm are estimates; °C and the pools are a model", fontsize=11, color=TXT2)
    good = [r["depth_pass"] and r["parallel_pass"] and r["lockout"] and r["straight"] for r in reps]
    col = [AQUA if g else YELLOW for g in good]

    # 1 ---- height trace ----
    ax = fig.add_subplot(gs[0, :])
    hp = np.array(sig["sh_h"]) * 100; s0, s1 = sig["set0"], sig["set1"]
    ax.plot(t[s0:s1], hp[s0:s1], color=TXT, lw=1.6)
    nose = np.array(sig["nose_h"]) * 100
    ax.plot(t[s0:s1], np.clip(nose[s0:s1], -3, 80), color=VIOLET, lw=0.9, alpha=0.7)
    ax.text(t[s1] - 0.4, 6, "nose (measured, the ear-width scale)", color=VIOLET, fontsize=9, ha="right")
    for r in atts:
        c = AQUA if (r["depth_pass"] and r["parallel_pass"] and r["lockout"] and r["straight"]) else YELLOW
        ax.plot(r["t_bottom"], hp[r["f_bottom"]], "o", ms=8, color=c, mec="white", mew=1.5, zorder=5)
        if r["rep"] % 5 == 0 or r["rep"] == 1:
            ax.annotate(str(r["rep"]), (r["t_bottom"], hp[r["f_bottom"]]), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=9, color=TXT2)
    ax.axhline(0, color=GRID, lw=1)
    ax.set_title("Shoulder height above the floor through the set  (bottoms marked; the hips vanish behind the head there, the shoulders stay in view beside it)")
    ax.set_xlabel("seconds"); ax.set_ylabel("cm"); ax.set_ylim(-5, 70)

    # 2 ---- the bottom of every rep ----
    ax = fig.add_subplot(gs[1, 0])
    eb = [r["elbow_bottom"] for r in reps]
    ax.bar(x, eb, color=col, width=0.72, alpha=0.6)
    ax.axhline(90, color=TXT, lw=1.4)
    ax.text(0.02, 91, "USMC: upper arms parallel = 90°", color=TXT, fontsize=9.5, transform=ax.get_yaxis_transform(), va="bottom")
    ax.set_ylim(0, 120)
    ax.set_title(f"Elbow at the bottom: {TC['depth_pass']}/{n} under 90°, mean {TC['mean_elbow_bottom']:.0f}°")
    ax.set_xlabel("rep"); ax.set_ylabel("degrees (law of cosines)"); ax.set_xticks(x[::5])

    # 3 ---- peak speed ----
    ax = fig.add_subplot(gs[1, 1])
    pv = [r["peak_conc_v"] for r in reps]
    ax.plot(x, pv, "-o", color=BLUE, lw=2, ms=5)
    k = int(np.argmax(pv))
    ax.annotate("fastest", (x[k], pv[k]), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=9, color=BLUE)
    ax.axhline(0.75 * max(pv), color=YELLOW, lw=1.2, ls="--")
    ax.text(n, 0.75 * max(pv) + 0.01, "−25 % (the pull-up literature's training cut-off)", color=YELLOW, fontsize=8.5, ha="right")
    ax.set_title(f"Peak push speed: −{S['velocity_loss_vs_fastest_pct']:.0f} % vs the fastest by the end")
    ax.set_xlabel("rep"); ax.set_ylabel("m/s"); ax.set_xticks(x[::5]); ax.set_ylim(0, max(pv) * 1.25)

    # 4 ---- tempo ----
    ax = fig.add_subplot(gs[1, 2])
    ax.bar(x - 0.22, [r["t_eccentric"] for r in reps], width=0.2, color=BLUE, label="down")
    ax.bar(x, [r["t_bottom_hold"] for r in reps], width=0.2, color=YELLOW, label="bottom")
    ax.bar(x + 0.22, [r["t_concentric"] for r in reps], width=0.2, color=AQUA, label="up")
    ax.set_title("Tempo — the descents lengthen from rep 22")
    ax.set_xlabel("rep"); ax.set_ylabel("seconds"); ax.set_xticks(x[::5]); ax.set_ylim(0, 4)
    ax.legend(frameon=False, fontsize=9, ncol=3, loc="upper left")

    # 5 ---- body line ----
    ax = fig.add_subplot(gs[2, 0])
    sag = [r["hip_sag_cm"] if r["hip_sag_cm"] is not None else 0 for r in reps]
    ax.bar(x, sag, color=[AQUA if r["straight"] else ORANGE for r in reps], width=0.72, alpha=0.6)
    ax.axhline(0, color=TXT, lw=1.2)
    ax.set_title(f"Hip sag below the shoulder–toe line ({TC['mean_hip_sag_cm']:.1f} cm mean)")
    ax.set_xlabel("rep"); ax.set_ylabel("cm (− = hips below the line)"); ax.set_xticks(x[::5])

    # 6 ---- one rep's mechanics ----
    ax = fig.add_subplot(gs[2, 1:])
    r5 = reps[4]; a0, b0 = r5["f_start"] - 5, r5["f_end"] + 5
    tt = t[a0:b0] - t[r5["f_start"]]
    ax.plot(tt, Mo["K"]["F"][a0:b0], color=TXT, lw=1.8, label="hand force, both hands (N)")
    ax.plot(tt, Mo["M_el"][a0:b0] * 5, color=ORANGE, lw=1.8, label="elbow moment × 5 (N·m)")
    ax.plot(tt, Mo["M_sh"][a0:b0] * 5, color=VIOLET, lw=1.8, label="shoulder moment × 5 (N·m)")
    ax.axvspan(t[r5["f_ecc_end"]] - t[r5["f_start"]], t[r5["f_conc_start"]] - t[r5["f_start"]], color=GRID, alpha=0.6)
    ax.text(t[r5["f_ecc_end"]] - t[r5["f_start"]] + 0.02, ax.get_ylim()[1] * 0.02 + 20, "bottom", color=TXT2, fontsize=9)
    ax.set_title(f"Rep 5, the mechanics behind the colour: hand force {Mo['K']['F'][a0:b0].max():.0f} N peak; per arm elbow {Mo['M_el'][a0:b0].max():.0f} N·m, shoulder {Mo['M_sh'][a0:b0].max():.0f} N·m")
    ax.set_xlabel("seconds from the start of the descent"); ax.set_ylabel("N  ·  N·m × 5")
    ax.legend(frameon=False, fontsize=9, loc="upper right")

    # 7 ---- fatigued pools ----
    ax = fig.add_subplot(gs[3, :2])
    for m, c in (("pectoralis major", RED), ("triceps", ORANGE), ("anterior deltoid", MAGENTA), ("serratus anterior", VIOLET), ("forearm extensors", BLUE), ("rectus abdominis", AQUA)):
        ax.plot(t[s0:s1], Mo["MF"][m][s0:s1] * 100, color=c, lw=1.8)
        ax.text(t[s1] + 0.3, Mo["MF"][m][s1] * 100, m, color=c, fontsize=9, va="center")
    ax.set_xlim(t[s0], t[s1] + 14)
    ax.set_title("Modelled fatigued share of the motor-unit pool (Xia & Frey-Law 2008; Frey-Law et al. 2012 rates): nothing recovers under load")
    ax.set_xlabel("seconds"); ax.set_ylabel("% fatigued")

    # 8 ---- temperature ----
    ax = fig.add_subplot(gs[3, 2])
    Tend = sorted(((m, float(Mo["T"][m].max())) for m in TH.MUSCLES if m in TH.PAINTED), key=lambda kv: -kv[1])[:10]
    ax.barh([m for m, _ in Tend][::-1], [v for _, v in Tend][::-1], color=ORANGE, alpha=0.7)
    ax.set_title("Temperature rise, top ten (°C, a model)")
    ax.set_xlabel("°C")

    # 9 ---- technique card ----
    ax = fig.add_subplot(gs[4, :]); ax.axis("off")
    lines = [
        f"USMC PFT push-up: upper arms at least parallel at the bottom, arms fully extended at the top, body straight.  {TC['depth_pass']}/{n} depth · {TC['parallel_pass']}/{n} parallel · {TC['lockouts']}/{n} lock-out · {TC['straight']}/{n} straight",
        f"Shoulder at the bottom {TC['mean_sh_bottom_cm']:.0f} cm above the floor (the elbow at {TC['mean_elbow_h_bottom_cm']:.0f} cm: past parallel by {-TC['mean_upper_arm_tilt_bottom']:.0f}°), nose at the floor ({TC['mean_nose_bottom_cm']:+.0f} cm); shoulder at the top {TC['mean_sh_top_cm']:.0f} cm; range {S['mean_rom_cm']:.0f} cm",
        f"Elbow angle {TC['mean_elbow_bottom']:.0f}° at the bottom, {TC['mean_elbow_top']:.0f}° at the top by the law of cosines (MediaPipe's 3D angle {TC['mean_elbow_top_mediapipe']:.0f}°); elbow flare {TC['mean_flare_deg']:.0f}°; hands {S['hand_width_cm']:.0f} cm apart = {S['hand_to_shoulder_ratio']:.2f} × the shoulder landmarks",
        f"Tempo {S['mean_eccentric']:.2f} s down · {S['mean_bottom_hold']:.2f} s bottom · {S['mean_concentric']:.2f} s up · {S['mean_top_hold']:.2f} s at the top; {S['reps_per_min']:.1f} reps/min over {S['set_duration']:.0f} s; peak speed {S['peak_v_max']:.2f} m/s, −{S['velocity_loss_vs_fastest_pct']:.0f} % by the end",
        f"Hands carry 72–77 % of body weight (Eckel 2017; the moment balance here says {S['hand_frac_top']*100:.0f}–{S['hand_frac_bottom']*100:.0f} %); peak {S['peak_force_bw_max']:.2f} BW; about 0.8 kcal a rep (Nakagata 2022, measured), {Mo['budget_kj']/4.184:.0f} kcal over the set as heat; peak power {S['peak_power_w_max']:.0f} W",
        f"The colour on the body = the model's non-resting share of each muscle's pool (active + fatigued) with a temperature floor, on set #1's blue → red scale. A model, not a thermal camera. PUSHUP-MODEL.md ranks the assumptions: the hand position (a tape would settle it), the shoulder strength factor, the moment arms, the flare.",
    ]
    for k, ln in enumerate(lines):
        ax.text(0.0, 0.95 - k * 0.17, ln, fontsize=11, color=TXT if k < 5 else TXT2, transform=ax.transAxes, va="top")
    fig.savefig(out, facecolor=SURF)
    print("wrote", out)


if __name__ == "__main__":
    main()
