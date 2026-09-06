"""MediaPipe Hand Landmarker over every frame of a video -> npz of 21-point hand skeletons.

    python extract_hands_mp.py <video> <hand_landmarker.task> <out.npz> [num_hands=2]

Stores img (n, num_hands, 21, 3) normalised x,y,z (nan where no hand), score (n, num_hands),
handed (n, num_hands) 0=Left 1=Right (as MediaPipe labels them, i.e. mirrored for a
selfie camera), plus fps/width/height. VIDEO running mode so tracking is temporally smooth.
"""
import sys, time
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

video, model, out = sys.argv[1], sys.argv[2], sys.argv[3]
NH = int(sys.argv[4]) if len(sys.argv) > 4 else 2
cap = cv2.VideoCapture(video)
fps = cap.get(cv2.CAP_PROP_FPS); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
opts = vision.HandLandmarkerOptions(base_options=BaseOptions(model_asset_path=model),
                                    running_mode=vision.RunningMode.VIDEO, num_hands=NH,
                                    min_hand_detection_confidence=0.4, min_hand_presence_confidence=0.4,
                                    min_tracking_confidence=0.4)
det = vision.HandLandmarker.create_from_options(opts)
img = np.full((n, NH, 21, 3), np.nan, np.float32); score = np.zeros((n, NH), np.float32); handed = np.full((n, NH), -1, np.int8)
i = 0; t0 = time.time(); W = H = None
while True:
    ok, fr = cap.read()
    if not ok: break
    if W is None: H, W = fr.shape[:2]
    mpimg = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
    res = det.detect_for_video(mpimg, int(round(i * 1000.0 / fps)))
    for h, (lms, hd) in enumerate(zip(res.hand_landmarks, res.handedness)):
        if h >= NH: break
        img[i, h] = [(l.x, l.y, l.z) for l in lms]
        score[i, h] = hd[0].score; handed[i, h] = 1 if hd[0].category_name == "Right" else 0
    i += 1
    if i % 100 == 0: print(f"{i}/{n} {i/(time.time()-t0):.1f} fps", flush=True)
np.savez_compressed(out, img=img[:i], score=score[:i], handed=handed[:i], fps=fps, width=W, height=H, n_frames=i)
print("hands on", int((~np.isnan(img[:i, :, 0, 0])).any(axis=1).sum()), "of", i, "frames")
