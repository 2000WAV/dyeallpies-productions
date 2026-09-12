"""The marionette layer: MuJoCo poses rasterised on the GPU (depth + body ID at 2x, shaded in a
fragment shader, strings as anti-aliased quads, motion blur by accumulation), composited on the
plate behind the hand matte, with bloom, spill and grain.

    python render_puppet.py <master.mp4> <hand3d.npz> <sim.npz> <matte.npy> <out.mp4>
        [look=red] [style=neon|solid] [string_px=3] [bake=hand/work/puppet_layer.npy] [preview=42,44,48,60]
        [trim=0,267] [shutter=0.5] [scale=2] [backend=gl|cpu] [plate=wall|black] [hand_gain=1.0] [spill=1.0] [spill_hi=1.0] [wall=1.0]

Two backends, one look (2026-09-12). `backend=gl` (default, studio.gl on the RTX 2060) reproduces the
CPU shader below term for term from the same depth + ID buffers: 0.05 s a frame instead of 8.7 s
(8 motion-blur sub-samples of 0.30 s MuJoCo read-back + 0.57 s NumPy shading + 0.15 s strings).
`backend=cpu` is the 2026-09-11 path, kept for the equality check. The neon style's `core` term (the
distance to the body's edge) is a jump-flood distance field on the GPU (studio.gl.distance_field),
normalised by the body's own thickness in px instead of the image's per-body maximum.

Neon on black (2026-09-12, Dennis): `plate=black` isolates the hand on pitch black (the matte's edge
decontaminated against the wall colour), puts the figure behind it, blooms over both and lets the
figure's light fall on the hand (`spill`); `look=violet` / `violet-mix` (violet dominant, no green,
several neon hues on the parts).

Two styles (2026-09-12, Dennis: the neon figure "is very bright and loses focus against the white
wall; opaque and sharp without too much white"):
  neon  = the first delivery: emissive, a wide white-ish rim, a shoulder that lets the core go white, bloom 0.45.
  solid = an opaque figure lit by a directional key: E = c * (0.18 + 0.82 * lambert) + spec; a DARK
          rim (the silhouette edge multiplied by 0.55 where n.v is small) so the outline contrasts with
          the light wall instead of glowing into it; the maximum channel is held under 0.72 so nothing
          clips to white; the bloom is only the near halo (sigma 3 at 0.08) plus a faint wall spill.
          Item 09 (colour salience, figure-ground) is the source for the choice of a dark edge and a
          saturated hue; the numbers here are the first pass, judged on Dennis's screen.

Bake-once rule (memory render-iteration-cache): everything that depends on the sim and the look is
`bake_frame()`: it writes premultiplied linear RGB + alpha at 1x into `bake` (float16 memmap, one
record per source frame, a JSON sidecar with the validity key: studio.cache). The composite (matte,
bloom, spill, grain, encode) reads it back and works inside the figure's bounding box only.

Look (hand/PLAN.md decision 1: neon, "crystal / lighting", opaque, very 3D). The pass list follows
references/marionette/06-neon-rendering-and-assets.md section 10 (normal-from-depth gated by the
body id, emissive base, internal gradient, Schlick rim, specular, string cores, mip bloom):
  E = c * (0.22 + 0.45 * lambert + 0.45 * core) + rim + spec       (linear light, HDR)
  core    = the body's own thickness gradient (distance to its silhouette, normalised per body): the
            figure looks lit from inside, thicker parts brighter (what sells "crystal")
  lambert = max(n.l, 0) from a key light upper-left-front (the window is at the left; the specular
            read is what matters, not the room's exact light). The first render's 0.30 ambient +
            0.45 core made a flat pale blob, 0.12 + 0.55 lambert a dark plastic toy (2026-09-11).
  rim     = (1 - n.v)^3 * 2.0 * mix(c, white, 0.5): 06 gives Schlick's 5 as the physical exponent and
            2-3 as the stylised wide rim; a neon tube's bright edge is the wide one
  spec    = (n.h)^80 * 1.5 * white
  strings = a 3 px core at 2x (1.5 px at 1x, LINE_AA) in the string colour at 1.0x, not the 1.6x that
            blew them to white; catenary when slack, straight when taut, depth-tested against the figure
  bloom   = sum of Gaussian blurs of the visible layer (sigma 3, 9, 27, 81 px at 1x, weights 0.22 0.12
            0.07 0.04 = 0.45 total: 06 reports 0.04 (Jimenez 2014), 0.03-0.15 (LearnOpenGL), 0.05 (EEVEE)
            as a whole-frame game blend; here the layer is only the emissive subject, so the weight is the
            glow itself and sits above that range; the wide levels are the spill on the wall)
  shoulder: per channel y = x (x < 0.8), 0.8 + 0.2 (1 - exp(-(x - 0.8) / 0.2)) above: the hottest core
            goes white, the colour survives around it
  grain   = Gaussian noise at the plate's own high-pass std, on the figure's pixels only
Normals: from the 2x depth by central differences, one-sided at a body's edge (a different ID or
the background on the other side). Sub-frame motion blur: the sim's records inside the shutter
window are shaded and averaged (shutter 0.5 = 1/60 s at 30 fps; 05 will confirm the phone's).
"""
import sys, os, json, time, hashlib, inspect
import numpy as np
import cv2
import mujoco
from scipy.optimize import brentq
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # tools/ -> studio (or the .pth)
import puppet_model as pm
from studio import gl as sgl
from studio.colour import srgb_to_lin, lin_to_srgb, srgb8_to_lin, lin_to_srgb8
from studio.cache import BakeCache
from studio.encode import RawWriter

LOOKS = {
    # per-body linear-light colours (BGR order for OpenCV), a hue for the trunk/head and one for the limbs
    "cyan":    dict(trunk=(1.00, 0.70, 0.02), limb=(1.00, 0.45, 0.02), head=(1.00, 0.85, 0.10), string=(1.00, 0.90, 0.30)),
    "blue":    dict(trunk=(1.00, 0.30, 0.03), limb=(1.00, 0.18, 0.08), head=(1.00, 0.50, 0.12), string=(1.00, 0.70, 0.40)),
    "orange":  dict(trunk=(0.02, 0.40, 1.00), limb=(0.01, 0.25, 1.00), head=(0.10, 0.60, 1.00), string=(0.30, 0.75, 1.00)),
    # the saturated candidates for the solid style (2026-09-12): the strongest sRGB primaries and secondaries,
    # the limbs a little darker than the trunk so the joints read
    "red":     dict(trunk=(0.02, 0.02, 1.00), limb=(0.02, 0.02, 0.70), head=(0.03, 0.05, 1.00), string=(0.05, 0.05, 0.90)),
    "magenta": dict(trunk=(0.75, 0.02, 1.00), limb=(0.50, 0.02, 0.70), head=(0.85, 0.05, 1.00), string=(0.70, 0.05, 0.90)),
    "eblue":   dict(trunk=(1.00, 0.20, 0.02), limb=(0.70, 0.12, 0.02), head=(1.00, 0.30, 0.05), string=(0.95, 0.25, 0.05)),
    "green":   dict(trunk=(0.05, 1.00, 0.02), limb=(0.03, 0.70, 0.02), head=(0.10, 1.00, 0.05), string=(0.10, 0.90, 0.05)),
    "sorange": dict(trunk=(0.02, 0.30, 1.00), limb=(0.02, 0.20, 0.70), head=(0.03, 0.40, 1.00), string=(0.03, 0.30, 0.90)),
    # the neon-on-black family (2026-09-12, Dennis: body parts may differ in colour, several neon hues, no green,
    # violet dominant). Spectral violet is outside sRGB; "electric violet" #8F00FF is the usual in-gamut stand-in
    # (item 12 for the numbers): linear BGR (1.00, 0.00, 0.28). `bodies` overrides the class colour per body name.
    "violet":     dict(trunk=(1.00, 0.00, 0.28), limb=(1.00, 0.00, 0.14), head=(1.00, 0.06, 0.36), string=(1.00, 0.35, 0.60)),
    "violet-mix": dict(trunk=(1.00, 0.00, 0.28), limb=(1.00, 0.00, 0.14), head=(1.00, 0.06, 0.36), string=(1.00, 0.35, 0.60),
                       bodies=dict(upper_arm_l=(0.75, 0.00, 1.00), upper_arm_r=(0.75, 0.00, 1.00),      # magenta
                                   forearm_l=(1.00, 0.10, 0.04), forearm_r=(1.00, 0.10, 0.04),          # electric blue
                                   thigh_l=(1.00, 0.00, 0.14), thigh_r=(1.00, 0.00, 0.14),              # blue-violet
                                   shank_l=(0.00, 0.00, 1.00), shank_r=(0.00, 0.00, 1.00))),            # the boots: pure red #FF0000 (Dennis: 255, 0, 0; was amber, then near-red)
}
BLOOM = [(3, 0.22), (9, 0.12), (27, 0.07), (81, 0.04)]   # neon: sigma px at 1x, weight (see the docstring; 06 for the range)
BLOOM_SOLID = [(3, 0.04)]                                 # solid: the faintest near halo; item 09: bloom is veiling luminance and
                                                          # collapses the edge on a bright wall (2026-09-12)
STRING_PX = 3                                             # the string's width at 1x (2026-09-12, Dennis: thicker; was 1.5)
SPILL_REACH = 350                                         # px at 1x: the figure's light on the hand halves at this distance (2026-09-12)
KEY_LIGHT = np.array([-0.55, -0.60, 0.58]); KEY_LIGHT /= np.linalg.norm(KEY_LIGHT)   # toward the light: left, front (the camera side), up


def catenary_points(A, B, L, n=40):
    """Points along an inextensible thread of length L hanging between A and B (world, z up). Straight
    when L <= chord. The catenary z = a cosh((x - x0)/a) + c in the vertical plane through A-B: a from
    2 a sinh(h / 2a) = sqrt(L^2 - v^2) (brentq), then x0, c from the endpoints (03 confirms the form)."""
    A = np.asarray(A, float); B = np.asarray(B, float)
    d = B - A; v = d[2]; hvec = d.copy(); hvec[2] = 0; h = np.linalg.norm(hvec)
    chord = np.linalg.norm(d); s = np.linspace(0, 1, n)
    if L <= chord * 1.0005 or h < 1e-6:
        if h < 1e-6 and L > chord:      # hanging straight down with slack: the thread bows out sideways (a vertical
            ex = (L - chord) / 2          # droop drew as a spike under the fist at the release, 2026-09-12)
            pts = A[None] + s[:, None] * d[None]
            pts[:, 0] += np.sin(np.pi * s) * ex * 0.8
            pts[:, 2] -= np.sin(np.pi * s) * ex * 0.3
            return pts
        return A[None] + s[:, None] * d[None]
    span = np.sqrt(max(L * L - v * v, 1e-12))
    if span <= h * (1 + 1e-6):                  # no sag to speak of: the root is beyond any bracket (crashed the bake, 2026-09-11)
        return A[None] + s[:, None] * d[None]
    f = lambda a: 2 * a * np.sinh(min(h / (2 * a), 700)) - span
    try:
        a = brentq(f, 1e-4, 1e4)
    except ValueError:
        return A[None] + s[:, None] * d[None]
    # x along the horizontal chord from A (x=0) to B (x=h); solve x0 so that z(h) - z(0) = v
    x0 = h / 2 - a * np.arcsinh(v / (2 * a * np.sinh(h / (2 * a))))
    c = A[2] - a * np.cosh((0 - x0) / a)
    x = s * h; z = a * np.cosh((x - x0) / a) + c
    u = hvec / h
    pts = A[None] + x[:, None] * u[None] + (z - A[2])[:, None] * np.array([0, 0, 1.0])[None]
    if h < 0.02 and L > chord + 0.01:     # a loop whose chord runs along the depth axis projects as a vertical spike
        ex = (L - chord) / 2               # (the head string at the release, 2026-09-12): bow it sideways, as a real
        pts[:, 0] += np.sin(np.pi * s) * ex * 0.6 * (1 - h / 0.02)     # slack thread never hangs in one plane
    return pts


class PuppetBase:
    """What both backends share: the figure, the sim arrays, the projection, the sub-sample schedule."""

    def __init__(self, hand, sim, look, scale=2, style="neon", string_px=STRING_PX):
        self.h = hand; self.sim = sim; self.scale = scale; self.style = style; self.string_px = string_px
        self.f = float(hand["f"]) * scale; self.W = int(hand["W"]) * scale; self.H = int(hand["H"]) * scale
        self.cx = self.W / 2.0; self.cy = self.H / 2.0
        p = json.loads(str(sim["params"]))
        self.model = mujoco.MjModel.from_xml_string(pm.build_xml(p)); self.data = mujoco.MjData(self.model)
        self.body_class = {}
        for b in pm.BODIES:
            bid = self.model.body(b).id
            self.body_class[bid] = "head" if b == "head" else ("trunk" if b in ("pelvis", "chest") else "limb")
        self.colours = LOOKS[look]
        self.mocap_ids = [self.model.body(f"pad_{nm}").mocapid[0] for nm, _ in pm.STRINGS]
        self.L = sim["L"]; self.sub = int(sim["sub"]); self.release = int(sim["release"])
        # the npz is lazy: pull the arrays once (each [] on an NpzFile decompresses the whole array)
        self.qpos = sim["qpos"]; self.xpos = sim["xpos"]; self.pad_pos = sim["pad_pos"]; self.site_pos = sim["site_pos"]; self.taut = sim["taut"]
        # the quaternion slices of qpos (the free root, the ball joints), renormalised after a lerp between records
        self.quat_slices = []
        for j in range(self.model.njnt):
            adr = int(self.model.jnt_qposadr[j]); t = int(self.model.jnt_type[j])
            if t == int(mujoco.mjtJoint.mjJNT_FREE): self.quat_slices.append(slice(adr + 3, adr + 7))
            elif t == int(mujoco.mjtJoint.mjJNT_BALL): self.quat_slices.append(slice(adr, adr + 4))
        self.string_site_ids = [self.model.site(s_).id for _, s_ in pm.STRINGS]
        self.max_sub = 32     # motion-blur samples per frame at most (2026-09-12: 8 left stepped ghosts on the 100 px snap-open)

    def project(self, X):
        X = np.asarray(X, float)
        return np.stack([self.cx + self.f * X[..., 0] / X[..., 1], self.cy - self.f * X[..., 2] / X[..., 1]], -1)

    def pose(self, r):
        """Set the figure at record r; a fractional r interpolates between two sim records (positions
        and pads lerped, quaternions lerped on the short arc and renormalised: the records are 1/480 s
        apart, so the arc is tiny) and gives the motion blur more samples than the sim stored."""
        m, d = self.model, self.data
        r0 = int(np.floor(r)); r1 = min(r0 + 1, self.qpos.shape[0] - 1); t = float(r - r0)
        if t < 1e-6 or r1 == r0:
            d.qpos[:] = self.qpos[r0]; pads = self.pad_pos[r0]
        else:
            q0 = self.qpos[r0].astype(np.float64); q1 = self.qpos[r1].astype(np.float64).copy()
            for sl in self.quat_slices:
                if np.dot(q0[sl], q1[sl]) < 0: q1[sl] *= -1
            q = (1 - t) * q0 + t * q1
            for sl in self.quat_slices: q[sl] /= np.linalg.norm(q[sl]) + 1e-12
            d.qpos[:] = q; pads = (1 - t) * self.pad_pos[r0] + t * self.pad_pos[r1]
        for k in range(5): d.mocap_pos[self.mocap_ids[k]] = pads[k]
        mujoco.mj_forward(m, d)
        self._pads = pads; self._taut = self.taut[r0 if t < 0.5 else r1]

    def records(self, i, shutter):
        """The sim records shaded for source frame i: adaptive, one per pixel of motion inside the shutter, up to sub * shutter."""
        r0 = i * self.sub; nsub = max(1, int(round(self.sub * shutter)))
        r1 = min(r0 + nsub, self.qpos.shape[0]) - 1
        move = np.abs(self.project(self.xpos[r1, 1:12]) - self.project(self.xpos[r0, 1:12])).max() / self.scale
        moves = np.abs(self.project(self.site_pos[r1]) - self.project(self.site_pos[r0])).max() / self.scale
        want = int(np.clip(np.ceil(max(move, moves)), 1, self.max_sub))
        return np.linspace(r0, r1, want) if want > 1 else np.array([float(r0)])

    def string_polylines(self, r):
        """The five strings at record r as (points (n,3) world, taut) lists."""
        self.pose(r); pads = self._pads; taut = self._taut
        sites = self.data.site_xpos[self.string_site_ids]
        return [catenary_points(pads[k], sites[k], self.L[k] if not taut[k] else 0.0, n=48) for k in range(5)]


class PuppetRenderer(PuppetBase):
    """The 2026-09-11 CPU path: MuJoCo's own depth + segmentation renders, NumPy shading. Kept as the
    reference the GL backend is checked against, and for the neon style."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        cam = self.model.camera("cam"); self.model.cam_fovy[cam.id] = np.degrees(2 * np.arctan(self.H / 2 / self.f))
        self.model.vis.global_.offwidth = self.W; self.model.vis.global_.offheight = self.H
        self.renderer = mujoco.Renderer(self.model, height=self.H, width=self.W)
        self.geom_body = self.model.geom_bodyid.copy()

    def render_record(self, r):
        """One sim record -> depth (H,W) m, body id map (H,W) (-1 = none)."""
        self.pose(r); d = self.data
        self.renderer.enable_depth_rendering(); self.renderer.update_scene(d, camera="cam"); depth = self.renderer.render().copy(); self.renderer.disable_depth_rendering()
        self.renderer.enable_segmentation_rendering(); self.renderer.update_scene(d, camera="cam"); seg = self.renderer.render(); self.renderer.disable_segmentation_rendering()
        gid = seg[..., 0].astype(np.int32); typ = seg[..., 1]
        body = np.full(gid.shape, -1, np.int32)
        ok = (typ == int(mujoco.mjtObj.mjOBJ_GEOM)) & (gid >= 0)   # int(): comparing against the enum object costs 5.5 s per 8 MP frame (2026-09-11)
        body[ok] = self.geom_body[gid[ok]]
        # the pad bodies carry no geoms (sites are not rendered in segmentation), so only puppet bodies appear
        return depth, body

    def shade(self, depth, body):
        """Shade inside the figure's bounding box only (46 s a frame over the full 2x frame, 2026-09-11)."""
        Hf, Wf = depth.shape
        E_full = np.zeros((Hf, Wf, 3), np.float32); a_full = np.zeros((Hf, Wf), np.float32)
        ys, xs = np.where(body >= 0)
        if len(ys) == 0: return E_full, a_full
        y0, y1 = max(ys.min() - 4, 0), min(ys.max() + 5, Hf); x0, x1 = max(xs.min() - 4, 0), min(xs.max() + 5, Wf)
        depth = depth[y0:y1, x0:x1]; body = body[y0:y1, x0:x1]
        H, W = depth.shape
        mask = body >= 0
        # camera-space positions and normals from the depth (x right, y down, z forward)
        u = (np.arange(x0, x1) - self.cx)[None, :]; v = (np.arange(y0, y1) - self.cy)[:, None]
        z = np.where(mask, depth, np.nan)
        X = u / self.f * z; Y = v / self.f * z
        P = np.stack([X, Y, z], -1)
        # central differences where both neighbours are the same body, one-sided otherwise
        def grad(axis):
            fw = np.roll(P, -1, axis) - P; bw = P - np.roll(P, 1, axis)
            same_f = np.roll(body, -1, axis) == body; same_b = np.roll(body, 1, axis) == body
            g = np.where(same_f[..., None] & same_b[..., None], 0.5 * (fw + bw), np.where(same_f[..., None], fw, bw))
            return g
        gx = grad(1); gy = grad(0)
        n = np.cross(gx, gy); n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-12
        n = np.where(np.isfinite(n), n, 0)
        # the camera-space normal should face the camera (-z); flip the ones that do not
        n[n[..., 2] > 0] *= -1
        view = -P / (np.linalg.norm(P, axis=-1, keepdims=True) + 1e-12)          # toward the camera
        ndv = np.clip(np.sum(n * view, -1), 0, 1)
        l = np.array([KEY_LIGHT[0], -KEY_LIGHT[2], KEY_LIGHT[1]])                   # world (x, y_depth, z_up) -> camera (x, -z, y)
        l = l / np.linalg.norm(l)
        ndl = np.clip(np.sum(n * l[None, None], -1), 0, 1)
        hvec = l[None, None] + view; hvec /= np.linalg.norm(hvec, axis=-1, keepdims=True) + 1e-12
        ndh = np.clip(np.sum(n * hvec, -1), 0, 1)
        # the core: distance to the body's silhouette, normalised by the body's own thickness
        core = np.zeros((H, W), np.float32)
        if self.style != "solid":
            for bid in np.unique(body[mask]):
                bm = (body == bid).astype(np.uint8)
                dt = cv2.distanceTransform(bm, cv2.DIST_L2, 5)
                core[bm > 0] = np.clip(dt[bm > 0] / (dt.max() + 1e-6), 0, 1) ** 0.7
        col = np.zeros((H, W, 3), np.float32)
        for bid, cls in self.body_class.items():
            col[body == bid] = self.colours[cls]
        white = np.ones(3, np.float32)
        if self.style == "solid":
            # an opaque body under a directional key; the edge goes DARK so the silhouette holds against the light wall
            edge = np.clip((1 - ndv - 0.45) / 0.55, 0, 1) ** 1.5           # 0 in the middle, 1 at the grazing silhouette
            E = col * (0.18 + 0.82 * ndl)[..., None] * (1 - 0.55 * edge)[..., None] + (ndh ** 90)[..., None] * 0.35 * (0.5 * col + 0.5 * white)
            E = np.minimum(E, 0.72)                                            # nothing clips to white
        else:
            rim = ((1 - ndv) ** 3)[..., None] * 2.0 * (0.5 * col + 0.5 * white)
            spec = (ndh ** 80)[..., None] * 1.5 * white
            E = col * (0.22 + 0.45 * ndl + 0.45 * core)[..., None] + rim + spec
        E[~mask] = 0
        E_full[y0:y1, x0:x1] = E; a_full[y0:y1, x0:x1] = mask
        return E_full, a_full

    def strings(self, r, E, alpha, depth, body):
        """Draw the five strings into E/alpha at 2x, depth-tested against the figure."""
        H, W = alpha.shape
        col = np.array(self.colours["string"], np.float32)
        a = np.zeros((H, W), np.float32)
        for pts in self.string_polylines(r):
            # world -> camera depth for the test: y_world is the depth
            pix = self.project(pts); zs = pts[:, 1]
            for i in range(len(pts) - 1):
                p0, p1 = pix[i], pix[i + 1]; zmid = 0.5 * (zs[i] + zs[i + 1])
                x, y = int(round(p1[0])), int(round(p1[1]))
                hidden = 0 <= x < W and 0 <= y < H and body[y, x] >= 0 and depth[y, x] < zmid - 0.002
                if hidden: continue
                cv2.line(a, tuple(np.round(p0).astype(int)), tuple(np.round(p1).astype(int)), 1.0, int(round(self.string_px * self.scale)), cv2.LINE_AA)
        ys, xs = np.where(a > 0)
        if len(ys):     # blend inside the strings' box only (the full-frame blend was a quarter of the frame's cost)
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            ab = a[y0:y1, x0:x1, None]
            E[y0:y1, x0:x1] = E[y0:y1, x0:x1] * (1 - ab) + col[None, None, :] * ab
            alpha[y0:y1, x0:x1] = np.maximum(alpha[y0:y1, x0:x1], ab[..., 0])

    def bake_frame(self, i, shutter=0.5):
        """Premultiplied linear RGB + alpha at 1x for source frame i, motion-blurred over the shutter."""
        if i < self.release:      # in the fist: nothing is drawn (the held state would show under the closed fist)
            return np.zeros((self.H // self.scale, self.W // self.scale, 4), np.float32)
        recs = self.records(i, shutter)
        acc = None
        for r in recs:
            depth, body = self.render_record(r)
            E, a = self.shade(depth, body)
            self.strings(r, E, a, depth, body)
            E = E * a[..., None]                       # premultiply
            acc = np.dstack([E, a]) if acc is None else acc + np.dstack([E, a])
        acc /= len(recs)
        return cv2.resize(acc, (self.W // self.scale, self.H // self.scale), interpolation=cv2.INTER_AREA)


# ---- the GPU backend ----------------------------------------------------------------------------
# The shading pass is the CPU `shade()` above, term for term, in GLSL: positions from the depth and the
# pixel's own ray, normals by central differences gated on the body id (one-sided at an edge, zero when
# both neighbours are foreign), the normal flipped to face the camera, the same key light, the same
# solid-style formula. Strings are quads with a 1 px coverage ramp (LINE_AA's look), discarded per
# fragment where the figure is in front by more than 2 mm.
SHADE_FS = """
#version 330
uniform sampler2D g;            // rg = (depth m, body id), id < 0 = nothing
uniform float f;                // focal length in px at this scale
uniform vec2 c;                 // cx, cy (u = index - cx: the CPU convention)
uniform vec3 body_col[24];      // BGR, linear light, by MuJoCo body id
uniform vec3 key;               // toward the light in camera coords (x right, y down, z forward)
uniform ivec2 size;
uniform int style;              // 0 = neon, 1 = solid
uniform sampler2D jfa;          // nearest ID-edge pixel (studio.gl.distance_field), neon only
uniform float thick[24];        // the body's thickness in px at this scale, normalises the core term
out vec4 o;

bool fetch(ivec2 p, out vec3 P, out float id) {
    if (p.x < 0 || p.y < 0 || p.x >= size.x || p.y >= size.y) { P = vec3(0.0); id = -1.0; return false; }
    vec2 t = texelFetch(g, p, 0).rg; id = t.g;
    vec2 uv = vec2(p) - c; P = vec3(uv.x / f * t.r, uv.y / f * t.r, t.r);
    return id >= 0.0;
}

// the CPU grad(): both neighbours the same body -> central; one -> one-sided toward it; none -> backward
// (which is NaN on the CPU when that neighbour is background, and then the normal is zeroed)
bool grad(vec3 P, float id, ivec2 p, ivec2 d, out vec3 gr) {
    vec3 Pf, Pb; float idf, idb;
    bool okf = fetch(p + d, Pf, idf), okb = fetch(p - d, Pb, idb);
    bool sf = okf && idf == id, sb = okb && idb == id;
    if (sf && sb) { gr = 0.5 * ((Pf - P) + (P - Pb)); return true; }
    if (sf) { gr = Pf - P; return true; }
    gr = P - Pb; return okb;
}

void main() {
    ivec2 p = ivec2(gl_FragCoord.xy);
    vec3 P; float id;
    if (!fetch(p, P, id)) { o = vec4(0.0); return; }
    vec3 gx, gy;
    bool vx = grad(P, id, p, ivec2(1, 0), gx), vy = grad(P, id, p, ivec2(0, 1), gy);
    vec3 n = vec3(0.0);
    if (vx && vy) {
        n = cross(gx, gy); float ln = length(n);
        n = (ln > 0.0) ? n / ln : vec3(0.0);
        if (n.z > 0.0) n = -n;
    }
    vec3 view = -normalize(P);
    float ndv = clamp(dot(n, view), 0.0, 1.0);
    float ndl = clamp(dot(n, key), 0.0, 1.0);
    vec3 h = normalize(key + view);
    float ndh = clamp(dot(n, h), 0.0, 1.0);
    int bid = int(id + 0.5);
    vec3 col = body_col[bid];
    if (style == 1) {
        float edge = pow(clamp((1.0 - ndv - 0.45) / 0.55, 0.0, 1.0), 1.5);
        vec3 E = col * (0.18 + 0.82 * ndl) * (1.0 - 0.55 * edge) + pow(ndh, 90.0) * 0.35 * (0.5 * col + 0.5);
        E = min(E, vec3(0.72));
        o = vec4(E, 1.0);
    } else {
        // the CPU neon formula: core = the thickness gradient (distance to the body's edge over its thickness)
        vec2 seed = texelFetch(jfa, p, 0).rg;
        float dist = (seed.x < 0.0) ? 0.0 : length(vec2(p) + 0.5 - seed);
        float core = pow(clamp(dist / max(thick[bid], 1.0), 0.0, 1.0), 0.7);
        // the rim and the specular carry less white than the wall-plate neon did (0.5 -> 0.25 of white in the
        // rim, the specular in the body's own colour): a pure-red boot went pink at its edge (Dennis, 2026-09-12)
        vec3 rim = pow(1.0 - ndv, 3.0) * 2.0 * (0.75 * col + 0.25);
        vec3 spec = pow(ndh, 80.0) * 1.5 * (0.6 * col + 0.4);
        vec3 E = col * (0.22 + 0.45 * ndl + 0.45 * core) + rim + spec;
        o = vec4(E, 1.0);
    }
}
"""

STRING_VS = """
#version 330
uniform vec2 size;
in vec2 in_px;          // image pixel coordinates at this scale (pixel centres at integers, as the CPU draws them)
in float in_depth;      // camera-forward depth of the thread here, m
in float in_s;          // signed distance across the thread, px
out float v_s; out float v_depth;
void main() {
    v_s = in_s; v_depth = in_depth;
    vec2 q = in_px + 0.5;
    gl_Position = vec4(2.0 * q.x / size.x - 1.0, 2.0 * q.y / size.y - 1.0, 0.0, 1.0);
}
"""

STRING_FS = """
#version 330
uniform sampler2D g;
uniform float half_w;   // half the thread width in px at this scale
in float v_s; in float v_depth;
out float o;
void main() {
    vec2 t = texelFetch(g, ivec2(gl_FragCoord.xy), 0).rg;
    if (t.g >= 0.0 && t.r < v_depth - 0.002) discard;        // the figure is in front of the thread
    o = clamp(half_w + 0.5 - abs(v_s), 0.0, 1.0);
}
"""


class PuppetRendererGL(PuppetBase):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        import moderngl
        self.moderngl = moderngl
        self.gl = sgl.GL(); ctx = self.gl.ctx
        W, H = self.W, self.H
        self.P = sgl.pinhole_clip_matrix(self.f, self.cx, self.cy, W, H, near=0.05, far=2.0)
        self.meshes = [(g, bid, self.gl.mesh_vao(v)) for g, bid, v in sgl.mujoco_geom_meshes(self.model)]
        self.g_tex = self.gl.tex(W, H, 2); self.g_fbo = self.gl.fbo([self.g_tex], depth=True)
        self.sh_tex = self.gl.tex(W, H, 4); self.sh_fbo = self.gl.fbo([self.sh_tex])
        self.st_tex = self.gl.tex(W, H, 1); self.st_fbo = self.gl.fbo([self.st_tex])
        self.acc_tex = self.gl.tex(W // self.scale, H // self.scale, 4); self.acc_fbo = self.gl.fbo([self.acc_tex])
        self.shade_prog = self.gl.program(sgl.FULLSCREEN_VS, SHADE_FS); self.shade_vao = self.gl.fullscreen_vao(self.shade_prog)
        self.shade_prog["f"].value = float(self.f); self.shade_prog["c"].value = (float(self.cx), float(self.cy)); self.shade_prog["size"].value = (W, H)
        l = np.array([KEY_LIGHT[0], -KEY_LIGHT[2], KEY_LIGHT[1]]); l = l / np.linalg.norm(l)
        self.shade_prog["key"].value = tuple(float(x) for x in l)
        cols = np.zeros((24, 3), np.float32)
        for bid, cls in self.body_class.items(): cols[bid] = self.colours.get("bodies", {}).get(self.model.body(bid).name, self.colours[cls])
        self.shade_prog["body_col"].write(cols.tobytes())
        self.shade_prog["style"].value = 1 if self.style == "solid" else 0
        # the body's thickness in metres for the core term: a capsule's radius, an ellipsoid's smallest semi-axis
        # (the silhouette's half-width seen from the front), the largest of the body's geoms
        self.body_r = np.zeros(24, np.float32)
        for g in range(self.model.ngeom):
            sz = self.model.geom_size[g]; t = int(self.model.geom_type[g])
            r = float(sz[0]) if t == int(mujoco.mjtGeom.mjGEOM_CAPSULE) else float(np.sort(sz[:3])[0])
            b = int(self.model.geom_bodyid[g]); self.body_r[b] = max(self.body_r[b], r)
        self.str_prog = self.gl.program(STRING_VS, STRING_FS); self.str_prog["size"].value = (float(W), float(H))
        self.str_prog["half_w"].value = float(self.string_px * self.scale / 2)
        self.str_buf = ctx.buffer(reserve=5 * 48 * 6 * 4 * 4)
        self.str_vao = ctx.vertex_array(self.str_prog, [(self.str_buf, "2f 1f 1f", "in_px", "in_depth", "in_s")])
        self.string_col = tuple(float(x) for x in self.colours["string"])

    def string_quads(self, r):
        """Vertex data for the five threads at record r: 6 vertices per segment of (u, v, depth, s)."""
        hw = self.string_px * self.scale / 2 + 1.0          # the thread plus a 1 px ramp on each side
        out = []
        for pts in self.string_polylines(r):
            pix = self.project(pts); z = pts[:, 1]
            p0, p1 = pix[:-1], pix[1:]; d = p1 - p0; ln = np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
            nrm = np.stack([-d[:, 1], d[:, 0]], 1) / ln * hw
            z0, z1 = z[:-1, None], z[1:, None]
            a = np.concatenate([p0 + nrm, z0, np.full_like(z0, hw)], 1); b = np.concatenate([p0 - nrm, z0, np.full_like(z0, -hw)], 1)
            c = np.concatenate([p1 + nrm, z1, np.full_like(z1, hw)], 1); e = np.concatenate([p1 - nrm, z1, np.full_like(z1, -hw)], 1)
            out.append(np.stack([a, b, c, b, e, c], 1).reshape(-1, 4))
        return np.concatenate(out, 0).astype(np.float32)

    def render_record(self, r):
        """One sim record -> (depth, id) at 2x on the GPU (the g-buffer), for the check against MuJoCo's own render."""
        self.pose(r)
        draws = [(vao, sgl.geom_model_matrix(self.data, g), bid) for g, bid, vao in self.meshes]
        self.gl.geometry_pass(self.g_fbo, self.P, draws)

    def read_gbuffer(self):
        g = self.gl.read(self.g_fbo, components=2, dtype="f4")
        return g[..., 0].copy(), np.where(g[..., 1] >= 0, g[..., 1] + 0.5, -1).astype(np.int32)

    def bake_frame(self, i, shutter=0.5):
        if i < self.release:
            return np.zeros((self.H // self.scale, self.W // self.scale, 4), np.float16)
        mgl = self.moderngl; ctx = self.gl.ctx
        recs = self.records(i, shutter)
        self.gl.make_current(); self.acc_fbo.use(); self.acc_fbo.clear(0.0, 0.0, 0.0, 0.0)
        for r in recs:
            self.render_record(r)
            # shade
            if self.style != "solid":
                jfa = self.gl.distance_field(self.g_tex, max_step=128)
                z = self.data.xpos[:, 1]                                   # each body's depth at this (possibly interpolated) record
                thick = np.zeros(24, np.float32); n = min(len(z), 24)
                thick[:n] = self.f * self.body_r[:n] / np.maximum(z[:n], 1e-3)
                self.shade_prog["thick"].write(thick.tobytes())
                jfa.use(1); self.shade_prog["jfa"].value = 1
            self.sh_fbo.use(); ctx.disable(mgl.DEPTH_TEST); ctx.disable(mgl.BLEND)
            self.g_tex.use(0); self.shade_prog["g"].value = 0; self.shade_vao.render(mgl.TRIANGLES)
            # strings: coverage with MAX blending, depth-tested against the g-buffer
            self.st_fbo.use(); self.st_fbo.clear(0.0, 0.0, 0.0, 0.0)
            q = self.string_quads(r); self.str_buf.write(q.tobytes())
            ctx.enable(mgl.BLEND); ctx.blend_func = (mgl.ONE, mgl.ONE); ctx.blend_equation = mgl.MAX
            self.g_tex.use(0); self.str_prog["g"].value = 0
            self.str_vao.render(mgl.TRIANGLES, vertices=len(q))
            ctx.blend_equation = mgl.FUNC_ADD; ctx.disable(mgl.BLEND)
            # accumulate: strings under, premultiply, 2x2 area average, 1/n
            self.gl.accumulate(self.acc_fbo, self.sh_tex, 1.0 / len(recs), self.st_tex, self.string_col)
        return self.gl.read(self.acc_fbo, components=4, dtype="f2")


def wide_blur(img, sigma, down=4):
    """A Gaussian of sigma >= 12 px computed at 1/down resolution and resized back: the same result to
    the eye at a sixteenth of the cost (the black composite's four wide blurs cost 1.4 s a frame at
    full resolution, 2026-09-12)."""
    if sigma < 12:
        return cv2.GaussianBlur(img, (0, 0), sigma)
    H, W = img.shape[:2]
    small = cv2.resize(img, (W // down, H // down), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), sigma / down)
    return cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR)


def clean_matte(matte):
    """Keep the hand-and-arm component only. The wall's dark horizontal line (row ~130 of the plate) came
    through the matte as a soft full-width band (alpha 100-140) and flickered on the black plate around
    1 s (Dennis, 2026-09-12): an opening drops anything thin, the largest component is the arm, a 6 px
    dilation gives the soft edge back, everything else (the band, slivers, the border rows) goes."""
    matte = matte.copy(); matte[:2] = 0; matte[-2:] = 0; matte[:, :2] = 0; matte[:, -2:] = 0   # rembg leaves alpha on the frame's
    hard = (matte > 128).astype(np.uint8)                                                  # border rows: the plate's dark top line showed through and flickered
    opened = cv2.morphologyEx(hard, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(opened, connectivity=8)
    if n < 2: return matte
    keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))   # the mask is applied even with one component: the wall line at
                                                             # row ~130 is a SOFT band (alpha ~100-140 across the width) that
                                                             # never reaches the hard matte (2026-09-12)
    mask = cv2.dilate((lab == keep).astype(np.uint8), np.ones((13, 13), np.uint8))
    return (matte * mask).astype(np.uint8)


def composite_black(plate_bgr, layer, matte, grain_std, bloom=BLOOM, style="neon", hand_gain=1.0, spill=1.0, wall=1.0, spill_hi=1.0):
    """The neon-on-black plate (2026-09-12): the hand isolated on pitch black, the figure behind it, the
    bloom over both (the glow wraps the finger edges), the figure's light on the hand, grain everywhere.
    - The hand's edge is decontaminated against the wall (Smith & Blinn 1996: C = a F + (1 - a) B, so
      F = (C - (1 - a) B) / a, in linear light, B = the plate's median in a ring 4-40 px outside the matte
      per frame): without it the soft edge carries the off-white wall as a halo on black.
    - hand_gain: the hand's exposure in the dark room (1.0 = as shot; item 12 for the day-for-night practice).
    - spill: how much the figure's light lands on the hand: hand * (1 + spill * irradiance), irradiance =
      a wide blur (sigma 40 px) of the UNOCCLUDED layer (the light reaches the fingers whether or not the
      camera sees the figure behind them), scaled so a figure at the fingertips gives ~+30 % at spill 1.
    - spill_hi: the hand's bright parts (nails, knuckles, the lit side) reflect the figure's colours more
      than its dark parts, as a glossy skin would: the hand's luminance above 0.25, squared, times the
      figure's irradiance colour, added on top (Dennis, 2026-09-12: "the white brightness of the hand
      renders the reflection of the doll's colours; the more, the better").
    - wall: the dark wall behind the figure catches its light (2026-09-12, Dennis: the doll's colours
      reflecting in the background): a near pool (sigma 60 px) and a broad one (sigma 180 px) of the
      unoccluded emission, dim, under the figure and the hand; 0 = pitch black."""
    # every array float32 and every full-frame pass counted: the first version cost 1.45 s a frame in
    # float64 temporaries, a full-frame exp for the shoulder and a fresh 6 M-sample noise draw (2026-09-12)
    matte = clean_matte(matte)
    a = matte.astype(np.float32)[..., None] * np.float32(1 / 255.0)
    C = srgb8_to_lin(plate_bgr); L = np.asarray(layer, dtype=np.float32)
    outside = (matte == 0).astype(np.uint8); dist = cv2.distanceTransform(outside, cv2.DIST_L2, 5)
    ring = (dist > 4) & (dist < 40)
    B = (np.median(C[ring], axis=0) if ring.sum() > 100 else np.median(C[matte == 0], axis=0)).astype(np.float32)
    hand = C * a                                                   # premultiplied; the soft band is decontaminated below
    band = (matte > 0) & (matte < 255)
    if band.any():
        ab = a[band]; hand[band] = np.clip((C[band] - (1 - ab) * B[None]) / np.maximum(ab, np.float32(1e-3)), 0, 1) * ab
    if hand_gain != 1.0: hand *= np.float32(hand_gain)
    E = L[..., :3] * (1 - a)                                       # the figure where the hand is not
    # the figure's light on the hand. Physically the irradiance of a 15 cm emitter 5-30 cm away is a few
    # percent of the hand's exposure and invisible (a sigma-40 blur x 6 read as nothing at spill 5, 2026-09-12);
    # Dennis wants the reflection strong ("the more, the better"), so the light field is a wide blur of the
    # emission NORMALISED to its own peak (0..1 over the frame, the fingertips near the figure at 0.3-0.6)
    # and its chromaticity tints the hand: reflected = hand * (1 + spill * field * tint) + gloss.
    field = wide_blur(L[..., :3], 60); field += wide_blur(L[..., :3], 200)
    lum = 0.114 * field[..., 0] + 0.587 * field[..., 1] + 0.299 * field[..., 2]
    tint = field / (lum[..., None] + 1e-6)                                        # the colour direction, luminance 1
    tint[lum < 1e-5] = 1.0
    # the strength by distance to the figure, 1 / (1 + (d / reach)^2): a Gaussian field was 0.5-6 % of its
    # peak on the hand (the figure hangs 100-800 px below the fingertips), invisible at any spill
    far = (L[..., 3] < 0.05).astype(np.uint8)
    dist = cv2.distanceTransform(far, cv2.DIST_L2, 5) if far.min() == 0 else np.full(far.shape, 1e4, np.float32)
    strength = (1.0 / (1.0 + (dist / np.float32(SPILL_REACH)) ** 2))[..., None].astype(np.float32)
    if spill_hi > 0:                                               # the glossy read: bright skin mirrors the figure's colour
        Y = 0.114 * hand[..., 0] + 0.587 * hand[..., 1] + 0.299 * hand[..., 2]
        hi = np.clip((Y - 0.25) / 0.45, 0, 1) ** 2
        gloss = tint * strength * hi[..., None]; gloss *= np.float32(0.35 * spill_hi)
    hand *= 1 + np.float32(spill) * strength * tint
    if spill_hi > 0: hand += gloss
    out = hand; out += E
    if wall > 0:
        src = L[..., :3]
        pool = wide_blur(src, 60); pool *= np.float32(0.35 * wall); pool += np.float32(0.25 * wall) * wide_blur(src, 180)
        pool *= (1 - a) * (1 - L[..., 3:4] * (1 - a)); out += pool
    for sigma, w in bloom:
        g = wide_blur(E, sigma); g *= np.float32(w); out += g
    if style == "neon":                                            # the shoulder only where it bites
        hi = out > 0.8
        if hi.any(): out[hi] = 0.8 + 0.2 * (1 - np.exp(-(out[hi] - 0.8) / 0.2))
    img = lin_to_srgb(out)
    if grain_std > 0:      # on a black plate the grain is added in sRGB, at the plate's own 8-bit high-pass std: a linear
        img += _grain(img.shape, grain_std, int(float(L[..., 3].sum()) % 8))   # std mapped near the wall's level is +-8 levels at black
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


_GRAIN = {}


def _grain(shape, std, k):
    """A bank of 8 fixed noise frames (a fresh 6 M-sample draw cost 0.2 s a frame); which one a frame
    gets follows the layer, so the grain still changes frame to frame."""
    key = (shape, std)
    if key not in _GRAIN:
        rng = np.random.default_rng(1234)
        _GRAIN[key] = [rng.normal(0, std, shape).astype(np.float32) for _ in range(8)]
    return _GRAIN[key][k % 8]


def composite(plate_bgr, layer, matte, grain_std, bloom=BLOOM, style="neon", plate="wall", hand_gain=1.0, spill=1.0, wall=1.0, spill_hi=1.0):
    """plate uint8 BGR, layer (H,W,4) premultiplied linear (float16 or float32), matte uint8 (255 = hand).
    Works inside the figure's bounding box (plus the widest bloom's 3 sigma); the plate passes through
    untouched elsewhere (the full-frame composite cost 0.5 s a frame, 2026-09-12). plate="black": the
    isolated hand on black (composite_black)."""
    if plate == "black":
        return composite_black(plate_bgr, layer, matte, grain_std, bloom, style, hand_gain, spill, wall, spill_hi)
    a_any = np.asarray(layer[..., 3]) > 0
    ys, xs = np.nonzero(a_any.any(1)), np.nonzero(a_any.any(0))
    if len(ys[0]) == 0:
        return plate_bgr.copy()
    pad = int(3 * max(s for s, _ in bloom)) + 2
    H, W = a_any.shape
    y0, y1 = max(ys[0].min() - pad, 0), min(ys[0].max() + pad + 1, H); x0, x1 = max(xs[0].min() - pad, 0), min(xs[0].max() + pad + 1, W)
    P = srgb8_to_lin(plate_bgr[y0:y1, x0:x1])
    L = np.asarray(layer[y0:y1, x0:x1], dtype=np.float32)
    m = matte[y0:y1, x0:x1].astype(np.float32)[..., None] / 255.0
    E = L[..., :3] * (1 - m); a = L[..., 3:4] * (1 - m)         # the hand is in front of the figure
    out = P * (1 - a) + E
    glow = np.zeros_like(E)
    for sigma, w in bloom:
        glow += w * cv2.GaussianBlur(E, (0, 0), sigma)
    out = out + glow
    if style == "neon":      # shoulder: the hottest core goes white, the colour survives around it
        hi = out > 0.8
        out = np.where(hi, 0.8 + 0.2 * (1 - np.exp(-(out - 0.8) / 0.2)), out)
    if grain_std > 0:
        noise = np.random.default_rng(int(float(L[..., 3].sum()) % 100000)).normal(0, grain_std, out.shape).astype(np.float32)
        out = out + noise * np.clip(a + glow.max(-1, keepdims=True) * 3, 0, 1)
    res = plate_bgr.copy(); res[y0:y1, x0:x1] = lin_to_srgb8(out)
    return res


def plate_grain(frame, domain="linear"):
    """The plate's high-pass std on the wall: in linear light near the wall's level (the wall composite
    adds grain in linear), or in sRGB units (the black composite adds it after the curve)."""
    g = frame[1200:, :, :].astype(np.float32) / 255.0
    hp = g - cv2.GaussianBlur(g, (0, 0), 2)
    if domain == "srgb": return float(hp.std())
    return float(srgb_to_lin(np.array(0.9)) - srgb_to_lin(np.array(0.9 - hp.std())))   # the std mapped through the curve near the wall's level


def bake_key(sim_npz, look, shutter, scale, style, string_px, backend):
    """Hashes only what the bake depends on: the figure, the renderer classes and their shaders, the
    studio GL module (not this file's docstring or the composite-time bloom, which forced a rebake on
    every doc edit before 2026-09-12)."""
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "puppet_model.py"), "rb").read()
    src += inspect.getsource(PuppetBase).encode() + inspect.getsource(catenary_points).encode()
    if backend == "gl":
        src += inspect.getsource(PuppetRendererGL).encode() + SHADE_FS.encode() + STRING_VS.encode() + STRING_FS.encode() + inspect.getsource(sgl).encode()
    else:
        src += inspect.getsource(PuppetRenderer).encode()
    return dict(sim=[os.path.getsize(sim_npz), os.path.getmtime(sim_npz)], look=look, shutter=shutter, scale=scale,
                code=hashlib.md5(src).hexdigest(), colours=LOOKS[look], style=style, string_px=string_px, backend=backend)


def main():
    video, hand_npz, sim_npz, matte_npy, out = sys.argv[1:6]
    kw = dict(a.split("=", 1) for a in sys.argv[6:])
    look = kw.get("look", "red"); bake = kw.get("bake"); shutter = float(kw.get("shutter", 0.5)); scale = int(kw.get("scale", 2))
    style = kw.get("style", "solid"); string_px = float(kw.get("string_px", STRING_PX))
    backend = kw.get("backend", "gl")
    bloom = BLOOM_SOLID if style == "solid" else BLOOM
    plate = kw.get("plate", "wall"); hand_gain = float(kw.get("hand_gain", 1.0)); spill = float(kw.get("spill", 1.0)); wall = float(kw.get("wall", 1.0)); spill_hi = float(kw.get("spill_hi", 1.0))
    comp = lambda fr, lay, m: composite(fr, lay, m, grain, bloom, style, plate, hand_gain, spill, wall, spill_hi)
    preview = [int(x) for x in kw["preview"].split(",")] if "preview" in kw else None
    t0_, t1_ = (int(x) for x in kw.get("trim", "0,267").split(","))
    hand = np.load(hand_npz); sim = np.load(sim_npz); matte = np.load(matte_npy, mmap_mode="r")
    cap = cv2.VideoCapture(video); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    R = (PuppetRendererGL if backend == "gl" else PuppetRenderer)(hand, sim, look, scale, style, string_px)
    print(f"backend {backend}, look {look}, style {style}, plate {plate}" + (f" (hand_gain {hand_gain}, spill {spill}, spill_hi {spill_hi}, wall {wall})" if plate == "black" else ""))
    # the alignment check: the pads projected through the render camera vs the tracked tips (should agree to the pad offset, a few px)
    r = int(sim["ref"]) * R.sub
    pp = R.project(R.pad_pos[r]) / scale; tips = hand["tips_img"][int(sim["ref"])]
    print(f"alignment at the reference frame: pads projected vs tracked tips, mean {np.linalg.norm(pp - tips, axis=1).mean():.1f} px (the 7 mm pad offset is ~{0.007 * float(hand['f']) / float(hand['z_hand']):.0f} px)")
    ok, f0 = cap.read(); grain = plate_grain(f0, "srgb" if plate == "black" else "linear"); cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    print(f"plate grain std ({'sRGB' if plate == 'black' else 'linear'}): {grain:.4f}")

    if bake:
        bake_from = int(kw.get("bake_from", 0))        # resume a crashed bake at this frame (the file keeps the earlier frames)
        bake_to = int(kw.get("bake_to", n))            # ... and stop after this frame: re-bake a range after a local fix
        c = BakeCache(bake, bake_key(sim_npz, look, shutter, scale, style, string_px, backend), (n, H, W, 4), np.float16, resume_from=bake_from)
        if c.valid:
            print("bake valid, reading back")
        else:
            print(f"baking the puppet layer (look {look}, {c.reason})", f"from frame {bake_from}" if bake_from else "")
            t0 = time.time()
            for i in range(bake_from, min(bake_to, n)):
                c.mm[i] = R.bake_frame(i, shutter)
                if i % 20 == 0: print(f"  bake {i}/{n} {(time.time() - t0) / (i - bake_from + 1):.3f} s/frame", flush=True)
            c.commit(); print(f"bake done: {min(bake_to, n) - bake_from} frames in {time.time() - t0:.1f} s")
        get_layer = lambda i: c.mm[i]
    else:
        get_layer = lambda i: R.bake_frame(i, shutter)

    if preview:
        tiles = []
        for i in preview:
            cap.set(cv2.CAP_PROP_POS_FRAMES, i); ok, fr = cap.read()
            img = comp(fr, get_layer(i), np.asarray(matte[i]))
            cv2.imwrite(out.replace(".mp4", f"_f{i:03d}.png"), img)
            t = cv2.resize(img, (W // 3, H // 3)); cv2.putText(t, str(i), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3); tiles.append(t)
        rows = [np.hstack(tiles[j:j + 4]) for j in range(0, len(tiles), 4)]
        w = max(r.shape[1] for r in rows)      # pad the short last row (it used to crop every row to it and lose tiles)
        rows = [np.hstack([r, np.zeros((r.shape[0], w - r.shape[1], 3), np.uint8)]) if r.shape[1] < w else r for r in rows]
        cv2.imwrite(out.replace(".mp4", "_sheet.png"), np.vstack(rows))
        print("preview written"); return

    enc = RawWriter(out, W, H, 30, audio_from=video)
    cap.set(cv2.CAP_PROP_POS_FRAMES, t0_); t0 = time.time()
    for i in range(t0_, min(t1_, n)):
        ok, fr = cap.read()
        if not ok: break
        enc.write(comp(fr, get_layer(i), np.asarray(matte[i])))
        if i % 60 == 0: print(f"  frame {i} {(time.time() - t0) / (i - t0_ + 1):.3f} s/frame", flush=True)
    rc = enc.close(); print(f"wrote {out} ffmpeg exit {rc}: {enc.n} frames in {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
