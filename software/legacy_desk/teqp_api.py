"""Shop view of JuniorTeqp. Falls back if JuniorLLM is off path."""
from __future__ import annotations


def state_props(values: list[float]) -> dict:
    try:
        from junior_bitnet.math import absmean
        from junior_bitnet.teqp import props

        z, sc = absmean(values)
        p = props(z)
        d = p.__dict__
        d["scale"] = sc
        d["plain"] = f"{p.phase} trit gas; rho={p.rho}"
        return d
    except Exception:
        nz = sum(1 for v in values if abs(v) > 1e-9)
        n = len(values) or 1
        return {"rho": nz / n, "phase": "unknown", "plain": "attach JuniorLLM for JuniorTeqp"}
