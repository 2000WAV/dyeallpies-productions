"""studio: the shared library behind every DyeAllPies video format (2026-09-12).

The per-format scripts in tools/scripts/ import from here instead of carrying their own copies of
the encoder pipe, the decode gate, the bake-once cache, the sRGB maths, the brand palette and the
GPU renderer. One module per concern:

    studio.colour   sRGB <-> linear (arrays and the 8-bit LUT), hex helpers, the WCAG contrast formula
    studio.encode   ffmpeg/ffprobe: the NVENC raw-frame writer, the decode gate, the 720p copy,
                    concat WITHOUT re-encoding (the sting append), a matching silent sting encode
    studio.cache    the bake-once memmap with a JSON validity key (memory render-iteration-cache)
    studio.gl       moderngl on the RTX 2060: standalone context, meshes for MuJoCo geoms, the
                    pinhole clip matrix, the depth+ID geometry pass, the 2x -> 1x accumulate pass
    studio.brand    the palette and the fonts (tools/brand/BRAND.md is the human-readable copy)

Import: `tools/install_studio.sh <venv>` drops a .pth into the venv so `import studio` works from
anywhere; the scripts also fall back to a sys.path insert of tools/ (see tools/README.md).
"""
__version__ = "0.1"
