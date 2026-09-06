"""Bottom-band ridgeline spectrum for the promo reel: decoration, continuous (no word
gating), same look as render_ridge_panel.py in the trend reel.

    python render_promo_panel.py <audio.wav> <n_frames> <outdir> [phones_graded.json]   -> band_%04d.png (1080 x BAND_H RGBA)

With phones_graded.json every ridge is tinted by the phone it belongs to (grade colour),
a divider ridge marks each phone onset with its IPA symbol floating at that depth, and
the phone being spoken sits big in the left column with its grade.
"""
import sys, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import stft
from PIL import Image, ImageDraw

wav, nfr, outdir = sys.argv[1], int(sys.argv[2]), sys.argv[3]
import json
from PIL import ImageFont
phones = json.load(open(sys.argv[4], encoding="utf-8")) if len(sys.argv) > 4 else []
FONT_S = "C:/Windows/Fonts/seguisb.ttf"; FONT_B = "C:/Windows/Fonts/segoeuib.ttf"
f_sym = ImageFont.truetype(FONT_S, 30); f_big = ImageFont.truetype(FONT_B, 64); f_grade = ImageFont.truetype(FONT_B, 28)
for _i, _ph in enumerate(phones): _ph["idx"] = _i
EMOJI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools", "assets", "emoji")
FLAG = {k: Image.open(os.path.join(EMOJI_DIR, f + ".png")).convert("RGBA").resize((110, 110), Image.LANCZOS) for k, f in (("GB", "1f1ec-1f1e7"), ("US", "1f1fa-1f1f8"))}
# accent-neutral phonemes: one flag, left half British, right half American
_half = FLAG["GB"].copy(); _half.paste(FLAG["US"].crop((55, 0, 110, 110)), (55, 0))
ImageDraw.Draw(_half).line([(55, 8), (55, 102)], fill=(6, 9, 20, 230), width=3)
FLAG["same"] = _half
f_flag = ImageFont.truetype(FONT_B, 26)
def phone_at(t):
    for ph in phones:
        if ph["t0"] <= t < ph["t1"]: return ph
    return None

# Consecutive phonemes alternate texture so their runs read as separate bands even when
# two neighbours share a grade colour: solid, checker, lines, then round again.
PATTERNS = {}
def _make_patterns():
    for name in ("solid", "checker", "lines"):
        m = Image.new("L", (W, BAND_H), 255)
        d = ImageDraw.Draw(m)
        if name == "checker":
            for y in range(0, BAND_H, 8):
                for x in range(0, W, 8):
                    if ((x // 8) + (y // 8)) % 2: d.rectangle([x, y, x + 7, y + 7], fill=60)
        elif name == "lines":
            for y in range(0, BAND_H, 7): d.line([(0, y), (W, y)], fill=50, width=3)
        PATTERNS[name] = m
STYLE = ("solid", "checker", "lines")
from PIL import ImageChops
def fill_patterned(img, pts, colour, alpha, style):
    """Fill the polygon under a ridge with the phone's colour through a texture mask."""
    if not PATTERNS: _make_patterns()
    xs_ = [p[0] for p in pts]; ys_ = [p[1] for p in pts]
    x0, x1 = int(max(0, min(xs_) - 1)), int(min(W, max(xs_) + 2))
    y0, y1 = int(max(0, min(ys_) - 1)), int(min(BAND_H, max(ys_) + 2))
    if x1 <= x0 or y1 <= y0: return
    mask = Image.new("L", (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(mask).polygon([(x - x0, y - y0) for x, y in pts], fill=alpha)
    mask = ImageChops.multiply(mask, PATTERNS[style].crop((x0, y0, x1, y1)))
    fill = Image.new("RGBA", (x1 - x0, y1 - y0), (colour[0], colour[1], colour[2], 255))
    fill.putalpha(mask)
    img.alpha_composite(fill, (x0, y0))
os.makedirs(outdir, exist_ok=True)
FPS = 30.0
W, BAND_H = 1080, 540
PX0, PX1 = 150, 850
PY1 = BAND_H - 40
DEPTH_H, SKEW, AMP, NSLICE, FMAX = 150, 45, 130, 30, 5000.0

sr, x = wavfile.read(wav)
if x.ndim > 1: x = x.mean(axis=1)
x = x.astype(np.float64) / 32768.0
HOP = 256
f, t, Z = stft(x, fs=sr, nperseg=1024, noverlap=1024 - HOP, padded=False, boundary=None)
keep = f <= FMAX
S = np.abs(Z[keep]); S = np.log1p(400 * S); S /= max(S.max(), 1e-9)
NBIN = 150
edges = np.linspace(0, keep.sum() - 1, NBIN + 1).astype(int)
Sb = np.stack([S[a:max(a + 1, b)].max(axis=0) for a, b in zip(edges[:-1], edges[1:])])
amp_db = 20 * np.log10(np.abs(Z).sum(axis=0) + 1e-9)
voiced_thr = amp_db.max() - 22.0

_STOPS = [(0.00, (28, 52, 120)), (0.22, (40, 130, 214)), (0.42, (54, 205, 208)),
          (0.60, (120, 224, 128)), (0.78, (255, 206, 84)), (1.00, (255, 92, 74))]
def ramp(v, vis):
    v = min(1.0, max(0.0, v))
    for i in range(len(_STOPS) - 1):
        a, ca = _STOPS[i]; b, cb = _STOPS[i + 1]
        if v <= b:
            fr = 0.0 if b == a else (v - a) / (b - a)
            c = tuple(int(ca[k] + (cb[k] - ca[k]) * fr) for k in range(3)); break
    else: c = _STOPS[-1][1]
    return (c[0], c[1], c[2], min(255, int(70 + 185 * vis * (0.45 + 0.55 * v))))

def slice_at(tt):
    i = int(np.clip(tt / (HOP / sr), 0, Sb.shape[1] - 1)); return Sb[:, i], amp_db[i] >= voiced_thr

# translucent backdrop so the subtitles drawn on top stay readable
back = Image.new("RGBA", (W, BAND_H), (0, 0, 0, 0))
bd = ImageDraw.Draw(back)
for y in range(BAND_H):
    a = int(30 + 150 * (y / BAND_H) ** 0.8)
    bd.line([(0, y), (W, y)], fill=(6, 9, 20, a))

for fi in range(nfr):
    tt = fi / FPS
    img = back.copy(); d = ImageDraw.Draw(img, "RGBA")
    times = np.linspace(max(0.0, tt - 0.42), tt, NSLICE)
    n = len(times)
    for k, ts in enumerate(times):
        depth = k / max(1, n - 1)
        sp, voiced = slice_at(ts)
        wid = (PX1 - PX0) * (0.72 + 0.28 * depth)
        xl = PX0 + (1 - depth) * SKEW + ((PX1 - PX0) - wid) * 0.5
        yb = PY1 - (1 - depth) * DEPTH_H
        a_ = AMP * (0.55 + 0.45 * depth)
        xs = xl + np.arange(NBIN) * (wid / (NBIN - 1)); ys = yb - sp * a_
        pts = list(zip(xs.tolist(), ys.tolist()))
        ph = phone_at(ts)
        d.polygon(pts + [(xs[-1], yb), (xs[0], yb)], fill=(9, 13, 26, int(210 * (0.35 + 0.65 * depth))))
        if ph is not None:
            c = ph["colour"]
            fill_patterned(img, pts + [(xs[-1], yb), (xs[0], yb)], c, int(70 + 110 * depth), STYLE[ph["idx"] % 3])
            d = ImageDraw.Draw(img, "RGBA")
        prev = phone_at(times[k - 1]) if k > 0 else None
        if ph is not None and (prev is None or prev is not ph) and (k > 0 or ts - ph["t0"] < 0.03):
            # phone onset: a divider ridge and the symbol floating at this depth
            c = ph["colour"]
            d.line(pts, fill=(255, 255, 255, int(120 + 120 * depth)), width=2 + int(2 * depth), joint="curve")
            d.line([(xs[0] - 6, yb), (xs[0] - 6, yb - 60 - 40 * depth)], fill=(c[0], c[1], c[2], int(160 + 90 * depth)), width=3)
            lab = ph["tok"]
            d.text((xs[0] - 12, yb - 62 - 40 * depth), lab, font=f_sym, fill=(c[0], c[1], c[2], int(200 + 55 * depth)), anchor="rs")
            d.line([(xs[-1] + 6, yb), (xs[-1] + 6, yb - 60 - 40 * depth)], fill=(c[0], c[1], c[2], int(160 + 90 * depth)), width=3)
            d.text((xs[-1] + 12, yb - 62 - 40 * depth), lab, font=f_sym, fill=(c[0], c[1], c[2], int(200 + 55 * depth)), anchor="ls")
        wdt = (2 if voiced else 1) + int(2 * depth)
        vis = (0.55 + 0.45 * depth) if voiced else (0.18 + 0.32 * depth)
        if voiced and depth > 0.6:
            d.line(pts, fill=(190, 226, 255, int(18 + 30 * (depth - 0.6) / 0.4)), width=wdt + 4, joint="curve")
        for j in range(0, NBIN - 1, 5):
            seg = pts[j:j + 6]
            if len(seg) < 2: break
            am = min(1.0, float(sp[j:j + 6].max()) / 0.30) ** 0.8
            d.line(seg, fill=ramp(am, vis), width=wdt, joint="curve")
    # the phone being spoken: big symbol + grade chip in the left column
    now = phone_at(tt)
    if now is not None:
        c = now["colour"]
        d.rounded_rectangle([14, PY1 - 150, 134, PY1 + 4], radius=18, fill=(6, 9, 20, 200), outline=(c[0], c[1], c[2], 230), width=3)
        d.text((74, PY1 - 92), now["tok"], font=f_big, fill=(c[0], c[1], c[2], 255), anchor="mm")
        d.text((74, PY1 - 24), now["grade"], font=f_grade, fill=(c[0], c[1], c[2], 255), anchor="mm")
        # accent column on the right: the flag of the accent this phone was said in
        acc = now.get("accent", "same"); cx = 975
        d.rounded_rectangle([cx - 68, PY1 - 150, cx + 68, PY1 + 4], radius=18, fill=(6, 9, 20, 200), outline=(90, 120, 170, 200), width=2)
        img.alpha_composite(FLAG.get(acc, FLAG["same"]), (cx - 55, PY1 - 140))
        d.text((cx, PY1 - 16), {"GB": "British", "US": "American"}.get(acc, "neutral"), font=f_flag,
               fill=(230, 235, 245, 255) if acc in ("GB", "US") else (170, 180, 195, 255), anchor="mm")
    d.line([(PX0 - 10, PY1 + 6), (PX1 + 10, PY1 + 6)], fill=(90, 120, 170, 150), width=2)
    for hz in (1000, 2000, 3000, 4000):
        gx = PX0 + (hz / FMAX) * (PX1 - PX0)
        d.line([(gx, PY1 + 6), (gx, PY1 + 16)], fill=(90, 120, 170, 120), width=2)
    img.save(os.path.join(outdir, f"band_{fi:04d}.png"))
    if fi % 100 == 0: print(fi, flush=True)
print("done", nfr)
