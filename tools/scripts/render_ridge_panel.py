"""Render the "waterfall ridgeline" spectrum panel as an RGBA PNG sequence.

Usage: render_ridge_panel.py <audio.wav> <timeline.json> <outdir> [--fps 30]

Replaces the heatmap spectrogram with something readable at phone size and at a third
of a second per word: each spectral slice is drawn as a glowing line, and successive
slices are stacked receding into fake 3-D perspective. F1 and F2 show up as two
travelling ridges instead of a smear. Same data as a spectrogram, drawn the classic
waterfall way, so it stays honest while reading as "sound waves" to a lay viewer.

Painter's algorithm back-to-front with an opaque fill under each ridge, so nearer
slices occlude further ones -- that occlusion is what sells the depth.
"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy.io import wavfile
from scipy.signal import stft
from PIL import Image, ImageDraw
from vowel_map import WORD_EMOJI, WORD_EMOJI_ALT

wav, tlj, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
FPS = float(sys.argv[sys.argv.index("--fps")+1]) if "--fps" in sys.argv else 30.0
os.makedirs(outdir, exist_ok=True)

W, H = 1080, 1920
PX0, PX1 = 95, 985          # panel horizontal extent (front slice)
PY1 = 1465                  # front slice baseline
DEPTH_H = 300               # how far back the stack recedes
SKEW = 60                   # lateral shift of the far slices
AMP = 250                   # peak ridge height
NSLICE = 34                 # slices held on screen
FMAX = 5000.0               # ceiling (men)
EMOJI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "emoji")
EMOJI_PX, EMOJI_Y = 150, 395   # flanks the word on BOTH sides
EMOJI_LX, EMOJI_RX = 150, 930  # left / right slot centres

_cache = {}
def emoji_for(word, alt=False):
    """Twemoji PNG carrying the word's MEANING -- much of the audience does not read
    English, so the picture does the work the word cannot. Two DIFFERENT pictures flank
    each word: a pair reads faster than one image repeated, and it disambiguates."""
    src = WORD_EMOJI_ALT if alt else WORD_EMOJI
    code = src.get(word.lower())
    if not code: return None
    key = code + ("a" if alt else "")
    if key not in _cache:
        f = os.path.join(EMOJI_DIR, code + ".png")
        _cache[key] = (Image.open(f).convert("RGBA").resize((EMOJI_PX, EMOJI_PX),
                        Image.LANCZOS) if os.path.exists(f) else None)
    return _cache[key]

tl = json.load(open(tlj, encoding="utf-8"))
words = tl["words"]
sr, x = wavfile.read(wav)
if x.ndim > 1: x = x.mean(axis=1)
x = x.astype(np.float64) / 32768.0

HOP = 256
f, t, Z = stft(x, fs=sr, nperseg=1024, noverlap=1024-HOP, padded=False, boundary=None)
keep = f <= FMAX
f = f[keep]; S = np.abs(Z[keep])
S = np.log1p(400 * S)
if S.max() > 0: S /= S.max()
NBIN = 150
edges = np.linspace(0, len(f)-1, NBIN+1).astype(int)
Sb = np.stack([S[a:max(a+1,b)].max(axis=0) for a, b in zip(edges[:-1], edges[1:])])  # NBIN x frames

# elevation ramp: deep blue -> cyan -> green -> amber -> hot red
_STOPS = [(0.00, (28, 52, 120)), (0.22, (40, 130, 214)), (0.42, (54, 205, 208)),
          (0.60, (120, 224, 128)), (0.78, (255, 206, 84)), (1.00, (255, 92, 74))]
def ramp(v, vis):
    v = 0.0 if v < 0 else (1.0 if v > 1 else v)
    for i in range(len(_STOPS) - 1):
        a, ca = _STOPS[i]; b, cb = _STOPS[i + 1]
        if v <= b:
            f = 0.0 if b == a else (v - a) / (b - a)
            c = tuple(int(ca[k] + (cb[k] - ca[k]) * f) for k in range(3))
            break
    else:
        c = _STOPS[-1][1]
    a = int(70 + 185 * vis * (0.45 + 0.55 * v))
    return (c[0], c[1], c[2], min(255, a))


def slice_at(tt):
    i = int(np.clip(tt / (HOP/sr), 0, Sb.shape[1]-1))
    return Sb[:, i]

# Render EVERY frame of the finished video, transparent where no word is on screen.
# Rendering only the word range meant the overlay had to be time-shifted into place,
# and that shift silently landed 5 frames early -- captions showed one word while the
# pictures showed the next. A full-length sequence composites at offset 0, so there is
# no alignment to get wrong.
# Which ridges actually CONTAIN the vowel. The panel otherwise shows a spectrum without
# saying which part of it is the vowel being graded. The nucleus is the voiced core:
# frames within 15 dB of the word's peak intensity -- the same definition used to measure
# F1/F2 in the first place, so the highlight marks exactly the frames that were graded.
env_hop = HOP / sr
_amp = np.abs(Z).sum(axis=0)
_amp_db = 20 * np.log10(_amp + 1e-9)
for _w in words:
    a = int(_w["t_start"] / env_hop); b = int(_w["t_end"] / env_hop)
    seg = _amp_db[a:b]
    if len(seg) == 0:
        _w["_nuc"] = None; continue
    thr = seg.max() - 15.0
    idx = np.where(seg >= thr)[0]
    _w["_nuc"] = (_w["t_start"] + idx[0] * env_hop,
                  _w["t_start"] + idx[-1] * env_hop) if len(idx) else None

def peak_bin(sp, hz):
    """Index of the spectral peak nearest a formant frequency -- i.e. WHICH mountain."""
    c = int(round(hz / FMAX * (NBIN - 1)))
    lo, hi = max(0, c - 13), min(NBIN, c + 14)
    return lo + int(np.argmax(sp[lo:hi]))

f0 = 0
f1 = int(sys.argv[sys.argv.index("--frames") + 1]) if "--frames" in sys.argv      else int(round(words[-1]["t_end"] * FPS))
print(f"panel frames {f0}..{f1}  ({f1-f0} frames, transparent outside the word section)")

for fi in range(f0, f1):
    tt = fi / FPS
    w = next((w for w in words if w["t_start"] <= tt < w["t_end"]), None)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    if w is not None:
        # SHINE: the vowel glows while it is actually being hit, then eases out. The
        # highlight above says which ridges hold the vowel; this says WHEN, so the two
        # together answer "that mountain, right now".
        _n = w.get("_nuc")
        if _n and _n[0] <= tt <= _n[1]:
            shine = 1.0
        elif _n and tt > _n[1]:
            shine = max(0.0, 1.0 - (tt - _n[1]) / 0.16)
        else:
            shine = 0.0
        # slices from the start of this word up to now, newest at the front
        span = tt - w["t_start"]
        times = np.linspace(max(w["t_start"], tt - 0.42), tt, NSLICE)
        times = times[times >= w["t_start"] - 1e-6]
        n = len(times)
        for k, ts in enumerate(times):                # k=0 oldest -> back
            depth = k / max(1, n - 1)                 # 0 back, 1 front
            sp = slice_at(ts)
            wid = (PX1 - PX0) * (0.70 + 0.30 * depth)
            xl = PX0 + (1 - depth) * SKEW + ((PX1 - PX0) - wid) * 0.5
            yb = PY1 - (1 - depth) * DEPTH_H
            amp = AMP * (0.55 + 0.45 * depth)
            xs = xl + np.arange(NBIN) * (wid / (NBIN - 1))
            ys = yb - sp * amp
            pts = list(zip(xs.tolist(), ys.tolist()))
            fill_a = int(210 * (0.35 + 0.65 * depth))
            d.polygon(pts + [(xs[-1], yb), (xs[0], yb)], fill=(9, 13, 26, fill_a))
            # colour each span by its ELEVATION, so loud partials read hot and quiet
            # ones stay cool -- height alone is hard to judge on a small screen
            nuc = w.get("_nuc")
            in_vowel = nuc is not None and nuc[0] <= ts <= nuc[1]
            wdt = (2 if in_vowel else 1) + int(2 * depth)
            vis = (0.55 + 0.45 * depth) if in_vowel else (0.16 + 0.34 * depth)
            if in_vowel and shine > 0.02 and depth > 0.5:
                # Only the NEAR ridges glow. Haloing all 34 stacked slices piles up into
                # a grey fog that buries the very structure the glow is meant to point at.
                halo = int(20 + 34 * shine * (depth - 0.5) / 0.5)
                d.line(pts, fill=(190, 226, 255, halo),
                       width=wdt + 3 + int(3 * shine), joint="curve")
            step = 5
            for j in range(0, NBIN - 1, step):
                seg = pts[j:j + step + 1]
                if len(seg) < 2: break
                # p95 of the normalised amplitude is ~0.30, so scale the ramp to that
                amp = min(1.0, float(sp[j:j + step + 1].max()) / 0.30) ** 0.8
                d.line(seg, fill=ramp(amp, vis), width=wdt, joint="curve")
            if in_vowel and depth > 0.55:
                # put a marker on the actual F1 and F2 peaks of THIS ridge
                for hz, col in ((w["f1"], (77, 181, 255)), (w["f2"], (255, 196, 77))):
                    bi = peak_bin(sp, hz)
                    px, py = xs[bi], ys[bi]
                    r = (4 + 4 * depth) * (1.0 + 0.55 * shine)
                    a_ = int(150 + 105 * depth)
                    if shine > 0.02:
                        gr = r + 7 * shine
                        d.ellipse([px - gr, py - gr, px + gr, py + gr],
                                  fill=(col[0], col[1], col[2], int(70 * shine)))
                    d.ellipse([px - r, py - r, px + r, py + r],
                              fill=(col[0], col[1], col[2], a_))
        # ground line + the two formant markers on the front slice
        d.line([(PX0 - 10, PY1 + 6), (PX1 + 10, PY1 + 6)], fill=(90, 120, 170, 150), width=2)
        for hz, col in ((w["f1"], (77, 181, 255, 255)), (w["f2"], (255, 196, 77, 255))):
            fx = PX0 + (hz / FMAX) * (PX1 - PX0)
            d.line([(fx, PY1 + 4), (fx, PY1 - 34)], fill=col, width=5)
            d.ellipse([fx-9, PY1-48, fx+9, PY1-30], fill=col)
        for hz in (1000, 2000, 3000, 4000):
            gx = PX0 + (hz / FMAX) * (PX1 - PX0)
            d.line([(gx, PY1 + 6), (gx, PY1 + 16)], fill=(90, 120, 170, 120), width=2)
        if w.get("_nuc"):
            d.text((PX0 - 4, PY1 + 22), "vowel", fill=(150, 200, 255, 210))
        for cx_slot, is_alt in ((EMOJI_LX, False), (EMOJI_RX, True)):
            em = emoji_for(w["word"], is_alt)
            if em is not None:
                img.alpha_composite(em, (cx_slot - EMOJI_PX // 2, EMOJI_Y - EMOJI_PX // 2))
    img.save(f"{outdir}/p_{fi:05d}.png")
print(f"wrote {f1-f0} panels to {outdir}")
