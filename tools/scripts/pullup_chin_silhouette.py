"""
Chin height from the SILHOUETTE, for a low camera where the head goes behind the lintel.

    python pullup_chin_silhouette.py <analysis.json> <matte.npy> <out.json> [strip=out.jpg] [win=15]

Landmark models invent a face when the head is hidden (MediaPipe visibility stays 1.0, YOLO's
nose confidence can stay high), so the chin witness here is the person's alpha matte (RVM):
in a window around every rep top, take the silhouette between the lintel line and the
shoulder line at the grip centre, measure its width row by row, find the neck (the narrowest
rows) and the jaw (where the width flares above the neck). Three outcomes per frame:

  hidden   the rows just under the lintel are neck-wide -> the whole head is above the lintel,
           so the chin is at least (lintel - bar) above the bar, at any depth;
  chin     the width flares below the lintel -> the flare row is the chin; its height vs the
           bar is measured in the rectified plane (in-plane number, depth caveat applies);
  none     no usable silhouette (face far below the bar, or the matte is empty there).

Writes per-rep: frames hidden, chin-above-bar time, the lowest measured chin gap while the
head was partly visible on the way up/down, and draws a proof strip.
"""
import sys, json
import numpy as np
import cv2


def main():
    ajson, mpath, out = sys.argv[1:4]
    strip = None; win = 15
    for a in sys.argv[4:]:
        if a.startswith("strip="): strip = a[6:]
        elif a.startswith("win="): win = int(a[4:])
    A = json.load(open(ajson)); S = A["summary"]; sig = A["signals"]
    M = np.load(mpath, mmap_mode="r")
    N, hs, ws, _ = M.shape
    W = 1080; H = 1920; sc = ws / W
    px_per_m = S["px_per_m"]; fps = S["fps"]
    Ht = np.array(S["H_total"])
    bar = (S["bar_slope"], S["bar_intercept"]); lin = (S["lintel_slope"], S["lintel_intercept"])
    lintel_gap_cm = S["technique"]["lintel_gap_cm"]
    sh_y_img = np.array(sig["sh_y_img"])
    sh_x = np.array(sig["sh_x"])          # rectified; use the image-space grip centre instead
    d = None
    res = []
    tiles = []
    for r in A["reps"]:
        f0, f1 = max(r["f_start"], r["f_top"] - win), min(r["f_end"], r["f_top"] + win)
        per = []
        for f in range(f0, f1 + 1):
            a = np.asarray(M[f, :, :, 0], dtype=np.float32) / 255.0
            # grip centre x in image space: the widest alpha run on the bar row
            yb = int(round((bar[0] * (W / 2) + bar[1]) * sc))
            yl = int(round((lin[0] * (W / 2) + lin[1]) * sc))
            ysh = int(round(sh_y_img[f] * sc))
            if ysh <= yl + 6:
                per.append(dict(f=f, state="none")); continue
            band = a[yl:ysh, :]
            cols = np.where(band.max(0) > 0.5)[0]
            if len(cols) < 5:
                per.append(dict(f=f, state="none")); continue
            xc = int(np.median(cols))
            widths = []
            for y in range(yl, ysh):
                row = a[y] > 0.5
                if not row[xc]:
                    # nearest run to xc
                    idx = np.where(row)[0]
                    if len(idx) == 0:
                        widths.append(0); continue
                    xc2 = idx[np.argmin(np.abs(idx - xc))]
                else:
                    xc2 = xc
                l = xc2
                while l > 0 and row[l - 1]: l -= 1
                rr = xc2
                while rr < ws - 1 and row[rr + 1]: rr += 1
                widths.append(rr - l + 1)
            wd = np.array(widths, float)
            if len(wd) < 12:
                per.append(dict(f=f, state="none")); continue
            # ignore 4 rows of matte feathering under the lintel and above the shoulders
            core = wd[4:-4]
            neck_i = int(np.argmin(core)) + 4; neck_w = float(wd[neck_i])
            top_w = float(np.median(wd[4:10]))
            if neck_w <= 0:
                per.append(dict(f=f, state="none")); continue
            if top_w < 1.18 * neck_w and neck_i < 0.6 * len(wd):
                per.append(dict(f=f, state="hidden", neck_w=neck_w / sc, top_w=top_w / sc, xc=xc / sc))
            else:
                # walk up from the neck minimum until the width flares: that row is the jaw/chin
                j = neck_i
                while j > 4 and wd[j - 1] < 1.15 * neck_w:
                    j -= 1
                chin_y_img = (yl + j) / sc
                p = cv2.perspectiveTransform(np.array([[[xc / sc, chin_y_img]]], float), Ht).reshape(2)
                gap_cm = (S["bar_y_rect"] - p[1]) / px_per_m * 100
                per.append(dict(f=f, state="chin", gap_cm=float(gap_cm), neck_w=neck_w / sc, top_w=top_w / sc,
                                chin_y_img=float(chin_y_img), xc=xc / sc))
        hid = [p for p in per if p["state"] == "hidden"]
        seen = [p for p in per if p["state"] == "chin"]
        above = [p for p in seen if p["gap_cm"] > 0]
        t_above = (len(hid) + len(above)) / fps
        best_seen = max((p["gap_cm"] for p in seen), default=None)
        rec = dict(rep=r["rep"], n=r["n"], f_top=r["f_top"], frames_hidden=len(hid), t_hidden=len(hid) / fps,
                   t_chin_above_bar=t_above, chin_max_seen_cm=best_seen,
                   chin_bound_cm=lintel_gap_cm if hid else None,
                   verdict=("above" if hid or (best_seen is not None and best_seen >= 1.5) else
                            "at" if best_seen is not None and best_seen >= -1.5 else "short"),
                   per_frame=per)
        res.append(rec)
        print(f"attempt {r['n']:2d} rep {r['rep']}: hidden {len(hid):2d} frames ({len(hid)/fps:.2f} s), chin seen on {len(seen):2d}, "
              f"max seen gap {best_seen if best_seen is None else round(best_seen,1)} cm, above-bar time {t_above:.2f} s -> {rec['verdict']}")
        if strip:
            cap = d or cv2.VideoCapture(sys.argv[4].split("=")[1] if False else "pullup/work3/master.mp4"); d = cap
            cap.set(cv2.CAP_PROP_POS_FRAMES, r["f_top"]); okf, fr = cap.read()
            a = cv2.resize(np.asarray(M[r["f_top"], :, :, 0]), (W, H)) > 127
            edge = cv2.morphologyEx(a.astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0
            fr[edge] = (0, 255, 255)
            for (sl, ic, col) in ((bar, "bar", (0, 0, 255)), (lin, "lintel", (255, 0, 255))):
                cv2.line(fr, (0, int(sl[1])), (W, int(sl[0] * W + sl[1])), col, 2)
            pt = next((p for p in per if p["f"] == r["f_top"]), None)
            if pt and pt["state"] == "chin":
                cv2.circle(fr, (int(pt["xc"]), int(pt["chin_y_img"])), 8, (0, 255, 0), 3)
            crop = fr[150:650, 380:1000].copy()
            cv2.putText(crop, f"#{r['n']} {rec['verdict']} {'hidden' if hid else ''}", (8, 36), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            tiles.append(cv2.resize(crop, (372, 300)))
    json.dump(res, open(out, "w"), indent=1)
    if strip and tiles:
        rows = [np.hstack(tiles[i:i + 6]) for i in range(0, len(tiles), 6)]
        rows = [rw if rw.shape[1] == rows[0].shape[1] else np.hstack([rw, np.zeros((300, rows[0].shape[1] - rw.shape[1], 3), np.uint8)]) for rw in rows]
        cv2.imwrite(strip, np.vstack(rows))
        print("strip ->", strip)


if __name__ == "__main__":
    main()
