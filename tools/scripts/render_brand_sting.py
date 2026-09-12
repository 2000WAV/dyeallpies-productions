"""The DyeAllPies Productions end sting: the five-string drop lights the wordmark, then the URL holds.

    python render_brand_sting.py <out.mp4>                    # the sting alone (2.5 s, 1080x1920, 30 fps, silent)
    python render_brand_sting.py <out.mp4> append=<shot.mp4>  # the shot with the sting appended (the shot's audio kept, silence under the sting)
    options: hold=1.5 (s of URL hold after the 1 s animation) frames=<dir> (write PNGs of the beats for a check)
             ground=#000000 (the sting's ground; default the brand main #231F20. Pitch black for the neon-on-black
             puppet, Dennis 2026-09-12: the shot ends on #000000 and the sting must not step to the warm near-black)
             look=neon [accent=#8F00FF core=#CCA1FF tick=#FF0000 gain=1.5 wall=0.8] (2026-09-12: the puppet video's
             own look carried into the logo: the wordmark and strings in the doll's violet with a pale tube core, the
             tick in the boots' red with the boots' glow, the glow computed in linear light with studio.glow's
             bloom + pool + shoulder, the same numbers as the video's composite)

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
from studio import glow as sglow
from studio.colour import srgb8_to_lin, lin_to_srgb8
from studio.encode import RawWriter, sting_encode_args, concat_copy, decode_check

W, H, FPS = 1080, 1920, 30
GROUND = brand.bgr("main")            # #231F20
ACCENT = brand.bgr("secondary")       # #D75413: the wordmark, the strings, the tick
NEUTRAL = brand.bgr("neutral")        # #F2F0EA: PRODUCTIONS, the URL, the strings' core
WHITE = brand.bgr("white")
TICK = ACCENT                         # the tick under the wordmark (the neon look gives it its own hue)
CORE = NEUTRAL                        # the tube core of the strings and, in the neon look, of the wordmark's glyphs
NEON = False                          # look=neon: the puppet video's own glow instead of the brand's sRGB three-Gaussian halo
NEON_GAIN = 1.5                       # the lit elements' emission in linear light (the doll's parts reach 1-2 with their rim and specular)
HOT_GAIN = 3.5                        # the `hot` layer's extra bloom (the violet-mix boots' glow gain)
WALL = 0.8                            # the pool on the wall (the puppet composite's wall=0.8)
CORE_INSET = 7                        # px: the glyph erosion that leaves the tube core (the wordmark's stems are ~28 px at 150 px)
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
    hot = np.zeros((H, W, 3), np.uint8)                      # the elements bloomed HOT_GAIN times more (the tick in the neon look, as the boots)
    pil = Image.new("RGB", (W, H)); dr = ImageDraw.Draw(pil)
    pil_word = Image.new("RGB", (W, H)); dr_word = ImageDraw.Draw(pil_word)   # the wordmark alone: the neon look carves its tube core from it
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
        dr_word.text((xs[k][0], y_word), ch, font=f_word, fill=(c[2], c[1], c[0]))
    # PRODUCTIONS tracks in, frames 22-30
    a = ease_out((i - 22) / 8)
    if a > 0:
        sub_w = dr.textlength(SUB, font=f_sub); spacing = 14 * a + 30 * (1 - a)
        total = sub_w + spacing * (len(SUB) - 1); x = xs[-1][1] - total; y = y_word + bbox[3] + 18
        for ch in SUB:
            dr.text((x, y), ch, font=f_sub, fill=(int(NEUTRAL[2] * a), int(NEUTRAL[1] * a), int(NEUTRAL[0] * a))); x += dr.textlength(ch, font=f_sub) + spacing
        # the accent tick under the wordmark's left half, drawn left to right
        x0, x1 = x_word, x_word + int(ww * 0.42 * a); yt = y_word + bbox[3] + 26
        cv2.line(hot if NEON else lit, (x0, yt), (x1, yt), TICK, 4, cv2.LINE_AA)
    # the URL fades in over 6 frames from frame 30 and holds
    a = ease_out((i - 30) / 6)
    if a > 0:      # two lines: 44 characters of mono at a legible size do not fit the 950 px safe width on one line
        for k, line in enumerate(("github.com/DyeAllPies/", "dyeallpies-productions")):
            uw = dr.textlength(line, font=f_url)
            dr.text(((W - uw) // 2, 1120 + k * 66), line, font=f_url, fill=(int(NEUTRAL[2] * a), int(NEUTRAL[1] * a), int(NEUTRAL[0] * a)))
    text = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR); word = cv2.cvtColor(np.array(pil_word), cv2.COLOR_RGB2BGR)
    if NEON:
        # the tube core: the glyph eroded by CORE_INSET px is filled with the pale core colour at the glyph's own
        # brightness (the light-up alpha and the flash carry through), the accent stays as the tube's rim: the
        # same read as the doll's parts, a bright thick middle and a coloured edge
        bright = np.clip(word.max(-1).astype(np.float32) / 255.0, 0, 1)
        inner = cv2.erode((bright > 0.02).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * CORE_INSET + 1, 2 * CORE_INSET + 1))) > 0
        core = (np.array(CORE, np.float32)[None, None] * bright[..., None]).astype(np.uint8)
        word[inner] = core[inner]
    lit = np.maximum(lit, np.maximum(text, word))
    if not NEON:
        return np.maximum(canvas, glow(lit))
    # the neon look (2026-09-12, Dennis: the logo in the doll's violet, its elements neon and shining, reflecting
    # in the background; "a common visual thread that extends into the logo"): the puppet composite's own glow in
    # linear light, studio.glow: the emission at NEON_GAIN, the mip bloom, the pool on the wall, the shoulder
    E = srgb8_to_lin(lit) * np.float32(NEON_GAIN); Eh = srgb8_to_lin(hot) * np.float32(NEON_GAIN)
    src = E + Eh * np.float32(HOT_GAIN)
    out = srgb8_to_lin(canvas) + E + Eh + sglow.bloom(src) + sglow.pool(src, WALL)
    return lin_to_srgb8(sglow.shoulder(out))


def main():
    out = sys.argv[1]; kw = dict(a.split("=", 1) for a in sys.argv[2:])
    hold = float(kw.get("hold", 1.5)); n = 30 + int(round(hold * FPS))
    global GROUND, ACCENT, NEUTRAL, TICK, CORE, NEON, NEON_GAIN, WALL
    if "ground" in kw:
        GROUND = brand.bgr(kw["ground"]); print(f"ground {kw['ground']}")
    if kw.get("look") == "neon":
        # the video's own thread carried into the logo (Dennis, 2026-09-12: no fixed brand yet): the wordmark and the
        # strings in the doll's electric violet, their cores and the secondary text in the strings' pale violet, the
        # tick in the boots' pure red with the boots' glow; the defaults are the violet-mix look's colours in sRGB
        NEON = True
        ACCENT = brand.bgr(kw.get("accent", "#8F00FF")); CORE = brand.bgr(kw.get("core", "#CCA1FF")); NEUTRAL = CORE
        TICK = brand.bgr(kw.get("tick", "#FF0000")); NEON_GAIN = float(kw.get("gain", NEON_GAIN)); WALL = float(kw.get("wall", WALL))
        print(f"look neon: accent {kw.get('accent', '#8F00FF')} core {kw.get('core', '#CCA1FF')} tick {kw.get('tick', '#FF0000')} gain {NEON_GAIN} wall {WALL}")
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
