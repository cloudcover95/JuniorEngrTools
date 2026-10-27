#!/usr/bin/env python3
"""Fillet weld shear screening CLI (stdlib only, offline).

Screens a straight fillet weld under a direct load using the throat-area
method: throat = 0.707 * leg, area = throat * length * welds,
shear stress = load / area. Compares against an allowable shear of
0.30 * electrode strength (Fexx), the common AWS-style screening value.

This is a quick screening aid, not a code-compliant design check.
Prints a plain text or JSON result. No network, no file writes, no server.

JuniorCloud LLC. Additive only.
"""
import argparse
import json
import sys

THROAT_FACTOR = 0.70710678  # equal-leg fillet: throat = leg * cos(45 deg)
ALLOW_FACTOR = 0.30         # allowable shear = 0.30 * Fexx (screening)

ELECTRODES = {  # electrode class -> Fexx in MPa (nominal)
    "E60": 414.0,
    "E70": 483.0,
    "E80": 552.0,
    "E90": 621.0,
    "E100": 689.0,
}


def screen(load_n, leg_mm, length_mm, welds=1, fexx_mpa=483.0):
    if load_n < 0:
        raise ValueError("load must be >= 0")
    if leg_mm <= 0 or length_mm <= 0:
        raise ValueError("leg and length must be > 0")
    if welds < 1:
        raise ValueError("welds must be >= 1")
    if fexx_mpa <= 0:
        raise ValueError("fexx must be > 0")
    throat = THROAT_FACTOR * leg_mm
    area = throat * length_mm * welds          # mm^2
    stress = load_n / area                      # N/mm^2 == MPa
    allow = ALLOW_FACTOR * fexx_mpa
    capacity = allow * area                     # N
    ratio = stress / allow
    min_leg = load_n / (allow * THROAT_FACTOR * length_mm * welds)
    return {
        "load_n": load_n,
        "leg_mm": leg_mm,
        "length_mm": length_mm,
        "welds": welds,
        "fexx_mpa": fexx_mpa,
        "throat_mm": round(throat, 4),
        "area_mm2": round(area, 3),
        "shear_mpa": round(stress, 3),
        "allow_mpa": round(allow, 3),
        "capacity_n": round(capacity, 1),
        "utilization": round(ratio, 4),
        "min_leg_mm": round(min_leg, 3),
        "verdict": "OK" if ratio <= 1.0 else "OVER",
    }


def build_parser():
    p = argparse.ArgumentParser(
        description="Screen a fillet weld for direct shear (throat method).")
    p.add_argument("--load", type=float, required=True, help="applied load in N")
    p.add_argument("--leg", type=float, required=True, help="weld leg size in mm")
    p.add_argument("--length", type=float, required=True,
                   help="effective weld length in mm (per weld)")
    p.add_argument("--welds", type=int, default=1,
                   help="number of identical weld lines sharing the load")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--electrode", choices=sorted(ELECTRODES), default="E70",
                   help="electrode class (default E70)")
    g.add_argument("--fexx", type=float, help="electrode strength in MPa (overrides --electrode)")
    p.add_argument("--json", action="store_true", help="print JSON")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    fexx = args.fexx if args.fexx is not None else ELECTRODES[args.electrode]
    try:
        r = screen(args.load, args.leg, args.length, args.welds, fexx)
    except ValueError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(r, indent=2, sort_keys=True))
    else:
        print("Fillet weld screen (throat method)")
        print("  throat      %.3f mm" % r["throat_mm"])
        print("  area        %.1f mm^2" % r["area_mm2"])
        print("  shear       %.2f MPa" % r["shear_mpa"])
        print("  allowable   %.2f MPa (0.30 x Fexx %.0f)" % (r["allow_mpa"], fexx))
        print("  capacity    %.0f N" % r["capacity_n"])
        print("  utilization %.3f  -> %s" % (r["utilization"], r["verdict"]))
        print("  min leg     %.2f mm for this load" % r["min_leg_mm"])
    return 0 if r["verdict"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
