# Muscle activation and muscle anatomy of the pull-up / chin-up

Literature sweep for the biomechanics-annotated Reel's per-muscle "heat" map. Builds on
`../pullup-emg/README.md` (Youdas 2010, Dickie 2017, Sánchez-Medina 2011) and
`../pullup-thermal/README.md` (Holzbaur 2007, Prinold & Bull 2016, Williamson & Price 2021,
Ronai & Scibek 2014) — those numbers are not repeated in full here, only cross-referenced.
Raw data extracted into `data/emg-mvic-by-study.csv` and `data/anatomy-pcsa-volume.csv`
(source column on every row). Abstracts in `abstracts/*.txt`, full text where it could be
fetched in `papers/`, full download log in `DOWNLOADS.md`.

Every number below is attributed to a study. Anything not found in a primary source is marked
**ESTIMATE** or **NOT FOUND** — none of those are invented.

## 1. Master table — %MVIC per muscle per study per grip variant

Full detail (n, population, normalisation, phase, notes) is in `data/emg-mvic-by-study.csv`.
Condensed here; "—" means the study reported only a direction/rank, not a number recoverable
from the abstract.

| study | exercise | grip | muscle | value | phase |
|---|---|---|---|---|---|
| Youdas 2010 (n=25) | pull-up/chin-up | pronated/supinated | latissimus dorsi | 117–130 %MVIC | whole rep |
| Youdas 2010 | ″ | ″ | biceps brachii | 78–96 %MVIC | whole rep |
| Youdas 2010 | ″ | ″ | infraspinatus | 71–79 %MVIC | whole rep |
| Youdas 2010 | ″ | ″ | lower trapezius | 45–56 %MVIC | whole rep |
| Youdas 2010 | ″ | ″ | pectoralis major | 44–57 %MVIC | whole rep |
| Youdas 2010 | ″ | ″ | erector spinae | 39–41 %MVIC | whole rep |
| Youdas 2010 | ″ | ″ | external oblique | 31–35 %MVIC | whole rep |
| Dickie 2017 (n=19) | pull-up | pronated | middle trapezius | 60.1±22.5 peak / 48.0±21.2 avg %MVIC | whole rep |
| Dickie 2017 | pull-up | neutral | middle trapezius | 37.1 peak / 27.4 avg %MVIC | whole rep |
| Dickie 2017 | pull-up | any | brachioradialis, biceps brachii, pectoralis major | concentric > eccentric, P<0.01 | conc vs ecc |
| **Snarr 2017 (n=15)** | traditional pull-up | pronated 1.5×biacromial | latissimus dorsi | 79.82±21.95 %MVC | whole rep |
| Snarr 2017 | ″ | ″ | biceps brachii | 43.93±13.94 %MVC | whole rep |
| Snarr 2017 | ″ | ″ | middle trapezius | 60.52±18.06 %MVC | whole rep |
| Snarr 2017 | ″ | ″ | posterior deltoid | 106.09±69.64 %MVC | whole rep |
| Snarr 2017 | suspension-device pull-up | ″ | LD/BB/MT/PD | 83.76 / 45.80 / 55.21 / 102.48 | whole rep |
| Snarr 2017 | towel pull-up | ″ | LD/BB/MT/PD | 85.34 / 41.42 / **51.00 (sig. lower MT)** / 100.94 | whole rep |
| **Tucker 2011 (n=30)** | supine pull-up | — | upper trapezius | 61.57±29.67 %MVIC | whole rep |
| Tucker 2011 | ″ | — | middle trapezius | 62.89±24.17 %MVIC | whole rep |
| Tucker 2011 | ″ | — | lower trapezius | 60.47±34.80 %MVIC | whole rep |
| Tucker 2011 | ″ | — | serratus anterior | 25.52±19.80 %MVIC (lowest of 3 exercises tested) | whole rep |
| **Dinunzio 2018 (n=11)** | kipping vs strict pull-up | pronated | rectus abdominis | +28.7±4.7 %MVIC in kip, P<0.001 | whole rep |
| Dinunzio 2018 | ″ | ″ | external oblique | +21.8±4.1 %MVIC in kip, P<0.001 | whole rep |
| Dinunzio 2018 | ″ | ″ | iliopsoas | +26.1±5.5 %MVIC in kip, P=0.001 | whole rep |
| Dinunzio 2018 | ″ | ″ | tensor fasciae latae | +13.5±2.3 %MVIC in kip, P<0.001 | whole rep |
| Dinunzio 2018 | ″ | ″ | biceps brachii | **−26.7±0.6 %MVIC in kip**, P=0.006 | whole rep |
| Andersen 2014 (n=15) | lat pull-down | narrow/med/wide (1×/1.5×/2× biacromial) | LD, trapezius, infraspinatus | no sig. diff whole-rep; wide>narrow eccentric (P≤0.04) | conc+ecc |
| Andersen 2014 | ″ | medium vs narrow | biceps brachii | medium greater, concentric only, P=0.03 | concentric |
| Sperandei 2009 (n=24) | lat pull-down (BNL/FNL/V-bar) | — | pectoralis major, posterior deltoid, biceps brachii | ordinal only, see CSV | both phases |
| Lusk 2010 (n=12) | lat pull-down | pronated vs supinated | latissimus dorsi | pronated > supinated, P<0.05, no number in abstract | both phases |
| Signorile 2002 (n=10) | lat pull-down (CG/SG/WGA/WGP) | wide-anterior best | latissimus dorsi, triceps long head | WGA highest, ordinal only | both phases |
| Doma 2013 (n unstated) | chin-up vs lat pull-down | pronated | biceps brachii, erector spinae | chin-up > lat pull-down, concentric, P<0.05 | concentric |
| Doma 2013 | ″ | ″ | rectus abdominis | lat pull-down > chin-up, eccentric, P<0.05 | eccentric |
| Park & Yoo 2013 (n=14) | isometric pull-down, 60/90/120° elevation | — | latissimus dorsi | activity + LD/LT ratio ↓ as elevation ↑ | isometric |
| Park & Yoo 2013 | ″ | ″ | lower trapezius | activity ↑ as elevation ↑ | isometric |
| Urbanczyk 2020 (n=11) | pull-up, modelled forces (not EMG) | wide/front/reverse | LD (wide↑), biceps+brachialis (front↑), rotator cuff (reverse↑) | P<.01–.02, modelled not %MVIC | whole rep |
| Williamson & Price 2021 | strict vs kipping vs butterfly | pronated | biceps brachii, latissimus dorsi | kipping reduces both, Cohen's d 1.1–1.4 | whole rep |
| **Ferrer-Uris 2023 (n=25 climbers)** | max dead-hang (not pull-up) | CRIMP/SLOPE/SLOPER | FDS | 610.64±236.73 / 520.87±228.28 / 675.56±231.44 mV RMS (**raw, not %MVIC**) | isometric |
| Ferrer-Uris 2023 | ″ | ″ | FCR | 189.77±70.04 / 179.43±79 / 292.6±130.81 mV RMS | isometric |
| Dykes 2019 (n=10) | static crimp hang | crimp, no tape | FDS / FDP | 102.4±59.1 / 96.6±40.0 **%RVC** (relative to a non-crimp hang, not MVIC) | isometric |
| Walker 2023 (n=10) | bar vs ring muscle-up | pull phase | upper trapezius, biceps brachii, forearm flexors | ring > bar, P=0.007/0.001/0.001, no numbers recoverable | pull phase |

**No band-assisted pull-up EMG study was found.** PubMed, Europe PMC and web search turned up
zero primary EMG studies of elastic-band-assisted pull-ups; the closest analogues are the
Redcord-sling (unstable suspension) study (De Mey 2014, n=47 — decreased serratus anterior,
increased pectoralis major with instability, no assistance/bodyweight-offload condition) and the
general finding that reducing pull-up difficulty (suspension device, towel) barely changes
latissimus dorsi/biceps/posterior deltoid activation (Snarr 2017) while changing scapular-muscle
demand more (middle trapezius lower on towel grip). Treat band-assisted %MVIC values used
anywhere in the pipeline as **ESTIMATE** extrapolated from these, not measured directly.

## 2. Firing order / phase — what actually has numbers behind it

- **Concentric > eccentric** for brachioradialis, biceps brachii and pectoralis major, P<0.01
  (Dickie 2017, n=19, pull-up). This is the only phase-ordering claim in the existing prior with
  a real statistic; it is already encoded in the heat model's phase factors.
- **Youdas 2010** describes pectoralis major and lower trapezius as the muscles that
  "**initiated**" the rep and latissimus dorsi + biceps brachii as the ones that "**completed**"
  it — language from the paper's discussion, not a measured onset-latency number. Treat "scapular
  depression first, then lats, then biceps" as the paper's qualitative account, not an EMG-onset
  time-series.
- **Park & Yoo 2013** (isometric pull-down, not a dynamic pull-up) is the only study located that
  gives a *quantitative, angle-dependent trade-off*: latissimus dorsi activity and the
  LD/lower-trapezius ratio **decrease** as shoulder elevation goes from 60°→90°→120°, while lower
  trapezius activity **increases** over the same range — i.e., near the top of a pull-up (higher
  elevation) the lower trapezius should be weighted up and the lat weighted down relative to the
  bottom of the rep, if the heat map wants an elevation-dependent lat/trap split. No exact %MVIC
  numbers were recoverable from the abstract, only the direction and significance.
- **Exel 2026** (n=11 climbers, dead hang to failure, not pull-up) found that fatigue increases
  intermuscular EMG coherence between brachioradialis–biceps and trapezius–biceps (β-band, P=0.04
  both) while trapezius–brachioradialis coherence in a different frequency band (γ) *decreases*
  (P=0.01) — a proximal-muscle synchronisation signature under fatigue. This supports the general
  "whole body warms up together as fatigue accumulates" assumption already in the heat model, but
  it is about coordination/coherence, not amplitude, and it is a hang, not a pull.
- **No study located gives a millisecond-scale onset-latency ("which muscle fires first")
  sequence for the pull-up.** The "scapular depression → lats → biceps" sequence used anywhere in
  the pipeline should be marked **ESTIMATE**, sourced only to Youdas's descriptive language and to
  the general NSCA technique column (Ronai & Scibek 2014, already in `../pullup-thermal/README.md`)
  which says scapular depression/retraction initiates the pull before the elbows bend — again
  descriptive coaching cue, not EMG-timed.
- **Core muscles are markedly phase- and technique-dependent, not just present.** Doma 2013 found
  rectus abdominis *higher in the lat pull-down than the chin-up* during the eccentric phase —
  i.e. a seated, hip-fixed exercise can demand more RA than a free-hanging one — a caution against
  assuming core demand scales simply with "how hard the pull is." Dinunzio 2018's kipping-vs-strict
  contrast (rectus abdominis +28.7%MVIC, external oblique +21.8%MVIC, both P<0.001, in the kip) is
  the largest, best-attested core-activation swing in this literature, and it is driven by hip/knee
  motion, not pull effort — a reason to keep core heat keyed to detected hip motion/kip, not to
  pull speed, if the pose tracker can see the hip.

## 3. Anatomy table per muscle

Full table with every source's numbers side by side is in `data/anatomy-pcsa-volume.csv`
(includes both Holzbaur 2007's MRI volumes, already in `../pullup-thermal/README.md`, and this
session's Garner & Pandy 2003 VHM-model values, which the paper's own text flags as running
**larger** than cadaver-dissection literature — treat the "Model" column as an upper bound, not
ground truth). Origin/insertion and fibre direction are anatomical-textbook knowledge, not
resolvable to a single PMID; PCSA/fibre-length/volume are cited to source.

| muscle | origin → insertion (words) | surface fibre direction (angle to body long axis) | PCSA (cm²) | optimal fibre length (cm) | volume/mass | source |
|---|---|---|---|---|---|---|
| latissimus dorsi | spinous processes T7–L5, thoracolumbar fascia, iliac crest, lower 3–4 ribs, inferior scapula angle → intertubercular groove of humerus | ~30–45° upward-lateral to downward-medial fan; the surface (lateral) fibres run roughly diagonal, steeper (~45°) near the axilla, flattening toward vertical near the iliac origin | 22.04 (Garner&Pandy, lit. compiled from Veeger/An) – 461.89 (Garner&Pandy VHM model, flagged high) | 39.27 (VHM model) | 262±147 cm³/side (Holzbaur, n=10) or 676.4 cm³ (VHM model, single male, flagged as overestimate) | Holzbaur 2007; Garner & Pandy 2003 |
| teres major | inferior angle/lateral border of scapula → medial lip of intertubercular groove | ~horizontal to slightly upward-lateral, roughly 10–20° | 514.57 (VHM model — anomalously high relative to the muscle's small size, flagged) | 5.72 | 33±16 cm³/side (Holzbaur); 38.70 cm³ (VHM model) | Holzbaur 2007; Garner & Pandy 2003 |
| biceps brachii | short head: coracoid process; long head: supraglenoid tubercle → radial tuberosity, bicipital aponeurosis | vertical, 0° to the humeral long axis | 849.29 (VHM model) | 8.77 (VHM model); 8.70 (Amis 1979, cited inside Garner&Pandy's Table 3) | 144±69 cm³/side (Holzbaur); 619.99 cm³ (VHM model) | Holzbaur 2007; Garner & Pandy 2003 |
| brachialis | anterior distal humerus → ulnar tuberosity/coronoid process | vertical, 0°, deep to biceps — only its distal-lateral edge is visible from the front | 853.76 (VHM model) | 14.22 | 144±64 cm³/side (Holzbaur); 365.84 cm³ (VHM model) | Holzbaur 2007; Garner & Pandy 2003 |
| brachioradialis | lateral supracondylar ridge of humerus → styloid process of radius | vertical, 0°, slight lateral rake at the wrist end | 101.56 (VHM model) | 10.28 | 65±36 cm³/side (Holzbaur); 265.96 cm³ (VHM model) | Holzbaur 2007; Garner & Pandy 2003 |
| forearm flexors — FDS | medial epicondyle, radius, ulna → middle phalanges II–V | vertical, 0° | not modelled separately in Garner&Pandy's abstracted tables | — | 74±27 cm³/side (Holzbaur) | Holzbaur 2007 |
| forearm flexors — FDP | proximal ulna, interosseous membrane → distal phalanges II–V | vertical, 0° | — | — | 92±39 cm³/side (Holzbaur) | Holzbaur 2007 |
| FCR | medial epicondyle → base of 2nd/3rd metacarpals | vertical, 0°, radial side of forearm | 368.63 (VHM model) | 4.48 | 35 cm³/side (Holzbaur); 80.41 cm³ (VHM model) | Holzbaur 2007; Garner & Pandy 2003 |
| FCU | medial epicondyle, olecranon → pisiform, hamate, 5th metacarpal | vertical, 0°, ulnar side of forearm | 561.00 (VHM model) | 5.10 | 37 cm³/side (Holzbaur); 56.97 cm³ (VHM model) | Holzbaur 2007; Garner & Pandy 2003 |
| infraspinatus | infraspinous fossa of scapula → greater tubercle of humerus | fan, roughly 30–60° converging toward the humerus; **on the back**, not visible from the front | 1100.13 (VHM model) or 9.95 (An 1981, cited inside Garner&Pandy) | 4.28 | 119±47 cm³/side (Holzbaur); 89.23 cm³ (VHM model) | Holzbaur 2007; Garner & Pandy 2003 |
| posterior/middle deltoid | scapular spine (posterior), acromion (middle) → deltoid tuberosity | posterior fibres ~45° downward-lateral to the tuberosity; middle fibres near-vertical, 0–10° | 2044.65 (VHM model, whole deltoid, not split by head) | 12.80 (whole deltoid) | 380±158 cm³/side whole deltoid (Holzbaur); 549.69 cm³ (VHM model) | Holzbaur 2007; Garner & Pandy 2003 |
| trapezius (upper/middle/lower) | external occipital protuberance, nuchal ligament, spinous processes C7–T12 → clavicle, acromion, scapular spine | upper: ~45° down-lateral neck→shoulder; middle: ~0°/horizontal; lower: ~45° up-lateral toward the scapula | 802.25 (VHM model, whole muscle only in this source) | 18.84 (whole muscle) | **not in Holzbaur; ESTIMATE ~250 cm³/side (48% lower/28% middle/23% upper), already flagged in `../pullup-thermal/README.md`**; VHM model whole-muscle volume 457.89 cm³ | Garner & Pandy 2003 (no split by region in the tables recovered); Holzbaur silent |
| rhomboids (major+minor) | spinous processes C7–T5 → medial scapular border | ~45° down-lateral, superior-medial to inferior-lateral | major 217.12, minor 221.45 (VHM model) | major 17.90, minor 17.55 | major 117.77 cm³, minor 71.92 cm³ (VHM model; no MRI/cadaver comparator was found for these two individually) | Garner & Pandy 2003 |
| pectoralis major | clavicle, sternum, costal cartilages 1–6 → lateral lip of intertubercular groove | fan: clavicular head ~30–45° down-lateral, sternocostal head near-horizontal to slightly upward-lateral converging on the humerus | 1175.01 (VHM model) | 19.00 | 290±169 cm³/side (Holzbaur); 73.14 cm³ (VHM model — this figure looks like a partial/mismatched entry relative to Holzbaur, flagged **ESTIMATE**, do not average the two) | Holzbaur 2007; Garner & Pandy 2003 |
| serratus anterior | outer surfaces of ribs 1–8/9 → costal (anterior) surface of the medial scapular border | ~45–60° up-and-back from the ribs toward the scapula, visible as diagonal "fingers" over the lateral ribcage | 677.30 (VHM model) | 17.47 | 358.56 cm³ (VHM model); not in Holzbaur | Garner & Pandy 2003 |
| external oblique | outer surfaces of ribs 5–12 → linea alba, iliac crest, inguinal ligament | ~45° down-and-medial ("hands in pockets" direction) | **NOT FOUND** in any primary anatomy source located this session | **NOT FOUND** | **NOT FOUND** | none — Youdas/Dickie measured its EMG, no anatomy paper covering PCSA/volume for trunk-wall muscles was found |
| rectus abdominis | pubic crest/symphysis → costal cartilages 5–7, xiphoid process | vertical, 0°, segmented by tendinous inscriptions | **NOT FOUND** | **NOT FOUND** | **NOT FOUND** | none |
| erector spinae | sacrum, iliac crest, spinous processes → ribs, transverse/spinous processes, skull (composite of iliocostalis/longissimus/spinalis) | vertical, 0°, either side of the spinous processes | **NOT FOUND** | **NOT FOUND** | **NOT FOUND** | none — on the back, would not be drawn on a front-view map regardless |

Klein Breteler et al. 1999 (16 shoulder muscles, 104 muscle elements, laser-diffraction sarcomere
measurement on a single embalmed male) and Langenderfer et al. 2004 (musculoskeletal parameters
for muscles crossing the shoulder and elbow, cadaver, 120 sarcomere samples/muscle) are exactly
the kind of dataset the brief asked for, but both are paywalled (Clinical Biomechanics/Elsevier,
J Biomech/Elsevier) and their actual per-muscle numbers are reported "in tabular format," not in
the abstract — so no specific PCSA/fibre-length value from either could be extracted without
circumventing a paywall. They are cited for completeness and as a pointer to where those numbers
live, not as a numeric source in the table above. Ward et al. 2009 (CORR, 27 muscles, 21 cadaver
lower extremities) is real, high-quality architecture data but is **lower-limb only** — it has no
overlap with any pull-up muscle and is not used for a single number here; it is listed only
because a companion Ward/Lieber/Delp lower-limb model paper (Arnold et al. 2010) is sometimes
confused with an upper-limb dataset.

## 4. Visible from the front, arms overhead — with reasoning

| muscle | visible from front? | reasoning |
|---|---|---|
| latissimus dorsi | **partly** — lateral edge only | wraps from the back around the torso; with arms overhead its anterior/lateral border shows as the "side stripe" from armpit to waist, which is what the current atlas already draws |
| teres major | **partly** | small, deep to the lat's edge at the armpit; only a sliver at the axilla is visible, easily lost in the lat's stripe |
| biceps brachii | **yes** | fully anterior, its whole belly is on the front of the arm |
| brachialis | **partly** | deep to biceps; only its distal-lateral edge peeks out just above the elbow crease |
| brachioradialis | **yes** | anterolateral forearm, clearly visible especially with elbow flexed as in the top of a pull-up |
| FDS/FDP/FCR/FCU (forearm flexors) | **yes**, as a mass | the flexor mass is the visible anterior forearm bulk; the four muscles are not individually distinguishable on skin without deep dissection or very lean, vascular subjects — draw as one "forearm flexor" region, not four |
| infraspinatus | **no** | entirely posterior, on the scapula; not visible from the front under any arm position. (Note: the current atlas's README already flags this as "partly, it sits on the back" for the pull-up context — with arms fully overhead a sliver may become visible above the shoulder cap from a 3/4 angle, but not from a strict front view) |
| posterior deltoid | **no**, middle deltoid **yes** | posterior fibres wrap to the back of the shoulder; the middle (lateral) deltoid cap is visible from the front and is what should carry the deltoid heat on a front-view map |
| trapezius — upper | **yes** | visible at the neck-to-shoulder line from the front |
| trapezius — middle/lower | **no** | both sit on the back between/below the scapulae; not visible from a front view at any arm position |
| rhomboids | **no** | deep to trapezius, entirely posterior |
| pectoralis major | **yes** | fully anterior chest |
| serratus anterior | **yes**, partially | its lower "finger" slips are visible on the lateral ribcage between pec major and lat dorsi, especially arms overhead when the ribcage rotates/elevates — a muscle the current atlas is missing entirely (see §6) |
| external oblique | **yes** | anterolateral abdomen |
| rectus abdominis | **yes** | anterior abdomen, midline |
| erector spinae | **no** | entirely posterior, alongside the spine |

## 5. Full citations

Newly collected this session (PMID / DOI, abstract file in `abstracts/`, full text in `papers/`
where available):

- Andersen V, Fimland MS, Wiik E, Skoglund A, Saeterbakken AH (2014). Effects of grip width on
  muscle strength and activation in the lat pull-down. *J Strength Cond Res* 28(4):1135-42.
  doi:10.1097/JSC.0000000000000232. PMID 24662157.
- Sperandei S, Barros MA, Silveira-Júnior PC, Oliveira CG (2009). Electromyographic analysis of
  three different types of lat pull-down. *J Strength Cond Res* 23(7):2033-8.
  doi:10.1519/JSC.0b013e3181b8d30a. PMID 19855327.
- Dinunzio C, Porter N, Van Scoy J, Cordice D, McCulloch RS (2019 [Epub 2018]). Alterations in
  kinematics and muscle activation patterns with the addition of a kipping action during a
  pull-up activity. *Sports Biomech* 18(6):622-635. doi:10.1080/14763141.2018.1452971.
  PMID 29768093.
- Tucker WS, Bruenger AJ, Doster CM, Hoffmeyer DR (2011). Scapular muscle activity in overhead
  and nonoverhead athletes during closed chain exercises. *Clin J Sport Med* 21(5):405-10.
  doi:10.1097/JSM.0b013e31822179e8. PMID 21814139.
- De Mey K, Danneels L, Cagnie B, Borms D, T'Jonck Z, Van Damme E, Cools AM (2014). Shoulder
  muscle activation levels during four closed kinetic chain exercises with and without Redcord
  slings. *J Strength Cond Res* 28(6):1626-35. doi:10.1519/JSC.0000000000000292. PMID 24172720.
- Karabay D, Emük Y, Özer Kaya D (2019). Muscle activity ratios of scapular stabilizers during
  closed kinetic chain exercises in healthy shoulders: a systematic review. *J Sport Rehabil*
  29(7):1001-1018. doi:10.1123/jsr.2018-0449. PMID 31860828.
- Walker CW, Bruenger AJ, Tucker WS, Lee HR (2023). Comparison of muscle activity during a ring
  muscle up and a bar muscle up. *Int J Exerc Sci* 16(1):1451-1460. doi:10.70252/FJQL7859.
  PMID 38288256. PMCID PMC10824315 (CC BY-ND).
- Urbanczyk CA, Prinold JAI, Reilly P, Bull AMJ (2020). Avoiding high-risk rotator cuff loading:
  muscle force during three pull-up techniques. *Scand J Med Sci Sports* 30(11):2205-2214.
  doi:10.1111/sms.13780. PMID 32715526.
- Lusk SJ, Hale BD, Russell DM (2010). Grip width and forearm orientation effects on muscle
  activity during the lat pull-down. *J Strength Cond Res* 24(7):1895-1900.
  doi:10.1519/JSC.0b013e3181ddb0ab. PMID 20543740.
- Signorile JF, Zink AJ, Szwed SP (2002). A comparative electromyographical investigation of
  muscle utilization patterns using various hand positions during the lat pull-down. *J Strength
  Cond Res* 16(4):539-46. PMID 12423182.
- Doma K, Deakin GB, Ness KF (2013). Kinematic and electromyographic comparisons between chin-ups
  and lat-pull down exercises. *Sports Biomech* 12(3):302-313. doi:10.1080/14763141.2012.760204.
  PMID 24245055.
- Park SY, Yoo WG (2013). Selective activation of the latissimus dorsi and the inferior fibers of
  trapezius at various shoulder angles during isometric pull-down exertion. *J Electromyogr
  Kinesiol* 23(6):1350-5. doi:10.1016/j.jelekin.2013.08.006. PMID 24064179.
- Ferrer-Uris B, Arias D, Torrado P, Marina M, Busquets A (2023). Exploring forearm muscle
  coordination and training applications of various grip positions during maximal isometric
  finger dead-hangs in rock climbers. *PeerJ* 11:e15464. doi:10.7717/peerj.15464. PMID 37304875.
  PMCID PMC10249616 (CC BY).
- Exel J, Kaufmann P, Froschauer O, Baca A, Kainz H, Mochizuki L (2026). Upper-body neuromechanical
  coordination strategies during fatiguing sustained dead hangs in climbers. *Eur J Sport Sci*
  26(6):e70197. doi:10.1002/ejsc.70197. PMID 42168114. PMCID PMC13240036 (CC BY).
- Dykes B, Johnson J, San Juan JG (2019). Effects of finger taping on forearm muscle activation
  in rock climbers. *J Electromyogr Kinesiol* 45:11-17. doi:10.1016/j.jelekin.2019.01.004.
  PMID 30721754.
- Snarr RL, Hallmark AV, Casey JC, Esco MR (2017). Electromyographical comparison of a
  traditional, suspension device, and towel pull-up. *J Hum Kinet* 58:5-13.
  doi:10.1515/hukin-2017-0068. PMID 28828073. PMCID PMC5548150 (CC BY).
- Garner BA, Pandy MG (2003). Estimation of musculotendon properties in the human upper limb.
  *Ann Biomed Eng* 31(2):207-20. doi:10.1114/1.1540105. PMID 12627828. Full text: author's
  faculty-page PDF (Baylor University), `papers/garnerpandy2003-musculotendon-upperlimb.pdf`.
- Garner BA, Pandy MG (1999/2001). A kinematic model of the upper limb based on the Visible Human
  Project (VHP) image dataset. *Comput Methods Biomech Biomed Engin* 2(2):107-124.
  doi:10.1080/10255849908907981. PMID 11264821. (Companion kinematic paper; not used for numbers.)
- Klein Breteler MD, Spoor CW, Van der Helm FC (1999). Measuring muscle and joint geometry
  parameters of a shoulder for modeling purposes. *J Biomech* 32(11):1191-7.
  doi:10.1016/s0021-9290(99)00122-0. PMID 10541069. (Abstract only; tables not accessible.)
- Langenderfer J, Jerabek SA, Thangamani VB, Kuhn JE, Hughes RE (2004). Musculoskeletal
  parameters of muscles crossing the shoulder and elbow and the effect of sarcomere length sample
  size on estimation of optimal muscle length. *Clin Biomech* 19(7):664-70.
  doi:10.1016/j.clinbiomech.2004.04.009. PMID 15288451. (Abstract only; tables not accessible.)
- Ward SR, Eng CM, Smallwood LH, Lieber RL (2009). Are current measurements of lower extremity
  muscle architecture accurate? *Clin Orthop Relat Res* 467(4):1074-82.
  doi:10.1007/s11999-008-0594-8. PMID 18972175. PMCID PMC2650051. (Lower-limb only; context/
  methodology citation, no pull-up-muscle numbers used from it.)
- Ishibashi RF (2026). Brachiation-based movement as a theoretical framework for addressing
  technology-related postural dysfunction: an evolutionary and neuromuscular perspective. *J
  Bodyw Mov Ther* 47:252-259. doi:10.1016/j.jbmt.2026.03.008. PMID 42264802. **Theoretical/
  narrative paper, not a primary EMG study** — its lower-trapezius "45-56% MVIC" figure is a
  re-citation of Youdas 2010 (already in the prior), and its "subscapularis 37% MVIC,
  infraspinatus 28% MVIC in perturbation studies" figures are unsourced in the abstract (no
  citation given for which perturbation study). Do not treat those two numbers as usable —
  flagged **ESTIMATE / unverifiable** and not carried into the CSV or the tables above.

Already on file from the earlier collection pass — see `../pullup-emg/README.md` and
`../pullup-thermal/README.md` for full citations: Youdas et al. 2010 (PMID 21068680), Dickie et
al. 2017 (PMID 28011412), Sánchez-Medina & González-Badillo 2011 (PMID 21311352), Holzbaur et al.
2007, Prinold & Bull 2016 (PMID 26383875), Williamson & Price 2021, Ronai & Scibek 2014.

## 6. How to use in the pipeline

**Grip-width refinement.** Dennis pulls pronated, roughly shoulder-width-plus. The best-matched
direct evidence is now Snarr 2017 at a 1.5×biacromial pronated grip (close to Dennis's grip) —
LD 79.82–85.34 %MVC, BB 41.42–45.80, MT 51.00–60.52, PD 100.94–106.09 across three pull-up
variants, all in the same range Youdas reported. **Recommendation: keep the Youdas pull-up-end
values as the primary prior (they remain the largest, most cited dataset and the two agree in
shape), but note in the report that Snarr's independent sample at almost the same grip width
corroborates the same ordering** (LD highest, then MT/PD-adjacent shoulder muscles, then BB) —
this is useful as a footnote/confidence statement, not a replacement number. The grip-width
literature as a whole (Andersen 2014, Lusk 2010, Signorile 2002) converges on: **grip width
matters far less than assumed for lat activation on a straight bar** (Andersen: no significant
whole-rep difference narrow/medium/wide) but **pronation vs supination matters a lot** (Lusk:
pronated > supinated for LD, P<0.05) — since Dennis already pulls pronated, no correction to the
current grip-width handling is needed; the literature actively argues against adding a grip-width
term to the model.

**Elevation-dependent lat/trap split.** Park & Yoo 2013 gives a legitimate, quantitative reason to
*shift weight from lat to lower-trapezius as the rep approaches the top* (higher shoulder
elevation → lower LD/LT ratio). The current heat model's phase factors (pull 1.0, top hold 0.85,
lower 0.65...) apply the same lat-vs-trap ratio at every phase; **a small refinement worth making:
multiply the lower-trapezius share up and the lat share down slightly during the "top hold" phase
relative to "pull," which the current model does not encode** (it only scales overall intensity by
phase, not the muscle mix within a phase).

**Core muscles.** The atlas currently draws external oblique from Youdas (31–35 %MVIC, strict
pull-up) and has no rectus abdominis number at all ("image contrast only", per the existing
README). Two new data points refine this: Doma 2013 shows rectus abdominis is *not* simply "low
because it's not the prime mover" — it's phase- and exercise-dependent, higher on the eccentric
of a fixed-hip lat pull-down than a free chin-up. Dinunzio 2018's kip-vs-strict contrast is the
single biggest core number found (+28.7 %MVIC RA, +21.8 %MVIC EO in a kip) — **if the pose
tracker ever detects hip swing / kipping, that is the trigger to substantially boost core heat,
not pull speed.** For a strict pull-up (Dennis's style, per the technique standard already in
`../pullup-thermal/README.md`), rectus abdominis heat should stay conservative — still
**ESTIMATE**, since no primary source gives a number for RA in a *strict* pull-up specifically.

**Forearm / grip muscles.** Still no pull-up-specific forearm flexor %MVIC exists (the atlas's
"brachioradialis 62, ESTIMATE" stands as the best guess). The new dead-hang literature
(Ferrer-Uris 2023, Dykes 2019, Exel 2026) is all rock-climbing dead-hangs, not pull-ups, and
mostly reports raw RMS (mV) or %RVC (relative to a reference hang), **not %MVIC** — these numbers
are not directly substitutable into a %MVIC-based heat model without a normalisation step the
source studies didn't do. What they do support qualitatively: forearm flexor demand is grip- and
fatigue-dependent (SLOPER > CRIMP > SLOPE for FDS/FCR; brachioradialis-biceps coherence rises
under fatigue) — consistent with, but not a numeric upgrade to, the current forearm ESTIMATE.

**Muscles the atlas is missing entirely:**

1. **Serratus anterior** — visible from the front (lower slips on the lateral ribcage), has real
   numbers now (Tucker 2011: 25.52±19.80 %MVIC in a supine pull-up, lowest of three exercises
   tested; Karabay 2019 review flags "half supine pull-up with slings" as an ideal exercise for
   its ratio to upper trapezius) but is not drawn anywhere in the current region list. Worth
   adding as a small region between pec major and the lat stripe.
2. **Upper trapezius specifically** — the atlas has "trapezius (middle/lower)" only; Tucker 2011
   gives upper trapezius its own number (61.57±29.67 %MVIC) and it is visible from the front at
   the neck-shoulder line, unlike middle/lower trapezius which are posterior. This is a
   visible-from-front region the atlas currently omits by lumping all trapezius under one
   "back-of-shoulder, not fully visible" treatment.
3. **Middle deltoid** — the atlas has "shoulder caps... infraspinatus/posterior shoulder,
   partly (it sits on the back)" but middle deltoid (distinct from posterior deltoid) is fully
   anterior/lateral and visible; no source found gives it a pull-up-specific %MVIC (Signorile
   2002 and Sperandei 2009 both measured *posterior* deltoid on the lat pull-down, not middle
   deltoid on a pull-up) — flag as a region to add with an **ESTIMATE** value, not a sourced one.
4. **Teres major** — small but real, sits at the visible edge of the axilla; Holzbaur gives its
   volume (33±16 cm³) but no EMG study located measured it separately from latissimus dorsi in
   any pull-up or lat pull-down variant; keep it folded into the lat stripe as the atlas already
   does, but know that is a simplification, not a measurement.
