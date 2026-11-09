"""Render an animated title card as a PNG frame sequence.

The title slides in from the left with linear motion, then holds.
Optionally the frames are assembled into a video clip with moviepy.
"""

import argparse
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PALETTE_PATH = os.path.join(HERE, "..", "assets", "palette.json")

MIN_HOLD = 2.5


def load_palette(path=PALETTE_PATH):
    """Load the default colors and fonts from the palette file."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        # Sensible fallback if the palette file is missing or broken.
        return {
            "colors": {"red": "#FF0000", "text": "#FFFFFF", "shadow": "#000000"},
            "fonts": ["Arial"],
        }


def resolve_color(value, palette):
    """Return a hex color from a palette name or pass a hex value through."""
    colors = palette.get("colors", {})
    return colors.get(value, value)


def load_font(name, size):
    """Try a font by name or path, falling back to Pillow's default font."""
    candidates = [name, name + ".ttf", name.lower().replace(" ", "") + ".ttf"]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    print(f"warning: font '{name}' not found, using default", file=sys.stderr)
    return ImageFont.load_default()


def lerp(a, b, t):
    """Linear interpolation between a and b."""
    return a + (b - a) * t


def text_size(draw, text, font):
    """Measure the rendered size of a string."""
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top


def render_frames(args, palette):
    """Draw every frame and save it to the output folder. Returns frame paths."""
    os.makedirs(args.out, exist_ok=True)

    bg = resolve_color(args.bg, palette)
    fg = resolve_color("text", palette)
    shadow = resolve_color("shadow", palette)
    font = load_font(args.font, args.size)

    slide_frames = max(1, int(round(args.slide * args.fps)))
    hold_frames = int(round(max(args.hold, MIN_HOLD) * args.fps))
    total = slide_frames + hold_frames

    # Measure once so every frame uses the same layout.
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    tw, th = text_size(probe, args.text, font)
    end_x = (args.width - tw) // 2
    start_x = -tw
    y = (args.height - th) // 2

    paths = []
    for i in range(total):
        img = Image.new("RGB", (args.width, args.height), bg)
        draw = ImageDraw.Draw(img)

        if i < slide_frames:
            t = i / max(1, slide_frames - 1)
            x = int(lerp(start_x, end_x, t))
        else:
            x = end_x

        # 1px shadow, then the text on top.
        draw.text((x + 1, y + 1), args.text, font=font, fill=shadow)
        draw.text((x, y), args.text, font=font, fill=fg)

        path = os.path.join(args.out, f"frame_{i + 1:04d}.png")
        img.save(path)
        paths.append(path)

    print(f"wrote {total} frames to {args.out}")
    return paths


def assemble(paths, fps, video_path):
    """Combine the PNG frames into a video clip with moviepy."""
    try:
        from moviepy.editor import ImageSequenceClip
    except ImportError:
        try:
            from moviepy import ImageSequenceClip
        except ImportError:
            print("moviepy is not installed; skipping video assembly", file=sys.stderr)
            return
    clip = ImageSequenceClip(paths, fps=fps)
    clip.write_videofile(video_path, fps=fps, codec="libx264", audio=False)
    clip.close()
    print(f"wrote {video_path}")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Render an animated title card.")
    parser.add_argument("--text", required=True, help="title text")
    parser.add_argument("--out", default="frames/title", help="output frame folder")
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--fps", type=int, default=12)
    parser.add_argument("--slide", type=float, default=1.0, help="slide-in seconds")
    parser.add_argument("--hold", type=float, default=MIN_HOLD, help="hold seconds")
    parser.add_argument("--size", type=int, default=120, help="font size in px")
    parser.add_argument("--font", default=None, help="font name or .ttf path")
    parser.add_argument("--bg", default="red", help="palette color name or hex")
    parser.add_argument("--video", default=None, help="optional output video path")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    palette = load_palette()
    if args.font is None:
        args.font = palette.get("fonts", ["Arial"])[0]
    paths = render_frames(args, palette)
    if args.video:
        assemble(paths, args.fps, args.video)
    return 0


if __name__ == "__main__":
    sys.exit(main())
