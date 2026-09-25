"""Dead-load screen. Not a takeoff. Not a PE stamp."""
CONC_PCF = 150.0


def weight(footprint_sqft: float, slab_in: float = 6.0, steel_psf: float = 8.5) -> dict:
    slab = footprint_sqft * (slab_in / 12.0) * CONC_PCF
    steel = footprint_sqft * steel_psf
    tot = slab + steel
    return {
        "slab_lb": round(slab, 1),
        "steel_lb": round(steel, 1),
        "total_lb": round(tot, 1),
        "total_ton": round(tot / 2000.0, 2),
        "pe_stamp": False,
        "note": "envelope+slab only; MEP/fitout extra",
    }
