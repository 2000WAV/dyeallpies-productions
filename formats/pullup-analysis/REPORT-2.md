# Pull-up analysis #2 — IMG_5990.MOV (shot and analysed 2026-09-06/07)

Second set, second camera position. Source: 67.4 s iPhone clip, 1080×1920 after the
rotation tag, 30 fps, 2022 frames. Phone further back and higher than the first shoot, so
the whole body is in frame — **the feet on the floor at the start and the head at the top
of every rep**, which is what makes this analysis stricter than the first one. Dennis
(188 cm, 79 kg), pronated grip, legs crossed and tucked behind.

The first report is `pullup/REPORT.md` and still stands for its own clip. This one supersedes
its *methods* wherever they differ.

## Headline

**11 reps and a twelfth attempt that failed.** Every rep locked out at the bottom, none
of them kipped, and every one of them came up **2 to 7 cm short of putting the chin over
the bar** (mean −4.3 cm, ±1.5). The set ran to genuine failure: peak pull speed fell 63 %,
and the twelfth attempt stalled 20 cm below the bar before he dropped off.

## What changed in the method, and why

| | |
|---|---|
| **The footage is de-rolled 2.7°** | Four independent references agree the camera was rolled: the vertical vanishing point fitted to 102 long edges in the room (2.9° at his position), his standing body (2.1°), and the plumb line of his hanging body (2.8° and 3.5°). The clip is rotated 2.7° counter-clockwise with edge replication and no zoom, so nothing is cropped. After the rotation the room's verticals read −0.03°. |
| **The bar is a line, not a row** | The bar still reads 3.0° off horizontal in the straightened image. That is not a crooked bar, it is camera yaw: horizontal lines at different heights converge, and the floor tiles tilt the other way. So the bar is fitted as a line (1626 sub-pixel edge points over 14 clean frames, residual 0.25 px) and **every height is measured against the bar line at that point's own x**. |
| **Hang onset from the feet** | The ankles are visible here. He stands on the floor holding the bar from 5.4 s to 10.2 s; his feet leave the floor at 10.3 s; the first pull starts 0.4 s later. The first video had to infer this from arm length. |
| **Phases from position, not velocity** | Each rep's concentric runs from 5 % to 95 % of its own amplitude, and the eccentric back down. The old velocity-threshold walker collapsed on rep 3 of this clip and reported a 0.03 s lowering. |
| **Scale from the standing stature** | He stands at the bar plane with his feet on the floor, so eye-to-ankle (1198 px = 168.6 cm) calibrates 711 px/m directly. The two alternatives now agree within 5 % — shoulder-to-ankle 701, arm-at-hang 747 px/m — where the first video's calibrations disagreed by 30 %. Range of motion is 60 cm by the first, 61 by the second, 57 by the third. |
| **Chin along the face axis** | At the top his head is tilted right back, so a fixed nose-to-chin drop measured standing is far too pessimistic. The chin is placed down the face axis: `chin = mouth + 0.60 × (mouth − eye midpoint)`, which absorbs head pitch and foreshortening together. A second, independent estimate anchors his shoulder-to-chin length measured standing. The two agree within about 1 cm on 9 of 11 reps. |
| **Asymmetry in the image plane first** | The frame is de-rolled, so image vertical is world vertical and left/right differences measured in the image are real. MediaPipe's 3D angles are a model estimate and are reported as such. |

**Cross-check.** YOLOv8m-pose, run independently on every frame, finds the same 12 attempts
and its shoulder track correlates with MediaPipe's at r = 0.998 over the set (median gap
12 px = 1.7 cm). MediaPipe found a pose on 1911 of 2022 frames.

## Timeline

| | |
|---|---|
| Standing on the floor, hands on the bar | 5.4 – 10.2 s (4.8 s) |
| Feet leave the floor | 10.3 s |
| Loaded dead hang before rep 1 | 0.4 s |
| Working set | 11.0 – 63.0 s (52.0 s, 12.7 reps/min) |
| Twelfth attempt, failed | 60.7 – 62.7 s, stalled at 62.0 s |
| Off the bar | 63.3 s |

## The set

| | |
|---|---|
| Reps | **11** counted, plus one failed attempt |
| Chin vs the bar | **0 above, 0 at, 11 short.** Best rep −1.8 cm, worst −6.9 cm, mean **−4.3 cm ±1.5** |
| Full lock-out at the bottom | **11 / 11** (3D elbow 163–168°, 2D 164–172°) |
| Range of motion | **60 cm** of shoulder travel per rep (58–62) |
| Tempo | 1.27 s up / 0.87 s hold / 1.26 s down, 0.91 s resting at the bottom |
| Peak pull speed | 1.08 m/s (rep 4) → 0.40 m/s (rep 11): **−63 %** |
| Hip travel during a rep | 4.0 cm — no swing |
| Legs | knees tuck through 38° of hip angle in each pull (see below) |
| Grip | 42 cm, 1.30 × shoulder width |
| Shoulder line at the top | tilted +1.7° (left shoulder 1.0 cm lower), vs +0.5° standing |
| Mean efficiency | 80 / 100 (a composite, not a form verdict) |

## Judge's card — USMC PFT pull-up standard

The standard: dead hang with the arms fully extended, chin above the bar, lower to full
extension, no kipping, kicking or leg movement to assist.

| check | result | verdict |
|---|---|---|
| Dead hang, arms extended | 3D elbow 163–168° at every bottom | **pass, 11/11** |
| Chin above the bar | −4.3 cm mean, best rep −1.8 cm | **fail on all 11** |
| Lower to full extension | 11/11 | **pass** |
| No kipping | hips travel 4.0 cm; no arch-to-hollow swing | **pass** |
| Leg movement | knees tuck 38° of hip angle per pull | **borderline** |
| Set honesty | taken past failure | — |

**On the chin.** This is the finding a critical viewer will care about, so here is the
evidence. The bar line is known to 0.25 px. At the top of the best rep his *mouth* clears
the bar by about 1.5 cm and his chin sits level with it or just under; on the average rep
the mouth is at the bar and the chin is 4 cm below. Two independent estimators agree. The
uncertainty is ±1.5 cm, dominated by the assumed mouth-to-chin proportion, so the best rep
is within noise of touching the bar — but no rep clearly cleared it. A judge would not
count these as chin-over-bar reps. The fix is about 4 cm more pull, which is roughly 7 %
more range on a 60 cm rep.

**On the legs.** Checked by eye on frame strips through reps 3 and 10: there is no kip.
He does not arch and hollow, and his hips travel 4 cm horizontally. But his knees are not
still — they hang low at the bottom and tuck up in front through about 38° of hip angle
as he pulls. That is not momentum generation, it is a habit, and it is the one thing on
this card a strict judge could argue with. Holding the legs still costs nothing.

**On the pause.** He holds the top for 0.87 s on average. That is unusual and good: it
rules out any bounce, and it means the range-of-motion number is not a momentary peak.

## Left vs right

The camera is level and square enough that image-plane differences are real. Sign
convention: **positive = the person's LEFT side is lower or larger**.

| measure | standing | at the hang | at the top | reading |
|---|---|---|---|---|
| Shoulder line tilt | +0.5° | +3.4° | +1.7° (+1.0 cm) | Real but small. It grows under load and relaxes at the top. |
| Ear to shoulder | L 23.8 / R 22.3 cm | L 19.5 / R 16.3 | L 24.4 / R 19.8 cm | The right shoulder sits closer to the ear throughout, standing included — so part of it is how he is built, not a shrug. **20.5 % apart at the top** is over the conventional 10 % flag. |
| Shrug vs standing | — | — | L +0.6 cm, R −2.5 cm | The right shoulder rides up 2.5 cm at the top; the left does not. This is the clearest asymmetry in the set. |
| Elbow height at the top | — | — | −1.3 cm | The right elbow finishes slightly lower. |
| Elbow angle at the top, 3D | — | — | L 57° / R 77° | **Unresolved.** The 3D model says 20° apart; measured in the image plane the same angles are 12.8° and 10.3°, i.e. 2.6° apart. A model estimate and a direct measurement disagree, so no asymmetry claim is made from the elbows. A side camera would settle it. |
| Grip | — | ±21.2 cm from the grip centre | — | Symmetric to the millimetre. |
| Body offset from the grip centre | — | hips −0.8 cm | hips +0.6 cm, shoulders −0.1 cm | He hangs and pulls centred. |
| Lead arm | — | — | 8 of 11 reps together, 2 left, 1 right | No consistent lead arm. |
| Neck | nose 1.6 cm above the ear line | — | nose 0.7 cm below | He tips his head **back** at the top rather than craning it forward. That is the right direction, but it is 2.3 cm of head extension, and it is part of why the chin reads short: the chin swings up and back rather than up and over. |

**The one-sentence version:** his right shoulder shrugs about 2.5 cm at the top while the
left does not, and his shoulder line runs about 1 cm out of level under load. Everything
else that a single front camera can measure is symmetric.

## Scapular initiation

He gains **14.0 cm of height in the first 0.52 s** before either elbow bends past 150° —
the scapular-depression phase that the coaching literature (Ronai & Scibek 2014) asks for.
That is nearly a quarter of the rep done before the arms start working, and it is done on
both sides together. This is the strongest technical thing in the set.

## Work, power, energy (188 cm, 79 kg, lifted mass 75.5 kg)

| | |
|---|---|
| Work per rep | 445 J — 5.26 kJ for the whole set |
| Mean pull power | 504 W best (rep 2) → 181 W (rep 11) |
| Peak power | ≈ 990 W |
| Peak force on the bar | ≈ 1.19 × body weight |
| Energy, rough | ≈ 1.0 kcal per rep, **≈ 12 kcal for the set** |
| Heat produced | **≈ 45 kJ** (27 kJ from muscle work, 18 kJ isometric) |
| Equivalent weighted 1RM | ≈ +28 kg for one rep (Epley on the lifted mass) |
| BMI | 22.4 |

The energy model is unchanged from the first report: concentric work ÷ 22 % efficiency,
lowering at 35 % of that, plus a 3.5 MET isometric cost for every second on the bar. It is
good for "about 1 kcal per rep" and nothing finer.

## Modelled muscle temperature — the colour on the body

The first video coloured the body by fatigue and called it heat. This one computes a
**temperature rise in degrees Celsius** and says on screen that it is a model. The heat
budget, per muscle:

```
C_m dT_m/dt = share_m · P_heat(t) − k_m(t) · dT_m
C_m     = 3.6 kJ/kg/K × muscle mass          specific heat of skeletal muscle
share_m = %MVIC × mass, normalised           EMG prior (Youdas 2010) × mass (Holzbaur 2007)
k_m(t)  = 42 W/K/kg × mass × (1 − e^(−t/90s)) blood carries heat off, ramping up over minutes
```

`P_heat` is the metabolic power minus the mechanical work that actually leaves the body:
during the pull, work ÷ 0.22 minus the work itself; during the lowering, the negative work
is absorbed and all of its metabolic cost is heat. The isometric "holding on" term is a
whole-body rate, so only the grip's share of it (22 %) is deposited locally, in the
forearms.

The constants come from measurements, not from fitting: González-Alonso et al. (2000)
measured 70 → 126 J/s of heat production in 2.68 kg of working muscle with blood-borne
removal rising from nothing to 112 J/s over three minutes — that fixes both the removal
coefficient and its time constant, and it is why **temperature never falls inside a 53 s
set**. Kenny et al. (2003) measured +2.0 to +3.2 °C in the vastus medialis over 15 minutes
at 60 % VO₂max, so degrees over minutes is the right order of magnitude.

| muscle | mass (kg) | %MVIC | share of heat | ΔT at the end |
|---|---|---|---|---|
| brachioradialis | 0.19 | 62 | 2.9 % | **+2.11 °C** |
| forearm flexors (grip) | 0.71 | 60 | 10.2 % | **+2.07 °C** |
| latissimus dorsi | 0.78 | 124 | 23.2 % | **+2.01 °C** |
| teres major | 0.10 | 99 | 2.3 % | +1.60 °C |
| biceps brachii | 0.43 | 78 | 8.0 % | +1.26 °C |
| brachialis | 0.43 | 78 | 8.0 % | +1.26 °C |
| infraspinatus | 0.35 | 75 | 6.4 % | +1.21 °C |
| posterior deltoid | 0.38 | 60 | 5.4 % | +0.97 °C |
| trapezius | 0.74 | 52 | 9.3 % | +0.84 °C |
| pectoralis major | 0.86 | 44 | 9.1 % | +0.71 °C |
| erector spinae (not painted) | 1.19 | 40 | 11.4 % | +0.65 °C |
| external oblique | 0.33 | 33 | 2.6 % | +0.53 °C |
| rectus abdominis | 0.30 | 20 | 1.4 % | +0.32 °C |
| hip flexors (holding the tuck) | 1.06 | 18 | isometric only | +0.19 °C |
| quadriceps | 3.18 | 8 | isometric only | +0.08 °C |
| gluteus maximus (not painted) | 1.80 | 8 | isometric only | +0.08 °C |
| hamstrings (not painted) | 2.01 | 6 | isometric only | +0.06 °C |
| calves | 1.38 | 4 | isometric only | +0.04 °C |

The legs are in the model because he holds a tucked, crossed-leg position for the whole
set. They take **no share of the work heat** — they do not lift the body — only a slice of
the isometric cost, which is why they finish the set between +0.04 and +0.19 °C and read
cold on screen. That is the honest picture and the reason the legs are blue rather than
unpainted.

Masses are Holzbaur et al. (2007) MRI volumes scaled ×1.40 for a 188 cm man (their ten
subjects averaged 2554 cm³ of upper-limb muscle across five men and five women) at
1.06 g/cm³. Trapezius, oblique, abdominal and erector volumes are estimates and are
flagged as such in the code. Where a muscle was not measured by Youdas — brachialis,
the forearm flexors, the posterior deltoid, the rectus abdominis — the activation is an
assumption, and it is marked in `tools/scripts/pullup_thermal.py`.

**What an infrared camera would show instead.** Not this. Skin over a working muscle
usually *cools* at the start of exercise as blood is routed inward, and warms mostly
after the set: Jung et al. (2021) measured the skin over a trained arm at 35.98 °C at the
start of a set, 36.11 °C at the end, and 37.24 °C five minutes into recovery, with the
target muscle only 0.86 °C warmer than the tissue around it. The colour in this video is
the muscle underneath, from a heat budget, not the skin, and not a measurement.

**Colour is temperature; brightness is activation.** Temperature accumulates slowly and
never falls inside the set. On top of it, the brightness of every region pulses with a
modelled *activation* that follows the movement itself: the EMG phase ordering (pull >
top hold > lowering > hang, Dickie et al. 2017) scaled by the measured pull speed of that
moment. So the map breathes with each rep instead of only creeping upward, and the two
quantities stay separable — the legend names both.

**Where the map is drawn.** Each muscle is a polygon in a canonical body frame — trunk
coordinates for the torso, per-segment coordinates for the arms — warped onto every frame
by that frame's landmarks and then clipped to the silhouette from the matting pass. The
polygons deliberately overshoot the body so the silhouette, not the polygon, sets the
edge. That replaces the first video's nearest-segment banding, which put lats wherever
the outline happened to be and left the arms half-painted.

## Chest flush — the one measured signal

Dennis asked whether the reddening of his chest could be measured and used. It can, and it
is the only quantity in this report that comes from the pixels rather than from the
literature.

Skin over working muscle reddens as blood is routed to it. The index used is
**(R − G) / (R + G) × 1000** over the chest skin, which is insensitive to overall
brightness — necessary, because a phone camera keeps changing exposure and white balance.
Two controls make it defensible:

1. Every sample is taken at the **dead hang after a rep**, where the pose, the distance to
   the camera and the lighting repeat as closely as this clip allows.
2. The same index is computed on a **fixed patch of wall in the same frame** and
   subtracted, so any exposure or white-balance shift moves both and cancels.

| | index |
|---|---|
| Standing on the floor, before the set | 17.6 |
| After rep 1 | 22.9 |
| After rep 5 | 46.8 |
| Plateau, reps 6–11 | 43.6 |
| Wall control across the set | 12.2 → 11.6 (flat, and it drifts the *other* way) |

The flush **doubles over the first five reps and then plateaus** — the shape of a
vasodilation response, not of a linear drift. Correlation with time across the reps is
+0.76; correlation with the modelled latissimus dorsi temperature is **+0.83**. The wall
control correlates −0.51 with time, so the rise is not the camera.

That is a genuine, independent cross-check on the thermal model: a measured signal on the
skin moving with a modelled quantity underneath it. It is still exploratory, and the
report says so: the chest is partly hair, the body moves into the door lintel's shadow at
the top of every rep, and one sample (the failed twelfth attempt) had to be dropped
because he passes in front of the control patch as he drops off the bar. It is a
correlation over eleven points in one set of one person.

## Per rep

| rep | top (s) | chin (cm) | ROM (cm) | up/hold/down (s) | rest (s) | peak v (m/s) | mean W | kcal | effort | RIR | lats ΔT | sh tilt | sway (cm) | eff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 12.4 | −2.7 | 58 | 1.30/0.63/1.00 | 0.93 | 0.96 | 333 | 0.95 | ×1.51 | 4 | +0.18 | +0.2° | 3.9 | 85 |
| 2 | 15.7 | −4.9 | 59 | 0.87/0.77/1.03 | 0.43 | 1.01 | 504 | 0.89 | ×1.00 | 4 | +0.36 | +4.2° | 2.6 | 78 |
| 3 | 18.8 | −3.7 | 60 | 0.97/0.87/1.03 | 0.70 | 1.03 | 458 | 0.94 | ×1.10 | 5 | +0.54 | +0.4° | 2.0 | 84 |
| 4 | 22.5 | −5.3 | 60 | 0.90/0.93/1.13 | 0.87 | 1.08 | 497 | 0.96 | ×1.01 | 5 | +0.73 | +3.5° | 4.7 | 78 |
| 5 | 26.2 | −3.5 | 61 | 1.00/0.90/1.27 | 1.40 | 0.97 | 449 | 1.03 | ×1.12 | 4 | +0.91 | +2.3° | 5.5 | 84 |
| 6 | 31.2 | **−1.8** | 61 | 1.03/0.73/1.20 | 0.60 | 0.83 | 436 | 0.95 | ×1.16 | 2 | +1.10 | +1.2° | 6.2 | **86** |
| 7 | 34.8 | −6.9 | 58 | 0.93/0.90/1.03 | 0.50 | 0.84 | 460 | 0.90 | ×1.09 | 3 | +1.27 | +0.8° | 5.3 | 72 |
| 8 | 38.3 | −4.7 | 59 | 1.17/0.87/1.10 | 0.70 | 0.78 | 377 | 0.95 | ×1.33 | 2 | +1.43 | +1.5° | 4.0 | 79 |
| 9 | 42.5 | −4.8 | 61 | 1.47/0.90/1.40 | 1.00 | 0.68 | 309 | 1.05 | ×1.63 | 1 | +1.60 | +0.7° | 2.9 | 81 |
| 10 | 47.7 | −5.3 | 62 | 1.90/1.13/1.63 | 2.00 | 0.53 | 240 | 1.21 | ×2.10 | 0 | +1.75 | +2.4° | 1.9 | 78 |
| 11 | 54.9 | −4.1 | 60 | 2.47/0.93/2.03 | 1.77 | 0.40 | 181 | 1.24 | ×2.78 | 0 | +1.88 | +1.8° | 4.6 | 80 |
| **fail** | 62.0 | **−19.7** | 50 | 2.57/0.67/0.40 | — | 0.35 | 146 | 0.84 | ×3.46 | 0 | +1.98 | +2.8° | 3.7 | 46 |

Effort is the fastest rep's mean pull speed divided by this rep's. RIR is estimated from
peak-velocity loss at roughly one rep per 9 % lost.

## What to change, in order of size

1. **Four more centimetres at the top.** Every rep is short of a judge's chin-over-bar.
   The pause at the top is already there, so the range is available — it is the last few
   centimetres of pull that stop early. Pulling the chest to the bar rather than the chin
   over it is the usual cue.
2. **Stop the right shoulder shrugging.** It rides 2.5 cm closer to the ear at the top
   while the left does not. Same cue as (1) in practice: keep the shoulder blades down
   and pull with the back rather than finishing with the traps.
3. **Hold the legs still.** 38° of knee tuck per pull is not a kip but it is movement a
   judge can point at, and it is free to fix.
4. **The set was already honest.** Velocity-based guidance says stop a set at 20–30 %
   speed loss; that point was rep 6. He went to rep 11 and then failed a twelfth. Nothing
   to fix, but the last four reps cost 2–3× the effort of the first ones for the same work.
5. **Nothing wrong with the lowering.** 1.26 s on average and it lengthens with fatigue,
   which is control, not decay.

## Caveats

- One camera, front-on. Everything is an image-plane measurement, corrected for camera
  roll but not for the remaining perspective. Depth is not measured.
- The chin numbers carry ±1.5 cm, dominated by the assumed mouth-to-chin proportion.
  The verdict "short on all 11" would survive an error of 1.5 cm; the best rep would not.
- The centimetre scale carries about ±5 % now (three independent anchors within that
  range), better than the first video's ±10–15 %.
- Every joint angle in 3D is MediaPipe's model estimate, not a measurement. Where the 3D
  and image-plane answers disagree — the elbows — no claim is made.
- The temperature map is a model on a literature prior, not a measurement. Muscle masses
  for the trapezius, obliques, abdominals and erectors are estimates; four activation
  values are assumptions.
- Leg angles use extrapolated landmarks whenever the crossed ankles occlude each other.

## Files

- `pullup/out/pullup2-reel.mp4` — the 19.7 s Reel (cold open on the failed attempt, rep 1
  at real speed, reps 2–11 at ×6, the failure at real speed, the judge's card), on the
  jungle plate with a see-through form grid.
- `pullup/assets/jungle_monkeys_plate.jpg` and `pullup/assets/ATTRIBUTION.md` — the
  backdrop and the credit line the post must carry.
- `pullup/work2/redness.json` — the measured chest-flush series.
- `pullup/out/pullup2-analysis-heat.mp4` — the full-length analysis with the summary card.
- `pullup/out/pullup2-dashboard.png` — twelve panels.
- `pullup/out/pullup2-report.html` — the interactive report.
- `pullup/work2/analysis.json` — every per-frame signal and per-rep number.
- `pullup/work2/straight.mp4` — the de-rolled master everything was measured on.
- References: `references/pullup-thermal/README.md` (temperature, technique standards,
  muscle masses) and `references/pullup-emg/README.md` (activation values).
