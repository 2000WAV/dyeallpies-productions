"""
Second MediaPipe pass with segmentation masks, to measure the torso SILHOUETTE
(lats / chest / waist / hip widths along the shoulder->hip axis) and to cut a
perspective-normalised torso patch per frame for lighting/texture analysis.

    python extract_torso.py <video> <model.task> <out.npz> [patch_w patch_h]

npz keys:
  fps, n_frames, taxis (K,)      fractions along shoulder-mid -> hip-mid axis (-0.2 .. 1.1)
  width_px (N, K)                silhouette width perpendicular to the axis (NaN if no pose)
  width_l, width_r (N, K)        the two half-widths (person's left = image right)
  axis_len (N,)                  shoulder-mid -> hip-mid length in px
  patch (N, ph, pw) uint8        grey torso patch (quad from shoulders/hips, widened 35 %,
                                 extended 25 % above the shoulders, 8 % below the hips)
  patch_rgb_mean (N, ph, pw, 3)  not stored (too big); colour means are computed later
  thumb (N, 192, 108) uint8      mask thumbnail
"""
import sys, time
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

L_SH, R_SH, L_HIP, R_HIP = 11, 12, 23, 24


def main():
    video, model, out = sys.argv[1:4]
    pw = int(sys.argv[4]) if len(sys.argv) > 4 else 240
    ph = int(sys.argv[5]) if len(sys.argv) > 5 else 320
    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    taxis = np.round(np.arange(-0.2, 1.101, 0.05), 3); K = len(taxis)
    width = np.full((n, K), np.nan, np.float32); wl = np.full((n, K), np.nan, np.float32); wr = np.full((n, K), np.nan, np.float32)
    axis_len = np.full(n, np.nan, np.float32)
    patch = np.zeros((n, ph, pw), np.uint8); thumb = np.zeros((n, 192, 108), np.uint8)
    ok = np.zeros(n, bool)

    opts = vision.PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path=model),
                                        running_mode=vision.RunningMode.VIDEO, num_poses=1,
                                        min_pose_detection_confidence=0.5, min_pose_presence_confidence=0.5,
                                        min_tracking_confidence=0.5, output_segmentation_masks=True)
    dst = np.float32([[0, 0], [pw, 0], [pw, ph], [0, ph]])
    t0 = time.time()
    with vision.PoseLandmarker.create_from_options(opts) as lm:
        i = 0
        while True:
            got, frame = cap.read()
            if not got or i >= n:
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = lm.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), int(round(i * 1000.0 / fps)))
            if res.pose_landmarks and res.segmentation_masks:
                ok[i] = True
                p = res.pose_landmarks[0]
                P = np.array([(l.x * W, l.y * H) for l in p], np.float32)
                mask = res.segmentation_masks[0].numpy_view() > 0.5
                thumb[i] = cv2.resize(mask.astype(np.uint8) * 255, (108, 192), interpolation=cv2.INTER_AREA)
                sm = (P[L_SH] + P[R_SH]) / 2; hm = (P[L_HIP] + P[R_HIP]) / 2
                ax = hm - sm; L = float(np.linalg.norm(ax)); axis_len[i] = L
                u = ax / (L + 1e-6); perp = np.array([-u[1], u[0]])   # perp points to image-left of the axis direction
                # silhouette widths: walk both ways along perp from the axis point until the mask ends
                for k, tt in enumerate(taxis):
                    c = sm + tt * ax
                    half = []
                    for sgn in (-1, 1):
                        d = 0
                        for step in range(0, 500, 2):
                            q = c + sgn * step * perp
                            x, y = int(round(q[0])), int(round(q[1]))
                            if x < 0 or y < 0 or x >= W or y >= H or not mask[y, x]:
                                break
                            d = step
                        half.append(d)
                    # sgn=-1 walks toward image-right when the axis points down (perp = (-uy, ux) -> (-1,0) for u=(0,1))
                    wr[i, k] = half[0]; wl[i, k] = half[1]; width[i, k] = half[0] + half[1]
                # torso patch: quad widened and extended in the axis frame
                sw = np.linalg.norm(P[R_SH] - P[L_SH]); hw = np.linalg.norm(P[R_HIP] - P[L_HIP])
                bw = max(sw, hw) * 1.35 / 2
                top = sm - 0.25 * ax; bot = hm + 0.08 * ax
                # image-left/right corners: use perp so that the patch is upright along the axis
                quad = np.float32([top + perp * bw, top - perp * bw, bot - perp * bw, bot + perp * bw])
                M = cv2.getPerspectiveTransform(quad, dst)
                g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                patch[i] = cv2.warpPerspective(g, M, (pw, ph), flags=cv2.INTER_LINEAR)
            i += 1
            if i % 100 == 0:
                el = time.time() - t0; print(f"  {i}/{n}  {el:.0f}s ({i/el:.1f} fps)", flush=True)
    cap.release()
    np.savez_compressed(out, fps=fps, n_frames=i, taxis=taxis, width_px=width[:i], width_l=wl[:i], width_r=wr[:i],
                        axis_len=axis_len[:i], patch=patch[:i], thumb=thumb[:i], ok=ok[:i])
    print(f"done -> {out}  ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
