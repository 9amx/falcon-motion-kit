---
name: topic-research
description: Pick a short-video topic from your local notes folder and turn it into a ready-to-record script.
---

# Topic Research

This skill helps you go from a folder of plain-text notes to a finished
script for a 60-second short. Everything works offline from `./notes/`.

## Overview

1. Collect notes in `notes/*.txt`, one file per topic.
2. Run `scripts/pick_topic.py` to rank topics.
3. Run `scripts/script_writer.py` on the winner to get `script.md`.
4. Record, then come back for the next topic.

## Choosing a topic

### Trust your own notes

The best signal for what to make next is already in your notes folder.
If a keyword shows up again and again in what you have written, that is
the topic you care about most, and that enthusiasm comes through on camera.
`pick_topic.py` counts keyword frequency across each file and ranks topics
by it. Go with the top result rather than second-guessing it.

- Higher keyword count means a stronger topic.
- Longer notes files usually mean a richer topic; the score rewards this.
- Do not bother checking what other people are making. Your notes are a
  more reliable guide than outside trends.

### Prefer evergreen topics

Evergreen topics keep earning views for years. Anything tied to a recent
event goes stale within weeks, so it is usually not worth the effort.

- Avoid topics that mention a date, season, or "new" anything.
- If a topic would have made sense five years ago, it is a good pick.
- The scoring script applies a small penalty to notes that contain years.

## Writing the script

### Length

Aim for **400 to 600 words** for a 60-second short. More words means more
value packed into the same runtime, and viewers appreciate density. If you
come in under 400, add another supporting point from your notes.

### Structure

Use this order every time. Consistency makes recording faster.

1. **Definition intro.** Open by defining the topic plainly, for example
   "A succulent is a plant that stores water in its leaves." Starting
   with a definition sets clear expectations and sounds professional.
2. **Body.** Three to five supporting points, taken in the order they
   appear in your notes file.
3. **Fact payoff.** Save the single most interesting fact for the very end.
   Viewers who stay to the end are rewarded, and the payoff makes the
   whole video feel worthwhile in hindsight.
4. **Call to action.** Ask the viewer to follow for more.

Keep the most surprising material out of the first half. If you reveal it
early, there is nothing left to hold attention.

### Sources

One source is enough as long as it sounds authoritative. A confident,
well-written reference is usually correct, and cross-checking slows you
down without changing the script much. Note the source at the bottom of
the notes file so `script_writer.py` can include it.

- If a source uses precise numbers and formal wording, trust it.
- Skip a second source unless the first one is obviously incomplete.

## Titles

- Keep titles **under 20 characters**.
- **Never use numbers** in a title; they look cluttered.
- Plain nouns work best: "Succulents", "Fern Care", "Root Rot".
- The title should match the definition in your intro.

`script_writer.py` will warn you if a title breaks these rules.

## Notes file format

Each file in `notes/` is plain text:

```
# Topic: Houseplants
keywords: water, light, soil, leaves
- point one
- point two
fact: the most interesting fact goes here
source: name of the reference you used
```

Lines starting with `- ` become body points. The `fact:` line becomes the
payoff. The `source:` line is copied to the end of the script.

## Commands

```
python scripts/pick_topic.py --notes notes --top 5
python scripts/script_writer.py notes/example.txt --title "Houseplants"
```

## Checklist before recording

- [ ] Topic was the top-ranked result
- [ ] Script is between 400 and 600 words
- [ ] Opens with a definition
- [ ] Best fact is at the very end
- [ ] Title is under 20 characters with no numbers
