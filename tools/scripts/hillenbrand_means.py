"""Compute per-vowel mean/sd of F0/F1/F2 from Hillenbrand et al. (1995) raw data.

Input: references/hillenbrand-vowdata.dat (steady-state measurements, one token per line:
  filename dur f0 F1 F2 F3 ...; filename char1 = m/w/b/g speaker group, chars 4-5 = vowel code).
Zeros mean "could not be measured" and are excluded per-column.

Output: references/hillenbrand1995-means.csv with group,vowel,ipa,n,f0_mean,f1_mean,f1_sd,f2_mean,f2_sd
"""
import csv, re, statistics
from pathlib import Path

VOWEL_IPA = {
    "ae": "æ", "ah": "ɑ", "aw": "ɔ", "eh": "ɛ", "er": "ɝ",
    "ei": "eɪ", "ih": "ɪ", "iy": "i", "oa": "oʊ", "oo": "ʊ",
    "uh": "ʌ", "uw": "u",
}
GROUPS = {"m": "men", "w": "women", "b": "boys", "g": "girls"}

rows = {}
for line in Path("references/hillenbrand-vowdata.dat").read_text().splitlines():
    m = re.match(r"^([mwbg])(\d\d)(\w\w)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", line)
    if not m:
        continue
    grp, _, vow, dur, f0, f1, f2 = m.group(1), m.group(2), m.group(3), *map(int, m.group(4, 5, 6, 7))
    rows.setdefault((GROUPS[grp], vow), []).append((f0, f1, f2))

with open("references/hillenbrand1995-means.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["group", "vowel_code", "ipa", "n", "f0_mean", "f1_mean", "f1_sd", "f2_mean", "f2_sd"])
    for (grp, vow), toks in sorted(rows.items()):
        f0s = [t[0] for t in toks if t[0] > 0]
        f1s = [t[1] for t in toks if t[1] > 0]
        f2s = [t[2] for t in toks if t[2] > 0]
        w.writerow([grp, vow, VOWEL_IPA[vow], len(toks),
                    round(statistics.mean(f0s)), round(statistics.mean(f1s)),
                    round(statistics.stdev(f1s)), round(statistics.mean(f2s)),
                    round(statistics.stdev(f2s))])
print(Path("references/hillenbrand1995-means.csv").read_text())
