"""
Run an Ultralytics YOLO-pose model over every frame and save the 17 COCO
keypoints (x, y in pixels, confidence) of the highest-confidence person.
Independent cross-check for the MediaPipe track.

Usage:
    python extract_pose_yolo.py <video> <model.pt> <out.npz> [imgsz]
"""
import sys, time
import numpy as np
import cv2
from ultralytics import YOLO


def main():
    video, model_path, out = sys.argv[1:4]
    imgsz = int(sys.argv[4]) if len(sys.argv) > 4 else 640
    model = YOLO(model_path)
    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    kp = np.full((n, 17, 3), np.nan, dtype=np.float32)
    box = np.full((n, 5), np.nan, dtype=np.float32)
    t0 = time.time()
    i = 0
    while True:
        got, frame = cap.read()
        if not got or i >= n:
            break
        r = model.predict(frame, imgsz=imgsz, conf=0.25, verbose=False, device="cpu")[0]
        if r.keypoints is not None and len(r.boxes) > 0:
            j = int(r.boxes.conf.argmax())
            xy = r.keypoints.xy[j].cpu().numpy()
            cf = r.keypoints.conf[j].cpu().numpy()
            kp[i, :, :2] = xy
            kp[i, :, 2] = cf
            b = r.boxes.xyxy[j].cpu().numpy()
            box[i] = [*b, float(r.boxes.conf[j])]
        i += 1
        if i % 100 == 0:
            el = time.time() - t0
            print(f"  {i}/{n}  {el:.0f}s  ({i/el:.1f} fps)", flush=True)
    cap.release()
    np.savez_compressed(out, fps=fps, n_frames=i, kp=kp[:i], box=box[:i])
    print(f"done -> {out} ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
