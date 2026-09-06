"""Track the speaker's head through a video; write smoothed per-frame anchors as JSON.

Usage: track_face.py <video> <out.json> [--every N]

Used to anchor beat-synced punch-in zooms on the speaker instead of on frame centre.
A centre-anchored zoom drifts off the subject whenever they are off-centre, which in
handheld selfie footage is most of the time.

Uses the MediaPipe PoseLandmarker task model already vendored in tools/models
(no download): landmarks 0-10 are the face (nose, eyes, ears, mouth), and their
centroid is a stabler head anchor than a face box on fast-moving handheld footage.
Gaps are interpolated and the track is smoothed -- a jittery anchor makes the zoom
look broken rather than energetic.
"""
import sys, json
import numpy as np, cv2
import mediapipe as mp
from mediapipe.tasks import python as mpy
from mediapipe.tasks.python import vision

src, out = sys.argv[1], sys.argv[2]
EVERY = int(sys.argv[sys.argv.index("--every") + 1]) if "--every" in sys.argv else 1
MODEL = "tools/models/pose_landmarker_lite.task"

cap = cv2.VideoCapture(src)
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
N = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); FPS = cap.get(cv2.CAP_PROP_FPS)
print(f"{src}: {W}x{H} {N} frames @ {FPS:.2f} fps")

opts = vision.PoseLandmarkerOptions(
    base_options=mpy.BaseOptions(model_asset_path=MODEL),
    running_mode=vision.RunningMode.VIDEO, num_poses=1, min_pose_detection_confidence=0.3)
lm = vision.PoseLandmarker.create_from_options(opts)

FACE = list(range(11))          # nose, eyes, ears, mouth corners
pts, i = [], 0
while True:
    ok, frame = cap.read()
    if not ok: break
    if i % EVERY == 0:
        img = mp.Image(image_format=mp.ImageFormat.SRGB,
                       data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        res = lm.detect_for_video(img, int(i * 1000 / FPS))
        if res.pose_landmarks:
            p = res.pose_landmarks[0]
            xs = [p[k].x for k in FACE if k < len(p)]
            ys = [p[k].y for k in FACE if k < len(p)]
            if xs:
                pts.append((i, float(np.mean(xs)) * W, float(np.mean(ys)) * H))
    i += 1
cap.release()
sampled = (N + EVERY - 1) // EVERY
print(f"detected in {len(pts)}/{sampled} sampled frames ({100*len(pts)/max(1,sampled):.0f}%)")
if not pts:
    raise SystemExit("no pose found - use a fixed anchor instead")

idx = np.array([p[0] for p in pts], float)
allf = np.arange(N, dtype=float)
win = max(3, int(FPS * 0.5) | 1)
def smooth(vals):
    v = np.interp(allf, idx, np.array(vals, float))
    k = np.ones(win) / win
    return np.convolve(np.pad(v, (win, win), mode="edge"), k, mode="same")[win:-win]
cx, cy = smooth([p[1] for p in pts]), smooth([p[2] for p in pts])

json.dump({"src": src, "w": W, "h": H, "fps": FPS, "n": N,
           "detected_frac": round(len(pts) / max(1, sampled), 3),
           "cx": [round(v, 1) for v in cx], "cy": [round(v, 1) for v in cy]},
          open(out, "w"), indent=1)
print(f"wrote {out}")
print(f"head anchor: x {cx.min():.0f}-{cx.max():.0f} (mean {cx.mean():.0f}), "
      f"y {cy.min():.0f}-{cy.max():.0f} (mean {cy.mean():.0f}), frame {W}x{H}")
