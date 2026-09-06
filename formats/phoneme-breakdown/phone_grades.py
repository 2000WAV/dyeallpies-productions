"""Grade every aligned phone and colour it.

    python phone_grades.py <cut_voice_44k.wav> <phones.json> <timeline.json> <deterding.csv> <out phones_graded.json>

Per phone class (see references/phonemes/README.md for the sources):
  monophthong vowels   F1/F2 over the middle half of the phone vs Deterding (1997) men's
                       connected-speech means, citation SDs floored -> Mahalanobis -> grade
  diphthongs           onset (first 30 %) and offset (last 30 %) vs monophthong anchors
                       (eɪ e->ɪ, aɪ a->ɪ, aʊ a->ʊ, əʊ ->ʊ), double tolerance, averaged
  word-initial stops   voice onset time vs Lisker & Abramson (1964): b 1, d 5, g 21,
                       p 58, t 70, k 80 ms, tolerance 15 ms
  sibilants s z ʃ ʒ    spectral centre of gravity (middle half, > 500 Hz)
                       vs Haley et al. (2010) men: s/z 6300 Hz, ʃ/ʒ 4200 Hz, tolerance 900 (no pre-emphasis)
  everything else      Goodness of Pronunciation (Witt & Young 2000) from the recogniser
A GOP below -3.5 ("the recogniser heard a different phone") caps any acoustic grade at C.
"""
import sys, json, csv
import numpy as np
import parselmouth
from scipy.io import wavfile
from scipy.signal import stft

wav, phj, tlj, detcsv, outj = sys.argv[1:6]
phones = json.load(open(phj, encoding="utf-8")); tl = json.load(open(tlj, encoding="utf-8"))
LOGP = np.load(phj.replace(".json", "_logp.npy")); VINFO = json.load(open(phj.replace(".json", "_vocab.json"), encoding="utf-8"))
VOCAB = VINFO["vocab"]; FRAME = VINFO["frame"]
import os
US = {}
for r in csv.DictReader(open(os.path.join(os.path.dirname(detcsv), "hillenbrand1995-means.csv"), encoding="utf-8")):
    if r["group"] != "men": continue
    US[r["vowel_code"]] = (float(r["f1_mean"]), max(45.0, float(r["f1_sd"])), float(r["f2_mean"]), max(130.0, float(r["f2_sd"])))
# RP vowel -> nearest American reference (Hillenbrand men, citation form)
US_OF = {"iː": "iy", "ɪ": "ih", "ɛ": "eh", "æ": "ae", "ʌ": "uh", "ɑː": "ah", "ɒ": "ah", "ɔː": "aw", "ʊ": "oo", "uː": "uw", "ɜː": "er"}
# GB/US alternations the recogniser can arbitrate: RP token -> American token
ALT = {"əʊ": "oʊ", "ɒ": "ɑ", "ɑː": "æ", "ɜː": "ɚ", "ə": "ɚ", "ɔː": "ɑ"}
def heard(t0, t1, tok):
    a, b = int(t0 / FRAME), max(int(t0 / FRAME) + 1, int(t1 / FRAME))
    return float(LOGP[a:b, VOCAB[tok]].mean()) if tok in VOCAB else -99.0

REF = {}
for r in csv.DictReader(open(detcsv, encoding="utf-8")):
    if r["group"] != "men": continue
    REF[r["ipa"]] = (float(r["f1_connected"]), max(45.0, float(r["f1_sd"])), float(r["f2_connected"]), max(130.0, float(r["f2_sd"])))
REF["ɛ"] = REF.pop("ɛ")
A_OPEN = ((REF["æ"][0] + REF["ʌ"][0]) / 2, 70.0, (REF["æ"][2] + REF["ʌ"][2]) / 2, 150.0)   # RP [a], onset of aɪ / aʊ
DIPH = {"eɪ": (REF["ɛ"], REF["ɪ"]), "aɪ": (A_OPEN, REF["ɪ"]), "aʊ": (A_OPEN, REF["ʊ"]), "əʊ": (None, REF["ʊ"]), "ɔɪ": (REF["ɔː"], REF["ɪ"])}
VOT_REF = {"b": 1, "d": 5, "ɡ": 21, "p": 58, "t": 70, "k": 80}
COG_REF = {"s": 6300, "z": 6300, "ʃ": 4200, "ʒ": 4200}
BANDS = [(1.0, "A+"), (1.75, "A"), (2.5, "B"), (3.25, "C"), (4.0, "D")]
GOP_BANDS = [(-0.5, "A+"), (-1.0, "A"), (-2.0, "B"), (-3.5, "C"), (-5.0, "D")]
ORDER = ["A+", "A", "B", "C", "D", "F"]
COLOUR = {"A+": (40, 220, 130), "A": (130, 225, 90), "B": (255, 214, 92), "C": (255, 150, 60), "D": (255, 96, 70), "F": (235, 55, 55)}
def grade_d(d): return next((g for lim, g in BANDS if d <= lim), "F")
def grade_gop(g): return next((gr for lim, gr in GOP_BANDS if g >= lim), "F")
def worse(a, b): return ORDER[max(ORDER.index(a), ORDER.index(b))]

snd = parselmouth.Sound(wav); sr = int(snd.sampling_frequency)
x = snd.values[0]
pitch = snd.to_pitch(time_step=0.005, pitch_floor=75.0, pitch_ceiling=350.0)
formant = snd.to_formant_burg(time_step=0.005, max_number_of_formants=5, maximum_formant=5000.0)
intensity = snd.to_intensity(minimum_pitch=75.0, time_step=0.005)
def voiced(t):
    v = pitch.get_value_at_time(t); return v is not None and not np.isnan(v)

def formants(t0, t1):
    f1s, f2s = [], []
    for t in np.arange(t0, t1, 0.005):
        if not voiced(t): continue
        f1 = formant.get_value_at_time(1, t); f2 = formant.get_value_at_time(2, t)
        if f1 and f2 and not np.isnan(f1) and not np.isnan(f2) and 150 < f1 < 1100 and 500 < f2 < 3000: f1s.append(f1); f2s.append(f2)
    return (float(np.median(f1s)), float(np.median(f2s)), len(f1s)) if len(f1s) >= 2 else (None, None, len(f1s))

def dist(f1, f2, ref, tol=1.0):
    m1, s1, m2, s2 = ref
    return float(np.hypot((f1 - m1) / (s1 * tol), (f2 - m2) / (s2 * tol)))

def cog(t0, t1):
    a, b = int(t0 * sr), int(t1 * sr)
    seg = x[a:b]
    if len(seg) < int(0.015 * sr): return None
    f, _, Z = stft(seg, fs=sr, nperseg=min(1024, len(seg)), noverlap=0, padded=False, boundary=None)
    P = (np.abs(Z) ** 2).mean(axis=1); keep = f > 500
    return float((f[keep] * P[keep]).sum() / max(P[keep].sum(), 1e-12))

def vot(t0, t1):
    """burst = first frame after the closure where high-band (>2 kHz) energy jumps; voicing = first voiced pitch frame after it."""
    a, b = int(max(0, t0 - 0.02) * sr), int(min(len(x), (t1 + 0.12)) * sr)
    seg = x[a:b]
    if len(seg) < int(0.03 * sr): return None
    hop = int(0.002 * sr); win = int(0.005 * sr)
    from scipy.signal import butter, sosfiltfilt
    sos = butter(4, 2000, btype="high", fs=sr, output="sos")
    hi = sosfiltfilt(sos, seg)
    env = np.array([np.sqrt((hi[i:i + win] ** 2).mean() + 1e-12) for i in range(0, len(seg) - win, hop)])
    if len(env) < 5: return None
    thr = env.min() + 0.25 * (env.max() - env.min())
    idx = np.where(env > thr)[0]
    if len(idx) == 0: return None
    burst = (a + idx[0] * hop) / sr
    for t in np.arange(burst + 0.004, burst + 0.15, 0.004):
        if voiced(t): return (t - burst) * 1000.0
    return 150.0

for i, p in enumerate(phones):
    t0, t1 = p["t0"], p["t1"]; dur = t1 - t0; sym = p["tok"]
    p["gop_grade"] = grade_gop(p["gop"]); g = None; note = None
    mid0, mid1 = t0 + 0.25 * dur, t1 - 0.25 * dur
    if sym in REF:
        f1, f2, n = formants(mid0, mid1) if dur >= 0.03 else formants(t0, t1)
        if f1:
            d = dist(f1, f2, REF[sym]); g = grade_d(d); note = f"F1 {f1:.0f} F2 {f2:.0f} d={d:.2f}"
            p.update(f1=round(f1), f2=round(f2), d=round(d, 2))
    elif sym in DIPH:
        on, off = DIPH[sym]; ds = []
        if on: f1, f2, n = formants(t0, t0 + 0.3 * dur); ds.append(dist(f1, f2, on, 2.0) if f1 else None)
        f1b, f2b, n = formants(t1 - 0.3 * dur, t1); ds.append(dist(f1b, f2b, off, 2.0) if f1b else None)
        ds = [d for d in ds if d is not None]
        if ds: d = float(np.mean(ds)); g = grade_d(d); note = f"onset/offset d={d:.2f}"; p["d"] = round(d, 2)
    elif sym in VOT_REF:
        nxt = phones[i + 1] if i + 1 < len(phones) else None
        word_initial = (i == 0 or phones[i - 1]["word"] != p["word"] or phones[i - 1]["line"] != p["line"])
        before_vowel = nxt is not None and nxt["word"] == p["word"] and (nxt["tok"] in REF or nxt["tok"] in DIPH or nxt["tok"] in ("ə", "i"))
        if word_initial and before_vowel:
            v = vot(t0, t1)
            if v is not None:
                d = abs(v - VOT_REF[sym]) / 15.0; g = grade_d(d); note = f"VOT {v:.0f} ms (ref {VOT_REF[sym]})"; p["vot_ms"] = round(v)
    elif sym in COG_REF:
        c = cog(mid0, mid1) if dur >= 0.04 else cog(t0, t1)
        if c:
            d = abs(c - COG_REF[sym]) / 900.0; g = grade_d(d); note = f"CoG {c:.0f} Hz (ref {COG_REF[sym]})"; p["cog_hz"] = round(c)
    if g is None:
        g = p["gop_grade"]; note = (note or "") + f" GOP {p['gop']:.2f}"; p["basis"] = "gop"
    else:
        p["basis"] = "acoustic"
        if p["gop"] < -3.5: g = worse(g, "C"); note += f" (GOP {p['gop']:.2f} caps at C)"
    p["grade"] = g; p["colour"] = COLOUR[g]; p["note"] = note.strip()
    # accent: which side of the Atlantic does this phone sit on?
    acc = "same"; why = ""
    nxt = phones[i + 1] if i + 1 < len(phones) else None
    prv = phones[i - 1] if i > 0 else None
    if sym in ALT and (sym != "ə" or nxt is None or nxt["word"] != p["word"]) and (sym != "ɔː" or True):
        gb, us = heard(t0, t1, sym), heard(t0, t1, ALT[sym])
        if abs(gb - us) >= 0.7: acc = "GB" if gb > us else "US"; why = f"heard {sym} {gb:.1f} vs {ALT[sym]} {us:.1f}"
    if acc == "same" and sym in US_OF and p.get("f1"):
        dgb = p["d"]; dus = dist(p["f1"], p["f2"], US[US_OF[sym]])
        if abs(dgb - dus) >= 0.5: acc = "GB" if dgb < dus else "US"; why = f"d(RP) {dgb:.2f} vs d(US) {dus:.2f}"
    if sym == "t" and prv is not None and nxt is not None and prv["word"] == p["word"] == nxt["word"] and (prv["tok"] in REF or prv["tok"] in DIPH) and (nxt["tok"] in REF or nxt["tok"] in DIPH or nxt["tok"] in ("ə", "i")):
        gb, us = heard(t0, t1, "t"), heard(t0, t1, "ɾ")
        if abs(gb - us) >= 0.7: acc = "GB" if gb > us else "US"; why = f"heard t {gb:.1f} vs flap {us:.1f}"
    p["accent"] = acc; p["accent_why"] = why

# colours into the subtitle timeline: every phone becomes an ipa span
for line in tl["words"]: line["ipa_spans"] = []
for p in phones:
    tl["words"][p["line"]]["ipa_spans"].append({"start": p["start"], "end": p["end"], "sym": p["tok"], "grade": p["grade"], "colour": p["colour"]})
json.dump(tl, open(tlj, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump(phones, open(outj, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
from collections import Counter
print(Counter(p["grade"] for p in phones), Counter(p["basis"] for p in phones))
print(Counter(p["accent"] for p in phones))
for p in phones: print(f"L{p['line']} {p['tok']:>3} {p['t0']:6.2f}-{p['t1']:6.2f} {p['grade']:>2} [{p['basis']:8s}] {p['accent']:4s} {p['note']}  {p['accent_why']}")
