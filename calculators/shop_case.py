"""Blacktail-style shop numbers as *inputs*, not facts from the video."""
from calculators.building_weight import weight
from calculators.roof_point_load import hung
from calculators.slab_point_load import wheel
from calculators.site_environmental import ratings


def blacktail_screen() -> dict:
    fp = 147000.0 / 21.0
    return {
        "footprint_from_volume_sqft": round(fp, 1),
        "weight": weight(fp, 6.0, 8.5),
        "contractor_guess_lb": 37_000_000,
        "fan_200": hung(60.0, 200.0, 15.0, 60.0),
        "root_5000": hung(60.0, 5000.0, 15.0, 60.0),
        "slab4_wheel6500": wheel(4.0, 6500.0),
        "slab6_wheel6500": wheel(6.0, 6500.0),
        "env": ratings(16.0, 91.0, "D", fp),
        "pe_stamp": False,
    }
