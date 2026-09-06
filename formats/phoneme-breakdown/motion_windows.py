"""Mean absolute frame difference per 0.5 s for each video; print the most intense 2.5 s window.
    python motion_windows.py out.json video1 video2 ..."""
import sys, json, subprocess, numpy as np
out = {}
W, H = 96, 170
for path in sys.argv[2:]:
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps=10,scale={W}:{H}", "-pix_fmt", "gray", "-f", "rawvideo", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    n = len(raw) // (W * H)
    fr = np.frombuffer(raw, np.uint8)[: n * W * H].reshape(n, H, W).astype(np.float32)
    d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))  # per 0.1 s
    t = np.arange(1, n) / 10.0
    win = 25  # 2.5 s
    s = np.convolve(d, np.ones(win) / win, mode="valid")
    i = int(np.argmax(s))
    out[path] = {"duration": n / 10.0, "best_start": round(float(t[i]), 2), "best_end": round(float(t[i] + win / 10.0), 2), "score": round(float(s[i]), 2),
                 "per_half_second": [round(float(x), 2) for x in d.reshape(-1)[: (len(d) // 5) * 5].reshape(-1, 5).mean(1)]}
    print(path, out[path]["best_start"], out[path]["best_end"], out[path]["score"])
json.dump(out, open(sys.argv[1], "w"), indent=1)
