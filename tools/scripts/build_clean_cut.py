"""Cut silences and rejected takes out of a practice video, producing a cleaned master.

Usage: build_clean_cut.py <video> <audio_44k.wav> <takes.json> <out_master.mp4> <out_cuts.json>

takes.json: ordered list of {"word", "take", "t0", "t1"} — exact ACOUSTIC spans of the takes to
keep (from find_speech_runs.py, not whisper's loose stamps). Optional "m0"/"m1" override the
MEASUREMENT span when it must be narrower than the kept span — e.g. a comedic cough inside a
self-censored word stays in the video but must not poison the vowel formant medians (a voiced
cough passes the voiced+loud nucleus filter). Each becomes one padded segment;
segments whose pads overlap are merged (keeping per-word spans).

The cut happens in ONE ffmpeg pass using trim/atrim + the concat FILTER. Do NOT extract
per-segment files and join them with the concat demuxer: each intermediate AAC encode loses
one ~23 ms audio frame on decode (priming), which accumulates into visible A/V drift over the
joined output (~0.2 s over 10 segments when this script did it that way). With a single
filter-graph pass, out-timeline positions are exact by construction: each word's new position
is the sum of prior segment durations plus its offset in its own segment. fps=30 (CFR) is
applied once after the concat so later PNG-sequence overlays align 1:1 with frames.

15 ms audio fades at both ends of every segment prevent clicks at the joins. F0/F1/F2 are
measured per word over its vowel nucleus (voiced frames within 15 dB of the word's peak
intensity) with Praat via parselmouth, on the ORIGINAL audio, and remapped to the new
timeline in out_cuts.json — so subtitles/overlays never need a re-transcription pass.
"""
import sys, json, subprocess, statistics
import parselmouth
from vowel_map import (WORD_VOWEL, DARK_L, TARGETS_MEN, RHOTIC_F3_MAX, match_percent,
                       vowel_distance, target_distance, dark_l_distance,
                       ending_distance, grade_of)

video, wav, takes_path, out_master, out_cuts = sys.argv[1:6]
PAD_PRE, PAD_POST = 0.15, 0.22
FPS = 30

takes = json.load(open(takes_path, encoding="utf-8"))

snd = parselmouth.Sound(wav)
pitch = snd.to_pitch(time_step=0.01, pitch_floor=75, pitch_ceiling=500)
formant = snd.to_formant_burg(time_step=0.01, max_number_of_formants=5,
                              maximum_formant=5000, window_length=0.025)
inten = snd.to_intensity(minimum_pitch=75, time_step=0.01)
DUR = snd.duration

def measure(t0, t1):
    frames = []
    t = t0
    while t <= t1:
        db, f0 = inten.get_value(t), pitch.get_value_at_time(t)
        f1, f2 = formant.get_value_at_time(1, t), formant.get_value_at_time(2, t)
        frames.append((t, db, f0, f1, f2))
        t += 0.01
    peak = max((f[1] for f in frames if f[1] == f[1]), default=None)
    nuc = [f for f in frames if all(x == x for x in f[1:]) and peak and f[1] > peak - 15]
    if not nuc:
        return None
    return {"f0": round(statistics.median(f[2] for f in nuc)),
            "f1": round(statistics.median(f[3] for f in nuc)),
            "f2": round(statistics.median(f[4] for f in nuc)),
            "nucleus_t0": round(nuc[0][0], 3), "nucleus_t1": round(nuc[-1][0], 3)}

def measure_ending_f3(t0, t1):
    """Median F3 (Hz) over voiced frames in an R-ending span — the r-coloring cue."""
    f3s, t = [], t0
    while t <= t1:
        f0, f3 = pitch.get_value_at_time(t), formant.get_value_at_time(3, t)
        if f0 == f0 and f3 == f3:
            f3s.append(f3)
        t += 0.01
    return round(statistics.median(f3s)) if f3s else None

# padded segments, merged when overlapping
merged = []
for tk in takes:
    s0, s1 = max(0, tk["t0"] - PAD_PRE), min(DUR, tk["t1"] + PAD_POST)
    # merge only a FORWARD overlap with the previous take — takes.json may be
    # deliberately out of source order (e.g. the US take of a UK/US pair plays
    # first), and a backward jump must never merge into the preceding segment
    if merged and merged[-1]["seg"][0] <= s0 < merged[-1]["seg"][1]:
        merged[-1]["seg"][1] = max(merged[-1]["seg"][1], s1)
        merged[-1]["words"].append(tk)
    else:
        merged.append({"seg": [s0, s1], "words": [tk]})

# one-pass filter graph
parts, pairs = [], []
for i, m in enumerate(merged):
    s0, s1 = m["seg"]
    d = s1 - s0
    parts.append(f"[0:v]trim=start={s0:.3f}:end={s1:.3f},setpts=PTS-STARTPTS[v{i}]")
    parts.append(f"[0:a]atrim=start={s0:.3f}:end={s1:.3f},asetpts=PTS-STARTPTS,"
                 f"afade=t=in:st=0:d=0.015,afade=t=out:st={max(0, d - 0.015):.3f}:d=0.015[a{i}]")
    pairs.append(f"[v{i}][a{i}]")
graph = ";".join(parts) + f";{''.join(pairs)}concat=n={len(merged)}:v=1:a=1[vc][a];" \
        f"[vc]fps={FPS}[v]"

subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", video,
                "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out_master],
               check=True)

# out-timeline mapping (exact: concat filter output = sum of exact segment durations)
cuts, t_out = [], 0.0
for m in merged:
    s0, s1 = m["seg"]
    for tk in m["words"]:
        word, variant = tk["word"], tk.get("variant")
        meas = measure(tk.get("m0", tk["t0"]), tk.get("m1", tk["t1"])) or {}
        if "f1" in meas and word in WORD_VOWEL:
            meas["match"] = match_percent(word, meas["f1"], meas["f2"])
        # R-ending SIDE NOTE: median F3 over the take's final rhotic/schwa span
        # ("r0"/"r1" — only takes that really end in /ə ~ ɚ/ carry one; e.g.
        # "customary" is a UK/US pair but ends in consonantal /r/+/i/, so no r-span)
        # decides r-colored vs plain. It is a verdict only, never a grade — the
        # video's focus is the studied vowel.
        if variant in ("UK", "US") and "r0" in tk:
            f3e = measure_ending_f3(tk["r0"], tk["r1"])
            if f3e:
                meas["f3_end"] = f3e
                meas["rhotic"] = f3e < RHOTIC_F3_MAX
                meas["r_out"] = [round(t_out + (tk["r0"] - s0), 3),
                                 round(t_out + (tk["r1"] - s0), 3)]
        # EVERY vowel gets a grade, stacked under the main stamp; the studied
        # (strut) vowel is always first/primary. Dark-L words are graded on F1
        # only with widened tolerance (dark /l/ coarticulates F2 away); extra
        # vowels come from the take's "vowels" spans (only Hillenbrand-referenced
        # ones — unstressed schwa has no reference); a UK/US ending's ə/ɚ is
        # graded 1-D on its F3 (the robust cue — tail F1/F2 frames are too weak).
        vowels = []
        if "f1" in meas and word in WORD_VOWEL:
            if word in DARK_L:
                meas["grade"] = grade_of(dark_l_distance(word, meas["f1"]))
                meas["grade_basis"] = "F1"
            else:
                meas["grade"] = grade_of(vowel_distance(word, meas["f1"], meas["f2"]))
            vowels.append({"ipa": WORD_VOWEL[word], "grade": meas["grade"]})
        for ev in tk.get("vowels", []):
            vm = measure(ev["m0"], ev["m1"])
            if vm and ev["ipa"] in TARGETS_MEN:
                vowels.append({"ipa": ev["ipa"], "f1": vm["f1"], "f2": vm["f2"],
                               "grade": grade_of(target_distance(ev["ipa"],
                                                                 vm["f1"], vm["f2"]))})
        if "f3_end" in meas and variant in ("UK", "US"):
            meas["ending_grade"] = grade_of(ending_distance(meas["f3_end"], variant))
            vowels.append({"ipa": "ɚ" if variant == "US" else "ə",
                           "grade": meas["ending_grade"]})
        if vowels:
            meas["vowels"] = vowels
        entry = {"word": word, "take": tk["take"],
                 **({"variant": variant} if variant else {}),
                 "word_start": round(t_out + (tk["t0"] - s0), 3),
                 "word_end": round(t_out + (tk["t1"] - s0), 3),
                 "seg_start": round(t_out, 3), "seg_end": round(t_out + (s1 - s0), 3),
                 "src": [tk["t0"], tk["t1"]], **meas}
        if "nucleus_t0" in meas:
            entry["nucleus"] = [round(t_out + (meas.pop("nucleus_t0") - s0), 3),
                                round(t_out + (meas.pop("nucleus_t1") - s0), 3)]
        m.setdefault("entries", []).append(entry)
        cuts.append(entry)
    # words whose pads merged into one segment must not share the whole display
    # window (subtitles/grades/emoji would stack) — split it at the word midpoints
    for prev, nxt in zip(m.get("entries", []), m.get("entries", [])[1:]):
        mid = round((prev["word_end"] + nxt["word_start"]) / 2, 3)
        prev["seg_end"], nxt["seg_start"] = mid, mid
    t_out += s1 - s0

json.dump(cuts, open(out_cuts, "w", encoding="utf-8"), indent=2)
print(f"master ~{t_out:.2f}s, {len(merged)} segments, {len(cuts)} words")
for c in cuts:
    print(f"  {c['word']:<9}#{c['take']}{c.get('variant','  '):>3} "
          f"out {c['word_start']:>5.2f}-{c['word_end']:<5.2f} "
          f"F0={c.get('f0','--')} F1={c.get('f1','--')} F2={c.get('f2','--')} "
          f"F3end={c.get('f3_end','--')} match={c.get('match','--')}% "
          f"grade={c.get('grade','--')}")
