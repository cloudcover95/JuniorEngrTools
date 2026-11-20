#!/usr/bin/env python3
"""pipe_pressure_drop_prod.py - Darcy-Weisbach pressure drop for a straight pipe (stdlib only)."""
import argparse
import json
import math


def friction_factor(re, rel_rough):
    if re <= 0:
        raise ValueError("Reynolds number must be positive")
    if re < 2300:
        return 64.0 / re
    # Swamee-Jain explicit approximation (turbulent)
    return 0.25 / math.log10(rel_rough / 3.7 + 5.74 / re ** 0.9) ** 2


def pressure_drop(flow_lps, dia_mm, length_m, rough_mm=0.045, rho=998.0, mu=1.0e-3):
    d = dia_mm / 1000.0
    q = flow_lps / 1000.0
    area = math.pi * d * d / 4.0
    v = q / area
    re = rho * v * d / mu
    f = friction_factor(re, (rough_mm / 1000.0) / d)
    dp = f * (length_m / d) * rho * v * v / 2.0
    return {"velocity_m_s": v, "reynolds": re, "friction_factor": f,
            "pressure_drop_pa": dp, "pressure_drop_kpa": dp / 1000.0,
            "head_loss_m": dp / (rho * 9.80665)}


def main(argv=None):
    p = argparse.ArgumentParser(description="Darcy-Weisbach pipe pressure drop (water defaults).")
    p.add_argument("--flow-lps", type=float, default=2.0, help="flow in litres/second")
    p.add_argument("--dia-mm", type=float, default=50.0, help="inner diameter in mm")
    p.add_argument("--length-m", type=float, default=100.0, help="pipe length in m")
    p.add_argument("--rough-mm", type=float, default=0.045, help="absolute roughness in mm")
    p.add_argument("--rho", type=float, default=998.0, help="density kg/m3")
    p.add_argument("--mu", type=float, default=1.0e-3, help="dynamic viscosity Pa.s")
    a = p.parse_args(argv)
    if min(a.flow_lps, a.dia_mm, a.length_m, a.rho, a.mu) <= 0 or a.rough_mm < 0:
        p.error("values must be positive")
    r = pressure_drop(a.flow_lps, a.dia_mm, a.length_m, a.rough_mm, a.rho, a.mu)
    print(json.dumps({k: round(v, 6) for k, v in r.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
