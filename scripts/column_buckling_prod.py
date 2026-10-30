#!/usr/bin/env python3
"""Euler / Johnson column buckling screening CLI (stdlib only, offline).

Estimates the critical buckling load of a straight column with a solid
round, hollow tube, or solid rectangular section, picking Euler or the
Johnson parabola from the slenderness ratio.  Screening use only; verify
with a qualified engineer and the governing code.

JuniorCloud LLC. Additive only. No network, no server, no sockets.
"""
import argparse
import json
import math
import sys

# Effective-length factors (theoretical) by end condition.
K_FACTORS = {
    "pinned-pinned": 1.0,
    "fixed-free": 2.0,
    "fixed-pinned": 0.699,
    "fixed-fixed": 0.5,
}

# Typical modulus (MPa) and yield (MPa) for quick picks.
MATERIALS = {
    "steel-a36": (200000.0, 250.0),
    "steel-1018": (205000.0, 370.0),
    "aluminum-6061-t6": (68900.0, 276.0),
    "stainless-304": (193000.0, 215.0),
}


def section_props(shape, d=None, di=None, b=None, h=None):
    """Return (area mm^2, least I mm^4)."""
    if shape == "round":
        if not d or d <= 0:
            raise ValueError("round needs --d > 0")
        return math.pi * d ** 2 / 4.0, math.pi * d ** 4 / 64.0
    if shape == "tube":
        if not d or di is None or d <= 0 or di < 0 or di >= d:
            raise ValueError("tube needs --d > --di >= 0")
        return (math.pi * (d ** 2 - di ** 2) / 4.0,
                math.pi * (d ** 4 - di ** 4) / 64.0)
    if shape == "rect":
        if not b or not h or b <= 0 or h <= 0:
            raise ValueError("rect needs --b > 0 and --h > 0")
        return b * h, min(b * h ** 3, h * b ** 3) / 12.0
    raise ValueError("unknown shape: %s" % shape)


def buckling(length, k, e_mpa, sy_mpa, area, inertia):
    r = math.sqrt(inertia / area)
    le = k * length
    slender = le / r
    transition = math.sqrt(2.0 * math.pi ** 2 * e_mpa / sy_mpa)
    if slender >= transition:
        mode = "euler"
        sigma_cr = math.pi ** 2 * e_mpa / slender ** 2
    else:
        mode = "johnson"
        sigma_cr = sy_mpa - (sy_mpa * slender / (2.0 * math.pi)) ** 2 / e_mpa
    return {
        "radius_of_gyration_mm": r,
        "effective_length_mm": le,
        "slenderness": slender,
        "transition_slenderness": transition,
        "mode": mode,
        "critical_stress_mpa": sigma_cr,
        "critical_load_n": sigma_cr * area,
    }


def build_parser():
    p = argparse.ArgumentParser(
        description="Column buckling screening (Euler/Johnson), units mm, MPa, N.")
    p.add_argument("--shape", choices=["round", "tube", "rect"], default="round")
    p.add_argument("--d", type=float, help="outer diameter, mm")
    p.add_argument("--di", type=float, help="tube inner diameter, mm")
    p.add_argument("--b", type=float, help="rect width, mm")
    p.add_argument("--h", type=float, help="rect height, mm")
    p.add_argument("--length", type=float, required=True, help="unbraced length, mm")
    p.add_argument("--ends", choices=sorted(K_FACTORS), default="pinned-pinned")
    p.add_argument("--k", type=float, help="override effective-length factor")
    p.add_argument("--material", choices=sorted(MATERIALS), default="steel-a36")
    p.add_argument("--e", type=float, help="override modulus, MPa")
    p.add_argument("--sy", type=float, help="override yield strength, MPa")
    p.add_argument("--load", type=float, help="applied axial load, N (for safety factor)")
    p.add_argument("--json", action="store_true", help="emit JSON")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    e_mpa, sy_mpa = MATERIALS[args.material]
    if args.e:
        e_mpa = args.e
    if args.sy:
        sy_mpa = args.sy
    k = args.k if args.k else K_FACTORS[args.ends]
    if args.length <= 0 or e_mpa <= 0 or sy_mpa <= 0 or k <= 0:
        print("error: length, E, Sy and K must be > 0", file=sys.stderr)
        return 2
    try:
        area, inertia = section_props(args.shape, args.d, args.di, args.b, args.h)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    res = buckling(args.length, k, e_mpa, sy_mpa, area, inertia)
    res.update({"area_mm2": area, "least_inertia_mm4": inertia, "k": k,
                "e_mpa": e_mpa, "sy_mpa": sy_mpa})
    if args.load:
        res["applied_load_n"] = args.load
        res["safety_factor"] = res["critical_load_n"] / args.load
    if args.json:
        print(json.dumps(res, indent=2, sort_keys=True))
    else:
        print("mode               : %s" % res["mode"])
        print("slenderness Le/r   : %.1f (transition %.1f)"
              % (res["slenderness"], res["transition_slenderness"]))
        print("critical stress    : %.1f MPa" % res["critical_stress_mpa"])
        print("critical load      : %.0f N" % res["critical_load_n"])
        if "safety_factor" in res:
            print("safety factor      : %.2f" % res["safety_factor"])
        print("screening only; verify against the governing code.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
