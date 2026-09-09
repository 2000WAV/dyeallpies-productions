# Deck walkthrough

A short silent MP4 that walks a collaborator through already-rendered figures, one slide
per figure with a title and a one-line takeaway above it: the quick peek before opening
the report. It is a preview of a document, not a replacement, so the closing slide says
what to open next. There is no source footage; every frame is drawn from scratch.

```
figures (PNG, already exported)
  └─> compose slides with PIL  ──> slideNN.png
        └─> ffmpeg xfade chain  ──> walkthrough.mp4
```

Keep the two steps separate: when a caption is wrong you re-render one slide, not the
analysis. The build script lives with the analysis it summarises (it reads that
project's results JSON and figure manifest), so there is no shared script here; the
recipe is the method below.

## Non-negotiables

- **Never retype a number onto a slide.** Read every value from the machine-readable
  artefact the analysis already produces (a results JSON, a metrics CSV). A slide that
  restates `0.772` as a string literal silently outlives the result it describes. The
  video is the deliverable people quote from and the least likely to be rebuilt when the
  numbers move.
- **Silent by default.** No voice track means no accent mismatch, no TTS artefacts, and
  it plays in an email preview pane. Mux a silent AAC track anyway, since some players
  refuse a video-only MP4:
  `-f lavfi -t <total> -i anullsrc=channel_layout=stereo:sample_rate=44100`.
- **Match the deck's palette exactly.** Read the same hex values the charts use; a video
  in slightly different greys reads as a different document.
- **Takeaway above the figure, not below.** The sentence is the reason the figure is on
  screen; put it where it is read first.

## The xfade chain

For N inputs with durations `d[]` and transition `t`, the k-th transition's offset is
measured on the accumulated stream: the running total minus the transitions already spent.

```python
offset = 0.0
for k in range(1, n):
    offset += d[k-1] - t
    f"{prev}[{k}:v]xfade=transition=fade:duration={t}:offset={offset:.3f}[v{k}]"
```

Final duration is `sum(d) - t*(n-1)`. Get this wrong and the tail slides are clipped or
frozen; always check the reported duration against the formula. End the chain with
`format=yuv420p`, or QuickTime and some Windows players show a black frame.

## Rules

- Exported figure PNGs have wildly different aspect ratios when cropped to content. Fit
  each into a fixed box preserving aspect and centre it.
- Guard against a missing PNG: drop its slide rather than rendering an empty card.
- Pacing: 7–10 s per figure slide, 10–14 s for a text slide with several bullets, 6–7 s
  for the title. Read each caption aloud at a normal pace and add ~2 s. Two minutes is
  long; past that, cut slides rather than speeding them up.
- Long encodes run detached, one at a time, verified with
  `ffmpeg -v error -i out.mp4 -f null -`.
