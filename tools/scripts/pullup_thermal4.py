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
     Looft & Heitsman 2012, Table 1, in the archive since v4.3), with Looft, Herkert & Frey-Law
     2018's rest multiplier: recovery runs r times faster only while the muscle produces no
     force. Between reps nothing here relaxes (the hang keeps the grip and the shoulder loaded
     above the blood-flow occlusion threshold, Sadamoto 1983), so the fatigued pool M_F only
     grows until the bar is released. That is the mechanism Dennis described as one rep carrying
     heat into the next: PERIPHERAL FATIGUE WITH INCOMPLETE RECOVERY (Carroll, Taylor & Gandevia
     2017), carried in M_F (references/pullup-science/09-fatigue-recovery-and-residual.md).
  6. METABOLIC HEAT per muscle from activation and contraction velocity (the structure of
     Umberger 2003: activation/maintenance heat plus a shortening term), calibrated so the set
     total equals the energy budget the analysis already reports (work / 22 % efficiency,
     eccentric at 35 %, isometric hang cost) - the numbers on the card do not change.
  7. TEMPERATURE: the same heat balance as v3, C dT/dt = q - k(t) dT with C = 3.6 kJ/kg/K and
     blood-borne removal ramping to 42 W/K/kg (Gonzalez-Alonso 2000). Never falls in a set.

What the video shows (v4.1, 2026-09-09): COLOUR = the EFFORT INDEX, 0.9 x effective
activation + 0.2 x temperature / 1.5 C (clipped at 1), on a blue -> red scale. The fast part contracts and
relaxes inside every rep (the biceps peaks mid-pull, the lats at the top, both fall on the
lowering and drop to the grip-only hang) and climbs through the set as the fatigued pool
grows; the slow part is the floor that rises through the set and never falls. v4 coloured
by temperature alone and put the activation into brightness, which Dennis read as "only a
progressive increase in heat" - the temperature never falls, so nothing on screen relaxed.
Muscles that do not cross a joint we can see (scapular stabilisers, core, legs) follow the
lat's activation at their published EMG ratio (Youdas 2010, Tucker 2011, Dinunzio 2018), the
trapezius with its own drive at the start of the pull and the legs breathing with the vertical
acceleration. The formulation and every assumption is written out in pullup/MUSCLE-MODEL.md.

v4.2 (2026-09-09, the model review Dennis asked for after seeing the biceps' fatigue above the
lats' on the card): the shoulder's depth behind the bar is COMPUTED per frame from the elbow
angle and the measured segment lengths instead of assumed (4 -> 20 cm); the biceps carries the
pronated grip's smaller moment arm; the shoulder capacities and moment arms are taken from the
strength norms and Ackland 2008 in references/pullup-science/08-moment-arms-and-strength.md.
The review's ordering test (whole-rep lats / biceps against Youdas 2010 and Snarr 2017) and the
capacity check (sum r F_max per joint against the norms) are printed by __main__.

v4.3 (2026-09-09, evening; Dennis: "each rep should get hotter, and only when I let go should the
whole body slightly cool"): the from-memory fatigue rates were checked against Frey-Law, Looft &
Heitsman 2012 Table 1 (full text archived). The elbow's were right; the SHOULDER'S were the
table's ANKLE row (0.00589 / 0.00058 instead of 0.01820 / 0.00168), the grip's R was the pooled
row, the trunk's a copy. With the true rows the shoulder fatigues twice as fast as the elbow, so
the lats' pool now empties faster than the biceps', the reverse of what v4.2 said. Looft 2018's
rest multiplier r (15, grip 30) is added: recovery of M_F is r times faster while the target
load is zero, i.e. only after the release. COLOUR is now the NON-RESTING share of the pool,
M_A + M_F = 1 - M_R: M_A contracts and relaxes inside the rep, M_F is the "remaining heat" that
climbs rep by rep and starts to clear only when the hands open. The temperature floor stays.
FATIGUE TEST printed by __main__: the prime movers' fatigued pool at the last rep against the
measured speed loss, and the recovery in the seconds after release against Harris 1976's
phosphocreatine half-time (21-22 s: about 15 % back in 5 s, so "slightly" is the physics).

WHAT GOES IN (every number the model reads, and where it comes from)
  analysis.json  summary.fps, summary.px_per_m (scale in the rectified doorway plane, from the
                 standing stature), summary.H_total (image -> rectified plane homography),
                 summary.lifted_mass_kg (body mass minus forearms and hands, de Leva 1996),
                 summary.height_m; signals.phase (SETUP/HANG/PULL/HOLD/LOWER/DONE per frame),
                 signals.height_pct (shoulder height, 0 = hang, 100 = best top),
                 signals.vy_m (shoulder vertical speed, m/s, + up), signals.elbow_l / elbow_r
                 (MediaPipe 3D elbow angle, 180 = straight), signals.knee_l / knee_r (3D knee
                 angle), signals.hang0 (first frame with the hands on the bar); reps[].f_start,
                 f_top, f_end, hip_sway_cm.
  pose_mp.npz    image-space landmarks 11/12 shoulders, 13/14 elbows, 15/16 wrists, 23/24 hips
                 (MediaPipe Pose heavy), mapped through H_total before any length is taken.
  constants      each one below says where it comes from: a paper, a file in
                 references/pullup-science/, or "assumed" with its rank in MUSCLE-MODEL.md section 5.

WHAT COMES OUT  per muscle, per frame: required activation u, activation a (after the dynamics),
                fatigued fraction M_F, effective activation a_eff = a / (1 - M_F), heat q (W),
                temperature rise T (deg C), effort index E (the colour); per frame: elbow and
                shoulder moments, the hand force and the shoulder depth (K).

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
D_SH_HANG = 0.04                  # m, the FLOOR of the shoulder's depth behind the bar plane: the arm hangs plumb
                                  # under the hand at the dead hang and the joint centre sits ~4 cm behind the
                                  # knuckles (assumed; only matters at the hang). The depth itself is computed per
                                  # frame in kinematics() since v4.2; v4's assumed 4 -> 20 cm ramp is retired.
D_SH_MAX = 0.40                   # m, sanity clip on the computed depth (an arm is 63 cm long)
COCONTRACTION = 0.12              # antagonist (triceps) drive as a fraction of the flexor drive (Youdas: ~15 %MVIC)
GRIP_AT_HANG = 0.60               # forearm flexor activation holding body weight (estimate, v3)
# v4.1 (2026-09-09, after Dennis's review of the second pass) -------------------------------------
ATHLETE = 1.20                    # one strength factor for a resistance-trained man over the healthy young adults of
                                  # the norms (Holzbaur, Delp, Gold & Murray 2007, J Biomech 40:742, PMID 17250841:
                                  # elbow flexion MVC at 90 deg 79.5 +- 8.1 N m, shoulder adduction MVC 93.7 +- 11.3
                                  # N m, men, n = 5; abstracts/holzbaur2007-pmid17250841.txt). Trained men test
                                  # 15-25 % above untrained in isometric strength; 1.2 is the middle. ASSUMED, the
                                  # same at both joints on purpose (v4.1 had 1.25 at the elbow only, chosen to stop
                                  # the display clipping, which is not a reason). Ranked in MUSCLE-MODEL.md.
ELBOW_STRENGTH = ATHLETE          # elbow capacity check (printed by __main__): sum r F_max at 90 deg, pronated, = 83
                                  # N m x 1.2 = 99 N m against the 79.5 N m supinated norm; the peak demand here is
                                  # 79 N m, so the flexors sit near their limit mid-pull, as Youdas' 78-96 %MVIC says.
SHOULDER_STRENGTH = ATHLETE       # shoulder capacity check: sum r F_max over the extensors / adductors = 88 N m
                                  # (generic PCSA x 50 N/cm2 x the high-elevation arms below) x 1.2 = 105 N m,
                                  # against Holzbaur 2007's 93.7 N m adduction MVC at 60 deg abduction; no overhead
                                  # extension MVC dataset exists (08-moment-arms-and-strength.md, gap list). The
                                  # demand with the computed depth is 100-150 N m, so the lats sit AT or above their
                                  # capacity through the pull, which is what Youdas 2010 measured (117-130 %MVIC).
INIT_TRAP = 0.35                  # lower/middle trapezius drive added while the shoulder rises with the elbow still
                                  # near straight: scapular depression starts the pull before the elbow flexes
                                  # (Prinold & Bull 2016; Youdas 2010 lower trapezius). Fraction of full activation.
INIT_ELBOW_DEG = 35.0             # "arm still straight" = elbow flexion under this
INIT_PEC = 0.25                   # pectoralis major initiation drive, same window (Youdas 2010: "initiated by the lower
                                  # trapezius and pectoralis major"; 07-phase-resolved-emg.md)
PRONATION_BICEPS = 0.75           # biceps flexion moment arm with the forearm pronated, relative to supinated. The
                                  # DIRECTION is measured (Murray, Delp & Buchanan 1995, PMID 7775488: the biceps'
                                  # peak arm is larger supinated; its numeric ratio sits in an un-OCR'd scan, see
                                  # 08-moment-arms-and-strength.md); the MAGNITUDE is assumed. Kohn et al. 2018
                                  # (PMID 29333724) measured pronated elbow-flexion MVC 42 % below supinated, so
                                  # 0.75 is conservative. This is the chin-up / pull-up difference: Youdas 2010 has
                                  # the biceps at 96 %MVIC supinated and 78 pronated, the load shifting to the
                                  # brachialis (deep, invisible to surface EMG) and brachioradialis.
POSTURAL_BREATHES = True          # the legs hold the tuck against g + a_y: their drive scales with the vertical
                                  # acceleration instead of sitting at one constant for the whole set
EFFORT_FAST, EFFORT_SLOW = 0.90, 0.20   # the colour on screen: fast part = the NON-RESTING share of the motor-unit
                                        # pool, M_A + M_F (v4.3; M_A contracts and relaxes inside the rep, M_F is the
                                        # fatigue carried from rep to rep, recovering only after the release), slow
                                        # part = temperature / T_REF (the floor that rises through the set and
                                        # never falls). The two weights are a display choice, ranked in MUSCLE-MODEL.md.
T_REF = 1.5                       # deg C, the temperature that counts as "fully warm" for the slow part

# Elbow flexors, ONE arm: (F_max N, peak flexion moment arm m, optimal fibre length m, source).
# F_max = the maximal isometric forces of the arm26 OpenSim model (Holzbaur, Murray & Delp 2005, Ann
# Biomed Eng 33:829, PMID 16078622, CC BY copy in anatomy-assets/opensim-models/); peak moment arms
# measured on 10 cadaver specimens by Murray, Buchanan & Delp 2000 (J Biomech 33:943, PMID 10828324:
# brachioradialis 7.7, biceps 4.7, brachialis 2.6 cm; papers/murray2000-*.pdf); l_opt from arm26.
ELBOW_FLEXORS = {
    "biceps brachii":  (1060.0, 0.047, 0.120, "arm26 BIClong 624 + BICshort 436 N; arm 4.7 cm Murray 2000"),
    "brachialis":      (987.0,  0.026, 0.086, "arm26 BRA 987 N; arm 2.6 cm Murray 2000"),
    "brachioradialis": (261.0,  0.075, 0.170, "Holzbaur 2005 BRD 261 N; arm 7.7 cm Murray 2000"),
}
# Shoulder extensors / adductors that bring the arm down from overhead, ONE side: (F_max N, moment arm m
# at high elevation, l_opt m, source). F_max = PCSA x SIGMA (An et al. 1981 and Holzbaur 2005 PCSAs,
# data/anatomy-pcsa-volume.csv). The moment arms are the weak point: Ackland, Pak, Richardson & Pandy
# 2008 (J Anat 213:383, PMID 18691376) measured them on cadavers through elevation but the numbers sit
# behind a paywall (08-moment-arms-and-strength.md); their abstract gives the RANKING (teres major,
# latissimus dorsi and pectoralis major dominate adduction; teres major and posterior deltoid,
# extension), which these values respect, and the values themselves are ASSUMED (section 5).
SHOULDER_ADDUCTORS = {
    "latissimus dorsi": (1253.0, 0.045, 0.25, "Holzbaur 2005 LAT1+LAT2+LAT3 = 389+435+429 N (PMID 16078622; An 1981's PCSA 22 cm2 x 50 gives 1100); arm 4.5 cm ASSUMED: the largest adductor in Ackland 2008's ranking, and with it the summed shoulder capacity equals Holzbaur 2007's 93.7 N m adduction norm"),
    "teres major":      (425.0,  0.025, 0.16, "Holzbaur 2005 TMAJ 425 N; arm 2.5 cm assumed"),
    # The pec: only its lower sternocostal fibres extend / adduct from overhead (Ackland 2008's
    # abstract names exactly those; the clavicular head is a flexor there), so half the muscle's
    # 900 N, at a small arm. Both numbers are CALIBRATED so that the cubic sharing reproduces
    # Youdas 2010's pec / lats ratio (44 / 124 = 0.35) rather than predicted: with the whole pec at
    # 2.5 cm the model gave 0.86, which the EMG rules out. Disclosed in MUSCLE-MODEL.md section 5.
    "pectoralis major": (450.0,  0.015, 0.14, "lower sternocostal fibres, ~9 cm2 x 50; arm 1.5 cm; CALIBRATED to Youdas' pec/lats 0.35"),
    "posterior deltoid": (260.0, 0.015, 0.14, "Holzbaur 2005 DELT3 260 N; arm 1.5 cm assumed"),
    # The triceps' long head crosses the shoulder, but with a 1.5 cm arm and 800 N the cubic
    # sharing handed it 0.7 of full activation where Youdas 2010 measures 15 %MVIC over the rep:
    # from full elevation its extension arm is small and the muscle is at a poor length. Its
    # shoulder arm is set to zero (it stays in the set for the heat and the fatigue bookkeeping)
    # and the elbow co-contraction below is what drives it. CALIBRATED to the EMG, disclosed.
    "triceps":          (800.0,  0.000, 0.134, "arm26 TRIlong 799 N; shoulder arm 0: co-contraction only, calibrated to Youdas' 15 %MVIC"),
}
# Muscles with no lever the front camera can see follow the lats' activation at the ratio of their
# whole-rep %MVIC to the lats' 124 %MVIC (pullup_thermal3.MUSCLES, column 1, with its sources):
# infraspinatus 75/124 (Youdas 2010), lower/middle trapezius 52/124 (Youdas 2010), upper trapezius
# 62/124 (Tucker 2011, supine pull-up), serratus anterior 26/124 (Tucker 2011), middle deltoid 45/124
# (ESTIMATE, no pull-up EMG found), external oblique 33/124 (Youdas 2010), rectus abdominis 20/124
# (estimate; Dinunzio 2018 gives the kipping rise), erector spinae 40/124 (Youdas 2010).
STABILISER_RATIO = {"infraspinatus": 0.60, "trapezius": 0.42, "upper trapezius": 0.50, "serratus anterior": 0.21,
                    "middle deltoid": 0.36, "external oblique": 0.27, "rectus abdominis": 0.16, "erector spinae": 0.32}
# Legs and hips hold the tuck: whole-rep %MVIC / 100 from pullup_thermal3.MUSCLES (all ESTIMATES; Dinunzio 2018
# shows the hip flexors active in a strict pull-up and rising +26 %MVIC in a kip). Scaled by g + a_y per frame.
POSTURAL_ACT = {"hip flexors": 0.18, "quadriceps": 0.08, "hamstrings": 0.06, "gluteus maximus": 0.08, "calves": 0.04}
# three-compartment fatigue (Xia & Frey-Law 2008), F and R in 1/s per joint region, from Frey-Law,
# Looft & Heitsman 2012 (J Biomech 45:1803, PMID 22579259) TABLE 1, read from the archived full text
# papers/freylawlooft2012-3cc-endurance-times.xml (v4.3; before that the shoulder held the ankle's
# row and the grip the pooled R, both from memory, see the v4.3 note above). The legs take the KNEE
# row: the hip flexors and quadriceps hold the tuck (assumed mapping, ranked in MUSCLE-MODEL.md).
FATIGUE = {"elbow": (0.00912, 0.00094),      # Table 1, elbow
           "shoulder": (0.01820, 0.00168),   # Table 1, shoulder: F is 2.0 x the elbow's
           "grip": (0.00980, 0.00064),       # Table 1, hand/grip (F:R 15.3, the slowest to recover under load)
           "trunk": (0.00755, 0.00075),      # Table 1, trunk
           "leg": (0.01500, 0.00149)}        # Table 1, knee (ankle would be 0.00589 / 0.00058)
# rest multiplier r (Looft, Herkert & Frey-Law 2018, J Biomech 77:16, PMID 29960732, Table 4, archived
# as papers/looft2018-3cc-r-intermittent.xml): while the target load is zero, M_F recovers at R x r
# (reactive hyperaemia once the contraction stops occluding the muscle's blood flow). Fitted per joint
# against 63 intermittent-contraction studies: ankle, knee, elbow 15, hand/grip 30; the shoulder was
# not in that meta-analysis, so it takes the paper's "General (all)" 15, EXTRAPOLATED.
REST_MULT = {"elbow": 15.0, "shoulder": 15.0, "grip": 30.0, "trunk": 15.0, "leg": 15.0}
REST_TL = 0.02                    # "no force": target load under 2 % of full activation counts as rest. Looft 2018
                                  # switches at TL = 0 exactly; the activation dynamics here never reach 0 (the
                                  # deactivation is exponential), so a threshold is needed. ASSUMED; the only frames
                                  # it selects are after the release (the hang keeps every bar muscle far above it).
JOINT_OF = {}
for m in ELBOW_FLEXORS: JOINT_OF[m] = "elbow"
for m in SHOULDER_ADDUCTORS: JOINT_OF[m] = "shoulder"
for m in GRIP_MUSCLES: JOINT_OF.setdefault(m, "grip")
for m in STABILISER_RATIO: JOINT_OF.setdefault(m, "shoulder" if m not in ("external oblique", "rectus abdominis", "erector spinae") else "trunk")
for m in POSTURAL: JOINT_OF[m] = "leg"
L_D = L_R = 10.0                  # 1/s, the recruitment / de-recruitment gains of the Xia & Frey-Law 2008 controller
                                  # (their L_D = L_R = 10 s^-1)
HEAT_SHORTEN, HEAT_LENGTHEN = 1.2, 0.3   # shortening / lengthening heat relative to the activation-maintenance term:
                                  # the STRUCTURE of Umberger, Gerritsen & Martin 2003 (h_AM + h_SL + work), the two
                                  # weights ASSUMED (ranked in MUSCLE-MODEL.md section 5). Only the shape per muscle
                                  # depends on them: the set total is calibrated to the analysis' energy budget.

L_SH, R_SH, L_EL, R_EL, L_WR, R_WR, L_HIP, R_HIP = 11, 12, 13, 14, 15, 16, 23, 24
_CACHE = {}


def _smooth(x, n=5):
    return np.convolve(x, np.ones(n) / n, mode="same")


def moment_arm_shape(theta_deg):
    """Elbow-flexor moment arm relative to its peak, vs elbow flexion (0 = straight). A smooth
    hump after Murray, Delp & Buchanan 1995 (J Biomech 28:513; their Fig. 4: the biceps' arm
    rises from ~1.5 cm at full extension to ~4.5 cm near 90-100 deg and falls again past 120):
    about a third of the peak at full extension, the peak near 90-100 deg. Applied to all three
    flexors (the brachialis and brachioradialis have the same shape, different peaks). The
    input is the on-screen 3D elbow angle from MediaPipe (signals.elbow_l / elbow_r)."""
    th = np.clip(theta_deg, 0, 145)
    return 0.30 + 0.70 * np.sin(np.radians(th) * (90.0 / 85.0))


def f_v(v_norm):
    """Hill force-velocity factor: the force a fully active muscle can give at a contraction
    velocity, relative to isometric. v_norm = v / v_max, + = shortening.
    Shortening: Hill 1938 hyperbola with a/F0 = HILL_A (0.25, the value Thelen 2003 uses).
    Lengthening: a saturating rise to ECC_PLATEAU x isometric (1.6; Thelen 2003 uses 1.4-1.8),
    with half the rise at 8 % of v_max. The velocity comes from the joint angular velocity times
    the muscle's moment arm, divided by V_MAX_LOPT optimal fibre lengths per second (10, arm26)."""
    v = np.clip(v_norm, -1.0, 0.98)
    conc = (1 - v) / (1 + v / HILL_A)
    ecc = 1 + (ECC_PLATEAU - 1) * (-v) / (0.08 + (-v))
    return np.where(v >= 0, conc, ecc)


def feet_off_frame(analysis, knee_deg=120.0, hold=5):
    """First frame after the hands are on the bar where the knees stay bent under knee_deg for
    `hold` frames: the legs lifting into the tuck. Before it he stands (or half-hangs) with the
    feet on the floor (set #3: hands on at 9.4 s, shoulders sink at 11.5-12.7 s with the feet
    still down, legs lift at 14.2 s). Falls back to the first rep's start if nothing is found."""
    sig = analysis["signals"]
    kl = np.nan_to_num(np.array(sig.get("knee_l", []), float), nan=180.0)
    kr = np.nan_to_num(np.array(sig.get("knee_r", []), float), nan=180.0)
    first = analysis["reps"][0]["f_start"] if analysis.get("reps") else len(sig["phase"])
    if len(kl) == 0 or len(kr) == 0:
        return first
    knee = 0.5 * (kl + kr)
    h0 = int(sig.get("hang0", 0))
    bent = knee < knee_deg
    for i in range(h0, min(first, len(knee) - hold)):
        if bent[i:i + hold].all():
            return i
    return first


def hand_load_fraction(analysis, P):
    """Fraction of the lifted weight on the hands per frame: 1 once the feet are off the floor;
    before that, how far the shoulders have sunk from the standing hold toward the hanging
    level (image space), floored at 0.2 for the grip that already holds the bar."""
    N = len(P)
    load = np.ones(N)
    sig = analysis["signals"]; h0 = int(sig.get("hang0", 0)); f_off = feet_off_frame(analysis)
    if f_off <= h0 + 5:
        return load
    sh_y = 0.5 * (P[:, L_SH, 1] + P[:, R_SH, 1])
    y_hold = float(np.median(sh_y[h0:min(h0 + 30, f_off)]))
    y_hang = float(np.median(sh_y[f_off:min(f_off + 30, N)]))
    if y_hang - y_hold < 5:
        return load
    frac = np.clip((sh_y - y_hold) / (y_hang - y_hold), 0.0, 1.0)
    load[:f_off] = 0.2 + 0.8 * frac[:f_off]
    load[:h0] = 0.0
    return _smooth(load, 5)


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
        ang3 = np.array(sig["elbow_" + side], float)          # 3D elbow angle, 180 = straight
        theta = _smooth(np.clip(180.0 - np.nan_to_num(ang3, nan=160.0), 0, 150))
        # v4.2 (2026-09-09, Dennis: "are you sure the lats should be under the biceps?"): the
        # shoulder's depth behind the bar is COMPUTED per frame instead of assumed 4 -> 20 cm.
        # Hand-to-shoulder distance from the elbow angle (law of cosines over the measured forearm
        # and upper arm), minus what the picture shows across and down: the rest is depth. At the
        # top (elbow 60 deg, shoulder 15 cm under the bar) that is ~27 cm, not 20, and it is the
        # number that sets the lats' level.
        # The "upper arm" here is the elbow-to-SHOULDER-LANDMARK distance measured at the dead hang
        # (26 cm), not the anatomical 35 cm: the landmark sits at the joint centre, and it is the
        # landmark whose depth we need. (Using the table's 35 cm put the shoulder 30 cm behind the
        # bar at a plumb dead hang, which is impossible: tried and rejected, 2026-09-09.) The two
        # elbows' 3D angles disagree by 20 deg where the image plane says 2 (unclaimed for three
        # sets), so the depth uses their mean, the number shown on screen.
        L_up_img = np.linalg.norm(upper, axis=1)
        L_up = float(np.median(L_up_img[hang_frames])) if len(hang_frames) > 5 else float(np.percentile(L_up_img, 95))
        th_mean = _smooth(np.clip(180.0 - np.nan_to_num(0.5 * (np.array(sig["elbow_l"], float) + np.array(sig["elbow_r"], float)), nan=160.0), 0, 150))
        L_hs = np.sqrt(np.maximum(L_true ** 2 + L_up ** 2 - 2 * L_true * L_up * np.cos(np.radians(180.0 - th_mean)), 1e-4))
        dx_hs = np.abs((R[:, wr, 0] - R[:, sh, 0]) / ppm)
        dy_hs = np.abs((R[:, wr, 1] - R[:, sh, 1]) / ppm)
        d_sh = np.sqrt(np.maximum(L_hs ** 2 - dx_hs ** 2 - dy_hs ** 2, D_SH_HANG ** 2))
        d_sh = np.clip(_smooth(d_sh, 7), D_SH_HANG, D_SH_MAX)
        # lever about the shoulder for a vertical hand force = the horizontal hand-to-shoulder
        # distance = across (measured in the plane) and depth (computed above) combined
        lever_sh = np.sqrt(dx_hs ** 2 + d_sh ** 2)
        omega_el = np.radians(np.gradient(theta)) * fps          # rad/s, + = flexing
        trunk = (R[:, L_HIP] + R[:, R_HIP]) / 2 - (R[:, L_SH] + R[:, R_SH]) / 2
        cosang = np.einsum("ij,ij->i", upper, -trunk) / (np.linalg.norm(upper, axis=1) * np.linalg.norm(trunk, axis=1) + 1e-6)
        elev = _smooth(np.degrees(np.arccos(np.clip(cosang, -1, 1))))   # upper arm vs the trunk axis, 180 = overhead
        omega_sh = -np.radians(np.gradient(elev)) * fps          # + = adducting (arm coming down toward the trunk)
        out[side] = dict(lever_el=lever_el, lever_sh=lever_sh, theta=theta, omega_el=_smooth(omega_el),
                         elev=elev, omega_sh=_smooth(omega_sh), L_fore=L_true, L_up=L_up, d_sh=d_sh)
    vy = np.array(sig["vy_m"], float)
    ay = _smooth(np.gradient(_smooth(vy)) * fps, 7)
    m_lift = S.get("lifted_mass_kg") or S["mass_kg"] * 0.956
    load = hand_load_fraction(analysis, P)          # < 1 while the feet are still on the floor
    F_hand = np.where(on_bar, 0.5 * m_lift * np.clip(G + ay, 0, None) * load, 0.0)   # N, per arm
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
        # STEP 1, inverse dynamics: joint moment = vertical hand force (per arm, from m_lift (g + a_y)
        # times the hand-load fraction) x horizontal lever to the joint (kinematics: the forearm's
        # foreshortening for the elbow, across + computed depth for the shoulder). Segment weights
        # and inertia of the arm are ignored (about 5 % of the hand force; ranked in section 5).
        Mel = F * k["lever_el"]; Msh = F * k["lever_sh"]
        M_el += 0.5 * Mel; M_sh += 0.5 * Msh
        # STEP 2, force sharing at the elbow: Crowninshield & Brand 1981 (J Biomech 14:793), minimise
        # sum_i (F_i / F_max,i)^p subject to sum_i r_i F_i = M, p = SHARE_P = 3. With all agonists
        # pulling the same way the Lagrangian gives the closed form
        #     F_i = M (r_i F_max,i)^(1/(p-1)) F_max,i / sum_k (r_k F_max,k)^(p/(p-1))
        # so bigger and better-levered muscles take more of the moment. F_max,i = sigma x PCSA from
        # the arm26 OpenSim model (Holzbaur 2005 values), r_i = peak moment arm x the flexion shape.
        shape = moment_arm_shape(k["theta"])
        # v4.2: pronated grip. The biceps is also a supinator and its flexion moment arm is smaller
        # with the forearm pronated (Murray, Delp & Buchanan 1995); the brachialis and
        # brachioradialis are unaffected. This is the chin-up / pull-up difference in the EMG
        # (Youdas 2010: biceps 96 -> 78 %MVIC, lower trapezius up). Factor from memory of Murray
        # 1995 (~0.75 at 90 deg); see 08-moment-arms-and-strength.md once fetched.
        r = {m: v[1] * shape * (PRONATION_BICEPS if m == "biceps brachii" else 1.0) for m, v in ELBOW_FLEXORS.items()}
        denom = sum((r[m] * ELBOW_FLEXORS[m][0]) ** (SHARE_P / (SHARE_P - 1)) for m in ELBOW_FLEXORS) + 1e-9
        for m, (Fmax, r_pk, lopt, _) in ELBOW_FLEXORS.items():
            Fi = Mel * (r[m] * Fmax) ** (1 / (SHARE_P - 1)) / denom * Fmax
            # STEP 3, force-velocity: the activation needed for F_i is F_i / (F_max f_v(v)); the fibre
            # velocity is the elbow angular velocity (from the smoothed 3D elbow angle) x moment arm,
            # in optimal fibre lengths per second. Shortening (the pull) costs more activation per
            # newton than lengthening (the lowering): Hill 1938, Dickie 2017 measured the EMG side.
            vn = r[m] * k["omega_el"] / (V_MAX_LOPT * lopt)       # shortening when flexing
            u[m] += 0.5 * Fi / (ELBOW_STRENGTH * Fmax * f_v(vn))   # the sharing is unchanged by a common factor
        # The same two steps at the shoulder: the extensors / adductors that bring the arm down from
        # overhead share M_sh with p = 3; moment arms at high elevation from Ackland 2008 (J Anat
        # 213:383), capacities from PCSA x sigma with the athlete factor SHOULDER_STRENGTH. The
        # angular velocity is that of the upper arm against the trunk axis (kinematics: elev).
        denom = sum((v[1] * v[0]) ** (SHARE_P / (SHARE_P - 1)) for v in SHOULDER_ADDUCTORS.values())
        for m, (Fmax, r_m, lopt, _) in SHOULDER_ADDUCTORS.items():
            Fi = Msh * (r_m * Fmax) ** (1 / (SHARE_P - 1)) / denom * Fmax
            vn = r_m * k["omega_sh"] / (V_MAX_LOPT * lopt)
            u[m] += 0.5 * Fi / (SHOULDER_STRENGTH * Fmax * f_v(vn))
    # Antagonist: the triceps co-contracts at the elbow at COCONTRACTION x the biceps' drive (Youdas
    # 2010 has the triceps near 15 %MVIC over the rep); it is also a shoulder extensor (long head)
    # in the sharing above, and the larger of the two applies.
    u["triceps"] = np.maximum(u["triceps"], COCONTRACTION * u["biceps brachii"])
    # Grip: the forearm flexors hold the hand force isometrically, GRIP_AT_HANG (0.60, estimate:
    # no pull-up grip EMG exists, climbing dead-hang studies show large flexor RMS) at body weight
    # and proportional to the hand force otherwise, so the hang between reps never lets go. The
    # extensors stabilise the wrist at 35/60 of that (both estimates, MUSCLES table).
    grip = GRIP_AT_HANG * K["F_hand"] / (0.5 * K["m_lift"] * G)
    u["forearm flexors"] = grip
    u["forearm extensors"] = grip * 35.0 / 60.0
    # Muscles without a lever the front camera can see (rotator cuff, trapezius, serratus, core,
    # erector spinae) follow the lats' required activation at their %MVIC ratio (STABILISER_RATIO).
    lat = u["latissimus dorsi"]
    for m, ratio in STABILISER_RATIO.items():
        u[m] = ratio * lat
    # Park & Yoo 2013: lat -> trapezius shift as the shoulder comes down at the top
    sig = analysis["signals"]; phase = np.array(sig["phase"], dtype=object)
    hold = _smooth(np.array([ph == "HOLD" for ph in phase], float))
    u["latissimus dorsi"] = u["latissimus dorsi"] * (1 - 0.15 * hold)
    u["trapezius"] = u["trapezius"] + 0.15 * hold * lat
    u["upper trapezius"] = u["upper trapezius"] + 0.10 * hold * lat
    # v4.1: the pull STARTS with scapular depression (lower / middle trapezius, with the lats) before the
    # elbow flexes (Prinold & Bull 2016). While the phase is PULL and the elbow is still near straight,
    # the trapezius gets its own drive instead of only following the lats
    init = np.zeros(N)
    for side in ("l", "r"):
        init += 0.5 * ((K[side]["theta"] < INIT_ELBOW_DEG) & (phase == "PULL")).astype(float)
    init = _smooth(init, 5)
    u["trapezius"] = u["trapezius"] + INIT_TRAP * init
    # Youdas 2010 (full text, via Di Fonza 2026): the rep is "initiated by the lower trapezius and
    # pectoralis major" (07-phase-resolved-emg.md). The pec's sternal fibres extend the arm from
    # overhead, so it leads with the trapezius and eases as the biceps and lats take over
    u["pectoralis major"] = u["pectoralis major"] + INIT_PEC * init
    # Dinunzio 2018: core rises with hip motion, not pull effort
    sway = np.zeros(N)
    for rp in analysis["reps"]:
        sway[rp["f_start"]:rp["f_end"] + 1] = rp.get("hip_sway_cm", 4.0)
    kip = np.clip((sway - 4.0) / 8.0, 0, 1)
    u["rectus abdominis"] = u["rectus abdominis"] + 0.6 * kip * lat
    u["external oblique"] = u["external oblique"] + 0.4 * kip * lat
    # v4.1: the legs hold the tuck against g + a_y, so their drive breathes with the vertical acceleration
    load = np.clip((G + K["ay"]) / G, 0.5, 1.6) if POSTURAL_BREATHES else np.ones(N)
    for m, a0 in POSTURAL_ACT.items():
        u[m] = a0 * K["on_bar"] * load
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
    # STEP 4, activation dynamics (Thelen 2003, J Biomech Eng 125:70, eq. 1-3; Winters 1995):
    # da/dt = (u - a) / tau with tau_act = 15 ms when the demand rises and tau_deact = 50 ms when it
    # falls, integrated exactly over one frame. u is clipped at 1 here: a muscle cannot be more
    # than fully active, and a demand above 1 means the model's capacity is short (printed by
    # __main__ as the peak of u).
    a = {m: np.zeros(N) for m in MUSCLES}
    for m in MUSCLES:
        cur = 0.0
        um = np.clip(u[m], 0, 1)
        for i in range(N):
            tau = TAU_ACT if um[i] > cur else TAU_DEACT
            cur += (um[i] - cur) * (1 - np.exp(-dt / tau))
            a[m][i] = cur
    # STEP 5, fatigue that compounds: Xia & Frey-Law 2008 (J Biomech 41:3046) three-compartment
    # model per muscle. Motor units are resting M_R, active M_A or fatigued M_F (sum = 1):
    #     dM_A/dt = C(t) - F M_A,   dM_F/dt = F M_A - R M_F,   dM_R/dt = -C(t) + R M_F
    # C(t) recruits resting units (gain L_D) when the target load TL = a(t) exceeds M_A and
    # releases them (gain L_R) when it falls below; F and R are the joint region's fatigue and
    # recovery rates per second (FATIGUE, Frey-Law, Looft & Heitsman 2012 Table 1). While the target
    # load is zero the recovery runs at R x r (REST_MULT, Looft, Herkert & Frey-Law 2018: the
    # 3CC-r model, dM_R/dt = -C + R r M_F when TL = 0). Under load R is ~0.001-0.002 /s, so the
    # fatigued pool only grows inside the set (nothing relaxes between reps: the hang keeps the
    # grip and the shoulder above the occlusion threshold, Sadamoto 1983, 50-64 %MVC) and starts to
    # clear at 15-30 x that rate once the hands open. M_F is the fatigue one rep carries into the
    # next (peripheral fatigue with incomplete recovery, Carroll, Taylor & Gandevia 2017). Two
    # views of it are kept: a_eff = a / (1 - M_F), the share of the still-able units in use
    # (the brightness nudge), and the NON-RESTING share M_A + M_F = 1 - M_R, the colour (step 8).
    MF = {m: np.zeros(N) for m in MUSCLES}; MA = {m: np.zeros(N) for m in MUSCLES}
    for m in MUSCLES:
        joint = JOINT_OF.get(m, "shoulder")
        Fr, Rr = FATIGUE[joint]; rr = REST_MULT[joint]
        mr, ma, mf = 1.0, 0.0, 0.0
        for i in range(N):
            TL = a[m][i]
            if ma < TL:
                C = L_D * min(TL - ma, mr)
            else:
                C = L_R * (TL - ma)
            R_now = Rr * rr if TL < REST_TL else Rr        # rest: recovery x r (Looft 2018)
            dma = C - Fr * ma; dmf = Fr * ma - R_now * mf; dmr = -C + R_now * mf
            ma += dma * dt; mf += dmf * dt; mr += dmr * dt
            ma = max(ma, 0.0); mf = max(mf, 0.0); mr = max(mr, 0.0)
            tot = ma + mf + mr
            ma, mf, mr = ma / tot, mf / tot, mr / tot
            MA[m][i] = ma; MF[m][i] = mf
    a_eff = {m: np.clip(a[m] / np.maximum(1 - MF[m], 0.2), 0, 1) for m in MUSCLES}
    busy = {m: np.clip(MA[m] + MF[m], 0, 1) for m in MUSCLES}   # non-resting share, 1 - M_R
    # STEP 6, metabolic heat per muscle: the structure of Umberger, Gerritsen & Martin 2003
    # (Comput Methods Biomech Biomed Engin 6:99): an activation / maintenance term proportional
    # to muscle mass x activation, a shortening term (HEAT_SHORTEN x the normalised shortening
    # velocity) and a smaller lengthening term. Masses from pullup_thermal3.muscle_masses (Holzbaur
    # 2007 volumes x 1.06 kg/l, both sides). The one free constant kcal_scale is fixed so that the
    # SET TOTAL equals the analysis' own energy budget (frame_powers: mechanical work / 22 %
    # efficiency, eccentric at 35 % of that, the isometric hang with the grip's and legs' share),
    # so the calories and kJ on screen are the analysis', and only WHERE and WHEN the heat lands
    # is the model's.
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
    # STEP 7, temperature (unchanged from v3): a lumped heat balance per muscle,
    #     C m dT/dt = q - k(t) m T,   C = C_MUSCLE = 3.6 kJ/kg/K (muscle specific heat),
    # blood-borne removal k ramping as 1 - exp(-t_on / TAU_PERFUSION) toward K_BLOOD = 42 W/K/kg
    # (Gonzalez-Alonso et al. 2000, J Physiol 524:603: heat production 70 -> 126 J/s and removal
    # 0 -> 112 J/s over three minutes in 2.68 kg of quadriceps, which fixes both the coefficient and
    # its time constant; Kenny et al. 2003 for the order of magnitude). Conduction to the skin is
    # ignored on purpose: it is too slow to matter in 50 s (04-thermal-skin-and-anatomy-assets.md).
    # Temperature therefore never falls inside a set, which is why it is the FLOOR of the colour
    # and not the colour (see step 8).
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
    # 8. the EFFORT INDEX the paint is coloured by (v4.3): fast part = the non-resting share of the
    #    motor-unit pool, M_A + M_F. M_A contracts and relaxes inside the rep; M_F is the heat one
    #    rep leaves in the next (it climbs through the set and clears only after the release, at
    #    R x r). Slow part = the temperature as a fraction of T_REF, the floor that never falls.
    #    v4.1-4.2 used a_eff for the fast part, which returned to the hang's value between reps and
    #    hid the carry-over (Dennis, 2026-09-09: "each rep should get hotter").
    E = {m: np.clip(EFFORT_FAST * busy[m] + EFFORT_SLOW * np.minimum(T[m] / T_REF, 1.0), 0, 1) for m in MUSCLES}
    out = dict(u=u, a=a, a_eff=a_eff, busy=busy, MF=MF, MA=MA, T=T, q=q, E=E, M_el=extra["M_el"], M_sh=extra["M_sh"], K=K,
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


def effort(analysis, P=None, fps=None):
    """Per-muscle effort index 0..1, the quantity the paint is coloured by (v4.1)."""
    if P is None:
        raise ValueError("pullup_thermal4.effort needs the landmarks: effort(A, P=P)")
    return model(analysis, P, fps)["E"]


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
                    ecc_plateau=ECC_PLATEAU, d_sh_hang=D_SH_HANG, d_sh_max=D_SH_MAX, elbow_strength=ELBOW_STRENGTH, shoulder_strength=SHOULDER_STRENGTH, pronation_biceps=PRONATION_BICEPS, cocontraction=COCONTRACTION,
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
    # ---- the review tests (CLAUDE.md, "Model code"): ordering against the EMG literature and
    #      each joint's capacity against the strength norms, printed before any render ----
    ph = np.array(A["signals"]["phase"], dtype=object); rep = np.isin(ph, ["PULL", "HOLD", "LOWER"])
    U = Mo["u"]; K = Mo["K"]
    wr = {m: float(U[m][rep].mean()) for m in ("biceps brachii", "brachialis", "latissimus dorsi", "pectoralis major", "trapezius")}
    print("\nORDERING TEST, whole-rep required activation:", {m: round(v, 2) for m, v in wr.items()})
    print(f"  lats / biceps = {wr['latissimus dorsi'] / wr['biceps brachii']:.2f}   (Youdas 2010 pull-up 124/78 = 1.59; Snarr 2017 79.8/43.9 = 1.82)")
    print(f"  pec / lats    = {wr['pectoralis major'] / wr['latissimus dorsi']:.2f}   (Youdas 2010 44/124 = 0.35)")
    print(f"  peaks: lats {U['latissimus dorsi'].max():.2f}, biceps {U['biceps brachii'].max():.2f}  (above 1 = demand over capacity, clipped on screen)")
    cap_el = ELBOW_STRENGTH * sum(v[0] * v[1] * (PRONATION_BICEPS if m == "biceps brachii" else 1.0) for m, v in ELBOW_FLEXORS.items())
    cap_sh = SHOULDER_STRENGTH * sum(v[0] * v[1] for v in SHOULDER_ADDUCTORS.values())
    print(f"CAPACITY TEST: elbow {cap_el:.0f} N m at 90 deg pronated vs demand peak {Mo['M_el'].max():.0f} (norm: 79.5 N m supinated, Holzbaur 2007); "
          f"shoulder {cap_sh:.0f} N m vs demand peak {Mo['M_sh'].max():.0f}, PULL median {np.median(Mo['M_sh'][ph == 'PULL']):.0f} (norm: 93.7 N m adduction at 60 deg, Holzbaur 2007)")
    # FATIGUE TEST (v4.3): (1) the carry-over. The fatigued pool of the prime movers at each rep's
    #    top, and the colour's floor at each rep's hang, must climb monotonically through the set
    #    (nothing recovers under load: Sadamoto 1983 occlusion, Harris 1976 no PCr resynthesis
    #    without blood flow); the measured speed loss is the observable to compare against.
    #    (2) the release. From the DONE frame on, M_F must fall, slowly: Harris 1976's fast PCr
    #    half-time is 21-22 s, i.e. ~15 % back in 5 s; the model's R x r gives the number below.
    MFm = Mo["MF"]; Em = Mo["E"]; fps = A["summary"]["fps"]
    tops = [r_["f_top"] for r_ in A["reps"]]
    # the settled hang before each rep: the frame before the rep starts (rep 1: the last frame before it)
    hangs = [r_["f_start"] - 1 for r_ in A["reps"]]
    for m in ("latissimus dorsi", "biceps brachii", "forearm flexors"):
        print(f"FATIGUE TEST {m}: M_F at the tops {np.round([MFm[m][t] * 100 for t in tops]).astype(int).tolist()} %; "
              f"colour in the hang before each rep {np.round([Em[m][h] * 100 for h in hangs]).astype(int).tolist()} %")
    print(f"  measured: peak speed rep 1 -> rep {len(tops)}: -{A['summary']['velocity_loss_pct']:.0f} % (analysis.json); "
          f"the model's biceps pool at the last top over the first: x{MFm['biceps brachii'][tops[-1]] / max(MFm['biceps brachii'][tops[0]], 1e-6):.1f}")
    # the literature's shape for the same thing (10-rep-to-rep-fatigue-in-a-set.md): EMG amplitude climbs
    # first -> last rep, 86 -> 124 %MVC in Sundstrup 2012 (lateral raise to failure, curvilinear, plateau
    # in the last 3-5 reps); sets to failure end at 40-60 % speed / power loss (Izquierdo 2009/2011,
    # Garcia-Ramos 2020); 5 s of UNLOADED rest halves the loss (Garcia-Ramos 2020), but the hang is
    # loaded rest, and forearm blood flow is occluded above ~25 %MVC (Bystrom & Kilbom 1990), so the
    # grip gets no inter-rep recovery here and the prime movers only what the 3CC's under-load R gives.
    first_last = {m: (Em[m][hangs[0]:tops[0] + 1].max(), Em[m][hangs[-1]:tops[-1] + 1].max()) for m in ("trapezius", "biceps brachii")}
    print("  literature: EMG amplitude first -> last rep 86 -> 124 %MVC (Sundstrup 2012, x1.44); model's peak colour first -> last rep "
          + ", ".join(f"{m} {a0*100:.0f} -> {a1*100:.0f} %" for m, (a0, a1) in first_last.items())
          + "; unloaded 5 s rest would halve the speed loss (Garcia-Ramos 2020), the hang is loaded, so none is granted")
    done = np.where(ph == "DONE")[0]
    if len(done):
        f0 = done[0]; f5 = min(f0 + int(5 * fps), len(ph) - 1)
        for m in ("latissimus dorsi", "biceps brachii", "forearm flexors"):
            rec = 100 * (1 - MFm[m][f5] / max(MFm[m][f0], 1e-6))
            print(f"  release {m}: M_F {MFm[m][f0]*100:.1f} % at let-go -> {MFm[m][f5]*100:.1f} % {(f5 - f0) / fps:.1f} s later "
                  f"({rec:.0f} % recovered; Harris 1976 PCr fast half-time 21-22 s = 15 % in 5 s); colour {Em[m][f0]*100:.0f} -> {Em[m][f5]*100:.0f} %")
    hang = (ph == "HANG") & (np.arange(len(ph)) > A["reps"][0]["f_end"])
    for side in "lr":
        print(f"GEOMETRY {side}: forearm {K[side]['L_fore']*100:.1f} cm, elbow-to-shoulder landmark {K[side]['L_up']*100:.1f} cm (tables: 27.4 / 35.0 for 188 cm); "
              f"shoulder depth behind the bar: hang {np.median(K[side]['d_sh'][hang])*100:.0f} cm, tops {np.round([K[side]['d_sh'][t]*100 for t in tops]).astype(int).tolist()} cm")
