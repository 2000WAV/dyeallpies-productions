"""Beat-synced "locked subject, streaking world" effect for a walking shot.

Usage: walk_fx.py <video> <face.json> <out.mp4> --start S --dur D --bpm B [--phase P]

Reproduces the look used in the trend reference: the subject is held at a fixed screen
position and stays sharp, while the surroundings smear with radial (zoom) blur that
punches on every beat.

Three stacked moves, all driven by the beat grid:
  1. STABILISE + PUNCH IN. A crop window follows the tracked head so the subject sits
     at a fixed screen point. Because the anchor is fixed, the sharp-centre mask can be
     a single static radial gradient instead of a per-frame one.
  2. BEAT PULSE. Zoom kicks up on each beat and eases back (exponential decay), so the
     push is felt rather than seen.
  3. SWAY. The framing drifts left/right over a two-beat cycle -- the trend's side-to-side
     motion -- without letting the subject leave the sharp zone.

Radial blur is a real accumulation of progressively scaled copies about the anchor
(ffmpeg has no radial blur), so the streaks converge on the subject the way a zoom blur
does. Blur strength rises with the beat pulse, so the world tears hardest on the hit.
"""
import sys, json, subprocess
import numpy as np, cv2

def arg(name, default=None, cast=float):
    return cast(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default

src, facejson, out = sys.argv[1], sys.argv[2], sys.argv[3]
START = arg("--start", 0.0); DUR = arg("--dur", 8.0)
BPM = arg("--bpm", 109.94); PHASE = arg("--phase", 0.0)
ZOOM = arg("--zoom", 1.45)          # base punch-in
PULSE = arg("--pulse", 0.10)        # extra zoom on the beat
SWAY = arg("--sway", 0.055)         # fraction of width, peak-to-centre
BLUR = arg("--blur", 0.085)         # max radial blur reach (fraction of frame)
SHARP_R = arg("--sharp", 0.24)      # radius held sharp (fraction of half-diagonal)
FEATHER = arg("--feather", 0.30)    # fade-out width
NSAMP = int(arg("--samples", 9, float))
OUTW, OUTH = 1080, 1920

face = json.load(open(facejson))
cx_t, cy_t = np.array(face["cx"]), np.array(face["cy"])
cap = cv2.VideoCapture(src)
FPS = cap.get(cv2.CAP_PROP_FPS)
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
f0 = int(round(START * FPS)); nfr = int(round(DUR * FPS))
beat = 60.0 / BPM

# where the subject is pinned on screen: centred horizontally, head high in frame
ANCH_X, ANCH_Y = OUTW * arg("--ax", 0.50), OUTH * arg("--ay", 0.42)

# static radial mask: 1 = keep sharp, 0 = fully blurred
yy, xx = np.mgrid[0:OUTH, 0:OUTW].astype(np.float32)
r = np.sqrt(((xx - ANCH_X) / (OUTW * 0.5)) ** 2 + ((yy - ANCH_Y) / (OUTH * 0.5)) ** 2)
mask = np.clip((FEATHER - (r - SHARP_R)) / FEATHER, 0.0, 1.0)
mask = (mask ** 1.4)[..., None]

enc = subprocess.Popen(
    ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
     "-s", f"{OUTW}x{OUTH}", "-r", f"{FPS}", "-i", "-",
     "-c:v", "h264_nvenc", "-preset", "p5", "-tune", "hq", "-rc", "vbr", "-cq", "19",
     "-b:v", "0", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)

cap.set(cv2.CAP_PROP_POS_FRAMES, f0)
for n in range(nfr):
    ok, frame = cap.read()
    if not ok: break
    t = n / FPS
    ph = ((t + PHASE) % beat) / beat            # 0 at the beat, ->1 before the next
    kick = float(np.exp(-5.0 * ph))             # sharp attack, quick decay
    z = ZOOM * (1.0 + PULSE * kick)
    nbeat = int((t + PHASE) / beat)
    sway = SWAY * np.sin(np.pi * nbeat + np.pi * ph) * OUTW   # alternates every beat

    fi = min(f0 + n, len(cx_t) - 1)
    # crop window in source pixels that puts the tracked head on the anchor
    cw, ch = OUTW / z, OUTH / z
    x0 = cx_t[fi] - (ANCH_X / OUTW) * cw + sway / z
    y0 = cy_t[fi] - (ANCH_Y / OUTH) * ch
    x0 = float(np.clip(x0, 0, max(0, W - cw))); y0 = float(np.clip(y0, 0, max(0, H - ch)))
    M = np.float32([[OUTW / cw, 0, -x0 * OUTW / cw], [0, OUTH / ch, -y0 * OUTH / ch]])
    base = cv2.warpAffine(frame, M, (OUTW, OUTH), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REPLICATE)

    # radial (zoom) blur about the anchor, strength riding the beat
    reach = BLUR * (0.55 + 0.45 * kick)
    acc = np.zeros_like(base, dtype=np.float32)
    for k in range(NSAMP):
        s = 1.0 + reach * k / (NSAMP - 1)
        Ms = np.float32([[s, 0, ANCH_X * (1 - s)], [0, s, ANCH_Y * (1 - s)]])
        acc += cv2.warpAffine(base, Ms, (OUTW, OUTH), flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_REPLICATE)
    blurred = acc / NSAMP

    outf = base * mask + blurred * (1.0 - mask)
    enc.stdin.write(np.clip(outf, 0, 255).astype(np.uint8).tobytes())

cap.release(); enc.stdin.close(); enc.wait()
print(f"wrote {out}  ({nfr} frames, {nfr/FPS:.3f} s, zoom {ZOOM} +{PULSE} pulse @ {BPM} BPM)")
