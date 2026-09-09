# References — muscle heating, skin temperature, technique standards (pull-up set #2)

Collected 2026-09-06 (night) for the second pull-up video (IMG_5990.MOV). Abstracts fetched
from PubMed E-utilities; the Williamson & Price paper is open access (SESNZ). Used by the
`pullup-video` format's thermal model and technique assessment. See `../pullup-emg/README.md`
for the EMG activation values (Youdas 2010, Dickie 2017) and the fatigue references.

## Muscle temperature during exercise (what a heat map may honestly claim)

- **González-Alonso J, Quistorff B, Krustrup P, Bangsbo J, Saltin B (2000).** Heat production
  in human skeletal muscle at the onset of intense dynamic exercise. *J Physiol* 524(2):603-15.
  PMID 10766936. Five men, 180 s of knee-extensor exercise at ~80 W, active muscle mass
  2.68 ± 0.46 kg. Heat production in the active muscle 70 ± 10 J/s in the first 5 s → ~126 J/s
  at 180 s (+77 %; +107 % from the first 5 s). Heat storage rate 70-80 J/s in the first 45 s,
  falling to 14 ± 10 J/s at 180 s as blood-borne removal rose from ~0 (first 10 s) to
  112 ± 14 J/s. Quadriceps temperature +0.04 °C in the first 5 s, +0.89-1.03 °C over 3 min.
  Mechanical efficiency 53 % → 36 % over the bout. Aerobic share 32 % (first 30 s) → 86 %
  (last 30 s). **Use:** heat removal by blood is negligible for the first ~10 s and reaches
  the production rate only after ~3 min, so within a 50 s set most of the heat is stored.
- **Kenny GP, Reardon FD, Zaleski W, Reardon ML, Haman F, Ducharme MB (2003).** Muscle
  temperature transients before, during, and after exercise measured using an intramuscular
  multisensor probe. *J Appl Physiol* 94(6):2350-7. PMID 12598487. Resting vastus medialis
  36.14 / 35.86 / 35.01 °C at 10 / 25 / 40 mm depth (oesophageal 36.80). 15 min of knee
  extension at 60 % VO2max: muscle +2.00 / +2.37 / +3.20 °C (core +0.55). Still +0.92 /
  +1.05 / +1.77 °C at the end of recovery. **Use:** the working muscle warms by degrees, not
  tenths, over minutes; it cools over tens of minutes, not seconds.
- **Saltin B, Gagge AP, Stolwijk JA (1968).** Muscle temperature during submaximal exercise
  in man. *J Appl Physiol* 25(6):679-88. PMID 5727193 (see `../pullup-emg/`).
- Specific heat of skeletal muscle ≈ 3.6 kJ·kg⁻¹·K⁻¹ (tissue tables, e.g. the *Temperature*
  toolbox review 2022, PMC10274559: human tissues 3.6-3.9 kJ/kg/K).

## Skin temperature (what an infrared camera would actually show)

- **Jung H, Seo J, Seo K, Kim D, Park S (2021).** Detection of Muscle Activation during
  Resistance Training Using Infrared Thermal Imaging. *Sensors* 21(13):4505. PMID 34209377.
  Arm curl / kickback / lateral raise with a 10 kg dumbbell: skin over the target muscle
  35.98 °C at the start, 36.11 °C at the end of the set (0.13 °C/min), 37.24 °C after
  5 min of recovery (0.47 °C/min during recovery). Target muscle vs surrounding skin differed
  by 0.86 °C on average; a CNN on difference heat maps located the working muscle with
  92.3 % accuracy. **Use:** the skin over a working muscle *can* be localised by IR, but the
  warming arrives mostly after the set, and the differences are under 1 °C.
- Consensus of the running / strength thermography literature (ThermoHuman summaries,
  Fernández-Cuevas et al.): skin temperature often *drops* at the start of exercise
  (cutaneous vasoconstriction as blood is routed to the muscle) and rises after it ends.
  **Say on screen and in the report: the colour is modelled muscle temperature, not skin;
  a thermal camera pointed at the set would show less, later.**

## Muscle masses for the per-muscle heat budget

- **Holzbaur KRS, Murray WM, Gold GE, Delp SL (2007).** Upper limb muscle volumes in adult
  subjects. *J Biomech* 40(4):742-9. MRI, 10 adults (5 men, 5 women), total upper-limb muscle
  volume 2554 ± 1167 cm³ (range 1427-4426). Mean volumes per side, cm³ (SD): latissimus
  dorsi 262 (147), pectoralis major 290 (169), deltoid 380 (158), infraspinatus 119 (47),
  teres major 33 (16), subscapularis 165 (64), biceps brachii 144 (69), brachialis 144 (64),
  brachioradialis 65 (36), triceps 372 (177), flexor digitorum superficialis 74 (27),
  flexor digitorum profundus 92 (39), flexor carpi radialis 35, flexor carpi ulnaris 37.
  Volume fractions are stable across subjects (r² = 0.98), so scale by total volume: for a
  188 cm / 79 kg trained man use ~1.4 × the means (the study mean is small-bodied; state
  the factor). Density 1.06 g/cm³. Trapezius is not in Holzbaur; take ~250 cm³ per side
  (lower fibres 48 %, middle 28 %, upper 23 % of the volume) and flag it as an estimate.

## Technique standards (what "strict" means to a judge)

- **US Marine Corps PFT pull-up rules:** start from a dead hang with the arms fully extended;
  one rep = raise the body until the **chin is above the bar**, then lower until the arms
  are **fully extended**; no whipping, kicking, kipping or leg movement that assists the
  vertical progress; the elbow lock-out must be visible (sleeves off). Sources:
  topendsports.com/testing/tests/pull-up-pft.htm, marines.com "Pull-Ups Matter".
- **Williamson T, Price P (2021).** A comparison of muscle activity between strict, kipping
  and butterfly pull-ups. *J Sport Exerc Sci* 5(2):149-55. doi:10.36905/jses.2021.02.08.
  Strict pull-up definition used: hanging start, arms fully extended, feet off the floor,
  pulled "using only their upper body and without the use of the lower limbs to generate
  momentum", top = chin passes the horizontal line of the bar. Pronated grip at 1.5 ×
  bi-acromial width. Kipping cuts biceps and lat activation (d = 1.1-1.4) and multiplies
  rectus femoris / gluteus / rectus abdominis activation — i.e. hip and knee angle changes
  during the pull are the signature of a kip.
- **Prinold JAI, Bull AMJ (2016).** Scapula kinematics of pull-up techniques: avoiding
  impingement risk with training changes. *J Sci Med Sport* 19(8):629-35. PMID 26383875.
  11 regular practitioners; front, reverse and wide grips. High arm elevation reduces the
  sub-acromial space; the wide grip reaches 90° abduction with 45° external rotation and
  is the impingement-risk variant; the front (pronated, shoulder-width-ish) pull-up has the
  largest scapular protraction/retraction range (22°). Hand-force asymmetry SD < 5 % BW in
  regular practitioners (a usable "symmetric" yardstick).
- **Ronai P, Scibek E (2014).** The Pull-up. *Strength Cond J* 36(3):88-90 (paywalled; the
  abstract at digitalcommons.sacredheart.edu/pthms_fac/129). Standard NSCA technique column:
  scapular depression/retraction initiates the pull before the elbows bend, neutral neck
  (chin clears the bar by pulling, not by craning), controlled lowering to full extension.
- **Bishop C, Turner A, Read P (2018).** Effects of inter-limb asymmetries on physical and
  sports performance: a systematic review. *J Sports Sci* 36(10):1135-44. The common 10 %
  (10-15 %) asymmetry threshold; Bishop 2021 warns it is task- and metric-specific. Use
  10 % as the on-screen "flag" line, say it is a convention.
- **Youdas 2010** (in `../pullup-emg/`): elbow ROM during a pull-up 93 ± 15°.
