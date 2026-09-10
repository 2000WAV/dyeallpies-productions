# The push-up model behind the heat map (v1, 2026-09-10)

Written by Fable for Dennis's push-up video. The pull-up model (`pullup/MUSCLE-MODEL.md`, v4.3) is
the parent: the same chain of inverse dynamics → force sharing → muscle mechanics → fatigue that
carries over → heat → temperature, and the same colour definition. What changes is the camera,
the joints and the evidence. Implemented in `tools/scripts/pushup_thermal.py`; the geometry in
`tools/scripts/pushup_recon.py` and `tools/scripts/analyze_pushups.py`; every number below has its
file in `references/pushup-science/` (or the pull-up archive where stated).

## 1. What this camera can and cannot see

One phone standing on its edge at the head end, lens 13 cm above the floor, looking along the
body 7.8° upward (two vanishing points from the corridor and the door jambs; f = 1694 px). The
head comes toward the lens at the bottom of every rep. Nothing here measures height directly, so
the geometry is closed with lengths measured on Dennis in pull-up set #3's rectified doorway plane
(the same MediaPipe landmarks): forearm 28.4 / 27.0 cm, elbow-to-shoulder 26.6 / 25.2 cm, trunk
(shoulder-mid to hip-mid, arms down) 58.7 cm, hip landmark width 19.0 cm, ear width 15.1 cm.

| quantity | how it is measured | what it rests on |
|---|---|---|
| hips (position, height) | the hip landmarks' picture width → distance (f · 19.0 cm / px), their ray → position | the hip landmark width carried from set #3 (±3 % → ±1 cm of height); hidden behind the head at the bottom of each rep (then bridged from the shoulders and the toes with the trunk and leg lengths) |
| shoulders | on their rays, at the trunk length from the hip midpoint (the near root) where the hips are seen; where the hips are hidden, at the depth that makes their picture width the set's 29.2 cm | the rigid trunk; checked: the shoulder width comes out 29.2 cm on every frame type, and the shoulders at the bottom sit 16 cm above the floor while the nose (independent scale) touches it |
| camera height h_c | the one free scale: the wrists' rays meet the floor at a distance ∝ h_c; chosen so the wrist-to-shoulder distance at the locked tops equals the arm (53.1 cm) | 13.0 cm; the phone's lens standing on its edge is 12.5 cm; YOLO's ankle row agrees within 16 px. **A tape on the hand spacing would replace this** (38 cm reconstructed) |
| elbow angle | the law of cosines over the wrist-to-shoulder distance | no elbow landmark; near lock-out 2 cm is 20°, so lock-out is judged at 140° (94 % of the arm) with MediaPipe's 3D angle beside it |
| elbow position (levers) | the circle the two arm lengths allow, placed by the elbow flare read where the elbows are in frame (26 / 35° median) and interpolated across the bottoms | assumed: the flare changes slowly; ranked below |
| toes (the pivot) | hips + 0.95 m along the body line, on the floor | hip-to-ankle 80.5 cm standing (set #3) + the foot; YOLO's ankles sit within a degree of the horizon and cannot be ranged |
| nose, ears | the ear-width scale, every frame | the witness at the bottom: nose −1 ± 2 cm, ears 7 cm |

Results of `analyze_pushups.py` on this set: 30 reps, none failed; shoulder 53 cm (top) → 16 cm
(bottom); elbow 69° at the bottom (58–99), upper arm past parallel on every rep (the shoulder
below the elbow, 22 cm); lock-out on every rep; body line 173° mean, hip sag 1 → 7 cm over the
last ten reps; hand spacing 38 cm, 1.3 × the landmark shoulder width; flare ~40°; peak push speed
0.84 m/s, −26 % by the end against the fastest rep (+14 % against rep 1, which was slow).

## 2. The formulation

### 2.1 Inverse dynamics

The hands carry a **measured** share of body weight: Eckel et al. 2017 (force plate, 16 men,
`02-pushup-hand-force-and-joint-moments.md` §1): 71.95 % with the arms locked, 76.70 % with the
upper arms parallel. The model interpolates between the two with the shoulder height and
multiplies by (g + a_com)/g, the vertical acceleration of the body's centre of mass from the
reconstruction (de Leva 1996 segment masses, `pullup-science/data/pullup-energy-and-segments.csv`).
The analysis' own quasi-static moment balance about the toes gives 76 / 82 %, 5 points above
Eckel, and is printed beside it. Peak hand force 967 N (1.25 BW; the dynamic literature has 1.3–1.6
BW at 60 reps/min, Rozenek 2022).

The force is vertical through each hand (friction ignored, stated). Per arm:

    M_elbow    = F/2 · lever_el      lever_el = horizontal wrist-to-elbow distance
    M_shoulder = F/2 · lever_sh      lever_sh = horizontal wrist-to-shoulder distance
    M_wrist    = F/2 · 2 cm          the centre of pressure ahead of the wrist joint (assumed)

On this set: elbow 34 N·m median through the push (peak 93 at a few frames), shoulder 96 N·m
median (peak 160), wrist 10 N·m. **Donkers, An, Chao & Morrey 1993** measured the push-up's elbow
torque at 23 N·m = 56 % of their subjects' MVIC; against Holzbaur 2007's 60.5 N·m elbow-extension
norm the model's 34 N·m is 55 %: the one push-up joint moment that has been measured agrees. **No
push-up shoulder moment has ever been measured** (`02-*.md` §4), and the shoulders here sit 17–23 cm
ahead of the wrists at the top (hands placed under the chest), so the shoulder flexors are loaded
even at lock-out; a tape on the hand spacing would confirm the lever.

### 2.2 Force sharing (Crowninshield & Brand 1981, p = 3, closed form as in the pull-up model)

| joint | muscles (F_max = 50 N/cm² × PCSA) | moment arm | source |
|---|---|---|---|
| elbow extension | triceps long 798.5 + lateral 624.3 + medial 624.3 N; anconeus 350 N | 2.3 cm (triceps), 1.2 cm | arm26 / Holzbaur 2005 Table 1 (archived extract); Murray, Buchanan & Delp 2000 Table 2 |
| shoulder flexion / horizontal adduction | pectoralis major clavicular 364.4 + sternal 515.4 + costal 390.5 N; anterior deltoid 1142.6; coracobrachialis 242.5; biceps long head; middle deltoid (small arm) | pec **4.0 cm assumed** (the largest, Kuechle 1997's ranking); anterior deltoid **3.6 cm calibrated** so ant. deltoid / pec = 0.9 (Snarr & Esco 2013 0.93, Calatayud 2014 0.89; the share ratio is √(rF/rF)); coracobrachialis 2.0 assumed | Holzbaur 2005; Kuechle 1997 (abstract, ranking only; numbers paywalled) |
| wrist extension | extensors ~600 N | 1.5 cm assumed | Holzbaur 2005 order of magnitude |

Strength factors: the elbow keeps the pull-up's athlete factor 1.2 (Donkers' 56 % is reproduced
with it). The shoulder gets **2.0, calibrated** (§5 rank 1): with 1.2 the pec sat at 1.0 whole rep
and its fatigued pool at 80 %, which is failure by rep 15 under Frey-Law's shoulder rates, while
Dennis did 30 reps at −26 % speed; no norm for horizontal flexion exists (Holzbaur 2007 measured
abduction / adduction only). With 2.0 the whole-rep pec is 0.52 and the pool ends at 75 %, the
triceps / pec ratio 1.25, at the top of the literature's 0.58–1.17 band.

### 2.3–2.7 Hill force–velocity, activation dynamics, fatigue, heat, temperature

Unchanged from the pull-up model (functions imported from `pullup_thermal4`): Hill 1938 with a/F₀
= 0.25 and the 1.6 eccentric plateau; Thelen 2003 τ = 15 / 50 ms; the Xia & Frey-Law 2008 three
compartments with Frey-Law, Looft & Heitsman 2012 Table 1 rates (elbow 0.00912 / 0.00094, shoulder
0.01820 / 0.00168, trunk, grip, knee rows for the legs; verified from the archived full text in
v4.3) and Looft 2018's rest multiplier when the target load drops under 2 % (it never does inside
this set: the plank keeps every prime mover loaded, so the pools only grow until the hands leave
the floor); Umberger 2003's heat structure; González-Alonso 2000's heat balance.

The **heat budget** is the one directly measured push-up energy figure: **Nakagata, Yamada & Naito
2022**, 0.77 ± 0.20 kcal per push-up by indirect calorimetry (`03-*.md` §4.1; the PDF is in
`papers/`), which is within 4 % of the Compendium's 7.5 MET rating for vigorous calisthenics. The
analysis' own budget (work / 22 % + eccentric 35 % + a 3 MET plank) gives 0.48 kcal a rep; a
measurement beats an assumed efficiency, so the muscles' heat is scaled to 0.77 × 30 = 23 kcal
(97 kJ) plus the plank holds (110 kJ total), and the screen says "about 0.8 kcal a rep".

### 2.8 Muscles without a lever the camera can see

Each ratio from ONE study, never across studies (the push-up literature normalises to different
references, `01-*.md` header):

| muscle | drive | source |
|---|---|---|
| serratus anterior | 0.77 × pec, + 0.30 × pec as the elbow straightens past 60° of flexion | Youdas 2010 (whole rep); San Juan 2015 (SA peaks by 55° of elbow extension, direction only) |
| upper trapezius | 0.20 × pec | Calatayud 2014 (5.9 / 29.6; the lowest of the girdle) |
| lower / middle trapezius | 0.25 × pec | ESTIMATE (not measured in a standard push-up) |
| latissimus dorsi | 0.25 × pec | Batbayar 2015, push-up plus, 16.6 %MVC (the only number) |
| posterior deltoid | 0.18 × pec | Youdas 2010 11–21 %MVIC |
| biceps, brachialis, brachioradialis | 0.12 / 0.10 / 0.12 × triceps | Alizadeh 2020 (provisional); co-contraction |
| rectus abdominis, external oblique, erector spinae | 0.22 / 0.14 / 0.05 isometric through the plank, × (1 + 0.10 per cm of measured hip sag) | Tahani 2026 (21.9 / 13.8 / 6.6 %MVIC), Calatayud 2014 (23.9 / – / 2.0) |
| quadriceps, gluteus, hip flexors, hamstrings, calves | 0.12 / 0.06 / 0.10 / 0.05 / 0.05 × (g + a)/g | Calatayud 7.5 and Borreani 20.6 (rectus femoris), Tahani gluteus medius 5.2; the rest ESTIMATES |
| forearm flexors | 0.18 × triceps | ESTIMATE (the hand is flat, not gripping) |

## 3. What the map shows

As in v4.3: colour = 0.9 × (active + fatigued share of the pool) + 0.2 × temperature / 1.5 °C,
on **set #1's pure blue → violet → red → hot scale** (Dennis: the pure blue-red effect was one
reason the first reel went viral), at set #1's 0.96 opacity with the fibre striations reduced to
a faint texture (`pushup_atlas.STRIATION = 0.14` against set #3's 0.36). The triceps peak at the
bottom (1.08: the elbow lever is largest there, and demand exceeds the 62 N·m capacity for a few
frames) and drop to 0.34 in the plank; the pec, anterior deltoid and serratus peak at the bottom
(0.63 / 0.57 / 0.49) and stay at ~0.4 at the top because the shoulders are ahead of the hands; the
wrist extensors sit at 0.6–0.9 throughout (the assumed 2 cm lever, §5); the core at 0.2, the legs
under 0.15, blue. The fatigued pools climb every rep and only start to clear when the hands leave
the floor (pec 75 → 67 % in 5 s, triceps 43 → 40 %).

## 4. Validation (printed by `python pushup_thermal.py analysis.json`, `pushup/work/model_v4.txt`)

| test | model | literature |
|---|---|---|
| triceps / pec, whole rep | 1.25 | 0.58–1.17 across four standard-push-up studies (co-dominant) |
| anterior deltoid / pec | 0.91 | Snarr & Esco 2013 0.93, Calatayud 2014 0.89 |
| serratus / pec | 0.82 | Youdas 2010 0.77 |
| upper trapezius / pec | 0.20 | Calatayud 2014 0.20 |
| elbow moment, push median | 34 N·m = 55 % of the 62 N·m capacity | Donkers 1993: 23 N·m = 56 % of MVIC |
| shoulder moment | 96 N·m median, 160 peak, capacity 280 with the factor 2.0 | no measurement exists |
| wrist moment | 10 N·m | norm 14.0 N·m (Holzbaur 2007) |
| fatigue | pec pool 4 → 75 % over 30 reps, triceps 2 → 43 %, monotonic; release clears 8 / 3 % in 5 s | speed −26 % vs the fastest rep; the last ten reps have 3–5 s top holds and 7 cm of hip sag |
| hand force | Eckel 72 / 77 %; the analysis' balance 76 / 82 % | Gouvali 2005 66 %, Ebben 2011 64 % (secondhand) |

## 5. Assumptions, ranked by how much they move the picture

1. **The camera height / hand position** (h_c = 13 cm from the locked-arm closure): ±3 cm moves
   the wrists ±20 cm along the corridor and the shoulder lever by the same, i.e. the shoulder
   moment ×0.5–2. Three independent numbers agree (the closure, the lens height of a standing iPhone
   14, YOLO's ankle row); a tape on the hand spacing replaces all three.
2. **The shoulder strength factor 2.0**: calibrated so the set does not fail; it sets the pec's
   level and its pool. A horizontal-flexion norm or a dynamometer number replaces it.
3. **The pec's 4.0 cm moment arm** (assumed within Kuechle's ranking) and the deltoid's 3.6 cm
   (calibrated to the EMG ratio): Ackland 2008's or Kuechle 1997's numbers would replace both.
4. **The elbow flare** interpolated across the bottoms where the elbows leave the frame: it places
   the elbow on its circle and sets the elbow lever (±10° of flare ≈ ±3 cm of lever at the bottom).
5. **The wrist lever 2 cm**: it alone makes the wrist extensors one of the hottest regions.
6. **The hip landmark width 19.0 cm and the trunk 58.7 cm** carried from set #3 (arms in a
   different position there).
7. **The 3 cm wrist landmark height, the 0.95 m hip-to-toe length, the 0.16 m head CM offset,
   the segment CM fractions** in the toe pivot and the moment balance.
8. **Every ratio in §2.8**, and the isometric core / leg levels.
9. **Force–length ignored; segment weights of the arms ignored; both arms share the force equally**
   (the elbow angles differ by up to 20° at the bottom on some reps: the reconstruction says the
   left arm bends deeper).
10. The effort-index weights (0.9 / 0.2) and set #1's LUT: display choices; the legend says "a
    model" on every frame.

## 6. What a second camera would add

A phone at hip height, 3 m to the side: the hand position relative to the shoulders (rank 1),
the elbow's true position through the bottom (rank 4), the chest's distance to the floor directly
(the judge's line, now inferred from the shoulders beside the head), and the hip sag in its own
plane.

## References (all in `references/pushup-science/` unless marked)

Eckel et al. 2017 · Gouvali & Boudolos 2005 · Ebben et al. 2011 (via Adams 2022) · Rozenek et al.
2022 · Donkers, An, Chao & Morrey 1993 · An et al. 1990 / 1992 · Youdas et al. 2010 · Snarr & Esco
2013 · Calatayud et al. 2014 · Borreani et al. 2015 · Freeman et al. 2006 · Cogley et al. 2005 ·
Batbayar et al. 2015 · Ludewig et al. 2004 · San Juan et al. 2015 · Gioftsos et al. 2016 · Tahani
et al. 2026 · Alizadeh et al. 2020 · Kowalski et al. 2022 · Nakagata, Yamada & Naito 2022 · MCO
6100.13A (via two secondary compilations, the .mil pages returned 403) · Kuechle et al. 1997 ·
Holzbaur, Murray & Delp 2005 and Holzbaur et al. 2007, Murray, Buchanan & Delp 2000, arm26, de
Leva 1996, Frey-Law et al. 2012, Looft et al. 2018, Xia & Frey-Law 2008, Thelen 2003, Hill 1938,
Crowninshield & Brand 1981, Umberger et al. 2003, González-Alonso et al. 2000 (pull-up archive).
