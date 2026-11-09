#!/usr/bin/env python3
"""Build a script skeleton from a single notes file.

The skeleton follows a fixed order: definition intro, body points,
fact payoff at the end, then a call to action. The result is written
to script.md (or the path given with --out).
"""

import argparse
import re
import sys
from pathlib import Path

MIN_WORDS = 400
MAX_WORDS = 600
MAX_TITLE_CHARS = 20


def parse_args():
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description="Write a script skeleton.")
    parser.add_argument("notes_file", help="path to a notes .txt file")
    parser.add_argument("--title", help="video title (defaults to topic name)")
    parser.add_argument("--out", default="script.md",
                        help="output file (default: script.md)")
    parser.add_argument("--cta", default="Follow for more.",
                        help="closing call to action")
    return parser.parse_args()


def parse_notes(text):
    """Split a notes file into topic, points, fact and source."""
    data = {"topic": "", "points": [], "fact": "", "source": ""}
    for raw in text.splitlines():
        line = raw.strip()
        lower = line.lower()
        if lower.startswith("# topic:"):
            data["topic"] = line.split(":", 1)[1].strip()
        elif line.startswith("- "):
            data["points"].append(line[2:].strip())
        elif lower.startswith("fact:"):
            data["fact"] = line.split(":", 1)[1].strip()
        elif lower.startswith("source:"):
            data["source"] = line.split(":", 1)[1].strip()
    return data


def check_title(title):
    """Return a list of warnings for a title that breaks the house rules."""
    warnings = []
    if len(title) >= MAX_TITLE_CHARS:
        warnings.append(f"title is {len(title)} characters; keep it under {MAX_TITLE_CHARS}")
    if re.search(r"\d", title):
        warnings.append("title contains a number; remove it")
    return warnings


def build_intro(topic):
    """Open with a plain definition of the topic."""
    return (f"{topic} are a subject worth understanding. "
            f"In simple terms, {topic.lower()} can be defined as follows: "
            "[write a one-sentence definition here].")


def build_body(points):
    """Turn the notes points into body paragraphs, in their original order."""
    paragraphs = []
    for point in points:
        sentence = point if point.endswith(".") else point + "."
        paragraphs.append(f"{sentence} [Expand this point with one or two sentences.]")
    return paragraphs


def build_payoff(fact):
    """The most interesting fact is saved for the end."""
    if not fact:
        return "[Add your most interesting fact here as the payoff.]"
    return f"And finally, here is the best part: {fact}"


def word_count(text):
    """Count words, ignoring markdown symbols and bracketed placeholders."""
    cleaned = re.sub(r"\[[^\]]*\]", "", text)
    return len(re.findall(r"[A-Za-z']+", cleaned))


def render(title, intro, body, payoff, cta, source):
    """Assemble the final markdown document."""
    lines = [f"# {title}", "", "## Intro", "", intro, "", "## Body", ""]
    for paragraph in body:
        lines.extend([paragraph, ""])
    lines.extend(["## Payoff", "", payoff, "", "## Call to action", "", cta, ""])
    if source:
        lines.extend(["---", f"Source: {source}", ""])
    return "\n".join(lines)


def main():
    args = parse_args()
    notes_path = Path(args.notes_file)
    try:
        text = notes_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read {notes_path}: {exc}", file=sys.stderr)
        return 1

    data = parse_notes(text)
    topic = data["topic"] or notes_path.stem.replace("_", " ").title()
    title = args.title or topic

    for warning in check_title(title):
        print(f"warning: {warning}", file=sys.stderr)

    document = render(
        title=title,
        intro=build_intro(topic),
        body=build_body(data["points"]),
        payoff=build_payoff(data["fact"]),
        cta=args.cta,
        source=data["source"],
    )

    Path(args.out).write_text(document, encoding="utf-8")

    words = word_count(document)
    print(f"Wrote {args.out} ({words} words before expansion)")
    if words < MIN_WORDS:
        print(f"note: expand to at least {MIN_WORDS} words for a 60s short")
    elif words > MAX_WORDS:
        print(f"note: trim to {MAX_WORDS} words or fewer")
    return 0


if __name__ == "__main__":
    sys.exit(main())
