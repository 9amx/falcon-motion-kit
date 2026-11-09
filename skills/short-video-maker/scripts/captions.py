"""Generate an .srt caption file from a plain-text script.

Captions are split into short chunks and laid out on a fixed timeline:
each chunk is shown for CAPTION_DURATION seconds, and the whole track is
shifted by CAPTION_OFFSET seconds so text appears just after the voice.
"""

import argparse
from pathlib import Path

CAPTION_DURATION = 3.2   # seconds each caption stays on screen
CAPTION_OFFSET = 0.6     # delay applied to every caption
MAX_WORDS = 7            # words per caption chunk


def format_timestamp(seconds):
    """Convert seconds to an SRT timestamp (HH:MM:SS,mmm)."""
    millis = int(round(seconds * 1000))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def split_into_chunks(text, max_words=MAX_WORDS):
    """Split script text into caption-sized chunks of words."""
    chunks = []
    for line in text.splitlines():
        words = line.strip().split()
        for i in range(0, len(words), max_words):
            chunk = " ".join(words[i:i + max_words])
            if chunk:
                chunks.append(chunk)
    return chunks


def build_captions(chunks, duration=CAPTION_DURATION, offset=CAPTION_OFFSET):
    """Return a list of (start, end, text) tuples on a fixed timeline."""
    captions = []
    for index, chunk in enumerate(chunks):
        start = offset + index * duration
        end = start + duration
        captions.append((start, end, chunk))
    return captions


def write_srt(captions, out_path):
    """Write caption tuples to an .srt file."""
    lines = []
    for number, (start, end, text) in enumerate(captions, start=1):
        lines.append(str(number))
        lines.append(f"{format_timestamp(start)} --> {format_timestamp(end)}")
        lines.append(text)
        lines.append("")
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")


def make_captions(script_path, out_path):
    """Read a script file and write the matching .srt file."""
    text = Path(script_path).read_text(encoding="utf-8")
    captions = build_captions(split_into_chunks(text))
    write_srt(captions, out_path)
    return captions


def main():
    parser = argparse.ArgumentParser(description="Create SRT captions from a script.")
    parser.add_argument("script", help="path to the script text file")
    parser.add_argument("--out", default="captions.srt", help="output .srt path")
    args = parser.parse_args()

    captions = make_captions(args.script, args.out)
    print(f"Wrote {len(captions)} captions to {args.out}")


if __name__ == "__main__":
    main()
