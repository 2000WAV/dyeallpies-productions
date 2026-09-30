"""
Checks for rep_feedback.py: removing / restoring a rep, the removed flag on the analysis, and the
"not you?" suggestion learnt from the removals.  Run: python tools/scripts/test_rep_feedback.py
"""
import os, sys, tempfile

sys.path.insert(0, os.path.dirname(__file__))
import rep_feedback as rf


def rep(t, ratio, x, facing=1):
    return dict(t_transition=t, torso_ratio=ratio, x_rel=x, facing=facing)


def test_remove_restore_and_flag():
    with tempfile.TemporaryDirectory() as d:
        fb = rf.Feedback(os.path.join(d, "feedback.json"))
        analysis = dict(reps=[rep(10.0, 1.0, 0.5), rep(20.0, 0.5, 0.2)])
        fb.set("muscleup-2026-08-24-01.mp4", 20.02, True, analysis)
        out = fb.annotate("muscleup-2026-08-24-01.mp4", analysis)
        assert [r["removed"] for r in out["reps"]] == [False, True]
        fb2 = rf.Feedback(os.path.join(d, "feedback.json"))                 # persisted
        assert [r["removed"] for r in fb2.annotate("muscleup-2026-08-24-01.mp4", analysis)["reps"]] == [False, True]
        fb2.set("muscleup-2026-08-24-01.mp4", 20.0, False, analysis)
        assert not any(r["removed"] for r in fb2.annotate("muscleup-2026-08-24-01.mp4", analysis)["reps"])


def test_learns_what_is_not_you():
    with tempfile.TemporaryDirectory() as d:
        fb = rf.Feedback(os.path.join(d, "feedback.json"))
        # in 3 clips he removes the small, far-left person's reps and keeps his own (big, centred)
        for i in range(3):
            a = dict(reps=[rep(10.0, 1.0, 0.55), rep(30.0, 0.45, 0.15)])
            fb.set(f"muscleup-2026-08-2{i}-01.mp4", 30.0, True, a)
            fb.annotate(f"muscleup-2026-08-2{i}-01.mp4", a)
        fresh = dict(reps=[rep(5.0, 0.98, 0.5), rep(9.0, 0.5, 0.18)])
        out = fb.annotate("muscleup-2026-09-01-01.mp4", fresh)["reps"]
        assert [r["suspect"] for r in out] == [False, True], out
        assert not any(r["removed"] for r in out)                             # suggested, never removed


def test_no_suggestion_without_enough_examples():
    with tempfile.TemporaryDirectory() as d:
        fb = rf.Feedback(os.path.join(d, "feedback.json"))
        a = dict(reps=[rep(10.0, 1.0, 0.55), rep(30.0, 0.45, 0.15)])
        fb.set("muscleup-2026-08-20-01.mp4", 30.0, True, a)
        out = fb.annotate("muscleup-2026-09-01-01.mp4", dict(reps=[rep(9.0, 0.5, 0.18)]))["reps"]
        assert out[0]["suspect"] is False


if __name__ == "__main__":
    for f in (test_remove_restore_and_flag, test_learns_what_is_not_you, test_no_suggestion_without_enough_examples):
        f()
        print("ok", f.__name__)
