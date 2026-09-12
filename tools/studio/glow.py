"""The neon glow, shared by the puppet composite and the brand sting (2026-09-12): a wide Gaussian at
quarter resolution, the mip bloom, the pool of light on a dark wall, the shoulder that lets a hot
core go white while the colour survives around it. Everything works in LINEAR light on float32 BGR.

The numbers are the puppet's (render_puppet.py's docstring, references/marionette/06 section 10 for
the bloom, item 12 for the halo target): BLOOM = sigma px at 1x and weight, 0.45 in total, above the
0.03-0.15 whole-frame game range because the layer is only the emissive subject; the pool is a
sigma 60 + 180 px blur of the emission at 0.35 + 0.25, scaled by `wall` (0.8 shipped).
"""
import numpy as np
import cv2

BLOOM = [(3, 0.22), (9, 0.12), (27, 0.07), (81, 0.04)]
POOL = [(60, 0.35), (180, 0.25)]


def wide_blur(img, sigma, down=4):
    """A Gaussian of sigma >= 12 px computed at 1/down resolution and resized back: the same result to
    the eye at a sixteenth of the cost (the black composite's four wide blurs cost 1.4 s a frame at
    full resolution, 2026-09-12)."""
    if sigma < 12:
        return cv2.GaussianBlur(img, (0, 0), sigma)
    H, W = img.shape[:2]
    small = cv2.resize(img, (W // down, H // down), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), sigma / down)
    return cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR)


def bloom(E, levels=BLOOM):
    """The sum of the weighted Gaussians of the emission E (linear, premultiplied where it matters)."""
    out = np.zeros_like(E, dtype=np.float32)
    for sigma, w in levels:
        g = wide_blur(E, sigma); g *= np.float32(w); out += g
    return out


def pool(E, wall=0.8, levels=POOL):
    """The emission's light on the dark wall behind it: a near pool and a broad one, dim; 0 = pitch black."""
    out = np.zeros_like(E, dtype=np.float32)
    if wall <= 0: return out
    for sigma, w in levels:
        g = wide_blur(E, sigma); g *= np.float32(w * wall); out += g
    return out


def shoulder(out, knee=0.8):
    """Per channel y = x below the knee, knee + (1 - knee)(1 - exp(-(x - knee) / (1 - knee))) above: the
    hottest core goes white, the colour survives around it. In place, only where it bites."""
    hi = out > knee
    if hi.any(): out[hi] = knee + (1 - knee) * (1 - np.exp(-(out[hi] - knee) / (1 - knee)))
    return out
