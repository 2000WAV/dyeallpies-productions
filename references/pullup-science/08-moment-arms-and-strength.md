# Elbow-flexor moment arms and upper-limb strength norms

Collected for the biomechanical pull-up model's inverse-dynamics/moment layer: the elbow
flexors' moment arms as a function of forearm rotation and elbow angle (table A), and
maximal isometric joint strength norms for the elbow, shoulder and wrist (table B). Every
number is in `data/moment-arms-and-strength-norms.csv` (columns: quantity, muscle_or_joint,
condition, value, unit, population, n, source, pmid_or_doi, measured_or_estimated, note).
Abstracts in `abstracts/*.txt`, full text where obtained in `papers/*`, full download log in
`DOWNLOADS.md`. Builds on `01-emg-and-anatomy.md` (PCSA/volume from Garner & Pandy 2003 and
Holzbaur et al.'s separate 2007 *volumes* paper) — those numbers are not repeated here.

Every number below is attributed to a study. **NOT FOUND** means a real, repeated attempt
this session (PubMed, Europe PMC, Semantic Scholar, direct publisher fetch, WebSearch for a
secondary citation) failed to recover it — it is a documented gap, not an invented value.

## Table A — elbow-flexor moment arms and forearm-rotation effects

| muscle | quantity | condition | value | source |
|---|---|---|---|---|
| brachioradialis | peak moment arm | elbow flexion, forearm **neutral**, averaged 20–120° flexion | **7.7 cm** (SD 0.7) | Murray, Buchanan & Delp 2000 |
| biceps brachii (combined) | peak moment arm | elbow flexion, forearm **neutral** | **4.7 cm** (SD 0.4) | Murray, Buchanan & Delp 2000 |
| brachialis | peak moment arm | elbow flexion, forearm **neutral** | **2.6 cm** (SD 0.3) | Murray, Buchanan & Delp 2000 |
| triceps brachii (combined) | peak moment arm | elbow extension, forearm neutral (context, not a flexor) | 2.3 cm (SD 0.3) | Murray, Buchanan & Delp 2000 |
| brachioradialis | PCSA | — | 1.2 cm² (smallest of all elbow muscles, despite the largest moment arm — the paper's central finding) | Murray, Buchanan & Delp 2000 |
| triceps brachii (combined) | PCSA | — | 14.9 cm² (largest of all elbow muscles) | Murray, Buchanan & Delp 2000 |
| biceps brachii | **pronated vs. supinated peak flexion moment-arm ratio** | elbow flexion | **NOT FOUND (numeric)** — abstract confirms direction only: "biceps flexion moment arm peaks in a more extended elbow position and has a larger peak when the forearm is supinated... the peak biceps supination moment arm decreases as the elbow is extended" | Murray, Delp & Buchanan 1995 |
| elbow flexors (load-cell force) | isometric MVC force | pronated / supinated / neutral forearm | **113.6 N / 213.6 N / 243.6 N** (11 young men) | Kohn, Smart & Jakobi 2018 |
| elbow flexors | voluntary activation | pronated / supinated / neutral | 70.9% / 93.0% / 96.1% | Kohn, Smart & Jakobi 2018 |
| elbow flexors | **the classic result, quantified**: pronated peak tension vs. supinated | rested state (electrically evoked, isolates the mechanical contribution) | **42% less** | Kohn, Smart & Jakobi 2018 |
| elbow flexors | pronated peak tension vs. supinated / neutral | potentiated state | 50% less / 53% less | Kohn, Smart & Jakobi 2018 |

**Why Murray 1995's exact ratio is missing.** The paper is real and correctly identified
(PMID 7775488, *J Biomech* 28:513–525), and a full-text PDF was found and downloaded from the
Delp lab's own site (`papers/murray1995-elbow-moment-arms-scanned.pdf`) — but it is an
Elsevier TIFF-to-PDF scan of the original 1995 print pages with **no text layer**, and this
machine has no OCR tool installed (`tesseract` not found). No secondary source (Ettema et al.
1998's own cadaver moment-arm paper, Holzbaur et al. 2005's model-validation paper, or general
web search) quotes Murray's specific cm values or a pronated:supinated ratio number either —
Ettema et al. (1998) explicitly cites Murray 1995 for the *qualitative* finding and adds their
own view that "the interaction effects are relatively small," which is itself worth noting as
a caution against overweighting the pronation/supination term in the model. **Use Kohn et
al. 2018's 42–53% strength reduction as the quantitative stand-in** for "how much weaker
pronated flexion is" — it is a force/torque measurement, not a moment-arm measurement, but it
is the closest sourced number available and matches the direction Murray reported.

## Table B — maximal isometric joint strength norms

| joint / muscle | condition | value | population | source |
|---|---|---|---|---|
| Elbow flexion | 90° elbow flexion, forearm **supinated** | **79.5 Nm** (SD 8.1), men; 31.9 Nm women; 55.7 Nm combined | 10 healthy young adults (5M/5F), non-athlete | Holzbaur, Delp, Gold & Murray 2007 |
| Elbow extension | 90° elbow flexion (test posture), forearm supinated | 60.5 Nm (SD 6.2), men; 42.8 Nm combined | same | Holzbaur et al. 2007 |
| Shoulder adduction | **60° abduction** (not overhead), elbow extended, forearm neutral | **93.7 Nm** (SD 11.3), men; **67.9 Nm combined (the largest of all 6 joint moments Holzbaur measured)** | same | Holzbaur et al. 2007 |
| Shoulder abduction | 60° abduction, elbow extended | 74.4 Nm (SD 10.8), men; 54.7 Nm combined | same | Holzbaur et al. 2007 |
| Shoulder extension | — | **NOT TESTED** — Holzbaur 2007 measured only abduction/adduction, no flexion/extension at all | — | Holzbaur et al. 2007 |
| Wrist flexion / extension | wrist neutral, forearm pronated, elbow 90° | 25.6 Nm / 14.0 Nm, men | same | Holzbaur et al. 2007 (context only) |
| Elbow & knee flexion/extension, 3D torque-angle-velocity **surface shape** | isometric + isokinetic, Biodex | surface **normalized to each subject's own peak**; shape does not differ by sex; **absolute Nm NOT recoverable** from the accessible manuscript text | 54 adults (30 men) | Frey-Law et al. 2012 |
| Shoulder moment arms at high elevation: latissimus dorsi, teres major, pectoralis major, posterior deltoid | coronal abduction + sagittal flexion, cadaver tendon-excursion, 18 sub-regions | **NOT FOUND (numeric mm)** — abstract-only; qualitative ranking below | 8 cadaver specimens | Ackland, Pak, Richardson & Pandy 2008 |
| Same ranking, independent corroboration | horizontal flexion + multi-plane elevation, cadaver | **NOT FOUND (numeric)** — qualitative only | cadaver specimens | Kuechle, Newman, Itoi, Morrey & An 1997 |
| General normative torque battery (shoulder/elbow/wrist, 18 protocols) | Biodex isokinetic + isometric | **NOT FOUND (absolute Nm in abstract)**; paywalled full text | 178 healthy adults, 15–83 yr (93M/85F) | Harbo, Brincks & Andersen 2012 |

**Ackland 2008 — what the abstract does confirm (ranking only, no numbers):**
Most effective **adductors**: teres major, middle/inferior latissimus dorsi (lumbar-vertebrae
and iliac-crest fibers), middle/inferior pectoralis major (sternal and lower-costal fibers).
Largest **extensor** moment arms: teres major and posterior deltoid. Most effective
**flexors**: superior pectoralis major (clavicular fibers), anterior/posterior supraspinatus,
anterior deltoid. Kuechle et al. 1997 independently reaches the same adductor ranking
("pectoralis major, latissimus dorsi, and teres major") by the same tendon-excursion method,
which is reasonable corroboration of the *ranking* even without either paper's numbers.

**Why Ackland's numbers are missing.** This is a fully real, correctly-identified open-access
paper (PMCID PMC2644775) but the full text could not be retrieved by any route tried this
session: the PMC XML record itself carries a publisher note refusing full-text XML download;
Europe PMC's `fullTextXML` endpoint returned empty; the PMC-hosted PDF and Wiley's own
"open" PDF link (confirmed BRONZE-license and supposedly free via Semantic Scholar's API) both
returned a Cloudflare "Just a moment..." interstitial to `curl`, and Wiley's page also 403'd a
direct fetch. This matches the pattern already logged in this repo's `DOWNLOADS.md` for other
Wiley/Cloudflare-walled papers.

## What the model should use

1. **Use Murray 2000's neutral-forearm peak moment arms as the baseline magnitudes** for
   biceps (4.7 cm), brachialis (2.6 cm) and brachioradialis (7.7 cm) — real cadaver numbers,
   directly sourced, and internally consistent with each other (same 10 specimens).
2. **Do not fabricate a pronated/supinated moment-arm multiplier from Murray 1995** — the exact
   ratio was not recoverable this session. Instead, apply **Kohn et al. 2018's 42–53% strength
   reduction pronated-vs-supinated** as a force-scaling factor when the pose tracker detects a
   pronated grip (a strict pull-up), since Dennis pulls pronated per the existing atlas notes.
3. **Use Holzbaur 2007's 79.5 Nm (men) as the elbow-flexion-at-90° strength ceiling** for a
   young, non-athlete-normed reference subject — flag it as likely an *underestimate* for a
   resistance-trained population, since no trained-population-specific elbow-flexion Nm dataset
   was found this session.
4. **Treat Holzbaur 2007's 93.7/67.9 Nm shoulder-adduction figures as a floor, not a match, for
   the pull-up's overhead pulling moment** — that test was done at only 60° abduction, well
   short of the ~90–150° elevation a pull-up actually loads; scale it up qualitatively using
   Ackland/Kuechle's *ranking* (lat dorsi + teres major + pec major dominate the adduction/
   depression moment at high elevation) even though neither gives a usable number.
5. **There is no sourced shoulder-extension MVC number anywhere in this session's search** —
   Holzbaur 2007 didn't test it, and no other open dataset was found; if the model needs a
   sagittal-plane pulling-moment number, it will have to come from a future session's search
   (candidates not yet tried: Otis et al. 1994's rotator-cuff/deltoid moment-arm paper combined
   with a PCSA-based force estimate, or a swimming/rowing-specific overhead-pull strength study).
