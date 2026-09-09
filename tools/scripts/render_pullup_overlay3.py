"""
Render the pull-up analysis, version 3 (set #3, floor camera, anatomy paint).

    python render_pullup_overlay3.py <video> <pose_mp.npz> <analysis.json> <out.mp4>
        [heat=matte.npy] [bg=plate.jpg] [look=1] [grid=1] [cat=1] [lut=bluered|iron|blue]
        [trim=f0,f1] [hold=4.0] [schedule=sched.json] [preview=i,i,..] [silent=1] [tscale=1.5]

Differences from render_pullup_overlay2.py (kept for set #2):
  * the body is painted by pullup_atlas3 (muscles with fibre direction, one continuous colour
    field with no boundary lines, the frame's own definition) coloured by the muscle model's EFFORT INDEX
    (pullup_thermal4 v4.3: the non-resting share of the motor-unit pool, M_A + M_F, plus a
    temperature floor) on a blue -> red scale, so a muscle lights up as it contracts and cools
    as it relaxes inside every rep, the fatigued share M_F carries from rep to rep and clears
    only after the release (v4.1 used the effective activation; v4 coloured by temperature,
    which never falls in a set);
  * muscle NAMES appear once each, the first time that muscle's effort passes LABEL_E;
  * the form grid is drawn in the rectified doorway plane and mapped back through the
    homography, so the rules converge exactly as the room does (the grid is honest about
    the perspective, and every rule is a true 10 cm in the bar plane);
  * fewer, bigger readouts (nothing that must be read is under 44 px);
  * the judge's card leads with three numbers and stays for 4 s;
  * the cat is kept in front of the backdrop (a dark-blob mask in its corner, after it sits).
"""
import sys, json, subprocess, os
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pullup_look import LookPass
import pullup_thermal3 as TH3
import pullup_thermal4 as TH4
import pullup_atlas3 as AT
TH = TH4                  # model=3 on the command line swaps the phase-table model back in

FONT_B = "C:/Windows/Fonts/segoeuib.ttf"; FONT_S = "C:/Windows/Fonts/seguisb.ttf"
FONT_R = "C:/Windows/Fonts/segoeui.ttf"; FONT_SYM = "C:/Windows/Fonts/seguisym.ttf"
VERDICT = {"above": ("CHIN OVER THE BAR", "\u2713"), "at": ("CHIN AT THE BAR", "~"), "short": ("CHIN SHORT", "\u2717")}
VERDICT_COL = {"above": (25, 158, 112), "at": (201, 133, 0), "short": (217, 89, 38)}
BLUE = (57, 135, 229); ORANGE = (217, 89, 38); AQUA = (25, 158, 112); YELLOW = (201, 133, 0)
WHITE = (255, 255, 255); MUTED = (195, 194, 183); INK = (26, 26, 25)
PHASE_COL = {"PULL": AQUA, "HOLD": YELLOW, "LOWER": BLUE, "HANG": MUTED, "HANDS ON BAR": MUTED,
             "LOADING": YELLOW, "SETUP": MUTED, "DONE": MUTED}
EDGES = [(11, 13, BLUE), (13, 15, BLUE), (12, 14, ORANGE), (14, 16, ORANGE), (11, 12, WHITE), (11, 23, WHITE),
         (12, 24, WHITE), (23, 24, WHITE), (23, 25, BLUE), (25, 27, BLUE), (24, 26, ORANGE), (26, 28, ORANGE)]
JOINTS = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
GRID_BOTTOM = 1500
STACK_Y0 = 536            # the live left stack starts under the phase pill (six rows, 76 px apart) ...
LABEL_Y0 = 996            # ... and the one muscle-name slot sits under it, ending at 1042: the red
                          # monkey on the left lives at y 1060-1240 after the push-in, leave him be
LABEL_E = 0.55            # a muscle is named the first time its effort index passes this (0..1)
LABEL_S = 1.4             # seconds the name stays (one at a time: the stagger below equals it)
BLUERED_STOPS = AT._STOPS  # the default (v4.1): blue -> cyan -> green -> yellow -> orange -> red
BLUE_STOPS = [(0.00, (110, 30, 15)), (0.18, (200, 70, 20)), (0.36, (220, 170, 0)), (0.52, (60, 210, 120)),
              (0.68, (0, 210, 240)), (0.82, (20, 90, 250)), (0.93, (60, 40, 235)), (1.00, (225, 235, 255))]
IRON_STOPS = [(0.00, (40, 0, 20)), (0.15, (120, 0, 60)), (0.32, (170, 10, 120)), (0.50, (60, 20, 210)),
              (0.66, (0, 90, 240)), (0.80, (0, 180, 250)), (0.92, (90, 240, 255)), (1.00, (240, 250, 255))]


def make_lut(stops):
    lut = np.zeros((256, 1, 3), np.uint8); xs = [s[0] for s in stops]; cs = np.array([s[1] for s in stops], float)
    for i in range(256):
        tt = i / 255; k = min(max(j for j in range(len(xs)) if xs[j] <= tt), len(xs) - 2)
        u = (tt - xs[k]) / (xs[k + 1] - xs[k]); lut[i, 0] = np.clip(cs[k] * (1 - u) + cs[k + 1] * u, 0, 255)
    return lut


def font(path, size):
    return ImageFont.truetype(path, size)


def rounded(draw, box, r, fill):
    draw.rounded_rectangle(box, radius=r, fill=fill)


_FC = {}


def fit(draw, text, path, size, max_w, min_size=16):
    while size > min_size:
        k = (path, size)
        if k not in _FC:
            _FC[k] = ImageFont.truetype(path, size)
        if draw.textlength(text, font=_FC[k]) <= max_w:
            return _FC[k]
        size -= 2
    return _FC.setdefault((path, min_size), ImageFont.truetype(path, min_size))


def cat_mask(frame_bgr, roi, prev=None):
    """The cat: the dark blob inside its corner of the frame, feathered; temporally smoothed."""
    x0, y0, x1, y1 = roi
    H, W = frame_bgr.shape[:2]
    g = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    m = np.zeros((H, W), np.uint8)
    sub = g[y0:y1, x0:x1]
    blob = (sub < 70).astype(np.uint8)
    blob = cv2.morphologyEx(blob, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    blob = cv2.morphologyEx(blob, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(blob)
    if n > 1:
        k = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        if stats[k, cv2.CC_STAT_AREA] > 1500:
            m[y0:y1, x0:x1] = (lab == k).astype(np.uint8) * 255
    mf = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 2.0)
    if prev is not None:
        mf = 0.6 * prev + 0.4 * mf
    return mf


def main():
    video, npz, ajson, out = sys.argv[1:5]
    hold_s = 4.0; heat_path = None; preview = None; look_on = False; sched_path = None
    silent = False; trim = None; bg_path = None; grid_on = False; cat_on = False; lut_name = "bluered"; t_scale = 1.5
    model_v = 4
    for a in sys.argv[5:]:
        if a.startswith("heat="): heat_path = a[5:]
        elif a.startswith("preview="): preview = [int(x) for x in a[8:].split(",")]
        elif a.startswith("look="): look_on = a[5:] not in ("0", "", "no")
        elif a.startswith("schedule="): sched_path = a[9:]
        elif a.startswith("silent="): silent = a[7:] not in ("0", "", "no")
        elif a.startswith("hold="): hold_s = float(a[5:])
        elif a.startswith("trim="): trim = [int(x) for x in a[5:].split(",")]
        elif a.startswith("bg="): bg_path = a[3:]
        elif a.startswith("grid="): grid_on = a[5:] not in ("0", "", "no")
        elif a.startswith("cat="): cat_on = a[4:] not in ("0", "", "no")
        elif a.startswith("lut="): lut_name = a[4:]
        elif a.startswith("tscale="): t_scale = float(a[7:])
        elif a.startswith("model="): model_v = int(a[6:])
    global TH
    TH = TH3 if model_v == 3 else TH4
    AT.LUT = make_lut({"iron": IRON_STOPS, "blue": BLUE_STOPS}.get(lut_name, BLUERED_STOPS))
    LUT = AT.LUT

    d = np.load(npz); img = d["img"]; ok = d["ok"]; fps = float(d["fps"])
    W, H = int(d["width"]), int(d["height"])
    P = img[:, :, :2] * np.array([W, H]); V = np.nan_to_num(img[:, :, 3])
    A = json.load(open(ajson)); S = A["summary"]; atts = A["reps"]; sig = A["signals"]
    reps = [r for r in atts if r.get("rep")]
    N = len(img); t = np.array(sig["t"])
    vy = np.array(sig["vy_m"]); el_l = np.array(sig["elbow_l"]); el_r = np.array(sig["elbow_r"])
    sh_tilt = np.array(sig["sh_tilt"])
    bar_a, bar_b = S["bar_slope"], S["bar_intercept"]
    hang0, hang1 = sig["hang0"], sig["hang1"]
    phase = list(sig["phase"])
    # before the feet leave the floor he is holding the bar, not hanging (Dennis, 2026-09-09):
    # the pill says HANDS ON BAR there and the model carries a reduced hand load
    FEET_OFF = TH4.feet_off_frame(A)
    print(f"feet leave the floor at frame {FEET_OFF} ({FEET_OFF / fps:.1f} s source)", flush=True)
    ppm = S["px_per_m"]
    hang_ref, top_ref = S["hang_ref_y"], S["top_ref_y"]
    height_pct = np.clip(np.array(sig["height_pct"]), -10, 115)
    rom_cm = (hang_ref - top_ref) / ppm * 100
    chin_bar_pct = 100 + (-S["mean_chin_cm"]) / rom_cm * 100
    Ht = np.array(S["H_total"]); Hinv = np.linalg.inv(Ht)
    BAR_Y = S["bar_y_rect"]

    # ---- muscle model: v4 = inverse dynamics + force sharing + activation dynamics + fatigue ----
    if TH is TH4:
        Mo = TH4.model(A, P); Tm = Mo["T"]; Am = Mo["a_eff"]; Em = Mo["E"]; masses = TH.muscle_masses()
        tsum = TH4.summarise(A, Tm, P)
        fat_bic = Mo["MF"]["biceps brachii"]; fat_lat = Mo["MF"]["latissimus dorsi"]
        print(f"model v4.1: elbow moment peak {Mo['M_el'].max():.0f} N m, shoulder {Mo['M_sh'].max():.0f} N m; "
              f"fatigued pool at the end: biceps {fat_bic[-1]*100:.0f} %, lats {fat_lat[-1]*100:.0f} %", flush=True)
    else:
        Tm = TH.integrate(A); Am = TH.activation(A); Em = Am; masses = TH.muscle_masses()
        tsum = TH.summarise(A, Tm); fat_bic = fat_lat = np.zeros(len(img))
    lat_T = Tm["latissimus dorsi"]; lat_A = Am["latissimus dorsi"]
    heat_kj = np.cumsum(sum(Mo["q"][m] for m in Mo["q"])) / fps / 1000 if TH is TH4 else np.zeros(len(img))
    # per-region series: temperature (for the numbers) and the effort index (for the colour and the labels)
    reg_T_series = {r: np.zeros(N) for r in AT.REGIONS}; reg_E_series = {r: np.zeros(N) for r in AT.REGIONS}
    for r, ms in AT.REGION_MUSCLES.items():
        w = sum(masses[m] for m in ms)
        reg_T_series[r] = sum(Tm[m] * masses[m] for m in ms) / w
        reg_E_series[r] = sum(Em[m] * masses[m] for m in ms) / w
    label_at = {}
    for r in AT.REGIONS:
        idx = np.where(reg_E_series[r] >= LABEL_E)[0]
        if len(idx):
            label_at[r] = int(idx[0])
    # stagger labels that would fire on the same frame
    order = sorted(label_at, key=lambda r: label_at[r]); last = -999
    for r in order:
        if label_at[r] < last + int(LABEL_S * fps) + 2:
            label_at[r] = last + int(LABEL_S * fps) + 2
        last = label_at[r]
    print("labels:", {AT.LABELS[r]: round(label_at[r] / fps, 1) for r in order}, flush=True)

    kcal = np.zeros(N)
    if "kcal" in atts[0]:
        rate = np.zeros(N); rate[hang0:hang1 + 1] = S["hang_kcal_per_s"] / fps
        for r in atts:
            a0, b0 = r["f_start"], r["f_end"]
            rate[a0:b0 + 1] += (r["kcal"] - S["hang_kcal_per_s"] * (b0 - a0 + 1) / fps) / (b0 - a0 + 1)
        kcal = np.cumsum(rate)
    vloss = np.zeros(N); v1 = reps[0]["peak_conc_v"]
    for r in atts:
        vloss[r["f_end"]:] = max(0.0, (1 - r["peak_conc_v"] / v1) * 100)
    # live tallies for the left stack: chin verdicts so far, running peak power, running kcal
    chin_ok = np.zeros(N, int); chin_n = np.zeros(N, int); peak_w = np.zeros(N)
    for r in atts:
        chin_n[r["f_end"]:] += 1
        if r.get("chin_verdict", "at") in ("at", "above") and not r.get("failed"):
            chin_ok[r["f_end"]:] += 1
        peak_w[r["f_end"]:] = np.maximum(peak_w[r["f_end"]:], r.get("peak_power_w", 0.0))
    count = np.zeros(N, int); card = [None] * N
    for r in atts:
        if r.get("rep"):
            count[r["f_top"]:] = r["rep"]
        for i in range(r["f_end"], min(N, r["f_end"] + int(2.0 * fps))):
            card[i] = r

    F = {k: font(*v) for k, v in dict(
        counter=(FONT_B, 150), counter_lbl=(FONT_S, 36), phase=(FONT_B, 54), metric=(FONT_B, 60), pill=(FONT_B, 40), pill_l=(FONT_S, 26),
        small=(FONT_S, 34), tiny=(FONT_R, 27), card_t=(FONT_B, 52), card=(FONT_S, 36),
        title=(FONT_B, 76), sub=(FONT_S, 40), sum_h=(FONT_B, 60), sum_big=(FONT_B, 124),
        sum_l=(FONT_S, 34), sym=(FONT_SYM, 30), lab=(FONT_B, 30)).items()}

    PX0, PY0, PX1, PY1 = 60, 1536, 936, 1822
    CX0, CY0, CX1, CY1 = PX0 + 24, PY0 + 86, PX1 - 24, PY1 - 70
    t_end = t[-1]

    def tx(tt): return CX0 + (CX1 - CX0) * tt / t_end

    def hy(pct): return CY1 - (CY1 - CY0) * np.clip(pct, -5, 112) / 112
    trace_pts = [(tx(t[i]), hy(height_pct[i])) for i in range(N)]

    masks = None; look = None
    if heat_path:
        masks = np.load(heat_path, mmap_mode="r")
        look = LookPass(W, H) if look_on else None
        print(f"heat: scale 0..{t_scale} C ({lut_name}); lats end at +{lat_T.max():.2f} C", flush=True)
    plate = None; bar_mask = None
    if bg_path:
        plate = cv2.resize(cv2.imread(bg_path), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
        capb = cv2.VideoCapture(video); capb.set(cv2.CAP_PROP_POS_FRAMES, 1770); _, f0 = capb.read(); capb.release()
        g0 = cv2.cvtColor(f0, cv2.COLOR_BGR2GRAY)
        band = np.zeros((H, W), np.uint8)
        for x in range(W):
            yb = int(bar_a * x + bar_b)
            band[max(0, yb - 10):min(H, yb + 42), x] = 1
        barm = ((g0 < 90).astype(np.uint8) * band)
        barm = cv2.morphologyEx(barm, cv2.MORPH_CLOSE, np.ones((5, 21), np.uint8))
        barm = cv2.dilate(barm, np.ones((5, 5), np.uint8))
        bar_mask = cv2.GaussianBlur(barm.astype(np.float32), (0, 0), 1.5)[:, :, None]
        print(f"backdrop: {bg_path}, bar kept over {int((barm > 0).sum())} px", flush=True)
    CAT_ROI = (400, 1640, 760, 1900); cat_prev = None; cat_from = int(15.0 * fps)
    # push-in: the camera is far, so the composed frame is cropped and scaled before the UI goes on
    # (bar stays under the Instagram top band: (365 - ZY0) * Z >= 240)
    Z = 1.12; ZW, ZH = int(round(W / Z)), int(round(H / Z)); ZX0, ZY0 = 150, 150

    def zmap(x, y):
        return (x - ZX0) * Z, (y - ZY0) * Z
    CAT_AT = (820, 1180)      # where the cat is placed after the push-in (its own crop from the source)

    # ---- the grid in the rectified plane, mapped back: rules every 10 cm both ways ----
    grid_lines = []; grid_cols = []
    if grid_on:
        step = 0.10 * ppm
        k = 1
        while True:
            yr = BAR_Y + k * step
            pts = np.array([[[x, yr]] for x in np.linspace(-200, W + 200, 12)], float)
            pi = cv2.perspectiveTransform(pts, Hinv).reshape(-1, 2)
            if pi[:, 1].min() > GRID_BOTTOM:
                break
            grid_lines.append((k, pi))
            k += 1
        # verticals: same spacing, same weight, centred on the grip midpoint at the dead hang
        gx0 = float(np.median([(cv2.perspectiveTransform(np.array([[[(P[i][15][0] + P[i][16][0]) / 2, (P[i][15][1] + P[i][16][1]) / 2]]]), Ht)[0, 0, 0])
                               for i in range(hang0, min(hang0 + 30, N))]))
        for k in range(-12, 13):
            xr = gx0 + k * step
            pts = np.array([[[xr, y]] for y in np.linspace(BAR_Y - 40, BAR_Y + 3.2 * ppm, 12)], float)
            pi = cv2.perspectiveTransform(pts, Hinv).reshape(-1, 2)
            if pi[:, 0].max() < -20 or pi[:, 0].min() > W + 20:
                continue
            grid_cols.append((k, pi))

    # ---- output frame list ----
    plan = []
    if sched_path:
        sched = json.load(open(sched_path))
        for seg in sched:
            if seg["kind"] == "freeze":
                for _ in range(int(round(seg["dur"] * fps))):
                    plan.append((int(seg["f"]), "freeze", seg))
            elif seg["kind"] == "play":
                step = int(seg.get("step", 1))
                for f in range(int(seg["f0"]), int(seg["f1"]), step):
                    plan.append((min(f, N - 1), "play", seg))
            elif seg["kind"] == "summary":
                back = int(seg["f"]) if "f" in seg else (plan[-1][0] if plan else N - 1)
                for _ in range(int(round(seg["dur"] * fps))):
                    plan.append((back, "summary", seg))
    else:
        f0, f1 = (trim if trim else (0, N))
        for f in range(f0, min(f1, N)):
            plan.append((f, "play", {"step": 1}))
        for _ in range(int(hold_s * fps)):
            plan.append((plan[-1][0], "summary", {}))
    total = len(plan)
    print(f"rendering {total} frames ({total/fps:.2f} s)", flush=True)

    proc = None
    if preview is None:
        cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", f"{fps}", "-i", "pipe:0"]
        if not silent and not sched_path:
            off = (trim[0] / fps) if trim else 0.0
            cmd += ["-ss", f"{off:.3f}", "-i", video, "-map", "0:v", "-map", "1:a", "-af", "apad", "-shortest"]
        cmd += ["-c:v", "h264_nvenc", "-preset", "p5", "-tune", "hq", "-rc", "vbr", "-cq", "19", "-b:v", "0",
                "-spatial-aq", "1", "-temporal-aq", "1", "-pix_fmt", "yuv420p"]
        if not silent and not sched_path:
            cmd += ["-c:a", "aac", "-b:a", "160k"]
        cmd += ["-movflags", "+faststart", out]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    cap = cv2.VideoCapture(video)
    cur_src = -1; frame = None; last_ok = None
    for i, (fi, kind, seg) in enumerate(plan):
        if preview is not None and i not in preview:
            if i > max(preview): break
            continue
        if fi != cur_src:
            if cur_src >= 0 and 0 < fi - cur_src <= 12:
                for _ in range(fi - cur_src):
                    got, fr = cap.read()
                    if not got: break
            else:
                cap.set(cv2.CAP_PROP_POS_FRAMES, fi); got, fr = cap.read()
            if got:
                frame = fr; cur_src = fi
        f = frame.copy(); src = frame
        if ok[fi]:
            P_use, V_use = P[fi], V[fi]; last_ok = (P[fi], V[fi])
        else:
            P_use, V_use = last_ok if last_ok is not None else (P[fi], V[fi])
        ph = phase[fi] if kind != "summary" else "DONE"
        if ph == "HANG" and fi < FEET_OFF:
            ph = "HANDS ON BAR"
        pc = PHASE_COL.get(ph, MUTED)
        fast = int(seg.get("step", 1)) if kind == "play" else 1

        comp_now = np.asarray(masks[fi]) if masks is not None else None
        if plate is not None and comp_now is not None:
            alpha_full = cv2.resize(comp_now[..., 0], (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255
            z = 1.0 + 0.05 * (i / max(1, total - 1))
            cw, ch = int(W / z), int(H / z); px0 = (W - cw) // 2; py0 = (H - ch) // 2
            pl = cv2.resize(plate[py0:py0 + ch, px0:px0 + cw], (W, H), interpolation=cv2.INTER_LINEAR)
            keep = np.clip(alpha_full[:, :, None] + bar_mask, 0, 1)
            f = np.clip(pl * (1 - keep) + f.astype(np.float32) * keep, 0, 255).astype(np.uint8)
        lab_full = None
        if masks is not None and last_ok is not None and ph not in ("SETUP",):
            # colour = the effort index (0..1, scale 1.0); the brightness nudge = effective activation
            reg_E = AT.region_values(Em, masses, fi); reg_A = AT.region_values(Am, masses, fi)
            f, mf, lab_full = AT.paint(f, comp_now, P_use, reg_E, reg_A, 1.0, (bar_a, bar_b))
            if look is not None:
                rim_v = float(np.clip(lat_T[fi] / t_scale, 0, 1))
                rim = tuple(int(c) for c in LUT[int((0.15 + 0.7 * rim_v) * 255), 0])
                f = look.apply(f, mf, rim, 0.8, i, keep_colour=plate is not None, rim=0.0)

        # ---- grid under the skeleton ----
        if grid_on and last_ok is not None and ph not in ("SETUP", "DONE"):
            gl = f.copy()
            for k, pi in grid_cols:
                pc_ = pi[pi[:, 1] <= GRID_BOTTOM]
                if len(pc_) > 1:
                    cv2.polylines(gl, [np.round(pc_).astype(np.int32).reshape(-1, 1, 2)], False, (215, 215, 210), 1, cv2.LINE_AA)
            for k, pi in grid_lines:
                pts = np.round(pi).astype(np.int32).reshape(-1, 1, 2)
                cv2.polylines(gl, [pts], False, (215, 215, 210), 1, cv2.LINE_AA)
                if k % 2 == 0:
                    xe = pi[np.argmin(np.abs(pi[:, 0] - 24))]
                    cv2.putText(gl, f"-{k*10}", (14, int(xe[1]) - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (215, 215, 210), 1, cv2.LINE_AA)
            gc_x = int((P_use[15][0] + P_use[16][0]) / 2)
            for yy0 in range(int(bar_a * gc_x + bar_b), GRID_BOTTOM, 26):
                cv2.line(gl, (gc_x, yy0), (gc_x, min(yy0 + 14, GRID_BOTTOM)), (240, 240, 236), 2, cv2.LINE_AA)
            f = cv2.addWeighted(f, 0.70, gl, 0.30, 0)
            sl_, sr_ = P_use[11].astype(int), P_use[12].astype(int)
            smx, smy = (sl_[0] + sr_[0]) // 2, (sl_[1] + sr_[1]) // 2
            half_w = int(abs(sl_[0] - sr_[0]) * 0.72) + 30
            cv2.line(f, (smx - half_w, smy), (smx + half_w, smy), (120, 120, 118), 2, cv2.LINE_AA)
            cv2.line(f, tuple(sl_), tuple(sr_), (255, 255, 255), 2, cv2.LINE_AA)

        # ---- a light skeleton (thin: the anatomy is the picture now) ----
        if last_ok is not None and ph not in ("SETUP", "DONE"):
            Pf, Vf = P_use, V_use
            for a1, b1, col in EDGES:
                if Vf[a1] > 0.5 and Vf[b1] > 0.5:
                    pa, pb = tuple(Pf[a1].astype(int)), tuple(Pf[b1].astype(int))
                    cv2.line(f, pa, pb, INK, 6, cv2.LINE_AA); cv2.line(f, pa, pb, col[::-1], 2, cv2.LINE_AA)
            for j in JOINTS:
                if Vf[j] > 0.5:
                    p = tuple(Pf[j].astype(int))
                    cv2.circle(f, p, 9, INK, -1, cv2.LINE_AA); cv2.circle(f, p, 5, WHITE[::-1], -1, cv2.LINE_AA)
        for x in range(0, W, 36):
            y1p = int(bar_a * x + bar_b); y2p = int(bar_a * min(x + 18, W) + bar_b)
            cv2.line(f, (x, y1p), (min(x + 18, W), y2p), (255, 255, 255), 2, cv2.LINE_AA)

        f = cv2.resize(f[ZY0:ZY0 + ZH, ZX0:ZX0 + ZW], (W, H), interpolation=cv2.INTER_LANCZOS4)
        if cat_on and fi >= cat_from and plate is not None:
            cat_prev = cat_mask(src, CAT_ROI, cat_prev)
            x0c, y0c, x1c, y1c = CAT_ROI
            cm = cat_prev[y0c:y1c, x0c:x1c]
            if cm.max() > 0.5:
                ys, xs = np.where(cm > 0.5); cy0, cy1, cx0, cx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
                patch = src[y0c + cy0:y0c + cy1, x0c + cx0:x0c + cx1].astype(np.float32)
                al = cm[cy0:cy1, cx0:cx1][:, :, None]
                px, py = CAT_AT[0] - (cx1 - cx0) // 2, CAT_AT[1] - (cy1 - cy0)
                hh, ww = patch.shape[:2]
                if 0 <= px and px + ww <= W and 0 <= py and py + hh <= H:
                    roi = f[py:py + hh, px:px + ww].astype(np.float32)
                    f[py:py + hh, px:px + ww] = np.clip(roi * (1 - al) + patch * al, 0, 255).astype(np.uint8)
        im = Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)).convert("RGBA")
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(ov)
        bx, by = zmap(W - 150, bar_a * (W - 150) + bar_b)
        dr.text((min(bx, W - 40), by + 44), "BAR", font=F["small"], fill=(*WHITE, 230), anchor="rs")

        # ---- muscle names, once each, in a slot beside the counter with a leader line ----
        if lab_full is not None and kind == "play":
            cents = AT.label_centroids(lab_full, W, H)
            slot = 0
            for r_ in order:
                f_at = label_at[r_]; age = (fi - f_at) / fps
                if 0 <= age < LABEL_S and r_ in cents:
                    a_ = int(255 * min(1.0, age / 0.2, (LABEL_S - age) / 0.3))
                    cx, cy = zmap(cents[r_][0], cents[r_][1])
                    txt = f"{AT.LABELS[r_]}  {reg_E_series[r_][fi] * 100:.0f} %"
                    fnt = fit(dr, txt, FONT_B, 30, 380); tw = dr.textlength(txt, font=fnt) + 28
                    lx, ly = 60, LABEL_Y0 + slot * 56
                    dr.line((cx, cy, lx + tw / 2, ly + 46), fill=(*WHITE, a_), width=2)
                    dr.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=(*WHITE, a_))
                    rounded(dr, (lx, ly, lx + tw, ly + 46), 10, (*INK, int(225 * a_ / 255)))
                    dr.text((lx + 14, ly + 6), txt, font=fnt, fill=(*WHITE, a_))
                    slot += 1

        if kind == "freeze":
            ttl = seg.get("title"); sub = seg.get("sub")
            rounded(dr, (60, 250, 936, 470 if not sub else 520), 24, (*INK, 215))
            if ttl: dr.text((84, 272), ttl, font=fit(dr, ttl, FONT_B, 72, 828), fill=(*ORANGE, 255))
            if sub:
                dr.text((84, 372), sub, font=fit(dr, sub, FONT_S, 40, 828), fill=WHITE)
                dr.text((84, 436), seg.get("sub2", ""), font=fit(dr, seg.get("sub2", ""), FONT_R, 30, 828), fill=MUTED)
        elif ph == "SETUP":
            rounded(dr, (60, 240, 936, 520), 24, (*INK, 205))
            dr.text((84, 262), "PULL UP ANALYSIS", font=fit(dr, "PULL UP ANALYSIS", FONT_B, 76, 828), fill=WHITE)
            dr.text((84, 352), "by Fable", font=fit(dr, "by Fable", FONT_S, 46, 828), fill=WHITE)
            sub = "16 muscles · 3 trackers · judged to the USMC standard"
            dr.text((84, 430), sub, font=fit(dr, sub, FONT_S, 34, 828), fill=MUTED)
        elif kind != "summary":
            rounded(dr, (60, 240, 252, 428), 22, (*INK, 205))
            dr.text((156, 226), str(count[fi]), font=F["counter"], fill=WHITE, anchor="ma")
            dr.text((156, 386), "REPS", font=F["counter_lbl"], fill=MUTED, anchor="ma")
            pw = dr.textlength(ph, font=F["phase"]) + 52
            rounded(dr, (60, 446, 60 + pw, 516), 18, (*pc, 235))
            dr.text((86, 452), ph, font=F["phase"], fill=WHITE if ph in ("PULL", "LOWER") else INK)
            if fast > 1:
                fw = dr.textlength(f"×{fast}", font=F["phase"]) + 44
                rounded(dr, (60 + pw + 12, 446, 60 + pw + 12 + fw, 516), 18, (*WHITE, 230))
                dr.text((60 + pw + 12 + 22, 452), f"×{fast}", font=F["phase"], fill=INK)
            # ---- the left stack: the numbers people share, live, between the two monkeys ----
            if count[fi] > 0:
                vcol = WHITE if vloss[fi] < 25 else YELLOW if vloss[fi] < 50 else ORANGE
                rows_ = [(f"{chin_ok[fi]}/{chin_n[fi]}" if chin_n[fi] else "–", "CHIN AT THE BAR", AQUA if chin_ok[fi] == chin_n[fi] else YELLOW),
                         (f"−{vloss[fi]:.0f} %" if vloss[fi] >= 1 else "0 %", "SPEED VS REP 1", vcol),
                         (f"{peak_w[fi]:.0f} W", "PEAK POWER", WHITE),
                         (f"+{lat_T[fi]:.2f} °C", "LATS · MODELLED", ORANGE)]
                if TH is TH4:
                    # both prime movers' fatigued pools. v4.3: with Frey-Law 2012's real shoulder row
                    # (F = 2.0 x the elbow's; v4.2 held the ankle's row from memory) the lats' pool
                    # leads, as the muscle that works hardest should. Neither recovers under load;
                    # both start to clear after the release (Looft 2018 rest multiplier).
                    rows_.append((f"{fat_lat[fi]*100:.0f} % · {fat_bic[fi]*100:.0f} %", "LATS · BICEPS FATIGUED, MODEL", WHITE))
                rows_.append((f"≈ {kcal[fi]:.1f} kcal", f"{heat_kj[fi]:.0f} kJ OF HEAT" if TH is TH4 else "ENERGY, A MODEL", MUTED))
                y_ = STACK_Y0
                bw = max(max(dr.textlength(b_, font=F["pill"]), dr.textlength(s_, font=F["pill_l"])) for b_, s_, _ in rows_) + 28
                for big, small, col in rows_:
                    rounded(dr, (60, y_, 60 + bw, y_ + 70), 14, (*INK, 200))
                    dr.text((74, y_ + 0), big, font=F["pill"], fill=col)
                    dr.text((74, y_ + 44), small, font=F["pill_l"], fill=MUTED)
                    y_ += 76
            # diegetic pills: the elbow angle at the elbow, the speed at the hips, the lats' temperature at the lats
            if last_ok is not None and fast == 1:
                def pill(x, y, big, small, anchor_right=False):
                    bw = max(dr.textlength(big, font=F["pill"]), dr.textlength(small, font=F["pill_l"])) + 28
                    x0p = x - bw if anchor_right else x
                    rounded(dr, (x0p, y, x0p + bw, y + 84), 14, (*INK, 205))
                    dr.text((x0p + 14, y + 4), big, font=F["pill"], fill=WHITE)
                    dr.text((x0p + 14, y + 52), small, font=F["pill_l"], fill=MUTED)
                ex, ey = zmap(*P_use[13]); pill(ex - 150 if ex > 300 else 60, ey - 42, f"{(el_l[fi] + el_r[fi]) / 2:.0f}°", "ELBOW", anchor_right=ex > 300)
                hx, hy_ = zmap(*P_use[24]); pill(min(hx + 60, W - 260), min(hy_ - 42, 1192 - 8 - 84), f"{abs(vy[fi]):.2f} m/s", "SPEED " + ("UP" if vy[fi] > 0.05 else "DOWN" if vy[fi] < -0.05 else ""))   # stays above the card / GitHub box
                if masks is not None and count[fi] == 0:
                    lx_, ly_ = zmap(*((P_use[11] + P_use[23]) / 2)); pill(lx_ + 40, ly_ - 42, f"+{lat_T[fi]:.2f} °C", "LATS, MODELLED")

        r = card[fi]
        if r is not None and kind == "play" and fast == 1:
            age = (fi - r["f_end"]) / fps
            a = int(255 * min(1.0, max(age, 0) / 0.15))
            x0, y0, x1, y1 = 60, 1192, 936, 1478
            rounded(dr, (x0, y0, x1, y1), 24, (*INK, int(215 * a / 255)))
            vk = r.get("chin_verdict", "at"); vtxt, vsym = VERDICT[vk]; gc = VERDICT_COL[vk]
            if r.get("failed"):
                vtxt, vsym, gc = "FAILED", "\u2717", ORANGE
            elif vk == "short":
                vtxt = f"CHIN {abs(r['chin_cm']):.0f} CM SHORT"
            bx0 = x1 - 330
            rounded(dr, (bx0, y0 + 18, x1 - 24, y1 - 18), 20, (*gc, a))
            bcx = (bx0 + x1 - 24) // 2
            dr.text((bcx, y0 + 34), vsym, font=fit(dr, vsym, FONT_SYM, 96, 200), fill=(*INK, a), anchor="ma")
            dr.text((bcx, y0 + 150), vtxt, font=fit(dr, vtxt, FONT_B, 34, x1 - 24 - bx0 - 24), fill=(*INK, a), anchor="ma")
            note = f"{r['chin_cm']:+.1f} cm in plane, +{r.get('chin_depth_allowance_cm', 0):.0f} hidden by the camera"
            dr.text((bcx, y1 - 30), note, font=fit(dr, note, FONT_R, 26, x1 - 24 - bx0 - 24), fill=(*INK, a), anchor="ms")
            head = f"REP {r['rep']}" if r.get("rep") else f"ATTEMPT {r['n']}"
            dr.text((x0 + 24, y0 + 18), head, font=F["card_t"], fill=(*WHITE, a))
            lock = "FULL LOCK-OUT" if r["lockout"] else "NO LOCK-OUT"
            cx = x0 + 24
            for txt, good in ((lock, r["lockout"]), ("NO SWING", r["hip_sway_cm"] <= 8)):
                col = AQUA if good else ORANGE
                tw = dr.textlength(txt, font=F["small"]) + 28
                rounded(dr, (cx, y0 + 88, cx + tw, y0 + 132), 12, (*col, a))
                dr.text((cx + 14, y0 + 92), txt, font=F["small"], fill=(*INK, a))
                cx += tw + 12
            lines = [f"up {r['t_concentric']:.1f} s   hold {r['t_top_hold']:.1f} s   down {r['t_eccentric']:.1f} s",
                     f"peak {r['peak_conc_v']:.2f} m/s   {r['mean_power_w']:.0f} W   ≈ {r['kcal']:.1f} kcal",
                     f"speed loss {max(0, r.get('velocity_loss_pct', 0)):.0f} %   sway {r['hip_sway_cm']:.0f} cm"]
            for k, ln in enumerate(lines):
                dr.text((x0 + 24, y0 + 146 + k * 44), ln, font=fit(dr, ln, FONT_S, 34, x1 - x0 - 380), fill=(*MUTED, a))
        # ---- the GitHub box: the same slot as the rep card, shown whenever the card is not (Dennis,
        # 2026-09-09: the cut start loses the title card, this carries the title and the repository) ----
        if kind == "play" and ph != "SETUP":
            gh_a = 1.0
            if r is not None and fast == 1:
                gh_a = 1.0 - a / 255
            elif fast == 1:
                # fade back in after a card window; only at real speed, where cards are drawn at
                # all (at x3 the ramp is one or two frames and the box blinked once per rep)
                prev_end = [rr["f_end"] for rr in atts if rr["f_end"] + int(2.0 * fps) <= fi]
                if prev_end:
                    gh_a = min(1.0, (fi - (max(prev_end) + int(2.0 * fps))) / (0.15 * fps))
            if gh_a > 0.01:
                ga = int(255 * gh_a)
                x0, y0, x1, y1 = 60, 1192, 936, 1478
                rounded(dr, (x0, y0, x1, y1), 24, (*INK, int(215 * gh_a)))
                # Dennis, 2026-09-09 evening: the credit is "by Fable" only, the repository NAME sits on
                # top with no slash, and the link line ends with one (the box said DyeAllPies three times)
                dr.text((x0 + 24, y0 + 22), "PULL UP ANALYSIS · BY FABLE", font=fit(dr, "PULL UP ANALYSIS · BY FABLE", FONT_S, 30, 828), fill=(*MUTED, ga))
                dr.text((x0 + 24, y0 + 64), "dyeallpies-productions", font=fit(dr, "dyeallpies-productions", FONT_B, 82, 828), fill=(*WHITE, ga))
                gh_l1 = "github.com/DyeAllPies/dyeallpies-productions/"
                dr.text((x0 + 24, y0 + 170), gh_l1, font=fit(dr, gh_l1, FONT_S, 40, 828), fill=(*ORANGE, ga))
                gh_l2 = "the scripts, the muscle model and the papers, open"
                dr.text((x0 + 24, y0 + 226), gh_l2, font=fit(dr, gh_l2, FONT_R, 30, 828), fill=(*MUTED, ga))

        rounded(dr, (PX0, PY0, PX1, PY1), 24, (*INK, 200))
        dr.text((PX0 + 24, PY0 + 14), "SHOULDER HEIGHT", font=F["small"], fill=MUTED)
        if masks is not None:
            grad = Image.fromarray(cv2.cvtColor(cv2.LUT(cv2.merge([np.tile(np.arange(256, dtype=np.uint8), (10, 1))] * 3), LUT), cv2.COLOR_BGR2RGB)).resize((150, 12))
            gx = PX1 - 24 - 150
            ov.paste(grad.convert("RGBA"), (gx, PY0 + 24)); dr = ImageDraw.Draw(ov)
            dr.text((gx - 12, PY0 + 16), "MUSCLE EFFORT  rest", font=F["tiny"], fill=MUTED, anchor="ra")
            dr.text((PX1 - 24, PY0 + 40), "max · a model, not a thermal camera", font=F["tiny"], fill=MUTED, anchor="ra")
        else:
            dr.text((PX0 + 24 + dr.textlength("SHOULDER HEIGHT", font=F["small"]) + 18, PY0 + 18), "0 = hang · 100 = best rep", font=F["tiny"], fill=MUTED)
        for pct, lab in ((0, "0"), (50, "50"), (100, "100")):
            yy = hy(pct); dr.line((CX0, yy, CX1, yy), fill=(70, 70, 68), width=1)
            dr.text((CX0 - 6, yy), lab, font=F["tiny"], fill=MUTED, anchor="rm")
        upto = fi + 1
        if upto > 1:
            pts = trace_pts[hang0 if fi >= hang0 else 0:upto]
            if len(pts) > 1:
                dr.line(pts, fill=WHITE, width=3, joint="curve")
        for r2 in atts:
            if r2["f_top"] <= fi:
                x, y = trace_pts[r2["f_top"]]
                gc = ORANGE if r2.get("failed") else VERDICT_COL[r2.get("chin_verdict", "at")]
                dr.ellipse((x - 8, y - 8, x + 8, y + 8), fill=gc, outline=INK, width=2)
                dr.text((x, y - 14), str(r2["rep"]) if r2.get("rep") else "X", font=F["tiny"], fill=WHITE, anchor="ms")
        px = tx(t[fi]); dr.line((px, CY0, px, CY1), fill=(*pc, 220), width=2)
        for k, r2 in enumerate(atts):
            cx = CX0 + k * ((CX1 - CX0) / len(atts)); cw = (CX1 - CX0) / len(atts) - 8
            done = r2["f_end"] <= fi
            col = (ORANGE if r2.get("failed") else VERDICT_COL[r2.get("chin_verdict", "at")]) if done else (60, 60, 58)
            rounded(dr, (cx, PY1 - 56, cx + cw, PY1 - 16), 10, (*col, 255))
            dr.text((cx + cw / 2, PY1 - 36), "X" if r2.get("failed") else str(r2["rep"]), font=F["small"],
                    fill=INK if done else MUTED, anchor="mm")

        if kind == "summary":
            # The closing frame is a REFERENCES card (Dennis, 2026-09-09: the judge's card was a
            # static screen people skip; the numbers live in the caption and the report, the papers
            # go here, held for `hold` seconds). Grouped by what each one feeds.
            a = 255
            rounded(dr, (60, 200, 936, 1170), 28, (*INK, 236))
            dr.text((498, 224), "REFERENCES", font=F["sum_h"], fill=(*WHITE, a), anchor="ma")
            dr.text((498, 292), "the papers behind every number · full archive in the repository", font=F["tiny"], fill=(*MUTED, a), anchor="ma")
            refs = [("EMG", "Youdas et al. 2010 · J Strength Cond Res · pull-up vs chin-up"),
                    ("", "Dickie et al. 2017 · J Electromyogr Kinesiol · grips, concentric vs eccentric"),
                    ("", "Snarr et al. 2017 · grip width · Prinold & Bull 2016 · scapula"),
                    ("", "Dinunzio et al. 2018 · kipping vs strict · Tucker et al. 2011"),
                    ("MODEL", "Crowninshield & Brand 1981 · J Biomech · force sharing"),
                    ("", "Hill 1938 · force–velocity · Thelen 2003 · activation dynamics"),
                    ("", "Xia & Frey-Law 2008 · fatigue · Frey-Law et al. 2012 · rates"),
                    ("", "Murray, Delp & Buchanan 1995 · elbow arms · Ackland et al. 2008 · shoulder"),
                    ("", "Holzbaur et al. 2005 · upper-limb model · de Leva 1996 · segments"),
                    ("HEAT", "Umberger et al. 2003 · energetics · González-Alonso et al. 2000 · J Physiol"),
                    ("", "Kenny et al. 2003 · Ducharme & Tikuisis 1991 · Jung et al. 2021"),
                    ("SPEED", "Sánchez-Moreno et al. 2020 · velocity loss · Beckham et al. 2018"),
                    ("VISION", "MediaPipe Pose · YOLOv8-pose · Lin et al. 2022 · Robust Video Matting"),
                    ("STANDARD", "USMC PFT pull-up · chin above the bar, dead hang, no kip")]
            for k, (tag, txt) in enumerate(refs):
                yy = 340 + k * 54
                if tag:
                    dr.text((96, yy + 6), tag, font=F["pill_l"], fill=(*ORANGE, a))
                dr.text((252, yy), txt, font=fit(dr, txt, FONT_S, 32, 896 - 252), fill=(*WHITE, a))
            foot = "github.com/DyeAllPies/dyeallpies-productions/ · references/pullup-science · 70 papers, tables and full texts"
            # measured 2026-09-09: 736 px wide at the 16 px floor (18 px would be 844, over the box)
            dr.text((498, 1152), foot, font=fit(dr, foot, FONT_R, 24, 820), fill=(*MUTED, a), anchor="ms")

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
