"""Cut the two monkeys out of their source photos with GrabCut.

Run once before build_plate.py. The rectangles are tight around each animal: a loose one
leaves a visible box of background in the composite (learned the hard way).

  capuchin  "A curious Capuchin monkey perched on a branch.jpg", Nasehi2277, CC0
  langur    "Langur Monkey in tree Betla 2025.jpg", Dev0745, CC BY 4.0
"""
import cv2
import numpy as np

JOBS = [
    ("pullup/assets/monkey_capuchin.jpg", (0.475, 0.21, 0.20, 0.66), "capuchin"),
    ("pullup/assets/monkey_langur.jpg",   (0.27, 0.385, 0.17, 0.165), "langur"),
]

for path, (rx, ry, rw, rh), name in JOBS:
    im = cv2.imread(path)
    h, w = im.shape[:2]
    rect = (int(rx * w), int(ry * h), int(rw * w), int(rh * h))
    m = np.zeros(im.shape[:2], np.uint8)
    bg, fg = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(im, m, rect, bg, fg, 10, cv2.GC_INIT_WITH_RECT)
    a = np.where((m == 1) | (m == 3), 255, 0).astype(np.uint8)
    a = cv2.morphologyEx(a, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(a)
    if n > 1:
        k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        a = np.where(lab == k, 255, 0).astype(np.uint8)
    ys, xs = np.nonzero(a)
    af = cv2.GaussianBlur(a, (0, 0), 1.6).astype(np.float32) / 255
    crop = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    ac = af[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    np.save(f"pullup/work2/{name}_alpha.npy", ac)
    cv2.imwrite(f"pullup/work2/{name}_rgb.png", crop)
    print(f"{name}: {crop.shape[1]}x{crop.shape[0]}, coverage {ac.mean():.2f}")
