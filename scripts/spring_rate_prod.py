#!/usr/bin/env python3
"""spring_rate_prod.py - helical compression spring rate and stress screening.

Stdlib only. Offline. No network, no server.

Inputs (round wire, closed and ground ends assumed for solid height):
  d   wire diameter
  D   mean coil diameter
  Na  active coils
  G   shear modulus
  F   working load (optional, for stress and deflection)

Unit systems:
  si : d, D [mm], G [GPa], F [N]   -> rate N/mm, stress MPa, deflection mm
  us : d, D [in], G [Mpsi], F [lbf] -> rate lbf/in, stress ksi, deflection in

Formulas (Shigley):
  k   = G d^4 / (8 D^3 Na)
  C   = D / d
  Kw  = (4C - 1)/(4C - 4) + 0.615/C        (Wahl factor)
  tau = Kw * 8 F D / (pi d^3)
  y   = F / k
  Ls  = d * (Na + 2)                        (solid height, closed and ground)

Flags: spring index outside 4..12 and active coils below 3 are warned.
Screening only. Not a substitute for a licensed engineer's design check.
"""
import argparse
import json
import math
import sys

MATERIAL_G = {"si": {"music": 81.7, "stainless302": 69.0, "chrome-si": 77.2},
              "us": {"music": 11.85, "stainless302": 10.0, "chrome-si": 11.2}}


def compute(units, d, D, Na, G, F=None):
    if d <= 0 or D <= 0 or Na <= 0 or G <= 0:
        raise ValueError("d, D, Na and G must be positive")
    if D <= d:
        raise ValueError("mean diameter D must exceed wire diameter d")
    g_base = G * 1e3 if units == "si" else G * 1e6  # MPa or psi
    k = g_base * d ** 4 / (8.0 * D ** 3 * Na)        # N/mm or lbf/in
    C = D / d
    Kw = (4 * C - 1) / (4 * C - 4) + 0.615 / C
    out = {"units": units, "rate": round(k, 6), "index_C": round(C, 4),
           "wahl_Kw": round(Kw, 5), "solid_height": round(d * (Na + 2), 6),
           "warnings": []}
    if not 4 <= C <= 12:
        out["warnings"].append("spring index %.2f outside 4..12" % C)
    if Na < 3:
        out["warnings"].append("fewer than 3 active coils")
    if F is not None:
        tau = Kw * 8.0 * F * D / (math.pi * d ** 3)  # MPa or psi
        out["deflection"] = round(F / k, 6)
        out["shear_stress"] = round(tau if units == "si" else tau / 1e3, 4)
    out["rate_unit"] = "N/mm" if units == "si" else "lbf/in"
    out["stress_unit"] = "MPa" if units == "si" else "ksi"
    return out


def selftest():
    # Shigley-style check: music wire, d=2 mm, D=20 mm, Na=10, G=81.7 GPa
    r = compute("si", 2.0, 20.0, 10, 81.7, 50.0)
    k = 81700 * 16 / (8 * 8000 * 10)
    assert abs(r["rate"] - k) < 1e-6, r
    assert abs(r["deflection"] - 50.0 / k) < 1e-5
    assert r["solid_height"] == 24.0
    try:
        compute("si", 2.0, 1.0, 10, 81.7)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
    return True


def main(argv=None):
    p = argparse.ArgumentParser(description="Helical compression spring rate and stress screening (stdlib, offline).")
    p.add_argument("--units", choices=("si", "us"), default="si")
    p.add_argument("--d", type=float, help="wire diameter (mm or in)")
    p.add_argument("--D", type=float, help="mean coil diameter (mm or in)")
    p.add_argument("--na", type=float, help="active coils")
    p.add_argument("--G", type=float, help="shear modulus (GPa or Mpsi)")
    p.add_argument("--material", choices=sorted(MATERIAL_G["si"]), help="use a stock shear modulus instead of --G")
    p.add_argument("--F", type=float, help="working load (N or lbf)")
    p.add_argument("--json", action="store_true", help="print JSON")
    p.add_argument("--selftest", action="store_true", help="run built-in checks and exit")
    a = p.parse_args(argv)
    if a.selftest:
        selftest()
        print("selftest ok")
        return 0
    G = a.G if a.G is not None else (MATERIAL_G[a.units][a.material] if a.material else None)
    if a.d is None or a.D is None or a.na is None or G is None:
        p.error("need --d, --D, --na and --G or --material")
    try:
        r = compute(a.units, a.d, a.D, a.na, G, a.F)
    except ValueError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(r, indent=2, sort_keys=True))
    else:
        print("rate         %.4f %s" % (r["rate"], r["rate_unit"]))
        print("index C      %.3f   Wahl Kw %.4f" % (r["index_C"], r["wahl_Kw"]))
        print("solid height %.4f" % r["solid_height"])
        if "deflection" in r:
            print("deflection   %.4f" % r["deflection"])
            print("shear stress %.3f %s" % (r["shear_stress"], r["stress_unit"]))
        for w in r["warnings"]:
            print("warning: " + w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
