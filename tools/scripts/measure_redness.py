"""
Measure skin redness over the chest through a pull-up set - a MEASURED signal to sit
beside the modelled muscle temperature.

    python measure_redness.py <video> <pose.npz> <analysis.json> <matte.npy> <out.json>

Why it might mean something: working muscle drives vasodilation in the skin above it, and
the skin reddens. Why it is only exploratory: a phone camera has auto-exposure and
auto-white-balance, the body moves into the door lintel's shadow at the top of every rep,
and the chest is partly hair. Two controls are applied:

  * every sample is taken at the BOTTOM of a rep (the dead hang), where the pose, the
    distance to the camera and the lighting are as close to identical as this clip offers;
  * redness is reported relative to a fixed patch of the wall in the same frame, so a shift
    in exposure or white balance moves both and cancels.

The index is (R - G) / (R + G) over the chest skin, x1000. It rises with erythema and is
insensitive to overall brightness, which is what we want when the camera keeps changing it.
"""
import sys, json
import numpy as np
import cv2

L_SH, R_SH = 11, 12
L_HIP, R_HIP = 23, 24


def main():
    video, npz, ajson, matte, out = sys.argv[1:6]
    ref_frac = None; base_frames = None
    for a in sys.argv[6:]:
        if a.startswith("ref="):
            ref_frac = [float(x) for x in a[4:].split(",")]
        elif a.startswith("base="):
            base_frames = [int(x) for x in a[5:].split(",")]
    d = np.load(npz)
    W, H = int(d["width"]), int(d["height"])
    P = d["img"][:, :, :2] * np.array([W, H])
    A = json.load(open(ajson)); S = A["summary"]; atts = A["reps"]; sig = A["signals"]
    comp = np.load(matte, mmap_mode="r")
    cap = cv2.VideoCapture(video)

    # a fixed reference patch of wall: inside the doorway, above the shelf, never occupied
    # by the body (checked against the matte below).
    REF = (int(0.34 * W), int(0.20 * H), int(0.46 * W), int(0.27 * H))
    if ref_frac:      # set #3: the tile wall left of the doorway, never occupied
        REF = (int(ref_frac[0] * W), int(ref_frac[1] * H), int(ref_frac[2] * W), int(ref_frac[3] * H))

    def sample(fi):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(fi))
        ok, f = cap.read()
        if not ok:
            return None
        a = cv2.resize(np.asarray(comp[fi])[..., 0], (W, H), interpolation=cv2.INTER_LINEAR)
        clothes = cv2.resize(np.asarray(comp[fi])[..., 1], (W, H), interpolation=cv2.INTER_LINEAR)
        sh = (P[fi, L_SH] + P[fi, R_SH]) / 2
        hip = (P[fi, L_HIP] + P[fi, R_HIP]) / 2
        ax = hip - sh
        trunk = float(np.linalg.norm(ax))
        sw = float(np.linalg.norm(P[fi, L_SH] - P[fi, R_SH]))
        if trunk < 20 or sw < 20:
            return None
        u = ax / trunk
        nrm = np.array([-u[1], u[0]])
        # chest patch: upper third of the trunk, central 70 % of the shoulder width
        poly = []
        for s_, dd in ((0.10, -0.34), (0.10, 0.34), (0.42, 0.30), (0.42, -0.30)):
            poly.append(sh + s_ * trunk * u + dd * sw * nrm)
        m = np.zeros((H, W), np.uint8)
        cv2.fillPoly(m, [np.round(np.array(poly)).astype(np.int32)], 1)
        m = (m > 0) & (a > 200) & (clothes < 60)
        if m.sum() < 3000:
            return None
        px = f[m].astype(np.float32)
        r, g, b = px[:, 2], px[:, 1], px[:, 0]
        # drop the darkest and brightest deciles: hair, specular highlights, shadow edges
        lum = px.mean(1)
        lo, hi = np.percentile(lum, [12, 88])
        k = (lum > lo) & (lum < hi)
        r, g, b = r[k], g[k], b[k]
        idx = float(np.mean((r - g) / np.maximum(r + g, 1.0)) * 1000)
        ref = f[REF[1]:REF[3], REF[0]:REF[2]].astype(np.float32).reshape(-1, 3)
        rr, gg = ref[:, 2], ref[:, 1]
        ridx = float(np.mean((rr - gg) / np.maximum(rr + gg, 1.0)) * 1000)
        return dict(frame=int(fi), t=float(fi / S["fps"]), redness=idx, wall=ridx,
                    corrected=idx - ridx, lum=float(lum[k].mean()), px=int(k.sum()),
                    wall_lum=float(ref.mean()))

    # one sample per rep, at the dead hang after it, averaged over +-3 frames
    per_rep = []
    for a_ in atts:
        vals = [sample(fi) for fi in range(a_["f_bottom1"] - 3, a_["f_bottom1"] + 4)]
        vals = [v for v in vals if v]
        if not vals:
            continue
        per_rep.append(dict(
            rep=a_.get("rep"), t=float(np.mean([v["t"] for v in vals])),
            redness=float(np.mean([v["redness"] for v in vals])),
            wall=float(np.mean([v["wall"] for v in vals])),
            corrected=float(np.mean([v["corrected"] for v in vals])),
            lum=float(np.mean([v["lum"] for v in vals])),
            wall_lum=float(np.mean([v["wall_lum"] for v in vals])),
            sd=float(np.std([v["corrected"] for v in vals]))))
    # a baseline from the standing frames before the set, same treatment
    b0, b1 = (base_frames if base_frames else (sig["grab0"] + 30, sig["load0"] - 10))
    base = [sample(fi) for fi in range(b0, b1, 8)]
    base = [v for v in base if v]
    cap.release()

    res = dict(per_rep=per_rep,
               baseline=dict(corrected=float(np.mean([v["corrected"] for v in base])) if base else None,
                             redness=float(np.mean([v["redness"] for v in base])) if base else None,
                             n=len(base)),
               index="(R-G)/(R+G) x 1000 over chest skin, minus the same index on a fixed wall patch",
               ref_patch=REF)
    # reject samples whose wall reference is occluded (he passes in front of it when he
    # drops off the bar): the control patch must look like the wall, or the sample is void.
    wall_med = float(np.median([p["wall"] for p in per_rep]))
    for p in per_rep:
        p["valid"] = bool(abs(p["wall"] - wall_med) < 12.0)
    good = [p for p in per_rep if p["valid"]]
    res_bad = [p["rep"] for p in per_rep if not p["valid"]]
    if res_bad:
        print("wall reference occluded, samples dropped:", res_bad)
    if len(good) > 3:
        x = np.array([p["t"] for p in good]); y = np.array([p["corrected"] for p in good])
        sl, ic = np.polyfit(x, y, 1)
        res["slope_per_s"] = float(sl); res["intercept"] = float(ic)
        res["rise_over_set"] = float(y[-1] - y[0])
        res["rise_from_standing"] = float(np.mean(y[-6:]) - res["baseline"]["corrected"])
        res["plateau"] = float(np.mean(y[-6:]))
        res["first_rep"] = float(y[0])
        res["r_with_time"] = float(np.corrcoef(x, y)[0, 1])
        res["dropped_samples"] = res_bad
        # correlation with the modelled lat temperature at the same frames
        sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
        import pullup_thermal as TH
        T = TH.integrate(A)["latissimus dorsi"]
        gset = {p["rep"] for p in good}
        lat = np.array([T[a_["f_bottom1"]] for a_ in atts if a_.get("rep") in gset])
        res["r_with_modelled_temp"] = float(np.corrcoef(lat, y)[0, 1])
        # wall control: if the wall index tracks the chest, it is the camera, not the skin
        wv = np.array([p["wall"] for p in good])
        res["r_wall_with_time"] = float(np.corrcoef(x, wv)[0, 1])
        res["wall_rise"] = float(wv[-1] - wv[0])
    json.dump(res, open(out, "w"), indent=1)

    print(f"baseline (standing) {res['baseline']['corrected']:.1f}")
    print(" rep    t     chest   wall   corrected   lum")
    for p in per_rep:
        print(f"{str(p['rep'] or 'fail'):>4s} {p['t']:6.1f}  {p['redness']:7.1f} {p['wall']:6.1f} "
              f"{p['corrected']:9.1f}  {p['lum']:5.0f}")
    if "slope_per_s" in res:
        print(f"\nrise over the set {res['rise_over_set']:+.1f} units, r with time "
              f"{res['r_with_time']:+.2f}; wall control rise {res['wall_rise']:+.1f} "
              f"(r {res['r_wall_with_time']:+.2f}); r with modelled temperature "
              f"{res['r_with_modelled_temp']:+.2f}")
    print("wrote", out)


if __name__ == "__main__":
    main()
