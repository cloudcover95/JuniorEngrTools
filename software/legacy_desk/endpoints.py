"""User endpoints. Prefer JuniorBitNetDraft; else local ternary."""
from __future__ import annotations

from pathlib import Path

from software.legacy_desk.local_ternary import score


def health() -> dict:
    draft = False
    omega = False
    try:
        from adaptations.omega_cad.draft import interpret  # noqa: F401

        draft = True
    except Exception:
        pass
    try:
        from cad.legacy.cli import run  # noqa: F401

        omega = True
    except Exception:
        pass
    return {
        "product": "JuniorEngrTools legacy desk",
        "bind": "127.0.0.1:8766",
        "port": "JuniorBitNetDraft",
        "draft_import": draft,
        "omega_import": omega,
        "home": "JuniorHome orchestrates; this repo is the shop UI/API",
    }


def draft(sidecar: str) -> dict:
    try:
        from adaptations.omega_cad.draft import interpret

        c = interpret(sidecar)
        return {
            "port": c.port,
            "rec": c.rec,
            "rigidity": c.rigidity,
            "height": c.height,
            "allow_extrude": c.allow_extrude,
            "proposals": c.proposals,
        }
    except Exception:
        s = score(sidecar)
        low = sidecar.lower()
        allow = s["rec"] != "low_confidence" and ("elev" in low or "height" in low or "thickness" in low)
        return {**s, "allow_extrude": allow, "proposals": {}}


def pilot_file(path: Path, sidecar: str = "") -> dict:
    try:
        from cad.legacy.cli import run

        return run(Path(path), sidecar)
    except Exception as exc:
        return {"error": "omega_not_on_path", "detail": str(exc), "draft": draft(sidecar)}
