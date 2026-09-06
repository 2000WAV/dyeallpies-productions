"""Second pass for frames the first hand pass missed: pad the frame so a hand cut by the
edge becomes a whole object, lower the thresholds, IMAGE mode (no tracking history).
    python hands_retry.py <video> <model> <hands.npz> <out.npz> [pad_frac=0.3]"""
import sys, numpy as np, cv2, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
video, model, inp, out = sys.argv[1:5]
PAD = float(sys.argv[5]) if len(sys.argv) > 5 else 0.3
z = np.load(inp); img = z["img"].copy(); score = z["score"].copy(); handed = z["handed"].copy()
have = ~np.isnan(img[:, 0, 0, 0])
opts = vision.HandLandmarkerOptions(base_options=BaseOptions(model_asset_path=model), running_mode=vision.RunningMode.IMAGE,
                                    num_hands=2, min_hand_detection_confidence=0.15, min_hand_presence_confidence=0.15)
det = vision.HandLandmarker.create_from_options(opts)
cap = cv2.VideoCapture(video); i = 0; fixed = 0
while True:
    ok, fr = cap.read()
    if not ok: break
    if i < have.shape[0] and not have[i]:
        H, W = fr.shape[:2]; px, py = int(W * PAD), int(H * PAD)
        big = cv2.copyMakeBorder(fr, py, py, px, px, cv2.BORDER_CONSTANT, value=(128, 128, 128))
        res = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(big, cv2.COLOR_BGR2RGB)))
        best = None
        for lms, hd in zip(res.hand_landmarks, res.handedness):
            pts = np.array([((l.x * big.shape[1] - px) / W, (l.y * big.shape[0] - py) / H, l.z) for l in lms], np.float32)
            inside = ((pts[:, 0] > 0) & (pts[:, 0] < 1) & (pts[:, 1] > 0) & (pts[:, 1] < 1)).mean()
            if inside >= 0.3 and (best is None or hd[0].score > best[1]): best = (pts, hd[0].score, hd[0].category_name)
        if best:
            img[i, 0] = best[0]; score[i, 0] = best[1]; handed[i, 0] = 1 if best[2] == "Right" else 0; fixed += 1
    i += 1
np.savez_compressed(out, img=img, score=score, handed=handed, fps=z["fps"], width=z["width"], height=z["height"], n_frames=z["n_frames"])
print("recovered", fixed, "frames; now", int((~np.isnan(img[:, 0, 0, 0])).sum()), "of", img.shape[0])
missing = np.where(np.isnan(img[:, 0, 0, 0]))[0]
print("still missing (s):", sorted(set(np.round(missing / 30.0, 1).tolist())))
