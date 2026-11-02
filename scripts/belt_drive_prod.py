#!/usr/bin/env python3
"""Belt drive screening CLI (open belt, two pulleys).

Computes pitch length, small-pulley wrap angle, speed ratio, driven speed and
belt speed. Stdlib only, offline, no network, no sockets.
JuniorCloud LLC. Additive tool for JuniorEngrTools.

Example:
    python3 scripts/belt_drive_prod.py --d1 100 --d2 250 --center 500 --rpm1 1750
"""
import argparse
import json
import math
import sys


def belt_drive(d1, d2, center, rpm1):
    if d1 <= 0 or d2 <= 0 or center <= 0:
        raise ValueError("diameters and center distance must be positive")
    small, large = min(d1, d2), max(d1, d2)
    if center <= (large - small) / 2.0:
        raise ValueError("center distance too short for these pulleys")
    # Exact open-belt length
    phi = math.asin((large - small) / (2.0 * center))
    length = (2.0 * center * math.cos(phi)
              + math.pi * (large + small) / 2.0
              + phi * (large - small))
    wrap_small_deg = math.degrees(math.pi - 2.0 * phi)
    ratio = d2 / d1
    rpm2 = rpm1 / ratio if rpm1 is not None else None
    belt_speed = (math.pi * d1 * rpm1 / 60000.0) if rpm1 is not None else None
    flags = []
    if wrap_small_deg < 120.0:
        flags.append("wrap below 120 deg: consider idler or longer center")
    if center < large:
        flags.append("center shorter than large pulley diameter")
    if center > 3.0 * (d1 + d2):
        flags.append("center over 3x(d1+d2): belt whip risk")
    if belt_speed is not None and belt_speed > 30.0:
        flags.append("belt speed over 30 m/s: check belt rating")
    return {
        "d1_mm": d1, "d2_mm": d2, "center_mm": center,
        "belt_length_mm": round(length, 2),
        "wrap_small_deg": round(wrap_small_deg, 2),
        "speed_ratio": round(ratio, 4),
        "rpm1": rpm1,
        "rpm2": round(rpm2, 2) if rpm2 is not None else None,
        "belt_speed_m_s": round(belt_speed, 3) if belt_speed is not None else None,
        "flags": flags,
        "status": "ok" if not flags else "review",
    }


def main(argv=None):
    p = argparse.ArgumentParser(description="Open belt drive screening (stdlib, offline).")
    p.add_argument("--d1", type=float, required=True, help="driver pulley pitch diameter, mm")
    p.add_argument("--d2", type=float, required=True, help="driven pulley pitch diameter, mm")
    p.add_argument("--center", type=float, required=True, help="center distance, mm")
    p.add_argument("--rpm1", type=float, default=None, help="driver speed, rpm (optional)")
    p.add_argument("--json", action="store_true", help="print JSON")
    a = p.parse_args(argv)
    try:
        r = belt_drive(a.d1, a.d2, a.center, a.rpm1)
    except ValueError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        for k, v in r.items():
            print("%-16s %s" % (k, v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
