"""
Grade muscle-ups (bar, weighted or not) from a PROFILE-view pose track, on the four faults
Tescoaching's weighted muscle-up breakdown of the Finalrep Worlds flight names
(formats/muscleup-analysis/README.md):

  swing              too much horizontal swing before the pull
  hip_flexion_lost   the hip flexion built during the pull is given back before the bar
  weight_behind_bar  body centre of mass under or behind the bar at the transition
  leg_kickback       ankles thrown behind the bar after the transition (a no-rep in comp)

Usage:
    python analyze_muscleups.py <pose_mp.npz> <out.json>

pose_mp.npz comes from extract_pose_mp.py. The hands never leave the bar during an attempt,
so the wrist midpoint is the bar, frame by frame: everything is measured from it, which
cancels a hand-held camera that pans to follow the lift. Distances are in torso lengths
(shoulder-mid to hip-mid), so no height or camera calibration is needed. The camera must
look along the bar (side-on): from the front every metric here is depth and is not seen.
"""
import json, sys
from types import SimpleNamespace
import numpy as np

NOSE, EARS, SHOULDERS, WRISTS, HIPS, KNEES, ANKLES = 0, [7, 8], [11, 12], [15, 16], [23, 24], [25, 26], [27, 28]
DRAWN = [0, 7, 8, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]   # landmarks the viewer draws

# ponytail: thresholds set from the synthetic check and the video's verdicts, not fitted on
# real clips yet; recalibrate once there are graded profile clips (clean vs no-rep).
SWING_MAX = 0.5        # torso lengths, hip horizontal range in the 1.5 s before the pull
HIP_LOST_MAX = 25.0    # degrees of hip flexion given back between its peak and the transition
COM_MIN = 0.0          # torso lengths in front of the bar at the transition
KICK_MAX = 0.3         # torso lengths the ankles go behind the bar after the transition
DEAD_HANG = 0.7        # torso lengths the shoulders must hang under the hands before a pull: standing on
                       # the box with the hands on the bar reads ~0.4, a hang with straight arms ~0.9-1.1
LEG_VIS = 0.5          # median visibility of knees and ankles under which no knee angle is given
FRONT_MIN = 0.5        # shoulder width / torso length above this = seen from the front, no verdict
LOCK = -0.95           # torso lengths of shoulders over the hands that count as the lockout (arm ~ 1.1 torso)
PULL_MIN = 0.4        # torso lengths the shoulders must rise from the hang's low point: sliding down to let go is no attempt
STILL = 0.5            # torso lengths the hands may move within 0.1 s of the event: more is letting go
REACH = 0.3            # torso lengths under the hang's bar position the shoulders must reach: dropping off never does
GRIP = 1.0             # torso lengths the hands may drift from where the hang ended and still be on the bar


def fill_smooth(x, k):
    """Linear-fill NaNs along time, then a centred moving average of k frames."""
    x = x.copy()
    t = np.arange(len(x))
    for c in np.ndindex(x.shape[1:]):
        v = x[(slice(None),) + c]
        good = ~np.isnan(v)
        if good.sum() >= 2:
            v[~good] = np.interp(t[~good], t[good], v[good])
        if k > 1:
            pad = np.pad(v, k // 2, mode="edge")
            v[:] = np.convolve(pad, np.ones(k) / k, mode="valid")[: len(v)]
    return x


def steady_bar(B, vis, fps, hold_vis=0.3, window_s=1.0):
    """The hands do not move on the bar; only a following camera moves them in the image, slowly.
    Hold the last well-seen position while the wrists are hidden, then a 1 s rolling median: the
    tracker's frame-to-frame jumps (hands at the top edge of the frame) go, a pan is still followed."""
    B = B.copy()
    for i in range(1, len(B)):
        if vis[i] < hold_vis:
            B[i] = B[i - 1]
    k = max(1, int(window_s * fps)) | 1
    pad = np.pad(B, ((k // 2, k // 2), (0, 0)), mode="edge")
    win = np.lib.stride_tricks.sliding_window_view(pad, k, axis=0)
    return np.median(win, axis=-1)


def angle(a, b, c):
    """Angle at b (degrees) for (N, 2) point arrays."""
    u, v = a - b, c - b
    cos = (u * v).sum(1) / (np.linalg.norm(u, axis=1) * np.linalg.norm(v, axis=1))
    return np.degrees(np.arccos(np.clip(cos, -1, 1)))


def runs(m):
    """(start, end) of every run of True in a boolean array."""
    e = np.flatnonzero(np.diff(np.r_[0, m.astype(int), 0]))
    return list(zip(e[::2], e[1::2]))


def track(npz_path):
    """The smoothed track every analysis starts from (shared with analyze_pullups_side.py)."""
    d = np.load(npz_path)
    fps, w, h = float(d["fps"]), float(d["width"]), float(d["height"])
    px = fill_smooth(d["img"][..., :2] * [w, h], max(1, int(round(fps / 15))))
    mid = lambda idx: px[:, idx].mean(axis=1)
    S, Hp, K, A = mid(SHOULDERS), mid(HIPS), mid(KNEES), mid(ANKLES)
    # the bar is the wrists weighted by visibility squared: side-on, the far wrist is hidden behind
    # the body and MediaPipe guesses it 0.5 torso off, on the belly, at visibility ~0.1-0.3. Picking
    # the more visible one instead flips between them when both read ~0.5 and makes the bar jump.
    wv = np.nan_to_num(d["img"][:, WRISTS, 3]) ** 2 + 1e-6
    B = (px[:, WRISTS] * wv[..., None]).sum(axis=1) / wv.sum(axis=1)[:, None]
    B = steady_bar(B, np.nan_to_num(d["img"][:, WRISTS, 3]).max(axis=1), fps)
    nose, ears = px[:, NOSE], mid(EARS)
    found = d["ok"].astype(float)                 # frames where MediaPipe actually saw a pose
    L = np.nanmedian(np.linalg.norm(S - Hp, axis=1))
    # segment centres weighted by Winter's mass fractions: head+arms+trunk, thighs, shanks+feet
    com = 0.678 * (S + Hp) / 2 + 0.2 * (Hp + K) / 2 + 0.122 * (K + A) / 2
    hip = angle(S, Hp, K)
    knee = angle(Hp, K, A)                        # 180 = legs straight; Tescoaching: bent knees make the kick worse
    rise = (S[:, 1] - B[:, 1]) / L                # shoulders under the bar (+), over it (-)
    view = "front" if np.nanmedian(np.abs(np.diff(px[:, SHOULDERS, 0], axis=1))) / L > FRONT_MIN else "side"
    face = np.sign(np.nanmedian(nose[:, 0] - ears[:, 0])) or 1.0
    return SimpleNamespace(fps=fps, w=w, h=h, px=px, S=S, Hp=Hp, K=K, A=A, B=B, nose=nose, ears=ears,
                           found=found, L=L, com=com, hip=hip, knee=knee, rise=rise, view=view, face=face,
                           vis=np.nan_to_num(d["img"][..., 3]))


def viewer_series(T):
    """Per-frame arrays for mu_viewer.py."""
    rd = lambda a, n=1: np.round(np.nan_to_num(a), n).tolist()
    return dict(facing=int(T.face), points=rd(T.px[:, DRAWN].reshape(len(T.px), -1)), bar=rd(T.B),
                rise=rd(T.rise, 2), hip=rd(T.hip), knee=rd(T.knee), com=rd(T.face * (T.com[:, 0] - T.B[:, 0]) / T.L, 2))


TORSO_OF_HEIGHT = 0.288   # shoulder (0.818 H) to hip (0.530 H), Winter's anthropometric table


def speeds(T, a, b, height=None):
    """Mean and peak speed of the shoulders towards the hands from frame a to b: torso/s, and m/s
    when the athlete's height is known. Measured against the hands, so a following camera cancels."""
    if b <= a:
        return dict(mean_speed_torso_s=None, peak_speed_torso_s=None, mean_speed_m_s=None, peak_speed_m_s=None)
    k = max(1, int(round(0.2 * T.fps)))           # 0.2 s: the peak is otherwise frame-to-frame tracking noise
    v = np.convolve(-np.gradient(T.rise) * T.fps, np.ones(k) / k, mode="same")
    mean, peak = (T.rise[a] - T.rise[b]) * T.fps / (b - a), float(v[a:b + 1].max())
    m = TORSO_OF_HEIGHT * height if height else None
    r = lambda x: round(float(x), 2)
    return dict(mean_speed_torso_s=r(mean), peak_speed_torso_s=r(peak),
                mean_speed_m_s=r(mean * m) if m else None, peak_speed_m_s=r(peak * m) if m else None)


def analyze(npz_path, series=False, height=None):
    T = track(npz_path)
    fps, w, h, px, S, Hp, K, A, B = T.fps, T.w, T.h, T.px, T.S, T.Hp, T.K, T.A, T.B
    nose, ears, found, L, com, hip, knee, rise, view = T.nose, T.ears, T.found, T.L, T.com, T.hip, T.knee, T.rise, T.view

    # An attempt starts from a hang (hands above the nose, at least 0.3 s) and runs to the next
    # hang. The bar is where the hands sat just before the hang ended (0.4-0.15 s before: a hang
    # that ends by letting go ends with the hands already falling). The hands count as on the bar
    # while they stay within GRIP of it:
    # letting go and landing moves them 1.5-3 torso lengths, a following camera ~0.5. The
    # transition is the first time the shoulders stay over the hands for 0.15 s with the hands on
    # the bar; a rep if the shoulders then get a full arm over the hands while still on the bar,
    # a press miss if not.
    # With no transition it is a pull miss, graded at its highest point under the bar, if the
    # shoulders got within 0.25 torso of the bar. Either way the shoulders must have risen PULL_MIN
    # from the lowest point of the hang and reached within REACH of the bar, and the hands must be
    # still around the event (letting go brings the wrists down past the shoulders, which reads
    # like a pull). (Elbow angles are not used: MediaPipe loses the
    # arms when the head leaves the top of the frame, which is exactly when they matter.)
    hangs = [(a, b) for a, b in runs(B[:, 1] < nose[:, 1]) if b - a >= 0.3 * fps]
    reps = []
    for i, (a0, b0) in enumerate(hangs):
        end = min(hangs[i + 1][0] if i + 1 < len(hangs) else len(S), b0 + int(6 * fps))
        bar = np.median(B[max(a0, b0 - int(0.4 * fps)): max(a0 + 1, b0 - int(0.15 * fps))], axis=0)
        grip = np.linalg.norm(B[b0:end] - bar, axis=1) < GRIP * L
        over = [(b0 + a, b0 + b) for a, b in runs((rise[b0:end] < 0) & grip) if b - a >= 0.15 * fps]
        if over:
            tr = over[0][0]
            # lockout looked for over the whole grip, not just the first stay over the bar: a
            # one-frame tracking glitch as the head leaves the frame splits that stay in two
            outcome = "rep" if rise[tr:end][grip[tr - b0:]].min() < LOCK else "miss_press"
        else:
            under = np.flatnonzero((rise[b0:end] >= 0) & grip)
            if len(under) == 0:
                continue
            tr, outcome = b0 + under[np.argmin(rise[b0 + under])], "miss_pull"
            if rise[tr] > 0.25:
                continue
        k = int(0.1 * fps)
        moved = np.linalg.norm(B[max(0, tr - k): tr + k + 1] - B[tr], axis=1).max() / L
        reach = (S[tr, 1] - bar[1]) / L
        seen = found[max(0, tr - int(0.5 * fps)): tr + int(0.5 * fps) + 1].mean()   # not an interpolated gap
        if (rise[a0:b0].max() - rise[tr] < PULL_MIN or rise[a0:b0].max() < DEAD_HANG or moved > STILL
                or reach > REACH or seen < 0.5):
            continue
        face = np.sign(np.median(nose[a0:tr + 1, 0] - ears[a0:tr + 1, 0])) or 1.0   # +1: facing +x
        fwd = lambda p, t: face * (p[t, 0] - B[t, 0]) / L       # torso lengths in front of the bar
        pull = a0 + (tr - a0) - int(np.argmax(rise[a0:tr + 1][::-1]))    # last lowest-shoulder frame
        pre = np.arange(max(a0, pull - int(1.5 * fps)), pull + 1)
        swing = float(np.ptp(fwd(Hp, pre))) if len(pre) > 1 else 0.0
        hip_min = float(hip[pull:tr + 1].min())
        hip_lost = float(hip[tr] - hip_min)
        legs = np.median(T.vis[pull:tr + 1][:, [25, 26, 27, 28]]) >= LEG_VIS      # knees really seen
        knee_tr, knee_min = (float(knee[tr]), float(knee[pull:tr + 1].min())) if legs else (None, None)
        com_tr = float(fwd(com, tr))
        kick = float(max(0.0, -fwd(A, np.arange(tr, min(end, tr + int(fps)))).min()))
        faults = [name for name, bad in (("swing", swing > SWING_MAX),
                                         ("hip_flexion_lost", hip_lost > HIP_LOST_MAX),
                                         ("weight_behind_bar", com_tr < COM_MIN),
                                         ("leg_kickback", kick > KICK_MAX)) if bad and view == "side"]
        sp = speeds(T, pull, tr, height)
        reps.append(dict(rep=len(reps) + 1, outcome=outcome, facing=int(face),
                         pull_speed_torso_s=sp["mean_speed_torso_s"], pull_peak_torso_s=sp["peak_speed_torso_s"],
                         pull_speed_m_s=sp["mean_speed_m_s"], pull_peak_m_s=sp["peak_speed_m_s"],
                         t_pull=round(pull / fps, 2), t_transition=round(tr / fps, 2),
                         swing_torso=round(swing, 2), hip_min_deg=round(hip_min, 1),
                         hip_lost_deg=round(hip_lost, 1),
                         knee_at_transition_deg=None if knee_tr is None else round(knee_tr, 1),
                         knee_min_deg=None if knee_min is None else round(knee_min, 1), com_at_transition_torso=round(com_tr, 2),
                         kick_behind_bar_torso=round(kick, 2), faults=faults))
    res = dict(fps=fps, view=view, torso_px=round(float(L), 1), reps=reps)
    if series:                                    # per frame, for mu_viewer.py
        res.update(width=w, height=h, series=viewer_series(T))
    return res


def main():
    src, out = sys.argv[1:3]
    res = analyze(src)
    with open(out, "w") as f:
        json.dump(res, f, indent=2)
    print(f"torso {res['torso_px']} px  view {res['view']}")
    if res["view"] == "front":
        print("front view: swing, hip, CoM and kickback are depth here and not seen; no verdict given")
    for r in res["reps"]:
        print(f"{r['rep']}. {r['outcome']:10s} @ {r['t_transition']:.2f}s  swing {r['swing_torso']:.2f}  "
              f"hip lost {r['hip_lost_deg']:.0f} deg  knee {r['knee_at_transition_deg']} deg  CoM {r['com_at_transition_torso']:+.2f}  "
              f"kick {r['kick_behind_bar_torso']:.2f}  -> {', '.join(r['faults']) or ('clean' if res['view'] == 'side' else 'no verdict')}")
    if not res["reps"]:
        print("no attempt found: no hang followed by a pull to the bar (check the tracked landmarks)")


if __name__ == "__main__":
    main()
