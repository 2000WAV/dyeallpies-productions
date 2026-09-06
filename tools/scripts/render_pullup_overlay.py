"""
Render the pull-up analysis reel: original footage full-bleed (1080x1920) with the
tracked skeleton, a rep counter, live phase / elbow / speed / height readouts, a
progressive height chart, a per-rep grade card, and a frozen summary card at the end.

    python render_pullup_overlay.py <video> <pose_mp.npz> <analysis.json> <out.mp4> [hold_s] [heat=masks.npz] [preview=f1,f2,...]

heat=  paints the "muscle heat" overlay (see pullup_heat.py) inside the person mask.
preview=  writes those frame numbers as PNGs next to <out.mp4> instead of encoding.

Frames are piped raw to ffmpeg (NVENC); original audio is muxed back in and padded
with silence over the frozen outro.
"""
import sys, json, subprocess
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pullup_heat import HeatPainter, effort_from_speed, definition_map, fatigue_curve, LUT
from pullup_look import LookPass

FONT_B = "C:/Windows/Fonts/segoeuib.ttf"
FONT_S = "C:/Windows/Fonts/seguisb.ttf"
FONT_R = "C:/Windows/Fonts/segoeui.ttf"
FONT_SYM = "C:/Windows/Fonts/seguisym.ttf"
VERDICT = {"above": ("CHIN ABOVE BAR", "\u2713"), "at": ("CHIN AT BAR", "~"), "short": ("CHIN SHORT", "\u2717")}
VERDICT_COL = {"above": (25, 158, 112), "at": (201, 133, 0), "short": (217, 89, 38)}

# palette (dataviz dark steps)
BLUE = (57, 135, 229); ORANGE = (217, 89, 38); AQUA = (25, 158, 112); YELLOW = (201, 133, 0)
RED = (230, 103, 103); WHITE = (255, 255, 255); MUTED = (195, 194, 183); INK = (26, 26, 25)
PHASE_COL = {"PULL": AQUA, "HOLD": YELLOW, "LOWER": BLUE, "HANG": MUTED, "HANDS ON BAR": MUTED, "LOADING": YELLOW, "SETUP": MUTED, "DONE": MUTED}
GRADE_COL = {"A": AQUA, "B": YELLOW, "C": ORANGE, "D": RED}

# skeleton edges: (a, b, colour)  - MediaPipe ids; person's LEFT = blue, RIGHT = orange
EDGES = [(11, 13, BLUE), (13, 15, BLUE), (12, 14, ORANGE), (14, 16, ORANGE),
         (11, 12, WHITE), (11, 23, WHITE), (12, 24, WHITE), (23, 24, WHITE),
         (23, 25, BLUE), (25, 27, BLUE), (24, 26, ORANGE), (26, 28, ORANGE),
         (15, 19, BLUE), (16, 20, ORANGE), (27, 31, BLUE), (28, 32, ORANGE)]
JOINTS = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]


def font(path, size):
    return ImageFont.truetype(path, size)


def rounded(draw, box, r, fill):
    draw.rounded_rectangle(box, radius=r, fill=fill)


_FONT_CACHE = {}
def fit(draw, text, path, size, max_w, min_size=18):
    """Largest font <= size (same face) whose rendered text fits in max_w px."""
    while size > min_size:
        key = (path, size)
        if key not in _FONT_CACHE:
            _FONT_CACHE[key] = ImageFont.truetype(path, size)
        if draw.textlength(text, font=_FONT_CACHE[key]) <= max_w:
            return _FONT_CACHE[key]
        size -= 2
    return _FONT_CACHE.setdefault((path, min_size), ImageFont.truetype(path, min_size))


def main():
    video, npz, ajson, out = sys.argv[1:5]
    hold_s = 3.0; heat_path = None; preview = None; look_on = False; bg_path = None
    for a in sys.argv[5:]:
        if a.startswith("heat="): heat_path = a[5:]
        elif a.startswith("preview="): preview = [int(x) for x in a[8:].split(",")]
        elif a.startswith("look="): look_on = a[5:] not in ("0", "", "no")
        elif a.startswith("bg="): bg_path = a[3:]
        else: hold_s = float(a)
    d = np.load(npz); img = d["img"]; ok = d["ok"]; fps = float(d["fps"])
    W, H = int(d["width"]), int(d["height"])
    P = img[:, :, :2] * np.array([W, H]); V = img[:, :, 3]
    A = json.load(open(ajson)); S = A["summary"]; reps = A["reps"]; sig = A["signals"]
    N = len(img); t = np.array(sig["t"]); sh_y = np.array(sig["sh_y"]); vy = np.array(sig["vy_m"])
    el_l = np.array(sig["elbow_l"]); el_r = np.array(sig["elbow_r"])
    bar_y = S["bar_y"]; hang0, hang1 = sig["hang0"], sig["hang1"]; grab0, load0 = sig["grab0"], sig["load0"]

    # height %: 0 at the loaded dead hang (median of the rep bottoms), 100 at the best top
    hang_ref, top_ref = S["hang_ref_y"], S["top_ref_y"]
    height_pct = np.clip(np.array(sig["height_pct"]), -10, 110)
    chin_bar_pct = (hang_ref - (bar_y + (S["neck_cm"] + S["perspective_cm"]) / 100 * S["px_per_m"])) / (hang_ref - top_ref) * 100
    # energy: each rep's kcal accrues linearly over its pull+lower; the hang costs a little per second
    kcal = np.zeros(N)
    if "kcal" in reps[0]:
        rate = np.zeros(N); rate[hang0:hang1 + 1] = S["hang_kcal_per_s"] / fps
        for r in reps:
            a, b = r["f_start"], r["f_end"]
            rate[a:b + 1] += (r["kcal"] - S["hang_kcal_per_s"] * (b - a + 1) / fps) / (b - a + 1)
        kcal = np.cumsum(rate)

    # measured velocity loss of the latest completed rep vs the best so far, per frame
    vloss = np.zeros(N); best = 0.0
    for r in reps:
        best = max(best, r["peak_conc_v"]); vloss[r["f_end"]:] = (1 - r["peak_conc_v"] / best) * 100

    # per-frame phase, rep count, and rep card window
    phase = ["SETUP"] * N; count = np.zeros(N, int); card = [None] * N
    for i in range(grab0, load0):
        phase[i] = "HANDS ON BAR"
    for i in range(load0, hang0):
        phase[i] = "LOADING"
    for i in range(hang0, hang1 + 1):
        phase[i] = "HANG"
    for r in reps:
        for i in range(r["f_start"], r["f_conc_end"] + 1): phase[i] = "PULL"
        for i in range(r["f_conc_end"] + 1, r["f_ecc_start"]): phase[i] = "HOLD"
        for i in range(r["f_ecc_start"], r["f_end"] + 1): phase[i] = "LOWER"
        count[r["f_top"]:] = r["n"]
        for i in range(r["f_end"], min(N, r["f_end"] + int(1.8 * fps))): card[i] = r
    for i in range(hang1 + 1, N):
        phase[i] = "DONE"

    F = {k: font(*v) for k, v in dict(
        counter=(FONT_B, 190), counter_lbl=(FONT_S, 44), phase=(FONT_B, 60), metric=(FONT_S, 40), metric_v=(FONT_B, 52),
        small=(FONT_S, 30), tiny=(FONT_R, 26), card_t=(FONT_B, 48), card=(FONT_S, 34), grade=(FONT_B, 96),
        title=(FONT_B, 72), sub=(FONT_S, 38), sum_h=(FONT_B, 64), sum_big=(FONT_B, 120), sum_l=(FONT_S, 34), sym=(FONT_SYM, 30)).items()}

    # chart panel geometry (Reels safe box: x 60-936, bottom above y 1500)
    PX0, PY0, PX1, PY1 = 60, 1536, 936, 1822
    CX0, CY0, CX1, CY1 = PX0 + 24, PY0 + 56, PX1 - 24, PY1 - 70
    t_end = t[-1]
    def tx(tt): return CX0 + (CX1 - CX0) * tt / t_end
    def hy(pct): return CY1 - (CY1 - CY0) * np.clip(pct, -5, 105) / 105
    trace_pts = [(tx(t[i]), hy(height_pct[i])) for i in range(N)]

    # heat overlay setup
    painter = None
    if heat_path:
        masks = np.load(heat_path, mmap_mode="r") if heat_path.endswith(".npy") else np.load(heat_path)["masks"]
        effort = effort_from_speed(vy, phase, max(r["peak_conc_v"] for r in reps) * 0.8)
        fatigue = fatigue_curve(reps, N, S.get("set_kcal", 0.0))
        # calibrate "definition" on the loaded hang: 92nd percentile inside the body region
        capc = cv2.VideoCapture(video); refs = []
        for fr in [r["f_bottom1"] for r in reps[:3]]:
            capc.set(cv2.CAP_PROP_POS_FRAMES, fr); got, fm = capc.read()
            if not got: continue
            dm = definition_map(cv2.cvtColor(fm, cv2.COLOR_BGR2GRAY))
            m = cv2.resize(np.asarray(masks[fr])[..., 0] if np.asarray(masks[fr]).ndim == 3 else np.asarray(masks[fr]), (W, H)) > 128
            refs.append(np.percentile(dm[m], 92))
        capc.release()
        painter = HeatPainter(W, H, float(np.median(refs)), alpha=0.96, bar_y=bar_y)
        look = LookPass(W, H) if look_on else None
    plate = None
    if bg_path:
        plate = cv2.resize(cv2.imread(bg_path), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
        # keep the real bar: dark pixels in a band around the bar row of the first frame
        capb = cv2.VideoCapture(video); _, f0 = capb.read(); capb.release()
        g0 = cv2.cvtColor(f0, cv2.COLOR_BGR2GRAY)
        band = np.zeros((H, W), np.uint8); band[max(0, bar_y - 34):bar_y + 34, :] = 1
        barm = ((g0 < 70).astype(np.uint8) * band)
        barm = cv2.morphologyEx(barm, cv2.MORPH_CLOSE, np.ones((5, 21), np.uint8))
        barm = cv2.dilate(barm, np.ones((5, 5), np.uint8))
        bar_mask = cv2.GaussianBlur(barm.astype(np.float32), (0, 0), 1.5)[:, :, None]
        print(f"backdrop: {bg_path}, bar mask {int((barm > 0).sum())} px", flush=True)
        print(f"heat: definition ref {painter.def_ref:.1f}", flush=True)

    # ffmpeg sink
    total = N + int(hold_s * fps)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", f"{fps}",
           "-i", "pipe:0", "-i", video, "-map", "0:v", "-map", "1:a", "-af", "apad", "-shortest",
           "-c:v", "h264_nvenc", "-preset", "p5", "-tune", "hq", "-rc", "vbr", "-cq", "19", "-b:v", "0",
           "-spatial-aq", "1", "-temporal-aq", "1", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
           "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE) if not preview else None
    cap = cv2.VideoCapture(video)
    last = None; last_ok = None

    for i in range(total):
        if i < N:
            got, frame = cap.read()
            if not got:
                frame = last
            last = frame
            fi = i
        else:
            frame = last; fi = N - 1
        f = frame.copy()
        if preview is not None and i not in preview:
            if i > max(preview): break
            continue
        if ok[fi]:
            P_use, V_use = P[fi], V[fi]; last_ok = (P[fi], V[fi])
        else:
            P_use, V_use = last_ok if last_ok is not None else (P[fi], V[fi])
        if plate is not None and heat_path:
            comp0 = np.asarray(masks[fi])
            alpha_full = cv2.resize(comp0[..., 0], (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255
            z = 1.0 + 0.06 * (i / max(1, total - 1))                     # slow push-in
            cw, ch = int(W / z), int(H / z); x0 = (W - cw) // 2; y0 = (H - ch) // 2
            pl = cv2.resize(plate[y0:y0 + ch, x0:x0 + cw], (W, H), interpolation=cv2.INTER_LINEAR)
            keep = np.clip(alpha_full[:, :, None] + bar_mask, 0, 1)
            f = np.clip(pl * (1 - keep) + f.astype(np.float32) * keep, 0, 255).astype(np.uint8)
        if painter is not None and last_ok is not None:
            comp = np.asarray(masks[fi])
            f = painter.paint(f, comp, P_use, V_use, float(effort[fi]), float(fatigue[fi]))
            if look is not None:
                alpha_full = cv2.resize(comp[..., 0], (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255
                rim = tuple(int(c) for c in LUT[int((0.18 + 0.6 * float(fatigue[fi])) * 255), 0])
                f = look.apply(f, alpha_full, rim, 1.0, i, keep_colour=plate is not None)

        # --- skeleton (cv2, anti-aliased, dark underline + colour) ---
        if last_ok is not None:
            Pf, Vf = P_use, V_use
            head_ok = Pf[7, 1] > bar_y + 40 and Pf[8, 1] > bar_y + 40   # ears below the bar -> real
            for a, b, col in EDGES:
                if Vf[a] > 0.5 and Vf[b] > 0.5:
                    pa, pb = tuple(Pf[a].astype(int)), tuple(Pf[b].astype(int))
                    cv2.line(f, pa, pb, INK, 11, cv2.LINE_AA); cv2.line(f, pa, pb, col[::-1], 5, cv2.LINE_AA)
            if head_ok and Vf[7] > 0.5 and Vf[8] > 0.5:
                sm = ((Pf[11] + Pf[12]) / 2).astype(int); em = ((Pf[7] + Pf[8]) / 2).astype(int)
                cv2.line(f, tuple(sm), tuple(em), INK, 11, cv2.LINE_AA); cv2.line(f, tuple(sm), tuple(em), WHITE[::-1], 5, cv2.LINE_AA)
                cv2.circle(f, tuple(em), 12, INK, -1, cv2.LINE_AA); cv2.circle(f, tuple(em), 8, WHITE[::-1], -1, cv2.LINE_AA)
            for j in JOINTS:
                if Vf[j] > 0.5:
                    p = tuple(Pf[j].astype(int))
                    cv2.circle(f, p, 13, INK, -1, cv2.LINE_AA); cv2.circle(f, p, 8, WHITE[::-1], -1, cv2.LINE_AA)
        # bar line
        for x in range(0, W, 36):
            cv2.line(f, (x, bar_y), (min(x + 18, W), bar_y), (255, 255, 255), 2, cv2.LINE_AA)

        # --- PIL overlay ---
        im = Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)).convert("RGBA")
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(ov)
        ph = phase[fi]; pc = PHASE_COL[ph]
        dr.text((W - 150, bar_y - 40), "BAR", font=F["small"], fill=(*WHITE, 230), anchor="ls")

        if ph == "SETUP":
            rounded(dr, (60, 240, 936, 500), 24, (*INK, 200))
            dr.text((84, 262), "PULL UP ANALYSIS", font=fit(dr, "PULL UP ANALYSIS", FONT_B, 72, 828), fill=WHITE)
            dr.text((84, 350), "by Fable and DyeAllPies", font=fit(dr, "by Fable and DyeAllPies", FONT_S, 44, 828), fill=WHITE)
            sub = "33-point pose tracking · 3D angles · EMG heat map" if painter else "33-point pose tracking · 3D joint angles · 30 fps"
            dr.text((84, 416), sub, font=fit(dr, sub, FONT_S, 34, 828), fill=MUTED)
        elif ph != "DONE":
            # counter
            rounded(dr, (60, 240, 420, 470), 24, (*INK, 200))
            dr.text((84, 226), str(count[fi]), font=F["counter"], fill=WHITE)
            dr.text((84, 420), "REPS", font=F["counter_lbl"], fill=MUTED)
            # phase pill
            pw = dr.textlength(ph, font=F["phase"]) + 60
            rounded(dr, (60, 492, 60 + pw, 570), 20, (*pc, 235))
            dr.text((90, 500), ph, font=F["phase"], fill=WHITE if ph in ("PULL", "LOWER") else INK)
            # live metrics column
            y0 = 600
            rows = [("ELBOW", f"{(el_l[fi] + el_r[fi]) / 2:.0f}°", WHITE),
                    ("SPEED", f"{abs(vy[fi]):.2f} m/s", WHITE), ("ENERGY  (rough)", f"{kcal[fi]:.1f} kcal", WHITE),
                    ("FATIGUE  (speed loss)", f"{vloss[fi]:.0f} %", WHITE if vloss[fi] < 20 else YELLOW if vloss[fi] < 35 else ORANGE)]
            rounded(dr, (60, y0 - 16, 480, y0 + len(rows) * 92 - 8), 24, (*INK, 170))
            for k, (lab, val, col) in enumerate(rows):
                yy = y0 + k * 92
                dr.text((84, yy), lab, font=F["small"], fill=MUTED)
                dr.text((84, yy + 30), val, font=fit(dr, val, FONT_B, 52, 372), fill=col)
            # height gauge (right side, inside the safe box)
            gx0, gx1, gy0, gy1 = 872, 924, 620, 1120
            rounded(dr, (gx0 - 10, gy0 - 10, gx1 + 10, gy1 + 10), 18, (*INK, 170))
            rounded(dr, (gx0, gy0, gx1, gy1), 12, (60, 60, 58, 255))
            hp = float(np.clip(height_pct[fi], 0, 105)) / 105
            rounded(dr, (gx0, gy1 - (gy1 - gy0) * hp, gx1, gy1), 12, (*pc, 255))
            cy = gy1 - (gy1 - gy0) * np.clip(chin_bar_pct, 0, 105) / 105
            dr.line((gx0 - 8, cy, gx1 + 8, cy), fill=WHITE, width=3)
            dr.text((gx0 - 16, cy - 30), "CHIN", font=F["tiny"], fill=WHITE, anchor="ra")
            dr.text((gx0 - 16, cy - 4), "@BAR", font=F["tiny"], fill=WHITE, anchor="ra")

        # rep card
        r = card[fi]
        if r is not None and ph != "DONE":
            age = (fi - r["f_end"]) / fps
            a = int(255 * min(1.0, age / 0.15))
            x0, y0, x1, y1 = 60, 1192, 936, 1478
            rounded(dr, (x0, y0, x1, y1), 24, (*INK, int(215 * a / 255)))
            vk = r.get("chin_verdict", "at"); vtxt, vsym = VERDICT[vk]; gc = VERDICT_COL[vk]
            if vk == "short":
                vtxt = f"CHIN {-(r['chin_est_cm'] + S['perspective_cm']):.0f} CM SHORT"
            bx0 = x1 - 330
            rounded(dr, (bx0, y0 + 18, x1 - 24, y1 - 18), 20, (*gc, a))
            bcx = (bx0 + x1 - 24) // 2
            dr.text((bcx, y0 + 34), vsym, font=fit(dr, vsym, FONT_SYM, 96, 200), fill=(*INK, a), anchor="ma")
            dr.text((bcx, y0 + 150), vtxt, font=fit(dr, vtxt, FONT_B, 34, x1 - 24 - bx0 - 24), fill=(*INK, a), anchor="ma")
            dr.text((bcx, y1 - 30), f"efficiency {r['efficiency']:.0f}/100", font=fit(dr, f"efficiency {r['efficiency']:.0f}/100", FONT_R, 24, x1 - 24 - bx0 - 24), fill=(*INK, a), anchor="ms")
            dr.text((x0 + 24, y0 + 18), f"REP {r['n']}", font=F["card_t"], fill=(*WHITE, a))
            lock = "FULL LOCK-OUT" if r["lockout"] else "NO LOCK-OUT"
            cx = x0 + 24
            for txt, good in ((lock, r["lockout"]),):
                col = AQUA if good else ORANGE
                tw = dr.textlength(txt, font=F["small"]) + 28
                rounded(dr, (cx, y0 + 84, cx + tw, y0 + 126), 12, (*col, a))
                dr.text((cx + 14, y0 + 89), txt, font=F["small"], fill=(*INK, a))
                cx += tw + 12
            lines = [f"up {r['t_concentric']:.1f} s   down {r['t_eccentric']:.1f} s   peak {r['peak_conc_v']:.2f} m/s",
                     f"sway {r['hip_sway_cm']:.0f} cm   elbow gap {r['elbow_asym_mean']:.0f}°"]
            if "kcal" in r:
                lines.insert(1, f"≈ {r['kcal']:.2f} kcal   effort ×{r['effort_x']:.1f}   {r['mean_power_w']:.0f} W")
            for k, ln in enumerate(lines):
                dr.text((x0 + 24, y0 + 142 + k * 44), ln, font=fit(dr, ln, FONT_S, 34, x1 - x0 - 380), fill=(*MUTED, a))

        # heat legend
        if painter is not None and ph not in ("SETUP", "DONE"):
            lx0, lx1, ly = 744, 936, 1136
            rounded(dr, (lx0, ly - 8, lx1, ly + 46), 12, (*INK, 200))
            dr.text((lx0 + 12, ly - 4), "MUSCLE HEAT", font=F["tiny"], fill=WHITE)
            grad = Image.fromarray(cv2.cvtColor(cv2.LUT(cv2.merge([np.tile(np.arange(256, dtype=np.uint8), (10, 1))] * 3), LUT), cv2.COLOR_BGR2RGB)).resize((lx1 - lx0 - 24, 12))
            ov.paste(grad.convert("RGBA"), (lx0 + 12, ly + 26))
            dr = ImageDraw.Draw(ov)

        # chart panel (progressive reveal)
        rounded(dr, (PX0, PY0, PX1, PY1), 24, (*INK, 200))
        dr.text((PX0 + 24, PY0 + 14), "SHOULDER HEIGHT", font=F["small"], fill=MUTED)
        dr.text((PX0 + 24 + dr.textlength("SHOULDER HEIGHT", font=F["small"]) + 18, PY0 + 18), "0 % = dead hang · 100 % = best rep", font=F["tiny"], fill=MUTED)
        for pct, lab in ((0, "0"), (50, "50"), (100, "100")):
            yy = hy(pct); dr.line((CX0, yy, CX1, yy), fill=(70, 70, 68), width=1)
            dr.text((CX0 - 6, yy), lab, font=F["tiny"], fill=MUTED, anchor="rm")
        cyb = hy(chin_bar_pct); dr.line((CX0, cyb, CX1, cyb), fill=(*WHITE, 120), width=2)
        dr.text((CX1, cyb + 4), "chin at bar", font=F["tiny"], fill=(*WHITE, 180), anchor="ra")
        upto = fi + 1
        if upto > 1:
            pts = trace_pts[hang0 if fi >= hang0 else 0:upto]
            if len(pts) > 1:
                dr.line(pts, fill=WHITE, width=3, joint="curve")
        for r2 in reps:
            if r2["f_top"] <= fi:
                x, y = trace_pts[r2["f_top"]]
                gc = VERDICT_COL[r2.get("chin_verdict", "at")]
                dr.ellipse((x - 8, y - 8, x + 8, y + 8), fill=gc, outline=INK, width=2)
                dr.text((x, y - 14), str(r2["n"]), font=F["tiny"], fill=WHITE, anchor="ms")
        px = tx(t[fi]); dr.line((px, CY0, px, CY1), fill=(*pc, 220), width=2)
        # rep chips
        for k, r2 in enumerate(reps):
            cx = CX0 + k * ((CX1 - CX0) / len(reps)); cw = (CX1 - CX0) / len(reps) - 8
            done = r2["f_end"] <= fi
            vk2 = r2.get("chin_verdict", "at")
            col = VERDICT_COL[vk2] if done else (60, 60, 58)
            rounded(dr, (cx, PY1 - 56, cx + cw, PY1 - 16), 10, (*col, 255))
            dr.text((cx + cw / 2, PY1 - 36), (VERDICT[vk2][1] if done else str(k + 1)), font=(F["sym"] if done else F["small"]),
                    fill=INK if done else MUTED, anchor="mm")

        # outro summary (frozen tail + DONE phase)
        if ph == "DONE":
            age = (fi - hang1) / fps + (i - N + 1) / fps if i >= N else (fi - hang1) / fps
            a = int(255 * min(1.0, age / 0.4))
            rounded(dr, (60, 240, 936, 1130), 28, (*INK, int(225 * a / 255)))
            dr.text((498, 270), "SET SUMMARY", font=F["sum_h"], fill=(*WHITE, a), anchor="ma")
            dr.text((498, 342), "Pull Up Analysis by Fable and DyeAllPies", font=fit(dr, "Pull Up Analysis by Fable and DyeAllPies", FONT_S, 30, 820), fill=(*MUTED, a), anchor="ma")
            dr.text((260, 384), f"{S['reps']}", font=F["sum_big"], fill=(*WHITE, a), anchor="ma")
            dr.text((260, 524), "reps", font=F["sum_l"], fill=(*MUTED, a), anchor="ma")
            dr.text((736, 384), f"{S['mean_efficiency']:.0f}", font=F["sum_big"], fill=(*AQUA, a), anchor="ma")
            dr.text((736, 524), "avg efficiency / 100", font=F["sum_l"], fill=(*MUTED, a), anchor="ma")
            rows = [("chin above bar · at bar · short", f"{S.get('chin_above', 0)} · {S.get('chin_marginal', 0)} · {S.get('chin_short', 0)}"),
                    ("full lock-out at bottom", f"{S['lockouts']} / {S['reps']}"),
                    ("range of motion", f"{S['mean_rom_cm']:.0f} cm per rep"),
                    ("tempo  up / down", f"{S['mean_concentric']:.1f} s / {S['mean_eccentric']:.1f} s"),
                    ("peak speed  best → last", f"{S['peak_v_max']:.2f} → {S['peak_v_last']:.2f} m/s  (−{S['velocity_loss_pct']:.0f} %)"),
                    ("hip sway", f"{S['mean_hip_sway_cm']:.0f} cm avg"), ("elbow at top  L / R", f"{S['mean_elbow_top_l']:.0f}° / {S['mean_elbow_top_r']:.0f}°")]
            if "set_kcal_total" in S:
                rows += [("work · peak power", f"{S['set_work_kj']:.1f} kJ · {S['peak_power_w_max']:.0f} W"),
                         ("energy, rough estimate", f"≈ {S['set_kcal_total']:.0f} kcal for the set"),
                         ("last rep vs best", f"effort ×{S['effort_x_last']:.1f} · ~{S['est_rir_last']} reps left")]
            for k, (lab, val) in enumerate(rows):
                yy = 586 + k * 48
                dr.text((100, yy), lab, font=F["sum_l"], fill=(*MUTED, a))
                room = 896 - 100 - dr.textlength(lab, font=F["sum_l"]) - 24
                dr.text((896, yy), val, font=fit(dr, val, FONT_S, 34, room), fill=(*WHITE, a), anchor="ra")
            foot = f"MediaPipe 33-pt pose · YOLOv8 cross-check: {S.get('yolo_reps', S['reps'])} reps · {S['height_m']*100:.0f} cm, {S['mass_kg']:.0f} kg"
            dr.text((498, 1112), foot, font=fit(dr, foot, FONT_R, 26, 820), fill=(*MUTED, a), anchor="ms")

        im.alpha_composite(ov)
        if preview is not None:
            pth = os.path.splitext(out)[0] + f"_preview_{i}.png"
            im.convert("RGB").save(pth); print("wrote", pth, flush=True)
            continue
        proc.stdin.write(im.convert("RGB").tobytes())
        if i % 150 == 0:
            print(f"  frame {i}/{total}", flush=True)
    cap.release()
    if proc is not None:
        proc.stdin.close(); proc.wait()
        print("done ->", out, "rc", proc.returncode)


if __name__ == "__main__":
    main()
