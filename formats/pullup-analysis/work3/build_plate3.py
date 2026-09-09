"""Jungle-with-monkeys backdrop plate, set #3: Mata Atlantica (CC BY 4.0, Jens Lallensack) with
high-resolution monkey cut-outs (rembg isnet, alpha matting) placed on real trunks and branches.
Credits: pullup/assets/commons/CREDITS.json -> pullup/assets/ATTRIBUTION.md."""
import cv2, numpy as np, os
W, H = 1080, 1920
base = cv2.imread("pullup/assets/commons/mata_atlantica_00.jpg"); h, w = base.shape[:2]
tw = int(h * 9 / 16); x0 = (w - tw) // 2
plate = cv2.resize(base[:, x0:x0 + tw], (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
# a little darker and calmer, so the painted body leads
hsv = cv2.cvtColor(np.clip(plate, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
hsv[..., 1] *= 0.86; hsv[..., 2] *= 0.80
plate = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)


def paste(dst, name, cx, cy, height, flip=False, dark=0.92, blur=0.0):
    p = f"pullup/work3/cutouts/{name}.png"
    if not os.path.exists(p):
        print("missing", name); return
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    a = im[..., 3]; ys, xs = np.where(a > 30)
    im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    rgb = im[..., :3].astype(np.float32); al = im[..., 3].astype(np.float32) / 255
    h0, w0 = al.shape; s = height / h0; ww, hh = max(2, int(w0 * s)), max(2, int(h0 * s))
    rgb = cv2.resize(rgb, (ww, hh), interpolation=cv2.INTER_AREA) * dark
    al = cv2.resize(al, (ww, hh), interpolation=cv2.INTER_AREA)
    if blur > 0:
        rgb = cv2.GaussianBlur(rgb, (0, 0), blur); al = cv2.GaussianBlur(al, (0, 0), blur * 0.6)
    if flip:
        rgb = rgb[:, ::-1].copy(); al = al[:, ::-1].copy()
    x0_, y0_ = int(cx - ww / 2), int(cy - hh / 2)
    xs0, ys0 = max(0, x0_), max(0, y0_); xs1, ys1 = min(W, x0_ + ww), min(H, y0_ + hh)
    if xs1 <= xs0 or ys1 <= ys0:
        return
    sx0, sy0 = xs0 - x0_, ys0 - y0_
    roi = dst[ys0:ys1, xs0:xs1]
    a_ = al[sy0:sy0 + (ys1 - ys0), sx0:sx0 + (xs1 - xs0)][:, :, None]
    pj = rgb[sy0:sy0 + (ys1 - ys0), sx0:sx0 + (xs1 - xs0)]
    dst[ys0:ys1, xs0:xs1] = roi * (1 - a_) + pj * a_
    print(f"{name:24s} at ({cx},{cy}) h={height} flip={flip}")


paste(plate, "spider_monkey_04", 190, 430, 200, flip=False, dark=0.85, blur=0.6)   # walking a canopy branch, far
paste(plate, "howler_monkey_02", 975, 640, 230, flip=True, dark=0.90)              # howling on the right trunk
paste(plate, "marmoset_00", 185, 800, 250, flip=False, dark=0.95)                  # clinging to the left trunk
paste(plate, "capuchin_monkey_05", 62, 640, 330, flip=False, dark=0.85, blur=0.4)   # hanging from a liana, far left
paste(plate, "golden_lion_tamarin_01", 240, 1190, 150, flip=False, dark=0.92)      # on the low branch
paste(plate, "spider_monkey_09", 985, 1060, 260, flip=True, dark=0.90)             # right trunk, tail down
paste(plate, "spider_monkey_10", 130, 1520, 220, flip=False, dark=0.80, blur=0.8)   # in the fronds, far
# vignette
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
plate *= np.clip(1 - 0.28 * np.clip((r - 0.6) / 0.7, 0, 1) ** 1.5, 0, 1)[:, :, None]
cv2.imwrite("pullup/assets/jungle3_plate.jpg", np.clip(plate, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])
print("-> pullup/assets/jungle3_plate.jpg")
