#!/usr/bin/env python3
"""hydraulic_cylinder_prod.py - hydraulic cylinder force, speed and flow screening CLI.

Stdlib only, offline. No network, no sockets, no servers.
JuniorEngrTools / JuniorCloud LLC. Additive tool; screening estimates only,
verify against component ratings before relying on a result.

Extend force  F = P * A_bore * eff
Retract force F = P * (A_bore - A_rod) * eff
Speed         v = Q / A      (flow in L/min, area in mm^2 -> mm/s)
"""
import argparse
import json
import math
import sys


def area_mm2(diameter_mm):
    return math.pi * diameter_mm ** 2 / 4.0


def cylinder(bore, rod, pressure_bar, flow_lpm, eff, stroke):
    if bore <= 0 or rod < 0 or rod >= bore:
        raise SystemExit("need bore > 0 and 0 <= rod < bore")
    if not 0 < eff <= 1:
        raise SystemExit("eff must be in (0, 1]")
    a_bore = area_mm2(bore)
    a_ann = a_bore - area_mm2(rod)
    p = pressure_bar * 0.1  # bar -> N/mm^2 (MPa)
    q = flow_lpm * 1e6 / 60.0  # L/min -> mm^3/s
    out = {
        "bore_area_mm2": a_bore,
        "annulus_area_mm2": a_ann,
        "extend_force_N": p * a_bore * eff,
        "retract_force_N": p * a_ann * eff,
        "extend_speed_mm_s": q / a_bore,
        "retract_speed_mm_s": q / a_ann,
    }
    if stroke:
        out["extend_time_s"] = stroke / out["extend_speed_mm_s"]
        out["retract_time_s"] = stroke / out["retract_speed_mm_s"]
    out["hydraulic_power_kW"] = pressure_bar * flow_lpm / 600.0
    return out


def build_parser():
    p = argparse.ArgumentParser(description="Hydraulic cylinder force/speed/flow screening (offline).")
    p.add_argument("--bore", type=float, required=True, help="bore diameter, mm")
    p.add_argument("--rod", type=float, required=True, help="rod diameter, mm")
    p.add_argument("--pressure", type=float, required=True, help="pressure, bar")
    p.add_argument("--flow", type=float, required=True, help="pump flow, L/min")
    p.add_argument("--eff", type=float, default=0.9, help="mechanical efficiency 0-1 (default 0.9)")
    p.add_argument("--stroke", type=float, default=0.0, help="stroke, mm (adds travel times)")
    p.add_argument("--json", action="store_true", help="emit JSON")
    return p


def main(argv=None):
    a = build_parser().parse_args(argv)
    res = cylinder(a.bore, a.rod, a.pressure, a.flow, a.eff, a.stroke)
    if a.json:
        print(json.dumps(res, indent=2))
    else:
        for k, v in res.items():
            print("%-20s %.3f" % (k, v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
