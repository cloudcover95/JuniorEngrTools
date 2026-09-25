"""Generic metal-building screen. Inputs only."""
from calculators.building_weight import weight
from calculators.roof_point_load import hung
from calculators.slab_point_load import wheel
from calculators.site_environmental import ratings


def screen(footprint_sqft: float = 7000.0, span_ft: float = 60.0) -> dict:
    return {
        "weight": weight(footprint_sqft, 6.0, 8.5),
        "fan_200": hung(span_ft, 200.0, 15.0, 60.0),
        "hanger_5000": hung(span_ft, 5000.0, 15.0, 60.0),
        "slab4_wheel6500": wheel(4.0, 6500.0),
        "slab6_wheel6500": wheel(6.0, 6500.0),
        "env": ratings(16.0, 91.0, "D", footprint_sqft),
        "pe_stamp": False,
        "refs": ["ASCE 7", "IBC", "AISC 360", "ACI 360", "MBMA"],
    }
