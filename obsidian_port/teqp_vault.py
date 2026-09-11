"""Obsidian note for JuniorTeqp. Prefers JuniorLLM Library."""
from __future__ import annotations

from pathlib import Path


def sync(vault: Path) -> Path:
    vault = Path(vault)
    dest = vault / "JuniorTeqp"
    dest.mkdir(parents=True, exist_ok=True)
    try:
        from junior_bitnet.vault import write_vault

        return write_vault(vault)
    except Exception:
        note = dest / "property_table.md"
        note.write_text(
            "---\ntitle: JuniorTeqp\ntags: [juniorteqp]\n---\n\nAttach JuniorLLM for the full table.\n",
            encoding="utf-8",
        )
        return note
