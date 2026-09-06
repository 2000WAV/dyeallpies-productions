# References — pull-up muscle activation (surface EMG)

Used by the pullup-video format for the "muscle heat" overlay: an EMG-informed
activation map painted on the body, scaled by the measured pull effort. It is a
literature prior placed on the body by the pose landmarks, **not** a measurement of the
person's muscles. Both abstracts were fetched from PubMed (E-utilities) on 2026-09-05.

## Youdas et al. (2010) — the %MVIC values used

Youdas, J. W., Amundson, C. L., Cicero, K. S., Hahn, J. J., Harezlak, D. T., & Hollman,
J. H. (2010). *Surface electromyographic activation patterns and elbow joint motion
during a pull-up, chin-up, or Perfect-Pullup™ rotational exercise.* Journal of Strength
and Conditioning Research, 24(12), 3404–3414. doi:10.1519/JSC.0b013e3181f1598c. PMID
21068680. File: `youdas2010-pubmed-abstract.txt`.

21 men and 4 women; double-differential surface EMG at 1 kHz, normalised to MVIC.
Average activation over the repetition (range across pull-up / chin-up / rotational):

| muscle | %MVIC | note |
|---|---|---|
| latissimus dorsi | 117–130 | highest of all; "completed" the rep together with the biceps |
| biceps brachii | 78–96 | significantly higher in the chin-up than the pull-up |
| infraspinatus | 71–79 | |
| lower trapezius | 45–56 | significantly higher in the pull-up than the chin-up |
| pectoralis major | 44–57 | significantly higher in the chin-up; "initiated" the rep with the lower trapezius |
| erector spinae | 39–41 | |
| external oblique | 31–35 | |

Elbow range of motion 93.4 ± 14.6° (pull-up), 100.6 ± 14.5° (chin-up).

## Dickie et al. (2017) — grip variants and concentric vs eccentric

Dickie, J. A., Faulkner, J. A., Barnes, M. J., & Lark, S. D. (2017). *Electromyographic
analysis of muscle activation during pull-up variations.* Journal of Electromyography
and Kinesiology, 32, 30–36. doi:10.1016/j.jelekin.2016.11.004. PMID 28011412. File:
`dickie2017-pubmed-abstract.txt`.

19 strength-trained men (24.9 ± 5 y, 81.3 ± 11.3 kg); eight shoulder-arm-forearm muscles;
supinated, pronated, neutral and rope grips. Pronated grip: middle trapezius peak
60.1 ± 22.5 %MVIC, average 48.0 ± 21.2 %MVIC (vs 37.1 / 27.4 for the neutral grip).
**The concentric phase produced significantly greater average activation of the
brachioradialis, biceps brachii and pectoralis major than the eccentric phase**
(P < 0.01). Otherwise activation was similar across grips.

## Fatigue accumulation — why the whole body warms up through the set

- Sánchez-Medina, L., & González-Badillo, J. J. (2011). *Velocity loss as an indicator of
  neuromuscular fatigue during resistance training.* Medicine & Science in Sports &
  Exercise, 43(9), 1725–1734. doi:10.1249/MSS.0b013e318213f880. PMID 21311352. File:
  `pmid21311352-abstract.txt`. Within-set velocity loss correlated with post-exercise
  lactate at r = 0.93–0.97 and with countermovement-jump loss at r = 0.91–0.97; ammonia
  rose only once the set went past about half of the possible reps. Used as the
  justification for a body-wide fatigue base that rises with the measured speed loss
  and does not recover between reps.
- Saltin, B., Gagge, A. P., & Stolwijk, J. A. (1968). *Muscle temperature during
  submaximal exercise in man.* Journal of Applied Physiology, 25(6), 679–688.
  doi:10.1152/jappl.1968.25.6.679. PMID 5727193 (abstract not on PubMed; file holds the
  citation). Background for the "steadily heats up" intuition: working muscle warms by
  roughly a degree over the first minutes of exercise. The reel's colour encodes fatigue,
  not temperature.

## Outline / matting models used for the overlay

- Lin, S., Yang, L., Saleemi, I., & Sengupta, S. (2022). *Robust High-Resolution Video
  Matting with Temporal Guidance.* WACV 2022. Code and weights: github.com/PeterL1n/
  RobustVideoMatting (loaded via `torch.hub`, `mobilenetv3` variant, `rvm_mobilenetv3.pth`
  cached in `~/.cache/torch/hub`). Gives the person alpha at full resolution with a
  recurrent state for temporal consistency.
- MediaPipe Image Segmenter, model `selfie_multiclass_256x256` (Google, float32): classes
  background / hair / body-skin / face-skin / clothes / accessories, output at the input
  resolution. `tools/models/selfie_multiclass_256x256.tflite` (gitignored, re-download
  from the `mediapipe-models/image_segmenter/selfie_multiclass_256x256/float32/latest/`
  bucket).

## How the overlay uses them (`tools/scripts/pullup_heat.py`)

Dennis pulls with a pronated grip, so the pull-up end of each Youdas range is taken.
Heat per region = %MVIC ÷ 130, then × a phase factor (pull 1.0, top hold 0.85, lower
0.65, hang 0.35, loading 0.25, standing 0.12 — the concentric > eccentric ordering is
Dickie's; the rest are the model's assumptions) × the measured pull speed. A 25 % share
of the colour comes from the image itself (local skin contrast, where the light shows
lines). Regions are drawn from the landmarks and clipped to the person mask:

| region on the body | muscle | %MVIC used | visible from the front? |
|---|---|---|---|
| outer strips of the torso, armpit → waist | latissimus dorsi | 124 | its lateral edge, yes |
| upper arm | biceps brachii | 78 | yes |
| forearm | brachioradialis | 62 (**estimate**: measured by Dickie, no number in the abstract) | yes |
| shoulder caps | infraspinatus / posterior shoulder | 75 | partly (it sits on the back) |
| neck base → shoulders | trapezius (middle/lower) | 52 | the upper part only |
| chest | pectoralis major | 44 | yes |
| lower lateral abdomen | external oblique | 33 | yes |
| back | erector spinae | 40 | **no** — not drawn |
| abdomen centre | rectus abdominis | **not measured** in either study — image contrast only | yes |

Caveats: both studies used young trained adults; values are averages across subjects;
neither measured grip/forearm flexors or the rectus abdominis; Youdas's pull-up cycle was
a controlled cadence, not a set to fatigue. The map says "where the literature says a
pull-up works", warmed by how hard this particular rep was.
