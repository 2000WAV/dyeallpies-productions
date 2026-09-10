"""
3D reconstruction of the push-up from one floor-level phone at the head end (IMG_6107, 2026-09-09).

The camera looks along the body, so the picture cannot measure height directly: a shoulder that
drops toward the floor also comes toward the lens, and both read as "lower in the frame". What
the picture does fix is a RAY per landmark. Three things close the geometry without a second
camera:

  1. the WRISTS are on the floor. Their rays meet the floor plane (known from the room's two
     vanishing points: pushup/work/floor_fit.py -> K, R) at a point whose position is in units of
     the camera height h_c;
  2. the ARM SEGMENT LENGTHS are known for this person: forearm (wrist to elbow landmark) 28.4 /
     27.0 cm and elbow-to-shoulder landmark 26.6 / 25.2 cm (left / right), measured at the plumb
     dead hang of pull-up set #3 in its rectified doorway plane (pullup/work3/model_v43.txt,
     GEOMETRY lines; the same landmarks, the same person). With the wrist fixed, the elbow lies on
     a circle for every candidate shoulder position along the shoulder's ray, and only one distance
     along that ray puts the elbow's circle on the elbow's own ray. The shoulder's distance from
     the camera - and with it its height above the floor, the elbow's height, the elbow angle and
     the horizontal levers the inverse dynamics needs - follows from the arm's shape, not from
     MediaPipe's 3D angle (which was the pull-up model's weakest input, MUSCLE-MODEL.md section 5);
  3. one absolute length sets h_c: by default the landmark shoulder width, 38.2 cm arms-down in set
     #3's rectified plane (the arms-down width; 31.7 cm with the arms overhead, 26.4 cm hanging),
     applied at the TOP of the reps where the shoulders are square to the camera; a tape measure
     of the hand spacing (hand_cm=) or a plank width (plank_cm=) replaces it when Dennis measures
     one. Everything that follows scales with h_c, so the scale is printed as an error bar.

World frame: origin at the camera, X to the camera's right, Y forward along the corridor, Z up;
the floor is the plane Z = -h_c. A pixel p maps to the ray s * R^T K^-1 [p, 1].

    reconstruct(P_img, V, cam, lengths, hc) -> dict of per-frame arrays (metres, floor = 0)
    python pushup_recon.py pushup/work/pose_mp.npz pushup/work/cam.npz [hc=0.05]
"""
import sys
import numpy as np

L_SH, R_SH = 11, 12; L_EL, R_EL = 13, 14; L_WR, R_WR = 15, 16
L_HIP, R_HIP = 23, 24; L_KNEE, R_KNEE = 25, 26; L_ANK, R_ANK = 27, 28
NOSE = 0; L_EAR, R_EAR = 7, 8

# Dennis's segment lengths, landmark to landmark, from pull-up set #3's dead hang (rectified plane,
# pullup/work3/model_v43.txt GEOMETRY): the arm hangs plumb there, so the picture shows the whole length.
LENGTHS = dict(fore_l=0.284, fore_r=0.270, up_l=0.266, up_r=0.252,
               shoulder_w=0.382,     # landmark shoulder width, arms down (set #3, 57-58.6 s window)
               hip_w=0.190,          # landmark hip width (set #3, reach window)
               trunk=0.587)          # shoulder-mid to hip-mid, arms down (set #3)
WRIST_Z = 0.035      # m, the wrist landmark above the floor with the palm flat (assumed; ranked in PUSHUP-MODEL.md)
ANKLE_Z = 0.039 * 1.88   # lateral malleolus height / stature 0.039 (Drillis & Contini 1966) x 188 cm


def rays(P_img, K, R):
    """Unit ray directions in WORLD coordinates for image points P_img (..., 2)."""
    Ki = np.linalg.inv(K)
    p = np.concatenate([P_img, np.ones(P_img.shape[:-1] + (1,))], axis=-1)
    d = p @ Ki.T @ R          # (Ki p) in camera coords, then R^T: world = R^T cam, as a row vector p Ki^T R
    return d / np.linalg.norm(d, axis=-1, keepdims=True)


def project(X, K, R):
    """World points (..., 3) -> pixels (..., 2)."""
    xc = X @ R.T              # camera coords = R world (R columns = world axes in camera coords)
    z = np.maximum(xc[..., 2:3], 1e-6)
    uv = xc[..., :2] / z
    return uv * np.array([K[0, 0], K[1, 1]]) + np.array([K[0, 2], K[1, 2]])


def plane_hit(d, z):
    """Point on the ray s d with Z = z (z < 0 below the camera)."""
    s = z / np.where(np.abs(d[..., 2]) < 1e-6, -1e-6, d[..., 2])
    return s[..., None] * d


def elbow_error(w, S, d_e, e_obs, L_fore, L_up, K, R, n_phi=120):
    """For candidate shoulder positions S (n, 3) with the wrist at w (3,), the elbow lies on the circle
    |E - w| = L_fore, |E - S| = L_up. Returns, per candidate, the smallest reprojection error (px) of a
    point of that circle against the observed elbow pixel e_obs, and that point."""
    v = S - w[None, :]; dist = np.linalg.norm(v, axis=1)
    a = (L_fore ** 2 - L_up ** 2 + dist ** 2) / (2 * dist)
    r2 = L_fore ** 2 - a ** 2
    feasible = r2 > 1e-6
    r = np.sqrt(np.maximum(r2, 0))
    u = v / dist[:, None]
    C = w[None, :] + a[:, None] * u
    tmp = np.where(np.abs(u[:, 2:3]) < 0.9, np.array([[0, 0, 1.0]]), np.array([[1.0, 0, 0]]))
    e1 = np.cross(u, tmp); e1 /= np.linalg.norm(e1, axis=1, keepdims=True)
    e2 = np.cross(u, e1)
    phi = np.linspace(0, 2 * np.pi, n_phi, endpoint=False)
    E = C[:, None, :] + r[:, None, None] * (np.cos(phi)[None, :, None] * e1[:, None, :] + np.sin(phi)[None, :, None] * e2[:, None, :])
    uv = project(E, K, R)
    err = np.linalg.norm(uv - e_obs[None, None, :], axis=-1)
    err[~feasible] = 1e6
    k = np.argmin(err, axis=1)
    return err[np.arange(len(S)), k], E[np.arange(len(S)), k]


def reconstruct(P_img, V, cam, lengths=LENGTHS, hc=0.05, ok=None, verbose=True, hip_w=None, trunk=None, hip_depth=None, sh_w_ref=None):
    """The chain: hips (width scale, no h_c) -> shoulders (trunk sphere on their rays, no h_c) ->
    wrists on the floor (h_c) -> elbows (circle from the two arm lengths, picked by the elbow ray).
    Frames with ok=False get NaN shoulders/elbows; the hips are computed on every frame."""
    K = cam["K"]; R = cam["R"]; f = K[0, 0]
    N = len(P_img); z_floor = -hc
    hip_w = hip_w or lengths["hip_w"]; trunk = trunk or lengths["trunk"]
    d = rays(P_img, K, R)
    # ---- hips ----
    px = np.linalg.norm(P_img[:, L_HIP] - P_img[:, R_HIP], axis=1)
    if N > 15:
        from scipy.signal import savgol_filter
        px = savgol_filter(px, 15, 2)
    depth = f * hip_w / np.maximum(px, 1.0) if hip_depth is None else np.asarray(hip_depth, float)
    Ki = np.linalg.inv(K)
    def world_at_depth(pix, z):
        c = np.concatenate([pix, np.ones((N, 1))], axis=1) @ Ki.T
        return (c * z[:, None]) @ R                                 # camera -> world (row form of R^T x)
    Hm = 0.5 * (world_at_depth(P_img[:, L_HIP], depth) + world_at_depth(P_img[:, R_HIP], depth))
    # ---- shoulders on their rays, at the trunk length from the hip midpoint ----
    S3 = np.full((N, 2, 3), np.nan); y_sh = np.full(N, np.nan)
    ok = np.ones(N, bool) if ok is None else ok
    for i in np.where(ok)[0]:
        dl, dr = d[i, L_SH], d[i, R_SH]
        if dl[1] < 1e-3 or dr[1] < 1e-3:
            continue
        if not np.isfinite(Hm[i]).all():
            # the hips are hidden (behind the head at the bottom): the shoulders' own picture width sets
            # their depth, calibrated on the frames where the hips fixed it (sh_w_ref)
            if sh_w_ref is None:
                continue
            wpx = np.linalg.norm(P_img[i, L_SH] - P_img[i, R_SH])
            Y = f * sh_w_ref / max(wpx, 1.0)                    # depth of a fronto-parallel line of that width
            SL = Y / dl[1] * dl; SR = Y / dr[1] * dr
            Y = Y * sh_w_ref / max(np.linalg.norm(SL - SR), 1e-3)   # exact 3D width on the two rays
            y_sh[i] = Y; S3[i, 0] = Y / dl[1] * dl; S3[i, 1] = Y / dr[1] * dr
            continue
        # S_mid(s) with a shared depth Y: S_L = (Y/dl_y) dl, S_R = (Y/dr_y) dr; solve |S_mid - Hm| = trunk
        g = 0.5 * (dl / dl[1] + dr / dr[1])                         # S_mid = Y g
        # |Y g - H|^2 = trunk^2 -> Y^2 |g|^2 - 2 Y (g.H) + |H|^2 - trunk^2 = 0
        A_ = g @ g; B_ = -2 * g @ Hm[i]; C_ = Hm[i] @ Hm[i] - trunk ** 2
        disc = B_ ** 2 - 4 * A_ * C_
        if disc < 0:
            continue
        Y = (-B_ - np.sqrt(disc)) / (2 * A_)                          # the near root: shoulders toward the camera
        if Y <= 0.05:
            Y = (-B_ + np.sqrt(disc)) / (2 * A_)
        y_sh[i] = Y; S3[i, 0] = Y / dl[1] * dl; S3[i, 1] = Y / dr[1] * dr
    # ---- wrists on the floor, elbows from the two arm lengths and the elbow ray ----
    W3 = np.stack([plane_hit(d[:, L_WR], z_floor + WRIST_Z), plane_hit(d[:, R_WR], z_floor + WRIST_Z)], axis=1)
    E3 = np.full((N, 2, 3), np.nan); err = np.full((N, 2), np.nan)
    for i in np.where(ok & np.isfinite(y_sh))[0]:
        for j, (el, side) in enumerate(((L_EL, "l"), (R_EL, "r"))):
            e, E = elbow_error(W3[i, j], S3[i, j][None, :], d[i, el], P_img[i, el], lengths["fore_" + side], lengths["up_" + side], K, R, n_phi=360)
            err[i, j] = e[0]; E3[i, j] = E[0]
        if verbose and i % 500 == 0:
            print(f"  recon {i}/{N}", flush=True)
    out = dict(S=S3, E=E3, W=W3, Hm=Hm, hip_depth=depth, y_sh=y_sh, err_l=err[:, 0], err_r=err[:, 1], z_floor=z_floor)
    out["sh_h"] = S3[:, :, 2] - z_floor
    out["el_h"] = E3[:, :, 2] - z_floor
    out["hip_h"] = Hm[:, 2] - z_floor
    out["sh_w"] = np.linalg.norm(S3[:, 0] - S3[:, 1], axis=1)
    out["arm_len"] = np.linalg.norm(S3 - W3, axis=2)                 # wrist-to-shoulder, the straight-arm check (<= L_fore + L_up)
    v1 = W3 - E3; v2 = S3 - E3
    cosang = np.einsum("ijk,ijk->ij", v1, v2) / (np.linalg.norm(v1, axis=2) * np.linalg.norm(v2, axis=2) + 1e-9)
    out["elbow"] = np.degrees(np.arccos(np.clip(cosang, -1, 1)))
    up = S3 - E3
    out["upper_tilt"] = np.degrees(np.arcsin(np.clip(up[:, :, 2] / (np.linalg.norm(up, axis=2) + 1e-9), -1, 1)))
    out["flare"] = np.degrees(np.arctan2(np.abs(up[:, :, 0]), np.abs(up[:, :, 1]) + 1e-9))
    out["lever_el"] = np.linalg.norm((E3 - W3)[:, :, :2], axis=2)
    out["lever_sh"] = np.linalg.norm((S3 - W3)[:, :, :2], axis=2)
    out["sh_fwd"] = (S3 - W3)[:, :, 1]
    out["Sm"] = S3.mean(axis=1)
    return out


if __name__ == "__main__":
    d = np.load(sys.argv[1]); cam = np.load(sys.argv[2])
    hc = 0.05
    for a in sys.argv[3:]:
        if a.startswith("hc="): hc = float(a[3:])
    img = d["img"]; W, H = int(d["width"]), int(d["height"])
    P = img[:, :, :2] * np.array([W, H]); V = np.nan_to_num(img[:, :, 3]); ok = d["ok"]
    out = reconstruct(P, V, cam, hc=hc, ok=ok)
    print(f"hc = {hc*100:.1f} cm: shoulder width median {np.nanmedian(out['sh_w'])*100:.1f} cm; elbow reprojection error median "
          f"L {np.nanmedian(out['err_l']):.1f} / R {np.nanmedian(out['err_r']):.1f} px; shoulder height {np.nanmin(out['sh_h'])*100:.0f}..{np.nanmax(out['sh_h'])*100:.0f} cm; "
          f"elbow angle {np.nanmin(out['elbow']):.0f}..{np.nanmax(out['elbow']):.0f} deg")
