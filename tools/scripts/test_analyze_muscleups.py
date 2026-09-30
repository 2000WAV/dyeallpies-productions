"""
Synthetic check for analyze_muscleups.py: a clean rep and a faulty rep built from
hand-written profile trajectories, run through the same npz format extract_pose_mp.py
writes. Run: python tools/scripts/test_analyze_muscleups.py  (or pytest)
"""
import os, sys, tempfile
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import analyze_muscleups as am

FPS, W, H = 60.0, 1000, 1000
BAR = (500.0, 300.0)   # px; athlete faces +x (to the right)


def make_rep(swing, hip_hold, com_front, kick):
    """One rep, 4 s: hang with swing (0-1.5 s), pull (1.5-2.2 s), transition at 2.2 s,
    dip to lockout (2.2-3 s), support (3-4 s). All distances in px, torso = 200 px."""
    n = int(4 * FPS)
    t = np.arange(n) / FPS
    img = np.full((n, 33, 5), np.nan, np.float32)
    bx, by = BAR
    for i, ti in enumerate(t):
        if ti < 1.5:                                   # hang, hips swinging
            sy = by + 60
            hx = bx + swing * np.sin(2 * np.pi * ti / 1.5)
            hip_ang = 175.0
        elif ti < 2.2:                                 # pull: shoulders rise to the bar
            u = (ti - 1.5) / 0.7
            sy = by + 60 - 70 * u
            hx = bx + com_front * u
            # flex to 105 deg by 60 % of the pull, then give back hip_hold deg before the bar
            hip_ang = 175 - 70 * min(u / 0.6, 1) + hip_hold * max(0.0, (u - 0.6) / 0.4)
        else:                                          # above the bar
            u = min((ti - 2.2) / 0.8, 1.0)
            sy = by - 10 - 190 * u
            hx = bx + com_front
            hip_ang = 105 + hip_hold + (170 - 105 - hip_hold) * u   # normal extension to lockout
        sx = hx
        shy, hy = sy, sy + 200
        # thigh direction from the hip angle: straight down at 180, forward (+x) as it flexes
        a = np.radians(180 - hip_ang)
        kx, ky = hx + 150 * np.sin(a), hy + 150 * np.cos(a)
        ax, ay = kx, ky + 150
        if ti >= 2.2:
            ax -= kick * min((ti - 2.2) / 0.3, 1.0)    # ankles thrown back behind the bar
        pts = {0: (sx + 20, shy - 60), 7: (sx, shy - 60), 8: (sx, shy - 60),
               11: (sx, shy), 12: (sx, shy), 15: BAR, 16: BAR,
               23: (hx, hy), 24: (hx, hy), 25: (kx, ky), 26: (kx, ky), 27: (ax, ay), 28: (ax, ay)}
        for k, (x, y) in pts.items():
            img[i, k] = (x / W, y / H, 0, 1, 1)
    return img


def run(img):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "pose.npz")
        np.savez(p, fps=FPS, width=W, height=H, n_frames=len(img), img=img,
                 world=np.zeros((len(img), 33, 3)), ok=np.ones(len(img), bool))
        return am.analyze(p, bar=BAR)


def test_clean_rep():
    reps = run(make_rep(swing=20, hip_hold=5, com_front=40, kick=0))["reps"]
    assert len(reps) == 1, reps
    r = reps[0]
    assert r["faults"] == [], r
    assert r["com_at_transition_torso"] > 0


def test_faulty_rep():
    reps = run(make_rep(swing=150, hip_hold=50, com_front=-40, kick=150))["reps"]
    assert len(reps) == 1, reps
    f = set(reps[0]["faults"])
    assert f == {"swing", "hip_flexion_lost", "weight_behind_bar", "leg_kickback"}, reps[0]


def test_front_view_gives_no_verdict():
    img = make_rep(swing=150, hip_hold=50, com_front=-40, kick=150)
    img[:, 11, 0] -= 90 / W                            # shoulders 180 px apart: seen from the front
    img[:, 12, 0] += 90 / W
    res = run(img)
    assert res["view"] == "front", res
    assert res["reps"][0]["faults"] == [], res


def test_bar_auto_from_wrists():
    img = make_rep(swing=20, hip_hold=5, com_front=40, kick=0)
    bx, by = am.bar_from_wrists(img[:, 15:17, :2] * [W, H])
    assert abs(bx - BAR[0]) < 1 and abs(by - BAR[1]) < 1


if __name__ == "__main__":
    for f in (test_clean_rep, test_faulty_rep, test_front_view_gives_no_verdict, test_bar_auto_from_wrists):
        f()
        print("ok", f.__name__)
