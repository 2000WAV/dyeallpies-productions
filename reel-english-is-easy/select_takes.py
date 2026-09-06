"""Pick the best take of every word in all three frames, measure it, and grade it.

Word identity comes from transcribing each group in ISOLATION (formant-nearest matching
alone was ambiguous and produced a wrong verdict earlier). Confirmed content:
  p-frame: all 9 vowels
  b-frame: "bard" never said, "book" said twice -> 8 words; word 4 is "but", not "bud"
  h-frame: "hard" was never said -> 8 distinct words (speaker confirmed "hot" at 15 s;
           it MEASURES like /ɑː/, which is the error, not a mislabel).
           Word 2 is "hat", not "had" -- speaker confirmed, and whisper had it right.
"""
import subprocess, re, csv, json, statistics, io, sys
from pathlib import Path
import parselmouth
ROOT = str(Path(__file__).resolve().parents[1]) + "/"   # repo root
W = ROOT + "reel-english-is-easy/work/"
PY = sys.executable   # same interpreter this script runs under

FRAMES = {
 "p": ("12-words-c", [("pet","ɛ"),("pat","æ"),("part","ɑː"),("pot","ɒ"),("putt","ʌ"),
                      ("pert","ɜː"),("port","ɔː"),("pull","ʊ"),("pool","uː")]),
 "b": ("10-words-a", [("bed","ɛ"),("bad","æ"),("bod","ɒ"),("but","ʌ"),("bird","ɜː"),
                      ("bored","ɔː"),("book","ʊ"),(None,None),("boot","uː")]),
 "h": ("11-words-b", [("head","ɛ"),("hat","æ"),("hot","ɒ"),("hut","ʌ"),("hurt","ɜː"),
                      ("hoard","ɔː"),("hood","ʊ"),("who'd","uː")]),
}
SRC_OF = {"p":"12-words-c.MOV","b":"10-words-a.MOV","h":"11-words-b.MOV"}
IPA = {"pet":"pɛt","pat":"pæt","part":"pɑːt","pot":"pɒt","putt":"pʌt","pert":"pɜːt",
       "port":"pɔːt","pull":"pʊl","pool":"puːl",
       "bed":"bɛd","bad":"bæd","bod":"bɒd","but":"bʌt","bird":"bɜːd","bored":"bɔːd",
       "book":"bʊk","boot":"buːt",
       "head":"hɛd","hat":"hæt","hot":"hɒt","hard":"hɑːd","hut":"hʌt","hurt":"hɜːt","hoard":"hɔːd",
       "hood":"hʊd","who'd":"huːd"}
DARK_L = {"pull","pool"}
BEAT = 0.545750

ref = {}
for r in csv.DictReader(open(ROOT+"references/deterding1997-means.csv", encoding="utf-8")):
    if r["group"] == "men":
        ref[r["ipa"]] = (int(r["f1_mean"]), max(int(r["f1_sd"]), 40),
                         int(r["f2_mean"]), max(int(r["f2_sd"]), 80))
BANDS = [(1.0,"A+"),(1.5,"A"),(2.0,"B"),(2.5,"C"),(3.0,"D"),(4.0,"E")]
def grade(d):
    for lim,g in BANDS:
        if d <= lim: return g
    return "F"

out = {}
for tag,(stem,words) in FRAMES.items():
    txt = subprocess.run([PY, ROOT+"tools/scripts/find_speech_runs.py",
                          W+f"{stem}_44k.wav","50","0.10","0.12"],
                         capture_output=True, text=True).stdout
    runs=[]
    for ln in txt.splitlines():
        m=re.match(r"\s*([\d.]+)-\s*([\d.]+) dur=([\d.]+) peak=([\d.]+)dB voiced=([\d.]+) F0=(\d+)",ln)
        if m: runs.append(tuple(float(x) for x in m.groups()))
    groups,cur=[],[runs[0]]
    for r in runs[1:]:
        if r[0]-cur[-1][1] > 1.5: groups.append(cur); cur=[r]
        else: cur.append(r)
    groups.append(cur)
    snd = parselmouth.Sound(W+f"{stem}_44k.wav")
    fmt = snd.to_formant_burg(time_step=0.01, max_number_of_formants=5, maximum_formant=5000)
    inten = snd.to_intensity(minimum_pitch=75, time_step=0.01)
    rows=[]
    for (word,vowel),g in zip(words,groups):
        if word is None: continue
        # prefer takes that fit inside one beat; among those, clearest voicing
        picks = sorted(g, key=lambda r: (r[2] > BEAT - 0.02, -r[4], -r[3]))
        chosen=[]
        for r in picks[:2]:
            ts=[r[0]+0.01*i for i in range(max(1,int((r[1]-r[0])/0.01)))]
            pk=max((inten.get_value(t) or 0) for t in ts)
            f1s,f2s=[],[]
            for t in ts:
                iv=inten.get_value(t)
                if iv is None or iv<pk-15: continue
                a=fmt.get_value_at_time(1,t); b=fmt.get_value_at_time(2,t)
                if a==a and b==b: f1s.append(a); f2s.append(b)
            if not f1s: continue
            f1,f2=statistics.median(f1s),statistics.median(f2s)
            rf1,sd1,rf2,sd2=ref[vowel]
            d1,d2=(f1-rf1)/sd1,(f2-rf2)/sd2
            dist = abs(d1)/2 if word in DARK_L else (d1**2+d2**2)**.5
            chosen.append(dict(word=word,vowel=vowel,ipa=IPA[word],src=SRC_OF[tag],t0=round(r[0],3),f0=int(r[5]),
                               dur=round(r[2],3),f1=round(f1),f2=round(f2),
                               ref_f1=rf1,ref_f2=rf2,d1=round(d1,2),d2=round(d2,2),
                               dist=round(dist,2),grade=grade(dist),
                               dark_l=word in DARK_L))
        if chosen: rows.append(chosen[0])
    out[tag]={"stem":stem,"words":rows}
    print(f"\n=== frame {tag} ({stem}) — {len(rows)} words")
    for r in rows:
        fits="" if r["dur"]<=BEAT else "  !! longer than a beat"
        print(f"  {r['word']:7s} /{r['ipa']:5s}/ t={r['t0']:6.2f} dur={r['dur']:.3f} "
              f"F1={r['f1']:4d}({r['ref_f1']:4d}) F2={r['f2']:5d}({r['ref_f2']:5d}) "
              f"dist={r['dist']:5.2f} {r['grade']:2s}{fits}")

# "hard" was missing from the h-frame and was re-recorded on its own afterwards
snd = parselmouth.Sound(W+"13-hard_44k.wav")
fmt = snd.to_formant_burg(time_step=0.01, max_number_of_formants=5, maximum_formant=5000)
inten = snd.to_intensity(minimum_pitch=75, time_step=0.01)
r=(3.86,4.27,0.41,0,0,91)
ts=[r[0]+0.01*i for i in range(int((r[1]-r[0])/0.01))]
pk=max((inten.get_value(t) or 0) for t in ts)
f1s=[];f2s=[]
for t in ts:
    iv=inten.get_value(t)
    if iv is None or iv<pk-15: continue
    a=fmt.get_value_at_time(1,t); b=fmt.get_value_at_time(2,t)
    if a==a and b==b: f1s.append(a); f2s.append(b)
f1,f2=statistics.median(f1s),statistics.median(f2s)
rf1,sd1,rf2,sd2=ref["ɑː"]
d1,d2=(f1-rf1)/sd1,(f2-rf2)/sd2
dist=(d1**2+d2**2)**.5
hard=dict(word="hard",vowel="ɑː",ipa="hɑːd",src="13-hard.mp4",t0=r[0],dur=r[2],f0=91,
          f1=round(f1),f2=round(f2),ref_f1=rf1,ref_f2=rf2,d1=round(d1,2),d2=round(d2,2),
          dist=round(dist,2),grade=grade(dist),dark_l=False)
out["h"]["words"].insert(3, hard)
print("  + hard   /hɑːd / (re-recorded) F1=%d(%d) F2=%d(%d) dist=%.2f %s"
      % (hard["f1"], rf1, hard["f2"], rf2, hard["dist"], hard["grade"]))


json.dump(out, io.open(W+"all_takes.json","w",encoding="utf-8"), indent=1, ensure_ascii=False)
n=sum(len(v['words']) for v in out.values())
print(f"\nTOTAL {n} words = {n} beats = {n*BEAT:.2f} s")
