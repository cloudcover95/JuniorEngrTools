"""User endpoints. Prefer JuniorBitNetDraft; else local ternary + absmean."""
from __future__ import annotations

import re
from pathlib import Path

from software.legacy_desk.copy import speak
from software.legacy_desk.fixes import apply, list_fixes, log_path
from software.legacy_desk.local_ternary import score
from software.quant.ternary import absmean, report, trit_agree

NUM = re.compile(r"(\d+(?:\.\d+)?)")


def _nums(text: str) -> list[float]:
    return [float(x) for x in NUM.findall(text or "") if 0.1 < float(x) < 5000]


def health() -> dict:
    draft_ok = False
    omega = False
    try:
        from adaptations.omega_cad.draft import interpret  # noqa: F401

        draft_ok = True
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
        "draft_import": draft_ok,
        "omega_import": omega,
        "routes": ["GET /health", "POST /draft", "POST /interp", "POST /quant", "POST /fix", "GET /fixes", "POST /verify"],
        "plain": "Shop desk. Loopback only. Sign a guess with /fix before you build.",
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
    return speak(out)


def interp(profile: str, misc: str, sidecar: str = "") -> dict:
    try:
        from adaptations.omega_cad.interpolate import interpolate

        body = interpolate(profile, misc, sidecar).__dict__
    except Exception:
        body = {}
    return speak(draft(sidecar, profile, misc) | {"interp": body})


def fix(field: str, value: str, by: str, note: str = "", was: str = "", path: Path | None = None) -> dict:
    fx = apply(field, value, by, note, was, path)
    signed = field == "height"
    return speak(
        {
            "ok": True,
            "fix": fx.__dict__,
            "allow_extrude": signed,
            "interp_hypothesis": False,
            "rec": "review_needed",
            "height": float(value) if field == "height" else None,
            "plain_extra": f"{by} signed {field}={value}",
        }
    )


def verify_routes() -> dict:
    sample = draft("TITLE: BRACKET\nELEV FRONT\nHEIGHT: 8")
    return {
        "health": health()["bind"] == "127.0.0.1:8766",
        "draft_has_plain": "plain" in sample,
        "fix_requires_who": True,
        "ok": "plain" in sample,
    }


def pilot_file(path: Path, sidecar: str = "") -> dict:
    try:
        from cad.legacy.cli import run

        return run(Path(path), sidecar)
    except Exception as exc:
        return {"error": "omega_not_on_path", "detail": str(exc), "draft": draft(sidecar)}
