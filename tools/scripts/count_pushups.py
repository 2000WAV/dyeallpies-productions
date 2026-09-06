"""
Read the per-frame pose signal CSV, smooth it, detect peaks/valleys, and
count push-up reps. Also plots the signal for visual sanity-checking.

Usage:
    python count_pushups.py <signal_csv> <plot_out_png>
"""
import sys
import csv

import numpy as np
from scipy.signal import find_peaks, savgol_filter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    csv_path, plot_out = sys.argv[1], sys.argv[2]

    rows = list(csv.DictReader(open(csv_path)))
    time_s = np.array([float(r["time_s"]) for r in rows])

    # Average left/right elbow angle where available, interpolate gaps.
    angle = np.full(len(rows), np.nan)
    for i, r in enumerate(rows):
        l = float(r["left_elbow_angle"]) if r["left_elbow_angle"] else np.nan
        rr = float(r["right_elbow_angle"]) if r["right_elbow_angle"] else np.nan
        vals = [v for v in (l, rr) if not np.isnan(v)]
        if vals:
            angle[i] = sum(vals) / len(vals)

    # Interpolate NaNs (missed detections)
    nans = np.isnan(angle)
    if nans.any():
        angle[nans] = np.interp(time_s[nans], time_s[~nans], angle[~nans])

    # Smooth to remove per-frame jitter. Window must be odd and < len.
    window = min(31, len(angle) - (1 - len(angle) % 2))
    if window % 2 == 0:
        window -= 1
    smoothed = savgol_filter(angle, window_length=window, polyorder=3)

    # Push-up bottom = elbow bent = local minimum in angle.
    # Require a minimum prominence so shallow noise doesn't count as a rep.
    valleys, props = find_peaks(-smoothed, prominence=20, distance=15)

    print(f"Detected {len(valleys)} push-up reps")
    print("Rep bottom timestamps (s):", [round(t, 2) for t in time_s[valleys]])

    plt.figure(figsize=(14, 5))
    plt.plot(time_s, angle, alpha=0.3, label="raw elbow angle")
    plt.plot(time_s, smoothed, label="smoothed", linewidth=2)
    plt.plot(time_s[valleys], smoothed[valleys], "rv", markersize=10, label="rep (bottom)")
    plt.xlabel("time (s)")
    plt.ylabel("elbow angle (deg)")
    plt.title(f"Push-up signal — {len(valleys)} reps detected")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_out, dpi=120)
    print(f"saved plot to {plot_out}")


if __name__ == "__main__":
    main()
