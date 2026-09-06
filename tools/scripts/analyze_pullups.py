"""
Pull-up biomechanics from a MediaPipe pose track (extract_pose_mp.py output).

    python analyze_pullups.py <video> <pose_mp.npz> <analysis.json> [pose_yolo.npz] [height=1.88] [mass=79]

Height signal = shoulder midpoint (always visible; the face goes behind the bar /
door lintel at the top of every rep and MediaPipe hallucinates it there with
visibility 1.0 - never trust face landmarks near the bar).
Joint angles come from the metric 3D world landmarks (2D elbow angles collapse to
~10 deg at the top because the forearm points at the floor-level camera).
Scale: with height= given, vertical px/m is anchored on the straight arm at the loaded
hang (shoulder joint to wrist = 0.332 x stature, Drillis & Contini) - the one segment
aligned with the motion and at the depth of the motion. Hip-level horizontal measures
use the trunk-anchored scale (hips are closer to the camera); the standing neck length
uses the local world-fit scale. Without height=, the world-fit is used throughout.
With mass= given, work / power / force / a rough kcal per rep are computed.
"""
import sys, json
import numpy as np
import cv2
from scipy.signal import savgol_filter, find_peaks

NOSE = 0; L_EYE, R_EYE = 2, 5; L_EAR, R_EAR = 7, 8; L_MOUTH, R_MOUTH = 9, 10
L_SH, R_SH = 11, 12; L_EL, R_EL = 13, 14; L_WR, R_WR = 15, 16
L_HIP, R_HIP = 23, 24; L_KNEE, R_KNEE = 25, 26; L_ANK, R_ANK = 27, 28
G = 9.81
TRUNK_FRAC = 0.288          # shoulder-joint to hip-joint length / stature (Drillis & Contini 1966)
ARM_FRAC = 0.332            # shoulder joint to wrist (upper arm 0.186 + forearm 0.146)
LIFTED_FRAC = 0.956         # body mass minus hands + forearms (Dempster), which stay at the bar
ETA_CONC = 0.22             # metabolic efficiency of concentric muscle work
ECC_COST = 0.35             # eccentric metabolic cost relative to the same concentric work
HANG_MET = 3.5              # isometric bar hang, METs (rough)
KCAL_PER_J = 1 / 4184.0


def angle(a, b, c):
    v1 = a - b; v2 = c - b
    cos = (v1 * v2).sum(-1) / (np.linalg.norm(v1, axis=-1) * np.linalg.norm(v2, axis=-1) + 1e-9)
    return np.degrees(np.arccos(np.clip(cos, -1, 1)))


def smooth(x, win=9, order=2):
    x = np.array(x, dtype=float)
    nans = np.isnan(x)
    if nans.all():
        return x
    if nans.any():
        idx = np.arange(len(x))
        x[nans] = np.interp(idx[nans], idx[~nans], x[~nans])
    return savgol_filter(x, win, order)


def detect_bar(video, x0, x1):
    cap = cv2.VideoCapture(video); ok, f = cap.read(); cap.release()
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(float)
    prof = np.convolve(g[:, x0:x1].mean(axis=1), np.ones(9) / 9, mode="same")
    top_half = prof[: g.shape[0] // 2]
    y = int(np.argmin(top_half))
    return y, float(top_half[y])


def runs_of(mask, fps, merge_gap_s=0.5):
    idx = np.where(mask)[0]
    if len(idx) == 0:
        return []
    runs = [[idx[0], idx[0]]]
    for i in idx[1:]:
        if i - runs[-1][1] <= merge_gap_s * fps:
            runs[-1][1] = i
        else:
            runs.append([i, i])
    return runs


def main():
    video, npz, out = sys.argv[1:4]
    yolo = None; height = None; mass = None
    for a in sys.argv[4:]:
        if a.startswith("height="): height = float(a[7:])
        elif a.startswith("mass="): mass = float(a[5:])
        else: yolo = a
    d = np.load(npz)
    fps = float(d["fps"]); W = int(d["width"]); H = int(d["height"])
    img = d["img"]; world = d["world"]; ok = d["ok"]
    N = len(img); t = np.arange(N) / fps
    P = img[:, :, :2] * np.array([W, H], dtype=np.float32)
    V = img[:, :, 3]

    def mid(a, b):
        return (P[:, a] + P[:, b]) / 2
    nose = P[:, NOSE]; mouth = mid(L_MOUTH, R_MOUTH)
    chin = mouth + 0.9 * (mouth - nose)
    sh = mid(L_SH, R_SH); hip = mid(L_HIP, R_HIP); ear = mid(L_EAR, R_EAR); wr = mid(L_WR, R_WR)
    sh_w_px = smooth(np.linalg.norm(P[:, L_SH] - P[:, R_SH], axis=1), 15, 2)
    trunk_px = smooth((np.linalg.norm(P[:, L_SH] - P[:, L_HIP], axis=1) + np.linalg.norm(P[:, R_SH] - P[:, R_HIP], axis=1)) / 2, 15, 2)

    # --- world-fit scale (fallback) ---
    pairs = [(L_SH, R_SH), (L_HIP, R_HIP), (L_SH, L_HIP), (R_SH, R_HIP), (L_SH, L_EL), (R_SH, R_EL)]
    scale_fit = np.full(N, np.nan)
    for i in range(N):
        if not ok[i]:
            continue
        r = []
        for a, b in pairs:
            if V[i, a] > 0.5 and V[i, b] > 0.5:
                dp = np.linalg.norm(P[i, a] - P[i, b]); dw = np.linalg.norm(world[i, a] - world[i, b])
                if dw > 0.05:
                    r.append(dp / dw)
        if r:
            scale_fit[i] = np.median(r)
    scale_fit = smooth(scale_fit, 31, 2)

    # 3D joint angles (world) + 2D for reference
    el3_l = smooth(angle(world[:, L_SH], world[:, L_EL], world[:, L_WR]), 9, 2)
    el3_r = smooth(angle(world[:, R_SH], world[:, R_EL], world[:, R_WR]), 9, 2)
    el3 = (el3_l + el3_r) / 2
    el2_l = smooth(angle(P[:, L_SH], P[:, L_EL], P[:, L_WR]), 9, 2)
    el2_r = smooth(angle(P[:, R_SH], P[:, R_EL], P[:, R_WR]), 9, 2)
    kn3_l = smooth(angle(world[:, L_HIP], world[:, L_KNEE], world[:, L_ANK]), 9, 2)
    kn3_r = smooth(angle(world[:, R_HIP], world[:, R_KNEE], world[:, R_ANK]), 9, 2)
    hp3_l = smooth(angle(world[:, L_SH], world[:, L_HIP], world[:, L_KNEE]), 9, 2)
    hp3_r = smooth(angle(world[:, R_SH], world[:, R_HIP], world[:, R_KNEE]), 9, 2)
    knee_vis = np.minimum(V[:, L_KNEE], V[:, R_KNEE])

    # trunk orientation from world landmarks (camera frame: x right, y down, z toward camera negative)
    shw = (world[:, L_SH] + world[:, R_SH]) / 2; hpw = (world[:, L_HIP] + world[:, R_HIP]) / 2
    tv = shw - hpw
    trunk_lean = smooth(np.degrees(np.arctan2(-tv[:, 2], -tv[:, 1])), 9, 2)     # + = shoulders toward camera (leaning back / chest up)
    sh_line = world[:, R_SH] - world[:, L_SH]; hip_line = world[:, R_HIP] - world[:, L_HIP]
    yaw = smooth(np.degrees(np.arctan2(sh_line[:, 2], sh_line[:, 0])), 9, 2)     # shoulder line rotation about vertical
    yaw = yaw - np.nanmedian(yaw[: int(3 * fps)])                                   # relative to the standing pose
    def fold(a):
        a = (a + 180) % 360 - 180
        return np.where(a > 90, a - 180, np.where(a < -90, a + 180, a))
    sh_ang = fold(np.degrees(np.arctan2(P[:, R_SH, 1] - P[:, L_SH, 1], P[:, R_SH, 0] - P[:, L_SH, 0])))
    hip_ang = fold(np.degrees(np.arctan2(P[:, R_HIP, 1] - P[:, L_HIP, 1], P[:, R_HIP, 0] - P[:, L_HIP, 0])))
    lat_bend = smooth(sh_ang - hip_ang, 9, 2)       # + = shoulder line tilted relative to the hip line (image plane)
    trunk_len_w = smooth((np.linalg.norm(world[:, L_SH] - world[:, L_HIP], axis=1) + np.linalg.norm(world[:, R_SH] - world[:, R_HIP], axis=1)) / 2, 9, 2)

    bl = hip - sh
    body_tilt = np.degrees(np.arctan2(bl[:, 0], bl[:, 1]))
    sh_tilt = np.degrees(np.arctan2(P[:, R_SH, 1] - P[:, L_SH, 1], P[:, R_SH, 0] - P[:, L_SH, 0]))
    sh_tilt = np.where(sh_tilt > 90, sh_tilt - 180, np.where(sh_tilt < -90, sh_tilt + 180, sh_tilt))

    # --- bar ---
    hands_up = (P[:, L_WR, 1] < P[:, L_SH, 1]) & (P[:, R_WR, 1] < P[:, R_SH, 1]) & ok
    wrist_bar = float(np.nanmedian(wr[hands_up, 1]))
    bar_y, bar_dark = detect_bar(video, int(W * 0.15), int(W * 0.75))
    if abs(bar_y - wrist_bar) > 0.08 * H:
        print("bar detection rejected, falling back to wrist line")
        bar_y = int(wrist_bar - 0.02 * H)
    print(f"bar row {bar_y}px (wrist line {wrist_bar:.0f}px, darkness {bar_dark:.0f})")

    # --- hands-on-bar window and rep tops on the shoulder signal ---
    runs = runs_of(hands_up, fps, 0.5)
    grab0, grab1 = max(runs, key=lambda r: r[1] - r[0])
    sh_y = smooth(sh[:, 1], 9, 2)
    amp_ref = 0.10 * H
    tops, _ = find_peaks(-sh_y[grab0:grab1], prominence=amp_ref * 0.5, distance=int(0.6 * fps))
    tops = tops + grab0
    bottoms = [grab0 + int(np.argmax(sh_y[grab0:tops[0]]))]
    for a, b in zip(tops[:-1], tops[1:]):
        bottoms.append(a + int(np.argmax(sh_y[a:b])))
    bottoms.append(tops[-1] + int(np.argmax(sh_y[tops[-1]:grab1 + 1])))

    # --- hang onset: hands on the bar is not hanging. Arm length (shoulder->wrist px) and the
    # shoulder line both settle to new values when the body weight goes onto the bar. ---
    arm_px = smooth((np.linalg.norm(P[:, L_SH] - P[:, L_WR], axis=1) + np.linalg.norm(P[:, R_SH] - P[:, R_WR], axis=1)) / 2, 15, 2)
    first_top = int(tops[0])
    pre = slice(grab0, first_top)
    # the loaded hang = last 0.5 s before the first rise; standing = first 1 s with hands up
    rise_start = first_top
    while rise_start > grab0 and sh_y[rise_start - 1] > sh_y[rise_start] - 0.2:
        rise_start -= 1
    # simpler and robust: loaded reference = max shoulder y before the first top (= bottoms[0])
    loaded_f = bottoms[0]
    hang_arm = float(np.median(arm_px[max(grab0, loaded_f - int(0.4 * fps)):loaded_f + 1]))
    hang_sh = float(np.median(sh_y[max(grab0, loaded_f - int(0.4 * fps)):loaded_f + 1]))
    # standing reference = the longest quiet plateau of arm length between the grab and the loaded hang
    win = int(0.5 * fps); quiet = np.zeros(N, bool)
    for i in range(grab0 + win, loaded_f - win):
        seg = arm_px[i - win:i + win]
        quiet[i] = (seg.std() < 0.015 * seg.mean()) and abs(sh_y[i - win:i + win].std()) < 0.01 * H
    qruns = runs_of(quiet[:loaded_f], fps, 0.2)
    qruns = [r for r in qruns if r[0] >= grab0]
    if qruns:
        q0, q1 = max(qruns, key=lambda r: r[1] - r[0])
        stand_arm = float(np.median(arm_px[q0:q1 + 1])); stand_sh = float(np.median(sh_y[q0:q1 + 1]))
    else:
        stand_arm = hang_arm; stand_sh = hang_sh
    standing_first = (hang_arm - stand_arm) > 0.04 * stand_arm and (hang_sh - stand_sh) > 0.015 * H
    if standing_first:
        prog = np.clip(((arm_px - stand_arm) / (hang_arm - stand_arm) + (sh_y - stand_sh) / (hang_sh - stand_sh)) / 2, 0, 1)
        q_end = q1
        load0 = q_end + int(np.argmax(prog[q_end:loaded_f + 1] > 0.15))
        hang0 = q_end + int(np.argmax(prog[q_end:loaded_f + 1] > 0.85))
        print(f"standing with hands on the bar {t[grab0]:.2f}-{t[load0]:.2f}s, loading {t[load0]:.2f}-{t[hang0]:.2f}s "
              f"(arm +{(hang_arm/stand_arm-1)*100:.0f}%, shoulders sink {hang_sh-stand_sh:.0f}px), hanging from {t[hang0]:.2f}s")
    else:
        load0 = hang0 = grab0
        print(f"hanging from the grab at {t[grab0]:.2f}s")
    hang1 = grab1

    # --- scale (px/m) ---
    bot_frames = np.array(bottoms)
    scale_alt = {}
    if height:
        # The arm (shoulder joint -> wrist) at the loaded hang is straight, vertical, and spans exactly
        # the region the shoulders travel through, so it calibrates vertical px/m where it matters.
        arm_m = ARM_FRAC * height
        scale_arm = float(np.median(arm_px[bot_frames]) / arm_m)
        trunk_m = TRUNK_FRAC * height
        scale_trunk = float(np.median(trunk_px[bot_frames] / trunk_m))
        scale = np.full(N, scale_arm)
        scale_alt = dict(arm=scale_arm, trunk_at_bottom=scale_trunk, world_fit=float(np.nanmedian(scale_fit[bot_frames])))
        scale_note = (f"constant {scale_arm:.0f} px/m: shoulder-to-wrist at the loaded hang = {arm_m*100:.1f} cm "
                      f"(0.332 x {height:.2f} m). Alternatives: trunk-anchored {scale_trunk:.0f}, world-fit {scale_alt['world_fit']:.0f} px/m")
        print("scale:", scale_note)
    else:
        scale = scale_fit; scale_note = "per-frame fit between MediaPipe image and world landmarks"
    px_per_m = float(np.nanmedian(scale[hang0:hang1]))
    scale_hip = np.full(N, scale_alt.get("trunk_at_bottom", px_per_m))      # hips sit lower and closer to the camera than the arms

    # personal neck length: shoulder-mid -> chin while standing upright (first 2 s, face visible)
    stand = np.where((~hands_up[: int(2 * fps)]) & ok[: int(2 * fps)])[0]
    neck_px = np.nanmedian(np.linalg.norm(chin[stand] - sh[stand], axis=1))
    neck_cm = float(neck_px / np.nanmedian(scale_fit[stand]) * 100)     # local (world-fit) scale: standing body is closer to the camera
    print(f"shoulder-to-chin (standing): {neck_cm:.1f} cm")

    vy = -np.gradient(sh_y) * fps
    vy_m = vy / scale
    ay_m = smooth(np.gradient(vy_m) * fps, 9, 2)
    gap_cm = (sh_y - bar_y) / scale * 100
    chin_est_cm = neck_cm - gap_cm

    kp = np.load(yolo)["kp"] if yolo else None
    PERSPECTIVE_CM = 3.0
    hang_ref = float(np.median(sh_y[np.array(bottoms)]))         # 0 % height = loaded dead hang
    top_ref = float(min(sh_y[tp] for tp in tops))
    height_pct = (hang_ref - sh_y) / (hang_ref - top_ref) * 100

    m_lift = mass * LIFTED_FRAC if mass else None
    v_thr = 0.06 * px_per_m
    reps = []
    for k, top in enumerate(tops):
        b0, b1 = bottoms[k], bottoms[k + 1]
        amp = sh_y[b0] - sh_y[top]
        if amp < 0.35 * amp_ref:
            continue
        i = b0
        while i < top and vy[i] < v_thr: i += 1
        c_start = i
        i = top
        while i > c_start and vy[i] < v_thr: i -= 1
        c_end = i
        i = top
        while i < b1 and vy[i] > -v_thr: i += 1
        e_start = i
        i = e_start
        while i < b1 and vy[i] < -v_thr: i += 1
        e_end = i
        c_start, c_end = min(c_start, top), max(c_end, c_start + 1)
        e_start, e_end = max(e_start, top), max(e_end, e_start + 1)
        sl = slice(c_start, e_end + 1); conc = slice(c_start, c_end + 1); ecc = slice(e_start, e_end + 1)
        topw = slice(c_end, e_start + 1)
        legs_seen = float(np.nanmean(knee_vis[sl]))
        chin_cm = float(chin_est_cm[top])
        eyes_conf = float(kp[top - 3:top + 4, 1:3, 2].mean()) if kp is not None else None
        rom_m = float(amp / np.nanmean(scale[b0:top + 1]))
        rep = dict(
            n=len(reps) + 1,
            f_bottom0=int(b0), f_start=int(c_start), f_top=int(top), f_conc_end=int(c_end),
            f_ecc_start=int(e_start), f_end=int(e_end), f_bottom1=int(b1),
            t_start=float(t[c_start]), t_top=float(t[top]), t_end=float(t[e_end]),
            shoulder_gap_cm=float(gap_cm[top]), chin_est_cm=chin_cm,
            chin_at_bar=bool(chin_cm + PERSPECTIVE_CM >= 0), chin_over_bar=bool(chin_cm >= 0),
            chin_verdict=("above" if chin_cm + PERSPECTIVE_CM >= 1.0 else "at" if chin_cm + PERSPECTIVE_CM >= -1.0 else "short"),
            eyes_conf_top=eyes_conf, head_hidden_top=(eyes_conf is not None and eyes_conf < 0.3),
            nose_over_bar_line=bool(nose[top, 1] < bar_y),
            rom_px=float(amp), rom_cm=rom_m * 100,
            elbow_top=float(el3[top]), elbow_top_l=float(el3_l[top]), elbow_top_r=float(el3_r[top]),
            elbow_bottom_before=float(el3[b0]), elbow_bottom_after=float(el3[b1]),
            elbow_bottom_after_l=float(el3_l[b1]), elbow_bottom_after_r=float(el3_r[b1]),
            elbow2d_top=float((el2_l[top] + el2_r[top]) / 2),
            lockout=bool(el3[b1] >= 150),
            t_concentric=float((c_end - c_start) / fps), t_top_hold=float((e_start - c_end) / fps),
            t_eccentric=float((e_end - e_start) / fps), t_bottom_hold=0.0,
            t_cycle=float((bottoms[k + 1] - b0) / fps),
            peak_conc_v=float(np.nanmax(vy_m[conc])),
            mean_conc_v=float(rom_m / max((c_end - c_start) / fps, 1e-3)),
            peak_ecc_v=float(-np.nanmin(vy_m[ecc])),
            peak_acc=float(np.nanmax(ay_m[conc])),
            hip_sway_cm=float((np.nanmax(hip[sl, 0]) - np.nanmin(hip[sl, 0])) / np.nanmean(scale_hip[sl]) * 100),
            body_tilt_range=float(np.nanmax(body_tilt[sl]) - np.nanmin(body_tilt[sl])),
            body_tilt_max=float(np.nanmax(np.abs(body_tilt[sl]))),
            path_x_range_cm=float((np.nanmax(sh[sl, 0]) - np.nanmin(sh[sl, 0])) / np.nanmean(scale_hip[sl]) * 100),
            elbow_asym_mean=float(np.nanmean(np.abs(el3_l[sl] - el3_r[sl]))),
            elbow_asym_top=float(el3_l[top] - el3_r[top]),
            shoulder_tilt_range=float(np.nanmax(sh_tilt[sl]) - np.nanmin(sh_tilt[sl])),
            shoulder_tilt_top=float(sh_tilt[top]),
            knee_angle_min=float(np.nanmin(np.minimum(kn3_l[sl], kn3_r[sl]))) if legs_seen > 0.3 else None,
            hip_angle_min=float(np.nanmin(np.minimum(hp3_l[sl], hp3_r[sl]))) if legs_seen > 0.3 else None,
            hip_angle_top=float((hp3_l[top] + hp3_r[top]) / 2) if legs_seen > 0.3 else None,
            hip_angle_bottom=float((hp3_l[b1] + hp3_r[b1]) / 2) if legs_seen > 0.3 else None,
            legs_visible=legs_seen,
            # core / trunk (3D world)
            trunk_lean_top=float(trunk_lean[top]), trunk_lean_bottom=float(trunk_lean[b1]),
            trunk_lean_range=float(np.nanmax(trunk_lean[sl]) - np.nanmin(trunk_lean[sl])),
            yaw_top=float(yaw[top]), yaw_range=float(np.nanmax(yaw[sl]) - np.nanmin(yaw[sl])),
            lat_bend_top=float(lat_bend[top]), lat_bend_range=float(np.nanmax(lat_bend[sl]) - np.nanmin(lat_bend[sl])),
            lat_bend_absmax=float(np.nanmax(np.abs(lat_bend[sl]))),
            trunk_compress_pct=float((1 - trunk_len_w[top] / trunk_len_w[b1]) * 100),
            ear_shoulder_top_cm=float(np.linalg.norm(ear[top] - sh[top]) / scale[top] * 100),
            ear_shoulder_bottom_cm=float(np.linalg.norm(ear[b1] - sh[b1]) / scale[b1] * 100),
        )
        reps.append(rep)

    n = len(reps)
    for k, r in enumerate(reps):
        r["t_bottom_hold"] = float(reps[k + 1]["t_start"] - r["t_end"]) if k + 1 < n else 0.0
        r["t_under_tension"] = r["t_concentric"] + r["t_top_hold"] + r["t_eccentric"] + r["t_bottom_hold"]

    hang_frames = np.where(hands_up)[0]
    grip_w = np.nanmedian(np.linalg.norm(P[hang_frames, L_WR] - P[hang_frames, R_WR], axis=1))
    sh_w = np.nanmedian(sh_w_px[hang_frames])
    grip_ratio = float(grip_w / sh_w)

    # --- physics per rep (needs mass) ---
    peak_ref = max(r["peak_conc_v"] for r in reps)
    v_ref = max(r["mean_conc_v"] for r in reps)
    if mass:
        hang_power = HANG_MET * 3.5 * mass / 1000 * 5.0 / 60      # kcal/s: MET x 3.5 ml/kg/min x kg -> L/min x 5 kcal/L
        cum = 0.0
        for r in reps:
            w = m_lift * G * r["rom_cm"] / 100                       # J, concentric work on the lifted mass
            r["work_j"] = float(w)
            r["mean_power_w"] = float(w / r["t_concentric"])
            r["peak_power_w"] = float(m_lift * (G + max(r["peak_acc"], 0)) * r["peak_conc_v"])
            r["peak_force_n"] = float(m_lift * (G + max(r["peak_acc"], 0)))
            r["peak_force_bw"] = float(r["peak_force_n"] / (mass * G))
            # metabolic: concentric work / efficiency, eccentric at a fraction, plus isometric support for the whole cycle
            e_conc = w / ETA_CONC * KCAL_PER_J
            e_ecc = w * ECC_COST / ETA_CONC * KCAL_PER_J
            e_iso = hang_power * r["t_under_tension"]
            r["kcal_conc"] = float(e_conc); r["kcal_ecc"] = float(e_ecc); r["kcal_iso"] = float(e_iso)
            r["kcal"] = float(e_conc + e_ecc + e_iso)
            cum += r["kcal"]; r["kcal_cum"] = float(cum)
            # difficulty: force-velocity - same load, lower velocity = closer to max effort
            r["effort_x"] = float(v_ref / r["mean_conc_v"])
            vl = 1 - r["peak_conc_v"] / peak_ref
            r["velocity_loss_pct"] = float(vl * 100)
            r["est_rir"] = int(np.clip(round(5 - vl / 0.09), 0, 5))   # ~9 % velocity loss per rep in reserve, capped
        # dead hang and standing cost
        set_kcal = cum
        hang_before = (reps[0]["t_start"] - t[hang0]) * hang_power
        est_1rm_extra = m_lift * (1 + n / 30) - m_lift                  # Epley on the lifted mass
    else:
        set_kcal = hang_before = est_1rm_extra = None

    for r in reps:
        rom = 25 * float(np.clip(1 + (r["chin_est_cm"] + PERSPECTIVE_CM) / 10, 0, 1))
        lock = 15 * float(np.clip((r["elbow_bottom_after"] - 120) / 35, 0, 1))
        ctrl = 20 * float(np.clip(r["t_eccentric"] / 1.5, 0, 1))
        sway = 15 * float(np.clip(1 - (r["hip_sway_cm"] - 4) / 16, 0, 1))
        sym = 10 * float(np.clip(1 - (r["elbow_asym_mean"] - 5) / 20, 0, 1))
        vel = 15 * float(np.clip(r["peak_conc_v"] / peak_ref, 0, 1))
        r["score"] = dict(rom=rom, lockout=lock, control=ctrl, sway=sway, symmetry=sym, power=vel)
        r["efficiency"] = float(rom + lock + ctrl + sway + sym + vel)
        r["grade"] = "A" if r["efficiency"] >= 85 else "B" if r["efficiency"] >= 70 else "C" if r["efficiency"] >= 55 else "D"

    first_start = reps[0]["t_start"]
    summary = dict(
        reps=n, chin_over_bar=sum(r["chin_over_bar"] for r in reps), lockouts=sum(r["lockout"] for r in reps),
        chin_at_bar=sum(r["chin_at_bar"] for r in reps), head_hidden=sum(bool(r["head_hidden_top"]) for r in reps),
        chin_above=sum(r["chin_verdict"] == "above" for r in reps), chin_marginal=sum(r["chin_verdict"] == "at" for r in reps),
        chin_short=sum(r["chin_verdict"] == "short" for r in reps),
        perspective_cm=PERSPECTIVE_CM,
        grab_start=float(t[grab0]), load_start=float(t[load0]), hang_start=float(t[hang0]), hang_end=float(t[hang1]),
        standing_on_bar=float(t[load0] - t[grab0]), loading_duration=float(t[hang0] - t[load0]),
        hang_duration=float(t[hang1] - t[hang0]),
        dead_hang_before_first=float(first_start - t[hang0]),
        arm_stretch_pct=float((hang_arm / stand_arm - 1) * 100) if standing_first else 0.0,
        shoulder_sink_cm=float((hang_sh - stand_sh) / px_per_m * 100) if standing_first else 0.0,
        set_duration=float(reps[-1]["t_end"] - first_start),
        reps_per_min=float(n / (reps[-1]["t_end"] - first_start) * 60),
        mean_concentric=float(np.mean([r["t_concentric"] for r in reps])),
        mean_eccentric=float(np.mean([r["t_eccentric"] for r in reps])),
        mean_cycle=float(np.mean([r["t_cycle"] for r in reps[:-1]])) if n > 1 else 0.0,
        mean_efficiency=float(np.mean([r["efficiency"] for r in reps])),
        best_rep=int(max(reps, key=lambda r: r["efficiency"])["n"]),
        worst_rep=int(min(reps, key=lambda r: r["efficiency"])["n"]),
        peak_v_first=reps[0]["peak_conc_v"], peak_v_last=reps[-1]["peak_conc_v"], peak_v_max=peak_ref,
        velocity_loss_pct=float((1 - reps[-1]["peak_conc_v"] / peak_ref) * 100),
        mean_rom_cm=float(np.mean([r["rom_cm"] for r in reps])),
        mean_chin_est_cm=float(np.mean([r["chin_est_cm"] for r in reps])),
        neck_cm=neck_cm,
        mean_elbow_top=float(np.mean([r["elbow_top"] for r in reps])),
        mean_elbow_top_l=float(np.mean([r["elbow_top_l"] for r in reps])),
        mean_elbow_top_r=float(np.mean([r["elbow_top_r"] for r in reps])),
        mean_elbow_bottom=float(np.mean([r["elbow_bottom_after"] for r in reps])),
        mean_hip_sway_cm=float(np.mean([r["hip_sway_cm"] for r in reps])),
        mean_knee_min=float(np.mean([r["knee_angle_min"] for r in reps if r["knee_angle_min"] is not None])),
        mean_yaw_top=float(np.mean([r["yaw_top"] for r in reps])),
        mean_lat_bend_top=float(np.mean([r["lat_bend_top"] for r in reps])),
        mean_lat_bend_absmax=float(np.mean([r["lat_bend_absmax"] for r in reps])),
        mean_lat_bend_range=float(np.mean([r["lat_bend_range"] for r in reps])),
        mean_hip_angle_top=float(np.mean([r["hip_angle_top"] for r in reps if r["hip_angle_top"] is not None])),
        grip_ratio=grip_ratio, grip_width_cm=float(grip_w / px_per_m * 100), shoulder_width_cm=float(sh_w / px_per_m * 100),
        px_per_m=px_per_m, scale_note=scale_note, scale_alt=scale_alt,
        rom_cm_alt={k: float(np.mean([r["rom_px"] for r in reps]) / v * 100) for k, v in scale_alt.items()}, bar_y=int(bar_y), hang_ref_y=hang_ref, top_ref_y=top_ref,
        tracked_frames=int(ok.sum()), frames=N, fps=fps, height_m=height, mass_kg=mass,
    )
    if n >= 3:
        summary["velocity_slope"] = float(np.polyfit(range(n), [r["peak_conc_v"] for r in reps], 1)[0])
        summary["concentric_slope"] = float(np.polyfit(range(n), [r["t_concentric"] for r in reps], 1)[0])
    if mass:
        summary.update(dict(
            lifted_mass_kg=float(m_lift), work_per_rep_j=float(np.mean([r["work_j"] for r in reps])),
            set_work_kj=float(sum(r["work_j"] for r in reps) / 1000),
            set_kcal=float(set_kcal), hang_kcal_before=float(hang_before), set_kcal_total=float(set_kcal + hang_before),
            mean_power_w_first=reps[0]["mean_power_w"], mean_power_w_last=reps[-1]["mean_power_w"],
            peak_power_w_max=float(max(r["peak_power_w"] for r in reps)),
            peak_force_bw_max=float(max(r["peak_force_bw"] for r in reps)),
            effort_x_last=reps[-1]["effort_x"], est_rir_last=reps[-1]["est_rir"],
            est_1rm_extra_kg=float(est_1rm_extra), bmi=float(mass / height ** 2) if height else None,
            hang_kcal_per_s=float(hang_power),
            model=dict(lifted_frac=LIFTED_FRAC, eta_conc=ETA_CONC, ecc_cost=ECC_COST, hang_met=HANG_MET),
        ))

    if yolo:
        ysh = np.where((kp[:, 5, 2] > 0.3) & (kp[:, 6, 2] > 0.3), (kp[:, 5, 1] + kp[:, 6, 1]) / 2, np.nan)
        ysh = smooth(ysh, 9, 2)
        yt, _ = find_peaks(-ysh[grab0:grab1], prominence=amp_ref * 0.5, distance=int(0.6 * fps))
        summary["yolo_reps"] = int(len(yt)); summary["yolo_tops"] = [float(t[grab0 + i]) for i in yt]
        m = ~np.isnan(ysh)
        summary["yolo_mp_shoulder_corr"] = float(np.corrcoef(sh_y[m], ysh[m])[0, 1])
        summary["yolo_mp_shoulder_mad_px"] = float(np.nanmedian(np.abs(sh_y[m] - ysh[m])))
        summary["yolo_frames"] = int(m.sum())

    signals = dict(t=t.tolist(), sh_y=sh_y.tolist(), height_pct=np.nan_to_num(height_pct).tolist(),
                   gap_cm=np.nan_to_num(gap_cm).tolist(), chin_est_cm=np.nan_to_num(chin_est_cm).tolist(),
                   vy_m=np.nan_to_num(vy_m).tolist(), elbow_l=el3_l.tolist(), elbow_r=el3_r.tolist(),
                   body_tilt=np.nan_to_num(body_tilt).tolist(), hip_x=np.nan_to_num(hip[:, 0]).tolist(),
                   scale=np.nan_to_num(scale).tolist(), knee_l=kn3_l.tolist(), knee_r=kn3_r.tolist(),
                   sh_x=sh[:, 0].tolist(), arm_px=arm_px.tolist(), trunk_lean=np.nan_to_num(trunk_lean).tolist(),
                   yaw=np.nan_to_num(yaw).tolist(), lat_bend=np.nan_to_num(lat_bend).tolist(),
                   tops=[int(x) for x in tops], bottoms=[int(x) for x in bottoms],
                   grab0=int(grab0), load0=int(load0), hang0=int(hang0), hang1=int(hang1))
    json.dump(dict(summary=summary, reps=reps, signals=signals), open(out, "w"), indent=1)

    print(f"\nREPS: {n}  (chin at bar {summary['chin_at_bar']}, lockouts {summary['lockouts']})")
    for r in reps:
        kn = "n/a" if r["knee_angle_min"] is None else f"{r['knee_angle_min']:.0f}"
        phys = f"  {r['work_j']:.0f}J {r['mean_power_w']:.0f}W {r['kcal']:.2f}kcal x{r['effort_x']:.2f} RIR{r['est_rir']}" if mass else ""
        print(f" #{r['n']:2d} top {r['t_top']:5.2f}s chin {r['chin_est_cm']:+5.1f} ROM {r['rom_cm']:3.0f}cm elb L{r['elbow_top_l']:3.0f}/R{r['elbow_top_r']:3.0f} bot {r['elbow_bottom_after']:3.0f} "
              f"up {r['t_concentric']:.2f} hold {r['t_top_hold']:.2f} down {r['t_eccentric']:.2f} rest {r['t_bottom_hold']:.2f} v {r['peak_conc_v']:.2f} "
              f"sway {r['hip_sway_cm']:4.1f} lean {r['trunk_lean_top']:+4.0f} yaw {r['yaw_top']:+3.0f} latb {r['lat_bend_top']:+3.0f} knee {kn} eff {r['efficiency']:3.0f}{r['grade']}{phys}")
    print(json.dumps({k: v for k, v in summary.items() if k not in ('yolo_tops', 'model')}, indent=1))


if __name__ == "__main__":
    main()
