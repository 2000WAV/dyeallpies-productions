"""
Grade street / weighted pull-ups from a side-on pose track, rep by rep: chin over the bar, how
close the shoulders come to the hands at the top, time up (concentric), swing, and the hip and
knee angles that show a kip. Same track as analyze_muscleups.py: the hands are the bar, distances
are in torso lengths, a hand-held camera is fine.

Usage:
    python analyze_pullups_side.py <pose_mp.npz> <out.json>
"""
import json, sys
import numpy as np
from analyze_muscleups import track, viewer_series, runs, speeds

PROMINENCE = 0.3     # torso lengths the shoulders must rise from the bottom for a rep to count
MIN_GAP = 0.6        # seconds between two tops
DEAD_HANG = 0.7      # torso lengths the shoulders must be under the hands at the bottom: standing on the box with
                     # the hands on the bar reads ~0.4, a hang with straight arms ~0.9-1.1
HAND_VIS = 0.3       # a frame counts only if at least one wrist is really seen: hidden hands put the bar anywhere
STILL = 0.5          # torso lengths the hands may move from the bottom to the top: more is letting go, not a pull
LEG_VIS = 0.5        # median visibility of knees and ankles under which the knee and hip angles are not given


def analyze(npz_path, series=False, height=None):
    T = track(npz_path)
    fps, rise, B, Hp, nose = T.fps, T.rise, T.B, T.Hp, T.nose
    fwd = lambda p, i: T.face * (p[i, 0] - B[i, 0]) / T.L
    # a set: hands above the shoulders (hanging or pulling) for at least 1 s, with a pose really seen
    seen = (T.found > 0) & (T.vis[:, [15, 16]].max(axis=1) >= HAND_VIS)
    on = (B[:, 1] < T.S[:, 1]) & seen
    reps = []
    for a0, b0 in runs(on):
        if b0 - a0 < fps:
            continue
        r = rise[a0:b0]
        w = max(1, int(MIN_GAP * fps / 2))
        tops = [i for i in range(len(r)) if r[i] == r[max(0, i - w): i + w + 1].min()
                and r[max(0, i - int(1.5 * fps)): i + 1].max() - r[i] >= PROMINENCE]
        last = 0
        for i in tops:
            if reps and a0 + i - reps[-1]["_top"] < MIN_GAP * fps:
                continue
            seg = r[last:i + 1]
            bot = last + len(seg) - 1 - int(np.argmax(seg[::-1]))       # the last low point: where the pull starts
            top, bottom = a0 + i, a0 + bot
            if rise[bottom] < DEAD_HANG:
                continue
            if np.linalg.norm(B[bottom:top + 1] - B[bottom], axis=1).max() / T.L > STILL:
                continue
            span = np.arange(bottom, min(b0, top + int(0.3 * fps)) + 1)
            x = np.array([fwd(Hp, j) for j in span])
            legs = np.median(T.vis[span][:, [25, 26, 27, 28]]) >= LEG_VIS
            ang = lambda a: round(float(a[span].min()), 1) if legs else None
            reps.append(dict(_top=top, rep=len(reps) + 1, t_top=round(top / fps, 2),
                             chin_over_bar=bool(nose[top, 1] < B[top, 1]),
                             top_torso=round(float(rise[top]), 2),
                             concentric_s=round((top - bottom) / fps, 2),
                             **speeds(T, bottom, top, height),
                             swing_torso=round(float(np.ptp(x)), 2),
                             hip_min_deg=ang(T.hip), knee_min_deg=ang(T.knee)))
            last = i
    for rp in reps:
        rp.pop("_top")
    res = dict(fps=fps, view=T.view, torso_px=round(float(T.L), 1), reps=reps)
    if series:
        res.update(width=T.w, height=T.h, series=viewer_series(T))
    return res


def main():
    src, out = sys.argv[1:3]
    res = analyze(src)
    with open(out, "w") as f:
        json.dump(res, f, indent=2)
    for r in res["reps"]:
        print(f"{r['rep']}. @ {r['t_top']:.2f}s  {'chin over' if r['chin_over_bar'] else 'SHORT    '}  "
              f"top {r['top_torso']:+.2f}  up {r['concentric_s']:.2f}s  swing {r['swing_torso']:.2f}  "
              f"hip {r['hip_min_deg']} deg  knee {r['knee_min_deg']} deg")
    if not res["reps"]:
        print("no rep found")


if __name__ == "__main__":
    main()
