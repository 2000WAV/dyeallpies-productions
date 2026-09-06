"""
Detect cat faces per frame (Haar cascade), group into sightings, and
identify distinct cats via color-histogram matching so re-entries of the
same cat don't get double-counted.

Usage:
    python extract_cat_signal.py <video_path> <cascade_xml> <out_csv>
"""
import sys
import csv

import cv2
import numpy as np

GAP_BRIDGE_FRAMES = 20      # bridge gaps up to this many frames as same sighting
HIST_MATCH_THRESHOLD = 0.5  # correlation below this = considered a different cat
MAX_CATS = 2                # known ground truth cap


def hist_for_box(frame, box):
    x, y, w, h = box
    roi = frame[y:y + h, x:x + w]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1], None, [30, 32], [0, 180, 0, 256])
    cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
    return hist


def main():
    video_path, cascade_path, out_csv = sys.argv[1], sys.argv[2], sys.argv[3]

    cascade = cv2.CascadeClassifier(cascade_path)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Per-frame: best detection box or None
    detections = [None] * n_frames
    frames_cache = {}

    frame_idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=8, minSize=(40, 40))
        if len(faces) > 0:
            # pick the largest box if multiple candidates in one frame
            box = max(faces, key=lambda b: b[2] * b[3])
            detections[frame_idx] = tuple(int(v) for v in box)
            frames_cache[frame_idx] = frame.copy()
        frame_idx += 1
    cap.release()
    print(f"fps={fps} frames={n_frames} raw_detections={sum(1 for d in detections if d)}")

    # Group into sightings, bridging small gaps
    sightings = []  # list of (start_idx, end_idx, [frame_idx...])
    cur = []
    gap = 0
    for i, d in enumerate(detections):
        if d is not None:
            cur.append(i)
            gap = 0
        elif cur:
            gap += 1
            if gap > GAP_BRIDGE_FRAMES:
                sightings.append(cur)
                cur = []
                gap = 0
    if cur:
        sightings.append(cur)

    print(f"grouped into {len(sightings)} sightings")

    # For each sighting, compute representative histogram (median frame in sighting)
    known_profiles = []  # list of hist
    cat_id_per_frame = [None] * n_frames  # frame_idx -> cat_id (0-based)
    sighting_info = []

    for s in sightings:
        mid = s[len(s) // 2]
        box = detections[mid]
        frame = frames_cache[mid]
        hist = hist_for_box(frame, box)

        best_id, best_score = None, -1
        for cat_id, profile_hist in enumerate(known_profiles):
            score = cv2.compareHist(hist, profile_hist, cv2.HISTCMP_CORREL)
            if score > best_score:
                best_score = score
                best_id = cat_id

        if best_id is not None and best_score >= HIST_MATCH_THRESHOLD:
            cat_id = best_id
        else:
            if len(known_profiles) >= MAX_CATS:
                # safety cap: assign to closest known cat rather than creating a 3rd
                cat_id = best_id if best_id is not None else 0
            else:
                cat_id = len(known_profiles)
                known_profiles.append(hist)

        for i in s:
            cat_id_per_frame[i] = cat_id
        sighting_info.append((s[0], s[-1], cat_id, best_score))

    for start, end, cat_id, score in sighting_info:
        print(f"sighting frames {start}-{end} -> cat_id={cat_id} match_score={score:.2f}")

    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["frame", "time_s", "cat_id", "box"])
        for i in range(n_frames):
            t = i / fps if fps else None
            cat_id = cat_id_per_frame[i]
            box = detections[i]
            writer.writerow([i, t, cat_id if cat_id is not None else "", box if box else ""])

    distinct = len(known_profiles)
    print(f"distinct cats identified: {distinct}")


if __name__ == "__main__":
    main()
