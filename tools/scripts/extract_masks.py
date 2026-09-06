"""
Person segmentation mask for every frame (MediaPipe PoseLandmarker heavy), stored at a
third of the frame size as uint8 (0-255 soft mask) for the heat overlay.

    python extract_masks.py <video> <model.task> <out.npz> [scale_div]
"""
import sys, time
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions


def main():
    video, model, out = sys.argv[1:4]
    div = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    w, h = W // div, H // div
    masks = np.zeros((n, h, w), np.uint8)
    opts = vision.PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path=model),
                                        running_mode=vision.RunningMode.VIDEO, num_poses=1,
                                        min_pose_detection_confidence=0.5, min_pose_presence_confidence=0.5,
                                        min_tracking_confidence=0.5, output_segmentation_masks=True)
    t0 = time.time(); i = 0
    with vision.PoseLandmarker.create_from_options(opts) as lm:
        while True:
            got, frame = cap.read()
            if not got or i >= n:
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = lm.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), int(round(i * 1000.0 / fps)))
            if res.segmentation_masks:
                m = res.segmentation_masks[0].numpy_view()
                masks[i] = cv2.resize((np.clip(m, 0, 1) * 255).astype(np.uint8), (w, h), interpolation=cv2.INTER_AREA)
            i += 1
            if i % 200 == 0:
                el = time.time() - t0; print(f"  {i}/{n} {el:.0f}s ({i/el:.1f} fps)", flush=True)
    cap.release()
    np.savez_compressed(out, fps=fps, n_frames=i, div=div, masks=masks[:i])
    print(f"done -> {out} ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
