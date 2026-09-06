"""
Final overlay: push-up rep counter (top-right, pop animation) + live
elbow-angle sparkline (bottom) + distinct-cat counter (top-left, increments
only when a NEW cat identity is first seen, capped at 2).

Usage:
    python render_combined_overlay.py <video_path> <pushup_csv> <cat_csv> <out_video>
"""
import sys
import csv

import cv2
import numpy as np
from scipy.signal import find_peaks, savgol_filter

POP_DURATION_FRAMES = 12
BASE_FONT_SCALE = 2.2
POP_FONT_SCALE = 3.2
MARGIN = 30

GRAPH_HEIGHT = 140
GRAPH_MARGIN = 20
GRAPH_WINDOW_S = 6.0

CAT_FONT_SCALE = 1.3


def load_pushup_signal(csv_path):
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
    return time_s, smoothed, set(valleys.tolist())


def load_cat_signal(csv_path, n_frames):
    """Returns per-frame cumulative distinct-cat count (increments at each
    new cat_id's first-seen frame, chronological order)."""
    rows = list(csv.DictReader(open(csv_path)))
    first_seen = {}  # cat_id -> first frame index
    for r in rows:
        if r["cat_id"] == "":
            continue
        cat_id = int(r["cat_id"])
        frame = int(r["frame"])
        if cat_id not in first_seen or frame < first_seen[cat_id]:
            first_seen[cat_id] = frame

    increment_frames = sorted(first_seen.values())

    cumulative = np.zeros(n_frames, dtype=int)
    count = 0
    inc_idx = 0
    for i in range(n_frames):
        while inc_idx < len(increment_frames) and increment_frames[inc_idx] == i:
            count += 1
            inc_idx += 1
        cumulative[i] = count
    return cumulative, increment_frames


def draw_pushup_counter(frame, w, count, pop_progress):
    scale = POP_FONT_SCALE - (POP_FONT_SCALE - BASE_FONT_SCALE) * pop_progress
    text = str(count)
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 6
    (tw, th), baseline = cv2.getTextSize(text, font, scale, thickness)
    x = w - MARGIN - tw
    y = MARGIN + th
    pad = 18
    overlay = frame.copy()
    cv2.rectangle(overlay, (x - pad, y - th - pad), (x + tw + pad, y + baseline + pad), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)
    color = (255, 255, 255) if pop_progress > 0.3 else (80, 230, 120)
    cv2.putText(frame, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)
    label = "REPS"
    (ltw, lth), _ = cv2.getTextSize(label, font, 0.6, 2)
    cv2.putText(frame, label, (x, y - th - 4), font, 0.6, (200, 200, 200), 2, cv2.LINE_AA)


def draw_cat_counter(frame, cat_count, pop_progress):
    scale = CAT_FONT_SCALE + (0.6 * (1 - pop_progress))
    text = f"CATS: {cat_count}/2"
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 3
    (tw, th), baseline = cv2.getTextSize(text, font, scale, thickness)
    x, y = MARGIN, MARGIN + th
    pad = 14
    overlay = frame.copy()
    cv2.rectangle(overlay, (x - pad, y - th - pad), (x + tw + pad, y + baseline + pad), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)
    color = (255, 255, 255) if pop_progress > 0.3 else (255, 180, 60)
    cv2.putText(frame, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)


def draw_graph(frame, w, h, time_s, smoothed, valley_frames, frame_idx):
    gx0, gx1 = GRAPH_MARGIN, w - GRAPH_MARGIN
    gy0, gy1 = h - GRAPH_MARGIN - GRAPH_HEIGHT, h - GRAPH_MARGIN
    overlay = frame.copy()
    cv2.rectangle(overlay, (gx0, gy0), (gx1, gy1), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)

    t_now = time_s[frame_idx]
    t_start = max(0.0, t_now - GRAPH_WINDOW_S)
    lo = np.searchsorted(time_s, t_start)
    hi = frame_idx + 1
    if hi - lo < 2:
        return

    seg_t = time_s[lo:hi]
    seg_a = smoothed[lo:hi]
    a_min, a_max = 0.0, 180.0
    xs = gx0 + (seg_t - seg_t[0]) / max(seg_t[-1] - seg_t[0], 1e-6) * (gx1 - gx0)
    ys = gy1 - (seg_a - a_min) / (a_max - a_min) * (gy1 - gy0)
    pts = np.stack([xs, ys], axis=1).astype(np.int32)
    cv2.polylines(frame, [pts], False, (80, 230, 120), 3, cv2.LINE_AA)
    cv2.putText(frame, "elbow angle", (gx0 + 8, gy0 + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)

    for vf in valley_frames:
        if lo <= vf < hi:
            vt = time_s[vf]
            vx = gx0 + (vt - seg_t[0]) / max(seg_t[-1] - seg_t[0], 1e-6) * (gx1 - gx0)
            vy = gy1 - (smoothed[vf] - a_min) / (a_max - a_min) * (gy1 - gy0)
            cv2.circle(frame, (int(vx), int(vy)), 7, (60, 60, 255), -1, cv2.LINE_AA)


def main():
    video_path, pushup_csv, cat_csv, out_path = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

    time_s, smoothed, valley_frames = load_pushup_signal(pushup_csv)
    n_frames = len(time_s)
    cat_cumulative, cat_increment_frames = load_cat_signal(cat_csv, n_frames)
    cat_increment_set = set(cat_increment_frames)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(out_path, fourcc, fps, (w, h))

    rep_count = 0
    frame_idx = 0
    rep_pop_left = 0
    cat_pop_left = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if frame_idx in valley_frames:
            rep_count += 1
            rep_pop_left = POP_DURATION_FRAMES
        if frame_idx in cat_increment_set:
            cat_pop_left = POP_DURATION_FRAMES

        rep_pop_progress = 1.0 - (rep_pop_left / POP_DURATION_FRAMES) if rep_pop_left > 0 else 1.0
        cat_pop_progress = 1.0 - (cat_pop_left / POP_DURATION_FRAMES) if cat_pop_left > 0 else 1.0
        if rep_pop_left > 0:
            rep_pop_left -= 1
        if cat_pop_left > 0:
            cat_pop_left -= 1

        draw_graph(frame, w, h, time_s, smoothed, valley_frames, frame_idx)

        if rep_count > 0:
            draw_pushup_counter(frame, w, rep_count, rep_pop_progress)

        draw_cat_counter(frame, cat_cumulative[frame_idx], cat_pop_progress)

        writer.write(frame)
        frame_idx += 1

    cap.release()
    writer.release()
    print(f"wrote {out_path}, total reps={rep_count}, total distinct cats={cat_cumulative[-1]}")


if __name__ == "__main__":
    main()
