"""Stand-alone ternary scorer if JuniorLLM is not on PYTHONPATH."""
from __future__ import annotations

import hashlib


def score(text: str) -> dict:
    h = hashlib.sha256((text or "").encode()).hexdigest()
    bits = []
    for ch in h[:32]:
        v = int(ch, 16)
        bits.append(-1 if v < 5 else (0 if v < 10 else 1))
    nz = sum(1 for b in bits if b != 0) / 32
    rec = "high_confidence" if nz > 0.55 else ("review_needed" if nz > 0.35 else "low_confidence")
    return {"port": "JuniorBitNetDraft-local", "rec": rec, "rigidity": round(nz, 4), "state": bits}
