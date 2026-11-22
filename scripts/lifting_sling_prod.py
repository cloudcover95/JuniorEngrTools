#!/usr/bin/env python3
"""Lifting sling tension calculator (stdlib only, offline).

Computes per-leg tension for a multi-leg sling from load, leg count and the
sling angle measured from horizontal, plus the load factor 1/sin(angle).
"""
import argparse
import math
import sys


def sling_tension(load, legs, angle_deg):
    if load <= 0:
        raise ValueError("load must be > 0")
    if legs < 1:
        raise ValueError("legs must be >= 1")
    if not 0 < angle_deg <= 90:
        raise ValueError("angle must be in (0, 90] degrees from horizontal")
    factor = 1.0 / math.sin(math.radians(angle_deg))
    tension = load / legs * factor
    return {"load": load, "legs": legs, "angle_deg": angle_deg,
            "load_factor": factor, "leg_tension": tension}


def main(argv=None):
    p = argparse.ArgumentParser(description="Per-leg lifting sling tension (offline).")
    p.add_argument("--load", type=float, help="load weight (any force unit)")
    p.add_argument("--legs", type=int, default=2, help="number of legs (default 2)")
    p.add_argument("--angle", type=float, default=60.0, help="angle from horizontal, degrees (default 60)")
    p.add_argument("--rated", type=float, help="optional rated capacity per leg")
    p.add_argument("--selftest", action="store_true", help="run a built-in check")
    a = p.parse_args(argv)
    if a.selftest:
        r = sling_tension(1000.0, 2, 30.0)
        assert abs(r["leg_tension"] - 1000.0) < 1e-6
        r = sling_tension(1000.0, 2, 90.0)
        assert abs(r["leg_tension"] - 500.0) < 1e-6
        print("selftest ok")
        return 0
    if a.load is None:
        p.error("--load is required")
    try:
        r = sling_tension(a.load, a.legs, a.angle)
    except ValueError as e:
        print("error:", e, file=sys.stderr)
        return 2
    print("load factor : %.3f" % r["load_factor"])
    print("leg tension : %.2f" % r["leg_tension"])
    if a.rated is not None:
        ok = r["leg_tension"] <= a.rated
        print("rated check : %s (%.1f%% of rating)" % ("PASS" if ok else "FAIL", 100 * r["leg_tension"] / a.rated))
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
