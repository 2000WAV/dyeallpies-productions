# Item 2 — Puppet body dynamics

For the ~30 cm, ~11-rigid-body neon CG marionette hanging from 5 fingertip strings:
joint types and looseness, segment mass/inertia scaling, the drop-and-snap physics,
marionette simulation literature, and MuJoCo specifics. Every number below is
attributed to a saved file in `references/marionette/` (papers/, abstracts/,
data/); anything not found is marked **NOT FOUND** rather than guessed.

Full source list with URLs/licences/dates: `downloads-02.md`. Raw numbers in
`data/02-segment-parameters.csv` and `data/02-dynamics-numbers.csv`.

---

## 1. Marionette joint types, and how limp the joints are

Two families of source agree on the same picture: hobbyist/traditional
construction manuals, and the one detailed robotics-engineering survey of
marionette joints.

- **Traditional/craft construction** (Austman, *How to Make and Operate
  Marionettes*, `papers/takey-how-to-make-operate-marionettes.pdf`/`.txt`):
  knee and ankle joints are a **strip of leather**, nailed/tacked so as "to
  allow for a bend" — a single-axis (1-DOF), friction-only hinge with **no
  spring return**. Shoulder and hip are joined to the torso by a strip of
  **muslin cloth** or "the ribbed top of a stocking" — a flexible fabric
  joint, effectively low-stiffness and multi-axis rather than a rigid pin.
  Screw-eyes appear only as string pass-through points, not as the joints
  themselves. No angular range-of-motion or stiffness numbers are given
  anywhere in this source (it is a craft manual, not engineering) —
  **NOT FOUND** as quantitative data.

- **Engineering classification** (Chen, Tay, Xing & Yeo, "Marionette: From
  Traditional Manipulation to Robotic Manipulation",
  `papers/icdst-marionette-robotic-manipulation.pdf`/`.txt` — this PDF was
  already saved in the shared folder by another research item and is only
  read/cited here): puppet joints are built with "leather, cord, or
  screw-eyes" and are classified by DOF as 1-DOF revolute ("r-joint"), 2-DOF
  universal ("u-joint"), or 2-/3-DOF spherical ("s-joint"). Their own
  ~30 cm-scale robotic marionettes (Table 1, "ROMS-I/II/III") — heights
  **31.2 cm / 30.5 cm / 29.5 cm**, almost exactly this project's target scale
  — use predominantly **3-DOF ball joints** at the main body articulations
  (8, 9, and 4 s-joints respectively), with a handful of 1-DOF revolute
  joints (5, in ROMS-III) and one 2-DOF universal joint (ROMS-II). Total mass
  214–314 g; total joint count 23–35; motor/string count 8–16. See
  `data/02-dynamics-numbers.csv` for every number in this table.

- **Motorized marionette in practice** (Yamane, Hodgins & Brown 2003,
  `papers/yamane2003-marionette-icra.pdf`/`.txt`, ~60 cm marionette, 2× this
  project's scale): "the shoulder and elbow joints have **cloth stops** to
  prevent unrealistic joint angles" — i.e. the joint itself is otherwise
  unrestricted (free/underdamped), and range of motion is limited only by a
  soft cloth tether, not a rigid mechanical stop. This is the closest
  primary-source statement found of "how limp" a real marionette joint is:
  **essentially free within a soft, non-elastic limit**, with damping/friction
  only from the material itself.

- **Marionette joint angular range of motion in degrees**: **NOT FOUND** in
  any source consulted (academic or craft). Recommendation carried into
  `data/02-dynamics-numbers.csv`: use human anatomical ROM as an *upper*
  bound on MuJoCo joint `range` (e.g. shoulder ~180°, hip flexion ~120°),
  since a marionette joint is a looser, unstiffened version of the same
  hinge and is not anatomically restricted the way a living joint is — but
  flag this explicitly as a design choice, not a measured number.

- **Marionette joint damping coefficient**: **NOT FOUND** as a number
  anywhere. Yamane et al. (2003) fit a per-joint damping term experimentally
  but do not report its value in the available text. Recommendation: derive
  a starting damping from each limb's own pendulum period (Section 3) via
  MuJoCo's `solref` `dampratio=1` (critical damping) default, then hand-tune.

---

## 2. Segment mass fractions, lengths, COM, radius of gyration

Primary source: **de Leva (1996)**, "Adjustments to Zatsiorsky-Seluyanov's
Segment Inertia Parameters" (`papers/deleva1996-adjustments-zatsiorsky-seluyanov.pdf`,
full Table 4 transcribed). This gives, per segment and per sex, for a
reference female (61.9 kg / 1735 mm) and male (73.0 kg / 1741 mm): mass
fraction (% body mass), absolute segment length (mm, from which % of stature
is computed here), CM position (% of segment length from a named proximal
landmark), and **three-axis** (sagittal/transverse/longitudinal) radius of
gyration (% of segment length). Full table: `data/02-segment-parameters.csv`.
Headline mass fractions (male): Head 6.94%, Trunk 43.46%, Upper arm 2.71%,
Forearm 1.62%, Hand 0.61%, Thigh 14.16%, Shank 4.33%, Foot 1.37% — these sum
with left/right doubling of the paired limbs to ~100% of body mass, a useful
build-time check.

Secondary/cross-check source: **Dempster (1955)**, not obtained in the
original — the DTIC and University of Michigan mirrors were blocked/404, see
`downloads-02.md` — but his numbers survive verbatim in **Winter's Table 4.1**
(`papers/winter-anthro-table-illinois-me481.pdf`, a University of Illinois
ME481 course reproduction of Winter, *Biomechanics and Motor Control of Human
Movement*). This gives mass fraction, proximal/distal CM fraction, and
radius of gyration about the segment's own CG (single axis, not three) for
the same segments under slightly different landmark definitions (e.g.
Dempster's "Trunk" runs greater-trochanter to glenohumeral joint, i.e. hip to
shoulder, not de Leva's chest-only or cervicale-to-hip definitions — the two
are **not** interchangeable without checking endpoints; both are given in the
CSV with their endpoints spelled out so this isn't lost). Dempster's
head+neck mass fraction (8.1%) is higher than de Leva's head-only fraction
(6.68–6.94%) for exactly the reason it should be: it includes the neck — a
sanity check that passed.

**Segment length as a fraction of stature** (needed to scale to a 30 cm
figure): de Leva only reports absolute mm at one reference stature, so
fractions were *computed* here (length_mm / stature_mm, both from the same
table row — shown in the CSV notes column, not invented). The classic
literature source for length fractions directly, **Drillis & Contini
(1966)**, could only be found reproduced as a non-extractable figure (in
Winter's book) — recorded as **NOT FOUND** at the numeric-table level.
Substituted with **Fromuth et al. (2008)**,
`papers/fromuth2008-segment-lengths-stature.pdf`, an ASME IDETC/CIE paper
that reports very close modern ANSUR-survey-derived "boundary ratios" in the
same tradition: shoulder height 0.820×stature, hip height 0.528×stature, knee
height 0.284×stature, ankle height 0.038×stature, hand length 0.111×stature,
forearm length 0.151×stature, upper-arm length 0.193×stature (50th
percentile, averaged M/F). Derived thigh length (hip−knee) = 0.244×stature
and shank length (knee−ankle) = 0.246×stature agree with de Leva's
mm-derived fractions (0.212–0.249×stature) within the expected spread —
another passing cross-check between two independent sources.

**To scale to a 30 cm total mass M figure**: multiply each row's
`mass_fraction_pct_body_mass` by M for segment mass, `length_fraction_pct_stature`
by 0.30 m for segment length, and use the radius-of-gyration percentages
(of segment length, not stature) directly with the *scaled* segment length to
get each segment's rotational inertia via `I = m × (k × L)²` about the stated
axis, or via the parallel-axis theorem for inertia about a joint/string
attachment rather than the segment's own CG.

---

## 3. The drop and the snap

**Free fall inside the closing/opening fist** (10–15 cm per the brief, not a
literature number): kinematics gives fall time `t = √(2h/g)` and impact speed
`v = √(2gh)` — for h = 0.10 m, t ≈ 0.143 s, v ≈ 1.40 m/s; for h = 0.15 m,
t ≈ 0.175 s, v ≈ 1.72 m/s (both in `data/02-dynamics-numbers.csv`, marked as
computed, not sourced, since they follow directly from g).

**The snap itself**: the classical idealization (`papers/blacksacademy-impulsive-tensions-in-strings.pdf`,
cross-checked against `papers/mathspanda-impulsive-tension-lesson.pdf`) treats
a slack, massless, perfectly inextensible string suddenly going taut as a
**perfectly inelastic collision resolved along the string's own axis**:
momentum is conserved along the string direction, both ends are forced to the
same velocity component along the string, kinetic energy *is* lost in that
component (impulse `J = m_eff·v_along`), while the velocity component
perpendicular to the string is completely unaffected. This is the correct
mental model for what "5 strings suddenly taut" does to a falling rigid body:
each string kills its own along-string velocity component independently and
near-instantaneously. In a real numerical simulation the string is not
perfectly rigid, so this idealized discontinuity becomes a brief, finite-time
spring-like compression-and-release — which is the physical origin of the
"snap, then a bounce" behaviour specified in the brief, not an separate
assumption grafted on top.

**Georgia Tech's marionette-dynamics papers model the string the same way**,
as a hard unilateral constraint rather than a spring (Johnson & Murphey 2007,
`papers/johnson2007-dynamic-modeling-marionettes.pdf`/`.txt`): "the string
only enforces a maximum distance between two points," the force must be
positive (pulling only), and the constraint is dropped (string goes slack)
whenever the force needed to maintain it would go negative. They explicitly
call out and reject the alternative used in some computer-graphics work —
modelling a string as "a chain of small masses joined by stiff springs" —
as numerically unnecessary and prone to forcing very small integration
steps. This directly supports using MuJoCo's native length-limited tendon
(Section 5) rather than hand-building a spring chain for the 5 strings.

**Pendulum swing and its damping, once settled**: treat each swinging limb as
a **compound (physical) pendulum**, `T = 2π√(I_pivot / (m·g·d))`, with
`I_pivot` from the segment's own radius of gyration via the parallel-axis
theorem and `d` the distance from the pivot (joint or string attachment) to
the segment's CM — *not* the simple-pendulum formula unless the segment's own
rotational inertia is negligible next to `m·d²`.

For how fast a small, light body's swing decays from **air drag alone**,
`papers/salcedo2020-pendulum-resistance-coefficients.pdf`/`.txt` (Lee & Ju,
arXiv:2002.03796) measured pendulum balls of diameter 11.5–36.0 mm — a range
that brackets a marionette hand/head/torso — and found exponential damping
coefficients of **0.0096 s⁻¹ down to 0.0056 s⁻¹** as ball size *increased*
(mass grows faster than drag), with the linear-drag resistance coefficient
`c` (in `F = -c·v`) proportional to ball radius, 1.2×10⁻⁴ to 2.6×10⁻⁴ kg/s.
For a limb-scale pendulum with period on the order of 1 s, this gives a
logarithmic decrement of only **~0.006–0.01 per swing from air drag alone** —
i.e. air resistance is *not* the main mechanism that settles a marionette
over a 7 s shot; **joint/string friction has to do most of the settling
work**, consistent with Yamane et al. (2003) needing an experimentally fitted
extra damping term at the string/hand rather than relying on air drag.

(`papers/hatch2018-which-part-of-chain-breaks.pdf`, arXiv:1808.08668, on a
pulled harmonic chain, was also read for general "jerk" intuition — loading
rate vs. the system's natural period controls the outcome — but it models a
pulled chain, not a falling suspended body, so no number from it is used
directly; kept as context only, flagged in its abstract file.)

---

## 4. Marionette simulation / marionette-robot papers

| Paper | What it models | String/tendon treatment | Numbers reported |
|---|---|---|---|
| Yamane, Hodgins & Brown, ICRA 2003 (`yamane2003-marionette-icra`) | Motorized ~60 cm marionette driven from human mocap via inverse kinematics | String constraint only active in tension; hand swing modeled as a pendulum with a moving base, linearized, with a **fitted but unreported** damping term | Marionette height ~60 cm; cloth-stop joint limiting (qualitative) |
| Johnson & Murphey, ICRA 2007 (`johnson2007-dynamic-modeling-marionettes`) | Mixed dynamic-kinematic model, rigid bodies articulated by massless strings | Explicit **unilateral hard constraint** (string force ≥ 0, active only at full length); explicitly rejects spring-chain string models as numerically unnecessary | No stiffness/damping value reported — by design, their method needs none |
| Nguyen et al. (NTU "ROMS" group), RAM 2008 (`nguyen2008-toward-dynamic-model-marionettes`) | Lagrangian dynamic model of a robotic marionette, feed-forward/feedback control | Motor-pulley driven strings; parameter identification process described, values not extracted from available text | — |
| Chen/Tay/Xing/Yeo, "Marionette: From Traditional…" (`icdst-marionette-robotic-manipulation`, shared file) | Traditional-to-robotic joint survey + ROMS-I/II/III hardware | n/a (survey) | **Height 29.5–31.2 cm, mass 214–314 g, 23–35 joints, 8–16 motors/strings, joint-type breakdown** (Section 1) |
| Martin, Johnson, Murphey & Egerstedt, IEEE TAC 2011 | Abstraction-based motion-program synthesis for robotic marionettes from motion primitives | **NOT FOUND** — paywalled, no open mirror located | — |
| Jochum, Schultz, Johnson & Murphey, 2013/2014 book chapter (`murphey2013-robotic-puppets-autonomous-theater`) | Overview of the Georgia Tech/Northwestern robotic-marionette research programme | n/a (overview) | Confirms venue/authorship of the two papers above via its own reference list |
| Zimmermann, Poranne, Bern & Coros, "PuppetMaster", ACM TOG/SIGGRAPH 2019 (`zimmermann2019-puppetmaster`) | Trajectory-optimization control of a real marionette by a dual-arm robot (ABB YuMi) | Body-part rigidity modeled as a stiff spring, **k = 10⁴** for all experiments (Eq. 19); string tension modeled by an analogous **one-sided** spring energy term (Eq. 20) — whether the same k is reused for strings specifically could not be confirmed from the extracted PDF text (bracket/exponent formatting was lost in extraction; flagged as a caveat, not resolved by guessing) | k = 10⁴ (rigid-link spring constant, their non-dimensional units); integrator BDF-2, noted as having much less numerical damping than Implicit Euler |

No dedicated 2015–2026 "physics-based puppetry" paper beyond PuppetMaster
(2019) turned up in the searches run for this item; PuppetMaster appears to
be the most recent major result in this specific sub-field as of this
search. A citation inside Johnson & Murphey (2007) to "Kim, Zhang & Kim,
Haptic puppetry for interactive games" (the computer-graphics spring-chain
approach they argue against) was noted but not independently retrieved —
**NOT FOUND** as a standalone source in this archive; treat as third-hand
information only.

---

## 5. MuJoCo specifics

Saved: `papers/mujoco-tendon-doc.html` (full XML reference, 1.29 MB),
`papers/mujoco-modeling-doc.html`, `papers/mujoco-computation-doc.html`, and a
cleaned plain-text excerpt of the tendon/spatial section,
`papers/mujoco-tendon-spatial-section-extract.txt`. Full detail also in
`abstracts/mujoco-docs-tendon-solver-mocap.txt`.

- **Exactly the "taut pulls, slack does nothing" behaviour is a documented,
  built-in MuJoCo feature**, not something to approximate with a spring:
  quoting the docs directly, *"unactuated 2-point tendons with range or
  springlength of the form `[0 X]`, with positive X... act like a cable,
  applying force only when stretched."* Implementation: a `<tendon><spatial>`
  with two `<site>` sub-elements, `stiffness="0"`, `limited="true"`,
  `range="0 X"` where X is the string's physical length. Below length X the
  tendon applies zero force (slack); at length X the constraint solver
  enforces the length limit (taut).
- **Tendon-level attributes and defaults** (from the XML reference):
  `limited` [false/true/auto, default `"auto"`], `range` [default `"0 0"`],
  `stiffness` [default `"0"`], `damping` [default `"0"`], `springlength`
  [default `"-1 -1"`, meaning auto-computed from the reference pose], plus
  `solreflimit`/`solimplimit` (constraint solver parameters for the length
  limit specifically) and `solreffriction`/`solimpfriction` (for tendon dry
  friction, not needed here since strings are frictionless idealizations).
- **solref/solimp defaults**: `solref = "0.02 1"` → (timeconst = 0.02 s,
  dampratio = 1, i.e. critically damped by default); `solimp =
  "0.9 0.95 0.001 0.5 2"` → (d₀=0.9, d_width=0.95, width=0.001, midpoint=0.5,
  power=2). Documented stability rule: **"the timeconst parameter should be
  at least two times larger than the simulation time step"** — for the
  default timeconst this means `timestep ≤ 0.01 s`; MuJoCo's own default
  timestep (0.002 s) already satisfies this 5× over. If the snap needs to
  look stiffer/snappier, tighten `solreflimit`'s timeconst *and* the
  timestep together, keeping the 2× margin, rather than shrinking timestep
  alone.
- **Timestep and integrator advice for this stiff, fast-transient system**:
  the docs recommend **`implicitfast`** as the default integrator — a
  "strict improvement" over Euler at similar computational cost, and stable
  for velocity-dependent forces like tendon/actuator damping, which the plain
  Euler integrator does *not* handle implicitly (Euler only integrates joint
  damping implicitly, not tendon damping). The `discrete` integrator variant
  makes joint/tendon stiffness "unconditionally stable" by treating it
  implicitly in position, allowing stable simulation "far beyond the
  explicit stability limit of h ≲ 2/ω_max" for genuinely stiff tendons.
  Recommended starting timestep for this project: **0.001–0.002 s**
  (synthesized recommendation, not a literature number — see
  `data/02-dynamics-numbers.csv` for the reasoning: the free-fall/snap
  transient lasts ~0.05–0.09 s from a 10–15 cm drop's impact-to-full-stop
  window, so this timestep resolves it in tens of steps).
- **Mocap bodies**: documented as bodies with **no degrees of freedom and no
  integrated physics** — their pose (`mocap_pos`/`mocap_quat`) is set
  directly by the user every step (or interactively), while they still
  participate in collision filtering as the root of their own body group.
  Recommended use for this shot: the man's fist/fingers (the five string
  attachment points, driven frame-by-frame from the tracked hand video)
  should be **mocap bodies**, not simulated joints — the strings then connect
  each marionette fingertip/limb site to one of these five externally-driven
  mocap points.

---

## Numbers for the model

| Quantity | Value | Source file |
|---|---|---|
| Head mass fraction (M) | 6.94% body mass | `deleva1996-adjustments-zatsiorsky-seluyanov.txt` |
| Trunk mass fraction (M) | 43.46% body mass | `deleva1996-adjustments-zatsiorsky-seluyanov.txt` |
| Upper arm mass fraction (M) | 2.71% body mass | `deleva1996-adjustments-zatsiorsky-seluyanov.txt` |
| Forearm mass fraction (M) | 1.62% body mass | `deleva1996-adjustments-zatsiorsky-seluyanov.txt` |
| Hand mass fraction (M) | 0.61% body mass | `deleva1996-adjustments-zatsiorsky-seluyanov.txt` |
| Thigh mass fraction (M) | 14.16% body mass | `deleva1996-adjustments-zatsiorsky-seluyanov.txt` |
| Shank mass fraction (M) | 4.33% body mass | `deleva1996-adjustments-zatsiorsky-seluyanov.txt` |
| Foot mass fraction (M) | 1.37% body mass | `deleva1996-adjustments-zatsiorsky-seluyanov.txt` |
| All segment lengths (% stature) and radii of gyration (3-axis, % segment length) | full table | `data/02-segment-parameters.csv` (de Leva 1996 primary; Dempster-via-Winter and Fromuth-2008 cross-checks) |
| Reference ~30 cm robotic-marionette mass | 214–314 g | `icdst-marionette-robotic-manipulation.txt` (Chen/Tay/Xing/Yeo, Table 1) |
| Reference ~30 cm marionette joint count / types | 23–35 joints; predominantly 3-DOF ball ("s-joints") at main articulations, some 1-DOF revolute, one 2-DOF universal | `icdst-marionette-robotic-manipulation.txt`, Table 1 |
| Marionette joint angular ROM (deg) | **NOT FOUND** — recommend anatomical human ROM as an upper bound, by design choice | — |
| Marionette joint damping | **NOT FOUND** as a measured value — recommend starting near critical damping of each limb's own pendulum mode, then hand-tune | — |
| Free-fall time, h=0.10–0.15 m | 0.143–0.175 s | computed (kinematics, not a citation) |
| Free-fall impact speed, h=0.10–0.15 m | 1.40–1.72 m/s | computed |
| Idealized snap energy loss model | perfectly inelastic collision resolved along each string's own axis | `blacksacademy-impulsive-tensions-in-strings.txt` |
| Air-drag pendulum damping coefficient, small ball (11.5–36 mm) | 0.0056–0.0096 s⁻¹ | `salcedo2020-pendulum-resistance-coefficients.txt` |
| Implied log decrement from air drag alone (T~1s) | ~0.006–0.01 per swing (air drag is a minor contributor to settling) | computed from the row above |
| MuJoCo string/tendon recipe | 2-site spatial tendon, `stiffness=0`, `limited=true`, `range="0 X"` | `mujoco-tendon-doc.html` / `mujoco-tendon-spatial-section-extract.txt` |
| MuJoCo tendon-limit `solref` default | `0.02 1` (timeconst=0.02s, dampratio=1) | `mujoco-modeling-doc.html` |
| MuJoCo tendon-limit `solimp` default | `0.9 0.95 0.001 0.5 2` | `mujoco-modeling-doc.html` |
| MuJoCo timeconst/timestep rule | timeconst ≥ 2×timestep | `mujoco-modeling-doc.html` |
| Recommended MuJoCo timestep | 0.001–0.002 s | synthesized (see Section 5) |
| Recommended MuJoCo integrator | `implicitfast` | `mujoco-computation-doc.html` |
| Zimmermann et al. rigid-link spring constant | k = 10⁴ (their units; not directly portable) | `zimmermann2019-puppetmaster.txt` |
| Sanity check 1 | free-fall time to first taut string matches `t=√(2h/g)` for the modeled drop height | — |
| Sanity check 2 | each limb's simulated free-swing period matches the compound-pendulum formula `T=2π√(I_pivot/(m·g·d))` from its own mass/CG/radius of gyration | — |
| Sanity check 3 | every string's simulated tension ≥ 0 at all times (a string cannot push) | — |
| Sanity check 4 | in a settled hanging pose, the vector sum of all 5 string tensions equals total weight and net torque about the CM is zero | — |

## Caveats

- Dempster (1955) original report not obtained; used verbatim via Winter's
  textbook table instead (fully attributed, see `downloads-02.md`).
- Drillis & Contini (1966) segment-length-fraction table not obtained as
  numbers; substituted with a closely-agreeing modern ANSUR-derived table
  (Fromuth et al. 2008).
- No source anywhere gives a numeric marionette joint angular range or
  damping coefficient — both are flagged **NOT FOUND** and left as explicit
  design choices for whoever builds the MuJoCo model, not invented here.
- The Zimmermann et al. (2019) string-specific spring constant could not be
  disambiguated with full confidence from the rigid-link constant due to PDF
  text-extraction loss of bracket notation in their Eq. 20 — flagged rather
  than assumed identical.
- Martin et al. (2011, IEEE TAC) and the Chen et al. 2005 IEEE magazine
  article remain paywalled; only their citations and (for Martin et al.)
  secondary description could be recovered.
