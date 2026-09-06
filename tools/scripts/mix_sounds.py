"""
Mix real sound effects into the clip's audio track: a notification "ding"
played in full on each rep, and a real cat "meow" played in full on each
cat-count increment.

Usage:
    python mix_sounds.py <video_path> <pushup_csv> <cat_csv> <ding_wav> <meow_wav> <out_wav>
"""
import sys
import csv
import subprocess

import numpy as np
from scipy.signal import find_peaks, savgol_filter
from scipy.io import wavfile

SR = 44100

# --- rep detection (same logic as render_final_v2.py) ---
SY_PROMINENCE = 0.025
SY_DISTANCE = 20
SY_SMOOTH_WINDOW = 31
ANGLE_SANITY_MAX = 160

# --- cat detection (same logic as render_final_v2.py) ---
GAP_BRIDGE_FRAMES = 45
OVERRIDE_2CATS_FROM_S = 98.0

DING_VOLUME = 0.9
MEOW_VOLUME = 0.9


def load_pushup_events(csv_path):
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
    valleys = sorted(p for p in peaks if smoothed_angle[p] < ANGLE_SANITY_MAX)
    return [time_s[p] for p in valleys]


def load_cat_increment_events(csv_path, n_frames, fps):
    rows = list(csv.DictReader(open(csv_path)))
    live = np.zeros(n_frames, dtype=int)
    time_s = np.zeros(n_frames)
    for r in rows:
        idx = int(r["frame"])
        if idx < n_frames:
            live[idx] = int(r["live_count"])
            time_s[idx] = float(r["time_s"])

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

    events = []
    prev = 0
    for i in range(n_frames):
        if bridged[i] > prev:
            events.append(time_s[i])
        prev = bridged[i]
    return events


def load_wav_mono_float(path):
    sr, data = wavfile.read(path)
    if data.ndim > 1:
        data = data.mean(axis=1)
    data = data.astype(np.float32)
    if np.abs(data).max() > 1.5:
        data = data / 32768.0
    if sr != SR:
        n_new = int(len(data) * SR / sr)
        data = np.interp(np.linspace(0, len(data), n_new, endpoint=False), np.arange(len(data)), data)
    return data


def main():
    video_path, pushup_csv, cat_csv, ding_wav, meow_wav, out_wav = sys.argv[1:7]

    rep_events = load_pushup_events(pushup_csv)
    print(f"{len(rep_events)} rep events")

    rows = list(csv.DictReader(open(cat_csv)))
    n_frames = len(rows)
    fps = 1.0 / (float(rows[1]["time_s"]) - float(rows[0]["time_s"]))
    cat_events = load_cat_increment_events(cat_csv, n_frames, fps)
    print(f"{len(cat_events)} cat-increment events")

    duration_s = n_frames / fps

    orig_wav = "scratch_orig_audio.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, "-ar", str(SR), "-ac", "1", orig_wav],
        check=True, capture_output=True,
    )
    sr, orig = wavfile.read(orig_wav)
    orig = orig.astype(np.float32) / 32768.0

    ding = load_wav_mono_float(ding_wav) * DING_VOLUME
    meow = load_wav_mono_float(meow_wav) * MEOW_VOLUME

    # buffer must be long enough to hold the full effect sound even if it
    # starts near the very end of the clip -- effects are always played in
    # full, never truncated
    tail_pad = max(len(ding), len(meow))
    n_samples = int(duration_s * SR) + tail_pad
    buf = np.zeros(n_samples, dtype=np.float32)
    copy_len = min(len(orig), int(duration_s * SR))
    buf[:copy_len] = orig[:copy_len] * 0.9  # slightly duck original to leave headroom for effects

    def add_at(buf, sound, t):
        start = int(t * SR)
        end = start + len(sound)
        buf[start:end] += sound

    for t in rep_events:
        add_at(buf, ding, t)

    for t in cat_events:
        add_at(buf, meow, t)

    exact_len = int(duration_s * SR)
    latest_event_end = max(
        [t + len(ding) / SR for t in rep_events] + [t + len(meow) / SR for t in cat_events] + [0]
    )
    if latest_event_end * SR > exact_len:
        print(f"WARNING: an effect would be truncated (ends at {latest_event_end:.2f}s, "
              f"video is {duration_s:.2f}s) -- extending output past video length instead")
    else:
        buf = buf[:exact_len]

    peak = np.abs(buf).max()
    if peak > 0.98:
        buf = buf / peak * 0.98

    wavfile.write(out_wav, SR, (buf * 32767).astype(np.int16))
    print(f"wrote {out_wav}")


if __name__ == "__main__":
    main()
