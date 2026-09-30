"""
Synthetic check for analyze_pullups_side.py: a standing lead-in, then a set of three pull-ups
(two with the chin over the bar, one short), built in the npz format extract_pose_mp.py writes.
Run: python tools/scripts/test_analyze_pullups_side.py  (or pytest)
"""
import os, sys, tempfile
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import analyze_pullups_side as ap

FPS, W, H = 30.0, 1000, 1000
BAR = (500.0, 300.0)            # hands on the bar; torso = 200 px; athlete faces +x


def pose(sx, sy, hands=BAR, knee_bend=0.0, leg_vis=1.0):
    """Landmarks for shoulders at (sx, sy), straight body under them."""
    hy = sy + 200
    kx, ky = sx, hy + 150
    ax, ay = kx - knee_bend, ky + 150
    pts = {0: (sx + 20, sy - 40), 7: (sx, sy - 40), 8: (sx, sy - 40), 11: (sx, sy), 12: (sx, sy),
           15: hands, 16: hands, 23: (sx, hy), 24: (sx, hy), 25: (kx, ky), 26: (kx, ky), 27: (ax, ay), 28: (ax, ay)}
    f = np.full((33, 5), np.nan, np.float32)
    for k, (x, y) in pts.items():
        v = leg_vis if k in (25, 26, 27, 28) else 1
        f[k] = (x / W, y / H, 0, v, 1)
    return f


def make_set(tops=(20.0, 20.0, 100.0), knee_bend=0.0):
    """2 s standing (hands at the hips), then a hang (shoulders 180 px under the hands) and one
    pull-up per entry of `tops` (shoulders this far under the hands at the top), 1.5 s each."""
    frames = [pose(800, 200, hands=(800, 400)) for _ in range(int(2 * FPS))]
    frames += [pose(500, 480) for _ in range(int(1 * FPS))]
    for top in tops:
        n = int(1.5 * FPS)
        for i in range(n):
            u = np.sin(np.pi * i / n)                           # down - up - down
            frames.append(pose(500, 480 - (180 - top) * u, knee_bend=knee_bend * u))
    frames += [pose(500, 480) for _ in range(int(1 * FPS))]
    return np.array(frames)


def run(img, series=False, height=None):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "pose.npz")
        np.savez(p, fps=FPS, width=W, height=H, n_frames=len(img), img=img,
                 world=np.zeros((len(img), 33, 3)), ok=~np.isnan(img[:, 11, 0]))
        return ap.analyze(p, series=series, height=height)


def test_counts_reps_and_chin_over_bar():
    res = run(make_set())
    reps = res["reps"]
    assert len(reps) == 3, reps
    assert [r["chin_over_bar"] for r in reps] == [True, True, False], reps
    assert all(0.4 < r["concentric_s"] < 1.0 for r in reps), reps
    assert reps[0]["top_torso"] < 0.2 and reps[2]["top_torso"] > 0.4, reps


def test_standing_is_not_a_set():
    img = np.array([pose(800, 200, hands=(800, 400)) for _ in range(int(4 * FPS))])
    assert run(img)["reps"] == []


def test_kipping_knees():
    strict = run(make_set(tops=(20.0,)))["reps"][0]
    kip = run(make_set(tops=(20.0,), knee_bend=200.0))["reps"][0]
    assert strict["knee_min_deg"] > 170 and kip["knee_min_deg"] < 130, (strict, kip)


def test_series_for_the_viewer():
    img = make_set()
    sr = run(img, series=True)["series"]
    assert len(sr["rise"]) == len(img) and len(sr["points"]) == len(img) and sr["facing"] == 1


def test_standing_on_the_box_holding_the_bar_is_not_a_rep():
    # on the box, hands on the bar, arms bent (shoulders 80 px = 0.4 torso under the hands), bobbing
    # up 100 px twice, chin over: never a dead hang, so no rep
    frames = [pose(800, 200, hands=(800, 400)) for _ in range(int(2 * FPS))]
    for _ in range(2):
        n = int(1.5 * FPS)
        frames += [pose(500, 380 - 100 * np.sin(np.pi * i / n)) for i in range(n)]
    assert run(np.array(frames))["reps"] == []


def test_legs_out_of_frame_give_no_knee_angle():
    img = make_set(tops=(20.0,))
    img[:, 25:29, 3] = 0.1                                     # knees and ankles guessed, not seen
    r = run(img)["reps"][0]
    assert r["knee_min_deg"] is None and r["chin_over_bar"], r


def test_hidden_hands_and_letting_go_are_not_reps():
    img = make_set(tops=(20.0,))
    n = len(img)
    # 1 s with the wrists hidden and wrongly placed above the head, shoulders bobbing: no bar, no rep
    hid = np.array([pose(500, 380 - 100 * np.sin(np.pi * i / 30), hands=(500, 250)) for i in range(30)])
    hid[:, 15:17, 3] = 0.05
    # letting go: from the hang the hands come down 150 px while the shoulders rise 100 px
    let = np.array([pose(500, 480 - 100 * i / 20, hands=(500, 300 + 150 * i / 20)) for i in range(21)])
    reps = run(np.concatenate([img, hid, img[-30:], let]))["reps"]
    assert len(reps) == 1 and reps[0]["chin_over_bar"], reps


def test_speed_up():
    # 160 px = 0.8 torso of rise in half of a 1.5 s sine: mean ~1.07 torso/s, peak pi/2 x mean
    r = run(make_set(tops=(20.0,)), height=1.80)["reps"][0]
    assert 0.95 < r["mean_speed_torso_s"] < 1.2, r
    assert r["peak_speed_torso_s"] > r["mean_speed_torso_s"] * 1.3, r
    torso_m = 0.288 * 1.80
    assert abs(r["mean_speed_m_s"] - r["mean_speed_torso_s"] * torso_m) < 0.02, r
    assert run(make_set(tops=(20.0,)))["reps"][0]["mean_speed_m_s"] is None      # no height, no m/s


def test_jittery_wrists_give_a_steady_bar():
    # hands at the top of the frame: the tracker throws the wrists +-30 px frame to frame
    img = make_set()
    rng = np.random.default_rng(0)
    img[:, 15:17, 1] += (rng.uniform(-30, 30, (len(img), 1)) / H).astype(np.float32)
    res = run(img, series=True)
    bar_y = np.array(res["series"]["bar"])[int(2.5 * FPS):, 1]              # once he is on the bar
    assert bar_y.std() < 4, bar_y.std()
    reps = res["reps"]
    assert [r["chin_over_bar"] for r in reps] == [True, True, False], reps


if __name__ == "__main__":
    for f in (test_counts_reps_and_chin_over_bar, test_standing_is_not_a_set, test_kipping_knees,
              test_series_for_the_viewer, test_standing_on_the_box_holding_the_bar_is_not_a_rep,
              test_legs_out_of_frame_give_no_knee_angle, test_hidden_hands_and_letting_go_are_not_reps,
              test_speed_up, test_jittery_wrists_give_a_steady_bar):
        f()
        print("ok", f.__name__)
