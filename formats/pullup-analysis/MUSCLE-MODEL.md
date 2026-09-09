# The muscle model behind the heat map (v4, 2026-09-08)

Written by Fable for Dennis, who asked for the heat map to "integrate contraction and
relaxation of the movement" and for "a more scientific and precise way to formulate the
problem". This is that formulation. It is implemented in `tools/scripts/pullup_thermal4.py`
and drives every export from now on; v3 (`pullup_thermal3.py`, a phase table) is kept for
comparison and can be switched back with `model=3`.

## 1. What was wrong with v3

v3 gave every muscle a fixed share of the set's heat (%MVIC × mass, Youdas 2010) and read the
per-frame "activation" from a table: PULL 1.0, HOLD 0.85, LOWER 0.65, HANG 0.35, scaled a
little by the pull speed. Three consequences:

- a muscle could not contract and relax inside a rep, only brighten with the phase name;
- a late rep cost exactly what an early one did, so nothing compounded except temperature;
- the biceps and the lats had the same time-course, only different amplitudes.

## 2. The formulation

The problem is: given the body's motion in the video, estimate for every muscle *m* and every
frame *t* its activation *a_m(t)*, its fatigue state, its metabolic heat *q_m(t)* and its
temperature rise *ΔT_m(t)*. The standard way to do that in biomechanics is a chain of
inverse dynamics → muscle force sharing → muscle mechanics → energetics, with a fatigue
state that carries over from rep to rep. Each link, with what is measured and what is assumed:

### 2.1 Inverse dynamics (measured)

The hand force is what the body weighs plus what it accelerates:

    F(t) = m_lift · (g + a_y(t))          per arm: F/2

*m_lift* = 75.5 kg (body mass minus the forearms and hands, from the analysis), *a_y* from the
shoulder trace in the rectified bar plane. The force acts vertically through the hand, so a
joint's moment is the force times the **horizontal** distance from the hand to the joint:

    M_elbow(t)    = F/2 · d_elbow(t)
    M_shoulder(t) = F/2 · d_shoulder(t)

`d_elbow` is the trick that makes a front camera enough: the forearm's true length *L* is
measured at the dead hang (it is vertical and in the bar plane there: 28.4 cm left, 27.0 cm
right, against 27.4 cm from the segment tables for 188 cm), and in any later frame

    d_elbow = sqrt(L² − Δy²)

because whatever foreshortening took away from the picture is exactly the horizontal extent
of the forearm. `d_shoulder` has a measured across-the-picture part and an **assumed** depth
of the shoulder joint behind the bar plane: 4 cm at the hang, 20 cm at the top, interpolated
by the shoulder height. That depth is the one number a front camera cannot give; a side phone
next time replaces it with a measurement.

Result on this set: elbow moment 9 N·m at the hang, 79 N·m peak mid-pull; shoulder moment 24
N·m at the hang, 76 N·m peak. Elbow-flexion strength for a trained man is about 70–80 N·m, so
the biceps is at its limit in the middle of the pull, which is what the EMG literature says.

### 2.2 Force sharing (literature, closed form)

More muscles cross each joint than there are equations, so the moment is shared by the static
optimisation of Crowninshield & Brand (1981): minimise Σ (F_i / F_max,i)³ subject to
Σ r_i F_i = M. With every agonist pulling the same way this has a closed form for the
activation of each muscle:

    a_i = M · (r_i F_max,i)^(1/2) / Σ_k (r_k F_max,k)^(3/2)

*F_max* = 50 N/cm² × PCSA (biceps 1060 N and brachialis 987 N from the CC BY `arm26` OpenSim
model in the archive; lats 1100 N from the An 1981 PCSA of 22 cm² in
`data/anatomy-pcsa-volume.csv`; the rest listed with their source in the module). Moment arms:
elbow flexors from Murray, Delp & Buchanan 1995 as a hump over the elbow angle (a third of the
peak at full extension, the peak near 90–100°); shoulder adductors from Ackland et al. 2008.
The triceps co-contracts at 12 % of the flexor drive (Youdas' 15 %MVIC).

### 2.3 Force–velocity (Hill 1938)

The activation a muscle needs for a force depends on how fast it is changing length:

    u_i = F_i / (F_max,i · f_v(v_i)),   v_i = r_i · ω_joint / (10 · l_opt,i)

with the Hill hyperbola for shortening (a/F₀ = 0.25) and a plateau at 1.6 × isometric for
lengthening. This is why the pull costs more than the lowering; in v3 that was a table entry
(0.65), here it follows from the elbow and shoulder angular velocities that the trackers
measure. Force–length is ignored (stated).

### 2.4 Activation dynamics (Thelen 2003)

    da/dt = (u − a) / τ,   τ = 15 ms when u > a, 50 ms when u < a

Relaxation lags contraction by a few frames. Small at 30 fps, but physically right, and it is
the part that makes the map "breathe" rather than switch.

### 2.5 Fatigue that compounds (Xia & Frey-Law 2008)

Every muscle has three pools of motor units, resting *M_R*, active *M_A* and fatigued *M_F*,
that sum to 1:

    dM_A/dt = C(t) − F · M_A
    dM_F/dt = F · M_A − R · M_F
    dM_R/dt = −C(t) + R · M_F

*C(t)* is a controller that recruits resting units to make *M_A* follow the target *a(t)*
(gains 10 /s). *F* and *R* are the fatigue and recovery rates, joint-specific after Frey-Law,
Looft & Heitsenrether (2012): elbow 0.0091 / 0.00094 per second, shoulder 0.0059 / 0.00058,
grip 0.0098 / 0.00091. **Those rates were entered from memory of that paper and are not in the
archive; verify before quoting them.** What the viewer sees is the *effective* activation,
the share of the still-able units being used:

    a_eff = a / (1 − M_F)

On this set the fatigued pool ends at 24 % for the biceps, 27 % for the grip, 16 % for the
lats. That is the compounding Dennis asked about: the same rep late in the set is drawn from a
smaller pool, so it costs more of what is left, and the measured −40 % peak speed is the
consequence (a fatigued muscle cannot produce the same force at the same speed).

### 2.6 Metabolic heat (Umberger 2003 structure, calibrated)

Per muscle, per frame:

    q_i = k · mass_i · a_i · (1 + 1.2 · max(v̂_i, 0) + 0.3 · max(−v̂_i, 0))

activation/maintenance heat plus a shortening term and a small lengthening term. The one
constant *k* is fixed so that the set total equals the energy budget the analysis already
reports (work / 22 % efficiency, eccentric at 35 % of that, the isometric hang cost with the
grip's and the legs' local share): 26.9 kJ deposited in the muscles, the same figure v3 used.
The numbers on the judge's card therefore do not change; only *where* and *when* the heat
lands does.

### 2.7 Temperature (unchanged from v3)

    C · dT_i/dt = q_i − k_blood(t) · ΔT_i,   C = 3.6 kJ/kg/K,  k_blood → 42 W/K/kg with τ = 90 s

González-Alonso 2000, Kenny 2003; temperature never falls inside a set.

## 3. What the map shows now

- **Colour** = modelled temperature rise on the ironbow scale, 0 → +1.5 °C. Slow, accumulates.
- **Brightness** = effective activation *a_eff*. Fast: contracts and relaxes with the levers
  of the rep, and climbs through the set as the fatigued pool grows.
- **The left stack** carries the numbers that compound: chin tally, speed loss, running peak
  power, lats' temperature, the biceps' fatigued pool, calories and heat so far.

Muscles without a visible lever (rotator cuff, trapezius, serratus, core, legs) follow the lat's
activation at their published EMG ratio (Youdas 2010, Tucker 2011), the core rising with
measured hip motion (Dinunzio 2018), as in v3.

## 4. Validation against the EMG literature

Mean required activation per phase, this set (v4), against the whole-rep %MVIC of Youdas 2010:

| muscle | PULL | HOLD | LOWER | HANG | fatigued at the end | Youdas %MVIC |
|---|---|---|---|---|---|---|
| biceps brachii | 1.01 | 0.59 | 0.71 | 0.25 | 24 % | 78–96 |
| brachialis | 0.69 | 0.42 | 0.52 | 0.18 | 19 % | (78, assumed) |
| brachioradialis | 0.65 | 0.37 | 0.44 | 0.16 | 17 % | 62 (est.) |
| forearm flexors (grip) | 0.60 | 0.55 | 0.61 | 0.61 | 27 % | 60 (est.) |
| latissimus dorsi | 0.54 | 0.84 | 0.71 | 0.35 | 16 % | 117–130 |
| pectoralis major | 0.41 | 0.75 | 0.57 | 0.27 | 13 % | 44–57 |
| teres major | 0.28 | 0.51 | 0.38 | 0.18 | 9 % | (99, assumed) |
| triceps | 0.31 | 0.55 | 0.38 | 0.19 | 9 % | 15 (est.) |

Where it agrees: the biceps at its limit mid-pull, the lats highest at the top, the grip flat
through the whole set, concentric above eccentric everywhere without a table saying so. Where
it does not: Youdas has the lats above the biceps over the whole rep and the model has them
below; the pec and triceps come out higher than the EMG. Both point at the same thing, the
shoulder's depth behind the bar, which the front camera cannot see and which was assumed. A
side camera turns that assumption into a measurement.

## 5. Assumptions, ranked by how much they move the picture

1. Shoulder depth behind the bar (4 → 20 cm). Sets the lats' whole level.
2. Fatigue rates F, R (from memory of Frey-Law 2012). Set how fast the pool empties.
3. Shoulder moment arms (Ackland 2008) at overhead elevation; the pec's role above 90°.
4. Grip activation at the hang (60 %) and its scaling with the hand force.
5. Force–length ignored; segment weights of the arm ignored; both arms share the force
   equally (Prinold 2016: < 5 % BW asymmetry in regular practitioners).
6. The heat calibration: the shape per muscle is the model's, the total is the analysis'.

## 6. What a side camera would add

Chin depth, shoulder depth, elbow angle in its own plane, the sagittal lever of every joint —
the four assumptions above collapse into measurements. One phone at hip height, 3 m to the
side, is enough.

## References (all in `references/pullup-science/` unless marked)

Crowninshield & Brand 1981 (J Biomech; classic, not in the archive) · Murray, Delp & Buchanan
1995 (J Biomech; classic, not in the archive) · Ackland, Pak, Richardson & Pandy 2008 (J Anat;
not in the archive) · Hill 1938 · Thelen 2003 (J Biomech Eng) · Xia & Frey-Law 2008 (J
Biomech) · Frey-Law, Looft & Heitsenrether 2012 (J Biomech) · Umberger, Gerritsen & Martin
2003 (Comput Methods Biomech Biomed Engin) · Youdas 2010, Tucker 2011, Dinunzio 2018, Dickie
2017, Snarr 2017 (`01-emg-and-anatomy.md`) · Holzbaur 2005/2007, Garner & Pandy 2003, An 1981
(`data/anatomy-pcsa-volume.csv`) · González-Alonso 2000, Kenny 2003 (`04-thermal-skin…`) ·
OpenSim `arm26.osim` (`anatomy-assets/opensim-models/`, CC BY 3.0).
