"""
Anatomy atlas for the push-up (2026-09-10): pullup_atlas3's landmark-warped polygons and one
continuous feathered field, seen from the head end. The trunk frame (shoulder-mid -> hip-mid axis,
lateral in half shoulder widths) is the same; the body is foreshortened along the axis and the
silhouette clips every polygon, so the torso regions carry over unchanged. What differs:

  * the regions are mapped to the push-up model's muscles (pushup_thermal.MUSCLES): the deltoid
    cap is the ANTERIOR deltoid (the front of the shoulder faces this camera), the forearm's
    outer half is the wrist EXTENSORS (they hold the wrist under the hand force), the upper arm's
    roll puts the triceps' lateral head on the outside as the elbows flare;
  * no bar line: nothing above the body is clipped;
  * the default LUT is set #1's pure blue -> violet -> red -> hot (pullup_heat._STOPS), the look
    Dennis asked for; the renderer can swap the v4 scale back with lut=bluered.
  * the head gate matters more: at the bottom of every rep the head fills the frame; the geometric
    ellipse scales with the ear separation and the segmenter's head class widens it.

    python pushup_atlas.py <video> <pose_mp.npz> <analysis.json> <matte.npy> <frame,frame,..> <out_prefix>
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
    "upper trapezius": ["upper trapezius", "trapezius"],
    "pectoralis major": ["pectoralis major"],
    "serratus anterior": ["serratus anterior"],
    "latissimus dorsi": ["latissimus dorsi"],
    "external oblique": ["external oblique"],
    "rectus abdominis": ["rectus abdominis"],
    "deltoid": ["anterior deltoid", "middle deltoid"],
    "biceps": ["biceps brachii", "brachialis"],
    "triceps": ["triceps"],
    "forearm flexors": ["forearm flexors", "brachioradialis"],
    "forearm extensors": ["forearm extensors"],
    "hip flexors": ["hip flexors"],
    "quadriceps": ["quadriceps", "hamstrings"],
    "calves": ["calves"],
}
LABELS = {
    "upper trapezius": "TRAPEZIUS", "pectoralis major": "PECTORALIS MAJOR", "serratus anterior": "SERRATUS ANTERIOR",
    "latissimus dorsi": "LATISSIMUS DORSI", "external oblique": "EXTERNAL OBLIQUE", "rectus abdominis": "RECTUS ABDOMINIS",
    "deltoid": "ANTERIOR DELTOID", "biceps": "BICEPS BRACHII", "triceps": "TRICEPS", "forearm flexors": "FOREARM FLEXORS",
    "forearm extensors": "WRIST EXTENSORS", "hip flexors": "HIP FLEXORS", "quadriceps": "QUADRICEPS", "calves": "CALVES",
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
        if name.startswith("arm_"):
            # Upper arm: do NOT flip e2. The medial side of the humerus genuinely swaps sides in
            # the picture between the hang (arm overhead, medial = toward the head) and the top
            # (arm abducted, medial = the lower edge); a hard sign flip half-way put the biceps
            # on the wrong side for a frame (Dennis, 2026-09-08). Instead the roll rho in
            # [-1, 1] says how far the trunk centre sits on the +e2 side of the segment, and
            # upper_arm_specs() slides the biceps band across the visible face continuously.
            ref = mid - (a + b) / 2; ref = ref / (np.linalg.norm(ref) + 1e-6)
            out["rho_" + name] = float(np.clip(np.dot(e2, ref) / 0.5, -1, 1))
        elif np.dot(e2, mid - a) < 0:
            # + w must point toward the body's midline (medial); forearms and legs never
            # cross the ambiguous geometry, so the flip is stable there
            e2 = -e2
        out[name] = (a, e1, e2, L, WIDTHS[wk] * half)
    return out


def upper_arm_specs(rho):
    """Biceps / triceps polygons for one upper arm, as a function of the roll rho.

    The biceps is the anterior belly, so it stays in the middle of the visible face; the
    triceps shows only as a rim - the lateral head on the lateral edge, the long head at the
    axilla - and the rim on the side away from the trunk grows as the arm rolls. Continuous
    in rho, so no frame can jump."""
    w_minus = 0.25 + 0.55 * max(rho, 0.0)      # -e2 side is lateral when the trunk is on +e2
    w_plus = 0.25 + 0.55 * max(-rho, 0.0)
    lo, hi = -1.35 + w_minus, 1.35 - w_plus
    return {
        "deltoid": UPPER_ARM["deltoid"],
        "biceps": dict(polys=[[(0.30, lo), (0.30, hi), (1.00, hi), (1.00, lo)]], fibre=("par", 0.0)),
        "triceps": dict(polys=[[(0.30, -1.35), (0.30, lo), (1.00, lo), (1.00, -1.35)],
                               [(0.30, hi), (0.30, 1.35), (1.00, 1.35), (1.00, hi)]], fibre=("par", 0.0)),
    }


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
                if nm in fr: paint(key, upper_arm_specs(fr["rho_" + nm])[key], *fr[nm])
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
    """Tendinous intersections and the linea alba, as a line mask. Not drawn since 2026-09-09
    (no delimitations on the body); kept for the debug atlas and set #2's renderer."""
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


# BGR, rest -> max effort. Blue -> cyan -> green -> yellow -> orange -> red (Dennis, 2026-09-09: the
# ironbow's purple was too dark; the renderer can still swap the ironbow in with lut=iron).
# set #1's scale (pullup_heat._STOPS, the 140k reel): blue -> violet -> red -> hot, BGR. Dennis (2026-09-09): the pure
# blue-red effect was one reason the first reel went viral. The v4 six-hue scale stays available as BLUERED4.
_STOPS = [(0.00, (200, 90, 30)), (0.35, (190, 60, 140)), (0.65, (60, 50, 230)), (0.85, (40, 120, 255)), (1.00, (120, 230, 255))]
BLUERED4 = [(0.00, (130, 25, 15)), (0.12, (225, 70, 25)), (0.26, (250, 185, 0)), (0.40, (120, 220, 40)),
            (0.54, (40, 235, 235)), (0.68, (0, 150, 255)), (0.82, (20, 40, 235)), (1.00, (90, 90, 255))]


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
_HEAD_PREV = None       # temporal state of the class-based part of the head gate (see paint)
STRIATION = 0.0         # amplitude of the fibre striations in the shading (set #3 used 0.36). Dennis (2026-09-09, and again on
                        # 2026-09-10 with a screen recording of set #1): the PURE blue-red look of set #1, a solid fill at 0.96
                        # opacity with only the frame's own shading under it, is the look. No fibres.
ALPHA = 0.96            # paint opacity (set #1's value)
DEFINITION = 0.25       # weight of the frame's local contrast in the colour index (set #1: 0.25)
DEF_REF = 13.5          # the definition map's reference: the 90th percentile over the person, median over the set's frames (measured 2026-09-10; set #1 took a median the same way)
LEG_CAPSULE = 0.11      # radius of the synthetic shank + foot capsule, in shoulder widths (the far legs are ~60 px wide on a 600 px shoulder line)


def paint(frame_bgr, comp_small, P, reg_T, reg_A, t_scale, bar_line, alpha=None, head_gate=True, seed=0):
    alpha = ALPHA if alpha is None else alpha
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
    # The head gate is GEOMETRIC: an ellipse on the face landmarks, scaled on the shoulder
    # width. The segmenter's head class was the gate before, and it wanders between 6 % and
    # 56 % of the face from one frame to the next when the head is near the bar, so the paint
    # flashed over the face (Dennis, 2026-09-08). The class now only widens the ellipse, and
    # is smoothed over time so it cannot flash either.
    global _HEAD_PREV
    nose = P[0] * s; eye = (P[2] + P[5]) / 2 * s
    fc = 0.5 * (ear + nose)                                   # face centre, between ears and nose
    ax_ = max(0.40 * sw, 0.5 * float(np.linalg.norm(P[7] - P[8])) * s + 6)
    ay_ = max(0.52 * sw, 1.6 * float(np.linalg.norm(eye - nose)) + 8)
    ell = np.sqrt(((xx - fc[0]) / ax_) ** 2 + ((yy - fc[1]) / ay_) ** 2)
    geo = np.clip((1.18 - ell) / 0.25, 0, 1)
    # The push-up's head gate (2026-09-10): from the head end the skull is a ball around the ear line,
    # and at the bottom of every rep it hangs BELOW the shoulder row in the picture and fills the frame,
    # so the pull-up's "only above the shoulders" limit and its ear-neighbourhood limit are dropped. The
    # gate is the face ellipse, a circle on the ear midpoint of radius 0.75 x the ear separation (the
    # crown sits ~10 cm above the ear canals on a 15 cm wide head), and the segmenter's head class,
    # smoothed over time; the class only widens the gate.
    ear_sep = max(float(np.linalg.norm(P[7] - P[8])) * s, 8.0)
    # The skull, geometrically: from this camera the crown can sit 2 ear-widths from the ear line (at the
    # bottom of the rep the head hangs toward the lens and is seen from above), so the gate is an ellipse
    # along the head's own axis (nose -> ear midpoint, continued toward the crown): 0.62 ear widths across,
    # 1.3 along, centred 0.7 ear widths past the ears. Checked 2026-09-10 on frame 594 (ears 375 px apart,
    # the crown 700 px above them) and on the tops (ears 283 px apart, the crown 190 px above).
    ax_dir = ear - nose; ax_dir = ax_dir / (np.linalg.norm(ax_dir) + 1e-6)
    ccx, ccy = ear[0] + 0.70 * ear_sep * ax_dir[0], ear[1] + 0.70 * ear_sep * ax_dir[1]
    dxp = xx - ccx; dyp = yy - ccy
    along = dxp * ax_dir[0] + dyp * ax_dir[1]; across = -dxp * ax_dir[1] + dyp * ax_dir[0]
    crown = np.clip((1.0 - np.sqrt((across / (0.62 * ear_sep)) ** 2 + (along / (1.30 * ear_sep)) ** 2)) / 0.18, 0, 1)
    cls = np.clip(cv2.GaussianBlur(head, (0, 0), 0.012 * ws) * 2.2, 0, 1)   # the class, blurred and gained: its fringe fades at the skull's edge
    if _HEAD_PREV is not None and _HEAD_PREV.shape == cls.shape:
        cls = 0.6 * _HEAD_PREV + 0.4 * cls
    _HEAD_PREV = cls
    face_in = (0 <= nose[0] < ws and 0 <= nose[1] < hs and 0 <= ear[0] < ws and 0 <= ear[1] < hs and 6 < ear_sep < 0.9 * ws)
    head_g = (np.maximum(np.maximum(geo, crown), cls) if face_in else cls) if head_gate else 0.0   # no face in the frame (he stands up at the end): the class alone
    below = np.clip((yy - (hip[1] - 0.30 * trunk)) / (0.06 * trunk), 0, 1)
    m = a_s * (1 - head_g) * (1 - clothes * below)
    if bar_line is not None:
        bar_row = (bar_line[0] * xx / s + bar_line[1]) * s
        m = m * np.clip((yy - (bar_row + 6 * s)) / 3.0, 0, 1)
    # the hands are not painted (2026-09-10: they read as blue gloves): a half-plane beyond each wrist,
    # perpendicular to the forearm, fades the paint out over ~3 % of the frame width
    for sh_i, wr_i in ((11, 15), (12, 16)):                 # the axis from the SHOULDER (reliable) to the wrist: the elbow leaves the frame at the bottom
        e_ = P[sh_i] * s; w_ = P[wr_i] * s; ax = w_ - e_; L_ = float(np.linalg.norm(ax))
        if L_ > 4:
            ax /= L_
            beyond = ((xx - w_[0]) * ax[0] + (yy - w_[1]) * ax[1]) / (0.03 * ws)
            near_w = np.clip((0.55 * sw - np.sqrt((xx - w_[0]) ** 2 + (yy - w_[1]) ** 2)) / (0.10 * sw), 0, 1)   # only near the wrist: when he stands, "beyond the wrist" would be the whole leg
            m = m * (1 - near_w * np.clip(beyond, 0, 1))
    # Dennis (2026-09-10): "get my legs into the picture, with the heat map, even if artificially". The RVM
    # matte holds no alpha at the far feet (2 m away, a few dozen px), so the shanks and feet get a synthetic
    # capsule from the knee -> ankle landmarks (the renderer passes STATIC medians while the feet are on the
    # floor, since they do not move, and the live landmarks once he stands up), radius LEG_CAPSULE x the
    # shoulder width, only below the hips in the picture.
    for kn_i, an_i in ((25, 27), (26, 28)):
        k_ = P[kn_i] * s; a_ = P[an_i] * s
        if not (np.isfinite(k_).all() and np.isfinite(a_).all()) or k_[1] < hip[1] or a_[1] < hip[1]:
            continue
        seg = a_ - k_; L_ = float(np.linalg.norm(seg))
        if L_ < 3 or L_ > 0.6 * hs:
            continue
        foot = a_ + seg / L_ * 0.35 * L_                       # the foot continues past the ankle toward the toes
        tvec = foot - k_; TL = float(np.linalg.norm(tvec)); u_ = tvec / TL
        proj = np.clip(((xx - k_[0]) * u_[0] + (yy - k_[1]) * u_[1]) / TL, 0, 1)
        cxp = k_[0] + proj * tvec[0]; cyp = k_[1] + proj * tvec[1]
        dist_ = np.sqrt((xx - cxp) ** 2 + (yy - cyp) ** 2)
        r_ = LEG_CAPSULE * sw
        cap = np.clip((r_ - dist_) / (0.35 * r_), 0, 1) * (1 - head_g)
        m = np.maximum(m, cap.astype(np.float32))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    mask = m > 0.4

    lab, theta = label_and_fibre(P, (hs, ws), div=1 / s)
    lab = np.where(mask, lab, 0).astype(np.uint8)
    # ---- one continuous field (Dennis, 2026-09-09 evening): feather every region's mask against
    # its neighbours and normalise the set to a partition of unity inside the silhouette. Every
    # per-region quantity below (effort, activation, the striation texture) is a sum of
    # weight x region value, so it crosses a boundary as a smooth ramp about 2 x sig_f wide
    # (~17 px on screen) instead of a step. The set #2/#3 renders drew a dark line on every
    # boundary and shaded each region toward its edge; both are gone.
    sig_f = max(2.0, 0.016 * ws)                 # 8.6 px in the half-res grid on a 1080-wide frame
    present = [int(i) for i in np.unique(lab) if i > 0]
    wts = {}; wsum = np.zeros((hs, ws), np.float32)
    for idx in present:
        wi = cv2.GaussianBlur((lab == idx).astype(np.float32), (0, 0), sig_f)
        wts[idx] = wi; wsum += wi
    inside = wsum > 0.05
    for idx in present:
        wts[idx] = np.where(inside, wts[idx] / np.maximum(wsum, 1e-3), 0).astype(np.float32)
    # Dennis (2026-09-10): "get my legs into the picture, with the heat map". The legs are 2 m away and
    # MediaPipe's knee / ankle visibility is near zero, so the thigh and shank polygons often miss them;
    # every masked pixel that no polygon reaches is painted as LEGS (the quadriceps' value), feathered.
    orphan = cv2.GaussianBlur((mask & ~inside).astype(np.float32), (0, 0), sig_f)
    orphan = np.where(mask, orphan, 0).astype(np.float32)
    LEG_KEY = "quadriceps"

    def field(vals, scale_by):
        f = np.zeros((hs, ws), np.float32)
        for key, idx in IDX.items():
            if idx in wts:
                f += wts[idx] * float(np.clip(vals.get(key, 0.0) / scale_by, 0, 1))
        f += orphan * float(np.clip(vals.get(LEG_KEY, 0.0) / scale_by, 0, 1))
        return np.clip(f, 0, 1).astype(np.float32)

    temp = field(reg_T, t_scale)
    act = field(reg_A, 1.0)

    # ---- anatomy shading, at matte resolution ----
    # 1. a gentle whole-body bulge: distance to the SILHOUETTE edge (never to a region boundary),
    #    scaled on the shoulder width so a limb reaches ~0.5 and the trunk 1; amplitude 0.14 in
    #    the shade below. The matte handles the silhouette edge itself; this only rounds the limbs.
    dist = cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 3)
    belly = cv2.GaussianBlur(np.clip(dist / (0.30 * sw), 0, 1).astype(np.float32), (0, 0), 3.0)
    # 2. striations along the fibre field: thin, irregular fibre bundles. The across-fibre
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
    #    Two fibre directions meet at every region boundary, and the hard pattern showed a grain
    #    boundary there (a line by another name). Each region keeps its own sharp pattern inside
    #    and is extended a few px past its edge by normalised convolution; the feathered weights
    #    cross-fade the patterns across the seam, the same way the effort crosses it.
    blend = np.zeros((hs, ws), np.float32)
    for idx in present:
        mi = (lab == idx).astype(np.float32)
        num = cv2.GaussianBlur(stria * mi, (0, 0), sig_f); den = cv2.GaussianBlur(mi, (0, 0), sig_f)
        ext = np.where(mi > 0, stria, np.where(den > 0.02, num / np.maximum(den, 1e-3), 0.5))
        blend += wts[idx] * ext
    stria = np.where(inside, blend, 0.5).astype(np.float32)

    # ---- compose at full resolution: set #1's recipe (pullup_heat.HeatPainter.paint, commit cc01157, the 140k
    # reel; Dennis 2026-09-10: "look into the old code for the visual"). Two things made that look: the colour
    # index carried a DEFINITION term, the frame's own local contrast (where the light shows the muscle lines)
    # at a quarter weight and kept away from the outline; and the shading under the colour was near solid,
    # lum = 0.78 + 0.26 x grey, "only a hint of shading". Set #3's deeper luminance, belly and striations are
    # gone here; the activation pulse stays a nudge. ----
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    up = lambda a: cv2.resize(a.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    tempF, actF = map(up, (temp, act))
    g8 = gray * 255
    hp = np.abs(g8 - cv2.GaussianBlur(g8, (0, 0), 31 / 3)); defin = cv2.GaussianBlur(hp, (0, 0), 21 / 3)
    er = cv2.erode((mask).astype(np.uint8), np.ones((9, 9), np.uint8))
    interior = up(cv2.GaussianBlur(er.astype(np.float32), (0, 0), 2))
    d_ = np.clip(defin / DEF_REF, 0, 1.2) * interior
    idx = (np.clip(0.10 + 0.86 * tempF + DEFINITION * d_ * (0.4 + 0.6 * actF), 0, 1) * 255).astype(np.uint8)
    col = cv2.LUT(cv2.merge([idx, idx, idx]), LUT).astype(np.float32)
    lum = 0.78 + 0.26 * gray                                    # solid colour, only a hint of shading (set #1)
    shade = lum * (0.94 + 0.12 * actF)
    col = np.clip(col * shade[:, :, None], 0, 255)
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
