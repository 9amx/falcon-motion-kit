# creator-kit

Small set of skills and Python scripts I use for making short vertical videos.

## Skills

| Skill | What it does |
|---|---|
| `skills/short-video-maker` | Script -> voice -> clips -> captions -> export |
| `skills/motion-titles` | Animated title cards and lower thirds (Pillow frame sequences) |
| `skills/topic-research` | Picks topics from a local notes folder and drafts a script |

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r skills/short-video-maker/requirements.txt pillow
```

Copy a skill folder into your skills directory, or run the scripts directly:

```bash
python skills/topic-research/scripts/pick_topic.py --notes skills/topic-research/notes
python skills/short-video-maker/scripts/make_video.py --script script.md --clips ./clips --out out.mp4
```

## Notes

- Everything runs locally; put your own clips in `./clips` and music in `./music`.
- Tested on Python 3.10 and 3.11.
