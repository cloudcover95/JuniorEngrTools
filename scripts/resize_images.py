#!/usr/bin/env python3
"""Portrait dash crop. Pillow is operator-only, not handshake."""
from __future__ import annotations

import argparse
import os
import sys

try:
    from PIL import Image
except ImportError:
    Image = None


def resize_and_pad(image_path: str, output_path: str, target_w: int = 750, target_h: int = 1500) -> bool:
    if Image is None:
        print("Pillow missing. pip install Pillow on the operator box.")
        return False
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return False
    with Image.open(image_path) as img:
        img = img.convert("RGBA")
        scale = max(target_w / img.width, target_h / img.height)
        new_w = int(img.width * scale)
        new_h = int(img.height * scale)
        resized_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        final_img = resized_img.crop((left, top, left + target_w, top + target_h))
        final_img.save(output_path, "PNG")
    print(f"[SUCCESS] Saved: {output_path} ({target_w}x{target_h})")
    return True


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("src", nargs="?", default="image.png")
    p.add_argument("dst", nargs="?", default="image_750x1500.png")
    p.add_argument("--w", type=int, default=750)
    p.add_argument("--h", type=int, default=1500)
    a = p.parse_args()
    return 0 if resize_and_pad(a.src, a.dst, a.w, a.h) else 1


if __name__ == "__main__":
    sys.exit(main())
