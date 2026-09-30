"""
Local viewer for the sorted muscle-up and pull-up clips on the NAS (01-MuscleUp, 02-PullUp):
pick the MU or PU view, a week, a session, a clip; watch it with the tracked skeleton, the bar
(the hands), the live numbers and every graded attempt or rep drawn over the video as it plays.
Each clip is fetched from the NAS (read only), re-encoded to H.264 if the browser cannot play it,
run through extract_pose_mp.py and analyze_muscleups.py or analyze_pullups_side.py, and cached.
The clip after the one on screen is prepared meanwhile.

Usage:
    python tools/scripts/mu_viewer.py [port=8765] [cache=work/viewer] [host=nas-git]
                                      [dir=/volume1/07-Scratch/02-StreetLifting] [height=1.80]
height (metres) turns the rise speeds into m/s.
then open http://localhost:8765. Listens on 127.0.0.1 only.
"""
import datetime, json, os, re, shlex, subprocess, sys, threading, traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze_muscleups, analyze_pullups_side

NAME = re.compile(r"(muscleup|pullup)-(\d{4}-\d{2}-\d{2})-\d{2}\.(mp4|mov)")
FOLDERS = {"muscleup": "01-MuscleUp", "pullup": "02-PullUp"}
ANALYSES = {"muscleup": analyze_muscleups.analyze, "pullup": analyze_pullups_side.analyze}
MODEL = os.path.join(HERE, "..", "models", "pose_landmarker_heavy.task")


def valid_name(name):
    return bool(NAME.fullmatch(name or ""))


def folder_of(name):
    return FOLDERS[name.split("-", 1)[0]]


def week_of(name):
    y, w, _ = datetime.date.fromisoformat(NAME.fullmatch(name).group(2)).isocalendar()
    return f"{y}-S{w:02d}"


def parse_range(header, size):
    """(first, last) byte for a single 'bytes=' range, None without a header, 'bad' if unusable."""
    if header is None:
        return None
    m = re.fullmatch(r"bytes=(\d*)-(\d*)", header.strip())
    if not m or m.group(1) == m.group(2) == "":
        return "bad"
    if m.group(1) == "":                          # suffix: the last N bytes
        return (max(0, size - int(m.group(2))), size - 1)
    first = int(m.group(1))
    last = min(int(m.group(2)), size - 1) if m.group(2) else size - 1
    return "bad" if first >= size or last < first else (first, last)


class Clips:
    """The clip list, each clip's state, and one worker preparing the most recently asked clip
    first (the one on screen beats the one queued for later)."""

    def __init__(self, cache, host, folder, height=None):
        self.cache, self.host, self.folder, self.height = cache, host, folder, height
        os.makedirs(cache, exist_ok=True)
        self.state, self.wanted = {}, []
        self.cv = threading.Condition()
        threading.Thread(target=self.work, daemon=True).start()

    def path(self, name, ext):
        # keyed by folder too: sorting reused INBOX names (muscleup-...-01) for other videos
        return os.path.join(self.cache, folder_of(name) + "__" + os.path.splitext(name)[0] + ext)

    def listing(self, kind):
        cmd = f"find {shlex.quote(self.folder + '/' + FOLDERS[kind])} -maxdepth 1 -type f -name '{kind}-*'"
        out = subprocess.run(["ssh", self.host, cmd], capture_output=True, text=True, timeout=60)
        if out.returncode:
            raise RuntimeError(f"NAS listing failed: {out.stderr.strip()[:200]}")
        names = sorted({os.path.basename(p) for p in out.stdout.split("\n") if valid_name(os.path.basename(p))},
                       reverse=True)
        return [dict(name=n, state=self.status(n), week=week_of(n), day=NAME.fullmatch(n).group(2))
                for n in names]

    def status(self, name):
        if os.path.exists(self.path(name, ".analysis.json")):
            return "ready"
        return self.state.get(name, "new")

    def want(self, name):
        with self.cv:
            if self.status(name) in ("ready", "fetching", "encoding", "pose", "analysis"):
                return
            if name in self.wanted:
                self.wanted.remove(name)
            self.wanted.append(name)
            self.state[name] = "queued"
            self.cv.notify()

    def work(self):
        while True:
            with self.cv:
                while not self.wanted:
                    self.cv.wait()
                name = self.wanted.pop()
            try:
                self.prepare(name)
            except Exception as e:
                traceback.print_exc()
                self.state[name] = f"error: {e}"[:300]

    def prepare(self, name):
        raw, video, npz = self.path(name, ".src"), self.path(name, ".mp4"), self.path(name, ".npz")
        if not os.path.exists(video):
            self.state[name] = "fetching"
            remote = shlex.quote(f"{self.folder}/{folder_of(name)}/{name}")
            with open(raw + ".part", "wb") as f:           # read only on the NAS: cat, nothing else
                subprocess.run(["ssh", self.host, f"cat {remote}"], stdout=f, check=True, timeout=900)
            os.replace(raw + ".part", raw)
            self.state[name] = "encoding"
            codec = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                    "stream=codec_name", "-of", "default=nw=1:nk=1", raw],
                                   capture_output=True, text=True, check=True).stdout.strip()
            enc = ["-c:v", "copy"] if codec == "h264" else ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20"]
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, *enc, "-an", "-movflags", "+faststart",
                            video + ".part.mp4"], check=True)
            os.replace(video + ".part.mp4", video)
            os.remove(raw)
        if not os.path.exists(npz):
            self.state[name] = "pose"
            subprocess.run([sys.executable, os.path.join(HERE, "extract_pose_mp.py"), video, MODEL,
                            npz + ".part.npz"], check=True, capture_output=True)
            os.replace(npz + ".part.npz", npz)
        self.state[name] = "analysis"
        res = ANALYSES[name.split("-", 1)[0]](npz, series=True, height=self.height)
        tmp = self.path(name, ".analysis.json.part")
        with open(tmp, "w") as f:
            json.dump(res, f)
        os.replace(tmp, self.path(name, ".analysis.json"))
        self.state[name] = "ready"


def handler(clips):
    class H(BaseHTTPRequestHandler):
        def send(self, code, body, ctype="application/json"):
            body = body if isinstance(body, bytes) else json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            u = urlparse(self.path)
            name = parse_qs(u.query).get("name", [""])[0]
            try:
                if u.path == "/":
                    with open(os.path.join(HERE, "mu_viewer.html"), "rb") as f:
                        return self.send(200, f.read(), "text/html; charset=utf-8")
                if u.path == "/api/clips":
                    kind = parse_qs(u.query).get("kind", ["muscleup"])[0]
                    if kind not in FOLDERS:
                        return self.send(400, dict(error="bad kind"))
                    return self.send(200, dict(clips=clips.listing(kind)))
                if not valid_name(name):
                    return self.send(400, dict(error="bad clip name"))
                if u.path == "/api/clip":
                    clips.want(name)
                    st = clips.status(name)
                    if st != "ready":
                        return self.send(200, dict(state=st))
                    with open(clips.path(name, ".analysis.json"), "rb") as f:
                        return self.send(200, f.read())
                if u.path == "/video":
                    return self.video(clips.path(name, ".mp4"))
                self.send(404, dict(error="not found"))
            except (BrokenPipeError, ConnectionResetError):
                pass
            except Exception as e:
                traceback.print_exc()
                self.send(500, dict(error=str(e)[:300]))

        def video(self, path):
            if not os.path.exists(path):
                return self.send(404, dict(error="clip not prepared"))
            size = os.path.getsize(path)
            rng = parse_range(self.headers.get("Range"), size)
            if rng == "bad":
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                return self.end_headers()
            first, last = rng or (0, size - 1)
            self.send_response(206 if rng else 200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(last - first + 1))
            if rng:
                self.send_header("Content-Range", f"bytes {first}-{last}/{size}")
            self.end_headers()
            with open(path, "rb") as f:
                f.seek(first)
                left = last - first + 1
                while left > 0:
                    chunk = f.read(min(1 << 20, left))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    left -= len(chunk)

        def log_message(self, fmt, *args):         # quiet: no line per video chunk
            pass

    return H


def main():
    kw = dict(a.split("=", 1) for a in sys.argv[1:])
    port = int(kw.get("port", 8765))
    clips = Clips(kw.get("cache", "work/viewer"), kw.get("host", "nas-git"),
                  kw.get("dir", "/volume1/07-Scratch/02-StreetLifting"),
                  float(kw["height"]) if "height" in kw else None)
    print(f"muscle-up viewer on http://localhost:{port}  (cache {os.path.abspath(clips.cache)})", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), handler(clips)).serve_forever()


if __name__ == "__main__":
    main()
