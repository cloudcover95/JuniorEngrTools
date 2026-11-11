#!/usr/bin/env python3
"""Spur gear train screening CLI (stdlib only, offline).

Given tooth counts for a chain of meshed gear pairs, an input speed and an
input torque, reports overall ratio, output speed, output torque (with a
per-mesh efficiency) and center distances for a given module.

Screening tool only: no tooth stress, wear, or backlash analysis.
JuniorCloud LLC. Additive, no network, no server.
"""
import argparse
import json
import sys


def parse_stages(text):
    """'20:40,18:54' -> [(20, 40), (18, 54)] as (driver, driven)."""
    stages = []
    for part in text.split(","):
        try:
            a, b = part.strip().split(":")
            z1, z2 = int(a), int(b)
        except ValueError:
            raise ValueError("bad stage %r, use DRIVER:DRIVEN" % part)
        if z1 < 6 or z2 < 6:
            raise ValueError("tooth counts must be >= 6")
        stages.append((z1, z2))
    if not stages:
        raise ValueError("need at least one stage")
    return stages


def analyze(stages, rpm_in, torque_in, module_mm, eff):
    if not 0 < eff <= 1:
        raise ValueError("efficiency must be in (0, 1]")
    if module_mm <= 0 or rpm_in <= 0:
        raise ValueError("module and rpm must be > 0")
    ratio = 1.0
    rows = []
    for z1, z2 in stages:
        ratio *= z2 / z1
        rows.append({
            "driver": z1, "driven": z2,
            "stage_ratio": round(z2 / z1, 5),
            "center_distance_mm": round(module_mm * (z1 + z2) / 2.0, 4),
        })
    total_eff = eff ** len(stages)
    return {
        "stages": rows,
        "overall_ratio": round(ratio, 5),
        "output_rpm": round(rpm_in / ratio, 4),
        "output_torque_nm": round(torque_in * ratio * total_eff, 4),
        "overall_efficiency": round(total_eff, 5),
        "module_mm": module_mm,
    }


def build_parser():
    p = argparse.ArgumentParser(description="Spur gear train screening (stdlib, offline).")
    p.add_argument("--stages", default="20:40,18:54", help="DRIVER:DRIVEN pairs, comma separated")
    p.add_argument("--rpm", type=float, default=1500.0, help="input rev/min (default 1500)")
    p.add_argument("--torque", type=float, default=10.0, help="input torque N*m (default 10)")
    p.add_argument("--module", type=float, default=2.0, help="gear module mm (default 2)")
    p.add_argument("--eff", type=float, default=0.98, help="per-mesh efficiency (default 0.98)")
    p.add_argument("--json", action="store_true", help="emit JSON")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        out = analyze(parse_stages(args.stages), args.rpm, args.torque, args.module, args.eff)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        for k, v in out.items():
            if k == "stages":
                for r in v:
                    print("stage %(driver)s:%(driven)s ratio %(stage_ratio)s center %(center_distance_mm)s mm" % r)
            else:
                print("%-20s %s" % (k, v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
