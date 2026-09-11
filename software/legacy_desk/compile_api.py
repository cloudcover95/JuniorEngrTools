"""Compile user inputs. Prefer JuniorLLM compile_sheet."""
from __future__ import annotations


def compile_inputs(sidecar: str, profile: str = "", misc: str = "", fixes: list | None = None) -> dict:
    try:
        from junior_bitnet.compile_sheet import compile_sheet

        c = compile_sheet(sidecar, profile, misc, fixes)
        return {
            "ready": c.ready,
            "height": c.height,
            "run_iq": c.data["run_iq"],
            "actions": [a.__dict__ for a in c.actions],
            "plain": "Ready to build." if c.ready else "Finish the action list before 3D.",
            "data": {k: c.data[k] for k in ("height", "run_iq")},
        }
    except Exception:
        need = []
        if "HEIGHT" not in sidecar.upper():
            need.append({"kind": "fix", "field": "height", "detail": "Sign height", "blocking": True})
        return {"ready": not need, "actions": need, "plain": "Local compile; attach JuniorLLM for full gate."}
