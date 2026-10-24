#!/usr/bin/env python3
"""thermal_expansion_prod.py - linear thermal expansion and fit-change screening CLI.

Stdlib only, offline. No network, no sockets, no servers.
JuniorEngrTools / JuniorCloud LLC. Additive tool; screening estimates only,
verify against your material data sheet before relying on a result.

Linear expansion:  dL = alpha * L0 * dT
Fit change (shaft in bore, both heated by the same dT):
    change in diametral clearance = (alpha_bore - alpha_shaft) * D * dT
"""
import argparse
import json
import sys

# Typical coefficients of linear thermal expansion, 1e-6 per degC (room temp).
MATERIALS = {
    "steel": 12.0,
    "stainless304": 17.3,
    "aluminum6061": 23.6,
    "brass": 19.0,
    "copper": 16.5,
    "titanium": 8.6,
    "cast_iron": 10.8,
    "invar": 1.2,
    "abs": 90.0,
    "nylon": 100.0,
}


def alpha_of(name_or_value):
    """Return alpha in 1/degC from a material key or a number in 1e-6/degC."""
    key = str(name_or_value).strip().lower()
    if key in MATERIALS:
        return MATERIALS[key] * 1e-6
    try:
        return float(key) * 1e-6
    except ValueError:
        raise SystemExit("unknown material %r; use one of %s or a number in 1e-6/degC"
                         % (name_or_value, ", ".join(sorted(MATERIALS))))


def expansion(length, alpha, t0, t1):
    dt = t1 - t0
    dl = alpha * length * dt
    return {"length": length, "alpha_per_C": alpha, "delta_T": dt,
            "delta_L": dl, "final_length": length + dl}


def fit_change(diameter, clearance, alpha_bore, alpha_shaft, t0, t1):
    dt = t1 - t0
    d_bore = alpha_bore * diameter * dt
    d_shaft = alpha_shaft * diameter * dt
    new_clear = clearance + d_bore - d_shaft
    return {"diameter": diameter, "delta_T": dt, "bore_growth": d_bore,
            "shaft_growth": d_shaft, "clearance_start": clearance,
            "clearance_end": new_clear,
            "status": "interference" if new_clear < 0 else "clearance"}


def build_parser():
    p = argparse.ArgumentParser(
        description="Linear thermal expansion and shaft/bore fit-change screening (stdlib, offline).")
    p.add_argument("--json", action="store_true", help="print JSON instead of text")
    sub = p.add_subparsers(dest="cmd")
    e = sub.add_parser("expand", help="length change of one part")
    e.add_argument("--length", type=float, required=True, help="starting length (any unit)")
    e.add_argument("--material", default="steel", help="material key or alpha in 1e-6/degC")
    e.add_argument("--t0", type=float, default=20.0, help="start temperature degC")
    e.add_argument("--t1", type=float, required=True, help="end temperature degC")
    f = sub.add_parser("fit", help="clearance change of a shaft in a bore")
    f.add_argument("--diameter", type=float, required=True, help="nominal diameter")
    f.add_argument("--clearance", type=float, default=0.0,
                   help="diametral clearance at t0 (negative = interference)")
    f.add_argument("--bore", default="aluminum6061", help="bore material or alpha")
    f.add_argument("--shaft", default="steel", help="shaft material or alpha")
    f.add_argument("--t0", type=float, default=20.0)
    f.add_argument("--t1", type=float, required=True)
    sub.add_parser("materials", help="list built-in materials")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.cmd == "expand":
        out = expansion(args.length, alpha_of(args.material), args.t0, args.t1)
    elif args.cmd == "fit":
        out = fit_change(args.diameter, args.clearance, alpha_of(args.bore),
                         alpha_of(args.shaft), args.t0, args.t1)
    elif args.cmd == "materials":
        out = {k: v for k, v in sorted(MATERIALS.items())}
    else:
        build_parser().print_help()
        return 0
    if args.json:
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        for k, v in out.items():
            print("%-16s %s" % (k, ("%.6g" % v) if isinstance(v, float) else v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
