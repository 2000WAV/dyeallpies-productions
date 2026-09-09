"""Build the jungle-with-monkeys backdrop plate (1080x1920) for the pull-up reel.

Base:    Palawan rainforest canopy, Vyacheslav Argenberg, CC BY 4.0.
Monkeys: a white-faced capuchin on a branch (CC0, Nasehi2277) and a grey langur in a tree
         (CC BY 4.0, Dev0745), both cut out with GrabCut (see cut_monkeys.py) and placed
         in the canopy away from the centre column where the body hangs.
"""
import cv2
import numpy as np

W, H = 1080, 1920
base = cv2.resize(cv2.imread("pullup/assets/jungle_plate.jpg"), (W, H), interpolation=cv2.INTER_AREA)
out = base.astype(np.float32)


def paste(dst, src, alpha, cx, cy, height, flip=False, dark=1.0, blur=0.0):
    h0, w0 = src.shape[:2]
    s = height / h0
    w, h = max(2, int(w0 * s)), max(2, int(h0 * s))
    im = cv2.resize(src, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) * dark
    al = cv2.resize(alpha, (w, h), interpolation=cv2.INTER_AREA)
    if blur > 0:
        im = cv2.GaussianBlur(im, (0, 0), blur)
        al = cv2.GaussianBlur(al, (0, 0), blur * 0.6)
    al = al[:, :, None]
    if flip:
        im = im[:, ::-1].copy(); al = al[:, ::-1].copy()
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    xs0, ys0 = max(0, x0), max(0, y0)
    xs1, ys1 = min(dst.shape[1], x0 + w), min(dst.shape[0], y0 + h)
    if xs1 <= xs0 or ys1 <= ys0:
        return
    sx0, sy0 = xs0 - x0, ys0 - y0
    roi = dst[ys0:ys1, xs0:xs1]
    a = al[sy0:sy0 + (ys1 - ys0), sx0:sx0 + (xs1 - xs0)]
    pj = im[sy0:sy0 + (ys1 - ys0), sx0:sx0 + (xs1 - xs0)]
    dst[ys0:ys1, xs0:xs1] = roi * (1 - a) + pj * a


cap_rgb = cv2.imread("pullup/work2/capuchin_rgb.png"); cap_a = np.load("pullup/work2/capuchin_alpha.npy")
lan_rgb = cv2.imread("pullup/work2/langur_rgb.png"); lan_a = np.load("pullup/work2/langur_alpha.npy")

# canopy dwellers, clear of the centre column the body hangs in
paste(out, cap_rgb, cap_a, W * 0.135, H * 0.300, int(H * 0.190), dark=0.80)
paste(out, lan_rgb, lan_a, W * 0.880, H * 0.235, int(H * 0.135), dark=0.84)
paste(out, cap_rgb, cap_a, W * 0.905, H * 0.585, int(H * 0.098), flip=True, dark=0.62, blur=0.7)
paste(out, lan_rgb, lan_a, W * 0.075, H * 0.700, int(H * 0.070), flip=True, dark=0.55, blur=1.1)

out = np.clip(out, 0, 255).astype(np.uint8)
cv2.imwrite("pullup/assets/jungle_monkeys_plate.jpg", out, [cv2.IMWRITE_JPEG_QUALITY, 95])
print("wrote pullup/assets/jungle_monkeys_plate.jpg")
