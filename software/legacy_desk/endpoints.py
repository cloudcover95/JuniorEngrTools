"""User endpoints. Prefer JuniorBitNetDraft; else local ternary + absmean."""
from __future__ import annotations

import re
from pathlib import Path

from software.legacy_desk.local_ternary import score
from software.quant.ternary import absmean, report, trit_agree

NUM = re.compile(r"(\d+(?:\.\d+)?)")


def _nums(text: str) -> list[float]:
    return [float(x) for x in NUM.findall(text or "") if 0.1 < float(x) < 5000]


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
        "quant": ["absmean", "sign", "absmax", "i2s"],
        "draft_import": draft,
        "omega_import": omega,
        "home": "JuniorHome orchestrates; this repo is the shop UI/API",
    }


def quant_dims(values: list[float], method: str = "absmean") -> dict:
    r = report(values, method)
    return r.__dict__


def draft(sidecar: str, profile: str = "", misc: str = "") -> dict:
    try:
        from adaptations.omega_cad.draft import interpret

        c = interpret(sidecar, profile=profile, misc=misc)
        out = {
            "port": c.port,
            "rec": c.rec,
            "rigidity": c.rigidity,
            "height": c.height,
            "allow_extrude": c.allow_extrude,
            "interp_source": c.interp_source,
            "interp_hypothesis": c.interp_hypothesis,
            "agreement": c.agreement,
            "proposals": c.proposals,
        }
    except Exception:
        s = score(sidecar + profile + misc)
        low = sidecar.lower()
        allow = s["rec"] != "low_confidence" and ("elev" in low or "height" in low)
        out = {**s, "allow_extrude": allow, "interp_hypothesis": True, "proposals": {}}
    pn, mn = _nums(profile), _nums(misc)
    if pn and mn:
        tp, _ = absmean(pn)
        tm, _ = absmean(mn[: len(tp)] + [0] * max(0, len(tp) - len(mn)))
        out["trit_agree"] = trit_agree(tp, tm[: len(tp)])
        out["quant_method"] = "absmean"
    return out


def interp(profile: str, misc: str, sidecar: str = "") -> dict:
    try:
        from adaptations.omega_cad.interpolate import interpolate

        body = interpolate(profile, misc, sidecar).__dict__
    except Exception:
        body = draft(sidecar, profile, misc)
    return draft(sidecar, profile, misc) | {"interp": body}


def pilot_file(path: Path, sidecar: str = "") -> dict:
    try:
        from cad.legacy.cli import run

        return run(Path(path), sidecar)
    except Exception as exc:
        return {"error": "omega_not_on_path", "detail": str(exc), "draft": draft(sidecar)}
