"""
Matte components for the heat overlay, per frame, stored as a uint8 memmap (N, H/div, W/div, 3):

    [..., 0]  RVM alpha            - the person, full-resolution outline (Lin et al. 2022)
    [..., 1]  clothes confidence   - MediaPipe selfie_multiclass class 4
    [..., 2]  head confidence      - MediaPipe selfie_multiclass hair (1) + face-skin (3)

The paint region is composed later (pullup_heat.py) as alpha x (1 - clothes) x (1 - head),
with the head term gated to the neighbourhood of the head landmarks: with the face out of
view (behind the bar) the segmenter sometimes labels the chest as face-skin, and a tattoo as
clothes - neither may punch a hole in the torso.

    python extract_matte.py <video> <out.npy> [div=2]
"""
import sys, time
import numpy as np
import cv2
import torch
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

HAIR, BODY_SKIN, FACE_SKIN, CLOTHES = 1, 2, 3, 4


def main():
    video, out = sys.argv[1:3]
    div = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    w, h = W // div, H // div
    comp = np.lib.format.open_memmap(out, mode="w+", dtype=np.uint8, shape=(n, h, w, 3))

    rvm = torch.hub.load("PeterL1n/RobustVideoMatting", "mobilenetv3", trust_repo=True).eval()
    seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
        base_options=BaseOptions(model_asset_path="tools/models/selfie_multiclass_256x256.tflite"),
        running_mode=vision.RunningMode.VIDEO, output_category_mask=False, output_confidence_masks=True))
    rec = [None] * 4
    t0 = time.time(); i = 0
    with torch.no_grad():
        while True:
            got, frame = cap.read()
            if not got or i >= n:
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            src = torch.from_numpy(rgb).permute(2, 0, 1).float().div(255)[None]
            fgr, pha, *rec = rvm(src, *rec, downsample_ratio=0.25)
            alpha = pha[0, 0].numpy()
            res = seg.segment_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), int(round(i * 1000.0 / fps)))
            cm = [np.squeeze(m.numpy_view()) for m in res.confidence_masks]
            clothes = cm[CLOTHES]; head = np.clip(cm[HAIR] + cm[FACE_SKIN], 0, 1)
            stack = np.dstack([alpha, clothes, head])
            comp[i] = cv2.resize((np.clip(stack, 0, 1) * 255).astype(np.uint8), (w, h), interpolation=cv2.INTER_AREA)
            i += 1
            if i % 100 == 0:
                el = time.time() - t0; print(f"  {i}/{n} {el:.0f}s ({i/el:.1f} fps)", flush=True)
    comp.flush(); cap.release()
    print(f"done -> {out} ({i} frames, {time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
