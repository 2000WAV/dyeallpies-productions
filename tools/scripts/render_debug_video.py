"""
Render a debug video overlaying the smoothed elbow angle and running rep
count, so the count can be visually verified against the source footage.

Usage:
    python render_debug_video.py <video_path> <signal_csv> <out_video>
"""
import sys
import csv

import cv2
import numpy as np
from scipy.signal import find_peaks, savgol_filter


def main():
    video_path, csv_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

    rows = list(csv.DictReader(open(csv_path)))
    time_s = np.array([float(r["time_s"]) for r in rows])
    angle = np.full(len(rows), np.nan)
    for i, r in enumerate(rows):
        l = float(r["left_elbow_angle"]) if r["left_elbow_angle"] else np.nan
        rr = float(r["right_elbow_angle"]) if r["right_elbow_angle"] else np.nan
        vals = [v for v in (l, rr) if not np.isnan(v)]
        if vals:
            angle[i] = sum(vals) / len(vals)
    nans = np.isnan(angle)
    if nans.any():
        angle[nans] = np.interp(time_s[nans], time_s[~nans], angle[~nans])

    window = min(31, len(angle) - (1 - len(angle) % 2))
    if window % 2 == 0:
        window -= 1
    smoothed = savgol_filter(angle, window_length=window, polyorder=3)

    valleys, _ = find_peaks(-smoothed, prominence=20, distance=15)
    valley_set = set(valleys.tolist())

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(out_path, fourcc, fps, (w, h))

    rep_count = 0
    frame_idx = 0
    flash_frames_left = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if frame_idx in valley_set:
            rep_count += 1
            flash_frames_left = 10

        a = smoothed[frame_idx] if frame_idx < len(smoothed) else None

        color = (0, 255, 0) if flash_frames_left > 0 else (255, 255, 255)
        cv2.putText(frame, f"REPS: {rep_count}", (20, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 4, cv2.LINE_AA)
        if a is not None:
            cv2.putText(frame, f"angle: {a:.0f}", (20, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2, cv2.LINE_AA)

        writer.write(frame)
        frame_idx += 1
        if flash_frames_left > 0:
            flash_frames_left -= 1

    cap.release()
    writer.release()
    print(f"wrote {out_path}, total reps={rep_count}")


if __name__ == "__main__":
    main()
