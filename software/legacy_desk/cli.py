#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from software.legacy_desk.endpoints import draft, health, pilot_file


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "health"
    if cmd == "health":
        print(json.dumps(health(), indent=2))
        return 0
    if cmd == "draft":
        text = Path(argv[2]).read_text(encoding="utf-8") if len(argv) > 2 else sys.stdin.read()
        print(json.dumps(draft(text), indent=2))
        return 0
    if cmd == "pilot" and len(argv) > 2:
        side = Path(argv[3]).read_text(encoding="utf-8") if len(argv) > 3 else ""
        print(json.dumps(pilot_file(Path(argv[2]), side), indent=2, default=str))
        return 0
    if cmd == "serve":
        from software.legacy_desk.server import serve

        return serve()
    print("health | draft [file] | pilot <sheet> [sidecar] | serve")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
