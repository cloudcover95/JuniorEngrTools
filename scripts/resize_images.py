#!/usr/bin/env python3
"""Scan/title-block resize. PIL extra. Modes: crop (cover) or pad (contain)."""
from __future__ import annotations

import argparse
import os
import sys

PRESETS = {
    "portrait": (750, 1500),
    "landscape": (1500, 750),
    "dash": (1920, 1080),
    "square": (1024, 1024),
}


def resize_and_pad(image_path: str, output_path: str, target_w: int = 750, target_h: int = 1500, mode: str = "crop") -> bool:
    try:
        from PIL import Image
    except ImportError:
        print("PIL missing. pip install pillow", file=sys.stderr)
        return False
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return False
    with Image.open(image_path) as img:
        img = img.convert("RGBA")
        if mode == "pad":
            scale = min(target_w / img.width, target_h / img.height)
            new_w = max(1, int(img.width * scale))
            new_h = max(1, int(img.height * scale))
            resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", (target_w, target_h), resized.getpixel((0, 0)))
            canvas.paste(resized, ((target_w - new_w) // 2, (target_h - new_h) // 2))
            final = canvas
        else:
            scale = max(target_w / img.width, target_h / img.height)
            new_w = max(1, int(img.width * scale))
            new_h = max(1, int(img.height * scale))
            resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            left = max(0, (new_w - target_w) // 2)
            top = max(0, (new_h - target_h) // 2)
            final = resized.crop((left, top, left + target_w, top + target_h))
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        final.save(output_path, "PNG")
        print(f"[SUCCESS] {output_path} ({target_w}x{target_h}) mode={mode}")
        return True


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("src", nargs="?", default="image.png")
    p.add_argument("dst", nargs="?", default="image_750x1500.png")
    p.add_argument("--preset", choices=sorted(PRESETS), default=None)
    p.add_argument("--w", type=int, default=750)
    p.add_argument("--h", type=int, default=1500)
    p.add_argument("--mode", choices=("crop", "pad"), default="crop")
    args = p.parse_args()
    w, h = PRESETS[args.preset] if args.preset else (args.w, args.h)
    return 0 if resize_and_pad(args.src, args.dst, w, h, args.mode) else 1


if __name__ == "__main__":
    raise SystemExit(main())
