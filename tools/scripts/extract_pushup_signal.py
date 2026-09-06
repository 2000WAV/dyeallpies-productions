"""
Run MediaPipe PoseLandmarker (Tasks API) over a video, extract elbow-angle
signal per frame, save to CSV.

Usage:
    python extract_pushup_signal.py <video_path> <model_path> <output_csv>
"""
import sys
import csv
import math

import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

# Landmark indices per MediaPipe Pose spec
LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST = 11, 13, 15
RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST = 12, 14, 16


def angle(a, b, c):
    """Angle at point b, formed by rays b->a and b->c, in degrees."""
    ax, ay = a[0] - b[0], a[1] - b[1]
    cx, cy = c[0] - b[0], c[1] - b[1]
    dot = ax * cx + ay * cy
    mag_a = math.hypot(ax, ay)
    mag_c = math.hypot(cx, cy)
    if mag_a == 0 or mag_c == 0:
        return None
    cos_theta = max(-1.0, min(1.0, dot / (mag_a * mag_c)))
    return math.degrees(math.acos(cos_theta))


def main():
    video_path, model_path, out_csv = sys.argv[1], sys.argv[2], sys.argv[3]

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"fps={fps} frames={n_frames}")

    options = vision.PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    rows = []
    with vision.PoseLandmarker.create_from_options(options) as landmarker:
        frame_idx = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            timestamp_ms = int((frame_idx / fps) * 1000) if fps else frame_idx
            result = landmarker.detect_for_video(mp_image, timestamp_ms)

            row = {
                "frame": frame_idx,
                "time_s": frame_idx / fps if fps else None,
                "left_elbow_angle": None,
                "right_elbow_angle": None,
                "shoulder_y": None,
                "visibility": None,
            }

            if result.pose_landmarks:
                lm = result.pose_landmarks[0]

                def pt(idx):
                    return (lm[idx].x, lm[idx].y)

                l_sh, l_el, l_wr = pt(LEFT_SHOULDER), pt(LEFT_ELBOW), pt(LEFT_WRIST)
                r_sh, r_el, r_wr = pt(RIGHT_SHOULDER), pt(RIGHT_ELBOW), pt(RIGHT_WRIST)

                row["left_elbow_angle"] = angle(l_sh, l_el, l_wr)
                row["right_elbow_angle"] = angle(r_sh, r_el, r_wr)
                row["shoulder_y"] = (l_sh[1] + r_sh[1]) / 2
                row["visibility"] = (lm[LEFT_ELBOW].visibility + lm[RIGHT_ELBOW].visibility) / 2

            rows.append(row)
            frame_idx += 1

    cap.release()

    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} rows to {out_csv}")


if __name__ == "__main__":
    main()
