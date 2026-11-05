#!/usr/bin/env python3
"""Solid/hollow round shaft torsion screening CLI (stdlib only, offline).

Given transmitted power and speed (or a direct torque), computes shear stress,
angle of twist and a factor of safety for a round shaft, or sizes the minimum
solid diameter for an allowable shear stress.

Screening tool only: no keyways, fatigue, or stress concentration factors.
JuniorCloud LLC. Additive, no network, no server.
"""
import argparse
import json
import math
import sys

MATERIALS = {
    # name: (shear modulus G [GPa], shear yield [MPa])
    "steel_1018": (79.3, 213.0),
    "steel_4140": (80.0, 400.0),
    "stainless_304": (77.2, 124.0),
    "aluminum_6061": (26.0, 159.0),
    "brass_360": (37.0, 179.0),
    "titanium_6al4v": (44.0, 550.0),
}


def torque_from_power(power_kw, rpm):
    if rpm <= 0:
        raise ValueError("rpm must be > 0")
    return power_kw * 1000.0 / (2.0 * math.pi * rpm / 60.0)


def polar_moment(d_mm, di_mm=0.0):
    if d_mm <= 0 or di_mm < 0 or di_mm >= d_mm:
        raise ValueError("need 0 <= inner diameter < outer diameter, outer > 0")
    return math.pi * (d_mm ** 4 - di_mm ** 4) / 32.0


def analyze(torque_nm, d_mm, di_mm, length_mm, g_gpa, tau_y_mpa):
    j = polar_moment(d_mm, di_mm)  # mm^4
    t_nmm = torque_nm * 1000.0
    tau = t_nmm * (d_mm / 2.0) / j  # MPa
    theta = t_nmm * length_mm / (g_gpa * 1000.0 * j)  # rad
    return {
        "torque_nm": round(torque_nm, 4),
        "outer_d_mm": d_mm,
        "inner_d_mm": di_mm,
        "polar_moment_mm4": round(j, 3),
        "shear_stress_mpa": round(tau, 4),
        "twist_deg": round(math.degrees(theta), 5),
        "twist_deg_per_m": round(math.degrees(theta) / (length_mm / 1000.0), 5) if length_mm > 0 else None,
        "factor_of_safety": round(tau_y_mpa / tau, 3) if tau > 0 else None,
    }


def size_solid(torque_nm, tau_allow_mpa):
    if tau_allow_mpa <= 0:
        raise ValueError("allowable shear must be > 0")
    return (16.0 * torque_nm * 1000.0 / (math.pi * tau_allow_mpa)) ** (1.0 / 3.0)


def build_parser():
    p = argparse.ArgumentParser(description="Round shaft torsion screening (stdlib, offline).")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--torque", type=float, help="torque in N*m")
    g.add_argument("--power-kw", type=float, help="transmitted power in kW (use with --rpm)")
    p.add_argument("--rpm", type=float, help="shaft speed in rev/min")
    p.add_argument("--d", type=float, default=25.0, help="outer diameter mm (default 25)")
    p.add_argument("--di", type=float, default=0.0, help="inner diameter mm for hollow shaft (default 0)")
    p.add_argument("--length", type=float, default=500.0, help="length mm (default 500)")
    p.add_argument("--material", choices=sorted(MATERIALS), default="steel_1018")
    p.add_argument("--fos", type=float, default=2.0, help="design factor for sizing (default 2)")
    p.add_argument("--size", action="store_true", help="also size minimum solid diameter")
    p.add_argument("--json", action="store_true", help="emit JSON")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.power_kw is not None:
            if args.rpm is None:
                raise ValueError("--power-kw needs --rpm")
            torque = torque_from_power(args.power_kw, args.rpm)
        elif args.torque is not None:
            torque = args.torque
        else:
            torque = 100.0
        g_gpa, tau_y = MATERIALS[args.material]
        out = analyze(torque, args.d, args.di, args.length, g_gpa, tau_y)
        out["material"] = args.material
        if args.size:
            out["min_solid_d_mm"] = round(size_solid(torque, tau_y / args.fos), 3)
            out["design_factor"] = args.fos
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        for k, v in out.items():
            print("%-20s %s" % (k, v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
