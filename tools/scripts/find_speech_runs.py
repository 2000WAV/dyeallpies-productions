"""List all loud speech runs in a WAV: contiguous intensity>threshold regions with stats.

Usage: find_speech_runs.py <wav> [thresh_db=50] [min_dur=0.10] [merge_gap=0.10]
Prints one line per run: start, end, peak dB, voiced fraction, median F0/F1/F2 over voiced frames.
"""
import sys, statistics
import parselmouth

wav = sys.argv[1]
TH = float(sys.argv[2]) if len(sys.argv) > 2 else 50.0
MIN_DUR = float(sys.argv[3]) if len(sys.argv) > 3 else 0.10
GAP = float(sys.argv[4]) if len(sys.argv) > 4 else 0.10

snd = parselmouth.Sound(wav)
inten = snd.to_intensity(minimum_pitch=75, time_step=0.01)
pitch = snd.to_pitch(time_step=0.01, pitch_floor=75, pitch_ceiling=500)
fmt = snd.to_formant_burg(time_step=0.01, max_number_of_formants=5, maximum_formant=5000)

step = 0.01
t, runs, cur = 0.0, [], None
while t < snd.duration:
    v = inten.get_value(t)
    loud = v == v and v > TH
    if loud and cur is None:
        cur = [t, t]
    elif loud:
        cur[1] = t
    elif cur and t - cur[1] > GAP:
        runs.append(cur); cur = None
    t += step
if cur:
    runs.append(cur)
runs = [r for r in runs if r[1] - r[0] >= MIN_DUR]

for r0, r1 in runs:
    f0s, f1s, f2s, dbs, n = [], [], [], [], 0
    t = r0
    while t <= r1:
        n += 1
        db = inten.get_value(t)
        if db == db:
            dbs.append(db)
        f0 = pitch.get_value_at_time(t)
        if f0 == f0:
            f0s.append(f0)
            f1, f2 = fmt.get_value_at_time(1, t), fmt.get_value_at_time(2, t)
            if f1 == f1 and f2 == f2:
                f1s.append(f1); f2s.append(f2)
        t += step
    vf = len(f0s) / n if n else 0
    print(f"{r0:6.2f}-{r1:6.2f} dur={r1-r0:4.2f} peak={max(dbs):4.1f}dB voiced={vf:.2f} "
          f"F0={round(statistics.median(f0s)) if f0s else '--'} "
          f"F1={round(statistics.median(f1s)) if f1s else '--'} "
          f"F2={round(statistics.median(f2s)) if f2s else '--'}")
