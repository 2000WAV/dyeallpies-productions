"""
Final overlay v2:
- Rep detection fixed: uses smoothed shoulder-y (more robust to elbow
  occlusion/blur than elbow angle alone) with an elbow-angle sanity filter
  to reject shallow/false dips.
- Centered layout: big REPS number top-center (Impact font, pop animation),
  current rep depth in degrees just below it, smaller live CATS count
  below that.
- Cat count: live per-frame visibility (not cumulative-only-increase),
  capped at 2, from the YOLO-based signal CSV.

Usage:
    python render_final_v2.py <video_path> <pushup_csv> <cat_csv> <out_video>
"""
import sys
import csv

import cv2
import numpy as np
from scipy.signal import find_peaks, savgol_filter
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "C:/Windows/Fonts/impact.ttf"

POP_DURATION_FRAMES = 12
REPS_BASE_SIZE = 90
REPS_POP_SIZE = 130
DEG_SIZE = 40
CATS_BASE_SIZE = 46
CATS_POP_SIZE = 62
TOP_MARGIN = 24
LINE_GAP = 8

SY_PROMINENCE = 0.025
SY_DISTANCE = 20
SY_SMOOTH_WINDOW = 31
ANGLE_SANITY_MAX = 160  # reject "down" detections where arm is still nearly straight


def load_pushup_signal(csv_path):
    rows = list(csv.DictReader(open(csv_path)))
    time_s = np.array([float(r["time_s"]) for r in rows])

    sy = np.full(len(rows), np.nan)
    angle = np.full(len(rows), np.nan)
    for i, r in enumerate(rows):
        sy[i] = float(r["shoulder_y"]) if r["shoulder_y"] else np.nan
        l = float(r["left_elbow_angle"]) if r["left_elbow_angle"] else np.nan
        rr = float(r["right_elbow_angle"]) if r["right_elbow_angle"] else np.nan
        vals = [v for v in (l, rr) if not np.isnan(v)]
        if vals:
            angle[i] = sum(vals) / len(vals)

    nans = np.isnan(sy)
    sy[nans] = np.interp(time_s[nans], time_s[~nans], sy[~nans])
    nans2 = np.isnan(angle)
    angle[nans2] = np.interp(time_s[nans2], time_s[~nans2], angle[~nans2])

    smoothed_sy = savgol_filter(sy, window_length=SY_SMOOTH_WINDOW, polyorder=3)
    smoothed_angle = savgol_filter(angle, window_length=SY_SMOOTH_WINDOW, polyorder=3)

    peaks, _ = find_peaks(smoothed_sy, prominence=SY_PROMINENCE, distance=SY_DISTANCE)
    valleys = [p for p in peaks if smoothed_angle[p] < ANGLE_SANITY_MAX]

    return time_s, smoothed_angle, set(valleys)


GAP_BRIDGE_FRAMES = 45  # ~1.5s at 30fps -- bridge sparse hits into continuous sightings
OVERRIDE_2CATS_FROM_S = 98.0  # both cats confirmed visible from here to the end (manual override)


def load_cat_signal(csv_path, n_frames, fps):
    rows = list(csv.DictReader(open(csv_path)))
    live = np.zeros(n_frames, dtype=int)
    for r in rows:
        idx = int(r["frame"])
        if idx < n_frames:
            live[idx] = int(r["live_count"])

    # raw per-frame detection is sparse (confidence flickers even when the
    # cat is continuously visible), so bridge nearby hits into continuous
    # runs rather than just smoothing away single-frame noise
    detected_idx = np.where(live > 0)[0]
    runs = []
    cur = []
    for i in detected_idx:
        if cur and i - cur[-1] > GAP_BRIDGE_FRAMES:
            runs.append(cur)
            cur = []
        cur.append(i)
    if cur:
        runs.append(cur)

    bridged = np.zeros(n_frames, dtype=int)
    for run in runs:
        start, end = run[0], run[-1]
        vals = live[run]
        count = max(1, min(2, int(round(vals.mean()))))
        bridged[start:end + 1] = count

    override_start_frame = int(OVERRIDE_2CATS_FROM_S * fps)
    if override_start_frame < n_frames:
        bridged[override_start_frame:] = 2

    return bridged


def pil_font(size):
    return ImageFont.truetype(FONT_PATH, size)


def draw_centered_text(draw, cx, y, text, font, fill, stroke_width=0, stroke_fill=None):
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = cx - tw / 2 - bbox[0]
    draw.text((x, y - bbox[1]), text, font=font, fill=fill,
               stroke_width=stroke_width, stroke_fill=stroke_fill)
    return th


def main():
    video_path, pushup_csv, cat_csv, out_path = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

    time_s, smoothed_angle, valley_frames = load_pushup_signal(pushup_csv)
    n_frames = len(time_s)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    cat_live = load_cat_signal(cat_csv, n_frames, fps)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(out_path, fourcc, fps, (w, h))

    reps_font_base = pil_font(REPS_BASE_SIZE)
    deg_font = pil_font(DEG_SIZE)
    cats_font_base = pil_font(CATS_BASE_SIZE)

    rep_count = 0
    last_rep_angle = None
    frame_idx = 0
    pop_frames_left = 0
    prev_cat_live = cat_live[0] if n_frames else 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if frame_idx in valley_frames:
            rep_count += 1
            last_rep_angle = smoothed_angle[frame_idx]
            pop_frames_left = POP_DURATION_FRAMES

        pop_progress = 1.0 - (pop_frames_left / POP_DURATION_FRAMES) if pop_frames_left > 0 else 1.0
        if pop_frames_left > 0:
            pop_frames_left -= 1

        cats_pop = cat_live[frame_idx] != prev_cat_live
        prev_cat_live = cat_live[frame_idx]

        # composite via PIL for TrueType font support
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img)

        cx = w // 2
        y = TOP_MARGIN

        if rep_count > 0:
            reps_size = int(REPS_POP_SIZE - (REPS_POP_SIZE - REPS_BASE_SIZE) * pop_progress)
            reps_font = pil_font(reps_size)
            color = (255, 255, 255) if pop_progress > 0.3 else (100, 255, 140)
            th = draw_centered_text(draw, cx, y, str(rep_count), reps_font, color,
                                     stroke_width=4, stroke_fill=(0, 0, 0))
            y += th + LINE_GAP

            if last_rep_angle is not None:
                deg_text = f"{last_rep_angle:.0f}\u00b0 elbow bend"
                th2 = draw_centered_text(draw, cx, y, deg_text, deg_font, (255, 230, 120),
                                          stroke_width=2, stroke_fill=(0, 0, 0))
                y += th2 + LINE_GAP

        cats_size = int(CATS_POP_SIZE if cats_pop else CATS_BASE_SIZE)
        cats_font = pil_font(cats_size)
        cats_text = f"CATS {cat_live[frame_idx]}/2"
        draw_centered_text(draw, cx, y, cats_text, cats_font, (150, 210, 255),
                            stroke_width=3, stroke_fill=(0, 0, 0))

        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        writer.write(frame)
        frame_idx += 1

    cap.release()
    writer.release()
    print(f"wrote {out_path}, total reps={rep_count}")


if __name__ == "__main__":
    main()
