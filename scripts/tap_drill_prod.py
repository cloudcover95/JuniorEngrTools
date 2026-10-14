#!/usr/bin/env python3
"""Tap drill calculator for ISO metric and Unified (UNC/UNF) threads.

Computes tap drill diameter for a target thread engagement percentage,
plus minor diameter and approximate thread height. Stdlib only.

Examples:
  python3 scripts/tap_drill_prod.py M6x1
  python3 scripts/tap_drill_prod.py 1/4-20 --engagement 65
  python3 scripts/tap_drill_prod.py M10x1.5 --json
"""
import argparse
import json
import re
import sys
from fractions import Fraction

INCH = 25.4
# H = 0.866025*P; basic thread depth (external) = 0.649519*P.
# Tap drill for X% engagement: D - 2 * (0.541266 * P) * X/100  (ISO 68-1 basic profile, 5/8 H * 0.866)
DEPTH_FACTOR = 1.082532  # 2 * 5/8 * H/P


def parse_thread(spec):
    s = spec.strip().upper().replace(" ", "")
    m = re.fullmatch(r"M(\d+(?:\.\d+)?)(?:X(\d+(?:\.\d+)?))?", s)
    if m:
        d = float(m.group(1))
        if not m.group(2):
            raise ValueError("metric spec needs pitch, e.g. M6x1")
        return {"system": "metric", "major_mm": d, "pitch_mm": float(m.group(2))}
    m = re.fullmatch(r"(#?\d+|\d+/\d+|\d+(?:\.\d+)?)-(\d+)", s)
    if m:
        size, tpi = m.group(1), int(m.group(2))
        if size.startswith("#"):
            d_in = 0.060 + 0.013 * int(size[1:])
        elif "/" in size:
            d_in = float(Fraction(size))
        else:
            d_in = float(size)
            if d_in.is_integer() and d_in <= 12 and "." not in size:
                d_in = 0.060 + 0.013 * int(d_in)  # numbered screw size
        return {"system": "unified", "major_mm": d_in * INCH, "pitch_mm": INCH / tpi, "tpi": tpi}
    raise ValueError(f"unrecognized thread spec: {spec!r}")


def calc(spec, engagement):
    if not 0 < engagement <= 100:
        raise ValueError("engagement must be in (0, 100]")
    t = parse_thread(spec)
    d, p = t["major_mm"], t["pitch_mm"]
    drill = d - DEPTH_FACTOR * p * engagement / 100.0
    minor = d - DEPTH_FACTOR * p
    return {
        "thread": spec,
        "system": t["system"],
        "major_mm": round(d, 4),
        "pitch_mm": round(p, 4),
        "engagement_pct": engagement,
        "tap_drill_mm": round(drill, 3),
        "tap_drill_in": round(drill / INCH, 4),
        "basic_minor_mm": round(minor, 3),
        "thread_height_mm": round(0.541266 * p, 4),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Tap drill calculator (ISO metric, UNC/UNF).")
    ap.add_argument("threads", nargs="+", help="thread specs, e.g. M6x1 1/4-20 #10-32")
    ap.add_argument("-e", "--engagement", type=float, default=75.0,
                    help="thread engagement percent (default 75)")
    ap.add_argument("--json", action="store_true", help="output JSON")
    a = ap.parse_args(argv)
    out, rc = [], 0
    for spec in a.threads:
        try:
            out.append(calc(spec, a.engagement))
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            rc = 2
    if a.json:
        print(json.dumps(out, indent=2))
    else:
        for r in out:
            print(f"{r['thread']:<10} drill {r['tap_drill_mm']:.3f} mm ({r['tap_drill_in']:.4f} in) "
                  f"@ {r['engagement_pct']:g}%  minor {r['basic_minor_mm']:.3f} mm")
    return rc


if __name__ == "__main__":
    sys.exit(main())
