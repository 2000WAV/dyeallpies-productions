"""
Muscle model for the push-up (2026-09-09): the pull-up model's chain (pullup_thermal4, v4.3) with
the push-up's levers, muscles and evidence. Same physics, different joints:

  1. INVERSE DYNAMICS. The hands carry a measured fraction of body weight (Eckel et al. 2017,
     isometric force plate, 16 men: 71.95 % at the top with the arms locked, 76.70 % at the bottom
     with the upper arms parallel; references/pushup-science/02-*.md section 1), interpolated with
     the shoulder height and multiplied by (g + a_com)/g from the video; the analysis' own moment
     balance about the toes (de Leva segment masses on the reconstructed body) is printed beside it
     as the check (77 / 82 % on this set). The force is vertical through each hand. Joint moments:
        M_elbow    = F/2 x lever_el   (horizontal wrist-to-elbow distance, from the reconstructed elbow)
        M_shoulder = F/2 x lever_sh   (horizontal wrist-to-shoulder distance)
        M_wrist    = F/2 x WRIST_LEVER (the ground force acts at the heel of the hand, ahead of the joint)
     Both levers come from the 3D reconstruction (pushup_recon.py): the shoulders on their rays with
     the hips (width scale) and the rigid trunk fixing the depth, the wrists on the floor, the elbow
     on the circle the two arm lengths allow, placed by the measured flare.
  2. FORCE SHARING (Crowninshield & Brand 1981, p = 3) at each joint among the muscles that make the
     moment: elbow EXTENSORS (triceps long / lateral / medial, anconeus), shoulder FLEXORS / HORIZONTAL
     ADDUCTORS (pectoralis major in three compartments, anterior deltoid, coracobrachialis) and the
     WRIST EXTENSORS. F_max = 50 N/cm2 x PCSA from Holzbaur, Murray & Delp 2005 Table 1 (archived
     extract) and the arm26 OpenSim model; moment arms: triceps 2.3 cm (Murray, Buchanan & Delp 2000,
     archived), the shoulder arms ASSUMED within Kuechle et al. 1997's ranking (pectoralis major the
     largest horizontal-flexion arm at 90 deg elevation, then the anterior deltoid) and the anterior
     deltoid's CALIBRATED to the EMG ratio anterior deltoid / pectoralis = 0.9 (Snarr & Esco 2013 0.93,
     Calatayud et al. 2014 0.89; 01-*.md section 4). The athlete factor 1.2 as in the pull-up model.
  3. FORCE-VELOCITY (Hill 1938), 4. ACTIVATION DYNAMICS (Thelen 2003), 5. THREE-COMPARTMENT FATIGUE
     (Xia & Frey-Law 2008; rates per joint from Frey-Law, Looft & Heitsman 2012 Table 1, archived in
     the pull-up archive; Looft 2018 rest multiplier when the target load is under 2 %), 6. HEAT
     (Umberger 2003 structure) calibrated to the set's energy budget, 7. TEMPERATURE (Gonzalez-Alonso
     2000): all as in pullup_thermal4, functions imported from it.
  8. COLOUR = the effort index of v4.3: 0.9 x the non-resting share of the motor-unit pool (active +
     fatigued) + 0.2 x temperature / 1.5 C, clipped at 1.

MUSCLES WITHOUT A VISIBLE LEVER follow a prime mover at their EMG ratio, each ratio from ONE study
(01-*.md section 4, "never divide across studies"): serratus anterior 0.77 x pec (Youdas 2010),
rising toward the pec at lock-out (San Juan 2015: SA peaks by 55 deg of elbow extension); upper
trapezius 0.20 x pec (Calatayud 2014: 5.9 over 29.6); latissimus dorsi 0.25 x pec (Batbayar 2015's
push-up-plus row, the only number); biceps 0.12 x triceps (co-contraction, Alizadeh 2020 provisional);
rectus abdominis 0.22 and external oblique 0.14 of MVIC isometric through the plank (Tahani 2026,
Calatayud 2014), scaled by the measured hip sag; erector spinae 0.05, gluteus 0.06 (Tahani 2026
gluteus medius 5.2 %), quadriceps 0.12 (Calatayud 7.5 %, Borreani 20.6 %), hip flexors 0.10 and calves
0.05 (ASSUMED, no push-up EMG found). The forearm flexors (grip) 0.15 (assumed).

ENERGY: the analysis' own budget (work / 22 %, eccentric 35 %, plank cost at 3 METs) gives 0.48 kcal a
rep on this set; the one direct measurement, Nakagata, Yamada & Naito 2022 (indirect calorimetry, PMC
9042340; 03-*.md section 4.1), gives 0.77 +- 0.20 kcal a rep. The heat budget uses Nakagata's constant
(a measurement beats an assumed efficiency); the calorie line on screen says "about 0.8 kcal a rep".

VALIDATION printed by __main__: the whole-rep ORDERING (triceps / pec within 0.6-1.2, the four
standard-push-up studies; anterior deltoid / pec 0.85-0.95; serratus / pec ~0.77; upper trapezius the
lowest), the CAPACITY at each joint against Holzbaur 2007's norms (elbow extension 60.5 N m for young
men) and Donkers 1993's measured push-up elbow torque (23 N m = 56 % of MVIC), and the FATIGUE test.

IT IS A MODEL, NOT A MEASUREMENT.
"""
import numpy as np
import pullup_thermal3 as T3
import pullup_thermal4 as T4
from pullup_thermal4 import (G, SIGMA, SHARE_P, V_MAX_LOPT, TAU_ACT, TAU_DEACT, FATIGUE, REST_MULT, REST_TL,
                             L_D, L_R, HEAT_SHORTEN, HEAT_LENGTHEN, EFFORT_FAST, EFFORT_SLOW, T_REF, ATHLETE, f_v)
from pullup_thermal3 import C_MUSCLE, K_BLOOD, TAU_PERFUSION, ETA_CONC, ECC_COST, HOLZBAUR_SCALE, DENSITY

# ---- the hands' share of body weight: Eckel et al. 2017 (02-pushup-hand-force-and-joint-moments.md) ----
HAND_FRAC_TOP = 0.7195           # men, arms locked, isometric hold on a force plate
HAND_FRAC_BOTTOM = 0.7670        # men, upper arms parallel
SHOULDER_STRENGTH = 2.0          # CALIBRATED (2026-09-10): with the athlete factor alone the pec sat at 1.0 whole rep and its fatigued pool at 80 %,
                                 # i.e. failure by rep 15 (Frey-Law 2012 shoulder rates), while Dennis did 30 reps at -26 % speed; no norm for shoulder
                                 # horizontal flexion exists (Holzbaur 2007 measured abduction / adduction only; 02-*.md section 4). Ranked in PUSHUP-MODEL.md.
ELBOW_STRENGTH = ATHLETE          # the elbow keeps the pull-up model's athlete factor: Donkers 1993 measured 56 % of MVIC, the model gives 55 % (PUSH median)
LEVER_EL_MAX, LEVER_SH_MAX, A_COM_MAX = 0.30, 0.45, 8.0   # physical clips on the reconstructed levers (m) and the CoM acceleration (m/s2): a few frames outside the reps go wild
WRIST_LEVER = 0.02               # m, the ground force's centre of pressure ahead of the wrist joint (assumed, ranked)
SA_LOCKOUT_RISE = 0.30           # serratus: + this x pec as the elbow straightens past 120 deg (San Juan 2015, direction only)
CORE_SAG_GAIN = 0.10             # rectus / obliques rise by this per cm of measured hip sag (assumed, ranked)
KCAL_PER_REP_MEASURED = 0.77     # Nakagata 2022, kcal per push-up, indirect calorimetry (archived PDF)
# The effort index the colour shows (a display choice, rank 10 in PUSHUP-MODEL.md section 5). The pull-up's v4.3 weights were
# 0.9 fast / 0.2 slow; for the push-up (2026-09-10, after Dennis's screen recording of set #1) the slow part, the modelled
# temperature, carries more weight so the WHOLE body drifts from blue to red through the set the way set #1's fatigue base did,
# while the fast part still contracts and relaxes inside each rep. Temperature is real accumulation (Gonzalez-Alonso 2000).
E_FAST, E_SLOW = 0.80, 0.45

# ---- muscles: (%MVIC in a standard push-up from the archive, volume cm3 both sides, source, scaled_with_holzbaur) ----
# Volumes: the pull-up table's Holzbaur 2007 values (pullup_thermal3.MUSCLES) reused for the same muscles.
MUSCLES = {
    "pectoralis major":   (85,  2 * 290.0, "Youdas 2010 95-105, Snarr 2013 64, Freeman 2006 61 %MVIC; Holzbaur 2007 volume"),
    "triceps":            (80,  2 * 372.0, "Youdas 2010 73-109, Snarr 2013 74, Freeman 66, Cogley 101 %MVIC; Holzbaur 2007"),
    "anterior deltoid":   (70,  2 * 126.8, "Snarr 2013 59, Borreani 2015 79 %MVIC; Holzbaur deltoid volume / 3"),
    "middle deltoid":     (25,  2 * 126.8, "ESTIMATE (no push-up EMG found for the middle head); Holzbaur / 3"),
    "posterior deltoid":  (16,  2 * 126.8, "Youdas 2010 11-21 %MVIC; Holzbaur / 3"),
    "serratus anterior":  (60,  2 * 90.0,  "Youdas 2010 67-87, Borreani 29, Tahani 24 %MVIC; volume is an estimate"),
    "upper trapezius":    (6,   2 * 60.0,  "Calatayud 2014 5.9, Borreani 5.8 %MVIC (the lowest measured); volume estimate"),
    "trapezius":          (10,  2 * 190.0, "lower / middle fibres, ESTIMATE (not measured in a standard push-up); volume estimate"),
    "latissimus dorsi":   (17,  2 * 262.3, "Batbayar 2015 16.6 %MVC (push-up plus, the only number); Holzbaur 2007"),
    "biceps brachii":     (12,  2 * 143.7, "Alizadeh 2020 (provisional), a minor antagonist; Holzbaur 2007"),
    "brachialis":         (10,  2 * 143.7, "assumed = biceps; Holzbaur 2007"),
    "brachioradialis":    (10,  2 * 65.1,  "ESTIMATE; Holzbaur"),
    "forearm flexors":    (15,  2 * 238.0, "grip, ESTIMATE (the hand is flat, not gripping); Holzbaur FDS+FDP+FCR+FCU"),
    "forearm extensors":  (45,  2 * 150.0, "wrist extensors holding the wrist under load, ESTIMATE from the wrist moment below; volume estimate"),
    "rectus abdominis":   (22,  200.0,     "Tahani 2026 21.9, Calatayud 2014 23.9 %MVIC"),
    "external oblique":   (14,  2 * 110.0, "Tahani 2026 13.8 %MVIC; volume estimate"),
    "erector spinae":     (5,   2 * 400.0, "Calatayud 2.0, Tahani 6.6 %MVIC; on the back, not painted"),
    "hip flexors":        (10,  2 * 500.0, "ESTIMATE (no push-up EMG); iliopsoas + TFL holding the plank", False),
    "quadriceps":         (12,  2 * 1500.0, "rectus femoris: Calatayud 7.5, Borreani 20.6 %MVIC; the vasti NOT FOUND", False),
    "hamstrings":         (5,   2 * 950.0,  "ESTIMATE", False),
    "gluteus maximus":    (6,   2 * 850.0,  "Tahani 2026 gluteus medius 5.2 %MVIC; maximus NOT FOUND", False),
    "calves":             (5,   2 * 650.0,  "ESTIMATE (on the toes)", False),
}
GRIP_MUSCLES = ("forearm flexors", "brachioradialis", "forearm extensors")
POSTURAL = ("hip flexors", "quadriceps", "hamstrings", "gluteus maximus", "calves")
PAINTED = [m for m in MUSCLES if m not in ("erector spinae", "hamstrings", "gluteus maximus")]

# ---- the movers with a lever: (F_max N, moment arm m, optimal fibre length m, source) ----
ELBOW_EXTENSORS = {
    "triceps": (798.5 + 624.3 + 624.3, 0.023, 0.120, "arm26 / Holzbaur 2005: TRIlong 798.5 + TRIlat 624.3 + TRImed 624.3 N; arm 2.3 cm Murray 2000 (Table 2, combined heads); lopt 13.4 / 11.4 cm"),
}
ANCONEUS = (350.0, 0.012, 0.027)      # Holzbaur 2005 Table 1 anconeus 350 N, arm 1.2 cm: folded into the triceps region's demand
SHOULDER_FLEXORS = {
    "pectoralis major":  (364.4 + 515.4 + 390.5, 0.040, 0.14, "Holzbaur 2005 PMAJ1 364.4 + PMAJ2 515.4 + PMAJ3 390.5 N; horizontal-flexion arm 4.0 cm ASSUMED, the largest in Kuechle 1997's ranking"),
    "anterior deltoid":  (1142.6, 0.036, 0.098, "Holzbaur 2005 DELT1 1142.6 N; arm 3.6 cm CALIBRATED to ant. deltoid / pec = 0.9 (Snarr 0.93, Calatayud 0.89): the share ratio is sqrt(r F / r F)"),
    "middle deltoid":    (1142.6, 0.004, 0.108, "Holzbaur 2005 DELT2 1142.6 N; a small horizontal-adduction arm ASSUMED (its EMG is not measured in a push-up)"),
    "coracobrachialis":  (242.5, 0.020, 0.093, "Holzbaur 2005 CORB 242.5 N; arm 2.0 cm assumed"),
    "biceps brachii":    (624.3 + 435.6, 0.010, 0.116, "arm26 BIClong + BICshort; a small shoulder-flexion arm for the long head (assumed)"),
}
WRIST_EXTENSORS = {"forearm extensors": (600.0, 0.015, 0.06, "ECRL + ECRB + ECU, ~12 cm2 x 50 (Holzbaur 2005 order of magnitude); arm 1.5 cm assumed")}
# ratios to a prime mover for the muscles without a visible lever (one study each, 01-*.md section 4)
FOLLOW_PEC = {"serratus anterior": 0.77, "upper trapezius": 0.20, "trapezius": 0.25, "latissimus dorsi": 0.25, "posterior deltoid": 0.18}
FOLLOW_TRI = {"brachialis": 0.10, "brachioradialis": 0.12, "forearm flexors": 0.18}
ISO_CORE = {"rectus abdominis": 0.22, "external oblique": 0.14, "erector spinae": 0.05}
POSTURAL_ACT = {"hip flexors": 0.10, "quadriceps": 0.12, "hamstrings": 0.05, "gluteus maximus": 0.06, "calves": 0.05}
JOINT_OF = {m: "elbow" for m in ("triceps", "biceps brachii", "brachialis", "brachioradialis")}
JOINT_OF.update({m: "shoulder" for m in ("pectoralis major", "anterior deltoid", "middle deltoid", "posterior deltoid", "serratus anterior",
                                          "upper trapezius", "trapezius", "latissimus dorsi")})
JOINT_OF.update({m: "grip" for m in ("forearm flexors", "forearm extensors")})
JOINT_OF.update({m: "trunk" for m in ("rectus abdominis", "external oblique", "erector spinae")})
JOINT_OF.update({m: "leg" for m in POSTURAL})

_CACHE = {}


def _smooth(x, n=5):
    return np.convolve(x, np.ones(n) / n, mode="same")


def muscle_masses():
    out = {}
    for m, v in MUSCLES.items():
        scaled = v[3] if len(v) > 3 else True
        out[m] = v[1] * (HOLZBAUR_SCALE if scaled else 1.0) * DENSITY / 1000.0
    return out


def kinematics(analysis):
    """Per-frame levers and joint rates from the analysis JSON (metres, rad/s)."""
    S = analysis["summary"]; sig = analysis["signals"]; fps = S["fps"]
    N = len(sig["t"])
    phase = np.array(sig["phase"], dtype=object)
    on = np.isin(phase, ["PLANK", "LOWER", "BOTTOM", "PUSH"])
    h = np.clip(np.array(sig["height_pct"], float), 0, 110) / 100        # 0 = bottom, 1 = top
    # STEP 1a, the hand force: Eckel 2017's measured fractions interpolated with the height, times the
    # vertical acceleration of the body's centre of mass from the video (signals.a_com, m/s2)
    frac = HAND_FRAC_BOTTOM + (HAND_FRAC_TOP - HAND_FRAC_BOTTOM) * h
    a_com = np.clip(np.nan_to_num(np.array(sig["a_com"], float)), -A_COM_MAX, A_COM_MAX)
    F = np.where(on, S["mass_kg"] * np.clip(G + a_com, 0, None) * frac, 0.0)     # N, both hands
    out = dict(on=on, F=F, frac=frac, F_model=np.nan_to_num(np.array(sig["F_hand_n"], float)))
    for side in ("l", "r"):
        lever_el = np.clip(np.nan_to_num(np.array(sig["lever_el_" + side], float)), 0, LEVER_EL_MAX)
        lever_sh = np.clip(np.nan_to_num(np.array(sig["lever_sh_" + side], float)), 0, LEVER_SH_MAX)
        theta = np.clip(180.0 - np.nan_to_num(np.array(sig["elbow_" + side], float), nan=160.0), 0, 150)   # flexion, 0 = straight
        omega_el = np.radians(np.gradient(_smooth(theta))) * fps            # + = flexing (the lowering); the triceps SHORTEN when it falls
        # the upper arm's angle against the trunk axis (the shoulder's flexion angle), from the elbow tilt
        tilt = np.nan_to_num(np.array(sig["upper_tilt_" + side], float))
        omega_sh = np.radians(np.gradient(_smooth(tilt))) * fps
        out[side] = dict(lever_el=lever_el, lever_sh=lever_sh, theta=theta, omega_el=_smooth(omega_el), omega_sh=_smooth(omega_sh))
    return out


def required_activation(analysis):
    K = kinematics(analysis); N = len(K["F"])
    u = {m: np.zeros(N) for m in MUSCLES}
    M_el = np.zeros(N); M_sh = np.zeros(N); M_wr = np.zeros(N)
    for side in ("l", "r"):
        k = K[side]; F = 0.5 * K["F"]                                   # per hand
        Mel = F * k["lever_el"]; Msh = F * k["lever_sh"]; Mwr = F * WRIST_LEVER
        M_el += 0.5 * Mel; M_sh += 0.5 * Msh; M_wr += 0.5 * Mwr
        # STEP 2, elbow: the triceps (three heads, one arm) with the anconeus sharing at p = 3
        Fmax_t, r_t, lopt_t, _ = ELBOW_EXTENSORS["triceps"]; Fmax_a, r_a, lopt_a = ANCONEUS
        denom = (r_t * Fmax_t) ** 1.5 + (r_a * Fmax_a) ** 1.5
        Fi = Mel * (r_t * Fmax_t) ** 0.5 / denom * Fmax_t
        # STEP 3, force-velocity: the triceps shortens as the elbow extends (omega_el < 0 while pushing)
        vn = -r_t * k["omega_el"] / (V_MAX_LOPT * lopt_t)
        u["triceps"] += 0.5 * Fi / (ELBOW_STRENGTH * Fmax_t * f_v(vn))
        # shoulder: the flexors / horizontal adductors share Msh
        denom = sum((v[1] * v[0]) ** 1.5 for v in SHOULDER_FLEXORS.values())
        for m, (Fmax, r_m, lopt, _) in SHOULDER_FLEXORS.items():
            Fi = Msh * (r_m * Fmax) ** 0.5 / denom * Fmax
            vn = -r_m * k["omega_sh"] / (V_MAX_LOPT * lopt)             # shortening as the upper arm swings forward on the push
            key = m if m in u else None
            if key is not None:
                u[key] += 0.5 * Fi / (SHOULDER_STRENGTH * Fmax * f_v(vn))
        # the wrist extensors hold the wrist under the hand force
        Fmax_w, r_w, lopt_w, _ = WRIST_EXTENSORS["forearm extensors"]
        u["forearm extensors"] += 0.5 * (Mwr / r_w) / (ELBOW_STRENGTH * Fmax_w)
    pec = u["pectoralis major"]; tri = u["triceps"]
    for m, ratio in FOLLOW_PEC.items():
        u[m] = ratio * pec
    sig = analysis["signals"]
    # serratus rises toward the pec at lock-out (San Juan 2015: SA reaches its peak by 55 deg of elbow extension)
    th = 0.5 * (K["l"]["theta"] + K["r"]["theta"])
    lock = np.clip((60.0 - th) / 40.0, 0, 1)                         # 0 at 60 deg of flexion, 1 when straight
    u["serratus anterior"] = u["serratus anterior"] + SA_LOCKOUT_RISE * lock * pec
    for m, ratio in FOLLOW_TRI.items():
        u[m] = ratio * tri
    u["biceps brachii"] = np.maximum(u["biceps brachii"], 0.12 * tri)   # co-contraction (Alizadeh 2020, provisional)
    # core: isometric through the plank, rising with the measured hip sag
    sag = np.abs(np.nan_to_num(np.array(sig["hip_sag_cm"], float)))
    for m, a0 in ISO_CORE.items():
        u[m] = a0 * K["on"] * (1 + CORE_SAG_GAIN * sag)
    load = np.clip((G + np.nan_to_num(np.array(sig["a_com"], float))) / G, 0.5, 1.6)
    for m, a0 in POSTURAL_ACT.items():
        u[m] = a0 * K["on"] * load
    for m in u:
        u[m] = np.clip(np.nan_to_num(u[m]), 0, 1.5)
    return u, dict(M_el=M_el, M_sh=M_sh, M_wr=M_wr, K=K)


def frame_powers(analysis, fps=None):
    """Heat budget per frame, W: Nakagata 2022's measured 0.77 kcal per rep spread over each rep's time
    under tension, plus the plank cost between reps (the analysis' 3 MET figure)."""
    S = analysis["summary"]; sig = analysis["signals"]; fps = fps or S["fps"]
    N = len(sig["t"]); P = np.zeros(N)
    plank_w = S.get("plank_kcal_per_s", 0.0) * 4184.0
    on = np.isin(np.array(sig["phase"], dtype=object), ["PLANK", "LOWER", "BOTTOM", "PUSH"])
    P[on] = plank_w
    for r in analysis["reps"]:
        a0, b0 = r["f_start"], r["f_end"]
        P[a0:b0 + 1] += (KCAL_PER_REP_MEASURED * 4184.0 - plank_w * (b0 - a0 + 1) / fps) / ((b0 - a0 + 1) / fps)
    return P


def model(analysis, P_img=None, fps=None):
    key = id(analysis)
    if key in _CACHE:
        return _CACHE[key]
    S = analysis["summary"]; fps = fps or S["fps"]; dt = 1.0 / fps
    u, extra = required_activation(analysis)
    K = extra["K"]; N = len(K["F"]); mass = muscle_masses()
    # STEP 4, activation dynamics (Thelen 2003)
    a = {m: np.zeros(N) for m in MUSCLES}
    for m in MUSCLES:
        cur = 0.0; um = np.clip(u[m], 0, 1)
        for i in range(N):
            tau = TAU_ACT if um[i] > cur else TAU_DEACT
            cur += (um[i] - cur) * (1 - np.exp(-dt / tau)); a[m][i] = cur
    # STEP 5, three-compartment fatigue (Xia & Frey-Law 2008; rates Frey-Law 2012 Table 1; Looft 2018 rest multiplier)
    MF = {m: np.zeros(N) for m in MUSCLES}; MA = {m: np.zeros(N) for m in MUSCLES}
    for m in MUSCLES:
        joint = JOINT_OF.get(m, "shoulder"); Fr, Rr = FATIGUE[joint]; rr = REST_MULT[joint]
        mr, ma, mf = 1.0, 0.0, 0.0
        for i in range(N):
            TL = a[m][i]
            C = L_D * min(TL - ma, mr) if ma < TL else L_R * (TL - ma)
            R_now = Rr * rr if TL < REST_TL else Rr
            dma = C - Fr * ma; dmf = Fr * ma - R_now * mf; dmr = -C + R_now * mf
            ma = max(ma + dma * dt, 0.0); mf = max(mf + dmf * dt, 0.0); mr = max(mr + dmr * dt, 0.0)
            tot = ma + mf + mr; ma, mf, mr = ma / tot, mf / tot, mr / tot
            MA[m][i] = ma; MF[m][i] = mf
    a_eff = {m: np.clip(a[m] / np.maximum(1 - MF[m], 0.2), 0, 1) for m in MUSCLES}
    busy = {m: np.clip(MA[m] + MF[m], 0, 1) for m in MUSCLES}
    # STEP 6, heat (Umberger 2003 structure) calibrated to the measured budget
    vnorm = {m: np.zeros(N) for m in MUSCLES}
    for side in ("l", "r"):
        k = K[side]
        vnorm["triceps"] += 0.5 * (-ELBOW_EXTENSORS["triceps"][1] * k["omega_el"]) / (V_MAX_LOPT * ELBOW_EXTENSORS["triceps"][2])
        for m, (Fmax, r_m, lopt, _) in SHOULDER_FLEXORS.items():
            if m in vnorm:
                vnorm[m] += 0.5 * (-r_m * k["omega_sh"]) / (V_MAX_LOPT * lopt)
    raw = {}
    for m in MUSCLES:
        vn = np.clip(vnorm[m], -1, 1)
        raw[m] = mass[m] * a[m] * (1 + HEAT_SHORTEN * np.maximum(vn, 0) + HEAT_LENGTHEN * np.maximum(-vn, 0))
    P_heat = frame_powers(analysis, fps)
    budget = P_heat.sum()
    raw_tot = sum(raw[m].sum() for m in MUSCLES) + 1e-9
    kcal_scale = budget / raw_tot
    q = {m: raw[m] * kcal_scale for m in MUSCLES}
    # STEP 7, temperature
    T = {m: np.zeros(N) for m in MUSCLES}; t_on = 0.0; cur = {m: 0.0 for m in MUSCLES}
    for i in range(N):
        if P_heat[i] > 0:
            t_on += dt
        perf = 1.0 - np.exp(-t_on / TAU_PERFUSION)
        for m in MUSCLES:
            kk = K_BLOOD * mass[m] * perf
            cur[m] = max(cur[m] + (q[m][i] - kk * cur[m]) / (C_MUSCLE * mass[m]) * dt, 0.0); T[m][i] = cur[m]
    E = {m: np.clip(E_FAST * busy[m] + E_SLOW * np.minimum(T[m] / T_REF, 1.0), 0, 1) for m in MUSCLES}
    out = dict(u=u, a=a, a_eff=a_eff, busy=busy, MF=MF, MA=MA, T=T, q=q, E=E, M_el=extra["M_el"], M_sh=extra["M_sh"], M_wr=extra["M_wr"],
               K=K, heat_scale=kcal_scale, budget_kj=float(budget / fps / 1000))
    _CACHE[key] = out
    return out


def integrate(analysis, P=None, fps=None):
    return model(analysis, P, fps)["T"]


def activation(analysis, P=None, fps=None):
    return model(analysis, P, fps)["a_eff"]


def effort(analysis, P=None, fps=None):
    return model(analysis, P, fps)["E"]


def summarise(analysis, T=None, P=None):
    Mo = model(analysis, P); sig = analysis["signals"]; phase = np.array(sig["phase"], dtype=object)
    val = {}
    for m in MUSCLES:
        row = {ph: (float(Mo["u"][m][phase == ph].mean()) if (phase == ph).any() else 0.0) for ph in ("LOWER", "BOTTOM", "PUSH", "PLANK")}
        row["fatigued_end"] = float(Mo["MF"][m][-1]); row["delta_T_C"] = float(Mo["T"][m].max())
        val[m] = row
    return dict(validation=val, peak_elbow_moment_nm=float(Mo["M_el"].max()), peak_shoulder_moment_nm=float(Mo["M_sh"].max()),
                peak_wrist_moment_nm=float(Mo["M_wr"].max()), heat_budget_kj=Mo["budget_kj"], muscles={m: dict(delta_T_C=val[m]["delta_T_C"]) for m in MUSCLES})


if __name__ == "__main__":
    import sys, json
    A = json.load(open(sys.argv[1]))
    Mo = model(A); s = summarise(A)
    ph = np.array(A["signals"]["phase"], dtype=object); rep = np.isin(ph, ["LOWER", "BOTTOM", "PUSH"])
    print(f"hand force: Eckel 2017 fractions {HAND_FRAC_TOP:.2f} top / {HAND_FRAC_BOTTOM:.2f} bottom; the analysis' own moment balance "
          f"{A['summary']['hand_frac_top']:.2f} / {A['summary']['hand_frac_bottom']:.2f}; peak hand force {Mo['K']['F'].max():.0f} N ({Mo['K']['F'].max() / (A['summary']['mass_kg'] * G):.2f} BW)")
    print(f"moments per arm: elbow peak {s['peak_elbow_moment_nm']:.0f} N m (Donkers 1993 measured 23 N m = 56 % of MVIC; norm 60.5 N m, Holzbaur 2007); "
          f"shoulder peak {s['peak_shoulder_moment_nm']:.0f} N m (no push-up shoulder-moment measurement exists: 02-*.md section 4); wrist peak {s['peak_wrist_moment_nm']:.0f} N m (norm 14.0)")
    print(f"heat budget {s['heat_budget_kj']:.1f} kJ over the set (Nakagata 2022: {KCAL_PER_REP_MEASURED} kcal x {len(A['reps'])} reps); the analysis' own budget {A['summary']['set_kcal']:.1f} kcal")
    print(f"{'muscle':20s} {'LOWER':>5s} {'BOTTOM':>6s} {'PUSH':>5s} {'PLANK':>5s} | {'fat.end':>7s} | dT C   (archive %MVIC)")
    for m in sorted(MUSCLES, key=lambda m: -s["muscles"][m]["delta_T_C"]):
        r = s["validation"][m]
        print(f"{m:20s} {r['LOWER']:5.2f} {r['BOTTOM']:6.2f} {r['PUSH']:5.2f} {r['PLANK']:5.2f} | {r['fatigued_end']:7.3f} | +{r['delta_T_C']:.2f}  ({MUSCLES[m][0]})")
    U = Mo["u"]
    wr = {m: float(U[m][rep].mean()) for m in ("pectoralis major", "triceps", "anterior deltoid", "serratus anterior", "upper trapezius", "rectus abdominis", "erector spinae")}
    print("\nORDERING TEST, whole-rep required activation:", {m: round(v, 2) for m, v in wr.items()})
    print(f"  triceps / pec    = {wr['triceps'] / wr['pectoralis major']:.2f}   (four standard-push-up studies: 0.58-1.17, co-dominant; 01-*.md section 4)")
    print(f"  ant. deltoid/pec = {wr['anterior deltoid'] / wr['pectoralis major']:.2f}   (Snarr & Esco 2013 0.93, Calatayud 2014 0.89)")
    print(f"  serratus / pec   = {wr['serratus anterior'] / wr['pectoralis major']:.2f}   (Youdas 2010 0.77 whole rep, rising at lock-out)")
    print(f"  upper trap / pec = {wr['upper trapezius'] / wr['pectoralis major']:.2f}   (Calatayud 2014 0.20, the lowest of the girdle)")
    print(f"  peaks: pec {U['pectoralis major'].max():.2f}, triceps {U['triceps'].max():.2f}, ant. deltoid {U['anterior deltoid'].max():.2f}  (above 1 = demand over capacity, clipped)")
    cap_el = ELBOW_STRENGTH * (ELBOW_EXTENSORS["triceps"][0] * ELBOW_EXTENSORS["triceps"][1] + ANCONEUS[0] * ANCONEUS[1])
    cap_sh = SHOULDER_STRENGTH * sum(v[0] * v[1] for v in SHOULDER_FLEXORS.values())
    print(f"CAPACITY TEST: elbow extension {cap_el:.0f} N m vs demand peak {Mo['M_el'].max():.0f}, PUSH median {np.median(Mo['M_el'][ph == 'PUSH']):.0f} "
          f"(norm 60.5 N m at 90 deg, Holzbaur 2007; Donkers 1993: a push-up asks 56 % of it); shoulder {cap_sh:.0f} N m vs demand peak {Mo['M_sh'].max():.0f}, PUSH median {np.median(Mo['M_sh'][ph == 'PUSH']):.0f}")
    MFm = Mo["MF"]; Em = Mo["E"]; fps = A["summary"]["fps"]
    bots = [r_["f_bottom"] for r_ in A["reps"]]; tops = [r_["f_end"] for r_ in A["reps"]]
    for m in ("pectoralis major", "triceps", "anterior deltoid"):
        print(f"FATIGUE TEST {m}: M_F at the bottoms {np.round([MFm[m][b] * 100 for b in bots]).astype(int).tolist()} %; "
              f"colour at the top after each rep {np.round([Em[m][t_] * 100 for t_ in tops]).astype(int).tolist()} %")
    print(f"  measured: peak speed rep 1 -> last: {A['summary']['velocity_loss_pct']:+.0f} % (vs the fastest rep {A['summary']['velocity_loss_vs_fastest_pct']:.0f} %); hip sag {A['summary']['technique']['mean_hip_sag_cm']:.1f} cm mean")
    done = np.where(ph == "DONE")[0]
    if len(done):
        f0 = done[0]; f5 = min(f0 + int(5 * fps), len(ph) - 1)
        for m in ("pectoralis major", "triceps"):
            print(f"  release {m}: M_F {MFm[m][f0]*100:.1f} % -> {MFm[m][f5]*100:.1f} % {(f5 - f0) / fps:.1f} s later; colour {Em[m][f0]*100:.0f} -> {Em[m][f5]*100:.0f} %")
