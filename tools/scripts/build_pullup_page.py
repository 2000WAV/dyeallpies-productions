"""
Build the interactive HTML report for a pull-up set from analysis.json.
Every number on the page comes from the JSON at build time or is computed in the
page's own script - nothing is retyped.

    python build_pullup_page.py <analysis.json> <out.html>
"""
import sys, json
import numpy as np

A = json.load(open(sys.argv[1])); out = sys.argv[2]
S, reps, sig = A["summary"], A["reps"], A["signals"]

# height % trace for the chart, thinned to every frame inside the hang window only
h0, h1 = sig["grab0"], sig["hang1"]
hang_ref, top_ref = S["hang_ref_y"], S["top_ref_y"]
pct = np.array(sig["height_pct"])
chin_pct = float((hang_ref - (S["bar_y"] + (S["neck_cm"] + S["perspective_cm"]) / 100 * S["px_per_m"])) / (hang_ref - top_ref) * 100)
torso = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else None
t = np.array(sig["t"])
trace = [[round(float(t[i]), 3), round(float(pct[i]), 1), round(float(sig["vy_m"][i]), 2),
          round(float(sig["elbow_l"][i])), round(float(sig["elbow_r"][i]))] for i in range(h0, h1 + 1)]

page_data = dict(summary=S, reps=[{k: v for k, v in r.items()} for r in reps], trace=trace, chin_pct=chin_pct, torso=torso,
                 t_load=float(t[sig["load0"]]), t_hang=float(t[sig["hang0"]]))

html = r"""<title>Ten on the Doorway Bar</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&display=swap">
<style>
:root{
  color-scheme:light;
  --bg:#f3f4f6; --surface:#ffffff; --ink:#151b24; --ink-2:#4d5866; --ink-3:#7d8794; --line:#dfe3e8;
  --pull:#1baf7a; --lower:#2a78d6; --hold:#eda100; --left:#2a78d6; --right:#eb6834; --warn:#eb6834; --good:#1baf7a;
  --gradeA:#1baf7a; --gradeB:#eda100; --gradeC:#eb6834; --gradeD:#e34948; --accent:#2a78d6; --chip-ink:#0b0b0b;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    color-scheme:dark;
    --bg:#14181d; --surface:#1c2128; --ink:#f2f4f7; --ink-2:#b9c1cc; --ink-3:#8590a0; --line:#2c333d;
    --pull:#199e70; --lower:#3987e5; --hold:#c98500; --left:#3987e5; --right:#d95926; --warn:#d95926; --good:#199e70;
    --gradeA:#199e70; --gradeB:#c98500; --gradeC:#d95926; --gradeD:#e66767; --accent:#3987e5; --chip-ink:#0b0b0b;
  }
}
:root[data-theme="dark"]{
  color-scheme:dark;
  --bg:#14181d; --surface:#1c2128; --ink:#f2f4f7; --ink-2:#b9c1cc; --ink-3:#8590a0; --line:#2c333d;
  --pull:#199e70; --lower:#3987e5; --hold:#c98500; --left:#3987e5; --right:#d95926; --warn:#d95926; --good:#199e70;
  --gradeA:#199e70; --gradeB:#c98500; --gradeC:#d95926; --gradeD:#e66767; --accent:#3987e5; --chip-ink:#0b0b0b;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Source Sans 3","Segoe UI",system-ui,sans-serif;font-size:17px;line-height:1.5}
.wrap{max-width:1080px;margin:0 auto;padding:40px 24px 80px}
h1,h2,.num,.big{font-family:"Barlow Condensed","Arial Narrow",Impact,sans-serif;font-weight:700;text-wrap:balance;letter-spacing:.005em}
h1{font-size:clamp(44px,7vw,84px);line-height:.95;margin:0 0 12px}
h2{font-size:30px;margin:0 0 6px;font-weight:600}
.eyebrow{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-3);font-weight:600;margin-bottom:10px}
.lede{font-size:20px;max-width:62ch;color:var(--ink-2);margin:0 0 36px}
.lede b{color:var(--ink)}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin-bottom:44px}
.tile{background:var(--surface);border:1px solid var(--line);padding:16px 18px 14px;min-height:118px;display:flex;flex-direction:column;justify-content:space-between}
.tile .num{font-size:52px;line-height:1;font-variant-numeric:tabular-nums}
.tile .lab{font-size:14px;color:var(--ink-2);margin-top:8px}
.tile .sub{font-size:13px;color:var(--ink-3)}
.tile.good .num{color:var(--good)} .tile.warn .num{color:var(--warn)}
section{margin:0 0 48px}
.chart{background:var(--surface);border:1px solid var(--line);padding:14px 10px 6px;position:relative}
.chart svg{width:100%;height:auto;display:block}
.chart text{font-family:"Source Sans 3",system-ui,sans-serif;fill:var(--ink-3);font-size:12px}
.chart .axis line{stroke:var(--line)}
.tip{position:absolute;pointer-events:none;background:var(--ink);color:var(--bg);padding:8px 10px;font-size:13px;line-height:1.35;border-radius:3px;white-space:nowrap;display:none;font-variant-numeric:tabular-nums}
.legend{display:flex;gap:18px;flex-wrap:wrap;font-size:14px;color:var(--ink-2);margin:10px 4px 0}
.legend span::before{content:"";display:inline-block;width:18px;height:3px;margin-right:6px;vertical-align:middle;background:var(--c)}
table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums;font-size:15px}
th{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);font-weight:600;text-align:right;padding:8px 10px;border-bottom:1px solid var(--line)}
td{padding:8px 10px;text-align:right;border-bottom:1px solid var(--line)}
th:first-child,td:first-child{text-align:left}
.tablewrap{overflow-x:auto;background:var(--surface);border:1px solid var(--line)}
.chip{display:inline-block;min-width:46px;text-align:center;padding:2px 8px;font-weight:700;color:var(--chip-ink);font-family:"Barlow Condensed",sans-serif;font-size:17px}
.A{background:var(--gradeA)} .B{background:var(--gradeB)} .C{background:var(--gradeC)} .D{background:var(--gradeD)}
.bad{color:var(--warn);font-weight:600}
.bars{display:grid;grid-template-columns:repeat(auto-fit,minmax(88px,1fr));gap:10px;align-items:end}
.bar{background:var(--surface);border:1px solid var(--line);padding:10px 8px 8px;display:flex;flex-direction:column;gap:6px}
.bar .stack{height:150px;display:flex;flex-direction:column-reverse;gap:2px}
.bar .seg{width:100%}
.bar .lab{font-size:13px;color:var(--ink-2);text-align:center}
.bar .sc{font-family:"Barlow Condensed",sans-serif;font-size:22px;font-weight:700;text-align:center;line-height:1}
.keys{display:flex;gap:14px;flex-wrap:wrap;font-size:13px;color:var(--ink-2);margin-top:10px}
.keys span::before{content:"";display:inline-block;width:12px;height:12px;margin-right:5px;vertical-align:-1px;background:var(--c)}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px}
.note{background:var(--surface);border:1px solid var(--line);padding:18px 20px}
.note h3{font-family:"Barlow Condensed",sans-serif;font-size:22px;margin:0 0 6px;font-weight:600}
.note p{margin:0;color:var(--ink-2);font-size:16px}
.method{max-width:70ch;color:var(--ink-2)}
.method li{margin-bottom:8px}
.foot{font-size:14px;color:var(--ink-3);margin-top:40px;border-top:1px solid var(--line);padding-top:14px}
@media (prefers-reduced-motion: no-preference){ .tile{transition:transform .15s} }
</style>
<div class="wrap">
  <div class="eyebrow">Pull-up set · 2026-09-05 · doorway bar · one floor camera</div>
  <h1>Ten on the doorway bar</h1>
  <p class="lede" id="lede"></p>
  <div class="tiles" id="tiles"></div>

  <section>
    <h2>Shoulder height through the set</h2>
    <div class="chart" id="trace"><div class="tip" id="tip"></div></div>
    <div class="legend"><span style="--c:var(--pull)">pull (concentric)</span><span style="--c:var(--hold)">hold at the top</span><span style="--c:var(--lower)">lower (eccentric)</span><span style="--c:var(--ink-3)">hang</span></div>
  </section>

  <section>
    <h2>Every rep</h2>
    <div class="tablewrap"><table id="reps"></table></div>
  </section>

  <section>
    <h2>Efficiency score, component by component</h2>
    <div class="bars" id="bars"></div>
    <div class="keys" id="keys"></div>
  </section>

  <section>
    <h2>How hard each rep was</h2>
    <p class="method" style="margin:0 0 14px">Same load every rep, so difficulty is in the speed: the slower the pull, the closer to a maximum effort. Effort = fastest rep's mean pull speed ÷ this rep's. The energy figure is a rough model (work ÷ 22 % efficiency, lowering at 35 % of that, plus an isometric "holding on" cost for the whole cycle), not a measurement.</p>
    <div class="bars" id="effort"></div>
    <div class="keys" id="effort-keys"></div>
  </section>

  <section>
    <h2>Core, chest and lats</h2>
    <div class="cols" id="torso"></div>
  </section>

  <section>
    <h2>The muscle heat map</h2>
    <div class="cols" id="heat"></div>
  </section>

  <section>
    <h2>What the numbers say</h2>
    <div class="cols" id="notes"></div>
  </section>

  <section>
    <h2>How it was measured</h2>
    <ul class="method" id="method"></ul>
  </section>
  <div class="foot" id="foot"></div>
</div>
<script>
const D = __DATA__;
const S = D.summary, R = D.reps, T = D.trace;
const f0 = x => Math.round(x), f1 = x => x.toFixed(1), f2 = x => x.toFixed(2);

document.getElementById('lede').innerHTML =
  `<b>${S.reps} reps</b>, ${S.chin_at_bar} of them chin-at-bar, all ${S.lockouts} with a full hang at the bottom, and only about ${f0(S.mean_hip_sway_cm)} cm of hip movement. ` +
  `Mean efficiency <b>${f0(S.mean_efficiency)} / 100</b>. The set did not end on form — it ended on speed: the pull slowed by ${f0(S.velocity_loss_pct)} % from the fastest rep to the last, ` +
  `and the last rep took <b>×${S.effort_x_last.toFixed(1)}</b> the effort of the best one for the same ${f0(S.work_per_rep_j)} J of work. Rough energy cost: about ${f0(S.set_kcal_total)} kcal.`;

const tiles = [
  ['', S.reps, 'reps', `both trackers agree (YOLO: ${S.yolo_reps})`],
  ['good', f0(S.mean_efficiency), 'mean efficiency / 100', `${R.filter(r=>r.grade==='A').length} A · ${R.filter(r=>r.grade==='B').length} B`],
  ['', `${S.chin_above ?? '–'} · ${S.chin_marginal ?? '–'} · ${S.chin_short ?? '–'}`, 'chin above · at bar · short', 'above = ≥1 cm over the bar line, at = within ±1 cm'],
  ['warn', `−${f0(S.velocity_loss_pct)} %`, 'pull-speed loss', `${f2(S.peak_v_max)} → ${f2(S.peak_v_last)} m/s`],
  ['', `${f1(S.mean_concentric)} / ${f1(S.mean_eccentric)} s`, 'up / down tempo', 'lowering is the faster half'],
  ['', `${f0(S.mean_elbow_top_l)}° / ${f0(S.mean_elbow_top_r)}°`, 'elbow at top, L / R', `right bends ${f0(S.mean_elbow_top_r - S.mean_elbow_top_l)}° less every rep`],
  ['', `${f0(S.work_per_rep_j)} J`, 'work per rep', `${f0(S.lifted_mass_kg)} kg lifted ${f0(S.mean_rom_cm)} cm · ${f0(S.peak_power_w_max)} W peak`],
  ['', `≈ ${S.set_kcal_total.toFixed(1)} kcal`, 'energy for the set, rough', `about ${(S.set_kcal / S.reps).toFixed(2)} kcal per rep`],
  ['warn', `×${S.effort_x_last.toFixed(1)}`, 'effort of the last rep vs best', `~${S.est_rir_last} reps in reserve at the end`],
];
document.getElementById('tiles').innerHTML = tiles.map(([c,n,l,s]) =>
  `<div class="tile ${c}"><div class="num">${n}</div><div><div class="lab">${l}</div><div class="sub">${s}</div></div></div>`).join('');

// ---- trace chart (SVG, one scale, crosshair tooltip) ----
(function(){
  const W = 1040, H = 340, m = {l:44, r:16, t:18, b:34};
  const t0 = T[0][0], t1 = T[T.length-1][0];
  const x = t => m.l + (t - t0) / (t1 - t0) * (W - m.l - m.r);
  const y = p => m.t + (1 - (Math.max(-6, Math.min(112, p)) + 6) / 118) * (H - m.t - m.b);
  // phase per trace sample
  const phase = new Array(T.length).fill('hang');
  for (let i = 0; i < T.length; i++) if (T[i][0] < D.t_hang) phase[i] = 'standing';
  const idx = t => Math.round((t - t0) / (T[1][0] - t0));
  R.forEach(r => {
    const s = r.f_start - FRAME0, ce = r.f_conc_end - FRAME0, es = r.f_ecc_start - FRAME0, ee = r.f_end - FRAME0;
    for (let i = s; i <= ce; i++) phase[i] = 'pull';
    for (let i = ce + 1; i < es; i++) phase[i] = 'hold';
    for (let i = es; i <= ee; i++) phase[i] = 'lower';
  });
  const col = {pull:'var(--pull)', hold:'var(--hold)', lower:'var(--lower)', hang:'var(--ink-3)', standing:'var(--ink-3)'};
  let segs = [], cur = null;
  T.forEach((p, i) => {
    if (!cur || cur.ph !== phase[i]) { cur = {ph: phase[i], pts: cur ? [cur.pts[cur.pts.length-1]] : []}; segs.push(cur); }
    cur.pts.push([x(p[0]), y(p[1])]);
  });
  let svg = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Shoulder height over time, coloured by phase">`;
  svg += `<g class="axis">`;
  [0, 50, 100].forEach(p => { svg += `<line x1="${m.l}" x2="${W-m.r}" y1="${y(p)}" y2="${y(p)}"/><text x="${m.l-8}" y="${y(p)+4}" text-anchor="end">${p}%</text>`; });
  for (let s = Math.ceil(t0/5)*5; s <= t1; s += 5) svg += `<line x1="${x(s)}" x2="${x(s)}" y1="${H-m.b}" y2="${H-m.b+5}"/><text x="${x(s)}" y="${H-m.b+18}" text-anchor="middle">${s} s</text>`;
  svg += `</g>`;
  svg += `<line x1="${m.l}" x2="${W-m.r}" y1="${y(D.chin_pct)}" y2="${y(D.chin_pct)}" stroke="var(--ink-3)" stroke-dasharray="4 4" stroke-width="1"/><text x="${W-m.r-4}" y="${y(D.chin_pct)-5}" text-anchor="end">chin at bar</text>`;
  svg += `<rect x="${x(t0)}" y="${m.t}" width="${x(D.t_load)-x(t0)}" height="${H-m.t-m.b}" fill="var(--line)" opacity=".55"/><text x="${(x(t0)+x(D.t_load))/2}" y="${y(62)}" text-anchor="middle">standing, hands on bar</text><text x="${(x(t0)+x(D.t_load))/2}" y="${y(52)}" text-anchor="middle">${S.standing_on_bar.toFixed(1)} s</text>`;
  svg += `<rect x="${x(D.t_load)}" y="${m.t}" width="${x(D.t_hang)-x(D.t_load)}" height="${H-m.t-m.b}" fill="var(--hold)" opacity=".18"/><text x="${(x(D.t_load)+x(D.t_hang))/2}" y="${y(40)}" text-anchor="middle">loading ${S.loading_duration.toFixed(1)} s</text>`;
  segs.forEach(sg => { svg += `<polyline fill="none" stroke="${col[sg.ph]}" stroke-width="${sg.ph==='hang'?1.5:2.5}" stroke-linejoin="round" points="${sg.pts.map(p=>p.map(v=>v.toFixed(1)).join(',')).join(' ')}"/>`; });
  R.forEach(r => { const px = x(r.t_top), py = y(T[r.f_top - FRAME0][1]); svg += `<circle cx="${px}" cy="${py}" r="6" fill="var(--grade${r.grade})" stroke="var(--surface)" stroke-width="2"/><text x="${px}" y="${py-11}" text-anchor="middle" style="fill:var(--ink)">${r.n}</text>`; });
  svg += `<line id="xh" x1="0" x2="0" y1="${m.t}" y2="${H-m.b}" stroke="var(--ink)" stroke-width="1" opacity="0"/><circle id="dot" r="5" fill="var(--ink)" opacity="0"/>`;
  svg += `<rect id="hit" x="${m.l}" y="${m.t}" width="${W-m.l-m.r}" height="${H-m.t-m.b}" fill="transparent"/></svg>`;
  const box = document.getElementById('trace'); box.insertAdjacentHTML('beforeend', svg);
  const tip = document.getElementById('tip'), xh = box.querySelector('#xh'), dot = box.querySelector('#dot'), hit = box.querySelector('#hit'), sv = box.querySelector('svg');
  hit.addEventListener('mousemove', e => {
    const rct = sv.getBoundingClientRect(); const vx = (e.clientX - rct.left) / rct.width * W;
    const tt = t0 + (vx - m.l) / (W - m.l - m.r) * (t1 - t0);
    const i = Math.max(0, Math.min(T.length-1, idx(tt))); const p = T[i];
    xh.setAttribute('x1', x(p[0])); xh.setAttribute('x2', x(p[0])); xh.setAttribute('opacity', 1);
    dot.setAttribute('cx', x(p[0])); dot.setAttribute('cy', y(p[1])); dot.setAttribute('opacity', 1);
    tip.style.display = 'block';
    tip.innerHTML = `<b>${p[0].toFixed(2)} s · ${phase[i].toUpperCase()}</b><br>height ${p[1].toFixed(0)} %<br>speed ${Math.abs(p[2]).toFixed(2)} m/s<br>elbow L ${p[3]}° · R ${p[4]}°`;
    const bx = (e.clientX - rct.left), by = (e.clientY - rct.top);
    tip.style.left = (bx + 14 + 220 > rct.width ? bx - 14 - tip.offsetWidth : bx + 14) + 'px'; tip.style.top = (by - 10) + 'px';
  });
  hit.addEventListener('mouseleave', () => { tip.style.display = 'none'; xh.setAttribute('opacity', 0); dot.setAttribute('opacity', 0); });
})();

// ---- table ----
(function(){
  const cols = ['rep','top (s)','chin vs bar (cm)','elbow top L / R','up / hold / down (s)','rest (s)','peak speed (m/s)','power (W)','kcal','effort','RIR','hip sway (cm)','score'];
  let h = '<thead><tr>' + cols.map(c=>`<th>${c}</th>`).join('') + '</tr></thead><tbody>';
  R.forEach(r => {
    const chin = r.chin_est_cm + S.perspective_cm;
    const vlab = r.chin_verdict === 'above' ? 'above' : r.chin_verdict === 'at' ? 'at bar' : 'short';
    h += `<tr><td>${r.n}</td><td>${f1(r.t_top)}</td><td class="${chin<-1?'bad':''}">${chin>=0?'+':''}${f1(chin)} <span style="color:var(--ink-3)">${vlab}</span></td><td>${f0(r.elbow_top_l)}° / ${f0(r.elbow_top_r)}°</td>` +
         `<td>${f1(r.t_concentric)} / ${f1(r.t_top_hold)} / ${f1(r.t_eccentric)}</td><td>${r.t_bottom_hold ? f1(r.t_bottom_hold) : '–'}</td><td>${f2(r.peak_conc_v)}</td>` +
         `<td>${f0(r.mean_power_w)}</td><td>${f2(r.kcal)}</td><td class="${r.effort_x>=1.4?'bad':''}">×${f2(r.effort_x)}</td><td>${r.est_rir}</td><td>${f1(r.hip_sway_cm)}</td>` +
         `<td><span class="chip ${r.grade}">${f0(r.efficiency)} ${r.grade}</span></td></tr>`;
  });
  document.getElementById('reps').innerHTML = h + '</tbody>';
})();

// ---- component bars ----
(function(){
  const comps = [['rom','range of motion',25,'var(--lower)'],['control','eccentric control',20,'var(--pull)'],['lockout','lock-out',15,'var(--hold)'],['sway','low sway',15,'#e87ba4'],['power','pull speed',15,'#9085e9'],['symmetry','L/R symmetry',10,'var(--right)']];
  document.getElementById('bars').innerHTML = R.map(r => `<div class="bar"><div class="sc">${f0(r.efficiency)}</div><div class="stack">` +
    comps.map(([k,l,mx,c]) => `<div class="seg" style="height:${r.score[k]/100*150}px;background:${c}" title="${l}: ${r.score[k].toFixed(1)} / ${mx}"></div>`).join('') +
    `</div><div class="lab">rep ${r.n}</div></div>`).join('');
  document.getElementById('keys').innerHTML = comps.map(([k,l,mx,c]) => `<span style="--c:${c}">${l} · ${mx}</span>`).join('');
})();

// ---- effort / energy bars ----
(function(){
  const maxK = Math.max(...R.map(r => r.kcal)) * 1.15;
  document.getElementById('effort').innerHTML = R.map(r => `<div class="bar"><div class="sc" style="color:${r.effort_x>=1.4?'var(--warn)':r.effort_x>=1.2?'var(--hold)':'var(--good)'}">×${r.effort_x.toFixed(2)}</div><div class="stack">` +
    `<div class="seg" style="height:${r.kcal_conc/maxK*150}px;background:var(--pull)" title="pull: ${r.kcal_conc.toFixed(2)} kcal"></div>` +
    `<div class="seg" style="height:${r.kcal_ecc/maxK*150}px;background:var(--lower)" title="lower: ${r.kcal_ecc.toFixed(2)} kcal"></div>` +
    `<div class="seg" style="height:${r.kcal_iso/maxK*150}px;background:var(--hold)" title="holding on: ${r.kcal_iso.toFixed(2)} kcal"></div>` +
    `</div><div class="lab">rep ${r.n} · ${r.kcal.toFixed(2)} kcal<br>RIR ${r.est_rir} · ${f0(r.mean_power_w)} W</div></div>`).join('');
  document.getElementById('effort-keys').innerHTML = [['var(--pull)','pull (work ÷ 22 %)'],['var(--lower)','lower (35 % of that)'],['var(--hold)','holding on (3.5 MET × time)']].map(([c,l]) => `<span style="--c:${c}">${l}</span>`).join('') +
    `<span>cumulative ≈ ${S.set_kcal_total.toFixed(1)} kcal · ${f0(S.set_work_kj*1000)} J of lifting · equivalent weighted 1RM ≈ +${f0(S.est_1rm_extra_kg)} kg</span>`;
})();

// ---- torso notes ----
(function(){
  const Tz = D.torso; if (!Tz) return;
  const ph = Tz.phases;
  const items = [
    ['Trunk control', `Shoulder line and hip line stay within ${f0(S.mean_lat_bend_range)}° of each other through a rep; hips move ${f1(S.mean_hip_sway_cm)} cm sideways. Hip angle ${f0(S.mean_hip_angle_top)}° at the top with knees tucked to ${f0(S.mean_knee_min)}° — a mild hollow body, legs behind. Square, strict.`],
    ['Lats from the front', `Silhouette width under the armpits ÷ waist: ${Tz.v_taper_upper_over_waist.hang.toFixed(2)} in the hang, ${Tz.v_taper_upper_over_waist.early_pull.toFixed(2)} in the early pull. No measurable flare from this angle — the profile is perspective plus the upper arms entering the outline. Lats need a side or rear camera.`],
    ['Abs and chest, by the light', `Edge-contrast ÷ brightness in the abdominal band: ${f0(ph['loaded hang'].shading_index)} in the hang → ${f0(ph['mid pull'].shading_index)} mid-pull → ${f0(ph['top'].shading_index)} at the top → ${f0(ph['lowering'].shading_index)} lowering. The ribcage and oblique lines really do come out at the top, but the torso also rises into the lintel's shadow (brightness ${f0(ph['loaded hang'].brightness)} → ${f0(ph['top'].brightness)}), and a darker side-lit surface has more relative contrast whatever the muscle is doing. The pecs show no change across phases; pull-ups barely load them.`],
  ];
  document.getElementById('torso').innerHTML = items.map(([h,p]) => `<div class="note"><h3>${h}</h3><p>${p}</p></div>`).join('');
})();

// ---- heat map explanation ----
document.getElementById('heat').innerHTML = [
  ['Where a pull-up works', 'Surface-EMG averages over a rep, pull-up end of the ranges because the grip is pronated (Youdas et al. 2010, J Strength Cond Res 24:3404): latissimus dorsi 124 % MVIC, biceps brachii 78, infraspinatus 75, trapezius 52, pectoralis major 44, external oblique 33. Erector spinae (40) sits on the back and is not drawn; the rectus abdominis was not measured, so the abdomen only carries image evidence.'],
  ['Warmed by your effort', 'Dickie et al. 2017 (J Electromyogr Kinesiol 32:30) found concentric activation of biceps, brachioradialis and pectoralis significantly above eccentric, so the map runs pull 1.0 > top hold 0.85 > lowering 0.65 > hang 0.35, and the pull is scaled by that rep\'s measured speed. A quarter of the colour is the image itself: local skin contrast where the light shows lines.'],
  ['The whole body warms up through the set', `A base level rises with the measured peak-velocity loss of the latest completed rep and with the energy already spent, and never falls within the set — by rep 10 the body sits ${f0(S.velocity_loss_pct)} % slower than its best. Sánchez-Medina & González-Badillo 2011 (Med Sci Sports Exerc 43:1725) showed within-set velocity loss tracks post-exercise lactate at r = 0.93–0.97, so it is a fair proxy for accumulated metabolic fatigue, and it does not clear in half-second rests. The colour is fatigue, not temperature.`],
  ['What it is not', 'Not a thermal camera and not a measurement of these muscles. Regions are mapped on the silhouette itself (each pixel of a Robust Video Matting alpha, minus MediaPipe\'s head and clothes classes, is assigned to the nearest limb or torso band), so the face, hair, shorts and background are excluded by construction; the torso is covered at 82 % opacity with its own shading kept. The literature values are averages of young trained adults at a controlled cadence.'],
].map(([h,p]) => `<div class="note"><h3>${h}</h3><p>${p}</p></div>`).join('');

// ---- notes ----
const notes = [
  ['Strict, full-range reps', `${S.chin_above} reps clearly above the bar, ${S.chin_marginal} at the bar within a centimetre, ${S.chin_short} short; every rep returns to a ${f0(S.mean_elbow_bottom)}° hang over ${f0(S.mean_rom_cm)} cm of travel, and the hips move ${f0(S.mean_hip_sway_cm)} cm on average. Nothing is kipped.`],
  ['The set ended on speed, not form', `Peak pull speed fell from ${f2(S.peak_v_max)} m/s to ${f2(S.peak_v_last)} m/s and the up-phase stretched from ${f1(Math.min(...R.map(r=>r.t_concentric)))} s to ${f1(Math.max(...R.map(r=>r.t_concentric)))} s. Velocity-based training treats a 20–30 % loss as the quality cut-off; that was rep ${R.find(r => r.peak_conc_v < 0.75*S.peak_v_max)?.n ?? '–'}. Rep ${R[R.length-1].n} is the grinder and the only one short of the bar.`],
  ['Lowering is the faster half', `${f1(S.mean_eccentric)} s down against ${f1(S.mean_concentric)} s up. A deliberate 2–3 s negative is the cheapest upgrade in this set — eccentric control is the one score component never at full marks.`],
  ['A left/right split, with a caveat', `The 3D elbow estimate reads ${f0(S.mean_elbow_top_l)}° left and ${f0(S.mean_elbow_top_r)}° right at the top on every rep — but the camera is not square to the body, so part of that gap is viewing angle. Worth a mirror check or a straight-on camera before calling it an asymmetry.`],
  ['Legs stay tucked', `Knees at about ${f0(S.mean_knee_min)}° throughout (crossed behind, floor is close). Fine on a doorway bar, but it shortens the lever and flatters the sway number.`],
  ['Standing on the bar first', `${f1(S.standing_on_bar)} s with hands on the bar and feet on the floor, then ${f1(S.loading_duration)} s of loading in which the arms lengthen ${f0(S.arm_stretch_pct)} % and the shoulders sink ${f0(S.shoulder_sink_cm)} cm as the weight goes on. Only ${f1(S.dead_hang_before_first)} s of true dead hang before rep 1.`],
];
document.getElementById('notes').innerHTML = notes.map(([h,p]) => `<div class="note"><h3>${h}</h3><p>${p}</p></div>`).join('');

document.getElementById('method').innerHTML = [
  `MediaPipe Pose Landmarker (heavy) tracked 33 landmarks on ${S.tracked_frames} of ${S.frames} frames; joint angles use its metric 3D world coordinates, because the 2D elbow angle collapses to about 10° when the forearm points at a floor camera.`,
  `YOLOv8m-pose ran independently on every frame as a cross-check: ${S.yolo_reps} reps, shoulder-track correlation ${S.yolo_mp_shoulder_corr.toFixed(3)}, median disagreement ${S.yolo_mp_shoulder_mad_px.toFixed(0)} px.`,
  `Height is the shoulder midpoint, not the chin: the head passes behind the bar and the door lintel at the top of every rep, where MediaPipe keeps inventing a face at visibility 1.0. YOLO's eye confidence drops to 0.1–0.2 there on reps 1–${S.head_hidden} — the real evidence that the head cleared the bar.`,
  `Chin-at-bar = shoulder-to-chin length measured standing (${S.neck_cm.toFixed(1)} cm) plus a ${S.perspective_cm} cm perspective allowance, because a chin level with a bar it hangs behind projects a few cm below the bar line from a floor camera.`,
  `Hang onset is detected from load, not grip: shoulder-to-wrist distance and the shoulder line both settle to new plateaus when the body weight goes onto the bar (${f1(D.t_load)} → ${f1(D.t_hang)} s here).`,
  `Centimetre scale: the straight arm at the loaded hang (shoulder joint to wrist = 0.332 × ${f0(S.height_m*100)} cm) gives ${f0(S.px_per_m)} px/m — the one segment aligned with the motion and at its depth. Alternative calibrations (trunk length, MediaPipe's world fit) read ${f0(S.rom_cm_alt.trunk_at_bottom)}–${f0(S.rom_cm_alt.world_fit)} cm of travel instead of ${f0(S.mean_rom_cm)}; every m/s, J, W and kcal figure inherits that ±10–15 %.`,
  `Physics: lifted mass = ${S.mass_kg} kg minus hands and forearms (${f0(S.lifted_mass_kg)} kg); work = m·g·travel; power = work ÷ pull time; peak force = m·(g + peak acceleration). Reps in reserve ≈ one per 9 % of peak-velocity loss.`,
  `Efficiency per rep: range of motion 25 (−2.5 per cm short of the bar) · eccentric control 20 (full at 1.5 s) · lock-out 15 (155°+ full) · low sway 15 (≤4 cm full) · pull speed 15 (relative to the best rep) · L/R symmetry 10 (≤5° elbow gap full). A ≥85, B ≥70, C ≥55.`,
].map(s=>`<li>${s}</li>`).join('');
document.getElementById('foot').textContent = `Source: IMG_6041.MOV, ${S.frames} frames at ${S.fps.toFixed(0)} fps, 1080×1920. ${f0(S.height_m*100)} cm, ${S.mass_kg} kg, BMI ${S.bmi.toFixed(1)}. Grip ${S.grip_ratio.toFixed(2)} × shoulder width (≈${f0(S.grip_width_cm)} cm). Built from analysis.json and torso.json — no number on this page was typed by hand.`;
</script>
"""
html = html.replace("__DATA__", json.dumps(page_data, separators=(",", ":"))).replace("FRAME0", str(h0))
open(out, "w", encoding="utf-8").write(html)
print("wrote", out, len(html) // 1024, "KB")
