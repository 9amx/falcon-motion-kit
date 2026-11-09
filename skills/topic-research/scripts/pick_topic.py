#!/usr/bin/env python3
"""Rank topics in a local notes folder by keyword frequency.

Each notes file is a plain-text file in ./notes/. A file may declare its
keywords on a line such as ``keywords: water, light, soil``. The script
counts how often those keywords appear in the file, applies a few simple
adjustments and prints a ranked table.
"""

import argparse
import re
import sys
from pathlib import Path

# Words ignored when no explicit keywords line is present.
STOPWORDS = {
    "the", "and", "a", "an", "of", "to", "in", "is", "it", "for", "on",
    "with", "as", "can", "are", "be", "more", "most", "than", "that",
    "this", "when", "or", "every", "few", "top", "only", "too", "much",
}

YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")
WORD_PATTERN = re.compile(r"[a-zA-Z']+")


def parse_args():
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description="Rank topics from notes files.")
    parser.add_argument("--notes", default="notes",
                        help="folder containing .txt notes (default: notes)")
    parser.add_argument("--top", type=int, default=10,
                        help="number of results to show (default: 10)")
    parser.add_argument("--min-score", type=float, default=0.0,
                        help="hide topics scoring below this value")
    return parser.parse_args()


def read_notes(path):
    """Return the text of a notes file, or an empty string on failure."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"warning: could not read {path}: {exc}", file=sys.stderr)
        return ""


def topic_name(text, path):
    """Use the '# Topic:' header if present, otherwise the file name."""
    for line in text.splitlines():
        if line.lower().startswith("# topic:"):
            return line.split(":", 1)[1].strip()
    return path.stem.replace("_", " ").title()


def declared_keywords(text):
    """Return keywords from a 'keywords:' line, lower-cased."""
    for line in text.splitlines():
        if line.lower().startswith("keywords:"):
            raw = line.split(":", 1)[1]
            return [k.strip().lower() for k in raw.split(",") if k.strip()]
    return []


def fallback_keywords(words, limit=5):
    """Pick the most frequent non-stopwords when none are declared."""
    counts = {}
    for word in words:
        if word in STOPWORDS or len(word) < 4:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return [word for word, _ in ranked[:limit]]


def score_topic(text):
    """Compute a score and supporting stats for one notes file."""
    words = [w.lower() for w in WORD_PATTERN.findall(text)]
    keywords = declared_keywords(text) or fallback_keywords(words)

    # Count every occurrence of each keyword in the body.
    hits = sum(words.count(k) for k in keywords)
    points = sum(1 for line in text.splitlines() if line.startswith("- "))

    # Base score: keyword hits, plus a small bonus for longer notes.
    score = hits * 1.0 + points * 0.5 + len(words) / 100.0

    # Evergreen preference: notes mentioning years are penalised.
    years = len(YEAR_PATTERN.findall(text))
    score -= years * 2.0

    return {
        "score": round(max(score, 0.0), 2),
        "hits": hits,
        "points": points,
        "words": len(words),
        "keywords": keywords,
    }


def print_table(rows):
    """Print results as a simple aligned table."""
    header = f"{'#':>2}  {'Topic':<24} {'Score':>7} {'Hits':>5} {'Pts':>4} {'Words':>6}"
    print(header)
    print("-" * len(header))
    for rank, row in enumerate(rows, start=1):
        print(f"{rank:>2}  {row['topic'][:24]:<24} {row['score']:>7.2f} "
              f"{row['hits']:>5} {row['points']:>4} {row['words']:>6}")


def main():
    args = parse_args()
    notes_dir = Path(args.notes)
    if not notes_dir.is_dir():
        print(f"error: notes folder not found: {notes_dir}", file=sys.stderr)
        return 1

    rows = []
    for path in sorted(notes_dir.glob("*.txt")):
        text = read_notes(path)
        if not text.strip():
            continue
        stats = score_topic(text)
        stats["topic"] = topic_name(text, path)
        stats["file"] = str(path)
        if stats["score"] >= args.min_score:
            rows.append(stats)

    if not rows:
        print("No topics found.")
        return 0

    rows.sort(key=lambda r: r["score"], reverse=True)
    print_table(rows[: args.top])
    print(f"\nSuggested topic: {rows[0]['topic']} ({rows[0]['file']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
