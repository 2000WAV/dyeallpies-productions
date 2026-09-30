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


def make_rep(swing, hip_hold, com_front, kick, fail=False, press_fail=False):
    """One rep, 4 s: hang with swing (0-1.5 s), pull (1.5-2.2 s), transition at 2.2 s,
    dip to lockout (2.2-3 s), support (3-4 s). All distances in px, torso = 200 px.
    fail: the shoulders stop 15 px under the bar at 2.2 s and drop back to the hang.
    press_fail: over the bar but stuck in the dip, shoulders never a full arm over the hands."""
    n = int(4 * FPS)
    t = np.arange(n) / FPS
    img = np.full((n, 33, 5), np.nan, np.float32)
    bx, by = BAR
    for i, ti in enumerate(t):
        if ti < 1.5:                                   # hang, arms long: shoulders 0.9 torso under the bar
            sy = by + 180
            hx = bx + swing * np.sin(2 * np.pi * ti / 1.5)
            hip_ang = 175.0
        elif ti < 2.2:                                 # pull: shoulders rise to the bar
            u = (ti - 1.5) / 0.7
            sy = by + 180 - 190 * u
            hx = bx + com_front * u
            # flex to 105 deg by 60 % of the pull, then give back hip_hold deg before the bar
            hip_ang = 175 - 70 * min(u / 0.6, 1) + hip_hold * max(0.0, (u - 0.6) / 0.4)
        elif fail:                                     # stalls under the bar, back to the hang
            u = min((ti - 2.2) / 0.5, 1.0)
            sy = by + 10 + 170 * u
            hx = bx + com_front
            hip_ang = 105 + hip_hold + (175 - 105 - hip_hold) * u
        else:                                          # above the bar
            u = min((ti - 2.2) / 0.8, 1.0)
            sy = by - 10 - (110 if press_fail else 220) * u
            hx = bx + com_front
            hip_ang = 105 + hip_hold + (170 - 105 - hip_hold) * u   # normal extension to lockout
        sx = hx
        shy, hy = sy, sy + 200
        # thigh direction from the hip angle: straight down at 180, forward (+x) as it flexes
        a = np.radians(180 - hip_ang)
        kx, ky = hx + 150 * np.sin(a), hy + 150 * np.cos(a)
        ax, ay = kx + 150 * np.sin(a), ky + 150 * np.cos(a)   # legs straight: shank in line with the thigh
        if ti >= 2.2:
            ax -= kick * min((ti - 2.2) / 0.3, 1.0)    # ankles thrown back behind the bar
        pts = {0: (sx + 20, shy - 40), 7: (sx, shy - 40), 8: (sx, shy - 40),
               11: (sx, shy), 12: (sx, shy), 15: BAR, 16: BAR,
               23: (hx, hy), 24: (hx, hy), 25: (kx, ky), 26: (kx, ky), 27: (ax, ay), 28: (ax, ay)}
        for k, (x, y) in pts.items():
            img[i, k] = (x / W, y / H, 0, 1, 1)
    return img


def standing(seconds):
    """Walking about in front of the rig: shoulders above the bar line in the image,
    hands still at the hips, nowhere near the bar."""
    n = int(seconds * FPS)
    img = np.full((n, 33, 5), np.nan, np.float32)
    x, sy = BAR[0] + 300, BAR[1] - 100
    pts = {0: (x + 20, sy - 60), 7: (x, sy - 60), 8: (x, sy - 60), 11: (x, sy), 12: (x, sy), 15: (x, sy + 200), 16: (x, sy + 200), 23: (x, sy + 200), 24: (x, sy + 200),
           25: (x, sy + 350), 26: (x, sy + 350), 27: (x, sy + 500), 28: (x, sy + 500)}
    for k, (px, py) in pts.items():
        img[:, k] = (px / W, py / H, 0, 1, 1)
    return img


def run(img, series=False):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "pose.npz")
        np.savez(p, fps=FPS, width=W, height=H, n_frames=len(img), img=img,
                 world=np.zeros((len(img), 33, 3)), ok=~np.isnan(img[:, 11, 0]))
        return am.analyze(p, series=series)


def test_clean_rep():
    reps = run(make_rep(swing=20, hip_hold=5, com_front=40, kick=0))["reps"]
    assert len(reps) == 1, reps
    r = reps[0]
    assert r["outcome"] == "rep", r
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


def test_panning_camera_changes_nothing():
    still = run(make_rep(swing=150, hip_hold=50, com_front=-40, kick=150))["reps"]
    img = make_rep(swing=150, hip_hold=50, com_front=-40, kick=150)
    pan = np.linspace(0, 0.25, len(img))[:, None]           # a quarter frame, left and up
    img[..., 0] -= pan
    img[..., 1] -= pan
    moved = run(img)["reps"]
    assert [r["faults"] for r in moved] == [r["faults"] for r in still], moved
    assert abs(moved[0]["com_at_transition_torso"] - still[0]["com_at_transition_torso"]) < 0.05


def test_walking_past_is_not_a_rep():
    img = np.concatenate([standing(3), make_rep(swing=20, hip_hold=5, com_front=40, kick=0)])
    reps = run(img)["reps"]
    assert len(reps) == 1 and reps[0]["outcome"] == "rep", reps


def test_failed_attempt_is_graded():
    reps = run(make_rep(swing=150, hip_hold=50, com_front=-40, kick=0, fail=True))["reps"]
    assert len(reps) == 1, reps
    r = reps[0]
    assert r["outcome"] == "miss_pull", r
    assert {"swing", "hip_flexion_lost", "weight_behind_bar"} <= set(r["faults"]), r


def test_dropping_off_is_not_a_rep():
    # a missed pull, then down on the box: shoulders over the wrists, arms straight
    img = np.concatenate([make_rep(swing=20, hip_hold=5, com_front=40, kick=0, fail=True), standing(2)])
    reps = run(img)["reps"]
    assert [r["outcome"] for r in reps] == ["miss_pull"], reps


def test_sliding_down_before_letting_go_is_not_an_attempt():
    # stuck in the dip, slid back under the bar into a short hang (shoulders 0.7 torso
    # under it), then the hands open and fall past the shoulders: one press miss, nothing else
    img = make_rep(swing=20, hip_hold=5, com_front=40, kick=0, press_fail=True)
    bent = make_rep(swing=0, hip_hold=0, com_front=0, kick=0)[int(1.65 * FPS)]
    fall = np.repeat(bent[None], int(0.15 * FPS), 0)
    fall[:, 15:17, 1] += np.linspace(0, 200 / H, len(fall))[:, None]     # a torso length in 0.15 s
    back = np.concatenate([np.repeat(bent[None], int(0.4 * FPS), 0), fall])
    reps = run(np.concatenate([img, back, standing(2)]))["reps"]
    assert [r["outcome"] for r in reps] == ["rep"], reps


def test_press_is_measured_not_judged():
    # over the bar but only 0.6 torso over the hands: the height is reported, no press verdict
    # (on real clips clean reps read -0.75 to -1.2 and a stuck dip -0.94: the camera decides)
    r = run(make_rep(swing=20, hip_hold=5, com_front=40, kick=0, press_fail=True))["reps"][0]
    assert r["outcome"] == "rep" and -0.7 < r["support_torso"] < -0.4, r


def test_dropping_from_the_hang_is_not_a_rep():
    # hanging, lets go slowly and steps down, hands ending at the chest: the shoulders end up over
    # the wrists, the hands stay within a torso of where the hang ended, but the body went down
    hang = make_rep(swing=0, hip_hold=0, com_front=0, kick=0)[:int(1.4 * FPS)]
    last = hang[-1].copy()
    n = int(1.2 * FPS)
    drop = np.repeat(last[None], n, 0)
    u = np.linspace(0, 1, n)[:, None]
    drop[:, :, 1] += (u * 100 / H)                                  # whole body 0.5 torso down
    drop[:, 15:17, 1] += (u * 260 / H)                              # hands 1.8 torso down, to the chest
    land = np.repeat(drop[-1:], int(1.0 * FPS), 0)
    reps = run(np.concatenate([hang, drop, land]))["reps"]
    assert reps == [], reps


def test_tracking_glitch_over_the_bar_keeps_the_rep():
    # the head leaves the frame on the way to lockout and the tracker drops the shoulders under
    # the bar for 0.1 s: the rep is still locked out after it
    img = make_rep(swing=20, hip_hold=5, com_front=40, kick=0)
    i = int(2.5 * FPS)
    img[i:i + int(0.1 * FPS), 11:13, 1] = (BAR[1] + 100) / H
    reps = run(img)["reps"]
    assert [r["outcome"] for r in reps] == ["rep"], reps


def test_series_for_the_viewer():
    img = make_rep(swing=20, hip_hold=5, com_front=40, kick=0)
    res = run(img, series=True)
    sr = res["series"]
    n = len(img)
    assert len(sr["points"]) == n and len(sr["points"][0]) == len(am.DRAWN) * 2
    assert len(sr["bar"]) == n and len(sr["rise"]) == n and len(sr["hip"]) == n and len(sr["com"]) == n
    i = int(3.5 * FPS)                                  # in support: shoulders a torso over the bar
    assert sr["rise"][i] < -0.9 and abs(sr["bar"][i][1] - BAR[1]) < 1
    assert sr["facing"] == 1                            # one facing for the clip: the page must not guess per frame
    assert "series" not in run(img)                     # the CLI JSON stays small


def test_hidden_wrist_does_not_move_the_bar():
    # side-on, the far wrist is hidden behind the body: MediaPipe guesses it on the belly with a
    # low visibility. The bar must stay on the visible hand.
    img = make_rep(swing=20, hip_hold=5, com_front=40, kick=0)
    img[:, 16, 1] += 150 / H
    img[:, 16, 3] = 0.2
    res = run(img, series=True)
    assert all(abs(b[1] - BAR[1]) < 10 for b in res["series"]["bar"]), res["series"]["bar"][:3]   # 0.05 torso
    assert [r["outcome"] for r in res["reps"]] == ["rep"], res["reps"]


def test_no_pose_no_attempt():
    # nobody in frame around the transition: the gap is interpolated for drawing, never graded
    img = make_rep(swing=20, hip_hold=5, com_front=40, kick=0)
    img[int(1.6 * FPS):int(2.9 * FPS)] = np.nan
    assert run(img)["reps"] == []


def test_knee_flexion():
    straight = run(make_rep(swing=20, hip_hold=5, com_front=40, kick=0), series=True)
    assert straight["reps"][0]["knee_at_transition_deg"] > 170, straight["reps"][0]
    img = make_rep(swing=20, hip_hold=5, com_front=40, kick=0)
    i = int(1.5 * FPS)
    img[i:, 27:29, 0] -= 120 / W                       # heels pulled back from the pull on
    bent = run(img, series=True)
    r = bent["reps"][0]
    assert r["knee_at_transition_deg"] < 150 and r["knee_min_deg"] <= r["knee_at_transition_deg"], r
    assert len(bent["series"]["knee"]) == len(img) and bent["series"]["knee"][int(3 * FPS)] < 150


def test_pull_speed():
    reps = run(make_rep(swing=20, hip_hold=5, com_front=40, kick=0))["reps"]
    r = reps[0]
    # shoulders rise 190 px (0.95 torso) in 0.7 s: ~1.36 torso/s between pull start and transition
    assert 1.0 < r["pull_speed_torso_s"] < 1.7 and r["pull_peak_torso_s"] >= r["pull_speed_torso_s"], r


def test_legs_out_of_frame_give_no_knee_angle():
    img = make_rep(swing=20, hip_hold=5, com_front=40, kick=0)
    img[:, 25:29, 3] = 0.1                                     # knees and ankles guessed, not seen
    r = run(img)["reps"][0]
    assert r["knee_min_deg"] is None and r["knee_at_transition_deg"] is None and r["outcome"] == "rep", r


def test_standing_on_the_box_is_not_an_attempt():
    # on the box, hands on the bar, arms bent (shoulders 90 px = 0.45 torso under the hands), then he
    # straightens up so the shoulders pass the hands, and steps off: never a dead hang, no attempt
    rep = make_rep(swing=0, hip_hold=0, com_front=0, kick=0)
    frames = []
    for i in range(int(2 * FPS)):
        u = min(1.0, i / FPS)
        f = rep[0].copy()
        f[:, 1] -= (90 + 110 * u) / H          # whole body up: shoulders from +0.45 to -0.1 torso
        f[15:17, 1] = BAR[1] / H               # hands stay on the bar
        frames.append(f)
    reps = run(np.concatenate([np.array(frames), standing(2)]))["reps"]
    assert reps == [], reps


def test_head_bowed_over_the_bar_is_not_a_new_hang():
    # at the transition he bows the head forward: the nose drops under the hands for 0.5 s while the
    # shoulders are already over them. One muscle-up, locked out, not a press miss plus a second rep
    img = make_rep(swing=20, hip_hold=5, com_front=40, kick=0)
    i = int(2.35 * FPS)
    img[i:i + int(0.5 * FPS), 0, 1] = (BAR[1] + 40) / H
    reps = run(img)["reps"]
    assert [r["outcome"] for r in reps] == ["rep"], reps


def test_knee_angle_from_the_visible_leg():
    # side-on: the near leg is seen and straight, the far leg is hidden and guessed bent
    img = make_rep(swing=20, hip_hold=5, com_front=40, kick=0)
    img[:, [26, 28], 3] = 0.1                                   # far knee and ankle hidden
    img[:, 28, 0] -= 150 / W                                    # ... and guessed 150 px off
    r = run(img)["reps"][0]
    assert r["knee_min_deg"] is not None and r["knee_min_deg"] > 170, r


def test_split_attempt_is_merged():
    reps = [dict(rep=1, t_transition=10.0, outcome="miss_pull"), dict(rep=2, t_transition=11.3, outcome="rep"),
            dict(rep=3, t_transition=20.0, outcome="miss_pull")]
    out = am.merge_split(reps)
    assert [(r["rep"], r["outcome"]) for r in out] == [(1, "rep"), (2, "miss_pull")], out


if __name__ == "__main__":
    for f in (test_clean_rep, test_faulty_rep, test_front_view_gives_no_verdict,
              test_panning_camera_changes_nothing, test_walking_past_is_not_a_rep, test_failed_attempt_is_graded,
              test_dropping_off_is_not_a_rep, test_press_is_measured_not_judged,
              test_sliding_down_before_letting_go_is_not_an_attempt, test_dropping_from_the_hang_is_not_a_rep,
              test_tracking_glitch_over_the_bar_keeps_the_rep, test_series_for_the_viewer,
              test_hidden_wrist_does_not_move_the_bar, test_no_pose_no_attempt,
              test_knee_flexion, test_pull_speed, test_legs_out_of_frame_give_no_knee_angle,
              test_standing_on_the_box_is_not_an_attempt, test_head_bowed_over_the_bar_is_not_a_new_hang,
              test_knee_angle_from_the_visible_leg, test_split_attempt_is_merged):
        f()
        print("ok", f.__name__)
