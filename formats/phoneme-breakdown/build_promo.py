"""Composite the GitHub promo reel: cut master + hand skeleton + top-row thumbnails / live
clips / repo card + English & IPA subtitles with meaning emoji on the ridgeline band.

    python build_promo.py <cut_master.mov> <cut.json> <timeline.json> <hands.npz> <band_dir> <out.mp4> [preview=f1,f2,...]

Every layer reads the frame-quantised timeline (work/cut.json + work/timeline.json).
Overlay PNG band sequence covers every frame and is composited at offset 0.
"""
import sys, os, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

master, cutj, tlj, handsnpz, band_dir, out = sys.argv[1:7]
preview = None
for a in sys.argv[7:]:
    if a.startswith("preview="): preview = [int(v) for v in a[8:].split(",")]

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
EMOJI = os.path.join(ROOT, "tools", "assets", "emoji")
W, H, FPS = 1080, 1920, 30
FONT_B = "C:/Windows/Fonts/segoeuib.ttf"
FONT_S = "C:/Windows/Fonts/seguisb.ttf"
FONT_R = "C:/Windows/Fonts/segoeui.ttf"

cut = json.load(open(cutj)); tl = json.load(open(tlj, encoding="utf-8"))
N = cut["n_frames"]
hz = np.load(handsnpz); hands = hz["img"]; hscore = hz["score"]

def src_frame(k):
    for t in cut["takes"]:
        if t["cut_f0"] <= k < t["cut_f1"]: return t["src_f0"] + (k - t["cut_f0"])
    return None

_fc = {}
def font(path, size):
    key = (path, size)
    if key not in _fc: _fc[key] = ImageFont.truetype(path, size)
    return _fc[key]

def fit(draw, text, path, size, max_w, min_size=24):
    """Shrink the face until the line fits its box -- never assume it fits."""
    while size > min_size:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_w: return f
        size -= 2
    return font(path, min_size)

_ec = {}
def emoji(code, px):
    key = (code, px)
    if key not in _ec:
        p = os.path.join(EMOJI, code + ".png")
        _ec[key] = Image.open(p).convert("RGBA").resize((px, px), Image.LANCZOS) if os.path.exists(p) else None
    return _ec[key]

def ease(t):  # smoothstep
    t = min(1.0, max(0.0, t)); return t * t * (3 - 2 * t)

def rounded(size, radius, fill):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=fill)
    return im

def round_mask(size, radius):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return m

# ---------- top row: thumbnails / live clips / repo card ----------
TILE_W, TILE_H = 225, 400
TILE_Y = 150
TILE_X = [90, 427, 765]
NAMES = ["pullup", "english", "strut"]
def _thumb(n):
    im = Image.open(os.path.join(HERE, "work", "thumbs", n + ".png")).convert("RGBA")
    return im.resize((TILE_W, TILE_H), Image.LANCZOS)
thumbs = [_thumb(n) for n in NAMES]
clip_dirs = [os.path.join(HERE, "work", "clips", n) for n in NAMES]
clip_n = [len([f for f in os.listdir(d) if f.endswith(".png")]) for d in clip_dirs]
_cc = {}
def clip_frame(i, j):
    key = (i, j)
    if key not in _cc:
        _cc[key] = Image.open(os.path.join(clip_dirs[i], f"f{j+1:03d}.png")).convert("RGBA").resize((TILE_W, TILE_H), Image.LANCZOS)
    return _cc[key]
tile_mask = round_mask((TILE_W, TILE_H), 22)

def paste_tile(frame, im, x, y, scale=1.0, alpha=1.0, glow=(255, 255, 255)):
    w, h = int(TILE_W * scale), int(TILE_H * scale)
    cx, cy = x + TILE_W // 2, y + TILE_H // 2
    tile = im.resize((w, h), Image.LANCZOS) if scale != 1.0 else im
    m = round_mask((w, h), int(22 * scale))
    if alpha < 1.0: m = m.point(lambda v: int(v * alpha))
    # soft shadow / glow
    sh = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([30, 30, 30 + w, 30 + h], radius=int(22 * scale), fill=glow + (int(150 * alpha),))
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    frame.alpha_composite(sh, (cx - w // 2 - 30, cy - h // 2 - 30))
    frame.paste(tile, (cx - w // 2, cy - h // 2), m)

def draw_views(frame, x, y, views, alpha):
    """Eye + count pill under the tile, mirroring Instagram's own overlay (the eye is
    drawn: Segoe UI has no eye glyph and renders a box)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay, "RGBA")
    f = font(FONT_B, 40)
    tw = d.textlength(views, font=f)
    ew = 46
    px, py = x + TILE_W // 2 - (tw + ew + 12) / 2 - 18, y + TILE_H + 14
    d.rounded_rectangle([px, py, px + tw + ew + 12 + 36, py + 58], radius=29, fill=(0, 0, 0, int(170 * alpha)))
    ex, ey = px + 18 + ew / 2, py + 29
    wc = (255, 255, 255, int(255 * alpha))
    d.ellipse([ex - 20, ey - 11, ex + 20, ey + 11], outline=wc, width=3)
    d.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], fill=wc)
    d.text((px + 18 + ew + 12, py + 4), views, font=f, fill=wc)
    frame.alpha_composite(lay)

def top_row(frame, tt):
    ov = tl["overlays"]
    th0, th1 = ov["thumbs"]; cl0, cl1 = ov["clips"]; rp0, rp1 = ov["repo"]; c20, c21 = ov["clips2"]
    # 1. Instagram tiles from the start (the hook), then the live clips until "GitHub"
    if th0 <= tt < cl1:
        for i, (x, name) in enumerate(zip(TILE_X, NAMES)):
            a_in = ease((tt - th0 - i * 0.12) / 0.28)
            if a_in <= 0: continue
            if tt >= cl0:
                j = int((tt - cl0) * FPS) % clip_n[i]
                xf = ease((tt - cl0) / 0.25)
                a_out = 1 - ease((tt - (cl1 - 0.2)) / 0.2)
                if xf < 1:
                    paste_tile(frame, thumbs[i], x, TILE_Y, scale=1.0, alpha=a_in * (1 - xf), glow=(255, 255, 255))
                paste_tile(frame, clip_frame(i, j), x, TILE_Y, scale=1.0 + 0.04 * xf, alpha=a_in * xf * a_out, glow=(120, 220, 255))
                draw_views(frame, x, TILE_Y, tl["views"][name], a_in * xf * a_out)
            else:
                # the real Instagram tile, view count and all, exactly as the profile shows it
                paste_tile(frame, thumbs[i], x, TILE_Y, scale=0.9 + 0.1 * a_in, alpha=a_in)
    # 2. repo card when he points up at "GitHub repository"
    if rp0 <= tt < rp1:
        a = ease((tt - rp0) / 0.3) * (1 - ease((tt - (rp1 - 0.25)) / 0.25))
        if a > 0: repo_card(frame, a, tt - rp0)
    # 3. the clips come back after the card and keep playing to the end (time continues from cl0)
    if c20 <= tt < c21:
        for i, (x, name) in enumerate(zip(TILE_X, NAMES)):
            a_in = ease((tt - c20 - i * 0.08) / 0.25)
            if a_in <= 0: continue
            j = int((tt - cl0) * FPS) % clip_n[i]
            paste_tile(frame, clip_frame(i, j), x, TILE_Y, scale=1.0, alpha=a_in, glow=(120, 220, 255))
            draw_views(frame, x, TILE_Y, tl["views"][name], a_in)

def repo_card(frame, a, since):
    cw, ch = 960, 300
    x0, y0 = (W - cw) // 2, 180 - int(20 * (1 - a))
    card = rounded((cw, ch), 34, (14, 17, 23, int(232 * a)))
    d = ImageDraw.Draw(card, "RGBA")
    d.rounded_rectangle([0, 0, cw - 1, ch - 1], radius=34, outline=(70, 80, 100, int(255 * a)), width=3)
    # GitHub mark: a plain white disc with the wordmark, no trademark art
    d.ellipse([34, 34, 34 + 64, 34 + 64], fill=(255, 255, 255, int(255 * a)))
    d.text((66, 66), "G", font=font(FONT_B, 44), fill=(14, 17, 23, int(255 * a)), anchor="mm")
    f1 = fit(d, "github.com/DyeAllPies/", FONT_R, 40, cw - 150)
    d.text((118, 66), "github.com/DyeAllPies/", font=f1, fill=(160, 175, 200, int(255 * a)), anchor="lm")
    f2 = fit(d, "dyeallpies-productions", FONT_B, 74, cw - 70)
    d.text((34, 150), "dyeallpies-productions", font=f2, fill=(88, 166, 255, int(255 * a)), anchor="lm")
    line3 = "every video: scripts, methods, machine learning"
    f3 = fit(d, line3, FONT_S, 36, cw - 240)
    d.text((34, 232), line3, font=f3, fill=(220, 226, 235, int(255 * a)), anchor="lm")
    pw = d.textlength("PUBLIC", font=font(FONT_B, 28)) + 36
    d.rounded_rectangle([cw - 34 - pw, 214, cw - 34, 252], radius=19, fill=(35, 134, 54, int(255 * a)))
    d.text((cw - 34 - pw / 2, 233), "PUBLIC", font=font(FONT_B, 28), fill=(255, 255, 255, int(255 * a)), anchor="mm")
    frame.alpha_composite(card, (x0, y0))

# ---------- hand skeleton ----------
CONN = [(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(5,9),(9,10),(10,11),(11,12),(9,13),(13,14),(14,15),(15,16),(13,17),(17,18),(18,19),(19,20),(0,17)]
TIPS = {4, 8, 12, 16, 20}
last_hand = None
def hand_layer(frame, k, tt):
    global last_hand
    sf = src_frame(k)
    pts = None
    if sf is not None and sf < hands.shape[0]:
        for h in range(hands.shape[1]):
            if not np.isnan(hands[sf, h, 0, 0]) and hscore[sf, h] >= 0.5:
                pts = hands[sf, h, :, :2] * np.array([W, H]); break
    if pts is None:
        # hold the last skeleton for a few dropped frames, then let it go (no one-frame flashes)
        if last_hand is not None and k - last_hand[0] <= 4: pts = last_hand[1]
        else: return
    else:
        last_hand = (k, pts)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay, "RGBA")
    for a, b in CONN:
        d.line([tuple(pts[a]), tuple(pts[b])], fill=(80, 220, 255, 150), width=14)
    lay = lay.filter(ImageFilter.GaussianBlur(6))
    d = ImageDraw.Draw(lay, "RGBA")
    for a, b in CONN:
        d.line([tuple(pts[a]), tuple(pts[b])], fill=(255, 255, 255, 235), width=5)
    for i, p in enumerate(pts):
        r = 11 if i in TIPS else 8
        col = (255, 196, 77, 255) if i == 8 else ((80, 220, 255, 255) if i in TIPS else (255, 255, 255, 255))
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col, outline=(20, 30, 50, 200), width=2)
    # pulsing ring on the index tip
    p = pts[8]; rr = 22 + 6 * np.sin(tt * 7.0)
    d.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], outline=(255, 196, 77, 200), width=3)
    frame.alpha_composite(lay)

# ---------- subtitles on the band ----------
BAND_Y = H - 540
SUB_Y_EN, SUB_Y_IPA = BAND_Y + 62, BAND_Y + 148
EM_PX = 116
NEUTRAL = (225, 230, 240)
LEGEND = [("A+", (40, 220, 130)), ("A", (130, 225, 90)), ("B", (255, 214, 92)), ("C", (255, 150, 60)), ("D", (255, 96, 70)), ("F", (235, 55, 55))]
def subtitle(frame, tt):
    w = next((w for w in tl["words"] if w["t_start"] <= tt < w["t_end"]), None)
    if w is None: return
    a = ease((tt - w["t_start"]) / 0.12)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay, "RGBA")
    max_w = W - 2 * (EM_PX + 60)
    fe = fit(d, w["text"], FONT_B, 66, max_w)
    fi = fit(d, "/" + w["ipa"] + "/", FONT_S, 52, max_w)
    def outlined(x, y, txt, f, col, anchor="mm"):
        for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2), (-2, 2), (2, -2)):
            d.text((x + dx, y + dy), txt, font=f, fill=(0, 0, 0, int(230 * a)), anchor=anchor)
        d.text((x, y), txt, font=f, fill=col + (int(255 * a),), anchor=anchor)
    outlined(W / 2, SUB_Y_EN, w["text"], fe, (255, 255, 255))
    # IPA line: each graded vowel in its grade colour, everything else neutral
    ipa = "/" + w["ipa"] + "/"
    spans = sorted(w.get("ipa_spans", []), key=lambda sp: sp["start"])
    runs = []; pos = 0
    for sp in spans:
        a0, b0 = sp["start"] + 1, sp["end"] + 1  # +1 for the leading slash
        if a0 > pos: runs.append((ipa[pos:a0], NEUTRAL))
        runs.append((ipa[a0:b0], tuple(sp["colour"]))); pos = b0
    if pos < len(ipa): runs.append((ipa[pos:], NEUTRAL))
    total = sum(d.textlength(t, font=fi) for t, _ in runs)
    x = W / 2 - total / 2
    for t, col in runs:
        outlined(x, SUB_Y_IPA, t, fi, col, anchor="lm"); x += d.textlength(t, font=fi)
    for code, cx in ((w["emoji_l"], 40 + EM_PX // 2), (w["emoji_r"], W - 40 - EM_PX // 2)):
        em = emoji(code, EM_PX)
        if em is None: continue
        s = 0.8 + 0.2 * a
        e2 = em.resize((int(EM_PX * s), int(EM_PX * s)), Image.LANCZOS)
        if a < 1: e2.putalpha(e2.getchannel("A").point(lambda v: int(v * a)))
        lay.alpha_composite(e2, (int(cx - e2.width / 2), int((SUB_Y_EN + SUB_Y_IPA) / 2 - e2.height / 2)))
    frame.alpha_composite(lay)

# ---------- main loop ----------
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", master, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
if preview is None:
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "h264_nvenc", "-preset", "p5", "-tune", "hq", "-rc", "vbr", "-cq", "19", "-b:v", "0",
                            "-spatial-aq", "1", "-temporal-aq", "1", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
for k in range(N):
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    if preview is not None and k not in preview: continue
    tt = k / FPS
    frame = Image.frombuffer("RGB", (W, H), raw).convert("RGBA")
    band = Image.open(os.path.join(band_dir, f"band_{k:04d}.png")).convert("RGBA")
    frame.alpha_composite(band, (0, BAND_Y))
    hand_layer(frame, k, tt)
    top_row(frame, tt)
    subtitle(frame, tt)
    if preview is not None:
        frame.convert("RGB").save(os.path.join(HERE, "work", f"preview_{k:04d}.png")); print("preview", k)
    else:
        enc.stdin.write(frame.convert("RGB").tobytes())
        if k % 60 == 0: print(k, "/", N, flush=True)
dec.stdout.close()
if preview is None:
    enc.stdin.close(); enc.wait(); print("video done", out)
