"""Second-brain view of the trit property table."""
from __future__ import annotations


def index() -> dict:
    try:
        from junior_bitnet.refprop import Library

        lib = Library()
        return {
            "engine": "JuniorTeqp",
            "fluids": lib.names(),
            "palace_backend": lib.palace.backend,
            "plain": "Trit REFPROP-shaped table. Sealed slots; public rho/phase.",
        }
    except Exception as exc:
        return {"engine": "JuniorTeqp", "error": str(exc), "plain": "Load JuniorLLM on PYTHONPATH."}
