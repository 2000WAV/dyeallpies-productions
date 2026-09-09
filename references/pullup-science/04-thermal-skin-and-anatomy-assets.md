# Thermal skin layer (Pennes bioheat), the flush, and licensed anatomy assets

Literature sweep for two extensions to the pull-up thermal model: (1) a skin-surface layer —
"what an infrared camera would actually see" — computed through the muscle→fat→skin stack with
the Pennes bioheat equation, and (2) a physiological model of cutaneous vasodilation (the skin
flush) to compare against the measured chest-skin redness. Builds on `../pullup-thermal/README.md`
(González-Alonso 2000, Kenny 2003, Jung 2021, Holzbaur 2007, specific heat 3.6 kJ/kg/K) and
`../pullup-emg/README.md` — those numbers are cross-referenced, not repeated in full. Raw
extraction in `data/bioheat-tissue-parameters.csv`, `data/skin-blood-flow-and-perfusion.csv`,
`data/skin-temperature-responses.csv`. Abstracts in `abstracts/*.txt`. Anatomy-asset licence audit
and downloads in `anatomy-assets/CREDITS.md`. Download log in `DOWNLOADS.md` under today's date.

**Read this first:** the IT'IS Foundation's tissue-properties database
(itis.swiss/virtual-population/tissue-properties) could **not** be scraped this session — its
per-tissue tables render via client-side JavaScript, and both `curl` and `WebFetch` returned only
the page shell with no numeric data. Every bioheat-parameter number below that is not traced to a
named physiology paper is marked **ESTIMATE** and its actual (non-IT'IS) provenance is stated. Do
not represent any ESTIMATE row as IT'IS-sourced in the pipeline or on screen.

## 1. Pennes bioheat parameters — muscle / fat / skin

Pennes bioheat equation: `ρc (∂T/∂t) = k∇²T + ρ_b c_b w_b (T_a − T) + Q_met`, where ρ=tissue
density, c=specific heat, k=thermal conductivity, w_b=blood perfusion rate, T_a=arterial blood
temperature (~37°C), Q_met=metabolic heat generation.

| tissue | parameter | value | condition | source | status |
|---|---|---|---|---|---|
| skeletal muscle | specific heat | 3.6 kJ/kg/K (range 3.6–3.9 across tissue tables) | generic | *Temperature* toolbox review 2022, PMC10274559 (already in `../pullup-thermal/README.md`) | secondary/compiled |
| skeletal muscle | density | 1.06 g/cm³ | generic | Holzbaur 2007 (already in `../pullup-thermal/README.md`) | primary |
| skeletal muscle | effective (perfused) thermal conductivity, forearm | 0.56 → 1.91 W/m/K rising with blood flow, 15→36°C water immersion | in vivo, resting forearm | **Ducharme & Tikuisis 1991**, *J Appl Physiol* 70(6):2682-90, PMID 1885465 | **primary** |
| skin + subcutaneous fat | effective thermal conductivity, forearm | 0.28 → 0.73 W/m/K, same protocol | in vivo, resting forearm | Ducharme & Tikuisis 1991, PMID 1885465 | **primary** — muscle tissue accounted for 92±1% of total forearm insulation across the whole range |
| skin | thermal conductivity (static/table values) | 0.187–0.5 W/m/K (wide spread across sources) | generic | compiled from multiple secondary bioheat-engineering papers (WebSearch synthesis; not independently verified against one named primary paper) | **ESTIMATE** |
| subcutaneous fat | thermal conductivity (static/table values) | 0.19–0.23 W/m/K | generic | same as above | **ESTIMATE** |
| skin | specific heat | 3.5–4.3 kJ/kg/K (or ~4.3 J/cm³/K volumetric) | generic | compiled secondary sources | **ESTIMATE** |
| subcutaneous fat | specific heat | 2.3–2.5 kJ/kg/K | generic | compiled secondary sources (fat's low water content lowers c vs muscle/skin) | **ESTIMATE** |
| blood | specific heat / density | 3.77 kJ/kg/K / 1060 kg/m³ | generic | widely-cited engineering bioheat constant | **ESTIMATE** — not traced to a physiology primary source this session |
| skin (epidermis+dermis) | thickness | 1.5–2.0 mm | generic ultrasound convention (what ultrasound software attributes to "skin" vs "fat" layer) | compiled secondary | **ESTIMATE** |
| subcutaneous fat | thickness, upper arm (triceps site) | 3.00 mm (mean) | lean-to-overweight men, BMI 20–28.4 | 8-site standardized ultrasound validation study, PMC6214952 | primary (PMID/author not independently re-confirmed this session — re-verify before quoting in a script) |
| subcutaneous fat | thickness, forearm (brachioradialis site) | 1.15 mm (mean) | same population | PMC6214952 | same caveat |
| subcutaneous fat | thickness, anterior trunk (chest+abdomen composite) | 4.69 mm (mean, includes fibrous septa) | same population | PMC6214952 | same caveat — this is a chest+abdomen average, not chest alone; treat as an upper bound for the chest site |
| core body temperature | rest | 37.0°C (36.80°C oesophageal) | rest | Kenny et al. 2003, PMID 12598487 (in `../pullup-thermal/README.md`) | primary |
| vastus medialis muscle | rest, by depth | 36.14 / 35.86 / 35.01°C at 10/25/40 mm | rest | Kenny et al. 2003, PMID 12598487 | primary — note the *shallower* probe reads warmer at rest in this dataset, not the deeper one; do not assume a monotonic "deeper = warmer" gradient without re-reading the original |
| skin/subcutaneous/muscle/core (29-site map) | rest, comfort/heat/cold | tabulated (esophagus, rectum, ear canal; back+thigh muscle at 20/40mm; 6 subq sites; 16 skin sites) at 27°C comfort, 45°C heat, 15°C cold | rest, nude, 6 men | **Webb 1992**, *Eur J Appl Physiol* 64(5):471-6, PMID 1612090 | primary reference exists; exact mean values are in the paywalled full text only — abstract confirms the core-shell structure and that the subq-to-skin gradient differed substantially between comfort/sweating-onset/shivering-onset, but the numbers themselves are **NOT extracted** this session |
| core-to-skin gradient | rest, cool ambient (approximate) | ~8–9°C (derived by subtracting a reported cool-ambient Tsk of ~28.7±1.1°C from Tcore ~37°C) | rest | derived by subtraction from a heat-acclimation exercise study found via WebSearch (title/PMID not independently confirmed) | **ESTIMATE — do not cite as a direct measurement** |
| core-to-skin gradient | exercise in heat, mid-bout → end of bout | 1.3–2.6°C (mid) → 2.1–3.5°C (end), narrower at higher ambient temperature | cycling, 18/26/42°C ambient | WebSearch summary of a cardiovascular/hot-skin cycling study; **PMID not confirmed this session** | **ESTIMATE — re-verify source before quoting in a script or on screen** |
| model of the whole passive thermal system | — | multi-node/multi-segment passive+active human thermoregulation model, the standard reference architecture for exactly this kind of layered bioheat scheme | — | **Fiala, Lomas, Stohrer 1999**, *J Appl Physiol* 87(5):1957-72, PMID 10562642 | primary (methods paper; use as the architectural reference for the 1-D scheme below, not as a source of specific tissue-constant values — those weren't recoverable from the abstract) |

## 2. Measured skin-temperature responses during/after upper-body exercise

Full detail in `data/skin-temperature-responses.csv`.

| study | exercise | region | ΔT during | ΔT after | time to peak |
|---|---|---|---|---|---|
| **Jung et al. 2021** (PMID 34209377, in `../pullup-thermal/README.md`) | arm curl / kickback / lateral raise, 10 kg | skin over target muscle | +0.13°C/min (35.98→36.11°C) | +0.47°C/min over 5 min recovery (→37.24°C) | after the set, during recovery |
| **Kenny et al. 2003** (PMID 12598487, in `../pullup-thermal/README.md`) | knee extension, 60% VO2max, 15 min | vastus medialis, intramuscular | +2.00/+2.37/+3.20°C at 10/25/40mm | still +0.92/+1.05/+1.77°C at end of recovery | end of the 15-min bout — this is muscle, not skin |
| **Merla et al. 2010**, *Ann Biomed Eng* 38(1):158-63, PMID 19798579 | graded treadmill running to max HR | whole-body anterior skin (thighs/forearms earliest) | **decrease** throughout, −3 to −5°C vs baseline at termination | increase during recovery, thighs/forearms earliest | during recovery |
| **Formenti, Ludwig et al. 2016**, *J Therm Biol* 59:58-63, PMID 27264889 | squat, ~50% 1RM, 1s vs 5s tempo | skin over quadriceps | ST changes more slowly at 5s tempo (p=0.002); delta magnitude similar between tempos | tracked through a 480s post-onset window (non-steady-state) | within the 480s window |
| **Perpetuini, Formenti et al. 2022**, *Biology* 11(2):322, PMID 35205188 | unilateral knee extension to exhaustion | exercised vs non-exercised leg; nose tip; corrugator (face) | significant region×time difference (F=15.14, p=0.0018) | single pre-post delta, not a continuous curve | immediately post-exhaustion |
| **Chudecka et al. 2015**, *J Hum Kinet* 49:141-7, PMID 26839614 (open access, PMC4723162) | rowing ergometer (symmetric) vs handball match (asymmetric) | symmetric/asymmetric working-muscle pairs | mean skin temp always **lower** post- than pre-exercise in both groups | single post-exercise timepoint | post-exercise |

**Consensus reaffirmed by every primary source fetched this session:** skin over the working
muscle tends to **drop** during a short bout (cutaneous vasoconstriction diverting flow to
muscle), then **rises** after exercise ends, over minutes. This matches
`../pullup-thermal/README.md`'s existing caveat and should stay on screen: *the colour is modelled
muscle temperature, not skin — a thermal camera pointed at a ~30-60 s pull-up set would show less
warming, later, than the reel's muscle-temperature overlay implies.*

## 3. Vasodilation / flush time course

### 3a. Skeletal-muscle blood flow (drives internal heat removal, not the visible flush)

| measure | rest | exercise | onset dynamics | source |
|---|---|---|---|---|
| femoral artery blood flow, knee-extensor | ~0.3 L/min | 6–10 L/min (linear with power: Q=1.94+0.07·load); peak perfusion ~100-fold rest | T1/2 = 2–10 s (muscle-pump-driven first rise); steady state within ~10–150 s | **Saltin, Rådegran, Koskolou, Roach 1998** review, *Acta Physiol Scand* 162(3):421-36, PMID 9578388 |
| immediate exercise hyperemia | — | substantial rise in first 0–5 s; rapid vasodilation detectable within ~2 s | muscle pump (venous-pressure-lowering) + an undetermined rapid vasodilator signal (candidates: K⁺, adenosine, mechanical) | **Tschakovsky & Sheriff 2004** mini-review, *J Appl Physiol* 97(2):739-47, PMID 15247202 |

### 3b. Cutaneous (skin) blood flow — what actually produces visible redness

1. **Initial vasoconstriction, not dilation, at exercise onset.** Cutaneous vascular conductance
   (CVC = laser-Doppler flux / mean arterial pressure) falls **significantly within the first
   minute** of dynamic exercise, for two-leg exercise at either workload and one-leg exercise at
   the higher workload; the reduction correlates with *absolute* external work load (r=0.75), not
   relative (%capacity) load; isometric exercise and small-muscle-group dynamic exercise do **not**
   significantly reduce CVC. — **Taylor, Johnson & Kosiba 1990**, *J Appl Physiol* 69(3):1131-6,
   PMID 2246162.
2. **The active (thermal) vasodilator system has no resting tone** and only switches on once
   deep-body temperature rises; it is mediated by cholinergic co-transmission (candidates: nitric
   oxide, VIP, prostaglandins, substance P — no single confirmed sole mediator). This is distinct
   from, and only unmasked by *withdrawing*, the tonically-active noradrenergic vasoconstrictor
   system. — **Charkoudian 2010** review, *J Appl Physiol* 109(4):1221-8, PMID 20448028 (open
   access, PMC2963327).
3. **The core-temperature threshold for active cutaneous vasodilation is raised by exercise
   itself**, from 36.95±0.06-0.07°C at rest to 37.20–37.23±0.04-0.05°C during dynamic exercise (a
   ~0.25–0.28°C upward shift), whether or not local adrenergic vasoconstrictor control was
   pharmacologically blocked — i.e. the shift works through *delaying the vasodilator system*, not
   through extra vasoconstrictor drive. — **Kellogg, Johnson & Kosiba 1991**, *J Appl Physiol*
   71(6):2476-82, PMID 1778949.
4. **The vasodilation-onset trigger is dominated by internal/deep-tissue temperature, not skin
   temperature**, and more so at higher relative exercise intensity: in a light-exercise (20%
   VO2peak) condition the CVC rise appeared only in the warmest ambient condition tested, while at
   moderate exercise (50% VO2peak) it appeared across all three ambient conditions tested. —
   **Demachi et al. 2013**, *Int J Biometeorol* 57(4):589-96, PMID 22960747.
5. **Implication for a ~30–60 s pull-up set:** points 1–4 together say the *classical* thermally-
   driven active cutaneous vasodilation (the "exercise flush") requires a core-temperature rise of
   several tenths of a degree above an already-elevated exercise threshold — this is a
   multi-minute phenomenon in the cited studies (7–30 min bouts), not a sub-minute one. A single
   pull-up set is very unlikely to trigger it. What a camera **could** plausibly catch in a short,
   maximal, Valsalva-heavy set instead: (a) the well-documented first-minute cutaneous
   *vasoconstriction* (which would read as *less* redness, if anything, over the chest specifically
   only insofar as chest skin behaves like the forearm skin measured in these studies — not
   independently confirmed for the chest); (b) local skin-surface changes from increased venous
   pressure and engorgement during a forceful Valsalva strain against a closed glottis (straining
   under load produces systolic pressures reported in excess of 300 mmHg in the general
   Valsalva/resistance-exercise literature — a mechanical/hemodynamic engorgement effect, not the
   thermal reflex); (c) an immediate, local, load-correlated non-thermal component in muscle blood
   flow (section 3a) that is a *muscle*, not *skin*, phenomenon and would not by itself redden the
   overlying skin within a single set. **None of (a)–(c) is a confirmed primary-sourced mechanism
   for chest-skin redness specifically during a bodyweight pull-up set — flag any on-screen
   redness claim as a plausible-mechanism list, not a demonstrated one, until a primary source
   measuring chest skin (not forearm/thigh/quadriceps) during a short resistance set is found.**
6. **Histamine** is a documented contributor to *post*-exercise vasodilation (blocking both H1 and
   H2 receptors together removed roughly 80% of sustained post-cycling vasodilation in the
   secondary literature found this session) but this is a recovery-phase, minutes-to-90-minutes
   phenomenon, not an intra-set one — found via WebSearch synthesis, **no PMID independently
   confirmed this session; do not cite a specific paper for this claim without re-fetching it.**

## 4. Anatomy assets — licence table (condensed; full audit in `anatomy-assets/CREDITS.md`)

| source | licence | usable (CC BY/CC0/PD only)? |
|---|---|---|
| Wikimedia Commons, Gray's Anatomy plates (1918) | Public domain | **Yes** — downloaded, 23 files |
| Wikimedia Commons, Mikael Häggström originals | CC0 1.0 | Yes (not needed/downloaded this session) |
| BodyParts3D / Anatomography (DBCLS) | CC BY-SA 2.1 Japan | **No** — ShareAlike |
| Z-Anatomy | CC BY-SA 4.0 | **No** — ShareAlike (also a BodyParts3D derivative) |
| OpenAnatomy | not stated / unresolved per-atlas | Unresolved — do not use without checking |
| Anatomy Standard | CC BY-NC 4.0 | **No** — NonCommercial |
| Visible Human Project (NLM) | Public domain | Yes in principle, wrong asset type (cadaver cross-sections, not muscle outlines) |
| Sketchfab "CC BY" search results | varies per model, unverified | Not vetted; download also needs an authenticated account |
| OpenSim `arm26` (Holzbaur-derived) | **CC BY 3.0** (embedded in file) | **Yes** — downloaded; biceps+triceps muscle-path geometry |
| OpenSim Rajagopal 2016 full-body | **MIT** (SimTK page) | Yes but gait/trunk-focused, no arm/shoulder detail — downloaded anyway as a second confirmed-permissive example |
| Holzbaur (2005) full upper-extremity / MoBL-ARMS | unresolved — SimTK login/click-through required | **Not fetched** — the one follow-up worth doing by hand if literal whole-arm muscle-path geometry is wanted |

Downloaded files live in `anatomy-assets/grays-anatomy/` (23 PNG/JPG plates and individual
muscle-highlight diagrams covering chest, back, shoulder, upper arm and forearm) and
`anatomy-assets/opensim-models/` (`arm26/arm26.osim`, `rajagopal/Rajagopal2016.osim` +
`README.txt`).

## 5. How to use in the pipeline

### 5a. A concrete 1-D layered bioheat scheme (muscle → fat → skin)

For each per-muscle heat region already computed by `tools/scripts/pullup_heat.py` (muscle core
temperature `T_muscle(t)` from the existing `C dT/dt = share·P_heat − k(t)·dT` model), add two more
1-D nodes along the outward normal at that body region — fat and skin — each obeying the discretized
Pennes equation:

```
node i:  ρ_i c_i A_i Δx_i · dT_i/dt = k_i A_i (T_{i-1} − T_i)/Δx_i        (conduction from the node inward)
                                     − k_i A_i (T_i − T_{i+1})/Δx_i        (conduction to the node outward)
                                     + ρ_b c_b w_b,i · A_i Δx_i · (T_a − T_i)   (blood-borne exchange, fat≈0, skin>0 and rising with exercise)
                                     + Q_met,i · A_i Δx_i                  (near-zero for fat and skin)
                                     − h_conv A_i (T_skin − T_ambient)      (skin's outer boundary only: convection+radiation to air)
```

Concretely, per region, per this session's numbers (fat and skin values marked ESTIMATE per
section 1 — use the Ducharme & Tikuisis 1991 in-vivo forearm values as the anchor where a
region-specific in-vivo number isn't available):

1. **Muscle node** — already modelled; feed its `T_muscle(t)` output as the fixed inner boundary
   condition for the fat node (do not re-derive it here).
2. **Fat node** — thickness by region from section 1 (chest+abdomen composite 4.69mm, upper arm
   3.00mm, forearm 1.15mm — all **ESTIMATE-adjacent primary numbers**, see caveats above; back not
   separately measured this session, use the anterior-trunk value as a stand-in and flag it).
   k≈0.19–0.23 W/m/K (ESTIMATE) or Ducharme's in-vivo 0.28–0.73 W/m/K skin+fat combined range if
   treating fat+skin as one lumped node instead (simpler, defensible given the combined-layer
   primary data actually exists for that lumping, unlike the split values). w_b≈0 (fat is poorly
   perfused; Ducharme's data support treating skin+fat's *combined* effective k as blood-flow-
   dependent, which implicitly captures perfusion effects without needing a separate w_b term for
   fat alone).
3. **Skin node** — thickness ~1.5–2.0mm (ESTIMATE). k and c per section 1 (ESTIMATE — or use
   Ducharme's combined skin+fat effective conductivity if lumping, which is the **better-supported
   choice given this session's actual source material**). w_b,skin is the load-bearing term for
   the flush: **falls in the first minute of exercise** (Taylor/Johnson/Kosiba 1990) before any
   possible later thermal-vasodilation rise — for a ~30-60s pull-up set, model w_b,skin as flat-to-
   falling, not rising; do NOT apply a rising vasodilation curve within a single short set unless
   core temperature is separately tracked and shown to cross the ~37.2°C exercise-shifted
   threshold (Kellogg 1991), which a single set essentially never will.
4. **Outer boundary** — standard convective/radiative loss to ambient air, `h_conv` typically
   ~5-10 W/m²/K free convection indoors (not independently sourced this session — use existing
   pipeline defaults if any, else treat as a display-tunable constant, not a physiology claim).

**Practical simplification actually justified by what was found this session:** because Ducharme &
Tikuisis 1991 is the one primary in-vivo human dataset recovered here for both thickness-adjacent
and conductivity numbers together, lump fat+skin into a **single outer node** with effective
conductivity 0.28–0.73 W/m/K (rising with local blood flow) rather than modelling fat and skin
separately with the ESTIMATE-tagged split values — this is more defensible than the alternative and
should be the pipeline's default; only split them if a chest/back/arm-specific in-vivo skin+fat
dataset is found later.

### 5b. What the skin-node output should say on screen

Given section 2 and 3, the honest on-screen behaviour for a 30-60s set is: the fat+skin node's
temperature should **lag and under-shoot** the muscle node throughout the set (high thermal mass,
low conductivity, and — per Taylor/Johnson/Kosiba 1990 — *falling*, not rising, skin blood flow in
the first minute), then continue rising for several minutes into the "recovery" state after the
last rep (per Merla 2010, Jung 2021, Chudecka 2015). If the reel only shows the working set itself,
the skin layer's colour change should be visually minor and possibly in the *cooling* direction —
this is the finding to defend if anyone asks "why doesn't the skin look as hot as the muscle."

### 5c. Which anatomy asset to use for muscle fibre directions

- **For the visible outline / region shape on screen (chest, back, shoulder, upper arm, forearm):**
  use the Gray's Anatomy plates in `anatomy-assets/grays-anatomy/` — Public Domain, no
  attribution legally required (though crediting "Gray's Anatomy, 1918, public domain via
  Wikimedia Commons" costs nothing and matches the channel's existing citation habits). The
  individual muscle-highlighted diagrams (`musculus-biceps-brachii.png`,
  `musculus-triceps-brachii.png`, `musculus-deltoideus.png`, `musculus-infraspinatus.png`,
  `musculus-teres-major.png`, `musculus-teres-minor.png`, `musculus-subscapularis.png`,
  `musculus-supraspinatus.png`, `musculus-brachialis.png`, `musculus-brachioradialis.png`,
  `musculus-coracobrachialis.png`) are cleaner per-muscle shapes than the full regional plates and
  are the better source to trace fibre-direction lines from by hand or with an edge-detector.
  Latissimus dorsi, trapezius and pectoralis major have no individual highlight plate in this set —
  use `gray409-back-upperlimb-to-vertebral-column.png` and `gray410-pectoralis-major.png` instead.
- **For an actual anatomically-derived line-of-action (not a hand-traced approximation from a
  flat plate):** use `anatomy-assets/opensim-models/arm26/arm26.osim` (CC BY 3.0) — it carries
  real 3D origin/insertion/via-point coordinates for biceps brachii and triceps brachii on a
  generic skeleton, which can be projected onto the pose-landmark skeleton the pipeline already
  tracks (MediaPipe 33-point) to get a true muscle-belly direction vector for the upper-arm heat
  regions, rather than assuming a straight line between two hand-picked landmarks. This only
  covers the elbow flexors/extensors; it does **not** cover lats, pecs, delts, or the rotator cuff
  — for those, either stay with the Gray's-plate hand-traced approach, or pursue the Holzbaur
  (2005)/MoBL-ARMS full upper-extremity model by hand-downloading it from SimTK (flagged as
  unresolved in section 4 — needs an authenticated login this session didn't have).
- **Do not use** BodyParts3D/Anatomography or Z-Anatomy renders for anything that ends up in the
  published Reel, even for internal draft/reference purposes that might accidentally get
  reused later — both are ShareAlike and both explicitly excluded by Dennis's constraint.
