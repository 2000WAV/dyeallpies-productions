"""
"Look" pass for the pull-up reel: make phone footage shot indoors without daylight read
as a deliberate, higher-quality image. Everything is driven by the person matte:

  background  desaturated, darkened and softened (shallow depth-of-field illusion)
  subject     unsharp-masked (crisper skin/heat edges), contrast lifted
  rim glow    a thin coloured aura just outside the silhouette (colour = the heat LUT
              at the current fatigue level), so the body separates from the wall
  grain       fine monochrome grain over everything (hides compression mush)
  vignette    soft darkening of the corners (keeps the eye centred)

    look = LookPass(W, H); frame = look.apply(frame_bgr, alpha_full, rim_bgr, strength)
"""
import numpy as np
import cv2


class LookPass:
    def __init__(self, W, H, seed=7):
        self.W, self.H = W, H
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        self.vignette = np.clip(1 - 0.32 * np.clip((r - 0.55) / 0.75, 0, 1) ** 1.6, 0, 1)[:, :, None]
        rng = np.random.default_rng(seed)
        self.grain = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(8)]

    def apply(self, frame, alpha, rim_bgr, strength=1.0, i=0, keep_colour=False):
        f = frame.astype(np.float32)
        a = np.clip(alpha, 0, 1)[:, :, None]
        if keep_colour:
            # a replaced backdrop: keep its colour, just a touch darker and softer
            bg = cv2.GaussianBlur(f, (0, 0), 1.4) * 0.88
        else:
            # the real room: desaturate, darken, soften
            bg = cv2.GaussianBlur(f, (0, 0), 2.2)
            g = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)[:, :, None]
            bg = (bg * 0.45 + g * 0.55) * 0.72
        # subject: unsharp mask + a touch of contrast
        blur = cv2.GaussianBlur(f, (0, 0), 1.6)
        fg = np.clip(f + 0.55 * (f - blur), 0, 255)
        fg = np.clip((fg - 118) * 1.10 + 118, 0, 255)
        out = bg * (1 - a) + fg * a
        # rim glow outside the silhouette
        a8 = (np.clip(alpha, 0, 1) * 255).astype(np.uint8)
        ring = cv2.GaussianBlur(cv2.dilate(a8, np.ones((13, 13), np.uint8)), (0, 0), 7).astype(np.float32) / 255
        ring = np.clip(ring - np.clip(alpha, 0, 1), 0, 1)[:, :, None]
        out = out * (1 - 0.75 * ring) + np.array(rim_bgr, np.float32)[None, None, :] * 0.75 * ring
        # grain + vignette
        gr = cv2.resize(self.grain[i % len(self.grain)], (self.W, self.H), interpolation=cv2.INTER_LINEAR)[:, :, None]
        out = out + gr * 5.5
        out = out * self.vignette
        return np.clip(f * (1 - strength) + out * strength, 0, 255).astype(np.uint8)
