# The hand-puppet video — plan (2026-09-11, before any build)

Source: `Hand_IMG_6087.MOV` (iPhone 14, 2026-09-07, 8.9 s, 267 frames at 30 fps, 1920×1080 HLG
10-bit with no rotation tag, which is why the phone shows it sideways). The upright master is
already made: `hand/work/master.mp4`, 1080×1920, tone-mapped like the push-up master and turned
90° clockwise (sleeve at the top, fingers pointing down, the rune tattoos read upright). The
MediaPipe hand tracker ran on it: `hand/work/hands_mp.npz`, a hand on 254 of 267 frames; the 13
missing frames (28–40, 0.93–1.33 s) are the closed fist.

## What happens in the shot (from the tracker; spread = thumb-to-pinky over the palm length)

| time (s) | frames | hand | puppet |
|---|---|---|---|
| 0.0–0.5 | 0–15 | open, spread 2.3 → 1.7 | not yet in the shot |
| 0.6–1.35 | 18–40 | closes into a fist, the tracker loses it | hidden behind / inside the fist |
| 1.4 | 42 | snaps open, fully stretched (spread 2.2) | **drops** from the palm, falls until the five strings go taut, bounces, settles upright |
| 2.0–2.2 | 60–66 | fingers pulled together (spread 0.9) | strings converge: arms pulled in, a small lift |
| 2.4–5.2 | 72–156 | wide, tips drifting down ~80 px | strings slacken unevenly, the puppet lowers and lolls |
| 5.4–5.6, 6.2–6.4 | 162–168, 186–192 | tips together (spread 1.3) | hands meet, head tips |
| 6.6–7.2, 8.4 | 198–216, 252 | wide again | arms open, upright |
| 7.8–8.2 | 234–246 | together | same |
| 8.6–8.9 | 258–266 | closing again | the puppet is hoisted and crumples as the fist closes (the ending) |

The physics decides what the puppet actually does in each phase; the table is what the finger
motion implies, not a script.

## The pipeline (the pull-up / push-up pattern: extract, analyse, model, render, gate, publish)

1. **Hand in 3D.** Image landmarks + MediaPipe world landmarks; a pinhole camera with the iPhone
   14's video focal length (from research; the puppet's size relative to the hand does not depend
   on it); depth from the palm's pixel width against Dennis's taped palm width (fallback: the male
   norm from research, ranked in the model document). String anchors = the five fingertip pads
   (landmarks 4, 8, 12, 16, 20), smoothed (One Euro) and interpolated across the fist frames.
   First check: whether the camera is static (the wall gave no usable feature for a quick test;
   track the sleeve / wall edges properly). If it moves, the virtual camera follows.
2. **The marionette.** An artist-mannequin-style figure (neon look, see the decisions below) about 30 cm tall, ~150 g, 11 rigid
   bodies (head, torso, pelvis, upper arms, forearms, thighs, shins) with marionette-joint limits, masses
   from segment fractions scaled to the figure (research), every constant sourced in
   `hand/PUPPET-MODEL.md`. Five strings, one per finger; default mapping, to be confirmed by the
   stringing research: thumb → left hand, index → head (left), middle → back yoke, ring → head
   (right), pinky → right hand; the legs hang free and swing. String lengths are set so that at the
   fully stretched hand (frame 42–54) every string is just taut with the puppet upright: from then on
   a fingertip rising pulls its part up, a fingertip lowering lets that string go slack and the part
   drop, fingers spreading pull the arms out.
3. **Physics: MuJoCo** (pip, Python 3.13 wheels exist; a new `.venv-hand`). Strings = spatial
   tendons from a mocap body at each fingertip to a site on the puppet, with a length limit: a
   tendon at its limit pulls, below it does nothing (the slack / taut behaviour Dennis asked for),
   with a little compliance for the thread's give. Sim at 600 Hz on fingertip trajectories
   interpolated from 30 fps; the drop is real free fall followed by the snap when the strings reach
   length; slow motion is free (the sim has the sub-frames) if the plate is interpolated. Sanity
   prints before rendering, like the muscle model's tests: the free-fall time from the palm to the
   taut length against √(2h/g); the settled swing period against 2π√(L/g); every string's tension
   ≥ 0 always; the sum of taut-string tensions at rest = the puppet's weight.
4. **Rendering.** MuJoCo's own renderer offscreen at 1080×1920 (Phong, shadows, textures, MSAA),
   camera matched to the pinhole, the neon material (see the decisions); the strings as glowing tubes: straight
   when taut, a catenary computed from the endpoints and the string length when slack (a light
   thread sags visibly, research confirms the mass per metre). Per-frame motion blur by averaging
   sub-frame renders. A shadow catcher: the wall as a plane at the depth the hand's own shadow
   implies, lit from the direction the hand's shadow gives, rendered with and without the puppet and
   the ratio multiplied into the plate. Fallback if the look is too flat: the same poses rendered in
   Blender EEVEE with a glTF puppet and PBR wood (a bigger install; only if needed).
5. **Compositing.** Puppet layer over the plate; a hand matte (uniform wall: colour key, rembg
   as the check) so the puppet emerges from behind the fist at frame 42 and passes behind the
   fingers if it ever swings up; colour, grain and softness matched to the plate.
6. **Gates and delivery.** Decode check, the flicker gate on the puppet layer, eyeball the frame
   before the drop, the drop, the taut hang, one finger move, the ending and the last frame at half
   size; `hand/out/hand-puppet.mp4` (1080×1920) + the 720 copy; `hand/CAPTION.md` (caption rules
   from CLAUDE.md); `.claude/skills/puppet-video/SKILL.md`; the mirror script; handoff rotated.

7. **The DyeAllPies Productions end vignette (about 1 s, appended after the shot).** Real
   branding, not a card: an animated logo / wordmark sting with a motion signature that the
   marionette look feeds (neon, 3D, the strings or the puppet can hand over into the mark), the
   GitHub link `github.com/DyeAllPies/dyeallpies-productions` in it, legible at reel size. There is
   no branding yet; this is its start, so build it as a reusable asset (`tools/brand/`: the
   wordmark, palette, type, the motion rules in a `BRAND.md`) and a script
   (`tools/scripts/render_brand_sting.py`) that every later export can append, not a one-off drawn
   into the puppet renderer. The push-up/pull-up exports credit "by Fable" and the GitHub box in
   their own UI; the sting replaces nothing there yet, but it is the template for it.

Iteration rule from the earlier formats applies from the first line: the sim is seconds, the
render is the cost; bake the puppet layer (RGBA + shadow) once per sim/look change and composite
in minutes.

## Research plan (agents in parallel, archive to `references/marionette/` as `01`–`07` + abstracts,
open-access texts and a CSV of the numbers, `DOWNLOADS.md` listing every file)

1. **Marionette construction and stringing.** String counts and attachment points by tradition
   (Czech, Sicilian, Burmese, the "airplane" control), what each string does (knee strings walk,
   head strings nod and turn, back string bears the weight), typical size and mass of a 30 cm
   figure, thread material, diameter, mass per metre, stretch. Output: the five-finger mapping with
   a reason, and the numbers for the model.
2. **Puppet body dynamics.** Wooden-joint types and ranges, joint damping, segment mass fractions
   (de Leva 1996 / Dempster) scaled to the figure; the drop and snap (impulsive tension, bounce),
   pendulum period and damping per swing; the marionette-simulation and marionette-robot papers
   (Yamane et al. 2003 ICRA, Chen & Egerstedt, later ones) for how they model strings and what
   parameters keep the sim stable.
3. **Slack strings.** The catenary for a thread of given length between two moving points (closed
   form), when the sag is visible at this thread mass, what a slack thread does when its anchor
   moves (swing, whip), unilateral constraints in MuJoCo tendons vs. PBD chains, rendering thin
   tubes without aliasing.
4. **Hand tracking to 3D.** MediaPipe world-landmark accuracy and depth papers, fingertip pad vs.
   landmark offset, bridging the closed fist, smoothing at 30 fps; male hand length / palm breadth
   norms (ANSUR II, NASA) as the scale fallback.
5. **Camera, light and compositing.** iPhone 14 video field of view / focal length in pixels
   (with the stabilisation crop), estimating light direction and softness from a shadow on a wall,
   the wall distance from the shadow offset, shadow-catcher compositing, matching CG to phone
   footage (colour, grain, blur).
6. **Assets and tools.** CC0 / CC-BY marionette or wooden mannequin models (Sketchfab, Poly
   Haven, Blend Swap, Smithsonian), CC0 wood textures (ambientCG, Poly Haven), licences recorded;
   MuJoCo offscreen rendering on Windows (`MUJOCO_GL`), its shadow and texture limits; pyrender
   and Blender as beauty-pass options. Half literature, half a prototype spike.
7. **The reel.** How hand-tracked CG / "AR magic" reels perform, the hook in the first second, the
   drop as the hook, looping, caption style; short.

8. **Branding and the end sting.** What a 1-second logo sting can carry at reel size (logo
   animation and "sting" conventions, ident timing, legibility of a URL in one second, safe
   areas on Instagram / YouTube Shorts UI), brand-identity foundations for a small production
   label (wordmark vs. symbol, palette derived from the neon look, type licensing: open fonts
   only), how creators brand the last second and whether it costs retention or completion rate.
   Output: three concept directions with reference frames, and the numbers (on-screen times,
   sizes) for `tools/brand/BRAND.md`.

## Dennis's decisions (2026-09-11)

1. **The puppet is a 3D mannequin marionette in a NEON style**: crystal / "lighting"-like but
   opaque, very 3D, in blue, cyan or orange (try neon first; the NVIDIA card is available if the
   render needs it). Not wood. This changes step 4: the look is an emissive, glowing figure with
   a strong specular / rim read, bloom on the plate, and the strings glow the same way; the
   shadow-catcher pass may become a light-spill pass (a neon object lights the wall) — research
   item 6 now also covers neon / emissive rendering (bloom, glow falloff, what makes it read as
   "3D" rather than flat), and MuJoCo's fixed-function renderer may not be enough: expect a
   custom shader pass (moderngl / pyrender / Blender EEVEE with bloom) for the beauty layer.
2. **Real time**, the 8.9 s as shot, 1080×1920. No slow motion.
3. **The puppet falls out of the fist**: he was holding it when the hand closed, so it drops from
   behind the hand the moment it opens. The hand and fingers need a precise matte (outline of every
   finger, sharp edge, no halo) so the puppet is occluded cleanly while it is behind the hand and
   the strings leave the fingertips without a seam. The footage is sharp enough for it. This is a
   first-class step: colour-key on the uniform wall + rembg as the cross-check, edge-refined,
   and eyeballed at 1:1 on the snap-open frames (42–54).
4. **Audio does not matter**: he will put a song over it. No clacks, no room-tone work; keep the
   source audio track in the export so the timing is preserved.
5. **The hand stays as it is**: no measuring, no painting, no alteration of the hand. Hand scale
   from the male norms (ANSUR II / NASA hand length and breadth), ranked as the one free scale in
   the model document, exactly as the camera height was in the push-up model.
7. **A DyeAllPies Productions vignette closes the video** (2026-09-11, later): an added final
   second of real branding, not a card, with the GitHub link. There is no branding yet: this is
   the start of it (pipeline step 7, research item 8).
6. **Installing is fine**: `.venv-hand` with MuJoCo, MediaPipe, OpenCV, SciPy, rembg, GLFW is
   being set up; Blender or moderngl later if the neon look needs them.
