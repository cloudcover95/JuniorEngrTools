#!/usr/bin/env python3
"""Keyed shaft joint check: key shear and bearing (crushing) stress. Stdlib only."""
import argparse, json, sys


def key_check(torque_nm, shaft_d_mm, key_w_mm, key_h_mm, key_len_mm, yield_mpa, sf_target):
    for n, v in (("torque", torque_nm), ("shaft_d", shaft_d_mm), ("key_w", key_w_mm),
                 ("key_h", key_h_mm), ("key_len", key_len_mm), ("yield", yield_mpa)):
        if v <= 0:
            raise ValueError(n + " must be > 0")
    force_n = torque_nm / (shaft_d_mm / 2000.0)
    shear = force_n / (key_w_mm * key_len_mm)
    bearing = force_n / ((key_h_mm / 2.0) * key_len_mm)
    sf_shear = 0.577 * yield_mpa / shear
    sf_bear = yield_mpa / bearing
    return {"force_n": round(force_n, 2), "shear_mpa": round(shear, 2),
            "bearing_mpa": round(bearing, 2), "sf_shear": round(sf_shear, 2),
            "sf_bearing": round(sf_bear, 2),
            "ok": min(sf_shear, sf_bear) >= sf_target}


def main(argv=None):
    p = argparse.ArgumentParser(description="Keyed shaft joint shear/bearing check")
    p.add_argument("--torque-nm", type=float, default=200.0)
    p.add_argument("--shaft-d-mm", type=float, default=40.0)
    p.add_argument("--key-w-mm", type=float, default=12.0)
    p.add_argument("--key-h-mm", type=float, default=8.0)
    p.add_argument("--key-len-mm", type=float, default=50.0)
    p.add_argument("--yield-mpa", type=float, default=300.0)
    p.add_argument("--sf", type=float, default=2.0)
    a = p.parse_args(argv)
    try:
        r = key_check(a.torque_nm, a.shaft_d_mm, a.key_w_mm, a.key_h_mm, a.key_len_mm, a.yield_mpa, a.sf)
    except ValueError as e:
        print("error: " + str(e), file=sys.stderr)
        return 2
    print(json.dumps(r, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
