"""Hand matte on a uniform wall: rembg (isnet) for the trimap, a colour key against the locally
estimated wall colour for the edge band, a guided filter to snap the edge to the plate.

    python extract_hand_matte.py <master.mp4> <out_dir> rembg          # stage 1: rembg alpha per frame -> out_dir/rembg.npy (uint8, n x H x W)
    python extract_hand_matte.py <master.mp4> <out_dir> refine [band=12] [key=0] [shrink=0.12]   # stage 2: -> out_dir/matte.npy (uint8) + a check sheet

Written 2026-09-11 for the hand-puppet video (hand/PLAN.md decision 3: a precise matte, every
finger's outline sharp, no halo, judged at 1:1 on the snap-open frames 42-54).

What was tried (2026-09-11, judged at 1:1 on frames 42-165): rembg's alpha alone leaves a faint
one-pixel light halo on a finger's shaded side. A colour key against the local wall colour inside a
trimap band (chroma + luminance distance, k=10) opened holes at the pale nails and fingertip pads,
whose chroma is within 4-6 of the wall's, on every frame checked: worse than rembg. What stands:
rembg decides everything, and inside a +-band px edge band its alpha is passed through the guided
filter (He, Sun & Tang 2010) on the plate's luminance, which snaps the ramp to the picture's own
edge and keeps the motion-blur ramp of the snap-open; a half-pixel erosion (the `shrink` factor)
takes the halo. The colour key stays in the file, switched off (key=1 turns it on).

Matte convention: 255 = hand (occludes the puppet), 0 = wall. The wall is only ever the plate.
"""
import sys, os, time
import numpy as np
import cv2


def box(x, r):
    return cv2.blur(x, (2 * r + 1, 2 * r + 1), borderType=cv2.BORDER_REFLECT)


def guided_filter(I, p, r, eps):
    """He, Sun & Tang 2010 (ECCV; TPAMI 2013) guided filter, grey guide I in [0,1], input p in [0,1]."""
    mI, mp = box(I, r), box(p, r)
    cov = box(I * p, r) - mI * mp
    var = box(I * I, r) - mI * mI
    a = cov / (var + eps)
    b = mp - a * mI
    return box(a, r) * I + box(b, r)


def local_wall(lab, wall_mask, r=60):
    """Normalised convolution: the wall's colour under and around the hand, from the confident wall
    pixels near it (the shadow gradient is low-frequency, so a 121 px box follows it)."""
    m = wall_mask.astype(np.float32)
    num = cv2.blur(lab * m[..., None], (2 * r + 1, 2 * r + 1))
    den = cv2.blur(m, (2 * r + 1, 2 * r + 1))[..., None]
    est = num / np.maximum(den, 1e-3)
    # where no wall pixel is within the box (deep inside the hand) fall back to a wider estimate
    far = den[..., 0] < 0.02
    if far.any():
        num2 = cv2.blur(lab * m[..., None], (401, 401)); den2 = cv2.blur(m, (401, 401))[..., None]
        est[far] = (num2 / np.maximum(den2, 1e-3))[far]
    return est


def refine_frame(bgr, ralpha, band, k, use_key=False, shrink=0.12):
    H, W = ralpha.shape
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    lab[..., 0] *= 100.0 / 255.0; lab[..., 1:] -= 128.0
    hard = ralpha > 128
    ker = np.ones((2 * band + 1, 2 * band + 1), np.uint8)
    inner = cv2.erode(hard.astype(np.uint8), ker) > 0          # certainly hand
    outer = cv2.dilate(hard.astype(np.uint8), ker) > 0         # hand or edge band
    wall_conf = ~cv2.dilate(hard.astype(np.uint8), np.ones((2 * band + 41, 2 * band + 41), np.uint8)).astype(bool)
    est = local_wall(lab, wall_conf)
    dL = est[..., 0] - lab[..., 0]                              # darker than the local wall (ink, skin, shadow-of-finger-on-finger)
    dC = np.hypot(lab[..., 1] - est[..., 1], lab[..., 2] - est[..., 2])   # chroma away from the wall (skin, the rose)
    # distance in a metric where the wall's own shadow (dL up to ~25, dC ~ 2) stays wall and skin (dC > 8) or ink (dL > 40) is hand
    d = np.hypot(dC, np.maximum(dL - 12.0, 0.0) * 0.35)
    key = np.clip(d / k, 0.0, 1.0)
    base = ralpha.astype(np.float32) / 255.0
    if use_key: base = np.minimum(base, key)
    alpha = np.where(inner, 1.0, np.where(outer, base, 0.0)).astype(np.float32)
    # guided filter on the plate's luminance snaps the band to the real edge and keeps the blur ramp
    g = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    a2 = guided_filter(g, alpha, 4, 2e-3)
    a2 = np.clip((a2 - shrink) / (1.0 - shrink), 0.0, 1.0)      # a half-pixel erosion of the ramp: the halo goes
    a2 = np.where(inner, 1.0, np.where(outer, a2, 0.0))
    return np.clip(a2 * 255.0 + 0.5, 0, 255).astype(np.uint8)


def main():
    video, out_dir, stage = sys.argv[1], sys.argv[2], sys.argv[3]
    kw = dict(a.split("=", 1) for a in sys.argv[4:])
    os.makedirs(out_dir, exist_ok=True)
    cap = cv2.VideoCapture(video)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if stage == "rembg":
        from rembg import remove, new_session
        sess = new_session("isnet-general-use")
        out = np.lib.format.open_memmap(os.path.join(out_dir, "rembg.npy"), mode="w+", dtype=np.uint8, shape=(n, H, W))
        t0 = time.time()
        for i in range(n):
            ok, f = cap.read()
            if not ok: break
            m = remove(cv2.cvtColor(f, cv2.COLOR_BGR2RGB), session=sess, only_mask=True, post_process_mask=False)
            out[i] = np.asarray(m)
            if i % 20 == 0: print(f"{i}/{n} {(time.time()-t0)/(i+1):.2f} s/frame", flush=True)
        out.flush(); print("rembg done", n)
    elif stage == "refine":
        band = int(kw.get("band", 12)); k = float(kw.get("k", 10)); use_key = kw.get("key", "0") == "1"; shrink = float(kw.get("shrink", 0.12))
        ra = np.load(os.path.join(out_dir, "rembg.npy"), mmap_mode="r")
        out = np.lib.format.open_memmap(os.path.join(out_dir, "matte.npy"), mode="w+", dtype=np.uint8, shape=(n, H, W))
        t0 = time.time(); checks = {}
        want = {int(x) for x in kw.get("check", "42,44,48,54,63,165").split(",")}
        for i in range(n):
            ok, f = cap.read()
            if not ok: break
            out[i] = refine_frame(f, np.asarray(ra[i]), band, k, use_key, shrink)
            if i in want: checks[i] = (f, out[i].copy(), np.asarray(ra[i]).copy())
            if i % 20 == 0: print(f"{i}/{n} {(time.time()-t0)/(i+1):.2f} s/frame", flush=True)
        out.flush()
        # check sheet: for each frame, 1:1 crops around the lowest finger tips: plate | refined edge tinted | rembg edge tinted
        rows = []
        for i, (f, m, r) in checks.items():
            ys, xs = np.where(m > 128)
            if len(ys) == 0: continue
            y = int(np.percentile(ys, 99)); x = int(np.median(xs[ys > y - 60]))
            def crop(img): return img[max(0, y - 220):y + 120, max(0, x - 260):x + 260]
            def tint(mm):
                o = f.copy(); w = mm < 128; o[w] = (o[w] * 0.55 + np.array([255, 60, 0]) * 0.45).astype(np.uint8); return o
            tiles = [crop(f), crop(tint(m)), crop(tint(r))]
            h = min(t.shape[0] for t in tiles); w = min(t.shape[1] for t in tiles)
            row = np.hstack([t[:h, :w] for t in tiles]); cv2.putText(row, str(i), (8, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            rows.append(row)
        if rows:
            w = min(r.shape[1] for r in rows)
            cv2.imwrite(os.path.join(out_dir, "matte_check.png"), np.vstack([r[:, :w] for r in rows]))
        print("refine done", n)


if __name__ == "__main__":
    main()
