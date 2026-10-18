#!/usr/bin/env python3
"""bolt_preload_prod.py - bolt preload / tightening torque screening CLI.

JuniorEngrTools, JuniorCloud LLC. Stdlib only, offline, no network, no server.

Short-form torque relation:  T = K * F * d
  T  tightening torque (N*m)
  K  nut factor (dimensionless; ~0.20 dry steel, ~0.15 lubricated)
  F  target preload (N)
  d  nominal diameter (m)

Preload target defaults to a fraction of proof load:  F = frac * Sp * At
  Sp proof strength (MPa) by ISO 898-1 property class
  At tensile stress area (mm^2) for ISO metric coarse threads

Screening estimates only. Verify against the fastener maker's data.
"""
import argparse
import json
import sys

# ISO 261/724 metric coarse: size -> (nominal d mm, pitch mm)
METRIC_COARSE = {
    "M3": (3.0, 0.5), "M4": (4.0, 0.7), "M5": (5.0, 0.8), "M6": (6.0, 1.0),
    "M8": (8.0, 1.25), "M10": (10.0, 1.5), "M12": (12.0, 1.75),
    "M14": (14.0, 2.0), "M16": (16.0, 2.0), "M20": (20.0, 2.5),
    "M24": (24.0, 3.0), "M30": (30.0, 3.5),
}

# ISO 898-1 proof strength Sp (MPa), d <= 16 mm values used as screening default
PROOF_MPA = {"4.6": 225.0, "5.8": 380.0, "8.8": 600.0, "10.9": 830.0, "12.9": 970.0}

NUT_FACTORS = {"dry": 0.20, "oiled": 0.18, "moly": 0.15, "zinc": 0.22, "ptfe": 0.12}


def stress_area_mm2(d_mm, p_mm):
    """ISO 898-1 tensile stress area At = pi/4 * (d - 0.9382 P)^2."""
    import math
    return math.pi / 4.0 * (d_mm - 0.9382 * p_mm) ** 2


def compute(size, prop_class, k, frac):
    if size not in METRIC_COARSE:
        raise ValueError("unknown size %r; choose from %s" % (size, ", ".join(METRIC_COARSE)))
    if prop_class not in PROOF_MPA:
        raise ValueError("unknown class %r; choose from %s" % (prop_class, ", ".join(PROOF_MPA)))
    if not 0.0 < frac <= 1.0:
        raise ValueError("fraction must be in (0, 1]")
    if not 0.05 <= k <= 0.5:
        raise ValueError("nut factor K outside plausible range 0.05-0.5")
    d_mm, p_mm = METRIC_COARSE[size]
    at = stress_area_mm2(d_mm, p_mm)
    sp = PROOF_MPA[prop_class]
    proof_n = sp * at
    preload_n = frac * proof_n
    torque_nm = k * preload_n * d_mm / 1000.0
    return {
        "size": size, "pitch_mm": p_mm, "class": prop_class,
        "stress_area_mm2": round(at, 2), "proof_mpa": sp,
        "proof_load_kn": round(proof_n / 1000.0, 2),
        "preload_fraction": frac, "preload_kn": round(preload_n / 1000.0, 2),
        "nut_factor": k, "torque_nm": round(torque_nm, 2),
        "torque_ftlb": round(torque_nm * 0.737562, 2),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Bolt preload and tightening torque screening (T = K*F*d), ISO metric coarse.")
    ap.add_argument("size", nargs="?", help="thread size, e.g. M8 (omit with --table)")
    ap.add_argument("-c", "--class", dest="prop_class", default="8.8",
                    help="ISO 898-1 property class (default 8.8)")
    ap.add_argument("-k", "--nut-factor", type=float, default=None,
                    help="nut factor K (overrides --lube)")
    ap.add_argument("-l", "--lube", choices=sorted(NUT_FACTORS), default="dry",
                    help="lubrication condition for default K (default dry)")
    ap.add_argument("-f", "--fraction", type=float, default=0.75,
                    help="preload as fraction of proof load (default 0.75)")
    ap.add_argument("--table", action="store_true", help="print all sizes for the class")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    a = ap.parse_args(argv)

    k = a.nut_factor if a.nut_factor is not None else NUT_FACTORS[a.lube]
    sizes = list(METRIC_COARSE) if a.table else ([a.size] if a.size else [])
    if not sizes:
        ap.error("give a size (e.g. M8) or --table")
    try:
        rows = [compute(s.upper(), a.prop_class, k, a.fraction) for s in sizes]
    except ValueError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(rows if a.table else rows[0], indent=2))
        return 0
    print("%-5s %6s %9s %10s %10s %9s %9s" % ("size", "pitch", "At mm2", "proof kN",
                                              "preload kN", "T N*m", "T ft*lb"))
    for r in rows:
        print("%-5s %6.2f %9.2f %10.2f %10.2f %9.2f %9.2f" % (
            r["size"], r["pitch_mm"], r["stress_area_mm2"], r["proof_load_kn"],
            r["preload_kn"], r["torque_nm"], r["torque_ftlb"]))
    print("class %s, K=%.2f, preload %.0f%% of proof. Screening only." % (
        a.prop_class, k, a.fraction * 100))
    return 0


if __name__ == "__main__":
    sys.exit(main())
