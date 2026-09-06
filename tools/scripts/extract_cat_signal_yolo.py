"""
Detect cats per frame with YOLOv8n (robust to any body angle, not just
frontal faces), then identify distinct individuals via color-histogram
matching on the detected boxes so re-entries of the same cat don't
double-count. Outputs a per-frame live visibility count (capped at 2).

Usage:
    python extract_cat_signal_yolo.py <video_path> <model_path> <out_csv>
"""
import sys
import csv

import cv2
import numpy as np
from ultralytics import YOLO

CAT_CLASS_ID = 15
DOG_CLASS_ID = 16  # small/partial cat views are frequently misclassified as dog by COCO models
CONF_THRESHOLD = 0.15
MAX_CATS = 2
HIST_MATCH_THRESHOLD = 0.4
MAX_BOX_AREA_FRAC = 0.15  # reject large boxes -- likely the person/shirt, not the small background cat


def hist_for_box(frame, box):
    x1, y1, x2, y2 = box
    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return None
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1], None, [30, 32], [0, 180, 0, 256])
    cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
    return hist


def main():
    video_path, model_path, out_csv = sys.argv[1], sys.argv[2], sys.argv[3]

    model = YOLO(model_path)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"fps={fps} frames={n_frames}")

    known_profiles = []  # list of hist
    rows = []
    frame_area = None

    frame_idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_area is None:
            frame_area = frame.shape[0] * frame.shape[1]

        results = model.predict(frame, verbose=False, conf=CONF_THRESHOLD,
                                 classes=[CAT_CLASS_ID, DOG_CLASS_ID])
        boxes = []
        if results and len(results[0].boxes) > 0:
            for b in results[0].boxes:
                x1, y1, x2, y2 = [int(v) for v in b.xyxy[0].tolist()]
                area_frac = (x2 - x1) * (y2 - y1) / frame_area
                if area_frac > MAX_BOX_AREA_FRAC:
                    continue
                boxes.append((x1, y1, x2, y2))

        frame_cat_ids = []
        for box in boxes:
            hist = hist_for_box(frame, box)
            if hist is None:
                continue
            best_id, best_score = None, -1
            for cat_id, profile_hist in enumerate(known_profiles):
                score = cv2.compareHist(hist, profile_hist, cv2.HISTCMP_CORREL)
                if score > best_score:
                    best_score = score
                    best_id = cat_id

            if best_id is not None and best_score >= HIST_MATCH_THRESHOLD:
                cat_id = best_id
                # slowly adapt profile toward latest observation
                known_profiles[cat_id] = 0.8 * known_profiles[cat_id] + 0.2 * hist
            elif len(known_profiles) < MAX_CATS:
                cat_id = len(known_profiles)
                known_profiles.append(hist)
            else:
                cat_id = best_id if best_id is not None else 0

            if cat_id not in frame_cat_ids:
                frame_cat_ids.append(cat_id)

        rows.append({
            "frame": frame_idx,
            "time_s": frame_idx / fps if fps else None,
            "cat_ids": ";".join(str(c) for c in sorted(frame_cat_ids)),
            "live_count": min(len(frame_cat_ids), MAX_CATS),
        })
        frame_idx += 1

    cap.release()

    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["frame", "time_s", "cat_ids", "live_count"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} rows to {out_csv}, distinct cat profiles={len(known_profiles)}")


if __name__ == "__main__":
    main()
