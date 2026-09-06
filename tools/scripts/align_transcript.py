import json, re, sys
from difflib import SequenceMatcher

SEG_PATH = sys.argv[1]
TRANSCRIPT_PATH = sys.argv[2]
ASS_PATH = sys.argv[3]

HIGHLIGHT_COLOR = "&H0000D7FF&"   # ASS is &HBBGGRR& -> this is a vivid orange/yellow (gold)
BASE_COLOR = "&H00FFFFFF&"        # white
NAME_COLOR = "&H00C8C8C8&"        # light grey

# Many OBS vertical recordings are horizontal gameplay letterboxed into a vertical canvas
# (black bars top/bottom). Subtitles should sit just below the visible video content, not at
# the very bottom of the canvas. Find the content box with:
#   ffmpeg -i <clip> -ss <mid-point> -t 5 -vf cropdetect=24:2:0 -f null - 2>&1 | grep -o "crop=[0-9:]*" | sort | uniq -c | sort -rn | head -1
# which prints `crop=W:H:X:Y` -> content bottom edge = Y + H. Adjust below per source video.
VIDEO_CONTENT_BOTTOM = 1268  # y-pixel where visible game footage ends (1080x1920 canvas)

def norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower())

segs = json.load(open(SEG_PATH, encoding="utf-8"))
wh_words = []
for seg in segs:
    for w in seg["words"]:
        n = norm(w["word"])
        if n:
            wh_words.append((n, w["start"], w["end"]))

raw = open(TRANSCRIPT_PATH, encoding="utf-8").read()
lines = raw.split("\n")
turns = []
cur_speaker = None
cur_text = []
speaker_re = re.compile(r'^([A-Z][A-Za-z .#0-9]*):\s*"?(.*)$')
for line in lines:
    stripped = line.strip()
    if not stripped:
        continue
    m = speaker_re.match(stripped)
    if m and len(m.group(1)) < 30:
        if cur_speaker is not None:
            turns.append({"speaker": cur_speaker, "text": " ".join(cur_text)})
        cur_speaker = m.group(1)
        cur_text = [m.group(2)]
    else:
        cur_text.append(stripped)
if cur_speaker is not None:
    turns.append({"speaker": cur_speaker, "text": " ".join(cur_text)})
for t in turns:
    t["text"] = t["text"].strip().strip('"')

tr_words = []
for ti, t in enumerate(turns):
    for w in t["text"].split():
        n = norm(w)
        if n:
            tr_words.append((n, ti, w))

wh_norms = [w[0] for w in wh_words]
tr_norms = [w[0] for w in tr_words]

sm = SequenceMatcher(None, wh_norms, tr_norms, autojunk=False)
opcodes = sm.get_opcodes()

tr_time = [None] * len(tr_words)
for tag, i1, i2, j1, j2 in opcodes:
    if tag == "equal":
        for k in range(i2 - i1):
            tr_time[j1 + k] = (wh_words[i1 + k][1], wh_words[i1 + k][2])
    elif tag == "replace":
        span = i2 - i1
        n = j2 - j1
        for k in range(n):
            idx = i1 + min(span - 1, (k * span) // max(n, 1)) if span > 0 else None
            if idx is not None:
                tr_time[j1 + k] = (wh_words[idx][1], wh_words[idx][2])

n = len(tr_time)
i = 0
while i < n:
    if tr_time[i] is None:
        j = i
        while j < n and tr_time[j] is None:
            j += 1
        prev_end = tr_time[i - 1][1] if i > 0 else (tr_time[j][0] if j < n else 0.0)
        next_start = tr_time[j][0] if j < n else prev_end + 0.5 * (j - i)
        gap = j - i
        for k in range(gap):
            frac0 = k / (gap + 1)
            frac1 = (k + 1) / (gap + 1)
            tr_time[i + k] = (prev_end + frac0 * (next_start - prev_end),
                              prev_end + frac1 * (next_start - prev_end))
        i = j
    else:
        i += 1

MAX_CHARS = 42
MAX_WORDS = 10

# group into pages (same logic as before), keep per-word (raw_word, start, end)
pages = []  # each: {speaker, words:[(raw_word, start, end), ...]}
cur_turn = None
cur_words = []

def flush():
    global cur_turn, cur_words
    if cur_words:
        pages.append({"speaker": turns[cur_turn]["speaker"], "words": cur_words})
    cur_words = []

for idx, (norm_w, ti, raw_w) in enumerate(tr_words):
    st, en = tr_time[idx]
    if cur_turn is None:
        cur_turn = ti
    if ti != cur_turn:
        flush()
        cur_turn = ti
    tentative = " ".join([w[0] for w in cur_words] + [raw_w])
    if cur_words and (len(tentative) > MAX_CHARS or len(cur_words) >= MAX_WORDS):
        flush()
        cur_turn = ti
        cur_words = [(raw_w, st, en)]
    else:
        cur_words.append((raw_w, st, en))
flush()

def fmt_ts(t):
    h = int(t // 3600); t -= h * 3600
    m = int(t // 60); t -= m * 60
    s = int(t); cs = int(round((t - s) * 100))
    if cs >= 100:
        cs -= 100; s += 1
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"

HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Word,Arial,64,{BASE_COLOR},{HIGHLIGHT_COLOR},&H00000000&,&H00000000&,-1,0,0,0,100,100,0,0,1,3,0,8,40,40,{VIDEO_CONTENT_BOTTOM + 60},1
Style: Name,Arial,24,{NAME_COLOR},{NAME_COLOR},&H00000000&,&H00000000&,0,0,0,0,100,100,0,0,1,2,0,8,40,40,{VIDEO_CONTENT_BOTTOM + 20},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

events = []
for page in pages:
    words = page["words"]
    page_start = words[0][1]
    page_end = words[-1][2]
    speaker = page["speaker"]
    # one persistent name event for the whole page
    events.append(
        f"Dialogue: 0,{fmt_ts(page_start)},{fmt_ts(page_end)},Name,,0,0,0,,{speaker}"
    )
    for wi, (raw_w, st, en) in enumerate(words):
        end_t = words[wi + 1][1] if wi + 1 < len(words) else page_end
        if end_t <= st:
            end_t = st + 0.05
        parts = []
        for wj, (rw, _, _) in enumerate(words):
            if wj == wi:
                parts.append("{\\c" + HIGHLIGHT_COLOR + "\\b1}" + rw + "{\\c" + BASE_COLOR + "\\b0}")
            else:
                parts.append(rw)
        text = " ".join(parts)
        events.append(
            f"Dialogue: 1,{fmt_ts(st)},{fmt_ts(end_t)},Word,,0,0,0,,{text}"
        )

with open(ASS_PATH, "w", encoding="utf-8") as f:
    f.write(HEADER)
    f.write("\n".join(events) + "\n")

print(f"Wrote {len(pages)} pages / {len(events)} events to {ASS_PATH}")
