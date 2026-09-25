"""Order-of-magnitude CFM / enclosure. Not ACGIH."""

def lean_to(cfm: float, volume_cuft: float, nr_db: float = 15.0) -> dict:
    ach = (cfm * 60.0) / volume_cuft if volume_cuft else 0.0
    return {"cfm": cfm, "ach": round(ach, 2), "nr_db_claimed": nr_db, "osha_dosimeter": False, "pe_stamp": False}
