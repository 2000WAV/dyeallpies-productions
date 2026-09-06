"""Third pass: for frames still without a hand, crop the left-edge region where the
hand fragment sits, upscale it and pad it, detect, map back; keep a detection only if
enough of it lands inside the real frame.
    python hands_retry_roi.py <video> <model> <hands.npz> <out.npz>"""
import sys, numpy as np, cv2, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
video, model, inp, out = sys.argv[1:5]
z = np.load(inp); img = z["img"].copy(); score = z["score"].copy(); handed = z["handed"].copy()
have = ~np.isnan(img[:, 0, 0, 0])
opts = vision.HandLandmarkerOptions(base_options=BaseOptions(model_asset_path=model), running_mode=vision.RunningMode.IMAGE,
                                    num_hands=1, min_hand_detection_confidence=0.1, min_hand_presence_confidence=0.1)
det = vision.HandLandmarker.create_from_options(opts)
cap = cv2.VideoCapture(video); i = 0; fixed = 0
while True:
    ok, fr = cap.read()
    if not ok: break
    if i < have.shape[0] and not have[i]:
        H, W = fr.shape[:2]
        x0, x1, y0, y1 = 0, int(0.5 * W), int(0.25 * H), int(0.8 * H)
        roi = fr[y0:y1, x0:x1]
        roi = cv2.resize(roi, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        px, py = int(roi.shape[1] * 0.5), int(roi.shape[0] * 0.3)
        big = cv2.copyMakeBorder(roi, py, py, px, px, cv2.BORDER_CONSTANT, value=(128, 128, 128))
        res = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(big, cv2.COLOR_BGR2RGB)))
        for lms, hd in zip(res.hand_landmarks, res.handedness):
            pts = np.array([(((l.x * big.shape[1] - px) / 2.0 + x0) / W, ((l.y * big.shape[0] - py) / 2.0 + y0) / H, l.z) for l in lms], np.float32)
            inside = ((pts[:, 0] > 0) & (pts[:, 0] < 1) & (pts[:, 1] > 0) & (pts[:, 1] < 1)).sum()
            if inside >= 6:
                img[i, 0] = pts; score[i, 0] = hd[0].score; handed[i, 0] = 1 if hd[0].category_name == "Right" else 0; fixed += 1; break
    i += 1
np.savez_compressed(out, img=img, score=score, handed=handed, fps=z["fps"], width=z["width"], height=z["height"], n_frames=z["n_frames"])
print("recovered", fixed, "frames; now", int((~np.isnan(img[:, 0, 0, 0])).sum()), "of", img.shape[0])
missing = np.where(np.isnan(img[:, 0, 0, 0]))[0]
print("still missing (s):", sorted(set(np.round(missing / 30.0, 1).tolist())))
