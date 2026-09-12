"""Simulate the marionette on the tracked fingertip pads: MuJoCo, strings as limited tendons.

    python puppet_sim.py <hand3d.npz> <out sim.npz> [release=41] [sub=16] [ref=120] [d_head=0.07] [drop=0.0]

What happens (hand/PLAN.md step 3, decisions 2 and 3):
  * The five pads (hand_to_3d.py, world metres, camera frame, gravity tilted by the measured roll)
    drive five mocap bodies; each string is a spatial tendon from a pad to its site on the puppet
    with range [0, L]: at length L it pulls, below it does nothing (slack). L is set at the reference
    frame (the stretched hand right after the snap-open) so that the puppet hanging upright with
    its head-top site d_head under the middle pad has every string just taut.
  * Before the release frame the puppet is in the fist: crumpled, behind the palm, not simulated.
    At the release frame's start it is placed there with the palm's velocity and let go: real free
    fall, the strings snap taut one after another, it unfolds, bounces and settles; from then on the
    fingers move it through the strings only. The release is the first frame the tracker sees the
    open hand (41 here; the fist starts opening at 40), because once the fingers are spread the
    pads are farther from the palm than the strings are long: a release at 42 was yanked at 75 x the
    weight instead of falling, and a release at 40 hung the crumpled figure under the still-closed
    fist for a frame (2026-09-11). WHERE it is released: the head string is the shortest (7 cm), so
    a figure crumpled behind the palm centre is already over-length on it once the hand is open; a
    figure lowered until the strings are slack hung below the fingertips before it ever dropped
    (12 cm under the palm, 2026-09-11). So the figure is released UPSIDE DOWN, its head-top site at
    the middle fingertip pad (`drop` metres below it, behind the finger) and its folded body up
    behind the fingers: every string is slack there, it tumbles out head first and the head and
    shoulder strings right it as it falls. The printed slack must be >= 0.
  * The reference frame for the string lengths is a typical mid-shot hand (120, "wide, drifting
    down" in hand/PLAN.md), not the snap-open (48): with the highest, widest hand as the reference
    every later pose was slacker and the settled figure hung from one shoulder string (2026-09-11).
    With 120 the load is shared in the long lolling phase and the snap-open lifts the figure.
  * Sub-frame states (sub per frame, default 16 = 480 Hz) are recorded for the renderer's motion blur
    (8 samples inside a 1/60 s shutter; 4 showed as stepped ghosts on the drop, 2026-09-11).
Sanity prints, before any frame is rendered (CLAUDE.md model code): the free-fall time until the
first string goes taut against sqrt(2h/g); the settled swing period against 2 pi sqrt(L/g); every
string tension >= 0; the sum of the taut tensions at the quietest hang = the puppet's weight; the
peak tension at the snap; the joint limits respected.
"""
import sys, json
import numpy as np
import mujoco
from scipy.interpolate import CubicSpline
import puppet_model as pm

FPS = 30.0


def main():
    hand_npz, out = sys.argv[1], sys.argv[2]
    kw = dict(a.split("=", 1) for a in sys.argv[3:])
    release = int(kw.get("release", 41)); sub = int(kw.get("sub", 16)); ref = int(kw.get("ref", pm.P["ref_frame"]))
    drop = float(kw.get("drop", 0.0))
    p = dict(pm.P); p["d_head"] = float(kw.get("d_head", p["d_head"]))
    h = np.load(hand_npz)
    pads, palm, roll = h["pads"], h["palm"], np.radians(h["roll"])   # (n,5,3), (n,3), (n,)
    n = pads.shape[0]; t_frames = np.arange(n) / FPS
    pad_spl = CubicSpline(t_frames, pads, axis=0); palm_spl = CubicSpline(t_frames, palm, axis=0)
    roll_spl = CubicSpline(t_frames, roll)

    model = mujoco.MjModel.from_xml_string(pm.build_xml(p)); data = mujoco.MjData(model)
    dt = model.opt.timestep
    pad_mid = [model.body(f"pad_{nm}").mocapid[0] for nm, _ in pm.STRINGS]
    site_id = [model.site(s).id for _, s in pm.STRINGS]
    ten_id = [model.tendon(f"str_{nm}").id for nm, _ in pm.STRINGS]
    root_adr = model.joint("root").qposadr[0]; root_vadr = model.joint("root").dofadr[0]
    mass = float(sum(model.body_mass[model.body(b).id] for b in pm.BODIES)); g = 9.81

    def set_pads(t):
        P = pad_spl(t)
        for k, mid in enumerate(pad_mid): data.mocap_pos[mid] = P[k]
        r = roll_spl(t)   # camera roll: gravity tilts in the image plane by the measured angle (under 1.2 deg here)
        model.opt.gravity[:] = (g * np.sin(r), 0.0, -g * np.cos(r))

    # --- string lengths at the reference frame: the puppet upright, head-top site d_head under the middle pad
    mujoco.mj_resetData(model, data); set_pads(ref / FPS)
    data.qpos[root_adr:root_adr + 7] = [0, 0.33, 0, 1, 0, 0, 0]; mujoco.mj_forward(model, data)
    head_site = data.site_xpos[model.site("s_head_top").id].copy(); pelvis0 = data.xpos[model.body("pelvis").id].copy()
    mid = pad_spl(ref / FPS)[2]
    target_pelvis = pelvis0 + (mid - head_site) + np.array([0, 0, -p["d_head"]])
    data.qpos[root_adr:root_adr + 3] = target_pelvis; mujoco.mj_forward(model, data)
    L = np.array([np.linalg.norm(data.site_xpos[s] - pad_spl(ref / FPS)[k]) for k, s in enumerate(site_id)])
    for k, tid in enumerate(ten_id): model.tendon_range[tid] = [0.0, L[k]]
    feet_z = min(data.geom_xpos[model.geom(f"g_foot_{sd}").id][2] for sd in "lr")
    print(f"puppet {p['height']*100:.0f} cm, {mass*1000:.1f} g; at the reference frame {ref} the head top is {p['d_head']*100:.1f} cm under the middle pad,"
          f" the feet at z = {feet_z*100:.1f} cm (frame bottom at the hand's depth: {-(h['H']/2)/h['f']*h['z_hand']*100:.1f} cm)")
    print("string lengths (cm): " + ", ".join(f"{nm} {L[k]*100:.1f}" for k, (nm, _) in enumerate(pm.STRINGS)))

    # --- the release state: crumpled at the palm centre with the palm's velocity
    t_rel = release / FPS
    mujoco.mj_resetData(model, data); set_pads(t_rel)
    pm.set_pose(model, data, pm.CRUMPLED, mujoco)
    data.qpos[root_adr:root_adr + 7] = [0, 0.33, 0, 0, 1, 0, 0]      # upside down: 180 deg about x (a somersault as it rights itself)
    mujoco.mj_forward(model, data)
    head_site = data.site_xpos[model.site("s_head_top").id].copy()
    mid_pad = pad_spl(t_rel)[2]
    data.qpos[root_adr:root_adr + 3] += mid_pad + np.array([0, 0.012, -drop]) - head_site   # the head top at the middle pad, 1.2 cm behind the finger
    mujoco.mj_forward(model, data)
    slack0 = L - data.ten_length[ten_id]
    P2 = pad_spl(t_rel + 2 / FPS); s2 = L - np.linalg.norm(data.site_xpos[site_id] - P2, axis=1) + 0.02
    data.qvel[root_vadr:root_vadr + 3] = palm_spl(t_rel, 1)
    com = data.subtree_com[model.body("pelvis").id]
    print(f"release: head top at the middle pad, the figure's centre {(com[2] - mid_pad[2])*100:+.1f} cm above it; slack at the release (cm, must all be >= 0 or the string yanks on frame 1): " + ", ".join(f"{nm} {slack0[k]*100:+.1f}" for k, (nm, _) in enumerate(pm.STRINGS)))
    if (slack0 < 0).any(): print("  WARNING: a string is over-length at the release; lower the puppet or lengthen the string")
    print("slack two frames later, pads at the open hand, figure 2 cm lower (cm): " + ", ".join(f"{nm} {s2[k]*100:+.1f}" for k, (nm, _) in enumerate(pm.STRINGS)))

    # --- run
    n_rec = n * sub
    xpos = np.zeros((n_rec, model.nbody, 3)); xquat = np.zeros((n_rec, model.nbody, 4))
    qpos = np.zeros((n_rec, model.nq)); ten_len = np.zeros((n_rec, 5)); ten_force = np.zeros((n_rec, 5)); site_pos = np.zeros((n_rec, 5, 3)); pad_pos = np.zeros((n_rec, 5, 3))
    times = np.arange(n_rec) / (FPS * sub)
    rel_state = (data.qpos.copy(), data.qvel.copy())
    first_taut = None; peak_force = 0.0; peak_t = 0.0
    for r in range(n_rec):
        t = times[r]
        if t < t_rel:            # in the fist: hold the release state (rendered behind the hand matte, or not at all)
            data.qpos[:] = rel_state[0]; data.qvel[:] = 0; set_pads(t); mujoco.mj_forward(model, data)
        else:
            if t == times[r] and abs(t - t_rel) < 0.5 / (FPS * sub) and first_taut is None and r > 0:
                data.qpos[:] = rel_state[0]; data.qvel[:] = rel_state[1]; data.time = t
            t_next = times[r] + 1.0 / (FPS * sub)
            while data.time < t_next - 1e-9:
                set_pads(data.time)
                mujoco.mj_step(model, data)
                # tendon-limit constraint forces (one-sided, so >= 0 by construction; summed per tendon)
                f = np.zeros(5)
                for e in range(data.nefc):
                    if data.efc_type[e] == mujoco.mjtConstraint.mjCNSTR_LIMIT_TENDON:
                        k = ten_id.index(int(data.efc_id[e])); f[k] += data.efc_force[e]
                if first_taut is None and (f > 1e-4).any():
                    first_taut = (data.time, int(np.argmax(f)))
                if f.max() > peak_force: peak_force, peak_t = float(f.max()), float(data.time)
            ten_force[r] = f
        xpos[r] = data.xpos; xquat[r] = data.xquat; ten_len[r] = data.ten_length[ten_id]; qpos[r] = data.qpos
        site_pos[r] = data.site_xpos[site_id]; pad_pos[r] = data.mocap_pos[pad_mid]
        if r % (30 * sub) == 0: print(f"  t={t:.2f}s", flush=True)

    # --- the checks
    taut = ten_len >= L - 5e-4
    if first_taut:
        t_ft, k_ft = first_taut
        d_fall = slack0[k_ft]      # the string that went taut first fell its own slack (straight down, roughly)
        print(f"free fall: the {pm.STRINGS[k_ft][0]} string went taut {t_ft - t_rel:.3f} s after the release; sqrt(2h/g) for its {d_fall*100:.1f} cm of slack = {np.sqrt(2*max(d_fall,0)/g):.3f} s (the body also unfolds and swings, so the string reaches length a little early)")
    print(f"peak string tension {peak_force:.3f} N at t={peak_t:.2f}s (frame {peak_t*FPS:.1f}); the puppet's weight is {mass*g:.3f} N -> the snap is {peak_force/(mass*g):.1f} x the weight")
    print(f"tension minimum over the whole run: {ten_force.min():.4f} N (must be >= 0)")
    # quietest hang: the record in frames 90-160 with the lowest pelvis speed
    pel = model.body("pelvis").id
    v = np.linalg.norm(np.diff(xpos[:, pel], axis=0), axis=1) * FPS * sub
    lo, hi = 90 * sub, 160 * sub
    q = lo + int(np.argmin(v[lo:hi]))
    w = ten_force[max(q - sub, 0):q + sub].mean(0)
    print(f"quietest hang at frame {q/sub:.1f}: pelvis speed {v[q]*100:.1f} cm/s; taut strings {[pm.STRINGS[k][0] for k in range(5) if taut[q, k]]}; "
          f"sum of tensions {w.sum():.3f} N vs weight {mass*g:.3f} N (ratio {w.sum()/(mass*g):.2f}); per string N: " + ", ".join(f"{pm.STRINGS[k][0]} {w[k]:.3f}" for k in range(5)))
    # swing period: zero crossings of the pelvis x about its running mean, frames 60-160
    comx = np.average(xpos[:, 1:12, 0], axis=1, weights=model.body_mass[1:12])
    seg = comx[60 * sub:160 * sub]; seg = seg - seg.mean()
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))); freqs = np.fft.rfftfreq(len(seg), 1.0 / (FPS * sub))
    band = (freqs > 0.4) & (freqs < 4.0); fpk = freqs[band][np.argmax(spec[band])]
    com_z = np.average(xpos[q, 1:12, 2], weights=model.body_mass[1:12]); Lp = pad_pos[q, :, 2].mean() - com_z
    print(f"dominant sway of the centre of mass (x, frames 60-160, 0.4-4 Hz): period {1/fpk:.2f} s; 2 pi sqrt(L/g) with L = pads-to-COM {Lp*100:.1f} cm: {2*np.pi*np.sqrt(Lp/g):.2f} s (the fingers drive it too, so a match within ~30 % is the expectation)")
    # joint limits: MuJoCo enforces them softly; report the worst hinge overshoot
    worst = 0.0
    for j in range(model.njnt):
        if model.jnt_limited[j] and model.jnt_type[j] == mujoco.mjtJoint.mjJNT_HINGE:
            q = qpos[:, model.jnt_qposadr[j]]; lo_, hi_ = model.jnt_range[j]
            worst = max(worst, float(np.degrees(max(lo_ - q.min(), q.max() - hi_, 0))))
    print(f"worst hinge overshoot past its limit: {worst:.1f} deg")
    print(f"max speed of any body over the run: {np.linalg.norm(np.diff(xpos[:, 1:12], axis=0), axis=2).max() * FPS * sub:.2f} m/s")
    # where the figure is in the frame, per phase (for the composition check)
    f_px, cx, cy = float(h["f"]), float(h["cx"]), float(h["cy"])
    def to_px(X): return np.stack([cx + f_px * X[..., 0] / X[..., 1], cy - f_px * X[..., 2] / X[..., 1]], -1)
    feet = np.minimum(to_px(xpos[:, model.body("shank_l").id])[:, 1], to_px(xpos[:, model.body("shank_r").id])[:, 1])
    print(f"lowest shank origin in the frame (px, of {int(h['H'])}): {feet.max():.0f} at frame {np.argmax(feet)/sub:.1f}; head top at the reference frame: {to_px(site_pos[ref*sub, 2])[1]:.0f} px")
    np.savez_compressed(out, xpos=xpos, xquat=xquat, qpos=qpos, ten_len=ten_len, ten_force=ten_force, taut=taut, site_pos=site_pos, pad_pos=pad_pos,
                        times=times, L=L, sub=sub, release=release, ref=ref, mass=mass, body_names=np.array([model.body(i).name for i in range(model.nbody)]),
                        params=json.dumps({k: (v if not isinstance(v, dict) else v) for k, v in p.items()}))
    print("wrote", out)


if __name__ == "__main__":
    main()
