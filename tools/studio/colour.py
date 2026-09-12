"""Colour maths shared by the renderers and the brand: sRGB transfer, hex helpers, WCAG contrast.

The sRGB transfer function is IEC 61966-2-1 (the piecewise curve with the 0.04045 / 0.0031308
knees). The WCAG relative luminance and contrast ratio follow WCAG 2.2's definitions
(references/marionette/brand/w3-wcag-glossary-relative-luminance.html, item 08):
L = 0.2126 R + 0.7152 G + 0.0722 B on the linearised channels, contrast = (L1 + 0.05) / (L2 + 0.05).
"""
import numpy as np


def srgb_to_lin(x):
    """sRGB [0,1] -> linear light. Works on floats and arrays."""
    x = np.asarray(x, dtype=np.float32)
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4).astype(np.float32)


def lin_to_srgb(x):
    """Linear light -> sRGB [0,1], clipped."""
    x = np.clip(np.asarray(x, dtype=np.float32), 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055).astype(np.float32)


# the 8-bit plate goes through a 256-entry table instead of a power function over every pixel
# (a full-frame srgb_to_lin cost 0.10 s a frame in the puppet composite, 2026-09-12; the LUT is exact)
SRGB8_TO_LIN = srgb_to_lin(np.arange(256, dtype=np.float32) / 255.0)


def srgb8_to_lin(img_u8):
    return SRGB8_TO_LIN[img_u8]


def lin_to_srgb8(x):
    return (lin_to_srgb(x) * 255 + 0.5).astype(np.uint8)


def hex_to_rgb01(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def hex_to_bgr8(h):
    """OpenCV's channel order."""
    r, g, b = (int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    return (b, g, r)


def hex_to_rgb8(h):
    return tuple(int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))


def wcag_luminance(h):
    r, g, b = srgb_to_lin(np.array(hex_to_rgb01(h)))
    return float(0.2126 * r + 0.7152 * g + 0.0722 * b)


def wcag_contrast(fg, bg):
    """Contrast ratio between two hex colours (>= 1), order-independent."""
    a, b = wcag_luminance(fg), wcag_luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


if __name__ == "__main__":
    import sys
    cols = sys.argv[1:] or ["#231F20", "#D75413", "#F2F0EA", "#FFFFFF"]
    for i, a in enumerate(cols):
        for b in cols[i + 1:]:
            print(f"{a} on {b}: {wcag_contrast(a, b):.2f}:1")
