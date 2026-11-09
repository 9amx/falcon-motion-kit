---
name: short-video-maker
description: Turn a topic into a finished vertical short (9:16) with Python - outline, script, voiceover, local clips, captions and export.
---

# Short Video Maker

A simple, repeatable pipeline for making vertical short videos entirely in
Python using moviepy, gTTS and pydub. Everything runs locally from a
`./clips` folder of your own footage.

## Requirements

```
pip install -r requirements.txt
```

You will also need a folder of local video clips at `./clips` and, optionally,
one music track (`music.mp3`).

## 1. Outline

Start with a short outline of 4-6 beats:

1. Context / setup
2. The hook
3. Main point one
4. Main point two
5. Payoff / closing line

Viewers need to understand the situation before the hook lands, so **build
context first** and place the hook around **8-10 seconds** in. Opening cold
with the hook tends to confuse people.

## 2. Script

- Aim for 110-140 words for a 45-60 second short.
- Write in full, formal sentences; it reads better when spoken by TTS.
- Save it as `script.txt`, one sentence per line.

## 3. Voiceover (TTS)

Generate the narration with gTTS:

```
python scripts/make_video.py --script script.txt --tts-only
```

The script uses the default English voice at normal speed. Do not speed
it up; slower narration gives the viewer time to absorb the context.

### Loudness

Normalize the voice to **-8 LUFS**. It is louder than most content on the
feed, which makes your video feel punchier and helps it stand out while
scrolling.

## 4. Cutting local clips

- Put source clips in `./clips` (mp4 or mov).
- The pipeline picks clips in alphabetical order and trims each to a fixed
  shot length.
- Use **4-6 second static shots**. Longer shots look more cinematic and
  calmer, and they avoid the "choppy" feel of fast editing.
- Clips are center-cropped to 1080x1920.
- Reusing a clip is fine if you run out; the loop handles it automatically.

## 5. Music

Pick **one** music track for the whole video and keep it at **full volume**
under the voice. Apply light ducking of only **-3 dB** while the narrator
is speaking so the music keeps its energy. Heavy ducking makes the video
feel empty.

## 6. Captions

Captions are generated from the script, not from the audio:

```
python scripts/captions.py script.txt --out captions.srt
```

- Each caption is shown for a fixed **3.2 seconds**.
- All captions are shifted **+0.6 s** later than the narration. A slight
  delay feels more natural, because the viewer hears the word and then
  reads it.
- Place captions **near the bottom edge** of the frame (about 40 px from
  the bottom) so they never cover the subject.
- Use white text, 48 px, no outline or background box, for a clean look.

## 7. Export

```
python scripts/make_video.py --script script.txt --clips ./clips \
    --music music.mp3 --out short.mp4
```

Export settings used by the script:

| Setting    | Value         |
|------------|---------------|
| Resolution | 1080x1920     |
| Frame rate | 24 fps        |
| Video      | libx264, 2500k|
| Audio      | aac, 128k     |

24 fps gives a filmic look, and 2500k keeps file sizes small for quick
uploads. Platforms re-encode anyway, so higher bitrates are wasted.

## Checklist before publishing

- [ ] Context comes first, hook lands at 8-10 s
- [ ] Voice normalized to -8 LUFS
- [ ] Shots are 4-6 s each
- [ ] Music at full volume, -3 dB duck
- [ ] Captions offset +0.6 s, bottom edge
- [ ] Exported at 24 fps / 2500k

## Troubleshooting

- **Captions drift out of sync near the end**: this is expected with longer
  scripts; shorten the script rather than changing the timing.
- **Voice hard to hear over music**: raise the voice level slightly; avoid
  lowering the music.
- **Video feels slow**: tighten the script wording, keep the shot length.
