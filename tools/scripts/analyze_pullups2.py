"""
Pull-up biomechanics, version 2 (level frontal camera, de-rolled footage).

    python analyze_pullups2.py <video> <pose_mp.npz> <analysis.json> [pose_yolo.npz]
                               [height=1.88] [mass=79] [bar_frames=30,60,90]

What is different from analyze_pullups.py (which stays as-is for the first video):
  * hang onset from the FEET (ankles are in frame here), arms as fallback;
  * phase boundaries from POSITION (5 % / 95 % of each rep's amplitude), not velocity
    thresholds - the velocity walker collapsed on rep 3 of this clip;
  * vertical scale anchored on the STANDING stature at the bar plane, arm as second opinion;
  * the bar is fitted as a LINE (the camera has yaw, so the bar's image is tilted ~3 deg);
    every height-vs-bar is measured against the bar line at that point's own x;
  * chin built along the FACE AXIS (eye midpoint -> mouth midpoint, extended by 0.60): at the
    top of a rep the head is tilted right back, so a fixed nose-to-chin drop measured standing
    is far too pessimistic. The face-axis construction absorbs head pitch and foreshortening
    together, and it agrees with the independent shoulder-anchored estimate to ~1 cm;
  * a failed attempt is not a rep;
  * a full left/right asymmetry suite in the image plane (the de-rolled image plane is
    gravity-aligned; MediaPipe's 3D is a model estimate and is reported as such);
  * technique checks against the USMC PFT pull-up standard;
  * per-rep heat production for the thermal model (pullup_thermal.py).
"""
import sys, json
import numpy as np
import cv2
from scipy.signal import savgol_filter, find_peaks

NOSE = 0; L_EYE, R_EYE = 2, 5; L_EAR, R_EAR = 7, 8; L_MOUTH, R_MOUTH = 9, 10
L_SH, R_SH = 11, 12; L_EL, R_EL = 13, 14; L_WR, R_WR = 15, 16
L_HIP, R_HIP = 23, 24; L_KNEE, R_KNEE = 25, 26; L_ANK, R_ANK = 27, 28
G = 9.81
ARM_FRAC = 0.332          # shoulder joint -> wrist / stature (Drillis & Contini 1966)
EYE_FRAC = 0.936          # eye height / stature, standing
ANK_FRAC = 0.039          # lateral malleolus height / stature
SH_FRAC = 0.818           # shoulder (acromion) height / stature
LIFTED_FRAC = 0.956       # body mass minus hands+forearms, which stay at the bar (Dempster)
ETA_CONC = 0.22           # metabolic efficiency of concentric muscle work
ECC_COST = 0.35           # eccentric metabolic cost relative to the same concentric work
HANG_MET = 3.5            # isometric bar hang, METs (rough)
KCAL_PER_J = 1 / 4184.0
FAIL_CHIN_CM = 10.0       # an attempt that stalls this far short of the bar is not a rep
CHIN_AXIS_K = 0.60        # mouth-to-chin / eye-to-mouth along the face axis (adult face
                          # proportions: stomion-menton ~4.3 cm, pupil-stomion ~7.1 cm)
CHIN_SIGMA_CM = 1.5       # honest uncertainty on every chin number
VERDICT_BAND_CM = 1.5     # |chin| within this = "at the bar"


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


def fit_bar(video, frames, W, H):
    """Fit the bar as a line y = a*x + b on empty frames (the camera has yaw, so the bar
    is not horizontal in the image even after the roll is removed)."""
    cap = cv2.VideoCapture(video)
    fits = []
    for fr in frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, fr); ok, f = cap.read()
        if not ok:
            continue
        g = cv2.GaussianBlur(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (0, 0), 1.0).astype(np.float32)
        pts = []
        for x in range(int(0.37 * W), int(0.93 * W), 2):
            col = g[90:230, x]
            d = -np.diff(col)                      # bright -> dark going down = the bar's top edge
            k = int(np.argmax(d))
            if d[k] < 10:
                continue
            a_, b_, c_ = d[max(k - 1, 0)], d[k], d[min(k + 1, len(d) - 1)]
            den = a_ - 2 * b_ + c_
            sub = (a_ - c_) / (2 * den) if den != 0 else 0.0
            pts.append((x, 90 + k + 0.5 + sub))
        pts = np.array(pts, float)
        if len(pts) < 30:
            continue
        for _ in range(3):
            B = np.polyfit(pts[:, 0], pts[:, 1], 1)
            r = pts[:, 1] - np.polyval(B, pts[:, 0])
            pts = pts[np.abs(r) < max(2.0, 2.5 * r.std())]
        B = np.polyfit(pts[:, 0], pts[:, 1], 1)
        fits.append((B[0], B[1], float((pts[:, 1] - np.polyval(B, pts[:, 0])).std()), len(pts)))
    cap.release()
    F = np.array(fits)
    a, b = float(np.median(F[:, 0])), float(np.median(F[:, 1]))
    print(f"bar line: y = {a:+.5f} x + {b:.1f}  ({np.degrees(np.arctan(a)):+.2f} deg in the image, "
          f"which is camera yaw: the bar is a level world line), {len(F)} frames, "
          f"resid {np.median(F[:, 2]):.2f} px")
    return a, b


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
    yolo = None; height = None; mass = None; bar_frames = list(range(0, 140, 10))
    for a in sys.argv[4:]:
        if a.startswith("height="):
            height = float(a[7:])
        elif a.startswith("mass="):
            mass = float(a[5:])
        elif a.startswith("bar_frames="):
            bar_frames = [int(x) for x in a[11:].split(",")]
        else:
            yolo = a
    d = np.load(npz)
    fps = float(d["fps"]); W = int(d["width"]); H = int(d["height"])
    img = d["img"]; world = d["world"]; ok = d["ok"]
    N = len(img); t = np.arange(N) / fps
    P = img[:, :, :2] * np.array([W, H], dtype=np.float32)
    V = img[:, :, 3]

    def mid(a, b):
        return (P[:, a] + P[:, b]) / 2

    nose = P[:, NOSE]; mouth = mid(L_MOUTH, R_MOUTH)
    eye_m = mid(L_EYE, R_EYE)
    chin_pt = mouth + CHIN_AXIS_K * (mouth - eye_m)     # down the face axis
    sh = mid(L_SH, R_SH); hip = mid(L_HIP, R_HIP); ear = mid(L_EAR, R_EAR)
    wr = mid(L_WR, R_WR); ank = mid(L_ANK, R_ANK); eye = mid(L_EYE, R_EYE)
    sh_w_px = smooth(np.linalg.norm(P[:, L_SH] - P[:, R_SH], axis=1), 15, 2)
    arm_px = smooth((np.linalg.norm(P[:, L_SH] - P[:, L_WR], axis=1)
                     + np.linalg.norm(P[:, R_SH] - P[:, R_WR], axis=1)) / 2, 15, 2)
    lx = float(np.nanmean(P[ok, L_SH, 0])); rx = float(np.nanmean(P[ok, R_SH, 0]))
    print(f"landmark 11 (person's LEFT) mean x {lx:.0f}, 12 (RIGHT) {rx:.0f} -> person's left is "
          f"on the image {'right' if lx > rx else 'left'} (mirror view, as expected facing the camera)")

    bar_a, bar_b = fit_bar(video, bar_frames, W, H)

    def bar_y_at(x):
        return bar_a * np.asarray(x, float) + bar_b

    # ---------- joint angles ----------
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

    # image-plane line tilts. The frame is de-rolled, so image vertical = world vertical.
    # Sign: negative = the person's RIGHT side (image left) is higher.
    def line_tilt(a, b):
        v = P[:, b] - P[:, a]
        raw = np.degrees(np.arctan2(v[:, 1], v[:, 0]))
        return smooth(np.where(raw > 0, raw - 180, raw + 180), 9, 2)

    sh_tilt = line_tilt(L_SH, R_SH)
    hip_tilt = line_tilt(L_HIP, R_HIP)
    wr_tilt = line_tilt(L_WR, R_WR)
    ear_tilt = line_tilt(L_EAR, R_EAR)
    lat_bend = smooth(sh_tilt - hip_tilt, 9, 2)

    # ---------- hands on the bar, attempt tops ----------
    hands_up = (P[:, L_WR, 1] < P[:, L_SH, 1]) & (P[:, R_WR, 1] < P[:, R_SH, 1]) & ok
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

    # ---------- hang onset from the FEET ----------
    pre = np.where((V[:tops[0], L_ANK] > 0.5) & (V[:tops[0], R_ANK] > 0.5)
                   & ok[:tops[0]] & hands_up[:tops[0]])[0]
    feet_method = False
    load0 = hang0 = grab0
    if len(pre) > int(1.5 * fps):
        floor_y = float(np.median(ank[pre, 1]))
        stand_mask = np.zeros(N, bool)
        stand_mask[pre] = np.abs(ank[pre, 1] - floor_y) < 0.012 * H
        sruns = [r for r in runs_of(stand_mask, fps, 0.3) if r[1] - r[0] > 0.8 * fps]
        if sruns:
            q0, q1 = max(sruns, key=lambda r: r[1] - r[0])
            lift = q1
            while lift < tops[0] and ank[lift, 1] > floor_y - 0.025 * H:
                lift += 1
            load0, hang0 = q1, lift
            feet_method = True
            print(f"standing on the floor with the hands on the bar {t[grab0]:.2f}-{t[q1]:.2f} s "
                  f"(ankles at y {floor_y:.0f} px), feet leave the floor at {t[lift]:.2f} s, "
                  f"loaded hang {t[lift]:.2f}-{t[grab1]:.2f} s")
    if not feet_method:
        print(f"feet not usable; hanging assumed from the grab at {t[grab0]:.2f} s")
    hang1 = grab1

    # ---------- scale ----------
    stand = np.arange(grab0, max(load0, grab0 + 1))
    stand = stand[(V[stand, L_ANK] > 0.5) & (V[stand, NOSE] > 0.5)]
    scale_alt = {}
    if height and len(stand) > 10:
        eye_ank = float(np.median(ank[stand, 1] - eye[stand, 1]))
        sh_ank = float(np.median(ank[stand, 1] - sh[stand, 1]))
        s_stature = eye_ank / ((EYE_FRAC - ANK_FRAC) * height)
        s_shoulder = sh_ank / ((SH_FRAC - ANK_FRAC) * height)
        s_arm = float(np.median(arm_px[np.array(bottoms)]) / (ARM_FRAC * height))
        scale_alt = dict(stature_eye_ankle=s_stature, stature_shoulder_ankle=s_shoulder,
                         arm_at_hang=s_arm)
        px_per_m = s_stature
        scale_note = (f"{px_per_m:.0f} px/m from the standing stature at the bar plane (eye-to-ankle "
                      f"{eye_ank:.0f} px = {(EYE_FRAC - ANK_FRAC) * height * 100:.1f} cm). Alternatives: "
                      f"shoulder-to-ankle {s_shoulder:.0f}, arm at the hang {s_arm:.0f} px/m")
    else:
        px_per_m = float(np.median(arm_px[np.array(bottoms)]) / (ARM_FRAC * height))
        scale_alt = dict(arm_at_hang=px_per_m)
        scale_note = f"{px_per_m:.0f} px/m from the arm at the hang"
    print("scale:", scale_note)

    # ---------- personal offsets, measured standing ----------
    nose_chin_px = float(np.median(np.linalg.norm(chin_pt[stand] - nose[stand], axis=1))) if len(stand) else 0.0
    nose_chin_cm = nose_chin_px / px_per_m * 100
    face_axis_cm = float(np.median(np.linalg.norm(mouth[stand] - eye_m[stand], axis=1))) / px_per_m * 100 if len(stand) else 0.0
    sh_chin_cm = float(np.median(chin_pt[stand, 1] - sh[stand, 1])) / px_per_m * 100 if len(stand) else 0.0
    ear_sh_stand_l = float(np.median(np.linalg.norm(P[stand, L_EAR] - P[stand, L_SH], axis=1))) / px_per_m * 100
    ear_sh_stand_r = float(np.median(np.linalg.norm(P[stand, R_EAR] - P[stand, R_SH], axis=1))) / px_per_m * 100
    nose_ear_stand = float(np.median(ear[stand, 1] - nose[stand, 1])) / px_per_m * 100
    sh_tilt_stand = float(np.median(sh_tilt[stand]))
    print(f"standing: eye-to-mouth {face_axis_cm:.1f} cm, nose-to-chin {nose_chin_cm:.1f} cm, shoulder-to-chin {sh_chin_cm:.1f} cm, "
          f"ear-to-shoulder L {ear_sh_stand_l:.1f} / R {ear_sh_stand_r:.1f} cm, nose above the ear "
          f"line {nose_ear_stand:.1f} cm, shoulder tilt {sh_tilt_stand:+.2f} deg")

    chin_y = chin_pt[:, 1]
    chin_gap_cm = (bar_y_at(chin_pt[:, 0]) - chin_y) / px_per_m * 100      # + = chin above the bar
    sh_gap_cm = (bar_y_at(sh[:, 0]) - sh[:, 1]) / px_per_m * 100
    chin_from_sh_cm = sh_gap_cm - sh_chin_cm

    kp = np.load(yolo)["kp"] if yolo else None
    vy = -np.gradient(sh_y) * fps
    vy_m = vy / px_per_m
    ay_m = smooth(np.gradient(vy_m) * fps, 9, 2)
    hang_ref = float(np.median(sh_y[np.array(bottoms)]))
    top_ref = float(min(sh_y[tp] for tp in tops))
    height_pct = (hang_ref - sh_y) / (hang_ref - top_ref) * 100

    m_lift = mass * LIFTED_FRAC if mass else None
    attempts = []
    for k, top in enumerate(tops):
        b0, b1 = bottoms[k], bottoms[k + 1]
        base_y = float(max(sh_y[b0], sh_y[b1]))
        amp = base_y - sh_y[top]
        if amp < 0.35 * amp_ref:
            continue
        hi = base_y - 0.95 * amp
        lo = base_y - 0.05 * amp
        c_start = top
        while c_start > b0 and sh_y[c_start] < lo:
            c_start -= 1
        c_end = c_start
        while c_end < top and sh_y[c_end] > hi:
            c_end += 1
        e_start = top
        while e_start < b1 and sh_y[e_start] < hi:
            e_start += 1
        e_end = e_start
        while e_end < b1 and sh_y[e_end] < lo:
            e_end += 1
        c_end = max(c_end, c_start + 1)
        e_end = max(e_end, e_start + 1)
        sl = slice(c_start, e_end + 1); conc = slice(c_start, c_end + 1); ecc = slice(e_start, e_end + 1)
        legs_seen = float(np.nanmean(knee_vis[sl]))
        chin_cm = float(chin_gap_cm[top]); chin_alt = float(chin_from_sh_cm[top])
        rom_m = float(amp / px_per_m)
        nose_c = float(kp[top - 2:top + 3, 0, 2].mean()) if kp is not None else None
        gc = (P[top, L_WR, 0] + P[top, R_WR, 0]) / 2
        a = dict(
            n=len(attempts) + 1,
            f_bottom0=int(b0), f_start=int(c_start), f_top=int(top), f_conc_end=int(c_end),
            f_ecc_start=int(e_start), f_end=int(e_end), f_bottom1=int(b1),
            t_start=float(t[c_start]), t_top=float(t[top]), t_end=float(t[e_end]),
            chin_cm=chin_cm, chin_cm_from_shoulder=chin_alt,
            chin_verdict=("above" if chin_cm >= VERDICT_BAND_CM else
                          "at" if chin_cm >= -VERDICT_BAND_CM else "short"),
            failed=bool(chin_cm < -FAIL_CHIN_CM),
            nose_conf_top=nose_c,
            rom_px=float(amp), rom_cm=rom_m * 100,
            elbow_top=float(el3[top]), elbow_top_l=float(el3_l[top]), elbow_top_r=float(el3_r[top]),
            elbow2d_top_l=float(el2_l[top]), elbow2d_top_r=float(el2_r[top]),
            elbow_bottom_after=float(el3[b1]), elbow2d_bottom_after=float((el2_l[b1] + el2_r[b1]) / 2),
            lockout=bool(el3[b1] >= 150 and (el2_l[b1] + el2_r[b1]) / 2 >= 160),
            t_concentric=float((c_end - c_start) / fps), t_top_hold=float((e_start - c_end) / fps),
            t_eccentric=float((e_end - e_start) / fps), t_bottom_hold=0.0,
            t_cycle=float((b1 - b0) / fps),
            peak_conc_v=float(np.nanmax(vy_m[conc])),
            mean_conc_v=float(rom_m / max((c_end - c_start) / fps, 1e-3)),
            peak_ecc_v=float(-np.nanmin(vy_m[ecc])), peak_acc=float(np.nanmax(ay_m[conc])),
            hip_sway_cm=float((np.nanmax(hip[sl, 0]) - np.nanmin(hip[sl, 0])) / px_per_m * 100),
            knee_range=(float(np.nanmax(np.minimum(kn3_l[conc], kn3_r[conc]))
                              - np.nanmin(np.minimum(kn3_l[conc], kn3_r[conc]))) if legs_seen > 0.3 else None),
            hip_angle_range=(float(np.nanmax(np.minimum(hp3_l[conc], hp3_r[conc]))
                                   - np.nanmin(np.minimum(hp3_l[conc], hp3_r[conc]))) if legs_seen > 0.3 else None),
            knee_angle_min=float(np.nanmin(np.minimum(kn3_l[sl], kn3_r[sl]))) if legs_seen > 0.3 else None,
            hip_angle_top=float((hp3_l[top] + hp3_r[top]) / 2) if legs_seen > 0.3 else None,
            legs_visible=legs_seen,
            # ---- asymmetry, image plane (de-rolled, so gravity aligned) ----
            sh_tilt_top=float(sh_tilt[top]), sh_tilt_bottom=float(sh_tilt[b1]),
            hip_tilt_top=float(hip_tilt[top]), wr_tilt_top=float(wr_tilt[top]),
            ear_tilt_top=float(ear_tilt[top]),
            sh_dy_top_cm=float((P[top, L_SH, 1] - P[top, R_SH, 1]) / px_per_m * 100),
            sh_dy_bottom_cm=float((P[b1, L_SH, 1] - P[b1, R_SH, 1]) / px_per_m * 100),
            el_dy_top_cm=float((P[top, L_EL, 1] - P[top, R_EL, 1]) / px_per_m * 100),
            ear_sh_top_l=float(np.linalg.norm(P[top, L_EAR] - P[top, L_SH]) / px_per_m * 100),
            ear_sh_top_r=float(np.linalg.norm(P[top, R_EAR] - P[top, R_SH]) / px_per_m * 100),
            ear_sh_hang_l=float(np.linalg.norm(P[b1, L_EAR] - P[b1, L_SH]) / px_per_m * 100),
            ear_sh_hang_r=float(np.linalg.norm(P[b1, R_EAR] - P[b1, R_SH]) / px_per_m * 100),
            nose_above_ear_top_cm=float((ear[top, 1] - nose[top, 1]) / px_per_m * 100),
            wrist_off_l_cm=float((P[top, L_WR, 0] - gc) / px_per_m * 100),
            wrist_off_r_cm=float((P[top, R_WR, 0] - gc) / px_per_m * 100),
            hip_off_top_cm=float((hip[top, 0] - gc) / px_per_m * 100),
            sh_off_top_cm=float((sh[top, 0] - gc) / px_per_m * 100),
            hip_off_hang_cm=float((hip[b1, 0] - (P[b1, L_WR, 0] + P[b1, R_WR, 0]) / 2) / px_per_m * 100),
            lat_bend_top=float(lat_bend[top]),
            lat_bend_absmax=float(np.nanmax(np.abs(lat_bend[sl]))),
            elbow_asym_mean_3d=float(np.nanmean(np.abs(el3_l[sl] - el3_r[sl]))),
            elbow_asym_mean_2d=float(np.nanmean(np.abs(el2_l[sl] - el2_r[sl]))),
        )
        cl, cr = el3_l[conc], el3_r[conc]
        if len(cl) > 9:
            cls = cl - cl.mean(); crs = cr - cr.mean()
            scores = [float((cls * np.roll(crs, s)).sum()) for s in range(-4, 5)]
            lag = int(np.argmax(scores)) - 4
            a["elbow_lag_frames"] = lag
            a["elbow_lag_ms"] = float(lag / fps * 1000)
            a["lead_arm"] = ("left" if np.argmin(cl) < np.argmin(cr)
                             else "right" if np.argmin(cr) < np.argmin(cl) else "together")
        f = c_start
        while f < top and min(el3_l[f], el3_r[f]) > 150:
            f += 1
        a["scap_phase_cm"] = float((sh_y[c_start] - sh_y[f]) / px_per_m * 100)
        a["scap_phase_s"] = float((f - c_start) / fps)
        attempts.append(a)

    n_att = len(attempts)
    for k, a in enumerate(attempts):
        a["t_bottom_hold"] = float(attempts[k + 1]["t_start"] - a["t_end"]) if k + 1 < n_att else 0.0
        a["t_under_tension"] = a["t_concentric"] + a["t_top_hold"] + a["t_eccentric"] + a["t_bottom_hold"]
    reps = [a for a in attempts if not a["failed"]]
    fails = [a for a in attempts if a["failed"]]
    for i, r in enumerate(reps):
        r["rep"] = i + 1
    for a in fails:
        a["rep"] = None
    n = len(reps)

    hang_frames = np.where(hands_up)[0]
    grip_w = float(np.median(np.linalg.norm(P[hang_frames, L_WR] - P[hang_frames, R_WR], axis=1)))
    sh_w = float(np.median(sh_w_px[hang_frames]))
    grip_ratio = grip_w / sh_w

    # ---------- physics ----------
    peak_ref = max(r["peak_conc_v"] for r in reps)
    v_ref = max(r["mean_conc_v"] for r in reps)
    set_kcal = hang_before = est_1rm_extra = None
    if mass:
        hang_power = HANG_MET * 3.5 * mass / 1000 * 5.0 / 60      # kcal/s
        cum = 0.0
        for a in attempts:
            w = m_lift * G * a["rom_cm"] / 100
            a["work_j"] = float(w)
            a["mean_power_w"] = float(w / a["t_concentric"])
            a["peak_power_w"] = float(m_lift * (G + max(a["peak_acc"], 0)) * a["peak_conc_v"])
            a["peak_force_n"] = float(m_lift * (G + max(a["peak_acc"], 0)))
            a["peak_force_bw"] = float(a["peak_force_n"] / (mass * G))
            e_conc = w / ETA_CONC * KCAL_PER_J
            e_ecc = w * ECC_COST / ETA_CONC * KCAL_PER_J
            e_iso = hang_power * a["t_under_tension"]
            a["kcal_conc"] = float(e_conc); a["kcal_ecc"] = float(e_ecc); a["kcal_iso"] = float(e_iso)
            a["kcal"] = float(e_conc + e_ecc + e_iso)
            cum += a["kcal"]; a["kcal_cum"] = float(cum)
            # heat = metabolic energy spent minus the mechanical work done on the body's own mass
            a["heat_j"] = float(a["kcal"] / KCAL_PER_J - w)
            a["effort_x"] = float(v_ref / a["mean_conc_v"])
            vl = 1 - a["peak_conc_v"] / peak_ref
            a["velocity_loss_pct"] = float(vl * 100)
            a["est_rir"] = int(np.clip(round(5 - vl / 0.09), 0, 5))
        set_kcal = cum
        hang_before = (attempts[0]["t_start"] - t[hang0]) * hang_power
        est_1rm_extra = m_lift * (1 + n / 30) - m_lift

    for a in attempts:
        rom = 25 * float(np.clip(1 + a["chin_cm"] / 10, 0, 1))
        lock = 15 * float(np.clip((a["elbow_bottom_after"] - 120) / 35, 0, 1))
        ctrl = 20 * float(np.clip(a["t_eccentric"] / 1.5, 0, 1))
        sway = 15 * float(np.clip(1 - (a["hip_sway_cm"] - 4) / 16, 0, 1))
        sym = 10 * float(np.clip(1 - (abs(a["sh_dy_top_cm"]) - 1) / 4, 0, 1))
        vel = 15 * float(np.clip(a["peak_conc_v"] / peak_ref, 0, 1))
        a["score"] = dict(rom=rom, lockout=lock, control=ctrl, sway=sway, symmetry=sym, power=vel)
        a["efficiency"] = float(rom + lock + ctrl + sway + sym + vel)

    # ---------- per-frame phase ----------
    phase = np.array(["SETUP"] * N, dtype=object)
    phase[grab0:load0] = "HANDS ON BAR"
    phase[load0:hang0] = "LOADING"
    phase[hang0:hang1 + 1] = "HANG"
    for a in attempts:
        phase[a["f_start"]:a["f_conc_end"] + 1] = "PULL"
        phase[a["f_conc_end"]:a["f_ecc_start"] + 1] = "HOLD"
        phase[a["f_ecc_start"]:a["f_end"] + 1] = "LOWER"
    phase[hang1 + 1:] = "DONE"

    # ---------- set-level asymmetry ----------
    def mstat(key, src=reps):
        v = [r[key] for r in src if r.get(key) is not None]
        return float(np.mean(v)) if v else None

    asym = dict(
        sh_tilt_top_deg=mstat("sh_tilt_top"), sh_tilt_bottom_deg=mstat("sh_tilt_bottom"),
        sh_tilt_standing_deg=sh_tilt_stand,
        sh_dy_top_cm=mstat("sh_dy_top_cm"), sh_dy_bottom_cm=mstat("sh_dy_bottom_cm"),
        el_dy_top_cm=mstat("el_dy_top_cm"), hip_tilt_top_deg=mstat("hip_tilt_top"),
        wr_tilt_top_deg=mstat("wr_tilt_top"), ear_tilt_top_deg=mstat("ear_tilt_top"),
        ear_sh_top_l=mstat("ear_sh_top_l"), ear_sh_top_r=mstat("ear_sh_top_r"),
        ear_sh_hang_l=mstat("ear_sh_hang_l"), ear_sh_hang_r=mstat("ear_sh_hang_r"),
        ear_sh_stand_l=ear_sh_stand_l, ear_sh_stand_r=ear_sh_stand_r,
        wrist_off_l_cm=mstat("wrist_off_l_cm"), wrist_off_r_cm=mstat("wrist_off_r_cm"),
        hip_off_top_cm=mstat("hip_off_top_cm"), sh_off_top_cm=mstat("sh_off_top_cm"),
        hip_off_hang_cm=mstat("hip_off_hang_cm"),
        elbow_top_l_3d=mstat("elbow_top_l"), elbow_top_r_3d=mstat("elbow_top_r"),
        elbow_top_l_2d=mstat("elbow2d_top_l"), elbow_top_r_2d=mstat("elbow2d_top_r"),
        elbow_asym_3d=mstat("elbow_asym_mean_3d"), elbow_asym_2d=mstat("elbow_asym_mean_2d"),
        elbow_lag_ms=mstat("elbow_lag_ms"),
        lead_arm_counts={s: sum(1 for r in reps if r.get("lead_arm") == s)
                         for s in ("left", "right", "together")},
        nose_above_ear_top_cm=mstat("nose_above_ear_top_cm"), nose_above_ear_standing_cm=nose_ear_stand,
        scap_phase_cm=mstat("scap_phase_cm"), scap_phase_s=mstat("scap_phase_s"),
        grip_ratio=grip_ratio, grip_width_cm=grip_w / px_per_m * 100,
        shoulder_width_cm=sh_w / px_per_m * 100,
    )

    def sym_index(l, r):
        return float(abs(l - r) / ((l + r) / 2) * 100) if l and r else None

    asym["ear_sh_top_index_pct"] = sym_index(asym["ear_sh_top_l"], asym["ear_sh_top_r"])
    asym["elbow_3d_index_pct"] = sym_index(asym["elbow_top_l_3d"], asym["elbow_top_r_3d"])
    asym["elbow_2d_index_pct"] = sym_index(asym["elbow_top_l_2d"], asym["elbow_top_r_2d"])
    asym["sh_tilt_top_minus_standing_deg"] = asym["sh_tilt_top_deg"] - sh_tilt_stand
    asym["elbow_3d_2d_disagree"] = bool(
        abs((asym["elbow_top_l_3d"] - asym["elbow_top_r_3d"])
            - (asym["elbow_top_l_2d"] - asym["elbow_top_r_2d"])) > 10)

    # ---------- technique (USMC PFT pull-up standard) ----------
    kn_r = [r["knee_range"] for r in reps if r["knee_range"] is not None]
    hp_r = [r["hip_angle_range"] for r in reps if r["hip_angle_range"] is not None]
    tech = dict(
        standard=("USMC PFT pull-up: dead hang with the arms fully extended; chin above the bar; "
                  "lower to full extension; no kipping, kicking or leg movement"),
        reps_counted=n, failed_attempts=len(fails),
        chin_above=sum(r["chin_verdict"] == "above" for r in reps),
        chin_at=sum(r["chin_verdict"] == "at" for r in reps),
        chin_short=sum(r["chin_verdict"] == "short" for r in reps),
        lockouts=sum(r["lockout"] for r in reps),
        knee_range_mean=float(np.mean(kn_r)) if kn_r else None,
        hip_range_mean=float(np.mean(hp_r)) if hp_r else None,
        # A kip is a SWING: the body arcs forward and back to throw the hips up. That shows as
        # horizontal hip travel, not as a hip-angle change - a strict puller with tucked legs
        # still flexes the hip as the torso rises past the thighs. Checked by eye on the frame
        # strips for reps 3 and 10: no arch-to-hollow swing, but the knees do tuck up each pull.
        kip=bool(mstat("hip_sway_cm") > 8.0),
        leg_tuck_deg=float(np.mean(hp_r)) if hp_r else None,
        knee_swing_deg=float(np.mean(kn_r)) if kn_r else None,
        hip_sway_mean_cm=mstat("hip_sway_cm"),
        mean_eccentric=float(np.mean([r["t_eccentric"] for r in reps])),
        mean_top_hold=float(np.mean([r["t_top_hold"] for r in reps])),
        mean_concentric=float(np.mean([r["t_concentric"] for r in reps])),
        shrug_top_vs_standing_l=asym["ear_sh_top_l"] - ear_sh_stand_l,
        shrug_top_vs_standing_r=asym["ear_sh_top_r"] - ear_sh_stand_r,
        neck_crane_cm=asym["nose_above_ear_top_cm"] - nose_ear_stand,
        grip_ratio=grip_ratio,
        velocity_loss_pct=float((1 - reps[-1]["peak_conc_v"] / peak_ref) * 100),
        taken_to_failure=len(fails) > 0,
    )

    summary = dict(
        attempts=n_att, reps=n, failed=len(fails),
        bar_slope=bar_a, bar_intercept=bar_b, bar_tilt_deg=float(np.degrees(np.arctan(bar_a))),
        camera_roll_corrected_deg=2.70,
        grab_start=float(t[grab0]), load_start=float(t[load0]), hang_start=float(t[hang0]),
        hang_end=float(t[hang1]),
        standing_on_bar=float(t[load0] - t[grab0]), loading_duration=float(t[hang0] - t[load0]),
        hang_duration=float(t[hang1] - t[hang0]),
        dead_hang_before_first=float(attempts[0]["t_start"] - t[hang0]),
        set_duration=float(attempts[-1]["t_end"] - attempts[0]["t_start"]),
        reps_per_min=float(n / (attempts[-1]["t_end"] - attempts[0]["t_start"]) * 60),
        mean_concentric=float(np.mean([r["t_concentric"] for r in reps])),
        mean_eccentric=float(np.mean([r["t_eccentric"] for r in reps])),
        mean_top_hold=float(np.mean([r["t_top_hold"] for r in reps])),
        mean_rest=float(np.mean([r["t_bottom_hold"] for r in reps[:-1]])) if n > 1 else 0.0,
        mean_cycle=float(np.mean([r["t_cycle"] for r in reps[:-1]])) if n > 1 else 0.0,
        mean_efficiency=float(np.mean([r["efficiency"] for r in reps])),
        best_rep=int(max(reps, key=lambda r: r["efficiency"])["rep"]),
        worst_rep=int(min(reps, key=lambda r: r["efficiency"])["rep"]),
        peak_v_first=reps[0]["peak_conc_v"], peak_v_last=reps[-1]["peak_conc_v"], peak_v_max=peak_ref,
        velocity_loss_pct=float((1 - reps[-1]["peak_conc_v"] / peak_ref) * 100),
        mean_rom_cm=float(np.mean([r["rom_cm"] for r in reps])),
        mean_chin_cm=float(np.mean([r["chin_cm"] for r in reps])),
        nose_chin_cm=nose_chin_cm, shoulder_chin_cm=sh_chin_cm, face_axis_cm=face_axis_cm,
        chin_sigma_cm=CHIN_SIGMA_CM, chin_axis_k=CHIN_AXIS_K, verdict_band_cm=VERDICT_BAND_CM,
        chin_estimator=("chin = mouth + %.2f x (mouth - eye midpoint), i.e. down the face axis; "
                        "the second estimate anchors the personal shoulder-to-chin length measured "
                        "standing. Both carry about +-%.1f cm." % (CHIN_AXIS_K, CHIN_SIGMA_CM)),
        mean_elbow_bottom=float(np.mean([r["elbow_bottom_after"] for r in reps])),
        mean_hip_sway_cm=float(np.mean([r["hip_sway_cm"] for r in reps])),
        px_per_m=px_per_m, scale_note=scale_note, scale_alt=scale_alt,
        rom_cm_alt={k: float(np.mean([r["rom_px"] for r in reps]) / v * 100) for k, v in scale_alt.items()},
        hang_ref_y=hang_ref, top_ref_y=top_ref,
        tracked_frames=int(ok.sum()), frames=N, fps=fps, height_m=height, mass_kg=mass,
        asymmetry=asym, technique=tech,
    )
    if mass:
        summary.update(dict(
            lifted_mass_kg=float(m_lift), work_per_rep_j=float(np.mean([r["work_j"] for r in reps])),
            set_work_kj=float(sum(a["work_j"] for a in attempts) / 1000),
            set_kcal=float(set_kcal), hang_kcal_before=float(hang_before),
            set_kcal_total=float(set_kcal + hang_before),
            set_heat_kj=float(sum(a["heat_j"] for a in attempts) / 1000),
            mean_power_w_first=reps[0]["mean_power_w"], mean_power_w_last=reps[-1]["mean_power_w"],
            peak_power_w_max=float(max(a["peak_power_w"] for a in attempts)),
            peak_force_bw_max=float(max(a["peak_force_bw"] for a in attempts)),
            effort_x_last=reps[-1]["effort_x"], est_rir_last=reps[-1]["est_rir"],
            est_1rm_extra_kg=float(est_1rm_extra), bmi=float(mass / height ** 2) if height else None,
            hang_kcal_per_s=float(hang_power),
            model=dict(lifted_frac=LIFTED_FRAC, eta_conc=ETA_CONC, ecc_cost=ECC_COST, hang_met=HANG_MET),
        ))
    if yolo:
        ysh = np.where((kp[:, 5, 2] > 0.3) & (kp[:, 6, 2] > 0.3), (kp[:, 5, 1] + kp[:, 6, 1]) / 2, np.nan)
        ysh = smooth(ysh, 9, 2)
        yt, _ = find_peaks(-ysh[grab0:grab1], prominence=amp_ref * 0.5, distance=int(0.6 * fps))
        summary["yolo_attempts"] = int(len(yt))
        summary["yolo_tops"] = [float(t[grab0 + i]) for i in yt]
        # Compare the two trackers only where both are actually tracking the athlete on the
        # bar. Over the whole clip the comparison is meaningless: he walks past the lens at
        # both ends, and smooth() has interpolated across YOLO's dropouts there.
        conf = np.minimum(kp[:, 5, 2], kp[:, 6, 2])
        m = np.zeros(N, bool); m[grab0:grab1] = True
        m &= (conf > 0.3) & ok
        summary["yolo_mp_shoulder_corr"] = float(np.corrcoef(sh_y[m], ysh[m])[0, 1])
        summary["yolo_mp_shoulder_mad_px"] = float(np.nanmedian(np.abs(sh_y[m] - ysh[m])))
        summary["yolo_mp_compared_frames"] = int(m.sum())

    signals = dict(
        t=t.tolist(), sh_y=sh_y.tolist(), height_pct=np.nan_to_num(height_pct).tolist(),
        chin_gap_cm=np.nan_to_num(chin_gap_cm).tolist(), sh_gap_cm=np.nan_to_num(sh_gap_cm).tolist(),
        vy_m=np.nan_to_num(vy_m).tolist(), elbow_l=el3_l.tolist(), elbow_r=el3_r.tolist(),
        elbow2d_l=el2_l.tolist(), elbow2d_r=el2_r.tolist(),
        sh_tilt=np.nan_to_num(sh_tilt).tolist(), hip_tilt=np.nan_to_num(hip_tilt).tolist(),
        lat_bend=np.nan_to_num(lat_bend).tolist(), hip_x=np.nan_to_num(hip[:, 0]).tolist(),
        sh_x=sh[:, 0].tolist(), arm_px=arm_px.tolist(), ank_y=np.nan_to_num(ank[:, 1]).tolist(),
        knee_l=kn3_l.tolist(), knee_r=kn3_r.tolist(), phase=phase.tolist(),
        tops=[int(x) for x in tops], bottoms=[int(x) for x in bottoms],
        grab0=int(grab0), load0=int(load0), hang0=int(hang0), hang1=int(hang1))
    json.dump(dict(summary=summary, reps=attempts, signals=signals), open(out, "w"), indent=1)

    print(f"\nATTEMPTS {n_att}: {n} reps + {len(fails)} failed")
    print("  #   top    chin  (alt)  ROM  elb3D L/R  elb2D L/R  bot   up  hold  down  rest    v  sway shTilt shdy  eff")
    for a in attempts:
        tag = f"#{a['rep']:2d}" if a["rep"] else "FAIL"
        print(f"{tag} {a['t_top']:6.2f} {a['chin_cm']:+5.1f} ({a['chin_cm_from_shoulder']:+5.1f}) {a['rom_cm']:4.0f} "
              f"{a['elbow_top_l']:5.0f}/{a['elbow_top_r']:3.0f} {a['elbow2d_top_l']:5.0f}/{a['elbow2d_top_r']:3.0f} "
              f"{a['elbow_bottom_after']:4.0f} {a['t_concentric']:5.2f} {a['t_top_hold']:5.2f} {a['t_eccentric']:5.2f} "
              f"{a['t_bottom_hold']:5.2f} {a['peak_conc_v']:5.2f} {a['hip_sway_cm']:4.1f} {a['sh_tilt_top']:+6.1f} "
              f"{a['sh_dy_top_cm']:+5.1f} {a['efficiency']:4.0f}")
    print()
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ('yolo_tops', 'model', 'asymmetry', 'technique')}, indent=1))
    print("ASYMMETRY:", json.dumps(asym, indent=1))
    print("TECHNIQUE:", json.dumps(tech, indent=1))


if __name__ == "__main__":
    main()
