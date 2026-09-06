"""
Run MediaPipe PoseLandmarker (Tasks API, VIDEO mode) over every frame of a video
and save ALL 33 landmarks: image-normalized (x, y, z, visibility, presence) and
metric world coordinates (x, y, z in metres, hip-centred).

Usage:
    python extract_pose_mp.py <video> <model.task> <out.npz>

Output npz keys:
    fps, width, height, n_frames
    img   (N, 33, 5)  normalized x,y,z,visibility,presence   (NaN where no pose)
    world (N, 33, 3)  world x,y,z metres                      (NaN where no pose)
    ok    (N,)        bool, pose found this frame
"""
import sys, time
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions


def main():
    video, model, out = sys.argv[1:4]
    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"{video}: {w}x{h} @ {fps:.3f} fps, {n} frames", flush=True)

    img = np.full((n, 33, 5), np.nan, dtype=np.float32)
    world = np.full((n, 33, 3), np.nan, dtype=np.float32)
    ok = np.zeros(n, dtype=bool)

    opts = vision.PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model),
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        output_segmentation_masks=False,
    )
    t0 = time.time()
    with vision.PoseLandmarker.create_from_options(opts) as lm:
        i = 0
        while True:
            got, frame = cap.read()
            if not got or i >= n:
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mpi = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            res = lm.detect_for_video(mpi, int(round(i * 1000.0 / fps)))
            if res.pose_landmarks:
                p = res.pose_landmarks[0]
                img[i] = [(l.x, l.y, l.z, l.visibility, l.presence) for l in p]
                wl = res.pose_world_landmarks[0]
                world[i] = [(l.x, l.y, l.z) for l in wl]
                ok[i] = True
            i += 1
            if i % 100 == 0:
                el = time.time() - t0
                print(f"  {i}/{n}  {el:.0f}s  ({i/el:.1f} fps)", flush=True)
    cap.release()
    np.savez_compressed(out, fps=fps, width=w, height=h, n_frames=i,
                        img=img[:i], world=world[:i], ok=ok[:i])
    print(f"done: {ok[:i].sum()}/{i} frames with pose -> {out}  ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
