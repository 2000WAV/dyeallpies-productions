"""
Grade muscle-ups (bar, weighted or not) from a PROFILE-view pose track, on the four faults
Tescoaching's weighted muscle-up breakdown of the Finalrep Worlds flight names
(formats/muscleup-analysis/README.md):

  swing              too much horizontal swing before the pull
  hip_flexion_lost   the hip flexion built during the pull is given back before the bar
  weight_behind_bar  body centre of mass under or behind the bar at the transition
  leg_kickback       ankles thrown behind the bar after the transition (a no-rep in comp)

Usage:
    python analyze_muscleups.py <pose_mp.npz> <out.json> [bar=X,Y]

pose_mp.npz comes from extract_pose_mp.py. bar= is the bar in source pixels; without it the
bar is the median position of the resting wrists. Distances are in torso lengths
(shoulder-mid to hip-mid), so no height or camera calibration is needed. The camera must
look along the bar (side-on): from the front every metric here is depth and is not seen.
"""
import json, sys
import numpy as np

NOSE, EARS, SHOULDERS, WRISTS, HIPS, KNEES, ANKLES = 0, [7, 8], [11, 12], [15, 16], [23, 24], [25, 26], [27, 28]

# ponytail: thresholds set from the synthetic check and the video's verdicts, not fitted on
# real clips yet; recalibrate once there are graded profile clips (clean vs no-rep).
SWING_MAX = 0.5        # torso lengths, hip horizontal range in the 1.5 s before the pull
HIP_LOST_MAX = 25.0    # degrees of hip flexion given back between its peak and the transition
COM_MIN = 0.0          # torso lengths in front of the bar at the transition
KICK_MAX = 0.3         # torso lengths the ankles go behind the bar after the transition
FRONT_MIN = 0.5        # shoulder width / torso length above this = seen from the front, no verdict


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


def bar_from_wrists(wr):
    """Bar = median wrist midpoint over the frames where the wrists are still (hang + support)."""
    m = np.nanmean(wr, axis=1)
    speed = np.r_[np.inf, np.linalg.norm(np.diff(m, axis=0), axis=1)]
    still = speed <= np.nanpercentile(speed, 50)
    return tuple(np.nanmedian(m[still], axis=0))


def angle(a, b, c):
    """Angle at b (degrees) for (N, 2) point arrays."""
    u, v = a - b, c - b
    cos = (u * v).sum(1) / (np.linalg.norm(u, axis=1) * np.linalg.norm(v, axis=1))
    return np.degrees(np.arccos(np.clip(cos, -1, 1)))


def analyze(npz_path, bar=None):
    d = np.load(npz_path)
    fps, w, h = float(d["fps"]), float(d["width"]), float(d["height"])
    px = fill_smooth(d["img"][..., :2] * [w, h], max(1, int(round(fps / 15))))
    mid = lambda idx: px[:, idx].mean(axis=1)
    S, Hp, K, A = mid(SHOULDERS), mid(HIPS), mid(KNEES), mid(ANKLES)
    bx, by = bar if bar else bar_from_wrists(px[:, WRISTS])

    face = np.sign(np.nanmedian(px[:, NOSE, 0] - mid(EARS)[:, 0])) or 1.0   # +1: facing +x
    L = np.nanmedian(np.linalg.norm(S - Hp, axis=1))
    fwd = lambda p: face * (p[:, 0] - bx) / L          # torso lengths in front of the bar
    # segment centres weighted by Winter's mass fractions: head+arms+trunk, thighs, shanks+feet
    com = 0.678 * (S + Hp) / 2 + 0.2 * (Hp + K) / 2 + 0.122 * (K + A) / 2
    hip = angle(S, Hp, K)
    view = "front" if np.nanmedian(np.abs(np.diff(px[:, SHOULDERS, 0], axis=1))) / L > FRONT_MIN else "side"

    above = S[:, 1] < by
    edges = np.flatnonzero(np.diff(np.r_[0, above.astype(int), 0]))
    reps = []
    for a, b in zip(edges[::2], edges[1::2]):
        if b - a < 0.15 * fps or a == 0:          # too short, or the clip starts above the bar
            continue
        tr = a
        w0 = max(0, tr - int(1.5 * fps))
        pull = w0 + len(S[w0:tr]) - 1 - np.argmax(S[w0:tr, 1][::-1])   # last lowest-shoulder frame
        sw = Hp[max(0, pull - int(1.5 * fps)): pull + 1]
        swing = float(np.ptp(face * sw[:, 0]) / L) if len(sw) > 1 else 0.0
        hip_min = float(hip[pull:tr + 1].min())
        hip_lost = float(hip[tr] - hip_min)
        com_tr = float(fwd(com)[tr])
        kick = float(max(0.0, -fwd(A)[tr: tr + int(1.0 * fps)].min()))
        faults = [name for name, bad in (("swing", swing > SWING_MAX),
                                         ("hip_flexion_lost", hip_lost > HIP_LOST_MAX),
                                         ("weight_behind_bar", com_tr < COM_MIN),
                                         ("leg_kickback", kick > KICK_MAX)) if bad and view == "side"]
        reps.append(dict(rep=len(reps) + 1, t_pull=round(float(pull / fps), 2), t_transition=round(float(tr / fps), 2),
                         swing_torso=round(swing, 2), hip_min_deg=round(hip_min, 1),
                         hip_lost_deg=round(hip_lost, 1), com_at_transition_torso=round(com_tr, 2),
                         kick_behind_bar_torso=round(kick, 2), faults=faults))
    return dict(fps=fps, bar_px=[round(float(bx), 1), round(float(by), 1)], facing=int(face), view=view,
                torso_px=round(float(L), 1), reps=reps)


def main():
    src, out = sys.argv[1:3]
    kw = dict(a.split("=", 1) for a in sys.argv[3:])
    bar = tuple(float(v) for v in kw["bar"].split(",")) if "bar" in kw else None
    res = analyze(src, bar)
    with open(out, "w") as f:
        json.dump(res, f, indent=2)
    print(f"bar {res['bar_px']}  torso {res['torso_px']} px  facing {res['facing']:+d}  view {res['view']}")
    if res["view"] == "front":
        print("front view: swing, hip, CoM and kickback are depth here and not seen; no verdict given")
    for r in res["reps"]:
        print(f"rep {r['rep']} @ {r['t_transition']:.2f}s  swing {r['swing_torso']:.2f}  "
              f"hip lost {r['hip_lost_deg']:.0f} deg  CoM {r['com_at_transition_torso']:+.2f}  "
              f"kick {r['kick_behind_bar_torso']:.2f}  -> {', '.join(r['faults']) or ('clean' if res['view'] == 'side' else 'no verdict')}")
    if not res["reps"]:
        print("no rep found: shoulders never went above the bar (check bar= and the camera angle)")


if __name__ == "__main__":
    main()
