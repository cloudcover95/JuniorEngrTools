"""Ternary quant methods used by the desk. Stdlib only.

BitNet b1.58: W_q = clip(round(W / mean(|W|)), -1, 1)
Activations: per-token absmax to int8.
I2_S: store ternary as 2-bit codes + scale (pack, not a cpp kernel).
"""
from __future__ import annotations

from dataclasses import dataclass


def _mean_abs(xs: list[float]) -> float:
    if not xs:
        return 1.0
    return sum(abs(x) for x in xs) / len(xs) or 1.0


def sign(xs: list[float]) -> list[int]:
    return [1 if x > 0 else (-1 if x < 0 else 0) for x in xs]


def absmean(xs: list[float]) -> tuple[list[int], float]:
    delta = _mean_abs(xs)
    out = []
    for x in xs:
        q = round(x / delta)
        out.append(1 if q > 1 else (-1 if q < -1 else int(q)))
    return out, delta


def absmax_act(xs: list[float]) -> tuple[list[int], float]:
    am = max((abs(x) for x in xs), default=1.0) or 1.0
    scale = 127.0 / am
    q = [max(-127, min(127, int(round(x * scale)))) for x in xs]
    return q, scale


def i2s_pack(trits: list[int]) -> bytes:
    """Pack {-1,0,1} as 2-bit codes 00/01/10."""
    codes = []
    for t in trits:
        codes.append(0 if t == 0 else (1 if t == 1 else 2))
    out = bytearray()
    acc = 0
    n = 0
    for c in codes:
        acc = (acc << 2) | c
        n += 2
        if n == 8:
            out.append(acc)
            acc = 0
            n = 0
    if n:
        out.append(acc << (8 - n))
    return bytes(out)


@dataclass
class QuantReport:
    method: str
    trits: list[int]
    scale: float
    sparsity: float
    packed: int


def report(xs: list[float], method: str = "absmean") -> QuantReport:
    if method == "sign":
        t, sc = sign(xs), 1.0
    else:
        t, sc = absmean(xs)
    zeros = t.count(0) / len(t) if t else 1.0
    return QuantReport(method, t, sc, round(zeros, 4), len(i2s_pack(t)))


def trit_agree(a: list[int], b: list[int]) -> float:
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    same = sum(1 for i in range(n) if a[i] == b[i])
    return same / n
