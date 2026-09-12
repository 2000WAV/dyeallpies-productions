"""The marionette as a MuJoCo model: 11 rigid bodies, loose marionette joints, five strings as
limited spatial tendons from five mocap "pads" (the fingertip pads from hand_to_3d.py).

Shared by puppet_sim.py (the physics) and render_puppet.py (the neon layer) so that both see the
same figure. Every constant says where it comes from (CLAUDE.md, model code); the ones marked
ASSUMED are ranked in hand/PUPPET-MODEL.md and are replaced when references/marionette/ confirms
a number. Written 2026-09-11.

Frame: world x right, y away from the camera (toward the wall), z up; the puppet faces the camera
(its front is -y). Bodies are named by the side of the FRAME they are on (l = frame left = the
puppet's own right), since the strings are mapped by the fingers' frame positions.
"""
import numpy as np

# ---- the figure -----------------------------------------------------------------------------
P = dict(
    height=0.15,        # m. DESIGN CHOICE (rank 1 in PUPPET-MODEL.md): sized so the figure, hanging d_head under the
                        # middle fingertip, keeps its feet above the frame's bottom while the fingers loll (an 18 cm
                        # figure at 5.5 cm put the feet on the bottom edge; 13 cm left 300 px unused, 2026-09-11); the
                        # real size scales with the hand-length norm in hand_to_3d.py (0.193 m).
    mass=0.055,         # kg. references/marionette/01-marionette-construction-and-stringing.md: three built and weighed
                        # 29.5-31.2 cm marionettes at 214-314 g (Chen et al., NTU); scaled by volume to 15 cm: 27-39 g,
                        # kept at 55 g for a solid "crystal" figure (the dynamics scale with mass only through air drag).
    d_head=0.07,        # m. DESIGN CHOICE: the head-top site sits this far under the middle fingertip pad at the
                        # reference frame; sets every string's length. It must leave every string slack when the
                        # crumpled figure is released at the palm as the fist opens (puppet_sim.py prints the slack).
    ref_frame=120,      # a typical mid-shot hand ("wide, drifting down", hand/PLAN.md timeline): strings just taut
                        # there, so the load is shared in the long phase and the higher snap-open hand lifts the figure
    # segment masses, fraction of total: de Leva 1996 J Biomech 29(9) Table 4, male, confirmed against
    # references/marionette/data/02-segment-parameters.csv (2026-09-11; sum = 1.000).
    m_frac=dict(head=0.0694, trunk=0.4346, upper_arm=0.0271, forearm=0.0162, hand=0.0061, thigh=0.1416, shank=0.0433, foot=0.0137),
    # segment lengths / landmark heights, fraction of stature: Drillis & Contini 1966 (the classic figure, reproduced
    # in Winter 2009 Fig. 4.1), cross-checked against Fromuth 2008 (ANSUR) in 02-segment-parameters.csv: shoulder
    # 0.820, hip 0.528, knee 0.284, ankle 0.038, forearm 0.151, upper arm 0.193 (ours 0.186 is de Leva's side).
    l_frac=dict(shoulder_h=0.818, hip_h=0.530, knee_h=0.285, ankle_h=0.039, upper_arm=0.186, forearm=0.146, hand=0.108,
                biacromial=0.259, hip_w=0.191, head_top=1.000, chin=0.870),
    # the trunk split (fraction of the trunk mass) into a pelvis body and a chest body: de Leva's lower trunk vs
    # middle + upper trunk (0.1117 / 0.4346 = 0.257; Table 4, FROM MEMORY: the CSV carries the whole trunk only).
    pelvis_frac=0.257,
    # joint ranges, degrees. DESIGN CHOICE: references/marionette/02-puppet-body-dynamics.md found no numeric
    # range for marionette joints anywhere (leather-strap knees, cloth stops at Yamane 2003's shoulders); human
    # ranges are the upper bound. Cone half-angles for the ball joints, flexion for the hinges.
    j_range=dict(hip=70, knee=140, shoulder=110, elbow=140, neck=40, waist=30),
    # joint damping: 02 found no measured value and recommends starting from the critical damping of each joint's
    # own pendulum mode; for a 13 cm figure's thigh (4.3 g, 3.2 cm) that is c = 2 sqrt(I m g d) ~ 5e-5 N m s,
    # and the arms are lighter still. 5e-5 for all joints (near critical for the legs, over for the arms) plus a
    # Coulomb term so the small residual motions die within seconds, as a real marionette's do (02: air drag
    # alone gives 0.006-0.01 per swing and cannot settle it).
    j_damping=5e-5,     # N m s / rad
    j_friction=5e-6,    # N m, Coulomb friction at every joint (ASSUMED; a string-loop joint has some)
    # air: standard values, MuJoCo's built-in inertia-box fluid model gives drag and hence the swing's decay
    air_density=1.2,    # kg/m^3, air at 20 C (CRC Handbook)
    air_viscosity=1.8e-5,   # Pa s, air at 20 C (CRC Handbook)
    # strings
    string_solref="0.004 1",    # MuJoCo tendon-limit constraint: time constant 4 ms (>= 2 x timestep, MuJoCo docs "Solver
                                # parameters"), damping ratio 1: a thread with very little give, no bounce of its own
    string_damping=0.002,       # N s / m, ASSUMED tiny: the thread's own air drag; pending 03
    timestep=1.0 / 1200,        # s. hand/PLAN.md said 600 Hz; 1200 Hz resolves the snap's impulse better at no cost
)

# the five fingers (hand_to_3d order: thumb, index, middle, ring, pinky) -> attachment sites.
# ASSUMED mapping (hand/PLAN.md decision list, adapted): the middle finger (lowest, central) carries the head
# so the head string is the short vertical one, the index and ring carry the shoulders (spreading them levels
# or tilts the shoulders), the thumb and pinky carry the hands (spreading them opens the arms). Pending
# references/marionette/01's recommended mapping; a different mapping is one edit here.
STRINGS = [("thumb", "s_hand_l"), ("index", "s_shoulder_l"), ("middle", "s_head_top"), ("ring", "s_shoulder_r"), ("pinky", "s_hand_r")]

BODIES = ["pelvis", "chest", "head", "upper_arm_l", "forearm_l", "upper_arm_r", "forearm_r", "thigh_l", "shank_l", "thigh_r", "shank_r"]


def build_xml(p=P):
    H = p["height"]; M = p["mass"]; f = p["m_frac"]; L = p["l_frac"]; J = p["j_range"]
    sh, hh, kh, ah = L["shoulder_h"] * H, L["hip_h"] * H, L["knee_h"] * H, L["ankle_h"] * H
    ua, fa, ha = L["upper_arm"] * H, L["forearm"] * H, L["hand"] * H
    sw, hw = L["biacromial"] * H / 2, L["hip_w"] * H / 2 * 0.7   # hip joint spacing a bit inside the hip width
    waist = hh + 0.07 * H
    m_pelvis = M * f["trunk"] * p["pelvis_frac"]; m_chest = M * f["trunk"] * (1 - p["pelvis_frac"])
    # geometry radii (mannequin proportions, a design choice: an artist's mannequin is rounder than a person)
    r_ua, r_fa, r_th, r_sh = 0.026 * H, 0.021 * H, 0.034 * H, 0.026 * H
    d = p["j_damping"]; fr = p["j_friction"]

    def capsule(name, z_len, r, mass, extra=""):
        # a capsule hanging from the body origin down -z
        return f'<geom name="{name}" type="capsule" fromto="0 0 0 0 0 {-z_len:.5f}" size="{r:.5f}" mass="{mass:.6f}" {extra}/>'

    def arm(side, sx):   # a child of the chest body, whose origin is at the waist (the arms hung 8 cm too high before 2026-09-11's first render)
        return f"""
      <body name="upper_arm_{side}" pos="{sx:.5f} 0 {sh - waist:.5f}">
        <joint name="shoulder_{side}" type="ball" limited="true" range="0 {J['shoulder']}" damping="{d}" frictionloss="{fr}"/>
        {capsule(f"g_upper_arm_{side}", ua, r_ua, M * f['upper_arm'])}
        <body name="forearm_{side}" pos="0 0 {-ua:.5f}">
          <joint name="elbow_{side}" type="hinge" axis="-1 0 0" limited="true" range="0 {J['elbow']}" damping="{d}" frictionloss="{fr}"/>
          {capsule(f"g_forearm_{side}", fa, r_fa, M * f['forearm'])}
          <geom name="g_hand_{side}" type="ellipsoid" pos="0 0 {-(fa + ha * 0.45):.5f}" size="{0.5 * ha * 0.55:.5f} {0.5 * ha * 0.28:.5f} {0.5 * ha:.5f}" mass="{M * f['hand']:.6f}"/>
          <site name="s_hand_{side}" pos="0 0 {-(fa + ha * 0.45):.5f}" size="0.002"/>
        </body>
      </body>"""

    def leg(side, sx):
        return f"""
      <body name="thigh_{side}" pos="{sx:.5f} 0 0">
        <joint name="hip_{side}" type="ball" limited="true" range="0 {J['hip']}" damping="{d}" frictionloss="{fr}"/>
        {capsule(f"g_thigh_{side}", hh - kh, r_th, M * f['thigh'])}
        <body name="shank_{side}" pos="0 0 {-(hh - kh):.5f}">
          <joint name="knee_{side}" type="hinge" axis="1 0 0" limited="true" range="0 {J['knee']}" damping="{d}" frictionloss="{fr}"/>
          {capsule(f"g_shank_{side}", kh - ah, r_sh, M * f['shank'])}
          <geom name="g_foot_{side}" type="ellipsoid" pos="0 {-0.03 * H:.5f} {-(kh - ah) - 0.015 * H:.5f}" size="{0.02 * H:.5f} {0.055 * H:.5f} {0.015 * H:.5f}" mass="{M * f['foot']:.6f}"/>
        </body>
      </body>"""

    pads = "\n".join(f'    <body name="pad_{n}" mocap="true" pos="0 0.33 0.1"><site name="s_pad_{n}" size="0.002"/></body>' for n, _ in STRINGS)
    tendons = "\n".join(f'    <spatial name="str_{n}" limited="true" range="0 1" damping="{p["string_damping"]}" solreflimit="{p["string_solref"]}" width="0.0005" rgba="0 1 1 1"><site site="s_pad_{n}"/><site site="{s}"/></spatial>' for n, s in STRINGS)

    xml = f"""<mujoco model="marionette">
  <option timestep="{p['timestep']:.8f}" gravity="0 0 -9.81" density="{p['air_density']}" viscosity="{p['air_viscosity']}" integrator="implicitfast"/>
  <visual><global offwidth="2160" offheight="3840"/><quality offsamples="0" shadowsize="1024"/><map znear="0.05" zfar="2"/></visual>
  <default><geom contype="0" conaffinity="0"/><site type="sphere"/><joint solreflimit="0.004 1"/></default>
  <worldbody>
    <camera name="cam" pos="0 0 0" quat="0.70710678 0.70710678 0 0" fovy="65"/>
{pads}
    <body name="pelvis" pos="0 0.33 0">
      <freejoint name="root"/>
      <geom name="g_pelvis" type="ellipsoid" pos="0 0 {0.035 * H:.5f}" size="{0.085 * H:.5f} {0.055 * H:.5f} {0.05 * H:.5f}" mass="{m_pelvis:.6f}"/>
{leg("l", -hw)}
{leg("r", hw)}
      <body name="chest" pos="0 0 {waist - hh:.5f}">
        <joint name="waist" type="ball" limited="true" range="0 {J['waist']}" damping="{d}" frictionloss="{fr}"/>
        <geom name="g_chest" type="ellipsoid" pos="0 0 {(sh - waist) * 0.55:.5f}" size="{0.105 * H:.5f} {0.06 * H:.5f} {(sh - waist) * 0.6:.5f}" mass="{m_chest:.6f}"/>
        <site name="s_shoulder_l" pos="{-sw * 0.9:.5f} 0 {sh - waist + 0.01 * H:.5f}" size="0.002"/>
        <site name="s_shoulder_r" pos="{sw * 0.9:.5f} 0 {sh - waist + 0.01 * H:.5f}" size="0.002"/>
        <body name="head" pos="0 0 {sh - waist + 0.02 * H:.5f}">
          <joint name="neck" type="ball" limited="true" range="0 {J['neck']}" damping="{d}" frictionloss="{fr}"/>
          <geom name="g_neck" type="capsule" fromto="0 0 0 0 0 {0.03 * H:.5f}" size="{0.02 * H:.5f}" mass="{M * f['head'] * 0.1:.6f}"/>
          <geom name="g_head" type="ellipsoid" pos="0 0 {0.03 * H + 0.065 * H:.5f}" size="{0.055 * H:.5f} {0.062 * H:.5f} {0.07 * H:.5f}" mass="{M * f['head'] * 0.9:.6f}"/>
          <site name="s_head_top" pos="0 0 {0.03 * H + 0.135 * H:.5f}" size="0.002"/>
        </body>
{arm("l", -sw)}
{arm("r", sw)}
      </body>
    </body>
  </worldbody>
  <tendon>
{tendons}
  </tendon>
</mujoco>"""
    return xml


# the crumpled pose the puppet has in the fist (rank: cosmetic; it unfolds in the first 0.2 s of the drop)
CRUMPLED = dict(hip_l=("x", 100), hip_r=("x", 95), knee_l=110, knee_r=120, shoulder_l=("x", -70), shoulder_r=("x", -60),
                elbow_l=100, elbow_r=115, neck=("x", -35), waist=("x", 25))


def quat_axis(axis, deg):
    a = np.radians(deg) / 2
    v = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[axis]
    return np.array([np.cos(a), *(np.sin(a) * np.array(v))])


def set_pose(model, data, pose, mujoco):
    for jn, val in pose.items():
        j = model.joint(jn); adr = j.qposadr[0]
        if j.type[0] == mujoco.mjtJoint.mjJNT_BALL:
            data.qpos[adr:adr + 4] = quat_axis(*val)
        else:
            data.qpos[adr] = np.radians(val)


if __name__ == "__main__":
    import mujoco
    m = mujoco.MjModel.from_xml_string(build_xml())
    d = mujoco.MjData(m); mujoco.mj_forward(m, d)
    tot = sum(m.body_mass[m.body(b).id] for b in BODIES)
    print(f"bodies {m.nbody - 1 - len(STRINGS)} puppet + {len(STRINGS)} pads; puppet mass {tot*1000:.1f} g (target {P['mass']*1000:.0f} g); tendons {m.ntendon}; joints {m.njnt}")
    for b in BODIES: print(f"  {b:12s} {m.body_mass[m.body(b).id]*1000:6.2f} g")
    z = [d.site_xpos[m.site(s).id][2] - d.xpos[m.body('pelvis').id][2] for s in ["s_head_top", "s_shoulder_l", "s_hand_l"]]
    print("rest pose: head top / shoulder / hand heights above the pelvis origin (m):", np.round(z, 4), "; feet at", round(float(d.geom_xpos[m.geom('g_foot_l').id][2] - d.xpos[m.body('pelvis').id][2]), 4))
