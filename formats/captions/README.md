# Word-highlighted captions

Burns "viral caption" subtitles into a clip: a page of about ten words on screen, with
only the word being spoken bold and gold, advancing in sync with the audio. Timing comes
from a real speech-to-text pass over the clip's own audio; wording comes from a reference
transcript when there is one, which is more accurate than raw ASR (correct names,
spelling, no mishearings).

## Pipeline

```bash
# 1. 16 kHz mono audio
ffmpeg -y -i clip.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 clip_audio.wav
# 2. word-level timestamps (CPU whisper is slow; run it detached)
python tools/scripts/transcribe_audio.py clip_audio.wav segments.json
# 3. align the reference transcript to whisper's timing → ASS with per-word highlight events
python tools/scripts/align_transcript.py segments.json transcript.txt clip.ass
# 4. burn with the `ass` filter (reads styling from the file, unlike `subtitles` + force_style)
ffmpeg -y -i clip.mp4 -vf "ass=clip.ass" -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart clip-highlighted.mp4
ffmpeg -v error -i clip-highlighted.mp4 -f null -
```

Without a reference transcript, burn whisper's own output; the alignment step is skipped.

## How the alignment works

`align_transcript.py` maps every reference-transcript word onto the nearest whisper word's
timestamp with a word-level `difflib.SequenceMatcher`, so the timing tracks the real audio
even where the reference wording differs from what whisper heard. It emits **ASS, not
SRT**: for every page of ~10 words, one `Dialogue` event per word carrying the full page
text with only that word bold and coloured. Events on the same page do not overlap in
time, so a single highlighted word "pops" through the line. This is deliberately not
ASS's built-in `\k` karaoke fill, which highlights cumulatively. The speaker name gets its
own smaller `Name` style so it does not compete with the caption.

The reference transcript is plain text, one speaker turn per paragraph, formatted
`Speaker Name: "line..."`; wrapped lines are joined.

## Rules

- **`PlayResX/Y` in the ASS header must match the clip's real resolution**
  (`ffprobe -select_streams v:0 -show_entries stream=width,height -of csv=p=0 clip.mp4`)
  or font sizes and margins scale wrong.
- **Trim the transcript to the clip's content first.** The aligner does not detect
  out-of-range material; if the transcript covers a whole show and the clip one segment,
  the word sequences do not correspond and timing is misassigned. Spot-check the first
  and last ~10 pages against the video.
- **Censor on the transcript copy, not the audio.** Timing still runs against what was
  said; the wording is softened on a copy so the original reference survives. Two styles:
  stars keeping first and last letter (`g**p`), or a euphemism that changes the offending
  root and keeps the rest of the word.
- **Scripted comedy and game dialogue are subtitled faithfully.** In-universe crude lines
  are not sanitised unless asked; if an online transcript censored a word the audio
  clearly says, start from the uncensored word and apply the requested style on top.
- Keep the `.ass` in the working directory and pass a relative filename to the filter;
  a Windows drive-letter colon inside a filter argument needs escaping and is easy to
  get wrong.
- Single narrator? Skip the `Name` event. Plain captions instead of highlighted? Emit
  one `Dialogue` per page and drop the per-word override tags.
