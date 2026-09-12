"""The DyeAllPies Productions end sting: the five-string drop lights the wordmark, then the URL holds.

    python render_brand_sting.py <out.mp4>                    # the sting alone (2.5 s, 1080x1920, 30 fps, silent)
    python render_brand_sting.py <out.mp4> append=<shot.mp4>  # the shot with the sting appended (the shot's audio kept, silence under the sting)
    options: hold=1.5 (s of URL hold after the 1 s animation) frames=<dir> (write PNGs of the beats for a check)

The brand rules and every number: tools/brand/BRAND.md (from references/marionette/08-brand-sting.md);
the palette and fonts come from studio.brand so the sting and the document cannot drift apart.
Beats at 30 fps: 0-8 the five strings fall (real gravity at the puppet's scale: the drop the reel is
about), 8-12 they snap taut and bounce, 10-22 the wordmark lights letter by letter as they land, 22-30
PRODUCTIONS tracks in and the orange tick draws; then the URL fades in over 6 frames and holds.
Written 2026-09-11 as the label's first reusable branding asset; every later export appends it.

2026-09-12: the decided colours (main #231F20, secondary #D75413; the off-white neutral for the
secondary text) replace the provisional neon cyan/blue. The append no longer re-encodes the shot:
the sting is encoded with the shot's own stream parameters (studio.encode.sting_encode_args) and
joined by the concat demuxer with -c copy, so the join costs seconds instead of a full NVENC pass.
"""
import sys, os, subprocess
import numpy as np
import cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # tools/ -> studio (or the .pth)
from studio import brand
from studio.encode import RawWriter, sting_encode_args, concat_copy, decode_check

W, H, FPS = 1080, 1920, 30
GROUND = brand.bgr("main")            # #231F20
ACCENT = brand.bgr("secondary")       # #D75413: the wordmark, the strings, the tick
NEUTRAL = brand.bgr("neutral")        # #F2F0EA: PRODUCTIONS, the URL, the strings' core
WHITE = brand.bgr("white")
WORD = "DyeAllPies"; SUB = "PRODUCTIONS"; URL = "github.com/DyeAllPies/dyeallpies-productions"


def ease_out(t):      # Fluent "fast out, slow in" cubic-bezier(0,0,0,1) ~ 1 - (1-t)^3
    t = np.clip(t, 0, 1); return 1 - (1 - t) ** 3


def string_drop(t, y_top, y_land):
    """The lower end of a string released at y_top: free fall at the puppet's scale (the reel's own
    7 cm drop took 0.12 s; here the fall is scaled to 8 frames), a snap at y_land, one damped bounce."""
    t_fall = 8 / FPS
    if t < t_fall: return y_top + (y_land - y_top) * (t / t_fall) ** 2
    dt = t - t_fall
    return y_land - 26 * np.sin(np.pi * dt / (6 / FPS)) * np.exp(-dt * 18) if dt < 6 / FPS else y_land


def glow(img, sigmas=((4, 0.30), (14, 0.18), (40, 0.10))):
    out = img.astype(np.float32)
    for s, w in sigmas: out += w * cv2.GaussianBlur(img.astype(np.float32), (0, 0), s)
    return np.clip(out, 0, 255).astype(np.uint8)


def frame(i, hold_frames):
    t = i / FPS
    canvas = np.zeros((H, W, 3), np.uint8); canvas[:] = GROUND
    lit = np.zeros((H, W, 3), np.uint8)                      # the emissive elements only (bloomed)
    pil = Image.new("RGB", (W, H)); dr = ImageDraw.Draw(pil)
    f_word = brand.font("wordmark", 150); f_sub = brand.font("sub", 44); f_url = brand.font("mono", 52)
    # layout: the wordmark centred at y = 900 (inside the 270-1250 safe band), PRODUCTIONS under its right half, the URL at 1150
    bbox = dr.textbbox((0, 0), WORD, font=f_word); ww = bbox[2] - bbox[0]; x_word = (W - ww) // 2; y_word = 900 - (bbox[3] - bbox[1]) // 2 - bbox[1]
    # letter positions for the light-up and the string landings
    xs = []; x = x_word
    for ch in WORD:
        cw = dr.textlength(ch, font=f_word); xs.append((x, x + cw)); x += cw
    land_x = [int((xs[k][0] + xs[k][1]) / 2) for k in (0, 2, 5, 7, 9)]          # five strings land on D, e, l, i, s
    y_land = y_word + bbox[1] - 8
    # strings (frames 0-14): the accent with a pale core, as a lit thread
    if i <= 14:
        for k, lx in enumerate(land_x):
            y_end = string_drop(t + k * 0.004, -40, y_land)                     # a 4 ms stagger, left to right
            a = 1.0 if i < 12 else 1.0 - (i - 11) / 4
            cv2.line(lit, (lx, 0), (lx, int(y_end)), tuple(int(c * a) for c in ACCENT), 7, cv2.LINE_AA)
            cv2.line(lit, (lx, 0), (lx, int(y_end)), tuple(int(c * a) for c in NEUTRAL), 3, cv2.LINE_AA)
            cv2.circle(lit, (lx, int(y_end)), 8, tuple(int(c * a) for c in WHITE), -1, cv2.LINE_AA)
    # the wordmark lights letter by letter, frames 10-22 (left to right, each over 4 frames)
    for k, ch in enumerate(WORD):
        t0 = 10 + k * 1.2; a = ease_out((i - t0) / 4)
        if a <= 0: continue
        c = tuple(int(ACCENT[j] * a + WHITE[j] * 0.35 * a * (1 - a) * 4) for j in range(3))   # a white flash on the way in
        dr.text((xs[k][0], y_word), ch, font=f_word, fill=(c[2], c[1], c[0]))
    # PRODUCTIONS tracks in, frames 22-30
    a = ease_out((i - 22) / 8)
    if a > 0:
        sub_w = dr.textlength(SUB, font=f_sub); spacing = 14 * a + 30 * (1 - a)
        total = sub_w + spacing * (len(SUB) - 1); x = xs[-1][1] - total; y = y_word + bbox[3] + 18
        for ch in SUB:
            dr.text((x, y), ch, font=f_sub, fill=(int(NEUTRAL[2] * a), int(NEUTRAL[1] * a), int(NEUTRAL[0] * a))); x += dr.textlength(ch, font=f_sub) + spacing
        # the accent tick under the wordmark's left half, drawn left to right
        x0, x1 = x_word, x_word + int(ww * 0.42 * a); yt = y_word + bbox[3] + 26
        cv2.line(lit, (x0, yt), (x1, yt), ACCENT, 4, cv2.LINE_AA)
    # the URL fades in over 6 frames from frame 30 and holds
    a = ease_out((i - 30) / 6)
    if a > 0:      # two lines: 44 characters of mono at a legible size do not fit the 950 px safe width on one line
        for k, line in enumerate(("github.com/DyeAllPies/", "dyeallpies-productions")):
            uw = dr.textlength(line, font=f_url)
            dr.text(((W - uw) // 2, 1120 + k * 66), line, font=f_url, fill=(int(NEUTRAL[2] * a), int(NEUTRAL[1] * a), int(NEUTRAL[0] * a)))
    text = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    lit = np.maximum(lit, text)
    out = np.maximum(canvas, glow(lit))
    return out


def main():
    out = sys.argv[1]; kw = dict(a.split("=", 1) for a in sys.argv[2:])
    hold = float(kw.get("hold", 1.5)); n = 30 + int(round(hold * FPS))
    shot = kw.get("append")
    if shot:
        # encode the sting so that it can be concatenated after the shot WITHOUT re-encoding the shot
        vid, a_in, a_args = sting_encode_args(shot)
        tmp = out + ".sting.mp4"
        enc = RawWriter(tmp, W, H, FPS, codec=vid, extra=a_args, audio_inputs=a_in, audio_t=n / FPS)
    else:
        tmp = out + ".sting.mp4"
        enc = RawWriter(tmp, W, H, FPS, codec=["-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p"])
    fdir = kw.get("frames")
    for i in range(n):
        f = frame(i, n - 30)
        enc.write(f)
        if fdir and i in (4, 9, 14, 20, 29, n - 1):
            os.makedirs(fdir, exist_ok=True); cv2.imwrite(os.path.join(fdir, f"sting_{i:02d}.png"), f)
    rc = enc.close()
    if not shot:
        os.replace(tmp, out); print("wrote", out, f"{n/FPS:.2f} s", "ffmpeg exit", rc); return
    concat_copy([shot, tmp], out); os.remove(tmp)
    ok, err = decode_check(out)
    print("wrote", out, "(concat copy, no re-encode of the shot); decode gate", "clean" if ok else "FAILED: " + err)


if __name__ == "__main__":
    main()
