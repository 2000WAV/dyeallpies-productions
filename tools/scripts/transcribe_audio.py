import sys, json
from faster_whisper import WhisperModel

audio_path = sys.argv[1]
out_path = sys.argv[2]

model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe(audio_path, word_timestamps=True, vad_filter=True)

result = []
for seg in segments:
    words = [{"start": w.start, "end": w.end, "word": w.word, "prob": w.probability} for w in (seg.words or [])]
    result.append({"start": seg.start, "end": seg.end, "text": seg.text, "words": words})
    print(f"[{seg.start:.2f}-{seg.end:.2f}] {seg.text}", flush=True)

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
