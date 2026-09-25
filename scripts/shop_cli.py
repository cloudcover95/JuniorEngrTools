#!/usr/bin/env python3
"""End-user inputs for shop screens. No Streamlit."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from calculators.building_weight import weight
from calculators.roof_point_load import hung
from calculators.slab_point_load import wheel
from calculators.site_environmental import ratings


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--footprint", type=float, default=7000.0)
    p.add_argument("--slab-in", type=float, default=6.0)
    p.add_argument("--steel-psf", type=float, default=8.5)
    p.add_argument("--span-ft", type=float, default=60.0)
    p.add_argument("--p-lb", type=float, default=200.0)
    p.add_argument("--s-in3", type=float, default=15.0)
    p.add_argument("--i-in4", type=float, default=60.0)
    p.add_argument("--wheel-lb", type=float, default=6500.0)
    p.add_argument("--snow-psf", type=float, default=16.0)
    p.add_argument("--wind-mph", type=float, default=91.0)
    p.add_argument("--sdc", default="D")
    a = p.parse_args()
    out = {
        "weight": weight(a.footprint, a.slab_in, a.steel_psf),
        "hung": hung(a.span_ft, a.p_lb, a.s_in3, a.i_in4),
        "wheel": wheel(a.slab_in, a.wheel_lb),
        "env": ratings(a.snow_psf, a.wind_mph, a.sdc, a.footprint),
        "pe_stamp": False,
    }
    print(json.dumps(out, indent=2))
    dest = Path.home() / ".juniorhome" / "engr" / "shop_last.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    html = dest.with_suffix(".html")
    html.write_text(
        "<!doctype html><meta charset=utf-8><title>shop screen</title>"
        "<pre>" + json.dumps(out, indent=2) + "</pre>",
        encoding="utf-8",
    )
    out["saved"] = str(dest)


if __name__ == "__main__":
    main()
