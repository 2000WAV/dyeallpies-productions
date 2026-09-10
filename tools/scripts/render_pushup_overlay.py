"""
Push-up Reels renderer (2026-09-10): render_pullup_overlay3's machinery (the body-layer cache, the
schedule cut, the cards, the left stack, the GitHub box, the references card) on the push-up's
signals. Full-bleed 1080x1920, no push-in: the body already fills the frame from the head end.

    python render_pushup_overlay.py <master.mp4> <pose_mp.npz> <analysis.json> <out.mp4>
        [heat=matte.npy] [bg=plate.png] [look=1] [grid=1] [lut=set1|bluered4] [trim=f0,f1] [hold=0.5]
        [schedule=sched.json] [preview=i,i,...] [silent=1] [cache=body.mkv] [bake=0|1|only]

What differs from the pull-up: phases LOWER / BOTTOM / PUSH / PLANK; the judge's three lines per rep
(USMC: upper arms parallel at the bottom, arms locked at the top, body straight); the chart is the
SHOULDER HEIGHT above the floor (0 = bottom, 100 = locked); the grid is the FLOOR (every 20 cm from
the camera model, drawn in image space); the plate is a ground-level jungle path above the corridor
floor's far edge (its own alpha); a title-card hook over the plank before rep 1; the colour is set
#1's pure blue -> red (pushup_atlas); the model is pushup_thermal (PUSHUP-MODEL.md).
"""
import sys, json, subprocess, os, time, hashlib, inspect
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pullup_look as PL
from pullup_look import LookPass
import pushup_thermal as TH
import pushup_atlas as AT
import pushup_recon as PR

FONT_B = "C:/Windows/Fonts/segoeuib.ttf"; FONT_S = "C:/Windows/Fonts/seguisb.ttf"
FONT_R = "C:/Windows/Fonts/segoeui.ttf"; FONT_SYM = "C:/Windows/Fonts/seguisym.ttf"
BLUE = (57, 135, 229); ORANGE = (217, 89, 38); AQUA = (25, 158, 112); YELLOW = (201, 133, 0)
WHITE = (255, 255, 255); MUTED = (195, 194, 183); INK = (26, 26, 25)
PHASE_COL = {"PUSH": AQUA, "BOTTOM": YELLOW, "LOWER": BLUE, "PLANK": MUTED, "SETUP": MUTED, "DONE": MUTED}
EDGES = [(11, 13, BLUE), (13, 15, BLUE), (12, 14, ORANGE), (14, 16, ORANGE), (11, 12, WHITE), (11, 23, WHITE),
         (12, 24, WHITE), (23, 24, WHITE)]
JOINTS = [11, 12, 13, 14, 15, 16, 23, 24]
GRID_BOTTOM = 1500
STACK_Y0 = 536; LABEL_Y0 = 996
LABEL_E = 0.55; LABEL_S = 1.4
CARD_BOX = (60, 1192, 936, 1478)
STD = "USMC PFT push-up"


def make_lut(stops):
    lut = np.zeros((256, 1, 3), np.uint8)
    xs = [s[0] for s in stops]; cs = np.array([s[1] for s in stops], float)
    for i in range(256):
        t = i / 255
        k = min(max(j for j in range(len(xs)) if xs[j] <= t), len(xs) - 2)
        u = (t - xs[k]) / (xs[k + 1] - xs[k])
        lut[i, 0] = np.clip(cs[k] * (1 - u) + cs[k + 1] * u, 0, 255)
    return lut


def font(path, size):
    return ImageFont.truetype(path, size)


def rounded(draw, box, r, fill):
    draw.rounded_rectangle(box, radius=r, fill=fill)


_FC = {}


def fit(draw, text, path, size, max_w, min_size=16):
    while size > min_size:
        f = _FC.get((path, size)) or _FC.setdefault((path, size), ImageFont.truetype(path, size))
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return _FC.get((path, min_size)) or _FC.setdefault((path, min_size), ImageFont.truetype(path, min_size))


def main():
    video, npz, ajson, out = sys.argv[1:5]
    hold_s = 0.5; heat_path = None; preview = None; look_on = False; sched_path = None
    silent = False; trim = None; bg_path = None; grid_on = False; lut_name = "set1"; t_scale = 1.5
    cache_path = None; bake_mode = "0"
    for a in sys.argv[5:]:
        if a.startswith("heat="): heat_path = a[5:]
        elif a.startswith("cache="): cache_path = a[6:]
        elif a.startswith("bake="): bake_mode = a[5:]
        elif a.startswith("preview="): preview = [int(x) for x in a[8:].split(",")]
        elif a.startswith("look="): look_on = a[5:] not in ("0", "", "no")
        elif a.startswith("schedule="): sched_path = a[9:]
        elif a.startswith("silent="): silent = a[7:] not in ("0", "", "no")
        elif a.startswith("hold="): hold_s = float(a[5:])
        elif a.startswith("trim="): trim = [int(x) for x in a[5:].split(",")]
        elif a.startswith("bg="): bg_path = a[3:]
        elif a.startswith("grid="): grid_on = a[5:] not in ("0", "", "no")
        elif a.startswith("lut="): lut_name = a[4:]
        elif a.startswith("tscale="): t_scale = float(a[7:])
    AT.LUT = make_lut(AT.BLUERED4 if lut_name == "bluered4" else AT._STOPS)
    LUT = AT.LUT

    d = np.load(npz); img = d["img"]; ok = d["ok"]; fps = float(d["fps"])
    W, H = int(d["width"]), int(d["height"])
    P = img[:, :, :2] * np.array([W, H]); V = np.nan_to_num(img[:, :, 3])
    A = json.load(open(ajson)); S = A["summary"]; atts = A["reps"]; sig = A["signals"]
    reps = [r for r in atts if r.get("rep")]
    N = len(img); t = np.array(sig["t"])
    vy = np.array(sig["vy_m"]); el_l = np.array(sig["elbow_l"]); el_r = np.array(sig["elbow_r"])
    sh_h = np.array(sig["sh_h"]); phase = list(sig["phase"])
    set0, set1 = sig["set0"], sig["set1"]
    height_pct = np.clip(np.array(sig["height_pct"]), -10, 115)
    first_rep = atts[0]["f_start"]
    cam = np.load("pushup/work/cam.npz"); K = cam["K"]; R = cam["R"]; z_floor = sig["z_floor"]

    # ---- static legs: the feet never move while the hands are on the floor, and MediaPipe barely sees them
    # (visibility ~0.02), so the knee and ankle landmarks used for the paint are the medians over the frames where
    # the hips are in view; once he stands up (after set1) the live landmarks take over ----
    hip_y_img = 0.5 * (P[:, 23, 1] + P[:, 24, 1]); ear_y_img = 0.5 * (P[:, 7, 1] + P[:, 8, 1])
    hips_seen = ok & ((hip_y_img - ear_y_img) > 0.6 * np.linalg.norm(P[:, 11] - P[:, 12], axis=1)) & (np.arange(N) >= set0) & (np.arange(N) <= set1)
    LEG_STATIC = np.nanmedian(P[hips_seen][:, 25:29], axis=0)
    print(f"static legs from {hips_seen.sum()} frames: knees {LEG_STATIC[0].round()} {LEG_STATIC[1].round()}, ankles {LEG_STATIC[2].round()} {LEG_STATIC[3].round()}", flush=True)

    def with_legs(Pf, fi):
        if fi <= set1:
            Pf = Pf.copy(); Pf[25:29] = LEG_STATIC
        return Pf

    # ---- the muscle model (PUSHUP-MODEL.md) ----
    Mo = TH.model(A); Tm = Mo["T"]; Am = Mo["a_eff"]; Em = Mo["E"]; masses = TH.muscle_masses()
    fat_pec = Mo["MF"]["pectoralis major"]; fat_tri = Mo["MF"]["triceps"]
    pec_T = Tm["pectoralis major"]
    print(f"model: elbow moment peak {Mo['M_el'].max():.0f} N m, shoulder {Mo['M_sh'].max():.0f} N m; fatigued pools at the end: pec {fat_pec[-1]*100:.0f} %, triceps {fat_tri[-1]*100:.0f} %", flush=True)
    heat_kj = np.cumsum(sum(Mo["q"][m] for m in Mo["q"])) / fps / 1000
    kcal = heat_kj / 4.184
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
    order = sorted(label_at, key=lambda r: label_at[r]); last = -999
    for r in order:
        if label_at[r] < last + int(LABEL_S * fps) + 2:
            label_at[r] = last + int(LABEL_S * fps) + 2
        last = label_at[r]
    print("labels:", {AT.LABELS[r]: round(label_at[r] / fps, 1) for r in order}, flush=True)

    # live tallies: reps passed on all three lines, speed vs the fastest, running peak power
    peak_ref = max(r["peak_conc_v"] for r in reps)
    vloss = np.zeros(N); passed = np.zeros(N, int); judged = np.zeros(N, int); peak_w = np.zeros(N)
    for r in atts:
        vloss[r["f_end"]:] = max(0.0, (1 - r["peak_conc_v"] / peak_ref) * 100)
        judged[r["f_end"]:] += 1
        if r.get("rep") and r["depth_pass"] and r["parallel_pass"] and r["lockout"] and r["straight"]:
            passed[r["f_end"]:] += 1
        peak_w[r["f_end"]:] = np.maximum(peak_w[r["f_end"]:], r.get("peak_power_w", 0.0))
    count = np.zeros(N, int); card = [None] * N
    for r in atts:
        if r.get("rep"):
            count[r["f_end"]:] = r["rep"]
        for i in range(r["f_end"], min(N, r["f_end"] + int(2.0 * fps))):
            card[i] = r

    F = {k: font(*v) for k, v in dict(
        counter=(FONT_B, 150), counter_lbl=(FONT_S, 36), phase=(FONT_B, 54), pill=(FONT_B, 40), pill_l=(FONT_S, 26),
        small=(FONT_S, 34), tiny=(FONT_R, 27), card_t=(FONT_B, 52), card=(FONT_S, 36),
        sum_h=(FONT_B, 60), sym=(FONT_SYM, 30)).items()}

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
        print(f"heat: {lut_name}; pec ends at +{pec_T.max():.2f} C (a model)", flush=True)
    plate = None; plate_a = None
    if bg_path:
        pl = cv2.imread(bg_path, cv2.IMREAD_UNCHANGED)
        pl = cv2.resize(pl, (W, H), interpolation=cv2.INTER_AREA)
        plate = pl[:, :, :3].astype(np.float32); plate_a = (pl[:, :, 3].astype(np.float32) / 255)[:, :, None] if pl.shape[2] == 4 else np.ones((H, W, 1), np.float32)
        print(f"backdrop: {bg_path} (its own alpha covers {plate_a.mean()*100:.0f} % of the frame)", flush=True)

    # ---- the floor grid from the camera model: every 20 cm, drawn in image space ----
    grid_lines = []
    if grid_on:
        for X in np.arange(-0.8, 0.81, 0.2):
            pts = np.array([[X, Y, z_floor] for Y in np.arange(0.35, 3.01, 0.05)])
            uv = PR.project(pts, K, R); uv = uv[(uv[:, 1] > 0) & (uv[:, 1] < H) & (uv[:, 0] > -50) & (uv[:, 0] < W + 50)]
            if len(uv) > 1: grid_lines.append((None, uv))
        for Y in np.arange(0.4, 3.01, 0.2):
            pts = np.array([[X, Y, z_floor] for X in np.linspace(-1.0, 1.0, 11)])
            uv = PR.project(pts, K, R)
            if 0 < uv[:, 1].mean() < H: grid_lines.append((round(float(Y), 1), uv))

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

    # ---- the body layer: plate + paint + look (baked once per source frame with cache=) ----
    def body_layer(f, fi, P_use, zprog, gi):
        lab_full = None
        comp_now = np.asarray(masks[fi]) if masks is not None else None
        if plate is not None and comp_now is not None:
            alpha_full = cv2.resize(comp_now[..., 0], (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255
            z = 1.0 + 0.05 * zprog
            cw, ch = int(W / z), int(H / z); px0 = (W - cw) // 2; py0 = (H - ch) // 2
            pl = cv2.resize(plate[py0:py0 + ch, px0:px0 + cw], (W, H), interpolation=cv2.INTER_LINEAR)
            pa = cv2.resize(plate_a[py0:py0 + ch, px0:px0 + cw, 0], (W, H), interpolation=cv2.INTER_LINEAR)[:, :, None]
            keep = np.clip(alpha_full[:, :, None] + (1 - pa), 0, 1)
            f = np.clip(pl * (1 - keep) + f.astype(np.float32) * keep, 0, 255).astype(np.uint8)
        if masks is not None and P_use is not None and phase[fi] != "SETUP":
            reg_E = AT.region_values(Em, masses, fi); reg_A = AT.region_values(Am, masses, fi)
            f, mf, lab_full = AT.paint(f, comp_now, with_legs(P_use, fi), reg_E, reg_A, 1.0, None)
            if look is not None:
                f = look.apply(f, mf, (0, 0, 0), 0.8, gi, keep_colour=plate is not None, rim=0.0)
        return f, lab_full

    # ---- after the set: one uniform field (Dennis, 2026-09-10: keep the map on while he stands up, "even if
    # artificially"). MediaPipe's landmarks jump on the close-up body and the polygons jumped with them (the
    # flicker gate caught it at 110-112 s), so every region gets the same value, the mass-weighted mean effort,
    # and the mask is the matte alone. Computed live for the ~190 frames after set1; the baked frames stay valid. ----
    mtot = sum(masses[m] for m in TH.PAINTED)
    E_mean = np.array([sum(Em[m][i_] * masses[m] for m in TH.PAINTED) / mtot for i_ in range(N)])
    A_mean = np.array([sum(Am[m][i_] * masses[m] for m in TH.PAINTED) / mtot for i_ in range(N)])

    def body_layer_done(f, fi, P_use, zprog, gi):
        comp_now = np.asarray(masks[fi]) if masks is not None else None
        if plate is not None and comp_now is not None:
            alpha_full = cv2.resize(comp_now[..., 0], (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255
            z = 1.0 + 0.05 * zprog
            cw, ch = int(W / z), int(H / z); px0 = (W - cw) // 2; py0 = (H - ch) // 2
            pl = cv2.resize(plate[py0:py0 + ch, px0:px0 + cw], (W, H), interpolation=cv2.INTER_LINEAR)
            pa = cv2.resize(plate_a[py0:py0 + ch, px0:px0 + cw, 0], (W, H), interpolation=cv2.INTER_LINEAR)[:, :, None]
            keep = np.clip(alpha_full[:, :, None] + (1 - pa), 0, 1)
            f = np.clip(pl * (1 - keep) + f.astype(np.float32) * keep, 0, 255).astype(np.uint8)
        if masks is not None and P_use is not None:
            reg_E = {r: float(E_mean[fi]) for r in AT.REGIONS}; reg_A = {r: float(A_mean[fi]) for r in AT.REGIONS}
            f, mf, _ = AT.paint(f, comp_now, P_use, reg_E, reg_A, 1.0, None)
            if look is not None:
                f = look.apply(f, mf, (0, 0, 0), 0.8, gi, keep_colour=plate is not None, rim=0.0)
        return f, None

    def _fstat(p):
        st = os.stat(p); return [os.path.basename(p), st.st_size, st.st_mtime_ns]

    def cache_key(f0, f1):
        h = hashlib.sha1()
        for m in (AT, TH, PL):
            h.update(open(m.__file__, "rb").read())
        return {"files": [_fstat(p) for p in (video, npz, ajson, heat_path, bg_path) if p],
                "modules": h.hexdigest()[:12],
                "body_layer": hashlib.sha1(inspect.getsource(body_layer).encode("utf-8")).hexdigest()[:12],
                "lut": hashlib.sha1(LUT.tobytes()).hexdigest()[:12],
                "params": {"look": bool(look_on), "t_scale": t_scale, "W": W, "H": H, "fps": fps},
                "range": [int(f0), int(f1)]}

    cache_cap = None; cache_f0 = 0; cache_cents = {}
    if cache_path:
        need = sorted({fi_ for fi_, _, _ in plan})
        meta_path = cache_path + ".json"
        meta = json.load(open(meta_path, encoding="utf-8")) if os.path.exists(meta_path) and os.path.exists(cache_path) else None
        stale = None
        if meta is None:
            stale = "no cache yet"
        else:
            ck = cache_key(*meta["range"])
            diff = [k for k in ck if ck[k] != meta["key"].get(k)]
            if diff:
                stale = "changed: " + ", ".join(diff)
            elif need[0] < meta["range"][0] or need[-1] >= meta["range"][1]:
                stale = f"baked range {meta['range']} does not cover {need[0]}..{need[-1]}"
        if stale or bake_mode in ("1", "only"):
            f0b, f1b = (trim if trim else (need[0], need[-1] + 1)); f1b = min(f1b, N)
            print(f"baking the body layer for source frames {f0b}..{f1b - 1} -> {cache_path} ({stale or 'bake forced'})", flush=True)
            AT._HEAD_PREV = None
            bcmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", f"{fps}",
                    "-i", "pipe:0", "-c:v", "ffv1", "-level", "3", "-g", "1", "-threads", "8", "-pix_fmt", "bgr0", cache_path]
            bproc = subprocess.Popen(bcmd, stdin=subprocess.PIPE)
            bcap = cv2.VideoCapture(video); bcap.set(cv2.CAP_PROP_POS_FRAMES, f0b)
            cents_all = {}; b_last = None; t0b = time.time(); nb = 0
            for fi_ in range(f0b, f1b):
                got, fr = bcap.read()
                if not got:
                    break
                if ok[fi_]:
                    b_last = P[fi_]
                fb, lab_b = body_layer(fr, fi_, b_last, (fi_ - f0b) / max(1, f1b - 1 - f0b), fi_)
                cents_all[str(fi_)] = ({str(k): [float(v[0]), float(v[1])] for k, v in AT.label_centroids(lab_b, W, H).items()}
                                       if lab_b is not None else {})
                bproc.stdin.write(np.ascontiguousarray(fb).tobytes()); nb += 1
                if (fi_ - f0b) % 150 == 0:
                    print(f"  bake {fi_ - f0b}/{f1b - f0b}  {time.time() - t0b:.0f} s", flush=True)
            bcap.release(); bproc.stdin.close(); bproc.wait()
            meta = {"key": cache_key(f0b, f0b + nb), "range": [f0b, f0b + nb], "centroids": cents_all}
            json.dump(meta, open(meta_path, "w", encoding="utf-8"))
            print(f"baked {nb} frames in {time.time() - t0b:.0f} s -> {cache_path} (ffmpeg rc {bproc.returncode})", flush=True)
            if bake_mode == "only" or nb == 0:
                return
        cache_f0 = int(meta["range"][0])
        rk = {str(r_): r_ for r_ in AT.REGIONS}
        cache_cents = {int(k): {rk.get(r_, r_): tuple(v) for r_, v in d.items()} for k, d in meta["centroids"].items()}
        cache_cap = cv2.VideoCapture(cache_path)
        print(f"body layer from the cache {cache_path} (source frames {meta['range'][0]}..{meta['range'][1] - 1})", flush=True)

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
    cur_src = -1; frame = None; last_ok = None; cur_cache = -1; cframe = None
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
        f = frame.copy()
        if ok[fi]:
            P_use, V_use = P[fi], V[fi]; last_ok = (P[fi], V[fi])
        else:
            P_use, V_use = last_ok if last_ok is not None else (P[fi], V[fi])
        ph = phase[fi] if kind != "summary" else "DONE"
        pc = PHASE_COL.get(ph, MUTED)
        fast = int(seg.get("step", 1)) if kind == "play" else 1
        title_on = (kind == "play" and count[fi] == 0 and fi < first_rep) or (kind == "freeze" and seg.get("title") is None and seg.get("hook") is None)

        if fi > set1:
            f, lab_full = body_layer_done(f, fi, P_use if last_ok is not None else None, i / max(1, total - 1), i)
            cents_now = {}
        elif cache_cap is not None:
            if fi != cur_cache:
                if cur_cache >= 0 and 0 < fi - cur_cache <= 12:
                    for _ in range(fi - cur_cache):
                        gotc, cf = cache_cap.read()
                        if not gotc: break
                else:
                    cache_cap.set(cv2.CAP_PROP_POS_FRAMES, fi - cache_f0); gotc, cf = cache_cap.read()
                if gotc:
                    cframe = cf; cur_cache = fi
            f = cframe.copy(); lab_full = None; cents_now = cache_cents.get(fi, {})
        else:
            f, lab_full = body_layer(f, fi, P_use if last_ok is not None else None, i / max(1, total - 1), i)
            cents_now = None

        # ---- the floor grid ----
        if grid_on and ph not in ("SETUP", "DONE"):
            gl = f.copy()
            for lab_, uv in grid_lines:
                pts = np.round(uv).astype(np.int32).reshape(-1, 1, 2)
                cv2.polylines(gl, [pts], False, (215, 215, 210), 1, cv2.LINE_AA)
                if lab_ is not None and uv[-1, 0] < W and uv[-1, 1] < GRID_BOTTOM:
                    cv2.putText(gl, f"{lab_:.1f} m", (int(min(uv[-1, 0], W - 90)), int(uv[-1, 1]) - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (215, 215, 210), 1, cv2.LINE_AA)
            f = cv2.addWeighted(f, 0.72, gl, 0.28, 0)

        # ---- a light skeleton ----
        if last_ok is not None and ph not in ("SETUP", "DONE"):
            Pf, Vf = P_use, V_use
            for a1, b1, col in EDGES:
                if Vf[a1] > 0.5 and Vf[b1] > 0.5:
                    pa, pb = tuple(Pf[a1].astype(int)), tuple(Pf[b1].astype(int))
                    cv2.line(f, pa, pb, INK, 6, cv2.LINE_AA); cv2.line(f, pa, pb, col[::-1], 2, cv2.LINE_AA)
            for j in JOINTS:
                if Vf[j] > 0.5:
                    p = tuple(Pf[j].astype(int))
                    if 0 <= p[0] < W and 0 <= p[1] < H:
                        cv2.circle(f, p, 9, INK, -1, cv2.LINE_AA); cv2.circle(f, p, 5, WHITE[::-1], -1, cv2.LINE_AA)

        im = Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)).convert("RGBA")
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(ov)

        # ---- muscle names, once each ----
        if (lab_full is not None or cents_now is not None) and kind == "play":
            cents = cents_now if cents_now is not None else AT.label_centroids(lab_full, W, H)
            slot = 0
            for r_ in order:
                f_at = label_at[r_]; age = (fi - f_at) / fps
                if 0 <= age < LABEL_S and r_ in cents:
                    a_ = int(255 * min(1.0, age / 0.2, (LABEL_S - age) / 0.3))
                    cx, cy = cents[r_][0], cents[r_][1]
                    txt = f"{AT.LABELS[r_]}  {reg_E_series[r_][fi] * 100:.0f} %"
                    fnt = fit(dr, txt, FONT_B, 30, 380); tw = dr.textlength(txt, font=fnt) + 28
                    lx, ly = 60, LABEL_Y0 + slot * 56
                    dr.line((cx, cy, lx + tw / 2, ly + 46), fill=(*WHITE, a_), width=2)
                    dr.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=(*WHITE, a_))
                    rounded(dr, (lx, ly, lx + tw, ly + 46), 10, (*INK, int(225 * a_ / 255)))
                    dr.text((lx + 14, ly + 6), txt, font=fnt, fill=(*WHITE, a_))
                    slot += 1

        if kind == "freeze" and (seg.get("title") or seg.get("hook")):
            # the hook: a big line and a sub-line over a frozen frame
            ttl = seg.get("hook") or seg.get("title"); sub = seg.get("sub"); sub2 = seg.get("sub2", "")
            rounded(dr, (60, 250, 936, 470 if not sub else 540), 24, (*INK, 215))
            dr.text((84, 272), ttl, font=fit(dr, ttl, FONT_B, 72, 828), fill=(*ORANGE, 255))
            if sub:
                dr.text((84, 372), sub, font=fit(dr, sub, FONT_S, 40, 828), fill=WHITE)
                dr.text((84, 440), sub2, font=fit(dr, sub2, FONT_R, 30, 828), fill=MUTED)
        elif title_on:
            rounded(dr, (60, 240, 936, 520), 24, (*INK, 205))
            dr.text((84, 262), "PUSH UP ANALYSIS", font=fit(dr, "PUSH UP ANALYSIS", FONT_B, 76, 828), fill=WHITE)
            dr.text((84, 352), "by Fable", font=fit(dr, "by Fable", FONT_S, 46, 828), fill=WHITE)
            sub = f"{len(reps)} reps · 22 muscles · judged to the {STD}"
            dr.text((84, 430), sub, font=fit(dr, sub, FONT_S, 34, 828), fill=MUTED)
        elif kind != "summary":
            rounded(dr, (60, 240, 252, 428), 22, (*INK, 205))
            dr.text((156, 226), str(count[fi]), font=F["counter"], fill=WHITE, anchor="ma")
            dr.text((156, 386), "REPS", font=F["counter_lbl"], fill=MUTED, anchor="ma")
            pw = dr.textlength(ph, font=F["phase"]) + 52
            rounded(dr, (60, 446, 60 + pw, 516), 18, (*pc, 235))
            dr.text((86, 452), ph, font=F["phase"], fill=WHITE if ph in ("PUSH", "LOWER") else INK)
            if fast > 1:
                fw = dr.textlength(f"×{fast}", font=F["phase"]) + 44
                rounded(dr, (60 + pw + 12, 446, 60 + pw + 12 + fw, 516), 18, (*WHITE, 230))
                dr.text((60 + pw + 12 + 22, 452), f"×{fast}", font=F["phase"], fill=INK)
            # ---- the left stack: the numbers that compound ----
            if count[fi] > 0:
                vcol = WHITE if vloss[fi] < 25 else YELLOW if vloss[fi] < 50 else ORANGE
                rows_ = [(f"{passed[fi]}/{judged[fi]}", "USMC · ALL THREE LINES", AQUA if passed[fi] == judged[fi] else YELLOW),
                         (f"−{vloss[fi]:.0f} %" if vloss[fi] >= 1 else "0 %", "SPEED VS THE FASTEST", vcol),
                         (f"{peak_w[fi]:.0f} W", "PEAK POWER", WHITE),
                         (f"+{pec_T[fi]:.2f} °C", "PEC · MODELLED", ORANGE),
                         (f"{fat_pec[fi]*100:.0f} % · {fat_tri[fi]*100:.0f} %", "PEC · TRICEPS FATIGUED, MODEL", WHITE),
                         (f"≈ {kcal[fi]:.1f} kcal", f"{heat_kj[fi]:.0f} kJ OF HEAT", MUTED)]
                y_ = STACK_Y0
                bw = max(max(dr.textlength(b_, font=F["pill"]), dr.textlength(s_, font=F["pill_l"])) for b_, s_, _ in rows_) + 28
                for big, small, col in rows_:
                    rounded(dr, (60, y_, 60 + bw, y_ + 70), 14, (*INK, 200))
                    dr.text((74, y_ + 0), big, font=F["pill"], fill=col)
                    dr.text((74, y_ + 44), small, font=F["pill_l"], fill=MUTED)
                    y_ += 76
            # diegetic pills at real speed: the elbow angle at the elbow, the speed beside the shoulders
            if last_ok is not None and fast == 1 and ph not in ("SETUP", "DONE") and fi <= set1:   # no readouts once the hands leave the floor: the speed and the elbow mean nothing while he stands up
                def pill(x, y, big, small, anchor_right=False):
                    bw = max(dr.textlength(big, font=F["pill"]), dr.textlength(small, font=F["pill_l"])) + 28
                    x0p = x - bw if anchor_right else x
                    x0p = float(np.clip(x0p, 60, W - 60 - bw)); y = float(np.clip(y, 240, CARD_BOX[1] - 8 - 84))
                    rounded(dr, (x0p, y, x0p + bw, y + 84), 14, (*INK, 205))
                    dr.text((x0p + 14, y + 4), big, font=F["pill"], fill=WHITE)
                    dr.text((x0p + 14, y + 52), small, font=F["pill_l"], fill=MUTED)
                ex, ey = P_use[13]
                pill(min(ex, W - 40) - 150, ey - 42, f"{(el_l[fi] + el_r[fi]) / 2:.0f}°", "ELBOW", anchor_right=True)
                sx, sy = P_use[12]
                pill(W - 60, max(sy - 42, 560), f"{abs(vy[fi]):.2f} m/s", "SPEED " + ("UP" if vy[fi] > 0.05 else "DOWN" if vy[fi] < -0.05 else ""), anchor_right=True)

        r = card[fi]
        a = 0
        if r is not None and kind == "play" and fast == 1:
            age = (fi - r["f_end"]) / fps
            a = int(255 * min(1.0, max(age, 0) / 0.15))
            x0, y0, x1, y1 = CARD_BOX
            rounded(dr, (x0, y0, x1, y1), 24, (*INK, int(215 * a / 255)))
            good = r["depth_pass"] and r["parallel_pass"] and r["lockout"] and r["straight"]
            if r.get("failed"):
                vtxt, vsym, gc = "FAILED", "\u2717", ORANGE
            elif good:
                vtxt, vsym, gc = "USMC · PASS", "\u2713", AQUA
            elif not (r["depth_pass"] and r["parallel_pass"]):
                vtxt, vsym, gc = "SHORT", "\u2717", ORANGE
            elif not r["lockout"]:
                vtxt, vsym, gc = "NO LOCK-OUT", "\u2717", ORANGE
            else:
                vtxt, vsym, gc = "HIPS SAG", "~", YELLOW
            bx0 = x1 - 330
            rounded(dr, (bx0, y0 + 18, x1 - 24, y1 - 18), 20, (*gc, a))
            bcx = (bx0 + x1 - 24) // 2
            dr.text((bcx, y0 + 34), vsym, font=fit(dr, vsym, FONT_SYM, 96, 200), fill=(*INK, a), anchor="ma")
            dr.text((bcx, y0 + 150), vtxt, font=fit(dr, vtxt, FONT_B, 34, x1 - 24 - bx0 - 24), fill=(*INK, a), anchor="ma")
            note = f"elbow {r['elbow_bottom']:.0f}° at the bottom · shoulder {r['sh_h_bottom_cm']:.0f} cm up"
            dr.text((bcx, y1 - 30), note, font=fit(dr, note, FONT_R, 26, x1 - 24 - bx0 - 24), fill=(*INK, a), anchor="ms")
            head = f"REP {r['rep']}" if r.get("rep") else f"ATTEMPT {r['n']}"
            dr.text((x0 + 24, y0 + 18), head, font=F["card_t"], fill=(*WHITE, a))
            cx = x0 + 24
            for txt, okk in (("PAST PARALLEL" if r["parallel_pass"] else "SHORT", r["depth_pass"] and r["parallel_pass"]),
                             ("LOCKED" if r["lockout"] else "NO LOCK-OUT", r["lockout"]),
                             ("STRAIGHT" if r["straight"] else f"SAG {abs(r['hip_sag_cm'] or 0):.0f} CM", r["straight"])):
                col = AQUA if okk else ORANGE
                tw = dr.textlength(txt, font=F["small"]) + 28
                rounded(dr, (cx, y0 + 88, cx + tw, y0 + 132), 12, (*col, a))
                dr.text((cx + 14, y0 + 92), txt, font=F["small"], fill=(*INK, a))
                cx += tw + 12
            lines = [f"down {r['t_eccentric']:.1f} s   bottom {r['t_bottom_hold']:.1f} s   up {r['t_concentric']:.1f} s",
                     f"peak {r['peak_conc_v']:.2f} m/s   {r['peak_power_w']:.0f} W   ≈ {TH.KCAL_PER_REP_MEASURED:.1f} kcal",
                     f"speed vs the fastest −{max(0, r.get('velocity_loss_vs_fastest_pct', 0)):.0f} %   hips {r['hip_sag_cm'] or 0:+.0f} cm"]
            for k, ln in enumerate(lines):
                dr.text((x0 + 24, y0 + 146 + k * 44), ln, font=fit(dr, ln, FONT_S, 34, x1 - x0 - 380), fill=(*MUTED, a))
        # ---- the GitHub box in the card's slot whenever the card is not showing ----
        if kind == "play" and not title_on:
            gh_a = 1.0
            if r is not None and fast == 1:
                gh_a = 1.0 - a / 255
            elif fast == 1:
                prev_end = [rr["f_end"] for rr in atts if rr["f_end"] + int(2.0 * fps) <= fi]
                if prev_end:
                    gh_a = min(1.0, (fi - (max(prev_end) + int(2.0 * fps))) / (0.15 * fps))
            if gh_a > 0.01:
                ga = int(255 * gh_a)
                x0, y0, x1, y1 = CARD_BOX
                rounded(dr, (x0, y0, x1, y1), 24, (*INK, int(215 * gh_a)))
                dr.text((x0 + 24, y0 + 22), "PUSH UP ANALYSIS · BY FABLE", font=fit(dr, "PUSH UP ANALYSIS · BY FABLE", FONT_S, 30, 828), fill=(*MUTED, ga))
                dr.text((x0 + 24, y0 + 64), "dyeallpies-productions", font=fit(dr, "dyeallpies-productions", FONT_B, 82, 828), fill=(*WHITE, ga))
                gh_l1 = "github.com/DyeAllPies/dyeallpies-productions/"
                dr.text((x0 + 24, y0 + 170), gh_l1, font=fit(dr, gh_l1, FONT_S, 40, 828), fill=(*ORANGE, ga))
                gh_l2 = "the scripts, the muscle model and the papers, open"
                dr.text((x0 + 24, y0 + 226), gh_l2, font=fit(dr, gh_l2, FONT_R, 30, 828), fill=(*MUTED, ga))

        # ---- the chart: shoulder height above the floor ----
        rounded(dr, (PX0, PY0, PX1, PY1), 24, (*INK, 200))
        dr.text((PX0 + 24, PY0 + 14), "SHOULDER HEIGHT", font=F["small"], fill=MUTED)
        if masks is not None:
            grad = Image.fromarray(cv2.cvtColor(cv2.LUT(cv2.merge([np.tile(np.arange(256, dtype=np.uint8), (10, 1))] * 3), LUT), cv2.COLOR_BGR2RGB)).resize((150, 12))
            gx = PX1 - 24 - 150
            ov.paste(grad.convert("RGBA"), (gx, PY0 + 24)); dr = ImageDraw.Draw(ov)
            dr.text((gx - 12, PY0 + 16), "MUSCLE EFFORT  rest", font=F["tiny"], fill=MUTED, anchor="ra")
            dr.text((PX1 - 24, PY0 + 40), "max · a model, not a thermal camera", font=F["tiny"], fill=MUTED, anchor="ra")
        else:
            dr.text((PX0 + 24 + dr.textlength("SHOULDER HEIGHT", font=F["small"]) + 18, PY0 + 18), "0 = bottom · 100 = locked", font=F["tiny"], fill=MUTED)
        for pct, lab in ((0, "0"), (50, "50"), (100, "100")):
            yy = hy(pct); dr.line((CX0, yy, CX1, yy), fill=(70, 70, 68), width=1)
            dr.text((CX0 - 6, yy), lab, font=F["tiny"], fill=MUTED, anchor="rm")
        upto = fi + 1
        if upto > 1:
            pts = trace_pts[set0 if fi >= set0 else 0:upto]
            if len(pts) > 1:
                dr.line(pts, fill=WHITE, width=3, joint="curve")
        for r2 in atts:
            if r2["f_bottom"] <= fi:
                x, y = trace_pts[r2["f_bottom"]]
                good2 = r2["depth_pass"] and r2["parallel_pass"] and r2["lockout"] and r2["straight"]
                gc = ORANGE if r2.get("failed") else (AQUA if good2 else YELLOW)
                dr.ellipse((x - 7, y - 7, x + 7, y + 7), fill=gc, outline=INK, width=2)
        px = tx(t[fi]); dr.line((px, CY0, px, CY1), fill=(*pc, 220), width=2)
        for k, r2 in enumerate(atts):
            cx = CX0 + k * ((CX1 - CX0) / len(atts)); cw = (CX1 - CX0) / len(atts) - 4
            done = r2["f_end"] <= fi
            good2 = r2["depth_pass"] and r2["parallel_pass"] and r2["lockout"] and r2["straight"]
            col = (ORANGE if r2.get("failed") else (AQUA if good2 else YELLOW)) if done else (60, 60, 58)
            rounded(dr, (cx, PY1 - 56, cx + cw, PY1 - 16), 8, (*col, 255))
            if len(atts) <= 16 or (k + 1) % 5 == 0 or k == 0:
                dr.text((cx + cw / 2, PY1 - 36), "X" if r2.get("failed") else str(r2["rep"]), font=F["tiny"],
                        fill=INK if done else MUTED, anchor="mm")

        if kind == "summary":
            a = 255
            rounded(dr, (60, 200, 936, 1170), 28, (*INK, 236))
            dr.text((498, 224), "REFERENCES", font=F["sum_h"], fill=(*WHITE, a), anchor="ma")
            dr.text((498, 292), "the papers behind every number · full archive in the repository", font=F["tiny"], fill=(*MUTED, a), anchor="ma")
            refs = [("EMG", "Youdas et al. 2010 · J Strength Cond Res · push-up variants"),
                    ("", "Snarr & Esco 2013 · Calatayud et al. 2014 · Borreani et al. 2015"),
                    ("", "San Juan et al. 2015 · serratus · Tahani et al. 2026 · core"),
                    ("FORCE", "Eckel et al. 2017 · hands carry 72–77 % of body weight"),
                    ("", "Donkers, An, Chao & Morrey 1993 · elbow load in a push-up"),
                    ("MODEL", "Crowninshield & Brand 1981 · force sharing · Hill 1938"),
                    ("", "Thelen 2003 · Xia & Frey-Law 2008 · Frey-Law et al. 2012 · rates"),
                    ("", "Holzbaur et al. 2005 · upper-limb model · Murray et al. 2000 · arms"),
                    ("HEAT", "Nakagata et al. 2022 · 0.77 kcal a push-up · Umberger et al. 2003"),
                    ("", "González-Alonso et al. 2000 · J Physiol · muscle temperature"),
                    ("GEOMETRY", "de Leva 1996 · segments · two vanishing points · Hartley & Zisserman"),
                    ("VISION", "MediaPipe Pose · YOLOv8-pose · Lin et al. 2022 · Robust Video Matting"),
                    ("STANDARD", "USMC PFT push-up · upper arms parallel, arms locked, body straight")]
            for k, (tag, txt) in enumerate(refs):
                yy = 340 + k * 58
                if tag:
                    dr.text((96, yy + 6), tag, font=F["pill_l"], fill=(*ORANGE, a))
                dr.text((252, yy), txt, font=fit(dr, txt, FONT_S, 32, 896 - 252), fill=(*WHITE, a))
            foot = "github.com/DyeAllPies/dyeallpies-productions/ · references/pushup-science · 90 papers, tables and full texts"
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
