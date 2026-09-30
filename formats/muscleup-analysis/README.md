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

**The hands are the bar.** They never leave it during an attempt, so the wrist midpoint is the
bar position frame by frame and every distance is taken from it. That cancels a hand-held phone
that pans to follow the lift, and needs no bar marking. All distances are in torso lengths
(shoulder midpoint to hip midpoint, median over the clip), so no height or camera calibration
is needed. "In front" means the side the lifter faces (nose vs ears).

**Attempts and outcomes.** An attempt starts from a hang (hands above the nose for 0.3 s) and
runs to the next hang. The transition is the first time the shoulders stay over the hands for
0.15 s while the hands are still on the bar.

| Outcome | Meaning |
|---|---|
| `rep` | over the bar (the transition is made). The support height, shoulders over the hands until he lets go, is reported in torso lengths but not judged: on real sets clean reps read 0.75 to 1.2 and a verified stuck dip 0.94, the camera angle and the head leaving the frame decide more than the lockout does |
| `miss_pull` | never over the bar; graded at the highest point, if the shoulders got within 0.25 torso of it |

What is **not** an attempt, each one a false positive met on real clips: walking past the rig
(no hang), letting go and landing (the shoulders never reach the bar: at most 0.3 torso under
where the hands were just before the hang ended), sliding back under the bar before letting go
(the hands move more than 0.5 torso within 0.1 s of the event, or the shoulders rose less than
0.4 torso from the hang's low point). Elbow angles are not used: MediaPipe loses the arms when
the head leaves the top of the frame, which is exactly when they matter.

| Fault | Metric | Flag when |
|---|---|---|
| `swing` | hip horizontal range in the 1.5 s before the pull starts (last lowest-shoulder frame) | > 0.5 |
| `hip_flexion_lost` | hip angle (shoulder-hip-knee) at the transition minus its minimum during the pull | > 25 deg |
| `weight_behind_bar` | centre of mass in front of the bar at the transition (segment centres weighted by Winter's mass fractions) | < 0 |
| `leg_kickback` | how far the ankle midpoint goes behind the bar in the second after the transition | > 0.3 |

Also measured, not graded: the knee angle (hip-knee-ankle, 180 = straight) at the transition
and its minimum during the pull. Tescoaching names bent knees on top of lost hip flexion as what
makes a kick-back worse (7:47); there is no threshold until graded clips give one.

The faults are graded on misses too: that is where they explain something. The hips opening
towards lockout after the transition is normal and not penalised. Pull height is not graded: in
this material it is never the limiter.

## Pipeline

```bash
PY=.venv/bin/python        # Windows: .venv/Scripts/python.exe
# 0. trim to the attempts (no warm-up pull-ups: a pull-up is a muscle-up with no transition and
#    grades as a miss) and, when anyone else is in the frame, crop to the lifter: MediaPipe
#    tracks ONE pose and picks whoever it likes, the loader or someone on the next rig
ffmpeg -ss T0 -to T1 -i clip.mp4 -vf "crop=W:H:X:Y" -an -c:v libx264 -crf 16 work/mu.mp4
# 1. pose
$PY tools/scripts/extract_pose_mp.py work/mu.mp4 tools/models/pose_landmarker_heavy.task work/mu_pose.npz
# 2. grade
$PY tools/scripts/analyze_muscleups.py work/mu_pose.npz work/mu.json
# check
$PY tools/scripts/test_analyze_muscleups.py
```

`analyze_muscleups.py` prints one line per attempt (outcome, the four metrics, the faults) and
writes them with the timestamps to the JSON. Look at the frames at each printed time before
trusting a line: draw the landmarks on them.

## Viewer

```bash
$PY tools/scripts/mu_viewer.py            # then open http://localhost:8765
```

A local page for going through the clips: it lists `muscleup-*` on the NAS (read only, over ssh),
fetches the chosen clip, re-encodes it to H.264 if needed, runs the pose and the analysis, caches
everything under `work/viewer/`, and prepares the next clip while this one plays. Over the video,
in sync: the skeleton, the bar (the hands) with its vertical plane, the shoulders marker (green
over the bar), the centre-of-mass arrow (green in front, red behind), and a banner with the
outcome and the faults during each attempt. Beside it, live: phase, shoulders vs bar, hip and
knee angles, centre of mass; the attempts with their metrics, click to jump. Keys: left / right
clip, space, `,` `.` frame by frame, 1 2 3 speed.

Clip names on this NAS came from a per-session sort and are wrong for about a third of the
files (a `muscleup-` clip can be dips): list by the sorted folder once the clips are filed.

### From the phone (gym)

The same server, reached from the iPhone over the tailnet (`tailscale serve`, HTTPS, never
funnel; the server itself stays on 127.0.0.1):

- **Envoyer**: pick or film a clip, choose MU or pull-ups; it is stored under `work/uploads/`
  with a name the server makes (`up-<kind>-<date>-<time>-<hex>.mp4|mov`, 600 MB cap, mp4/mov only),
  analysed like the NAS clips, and listed under *Envois*. Uploads stay on the PC, not the NAS.
- **Live** (`/live`): rear camera, MediaPipe Tasks Vision in the browser (lite model), skeleton,
  shoulders vs hands, rise speed, knee flexion and a rep counter. The counter is a small JS port of
  the rules above and only a live approximation; *Enregistrer* records the set and sends it for the
  full server analysis.
- Persistent: `~/.config/systemd/user/mu-viewer.service` (the PC and WSL must be on).

## Rules

- **Film side-on, the whole body and the bar in frame, head included at the top of the
  transition.** Swing, hip position, centre of mass and kick-back all happen in the sagittal
  plane; from the front they are depth and not seen. The script measures shoulder width against
  the torso and, on a front view, prints the numbers with no verdict rather than grading noise.
  A three-quarter view still grades, with every horizontal distance shrunk by the angle.
- **A hand-held phone is fine**, following the lift: the hands are the reference.
- **Trim and crop** (step 0): other people in the frame are the first source of wrong lines.
- **Recalibrate the thresholds** once there are side-on clips with known outcomes (clean /
  no-rep for the legs); they are first estimates.

## Worked checks (2026-09-30)

- **The source video** is front-on competition footage, so it only checks the plumbing: on the
  46.5 kg record attempt, cropped to the rig, the pose follows the lifter and the view is
  flagged `front` with no verdict. Uncropped, MediaPipe tracked the loader in front of the rig.
- **Eight gym clips** (weighted muscle-ups, April 2026, hand-held phone, side-on to
  three-quarter, other people training around), every printed line checked against the frames:
  - right: 7 reps and 2 press misses, including a miss stuck in the dip (over the bar,
    slid back, let go) and a rep whose lockout the tracker split in two as the head left the
    frame. Each false positive listed above came from these clips and has a test in
    `test_analyze_muscleups.py` built to fail without its rule.
  - wrong, all from framing, none fixable in the analysis: warm-up pull-ups read as pull misses
    (3), standing on the box to set the grip read as a pull miss (1), MediaPipe following
    someone else (a lifter on the rig behind, a bystander next to the phone, a figure at the
    far end of the gym: 6 lines over 3 clips), and one attempt filmed with the bar and the hands
    above the frame, not found at all. Hence step 0 and the framing rule.
  - the faults are **not yet discriminative**: every rep and every miss here is flagged for
    swing (0.7-1.4 torso) and for weight behind the bar, reps and misses alike.
    Either this lifter swings on every attempt, or the thresholds are too strict for a kipping
    weighted muscle-up filmed three-quarter. Settling it takes clips graded by a judge or a
    coach (clean / no-rep and why), the same way Tescoaching grades the Worlds flight.
