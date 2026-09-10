"""
Push-up biomechanics from one floor-level phone at the head end (IMG_6107, 2026-09-09).

    python analyze_pushups.py <video> <pose_mp.npz> <analysis.json> [pose_yolo.npz] [matte=matte.npy]
        [height=1.88] [mass=79] [cam=pushup/work/cam.npz] [hc=auto|0.13] [trim=t0,t1]

What the camera can and cannot see (pushup_recon.py has the geometry; every length below is a
landmark-to-landmark distance measured on Dennis in pull-up set #3's rectified plane):
  * the HIPS are visible in every frame, 1.3 m from the lens and never hidden. Their landmark
    width (19.0 cm) gives their distance, their ray gives their position. No camera height involved;
  * the SHOULDERS are visible at the top and through the middle of every rep; at the BOTTOM the
    head hides them and MediaPipe (and YOLO, with high confidence) invents them at the edges of the
    skull. Where they are seen, the rigid TRUNK (58.7 cm, shoulder-mid to hip-mid) puts them on their
    rays; where they are hidden, they are placed at the trunk length from the hips along the body
    line (toes -> hips, lifted by the hip sag measured on that rep's visible frames) and FLAGGED;
  * the WRISTS are on the floor, so their rays meet the floor plane at a distance proportional to the
    camera height h_c, the one free scale. hc=auto sets it from the LOCKED ARM at the tops: the
    wrist-to-shoulder distance there must be the arm's length (forearm + upper arm), and the
    shoulders do not depend on h_c while the wrists do. Two more numbers are printed beside it: the
    lens height of an iPhone 14 standing on its edge (about 12.5 cm) and the toes' image row;
  * the ELBOWS: where they are in the frame, the two arm lengths and the elbow ray fix their 3D
    position (levers, flare, upper-arm tilt). The elbow ANGLE itself comes from the wrist-to-shoulder
    distance by the law of cosines everywhere, which needs no elbow landmark at all; MediaPipe's own
    3D angle is printed beside it as the second witness;
  * the TOES are the pivot: YOLO's ankles (the feet never move, so their median over the confident
    frames), dropped to the floor and pushed 10 cm toward the far end for the toe-tips (assumed).

Judged to the USMC PFT push-up (MCO 6100.13A; references/pushup-science/03-*.md): elbows locked at
the top, the body straight from the head to the heels, at the bottom the upper arms at least
parallel to the deck (elbow at or under 90 deg); each line stated per rep with its number. A rep is
the shoulders back at the top after a full descent; a short descent is an attempt.
Sources: references/pushup-science/02-pushup-hand-force-and-joint-moments.md (hand force fractions),
04-pushup-fatigue-within-set.md (velocity loss), the pull-up archive for de Leva 1996 segment masses
(data/pullup-energy-and-segments.csv) and the Compendium METs.
"""
import sys, json, os
import numpy as np
import cv2
from scipy.signal import savgol_filter, find_peaks

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pushup_recon as PR

NOSE = 0; L_EYE, R_EYE = 2, 5; L_EAR, R_EAR = 7, 8
L_SH, R_SH = 11, 12; L_EL, R_EL = 13, 14; L_WR, R_WR = 15, 16
L_HIP, R_HIP = 23, 24; L_KNEE, R_KNEE = 25, 26; L_ANK, R_ANK = 27, 28
G = 9.81
EAR_W = 0.1506            # m, landmark ear-to-ear width, set #3 arms-down window (57-58.6 s), rectified plane, measured 2026-09-09
TRUNK = PR.LENGTHS["trunk"]
HIP_W = PR.LENGTHS["hip_w"]
ARM_LOCK = 0.99 * 0.5 * (PR.LENGTHS["fore_l"] + PR.LENGTHS["up_l"] + PR.LENGTHS["fore_r"] + PR.LENGTHS["up_r"])   # a locked arm, wrist to shoulder landmark, minus 1 % for the carrying angle (assumed)
LENS_PRIOR = 0.125        # m, the rear camera of an iPhone 14 standing on its bottom edge (146.7 mm tall, lens ~2 cm from the top; assumed)
ANKLE_PLANK = 0.14        # m, the ankle joint above the floor when on the toes (assumed, ranked)
TOE_BEYOND_ANKLE = 0.10   # m, the toe-tips beyond the ankle toward the far end (assumed)
# de Leva 1996 (data/pullup-energy-and-segments.csv, male): mass fractions of body mass
M_HAND, M_FORE, M_UPPER = 0.0061, 0.0162, 0.0271
M_TRUNK, M_HEAD = 0.4346, 0.0694          # de Leva 1996 Table 4 (trunk = UPT + MPT + LPT), head + neck
M_LEG = 0.1416 + 0.0433 + 0.0137          # thigh + shank + foot, one side
COM_UPPER, COM_FORE = 0.5772, 0.4574      # segment CM from the proximal end (de Leva Table 4)
COM_TRUNK_FROM_HIP = 0.55                 # trunk CM 44.86 % from the suprasternale (de Leva) -> ~55 % from the hips (assumed rounding)
COM_LEG_FROM_HIP = 0.40                   # composite thigh + shank + foot CM from the hip, fraction of hip->toe (assumed, ranked)
HEAD_BEYOND_SH = 0.16                     # m, head + neck CM beyond the shoulder line along the trunk axis (assumed, ranked)
ETA_CONC = 0.22; ECC_COST = 0.35          # as the pull-up analysis (Ryschon 1997, Bigland-Ritchie 1976 in the archive)
PLANK_MET = 3.0                           # Compendium 2024 code 02056, bodyweight resistance exercise, general (archived CSV)
KCAL_PER_J = 1 / 4184.0
VL_LANDMARKS = (25.0, 50.0)               # velocity-loss landmarks carried over from the pull-up literature (Sanchez-Moreno 2020);
                                          # push-up-specific thresholds: see 04-pushup-fatigue-within-set.md
USMC_ELBOW_BOTTOM = 90.0                  # deg, "upper arms parallel to the deck" = elbow at or under 90 (MCO 6100.13A)
LOCKOUT_DEG = 140.0                       # deg, elbows locked at the top. Law-of-cosines angle: near full extension 2 cm of wrist-to-shoulder distance is 20 deg (cos is flat there), and h_c was set so the median top distance is 99 % of the arm (~164 deg); 140 deg = 94 % of the arm length, i.e. 1 cm under the median top; the reps at 147-149 by this angle read 166-168 on MediaPipe and look locked on the frame. MediaPipe's own 3D angle is stored beside it
BODY_LINE_DEG = 168.0                     # straight body: shoulder-hip-toe angle at least this (12 deg of sag/pike allowed)
FAIL_SHORT_PCT = 0.60
ELBOW_ERR_MAX = 30.0                      # px, the elbow's 3D position is kept only when its circle point reprojects this close


def smooth(x, win=9, order=2):
    x = np.array(x, dtype=float)
    nans = ~np.isfinite(x)
    if nans.all():
        return x
    if nans.any():
        idx = np.arange(len(x))
        x[nans] = np.interp(idx[nans], idx[~nans], x[~nans])
    return savgol_filter(x, win, order)


def angle3(a, b, c):
    v1 = a - b; v2 = c - b
    cos = (v1 * v2).sum(-1) / (np.linalg.norm(v1, axis=-1) * np.linalg.norm(v2, axis=-1) + 1e-9)
    return np.degrees(np.arccos(np.clip(cos, -1, 1)))


def main():
    video, npz, out = sys.argv[1:4]
    yolo = None; matte_path = None; height = 1.88; mass = 79.0; cam_path = "pushup/work/cam.npz"; hc_arg = "auto"; trim = None
    for a in sys.argv[4:]:
        if a.startswith("height="): height = float(a[7:])
        elif a.startswith("mass="): mass = float(a[5:])
        elif a.startswith("cam="): cam_path = a[4:]
        elif a.startswith("hc="): hc_arg = a[3:]
        elif a.startswith("matte="): matte_path = a[6:]
        elif a.startswith("trim="): trim = tuple(float(x) for x in a[5:].split(","))
        else: yolo = a
    d = np.load(npz); fps = float(d["fps"]); W = int(d["width"]); H = int(d["height"])
    img = d["img"]; world = d["world"]; ok = d["ok"]
    N = len(img); t = np.arange(N) / fps
    P = img[:, :, :2] * np.array([W, H], dtype=np.float32)
    V = np.nan_to_num(img[:, :, 3])
    for j in range(P.shape[1]):
        for c in range(2):
            if not np.isfinite(P[:, j, c]).all():
                P[:, j, c] = smooth(P[:, j, c], 5, 1)
    cam = np.load(cam_path); K = cam["K"]; R = cam["R"]; f_px = float(K[0, 0])
    print(f"camera: f {f_px:.0f} px, pitch {float(cam['pitch']):+.2f} deg up, roll {float(cam['roll']):+.2f} deg")
    kp = np.load(yolo)["kp"] if yolo else None
    rays = PR.rays(P, K, R)

    # ---------- which frames show the shoulders and the elbows ----------
    el_in = ((P[:, L_EL, 0] > 25) & (P[:, L_EL, 0] < W - 25) & (P[:, R_EL, 0] > 25) & (P[:, R_EL, 0] < W - 25))
    vis_arm = (V[:, L_EL] > 0.6) & (V[:, R_EL] > 0.6) & (V[:, L_WR] > 0.6) & (V[:, R_WR] > 0.6)
    # the head hides the shoulders when the ear line drops to the shoulder line: ears above the shoulders'
    # image row by less than 30 % of the shoulder width means the skull is in front of them
    sh_w_px = np.linalg.norm(P[:, L_SH] - P[:, R_SH], axis=1)
    ear_y = 0.5 * (P[:, L_EAR, 1] + P[:, R_EAR, 1]); sh_y_img = 0.5 * (P[:, L_SH, 1] + P[:, R_SH, 1])
    head_clear = (sh_y_img - ear_y) > 0.30 * sh_w_px
    # The shoulders stay visible beside the head at the bottom (checked 2026-09-09: MediaPipe's shoulder
    # dots at the head's depth are 29-32 cm apart at every bottom, the same width as at the top, so they
    # are the deltoids, not the skull's edges). The HIPS do vanish behind the head at the bottom (the hip
    # dots then land on the skull): a hip is seen when it sits well below the ear line and its picture
    # width is near the set's.
    sh_vis = ok & (V[:, L_SH] > 0.6) & (V[:, R_SH] > 0.6)
    el_vis = sh_vis & el_in & vis_arm
    hip_y = 0.5 * (P[:, L_HIP, 1] + P[:, R_HIP, 1]); hip_px_raw = np.linalg.norm(P[:, L_HIP] - P[:, R_HIP], axis=1)
    hip_ref = float(np.nanmedian(hip_px_raw[sh_vis & head_clear]))
    hip_vis = ok & ((hip_y - ear_y) > 0.6 * sh_w_px) & (np.abs(hip_px_raw / hip_ref - 1) < 0.2)
    hip_depth = np.where(hip_vis, f_px * HIP_W / np.maximum(hip_px_raw, 1), np.nan)
    hip_depth_s = smooth(hip_depth, 15, 2)
    hip_depth = np.where(hip_vis, hip_depth_s, np.nan)
    print(f"shoulders seen on {sh_vis.sum()}/{N} frames (head clear of them {head_clear.sum()}), hips seen on {hip_vis.sum()}; elbows in frame as well on {el_vis.sum()}")

    # ---------- camera height from the locked arm at the tops ----------
    rec0 = PR.reconstruct(P, V, cam, hc=0.10, ok=sh_vis & hip_vis, verbose=False, hip_depth=hip_depth)
    SH_W_REF = float(np.nanmedian(rec0["sh_w"][sh_vis & hip_vis]))
    print(f"shoulder landmark width where the hips fix the distance: {SH_W_REF*100:.1f} cm (the depth scale for the frames where the hips are hidden)")
    rec0 = PR.reconstruct(P, V, cam, hc=0.10, ok=sh_vis, verbose=False, hip_depth=hip_depth, sh_w_ref=SH_W_REF)
    zS = np.where(sh_vis, rec0["Sm"][:, 2], np.nan)                       # shoulder Z relative to the camera: h_c-free
    top_fr = np.where(sh_vis & (zS > np.nanpercentile(zS, 85)))[0]
    def arm_at(hc_):
        o = PR.reconstruct(P[top_fr], V[top_fr], cam, hc=hc_, ok=np.ones(len(top_fr), bool), verbose=False, hip_depth=hip_depth[top_fr], sh_w_ref=SH_W_REF)
        return float(np.nanmedian(o["arm_len"]))
    grid = np.arange(0.06, 0.181, 0.005); arms = np.array([arm_at(h) for h in grid])
    for h_, a_ in zip(grid, arms):
        if abs(h_ * 200 - round(h_ * 200)) < 1e-6:
            print(f"  h_c {h_*100:4.1f} cm -> wrist-to-shoulder at the tops {a_*100:5.1f} cm (locked arm {ARM_LOCK*100:.1f})")
    if hc_arg == "auto":
        k = int(np.argmin(np.abs(arms - ARM_LOCK)))
        if 0 < k < len(grid) - 1:
            a_, b_ = (k - 1, k) if (arms[k - 1] - ARM_LOCK) * (arms[k] - ARM_LOCK) < 0 else (k, k + 1)
            hc = float(grid[a_] + (ARM_LOCK - arms[a_]) / (arms[b_] - arms[a_] + 1e-9) * (grid[b_] - grid[a_]))
        else:
            hc = float(grid[k])
        hc = float(np.clip(hc, grid[0], grid[-1]))
    else:
        hc = float(hc_arg)
    z_floor = -hc
    print(f"camera height h_c = {hc*100:.1f} cm from the locked arm at {len(top_fr)} top frames (lens prior for a standing iPhone 14: {LENS_PRIOR*100:.1f} cm)")

    # ---------- the chain on every frame ----------
    rec = PR.reconstruct(P, V, cam, hc=hc, ok=sh_vis, hip_depth=hip_depth, sh_w_ref=SH_W_REF)
    arm_top = PR.reconstruct(P[top_fr], V[top_fr], cam, hc=hc, ok=np.ones(len(top_fr), bool), verbose=False, hip_depth=hip_depth[top_fr], sh_w_ref=SH_W_REF)["arm_len"]
    print(f"  wrist-to-shoulder at the top frames: p10 {np.nanpercentile(arm_top, 10)*100:.1f}, median {np.nanmedian(arm_top)*100:.1f}, p90 {np.nanpercentile(arm_top, 90)*100:.1f} cm")
    Hm = rec["Hm"].copy(); Hm[~hip_vis] = np.nan
    hip_depth = rec["hip_depth"]
    err = np.stack([rec["err_l"], rec["err_r"]], axis=1)
    el_ok = el_vis & np.isfinite(err).all(axis=1) & (np.nan_to_num(err, nan=1e9) < ELBOW_ERR_MAX).all(axis=1)
    print(f"elbow circle solutions kept on {el_ok.sum()} frames (reprojection error median {np.nanmedian(err[el_vis]):.1f} px); "
          f"shoulder width where seen: median {np.nanmedian(rec['sh_w'][sh_vis])*100:.1f} cm (set #3: 38.2 arms down, 31.7 arms up); hips {np.nanmedian(hip_depth):.2f} m deep")
    if kp is not None:
        yw = np.linalg.norm(kp[:, 11, :2] - kp[:, 12, :2], axis=1); mw = np.linalg.norm(P[:, L_HIP] - P[:, R_HIP], axis=1)
        m_ = np.nan_to_num(kp[:, 11:13, 2]).min(axis=1) > 0.5
        print(f"  YOLO / MediaPipe hip width ratio here {np.nanmedian(yw[m_] / mw[m_]):.3f} (set #3 rectified plane: printed by the calibration check)")

    # ---------- toes: the pivot ----------
    # YOLO's ankles sit within a degree of the horizon, where a ray's floor distance is ill-conditioned
    # (a degree is a metre); the leg is the better ruler: hip-to-ankle 80.5 cm standing (set #3) plus the
    # foot on its toes, 0.95 m from the hip landmarks to the toe-tips along the body (assumed, ranked),
    # laid along the hips -> away-from-camera direction of the body line, on the floor
    LEG_TO_TOES = 0.95
    body_dir = np.nanmedian((Hm - rec["Sm"])[sh_vis], axis=0); body_dir[2] = 0; body_dir /= np.linalg.norm(body_dir)
    Hmed = np.nanmedian(Hm[sh_vis], axis=0)
    A_fixed = np.array([Hmed[0] + body_dir[0] * LEG_TO_TOES, Hmed[1] + body_dir[1] * LEG_TO_TOES, z_floor])
    toe_src = f"hips + {LEG_TO_TOES:.2f} m along the body line (hip-to-ankle 80.5 cm in set #3 + the foot; assumed)"
    if kp is not None:
        ca = np.nan_to_num(kp[:, 15:17, 2]).min(axis=1); good = ca > 0.3
        if good.sum() > 30:
            ank_px = np.median(np.stack([0.5 * (kp[good, 15, 0] + kp[good, 16, 0]), 0.5 * (kp[good, 15, 1] + kp[good, 16, 1])], axis=1), axis=0)
            # what row the ankle SHOULD be on for that toe position: a check on h_c, printed, not used
            ank_w = np.array([A_fixed[0], A_fixed[1] - TOE_BEYOND_ANKLE, z_floor + ANKLE_PLANK])
            pr = PR.project(ank_w[None, :], K, R)[0]
            print(f"  YOLO ankle row {ank_px[1]:.0f} px vs {pr[1]:.0f} px predicted for toes at Y {A_fixed[1]:.2f} m with the ankle {ANKLE_PLANK*100:.0f} cm up (h_c check: 1 px = ~4 cm of h_c)")
    A = np.tile(A_fixed, (N, 1))
    print(f"toes on the floor at Y {A_fixed[1]:.2f} m from the camera ({toe_src}); hips at Y {np.nanmedian(Hm[:, 1]):.2f} m, wrists at Y {np.nanmedian(rec['W'][:, :, 1]):.2f} m")

    # ---------- body line where seen; the hidden bottoms bridged ----------
    Sm_rec = rec["Sm"]
    sag_rec = np.full(N, np.nan); body_rec = np.full(N, np.nan)
    for i in np.where(sh_vis & hip_vis)[0]:
        S_, A_, H_ = Sm_rec[i], A[i], Hm[i]
        u = np.linalg.norm((H_ - S_)[:2]) / (np.linalg.norm((A_ - S_)[:2]) + 1e-9)
        sag_rec[i] = H_[2] - (S_[2] + u * (A_[2] - S_[2]))
        body_rec[i] = angle3(S_, H_, A_)

    Sm_all = np.stack([smooth(np.where(sh_vis, Sm_rec[:, c_], np.nan), 9, 2) for c_ in range(3)], axis=1)
    sag_fill = smooth(np.where(sh_vis & hip_vis, sag_rec, np.nan), 15, 1)
    # hips: seen -> the width scale; hidden -> the two rigid lengths from the shoulders and the toes
    LEG_TO_TOES = 0.95
    Hm_all = Hm.copy()
    last_sag = 0.0
    for i in range(N):
        if hip_vis[i] and np.isfinite(Hm[i]).all():
            continue
        S_ = Sm_all[i]; A_ = A[i]
        Dv = A_ - S_; D = np.linalg.norm(Dv); u = Dv / (D + 1e-9)
        cg = np.clip((TRUNK ** 2 + D ** 2 - LEG_TO_TOES ** 2) / (2 * TRUNK * D), -1, 1)
        horiz = np.array([u[0], u[1], 0.0]); horiz /= (np.linalg.norm(horiz) + 1e-9)
        v = np.cross(np.cross(u, np.array([0, 0, 1.0])), u); v /= (np.linalg.norm(v) + 1e-9)   # up-ish, perpendicular to S->A in the vertical plane
        sg = np.sqrt(max(1 - cg ** 2, 0)) * (1 if sag_fill[i] >= 0 or not np.isfinite(sag_fill[i]) else -1)
        Hm_all[i] = S_ + TRUNK * (cg * u + sg * v)
    for c_ in range(3):
        Hm_all[:, c_] = smooth(Hm_all[:, c_], 9, 2)
    sh_h = smooth(Sm_all[:, 2] - z_floor, 9, 2)
    hip_h = smooth(Hm_all[:, 2] - z_floor, 9, 2)
    Hm = Hm_all
    sag_fill = smooth(np.where(sh_vis, sag_rec, np.nan), 15, 1)

    # ---------- the head: nose height from the ear-width scale (every frame) ----------
    ear_px = smooth(np.linalg.norm(P[:, L_EAR] - P[:, R_EAR], axis=1), 9, 2)
    Ki = np.linalg.inv(K)
    nose_c = np.concatenate([P[:, NOSE], np.ones((N, 1))], axis=1) @ Ki.T
    Nw = (nose_c * (f_px * EAR_W / ear_px)[:, None]) @ R
    nose_h = smooth(Nw[:, 2] - z_floor, 9, 2)

    # ---------- elbow angle everywhere by the law of cosines; the 3D elbow where its circle solution holds ----------
    W3 = rec["W"]
    el_cos = np.full((N, 2), np.nan)
    half_w = float(np.nanmedian(rec["sh_w"][sh_vis])) / 2
    for j, side in enumerate(("l", "r")):
        S_side = np.where(sh_vis[:, None], rec["S"][:, j], Sm_all + np.array([half_w * (1 if side == "l" else -1), 0, 0]))
        dd = np.linalg.norm(S_side - W3[:, j], axis=1)
        Lf, Lu = PR.LENGTHS["fore_" + side], PR.LENGTHS["up_" + side]
        el_cos[:, j] = np.degrees(np.arccos(np.clip((Lf ** 2 + Lu ** 2 - dd ** 2) / (2 * Lf * Lu), -1, 1)))
    el_l = smooth(el_cos[:, 0], 9, 2); el_r = smooth(el_cos[:, 1], 9, 2)
    el3_l = smooth(angle3(world[:, L_SH], world[:, L_EL], world[:, L_WR]), 9, 2)
    el3_r = smooth(angle3(world[:, R_SH], world[:, R_EL], world[:, R_WR]), 9, 2)
    el_circ = np.where(el_ok[:, None], rec["elbow"], np.nan)
    print(f"elbow angle (law of cosines) vs the circle solution where kept: mean |diff| L {np.nanmean(np.abs(el_cos[el_ok, 0] - el_circ[el_ok, 0])):.1f} / "
          f"R {np.nanmean(np.abs(el_cos[el_ok, 1] - el_circ[el_ok, 1])):.1f} deg; vs MediaPipe 3D L {np.nanmean(np.abs(el_cos[sh_vis, 0] - el3_l[sh_vis])):.1f} / R {np.nanmean(np.abs(el_cos[sh_vis, 1] - el3_r[sh_vis])):.1f} deg")
    # ---------- the elbow on every frame: the arm circle, placed by the flare ----------
    # With the wrist, the shoulder and the elbow angle known, the elbow lies on a circle around the
    # wrist-shoulder axis; WHERE on it is the elbow flare (0 = elbows tucked along the body, 90 = straight
    # out to the side, seen from above). The flare is read from the circle solutions where the elbow
    # landmark is in the frame and its circle point reprojects within ELBOW_ERR_MAX (el_ok), smoothed and
    # interpolated across the bottoms where the elbows leave the frame (the flare is a posture that
    # changes slowly; assumed, ranked). The elbow then gives the levers (horizontal wrist-to-elbow, for the
    # elbow moment), the elbow height and the upper-arm tilt (the USMC "upper arms parallel to the deck").
    flare_raw = np.where(el_ok[:, None], rec["flare"], np.nan)
    flare = np.stack([smooth(flare_raw[:, 0], 31, 1), smooth(flare_raw[:, 1], 31, 1)], axis=1)
    E_geo = np.full((N, 2, 3), np.nan)
    for j, side in enumerate(("l", "r")):
        sgn = 1.0 if side == "l" else -1.0                    # the person's left is +X (image right, mirror view)
        S_side = np.where(sh_vis[:, None], rec["S"][:, j], Sm_all + np.array([half_w * sgn, 0, 0]))
        Wj = W3[:, j]; Lf, Lu = PR.LENGTHS["fore_" + side], PR.LENGTHS["up_" + side]
        th = np.radians(np.where(j == 0, el_l, el_r))
        v = S_side - Wj; dist = np.linalg.norm(v, axis=1); u = v / (dist[:, None] + 1e-9)
        a_ = (Lf ** 2 - Lu ** 2 + dist ** 2) / (2 * dist + 1e-9)
        r_ = np.sqrt(np.maximum(Lf ** 2 - a_ ** 2, 0))
        C = Wj + a_[:, None] * u
        tmp = np.where(np.abs(u[:, 2:3]) < 0.9, np.array([[0, 0, 1.0]]), np.array([[1.0, 0, 0]]))
        e1 = np.cross(u, tmp); e1 /= (np.linalg.norm(e1, axis=1, keepdims=True) + 1e-9); e2 = np.cross(u, e1)
        phi = np.linspace(0, 2 * np.pi, 180, endpoint=False)
        Ecand = C[:, None, :] + r_[:, None, None] * (np.cos(phi)[None, :, None] * e1[:, None, :] + np.sin(phi)[None, :, None] * e2[:, None, :])
        fl = np.radians(np.nan_to_num(flare[:, j], nan=40.0))
        target = np.stack([sgn * np.sin(fl), np.cos(fl)], axis=1)          # lateral and toward the feet (+Y)
        dxy = (Ecand - S_side[:, None, :])[:, :, :2]
        score = np.einsum("ijk,ik->ij", dxy, target)
        k = np.argmax(score, axis=1)
        E_geo[:, j] = Ecand[np.arange(N), k]
    lever_el = np.linalg.norm((E_geo - W3)[:, :, :2], axis=2)
    lever_sh = np.linalg.norm((np.stack([Sm_all, Sm_all], axis=1) - W3)[:, :, :2], axis=2)
    el_h = E_geo[:, :, 2] - z_floor
    up_v = np.stack([np.where(sh_vis[:, None], rec["S"][:, j], Sm_all + np.array([half_w * (1 if j == 0 else -1), 0, 0])) for j in range(2)], axis=1) - E_geo
    upper_tilt = np.degrees(np.arcsin(np.clip(up_v[:, :, 2] / (np.linalg.norm(up_v, axis=2) + 1e-9), -1, 1)))   # + = the elbow BELOW the shoulder
    for arr in (lever_el, lever_sh, el_h, upper_tilt):
        for j in range(2):
            arr[:, j] = smooth(arr[:, j], 9, 2)
    print(f"elbow flare median L {np.nanmedian(flare[:, 0]):.0f} / R {np.nanmedian(flare[:, 1]):.0f} deg (from {el_ok.sum()} in-frame frames); "
          f"elbow lever at the bottoms median {np.nanmedian([lever_el[b_].mean() for b_ in []] or [0]):.0f}")

    # ---------- the set: hands on the floor, reps from the shoulder height ----------
    hands_down = (V[:, L_WR] > 0.5) & (V[:, R_WR] > 0.5) & (P[:, L_WR, 1] > 0.6 * H) & (P[:, R_WR, 1] > 0.6 * H) & ok
    if trim:
        hands_down &= (t >= trim[0]) & (t <= trim[1])
    idx = np.where(hands_down)[0]
    runs = [[idx[0], idx[0]]]
    for i in idx[1:]:
        if i - runs[-1][1] <= 0.5 * fps: runs[-1][1] = i
        else: runs.append([i, i])
    set0, set1 = max(runs, key=lambda r: r[1] - r[0])
    hh = smooth(hip_h, 9, 2)
    amp_ref = 0.5 * (np.nanpercentile(sh_h[set0:set1], 95) - np.nanpercentile(sh_h[set0:set1], 5))
    bottoms, _ = find_peaks(-sh_h[set0:set1], prominence=amp_ref * 0.6, distance=int(0.8 * fps)); bottoms += set0
    tops = [set0 + int(np.argmax(sh_h[set0:bottoms[0]]))]
    for a_, b_ in zip(bottoms[:-1], bottoms[1:]):
        tops.append(a_ + int(np.argmax(sh_h[a_:b_])))
    tops.append(bottoms[-1] + int(np.argmax(sh_h[bottoms[-1]:set1 + 1])))
    print(f"hands on the floor {t[set0]:.1f}-{t[set1]:.1f} s; {len(bottoms)} bottoms from the shoulder height (amp ref {amp_ref*100:.0f} cm)")

    # ---------- per rep ----------
    v_sh = smooth(np.gradient(sh_h) * fps, 9, 2)                       # m/s, + up
    hip_v = smooth(np.gradient(hh) * fps, 9, 2)
    top_ref = float(np.nanmedian([sh_h[tp] for tp in tops])); bot_ref = float(np.nanmedian([sh_h[b] for b in bottoms]))
    height_pct = (sh_h - bot_ref) / (top_ref - bot_ref) * 100
    attempts = []; amps = []
    for k, b in enumerate(bottoms):
        t0_, t1_ = tops[k], tops[k + 1]
        amps.append(float(max(sh_h[t0_], sh_h[t1_]) - sh_h[b]))
    amp_set = float(np.median(amps))
    for k, b in enumerate(bottoms):
        t0_, t1_ = tops[k], tops[k + 1]
        top_h = float(max(sh_h[t0_], sh_h[t1_])); amp = top_h - sh_h[b]
        if amp < 0.25 * amp_set:
            continue
        hi = top_h - 0.05 * amp; lo = sh_h[b] + 0.05 * amp
        d0 = b
        while d0 > t0_ and sh_h[d0] < hi: d0 -= 1
        d1 = d0
        while d1 < b and sh_h[d1] > lo: d1 += 1
        u0 = b
        while u0 < t1_ and sh_h[u0] < lo: u0 += 1
        u1 = u0
        while u1 < t1_ and sh_h[u1] < hi: u1 += 1
        d1 = max(d1, d0 + 1); u1 = max(u1, u0 + 1)
        sl = slice(d0, u1 + 1); ecc = slice(d0, d1 + 1); conc = slice(u0, u1 + 1)
        el_b = float(min(el_l[b], el_r[b])); el_top = float(max(min(el_l[i_], el_r[i_]) for i_ in range(u0, t1_ + 1)))
        el_top_mp = float(max(min(el3_l[i_], el3_r[i_]) for i_ in range(u0, t1_ + 1)))
        tilt_b = float(np.nanmean(upper_tilt[b]))
        # the last frame before the bottom where the elbows were solved, and the tilt there
        seen = np.where(el_ok[d0:b + 1])[0]
        tilt_last = float(np.nanmean(rec["upper_tilt"][d0 + seen[-1]])) if len(seen) else None
        el_h_b = float(np.nanmean(el_h[b])); lever_el_b = float(np.nanmean(lever_el[b]))
        body_min = float(np.nanmin(body_rec[sl])) if np.isfinite(body_rec[sl]).any() else None
        sag_min = float(np.nanmin(sag_rec[sl])) if np.isfinite(sag_rec[sl]).any() else None
        flare_b = float(np.nanmean(flare[sl]))
        a = dict(
            n=len(attempts) + 1, f_top0=int(t0_), f_start=int(d0), f_bottom=int(b), f_ecc_end=int(d1), f_conc_start=int(u0),
            f_end=int(u1), f_top1=int(t1_), t_start=float(t[d0]), t_bottom=float(t[b]), t_end=float(t[u1]),
            rom_cm=float(amp * 100), sh_h_top_cm=float(top_h * 100), sh_h_bottom_cm=float(sh_h[b] * 100),
            hip_h_bottom_cm=float(hh[b] * 100), hip_h_top_cm=float(hh[t1_] * 100), nose_h_bottom_cm=float(nose_h[b] * 100),
            nose_h_top_cm=float(nose_h[t1_] * 100),
            elbow_bottom=el_b, elbow_bottom_l=float(el_l[b]), elbow_bottom_r=float(el_r[b]),
            elbow_top=el_top, elbow_top_l=float(el_l[t1_]), elbow_top_r=float(el_r[t1_]), elbow_top_mediapipe=el_top_mp,
            upper_arm_tilt_bottom=tilt_b, upper_arm_tilt_last_seen=tilt_last, elbow_flare_deg=flare_b, elbow_h_bottom_cm=el_h_b * 100, elbow_lever_bottom_cm=lever_el_b * 100,
            parallel_pass=bool(tilt_b <= 3.0),        # upper arm parallel or deeper = the shoulder at or below the elbow (tilt + = elbow below the shoulder), 3 deg of slack
            body_line_min=body_min, hip_sag_cm=(sag_min * 100 if sag_min is not None else None),
            depth_pass=bool(el_b <= USMC_ELBOW_BOTTOM), lockout=bool(el_top >= LOCKOUT_DEG),
            straight=bool(body_min is None or body_min >= BODY_LINE_DEG),
            t_eccentric=float((d1 - d0) / fps), t_bottom_hold=float((u0 - d1) / fps), t_concentric=float((u1 - u0) / fps),
            t_cycle=float((t1_ - t0_) / fps),
            peak_conc_v=float(np.nanmax(v_sh[conc])), mean_conc_v=float(amp / max((u1 - u0) / fps, 1e-3)),
            peak_ecc_v=float(-np.nanmin(v_sh[ecc])),
            peak_acc=float(np.nanmax(smooth(np.gradient(v_sh) * fps, 9, 2)[conc])),
            failed=bool(amp < FAIL_SHORT_PCT * amp_set),
            shoulders_seen_at_bottom=bool(sh_vis[b]), shoulders_seen_frac=float(sh_vis[sl].mean()), hips_seen_frac=float(hip_vis[sl].mean()),
            hips_hidden_s=float((~hip_vis[sl]).sum() / fps), hips_seen_at_bottom=bool(hip_vis[b]),
            elbow_asym_bottom=float(abs(el_l[b] - el_r[b])),
        )
        cl, cr = el_l[conc], el_r[conc]
        if len(cl) > 9:
            cls = cl - cl.mean(); crs = cr - cr.mean()
            scores = [float((cls * np.roll(crs, s)).sum()) for s in range(-4, 5)]
            lag = int(np.argmax(scores)) - 4
            a["elbow_lag_frames"] = lag; a["elbow_lag_ms"] = float(lag / fps * 1000)
        attempts.append(a)
    n_att = len(attempts)
    for k, a in enumerate(attempts):
        a["t_top_hold"] = float(attempts[k + 1]["t_start"] - a["t_end"]) if k + 1 < n_att else 0.0
        a["t_under_tension"] = a["t_eccentric"] + a["t_bottom_hold"] + a["t_concentric"] + a["t_top_hold"]
    reps = [a for a in attempts if not a["failed"]]; fails = [a for a in attempts if a["failed"]]
    for i, r in enumerate(reps): r["rep"] = i + 1
    for a in fails: a["rep"] = None
    n = len(reps)

    # ---------- kinetics: the hand force from the moment balance about the toes ----------
    Y_toe = A[:, 1]; Y_hip = Hm[:, 1]; Y_sh = Sm_all[:, 1]
    tdir = Sm_all - Hm; tdir /= (np.linalg.norm(tdir, axis=1, keepdims=True) + 1e-9)
    Y_head = Y_sh + HEAD_BEYOND_SH * tdir[:, 1]
    Y_legs = Y_hip + COM_LEG_FROM_HIP * (Y_toe - Y_hip)
    Y_trunk = Y_hip + COM_TRUNK_FROM_HIP * (Y_sh - Y_hip)
    W_l, W_r = W3[:, 0], W3[:, 1]
    Y_hand = 0.5 * (W_l[:, 1] + W_r[:, 1])
    E3 = E_geo
    E_y = E3[:, :, 1]; E_z = E3[:, :, 2]
    Y_upper = 0.5 * ((Y_sh + COM_UPPER * (E_y[:, 0] - Y_sh)) + (Y_sh + COM_UPPER * (E_y[:, 1] - Y_sh)))
    Y_fore = 0.5 * ((E_y[:, 0] + COM_FORE * (W_l[:, 1] - E_y[:, 0])) + (E_y[:, 1] + COM_FORE * (W_r[:, 1] - E_y[:, 1])))
    segs = [(2 * M_LEG, Y_legs), (M_TRUNK, Y_trunk), (M_HEAD, Y_head), (2 * M_UPPER, Y_upper), (2 * M_FORE, Y_fore), (2 * M_HAND, Y_hand)]
    mtot = sum(m for m, _ in segs)
    Y_com = sum(m * y for m, y in segs) / mtot
    Z_hip = Hm[:, 2]; Z_sh = Sm_all[:, 2]; Z_toe = A[:, 2]
    Z_legs = Z_hip + COM_LEG_FROM_HIP * (Z_toe - Z_hip); Z_trunk = Z_hip + COM_TRUNK_FROM_HIP * (Z_sh - Z_hip)
    Z_head = Z_sh + HEAD_BEYOND_SH * tdir[:, 2]
    Z_upper = Z_sh + COM_UPPER * (E_z.mean(axis=1) - Z_sh); Z_fore = E_z.mean(axis=1) + COM_FORE * ((z_floor + PR.WRIST_Z) - E_z.mean(axis=1))
    Z_com = (2 * M_LEG * Z_legs + M_TRUNK * Z_trunk + M_HEAD * Z_head + 2 * M_UPPER * Z_upper + 2 * M_FORE * Z_fore + 2 * M_HAND * (z_floor + PR.WRIST_Z)) / mtot
    Z_com = smooth(Z_com, 9, 2); a_com = smooth(np.gradient(np.gradient(Z_com) * fps) * fps, 9, 2)
    lever_com = np.abs(Y_toe - Y_com); lever_hand = np.abs(Y_toe - Y_hand)
    hand_frac = np.clip(lever_com / np.maximum(lever_hand, 0.3), 0.3, 1.0)
    F_hand_total = mass * np.clip(G + a_com, 0, None) * hand_frac
    on = np.zeros(N, bool); on[set0:set1 + 1] = True
    F_hand_total = np.where(on, F_hand_total, 0.0)

    # ---------- energy ----------
    plank_w = PLANK_MET * 3.5 * mass / 1000 * 5.0 / 60 * 4184.0
    peak_ref1 = reps[0]["peak_conc_v"]; v_ref1 = reps[0]["mean_conc_v"]; peak_ref = max(r["peak_conc_v"] for r in reps)
    cum = 0.0
    for a in attempts:
        sl = slice(a["f_start"], a["f_end"] + 1)
        dz = float(Z_com[a["f_end"]] - Z_com[a["f_bottom"]])
        w = mass * G * max(dz, 0.0)
        a["com_rise_cm"] = dz * 100; a["work_j"] = float(w)
        a["mean_power_w"] = float(w / max(a["t_concentric"], 1e-3))
        a["peak_force_n"] = float(np.nanmax(F_hand_total[sl])); a["peak_force_bw"] = float(a["peak_force_n"] / (mass * G))
        a["hand_frac_top"] = float(hand_frac[a["f_end"]]); a["hand_frac_bottom"] = float(hand_frac[a["f_bottom"]])
        a["peak_power_w"] = float(np.nanmax(F_hand_total[a["f_conc_start"]:a["f_end"] + 1] * np.clip(v_sh[a["f_conc_start"]:a["f_end"] + 1], 0, None)))
        e_conc = w / ETA_CONC * KCAL_PER_J; e_ecc = w * ECC_COST / ETA_CONC * KCAL_PER_J
        e_iso = plank_w * a["t_under_tension"] * KCAL_PER_J
        a["kcal_conc"] = e_conc; a["kcal_ecc"] = e_ecc; a["kcal_iso"] = e_iso; a["kcal"] = e_conc + e_ecc + e_iso
        cum += a["kcal"]; a["kcal_cum"] = cum
        a["heat_j"] = float(a["kcal"] / KCAL_PER_J - w)
        a["effort_x"] = float(v_ref1 / max(a["mean_conc_v"], 1e-3)); a["effort_x_vs_fastest"] = float(peak_ref / max(a["peak_conc_v"], 1e-3))
        vl1 = 1 - a["peak_conc_v"] / peak_ref1; vlf = 1 - a["peak_conc_v"] / peak_ref
        a["velocity_loss_pct"] = float(vl1 * 100); a["velocity_loss_vs_fastest_pct"] = float(vlf * 100)
        vl = max(vl1, 0.0) * 100
        a["est_rir_range"], a["vl_zone"] = (("4+", "under 25 %: fresh") if vl < VL_LANDMARKS[0] else ("1-3", "25-50 %: past the training cut-off") if vl < VL_LANDMARKS[1] else ("0-1", "over 50 %: grinding"))
    set_kcal = cum
    for a in attempts:
        depth = 25 * float(np.clip(1 - max(a["elbow_bottom"] - USMC_ELBOW_BOTTOM, 0) / 30, 0, 1))
        lock = 15 * float(np.clip((a["elbow_top"] - 130) / 30, 0, 1))
        line = 20 * float(np.clip(1 - (max(0.0, BODY_LINE_DEG - (a["body_line_min"] if a["body_line_min"] is not None else 180)) / 15), 0, 1))
        ctrl = 15 * float(np.clip(a["t_eccentric"] / 1.0, 0, 1))
        vel = 15 * float(np.clip(a["peak_conc_v"] / peak_ref, 0, 1))
        sym = 10 * float(np.clip(1 - (a["elbow_asym_bottom"] - 5) / 20, 0, 1))
        a["score"] = dict(depth=depth, lockout=lock, body_line=line, control=ctrl, power=vel, symmetry=sym)
        a["efficiency"] = float(depth + lock + line + ctrl + vel + sym)

    # ---------- phases ----------
    phase = np.array(["SETUP"] * N, dtype=object)
    phase[set0:set1 + 1] = "PLANK"
    for a in attempts:
        phase[a["f_start"]:a["f_ecc_end"] + 1] = "LOWER"
        phase[a["f_ecc_end"]:a["f_conc_start"] + 1] = "BOTTOM"
        phase[a["f_conc_start"]:a["f_end"] + 1] = "PUSH"
    phase[set1 + 1:] = "DONE"

    def mstat(key, src=reps):
        v = [r[key] for r in src if r.get(key) is not None]
        return float(np.mean(v)) if v else None

    tech = dict(
        standard=("USMC PFT push-up (MCO 6100.13A): elbows locked at the top; body straight from the head to the heels; "
                  "at the bottom the upper arms parallel to the deck (elbow at or under 90 deg); a rep counts when the arms lock again"),
        reps_counted=n, failed_attempts=len(fails),
        depth_pass=sum(r["depth_pass"] for r in reps), parallel_pass=sum(r["parallel_pass"] for r in reps), lockouts=sum(r["lockout"] for r in reps), straight=sum(r["straight"] for r in reps),
        mean_elbow_h_bottom_cm=mstat("elbow_h_bottom_cm"), mean_upper_arm_tilt_bottom=mstat("upper_arm_tilt_bottom"),
        mean_elbow_bottom=mstat("elbow_bottom"), mean_elbow_top=mstat("elbow_top"), mean_elbow_top_mediapipe=mstat("elbow_top_mediapipe"),
        mean_body_line_min=mstat("body_line_min"), mean_hip_sag_cm=mstat("hip_sag_cm"), mean_flare_deg=mstat("elbow_flare_deg"),
        mean_nose_bottom_cm=mstat("nose_h_bottom_cm"), mean_sh_bottom_cm=mstat("sh_h_bottom_cm"), mean_sh_top_cm=mstat("sh_h_top_cm"),
        mean_upper_arm_tilt_last_seen=mstat("upper_arm_tilt_last_seen"),
        velocity_loss_pct=float((1 - reps[-1]["peak_conc_v"] / peak_ref1) * 100),
        velocity_loss_vs_fastest_pct=float((1 - reps[-1]["peak_conc_v"] / peak_ref) * 100),
        vl_landmarks_pct=list(VL_LANDMARKS),
        rep_past_25pct=next((r["rep"] for r in reps if r["velocity_loss_pct"] >= VL_LANDMARKS[0]), None),
        rep_past_50pct=next((r["rep"] for r in reps if r["velocity_loss_pct"] >= VL_LANDMARKS[1]), None),
        taken_to_failure=len(fails) > 0,
        shoulders_seen_at_bottom=sum(r["shoulders_seen_at_bottom"] for r in reps),
        bottom_note=("At the bottom the head hides the hips from this camera; the shoulders stay visible beside it and their picture "
                     "width, calibrated where the hips fixed their distance, sets their depth. The nose and the ears are measured; the "
                     "elbow angle follows from the wrist-to-shoulder distance by the law of cosines (no elbow landmark needed)"),
    )
    hand_w = float(np.nanmedian(np.linalg.norm((W_l - W_r)[set0:set1, :2], axis=1)))
    sh_w_rec = float(np.nanmedian(rec["sh_w"][sh_vis]))
    summary = dict(
        attempts=n_att, reps=n, failed=len(fails), fps=fps, frames=N, tracked_frames=int(ok.sum()), height_m=height, mass_kg=mass,
        camera=dict(f_px=f_px, pitch_up_deg=float(cam["pitch"]), roll_deg=float(cam["roll"]), height_m=hc, lens_prior_m=LENS_PRIOR,
                    height_note="h_c chosen so the wrist-to-shoulder distance at the locked tops equals the arm length (forearm + upper arm, set #3)",
                    arm_lock_m=ARM_LOCK, elbow_reproj_px=float(np.nanmedian(err[el_vis])), shoulders_seen_frames=int(sh_vis.sum()), hips_seen_frames=int(hip_vis.sum()), elbows_solved_frames=int(el_ok.sum()), shoulder_width_ref_m=SH_W_REF,
                    hip_depth_m=float(np.nanmedian(hip_depth))),
        lengths=dict(PR.LENGTHS), wrist_z_m=PR.WRIST_Z, ankle_plank_m=ANKLE_PLANK, ear_w_m=EAR_W,
        set_start=float(t[set0]), set_end=float(t[set1]), set_duration=float(attempts[-1]["t_end"] - attempts[0]["t_start"]),
        reps_per_min=float(n / (attempts[-1]["t_end"] - attempts[0]["t_start"]) * 60),
        mean_eccentric=mstat("t_eccentric"), mean_bottom_hold=mstat("t_bottom_hold"), mean_concentric=mstat("t_concentric"),
        mean_top_hold=float(np.mean([r["t_top_hold"] for r in reps[:-1]])) if n > 1 else 0.0,
        mean_cycle=float(np.mean([r["t_cycle"] for r in reps[:-1]])) if n > 1 else 0.0,
        mean_efficiency=mstat("efficiency"), best_rep=int(max(reps, key=lambda r: r["efficiency"])["rep"]), worst_rep=int(min(reps, key=lambda r: r["efficiency"])["rep"]),
        peak_v_first=reps[0]["peak_conc_v"], peak_v_last=reps[-1]["peak_conc_v"], peak_v_max=peak_ref,
        velocity_loss_pct=tech["velocity_loss_pct"], velocity_loss_vs_fastest_pct=tech["velocity_loss_vs_fastest_pct"],
        mean_rom_cm=mstat("rom_cm"), top_ref_cm=top_ref * 100, bottom_ref_cm=bot_ref * 100,
        hand_width_cm=hand_w * 100, shoulder_width_rec_cm=sh_w_rec * 100, hand_to_shoulder_ratio=hand_w / sh_w_rec,
        toes_y_m=float(A_fixed[1]), hips_y_m=float(np.nanmedian(Y_hip)), hands_y_m=float(np.nanmedian(Y_hand)), toe_source=toe_src,
        lifted_mass_kg=mass, hand_frac_top=float(np.nanmedian([r["hand_frac_top"] for r in reps])), hand_frac_bottom=float(np.nanmedian([r["hand_frac_bottom"] for r in reps])),
        hand_frac_note="quasi-static moment balance about the toes with de Leva 1996 segment CMs; the force-plate literature is in 02-pushup-hand-force-and-joint-moments.md",
        work_per_rep_j=mstat("work_j"), set_work_kj=float(sum(a["work_j"] for a in attempts) / 1000), set_kcal=float(set_kcal),
        set_heat_kj=float(sum(a["heat_j"] for a in attempts) / 1000), plank_kcal_per_s=float(plank_w * KCAL_PER_J),
        mean_power_w_first=reps[0]["mean_power_w"], mean_power_w_last=reps[-1]["mean_power_w"], peak_power_w_max=float(max(a["peak_power_w"] for a in attempts)),
        peak_force_bw_max=float(max(a["peak_force_bw"] for a in attempts)), effort_x_last=reps[-1]["effort_x"], est_rir_last=reps[-1]["est_rir_range"],
        model=dict(eta_conc=ETA_CONC, ecc_cost=ECC_COST, plank_met=PLANK_MET, usmc_elbow_bottom=USMC_ELBOW_BOTTOM, lockout_deg=LOCKOUT_DEG, body_line_deg=BODY_LINE_DEG,
                   com_trunk_from_hip=COM_TRUNK_FROM_HIP, com_leg_from_hip=COM_LEG_FROM_HIP, head_beyond_sh_m=HEAD_BEYOND_SH, toe_beyond_ankle_m=TOE_BEYOND_ANKLE),
        technique=tech, velocity_reference="rep 1; the fastest rep is reported beside it",
    )
    if kp is not None:
        conf = np.nan_to_num(kp[:, 5:7, 2]).min(axis=1)
        summary["yolo_shoulder_conf_at_bottoms"] = [float(conf[b]) for b in bottoms]
        yh = smooth(np.where(np.nan_to_num(kp[:, 11:13, 2]).min(axis=1) > 0.3, (kp[:, 11, 1] + kp[:, 12, 1]) / 2, np.nan), 9, 2)
        yb, _ = find_peaks(yh[set0:set1], prominence=30, distance=int(0.8 * fps))
        summary["yolo_bottoms"] = int(len(yb)); summary["yolo_bottom_times"] = [float(t[set0 + i]) for i in yb]
        m = np.isfinite(yh) & on
        summary["yolo_mp_hip_corr"] = float(np.corrcoef(hh[m], -yh[m])[0, 1])
    signals = dict(
        t=t.tolist(), sh_h=sh_h.tolist(), sh_seen=sh_vis.astype(int).tolist(), hip_h=hh.tolist(), nose_h=nose_h.tolist(),
        height_pct=np.nan_to_num(height_pct).tolist(), vy_m=np.nan_to_num(v_sh).tolist(), hip_v=hip_v.tolist(),
        elbow_l=np.nan_to_num(el_l, nan=170.0).tolist(), elbow_r=np.nan_to_num(el_r, nan=170.0).tolist(),
        elbow_mp_l=np.nan_to_num(el3_l).tolist(), elbow_mp_r=np.nan_to_num(el3_r).tolist(),
        upper_tilt_l=np.nan_to_num(upper_tilt[:, 0]).tolist(), upper_tilt_r=np.nan_to_num(upper_tilt[:, 1]).tolist(),
        flare_l=np.nan_to_num(flare[:, 0]).tolist(), flare_r=np.nan_to_num(flare[:, 1]).tolist(),
        lever_el_l=np.nan_to_num(lever_el[:, 0]).tolist(), lever_el_r=np.nan_to_num(lever_el[:, 1]).tolist(),
        lever_sh_l=np.nan_to_num(lever_sh[:, 0]).tolist(), lever_sh_r=np.nan_to_num(lever_sh[:, 1]).tolist(),
        el_h_l=np.nan_to_num(el_h[:, 0]).tolist(), el_h_r=np.nan_to_num(el_h[:, 1]).tolist(), el_ok=el_ok.astype(int).tolist(), E_geo=np.nan_to_num(E_geo).tolist(),
        body_line=np.nan_to_num(body_rec, nan=180.0).tolist(), hip_sag_cm=(np.nan_to_num(sag_rec) * 100).tolist(),
        hand_frac=hand_frac.tolist(), F_hand_n=F_hand_total.tolist(), z_com=(Z_com - z_floor).tolist(), a_com=a_com.tolist(),
        S=np.nan_to_num(Sm_all).tolist(), Hp=Hm.tolist(), A=A_fixed.tolist(), W_l=W_l.tolist(), W_r=W_r.tolist(), E=np.nan_to_num(E3).tolist(),
        z_floor=z_floor, phase=phase.tolist(), tops=[int(x) for x in tops], bottoms=[int(x) for x in bottoms], set0=int(set0), set1=int(set1))
    json.dump(dict(summary=summary, reps=attempts, signals=signals), open(out, "w"), indent=1)

    print(f"\nATTEMPTS {n_att}: {n} reps + {len(fails)} failed")
    print("  #  bottom  shH_b hipH_b noseH  elbB L/R  tiltB elH  elbT/mp  bodyMin  sag flare  down hold   up  rest    v   VL%  frac t/b  eff hips%")
    for a in attempts:
        tag = f"#{a['rep']:2d}" if a["rep"] else "FAIL"
        tb = f"{a['upper_arm_tilt_bottom']:+4.0f} {a['elbow_h_bottom_cm']:3.0f}"
        bl = f"{a['body_line_min']:5.0f}" if a["body_line_min"] is not None else "   --"
        sg = f"{a['hip_sag_cm']:+4.0f}" if a["hip_sag_cm"] is not None else "  --"
        fl = f"{a['elbow_flare_deg']:4.0f}" if a["elbow_flare_deg"] is not None else "  --"
        print(f"{tag} {a['t_bottom']:6.2f} {a['sh_h_bottom_cm']:6.1f} {a['hip_h_bottom_cm']:6.1f} {a['nose_h_bottom_cm']:5.1f} "
              f"{a['elbow_bottom_l']:4.0f}/{a['elbow_bottom_r']:3.0f}   {tb}  {a['elbow_top']:3.0f}/{a['elbow_top_mediapipe']:3.0f}  {bl} {sg} {fl}  "
              f"{a['t_eccentric']:4.2f} {a['t_bottom_hold']:4.2f} {a['t_concentric']:4.2f} {a['t_top_hold']:4.2f} {a['peak_conc_v']:5.2f} "
              f"{a['velocity_loss_pct']:4.0f} {a['hand_frac_top']:.2f}/{a['hand_frac_bottom']:.2f} {a['efficiency']:4.0f}  {a['hips_seen_frac']*100:3.0f}")
    print()
    print(json.dumps({k: v for k, v in summary.items() if k not in ("technique", "model", "lengths", "yolo_bottom_times")}, indent=1))
    print("TECHNIQUE:", json.dumps(tech, indent=1))


if __name__ == "__main__":
    main()
