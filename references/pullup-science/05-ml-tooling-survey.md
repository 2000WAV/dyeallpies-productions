# ML tooling survey for the pull-up video pipeline (2026-09-08)

Scope: what could replace or augment the current stack (MediaPipe Pose Landmarker heavy +
YOLOv8m-pose + RVM mobilenetv3 + MediaPipe selfie_multiclass, all CPU, `.venv-pushup`,
torch 2.13 CPU, mediapipe 0.10.35, ultralytics 8.4, Python 3.13, Windows 11, RTX 2060 6 GB)
on this machine. Method: WebSearch + WebFetch against GitHub READMEs/LICENSE files and
Hugging Face model cards, this session (2026-09-08); PyPI JSON not separately queried where
a GitHub/HF source already gave the same answer. Nothing was installed. Where a claim below
could not be pinned to a primary source this session it is marked **unverified** or
**estimated** rather than stated as fact — do not treat those lines as licence-cleared.

Licence key: **OK** = permissive/commercial-safe (MIT, BSD, Apache-2.0). **NC** = non-commercial
only (CC BY-NC, custom research licences) — cannot be used for a video posted publicly with
monetisation/brand intent without a separate commercial licence. **Mixed** = permissive code,
restricted weights/data, or split by model size.

## 1. 2D whole-body / body pose (replacing/augmenting MediaPipe 33-pt + YOLOv8m-pose 17-pt)

| Tool | What it gives | Licence | Install (Windows pip) | Speed at ~1080p | Verdict |
|---|---|---|---|---|---|
| **RTMPose / RTMW / RTMO** via `rtmlib` | 17/26/133-kpt (RTMW = COCO-WholeBody, includes jawline + hands + feet), no mmcv/mmdet/mmpose build needed | **OK** — mmpose/mmengine are Apache-2.0; `rtmlib` itself Apache-2.0-style (Tau-J/rtmlib) | `pip install rtmlib onnxruntime` (CPU) or add `onnxruntime-gpu` for CUDA; pure-Python + ONNX, confirmed to run on Windows | Published numbers are on COCO's 256x192/384x288 person crops, not full 1080p frames: RTMPose-m ~90+ fps CPU (i7-11700), ~430+ fps on a GTX 1660 Ti; RTMW-x (133-kpt) ~130+ fps GPU on crops. On this RTX 2060, with one person filling most of a 1080x1920 frame, **estimate 25-45 fps** end-to-end (detector + pose net + Python overhead) — not directly benchmarked this session | **Best near-term upgrade.** Drop-in via `rtmlib`, no C++ build, Apache-licensed, and RTMW's 133 COCO-WholeBody points include the jawline — solves the "no chin point when the face is visible" gap directly. Still need YOLO-style occlusion witness logic; RTMPose keypoint *scores* (not MediaPipe's `visibility`) reportedly track occlusion more honestly (same distillation lineage as DWPose, see below) but this was not independently re-verified against the lintel-occlusion case this session. |
| **ViTPose / ViTPose++** (HF `transformers`) | ViT-B/L/H backbones, top accuracy on COCO, ViTPose++ adds MoE for multi-domain | **OK** — HF `transformers` integration (contributed 2025-01-08) is Apache-2.0; original ViTAE-Transformer weights also released under Apache-2.0 on the ViTPose repo | `pip install transformers torch` (already have torch); `AutoModel.from_pretrained("usyd-community/vitpose-*")` | ViT-H is heavy: expect single-digit fps on a 6 GB GPU for the large checkpoints, faster (~15-30 fps, estimated) for ViT-B. Not benchmarked this session at 1080p. | Good accuracy ceiling, easy HF install, but slower than RTMPose for the same GPU budget and only 17-kpt COCO (no wholebody variant found this session with the same ease-of-install) — use as a still-frame accuracy cross-check, not the per-frame tracker. |
| **YOLO11-pose** | 17-kpt COCO, newer YOLO backbone | **AGPL-3.0** (or paid Enterprise licence from Ultralytics) — same licence family already governing YOLOv8m-pose in the current pipeline | `pip install ultralytics` (already in venv) | Marginally faster/more accurate than YOLOv8-pose at equal size class per Ultralytics' own comparisons; no independent 1080p GPU number found this session | Trivial upgrade path (same `ultralytics` package, same AGPL situation as today) — swap `yolov8m-pose.pt` for `yolo11m-pose.pt`/`yolo11x-pose.pt` as a witness-tracker refresh, not a new licence conversation since the repo already ships under AGPL terms for this role. |
| **YOLOv8x-pose** | Largest YOLOv8-pose checkpoint | AGPL-3.0 (same as above) | Already installable via existing `ultralytics==8.4` | Larger/slower than the m-checkpoint already in use; no confirmed fps number at 1080p this session | Marginal accuracy gain for a real speed cost; lower priority than the RTMW switch. |
| **Sapiens-pose** (308 kpt: body+hands+feet+face) | Richest keypoint set of anything surveyed — 243 of the 308 points are facial, useful for a very literal chin point | **NC — CC BY-NC 4.0** (confirmed from the actual `facebookresearch/sapiens` `LICENSE` file this session; note this supersedes an earlier-seen "CC BY-NC-SA" claim from a secondary source — the primary LICENSE file says NonCommercial only, no ShareAlike clause) | `pip install` from source per `facebookresearch/sapiens`; no simple pip wheel found | 0.3B model is the fast end of the family; still a full ViT backbone — expect single-digit-to-teens fps on a 6 GB card for anything above the smallest checkpoint (estimated, not benchmarked) | **Cannot be used** — Instagram Reels posted publicly is exactly the kind of use CC BY-NC forbids without a separate agreement. Keep on the "if Meta ever relicenses" watchlist only. |
| **DWPose** | 133-kpt COCO-WholeBody, two-stage distillation, popular as the ControlNet pose input | **OK** — the `onnx` branch's LICENSE resolves to Apache License 2.0 (fetched directly from `IDEA-Research/DWPose` this session) | Available inside `rtmlib` (`Wholebody` solution) or standalone via the DWPose repo; ONNX weights on HF | Distilled to be fast — comparable to or faster than RTMPose-m at similar accuracy per the paper's own claims; not independently re-benchmarked at 1080p this session | Same practical path as RTMW (both are exposed through `rtmlib`) — either DWPose or RTMW gets you COCO-WholeBody's jawline/chin points under a clean licence; try both and keep whichever's face keypoints are more stable when the head goes behind the lintel. |

**On honest low-confidence under occlusion:** none of RTMPose/RTMW/DWPose/ViTPose's occlusion
behaviour with the head fully hidden behind a bar/lintel was independently re-tested this
session (no video was processed — this is a literature/licence survey only). The RTMPose
family reports a per-keypoint confidence score (like YOLO, unlike MediaPipe's binary-ish
`visibility`); whether that score actually collapses to ~0.1-0.2 the way YOLOv8's does when the
head is hidden — the behaviour the current pipeline relies on for the chin-witness rule — is
an assumption carried over from the shared COCO-style training signal, not a verified fact.
**Test this on a real clip before trusting it over the existing YOLOv8 witness.**

## 2. Monocular 3D pose / body mesh

| Tool | What it gives | Needs SMPL? | Licence | Verdict |
|---|---|---|---|---|
| **4D-Humans / HMR2.0** | SMPL body mesh + tracking across frames, transformer-based | Yes — SMPL model files (registration required) | Code: **MIT** (confirmed, `shubham-goel/4D-Humans/LICENSE.md`). Body model: **NC** (SMPL's own licence: non-commercial research/education/art only, per `smpl.is.tue.mpg.de/modellicense.html`) | Code is open but the mesh it outputs is legally unusable in a monetised public post without a commercial SMPL licence (Meshcapade). **Not clear for this project as-is.** |
| **WHAM** (world-grounded, accurate 3D motion) | Global trajectory + SMPL pose from video, handles camera motion | Yes — SMPL registration | Repo licence not independently confirmed this session (README describes the SMPL registration requirement clearly; no separate code-licence file was fetched) — assume **NC** by inheritance from SMPL until checked | Same SMPL-licence blocker as 4D-Humans. |
| **TRAM** | Global trajectory + SMPL motion from in-the-wild video (glocal reconstruction) | Yes — SMPL | Code: **MIT** (confirmed, `yufu-wang/tram/LICENSE`). Model output still needs SMPL (**NC**) | Same pattern: permissive code wrapped around a non-commercial body model — the *output* (the mesh) is what would appear in the Reel, and that's the NC part. |
| **TokenHMR** | Tokenized-pose HMR, CVPR 2024 | Yes — SMPL/SMPL-H | **NC** — the repo's own LICENSE is a Max-Planck "non-commercial scientific research, education, or artistic projects" licence (fetched directly this session), separate from and in addition to SMPL's own NC terms | Double-NC. Clearly out. |
| **SMPLer-X** | Expressive (body+hands+face) SMPL-X estimation, scaled-up training | Yes — SMPL-X | Code: **S-Lab License 1.0** (fetched from `SMPLCap/SMPLer-X/LICENSE`) — non-commercial, "contact contributors" for commercial use | Out for the same reason as the others, and the code licence itself is separately NC on top of SMPL-X. |
| **GVHMR** | World-grounded HMR via gravity-view coordinates, SIGGRAPH Asia 2024 | Yes — SMPL | Custom licence in `zju3dv/GVHMR/LICENSE`: "educational, research and non-profit purposes only," commercial use requires emailing the authors (confirmed this session) | Out. |
| **NLF (Neural Localizer Fields, Sárándi 2024)** | Continuous neural field — query any 3D point on the body without committing to SMPL topology; **does not require the SMPL model to run** (SMPL fitting is an optional post-process) | No (for its native output) — SMPL is opt-in | Models released for **noncommercial research use** (`isarandi/nlf` releases page) — so even though it sidesteps the SMPL licence problem specifically, the model weights themselves carry their own NC restriction | The one architecture here that is *not* SMPL-shaped by construction, which is architecturally interesting (fixes the "warped 33/133-point polygon" muscle-atlas problem for good, in principle) — but the released weights are still NC, so it is not usable today either. Worth re-checking if NLF ever ships an OK-licensed checkpoint. |

**Bottom line for section 2:** every monocular 3D mesh method surveyed is blocked for a
publicly-posted, non-research video, either through SMPL/SMPL-X's own non-commercial model
licence (4D-Humans, WHAM, TRAM, TokenHMR, SMPLer-X, GVHMR all sit on top of it) or through the
method's own weights being NC regardless of SMPL (Sapiens-pose, NLF). **None of these are a
green light this year.** The current MediaPipe-33-world-landmarks approach, despite its known
20-degree elbow-angle disagreement with the image plane, remains the only commercially-clear
3D-ish signal in this whole category — which is exactly why the skill already downgrades to
"report both, claim neither" when MediaPipe 3D and the 2D image plane disagree.

## 3. Per-pixel body-part parsing / dense correspondence

| Tool | What it gives | Licence | Windows/GPU reality | UV coords? | Verdict |
|---|---|---|---|---|---|
| **DensePose** (Detectron2) | Dense body-surface correspondence (UV per pixel, 24 body parts in the SMPL UV atlas) | Detectron2 itself: Apache-2.0 (code); DensePose model weights follow the same. | Detectron2 has **no official Windows support** — community forks exist (`DGMaxime/detectron2-windows`) but need a matching CUDA Toolkit + MSVC build environment; pre-built wheels only track specific CUDA+torch pairs (e.g. CUDA 11.8 + torch 2.0.1), not the CUDA 12.x + torch-2.13 combo this repo would want. **Realistic assessment: a real build headache on this machine, not a pip install.** | **Yes — this is the one method here that gives true UV coordinates**, meaning a muscle atlas could be authored once in UV space and warped by the correspondence map instead of by landmark polygons. | Technically the most correct fix for "muscle regions are warped polygons," but the Windows build tax is real. Worth a timeboxed spike only if the RTMPose/atlas approach hits a wall; don't block the next video on it. |
| **Sapiens body-part segmentation** (28 classes: torso/upper-arm/lower-arm/etc., incl. clothing/hair/teeth/tongue) | Per-pixel semantic classes, much finer than MediaPipe's 6-class multiclass segmenter | **NC — CC BY-NC 4.0** (same LICENSE file as Sapiens-pose, confirmed) | HF weights (`facebook/sapiens-seg-0.3b` etc.), ViT backbone, GPU-hungry | No (semantic classes, not continuous UV) | Would be an excellent skin/hair/clothes replacement for the current MediaPipe multiclass segmenter's flicker problem — but it's NC, same as Sapiens-pose. Blocked. |
| **SCHP (Self-Correction Human Parsing)** | LIP 20-class parsing (incl. upper-arm, lower-arm, torso-skin as separate classes) | **MIT** (confirmed, `PeikeLi/Self-Correction-Human-Parsing`) | Plain PyTorch, CPU or GPU, no exotic build | No | **Commercially clear and finer-grained than the current MediaPipe multiclass classes** — a real, low-friction upgrade candidate for the skin/hair/clothes gating logic that currently has to work around segmenter flicker near the head. |
| **Graphonomy** | Universal human parsing via graph transfer | **Apache-2.0** (confirmed, `Gaoyiminggithub/Graphonomy/LICENSE`) | PyTorch, older codebase (2019), may need dependency pinning | No | Also clear and finer-grained than MediaPipe's classes, but SCHP is the more actively maintained/mirrored of the two — prefer SCHP. |
| **CDGNet** | CVPR 2022 class-distribution-guided human parsing, SOTA-ish LIP accuracy at the time | **Unconfirmed** — no LICENSE file found in `tjpulkl/CDGNet` and the README doesn't state one | PyTorch | No | Don't use without a licence — an unlicensed public repo is legally "all rights reserved" by default; skip unless the authors clarify. |
| **FASHN Human Parser** (new, Jan 2026) | SegFormer-B4 fine-tune, 18 fashion/body classes (face, hair, arms, hands, tops, pants, dresses, accessories) | **NC — inherits the NVIDIA Source Code License-NC** from the SegFormer base model (confirmed: NVIDIA's SegFormer LICENSE restricts use to "non-commercial research or evaluation," binding on downstream users, not just NVIDIA) | `pip install fashn-human-parser`, easy | No | Newest and easiest to install of this group, but blocked by inheritance — flag this clearly since "open-sourced in 2026" reads as permissive but the base-model licence isn't. |

**Verdict for section 3:** **SCHP is the actionable upgrade** — MIT-licensed, finer body-part
classes than MediaPipe's multiclass segmenter, no exotic Windows build. DensePose is the
"someday, if there's a spare afternoon for the Detectron2 Windows build" option because it is
the only one offering true UV space. Everything else in this section is either NC (Sapiens,
FASHN) or unlicensed (CDGNet).

## 4. Video matting (replacing/augmenting RVM mobilenetv3 @ 0.8-2 fps CPU)

| Tool | What it gives | Licence | Speed | Verdict |
|---|---|---|---|---|
| **MatAnyone (CVPR 2025)** | Stable video matting with consistent memory propagation — designed exactly for the "hold a clean alpha across many frames of one subject" problem this pipeline has | **NC — NTU S-Lab License 1.0** (confirmed via search of the official `pq-yang/MatAnyone` repo's stated licence) | Not independently benchmarked this session; positioned as a quality-over-raw-speed method | Looks like the best *quality* answer to RVM's flicker/half-fps problems, but it's non-commercial — blocked for a posted Reel without contacting NTU S-Lab. |
| **BiRefNet / BiRefNet-matting** | High-resolution dichotomous segmentation + a matting-tuned checkpoint; trimap-free | **MIT** (confirmed, `ZhengPeng7/BiRefNet/LICENSE`) | ~17 fps at 1024x1024 on an RTX 4090 (vendor-reported); a 6 GB RTX 2060 will be meaningfully slower and 1080x1920 is a bigger frame than the benchmark's square crop — **estimate single-digit fps**, not verified this session | **The one clearly-licensed, modern option here.** MIT, actively maintained, has a matting-specific checkpoint. Worth a real bake-off against RVM: likely much better edge quality per frame even if not dramatically faster; batching/half-precision may close the speed gap on the 2060. |
| **ViTMatte** | Transformer trimap-guided matting, strong boundary detail | **MIT** (confirmed, `hustvl/ViTMatte/LICENSE`) — note the *training data* may carry its own non-commercial restriction separate from the code/weight licence, per a GitHub issue on the repo; not resolved further this session | ~5 fps reported in one third-party benchmark (unverified provenance) | Needs a trimap (or a proxy trimap generator) per frame, which is more pipeline complexity than RVM/BiRefNet's fully-automatic alpha. Second choice behind BiRefNet unless trimap quality turns out to matter more than expected. |
| **RMBG-2.0** (BRIA) | Strong general dichotomous segmentation, popular for background removal | **NC** — CC BY-NC 4.0 for non-commercial use; commercial use requires a paid BRIA agreement (confirmed on the HF model card) | Not benchmarked | Blocked without paying BRIA. |
| **SAM 2** (video segmentation) | Promptable, temporally-consistent object masks across a whole video; natively multi-object (mark the person AND the cat as two separate prompted objects, get two tracked masks) | **Apache-2.0** (confirmed, `facebookresearch/sam2` — checkpoints, demo and training code all Apache-2.0) | Real-time-oriented design (streaming memory architecture); exact 1080p fps on a 6 GB card not independently benchmarked this session, but SAM2's own base model is designed to run interactively on a single consumer GPU | **This is the standout recommendation of the whole survey.** Apache-2.0, does temporally-consistent person segmentation (fixing RVM's flicker) and can hold a second independent mask for the cat in the same pass with a second point/box prompt — solving both matting asks in section 4 with one tool. It gives a binary/soft mask, not a matte with fine hair detail the way RVM's alpha or BiRefNet-matting does, so the likely right combination is **SAM 2 for the temporally stable coarse mask + BiRefNet-matting (or RVM, kept) for the fine hair/edge alpha inside that mask** — i.e. SAM 2 solves "which pixels are the person, robustly, across the whole clip," not "exact hair-strand alpha." |
| **rembg** | Thin Python wrapper around various background-removal models (U2Net, ISNet, BiRefNet, etc.) | **MIT** wrapper (confirmed on PyPI); **the model weights it downloads keep their own licences** — several of its bundled models (e.g. any BRIA-derived ones) are NC even though `rembg` itself is MIT | `pip install rembg` | Model-dependent | Fine as a launcher, but check which underlying model `rembg` pulls before trusting the output as "MIT" — the wrapper being MIT does not launder the weight's licence. Use it pointed at BiRefNet's MIT weights, not at any BRIA-derived preset. |
| **BRIA RMBG-1.4** | Earlier BRIA background-removal model, common in `rembg` presets | **NC** — CC-licensed for non-commercial use, same commercial-agreement requirement as RMBG-2.0 (confirmed on the HF model card) | — | Blocked, same as RMBG-2.0. |

**For cutting monkeys out of high-res photos** (the `jungle_monkeys_plate.jpg` backdrop use
case already in the pipeline): **BiRefNet (MIT)** is the clean choice — general-purpose
dichotomous segmentation, no BRIA/Sapiens NC entanglement, and high-resolution checkpoints
exist (`BiRefNet_HR-matting`, 2048x2048) for a "high-resolution photo" use case specifically.
`rembg`'s default U2Net-based path is also fine licence-wise if BiRefNet isn't wired up yet.

## 5. Depth / surface normals of the person (for shading painted muscles)

| Tool | Sizes / variants | Licence | Verdict |
|---|---|---|---|
| **Depth Anything V2** | Small (25M) / Base (97M) / Large (335M) / Giant (1.3B) | **Split by size** — Small is **Apache-2.0**; Base, Large and Giant are **CC BY-NC-4.0** (confirmed via the model's own GitHub issues discussion and HF model cards) | Only the **Small** checkpoint is commercially clear. It's also the fastest, which happens to line up with this GPU's budget — a real win, but expect a visible accuracy drop vs. Large on fine torso relief; test whether Small's depth is smooth enough to shade a muscle-heat overlay convincingly before committing. |
| **Marigold** | Diffusion-based depth (and normals via a MarigoldNormals variant), repurposes Stable Diffusion | **Apache-2.0** since 2023-12-19 per the project's own licence update (confirmed via search of `prs-eth/Marigold`) | Diffusion-based means multiple denoising steps per frame — likely far too slow for per-frame video use on a 6 GB card without an ensemble-size/step-count that trades quality for speed; better suited to still frames (e.g. a single "hero" rep-top card) than the full clip. Fully commercial-clear though, which Depth-Anything's Base/Large are not. |
| **Sapiens normals / Sapiens2** | Per-pixel surface normals, Sapiens2 specifically emphasises normals + pointmaps over depth | **NC** — same Sapiens family CC BY-NC licence (Sapiens2's own README flags possible additional restrictions in its own licence text, not independently re-fetched this session) | Blocked, same as the rest of the Sapiens family. |

**Verdict:** **Depth-Anything-V2-Small (Apache-2.0)** for anything that must run per-frame on
this GPU; **Marigold (Apache-2.0)** only for occasional still frames (a hero card, a title
frame) where diffusion-model latency doesn't matter. Nothing NC-free gives both depth and
speed at once — that's the real trade-off in this section.

## 6. Face landmarks for a precise chin point (when the face is visible)

| Tool | Points | Licence | Behaviour under bar occlusion |
|---|---|---|---|
| **MediaPipe FaceMesh** (already effectively in the mediapipe install) | 478 points, incl. dense lip/jaw contour | **Apache-2.0** (MediaPipe's own licence, same as the Pose Landmarker already used) | **Already known from this project's own footage to hallucinate**: visibility/presence stays high even with the whole head hidden — this is the exact failure mode the current SKILL.md rules already work around by never trusting face-based chin/visibility signals during occlusion. No reason to expect FaceMesh's occlusion honesty to differ from Pose Landmarker's, since both come from the same MediaPipe confidence-head design. |
| **InsightFace** (106-pt 2D, or 68/3D variants) | 106 or 68 points | **Mixed** — the `insightface` *code* is MIT ("no limitations for commercial usage"), but the pretrained model packs (buffalo_l, antelopev2, etc.) are explicitly **non-commercial research only**, with a stated commercial-licensing contact (confirmed on the project's own site and GitHub issues) | Not tested this session; RetinaFace-style detectors typically report a bounding-box/landmark confidence that drops with partial visibility, but whether it degrades gracefully with a bar across the chin specifically wasn't verified | Blocked by the model-pack licence for the accurate 106-pt models, independent of any occlusion behaviour question. |
| **3DDFA_V3** (CVPR 2024 Highlight) | Dense 3D face + explicit facial-part segmentation used as reconstruction guidance | **Unconfirmed** — no LICENSE file located this session for `wang-zidu/3DDFA-V3`; treat as all-rights-reserved until the authors clarify | Its whole selling point is using part-segmentation to handle difficult poses/expressions, which sounds relevant to a tilted-back head at a rep top, but the licence gap makes this moot for now. | 
| **face-alignment** (Bulat, `1adrianb/face-alignment`) | 68-pt 2D or 3D jaw contour | **BSD-3-Clause** (confirmed, repo's own LICENSE file) | Not tested this session; a 2017-era heatmap-regression model, likely to behave like MediaPipe/dlib-era landmarkers under occlusion — no confidence output that's known to be more honest than MediaPipe's, so it likely inherits the same "hallucinate a chin position" risk when the head is behind the bar, rather than fixing it. | 

**Verdict:** none of these solve the actual occlusion problem better than the project's own
already-validated workaround (measure the chin geometrically from the visible eye/mouth axis
at oblique angles, and fall back to the YOLO occlusion witness when the head is fully hidden).
`face-alignment` (BSD) is the only commercially-clear *alternative* landmark source if FaceMesh
ever needs a second opinion on the visible-face frames, but it brings no evidence of being
better-behaved under occlusion than what's already in use, so it isn't worth adding without a
concrete accuracy complaint about FaceMesh on visible-face frames specifically.

## 7. CUDA torch / onnxruntime-gpu feasibility on this RTX 2060 (Turing, sm_75)

- **A fresh CUDA-enabled torch venv is straightforward in 2026.** PyTorch 2.9/2.10 (current
  stable line as of this session) ship pip wheels for `cu121`/`cu124`/`cu126`/`cu128`, and the
  standard **x86_64 Windows/Linux** wheels for all of these include **sm_75 (Turing)** kernels —
  confirmed by cross-referencing a compute-capability-by-PyTorch-version summary against the
  official CUDA-13 release notes (which explicitly says CUDA 13 keeps sm_75 as its new floor,
  i.e. sm_75 is even more clearly a first-class target than before, not a legacy one).
  **Caveat:** a PyTorch forum thread this session did show cu126 dropping sm_75 warnings for a
  Turing card — but that thread was specifically about the **ARM64** (`aarch64`) build variant
  used on Grace-Hopper-style systems, not the ordinary Windows x86_64 wheel this machine would
  install; it does not apply here. No install was attempted this session to double-confirm.
- **Install command:** `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128`
  (or `cu126`/`cu124`/`cu121` for an older CUDA driver on this machine — check
  `nvidia-smi`'s reported "CUDA Version" ceiling first; any of these index URLs work the same
  way, just swap the suffix).
- **Download size:** the torch wheel alone is on the order of **3-3.5 GB** for a `cu128`+Python
  3.13 combination (a same-shape cu128/Python-3.12 wheel was directly measured at 3338.3 MB by
  a third party this session); torchvision/torchaudio add a few hundred MB more. Budget roughly
  **4 GB of download** for the three packages together, on top of whatever CUDA runtime DLLs
  ship inside the wheel (recent torch wheels bundle their own CUDA/cuDNN runtime, so a separate
  system CUDA Toolkit install is not required just to run inference).
- **Keep it a NEW venv, not a change to `.venv-pushup`.** The current pipeline is deliberately
  CPU-only (`torch 2.13 CPU-only`) per the skill file; swapping that venv to a CUDA build risks
  breaking whatever pinned CPU-specific behaviour the existing scripts depend on. A second venv
  (e.g. `.venv-pushup-gpu`) sharing nothing but the source scripts is the safer path, exactly as
  this survey's "Recommended stack" section below assumes.
- **onnxruntime-gpu on Windows with CUDA 12 works via plain pip.** `pip install onnxruntime-gpu`
  has defaulted to CUDA-12.x-compatible builds since onnxruntime 1.19, confirmed on the
  project's own install docs; Python 3.13 support was also seen referenced directly in
  onnxruntime's own GitHub issue tracker this session. This is the path that makes `rtmlib`
  (section 1) GPU-accelerated on this machine without touching torch at all — `rtmlib` only
  needs `onnxruntime`/`onnxruntime-gpu`, not a torch CUDA build, which makes it the lowest-risk
  GPU entry point of everything surveyed.
- Net take: **a CUDA torch venv is realistic and well-supported for this GPU in 2026**, but the
  *lowest-friction* GPU win specifically for this project is `onnxruntime-gpu` + `rtmlib`
  (RTMPose/RTMW/DWPose), which sidesteps the torch-CUDA question entirely for the pose-tracking
  half of the pipeline.

## Recommended stack for the next video (priority order)

1. **`rtmlib` + RTMW (or DWPose) as a third, wholebody-aware tracker, CPU first, GPU via
   onnxruntime-gpu if the fps needs it.** Apache-2.0 throughout, installs with no C++ build,
   and RTMW's 133 COCO-WholeBody points include the jawline — this is the most direct fix for
   "no face-contour points for the chin measurement" and can slot in alongside the existing
   MediaPipe + YOLOv8 pair as a third cross-check rather than a replacement.
   `pip install rtmlib onnxruntime` (CPU) or swap in `onnxruntime-gpu` (needs the CUDA-12
   runtime pulled in automatically by the wheel — see section 7). **Before trusting it for the
   chin/occlusion logic, explicitly test whether RTMW's per-keypoint confidence collapses under
   lintel occlusion the way YOLOv8's does** — that behaviour is assumed, not verified, above.

2. **SAM 2 for a temporally-consistent coarse person (and cat) mask, feeding into the existing
   RVM/skin-classifier paint-region logic instead of replacing it outright.** Apache-2.0, and
   it is the one tool in this whole survey that cleanly solves *two* named asks at once (person
   matting stability + a second independent cat mask) under a licence with zero caveats.
   `pip install torch` (CPU is fine for SAM2's own inference speed class relative to this
   pipeline's other costs) `git+https://github.com/facebookresearch/sam2` per its own install
   instructions (no separate pip package was found under a stable name this session — install
   from source per the repo's README). Treat this as sitting *upstream* of RVM: SAM 2 says
   "these pixels are the person, robustly, every frame"; RVM (or BiRefNet-matting, below) still
   does the fine hair-strand alpha inside that stable region.

3. **SCHP (MIT) as a straight upgrade to the MediaPipe `selfie_multiclass_256x256` segmenter**
   for skin/hair/clothes classes — finer LIP-20 classes (separate upper-arm/lower-arm/torso
   skin), no exotic install, and it directly targets the flicker-near-the-head problem the
   skill file already documents as a workaround-requiring MediaPipe weakness.
   `pip install torch torchvision` (already have torch CPU; SCHP is plain PyTorch, no custom
   ops) then clone `PeikeLi/Self-Correction-Human-Parsing` and use its LIP checkpoint.

4. **BiRefNet-matting (MIT) as a bake-off candidate against RVM**, and as the tool for cutting
   the monkey backdrop subjects out of high-resolution photos (replacing any ad hoc GrabCut
   step). `pip install birefnet` (or run from the `ZhengPeng7/BiRefNet` repo directly;
   HF `transformers`-style loading is also documented on the model cards) — try it once on a
   representative clip before deciding whether to actually replace RVM, since RVM's ~5 fps CPU
   number and BiRefNet's ~17 fps *on an RTX 4090* mean this RTX 2060 result is genuinely unknown
   until measured.

5. **Depth-Anything-V2-Small (Apache-2.0)** as an experimental input to the muscle-heat shading
   — the only depth model in the whole survey that is both fast enough for this GPU and
   commercially clear (every larger/more-accurate Depth-Anything-V2 checkpoint is CC BY-NC).
   `pip install torch transformers` then `AutoModelForDepthEstimation.from_pretrained
   ("depth-anything/Depth-Anything-V2-Small-hf")`. Treat as exploratory (like the existing
   lighting-based torso indices) rather than a load-bearing measurement, and sanity-check
   whether Small's depth is detailed enough to shade convincingly before it goes in a real
   export.

**Explicitly not recommended, and why:** every SMPL/SMPL-X-based 3D mesh method (4D-Humans,
WHAM, TRAM, TokenHMR, SMPLer-X, GVHMR) and every Sapiens/BRIA/NLF/MatAnyone/RMBG checkpoint —
all NC, all blocked for a video posted publicly under the repo's own "must be able to post
publicly" constraint. DensePose is not rejected on licence grounds (it's Apache-2.0) but on the
realistic Windows-build cost of Detectron2 on this machine; revisit only if the SCHP-plus-atlas
path turns out to be a genuine dead end and true UV coordinates become worth a build fight.
