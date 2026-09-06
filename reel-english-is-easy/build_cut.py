# -*- coding: utf-8 -*-
"""Build the reel cut. EVERYTHING is measured in whole frames.

Why whole frames: one beat at 109.94 BPM is 545.75 ms = 16.3725 frames at 30 fps.
An earlier build let ffmpeg's fps filter round each word segment up to 17 frames and
silence-pad the audio to match, so every word landed 20.9 ms later than the subtitle
timeline said -- 523 ms of accumulated slip by word 26. On screen that showed as the
caption for the NEXT word appearing while the previous one was still being spoken, and
the final word losing its caption entirely. So segment lengths are integers here, and
the word start frames are the single source of truth for the text and panel layers too.

Long takes are shortened by removing a slice from the MIDDLE OF THE VOWEL rather than
letting the tail be chopped, which was cutting the final /d/ off "bored", "who'd" and
others. The removed slice is rounded to a whole number of pitch periods (from the take's
measured F0) so the waveform is in phase across the join and does not click.
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC, WORK = ROOT / "originals", ROOT / "work"
FPS = 30
BEAT = 0.545750
BAR = BEAT * 4
DROP1 = BAR * 12
PREROLL = 0.08
TAIL_PAD = 0.012          # keep a little air after the final consonant

ALL = json.loads((WORK / "all_takes.json").read_text(encoding="utf-8"))

# ---- intro segments, in whole frames -------------------------------------------
intro = [
    ("01-lookup.MOV",      0.00, round(BAR * 2 * FPS), False, "fill"),
    ("@walk_fx.mp4",       0.00, round(BAR * 4 * FPS), False, None),
    ("03-invite.MOV",      0.05, round(BAR * 1 * FPS), False, None),
    ("04-doubt.MOV",       1.50, round(BAR * 1 * FPS), False, None),
]
words_frame = sum(s[2] for s in intro)

# ---- word start frames: rounded once, never accumulated ------------------------
words = [{**w, "frame": tag} for tag in ("p", "b", "h") for w in ALL[tag]["words"]]
starts = [words_frame + round(k * BEAT * FPS) for k in range(len(words) + 1)]

pieces, timeline = [], []
for k, w in enumerate(words):
    nf = starts[k + 1] - starts[k]                 # 16 or 17 frames
    avail = nf / FPS
    src_start = w["t0"] - PREROLL
    need = PREROLL + w["dur"] + TAIL_PAD
    cut = need - avail
    if cut > 0.004:
        # take out whole pitch periods from the middle of the vowel
        period = 1.0 / max(70, w.get("f0") or 100)
        cut = max(1, round(cut / period)) * period
        nfa = max(4, min(nf - 4, round((PREROLL + w["dur"] * 0.45) * FPS)))
        pieces.append((w["src"], src_start, nfa, True, None))
        pieces.append((w["src"], src_start + nfa / FPS + cut, nf - nfa, True, None))
        spliced = round(cut * 1000)
    else:
        pieces.append((w["src"], src_start, nf, True, None))
        spliced = 0
    timeline.append({**w, "n_frames": nf, "spliced_ms": spliced,
                     "t_start": round(starts[k] / FPS, 5),
                     "t_onset": round((starts[k] / FPS) + PREROLL, 5),
                     "t_end": round(starts[k + 1] / FPS, 5)})

segs = intro + pieces
(WORK / "timeline.json").write_text(json.dumps(
    {"fps": FPS, "beat": BEAT, "words_frame": words_frame,
     "words_start": round(words_frame / FPS, 5), "words": timeline},
    indent=1, ensure_ascii=False), encoding="utf-8")

def path_of(f): return str(WORK / f[1:]) if f.startswith("@") else str(SRC / f)
files = sorted({s[0] for s in segs})
idx = {f: i for i, f in enumerate(files)}

fc, vl, al = [], [], []
for n, (f, ss, nfr, keep_a, mode) in enumerate(segs):
    dur = nfr / FPS
    if mode == "fill":                       # slow a short clip to fill its slot
        sp = 3.367 / dur
        fc.append(f"[{idx[f]}:v]trim=start={ss:.6f}:duration={dur*sp:.6f},"
                  f"setpts=(PTS-STARTPTS)/{sp:.9f},scale=1080:1920:flags=lanczos,setsar=1,"
                  f"fps={FPS},trim=end_frame={nfr}[v{n}]")
    else:
        fc.append(f"[{idx[f]}:v]trim=start={ss:.6f}:duration={dur+2.0/FPS:.6f},"
                  f"setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,setsar=1,"
                  f"fps={FPS},trim=end_frame={nfr},setpts=PTS-STARTPTS[v{n}]")
    vl.append(f"[v{n}]")
    if keep_a:
        fc.append(f"[{idx[f]}:a]atrim=start={ss:.6f}:duration={dur:.6f},"
                  f"asetpts=PTS-STARTPTS,aresample=48000[a{n}]")
    else:
        fc.append(f"anullsrc=r=48000:cl=mono,atrim=duration={dur:.6f},asetpts=PTS-STARTPTS[a{n}]")
    al.append(f"[a{n}]")
fc.append("".join(v + a for v, a in zip(vl, al)) + f"concat=n={len(segs)}:v=1:a=1[vo][ao]")

out = ROOT / "out" / "base-cut.mp4"
out.parent.mkdir(exist_ok=True)
cmd = ["ffmpeg", "-y", "-v", "error", "-stats"]
for f in files: cmd += ["-i", path_of(f)]
cmd += ["-filter_complex", ";".join(fc), "-map", "[vo]", "-map", "[ao]",
        "-c:v", "h264_nvenc", "-preset", "p5", "-tune", "hq", "-rc", "vbr", "-cq", "19",
        "-b:v", "0", "-spatial-aq", "1", "-temporal-aq", "1", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", str(out)]

tot = sum(s[2] for s in segs)
(WORK / "whip_cuts.txt").write_text(
    ",".join(f"{starts[k]/FPS:.4f}" for k in range(1, len(words))))
sp = [w for w in timeline if w["spliced_ms"]]
print(f"pieces {len(segs)}  total {tot} frames = {tot/FPS:.4f} s")
print(f"words start frame {words_frame} ({words_frame/FPS:.4f} s), {len(words)} words")
print(f"song offset: start the track at {DROP1 - words_frame/FPS - PREROLL:.4f} s")
print(f"spliced {len(sp)}: " + ", ".join(f"{w['word']}-{w['spliced_ms']}ms" for w in sp))
sys.stdout.flush()
subprocess.run(cmd, check=True)
print(f"\nwrote {out}")
