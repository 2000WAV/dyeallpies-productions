"""
"Muscle heat" overlay for the pull-up reel - an EMG-informed activation map, not a
measurement of Dennis's muscles.

    heat = base(fatigue) + literature activation(muscle region) x phase/effort
                         + skin definition (image contrast) x phase/effort

Literature (surface EMG, %MVIC, average over the rep):
  Youdas et al. 2010, J Strength Cond Res 24(12):3404-14 (pull-up / chin-up, 25 subjects):
    latissimus dorsi 117-130, biceps brachii 78-96, infraspinatus 71-79, lower trapezius
    45-56, pectoralis major 44-57, erector spinae 39-41, external oblique 31-35.
  Dickie et al. 2017, J Electromyogr Kinesiol 32:30-36 (19 trained men, 4 grips):
    concentric phases > eccentric phases for brachioradialis, biceps brachii and pec major.
  Fatigue base: Sanchez-Medina & Gonzalez-Badillo 2011, Med Sci Sports Exerc 43(9):1725-34 -
    velocity loss within a set tracks metabolic fatigue (lactate r = 0.93-0.97), and it does
    not recover in the seconds between reps. The whole body therefore warms up through the
    set in proportion to the measured velocity loss (plus the energy already spent).
Dennis uses a pronated grip, so the pull-up end of each Youdas range is used.

Paint region (from extract_matte.py): RVM alpha x (1 - clothes) x (1 - head), with the
head term allowed only above the shoulders near the head landmarks and the clothes term
only around and below the hips - a tattoo labelled "clothes" or a chest labelled "face"
when the real face is behind the bar must not punch holes in the torso.
"""
import numpy as np
import cv2

MUSCLES = {
    "latissimus dorsi": 124, "biceps brachii": 78, "infraspinatus": 75, "trapezius": 52,
    "pectoralis major": 44, "external oblique": 33, "brachioradialis (est.)": 62,
}
HEAT = {k: v / 130 for k, v in MUSCLES.items()}
PHASE_FACTOR = {"PULL": 1.0, "HOLD": 0.85, "LOWER": 0.65, "HANG": 0.35, "LOADING": 0.25, "HANDS ON BAR": 0.12, "SETUP": 0.08, "DONE": 0.08}

# blue -> violet -> red -> hot, BGR stops
_STOPS = [(0.00, (200, 90, 30)), (0.35, (190, 60, 140)), (0.65, (60, 50, 230)), (0.85, (40, 120, 255)), (1.00, (120, 230, 255))]


def make_lut():
    lut = np.zeros((256, 1, 3), np.uint8)
    xs = [s[0] for s in _STOPS]; cs = np.array([s[1] for s in _STOPS], float)
    for i in range(256):
        t = i / 255
        k = min(max(j for j in range(len(xs)) if xs[j] <= t), len(xs) - 2)
        u = (t - xs[k]) / (xs[k + 1] - xs[k])
        lut[i, 0] = np.clip(cs[k] * (1 - u) + cs[k + 1] * u, 0, 255)
    return lut


LUT = make_lut()


def definition_map(gray, k_hp=31, k_sm=21):
    g = gray.astype(np.float32)
    hp = np.abs(g - cv2.GaussianBlur(g, (0, 0), k_hp / 3))
    return cv2.GaussianBlur(hp, (0, 0), k_sm / 3)


def effort_from_speed(vy_m, phase, v_ref):
    """Per-frame effort 0..1: phase factor from the EMG literature, scaled by measured speed."""
    e = np.zeros(len(vy_m))
    for i, ph in enumerate(phase):
        f = PHASE_FACTOR.get(ph, 0.0)
        if ph == "PULL":
            f *= 0.7 + 0.3 * min(1.0, max(0.0, vy_m[i]) / v_ref)
        elif ph == "LOWER":
            f *= 0.8 + 0.2 * min(1.0, max(0.0, -vy_m[i]) / v_ref)
        e[i] = f
    return np.convolve(e, np.ones(5) / 5, mode="same")


def fatigue_curve(reps, N, kcal_total):
    """Per-frame fatigue 0..1 that only accumulates: velocity loss of the latest completed rep
    relative to the best rep so far (65 %) plus the share of the set's energy spent (35 %).
    Linear between rep ends, held afterwards (no recovery within a set: Sanchez-Medina 2011)."""
    f = np.zeros(N); best = 0.0; cum = 0.0; pts = [(0, 0.0)]
    for r in reps:
        best = max(best, r["peak_conc_v"]); cum += r.get("kcal", 0.0)
        vl = 1 - r["peak_conc_v"] / best
        val = float(np.clip(0.65 * vl / 0.45 + 0.35 * (cum / kcal_total if kcal_total else 0), 0, 1))
        pts.append((r["f_end"], max(val, pts[-1][1])))
    for (a, va), (b, vb) in zip(pts[:-1], pts[1:]):
        f[a:b + 1] = np.linspace(va, vb, b - a + 1)
    f[pts[-1][0]:] = pts[-1][1]
    return f


class HeatPainter:
    def __init__(self, W, H, def_ref, alpha=0.96, div=3, bar_y=None):
        self.W, self.H, self.def_ref, self.alpha, self.div, self.bar_y = W, H, def_ref, alpha, div, bar_y
        self.w, self.h = W // div, H // div

    def _line(self, canvas, a, b, thick, val):
        cv2.line(canvas, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), float(val), int(max(2, thick)), cv2.LINE_AA)

    def muscle_map(self, P):
        d = self.div
        c = np.zeros((self.h, self.w), np.float32)
        p = P / d
        sh_l, sh_r, hip_l, hip_r = p[11], p[12], p[23], p[24]
        el_l, el_r, wr_l, wr_r = p[13], p[14], p[15], p[16]
        sm, hm = (sh_l + sh_r) / 2, (hip_l + hip_r) / 2
        sw = max(np.linalg.norm(sh_r - sh_l), 8.0); ax = hm - sm; trunk = max(np.linalg.norm(ax), 8.0)
        u = ax / trunk
        def out(pt, side):
            v = pt - sm; v = v - u * (v @ u); n = np.linalg.norm(v)
            return v / n if n > 1e-3 else np.array([side, 0.0])
        layers = []
        def put(val, draw):
            l = np.zeros_like(c); draw(l); layers.append((l, val))
        for shp, hp, side in ((sh_l, hip_l, 1), (sh_r, hip_r, -1)):
            o = out(shp, side)
            a = shp + 0.16 * ax + o * 0.06 * sw; b = hp - 0.18 * ax + o * 0.04 * sw
            put(HEAT["latissimus dorsi"], lambda l, a=a, b=b: self._line(l, a, b, 0.42 * sw, 1.0))
        ctr = sm + 0.20 * ax
        put(HEAT["pectoralis major"], lambda l: cv2.ellipse(l, (int(ctr[0]), int(ctr[1])), (int(0.46 * sw), int(0.15 * trunk)), 0, 0, 360, 1.0, -1))
        for s_, e_, w_ in ((sh_l, el_l, wr_l), (sh_r, el_r, wr_r)):
            put(HEAT["biceps brachii"], lambda l, a=s_ + 0.15 * (e_ - s_), b=e_: self._line(l, a, b, 0.30 * sw, 1.0))
            put(HEAT["brachioradialis (est.)"], lambda l, a=e_, b=w_: self._line(l, a, b, 0.24 * sw, 1.0))
        for shp in (sh_l, sh_r):
            put(HEAT["infraspinatus"], lambda l, q=shp: cv2.circle(l, (int(q[0]), int(q[1])), int(0.24 * sw), 1.0, -1))
        neck = sm - 0.10 * ax
        for shp in (sh_l, sh_r):
            put(HEAT["trapezius"], lambda l, q=shp: self._line(l, neck, q, 0.16 * sw, 1.0))
        for hp, side in ((hip_l, 1), (hip_r, -1)):
            o = out(hp, side)
            a = hm + 0.45 * (-ax) + o * 0.34 * sw; b = hp + o * 0.05 * sw
            put(HEAT["external oblique"], lambda l, a=a, b=b: self._line(l, a, b, 0.28 * sw, 1.0))
        for l, val in layers:
            l = cv2.GaussianBlur(l, (0, 0), max(2.0, 0.045 * sw))
            c = np.maximum(c, l * val)
        return c

    def region(self, comp_small, P, V):
        """Paint region (full res 0..1) = alpha x (1 - head, gated) x (1 - clothes, gated) x hip fade."""
        cs = comp_small.astype(np.float32) / 255
        alpha, clothes, head = cs[..., 0], cs[..., 1], cs[..., 2]
        hs, ws = alpha.shape
        s = ws / self.W                                         # small-scale factor
        sh = (P[11] + P[12]) / 2 * s; hip = (P[23] + P[24]) / 2 * s
        trunk = float(np.linalg.norm(hip - sh)) + 1e-3
        yy = np.arange(hs, dtype=np.float32)[:, None]; xx = np.arange(ws, dtype=np.float32)[None, :]
        # head: only above the shoulders (minus a neck margin) and near the ear midpoint
        ear = (P[7] + P[8]) / 2 * s; ear_w = max(float(np.linalg.norm(P[7] - P[8])) * s, 12.0)
        above = np.clip((sh[1] - 0.10 * trunk - yy) / (0.06 * trunk), 0, 1)
        near = np.clip((1.9 * ear_w - np.sqrt((xx - ear[0]) ** 2 + (yy - ear[1]) ** 2)) / (0.4 * ear_w), 0, 1)
        head_g = head * above * near
        # clothes: only from a little above the hips downwards (shorts), never on the chest
        below = np.clip((yy - (hip[1] - 0.30 * trunk)) / (0.06 * trunk), 0, 1)
        clothes_g = clothes * below
        m = alpha * (1 - head_g) * (1 - clothes_g)
        if self.bar_y is not None:                               # nothing above the bar is body (fingers, lintel)
            m = m * np.clip((yy - (self.bar_y + 6) * s) / 3.0, 0, 1)
        # legs stay natural: fade out below the hip line
        y_lim = hip[1] + 0.12 * trunk
        m = m * np.clip((y_lim + 0.10 * trunk - yy) / (0.10 * trunk), 0, 1)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))   # seal pinholes
        mf = cv2.resize(m, (self.W, self.H), interpolation=cv2.INTER_CUBIC)
        mf = np.clip(cv2.GaussianBlur(mf, (0, 0), 1.0), 0, 1)
        er = cv2.erode((m > 0.5).astype(np.uint8), np.ones((9, 9), np.uint8))
        interior = cv2.resize(cv2.GaussianBlur(er.astype(np.float32), (0, 0), 2), (self.W, self.H))
        return mf, interior, m

    def muscle_map_sil(self, P, m_small):
        """Literature activation map built ON THE SILHOUETTE: every painted pixel is assigned to
        the nearest skeleton segment (torso axis, upper arms, forearms); torso pixels are then
        banded by how far out toward the silhouette edge they sit (lats = outer band from the
        armpit to the waist, obliques = outer band lower down, pecs = central upper chest,
        trapezius = just under the shoulder line, abdomen = base + image definition)."""
        hs, ws = m_small.shape
        s = ws / self.W
        p = P * s
        sh_l, sh_r, hip_l, hip_r = p[11], p[12], p[23], p[24]
        el_l, el_r, wr_l, wr_r = p[13], p[14], p[15], p[16]
        sm, hm = (sh_l + sh_r) / 2, (hip_l + hip_r) / 2
        sw = max(float(np.linalg.norm(sh_r - sh_l)), 6.0)
        ax = hm - sm; trunk = max(float(np.linalg.norm(ax)), 6.0); u = ax / trunk; nrm = np.array([-u[1], u[0]])
        mask = m_small > 0.3
        ys, xs = np.nonzero(mask)
        out = np.zeros((hs, ws), np.float32)
        if len(xs) < 50:
            return out
        X = np.stack([xs, ys], 1).astype(np.float32)
        segs = [(sm, hm), (sh_l, el_l), (sh_r, el_r), (el_l, wr_l), (el_r, wr_r)]
        D = []
        for a, b in segs:
            ab = b - a; L2 = float(ab @ ab) + 1e-6
            t = np.clip(((X - a) @ ab) / L2, 0, 1)
            proj = a + t[:, None] * ab
            D.append(np.linalg.norm(X - proj, axis=1))
        D = np.stack(D, 1)
        lab = np.argmin(D, 1)
        val = np.full(len(xs), 0.12, np.float32)
        # arms
        val[lab == 1] = HEAT["biceps brachii"]; val[lab == 2] = HEAT["biceps brachii"]
        val[lab == 3] = HEAT["brachioradialis (est.)"]; val[lab == 4] = HEAT["brachioradialis (est.)"]
        # deltoid / posterior-shoulder caps on top
        for shp in (sh_l, sh_r):
            cap = np.linalg.norm(X - shp, axis=1) < 0.30 * sw
            val[cap] = np.maximum(val[cap], HEAT["infraspinatus"])
        # torso bands
        tor = lab == 0
        if tor.any():
            dt = cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 5)
            d_edge = dt[ys[tor], xs[tor]]
            rel = X[tor] - sm
            t = (rel @ u) / trunk                                  # 0 shoulders .. 1 hips
            d_axis = np.abs(rel @ nrm)
            frac = d_axis / (d_axis + d_edge + 1e-3)               # 0 centre .. 1 edge
            v = np.full(tor.sum(), 0.12, np.float32)
            pec = (t < 0.32) & (frac < 0.62)
            v[pec] = np.maximum(v[pec], HEAT["pectoralis major"])
            trap = t < 0.08
            v[trap] = np.maximum(v[trap], HEAT["trapezius"])
            obl = (t > 0.5) & (t < 1.08) & (frac > 0.5)
            v[obl] = np.maximum(v[obl], HEAT["external oblique"])
            lat = (t > 0.05) & (t < 0.85) & (frac > 0.55)
            lat_w = np.clip((frac - 0.55) / 0.2, 0, 1) * np.clip((0.85 - t) / 0.15, 0, 1)
            v[lat] = np.maximum(v[lat], HEAT["latissimus dorsi"] * (0.6 + 0.4 * lat_w[lat]))
            val[tor] = v
        out[ys, xs] = val
        out = cv2.GaussianBlur(out, (0, 0), max(1.5, 0.03 * sw))
        return out

    def paint(self, frame_bgr, comp_small, P, V, effort, fatigue=0.0):
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        reg, interior, m_small = self.region(comp_small, P, V)
        d = np.clip(definition_map(gray) / self.def_ref, 0, 1.2) * interior
        lit = cv2.resize(self.muscle_map_sil(P, m_small), (self.W, self.H), interpolation=cv2.INTER_LINEAR)
        heat = np.clip(0.10 + 0.30 * fatigue + 0.62 * lit * (0.35 + 0.65 * effort) + 0.25 * d * (0.4 + 0.6 * effort), 0, 1)
        idx = (heat * 255).astype(np.uint8)
        col = cv2.LUT(cv2.merge([idx, idx, idx]), LUT).astype(np.float32)
        lum = (0.78 + 0.26 * gray.astype(np.float32) / 255)[:, :, None]     # solid colour, only a hint of shading
        col = col * lum
        a = reg[:, :, None] * self.alpha
        return np.clip(frame_bgr.astype(np.float32) * (1 - a) + col * a, 0, 255).astype(np.uint8)
