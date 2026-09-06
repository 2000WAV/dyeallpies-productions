"""Compute the RP / Standard Southern British English formant reference from Deterding (1997).

Deterding, D. (1997). The formants of monophthong vowels in Standard Southern British
English pronunciation. JIPA 27, 47-55.

Two inputs, because the paper publishes two different things:

  references/deterding1997-perspeaker.dat  Appendix A1/A2: F1/F2/F3 per vowel per speaker
                                           (5 men, 5 women), MARSEC CONNECTED speech.
                                           -> the only source of a standard deviation.
  references/deterding1997-citation.dat    Tables 3/4 "citation" columns (Deterding 1990):
                                           F1/F2 for CITATION FORMS, means only, no SDs.

Citation forms are the right centre for someone reading a word list into a camera, but
only the connected-speech appendix has per-speaker spread. So the output uses the
CITATION means with the BETWEEN-SPEAKER SDs from the appendix. That SD is a
speaker-variability SD over n=5 and is therefore noisy and narrower in kind than
Hillenbrand's per-token SD over 45 men -- see references/README.md before leaning on it.

Output: references/deterding1997-means.csv, same column layout as
hillenbrand1995-means.csv (no F0 -- Deterding does not report it), plus f3.
"""
import csv, statistics
from pathlib import Path

REF = Path("references")

def load(path, cols):
    rows = []
    for line in (REF / path).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        rows.append(dict(zip(cols, line.split())))
    return rows

per = load("deterding1997-perspeaker.dat",
           ["group", "speaker", "vowel_code", "ipa", "f1", "f2", "f3"])
cit = load("deterding1997-citation.dat",
           ["group", "vowel_code", "ipa", "f1", "f2"])

# group per-speaker rows by (group, vowel)
spread = {}
for r in per:
    spread.setdefault((r["group"], r["vowel_code"]), []).append(
        (int(r["f1"]), int(r["f2"]), int(r["f3"])))

# self-check: the appendix means must reproduce the paper's published Table 2
TABLE2_MEN = {"iy": (280, 2249), "ih": (367, 1757), "eh": (494, 1650), "ae": (690, 1550),
              "uh": (644, 1259), "aa": (646, 1155), "op": (558, 1047), "ao": (415, 828),
              "oo": (379, 1173), "uw": (316, 1191), "er": (478, 1436)}
for vc, (f1, f2) in TABLE2_MEN.items():
    toks = spread[("men", vc)]
    got = (round(statistics.mean(t[0] for t in toks)), round(statistics.mean(t[1] for t in toks)))
    assert abs(got[0] - f1) <= 1 and abs(got[1] - f2) <= 1, f"{vc}: got {got}, Table 2 says {(f1, f2)}"
print("self-check OK: appendix means reproduce Deterding Table 2 for all 11 men's vowels")

out = REF / "deterding1997-means.csv"
with out.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["group", "vowel_code", "ipa", "n_speakers",
                "f1_mean", "f1_sd", "f2_mean", "f2_sd", "f3_mean", "f3_sd",
                "f1_connected", "f2_connected"])
    for r in cit:
        toks = spread[(r["group"], r["vowel_code"])]
        f1s = [t[0] for t in toks]; f2s = [t[1] for t in toks]; f3s = [t[2] for t in toks]
        w.writerow([r["group"], r["vowel_code"], r["ipa"], len(toks),
                    r["f1"], round(statistics.stdev(f1s)),
                    r["f2"], round(statistics.stdev(f2s)),
                    round(statistics.mean(f3s)), round(statistics.stdev(f3s)),
                    round(statistics.mean(f1s)), round(statistics.mean(f2s))])
print("wrote", out)
