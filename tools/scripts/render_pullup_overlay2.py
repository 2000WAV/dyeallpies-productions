"""
Render the pull-up analysis, version 2.

    python render_pullup_overlay2.py <video> <pose_mp.npz> <analysis.json> <out.mp4>
        [hold=3.0] [heat=matte.npy] [look=1] [schedule=sched.json] [preview=f1,f2,..]
        [silent=1]

Differences from render_pullup_overlay.py (kept for the first video):
  * the bar is a LINE (camera yaw), drawn and used as such;
  * the body colour is MODELLED MUSCLE TEMPERATURE in degrees C from pullup_thermal.py,
    on a fixed 0..+2.5 C scale with a legend that says what it is and is not;
  * muscle regions come from the landmark-warped atlas (pullup_atlas.py);
  * reps and failed attempts are distinguished everywhere;
  * a left/right SYMMETRY readout;
  * a JUDGE'S CARD outro naming the standard the reps were judged against;
  * schedule= renders a cut (freezes and speed-ups) from the SOURCE frames, so overlays
    never strobe the way decimating a finished render would.

schedule.json = [{"kind":"freeze","f":1861,"dur":1.2,"title":"..."},
                 {"kind":"play","f0":330,"f1":432,"step":1},
                 {"kind":"play","f0":432,"f1":1722,"step":6},
                 {"kind":"summary","dur":3.5}]
"""
import sys, json, subprocess, os
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pullup_heat import definition_map, LUT
from pullup_look import LookPass
import pullup_thermal as TH
import pullup_atlas as AT

FONT_B = "C:/Windows/Fonts/segoeuib.ttf"
FONT_S = "C:/Windows/Fonts/seguisb.ttf"
FONT_R = "C:/Windows/Fonts/segoeui.ttf"
FONT_SYM = "C:/Windows/Fonts/seguisym.ttf"
VERDICT = {"above": ("CHIN ABOVE BAR", "\u2713"), "at": ("CHIN AT BAR", "~"), "short": ("CHIN SHORT", "\u2717")}
VERDICT_COL = {"above": (25, 158, 112), "at": (201, 133, 0), "short": (217, 89, 38)}

BLUE = (57, 135, 229); ORANGE = (217, 89, 38); AQUA = (25, 158, 112); YELLOW = (201, 133, 0)
RED = (230, 103, 103); WHITE = (255, 255, 255); MUTED = (195, 194, 183); INK = (26, 26, 25)
PHASE_COL = {"PULL": AQUA, "HOLD": YELLOW, "LOWER": BLUE, "HANG": MUTED, "HANDS ON BAR": MUTED,
             "LOADING": YELLOW, "SETUP": MUTED, "DONE": MUTED}
EDGES = [(11, 13, BLUE), (13, 15, BLUE), (12, 14, ORANGE), (14, 16, ORANGE),
         (11, 12, WHITE), (11, 23, WHITE), (12, 24, WHITE), (23, 24, WHITE),
         (23, 25, BLUE), (25, 27, BLUE), (24, 26, ORANGE), (26, 28, ORANGE),
         (15, 19, BLUE), (16, 20, ORANGE), (27, 31, BLUE), (28, 32, ORANGE)]
JOINTS = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
T_SCALE = 2.5            # degrees C that map to the top of the colour scale
GRID_BOTTOM = 1500       # the form grid stops above the chart panel


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


def paint_heat(frame_bgr, comp_small, P, reg_T, def_ref, bar_line, alpha=0.95, reg_A=None):
    """Colour the body by modelled muscle temperature, clipped to the matte silhouette.

    Colour = temperature (a slow, accumulating quantity, on a fixed degrees-C scale).
    Brightness pulses with modelled ACTIVATION, which follows the movement itself, so the
    map breathes with each rep instead of only creeping upward. Two quantities, two
    channels, both named in the legend."""
    H, W = frame_bgr.shape[:2]
    cs = comp_small.astype(np.float32) / 255
    a_s, clothes, head = cs[..., 0], cs[..., 1], cs[..., 2]
    hs, ws = a_s.shape
    s = ws / W
    sh = (P[11] + P[12]) / 2 * s
    hip = (P[23] + P[24]) / 2 * s
    trunk = float(np.linalg.norm(hip - sh)) + 1e-3
    yy = np.arange(hs, dtype=np.float32)[:, None]
    xx = np.arange(ws, dtype=np.float32)[None, :]
    ear = (P[7] + P[8]) / 2 * s
    # The head gate must NOT be scaled by the ear separation: when he tilts his head back at
    # the top of a rep the ears close up in the image and the gate collapses to a dot, which
    # let the paint run over his face. Scale it on the shoulder width, which is stable.
    sw = max(float(np.linalg.norm(P[11] - P[12])) * s, 20.0)
    head_r = max(0.62 * sw, 1.9 * float(np.linalg.norm(P[7] - P[8])) * s)
    above = np.clip((sh[1] - 0.10 * trunk - yy) / (0.06 * trunk), 0, 1)
    near = np.clip((head_r - np.sqrt((xx - ear[0]) ** 2 + (yy - ear[1]) ** 2)) / (0.22 * head_r), 0, 1)
    head_g = np.clip(head * 1.6, 0, 1) * above * near
    below = np.clip((yy - (hip[1] - 0.30 * trunk)) / (0.06 * trunk), 0, 1)
    clothes_g = clothes * below
    m = a_s * (1 - head_g) * (1 - clothes_g)
    bar_row = (bar_line[0] * xx / s + bar_line[1]) * s
    m = m * np.clip((yy - (bar_row + 6 * s)) / 3.0, 0, 1)          # nothing above the bar is body
    # the legs are painted too (Dennis asked for it, and they are genuinely near-zero, so
    # they read blue); the shorts are still removed by the gated clothes class above.
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    field, act, _ = AT.build(P, m, reg_T, T_SCALE, (H, W), reg_A=reg_A)
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    er = cv2.erode((m > 0.5).astype(np.uint8), np.ones((9, 9), np.uint8))
    interior = cv2.resize(cv2.GaussianBlur(er.astype(np.float32), (0, 0), 2), (W, H))
    d = np.clip(definition_map(gray) / def_ref, 0, 1.2) * interior
    heat = cv2.resize(field, (W, H), interpolation=cv2.INTER_LINEAR)
    heat = np.clip(0.06 + 0.86 * heat + 0.10 * d * heat, 0, 1)
    idx = (heat * 255).astype(np.uint8)
    col = cv2.LUT(cv2.merge([idx, idx, idx]), LUT).astype(np.float32)
    lum = (0.78 + 0.26 * gray.astype(np.float32) / 255)[:, :, None]
    col = col * lum
    if reg_A is not None:
        af = cv2.resize(act, (W, H), interpolation=cv2.INTER_LINEAR)[:, :, None]
        col = np.clip(col * (0.82 + 0.42 * af), 0, 255)          # activation pulses the brightness
    mf = cv2.resize(m, (W, H), interpolation=cv2.INTER_CUBIC)
    mf = np.clip(cv2.GaussianBlur(mf, (0, 0), 1.0), 0, 1)
    aa = mf[:, :, None] * alpha
    # the LOOK pass needs the whole person (head, legs and shorts included), not the paint
    # region - otherwise it treats them as background and desaturates them.
    person = np.clip(cv2.resize(a_s, (W, H), interpolation=cv2.INTER_LINEAR), 0, 1)
    return np.clip(frame_bgr.astype(np.float32) * (1 - aa) + col * aa, 0, 255).astype(np.uint8), person


def main():
    video, npz, ajson, out = sys.argv[1:5]
    hold_s = 3.0; heat_path = None; preview = None; look_on = False; sched_path = None
    silent = False; trim = None; bg_path = None; grid_on = False; red_path = None
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
        elif a.startswith("redness="): red_path = a[8:]
        else: hold_s = float(a)

    d = np.load(npz); img = d["img"]; ok = d["ok"]; fps = float(d["fps"])
    W, H = int(d["width"]), int(d["height"])
    P = img[:, :, :2] * np.array([W, H]); V = img[:, :, 3]
    A = json.load(open(ajson)); S = A["summary"]; atts = A["reps"]; sig = A["signals"]
    reps = [r for r in atts if r.get("rep")]
    N = len(img); t = np.array(sig["t"])
    vy = np.array(sig["vy_m"]); el_l = np.array(sig["elbow_l"]); el_r = np.array(sig["elbow_r"])
    sh_tilt = np.array(sig["sh_tilt"])
    bar_a, bar_b = S["bar_slope"], S["bar_intercept"]
    hang0, hang1 = sig["hang0"], sig["hang1"]; grab0, load0 = sig["grab0"], sig["load0"]
    phase = list(sig["phase"])
    ppm = S["px_per_m"]
    hang_ref, top_ref = S["hang_ref_y"], S["top_ref_y"]
    height_pct = np.clip(np.array(sig["height_pct"]), -10, 115)
    rom_cm = (hang_ref - top_ref) / ppm * 100
    chin_bar_pct = 100 + (-S["mean_chin_cm"]) / rom_cm * 100     # where the chin would clear

    # ---- thermal model ----
    Tm = TH.integrate(A)
    Am = TH.activation(A)
    masses = TH.muscle_masses()
    tsum = TH.summarise(A, Tm)
    hot_name = tsum["hottest"]
    lat_T = Tm["latissimus dorsi"]; lat_A = Am["latissimus dorsi"]
    red_curve = None; red_info = None
    if red_path:
        red_info = json.load(open(red_path))
        gp = [p for p in red_info["per_rep"] if p.get("valid", True)]
        xs_ = [red_info["per_rep"][0]["t"] - 6.0] + [p["t"] for p in gp]
        ys_ = [red_info["baseline"]["corrected"]] + [p["corrected"] for p in gp]
        red_curve = np.interp(t, xs_, ys_)
        print(f"redness: standing {ys_[0]:.1f} -> {max(ys_):.1f}, r with modelled temp "
              f"{red_info.get('r_with_modelled_temp', 0):.2f}", flush=True)

    kcal = np.zeros(N)
    if "kcal" in atts[0]:
        rate = np.zeros(N); rate[hang0:hang1 + 1] = S["hang_kcal_per_s"] / fps
        for r in atts:
            a0, b0 = r["f_start"], r["f_end"]
            rate[a0:b0 + 1] += (r["kcal"] - S["hang_kcal_per_s"] * (b0 - a0 + 1) / fps) / (b0 - a0 + 1)
        kcal = np.cumsum(rate)
    vloss = np.zeros(N); best = 0.0
    for r in atts:
        best = max(best, r["peak_conc_v"]); vloss[r["f_end"]:] = (1 - r["peak_conc_v"] / best) * 100

    count = np.zeros(N, int); card = [None] * N
    for r in atts:
        if r.get("rep"):
            count[r["f_top"]:] = r["rep"]
        for i in range(r["f_end"], min(N, r["f_end"] + int(1.8 * fps))):
            card[i] = r

    F = {k: font(*v) for k, v in dict(
        counter=(FONT_B, 190), counter_lbl=(FONT_S, 44), phase=(FONT_B, 60), metric=(FONT_S, 40),
        small=(FONT_S, 30), tiny=(FONT_R, 26), card_t=(FONT_B, 48), card=(FONT_S, 34),
        title=(FONT_B, 72), sub=(FONT_S, 38), sum_h=(FONT_B, 58), sum_big=(FONT_B, 120),
        sum_l=(FONT_S, 32), sym=(FONT_SYM, 30), big=(FONT_B, 96)).items()}

    PX0, PY0, PX1, PY1 = 60, 1536, 936, 1822
    CX0, CY0, CX1, CY1 = PX0 + 24, PY0 + 56, PX1 - 24, PY1 - 70
    t_end = t[-1]

    def tx(tt): return CX0 + (CX1 - CX0) * tt / t_end

    def hy(pct): return CY1 - (CY1 - CY0) * np.clip(pct, -5, 112) / 112
    trace_pts = [(tx(t[i]), hy(height_pct[i])) for i in range(N)]

    masks = None; look = None; def_ref = 1.0
    if heat_path:
        masks = np.load(heat_path, mmap_mode="r")
        capc = cv2.VideoCapture(video); refs = []
        for fr in [r["f_bottom1"] for r in reps[:3]]:
            capc.set(cv2.CAP_PROP_POS_FRAMES, fr); got, fm = capc.read()
            if not got: continue
            dm = definition_map(cv2.cvtColor(fm, cv2.COLOR_BGR2GRAY))
            mm = cv2.resize(np.asarray(masks[fr])[..., 0], (W, H)) > 128
            if mm.sum() > 1000: refs.append(np.percentile(dm[mm], 92))
        capc.release()
        def_ref = float(np.median(refs)) if refs else 12.0
        print(f"heat: definition ref {def_ref:.1f}; scale 0..{T_SCALE} C; "
              f"lats end at +{lat_T.max():.2f} C", flush=True)
        look = LookPass(W, H) if look_on else None
    plate = None; bar_mask = None
    if bg_path:
        plate = cv2.resize(cv2.imread(bg_path), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
        capb = cv2.VideoCapture(video); _, f0 = capb.read(); capb.release()
        g0 = cv2.cvtColor(f0, cv2.COLOR_BGR2GRAY)
        band = np.zeros((H, W), np.uint8)
        xs_ = np.arange(W)
        for x in xs_:                                     # a band that follows the bar LINE
            yb = int(bar_a * x + bar_b)
            band[max(0, yb - 34):min(H, yb + 34), x] = 1
        barm = ((g0 < 80).astype(np.uint8) * band)
        barm = cv2.morphologyEx(barm, cv2.MORPH_CLOSE, np.ones((5, 21), np.uint8))
        barm = cv2.dilate(barm, np.ones((5, 5), np.uint8))
        bar_mask = cv2.GaussianBlur(barm.astype(np.float32), (0, 0), 1.5)[:, :, None]
        print(f"backdrop: {bg_path}, bar kept over {int((barm > 0).sum())} px", flush=True)

    # ---- build the output frame list ----
    plan = []          # (source_frame, kind, extra)
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
                back = plan[-1][0] if plan else N - 1     # freeze on the last frame shown
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
        cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{W}x{H}", "-r", f"{fps}", "-i", "pipe:0"]
        if not silent and not sched_path:
            off = (trim[0] / fps) if trim else 0.0
            cmd += ["-ss", f"{off:.3f}", "-i", video, "-map", "0:v", "-map", "1:a", "-af", "apad", "-shortest"]
        cmd += ["-c:v", "h264_nvenc", "-preset", "p5", "-tune", "hq", "-rc", "vbr", "-cq", "19",
                "-b:v", "0", "-spatial-aq", "1", "-temporal-aq", "1", "-pix_fmt", "yuv420p"]
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
            # read forward when we can (seeking every frame costs a keyframe decode each time);
            # seek only for a backward jump or a gap longer than a GOP
            if cur_src >= 0 and 0 < fi - cur_src <= 12:
                for _ in range(fi - cur_src):
                    got, fr = cap.read()
                    if not got:
                        break
            else:
                cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
                got, fr = cap.read()
            if got:
                frame = fr; cur_src = fi
        f = frame.copy()
        if ok[fi]:
            P_use, V_use = P[fi], V[fi]; last_ok = (P[fi], V[fi])
        else:
            P_use, V_use = last_ok if last_ok is not None else (P[fi], V[fi])
        ph = phase[fi] if kind != "summary" else "DONE"
        pc = PHASE_COL.get(ph, MUTED)
        fast = int(seg.get("step", 1)) if kind == "play" else 1

        comp_now = np.asarray(masks[fi]) if masks is not None else None
        if plate is not None and comp_now is not None:
            alpha_full = cv2.resize(comp_now[..., 0], (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255
            z = 1.0 + 0.06 * (i / max(1, total - 1))
            cw, ch = int(W / z), int(H / z); px0 = (W - cw) // 2; py0 = (H - ch) // 2
            pl = cv2.resize(plate[py0:py0 + ch, px0:px0 + cw], (W, H), interpolation=cv2.INTER_LINEAR)
            keep = np.clip(alpha_full[:, :, None] + bar_mask, 0, 1)
            f = np.clip(pl * (1 - keep) + f.astype(np.float32) * keep, 0, 255).astype(np.uint8)
        if masks is not None and last_ok is not None and ph not in ("SETUP",):
            reg_T = AT.region_temperatures(Tm, masses, fi)
            reg_A = AT.region_values(Am, masses, fi)
            f, mf = paint_heat(f, comp_now, P_use, reg_T, def_ref, (bar_a, bar_b), reg_A=reg_A)
            if look is not None:
                rim_v = float(np.clip(lat_T[fi] / T_SCALE, 0, 1))
                rim = tuple(int(c) for c in LUT[int((0.15 + 0.7 * rim_v) * 255), 0])
                f = look.apply(f, mf, rim, 1.0, i, keep_colour=plate is not None)

        if last_ok is not None:
            Pf, Vf = P_use, V_use
            for a1, b1, col in EDGES:
                if Vf[a1] > 0.5 and Vf[b1] > 0.5:
                    pa, pb = tuple(Pf[a1].astype(int)), tuple(Pf[b1].astype(int))
                    cv2.line(f, pa, pb, INK, 11, cv2.LINE_AA)
                    cv2.line(f, pa, pb, col[::-1], 5, cv2.LINE_AA)
            for j in JOINTS:
                if Vf[j] > 0.5:
                    p = tuple(Pf[j].astype(int))
                    cv2.circle(f, p, 13, INK, -1, cv2.LINE_AA)
                    cv2.circle(f, p, 8, WHITE[::-1], -1, cv2.LINE_AA)
        # ---- see-through form grid, drawn under the skeleton ----
        if grid_on and last_ok is not None and ph not in ("SETUP", "DONE"):
            gl = f.copy()
            step = 0.10 * ppm                               # a rule every 10 cm below the bar
            k = 1
            while True:
                off = int(round(k * step))
                if int(bar_b) + off > GRID_BOTTOM:
                    break
                cv2.line(gl, (0, int(bar_b) + off), (W, int(bar_a * W + bar_b) + off),
                         (215, 215, 210), 1, cv2.LINE_AA)
                if k % 2 == 0:
                    cv2.putText(gl, f"-{k * 10}", (10, int(bar_b) + off - 6),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.44, (215, 215, 210), 1, cv2.LINE_AA)
                k += 1
            gc_x = int((P_use[15][0] + P_use[16][0]) / 2)   # plumb line through the middle of the grip
            for yy0 in range(int(bar_a * gc_x + bar_b), GRID_BOTTOM, 26):
                cv2.line(gl, (gc_x, yy0), (gc_x, min(yy0 + 14, GRID_BOTTOM)), (240, 240, 236), 2, cv2.LINE_AA)
            f = cv2.addWeighted(f, 0.66, gl, 0.34, 0)
            # the shoulder line against a true horizontal through its own midpoint: the tilt
            # a viewer is being asked to judge, drawn at full strength
            sl_, sr_ = P_use[11].astype(int), P_use[12].astype(int)
            smx, smy = (sl_[0] + sr_[0]) // 2, (sl_[1] + sr_[1]) // 2
            half_w = int(abs(sl_[0] - sr_[0]) * 0.72) + 30
            cv2.line(f, (smx - half_w, smy), (smx + half_w, smy), (120, 120, 118), 2, cv2.LINE_AA)
            cv2.line(f, tuple(sl_), tuple(sr_), (255, 255, 255), 2, cv2.LINE_AA)

        # the bar line (dashed, follows the fitted line)
        for x in range(0, W, 36):
            y1p = int(bar_a * x + bar_b); y2p = int(bar_a * min(x + 18, W) + bar_b)
            cv2.line(f, (x, y1p), (min(x + 18, W), y2p), (255, 255, 255), 2, cv2.LINE_AA)

        im = Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)).convert("RGBA")
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(ov)
        dr.text((W - 150, int(bar_a * (W - 150) + bar_b) - 40), "BAR", font=F["small"], fill=(*WHITE, 230), anchor="ls")

        if kind == "freeze":
            ttl = seg.get("title"); sub = seg.get("sub")
            rounded(dr, (60, 250, 936, 470 if not sub else 520), 24, (*INK, 215))
            if ttl:
                dr.text((84, 272), ttl, font=fit(dr, ttl, FONT_B, 72, 828), fill=(*ORANGE, 255))
            if sub:
                dr.text((84, 372), sub, font=fit(dr, sub, FONT_S, 40, 828), fill=WHITE)
                dr.text((84, 436), seg.get("sub2", ""), font=fit(dr, seg.get("sub2", ""), FONT_R, 30, 828), fill=MUTED)
        elif ph == "SETUP":
            rounded(dr, (60, 240, 936, 500), 24, (*INK, 200))
            dr.text((84, 262), "PULL UP ANALYSIS", font=fit(dr, "PULL UP ANALYSIS", FONT_B, 72, 828), fill=WHITE)
            dr.text((84, 350), "by Fable and DyeAllPies", font=fit(dr, "by Fable and DyeAllPies", FONT_S, 44, 828), fill=WHITE)
            sub = "33-point pose tracking · judged to the USMC pull-up standard"
            dr.text((84, 416), sub, font=fit(dr, sub, FONT_S, 32, 828), fill=MUTED)
        elif kind != "summary":
            rounded(dr, (60, 240, 420, 470), 24, (*INK, 200))
            dr.text((84, 226), str(count[fi]), font=F["counter"], fill=WHITE)
            dr.text((84, 420), "REPS", font=F["counter_lbl"], fill=MUTED)
            pw = dr.textlength(ph, font=F["phase"]) + 60
            rounded(dr, (60, 492, 60 + pw, 570), 20, (*pc, 235))
            dr.text((90, 500), ph, font=F["phase"], fill=WHITE if ph in ("PULL", "LOWER") else INK)
            if fast > 1:
                fw = dr.textlength(f"×{fast}", font=F["phase"]) + 48
                rounded(dr, (60 + pw + 14, 492, 60 + pw + 14 + fw, 570), 20, (*WHITE, 230))
                dr.text((60 + pw + 14 + 24, 500), f"×{fast}", font=F["phase"], fill=INK)
            y0 = 600
            lt = lat_T[fi]
            if fast > 1:
                rows = [("LATS  activation", f"{lat_A[fi] * 100:.0f} %", WHITE),
                        ("LATS  modelled temp", f"+{lt:.2f} °C", WHITE),
                        ("FATIGUE  speed loss", f"{vloss[fi]:.0f} %", WHITE if vloss[fi] < 20 else YELLOW if vloss[fi] < 35 else ORANGE)]
            else:
                rows = [("ELBOW", f"{(el_l[fi] + el_r[fi]) / 2:.0f}°", WHITE),
                        ("LATS  activation", f"{lat_A[fi] * 100:.0f} %", WHITE),
                        ("LATS  modelled temp", f"+{lt:.2f} °C", WHITE),]
                if red_curve is not None:
                    rows.append(("CHEST FLUSH  measured", f"{red_curve[fi]:.0f}", ORANGE))
                rows += [
                        ("SHOULDER TILT  L/R", f"{sh_tilt[fi]:+.1f}°", WHITE if abs(sh_tilt[fi]) < 3 else YELLOW),
                        ("FATIGUE  speed loss", f"{vloss[fi]:.0f} %", WHITE if vloss[fi] < 20 else YELLOW if vloss[fi] < 35 else ORANGE)]
            rounded(dr, (60, y0 - 16, 520, y0 + len(rows) * 92 - 8), 24, (*INK, 170))
            for k, (lab, val, col) in enumerate(rows):
                yy = y0 + k * 92
                dr.text((84, yy), lab, font=F["small"], fill=MUTED)
                dr.text((84, yy + 30), val, font=fit(dr, val, FONT_B, 52, 412), fill=col)
            gx0, gx1, gy0, gy1 = 872, 924, 620, 1120
            rounded(dr, (gx0 - 10, gy0 - 10, gx1 + 10, gy1 + 10), 18, (*INK, 170))
            rounded(dr, (gx0, gy0, gx1, gy1), 12, (60, 60, 58, 255))
            hp = float(np.clip(height_pct[fi], 0, 112)) / 112
            rounded(dr, (gx0, gy1 - (gy1 - gy0) * hp, gx1, gy1), 12, (*pc, 255))
            cy = gy1 - (gy1 - gy0) * np.clip(chin_bar_pct, 0, 112) / 112
            dr.line((gx0 - 8, cy, gx1 + 8, cy), fill=WHITE, width=3)
            dr.text((gx0 - 16, cy - 30), "CHIN OVER", font=F["tiny"], fill=WHITE, anchor="ra")
            dr.text((gx0 - 16, cy - 4), "THE BAR", font=F["tiny"], fill=WHITE, anchor="ra")

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
            note = f"chin {r['chin_cm']:+.1f} cm vs bar  ±1.5"
            dr.text((bcx, y1 - 30), note, font=fit(dr, note, FONT_R, 24, x1 - 24 - bx0 - 24), fill=(*INK, a), anchor="ms")
            head = f"REP {r['rep']}" if r.get("rep") else "ATTEMPT 12"
            dr.text((x0 + 24, y0 + 18), head, font=F["card_t"], fill=(*WHITE, a))
            lock = "FULL LOCK-OUT" if r["lockout"] else "NO LOCK-OUT"
            cx = x0 + 24
            for txt, good in ((lock, r["lockout"]), ("NO SWING", r["hip_sway_cm"] <= 8)):
                col = AQUA if good else ORANGE
                tw = dr.textlength(txt, font=F["small"]) + 28
                rounded(dr, (cx, y0 + 84, cx + tw, y0 + 126), 12, (*col, a))
                dr.text((cx + 14, y0 + 89), txt, font=F["small"], fill=(*INK, a))
                cx += tw + 12
            lines = [f"up {r['t_concentric']:.1f} s   hold {r['t_top_hold']:.1f} s   down {r['t_eccentric']:.1f} s",
                     f"peak {r['peak_conc_v']:.2f} m/s   {r['mean_power_w']:.0f} W   ≈ {r['kcal']:.2f} kcal",
                     f"shoulder tilt {r['sh_tilt_top']:+.1f}°   sway {r['hip_sway_cm']:.0f} cm"]
            for k, ln in enumerate(lines):
                dr.text((x0 + 24, y0 + 142 + k * 44), ln, font=fit(dr, ln, FONT_S, 32, x1 - x0 - 380), fill=(*MUTED, a))

        if masks is not None and ph not in ("SETUP",) and kind != "summary":
            lx0, lx1, ly = 556, 852, 1082
            rounded(dr, (lx0, ly - 10, lx1, ly + 78), 12, (*INK, 205))
            dr.text((lx0 + 12, ly - 6), "MODELLED MUSCLE TEMP", font=F["tiny"], fill=WHITE)
            grad = Image.fromarray(cv2.cvtColor(cv2.LUT(cv2.merge([np.tile(np.arange(256, dtype=np.uint8), (10, 1))] * 3), LUT), cv2.COLOR_BGR2RGB)).resize((lx1 - lx0 - 24, 12))
            ov.paste(grad.convert("RGBA"), (lx0 + 12, ly + 24))
            dr = ImageDraw.Draw(ov)
            dr.text((lx0 + 12, ly + 40), "0", font=F["tiny"], fill=MUTED)
            dr.text((lx1 - 12, ly + 40), f"+{T_SCALE:g} °C", font=F["tiny"], fill=MUTED, anchor="ra")
            legend_cap = "colour = temp · brightness = activation"
            dr.text((lx0 + 12, ly + 62), legend_cap,
                    font=fit(dr, legend_cap, FONT_R, 26, lx1 - lx0 - 24), fill=MUTED)

        rounded(dr, (PX0, PY0, PX1, PY1), 24, (*INK, 200))
        dr.text((PX0 + 24, PY0 + 14), "SHOULDER HEIGHT", font=F["small"], fill=MUTED)
        dr.text((PX0 + 24 + dr.textlength("SHOULDER HEIGHT", font=F["small"]) + 18, PY0 + 18),
                "0 % = dead hang · 100 % = best rep", font=F["tiny"], fill=MUTED)
        for pct, lab in ((0, "0"), (50, "50"), (100, "100")):
            yy = hy(pct); dr.line((CX0, yy, CX1, yy), fill=(70, 70, 68), width=1)
            dr.text((CX0 - 6, yy), lab, font=F["tiny"], fill=MUTED, anchor="rm")
        cyb = hy(chin_bar_pct); dr.line((CX0, cyb, CX1, cyb), fill=(*WHITE, 140), width=2)
        dr.text((CX1, cyb - 26), "chin over the bar", font=F["tiny"], fill=(*WHITE, 200), anchor="ra")
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
            vk2 = r2.get("chin_verdict", "at")
            col = (ORANGE if r2.get("failed") else VERDICT_COL[vk2]) if done else (60, 60, 58)
            rounded(dr, (cx, PY1 - 56, cx + cw, PY1 - 16), 10, (*col, 255))
            lab2 = "X" if r2.get("failed") else str(r2["rep"])
            dr.text((cx + cw / 2, PY1 - 36), lab2, font=F["small"],
                    fill=INK if done else MUTED, anchor="mm")

        if kind == "summary":
            a = 255
            T2 = S["technique"]; AS = S["asymmetry"]
            rounded(dr, (60, 200, 936, 1170), 28, (*INK, 232))
            dr.text((498, 226), "JUDGE'S CARD", font=F["sum_h"], fill=(*WHITE, a), anchor="ma")
            std = "judged to the USMC pull-up standard"
            dr.text((498, 292), std, font=fit(dr, std, FONT_R, 28, 820), fill=(*MUTED, a), anchor="ma")
            dr.text((260, 330), f"{S['reps']}", font=F["sum_big"], fill=(*WHITE, a), anchor="ma")
            dr.text((260, 470), "reps counted", font=F["sum_l"], fill=(*MUTED, a), anchor="ma")
            dr.text((736, 330), f"+{lat_T.max():.1f}", font=F["sum_big"], fill=(*ORANGE, a), anchor="ma")
            dr.text((736, 470), "°C modelled, lats", font=F["sum_l"], fill=(*MUTED, a), anchor="ma")
            rows = [("chin above · at · short", f"{T2['chin_above']} · {T2['chin_at']} · {T2['chin_short']}"),
                    ("mean chin vs bar", f"{S['mean_chin_cm']:+.1f} cm  (±1.5)"),
                    ("full lock-out at the bottom", f"{T2['lockouts']} / {S['reps']}"),
                    ("kipping", f"no swing — hips travel {T2['hip_sway_mean_cm']:.1f} cm"),
                    ("legs", f"knees tuck {T2['leg_tuck_deg']:.0f}° in each pull"),
                    ("range of motion", f"{S['mean_rom_cm']:.0f} cm per rep"),
                    ("tempo  up / hold / down", f"{S['mean_concentric']:.1f} / {S['mean_top_hold']:.1f} / {S['mean_eccentric']:.1f} s"),
                    ("shoulder tilt at the top", f"{AS['sh_tilt_top_deg']:+.1f}°  ({AS['sh_dy_top_cm']:+.1f} cm)"),
                    ("peak speed  best → last", f"{S['peak_v_max']:.2f} → {S['peak_v_last']:.2f} m/s  (−{S['velocity_loss_pct']:.0f} %)"),
                    ("12th attempt", f"failed, {abs(atts[-1]['chin_cm']):.0f} cm short"),
                    ("work · peak power", f"{S['set_work_kj']:.1f} kJ · {S['peak_power_w_max']:.0f} W"),
                    ("energy, rough estimate", f"≈ {S['set_kcal_total']:.0f} kcal · {tsum['total_heat_kj']:.0f} kJ of heat")]
            if red_info is not None:
                rows.append(("chest flush, measured",
                             f"{red_info['baseline']['corrected']:.0f} → {red_info.get('plateau', 0):.0f}"
                             f"  (r {red_info.get('r_with_modelled_temp', 0):.2f} vs model)"))
            for k, (lab, val) in enumerate(rows):
                yy = 536 + k * 44
                dr.text((100, yy), lab, font=F["sum_l"], fill=(*MUTED, a))
                room = 896 - 100 - dr.textlength(lab, font=F["sum_l"]) - 24
                dr.text((896, yy), val, font=fit(dr, val, FONT_S, 32, room), fill=(*WHITE, a), anchor="ra")
            foot = f"MediaPipe 33-pt + YOLOv8 agree (r={S.get('yolo_mp_shoulder_corr', 0):.3f}) · {S['height_m']*100:.0f} cm, {S['mass_kg']:.0f} kg · temp is a model"
            dr.text((498, 1158), foot, font=fit(dr, foot, FONT_R, 23, 800), fill=(*MUTED, a), anchor="ms")

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
