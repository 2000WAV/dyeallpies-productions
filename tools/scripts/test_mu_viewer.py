"""
Checks for mu_viewer.py's two trust-boundary helpers: the clip name that ends up in an ssh
command, and the HTTP Range header the video element sends when seeking.
Run: python tools/scripts/test_mu_viewer.py  (or pytest)
"""
import os, sys

sys.path.insert(0, os.path.dirname(__file__))
import mu_viewer as mv


def test_clip_names():
    assert mv.valid_name("muscleup-2026-04-30-01.mp4")
    assert mv.valid_name("muscleup-2025-08-10-01.mov")
    assert mv.valid_name("pullup-2026-04-25-03.mp4")
    for bad in ("../muscleup-2026-04-30-01.mp4", "muscleup-2026-04-30-01.mp4; rm -rf /",
                "muscleup-2026-04-30-01.mp4 x", "dips-2026-04-30-01.mp4", "", "muscleup-2026-4-30-01.mp4",
                "muscleup-2026-04-30-01.mp4\n", "$(id).mp4"):
        assert not mv.valid_name(bad), bad


def test_folder_and_week():
    assert mv.folder_of("muscleup-2026-04-30-01.mp4") == "01-MuscleUp"
    assert mv.folder_of("pullup-2026-04-25-03.mp4") == "02-PullUp"
    assert mv.week_of("pullup-2026-04-30-01.mp4") == "2026-S18"      # Thursday of ISO week 18
    assert mv.week_of("muscleup-2025-12-29-01.mp4") == "2026-S01"    # ISO year, not calendar year


def test_range():
    assert mv.parse_range("bytes=0-", 1000) == (0, 999)
    assert mv.parse_range("bytes=100-199", 1000) == (100, 199)
    assert mv.parse_range("bytes=900-5000", 1000) == (900, 999)
    assert mv.parse_range("bytes=-100", 1000) == (900, 999)
    assert mv.parse_range(None, 1000) is None
    for bad in ("bytes=1000-", "bytes=500-100", "items=0-1", "bytes=a-b", "bytes=0-1,5-9"):
        assert mv.parse_range(bad, 1000) == "bad", bad


if __name__ == "__main__":
    for f in (test_clip_names, test_folder_and_week, test_range):
        f()
        print("ok", f.__name__)
