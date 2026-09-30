# Muscle-up analysis

A side-on clip of a bar muscle-up (bodyweight or weighted) is graded rep by rep on the four
technical faults that decide heavy weighted muscle-ups in competition. The faults, their
order and what causes what come from coach commentary on real competition attempts; the
script measures each of them on a MediaPipe pose track.

Status: the method and the script are in; the thresholds are set from a synthetic check and
the commentary below, and still have to be fitted on graded side-on clips.

## Source of the method

**Tescoaching, "Évite ces erreurs sur ton Muscle-up lesté ! (Étude de cas final rep)"**,
YouTube, 2025-10-05, <https://www.youtube.com/watch?v=HwAlRdk9OeQ> (French, 9:42). A
breakdown of the Finalrep Worlds weighted muscle-up flight. Only the method is kept here;
no frame of the video is redistributed.

Every lifter in that flight pulls high enough. The attempts are lost on technique, and the
commentary keeps coming back to one chain:

1. **Too much swing at the start** (*trop de balancement*). A one-shot start jumping off the
   box, or with the weight resting on the box, builds horizontal momentum (Aditya, 2:40;
   Bartos, 6:45). The coach advises against the small jump off the box.
2. **More swing needs more hip flexion** to keep the weight in front of the bar, and that
   flexion has to be **held through the transition** (*maintenir la flexion de hanche*,
   3:00-3:17). Enough, not excessive: the clean lifters flex just enough for their swing.
3. **Flexion lost means the weight ends up under or behind the bar** (3:20-3:32, 7:03). The
   weight should travel vertically and stay in front of the bar (1:30-2:15).
4. **Weight behind the bar always gives a leg kick-back** (*retour de jambe*, 3:32, 7:10).
   With enough height and speed the rep still goes up, but the kick is judged: Aditya's 40 kg
   third attempt (4:40-5:15) and Bartos (7:26) are no-reps for the legs, not for a lack of
   pull height. Knee flexion on top of the lost hip flexion makes it worse (Bartos, 7:47).

The clean references: the first lifter shown (0:00-2:30: little swing, feet fixed, weight in
front, vertical path, still at the top) and the last one, a 46.5 kg record attempt
(8:12-9:20: little swing, hip flexion sufficient and held, weight in front, only a slight
leg return because a little weight sits behind the bar at a 1RM).

## What is measured

All distances are in torso lengths (shoulder midpoint to hip midpoint, median over the clip),
so no height or camera calibration is needed. "In front" means the side the lifter faces
(nose vs ears).

| Fault | Metric | Flag when |
|---|---|---|
| `swing` | hip horizontal range in the 1.5 s before the pull starts (last lowest-shoulder frame) | > 0.5 |
| `hip_flexion_lost` | hip angle (shoulder-hip-knee) at the transition minus its minimum during the pull | > 25 deg |
| `weight_behind_bar` | centre of mass in front of the bar at the transition (segment centres weighted by Winter's mass fractions) | < 0 |
| `leg_kickback` | how far the ankle midpoint goes behind the bar in the second after the transition | > 0.3 |

The transition is the first frame the shoulder midpoint is above the bar; each stretch of at
least 0.15 s above the bar is one rep. The hips opening towards lockout after the transition
is normal and not penalised. Pull height is not graded: in this material it is never the
limiter.

## Pipeline

```bash
PY=.venv/bin/python        # Windows: .venv/Scripts/python.exe
# 0. only when other people are in the frame: crop to the lifter (MediaPipe tracks one pose
#    and will lock on to the loader in front of the rig)
ffmpeg -i clip.mp4 -vf "crop=W:H:X:Y" -an -c:v libx264 -crf 16 work/mu.mp4
# 1. pose
$PY tools/scripts/extract_pose_mp.py work/mu.mp4 tools/models/pose_landmarker_heavy.task work/mu_pose.npz
# 2. grade (bar=X,Y in source pixels overrides the bar found from the resting wrists)
$PY tools/scripts/analyze_muscleups.py work/mu_pose.npz work/mu.json
# check
$PY tools/scripts/test_analyze_muscleups.py
```

`analyze_muscleups.py` prints one line per rep and writes the metrics, the timestamps and the
faults to the JSON.

## Rules

- **Film side-on, camera level with the bar, the whole body and the bar in frame.** Swing,
  hip position, centre of mass and kick-back all happen in the sagittal plane; from the front
  they are depth and not seen. The script measures shoulder width against the torso and, on
  a front view, prints the numbers with no verdict rather than grading noise.
- **Crop to the lifter when anyone else is in the frame**, then check the tracked landmarks on
  a few frames before trusting any number.
- **Check the bar line** on one frame: the auto bar is the median of the resting wrists, which
  is wrong if the clip is mostly walking around.
- **Recalibrate the thresholds** once there are side-on clips with known outcomes (clean /
  no-rep for the legs); they are first estimates.

## Worked check (2026-09-30)

The source video is front-on competition footage, so it can only check the plumbing: on the
46.5 kg record attempt, cropped to the rig, the pose follows the lifter, the auto bar sits on
the bar, one rep is found at the transition and the view is flagged `front` with no verdict.
Without the crop, MediaPipe tracked the loader standing in front of the rig.
