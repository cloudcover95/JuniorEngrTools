#!/usr/bin/env python3
"""beam_deflection_prod.py - closed-form beam deflection / moment / shear screening.

Stdlib only. Offline. No network, no server.

Supported cases (linear-elastic, prismatic, small deflection, Euler-Bernoulli):
  ss-point   simply supported, point load P at distance a from left support
  ss-udl     simply supported, uniform load w over full span
  cant-point cantilever, point load P at free end
  cant-udl   cantilever, uniform load w over full span
  fixed-udl  fixed-fixed, uniform load w over full span
  fixed-point fixed-fixed, point load P at midspan

Unit systems:
  si : L [m], E [GPa], I [cm^4], P [kN], w [kN/m]  -> deflection mm, moment kN*m, shear kN
  us : L [ft], E [ksi], I [in^4], P [kip], w [kip/ft] -> deflection in, moment kip*ft, shear kip

Screening only. Not a substitute for a licensed engineer's design check.
"""
import argparse
import json
import math
import sys

CASES = ("ss-point", "ss-udl", "cant-point", "cant-udl", "fixed-udl", "fixed-point")


def to_base(units, L, E, I, P, w):
    """Convert inputs to N, m, Pa, m^4, N/m."""
    if units == "si":
        return L, E * 1e9, I * 1e-8, P * 1e3, w * 1e3
    # us
    ft = 0.3048
    inch = 0.0254
    kip = 4448.2216152605
    ksi = 6.894757293168e6
    return L * ft, E * ksi, I * inch ** 4, P * kip, w * kip / ft


def from_base(units, delta_m, moment_nm, shear_n):
    if units == "si":
        return delta_m * 1e3, moment_nm / 1e3, shear_n / 1e3
    kip = 4448.2216152605
    return delta_m / 0.0254, moment_nm / (kip * 0.3048), shear_n / kip


def solve(case, L, E, I, P=0.0, w=0.0, a=None):
    """Return (max_deflection_m, max_moment_Nm, max_shear_N, location_m) in base units."""
    if L <= 0 or E <= 0 or I <= 0:
        raise ValueError("L, E and I must be positive")
    EI = E * I
    if case == "ss-point":
        if a is None:
            a = L / 2.0
        if not 0 < a < L:
            raise ValueError("load position a must be strictly between supports")
        b = L - a
        # max deflection occurs in the longer segment
        if a >= b:
            x = math.sqrt((L * L - b * b) / 3.0)
            d = P * b * (L * L - b * b) ** 1.5 / (9.0 * math.sqrt(3.0) * L * EI)
        else:
            x = L - math.sqrt((L * L - a * a) / 3.0)
            d = P * a * (L * L - a * a) ** 1.5 / (9.0 * math.sqrt(3.0) * L * EI)
        m = P * a * b / L
        v = P * max(a, b) / L
        return d, m, v, x
    if case == "ss-udl":
        return 5.0 * w * L ** 4 / (384.0 * EI), w * L * L / 8.0, w * L / 2.0, L / 2.0
    if case == "cant-point":
        return P * L ** 3 / (3.0 * EI), P * L, P, L
    if case == "cant-udl":
        return w * L ** 4 / (8.0 * EI), w * L * L / 2.0, w * L, L
    if case == "fixed-udl":
        return w * L ** 4 / (384.0 * EI), w * L * L / 12.0, w * L / 2.0, L / 2.0
    if case == "fixed-point":
        return P * L ** 3 / (192.0 * EI), P * L / 8.0, P / 2.0, L / 2.0
    raise ValueError("unknown case: %s" % case)


def build_parser():
    p = argparse.ArgumentParser(
        prog="beam_deflection_prod.py",
        description="Closed-form beam deflection, max moment and shear screening (stdlib only, offline).",
        epilog="Example: beam_deflection_prod.py ss-udl --units us -L 20 -E 29000 -I 310 -w 1.2 --limit 360",
    )
    p.add_argument("case", choices=CASES, help="support/load case")
    p.add_argument("--units", choices=("si", "us"), default="si", help="unit system (default si)")
    p.add_argument("-L", "--length", type=float, required=True, help="span (m or ft)")
    p.add_argument("-E", "--modulus", type=float, required=True, help="elastic modulus (GPa or ksi)")
    p.add_argument("-I", "--inertia", type=float, required=True, help="second moment of area (cm^4 or in^4)")
    p.add_argument("-P", "--point", type=float, default=0.0, help="point load (kN or kip)")
    p.add_argument("-w", "--udl", type=float, default=0.0, help="uniform load (kN/m or kip/ft)")
    p.add_argument("-a", "--position", type=float, default=None,
                   help="ss-point load distance from left support (m or ft); default midspan")
    p.add_argument("--limit", type=float, default=360.0,
                   help="serviceability ratio L/limit to check against (default 360)")
    p.add_argument("--json", action="store_true", help="emit JSON instead of text")
    return p


def run(args):
    if args.case.endswith("point") and args.point == 0.0:
        raise ValueError("this case needs a point load -P")
    if args.case.endswith("udl") and args.udl == 0.0:
        raise ValueError("this case needs a uniform load -w")
    L, E, I, P, w = to_base(args.units, args.length, args.modulus, args.inertia, args.point, args.udl)
    a = None
    if args.position is not None:
        a = args.position * (0.3048 if args.units == "us" else 1.0)
    d, m, v, x = solve(args.case, L, E, I, P, w, a)
    d_out, m_out, v_out = from_base(args.units, d, m, v)
    allow = L / args.limit if args.limit > 0 else float("inf")
    allow_out = from_base(args.units, allow, 0.0, 0.0)[0]
    u = {"si": ("mm", "kN*m", "kN", "m"), "us": ("in", "kip*ft", "kip", "ft")}[args.units]
    x_out = x / (0.3048 if args.units == "us" else 1.0)
    ratio = (L / d) if d > 0 else float("inf")
    return {
        "case": args.case,
        "units": args.units,
        "max_deflection": round(d_out, 4),
        "deflection_unit": u[0],
        "deflection_at": round(x_out, 4),
        "length_unit": u[3],
        "max_moment": round(m_out, 4),
        "moment_unit": u[1],
        "max_shear": round(v_out, 4),
        "shear_unit": u[2],
        "span_over_deflection": round(ratio, 1) if math.isfinite(ratio) else None,
        "allowable_deflection": round(allow_out, 4),
        "limit": "L/%g" % args.limit,
        "passes": d <= allow,
        "note": "screening only; verify with a licensed engineer",
    }


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        r = run(args)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(r, indent=2))
    else:
        print("case            : %s (%s)" % (r["case"], r["units"]))
        print("max deflection  : %.4f %s at x=%.4f %s" % (r["max_deflection"], r["deflection_unit"],
                                                       r["deflection_at"], r["length_unit"]))
        print("span/deflection : %s" % r["span_over_deflection"])
        print("allowable (%s) : %.4f %s -> %s" % (r["limit"], r["allowable_deflection"],
                                                  r["deflection_unit"], "PASS" if r["passes"] else "FAIL"))
        print("max moment      : %.4f %s" % (r["max_moment"], r["moment_unit"]))
        print("max shear       : %.4f %s" % (r["max_shear"], r["shear_unit"]))
        print(r["note"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
