#!/usr/bin/env python3
"""Thin-walled pressure vessel screening CLI (stdlib only, offline).

Hoop and longitudinal membrane stress for a closed cylinder or sphere,
plus a von Mises equivalent and optional minimum-thickness sizing.
Thin-wall screening assumes t/r is small (flagged above 0.1) and that
radial stress is negligible. No nozzles, welds, fatigue, or code cases.

JuniorCloud LLC. Additive, no network, no server.
"""
import argparse
import json
import math
import sys

# name: (yield strength [MPa], notes unused beyond lookup)
MATERIALS = {
    "steel_1018": 370.0,
    "steel_sa516": 260.0,
    "stainless_304": 215.0,
    "aluminum_6061": 276.0,
    "brass_360": 125.0,
    "titanium_6al4v": 880.0,
}


def cylinder_stress(p_mpa, r_mm, t_mm):
    if p_mpa < 0:
        raise ValueError("pressure must be >= 0")
    if r_mm <= 0 or t_mm <= 0:
        raise ValueError("radius and thickness must be > 0")
    hoop = p_mpa * r_mm / t_mm
    longi = p_mpa * r_mm / (2.0 * t_mm)
    vm = math.sqrt(hoop * hoop + longi * longi - hoop * longi)
    return hoop, longi, vm


def sphere_stress(p_mpa, r_mm, t_mm):
    if p_mpa < 0:
        raise ValueError("pressure must be >= 0")
    if r_mm <= 0 or t_mm <= 0:
        raise ValueError("radius and thickness must be > 0")
    membrane = p_mpa * r_mm / (2.0 * t_mm)
    # Equal biaxial membrane; von Mises equals the membrane stress.
    return membrane, membrane, membrane


def size_thickness(p_mpa, r_mm, sigma_allow_mpa, shape):
    if sigma_allow_mpa <= 0:
        raise ValueError("allowable stress must be > 0")
    if p_mpa < 0 or r_mm <= 0:
        raise ValueError("pressure must be >= 0 and radius > 0")
    if shape == "sphere":
        return p_mpa * r_mm / (2.0 * sigma_allow_mpa)
    return p_mpa * r_mm / sigma_allow_mpa


def analyze(p_mpa, r_mm, t_mm, sigma_y_mpa, shape):
    if shape == "sphere":
        hoop, longi, vm = sphere_stress(p_mpa, r_mm, t_mm)
        governing = "membrane"
    else:
        hoop, longi, vm = cylinder_stress(p_mpa, r_mm, t_mm)
        governing = "hoop"
    tr = t_mm / r_mm
    return {
        "shape": shape,
        "pressure_mpa": p_mpa,
        "inner_radius_mm": r_mm,
        "wall_thickness_mm": t_mm,
        "t_over_r": round(tr, 5),
        "thin_wall_ok": tr <= 0.1,
        "hoop_stress_mpa": round(hoop, 4),
        "longitudinal_stress_mpa": round(longi, 4),
        "von_mises_mpa": round(vm, 4),
        "governing": governing,
        "factor_of_safety": round(sigma_y_mpa / hoop, 3) if hoop > 0 else None,
    }


def build_parser():
    p = argparse.ArgumentParser(
        description="Thin-walled pressure vessel screening (stdlib, offline).")
    p.add_argument("--shape", choices=("cylinder", "sphere"), default="cylinder")
    p.add_argument("--p", type=float, default=2.0, help="internal gauge pressure MPa (default 2)")
    p.add_argument("--r", type=float, default=250.0, help="inner radius mm (default 250)")
    p.add_argument("--t", type=float, default=5.0, help="wall thickness mm (default 5)")
    p.add_argument("--material", choices=sorted(MATERIALS), default="steel_sa516")
    p.add_argument("--fos", type=float, default=3.0, help="design factor for sizing (default 3)")
    p.add_argument("--size", action="store_true", help="also size minimum wall thickness")
    p.add_argument("--json", action="store_true", help="emit JSON")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.fos <= 0:
            raise ValueError("design factor must be > 0")
        sigma_y = MATERIALS[args.material]
        out = analyze(args.p, args.r, args.t, sigma_y, args.shape)
        out["material"] = args.material
        out["yield_mpa"] = sigma_y
        if args.size:
            out["min_thickness_mm"] = round(
                size_thickness(args.p, args.r, sigma_y / args.fos, args.shape), 4)
            out["design_factor"] = args.fos
            out["allowable_mpa"] = round(sigma_y / args.fos, 4)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        for k, v in out.items():
            print("%-28s %s" % (k, v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
