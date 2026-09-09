"""
Landmark-warped muscle atlas for the pull-up overlay.

The first video assigned every painted pixel to the nearest skeleton segment and then
banded the torso by distance-to-edge. That put "lats" wherever the outline happened to be
and left arms half-painted. This module instead draws each muscle ONCE as a polygon in a
canonical body frame and warps it onto the frame with that frame's landmarks:

  torso frame   origin = shoulder midpoint, s = fraction of the way down the trunk
                (0 at the shoulder line, 1 at the hip line), d = lateral offset in units
                of HALF the shoulder width (+ = the person's left, which is image right
                in this mirror view).
  arm frames    origin = the proximal joint, l = fraction along shoulder->elbow (or
                elbow->wrist), w = lateral offset in units of half the segment width.

Polygons deliberately overshoot the body outline; the silhouette (RVM alpha from
extract_matte.py) clips them, so every region ends exactly at the real edge and the map
follows the actual body rather than a fixed-width blob.

Region -> muscle names refer to tools/scripts/pullup_thermal.py.
"""
import numpy as np
import cv2

L_SH, R_SH = 11, 12; L_EL, R_EL = 13, 14; L_WR, R_WR = 15, 16
L_HIP, R_HIP = 23, 24; L_KNEE, R_KNEE = 25, 26; L_ANK, R_ANK = 27, 28

# ---- canonical torso polygons, (s, d). + d = the person's LEFT side. -------------------
# Each entry: region key -> list of polygons in canonical torso coordinates.
TORSO = {
    "trapezius": [
        [(-0.10, 0.10), (-0.09, 0.98), (0.05, 1.02), (0.06, 0.10)],
        [(-0.10, -0.10), (-0.09, -0.98), (0.05, -1.02), (0.06, -0.10)],
    ],
    "pectoralis major": [
        [(0.02, 0.06), (0.03, 0.92), (0.26, 0.86), (0.33, 0.10)],
        [(0.02, -0.06), (0.03, -0.92), (0.26, -0.86), (0.33, -0.10)],
    ],
    "latissimus dorsi": [
        [(0.05, 0.74), (0.04, 1.25), (0.60, 1.15), (0.62, 0.62), (0.30, 0.72)],
        [(0.05, -0.74), (0.04, -1.25), (0.60, -1.15), (0.62, -0.62), (0.30, -0.72)],
    ],
    "external oblique": [
        [(0.58, 0.40), (0.60, 1.15), (1.02, 1.00), (1.00, 0.26)],
        [(0.58, -0.40), (0.60, -1.15), (1.02, -1.00), (1.00, -0.26)],
    ],
    "rectus abdominis": [
        [(0.34, -0.30), (0.34, 0.30), (1.04, 0.24), (1.04, -0.24)],
    ],
}
# ---- canonical arm polygons, (l, w) ---------------------------------------------------
UPPER_ARM = {
    "elbow flexors": [[(0.14, -1.30), (0.14, 1.30), (1.00, 1.30), (1.00, -1.30)]],
}
FOREARM = {
    "forearm flexors": [[(0.00, -1.30), (0.00, 1.30), (0.96, 1.30), (0.96, -1.30)]],
}
# legs: hip->knee and knee->ankle, same per-segment frame as the arms
THIGH = {
    "hip flexors": [[(0.00, -1.30), (0.00, 1.30), (0.26, 1.30), (0.26, -1.30)]],
    "quadriceps":  [[(0.22, -1.30), (0.22, 1.30), (1.02, 1.30), (1.02, -1.30)]],
}
SHANK = {
    "calves": [[(0.00, -1.30), (0.00, 1.30), (1.02, 1.30), (1.02, -1.30)]],
}
# shoulder caps are drawn as discs at the shoulder landmarks
SHOULDER_CAP = "posterior shoulder"

# region -> the thermal-model muscles it stands for (mass-weighted when several)
REGION_MUSCLES = {
    "trapezius": ["trapezius"],
    "pectoralis major": ["pectoralis major"],
    "latissimus dorsi": ["latissimus dorsi", "teres major"],
    "external oblique": ["external oblique"],
    "rectus abdominis": ["rectus abdominis"],
    "elbow flexors": ["biceps brachii", "brachialis"],
    "forearm flexors": ["forearm flexors", "brachioradialis"],
    "posterior shoulder": ["posterior deltoid", "infraspinatus"],
    "hip flexors": ["hip flexors"],
    "quadriceps": ["quadriceps", "hamstrings"],
    "calves": ["calves"],
}
REGIONS = list(REGION_MUSCLES)
# draw order: later regions win where polygons overlap
ORDER = ["quadriceps", "calves", "hip flexors", "rectus abdominis", "external oblique",
         "pectoralis major", "latissimus dorsi", "trapezius", "posterior shoulder",
         "elbow flexors", "forearm flexors"]
IDX = {r: i + 1 for i, r in enumerate(ORDER)}       # 0 = unassigned


def region_values(series, masses, frame):
    """Mass-weighted value of each atlas region at one frame, for any per-muscle series."""
    out = {}
    for r, ms in REGION_MUSCLES.items():
        w = sum(masses[m] for m in ms)
        out[r] = sum(series[m][frame] * masses[m] for m in ms) / w
    return out


def region_temperatures(T, masses, frame):
    """Temperature of each atlas region at one frame (mass-weighted over its muscles)."""
    return region_values(T, masses, frame)


def _poly(pts, origin, e1, e2, scale1, scale2):
    a = np.array([origin + p[0] * scale1 * e1 + p[1] * scale2 * e2 for p in pts])
    return np.round(a).astype(np.int32)


def label_map(P, shape, div=1):
    """Region-index map (uint8) for one frame's landmarks P (33x2, image pixels).

    shape = (h, w) of the output map; div = P is divided by this before drawing."""
    h, w = shape
    lab = np.zeros((h, w), np.uint8)
    p = P / div
    sl, sr, hl, hr = p[L_SH], p[R_SH], p[L_HIP], p[R_HIP]
    sm = (sl + sr) / 2; hm = (hl + hr) / 2
    ax = hm - sm
    trunk = float(np.linalg.norm(ax))
    if trunk < 6:
        return lab
    u = ax / trunk                                   # down the trunk
    r = sl - sr
    sw = float(np.linalg.norm(r))
    if sw < 4:
        return lab
    r = r / sw                                       # toward the person's LEFT
    half = sw / 2

    for key in ORDER:
        idx = IDX[key]
        if key in TORSO:
            for poly in TORSO[key]:
                cv2.fillPoly(lab, [_poly(poly, sm, u, r, trunk, half)], idx)
        elif key == SHOULDER_CAP:
            for q in (sl, sr):
                cv2.circle(lab, (int(round(q[0])), int(round(q[1]))), int(round(0.27 * half * 2)), idx, -1)
        elif key == "elbow flexors":
            for a, b in ((p[L_SH], p[L_EL]), (p[R_SH], p[R_EL])):
                seg = b - a
                L = float(np.linalg.norm(seg))
                if L < 4:
                    continue
                e1 = seg / L
                e2 = np.array([-e1[1], e1[0]])
                for poly in UPPER_ARM[key]:
                    cv2.fillPoly(lab, [_poly(poly, a, e1, e2, L, 0.30 * half)], idx)
        elif key == "forearm flexors":
            for a, b in ((p[L_EL], p[L_WR]), (p[R_EL], p[R_WR])):
                seg = b - a
                L = float(np.linalg.norm(seg))
                if L < 4:
                    continue
                e1 = seg / L
                e2 = np.array([-e1[1], e1[0]])
                for poly in FOREARM[key]:
                    cv2.fillPoly(lab, [_poly(poly, a, e1, e2, L, 0.26 * half)], idx)
        elif key in THIGH or key in SHANK:
            table = THIGH if key in THIGH else SHANK
            pairs = (((p[L_HIP], p[L_KNEE]), (p[R_HIP], p[R_KNEE])) if key in THIGH
                     else ((p[L_KNEE], p[L_ANK]), (p[R_KNEE], p[R_ANK])))
            wid = 0.40 * half if key in THIGH else 0.32 * half
            for a, b in pairs:
                seg = b - a
                L = float(np.linalg.norm(seg))
                if L < 4:
                    continue
                e1 = seg / L
                e2 = np.array([-e1[1], e1[0]])
                for poly in table[key]:
                    cv2.fillPoly(lab, [_poly(poly, a, e1, e2, L, wid)], idx)
    return lab


def build(P, m_small, reg_T, t_scale, full_shape, reg_A=None):
    """Return (temperature field 0..1, activation field 0..1, label map) at m_small size.

    Pixels inside the silhouette with no region (head, gaps) get the lowest value so they
    stay cool rather than picking up a neighbour's colour.
    """
    h, w = m_small.shape
    scale = full_shape[1] / w
    lab = label_map(P, (h, w), div=scale)
    mask = m_small > 0.3
    sig = max(1.2, 0.02 * w)
    ms = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), sig)

    def field_from(vals, scale_by):
        f = np.zeros((h, w), np.float32)
        for key, idx in IDX.items():
            f[lab == idx] = float(np.clip(vals.get(key, 0.0) / scale_by, 0, 1))
        f = np.where(mask, f, 0).astype(np.float32)
        fs = cv2.GaussianBlur(f, (0, 0), sig)
        return np.clip(np.where(ms > 0.05, fs / np.maximum(ms, 1e-3), 0), 0, 1).astype(np.float32)

    temp = field_from(reg_T, t_scale)
    act = field_from(reg_A, 1.0) if reg_A else np.zeros((h, w), np.float32)
    return temp, act, np.where(mask, lab, 0).astype(np.uint8)
