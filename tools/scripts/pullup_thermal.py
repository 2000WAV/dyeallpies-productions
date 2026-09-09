"""
Modelled muscle temperature rise for the pull-up reel.

This replaces the first video's "fatigue tint" with something that has units. The colour
on the body is a modelled temperature rise in degrees C, computed as a heat budget:

    C_m dT_m/dt = share_m * P_heat(t) - k_m(t) * dT_m

    C_m      = 3.6 kJ/kg/K * mass_m            specific heat of skeletal muscle
    share_m  = %MVIC_m * mass_m / sum(...)     EMG prior x muscle mass
    k_m(t)   = K_BLOOD * mass_m * (1 - exp(-t/TAU))   heat carried off by blood, which
                                               ramps up over the first minutes of work

Sources (full citations in references/pullup-thermal/README.md):
  Youdas et al. 2010 (J Strength Cond Res) - %MVIC per muscle in a pull-up.
  Dickie et al. 2017 (J Electromyogr Kinesiol) - concentric > eccentric.
  Gonzalez-Alonso et al. 2000 (J Physiol) - heat production 70->126 J/s in 2.68 kg of
    active muscle; blood-borne removal ~0 for the first 10 s, 112 J/s at 180 s; quadriceps
    +0.9-1.0 C over 3 min. That fixes K_BLOOD (112 W/K / 2.68 kg = 42 W/K/kg) and TAU.
  Kenny et al. 2003 (J Appl Physiol) - vastus medialis +2.0 to +3.2 C over 15 min at
    60 % VO2max, still elevated after recovery: muscle warms by degrees over minutes and
    cools over tens of minutes, so it never cools inside a 53 s set.
  Holzbaur et al. 2007 (J Biomech) - upper-limb muscle volumes (MRI, 10 adults).
  Jung et al. 2021 (Sensors) - what an infrared camera would actually show: skin over the
    working muscle differs by ~0.9 C and warms mostly AFTER the set. This model is the
    muscle underneath, not the skin.

IT IS A MODEL, NOT A MEASUREMENT. Say so wherever the colour appears.
"""
import numpy as np

C_MUSCLE = 3600.0        # J/kg/K, specific heat of skeletal muscle
K_BLOOD = 42.0           # W/K per kg of muscle, fully perfused (Gonzalez-Alonso 2000)
TAU_PERFUSION = 90.0     # s, time constant for perfusion to ramp up
ETA_CONC = 0.22          # metabolic efficiency of concentric work
ECC_COST = 0.35          # eccentric metabolic cost relative to the same concentric work
GRIP_SHARE_OF_ISO = 0.22  # share of the isometric "holding on" cost deposited in the grip.
                          # The 3.5 MET hang figure is a WHOLE-BODY metabolic rate; about a
                          # third of it is basal, and the rest is spread over grip, shoulder
                          # stabilisers, heart and breathing. Only the grip part is local.
HOLZBAUR_SCALE = 1.40    # Holzbaur's 10 subjects (2554 cm3 total upper limb, 5 M / 5 F)
                          # scaled to a 188 cm, 79 kg man (~3600 cm3). State this.
DENSITY = 1.06           # g/cm3

# muscle: (%MVIC in a pull-up, volume cm3 for BOTH sides, source note, scale_with_holzbaur)
# The legs are in the table because Dennis holds a tucked, crossed-leg position for the whole
# set: the hip flexors hold the tuck and the thigh, glutes and calves are along for the ride.
# They are genuinely low-activation, so they stay at the cold end of the scale - which is the
# honest picture and the reason the legs read blue.
MUSCLES = {
    "latissimus dorsi":   (124, 2 * 262.3, "Youdas 2010 (117-130); Holzbaur 2007"),
    "biceps brachii":     (78,  2 * 143.7, "Youdas 2010 (78-96); Holzbaur 2007"),
    "brachialis":         (78,  2 * 143.7, "assumed = biceps (elbow flexor, not measured); Holzbaur 2007"),
    "brachioradialis":    (62,  2 * 65.1,  "estimate (measured by Dickie 2017, no number in the abstract)"),
    "forearm flexors":    (60,  2 * 238.0, "grip, estimate; Holzbaur FDS+FDP+FCR+FCU"),
    "infraspinatus":      (75,  2 * 118.9, "Youdas 2010 (71-79); Holzbaur 2007"),
    "teres major":        (99,  2 * 32.7,  "assumed 0.8 x lat; Holzbaur 2007"),
    "trapezius":          (52,  2 * 250.0, "Youdas 2010 lower trapezius (45-56); volume is an estimate"),
    "pectoralis major":   (44,  2 * 290.0, "Youdas 2010 (44-57); Holzbaur 2007"),
    "posterior deltoid":  (60,  2 * 126.8, "estimate; Holzbaur deltoid volume / 3"),
    "external oblique":   (33,  2 * 110.0, "Youdas 2010 (31-35); volume is an estimate"),
    "rectus abdominis":   (20,  200.0,     "not measured in either study; both values are estimates"),
    "erector spinae":     (40,  2 * 400.0, "Youdas 2010 (39-41); volume is an estimate. On the back, not painted"),
    # --- lower body: holding a tucked, crossed-leg position, not doing the work ---
    "hip flexors":        (18,  2 * 500.0, "iliopsoas + TFL, holding the tuck; Dinunzio 2018 shows them active in a pull-up. Both numbers are estimates", False),
    "quadriceps":         (8,   2 * 1500.0, "isometric, holding the knee bent; %MVIC and volume are estimates", False),
    "hamstrings":         (6,   2 * 950.0,  "isometric; %MVIC and volume are estimates", False),
    "gluteus maximus":    (8,   2 * 850.0,  "isometric; %MVIC and volume are estimates", False),
    "calves":             (4,   2 * 650.0,  "triceps surae, almost passive here; estimates", False),
}
GRIP_MUSCLES = ("forearm flexors", "brachioradialis")
# The legs do not lift the body; they hold a tucked position. So they take no share of the
# WORK heat - only a slice of the isometric "holding on" cost, like the grip does.
POSTURAL = ("hip flexors", "quadriceps", "hamstrings", "gluteus maximus", "calves")
POSTURAL_SHARE_OF_ISO = 0.18
# regions that the silhouette atlas can actually paint from the front
PAINTED = [m for m in MUSCLES if m not in ("erector spinae", "hamstrings", "gluteus maximus")]


def muscle_masses():
    """kg per muscle group (both sides), scaled to this athlete.

    Upper-limb volumes come from Holzbaur's ten subjects and are scaled up (their group
    averaged 2554 cm3 of upper-limb muscle across five men and five women). Lower-body
    volumes are given directly for a 188 cm man and are not scaled again."""
    out = {}
    for m, v in MUSCLES.items():
        scaled = v[3] if len(v) > 3 else True
        out[m] = v[1] * (HOLZBAUR_SCALE if scaled else 1.0) * DENSITY / 1000.0
    return out


def heat_shares():
    """Fraction of the local WORK heat each muscle takes: %MVIC x mass, normalised over the
    muscles that actually lift the body. The postural (leg) group is excluded here and is
    fed from the isometric term instead."""
    mass = muscle_masses()
    w = {m: (MUSCLES[m][0] * mass[m] if m not in POSTURAL else 0.0) for m in MUSCLES}
    tot = sum(w.values())
    return {m: w[m] / tot for m in w}, mass


def frame_powers(analysis, fps=None):
    """Per-frame mechanical and metabolic heat power (W) from the analysis JSON.

    Returns (P_work_heat, P_iso, P_mech): heat from muscle work that lands in the prime
    movers, the isometric 'holding on' cost, and the external mechanical power.
    """
    S = analysis["summary"]; sig = analysis["signals"]
    fps = fps or S["fps"]
    v = np.array(sig["vy_m"], float)                    # m/s, + = up
    phase = np.array(sig["phase"], dtype=object)
    N = len(v)
    m_lift = S.get("lifted_mass_kg") or 0.0
    P_mech = m_lift * 9.81 * v                          # W on the lifted mass
    on_bar = np.isin(phase, ["HANG", "PULL", "HOLD", "LOWER", "LOADING"])
    P_work_heat = np.zeros(N);
    up = (P_mech > 0) & on_bar
    dn = (P_mech < 0) & on_bar
    # concentric: metabolic = mech/eta, heat = metabolic - mech
    P_work_heat[up] = P_mech[up] / ETA_CONC - P_mech[up]
    # eccentric: negative work is absorbed; its metabolic cost is all heat
    P_work_heat[dn] = np.abs(P_mech[dn]) * ECC_COST / ETA_CONC
    # isometric baseline (3.5 METs) whenever the body is on the bar
    iso_w = S.get("hang_kcal_per_s", 0.0) * 4184.0
    P_iso = np.where(on_bar, iso_w, 0.0)
    return P_work_heat, P_iso, P_mech


PHASE_FACTOR = {"PULL": 1.0, "HOLD": 0.85, "LOWER": 0.65, "HANG": 0.35, "LOADING": 0.25,
                "HANDS ON BAR": 0.12, "SETUP": 0.05, "DONE": 0.05}


def activation(analysis, fps=None):
    """Per-frame activation 0..1 for every muscle, driven by the movement itself.

    The literature gives the shape (%MVIC per muscle, and concentric > top hold > eccentric
    > hang, Dickie 2017); the measured pull speed of the moment scales it. This is what makes
    the map breathe with the rep instead of only accumulating: temperature is the slow term,
    activation is the fast one."""
    S = analysis["summary"]; sig = analysis["signals"]
    fps = fps or S["fps"]
    v = np.array(sig["vy_m"], float)
    phase = np.array(sig["phase"], dtype=object)
    reps = [r for r in analysis["reps"] if r.get("rep")]
    v_ref = max(r["peak_conc_v"] for r in reps) * 0.8 if reps else 1.0
    base = np.zeros(len(v))
    for i, ph in enumerate(phase):
        f = PHASE_FACTOR.get(ph, 0.05)
        if ph == "PULL":
            f *= 0.70 + 0.30 * min(1.0, max(0.0, v[i]) / v_ref)
        elif ph == "LOWER":
            f *= 0.80 + 0.20 * min(1.0, max(0.0, -v[i]) / v_ref)
        base[i] = f
    base = np.convolve(base, np.ones(5) / 5, mode="same")
    top = max(m[0] for m in MUSCLES.values())
    return {m: np.clip(base * MUSCLES[m][0] / top, 0, 1) for m in MUSCLES}


def integrate(analysis, fps=None):
    """Per-frame temperature rise (K) per muscle. Never falls inside the set by
    construction: over 53 s, perfusion removes far less than the muscles produce."""
    S = analysis["summary"]
    fps = fps or S["fps"]
    dt = 1.0 / fps
    P_work, P_iso, _ = frame_powers(analysis, fps)
    N = len(P_work)
    share, mass = heat_shares()
    grip_mass = sum(mass[m] for m in GRIP_MUSCLES)
    post_w = {m: MUSCLES[m][0] * mass[m] for m in POSTURAL}
    post_tot = sum(post_w.values())
    T = {m: np.zeros(N) for m in MUSCLES}
    t_on = 0.0
    cur = {m: 0.0 for m in MUSCLES}
    for i in range(N):
        active = P_work[i] > 0 or P_iso[i] > 0
        if active:
            t_on += dt
        perf = 1.0 - np.exp(-t_on / TAU_PERFUSION)
        for m in MUSCLES:
            q = share[m] * P_work[i]
            if m in GRIP_MUSCLES:                    # the grip also holds the body up
                q += P_iso[i] * GRIP_SHARE_OF_ISO * mass[m] / grip_mass
            elif m in POSTURAL:                      # the legs hold the tuck
                q += P_iso[i] * POSTURAL_SHARE_OF_ISO * post_w[m] / post_tot
            k = K_BLOOD * mass[m] * perf
            cur[m] += (q - k * cur[m]) / (C_MUSCLE * mass[m]) * dt
            if cur[m] < 0:
                cur[m] = 0.0
            T[m][i] = cur[m]
    return T


def summarise(analysis, T=None):
    """Per-muscle end-of-set temperature rise plus the numbers the report quotes."""
    T = T if T is not None else integrate(analysis)
    S = analysis["summary"]
    share, mass = heat_shares()
    P_work, P_iso, P_mech = frame_powers(analysis)
    fps = S["fps"]
    out = dict(
        muscles={m: dict(delta_T_C=float(T[m].max()), mass_kg=float(mass[m]),
                         mvic=MUSCLES[m][0], share=float(share[m]), note=MUSCLES[m][2],
                         painted=(m in PAINTED))
                 for m in MUSCLES},
        work_heat_kj=float(P_work.sum() / fps / 1000),
        iso_heat_kj=float(P_iso.sum() / fps / 1000),
        total_heat_kj=float((P_work.sum() + P_iso.sum()) / fps / 1000),
        peak_heat_w=float(P_work.max() + P_iso.max()),
        model=dict(c_muscle=C_MUSCLE, k_blood=K_BLOOD, tau_perfusion=TAU_PERFUSION,
                   eta_conc=ETA_CONC, ecc_cost=ECC_COST, holzbaur_scale=HOLZBAUR_SCALE,
                   grip_share_of_iso=GRIP_SHARE_OF_ISO, postural_share_of_iso=POSTURAL_SHARE_OF_ISO),
    )
    hot = max(out["muscles"], key=lambda m: out["muscles"][m]["delta_T_C"] if out["muscles"][m]["painted"] else -1)
    out["hottest"] = hot
    out["hottest_delta_T_C"] = out["muscles"][hot]["delta_T_C"]
    out["max_delta_T_C"] = max(v["delta_T_C"] for v in out["muscles"].values())
    return out


if __name__ == "__main__":
    import sys, json
    A = json.load(open(sys.argv[1]))
    T = integrate(A)
    s = summarise(A, T)
    print(f"work heat {s['work_heat_kj']:.1f} kJ + isometric {s['iso_heat_kj']:.1f} kJ "
          f"= {s['total_heat_kj']:.1f} kJ; peak {s['peak_heat_w']:.0f} W")
    print(f"{'muscle':22s} {'kg':>5s} {'%MVIC':>6s} {'share':>6s}  dT (C)")
    for m, v in sorted(s["muscles"].items(), key=lambda kv: -kv[1]["delta_T_C"]):
        print(f"{m:22s} {v['mass_kg']:5.2f} {v['mvic']:6d} {v['share']*100:5.1f}%  "
              f"+{v['delta_T_C']:.2f}{'' if v['painted'] else '   (not painted)'}")
    print(f"\nhottest painted muscle: {s['hottest']} +{s['hottest_delta_T_C']:.2f} C")
