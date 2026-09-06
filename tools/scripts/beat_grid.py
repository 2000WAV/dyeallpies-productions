"""Estimate tempo and a beat grid from a music reference recording.

Usage: beat_grid.py <wav> [out.json] [--min-bpm N] [--max-bpm N]

Spectral-flux onset envelope -> autocorrelation tempo estimate -> phase fit of a
constant-tempo grid. Prints tempo, beat period, grid phase and the strongest onsets,
and writes the grid + onsets to JSON so cuts can be snapped to it.

Built for beat-syncing a reel to a track the user supplies purely as a TIMING
REFERENCE. Works fine on a low-bitrate phone recording: percussive onsets survive
heavy lossy compression even when the spectrum above ~8 kHz is gone.
"""
import sys, json
import numpy as np
from scipy.io import wavfile
from scipy.signal import stft, find_peaks

args = [a for a in sys.argv[1:] if not a.startswith("--")]
opts = dict(zip([a for a in sys.argv[1:] if a.startswith("--")],
                [sys.argv[i+1] for i, a in enumerate(sys.argv[1:], 1) if a.startswith("--")]))
wav = args[0]
out = args[1] if len(args) > 1 else None
MIN_BPM = float(opts.get("--min-bpm", 60))
MAX_BPM = float(opts.get("--max-bpm", 200))

sr, x = wavfile.read(wav)
if x.ndim > 1:
    x = x.mean(axis=1)
x = x.astype(np.float64) / (np.abs(x).max() or 1)

# --- onset strength envelope (spectral flux over a log-magnitude mel-ish spectrum) ---
HOP = 512
NFFT = 2048
f, t, Z = stft(x, fs=sr, nperseg=NFFT, noverlap=NFFT - HOP, padded=False, boundary=None)
S = np.log1p(1000 * np.abs(Z))
flux = np.diff(S, axis=1)
flux[flux < 0] = 0                       # half-wave rectify: only energy INCREASES
env = flux.sum(axis=0)
env = env - env.mean()
env[env < 0] = 0
fps = sr / HOP
env_t = t[1:]

# --- tempo via autocorrelation of the onset envelope ---
ac = np.correlate(env, env, mode="full")[len(env) - 1:]
ac[0] = 0
lag_min = int(round(fps * 60.0 / MAX_BPM))
lag_max = int(round(fps * 60.0 / MIN_BPM))
lag_max = min(lag_max, len(ac) - 1)
band = ac[lag_min:lag_max + 1]
# weight against octave errors: prefer lags nearer 120 BPM
lags = np.arange(lag_min, lag_max + 1)
bpms = 60.0 * fps / lags
weight = np.exp(-0.5 * (np.log2(bpms / 120.0) / 0.9) ** 2)
best = lags[int(np.argmax(band * weight))]
period = best / fps
bpm = 60.0 / period

# --- phase: choose the offset whose comb of beats maximises onset energy ---
n_beats = int((env_t[-1] - env_t[0]) / period)
phases = np.linspace(0, period, 200, endpoint=False)
scores = []
for ph in phases:
    times = env_t[0] + ph + period * np.arange(n_beats)
    idx = np.clip(((times - env_t[0]) * fps).astype(int), 0, len(env) - 1)
    scores.append(env[idx].sum())
phase = phases[int(np.argmax(scores))]
beats = (env_t[0] + phase + period * np.arange(n_beats + 1)).tolist()
beats = [b for b in beats if b <= env_t[-1]]

# --- strongest onsets, for locating section changes / the drop ---
pk, props = find_peaks(env, height=np.percentile(env, 90), distance=int(0.1 * fps))
order = np.argsort(props["peak_heights"])[::-1]
onsets = sorted(float(env_t[pk[i]]) for i in order[:80])

print(f"file        : {wav}")
print(f"duration    : {len(x)/sr:.2f} s")
print(f"tempo       : {bpm:.2f} BPM   (beat period {period*1000:.1f} ms)")
print(f"grid phase  : {beats[0]:.3f} s  -> {len(beats)} beats")
print(f"bar (4/4)   : {period*4:.3f} s")
print(f"first 16 beats: " + " ".join(f"{b:.2f}" for b in beats[:16]))

# energy per second, to find where the track changes section
sec = np.zeros(int(env_t[-1]) + 1)
for i, tt in enumerate(env_t):
    sec[int(tt)] += env[i]
sec = sec / (sec.max() or 1)
print("\nonset energy per second (0-9 scale, look for the drop):")
for row in range(0, len(sec), 30):
    chunk = sec[row:row + 30]
    print(f"  {row:3d}s |" + "".join(str(min(9, int(v * 10))) for v in chunk))

if out:
    json.dump({"file": wav, "bpm": bpm, "period": period, "beats": beats,
               "onsets": onsets, "energy_per_sec": sec.tolist()},
              open(out, "w"), indent=1)
    print(f"\nwrote {out}")
