"""Apply fast zoom-blur "whip" transitions at given cut times in a video.

Usage: blur_whip.py <in.mp4> <out.mp4> --cuts t1,t2,... [--frames N] [--reach R] [--bloom B]

Matches the transition measured in the trend reference: roughly 4 frames at 60 fps
(~67 ms) in which the picture smears radially outward and blooms toward white, with the
incoming shot resolving out of it. There is no dissolve -- the cut stays hard underneath,
the blur just hides the seam and carries the motion across it.

The effect is applied symmetrically around each cut (half on the outgoing frames, half on
the incoming), so it consumes no extra time and leaves audio and beat alignment untouched.
Strength follows a triangular envelope peaking exactly at the cut.
"""
import sys, subprocess
import numpy as np, cv2

def arg(name, default, cast=float):
    return cast(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default

src, out = sys.argv[1], sys.argv[2]
cuts = [float(x) for x in arg("--cuts", "", str).split(",") if x.strip()]
NF = int(arg("--frames", 3))        # total frames affected per cut (odd -> symmetric)
REACH = arg("--reach", 0.26)        # peak zoom-blur reach
BLOOM = arg("--bloom", 0.34)        # peak brightness lift
NSAMP = int(arg("--samples", 13))

cap = cv2.VideoCapture(src)
FPS = cap.get(cv2.CAP_PROP_FPS)
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
N = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# strength per frame index: triangular peak at each cut frame
strength = np.zeros(N + 2, dtype=np.float32)
half = NF // 2
for t in cuts:
    cf = int(round(t * FPS))
    for d in range(-half, half + 1):
        f = cf + d
        if 0 <= f < len(strength):
            strength[f] = max(strength[f], 1.0 - abs(d) / (half + 1.0))

cxp, cyp = W / 2.0, H / 2.0
enc = subprocess.Popen(
    ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
     "-s", f"{W}x{H}", "-r", f"{FPS}", "-i", "-",
     "-c:v", "h264_nvenc", "-preset", "p5", "-tune", "hq", "-rc", "vbr", "-cq", "19",
     "-b:v", "0", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)

n = 0
while True:
    ok, frame = cap.read()
    if not ok: break
    s = strength[n] if n < len(strength) else 0.0
    if s > 0.01:
        reach = REACH * s
        acc = np.zeros(frame.shape, dtype=np.float32)
        for k in range(NSAMP):
            sc = 1.0 + reach * k / (NSAMP - 1)
            M = np.float32([[sc, 0, cxp * (1 - sc)], [0, sc, cyp * (1 - sc)]])
            acc += cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LINEAR,
                                  borderMode=cv2.BORDER_REPLICATE)
        f = acc / NSAMP
        f = f * (1.0 + BLOOM * s) + 255.0 * (BLOOM * 0.45 * s)   # lift + wash toward white
        frame = np.clip(f, 0, 255).astype(np.uint8)
    enc.stdin.write(frame.tobytes())
    n += 1

cap.release(); enc.stdin.close(); enc.wait()
print(f"wrote {out}: {len(cuts)} whips over {n} frames ({NF} frames each, ~{1000*NF/FPS:.0f} ms)")
