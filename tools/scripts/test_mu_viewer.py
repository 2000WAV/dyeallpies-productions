"""
Checks for mu_viewer.py's two trust-boundary helpers: the clip name that ends up in an ssh
command, and the HTTP Range header the video element sends when seeking.
Run: python tools/scripts/test_mu_viewer.py  (or pytest)
"""
import http.client, json, os, re, sys, tempfile, threading
from http.server import ThreadingHTTPServer

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


def test_upload_names_are_made_by_the_server():
    n = mv.upload_name("pullup", "video/quicktime")
    assert re.fullmatch(r"up-pullup-\d{8}-\d{6}-[0-9a-f]{6}\.mov", n), n
    assert mv.valid_name(n) and mv.kind_of(n) == "pullup" and mv.folder_of(n) == "uploads"
    assert mv.upload_name("muscleup", "video/mp4").endswith(".mp4")
    assert mv.upload_name("pullup", "text/html") is None and mv.upload_name("dips", "video/mp4") is None
    for bad in ("up-pullup-20260930-120000-abc.mp4", "up-pullup-20260930-120000-zzzzzz.mp4",
                "up-pullup-20260930-120000-abcdef.mp4/../x", "up-squat-20260930-120000-abcdef.mp4"):
        assert not mv.valid_name(bad), bad


def test_upload_checks():
    assert mv.check_upload("video/mp4", "1000") is None
    assert mv.check_upload("video/mp4", None) == 411
    assert mv.check_upload("video/mp4", "-5") == 400
    assert mv.check_upload("video/mp4", str(mv.MAX_UPLOAD + 1)) == 413
    assert mv.check_upload("application/octet-stream", "1000") == 415


def test_upload_route():
    with tempfile.TemporaryDirectory() as d:
        clips = mv.Clips(os.path.join(d, "cache"), "nas-git", "/nowhere", uploads=os.path.join(d, "up"))
        srv = ThreadingHTTPServer(("127.0.0.1", 0), mv.handler(clips))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        port = srv.server_address[1]
        def post(path, body, ctype):
            c = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
            c.request("POST", path, body=body, headers={"Content-Type": ctype})
            r = c.getresponse(); return r.status, json.loads(r.read() or b"{}")
        assert post("/api/upload?kind=pullup", b"x" * 10, "text/plain")[0] == 415
        assert post("/api/upload?kind=dips", b"x" * 10, "video/mp4")[0] == 400
        st, j = post("/api/upload?kind=pullup", b"fake video bytes", "video/mp4")
        assert st == 200 and mv.valid_name(j["name"]) and mv.kind_of(j["name"]) == "pullup", (st, j)
        assert open(os.path.join(d, "up", j["name"]), "rb").read() == b"fake video bytes"
        c = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
        c.request("GET", "/api/clips?kind=uploads"); r = c.getresponse(); lst = json.loads(r.read())["clips"]
        assert [x["name"] for x in lst] == [j["name"]] and lst[0]["kind"] == "pullup", lst
        srv.shutdown()


if __name__ == "__main__":
    for f in (test_clip_names, test_folder_and_week, test_range, test_upload_names_are_made_by_the_server,
              test_upload_checks, test_upload_route):
        f()
        print("ok", f.__name__)
