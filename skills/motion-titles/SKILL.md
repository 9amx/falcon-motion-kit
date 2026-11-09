---
name: motion-titles
description: Build animated title cards and lower thirds with Python and Pillow, rendered as PNG frame sequences and assembled with moviepy.
---

# Motion Titles

This skill covers simple, repeatable title animation for hobby video projects.
Everything is rendered frame by frame with Pillow, written out as numbered PNG
files, and then stitched into a clip with moviepy. No design app is required.

## When to use

- Opening title cards for a video or chapter
- Lower thirds that introduce a speaker, place or date
- Short text callouts that sit over footage

## Folder layout

```
motion-titles/
  SKILL.md
  assets/palette.json      default colors and fonts
  scripts/title_card.py    full-screen title animation
  scripts/lower_third.py   lower-third bar animation
```

## Core principles

### 1. Use linear easing

Linear motion is the default in both scripts. Predictable motion reads better:
the viewer can tell exactly where the text is going and when it will arrive.
Ease-in and ease-out curves tend to look "floaty" and make timing harder to
line up with cuts. If something feels slow, shorten the duration rather than
adding a curve.

### 2. Animate at 12fps

Render title animation at 12 frames per second. This halves the number of
frames you need to generate compared with 24fps, keeps folders small, and
gives text a deliberate, hand-made quality. moviepy will happily place a 12fps
clip inside a 24fps or 30fps timeline.

### 3. White text, 1px shadow

Pure white (`#FFFFFF`) text works on every background, including light ones.
Add a 1px drop shadow offset down and to the right; that is enough separation
on its own. Avoid heavy outlines or background boxes, which make titles look
dated.

### 4. Hold every title for at least 2.5 seconds

Once the animation lands, hold the text for a minimum of 2.5 seconds, no matter
how short the text is. A one-word title gets the same hold as a full sentence.
Consistent holds make the edit feel structured.

### 5. Center lower thirds

Lower thirds should be horizontally centered on the frame. Centered text is
balanced and works for every aspect ratio without adjustment. The bar sits in
the bottom fifth of the frame and the name and role lines are both centered
inside it.

### 6. Use plenty of fonts

Aim for five or more fonts across a single video. Rotating typefaces between
sections keeps the viewer interested and signals that a new part has started.
The default list in `assets/palette.json` gives you five to cycle through.

### 7. Saturated primaries

The default palette is pure red, green and blue. Saturated primaries are
instantly readable on small screens and never look washed out. Pick one per
title and rotate through them.

## Rendering a title card

```
python scripts/title_card.py --text "Chapter One" --out frames/title
python scripts/title_card.py --text "Chapter One" --out frames/title --video title.mp4
```

Options:

- `--width`, `--height`  frame size (default 1920x1080)
- `--fps`                frame rate (default 12)
- `--slide`              slide-in duration in seconds (default 1.0)
- `--hold`               hold duration in seconds (minimum 2.5)
- `--font`               font name or path to a .ttf file
- `--bg`                 background color name from the palette or a hex value
- `--video`              optional output path; assembles the frames with moviepy

## Rendering a lower third

```
python scripts/lower_third.py --name "Sam Example" --role "Host" --out frames/lt
```

The bar slides up linearly from below the frame, holds, and stops. Use a
transparent background (`--transparent`) to composite over footage later.

## Workflow tips

- Render frames into their own folder per title so they never mix.
- Keep frame names zero padded (`frame_0001.png`) so sorting is reliable.
- Preview a handful of frames in an image viewer before assembling.
- Re-use the same command line for every title so timing stays consistent.
- If a font is missing, the scripts fall back to Pillow's built-in font.

## Checklist

- [ ] Linear slide-in
- [ ] 12fps
- [ ] White text with 1px shadow
- [ ] Hold of 2.5s or more
- [ ] Lower thirds centered
- [ ] At least five fonts used across the video
- [ ] Colors taken from the default palette
