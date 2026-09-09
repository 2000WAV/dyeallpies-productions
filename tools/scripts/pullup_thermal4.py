"""
Muscle model, version 4 (set #3, 2026-09-08, evening): the heat map driven by the mechanics
of the rep, not by a phase table.

Version 3 gave every muscle a fixed share of the heat (%MVIC x mass) and a per-frame
"activation" read from a table (PULL 1.0, HOLD 0.85, LOWER 0.65, HANG 0.35) scaled by the
pull speed. It could not show a muscle contracting and relaxing inside a rep, and it could not
show a late rep costing more than an early one for the same output. Dennis asked for both
(2026-09-08). This module replaces the table with a chain that is standard in biomechanics:

  1. INVERSE DYNAMICS in the rectified bar plane. The hand force is what the body weighs plus
     what it accelerates: F(t) = m_lift (g + a_y(t)), split over the two arms. Each joint's
     moment is that force times its lever: the horizontal distance from the vertical line
     through the hand to the elbow (from the forearm's foreshortening, see elbow_lever) and to
     the shoulder (measured across, assumed depth behind the bar plane).
  2. FORCE SHARING between the muscles that cross the joint: the Crowninshield & Brand 1981
     static optimisation, minimise sum (F_i / F_max,i)^p subject to sum r_i F_i = M, p = 3 as
     in the paper, which has the closed form a_i = M (r_i F_max,i)^(1/(p-1)) / sum_k (r_k
     F_max,k)^(p/(p-1)) for the activation of every agonist (antagonists get co-contraction). F_max = specific tension 50 N/cm2 x PCSA (the arm26 OpenSim model in the
     archive for the elbow, PCSA tables for the shoulder); moment arms from Murray 1995 (elbow,
     as a function of the elbow angle) and Ackland 2008 (shoulder).
  3. FORCE-VELOCITY: the activation a muscle needs for a force is F / (F_max f_v(v)); a
     shortening muscle (the pull) can give less force per unit activation than a lengthening
     one (the lowering), Hill 1938. This is why the concentric costs more than the eccentric
     - it falls out of the physics instead of being a table entry (Dickie 2017 measured it).
  4. ACTIVATION DYNAMICS: da/dt = (u - a) / tau, tau = 15 ms turning on, 50 ms turning off
     (Thelen 2003, Winters 1995). Relaxation lags contraction; the map breathes with the rep.
  5. FATIGUE that compounds: the three-compartment model of Xia & Frey-Law 2008 (resting,
     active, fatigued motor-unit pools; fatigue rate F, recovery rate R per joint from Frey-Law,
     Looft & Heitsenrether 2012). The same rep late in the set recruits a larger fraction of the
     units that are still able to fire: the EFFECTIVE activation shown is a / (1 - M_F).
  6. METABOLIC HEAT per muscle from activation and contraction velocity (the structure of
     Umberger 2003: activation/maintenance heat plus a shortening term), calibrated so the set
     total equals the energy budget the analysis already reports (work / 22 % efficiency,
     eccentric at 35 %, isometric hang cost) - the numbers on the card do not change.
  7. TEMPERATURE: the same heat balance as v3, C dT/dt = q - k(t) dT with C = 3.6 kJ/kg/K and
     blood-borne removal ramping to 42 W/K/kg (Gonzalez-Alonso 2000). Never falls in a set.

What the video shows: COLOUR = modelled temperature (slow, accumulates), BRIGHTNESS =
effective activation (fast, contracts and relaxes, and climbs through the set as the fatigued
pool grows). Muscles that do not cross a joint we can see (scapular stabilisers, core, legs)
follow the lat's activation at their published EMG ratio (Youdas 2010, Tucker 2011, Dinunzio
2018), as in v3. The formulation and every assumption is written out in pullup/MUSCLE-MODEL.md.

IT IS A MODEL, NOT A MEASUREMENT. The moments come from the video; the muscle forces, the
activations and the temperatures are inferred.
"""
import numpy as np
import cv2
from pullup_thermal3 import (MUSCLES, GRIP_MUSCLES, POSTURAL, PAINTED, muscle_masses, heat_shares,
                             frame_powers, C_MUSCLE, K_BLOOD, TAU_PERFUSION, GRIP_SHARE_OF_ISO,
                             POSTURAL_SHARE_OF_ISO, ETA_CONC, ECC_COST, HOLZBAUR_SCALE)

G = 9.81
SIGMA = 50.0                      # N/cm2 specific tension (Holzbaur 2005 upper-limb model convention)
SHARE_P = 3.0                     # Crowninshield & Brand 1981: minimise the sum of muscle stress CUBED
TAU_ACT, TAU_DEACT = 0.015, 0.050  # s, Thelen 2003 (10-15 ms on, 40-60 ms off)
V_MAX_LOPT = 10.0                 # optimal fibre lengths per second (arm26 default)
HILL_A = 0.25                     # a/F0 of the Hill hyperbola
ECC_PLATEAU = 1.6                 # eccentric force plateau relative to isometric
D_SH_HANG, D_SH_TOP = 0.04, 0.20  # m, glenohumeral joint behind the bar plane at the hang / at the top. ASSUMED:
                                  # the arm hangs plumb under the hand (4 cm); at the top the chin is 8 cm behind
                                  # the bar (the chin verdict) and the shoulder a further ~12 cm back
COCONTRACTION = 0.12              # antagonist (triceps) drive as a fraction of the flexor drive (Youdas: ~15 %MVIC)
GRIP_AT_HANG = 0.60               # forearm flexor activation holding body weight (estimate, v3)

# elbow flexors, ONE arm: F_max (N), peak moment arm (m), optimal fibre length (m), source
ELBOW_FLEXORS = {
    "biceps brachii":  (1060.0, 0.047, 0.120, "arm26.osim BIClong 624 + BICshort 436 N (CC BY); moment arm Murray 1995"),
    "brachialis":      (987.0,  0.026, 0.086, "arm26.osim BRA 987 N; Murray 1995"),
    "brachioradialis": (261.0,  0.075, 0.170, "Holzbaur 2005 model BRD (from memory, agrees with PCSA 5 cm2 x 50); Murray 1995"),
}
# shoulder adductors / extensors, ONE side: F_max (N), moment arm (m) at high elevation, l_opt (m)
SHOULDER_ADDUCTORS = {
    "latissimus dorsi": (1100.0, 0.035, 0.25, "PCSA 22.0 cm2 (An 1981, in data/anatomy-pcsa-volume.csv) x 50 N/cm2; Ackland 2008 moment arm"),
    "teres major":      (425.0,  0.025, 0.16, "Holzbaur 2005 TMAJ 425 N (from memory; PCSA ~8.5 cm2); Ackland 2008"),
    "pectoralis major": (900.0,  0.025, 0.14, "sternocostal heads, PCSA ~18 cm2 x 50; adducts above 90 deg elevation, Ackland 2008"),
    "posterior deltoid": (260.0, 0.015, 0.14, "Holzbaur 2005 DELT3 260 N (from memory); Ackland 2008"),
    "triceps":          (800.0,  0.015, 0.134, "arm26 TRIlong 799 N; long head at the shoulder, Ackland 2008"),
}
# activation as a ratio of the lat's, for muscles with no visible lever (Youdas 2010 / Tucker 2011 ratios)
STABILISER_RATIO = {"infraspinatus": 0.60, "trapezius": 0.42, "upper trapezius": 0.50, "serratus anterior": 0.21,
                    "middle deltoid": 0.36, "external oblique": 0.27, "rectus abdominis": 0.16, "erector spinae": 0.32}
POSTURAL_ACT = {"hip flexors": 0.18, "quadriceps": 0.08, "hamstrings": 0.06, "gluteus maximus": 0.08, "calves": 0.04}
# three-compartment fatigue (Xia & Frey-Law 2008), F and R in 1/s per joint (Frey-Law et al. 2012;
# values entered from memory of that paper - verify before quoting them; only their ORDER matters here)
FATIGUE = {"elbow": (0.00912, 0.00094), "shoulder": (0.00589, 0.00058), "grip": (0.00980, 0.00091),
           "trunk": (0.00589, 0.00058), "leg": (0.00589, 0.00058)}
JOINT_OF = {}
for m in ELBOW_FLEXORS: JOINT_OF[m] = "elbow"
for m in SHOULDER_ADDUCTORS: JOINT_OF[m] = "shoulder"
for m in GRIP_MUSCLES: JOINT_OF.setdefault(m, "grip")
for m in STABILISER_RATIO: JOINT_OF.setdefault(m, "shoulder" if m not in ("external oblique", "rectus abdominis", "erector spinae") else "trunk")
for m in POSTURAL: JOINT_OF[m] = "leg"
L_D = L_R = 10.0                  # 1/s, the controller gains of the fatigue model
HEAT_SHORTEN, HEAT_LENGTHEN = 1.2, 0.3   # shortening / lengthening heat relative to the activation term

L_SH, R_SH, L_EL, R_EL, L_WR, R_WR, L_HIP, R_HIP = 11, 12, 13, 14, 15, 16, 23, 24
_CACHE = {}


def _smooth(x, n=5):
    return np.convolve(x, np.ones(n) / n, mode="same")


def moment_arm_shape(theta_deg):
    """Elbow-flexor moment arm relative to its peak, vs elbow flexion (0 = straight). A smooth
    hump after Murray, Delp & Buchanan 1995: about a third of the peak at full extension, the
    peak near 90-100 deg, falling again past 120 deg."""
    th = np.clip(theta_deg, 0, 145)
    return 0.30 + 0.70 * np.sin(np.radians(th) * (90.0 / 85.0))


def f_v(v_norm):
    """Hill force-velocity factor. v_norm = v / v_max, + = shortening."""
    v = np.clip(v_norm, -1.0, 0.98)
    conc = (1 - v) / (1 + v / HILL_A)
    ecc = 1 + (ECC_PLATEAU - 1) * (-v) / (0.08 + (-v))
    return np.where(v >= 0, conc, ecc)


def kinematics(analysis, P):
    """Per-frame, per-arm levers (m), joint angles and rates, from the landmarks in the rectified
    plane. Returns a dict of arrays; 'ok' marks frames where the arm geometry is sane."""
    S = analysis["summary"]; sig = analysis["signals"]
    fps = S["fps"]; ppm = S["px_per_m"]
    Ht = np.array(S["H_total"], float)
    N = len(P)
    pts = P.reshape(-1, 1, 2).astype(np.float64)
    R = cv2.perspectiveTransform(pts, Ht).reshape(N, -1, 2)
    phase = np.array(sig["phase"], dtype=object)
    on_bar = np.isin(phase, ["HANG", "PULL", "HOLD", "LOWER", "LOADING"])
    height = np.clip(np.array(sig["height_pct"], float), 0, 110) / 100
    out = dict(on_bar=on_bar, height=height)
    hang_frames = np.where(phase == "HANG")[0]
    hang_frames = hang_frames[hang_frames < analysis["reps"][0]["f_start"]] if len(hang_frames) else hang_frames
    for side, (sh, el, wr) in dict(l=(L_SH, L_EL, L_WR), r=(R_SH, R_EL, R_WR)).items():
        fore = (R[:, wr] - R[:, el]) / ppm; upper = (R[:, el] - R[:, sh]) / ppm
        L_img = np.linalg.norm(fore, axis=1)
        L_true = float(np.median(L_img[hang_frames])) if len(hang_frames) > 5 else float(np.percentile(L_img, 95))
        # lever about the elbow for a vertical force through the hand = the forearm's horizontal
        # extent = sqrt(L^2 - dy^2): what the picture cannot see (depth) is what the foreshortening
        # took away, so the vertical component alone fixes the horizontal one
        dy = fore[:, 1]; dx = np.abs(fore[:, 0])
        lever_el = np.sqrt(np.maximum(L_true ** 2 - dy ** 2, dx ** 2))
        d_sh = D_SH_HANG + (D_SH_TOP - D_SH_HANG) * height
        dx_hs = np.abs((R[:, wr, 0] - R[:, sh, 0]) / ppm)
        lever_sh = np.sqrt(dx_hs ** 2 + d_sh ** 2)
        ang3 = np.array(sig["elbow_" + side], float)          # 3D elbow angle, 180 = straight
        theta = _smooth(np.clip(180.0 - np.nan_to_num(ang3, nan=160.0), 0, 150))
        omega_el = np.radians(np.gradient(theta)) * fps          # rad/s, + = flexing
        trunk = (R[:, L_HIP] + R[:, R_HIP]) / 2 - (R[:, L_SH] + R[:, R_SH]) / 2
        cosang = np.einsum("ij,ij->i", upper, -trunk) / (np.linalg.norm(upper, axis=1) * np.linalg.norm(trunk, axis=1) + 1e-6)
        elev = _smooth(np.degrees(np.arccos(np.clip(cosang, -1, 1))))   # upper arm vs the trunk axis, 180 = overhead
        omega_sh = -np.radians(np.gradient(elev)) * fps          # + = adducting (arm coming down toward the trunk)
        out[side] = dict(lever_el=lever_el, lever_sh=lever_sh, theta=theta, omega_el=_smooth(omega_el),
                         elev=elev, omega_sh=_smooth(omega_sh), L_fore=L_true)
    vy = np.array(sig["vy_m"], float)
    ay = _smooth(np.gradient(_smooth(vy)) * fps, 7)
    m_lift = S.get("lifted_mass_kg") or S["mass_kg"] * 0.956
    F_hand = np.where(on_bar, 0.5 * m_lift * np.clip(G + ay, 0, None), 0.0)   # N, per arm
    out["F_hand"] = F_hand; out["ay"] = ay; out["m_lift"] = m_lift
    return out


def required_activation(analysis, P):
    """Step 1-3: moments, force sharing, force-velocity -> required activation u (0..1+) per
    muscle (both arms averaged), plus the moments for the report."""
    K = kinematics(analysis, P)
    N = len(K["F_hand"])
    u = {m: np.zeros(N) for m in MUSCLES}
    M_el = np.zeros(N); M_sh = np.zeros(N)
    for side in ("l", "r"):
        k = K[side]; F = K["F_hand"]
        Mel = F * k["lever_el"]; Msh = F * k["lever_sh"]
        M_el += 0.5 * Mel; M_sh += 0.5 * Msh
        # elbow flexors
        shape = moment_arm_shape(k["theta"])
        r = {m: v[1] * shape for m, v in ELBOW_FLEXORS.items()}
        denom = sum((r[m] * ELBOW_FLEXORS[m][0]) ** (SHARE_P / (SHARE_P - 1)) for m in ELBOW_FLEXORS) + 1e-9
        for m, (Fmax, r_pk, lopt, _) in ELBOW_FLEXORS.items():
            Fi = Mel * (r[m] * Fmax) ** (1 / (SHARE_P - 1)) / denom * Fmax
            vn = r[m] * k["omega_el"] / (V_MAX_LOPT * lopt)       # shortening when flexing
            u[m] += 0.5 * Fi / (Fmax * f_v(vn))
        # shoulder adductors / extensors
        denom = sum((v[1] * v[0]) ** (SHARE_P / (SHARE_P - 1)) for v in SHOULDER_ADDUCTORS.values())
        for m, (Fmax, r_m, lopt, _) in SHOULDER_ADDUCTORS.items():
            Fi = Msh * (r_m * Fmax) ** (1 / (SHARE_P - 1)) / denom * Fmax
            vn = r_m * k["omega_sh"] / (V_MAX_LOPT * lopt)
            u[m] += 0.5 * Fi / (Fmax * f_v(vn))
    # the triceps also co-contracts at the elbow
    u["triceps"] = np.maximum(u["triceps"], COCONTRACTION * u["biceps brachii"])
    # grip: scales with the hand force
    grip = GRIP_AT_HANG * K["F_hand"] / (0.5 * K["m_lift"] * G)
    u["forearm flexors"] = grip
    u["forearm extensors"] = grip * 35.0 / 60.0
    # muscles without a visible lever follow the lats at their EMG ratio
    lat = u["latissimus dorsi"]
    for m, ratio in STABILISER_RATIO.items():
        u[m] = ratio * lat
    # Park & Yoo 2013: lat -> trapezius shift as the shoulder comes down at the top
    sig = analysis["signals"]; phase = np.array(sig["phase"], dtype=object)
    hold = _smooth(np.array([ph == "HOLD" for ph in phase], float))
    u["latissimus dorsi"] = u["latissimus dorsi"] * (1 - 0.15 * hold)
    u["trapezius"] = u["trapezius"] + 0.15 * hold * lat
    u["upper trapezius"] = u["upper trapezius"] + 0.10 * hold * lat
    # Dinunzio 2018: core rises with hip motion, not pull effort
    sway = np.zeros(N)
    for rp in analysis["reps"]:
        sway[rp["f_start"]:rp["f_end"] + 1] = rp.get("hip_sway_cm", 4.0)
    kip = np.clip((sway - 4.0) / 8.0, 0, 1)
    u["rectus abdominis"] = u["rectus abdominis"] + 0.6 * kip * lat
    u["external oblique"] = u["external oblique"] + 0.4 * kip * lat
    for m, a0 in POSTURAL_ACT.items():
        u[m] = a0 * K["on_bar"]
    for m in u:
        u[m] = np.clip(np.nan_to_num(u[m]), 0, 1.5)
    return u, dict(M_el=M_el, M_sh=M_sh, K=K)


def model(analysis, P, fps=None):
    """Steps 4-7 on top of required_activation. Cached per analysis object."""
    key = id(analysis)
    if key in _CACHE:
        return _CACHE[key]
    S = analysis["summary"]; fps = fps or S["fps"]; dt = 1.0 / fps
    u, extra = required_activation(analysis, P)
    K = extra["K"]; N = len(K["F_hand"])
    mass = muscle_masses()
    # 4. activation dynamics
    a = {m: np.zeros(N) for m in MUSCLES}
    for m in MUSCLES:
        cur = 0.0
        um = np.clip(u[m], 0, 1)
        for i in range(N):
            tau = TAU_ACT if um[i] > cur else TAU_DEACT
            cur += (um[i] - cur) * (1 - np.exp(-dt / tau))
            a[m][i] = cur
    # 5. fatigue: three compartments per muscle, target load = activation
    MF = {m: np.zeros(N) for m in MUSCLES}; MA = {m: np.zeros(N) for m in MUSCLES}
    for m in MUSCLES:
        Fr, Rr = FATIGUE[JOINT_OF.get(m, "shoulder")]
        mr, ma, mf = 1.0, 0.0, 0.0
        for i in range(N):
            TL = a[m][i]
            if ma < TL:
                C = L_D * min(TL - ma, mr)
            else:
                C = L_R * (TL - ma)
            dma = C - Fr * ma; dmf = Fr * ma - Rr * mf; dmr = -C + Rr * mf
            ma += dma * dt; mf += dmf * dt; mr += dmr * dt
            ma = max(ma, 0.0); mf = max(mf, 0.0); mr = max(mr, 0.0)
            tot = ma + mf + mr
            ma, mf, mr = ma / tot, mf / tot, mr / tot
            MA[m][i] = ma; MF[m][i] = mf
    a_eff = {m: np.clip(a[m] / np.maximum(1 - MF[m], 0.2), 0, 1) for m in MUSCLES}
    # 6. heat: activation/maintenance + shortening term, calibrated to the energy budget
    vnorm = {m: np.zeros(N) for m in MUSCLES}
    for side in ("l", "r"):
        k = K[side]
        for m, (Fmax, r_pk, lopt, _) in ELBOW_FLEXORS.items():
            vnorm[m] += 0.5 * r_pk * moment_arm_shape(k["theta"]) * k["omega_el"] / (V_MAX_LOPT * lopt)
        for m, (Fmax, r_m, lopt, _) in SHOULDER_ADDUCTORS.items():
            vnorm[m] += 0.5 * r_m * k["omega_sh"] / (V_MAX_LOPT * lopt)
    raw = {}
    for m in MUSCLES:
        vn = np.clip(vnorm[m], -1, 1)
        raw[m] = mass[m] * a[m] * (1 + HEAT_SHORTEN * np.maximum(vn, 0) + HEAT_LENGTHEN * np.maximum(-vn, 0))
    P_work, P_iso, P_mech = frame_powers(analysis, fps)
    grip_mass = sum(mass[m] for m in GRIP_MUSCLES)
    budget = P_work.sum() + P_iso.sum() * (GRIP_SHARE_OF_ISO + POSTURAL_SHARE_OF_ISO)   # W-frames
    raw_tot = sum(raw[m].sum() for m in MUSCLES) + 1e-9
    kcal_scale = budget / raw_tot
    q = {m: raw[m] * kcal_scale for m in MUSCLES}                 # W per muscle per frame
    # 7. temperature
    T = {m: np.zeros(N) for m in MUSCLES}
    t_on = 0.0; cur = {m: 0.0 for m in MUSCLES}
    for i in range(N):
        if P_work[i] > 0 or P_iso[i] > 0:
            t_on += dt
        perf = 1.0 - np.exp(-t_on / TAU_PERFUSION)
        for m in MUSCLES:
            kk = K_BLOOD * mass[m] * perf
            cur[m] += (q[m][i] - kk * cur[m]) / (C_MUSCLE * mass[m]) * dt
            cur[m] = max(cur[m], 0.0)
            T[m][i] = cur[m]
    out = dict(u=u, a=a, a_eff=a_eff, MF=MF, MA=MA, T=T, q=q, M_el=extra["M_el"], M_sh=extra["M_sh"], K=K,
               heat_scale=kcal_scale, budget_kj=float(budget / fps / 1000))
    _CACHE[key] = out
    return out


# ---- the v3 interface, so the atlas and renderer can swap the module in ----
def integrate(analysis, P=None, fps=None):
    if P is None:
        raise ValueError("pullup_thermal4.integrate needs the landmarks: integrate(A, P=P)")
    return model(analysis, P, fps)["T"]


def activation(analysis, P=None, fps=None):
    if P is None:
        raise ValueError("pullup_thermal4.activation needs the landmarks: activation(A, P=P)")
    return model(analysis, P, fps)["a_eff"]


def summarise(analysis, T=None, P=None):
    from pullup_thermal3 import summarise as s3
    out = s3(analysis, T)
    if P is None:
        return out
    Mo = model(analysis, P); sig = analysis["signals"]; phase = np.array(sig["phase"], dtype=object)
    S = analysis["summary"]; fps = S["fps"]
    val = {}
    for m in MUSCLES:
        row = {}
        for ph in ("PULL", "HOLD", "LOWER", "HANG"):
            sel = phase == ph
            row[ph] = float(Mo["u"][m][sel].mean()) if sel.any() else 0.0
        row["fatigued_end"] = float(Mo["MF"][m][-1])
        row["a_eff_pull_first"] = float(Mo["a_eff"][m][analysis["reps"][0]["f_start"]:analysis["reps"][0]["f_top"]].mean())
        row["a_eff_pull_last"] = float(Mo["a_eff"][m][analysis["reps"][-1]["f_start"]:analysis["reps"][-1]["f_top"]].mean())
        val[m] = row
    out["v4"] = dict(
        validation=val,
        peak_elbow_moment_nm=float(Mo["M_el"].max()), peak_shoulder_moment_nm=float(Mo["M_sh"].max()),
        hang_elbow_moment_nm=float(np.median(Mo["M_el"][phase == "HANG"])) if (phase == "HANG").any() else 0.0,
        hang_shoulder_moment_nm=float(np.median(Mo["M_sh"][phase == "HANG"])) if (phase == "HANG").any() else 0.0,
        forearm_true_m=dict(l=Mo["K"]["l"]["L_fore"], r=Mo["K"]["r"]["L_fore"]),
        heat_budget_kj=Mo["budget_kj"], heat_scale_w_per_kg=Mo["heat_scale"],
        params=dict(sigma=SIGMA, tau_act=TAU_ACT, tau_deact=TAU_DEACT, v_max_lopt=V_MAX_LOPT, hill_a=HILL_A,
                    ecc_plateau=ECC_PLATEAU, d_sh_hang=D_SH_HANG, d_sh_top=D_SH_TOP, cocontraction=COCONTRACTION,
                    grip_at_hang=GRIP_AT_HANG, fatigue=FATIGUE, heat_shorten=HEAT_SHORTEN, heat_lengthen=HEAT_LENGTHEN),
    )
    return out


if __name__ == "__main__":
    import sys, json
    A = json.load(open(sys.argv[1]))
    d = np.load(sys.argv[2]); img = d["img"]; W, H = int(d["width"]), int(d["height"])
    P = img[:, :, :2] * np.array([W, H])
    Mo = model(A, P)
    s = summarise(A, Mo["T"], P)
    v4 = s["v4"]
    print(f"forearm (true, from the hang) L {v4['forearm_true_m']['l']*100:.1f} cm  R {v4['forearm_true_m']['r']*100:.1f} cm")
    print(f"elbow moment: hang {v4['hang_elbow_moment_nm']:.0f} N m, peak {v4['peak_elbow_moment_nm']:.0f} N m;  "
          f"shoulder: hang {v4['hang_shoulder_moment_nm']:.0f}, peak {v4['peak_shoulder_moment_nm']:.0f} N m")
    print(f"heat budget {v4['heat_budget_kj']:.1f} kJ; total heat in v3 terms {s['total_heat_kj']:.1f} kJ")
    print(f"{'muscle':20s} {'PULL':>5s} {'HOLD':>5s} {'LOWER':>5s} {'HANG':>5s} | {'fat.end':>7s} {'eff 1st':>7s} {'eff last':>8s} | dT C  (Youdas %MVIC)")
    for m in sorted(MUSCLES, key=lambda m: -s["muscles"][m]["delta_T_C"]):
        r = v4["validation"][m]
        print(f"{m:20s} {r['PULL']:5.2f} {r['HOLD']:5.2f} {r['LOWER']:5.2f} {r['HANG']:5.2f} | {r['fatigued_end']:7.3f} "
              f"{r['a_eff_pull_first']:7.2f} {r['a_eff_pull_last']:8.2f} | +{s['muscles'][m]['delta_T_C']:.2f}  ({MUSCLES[m][0]})")
