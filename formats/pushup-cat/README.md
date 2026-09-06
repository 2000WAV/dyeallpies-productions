# Push-up counter with a cat counter

The first ML format (Aug 2026): a push-up set gets a big live rep counter with a pop
animation and the current rep's depth in degrees, and the cats that wander through the
frame get their own live count. A notification "ding" plays on each rep and a real meow
on each cat-count increment. The pull-up format grew out of this one.

## Pipeline

```bash
# 1. per-frame elbow-angle and shoulder-height signal from MediaPipe Pose
python tools/scripts/extract_pushup_signal.py in.mp4 tools/models/pose_landmarker_lite.task pushup.csv
# 2. count reps and plot the signal for a sanity check
python tools/scripts/count_pushups.py pushup.csv pushup_plot.png
# 3. cats: YOLOv8n detection (any body angle), colour-histogram identity so re-entries don't double count
python tools/scripts/extract_cat_signal_yolo.py in.mp4 tools/models/yolov8n.pt cats.csv
#    (Haar cascade alternative, frontal faces only: extract_cat_signal.py in.mp4 tools/models/haarcascade_frontalcatface_extended.xml cats.csv)
# 4. overlay: REPS top-centre (Impact), depth below it, live CATS count below that
python tools/scripts/render_final_v2.py in.mp4 pushup.csv cats.csv overlay.mp4
# 5. sound effects mixed into the clip's own audio, then muxed
python tools/scripts/mix_sounds.py in.mp4 pushup.csv cats.csv ding.wav meow.wav mixed.wav
ffmpeg -y -i overlay.mp4 -i mixed.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart final.mp4
ffmpeg -v error -i final.mp4 -f null -
```

| script | does |
|---|---|
| `extract_pushup_signal.py` | MediaPipe PoseLandmarker (Tasks API) per frame → elbow angle and shoulder y to CSV |
| `count_pushups.py` | Savitzky–Golay smoothing, peak / valley detection, rep count, diagnostic plot |
| `extract_cat_signal_yolo.py` | YOLOv8n `cat` boxes per frame, grouped into sightings; distinct individuals by HSV colour histogram; live visibility count capped at 2 |
| `extract_cat_signal.py` | the Haar-cascade version (frontal cat faces only) |
| `render_final_v2.py` | the final overlay: rep detection on smoothed shoulder y with an elbow-angle sanity filter to reject shallow dips |
| `render_final_overlay.py`, `render_combined_overlay.py`, `render_debug_video.py` | earlier overlay versions and the debug view with the raw signal |
| `mix_sounds.py` | places a full ding on every rep and a full meow on every cat increment over the original audio |

Models: `pose_landmarker_lite.task` (MediaPipe model card), `yolov8n.pt` (ultralytics
assets), `haarcascade_frontalcatface_extended.xml` (OpenCV's `data/haarcascades`). All
gitignored. The two sound effects are not included; any short WAV works.

## What it taught

- **Count on shoulder height, not the elbow angle alone.** Elbow occlusion and motion
  blur break the angle signal at the bottom of the rep; smoothed shoulder y is robust and
  the elbow angle is kept only as a sanity filter against shallow or false dips.
- **A live count, not a cumulative one, for the cats.** The count is what is visible now,
  capped at the number of cats in the house; identity by colour histogram stops the same
  cat re-entering from counting twice.
- **Full-length sound effects at the event**, never truncated to the next event; a cut-off
  meow reads as a glitch.
