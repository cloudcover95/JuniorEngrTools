"""Pass-through of listed ratings. Does not look up ASCE maps."""

def ratings(snow_psf: float, wind_mph: float, sdc: str, area_sqft: float) -> dict:
    return {
        "snow_psf": snow_psf,
        "snow_total_lb": round(snow_psf * area_sqft, 1),
        "wind_mph": wind_mph,
        "sdc": sdc,
        "map_lookup": False,
        "pe_stamp": False,
    }
