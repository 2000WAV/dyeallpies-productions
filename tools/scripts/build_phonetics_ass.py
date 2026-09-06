"""Build top-of-frame word + IPA subtitles (and grade stamps) from a cuts.json timeline.

Usage: build_phonetics_ass.py <cuts.json> <out.ass> <play_res_x> <play_res_y>

Per word, visible for the word's whole padded segment (no dead gaps between subtitles),
top-center within the Instagram Reels safe zone (top 220 px, left 60 px, right 144 px
avoided — see references/instagram-reels-format.md; sizes below at 1080x1920, scaled
from PlayRes):
  line 1 (Word style, 104 px): the word + take number as a superscript (take >1 only,
                               suppressed when a UK/US flag already disambiguates)
  line 2 (IPA style, 78 px):   /IPA/ in gold, studied vowel bolded; a UK/US take's
                               ending (/ə/ vs /ɚ/) teal; an XX take's wrong vowel red,
                               in narrow [brackets] (what was said, not the target)
  line 3 (Tag style, 50 px):   variant explainer ("British ending — no R → /ə/")
  grade stamp (Grade style):   color-coded letter grade at mid-right with a pop-in
                               animation. Grades come from cuts.json and always score
                               the studied vowel (see vowel_map.GRADE_BANDS).

Word→IPA (incl. per-variant) and word→vowel come from vowel_map.py. The flag/meaning
emoji are PNG overlays added by compose_reels.py, not ASS (Windows libass has no color
emoji).
"""
import sys, json
from vowel_map import WORD_VOWEL, DISPLAY_WORD, ipa_of

cuts_path, out_path, PRX, PRY = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])

SUPS = {1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵"}
sx, sy = PRX / 1080, PRY / 1920
FS_WORD, FS_IPA, FS_TAG = round(104 * sy), round(78 * sy), round(50 * sy)
M_TOP_WORD, M_TOP_IPA, M_TOP_TAG = round(230 * sy), round(370 * sy), round(478 * sy)
M_LEFT, M_RIGHT = round(60 * sx), round(144 * sx)
GRADE_X, GRADE_Y = round(860 * sx), round(600 * sy)
FS_GRADE, FS_SUB = round(120 * sy), round(34 * sy)

TEAL = r"\c&H9CC319&"          # ending highlight (#19c39c)
RED = r"\c&H3B3BD0&"           # the wrong vowel in a gag take (#d03b3b)
BLUE = r"\c&HFFB54D&"          # the studied (strut) vowel — its own color, matching
                               # the blue of its tokens on the vowel chart (#4db5ff)
GRADE_COLOR = {"A+": r"\c&H71CC2E&", "A": r"\c&H71CC2E&", "B": r"\c&H0FC4F1&",
               "C": r"\c&H227EE6&", "D": r"\c&H3C4CE7&", "F": r"\c&H2B39C0&"}
TAG_TEXT = {"UK": "British ending — no R → /ə/",
            "US": "American ending — R-colored /ɚ/",
            "XX": "that [uː] should be /ʌ/…"}
# substring of the IPA to teal-highlight for a variant take (last occurrence);
# customary's UK/US difference is the whole weak/full "-ary", not a final schwa
ENDING_HL = {"UK": "ə", "US": "ɚ",
             ("customary", "UK"): "əri", ("customary", "US"): "ɛri"}
# the offending vowel of an "XX" gag take, highlighted red
XX_HL = {"culture": "uː"}
# takes shown as narrow phonetic [brackets] — what was actually said — rather than
# the phonemic /target/: every XX gag, plus words whose measured production is
# deliberately kept as-is (Dennis's "no" is a monophthong [no], not GA /noʊ/)
BRACKET_WORDS = {"no"}

cuts = json.load(open(cuts_path, encoding="utf-8"))
multi_take = {c["word"] for c in cuts if c["take"] > 1 and not c.get("variant")}

def ts(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"

header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {PRX}
PlayResY: {PRY}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Word,Segoe UI Semibold,{FS_WORD},&H00FFFFFF,&H00FFFFFF,&H00101010,&H96000000,-1,0,0,0,100,100,0,0,1,5,2,8,{M_LEFT},{M_RIGHT},{M_TOP_WORD},1
Style: IPA,Segoe UI,{FS_IPA},&H0000D7FF,&H00FFFFFF,&H00101010,&H96000000,0,0,0,0,100,100,0,0,1,4,2,8,{M_LEFT},{M_RIGHT},{M_TOP_IPA},1
Style: Tag,Segoe UI,{FS_TAG},&H00E8E6DE,&H00FFFFFF,&H00101010,&H96000000,0,0,0,0,100,100,0,0,1,3,2,8,{M_LEFT},{M_RIGHT},{M_TOP_TAG},1
Style: Grade,Segoe UI Black,{FS_GRADE},&H00FFFFFF,&H00FFFFFF,&H00101010,&H96000000,-1,0,0,0,100,100,0,0,1,6,3,5,0,0,0,1
Style: Sub,Segoe UI,{FS_SUB},&H00E8E6DE,&H00FFFFFF,&H00101010,&H96000000,0,0,0,0,100,100,0,0,1,3,2,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Text
"""

def ipa_markup(ipa, word, variant):
    """Gold-bold the studied vowel; teal-highlight a variant take's ending;
    red-highlight the offending vowel of an XX gag take."""
    vow = WORD_VOWEL.get(word)
    # vow[0] fallback: a diphthong target over a monophthong production ([no] ~ /oʊ/)
    bold = next((v for v in (f"{vow}ː", vow, vow and vow[0]) if vow and v in ipa), None)
    i_v = ipa.find(bold) if bold else -1
    if variant == "XX":
        hl, hl_col = XX_HL.get(word), RED
    else:
        hl = (ENDING_HL.get((word, variant)) or ENDING_HL.get(variant)) \
            if variant else None
        hl_col = TEAL
    i_e = ipa.rfind(hl) if hl else -1
    if i_e >= 0 and i_e <= i_v:  # highlight must not collide with the studied vowel
        i_e = -1
    big, big_e = round(FS_IPA * 1.18), round(FS_IPA * 1.12)
    out, pos = [], 0
    if i_v >= 0:
        out += [ipa[pos:i_v], f"{{\\b1{BLUE}\\fs{big}}}{bold}{{\\b0\\c\\fs{FS_IPA}}}"]
        pos = i_v + len(bold)
    if i_e >= 0:
        out += [ipa[pos:i_e], f"{{\\b1{hl_col}\\fs{big_e}}}{hl}{{\\b0\\c\\fs{FS_IPA}}}"]
        pos = i_e + len(hl)
    return "".join(out) + ipa[pos:]

events = []
for c in cuts:
    word, take, variant = c["word"], c["take"], c.get("variant")
    t0, t1 = ts(c["seg_start"]), ts(c["seg_end"])
    ipa = ipa_of(word, variant)
    ipa_txt = ipa_markup(ipa, word, variant)
    # narrow phonetic [brackets] = what was actually said (gag takes, [no]);
    # phonemic /slashes/ = the target pronunciation
    l, r = ("[", "]") if variant == "XX" or word in BRACKET_WORDS else ("/", "/")
    sup = SUPS.get(take, "") if word in multi_take else ""
    events.append(f"Dialogue: 0,{t0},{t1},Word,,0,0,0,{DISPLAY_WORD.get(word, word)}{sup}")
    events.append(f"Dialogue: 0,{t0},{t1},IPA,,0,0,0,{l}{ipa_txt}{r}")
    if variant in TAG_TEXT:
        events.append(f"Dialogue: 0,{t0},{t1},Tag,,0,0,0,{TAG_TEXT[variant]}")
    # grades, stacked vertically: the studied vowel's stamp big on top, every
    # further graded vowel of the word ("eɪ A", ending "ɚ A+") in a smaller row
    for gi, gv in enumerate(c.get("vowels", [])):
        col = GRADE_COLOR[gv["grade"]]
        if gi == 0:
            pop = (f"{{\\an5\\pos({GRADE_X},{GRADE_Y})\\frz-8{col}\\fscx260\\fscy260"
                   f"\\t(0,140,\\fscx100\\fscy100)\\fad(60,0)}}")
            events.append(f"Dialogue: 1,{t0},{t1},Grade,,0,0,0,{pop}{gv['grade']}")
        else:
            y = GRADE_Y + round((116 + 74 * (gi - 1)) * sy)
            tag = (f"{{\\an5\\pos({GRADE_X},{y})\\b1{col}\\fs{round(56 * sy)}"
                   f"\\fad(60,0)}}")
            events.append(f"Dialogue: 1,{t0},{t1},Sub,,0,0,0,"
                          f"{tag}{gv['ipa']} {gv['grade']}")

with open(out_path, "w", encoding="utf-8-sig") as f:
    f.write(header + "\n".join(events) + "\n")
print(f"{len(events)} events -> {out_path}")
