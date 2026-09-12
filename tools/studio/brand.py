"""The DyeAllPies Productions palette and type, as code. tools/brand/BRAND.md is the human-readable
copy with the reasoning and the contrast table; the two must agree (BRAND.md's table is printed by
`python -m studio.brand`).

Colours (Dennis, 2026-09-12): main #231F20 (a warm near-black), secondary #D75413 (orange). The
off-white #F2F0EA is the neutral for type on the dark ground and doubles as the wall reference of
the hand-puppet plate. The cyan/blue of v0 were provisional from the neon look and are gone; the
puppet's own red is a per-video look decision (references/marionette/09), not the brand.
"""
import os
from PIL import ImageFont
from .colour import hex_to_bgr8, hex_to_rgb8, wcag_contrast

MAIN = "#231F20"          # the ground of every sting and card
SECONDARY = "#D75413"     # the wordmark, the tick, the strings: the one accent
NEUTRAL = "#F2F0EA"       # type that is not the accent (PRODUCTIONS, the URL); the wall reference
WHITE = "#FFFFFF"         # one flash beat only

PALETTE = {"main": MAIN, "secondary": SECONDARY, "neutral": NEUTRAL, "white": WHITE}

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "brand", "fonts")
FONTS = {"wordmark": ("SpaceGrotesk-Bold.ttf", 700), "sub": ("Inter.ttf", 600), "mono": ("JetBrainsMono.ttf", 500)}


def bgr(name_or_hex):
    return hex_to_bgr8(PALETTE.get(name_or_hex, name_or_hex))


def rgb(name_or_hex):
    return hex_to_rgb8(PALETTE.get(name_or_hex, name_or_hex))


def font(role, size):
    """A PIL font for a brand role ('wordmark', 'sub', 'mono') at its brand weight (variable axes set when the file has them)."""
    name, weight = FONTS[role]
    f = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    try: f.set_variation_by_axes([weight] if name != "Inter.ttf" else [14, weight])
    except Exception: pass
    return f


def contrast_table():
    rows = [("secondary on main", SECONDARY, MAIN), ("neutral on main", NEUTRAL, MAIN), ("white on main", WHITE, MAIN),
            ("main on neutral (the wall)", MAIN, NEUTRAL), ("secondary on neutral (the wall)", SECONDARY, NEUTRAL)]
    return [(label, a, b, wcag_contrast(a, b)) for label, a, b in rows]


if __name__ == "__main__":
    for label, a, b, c in contrast_table():
        aa = "AA" if c >= 4.5 else ("AA large" if c >= 3 else "fails")
        print(f"{label:34s} {a} on {b}: {c:5.2f}:1  {aa}")
