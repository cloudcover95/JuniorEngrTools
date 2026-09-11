"""Human overrides of interpolated values. Append-only."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / ".juniorengr" / "fixes.jsonl"


@dataclass
class Fix:
    field: str
    value: str
    by: str
    note: str
    was: str
    at: str


def log_path(path: Path | None = None) -> Path:
    p = path or ROOT
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text("", encoding="utf-8")
    return p


def apply(field: str, value: str, by: str, note: str = "", was: str = "", path: Path | None = None) -> Fix:
    field = field.strip().lower()
    if field not in {"height", "units", "title", "revision", "layer"}:
        raise ValueError("field must be height|units|title|revision|layer")
    if not by.strip():
        raise ValueError("who is signing this fix")
    fx = Fix(field, str(value), by.strip(), note, was, datetime.now(timezone.utc).isoformat())
    dest = log_path(path)
    with dest.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(asdict(fx)) + "\n")
    return fx


def list_fixes(path: Path | None = None) -> list[dict]:
    p = log_path(path)
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
