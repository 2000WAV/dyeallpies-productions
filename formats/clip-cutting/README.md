# Clip cutting

Cuts a time range out of a screen / OBS recording into an MP4 that plays full-frame in
WhatsApp, YouTube and Instagram, and optionally converts a 1920x1080 recording into a
1080x1920 vertical for Reels and Shorts. Sources are OBS files named like
`YYYY-MM-DD HH-MM-SS.mkv` (or `-vertical.mkv` for native vertical recordings).

## Landscape cut

```bash
ffmpeg -y -ss HH:MM:SS -to HH:MM:SS -i "source.mkv" \
  -c:v h264_nvenc -preset p5 -tune hq -rc vbr -cq 19 -b:v 0 -spatial-aq 1 -temporal-aq 1 \
  -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart \
  "source-clip-<startHHMM>-<endHHMM>.mp4"
```

- `-ss` / `-to` before `-i` for fast seeking.
- **Always re-encode. Never `-c copy`** into mkv or mp4: WhatsApp's compressor mishandles
  copied streams and renders black bars on the sides. An explicit pixel format and
  faststart avoid it.
- `libx264 -preset medium -crf 18` without an NVIDIA GPU. NVENC encodes 1080p60 at
  3–4× realtime against ~1× for x264 medium, with equivalent quality for YouTube and
  Instagram purposes (it spends more bitrate to get there).
- **Never reduce quality to save size.** These go to YouTube and Instagram, where a
  high-quality source matters; upload size does not.
- Name the output after the source with the start and end times, in the same directory.

## Vertical (Reels / Shorts) conversion

Centre-crop to 9:16 and upscale with Lanczos:

```
-vf "crop=608:1080:656:0,scale=1080:1920:flags=lanczos"
```

Gameplay usually keeps the player centred, so the centre crop keeps the action in frame,
but spot-check a frame of the output (`ffmpeg -ss <t> -i out.mp4 -frames:v 1 check.jpg`)
to confirm the image is centred rather than an edge. Name these
`<stem>-vertical-clip-<start>-<end>.mp4`.

## Rules

- **One encode at a time.**
- **Run long encodes detached.** A process killed mid-write leaves a file with a
  plausible size, a reported exit code 0, and no `moov` atom. This happened and silently
  produced a bad clip.
- **Verify before reporting** with `ffmpeg -v error -i clip.mp4 -f null -`.
- **Confirm the exact timestamps first**, especially "black screen" boundaries, which are
  often off by a second and cheap to get wrong against a re-encode.
- **Check the source still exists before queueing a batch.** Sources and uploaded cuts
  get deleted to free disk; a vertical master cut only into parts cannot be re-cut from
  the parts.
