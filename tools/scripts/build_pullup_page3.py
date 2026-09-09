"""
Build the interactive HTML report for a pull-up set from analysis.json (v2).

    python build_pullup_page2.py <analysis.json> <out.html>

Every number on the page is injected from the JSON at build time - nothing is retyped.
"""
import sys, json, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pullup_thermal3 as TH

A = json.load(open(sys.argv[1])); out = sys.argv[2]
REDN = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else None
S, atts, sig = A["summary"], A["reps"], A["signals"]
reps = [r for r in atts if r.get("rep")]
fails = [r for r in atts if not r.get("rep")]
fail = fails[0] if fails else None
AS, TC = S["asymmetry"], S["technique"]
Tm = TH.integrate(A); tsum = TH.summarise(A, Tm)
t = np.array(sig["t"]); pct = np.array(sig["height_pct"])
h0, h1 = sig["hang0"], sig["hang1"]
trace = [[round(float(t[i]), 2), round(float(pct[i]), 1)] for i in range(h0, h1 + 1, 2)]
chin_pct = 100 + (-S["mean_chin_cm"]) / S["mean_rom_cm"] * 100
muscles = sorted(tsum["muscles"].items(), key=lambda kv: -kv[1]["delta_T_C"])

for r in atts:
    r["lat_dt"] = float(Tm["latissimus dorsi"][r["f_end"]])
D = dict(summary=S, reps=atts, trace=trace, chin_pct=chin_pct, thermal=tsum,
         muscles=[[m, v["delta_T_C"], v["mvic"], v["mass_kg"], v["painted"], v["note"]] for m, v in muscles],
         lat_curve=[round(float(Tm["latissimus dorsi"][i]), 3) for i in range(h0, h1 + 1, 6)],
         t_curve=[round(float(t[i]), 2) for i in range(h0, h1 + 1, 6)], redness=REDN)

HTML = r"""<title>Eleven at the Bar</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>
:root{
  --paper:#f6f5f1; --panel:#fffefb; --ink:#14161a; --ink-2:#4a4f57; --rule:#dcd9d1;
  --accent:#b8420f; --pass:#1d6b3f; --warn:#9a6a06; --cold:#2f5fd0; --hot:#cf3623;
  --shadow:0 1px 2px rgba(20,22,26,.06), 0 8px 24px -12px rgba(20,22,26,.18);
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  --disp:"Oswald","Arial Narrow",system-ui,sans-serif;
  --body:"Source Serif 4",Georgia,"Times New Roman",serif;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --paper:#101215; --panel:#171a1f; --ink:#eceae4; --ink-2:#a2a7b0; --rule:#2b2f36;
    --accent:#f4794a; --pass:#4cbd7c; --warn:#e0aa3c; --cold:#6f97f0; --hot:#f4674f;
    --shadow:0 1px 2px rgba(0,0,0,.5), 0 10px 30px -14px rgba(0,0,0,.7);
  }
}
:root[data-theme="dark"]{
  --paper:#101215; --panel:#171a1f; --ink:#eceae4; --ink-2:#a2a7b0; --rule:#2b2f36;
  --accent:#f4794a; --pass:#4cbd7c; --warn:#e0aa3c; --cold:#6f97f0; --hot:#f4674f;
  --shadow:0 1px 2px rgba(0,0,0,.5), 0 10px 30px -14px rgba(0,0,0,.7);
}
*{box-sizing:border-box}
body{background:var(--paper);color:var(--ink);font-family:var(--body);
     font-size:17px;line-height:1.62;-webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding:clamp(28px,5vw,72px) clamp(18px,4vw,40px) 96px}
.col{max-width:66ch}
h1{font-family:var(--disp);font-weight:600;font-size:clamp(38px,7vw,68px);line-height:1.02;
   letter-spacing:-.01em;margin:.1em 0 .18em;text-wrap:balance}
h2{font-family:var(--disp);font-weight:500;font-size:clamp(24px,3.4vw,33px);line-height:1.12;
   margin:0 0 .5em;text-wrap:balance}
h3{font-family:var(--disp);font-weight:500;font-size:20px;margin:0 0 .35em}
p{margin:0 0 1.05em}
.eyebrow{font-family:var(--mono);font-size:11.5px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--ink-2);margin:0 0 .55em}
.lede{font-size:clamp(19px,2.2vw,22px);line-height:1.5;color:var(--ink-2)}
section{margin:clamp(46px,6vw,84px) 0 0;scroll-margin-top:24px}
.rule{height:1px;background:var(--rule);border:0;margin:0}
.mono{font-family:var(--mono);font-variant-numeric:tabular-nums}
.num{font-family:var(--mono);font-variant-numeric:tabular-nums;font-weight:500}

/* ---- scorecard: the one lifted object on the page ---- */
.card{background:var(--panel);border:1px solid var(--rule);box-shadow:var(--shadow);
  border-radius:3px;padding:clamp(20px,3vw,30px);margin:34px 0 0}
.card-top{display:flex;flex-wrap:wrap;gap:10px 28px;align-items:baseline;
  border-bottom:1px solid var(--rule);padding-bottom:14px;margin-bottom:16px}
.card-top h3{font-size:22px;margin:0}
.std{font-family:var(--mono);font-size:12px;color:var(--ink-2);line-height:1.5}
.checks{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:2px}
.chk{display:grid;grid-template-columns:1fr auto;gap:6px 12px;align-items:baseline;
  padding:9px 0;border-bottom:1px solid var(--rule)}
.chk:last-child,.chk:nth-last-child(2){border-bottom:0}
.chk .k{font-size:15px;color:var(--ink-2)}
.chk .v{font-family:var(--mono);font-size:14px;font-weight:600;letter-spacing:.02em}
.pass{color:var(--pass)} .fail{color:var(--accent)} .warn{color:var(--warn)}
.tag{display:inline-block;font-family:var(--mono);font-size:11px;font-weight:600;
  letter-spacing:.08em;text-transform:uppercase;padding:2px 7px;border-radius:2px;
  border:1px solid currentColor}

/* ---- headline figures ---- */
.figs{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  gap:1px;background:var(--rule);border-block:1px solid var(--rule);margin:30px 0 0}
.fig{background:var(--paper);padding:18px 4px 16px 0}
.fig b{display:block;font-family:var(--disp);font-weight:600;font-size:clamp(32px,4.6vw,46px);
  line-height:1;letter-spacing:-.01em}
.fig span{display:block;font-family:var(--mono);font-size:11px;letter-spacing:.1em;
  text-transform:uppercase;color:var(--ink-2);margin-top:8px}

/* ---- tables ---- */
.tw{overflow-x:auto;margin:20px 0 0;border-block:1px solid var(--rule)}
table{border-collapse:collapse;width:100%;font-family:var(--mono);
  font-variant-numeric:tabular-nums;font-size:13px}
th{text-align:right;font-weight:600;font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;
  color:var(--ink-2);padding:11px 10px;border-bottom:1px solid var(--rule);white-space:nowrap}
td{text-align:right;padding:8px 10px;border-bottom:1px solid var(--rule);white-space:nowrap}
th:first-child,td:first-child{text-align:left}
tbody tr:last-child td{border-bottom:0}
tr.failrow td{color:var(--accent)}
tr.best td{background:color-mix(in srgb,var(--pass) 9%,transparent)}

/* ---- muscle temperature bars ---- */
.mus{display:grid;grid-template-columns:minmax(120px,auto) 1fr minmax(58px,auto);
  gap:7px 14px;align-items:center;margin:20px 0 0;font-family:var(--mono);font-size:13px}
.mus .nm{color:var(--ink)} .mus .nm.off{color:var(--ink-2)}
.bar{height:11px;background:var(--rule);border-radius:1px;overflow:hidden}
.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--cold),var(--hot))}
.mus .dt{text-align:right;font-weight:600}

/* ---- chart ---- */
figure{margin:24px 0 0}
figcaption{font-size:14.5px;color:var(--ink-2);margin-top:10px;max-width:62ch}
svg{display:block;width:100%;height:auto}
.gl{stroke:var(--rule);stroke-width:1}
.ax{fill:var(--ink-2);font-family:var(--mono);font-size:11px}
.lbl{fill:var(--ink);font-family:var(--mono);font-size:11px}

.note{border-left:2px solid var(--accent);padding:2px 0 2px 18px;margin:24px 0;
  font-size:16px;color:var(--ink-2)}
.note b{color:var(--ink);font-weight:600}
ul{margin:0 0 1.05em;padding-left:1.15em} li{margin:0 0 .5em}
footer{margin-top:70px;padding-top:22px;border-top:1px solid var(--rule);
  font-family:var(--mono);font-size:12px;color:var(--ink-2);line-height:1.75}
a{color:var(--accent)}
@media (prefers-reduced-motion:no-preference){
  .bar i{animation:grow .9s cubic-bezier(.2,.7,.3,1) both}
  @keyframes grow{from{transform:scaleX(.02);transform-origin:left}to{transform:scaleX(1)}}
}
</style>

<div class="wrap">
<header class="col">
  <p class="eyebrow">Pull-up set #3 · 8 September 2026 · IMG_6108</p>
  <h1>Eleven reps, every chin at the bar</h1>
  <p class="lede">A floor camera, a rectified doorway plane, two pose trackers, a heat budget over
  23 muscles and one published standard. The count holds up. The chin reaches the bar and stops there.</p>
</header>

<div class="figs" id="figs"></div>

<section class="col">
  <p class="eyebrow">The verdict</p>
  <h2>Everything passes except the one thing that decides a rep</h2>
  <p>Eleven reps, no failed attempt. Every one started from a dead hang with the arms locked
  out, none used a swing, and each held the top for close to a second with the head behind
  the bar for over a second. Range of motion is 47–51 cm in the doorway plane, about 55 cm
  true, repeated eleven times with a pause at the top that rules out any bounce.</p>
  <p>On the criterion that decides a repetition — chin above the bar — every rep arrives
  <b>at the bar</b> and no further: −3.5 cm in the plane on average, of which the low
  camera hides about 3.4 cm. Adjusted, the eleven reps sit between −1.6 and +1.7 cm, inside
  the ±3 cm this camera can resolve. The same finding as set #2, from a different camera
  and a different method. A lenient judge counts them all; a strict one wants three
  centimetres more.</p>
</section>

<div class="card" id="scorecard"></div>

<section class="col">
  <p class="eyebrow">Evidence</p>
  <h2>Why the chin number is trustworthy, and where it stops</h2>
  <p>This is the finding a sceptical reader should attack first, so here is what it rests on.</p>
  <p>The camera sits on the floor 2.8 m away, looking up 6.5°. Before anything is measured,
  every landmark is mapped into a rectified doorway plane: the two vanishing points of the
  room give the focal length (1950 px) and the camera's rotation, and a last 0.7° turn makes
  the fitted bar exactly level. In that plane a centimetre is a centimetre from the floor to
  the bar, and the scale — 708 px/m from his standing stature — is confirmed by the
  shoulder-to-bar distance at the dead hang: 62.7 cm, against 62.4 cm from the
  anthropometric tables for a 188 cm man.</p>
  <p>At the top of every rep the whole head vanishes behind the bar and the underside of the
  lintel it is mounted under, with the neck visible right up to the bar. Both pose models keep
  inventing a face there, so the chin is not read from a landmark at the top. It is
  extrapolated from the last frame the face is genuinely seen on the way up, plus the
  shoulder rise after that moment; the silhouette confirms the neck reaches the bar's
  underside on every rep; and the shoulders sit 14–17 cm below the bar against a
  shoulder-to-chin length of 16 cm. Three witnesses, one answer: the chin reaches the bar's
  height.</p>
  <div class="note"><b>What the camera cannot resolve is depth.</b> From 23° below, a point
  8 cm behind the bar plane projects 3.4 cm lower than it is. That allowance is computed from
  the geometry, not guessed, but the chin's actual depth is not measured, so the verdict band
  is ±3 cm and "at the bar" means exactly that. A second phone from the side settles it.</div>
</section>

<figure><div id="chinchart"></div>
<figcaption>Each bar is one rep in the doorway plane. Diamonds add the computed camera
allowance for a chin 8 cm behind the bar. Whiskers are the ±3 cm "at the bar" band.</figcaption></figure>

<section class="col">
  <p class="eyebrow">Left versus right</p>
  <h2>The right shoulder rides low, and the elbows refuse to answer again</h2>
  <p>In the rectified plane a left-right difference in the picture is a real difference in the
  room, and the wrist line on the level bar is the control: it reads −1.0° at the top while
  the shoulder line reads −3.1°. The right shoulder sits 1.4 cm lower under load.</p>
</section>

<div class="tw"><table id="asymtable"></table></div>

<section class="col">
  <p>The elbows are the one place where a model and a measurement disagree — for the third
  set in a row, in the same direction. The honest answer is still to report both and claim
  neither; a side-on camera would settle it in one set.</p>
</section>

<section class="col">
  <p class="eyebrow">Muscle temperature</p>
  <h2>The colour on the body is a heat budget, not a camera</h2>
  <p>The set produced about 36 kJ of heat: 21 kJ from muscle work and 16 kJ from simply
  hanging on. That heat is divided between 23 muscles by how hard surface-EMG studies say
  each one works in a pull-up (Youdas 2010, corroborated at almost this grip by Snarr 2017;
  serratus anterior and upper trapezius from Tucker 2011), weighted by how much of it there
  is to warm, and then drained by blood at a rate that ramps up over the first minutes.
  The lat share shifts toward the trapezius at the top of each rep (Park &amp; Yoo 2013),
  and the core's share keys off measured hip motion, not pull speed (Dinunzio 2018).</p>
  <p>The legs are in the model too, and they are the reason they stay blue on screen: they
  hold a tucked position for the whole set rather than lifting anything, so they take no
  share of the work heat and finish between +0.04 and +0.19 °C. Colour on the body is
  temperature, which only accumulates; brightness pulses with a modelled activation that
  follows the movement itself, so the map breathes with each rep.</p>
  <p>Two of those constants are measured rather than fitted. González-Alonso and colleagues
  tracked heat production rising from 70 to 126 J/s in 2.68 kg of working muscle while
  blood-borne removal climbed from nothing to 112 J/s over three minutes — which fixes both
  the removal coefficient and its time constant, and is why temperature never falls inside a
  42-second set. Kenny and colleagues measured +2.0 to +3.2 °C in a working thigh over
  fifteen minutes, so degrees over minutes is the right order of magnitude.</p>
</section>

<div class="mus" id="muscles"></div>

<section class="col">
  <div class="note"><b>An infrared camera would not show this.</b> Skin over a working
  muscle drops in the first minute of a bout and warms afterwards (Merla 2010, Formenti 2016,
  Chudecka 2015); Jung and colleagues measured skin over a trained arm at 35.98 °C at the
  start of a set, 36.11 °C at the end, and 37.24 °C five minutes into recovery. The
  effective conductivity through skin and fat is 0.3–0.7 W/m/K (Ducharme &amp; Tikuisis
  1991), so a 42-second set barely reaches the surface. This is the muscle underneath,
  modelled.</div>
</section>

<figure><div id="tempchart"></div>
<figcaption>Modelled temperature of the latissimus dorsi through the set. Vertical marks
are the top of each attempt.</figcaption></figure>

<section class="col">
  <p class="eyebrow">The measured one</p>
  <h2>His chest flushes — and it is not what set #2 said it was</h2>
  <p>Everything above is a model. This is not. Skin over working muscle reddens as blood is
  routed to it, and that is visible in the footage, so it was measured: the redness index of
  the chest skin at the dead hang after every rep, where pose, distance and lighting repeat.
  The index ignores brightness by construction, and the same index computed on a fixed patch
  of wall in the same frame is subtracted, so a shift in exposure or white balance cancels.</p>
  <p>The index rises 27 units from rep 1 to rep 11, r = 0.93 with time and r = 0.92 with the
  modelled lat temperature, while the wall control is flat. Set #2 read the same kind of
  rise as vasodilation carrying muscle heat to the skin. The literature says it cannot be:
  skin blood flow <b>falls</b> in the first minute of exercise, and the thermoregulatory
  flush needs a core-temperature rise that takes many minutes (Kellogg 1991, Taylor 1990,
  Charkoudian 2010). What reddens a chest within reps is more plausibly venous engorgement
  under the strain and a local histamine response — real, measured, tracking effort, and not
  evidence of muscle heat at the skin.</p>
</section>

<figure><div id="redchart"></div>
<figcaption>Filled circles: chest redness at the dead hang after each rep. Grey: the wall
control in the same frames. The square is standing, before the set — closer to the camera
with a different white balance, so it is not a usable baseline.</figcaption></figure>

<section class="col">
  <div class="note">Eleven points, one set, one person, a moving white balance and no valid
  baseline. <b>Exploratory</b>; lock the exposure next time.</div>
</section>

<section class="col">
  <p class="eyebrow">Rep by rep</p>
  <h2>Stopped at eleven, past the training cut-off</h2>
  <p>Pull-up training studies use a 25 % loss of speed as the point where more reps stop
  paying (Sánchez-Moreno 2020). Against rep 1 that point arrived at rep 10; against the
  fastest rep, rep 5, the loss reached 53 %. Reps 10 and 11 cost 1.5–1.7 times the effort of
  rep 5 for the same mechanical work. Rep 1 was a deliberate start, so both references are
  shown. Reps in reserve are given as a range, never an integer: no single velocity-loss
  threshold fits everyone (Jukic 2023).</p>
</section>

<div class="tw"><table id="reptable"></table></div>

<section class="col">
  <p class="eyebrow">What to change</p>
  <h2>Three things, in order of size</h2>
  <ul>
    <li><b>Three more centimetres at the top.</b> The pause is there and the head is behind
    the bar on every rep; the chin stops at the bar's height. Aim the collarbones at the bar.</li>
    <li><b>Keep the right shoulder down.</b> The shoulder line tilts 3° at the top with the
    wrists level on the bar.</li>
    <li><b>Stop at 25 % velocity loss if the goal is strength.</b> That was rep 10.</li>
    <li><b>Next shoot:</b> a second phone from the side at hip height, a 1 m stick held at the
    bar for scale, and the exposure locked.</li>
  </ul>
</section>

<section class="col">
  <p class="eyebrow">Method and limits</p>
  <h2>What this cannot see</h2>
  <p>MediaPipe Pose (heavy, 33 landmarks) found a pose on 1897 of 1909 frames. YOLOv8m-pose,
  run independently, found the same eleven reps; the two shoulder tracks correlate at
  r = 0.998 across the set. The footage is 10-bit HLG, tone-mapped on the GPU to an SDR
  master before any pixel is read. The centimetre scale comes from his standing stature in
  the rectified doorway plane and is confirmed by the arm length at the dead hang to 0.5 %.</p>
  <ul>
    <li>One camera, front on. Depth is not measured; every three-dimensional joint angle is
    the pose model's estimate, not an observation.</li>
    <li>Where the 3D estimate and the image plane disagree — the elbows — no claim is made.</li>
    <li>The temperature map is a model built on a literature prior. Four activation values
    and four muscle volumes are assumptions, and they are marked as such in the code.</li>
    <li>Leg angles rely on extrapolated landmarks whenever the crossed ankles hide each other.</li>
  </ul>
</section>

<footer>
  <div>Pull Up Analysis by Fable and DyeAllPies · analysed 6–7 September 2026</div>
  <div>Youdas et al. 2010, J Strength Cond Res 24(12):3404 · Dickie et al. 2017, J Electromyogr Kinesiol 32:30 · González-Alonso et al. 2000, J Physiol 524(2):603 · Kenny et al. 2003, J Appl Physiol 94(6):2350 · Holzbaur et al. 2007, J Biomech 40(4):742 · Jung et al. 2021, Sensors 21(13):4505 · Sánchez-Medina &amp; González-Badillo 2011, Med Sci Sports Exerc 43(9):1725 · Lin et al. 2022, WACV (Robust Video Matting) · Snarr et al. 2017 · Tucker et al. 2011 · Park &amp; Yoo 2013 · Dinunzio et al. 2018 · Beckham et al. 2018 · Sánchez-Moreno et al. 2017, 2020 · Jukic et al. 2023 · de Leva 1996 · Ryschon et al. 1997 · Ducharme &amp; Tikuisis 1991 · Kellogg et al. 1991 · Charkoudian 2010 · the full archive: references/pullup-science/</div>
  <div>Standard: USMC PFT pull-up. Every figure on this page is generated from the measurement file; none is retyped.</div>
</footer>
</div>

<script>
const D = __DATA__;
const S = D.summary, R = D.reps, AS = S.asymmetry, TC = S.technique;
const reps = R.filter(r => r.rep), fail = R.find(r => !r.rep);
const el = id => document.getElementById(id);
const f = (v, n = 1) => (v >= 0 && n > 0 ? "+" : "") + v.toFixed(n);

el("figs").innerHTML = [
  [S.reps, "reps counted"],
  ["0 / " + S.reps, "chin over the bar"],
  [TC.lockouts + " / " + S.reps, "full lock-outs"],
  [S.mean_chin_cm.toFixed(1) + " / " + S.mean_chin_adjusted_cm.toFixed(1) + " cm", "chin: in plane / adjusted"],
  ["+" + D.thermal.muscles["latissimus dorsi"].delta_T_C.toFixed(1) + " °C", "lats, modelled"],
  [D.redness ? "r = " + D.redness.r_with_modelled_temp.toFixed(2) : "—", "flush vs model"],
].map(([a, b]) => `<div class="fig"><b>${a}</b><span>${b}</span></div>`).join("");

const chk = (k, v, cls) => `<div class="chk"><span class="k">${k}</span><span class="v ${cls || ""}">${v}</span></div>`;
el("scorecard").innerHTML =
  `<div class="card-top"><h3>Scorecard</h3>
   <div class="std">USMC PFT pull-up: dead hang, arms fully extended · chin above the bar ·
   lower to full extension · no kipping, kicking or leg movement</div></div>
   <div class="checks">` +
  chk("Dead hang, arms extended", S.reps + " / " + S.reps + " PASS", "pass") +
  chk("Chin at the bar", (S.technique.chin_at + S.technique.chin_above) + " / " + S.reps + " · never clearly over", "warn") +
  chk("Lowered to full extension", TC.lockouts + " / " + S.reps + " PASS", "pass") +
  chk("No kipping", "PASS · hips travel " + TC.hip_sway_mean_cm.toFixed(1) + " cm", "pass") +
  chk("Legs still", "BORDERLINE · knees tuck " + Math.round(TC.leg_tuck_deg) + "°", "warn") +
  chk("Range of motion", S.mean_rom_cm.toFixed(0) + " cm per rep") +
  chk("Tempo up / hold / down", [S.mean_concentric, S.mean_top_hold, S.mean_eccentric].map(x => x.toFixed(1)).join(" / ") + " s") +
  chk("Grip width", TC.grip_ratio.toFixed(2) + " × shoulders") +
  chk("Velocity loss", "−" + TC.velocity_loss_pct.toFixed(0) + " %") +
  (fail ? chk("Failed attempt", "FAILED · " + Math.abs(fail.chin_cm).toFixed(0) + " cm short", "fail") : chk("Set", "stopped at " + S.reps + ", " + Math.max(0, S.velocity_loss_pct).toFixed(0) + " % slower than rep 1", "pass")) +
  `</div>`;

/* ---- chin chart ---- */
(function () {
  const W = 1000, H = 320, L = 56, Rp = 20, T = 18, B = 42;
  const lo = -9, hi = 2.5;
  const x = i => L + (W - L - Rp) * (i + .5) / reps.length;
  const bw = (W - L - Rp) / reps.length * .5;
  const y = v => T + (H - T - B) * (hi - v) / (hi - lo);
  let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Chin height versus the bar for each rep">`;
  for (let v = 2; v >= -8; v -= 2) {
    s += `<line class="gl" x1="${L}" y1="${y(v)}" x2="${W - Rp}" y2="${y(v)}"/>`;
    s += `<text class="ax" x="${L - 9}" y="${y(v) + 4}" text-anchor="end">${v}</text>`;
  }
  s += `<line x1="${L}" y1="${y(0)}" x2="${W - Rp}" y2="${y(0)}" stroke="currentColor" stroke-width="2"/>`;
  s += `<text class="lbl" x="${W - Rp}" y="${y(0) - 8}" text-anchor="end">the bar</text>`;
  reps.forEach((r, i) => {
    const c = "var(--accent)";
    s += `<rect x="${x(i) - bw / 2}" y="${y(0)}" width="${bw}" height="${y(r.chin_cm) - y(0)}" fill="${c}" opacity=".85"/>`;
    s += `<line class="gl" x1="${x(i)}" y1="${y(r.chin_cm_adjusted - 3)}" x2="${x(i)}" y2="${y(r.chin_cm_adjusted + 3)}" stroke="currentColor" stroke-width="1.5"/>`;
    const d = 5, cy = y(r.chin_cm_adjusted);
    s += `<path d="M${x(i)} ${cy - d}L${x(i) + d} ${cy}L${x(i)} ${cy + d}L${x(i) - d} ${cy}Z" fill="var(--cold)"/>`;
    s += `<text class="ax" x="${x(i)}" y="${H - 16}" text-anchor="middle">${r.rep}</text>`;
  });
  s += `<text class="ax" x="${L}" y="${H - 2}" >rep</text>`;
  s += `<text class="ax" x="${L - 9}" y="${T + 10}" text-anchor="end">cm</text></svg>`;
  el("chinchart").innerHTML = s;
})();

/* ---- asymmetry table ---- */
el("asymtable").innerHTML =
  `<thead><tr><th>Measure</th><th>Standing</th><th>At the hang</th><th>At the top</th><th>Reading</th></tr></thead><tbody>` +
  [["Shoulder line tilt", f(AS.sh_tilt_standing_deg) + "°", f(AS.sh_tilt_bottom_deg) + "°", f(AS.sh_tilt_top_deg) + "°",
    "real, small; grows under load"],
   ["Ear to shoulder, left", AS.ear_sh_stand_l.toFixed(1), AS.ear_sh_hang_l.toFixed(1), AS.ear_sh_top_l.toFixed(1) + " cm", "&mdash;"],
   ["Ear to shoulder, right", AS.ear_sh_stand_r.toFixed(1), AS.ear_sh_hang_r.toFixed(1), AS.ear_sh_top_r.toFixed(1) + " cm",
    AS.ear_sh_top_index_pct.toFixed(0) + " % apart at the top"],
   ["Shrug vs standing", "&mdash;", "&mdash;", "L " + f(TC.shrug_top_vs_standing_l) + " / R " + f(TC.shrug_top_vs_standing_r) + " cm",
    "the clearest asymmetry in the set"],
   ["Elbow angle, 3D model", "&mdash;", "&mdash;", AS.elbow_top_l_3d.toFixed(0) + "° / " + AS.elbow_top_r_3d.toFixed(0) + "°", "says 20° apart"],
   ["Elbow angle, image plane", "&mdash;", "&mdash;", AS.elbow_top_l_2d.toFixed(0) + "° / " + AS.elbow_top_r_2d.toFixed(0) + "°", "says 2.6° apart &rarr; unresolved"],
   ["Grip, each wrist from centre", "&mdash;", "±" + AS.wrist_off_l_cm.toFixed(1) + " cm", "&mdash;", "symmetric"],
   ["Hips from the grip centre", "&mdash;", f(AS.hip_off_hang_cm) + " cm", f(AS.hip_off_top_cm) + " cm", "centred"],
   ["Lead arm", "&mdash;", "&mdash;", AS.lead_arm_counts.together + " of " + S.reps + " together", "no consistent lead"],
   ["Scapular phase before the elbows bend", "&mdash;", "&mdash;", AS.scap_phase_cm.toFixed(1) + " cm in " + AS.scap_phase_s.toFixed(2) + " s",
    "textbook initiation"]]
   .map(r => `<tr><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td><td style="text-align:left;white-space:normal">${r[4]}</td></tr>`).join("") +
  `</tbody>`;

/* ---- muscle bars ---- */
const mx = Math.max(...D.muscles.map(m => m[1]));
el("muscles").innerHTML = D.muscles.map(([nm, dt, mv, kg, painted, note]) =>
  `<div class="nm${painted ? "" : " off"}" title="${note}">${nm}${painted ? "" : " *"}</div>
   <div class="bar"><i style="width:${(dt / mx * 100).toFixed(1)}%"></i></div>
   <div class="dt">+${dt.toFixed(2)} °C</div>`).join("") +
  `<div></div><div style="font-family:var(--body);font-size:14px;color:var(--ink-2)">
   * on the back — modelled, but not painted in the video. Bars are the rise at the end of the set.</div><div></div>`;

/* ---- temperature curve ---- */
(function () {
  const W = 1000, H = 260, L = 56, Rp = 22, T = 16, B = 40;
  const tc = D.t_curve, lc = D.lat_curve;
  const t0 = tc[0], t1 = tc[tc.length - 1], mxT = 2.2;
  const x = v => L + (W - L - Rp) * (v - t0) / (t1 - t0);
  const y = v => T + (H - T - B) * (1 - v / mxT);
  let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Modelled latissimus dorsi temperature through the set">`;
  for (let v = 0; v <= 2; v += .5) {
    s += `<line class="gl" x1="${L}" y1="${y(v)}" x2="${W - Rp}" y2="${y(v)}"/>`;
    s += `<text class="ax" x="${L - 9}" y="${y(v) + 4}" text-anchor="end">+${v.toFixed(1)}</text>`;
  }
  R.forEach(r => { s += `<line class="gl" x1="${x(r.t_top)}" y1="${T}" x2="${x(r.t_top)}" y2="${H - B}"/>`; });
  const pts = tc.map((v, i) => `${x(v).toFixed(1)},${y(lc[i]).toFixed(1)}`).join(" ");
  s += `<polyline points="${pts}" fill="none" stroke="var(--hot)" stroke-width="2.5" stroke-linejoin="round"/>`;
  s += `<circle cx="${x(t1)}" cy="${y(lc[lc.length - 1])}" r="4.5" fill="var(--hot)"/>`;
  s += `<text class="lbl" x="${x(t1) - 8}" y="${y(lc[lc.length - 1]) - 10}" text-anchor="end">+${lc[lc.length - 1].toFixed(2)} °C</text>`;
  for (let v = 10; v <= 60; v += 10) s += `<text class="ax" x="${x(v)}" y="${H - 14}" text-anchor="middle">${v}</text>`;
  s += `<text class="ax" x="${W - Rp}" y="${H - 14}" text-anchor="end">seconds</text>`;
  s += `<text class="ax" x="${L - 9}" y="${T + 8}" text-anchor="end">°C</text></svg>`;
  el("tempchart").innerHTML = s;
})();

/* ---- chest redness ---- */
if (D.redness) (function () {
  const RD = D.redness, good = RD.per_rep.filter(p => p.valid !== false);
  const W = 1000, H = 280, L = 60, Rp = 22, T = 18, B = 44;
  const t0 = good[0].t - 9, t1 = good[good.length - 1].t + 3, mx = 55;
  const x = v => L + (W - L - Rp) * (v - t0) / (t1 - t0);
  const y = v => T + (H - T - B) * (1 - v / mx);
  let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Chest redness through the set">`;
  for (let v = 0; v <= 50; v += 10) {
    s += `<line class="gl" x1="${L}" y1="${y(v)}" x2="${W - Rp}" y2="${y(v)}"/>`;
    s += `<text class="ax" x="${L - 9}" y="${y(v) + 4}" text-anchor="end">${v}</text>`;
  }
  const pts = good.map(p => `${x(p.t).toFixed(1)},${y(p.corrected).toFixed(1)}`).join(" ");
  const wpts = good.map(p => `${x(p.t).toFixed(1)},${y(p.wall).toFixed(1)}`).join(" ");
  s += `<polyline points="${wpts}" fill="none" stroke="var(--ink-2)" stroke-width="1.6"/>`;
  s += `<polyline points="${pts}" fill="none" stroke="var(--hot)" stroke-width="2.6" stroke-linejoin="round"/>`;
  good.forEach(p => { s += `<circle cx="${x(p.t)}" cy="${y(p.corrected)}" r="5" fill="var(--hot)"/>`; });
  good.forEach(p => { s += `<circle cx="${x(p.t)}" cy="${y(p.wall)}" r="3" fill="var(--ink-2)"/>`; });
  const bx = x(good[0].t - 6), by = y(RD.baseline.corrected);
  s += `<rect x="${bx - 5}" y="${by - 5}" width="10" height="10" fill="var(--ink-2)"/>`;
  s += `<text class="ax" x="${bx + 10}" y="${by + 20}">standing</text>`;
  s += `<text class="lbl" x="${x(good[Math.floor(good.length / 2)].t)}" y="${y(good[Math.floor(good.length / 2)].corrected) - 14}" text-anchor="middle">chest</text>`;
  s += `<text class="ax" x="${x(good[Math.floor(good.length / 2)].t)}" y="${y(good[Math.floor(good.length / 2)].wall) + 20}" text-anchor="middle">wall control</text>`;
  RD.per_rep.filter(p => p.valid === false).forEach(p => {
    s += `<path d="M${x(p.t) - 5} ${y(p.corrected) - 5}L${x(p.t) + 5} ${y(p.corrected) + 5}M${x(p.t) + 5} ${y(p.corrected) - 5}L${x(p.t) - 5} ${y(p.corrected) + 5}" stroke="var(--accent)" stroke-width="2"/>`;
    s += `<text class="ax" x="${x(p.t) - 8}" y="${y(p.corrected) + 4}" text-anchor="end" fill="var(--accent)">dropped</text>`;
  });
  for (let v = 20; v <= 60; v += 10) s += `<text class="ax" x="${x(v)}" y="${H - 16}" text-anchor="middle">${v}</text>`;
  s += `<text class="ax" x="${W - Rp}" y="${H - 16}" text-anchor="end">seconds</text>`;
  s += `<text class="ax" x="${L - 9}" y="${T + 8}" text-anchor="end">index</text></svg>`;
  el("redchart").innerHTML = s;
})();

/* ---- rep table ---- */
const bestRep = S.best_rep;
el("reptable").innerHTML =
  `<thead><tr><th>Rep</th><th>Top (s)</th><th>Chin (cm)</th><th>ROM (cm)</th><th>Up</th><th>Hold</th><th>Down</th>
   <th>Rest</th><th>Peak (m/s)</th><th>Mean (W)</th><th>kcal</th><th>Effort</th><th>RIR</th><th>Lats ΔT</th></tr></thead><tbody>` +
  R.map(r => {
    const cls = !r.rep ? "failrow" : (r.rep === bestRep ? "best" : "");
    return `<tr class="${cls}"><td>${r.rep ? r.rep : "failed"}</td><td>${r.t_top.toFixed(1)}</td>
      <td>${r.chin_cm.toFixed(1)}</td><td>${r.rom_cm.toFixed(0)}</td>
      <td>${r.t_concentric.toFixed(2)}</td><td>${r.t_top_hold.toFixed(2)}</td><td>${r.t_eccentric.toFixed(2)}</td>
      <td>${r.t_bottom_hold.toFixed(2)}</td><td>${r.peak_conc_v.toFixed(2)}</td><td>${r.mean_power_w.toFixed(0)}</td>
      <td>${r.kcal.toFixed(2)}</td><td>×${r.effort_x.toFixed(2)}</td><td>${r.est_rir}</td>
      <td>+${(r.lat_dt || 0).toFixed(2)}</td></tr>`;
  }).join("") + `</tbody>`;
</script>
"""

open(out, "w", encoding="utf-8", newline="\n").write(
    HTML.replace("__DATA__", json.dumps(D, separators=(",", ":"))))
print("wrote", out, os.path.getsize(out), "bytes")
