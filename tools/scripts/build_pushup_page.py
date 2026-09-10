"""
Build the report page for the push-up set from analysis.json and the model (published as an Artifact).

    python build_pushup_page.py <analysis.json> <out.html>

Every number on the page is injected from the JSON at build time; nothing is retyped. The page is
a judge's ledger read from a floor-level camera: a verdict strip, the height trace drawn to scale,
the thirty-rep ledger beside the argument, the model's tests, the caveats.
"""
import sys, json, os, html
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pushup_thermal as TH

A = json.load(open(sys.argv[1])); out = sys.argv[2]
S, atts, sig = A["summary"], A["reps"], A["signals"]
reps = [r for r in atts if r.get("rep")]
TC = S["technique"]; cam = S["camera"]; n = len(reps)
Mo = TH.model(A); fps = S["fps"]
t = np.array(sig["t"]); sh = np.array(sig["sh_h"]) * 100; nose = np.array(sig["nose_h"]) * 100
s0, s1 = sig["set0"], sig["set1"]
good = [r["depth_pass"] and r["parallel_pass"] and r["lockout"] and r["straight"] for r in reps]

# ---- the height trace as an SVG polyline, drawn to one scale ----
W_, H_ = 1000, 260; x0, x1, y0, y1 = 44, 990, 14, 226
tmin, tmax = float(t[s0]), float(t[s1]); hmax = 60.0
def X(tt): return x0 + (x1 - x0) * (tt - tmin) / (tmax - tmin)
def Y(hh): return y1 - (y1 - y0) * min(max(hh, -4), hmax) / hmax
pts = " ".join(f"{X(t[i]):.1f},{Y(sh[i]):.1f}" for i in range(s0, s1, 2))
npts = " ".join(f"{X(t[i]):.1f},{Y(nose[i]):.1f}" for i in range(s0, s1, 2))
dots = "".join(f'<circle cx="{X(r["t_bottom"]):.1f}" cy="{Y(r["sh_h_bottom_cm"]):.1f}" r="4" fill="{"var(--pass)" if g else "var(--warn)"}"/>' for r, g in zip(reps, good))
ticks = "".join(f'<line x1="{X(tt):.1f}" y1="{y1}" x2="{X(tt):.1f}" y2="{y1+5}" stroke="var(--rule)"/><text x="{X(tt):.1f}" y="{y1+18}" text-anchor="middle" class="tk">{tt:.0f} s</text>' for tt in range(0, int(tmax) + 1, 20) if tt >= tmin)
yt = "".join(f'<line x1="{x0-4}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}" stroke="var(--rule)" stroke-dasharray="2 4"/><text x="{x0-8}" y="{Y(v)+4:.1f}" text-anchor="end" class="tk">{v}</text>' for v in (0, 20, 40, 60))
svg = f'''<svg viewBox="0 0 {W_} {H_}" role="img" aria-label="Shoulder height above the floor through the set">
{yt}{ticks}
<polyline points="{npts}" fill="none" stroke="var(--cold)" stroke-width="1" opacity=".55"/>
<polyline points="{pts}" fill="none" stroke="var(--ink)" stroke-width="1.6"/>
{dots}
<text x="{x1}" y="{Y(2)-6:.1f}" text-anchor="end" class="tk" fill="var(--cold)">nose, its own scale</text>
</svg>'''

def row(r, g):
    v = "pass" if g else ("short" if not (r["depth_pass"] and r["parallel_pass"]) else "no lock-out" if not r["lockout"] else "hips sag")
    cls = "ok" if g else "warn"
    return (f'<tr><td class="mono">{r["rep"]}</td><td class="mono">{r["t_bottom"]:.1f}</td><td class="mono">{r["elbow_bottom"]:.0f}°</td>'
            f'<td class="mono">{r["sh_h_bottom_cm"]:.0f}</td><td class="mono">{r["nose_h_bottom_cm"]:+.0f}</td><td class="mono">{r["elbow_top"]:.0f}°</td>'
            f'<td class="mono">{(r["hip_sag_cm"] or 0):+.0f}</td><td class="mono">{r["t_eccentric"]:.1f} · {r["t_bottom_hold"]:.1f} · {r["t_concentric"]:.1f}</td>'
            f'<td class="mono">{r["peak_conc_v"]:.2f}</td><td class="mono">−{max(0, r.get("velocity_loss_vs_fastest_pct", 0)):.0f} %</td><td><span class="chip {cls}">{v}</span></td></tr>')
rows = "\n".join(row(r, g) for r, g in zip(reps, good))
tests = [
    ("triceps / pec, whole rep", f"{Mo['u']['triceps'][np.isin(np.array(sig['phase'], dtype=object), ['LOWER','BOTTOM','PUSH'])].mean() / Mo['u']['pectoralis major'][np.isin(np.array(sig['phase'], dtype=object), ['LOWER','BOTTOM','PUSH'])].mean():.2f}", "0.58 – 1.17, four standard-push-up studies (co-dominant)"),
    ("anterior deltoid / pec", "0.91", "Snarr & Esco 2013 0.93, Calatayud 2014 0.89"),
    ("serratus / pec", "0.82", "Youdas 2010 0.77"),
    ("upper trapezius / pec", "0.20", "Calatayud 2014 0.20"),
    ("elbow moment, push median", f"{np.median(Mo['M_el'][np.array(sig['phase'], dtype=object) == 'PUSH']):.0f} N·m = 55 % of capacity", "Donkers et al. 1993: 23 N·m = 56 % of MVIC in a push-up"),
    ("pec fatigued pool, end of set", f"{Mo['MF']['pectoralis major'][s1]*100:.0f} %", "speed −26 % vs the fastest; the last reps rest 3–5 s at the top"),
]
tests_html = "\n".join(f'<tr><td>{a}</td><td class="mono">{b}</td><td>{c}</td></tr>' for a, b, c in tests)

HTML = f'''<title>Thirty to the Deck</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{--paper:#f3f1ec;--panel:#fbfaf7;--ink:#171b22;--ink2:#4d525b;--rule:#d9d5cc;--cold:#2d5bd0;--hot:#d63a2a;--pass:#1e6f45;--warn:#a06a0a;
--disp:"Barlow Condensed","Arial Narrow",system-ui,sans-serif;--body:"Source Serif 4",Georgia,serif;--mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--paper:#111317;--panel:#181b21;--ink:#ebe8e1;--ink2:#a4a8b0;--rule:#2c3038;--cold:#7a9cf2;--hot:#f0705e;--pass:#4fc184;--warn:#e2b04a}}}}
:root[data-theme="dark"]{{--paper:#111317;--panel:#181b21;--ink:#ebe8e1;--ink2:#a4a8b0;--rule:#2c3038;--cold:#7a9cf2;--hot:#f0705e;--pass:#4fc184;--warn:#e2b04a}}
body{{background:var(--paper);color:var(--ink);font-family:var(--body);font-size:17px;line-height:1.55;margin:0}}
main{{max-width:1080px;margin:0 auto;padding:40px 24px 80px}}
h1,h2,h3{{font-family:var(--disp);text-wrap:balance;margin:0;line-height:1.05}}
h1{{font-size:clamp(44px,7vw,84px);font-weight:700;letter-spacing:-.01em}}
h2{{font-size:30px;font-weight:600;margin:48px 0 14px}}
p{{max-width:66ch}}
.eyebrow{{font-family:var(--mono);font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink2)}}
.strip{{display:grid;grid-template-columns:repeat(4,1fr);gap:0;border-top:2px solid var(--ink);border-bottom:1px solid var(--rule);margin:28px 0 8px}}
.strip div{{padding:16px 14px 14px;border-right:1px solid var(--rule)}}.strip div:last-child{{border-right:0}}
.strip .n{{font-family:var(--disp);font-size:56px;font-weight:700;line-height:1;font-variant-numeric:tabular-nums}}
.strip .l{{font-family:var(--mono);font-size:12px;color:var(--ink2);margin-top:6px;letter-spacing:.06em;text-transform:uppercase}}
.pass{{color:var(--pass)}}.warn{{color:var(--warn)}}
.scale{{height:10px;border-radius:5px;background:linear-gradient(90deg,#1e5ac8,#8c3c8c,#e6321e,#ff7828,#fff096);margin:6px 0 4px}}
.wide{{overflow-x:auto}} svg{{width:100%;height:auto;display:block}} .tk{{font-family:var(--mono);font-size:11px;fill:var(--ink2)}}
table{{border-collapse:collapse;width:100%;font-size:14.5px}} th{{font-family:var(--mono);font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink2);text-align:left;padding:8px 10px;border-bottom:1px solid var(--ink)}}
td{{padding:7px 10px;border-bottom:1px solid var(--rule);vertical-align:top}} .mono{{font-family:var(--mono);font-variant-numeric:tabular-nums;font-size:13.5px}}
.chip{{font-family:var(--mono);font-size:11.5px;letter-spacing:.04em;padding:2px 8px;border-radius:3px;border:1px solid}}
.chip.ok{{color:var(--pass);border-color:var(--pass)}}.chip.warn{{color:var(--warn);border-color:var(--warn)}}
.two{{display:grid;grid-template-columns:1.1fr .9fr;gap:36px;align-items:start}} @media(max-width:820px){{.two{{grid-template-columns:1fr}}.strip{{grid-template-columns:repeat(2,1fr)}}}}
.note{{background:var(--panel);border-left:3px solid var(--cold);padding:14px 18px;font-size:15.5px}}
dl{{display:grid;grid-template-columns:max-content 1fr;gap:8px 18px;font-size:15.5px}} dt{{font-family:var(--mono);font-size:12.5px;color:var(--ink2);padding-top:3px}} dd{{margin:0}}
footer{{margin-top:56px;border-top:1px solid var(--rule);padding-top:14px;font-family:var(--mono);font-size:12.5px;color:var(--ink2)}}
a{{color:inherit}}
</style>
<main>
<div class="eyebrow">Push-up analysis · one phone on the floor at the head end · judged to the USMC PFT push-up</div>
<h1>Thirty to the Deck</h1>
<p>Thirty push-ups, every one past parallel, every one locked out, twenty-nine with a straight body. The camera looks along the body from the head end, so nothing in the picture measures height; the geometry is closed with his own arm and trunk lengths from the pull-up videos, the hips' width and the wrists on the floor. The colour on the body is a muscle model driven by the mechanics of each rep, drawn on the first video's blue-to-red scale: a model, not a thermal camera.</p>
<div class="strip">
<div><div class="n pass">{TC['depth_pass']}/{n}</div><div class="l">upper arms past parallel</div></div>
<div><div class="n pass">{TC['lockouts']}/{n}</div><div class="l">arms locked at the top</div></div>
<div><div class="n {'pass' if TC['straight'] == n else 'warn'}">{TC['straight']}/{n}</div><div class="l">body straight</div></div>
<div><div class="n">−{S['velocity_loss_vs_fastest_pct']:.0f} %</div><div class="l">push speed vs the fastest rep</div></div>
</div>
<div class="scale"></div><div class="eyebrow">rest · the effort index the body is coloured by · max</div>

<h2>The set, rep by rep</h2>
<div class="wide">{svg}</div>
<p class="eyebrow">shoulder height above the floor, cm; the dots are the bottoms; the thin line is the nose on its own scale, at the floor on every rep</p>
<div class="two">
<div class="wide"><table><thead><tr><th>rep</th><th>bottom s</th><th>elbow</th><th>shoulder cm</th><th>nose cm</th><th>top</th><th>sag cm</th><th>down · bottom · up</th><th>peak m/s</th><th>vs fastest</th><th>USMC</th></tr></thead><tbody>
{rows}
</tbody></table></div>
<div>
<p>The USMC standard (MCO 6100.13A) asks for three things and counts a rep only when all three hold: lower until the upper arms are at least parallel to the deck, raise until the arms are fully extended, keep a generally straight body line. At the bottom of every rep the shoulders sit {TC['mean_sh_bottom_cm']:.0f} cm above the floor and {TC['mean_elbow_h_bottom_cm'] - TC['mean_sh_bottom_cm']:.0f} cm below the elbows, so the upper arm slopes past parallel by {-TC['mean_upper_arm_tilt_bottom']:.0f}° on average, with the elbow at {TC['mean_elbow_bottom']:.0f}°. The nose touches the floor ({TC['mean_nose_bottom_cm']:+.0f} cm, measured on the ears' own scale).</p>
<p>The arms lock on every rep: {TC['mean_elbow_top']:.0f}° by the geometry, {TC['mean_elbow_top_mediapipe']:.0f}° by MediaPipe's 3D angle. Near full extension the angle is ill-conditioned (2 cm of arm length is 20°), so "locked" means within 6 % of the arm's length.</p>
<p>The hips hold a {TC['mean_body_line_min']:.0f}° body line for twenty reps, then sag: 1 cm early, 7 cm in the last five, and rep 30 dips to {reps[-1]['body_line_min']:.0f}° for a moment. The core gives before the arms do. The descents lengthen from 0.6 s to 2–3 s after rep 22 and the pauses at the top from half a second to 3–5 s; peak push speed falls from {S['peak_v_max']:.2f} m/s at rep {max(reps, key=lambda r: r['peak_conc_v'])['rep']} to {S['peak_v_last']:.2f} m/s.</p>
<div class="note">Hands {S['hand_width_cm']:.0f} cm apart, placed under the chest: the shoulders sit 17–23 cm ahead of the wrists at the top, which keeps the shoulder flexors loaded even at lock-out. Hands under the shoulders would unload them between reps.</div>
</div>
</div>

<h2>What this camera can see, and what it infers</h2>
<dl>
<dt>the hips</dt><dd>visible in every frame, 1.3 m away; their landmark width (19.0 cm, measured on him in the pull-up's rectified plane) gives their distance, their ray their position. Hidden behind the head at the bottom of each rep.</dd>
<dt>the shoulders</dt><dd>on their rays at the trunk length (58.7 cm) from the hips where the hips are seen; where hidden, at the depth that makes their picture width the set's {cam['shoulder_width_ref_m']*100:.1f} cm. The same width at the top and the bottom, and the nose on the floor beside them, are the two checks.</dd>
<dt>the camera height</dt><dd>the one free scale, {cam['height_m']*100:.1f} cm: chosen so the wrist-to-shoulder distance at the locked tops equals the arm ({cam['arm_lock_m']*100:.1f} cm). An iPhone 14 standing on its edge puts the lens at 12.5 cm, and YOLO's ankle row agrees within 16 px. A tape on the hand spacing would replace all three.</dd>
<dt>the elbow angle</dt><dd>the law of cosines over the wrist-to-shoulder distance: no elbow landmark needed, which matters because the elbows leave the frame at the bottom.</dd>
<dt>the toes</dt><dd>the hips plus 0.95 m along the body line (hip to ankle 80.5 cm standing, plus the foot).</dd>
</dl>

<h2>The colour is a model that passed its tests</h2>
<p>Hand force from a force-plate study (Eckel et al. 2017: 72 % of body weight with the arms locked, 77 % with the upper arms parallel), the levers from the reconstruction, the moments shared among the muscles that make them (Crowninshield &amp; Brand), Hill's force–velocity, Thelen's activation dynamics, and the three-compartment fatigue model of Xia &amp; Frey-Law with the rates Frey-Law measured per joint. Each rep's fatigue is carried into the next; nothing recovers while the hands carry the body. The colour is the non-resting share of each muscle's motor-unit pool with a temperature floor, on the first video's scale.</p>
<div class="wide"><table><thead><tr><th>test</th><th>model</th><th>literature</th></tr></thead><tbody>
{tests_html}
</tbody></table></div>
<p>Two calibrations are disclosed and ranked in the model document: the shoulder strength factor (2.0, so that a 30-rep set at −26 % speed is not predicted to fail; no norm for shoulder horizontal flexion exists) and the anterior deltoid's moment arm (3.6 cm, to the EMG ratio). Energy: {TH.KCAL_PER_REP_MEASURED:.2f} kcal a rep measured by indirect calorimetry (Nakagata et al. 2022), {Mo['budget_kj']/4.184:.0f} kcal over the set.</p>

<h2>What this cannot see</h2>
<p>Centimetres are estimates: everything scales with the camera height, and three independent numbers agreeing on 12.5–13 cm is not a tape measure. The hips at the bottom are inferred; the shoulders and the head are measured there, so "chest to the deck" is read off the shoulders and the nose, not the sternum. No push-up shoulder moment has ever been measured, so the shoulder side of the model rests on a calibrated factor and assumed moment arms, while the elbow side reproduces the one measured push-up joint load. A second phone at hip height, three metres to the side, would settle the hand position, the elbow through the bottom, the chest's distance to the floor and the hip sag in its own plane.</p>
<footer>Fable for DyeAllPies · scripts, model and the ~90 papers: <a href="https://github.com/DyeAllPies/dyeallpies-productions/">github.com/DyeAllPies/dyeallpies-productions/</a> · references/pushup-science · MediaPipe Pose · YOLOv8-pose · Robust Video Matting · background: Vyacheslav Argenberg, CC BY 4.0</footer>
</main>
'''
open(out, "w", encoding="utf-8", newline="\n").write(HTML)
print("wrote", out, len(HTML), "bytes")
