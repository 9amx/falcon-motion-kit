"""Render an animated lower-third bar as a PNG frame sequence.

The bar slides up from below the frame with linear motion and holds.
Name and role are centered inside the bar.
"""

import argparse
import os
import sys

from PIL import Image, ImageDraw

from title_card import MIN_HOLD, assemble, lerp, load_font, load_palette, resolve_color, text_size


def render(args, palette):
    """Draw the lower-third frames. Returns the list of frame paths."""
    os.makedirs(args.out, exist_ok=True)

    bar_color = resolve_color(args.bar, palette)
    fg = resolve_color("text", palette)
    shadow = resolve_color("shadow", palette)
    fonts = palette.get("fonts", ["Arial"])
    name_font = load_font(args.font or fonts[0], 64)
    role_font = load_font(args.font or fonts[1 % len(fonts)], 40)

    bar_h = args.height // 5
    end_y = args.height - bar_h - args.height // 20
    start_y = args.height

    slide_frames = max(1, int(round(args.slide * args.fps)))
    hold_frames = int(round(max(args.hold, MIN_HOLD) * args.fps))

    paths = []
    for i in range(slide_frames + hold_frames):
        mode = "RGBA" if args.transparent else "RGB"
        bg = (0, 0, 0, 0) if args.transparent else "#F2F2F2"
        img = Image.new(mode, (args.width, args.height), bg)
        draw = ImageDraw.Draw(img)

        t = min(1.0, i / max(1, slide_frames - 1))
        y = int(lerp(start_y, end_y, t))
        draw.rectangle([0, y, args.width, y + bar_h], fill=bar_color)

        # Centered name and role lines.
        for text, font, offset in ((args.name, name_font, 0.22), (args.role, role_font, 0.62)):
            tw, _ = text_size(draw, text, font)
            x = (args.width - tw) // 2
            ty = y + int(bar_h * offset)
            draw.text((x + 1, ty + 1), text, font=font, fill=shadow)
            draw.text((x, ty), text, font=font, fill=fg)

        path = os.path.join(args.out, f"frame_{i + 1:04d}.png")
        img.save(path)
        paths.append(path)

    print(f"wrote {len(paths)} frames to {args.out}")
    return paths


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Render an animated lower third.")
    parser.add_argument("--name", required=True, help="main line")
    parser.add_argument("--role", default="", help="second line")
    parser.add_argument("--out", default="frames/lower_third")
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--fps", type=int, default=12)
    parser.add_argument("--slide", type=float, default=0.75)
    parser.add_argument("--hold", type=float, default=MIN_HOLD)
    parser.add_argument("--font", default=None, help="override font for both lines")
    parser.add_argument("--bar", default="blue", help="palette color name or hex")
    parser.add_argument("--transparent", action="store_true")
    parser.add_argument("--video", default=None, help="optional output video path")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    paths = render(args, load_palette())
    if args.video:
        assemble(paths, args.fps, args.video)
    return 0


if __name__ == "__main__":
    sys.exit(main())
