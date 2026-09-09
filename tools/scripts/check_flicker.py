"""
Fail-safe for composited exports: find flashing / flicker before anyone watches it.

    python check_flicker.py <rendered.mp4> <matte.npy> <report.png> [thresh=3.0]
                            [offset=N] [map=frames.json] [skip=f1,f2,...]

offset= shifts the matte index (a render trimmed to start at source frame N).
map=    a JSON list, one source frame index per rendered frame (a scheduled cut); the
        gate then also knows where the cuts are and reports them separately, since a cut
        is a deliberate one-frame jump and not a flicker.

Per frame it measures, inside the person region (matte alpha channel 0, eroded) and in a
strip of the background (outside a dilated alpha):
  * mean colour (B, G, R) and the painted fraction,
  * the mean absolute difference to the previous frame,
then flags frames whose difference is a one-frame spike (> thresh x the local median of
the neighbouring 15 frames) or whose mean colour jumps and comes back within 2 frames.
Prints a table of suspects (frame, time, where, size) and writes a plot. Exit code 1 if
any suspect is found so it can gate a delivery.
"""
import sys
import numpy as np
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    video, matte, out = sys.argv[1:4]
    thresh = 3.0; offset = 0; fmap = None; skip = set(); zoom = None
    for a in sys.argv[4:]:
        if a.startswith("thresh="): thresh = float(a[7:])
        elif a.startswith("offset="): offset = int(a[7:])
        elif a.startswith("zoom="): zoom = [float(x) for x in a[5:].split(",")]   # x0,y0,z: the renderer's push-in
        elif a.startswith("map="):
            import json as _json
            fmap = _json.load(open(a[4:]))
        elif a.startswith("skip="): skip = {int(x) for x in a[5:].split(",")}
    comp = np.load(matte, mmap_mode="r")
    cap = cv2.VideoCapture(video); fps = cap.get(cv2.CAP_PROP_FPS); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    nm = comp.shape[0]
    body_mean = np.full((n, 3), np.nan); bg_mean = np.full((n, 3), np.nan)
    body_diff = np.full(n, np.nan); bg_diff = np.full(n, np.nan); area = np.full(n, np.nan)
    prev = None; prev_body = None
    i = 0
    while True:
        got, f = cap.read()
        if not got or i >= n:
            break
        fi = min((fmap[i] if fmap and i < len(fmap) else i + offset), nm - 1)
        a = cv2.resize(np.asarray(comp[fi])[..., 0], (W, H), interpolation=cv2.INTER_LINEAR)
        if zoom:      # the render was cropped at (x0, y0) and scaled by z before the UI went on
            x0, y0, z = int(zoom[0]), int(zoom[1]), zoom[2]
            a = cv2.resize(a[y0:y0 + int(round(H / z)), x0:x0 + int(round(W / z))], (W, H), interpolation=cv2.INTER_LINEAR)
        body = cv2.erode((a > 128).astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
        body[H // 2:] = False                      # torso/arms half: where the paint lives
        bg = cv2.dilate((a > 40).astype(np.uint8), np.ones((61, 61), np.uint8)) == 0
        bg[1100:] = False; bg[:220] = False        # avoid the chart / card panels and the title band
        bg[:, :500] = False; bg[:, 860:] = False   # avoid the counter, phase pill, metrics box and gauge
        small = f.astype(np.float32)
        if body.sum() > 500:
            body_mean[i] = small[body].mean(0); area[i] = body.mean()
            if prev is not None and prev_body is not None:
                both = body & prev_body
                if both.sum() > 500:
                    body_diff[i] = np.abs(small[both] - prev[both]).mean()
        if bg.sum() > 500:
            bg_mean[i] = small[bg].mean(0)
            if prev is not None:
                bg_diff[i] = np.abs(small[bg] - prev[bg]).mean()
        prev = small; prev_body = body
        i += 1
    cap.release()
    t = np.arange(n) / fps

    def spikes(d, label):
        out = []
        for k in range(1, n - 1):
            if np.isnan(d[k]):
                continue
            lo, hi = max(0, k - 8), min(n, k + 9)
            nb = np.concatenate([d[lo:k], d[k + 1:hi]]); nb = nb[~np.isnan(nb)]
            if len(nb) < 6:
                continue
            ref = np.median(nb) + 1e-3
            if d[k] > thresh * ref and d[k] > 4.0:
                if k in skip or (fmap and k > 0 and k < len(fmap)
                                 and abs(fmap[k] - fmap[k - 1]) not in (0, 1)
                                 and abs(fmap[k] - fmap[k - 1]) != (fmap[1] - fmap[0] if len(fmap) > 1 else 1)):
                    continue                      # a deliberate cut in the schedule
                out.append((k, t[k], label, d[k], ref))
        return out

    def bounces(m, label, tol=6.0):
        out = []
        for k in range(1, n - 2):
            if np.isnan(m[k]).any() or np.isnan(m[k - 1]).any() or np.isnan(m[k + 1]).any():
                continue
            jump = np.abs(m[k] - m[k - 1]).max(); back = np.abs(m[k + 1] - m[k - 1]).max()
            if jump > tol and back < jump * 0.4:
                out.append((k, t[k], label + " bounce", jump, back))
        return out

    sus = spikes(body_diff, "body diff") + spikes(bg_diff, "background diff") + bounces(body_mean, "body colour") + bounces(bg_mean, "background colour")
    sus.sort()
    # merge neighbours into events
    events = []
    for s in sus:
        if events and s[0] - events[-1][-1][0] <= 2:
            events[-1].append(s)
        else:
            events.append([s])
    print(f"{video}: {n} frames, {len(events)} suspect event(s) (thresh x{thresh})")
    for ev in events:
        k0, k1 = ev[0][0], ev[-1][0]
        kinds = sorted(set(e[2] for e in ev)); peak = max(e[3] for e in ev)
        print(f"  frames {k0}-{k1}  t={t[k0]:6.2f}s  {', '.join(kinds)}  peak {peak:.1f}")

    fig, axs = plt.subplots(3, 1, figsize=(16, 9), sharex=True)
    axs[0].plot(t, body_diff, lw=0.8, label="body: mean |frame - prev|"); axs[0].plot(t, bg_diff, lw=0.8, label="background")
    axs[0].legend(); axs[0].set_ylabel("Δ / frame")
    axs[1].plot(t, body_mean[:, 2], c="r", lw=0.8); axs[1].plot(t, body_mean[:, 1], c="g", lw=0.8); axs[1].plot(t, body_mean[:, 0], c="b", lw=0.8)
    axs[1].set_ylabel("body mean RGB")
    axs[2].plot(t, area, lw=0.8); axs[2].set_ylabel("painted area (frac)"); axs[2].set_xlabel("time (s)")
    for ev in events:
        for ax in axs:
            ax.axvspan(t[ev[0][0]] - 0.05, t[ev[-1][0]] + 0.05, color="orange", alpha=0.35)
    fig.suptitle(f"{video} — {len(events)} suspect event(s)")
    fig.tight_layout(); fig.savefig(out, dpi=100)
    print("plot ->", out)
    sys.exit(1 if events else 0)


if __name__ == "__main__":
    main()
