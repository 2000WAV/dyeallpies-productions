"""Phone-level forced alignment + Goodness of Pronunciation for the promo reel.

    python align_phones.py <cut_voice_44k.wav> <timeline.json> <out phones.json>

Model: facebook/wav2vec2-lv-60-espeak-cv-ft (wav2vec2 large fine-tuned on Common Voice
espeak phoneme transcriptions, 392 IPA-ish tokens, 20 ms frames). The RP IPA lines in
timeline.json are mapped to the model's tokens, torchaudio.functional.forced_align gives
every phone its frame span, and each phone gets a GOP score (Witt & Young 2000): mean over
its frames of log p(intended phone) - log p(best phone), i.e. 0 = the recogniser is sure it
heard exactly that phone, more negative = it heard something else.
"""
import sys, json, re
import numpy as np, torch, torchaudio
import torchaudio.functional as F
from transformers import Wav2Vec2ForCTC, Wav2Vec2FeatureExtractor
from huggingface_hub import hf_hub_download

wav, tlj, outj = sys.argv[1:4]
NAME = "facebook/wav2vec2-lv-60-espeak-cv-ft"
fe = Wav2Vec2FeatureExtractor.from_pretrained(NAME)
model = Wav2Vec2ForCTC.from_pretrained(NAME).eval()
vocab = json.load(open(hf_hub_download(NAME, "vocab.json"), encoding="utf-8"))
inv = {v: k for k, v in vocab.items()}

# RP subtitle symbol -> model token (espeak English conventions)
MAP = {"e": "ɛ", "r": "ɹ", "g": "ɡ"}
# only English phone tokens may match; the vocab also holds 'th', 'ts', 'eɑ'... from other languages
ALLOWED = {"iː","ɪ","ɛ","æ","ʌ","ɑː","ɒ","ɔː","ʊ","uː","ɜː","ə","eɪ","aɪ","aʊ","əʊ","ɔɪ","iə","eə","ʊə","i",
           "p","b","t","d","k","ɡ","tʃ","dʒ","f","v","θ","ð","s","z","ʃ","ʒ","h","m","n","ŋ","l","ɹ","j","w"}
assert ALLOWED <= set(vocab), ALLOWED - set(vocab)
def tokenize(ipa_word):
    """Greedy longest-match over the English tokens after stripping stress / syllable marks."""
    s = re.sub(r"[ˈˌ.|]", "", ipa_word)
    out = []; i = 0
    while i < len(s):
        if s.startswith("iəʊ", i):            # happY-i + GOAT, not the NEAR diphthong
            out.append((i, i + 1, "i")); i += 1; continue
        for L in (2, 1):
            if len(s[i:i + L]) < L: continue
            sub = MAP.get(s[i:i + L], s[i:i + L])
            if sub in ALLOWED: out.append((i, i + L, sub)); i += L; break
        else:
            raise ValueError(f"no token for {s[i:]!r} in {ipa_word!r}")
    return out

tl = json.load(open(tlj, encoding="utf-8"))
from scipy.io import wavfile
sr, xa = wavfile.read(wav)
if xa.ndim > 1: xa = xa.mean(axis=1)
x = torch.tensor(xa.astype(np.float32) / 32768.0)
x = torchaudio.functional.resample(x, sr, 16000)
with torch.no_grad():
    inp = fe(x.numpy(), sampling_rate=16000, return_tensors="pt")
    logits = model(inp.input_values).logits[0]          # (T, V)
logp = torch.log_softmax(logits, dim=-1)
T = logp.shape[0]; dur = len(x) / 16000.0; frame = dur / T
print(f"{T} frames, {frame*1000:.1f} ms each, {dur:.2f} s")

# one token sequence for the whole cut; remember which (line, word, char span) each token is
seq = []; meta = []
for li, line in enumerate(tl["words"]):
    ipa_words = [w for w in line["ipa"].split(" ") if w != "|"]
    off = 0
    for wi, iw in enumerate(ipa_words):
        for a, b, tok in tokenize(iw):
            # char offsets in the full IPA line: account for stripped marks before position a
            raw = iw
            # map stripped index back to raw index
            keep = [i for i, ch in enumerate(raw) if ch not in "ˈˌ.|"]
            ra, rb = keep[a], keep[b - 1] + 1
            seq.append(vocab[tok]); meta.append({"line": li, "word": wi, "start": line["ipa"].index(iw, off) + ra, "end": line["ipa"].index(iw, off) + rb, "tok": tok})
        off = line["ipa"].index(iw, off) + len(iw)
targets = torch.tensor([seq], dtype=torch.int32)
ali, scores = F.forced_align(logp.unsqueeze(0), targets, blank=vocab["<pad>"])
ali = ali[0]; scores = scores[0].exp()
spans = F.merge_tokens(ali, scores, blank=vocab["<pad>"])
assert len(spans) == len(seq), (len(spans), len(seq))
best = logp.max(dim=-1).values
phones = []
for m, sp in zip(meta, spans):
    f0, f1 = sp.start, sp.end
    tok_id = vocab[m["tok"]]
    gop = float((logp[f0:f1, tok_id] - best[f0:f1]).mean())
    phones.append({**m, "t0": round(f0 * frame, 3), "t1": round(f1 * frame, 3), "gop": round(gop, 2),
                   "p": round(float(logp[f0:f1, tok_id].exp().mean()), 3)})
# CTC alignments are peaky: a token owns a few frames and blanks fill the rest. Give every
# phone the blank frames after it, up to the next phone's start (inside a word always; across
# a word gap only if the gap is short), so the spans tile the speech.
for a, b in zip(phones, phones[1:]):
    same_word = a["line"] == b["line"] and a["word"] == b["word"]
    gap = b["t0"] - a["t1"]
    if same_word or gap < 0.12: a["t1"] = b["t0"]
    elif gap < 0.5: a["t1"] = round(a["t1"] + min(0.08, gap * 0.5), 3)
    else: a["t1"] = round(a["t1"] + 0.08, 3)
phones[-1]["t1"] = round(phones[-1]["t1"] + 0.08, 3)
json.dump(phones, open(outj, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
np.save(outj.replace(".json", "_logp.npy"), logp.numpy())
json.dump({"vocab": vocab, "frame": frame}, open(outj.replace(".json", "_vocab.json"), "w", encoding="utf-8"))
for p in phones:
    print(f"L{p['line']} w{p['word']} {p['tok']:>3} {p['t0']:6.2f}-{p['t1']:6.2f} gop={p['gop']:6.2f} p={p['p']:.2f}")
