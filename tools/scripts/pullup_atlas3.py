"""
Anatomy atlas, version 3: muscles drawn as muscles, not as one flat colour.

What set #2 painted was a silhouette filled with one temperature colour per region. This
module keeps the landmark-warped polygon idea (regions drawn once in canonical body frames,
warped by the frame's landmarks, clipped by the RVM silhouette) and adds what an anatomy
chart has:

  * more regions, from references/pullup-science/01-emg-and-anatomy.md: upper trapezius,
    serratus anterior, middle deltoid, triceps, forearm extensors, on top of set #2's list;
  * a FIBRE DIRECTION FIELD per region: parallel muscles (biceps, forearm, rectus abdominis,
    quadriceps) run along their segment, fan-shaped muscles (pectoralis major, latissimus,
    deltoid, upper trapezius) converge on their tendon. Striations are drawn along the field;
  * BOUNDARIES between muscles and the tendinous intersections of the rectus abdominis;
  * a BELLY shade: the interior of each region is lifted toward its centre and darkened at
    its edges, so every muscle reads as a rounded body;
  * the frame's own luminance still modulates everything, so the real definition shows.

Colour = modelled temperature (pullup_thermal3.py) on a thermal scale; brightness pulses
with modelled activation. Head, hair, shorts: natural. Everything is clipped by the matte.

    python pullup_atlas3.py <video> <pose_mp.npz> <analysis.json> <matte.npy> <frame,frame,..> <out_prefix>
"""
import sys, json, os
import numpy as np
import cv2

L_SH, R_SH = 11, 12; L_EL, R_EL = 13, 14; L_WR, R_WR = 15, 16
L_HIP, R_HIP = 23, 24; L_KNEE, R_KNEE = 25, 26; L_ANK, R_ANK = 27, 28

# ---- canonical torso polygons (s down the trunk 0..1, d lateral in half shoulder widths,
# + d = the person's LEFT). fibre: ("par", angle_deg from the trunk axis, mirrored for the
# right side) or ("fan", (s, d) convergence point). --------------------------------------
TORSO = {
    "upper trapezius": dict(
        polys=[[(-0.16, 0.08), (-0.12, 0.98), (0.03, 1.02), (0.05, 0.10)]],
        fibre=("fan", (-0.02, 1.12))),
    "pectoralis major": dict(
        polys=[[(0.02, 0.05), (0.02, 0.86), (0.24, 0.84), (0.33, 0.08)]],
        fibre=("fan", (0.00, 1.20))),
    "serratus anterior": dict(
        polys=[[(0.30, 0.52), (0.28, 0.84), (0.58, 0.86), (0.60, 0.48)]],
        fibre=("par", 62.0)),
    "latissimus dorsi": dict(
        polys=[[(0.04, 0.80), (0.02, 1.30), (0.62, 1.18), (0.64, 0.84), (0.30, 0.86)]],
        fibre=("fan", (-0.04, 0.98))),
    "external oblique": dict(
        polys=[[(0.60, 0.36), (0.62, 1.16), (1.04, 1.00), (1.02, 0.26)]],
        fibre=("par", -34.0)),
    "rectus abdominis": dict(
        polys=[[(0.34, 0.00), (0.34, 0.30), (1.05, 0.24), (1.05, 0.00)]],
        fibre=("par", 0.0)),
}
MIRROR = True                                  # every torso entry is drawn for both sides
RECTUS_INTERSECTIONS = (0.47, 0.61, 0.77)      # tendinous intersections, s down the trunk

# ---- per-segment polygons (l along the segment 0..1, w across in units of the segment's
# half width; + w = MEDIAL (toward the body midline). fibre angle from the segment axis. ----
UPPER_ARM = {
    "deltoid":  dict(polys=[[(-0.08, -1.35), (-0.08, 1.35), (0.34, 1.05), (0.42, 0.0), (0.34, -1.05)]], fibre=("fan", (0.48, 0.0))),
    "biceps":   dict(polys=[[(0.30, 0.00), (0.30, 1.35), (1.00, 1.35), (1.00, 0.00)]], fibre=("par", 0.0)),
    "triceps":  dict(polys=[[(0.30, -1.35), (0.30, 0.00), (1.00, 0.00), (1.00, -1.35)]], fibre=("par", 0.0)),
}
FOREARM = {
    "forearm flexors":   dict(polys=[[(0.00, 0.00), (0.00, 1.35), (0.96, 1.35), (0.96, 0.00)]], fibre=("par", 8.0)),
    "forearm extensors": dict(polys=[[(0.00, -1.35), (0.00, 0.00), (0.96, 0.00), (0.96, -1.35)]], fibre=("par", -8.0)),
}
THIGH = {
    "hip flexors": dict(polys=[[(0.00, -1.35), (0.00, 1.35), (0.26, 1.35), (0.26, -1.35)]], fibre=("par", 0.0)),
    "quadriceps":  dict(polys=[[(0.22, -1.35), (0.22, 1.35), (1.02, 1.35), (1.02, -1.35)]], fibre=("fan", (1.10, 0.0))),
}
SHANK = {
    "calves": dict(polys=[[(0.00, -1.35), (0.00, 1.35), (1.02, 1.35), (1.02, -1.35)]], fibre=("par", 0.0)),
}
WIDTHS = dict(upper=0.30, fore=0.26, thigh=0.40, shank=0.32)   # segment half widths / half shoulder width

# region -> thermal-model muscles (pullup_thermal3.MUSCLES), mass-weighted when several
REGION_MUSCLES = {
    "upper trapezius": ["upper trapezius"],
    "pectoralis major": ["pectoralis major"],
    "serratus anterior": ["serratus anterior"],
    "latissimus dorsi": ["latissimus dorsi", "teres major"],
    "external oblique": ["external oblique"],
    "rectus abdominis": ["rectus abdominis"],
    "deltoid": ["middle deltoid", "posterior deltoid", "infraspinatus"],
    "biceps": ["biceps brachii", "brachialis"],
    "triceps": ["triceps"],
    "forearm flexors": ["forearm flexors"],
    "forearm extensors": ["brachioradialis", "forearm extensors"],
    "hip flexors": ["hip flexors"],
    "quadriceps": ["quadriceps", "hamstrings"],
    "calves": ["calves"],
}
LABELS = {
    "upper trapezius": "TRAPEZIUS", "pectoralis major": "PECTORALIS MAJOR", "serratus anterior": "SERRATUS ANTERIOR",
    "latissimus dorsi": "LATISSIMUS DORSI", "external oblique": "EXTERNAL OBLIQUE", "rectus abdominis": "RECTUS ABDOMINIS",
    "deltoid": "DELTOID", "biceps": "BICEPS BRACHII", "triceps": "TRICEPS", "forearm flexors": "FOREARM FLEXORS (GRIP)",
    "forearm extensors": "BRACHIORADIALIS", "hip flexors": "HIP FLEXORS", "quadriceps": "QUADRICEPS", "calves": "CALVES",
}
# draw order: later wins where polygons overlap
ORDER = ["quadriceps", "calves", "hip flexors", "rectus abdominis", "external oblique", "serratus anterior",
         "pectoralis major", "latissimus dorsi", "upper trapezius", "triceps", "biceps", "deltoid",
         "forearm extensors", "forearm flexors"]
IDX = {r: i + 1 for i, r in enumerate(ORDER)}
REGIONS = list(REGION_MUSCLES)


def region_values(series, masses, frame):
    out = {}
    for r, ms in REGION_MUSCLES.items():
        w = sum(masses[m] for m in ms)
        out[r] = sum(series[m][frame] * masses[m] for m in ms) / w
    return out


region_temperatures = region_values


def _poly(pts, origin, e1, e2, s1, s2):
    return np.round(np.array([origin + p[0] * s1 * e1 + p[1] * s2 * e2 for p in pts])).astype(np.int32)


def _frames(P):
    """Local frames from the landmarks: returns dict of (origin, e1, e2, s1, s2) per drawable."""
    sl, sr, hl, hr = P[L_SH], P[R_SH], P[L_HIP], P[R_HIP]
    sm = (sl + sr) / 2; hm = (hl + hr) / 2
    ax = hm - sm; trunk = float(np.linalg.norm(ax))
    r = sl - sr; sw = float(np.linalg.norm(r))
    if trunk < 6 or sw < 4:
        return None
    u = ax / trunk; rr = r / sw; half = sw / 2
    out = {"torso": (sm, u, rr, trunk, half)}
    mid = (sm + hm) / 2
    for name, (a, b, wk) in dict(
            arm_l=(P[L_SH], P[L_EL], "upper"), arm_r=(P[R_SH], P[R_EL], "upper"),
            fore_l=(P[L_EL], P[L_WR], "fore"), fore_r=(P[R_EL], P[R_WR], "fore"),
            thigh_l=(P[L_HIP], P[L_KNEE], "thigh"), thigh_r=(P[R_HIP], P[R_KNEE], "thigh"),
            shank_l=(P[L_KNEE], P[L_ANK], "shank"), shank_r=(P[R_KNEE], P[R_ANK], "shank")).items():
        seg = b - a; L = float(np.linalg.norm(seg))
        if L < 4:
            continue
        e1 = seg / L; e2 = np.array([-e1[1], e1[0]])
        # + w must point toward the body's midline (medial)
        if np.dot(e2, mid - a) < 0:
            e2 = -e2
        out[name] = (a, e1, e2, L, WIDTHS[wk] * half)
    return out


def label_and_fibre(P, shape, div=1.0):
    """Region index map (uint8) and fibre-direction field (angle in radians, image coords)."""
    h, w = shape
    lab = np.zeros((h, w), np.uint8)
    theta = np.zeros((h, w), np.float32)
    fr = _frames(P / div)
    if fr is None:
        return lab, theta
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)

    def paint(key, spec, origin, e1, e2, s1, s2, mirror_sign=1.0):
        idx = IDX[key]
        tmp = np.zeros((h, w), np.uint8)
        for poly in spec["polys"]:
            pts = [(p[0], p[1] * mirror_sign) for p in poly]
            cv2.fillPoly(tmp, [_poly(pts, origin, e1, e2, s1, s2)], 1)
        m = tmp > 0
        if not m.any():
            return
        lab[m] = idx
        kind, val = spec["fibre"]
        if kind == "par":
            ang = np.radians(val) * mirror_sign
            dirv = np.cos(ang) * e1 + np.sin(ang) * e2
            theta[m] = np.arctan2(dirv[1], dirv[0])
        else:
            cs, cd = val
            c = origin + cs * s1 * e1 + cd * mirror_sign * s2 * e2
            dx = c[0] - xx[m]; dy = c[1] - yy[m]
            theta[m] = np.arctan2(dy, dx)

    for key in ORDER:
        if key in TORSO:
            sm, u, rr, trunk, half = fr["torso"]
            for sgn in ((1.0, -1.0) if MIRROR else (1.0,)):
                paint(key, TORSO[key], sm, u, rr, trunk, half, sgn)
        elif key in UPPER_ARM:
            for nm in ("arm_l", "arm_r"):
                if nm in fr: paint(key, UPPER_ARM[key], *fr[nm])
        elif key in FOREARM:
            for nm in ("fore_l", "fore_r"):
                if nm in fr: paint(key, FOREARM[key], *fr[nm])
        elif key in THIGH:
            for nm in ("thigh_l", "thigh_r"):
                if nm in fr: paint(key, THIGH[key], *fr[nm])
        elif key in SHANK:
            for nm in ("shank_l", "shank_r"):
                if nm in fr: paint(key, SHANK[key], *fr[nm])
    return lab, theta


def rectus_lines(P, shape, div=1.0):
    """Tendinous intersections and the linea alba, as a line mask."""
    h, w = shape
    m = np.zeros((h, w), np.uint8)
    fr = _frames(P / div)
    if fr is None:
        return m
    sm, u, rr, trunk, half = fr["torso"]
    for s in RECTUS_INTERSECTIONS:
        a = sm + s * trunk * u - 0.30 * half * rr; b = sm + s * trunk * u + 0.30 * half * rr
        cv2.line(m, tuple(np.round(a).astype(int)), tuple(np.round(b).astype(int)), 1, 1, cv2.LINE_AA)
    a = sm + 0.34 * trunk * u; b = sm + 1.05 * trunk * u
    cv2.line(m, tuple(np.round(a).astype(int)), tuple(np.round(b).astype(int)), 1, 1, cv2.LINE_AA)
    return m


_STOPS = [(0.00, (110, 30, 15)), (0.18, (200, 70, 20)), (0.36, (220, 170, 0)), (0.52, (60, 210, 120)),
          (0.68, (0, 210, 240)), (0.82, (20, 90, 250)), (0.93, (60, 40, 235)), (1.00, (225, 235, 255))]   # BGR, cold -> hot


def make_lut():
    lut = np.zeros((256, 1, 3), np.uint8)
    xs = [s[0] for s in _STOPS]; cs = np.array([s[1] for s in _STOPS], float)
    for i in range(256):
        tt = i / 255
        k = min(max(j for j in range(len(xs)) if xs[j] <= tt), len(xs) - 2)
        u = (tt - xs[k]) / (xs[k + 1] - xs[k])
        lut[i, 0] = np.clip(cs[k] * (1 - u) + cs[k + 1] * u, 0, 255)
    return lut


LUT = make_lut()


def paint(frame_bgr, comp_small, P, reg_T, reg_A, t_scale, bar_line, alpha=0.93, head_gate=True, seed=0):
    """Paint the muscles on one frame. comp_small = matte components (h/2, w/2, 3) uint8.
    Returns (painted frame, person alpha full-res, label map full-res)."""
    H, W = frame_bgr.shape[:2]
    cs = comp_small.astype(np.float32) / 255
    a_s, clothes, head = cs[..., 0], cs[..., 1], cs[..., 2]
    hs, ws = a_s.shape; s = ws / W
    sh = (P[11] + P[12]) / 2 * s; hip = (P[23] + P[24]) / 2 * s
    trunk = float(np.linalg.norm(hip - sh)) + 1e-3
    yy = np.arange(hs, dtype=np.float32)[:, None]; xx = np.arange(ws, dtype=np.float32)[None, :]
    ear = (P[7] + P[8]) / 2 * s
    sw = max(float(np.linalg.norm(P[11] - P[12])) * s, 20.0)
    head_r = max(0.62 * sw, 1.9 * float(np.linalg.norm(P[7] - P[8])) * s)
    above = np.clip((sh[1] - 0.10 * trunk - yy) / (0.06 * trunk), 0, 1)
    near = np.clip((head_r - np.sqrt((xx - ear[0]) ** 2 + (yy - ear[1]) ** 2)) / (0.22 * head_r), 0, 1)
    head_g = np.clip(head * 1.6, 0, 1) * above * near if head_gate else 0.0
    below = np.clip((yy - (hip[1] - 0.30 * trunk)) / (0.06 * trunk), 0, 1)
    m = a_s * (1 - head_g) * (1 - clothes * below)
    bar_row = (bar_line[0] * xx / s + bar_line[1]) * s
    m = m * np.clip((yy - (bar_row + 6 * s)) / 3.0, 0, 1)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    mask = m > 0.4

    lab, theta = label_and_fibre(P, (hs, ws), div=1 / s)
    lab = np.where(mask, lab, 0).astype(np.uint8)
    # temperature and activation fields, region-wise, feathered inside the silhouette
    sig = max(1.2, 0.012 * ws)
    ms = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), sig)

    def field(vals, scale_by):
        f = np.zeros((hs, ws), np.float32)
        for key, idx in IDX.items():
            f[lab == idx] = float(np.clip(vals.get(key, 0.0) / scale_by, 0, 1))
        f = np.where(mask, f, 0).astype(np.float32)
        fs = cv2.GaussianBlur(f, (0, 0), sig)
        return np.clip(np.where(ms > 0.05, fs / np.maximum(ms, 1e-3), 0), 0, 1).astype(np.float32)

    temp = field(reg_T, t_scale)
    act = field(reg_A, 1.0)

    # ---- anatomy shading, at matte resolution ----
    # 1. boundaries between regions (and the silhouette edge is NOT a boundary: the matte handles it)
    lab_f = lab.astype(np.float32)
    gx = cv2.Sobel(lab_f, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(lab_f, cv2.CV_32F, 0, 1, ksize=3)
    edge = ((np.abs(gx) + np.abs(gy)) > 0) & mask & (lab > 0)
    edge = cv2.GaussianBlur(edge.astype(np.float32), (0, 0), 0.8)
    # 2. belly: distance to the region boundary, normalised per region
    belly = np.zeros((hs, ws), np.float32)
    for idx in np.unique(lab):
        if idx == 0:
            continue
        rm = (lab == idx).astype(np.uint8)
        dist = cv2.distanceTransform(rm, cv2.DIST_L2, 3)
        dmax = float(dist.max()) if dist.max() > 0 else 1.0
        belly[rm > 0] = np.clip(dist[rm > 0] / (0.55 * dmax), 0, 1)
    belly = cv2.GaussianBlur(belly, (0, 0), 1.0)
    # 3. striations along the fibre field: thin, irregular fibre bundles. The across-fibre
    #    coordinate is warped by low-frequency noise so bundles wander and break like real
    #    fascicles instead of a knitted stripe; the profile is sharpened so lines stay thin.
    rng = np.random.default_rng(seed)
    n1 = cv2.GaussianBlur(rng.normal(0, 1, (hs, ws)).astype(np.float32), (0, 0), 3.0)
    n2 = cv2.GaussianBlur(rng.normal(0, 1, (hs, ws)).astype(np.float32), (0, 0), 9.0)
    period = max(2.6, 0.030 * sw) * (1.0 + 0.25 * n2)
    across = -np.sin(theta) * xx + np.cos(theta) * yy + 1.6 * n1
    ph = 2 * np.pi * across / period
    prof = 0.5 + 0.5 * np.cos(ph)
    stria = prof ** 3.0                                     # thin bright ridges, wide dark valleys
    amp = 0.55 + 0.45 * np.clip(n2 * 0.8 + 0.5, 0, 1)      # bundles fade in and out
    stria = 0.5 + (stria - 0.35) * amp
    stria = np.where(lab > 0, stria, 0.5).astype(np.float32)
    # groove between muscles: a dark line with a faint highlight just inside each region
    inner = cv2.GaussianBlur(edge, (0, 0), 2.2) - edge
    inner = np.clip(inner, 0, 1)
    # 4. rectus lines
    rl = rectus_lines(P, (hs, ws), div=1 / s).astype(np.float32)
    rl = cv2.GaussianBlur(rl, (0, 0), 0.7)

    # ---- compose at full resolution ----
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    up = lambda a: cv2.resize(a.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    tempF, actF, bellyF, striaF, edgeF, rlF, innerF = map(up, (temp, act, belly, stria, edge, rl, inner))
    idx = (np.clip(0.04 + 0.92 * tempF, 0, 1) * 255).astype(np.uint8)
    col = cv2.LUT(cv2.merge([idx, idx, idx]), LUT).astype(np.float32)
    # shading: real luminance (definition), belly bulge, striations, activation pulse
    lum = 0.30 + 0.85 * gray                                    # the real definition, deeper shadows
    shade = lum * (0.62 + 0.50 * bellyF) * (0.82 + 0.36 * (striaF - 0.5)) * (0.78 + 0.44 * actF)
    shade = shade * (1 + 0.35 * innerF)                         # highlight inside the groove
    col = col * shade[:, :, None]
    col = col * (1 - 0.70 * edgeF)[:, :, None] * (1 - 0.50 * rlF)[:, :, None]
    col = np.clip(col, 0, 255)
    mf = np.clip(cv2.GaussianBlur(up(m), (0, 0), 1.0), 0, 1)
    aa = mf[:, :, None] * alpha
    outf = np.clip(frame_bgr.astype(np.float32) * (1 - aa) + col * aa, 0, 255).astype(np.uint8)
    person = np.clip(up(a_s), 0, 1)
    return outf, person, cv2.resize(lab, (W, H), interpolation=cv2.INTER_NEAREST)


def label_centroids(lab_full, W, H):
    """Image-space centroid of every region present, for the first-appearance labels."""
    out = {}
    for key, idx in IDX.items():
        ys, xs = np.where(lab_full == idx)
        if len(xs) > 400:
            out[key] = (float(np.median(xs)), float(np.median(ys)), int(len(xs)))
    return out


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import pullup_thermal3 as TH
    video, npz, ajson, mpath, frames, prefix = sys.argv[1:7]
    frames = [int(x) for x in frames.split(",")]
    d = np.load(npz); img = d["img"]; W, H = int(d["width"]), int(d["height"])
    P = img[:, :, :2] * np.array([W, H])
    A = json.load(open(ajson)); S = A["summary"]
    M = np.load(mpath, mmap_mode="r")
    Tm = TH.integrate(A); Am = TH.activation(A); masses = TH.muscle_masses()
    cap = cv2.VideoCapture(video)
    for f in frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, f); ok, fr = cap.read()
        comp = np.asarray(M[f])
        reg_T = region_values(Tm, masses, f); reg_A = region_values(Am, masses, f)
        out, person, lab = paint(fr, comp, P[f], reg_T, reg_A, 2.0, (S["bar_slope"], S["bar_intercept"]))
        # debug: label outlines and fibre quivers over the frame
        dbg = fr.copy()
        labs, theta = label_and_fibre(P[f], (H // 2, W // 2), div=2.0)
        labs = cv2.resize(labs, (W, H), interpolation=cv2.INTER_NEAREST)
        mask = cv2.resize(comp[..., 0], (W, H)) > 128
        labs = np.where(mask, labs, 0)
        for key, idx in IDX.items():
            cnts, _ = cv2.findContours((labs == idx).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(dbg, cnts, -1, (0, 255, 255), 2)
        th = cv2.resize(theta, (W, H), interpolation=cv2.INTER_NEAREST)
        for y in range(0, H, 22):
            for x in range(0, W, 22):
                if labs[y, x] > 0:
                    a = th[y, x]; dx, dy = 9 * np.cos(a), 9 * np.sin(a)
                    cv2.line(dbg, (int(x - dx), int(y - dy)), (int(x + dx), int(y + dy)), (255, 80, 0), 1, cv2.LINE_AA)
        for key, (cx, cy, n) in label_centroids(labs, W, H).items():
            cv2.putText(dbg, LABELS[key], (int(cx) - 60, int(cy)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imwrite(f"{prefix}_paint_{f}.png", out); cv2.imwrite(f"{prefix}_atlas_{f}.png", dbg)
        print("wrote", f, {k: round(v, 2) for k, v in reg_T.items()})
    cap.release()
