#!/usr/bin/env python3
"""Rolling bearing L10 life calculator (ISO 281 basic rating life). Stdlib only."""
import argparse
import json
import sys


def l10_million_revs(dynamic_load_c, equivalent_load_p, bearing_type="ball"):
    if dynamic_load_c <= 0 or equivalent_load_p <= 0:
        raise ValueError("loads must be positive")
    exponent = 3.0 if bearing_type == "ball" else 10.0 / 3.0
    return (dynamic_load_c / equivalent_load_p) ** exponent


def l10_hours(l10_mrev, rpm):
    if rpm <= 0:
        raise ValueError("rpm must be positive")
    return l10_mrev * 1e6 / (60.0 * rpm)


def equivalent_load(fr, fa=0.0, x=1.0, y=0.0):
    return x * fr + y * fa


def main(argv=None):
    p = argparse.ArgumentParser(description="Bearing L10 life (ISO 281 basic rating).")
    p.add_argument("--c", type=float, default=25500.0, help="dynamic load rating C (N)")
    p.add_argument("--fr", type=float, default=3000.0, help="radial load (N)")
    p.add_argument("--fa", type=float, default=0.0, help="axial load (N)")
    p.add_argument("--x", type=float, default=1.0, help="radial factor X")
    p.add_argument("--y", type=float, default=0.0, help="axial factor Y")
    p.add_argument("--rpm", type=float, default=1800.0, help="shaft speed")
    p.add_argument("--type", choices=["ball", "roller"], default="ball")
    a = p.parse_args(argv)
    try:
        pe = equivalent_load(a.fr, a.fa, a.x, a.y)
        mrev = l10_million_revs(a.c, pe, a.type)
        hrs = l10_hours(mrev, a.rpm)
    except ValueError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    print(json.dumps({"P_N": round(pe, 3), "L10_Mrev": round(mrev, 3),
                      "L10_hours": round(hrs, 1), "type": a.type}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
