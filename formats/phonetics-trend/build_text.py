# -*- coding: utf-8 -*-
"""Generate the ASS overlay: title, walking claims, the turn, and the graded words.

All text goes through libass (harfbuzz + fribidi on this box) so Arabic and Persian
shape and run right-to-left correctly, Devanagari forms conjuncts, and the IPA block
renders. Sizes follow references/instagram-reels-format.md; word/IPA/grade are
deliberately oversized because each word holds the screen for one beat (546 ms).

Timings come from work/timeline.json, which is built in WHOLE FRAMES. Do not recompute
them from beat arithmetic here -- one beat is 16.3725 frames at 30 fps, and deriving
text times independently is exactly what put the captions a word ahead of the audio.
"""
import json, io
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"
BEAT = 0.545750
BAR = BEAT * 4

WHITE = "&H00FFFFFF"
GREEN, YELLOW, ORANGE, RED = "&H0050C878", "&H0000D4FF", "&H000080FF", "&H004040FF"
BLUE, AMBER, PINK = "&H00FFB54D", "&H004DC4FF", "&H00B45CFF"
GRADE_COLOUR = {"A+": GREEN, "A": GREEN, "B": YELLOW, "C": YELLOW,
                "D": ORANGE, "E": ORANGE, "F": RED}

def ts(t):
    return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"

L = []
def ev(t0, t1, style, text, layer=1):
    L.append(f"Dialogue: {layer},{ts(t0)},{ts(t1)},{style},,0,0,0,,{text}")

def pop(scale=118, ms=110):
    """Quick overshoot on entry -- the 'viral' snap."""
    return r"{\fscx%d\fscy%d\t(0,%d,\fscx100\fscy100)}" % (scale, scale, ms)

# ------------------------------------------------------------------ 1. title card
# The claim, in the languages this audience actually speaks. Spanish is dropped:
# "EL INGLÉS ES FÁCIL" reads as a near-duplicate of the Portuguese line.
TITLE = [
    ("ENGLISH IS EASY",   "Huge", 270, YELLOW),
    ("INGLÊS É FÁCIL",    "Mid",  455, WHITE),
    ("İNGİLİZCE KOLAY",   "Mid",  590, WHITE),
    ("الإنجليزية سهلة",     "Mid",  725, WHITE),
    ("انگلیسی آسان است",    "Mid",  860, WHITE),
]
T_END = BAR * 2
for i, (txt, sty, y, col) in enumerate(TITLE):
    ev(0.08 + i * 0.30, T_END, sty,
       r"%s{\pos(540,%d)\c%s\fad(140,0)}%s" % (pop(126 if i == 0 else 112), y, col, txt))

# ------------------------------------------------- 2. walking: two questions only
# One sentence per half, held for the whole half, shown in EVERY language at once.
# Simpler than the old stack of four different claims: the viewer reads one idea, and
# sees their own language in it.
w0, w_mid, w_end = BAR * 2, BAR * 4, BAR * 6

Q1 = [
    (r"IF ENGLISH IS {\c%s}SO EASY{\c%s},\NWHY DO SO MANY\N{\c%s}MISPRONOUNCE IT?" % (YELLOW, WHITE, ORANGE),
     "Ask", 92, 300),
    (r"SE O INGLÊS É TÃO FÁCIL,\NPOR QUE TANTOS ERRAM A PRONÚNCIA?",        "Tr", 62, 570),
    (r"İNGİLİZCE BU KADAR KOLAYSA,\NNEDEN BU KADAR ÇOK KİŞİ\NYANLIŞ TELAFFUZ EDİYOR?", "Tr", 62, 760),
    (r"إذا كانت الإنجليزية بهذه السهولة،\Nفلماذا يخطئ كثيرون في نطقها؟",           "Tr", 62, 950),
    (r"اگر انگلیسی این‌قدر آسان است،\Nچرا این‌همه نفر آن را غلط تلفظ می‌کنند؟",       "Tr", 62, 1110),
]
Q2 = [
    (r"WHAT IF I TOLD YOU\NTHERE IS A {\c%s}SCIENCE\N{\c%s}FOR PRONUNCIATION?" % (BLUE, BLUE),
     "Ask", 92, 300),
    (r"E SE EU TE DISSESSE QUE EXISTE\NUMA CIÊNCIA DA PRONÚNCIA?",           "Tr", 62, 570),
    (r"YA SANA TELAFFUZUN BİR BİLİMİ\NOLDUĞUNU SÖYLESEM?",                   "Tr", 62, 760),
    (r"وماذا لو قلت لك\Nإن للنطق علمًا؟",                                       "Tr", 62, 950),
    (r"اگر بگویم برای تلفظ\Nعلمی وجود دارد، چه؟",                               "Tr", 62, 1110),
]
for block, a, b in ((Q1, w0, w_mid), (Q2, w_mid, w_end)):
    for i, (txt, sty, size, y) in enumerate(block):
        col = WHITE if i == 0 else (YELLOW if i % 2 else BLUE)
        ev(a + i * 0.16, b, sty,
           r"%s{\pos(540,%d)\fs%d\c%s\fad(120,110)\t(0,2400,\fscx103\fscy103)}%s"
           % (pop(118, 130), y, size, col, txt))

# ------------------------------------------- 3. invite, then the hesitation
i0 = BAR * 6
INVITE = [
    ("LET ME SHOW YOU",      "Huge", 300, GREEN),
    ("DEIXA EU TE MOSTRAR",  "Tr",   500, WHITE),
    ("SANA GÖSTEREYİM",      "Tr",   640, YELLOW),
    ("دعني أريك",              "Tr",   780, WHITE),
    ("بگذار نشانت بدهم",       "Tr",   920, BLUE),
]
for i, (txt, sty, y, col) in enumerate(INVITE):
    ev(i0 + 0.04 + i * 0.13, i0 + BAR, sty,
       r"%s{\pos(540,%d)\c%s\fad(100,90)}%s" % (pop(120 if i == 0 else 112, 110), y, col, txt))

d0 = BAR * 7
ev(d0 + 0.04, d0 + BAR, "Huge",
   r"%s{\pos(540,330)\fad(100,80)}YOU SURE YOU\N{\c%s}WANNA KNOW?" % (pop(118), YELLOW))

# --------------------------------------------------------------------- 4. the words
tl = json.loads((WORK / "timeline.json").read_text(encoding="utf-8"))
words = tl["words"]
def frame_label(ipa):
    """First and last phoneme of what was ACTUALLY said -- "hat" is h_t, not h_d, and
    "pull" is p_l. A fixed per-group label would misstate the frame after the word
    corrections."""
    return "%s _ %s" % (ipa[0], ipa[-1])
for w in words:
    a, b = w["t_start"], w["t_end"]
    g = w["grade"]
    gc = GRADE_COLOUR[g]
    # the word: huge, white, outlined in its grade colour so the verdict reads instantly
    ev(a, b, "Word", r"%s{\pos(540,395)\3c%s\fad(45,0)}%s" % (pop(114, 90), gc, w["word"].upper()))
    # IPA with the studied vowel picked out
    ipa, v = w["ipa"], w["vowel"]
    k = ipa.find(v)
    marked = ("%s{\c%s}%s{\c%s}%s" % (ipa[:k], BLUE, v, WHITE, ipa[k+len(v):])) if k >= 0 else ipa
    ev(a, b, "Ipa", r"{\pos(540,527)\fad(45,0)}/%s/" % marked)
    ev(a, b, "Grade", r"%s{\pos(540,150)\c%s\fad(45,0)}%s" % (pop(126, 100), gc, g))
    ev(a, b, "Meas", r"{\pos(540,1533)\fad(45,0)}"
       r"{\c%s}F1 %d{\c%s}  {\c%s}F2 %d{\c%s}  Hz     target {\c&H00909090&}%d / %d"
       % (BLUE, w["f1"], WHITE, AMBER, w["f2"], WHITE, w["ref_f1"], w["ref_f2"]))
    ev(a, b, "Frame", r"{\pos(540,1601)\fad(45,0)}%s" % frame_label(w["ipa"]))

hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Huge,Segoe UI,136,{WHITE},&H00000000,&H80000000,-1,7,3,5,30,30,40,1
Style: Ask,Segoe UI,98,{WHITE},&H00000000,&H80000000,-1,7,3,5,30,30,40,1
Style: Tr,Segoe UI,62,{WHITE},&H00000000,&H80000000,-1,5,2,5,25,25,40,1
Style: Claim,Segoe UI,104,{WHITE},&H00000000,&H80000000,-1,7,3,5,30,30,40,1
Style: Mid,Segoe UI,96,{WHITE},&H00000000,&H80000000,-1,6,3,5,40,40,40,1
Style: Small,Segoe UI,56,&H00C0C0C0,&H00000000,&H80000000,0,4,2,5,40,40,40,1
Style: Word,Segoe UI,188,{WHITE},&H00000000,&H80000000,-1,9,4,5,20,20,30,1
Style: Ipa,Segoe UI,112,{WHITE},&H00000000,&H80000000,-1,7,3,5,30,30,30,1
Style: Grade,Segoe UI,210,{WHITE},&H00000000,&H80000000,-1,9,4,5,30,30,30,1
Style: Meas,Segoe UI,50,{WHITE},&H00000000,&H80000000,-1,4,2,5,30,30,30,1
Style: Frame,Segoe UI,46,&H0090C0FF,&H00000000,&H80000000,-1,4,2,5,30,30,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
io.open(WORK / "overlay.ass", "w", encoding="utf-8").write(hdr + "\n".join(L) + "\n")
print(f"wrote overlay.ass: {len(L)} events, {len(words)} words")
