"""The hand in 3D: five fingertip pads in a gravity-aligned world frame, from MediaPipe landmarks.

    python hand_to_3d.py <master.mp4> <hands_mp.npz> <out.npz> [f=1600] [hand_len=0.193] [pad=0.007] [seam=610,130]

Every number below says where it comes from (CLAUDE.md, model code). The one free scale is the hand
length norm: nothing in the picture measures the hand (hand/PLAN.md decision 5), so the depth in
metres and the puppet's size in centimetres scale together with it; ranked in hand/PUPPET-MODEL.md.

Pipeline (each step prints what a reviewer would check):
  1. Camera: the shot is handheld. The only fixed features are the wall/ceiling line at the top (its
     height at the left and right edges gives the roll and the vertical drift; measured 2026-09-11:
     170 -> 112 px over the shot, tilt -0.96 -> -0.12 deg) and a seam in that line (default x=610,
     y=130 on frame 0) that gives the horizontal drift by template matching. Both are measured and
     printed, and neither is compensated: the world frame IS the camera frame at every instant. A
     camera translating a few cm over seconds is a spurious anchor acceleration of ~0.05 m/s^2 on a
     9.8 m/s^2 problem, the wall has no texture that could show a shifted render, and the seam track
     itself jumps 25 px between frames (2026-09-11), so compensating it would add error, not remove
     it. What the camera's motion does change is gravity's direction in the image: the roll (under
     1.2 deg here) is written out and the simulation tilts gravity by it.
  2. Pose: MediaPipe's world landmarks (metric, canonical scale, origin at the hand centre; Zhang
     et al. 2020) are scaled so the median wrist-to-middle-tip length equals the male hand length
     norm, then solved by PnP against the image landmarks with a pinhole camera (f in px, principal
     point at the frame centre). The world landmarks are not rigid frame to frame (wrist-to-knuckle
     5.4-10.4 cm before scaling on this shot) and a hand with the fingers curled looks smaller, so
     the PnP depth jumped 10 cm in half a second whenever the fingers closed (2026-09-11). The arm
     does not move in this shot, so the hand's depth is HELD at the median PnP depth over the open
     phases (frames 42-160), and each landmark's depth is that plus its relative depth from the
     rotated, scaled shape (clipped to +-4 cm, smoothed over 15 frames); its lateral position is the
     back-projected image landmark at that depth, so the string leaves exactly the tracked tip.
  3. Pads: the string leaves the palmar pad of each tip, which the camera cannot see (the back of the
     hand faces it). Pad = tip landmark + pad * palmar normal, the normal from the palm's plane
     (wrist, index MCP, pinky MCP), signed to point away from the camera; checked on every frame.
  4. The closed fist (no detection, frames 28-40 here) is bridged with a cubic Hermite in 3D; the
     puppet is behind the fist then and the strings are slack, so only continuity matters.
  5. Smoothing: Savitzky-Golay, window 7 (0.23 s), order 2, zero phase; it keeps the snap-open peak
     (checked by printing the largest residual on the snap frames).
Outputs: pads (n,5,3) world metres [x right, y away from the camera, z up]; tips_img (n,5,2) px;
palm (n,3); normal (n,3); pan (n,2) px; roll (n) deg; f, cx, cy, scale; valid (n) bool.
"""
import sys, json
import numpy as np
import cv2
from scipy.signal import savgol_filter
from scipy.interpolate import CubicHermiteSpline

TIPS = [4, 8, 12, 16, 20]
TIP_NAMES = ["thumb", "index", "middle", "ring", "pinky"]


def cam_track(video, seam):
    """Pan (dx, dy) of the camera per frame from a 90x50 patch around the top line's seam, and the
    roll from the line's height at the frame's left and right edges."""
    cap = cv2.VideoCapture(video)
    ok, f0 = cap.read(); g0 = cv2.cvtColor(f0, cv2.COLOR_BGR2GRAY)
    H, W = g0.shape
    sx, sy = seam
    tpl = g0[sy - 25:sy + 25, sx - 45:sx + 45]
    pans = [(0.0, 0.0)]; rolls = []
    def line_roll(g):
        ys = []
        for c0, c1 in [(0, 120), (W - 120, W)]:
            prof = g[:400, c0:c1].astype(np.float32).mean(1)
            d = np.abs(np.diff(cv2.GaussianBlur(prof.reshape(-1, 1), (1, 7), 2).ravel()))
            k = int(np.argmax(d[20:380])) + 20
            a, b, c = d[k - 1], d[k], d[k + 1]; ys.append(k + 0.5 * (a - c) / (a - 2 * b + c + 1e-9))
        return np.degrees(np.arctan2(ys[1] - ys[0], W - 120))
    rolls.append(line_roll(g0))
    while True:
        ok, f = cap.read()
        if not ok: break
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        y0, y1 = max(0, sy - 120), sy + 120; x0, x1 = max(0, sx - 200), sx + 200
        r = cv2.matchTemplate(g[y0:y1, x0:x1], tpl, cv2.TM_CCOEFF_NORMED)
        _, mx, _, loc = cv2.minMaxLoc(r)
        px, py = loc[0] + x0 + 45, loc[1] + y0 + 25
        # sub-pixel by a parabola on the response peak
        lx, ly = loc
        if 0 < lx < r.shape[1] - 1: px += 0.5 * (r[ly, lx - 1] - r[ly, lx + 1]) / (r[ly, lx - 1] - 2 * r[ly, lx] + r[ly, lx + 1] + 1e-9)
        if 0 < ly < r.shape[0] - 1: py += 0.5 * (r[ly - 1, lx] - r[ly + 1, lx]) / (r[ly - 1, lx] - 2 * r[ly, lx] + r[ly + 1, lx] + 1e-9)
        pans.append((px - sx, py - sy) if mx > 0.5 else pans[-1])
        rolls.append(line_roll(g))
    return np.array(pans, np.float64), np.array(rolls, np.float64), (W, H)


def main():
    video, npz, out = sys.argv[1:4]
    kw = dict(a.split("=", 1) for a in sys.argv[4:])
    f = float(kw.get("f", 1600))            # px at 1080x1920: references/marionette/05-camera-light-compositing.md, derived from
                                            # Apple's 26 mm-equivalent spec, the 1.9 um pixel pitch and the ~10 % stabilisation crop
                                            # (1441 px uncropped); +-50 px per an iPhone 14 checkerboard calibration (ISPRS 2025).
                                            # The puppet's size relative to the hand does not depend on it; ranked in PUPPET-MODEL.md
    hand_len = float(kw.get("hand_len", 0.193))   # m, male hand length (wrist crease to middle tip): from memory of ANSUR II (~19.3 cm)
                                                  # until references/marionette/data/04-hand-norms.csv confirms; the one free scale
    pad = float(kw.get("pad", 0.007))       # m, tip landmark to the palmar pad: about half a fingertip's depth; cosmetic, sets where
                                            # the string emerges behind the finger
    seam = tuple(int(x) for x in kw.get("seam", "610,130").split(","))
    d = np.load(npz)
    img = d["img"][:, 0].astype(np.float64); world = d["world"][:, 0].astype(np.float64)
    n = img.shape[0]; W, H = int(d["width"]), int(d["height"])
    valid = ~np.isnan(img[:, 0, 0])
    print(f"frames {n}, hand on {valid.sum()}, missing {np.where(~valid)[0].tolist()}")

    pan, roll, _ = cam_track(video, seam)
    print(f"camera pan px: dx {pan[:,0].min():.1f}..{pan[:,0].max():.1f}, dy {pan[:,1].min():.1f}..{pan[:,1].max():.1f}; "
          f"roll deg {roll.min():.2f}..{roll.max():.2f}")
    pan_s = np.zeros_like(pan); roll_s = savgol_filter(roll, 15, 2)   # pan measured, not compensated (see the docstring)

    # --- scale: the world landmarks' hand length -> the norm
    wl = np.linalg.norm(world[:, 12] - world[:, 0], axis=1)
    scale = hand_len / np.nanmedian(wl)
    print(f"world hand length median {np.nanmedian(wl)*100:.1f} cm -> scale {scale:.3f} to the {hand_len*100:.1f} cm norm")

    K = np.array([[f, 0, W / 2.0], [0, f, H / 2.0], [0, 0, 1]])
    pix = img[..., :2] * [W, H]
    pix_w = pix - pan_s[:, None, :]           # de-panned: the world frame is frame 0's camera
    X = np.full((n, 21, 3), np.nan); err = np.full(n, np.nan); zfp = np.full(n, np.nan)
    rvec = tvec = None
    for i in range(n):
        if not valid[i]: continue
        obj = (world[i] * scale).astype(np.float64)
        # SQPnP (Terzakis & Lourakis 2020): the hand's world landmarks are close to coplanar and the
        # iterative solver's DLT start diverged on them (depth 0, 2768 px error; 2026-09-11)
        ok, rvec, tvec = cv2.solvePnP(obj, np.ascontiguousarray(pix_w[i]), K, None, flags=cv2.SOLVEPNP_SQPNP)
        ok, rvec, tvec = cv2.solvePnP(obj, np.ascontiguousarray(pix_w[i]), K, None, rvec, tvec, useExtrinsicGuess=True, flags=cv2.SOLVEPNP_ITERATIVE)
        R, _ = cv2.Rodrigues(rvec)
        Xi = obj @ R.T + tvec.ravel()
        proj, _ = cv2.projectPoints(obj, rvec, tvec, K, None)
        err[i] = np.linalg.norm(proj[:, 0] - pix_w[i], axis=1).mean()
        X[i] = Xi
        # cross-check: depth from the image hand length as if fronto-parallel
        zfp[i] = f * hand_len / np.linalg.norm(pix_w[i, 12] - pix_w[i, 0])
    zc = X[:, :, 2].mean(1)
    print(f"PnP reprojection error px: median {np.nanmedian(err):.1f}, max {np.nanmax(err):.1f}")
    print(f"hand depth m: PnP median {np.nanmedian(zc):.3f} ({np.nanmin(zc):.3f}..{np.nanmax(zc):.3f}); fronto-parallel cross-check median {np.nanmedian(zfp):.3f}")
    z_hand = float(np.nanmedian(zc[42:161]))          # held constant: the arm does not move (docstring, step 2)
    rel = X[:, :, 2] - zc[:, None]                    # each landmark's depth relative to the hand centre, from the rotated shape
    rel = np.clip(rel, -0.04, 0.04)
    relf = rel.copy()
    for k in range(21):                               # smooth over 15 frames, gaps interpolated first
        v = ~np.isnan(rel[:, k]); relf[:, k] = np.interp(np.arange(n), np.where(v)[0], rel[v, k])
    relf = savgol_filter(relf, 15, 2, axis=0)
    Zl = z_hand + relf                                # (n, 21) depth per landmark
    Xbp = np.stack([(pix_w[..., 0] - W / 2.0) / f * Zl, (pix_w[..., 1] - H / 2.0) / f * Zl, Zl], axis=-1)
    Xbp[~valid] = np.nan
    print(f"hand depth held at {z_hand:.3f} m (median PnP over frames 42-160); tips' relative depth range {np.nanmin(relf[:, TIPS])*100:+.1f}..{np.nanmax(relf[:, TIPS])*100:+.1f} cm")
    X = Xbp

    # --- palmar normal: the palm plane (wrist 0, index MCP 5, pinky MCP 17), pointing away from the camera
    nrm = np.cross(X[:, 5] - X[:, 0], X[:, 17] - X[:, 0])
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12
    flip = nrm[:, 2] < 0
    nrm[flip] *= -1
    print(f"palmar normal: z-component (away from camera) median {np.nanmedian(nrm[:,2]):.2f}; frames whose raw normal faced the camera: {int(np.nansum(flip))} of {valid.sum()} (all should agree on a back-of-hand shot)")
    tips = X[:, TIPS] + pad * nrm[:, None, :]
    palm = X[:, [0, 5, 9, 13, 17]].mean(1)

    # --- bridge the fist and smooth (in the camera frame, metres)
    t = np.arange(n, dtype=np.float64)
    def bridge(arr):
        a = arr.copy()
        for k in range(a.shape[1]):
            v = ~np.isnan(a[:, k]); tv = t[v]; yv = a[v, k]
            dy = np.gradient(yv, tv)
            a[~v, k] = CubicHermiteSpline(tv, yv, dy)(t[~v])
        return a
    tips_b = bridge(tips.reshape(n, -1)).reshape(n, 5, 3)
    palm_b = bridge(palm); nrm_b = bridge(nrm); nrm_b /= np.linalg.norm(nrm_b, axis=1, keepdims=True)
    from scipy.ndimage import median_filter
    jump = np.linalg.norm(np.diff(tips_b, axis=0), axis=2) * 30   # m/s per tip
    big = np.argwhere(jump > 1.5)
    print(f"tip jumps over 1.5 m/s (tracker spikes), removed by a 5-frame median: {[(int(a), TIP_NAMES[b], round(float(jump[a, b]), 2)) for a, b in big][:12]}")
    tips_m = median_filter(tips_b, size=(5, 1, 1), mode='nearest'); palm_m = median_filter(palm_b, size=(5, 1), mode='nearest')
    tips_s = savgol_filter(tips_m, 7, 2, axis=0); palm_s = savgol_filter(palm_m, 7, 2, axis=0)
    res = np.linalg.norm(tips_s - tips_b, axis=2)
    j = int(np.nanargmax(res)); print(f"smoothing residual: max {res.max()*1000:.1f} mm at frame {j // 5} ({TIP_NAMES[j % 5]}); median {np.median(res)*1000:.2f} mm; on the snap frames 41-44 max {res[41:45].max()*1000:.1f} mm")

    # --- to the world frame: x right, y = depth (away from the camera), z = up; gravity gets the roll in the renderer
    def to_world(a): return np.stack([a[..., 0], a[..., 2], -a[..., 1]], axis=-1)
    pads_w = to_world(tips_s); palm_w = to_world(palm_s); nrm_w = to_world(nrm_b)

    # --- what the plan's table said, in metres now: the spread and the tips' height per phase
    spread = np.linalg.norm(pads_w[:, 0] - pads_w[:, 4], axis=1)
    for a, b, tag in [(0, 15, "open"), (42, 54, "snap-open"), (60, 66, "together"), (72, 156, "wide, drifting down"), (162, 168, "together"), (258, 266, "closing")]:
        z = pads_w[a:b + 1, :, 2].mean()
        print(f"  frames {a:3d}-{b:3d} {tag:20s} thumb-pinky {spread[a:b+1].mean()*100:5.1f} cm, tips' mean height {z*100:6.1f} cm (world z, camera origin), depth {pads_w[a:b+1,:,1].mean():.3f} m")
    vfall = np.linalg.norm(np.diff(pads_w[41:45], axis=0), axis=2).max() * 30
    print(f"fastest pad speed at the snap-open (frames 41-44): {vfall:.2f} m/s")

    np.savez_compressed(out, pads=pads_w, palm=palm_w, normal=nrm_w, tips_img=pix[:, TIPS], valid=valid, pan=pan_s, roll=roll_s,
                        f=f, cx=W / 2.0, cy=H / 2.0, scale=scale, hand_len=hand_len, pad=pad, depth_pnp=zc, depth_fp=zfp, err=err, z_hand=z_hand,
                        landmarks_cam=X, W=W, H=H)
    with open(out.replace(".npz", ".json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"f_px": f, "hand_len_m": hand_len, "scale": float(scale), "pad_m": pad, "depth_median_m": float(np.nanmedian(zc)),
                   "depth_fp_median_m": float(np.nanmedian(zfp)), "reproj_err_px_median": float(np.nanmedian(err)),
                   "pan_px_range": [pan[:, 0].min(), pan[:, 0].max(), pan[:, 1].min(), pan[:, 1].max()],
                   "roll_deg_range": [float(roll.min()), float(roll.max())], "missing_frames": np.where(~valid)[0].tolist()}, fh, indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
