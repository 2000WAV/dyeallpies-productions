# Phase-resolved EMG of the strict pronated pull-up

Built for the biomechanical muscle model's heat map, which needs muscles to contract and
relax *within* a rep, not just glow at one whole-rep intensity. Five phases: (1) initiation /
scapular depression at the start of the concentric, (2) mid concentric (elbow ~90°), (3) top /
hold (chin at the bar), (4) eccentric lowering, (5) dead hang between reps (passive vs active).

**Headline finding, and its limit:** no primary source located this session (or in the prior
`01-emg-and-anatomy.md`, `02-biomechanics-and-velocity.md` sweeps) reports a true time-normalised
EMG envelope across the pull-up cycle with numbers recoverable outside a paywall. Youdas et al.
(2010) measured exactly this ("the timing of peak muscle activation was expressed as a percentage
of the complete pull-up cycle") but the actual percentages are in the paywalled JSCR tables, not
the abstract; Prinold & Bull (2016) measured scapular kinematics continuously through the pull but
did not collect EMG. What follows is therefore a mix of (a) real whole-rep %MVIC numbers, (b) real
concentric-vs-eccentric *significance/direction* findings (Dickie 2017, Doma 2013), and (c) this
session's own phase-factor model — informed by and cited to (a) and (b) — built the same way the
existing atlas's `tools/scripts/pullup_heat.py` already scales whole-rep %MVIC by a phase factor.
Every number below says which of the three it is. Full machine-readable version, including every
number in this file plus the underlying baselines and phase factors: `data/pullup-phase-emg.csv`
(columns: muscle, phase, value, unit, exercise, n, source, pmid_or_doi, measured_or_estimated, note).

## 0. Phase definitions used across the sources (they are not identical)

- **Williamson & Price (2021)** (strict/kipping/butterfly pull-up EMG, PMID none — DOI
  10.36905/jses.2021.02.08, open access): concentric phase *start* = the instant the arms are
  fully extended at the bottom of the previous rep (marker at its lowest point); eccentric phase
  *start* = the instant the athlete begins descending from the top (marker at its highest point).
  This is the cleanest explicit phase-boundary definition found and is the one this file follows
  for "initiation" (= their concentric start) and "eccentric" (= their eccentric start).
- **Prinold & Bull (2016)** (scapular kinematics, PMID 26383875, PMCID PMC4916995, open access)
  normalised the *concentric pull only* to 0-100%, with 0% = the first peak in upward vertical
  hand-reaction force and 100% = the following trough in that force — a force-based, not
  position-based, normalisation, and it only covers the pull (no eccentric, no hang).
- **Youdas et al. (2010)** (PMID 21068680, closed access, JSCR/Ovid) normalised timing to "percent
  of the complete pull-up cycle" but the paper's own definition of cycle start/end was not
  recoverable from the abstract.
- This file's own five phases (initiation, mid concentric, top/hold, eccentric, hang) are a
  coarser bucketing on top of whichever of the above a given source used; treat "mid concentric"
  and "top/hold" as this session's interpolation between sources' endpoints, not a directly
  measured third point.

## 1. Muscle activation by phase

Values marked **measured** are the source's own number; **estimated** is this session's
phase-factor model (baseline whole-rep %MVIC × a factor informed by the cited direction-finding —
see the note column in the CSV for the exact multiplication). No study measured all five phases
for any muscle, so every phase-by-phase table below necessarily blends real numbers with the
model's interpolation between them.

### Phase 1 — Initiation / scapular depression (start of concentric)

| muscle | value | measured / estimated | source |
|---|---|---|---|
| pectoralis major | 24 %MVIC (est., 0.55× the 44 %MVIC whole-rep baseline) | estimated | phase factor informed by Youdas 2010 (PMID 21068680) — PM described as initiating the rep |
| lower trapezius | 34 %MVIC (est., 0.60× 56) | estimated | phase factor informed by Youdas 2010 — lower trapezius described as initiating the rep |
| middle/upper trapezius, serratus anterior | 55% of whole-rep proxy value | estimated | scapular-stabilizer group assumed to co-activate with lower trapezius at initiation |
| latissimus dorsi | 43 %MVIC (est., 0.35× 124) | estimated | still ramping — Youdas's "completed with LD/BB" language implies LD is NOT peak here |
| biceps brachii | 23 %MVIC (est., 0.30× 78) | estimated | same reasoning as latissimus dorsi |
| infraspinatus, deltoid | ~0.4-0.45× whole-rep value | estimated | stabilizing the glenohumeral joint as load comes on, not yet at end-range |
| forearm flexors (grip) | 33 %MVIC (est., 0.60× 55 ESTIMATE baseline) | estimated (baseline itself is also an estimate — no pull-up-specific grip %MVIC source exists) | grip must already be near-committed the instant load comes on the bar |
| rectus abdominis, external oblique, erector spinae, hip flexors, legs | 0.15-0.25× their (mostly estimated) whole-rep baselines | estimated | postural-only in a strict rep; see §3 for why these should stay flat |

**What actually has a citation here:** Youdas et al. (2010) discussion language — pull-ups and
chin-ups were "**initiated by the lower trapezius and pectoralis major** and **completed with
biceps brachii and latissimus dorsi recruitment**" (PMID 21068680, quoted directly from the
abstract). Ronai & Scibek's 2014 NSCA technique column (*Strength & Cond J* 36(3):88-90, paywalled,
citation only) gives the same claim as a coaching cue: scapular depression/retraction initiates
the pull before the elbows bend. **Neither source gives a millisecond- or %-cycle-scale onset
time** — this is a described sequence, not an EMG-onset time series. No study located this session
timed scapular depression against elbow-flexion onset with numbers.

### Phase 2 — Mid concentric (elbow ~90°)

| muscle | value | measured / estimated | source |
|---|---|---|---|
| latissimus dorsi | 93 %MVIC (est., 0.75× 124) | estimated | building toward peak |
| biceps brachii | 55 %MVIC (est., 0.70× 78) | estimated | building toward peak |
| lower trapezius | 50 %MVIC (est., 0.90× 56) | estimated | near its own peak already (scapular work front-loaded) |
| pectoralis major | 24 %MVIC (est., 0.55× 44, flat from initiation) | estimated | PM's role is initiation, not mid-pull, so its factor does not rise further |
| infraspinatus, deltoid | ~0.80× whole-rep value | estimated | approaching end-range stabilization demand |

**What actually has a citation here:** Di Fonza et al. (2026, *J Funct Morphol Kinesiol* 11(3):315,
PMID 42647355, PMCID PMC13510307, CC BY, full text fetched this session) is a 2026 narrative review
that had access to Youdas's full paper and paraphrases its timing result directly: "**scapular
muscles were recruited predominantly in the initial phase, with biceps brachii and latissimus
dorsi EMG amplitude increasing progressively toward the terminal concentric phase**" (Section 3.6,
citing Youdas et al. 2010). This is a secondary paraphrase of a primary finding this session could
not reach directly (JSCR/Ovid paywall) — treat it as one step removed from the primary source, not
as a re-derivation.

### Phase 3 — Top / hold (chin at the bar)

| muscle | value | measured / estimated | source |
|---|---|---|---|
| latissimus dorsi | 124 %MVIC (est., 1.00× whole-rep baseline — i.e. the whole-rep peak lands here) | estimated (baseline is measured, placement at this phase is the model's choice) | Youdas 2010 "completed with ... latissimus dorsi recruitment"; Park & Yoo 2013 (isometric lat pull-down, PMID 24064179) — LD/lower-trapezius ratio falls as shoulder elevation rises, i.e. near the top the mix should shift slightly toward trapezius |
| biceps brachii | 78 %MVIC (est., 1.00×) | estimated (baseline measured) | same reasoning — "completed with biceps brachii" |
| lower trapezius | 56 %MVIC (est., 1.00×) | estimated (baseline measured) | Park & Yoo 2013: lower-trapezius share of the LD/LT pair *increases* with shoulder elevation — the top of the rep is the highest-elevation point of the cycle |
| infraspinatus, deltoid | 1.00× whole-rep baseline | estimated | greatest external-rotation/end-range stabilization demand of the rep |
| pectoralis major | 26 %MVIC (est., 0.60× 44 — falling off its initiation-phase level) | estimated | PM's role (per Youdas) was to help initiate; nothing in the literature suggests it re-peaks at the top |

**Caveat carried over unchanged from `01-emg-and-anatomy.md`:** Park & Yoo (2013) is an
**isometric lat pull-down at fixed shoulder angles (60°/90°/120°)**, not a dynamic pull-up — it is
the only source with a quantitative, angle-dependent LD-vs-lower-trapezius trade-off, but its
angles are a proxy for "how close to the top", not a pull-up-cycle measurement. No exact %MVIC
numbers were recoverable from its abstract either, only direction and significance.

### Phase 4 — Eccentric lowering

| muscle | value | measured / estimated | source |
|---|---|---|---|
| biceps brachii | 43 %MVIC (est., 0.55× 78) | estimated, but the **direction is measured**: concentric significantly > eccentric, P<0.01 | Dickie et al. 2017, PMID 28011412 |
| brachioradialis | 34 %MVIC (est., 0.55× 62 ESTIMATE baseline) | estimated, direction measured (same P<0.01 finding) | Dickie et al. 2017 |
| pectoralis major | 24 %MVIC (est., 0.55× 44) | estimated, direction measured (same P<0.01 finding) | Dickie et al. 2017 |
| latissimus dorsi | 105 %MVIC (est., 0.85× 124 — kept relatively high, NOT dropped like BB/brachioradialis/PM) | estimated | Doma 2013 (PMID 24245055): in the chin-up, LD > triceps AND LD > rectus abdominis during the eccentric phase (P<0.05) — LD stays a dominant muscle eccentrically, unlike PM/BB/brachioradialis which Dickie shows dropping; Williamson & Price 2021 (DOI 10.36905/jses.2021.02.08) independently found strict-pull-up eccentric LD EMGpeak greater than the kipping and butterfly variants' eccentric LD, consistent with LD staying loaded through the lowering phase specifically in the strict form |
| triceps | 7 %MVIC (est., 0.35× 20 ESTIMATE baseline — bumped up slightly from other phases) | estimated | Doma 2013 measured triceps present (below BB/LD ordinally) in the eccentric phase specifically, consistent with an antagonist/elbow-control role during controlled lowering; no %MVIC number given |
| lower trapezius | 39 %MVIC (est., 0.70× 56) | estimated | Ronai & Scibek 2014's coaching cue ("controlled lowering to full extension") implies continued scapular control, not a sudden drop-off |

**What actually has a citation here:** Dickie et al. (2017) is the single strongest phase-specific
finding in the entire pull-up EMG literature: "**the concentric phases of each pull-up variation
resulted in significantly greater EMGarv of the brachioradialis, biceps brachii, and pectoralis
major in comparison to the eccentric phases (P<0.01)**" (quoted from the abstract, PMID 28011412).
This is a **measured direction with a real statistic**, the only one of its kind found across two
research sessions. It does **not** come with the actual %MVIC numbers for each phase — those are
in the paywalled *J Electromyogr Kinesiol* tables (ScienceDirect, no PMC copy, no open mirror
found). Doma et al. (2013, PMID 24245055) is the second-strongest: its abstract gives explicit
within-phase orderings for the **chin-up** (supinated grip, so a caveat on direct transfer to
pronated pull-ups) — concentric: BB, LD and erector spinae each > pectoralis major (P<0.05);
eccentric: BB and LD each > triceps, and LD > rectus abdominis (P<0.05). Both are ordinal findings,
not %MVIC values (see `data/pullup-phase-emg.csv` rows with phase `concentric_rank_chinup` /
`eccentric_rank_chinup` for the machine-readable form, rank 1 = highest, ordinal per the abstract's
explicit comparisons only — muscles not compared to each other in the abstract are not ranked
against each other, only against the muscle(s) actually named).

### Phase 5 — Dead hang between reps: passive vs active

| muscle | passive hang | active hang | measured / estimated |
|---|---|---|---|
| forearm flexors (grip) | 22 %MVIC (est., 0.40× 55 ESTIMATE baseline) | 22 %MVIC (est., same 0.40×) | estimated — grip cannot go fully passive while bodyweight hangs from the hand; see caveat below |
| latissimus dorsi | 6 %MVIC (est., 0.05× 124) | 37 %MVIC (est., 0.30× 124) | estimated, direction **not** confirmed by any primary EMG source (see caveat below) |
| lower trapezius | 3 %MVIC (est., 0.05× 56) | 20 %MVIC (est., 0.35× 56) | estimated, same caveat |
| serratus anterior | 1 %MVIC (est., 0.05× 25.52 proxy) | 8 %MVIC (est., 0.30× 25.52 proxy) | estimated, same caveat |
| everything else (biceps, PM, infraspinatus, deltoid, core, hip, legs) | ≤0.10× whole-rep baseline | ≤0.15× whole-rep baseline | estimated |

**This phase has the weakest evidentiary floor in the whole file — say so on screen if the model
visualises a hang.** No EMG study of a bar dead hang (passive or "active"/scapular-engaged) was
found by this session or the prior `01-emg-and-anatomy.md` sweep. What exists instead:

- **Edwards et al. (2017)**, a systematic review of EMG in *normal, uninjured shoulders* used to
  guide rotator-cuff-repair rehab (*J Orthop Sports Phys Ther* 47(12):931-944, PMID 28704624,
  closed access, abstract fetched this session): the review's own classification scheme buckets
  pooled mean %MVIC as low (0-15%), low-to-moderate (16-20%), moderate (21-40%), high (41-60%),
  very high (>60%). This is **not a pull-up or dead-hang measurement** — it is a general
  shoulder-rehab EMG literature summary — but it is a legitimate, citable anchor for "what does a
  genuinely low/passive shoulder-muscle EMG signal look like on this scale", which is why the
  passive-hang column above targets the low end of that range (≤10% for most muscles) rather than
  an invented near-zero.
- **Ferrer-Uris et al. (2023)** (rock-climbing maximal isometric finger dead-hangs, PeerJ,
  PMID 37304875, PMC10249616, CC BY, already archived) and **Dykes et al. (2019)** (static crimp
  hang, PMID 30721754, closed access, already archived): both confirm forearm flexors (FDS, FCR)
  stay substantially active through a sustained dead hang, but report raw RMS (mV) or %RVC
  (relative to a reference hang), **not %MVIC** — not numerically substitutable into this table,
  only directional support for "grip does not go to zero, even in a passive-looking hang."
- **The "active hang recruits 30-50% more lower trapezius/serratus anterior than a passive hang"
  claim** (surfaced via WebSearch from fitness-content sites, no primary study behind it) is
  **explicitly flagged here as unverified and not used as a number** — the active-hang column
  above is this session's own estimate of *plausible* magnitude and direction (an active hang is,
  by definition, a voluntary scapular-depression contraction, so it must be > passive), not a
  citation to that 30-50% figure. Do not repeat "30-50%" as if it were sourced.
- **Tucker et al. (2011)** supine-pull-up scapular-stabilizer numbers (upper trapezius 61.57%,
  middle trapezius 62.89%, lower trapezius 60.47%, serratus anterior 25.52% MVIC, PMID 21814139)
  are for an **active pulling exercise**, not a hang, and are not used in this table — they inform
  the whole-rep baselines in §1 Phases 1-4 instead (see `data/pullup-phase-emg.csv`).

## 2. Eccentric/concentric ratio per muscle

| muscle | ratio (eccentric ÷ concentric) | basis |
|---|---|---|
| brachioradialis | **measured direction:** eccentric < concentric, P<0.01. Magnitude not recoverable — abstract only. This session's phase-factor model implies ≈0.55 (see §1 Phase 4). | Dickie et al. 2017, PMID 28011412 |
| biceps brachii | Same as brachioradialis: **measured direction**, magnitude estimated ≈0.55 by this session's model. Doma 2013 (chin-up) independently shows BB still ranks above triceps eccentrically — the *ratio* drops but BB does not become a minor player. | Dickie et al. 2017; Doma et al. 2013 (PMID 24245055) |
| pectoralis major | **Measured direction** (Dickie 2017), same ≈0.55 model estimate. Consistent with PM's role being front-loaded at initiation (§1 Phase 1), not a prime mover at any later phase. | Dickie et al. 2017 |
| latissimus dorsi | **Not measured as a ratio anywhere.** This session's model keeps LD closest to 1.0 of any prime mover (≈0.85) because two independent sources show LD staying dominant eccentrically specifically (Doma 2013: LD>triceps and LD>rectus abdominis eccentrically; Williamson & Price 2021: strict-pull-up eccentric LD EMGpeak > kipping/butterfly variants' eccentric LD) — i.e. LD is the one prime mover the literature does *not* show falling off eccentrically the way BB/brachioradialis/PM do. | Doma et al. 2013; Williamson & Price 2021 |
| triceps | No ratio measurable; Doma 2013 shows triceps present but below BB/LD in the eccentric phase specifically (an antagonist/elbow-control role), with no equivalent concentric-phase mention — this session's model gives triceps a *higher* factor eccentrically than concentrically (0.35 vs 0.20-0.25), the only muscle in this file estimated to go the opposite direction from the brachioradialis/BB/PM pattern. | Doma et al. 2013 |
| trapezius (all three), serratus anterior, deltoid, infraspinatus | No ratio measured by any source. This session's model keeps these at 0.55-0.70 of their peak eccentrically (a moderate, not severe, drop) on the reasoning that scapular/rotator-cuff stabilization is still required to control the descent (Ronai & Scibek 2014 coaching-cue level only). | none primary — estimate only |
| rectus abdominis, external oblique, erector spinae, hip flexors, legs | No ratio measured for a **strict** rep. Doma 2013 shows rectus abdominis is *higher* in a seated, hip-fixed lat pull-down's eccentric phase than in a free-hanging chin-up's — a caution against assuming any of these core/leg muscles simply track pull effort. | Doma et al. 2013; Dinunzio et al. 2018 (kip-specific, not a ratio) |

**No study located gives a single clean "eccentric is X% of concentric" number for any pull-up
muscle.** The closest the literature comes is Dickie's significance test (three muscles, direction
only) and Doma's ordinal comparisons (chin-up, four muscle-pairs, ranks only). Every numeric ratio
implied above is this session's model, built to be consistent with those two measured directions
and flagged as such in `data/pullup-phase-emg.csv`.

## 3. What the model should do

- **Peak early (initiation):** pectoralis major, lower/middle/upper trapezius, serratus anterior.
  Grip (forearm flexors) also commits early and stays high throughout — it does not have a
  meaningful "off" phase within a rep, only between reps.
- **Build through the pull, peak late (terminal concentric / top-hold):** latissimus dorsi, biceps
  brachii, brachialis, brachioradialis (assumed to co-vary with biceps — no separate source),
  infraspinatus, posterior/middle deltoid. This is the best-attested pattern in the file — Youdas
  2010's own language ("initiated by ... completed by ...") plus the 2026 narrative review's
  paraphrase of the same finding.
- **Drop off sharply on the lower (eccentric), but not to zero:** biceps brachii, brachioradialis,
  pectoralis major — this is the one *measured* concentric-vs-eccentric direction in the whole
  literature (Dickie 2017, P<0.01). Latissimus dorsi should be the exception: keep it high through
  the eccentric phase rather than dropping it with the other prime movers (Doma 2013, Williamson &
  Price 2021). Triceps should nudge *up* slightly on the eccentric relative to its (low) concentric
  level — an antagonist/elbow-control bump, not a prime-mover contraction.
- **Stay flat and low all rep, regardless of phase, in a strict rep:** rectus abdominis, external
  oblique, hip flexors, legs. The literature's one large core-activation swing (Dinunzio 2018:
  +28.7 %MVIC-points rectus abdominis, +21.8 external oblique, +26.1 iliopsoas, all P≤0.001) is
  driven entirely by **kipping hip/knee motion**, not by pull effort or by phase within a strict
  rep — if the pose tracker ever detects hip swing, that is the trigger to boost this group, not
  pull speed or phase. Erector spinae is measured only as a whole-rep average (39-41 %MVIC, Youdas
  2010) with no phase-specific finding located; keep it comparatively flat across phases pending
  better data.
- **Relax hardest at the dead hang, but never to true zero for the grip:** every prime mover and
  scapular muscle should visibly cool at the hang. Forearm flexors are the one region that should
  stay visibly "warm" even in what looks like a passive hang, because the hand is still bearing
  full bodyweight isometrically. If the model or the pose tracker can distinguish a passive
  ("dead") hang from a deliberately scapula-engaged ("active") hang between reps, the active hang
  should show a modest re-ignition of latissimus dorsi, lower trapezius and serratus anterior
  relative to the passive hang — but say on screen that this specific distinction is this session's
  estimate, not a cited EMG measurement (see §1 Phase 5 caveat).
- **Do not claim millisecond-level onset timing.** The "scapular depression, then lats, then
  biceps" sequence is real and citable (Youdas 2010's discussion language, corroborated by a 2026
  secondary review), but it is a *descriptive* sequence from the paper's discussion section, not an
  EMG-onset-latency time series. If the heat map ever implies e.g. "trapezius fires 80ms before
  biceps," that specific number would be invented — no source in two collection sessions supports
  a number that granular.

## 4. Sources fetched this session

New primary/secondary sources fetched and used above (full citations; PMID/DOI as available):

- Williamson T, Price P (2021). A comparison of muscle activity between strict, kipping and
  butterfly pull-ups. *J Sport Exerc Sci* 5(2):149-155. doi:10.36905/jses.2021.02.08. Open access
  (St Mary's University repository). No PMID (not PubMed-indexed). Full PDF fetched and
  text-extracted; concentric/eccentric phase definitions and the SPU-normalised EMGpeak figures
  for biceps brachii, latissimus dorsi, infraspinatus, rectus femoris, gluteus maximus and rectus
  abdominis used in §0 and §2.
- Di Fonza D, Di Claudio G, Colantuono G, Persichini L, Cerulo N, Sangregorio B, Buonsenso A,
  Fiorilli G, Calcagno G, di Cagno A (2026). Electromyographic Analysis of Latissimus Dorsi
  Activation During Common Resistance Training Exercises: A Narrative Review. *J Funct Morphol
  Kinesiol* 11(3):315. doi:10.3390/jfmk11030315. PMID 42647355. PMCID PMC13510307. CC BY (MDPI).
  Full text XML fetched via NCBI eutils (db=pmc); Section 3.6 ("Pull-Ups") paraphrase of Youdas
  2010's timing finding used throughout §1.
- Edwards PK, Ebert JR, Littlewood C, Ackland T, Wang A (2017). A Systematic Review of
  Electromyography Studies in Normal Shoulders to Inform Postoperative Rehabilitation Following
  Rotator Cuff Repair. *J Orthop Sports Phys Ther* 47(12):931-944. doi:10.2519/jospt.2017.7271.
  PMID 28704624. Closed access (paper), abstract fetched via PubMed E-utilities. Used only for its
  low/moderate/high %MVIC bucket definitions as a general anchor for the passive-hang phase.
- Prinold JAI, Bull AMJ (2016). Scapula kinematics of pull-up techniques: avoiding impingement risk
  with training changes. *J Sci Med Sport* 19(8):629-35. doi:10.1016/j.jsams.2015.08.002.
  PMID 26383875. PMCID PMC4916995. Open access. Abstract fetched via PubMed E-utilities this
  session (was cited but not archived in `../pullup-thermal/README.md` from an earlier session);
  full text fetched via NCBI eutils (db=pmc) for the phase-normalisation method in §0 and the
  scapulothoracic protraction/retraction range numbers (front 22°, wide 10°, reverse 17°;
  posterior/anterior tilt ≈35° average across techniques; lateral/medial rotation ≈10° average) —
  these are scapular-kinematics numbers, not EMG, and are not repeated in the muscle tables above,
  only in this citation and in `data/pullup-phase-emg.csv` for completeness.
- Doma K, Deakin GB, Ness KF (2013). Kinematic and electromyographic comparisons between chin-ups
  and lat-pull down exercises. *Sports Biomech* 12(3):302-313. doi:10.1080/14763141.2012.760204.
  PMID 24245055. Closed access. Abstract already archived from an earlier session
  (`abstracts/doma2013-pmid24245055.txt`) — re-read in full this session; its concentric/eccentric
  ordinal muscle rankings (not previously extracted into a usable table) are the basis of §1
  Phases 3-4 and §2's latissimus dorsi and triceps rows.
- Youdas JW, Amundson CL, Cicero KS, Hahn JJ, Harezlak DT, Hollman JH (2010). Surface
  electromyographic activation patterns and elbow joint motion during a pull-up, chin-up, or
  Perfect-Pullup™ rotational exercise. *J Strength Cond Res* 24(12):3404-3414.
  doi:10.1519/JSC.0b013e3181f1598c. PMID 21068680. Closed access; abstract already archived
  (`abstracts/youdas2010-pubmed-abstract.txt` under `../pullup-emg/`) — re-read in full this
  session specifically for its discussion-section sequencing language, which was not previously
  quoted verbatim in this repo's files.
- Dickie JA, Faulkner JA, Barnes MJ, Lark SD (2017). Electromyographic analysis of muscle
  activation during pull-up variations. *J Electromyogr Kinesiol* 32:30-36.
  doi:10.1016/j.jelekin.2016.11.004. PMID 28011412. Closed access; abstract already archived
  (`../pullup-emg/dickie2017-pubmed-abstract.txt`) — re-read this session specifically for its
  concentric-vs-eccentric significance statement, which is the single strongest phase-specific
  claim in this file.
- Tucker WS, Bruenger AJ, Doster CM, Hoffmeyer DR (2011); Snarr RL, Hallmark AV, Casey JC, Esco MR
  (2017); Dinunzio C, Porter N, Van Scoy J, Cordice D, McCulloch RS (2018); Ferrer-Uris B, Arias D,
  Torrado P, Marina M, Busquets A (2023); Dykes B, Johnson J, San Juan JG (2019) — all already
  fully cited in `01-emg-and-anatomy.md` §5; re-used here for phase/hang-relevant numbers already
  quoted above, not re-fetched.

**Not found this session** (searched via PubMed E-utilities, Europe PMC, Semantic Scholar Graph
API, Google Scholar-style WebSearch, and direct WebFetch of ResearchGate/ScienceDirect/Tandfonline
abstract pages, all of which either 403'd or returned no abstract): the actual %MVIC-by-phase
tables inside Youdas 2010 or Dickie 2017 (both paywalled, no PMC/OA mirror, no legal full-text
route found); any primary EMG study of a bar dead hang, passive or active/scapular-engaged; any
millisecond- or %-cycle-scale EMG onset-latency sequencing study for the pull-up; any pull-up- or
chin-up-specific %MVIC number for brachialis, teres major, middle deltoid, rhomboids, or the
forearm flexors as a group (grip). Two secondary-thesis PDFs that WebSearch surfaced as possibly
quoting Youdas's phase tables (University of Wisconsin-La Crosse and a Swedish diva-portal
bachelor's thesis) both timed out on download (curl, 40s, `-A "Mozilla/5.0"`) and were not
retried given the marginal likelihood of new primary numbers.
