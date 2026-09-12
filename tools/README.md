# tools/ — the DyeAllPies design toolkit

Everything that is not one video's own data lives here. The per-video folders (`hand/`, `pushup/`,
`pullup/`, ...) hold a plan, a model document, a caption and the scratch (`work/`, `out/`); the code
that turns a recording into a delivered file is here, shared.

```
tools/
  studio/        the library every format imports (2026-09-12): encode, cache, colour, gl, brand
  scripts/       the per-format pipelines and one-off analysis scripts (python tools/scripts/<x>.py)
  brand/         BRAND.md (the reasoning), fonts/ (OFL); the palette itself is studio/brand.py
  models/        downloaded tracker weights (gitignored; the extract_*.py scripts say where from)
  assets/, sounds/   emoji sheets, the ding and the meow
  mirror_*.sh    what each format copies into the public mirror (../dyeallpies-productions)
  install_studio.sh  drops a .pth into a venv so `import studio` works there
```

## studio, the library

| module | what it holds | used by |
|---|---|---|
| `studio.encode` | `RawWriter` (BGR frames piped into NVENC or x264, audio from the source or a generated silent track), `decode_check`, `preview_720`, `probe`, `sting_encode_args` + `concat_copy` (a join with no re-encode) | render_puppet, render_brand_sting |
| `studio.cache` | `BakeCache`: the bake-once memmap + JSON validity key, with the reason a bake reran | render_puppet |
| `studio.glow` | the neon glow in linear light: the quarter-resolution wide Gaussian, the mip bloom (3/9/27/81 px), the pool of light on a dark wall (60/180 px), the shoulder that lets a hot core go white | render_puppet, render_brand_sting |
| `studio.colour` | sRGB <-> linear (arrays and the exact 8-bit LUT), hex helpers, WCAG luminance and contrast | render_puppet, brand |
| `studio.gl` | moderngl on the RTX 2060: context, meshes for MuJoCo capsules/ellipsoids/spheres, the pinhole clip matrix matching the scripts' `project()`, the depth+ID geometry pass, the 2x->1x premultiplied accumulate pass (supersampling + motion blur; a second R32F attachment on the accumulation fbo receives a per-pixel glow weight read from the shaded alpha, so a composite can bloom some bodies more than others) | render_puppet |
| `studio.brand` | the palette (`main #231F20`, `secondary #D75413`, `neutral #F2F0EA`, white), the fonts by role, the contrast table | render_brand_sting |

Rules for adding to it:

- A function moves here when a second format needs it, or when it is the encoder, a gate, or a
  cache: things every format must do the same way (CLAUDE.md's export rules).
- No per-video constants: a look, a model number or a layout stays in the format's script and its
  MODEL.md. `studio.brand` is the one exception because the brand is shared by definition.
- Every number in the library still says where it comes from (CLAUDE.md, model code) and the
  module docstring names the incident that made the rule.
- Scripts import it with the .pth (`bash tools/install_studio.sh .venv-hand`) or the two-line
  fallback at the top of `render_puppet.py` (a `sys.path.insert` of `tools/`).

## What is not (yet) in studio

The pull-up and push-up renderers carry their own copies of the encoder pipe, the FFV1 body-layer
cache, the sRGB maths and the PIL text boxes (`render_pullup_overlay3.py`, `render_pushup_overlay.py`,
`pullup_atlas3.py`, `pushup_atlas.py`); they were built before the library and are not to be touched
while their sets may still be iterated (HANDOFF.md). When one of them is next changed, its encoder
and cache move to `studio.encode` / `studio.cache` first. The flicker gate (`check_flicker.py`), the
caption checks (CLAUDE.md) and the mirror scripts are the next candidates, in that order.

## Where the GPU is used

- `studio.gl` for anything rasterised from a simulation (the puppet: 0.04 s a frame at 2x with
  motion blur, against 8.7 s in NumPy).
- NVENC for every export, one encode at a time (`machine-local` skill); x264 for 720p copies.
- The trackers (MediaPipe, YOLO, rembg) run on whatever their wheels support; DWPose via onnxruntime
  is installed in `.venv-pushup` and unused.
