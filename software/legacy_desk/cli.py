#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from software.legacy_desk.endpoints import draft, fix, health, interp, pilot_file, quant_dims, verify_routes


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "health"
    if cmd == "health":
        print(json.dumps(health(), indent=2))
        return 0
    if cmd == "verify":
        print(json.dumps(verify_routes(), indent=2))
        return 0
    if cmd == "draft":
        text = Path(argv[2]).read_text(encoding="utf-8") if len(argv) > 2 else sys.stdin.read()
        print(json.dumps(draft(text), indent=2))
        return 0
    if cmd == "interp":
        profile = Path(argv[2]).read_text(encoding="utf-8") if len(argv) > 2 else ""
        misc = Path(argv[3]).read_text(encoding="utf-8") if len(argv) > 3 else ""
        side = Path(argv[4]).read_text(encoding="utf-8") if len(argv) > 4 else ""
        print(json.dumps(interp(profile, misc, side), indent=2))
        return 0
    if cmd == "quant":
        print(json.dumps(quant_dims([float(x) for x in argv[2:]]), indent=2))
        return 0
    if cmd == "fix":
        # fix height 8 nico "tape measure"
        field, value, by = argv[2], argv[3], argv[4]
        note = " ".join(argv[5:]) if len(argv) > 5 else ""
        print(json.dumps(fix(field, value, by, note), indent=2))
        return 0
    if cmd == "pilot" and len(argv) > 2:
        side = Path(argv[3]).read_text(encoding="utf-8") if len(argv) > 3 else ""
        print(json.dumps(pilot_file(Path(argv[2]), side), indent=2, default=str))
        return 0
    if cmd == "serve":
        from software.legacy_desk.server import serve

        return serve()
    print("health | verify | draft | interp | quant | fix <field> <value> <who> [note] | pilot | serve")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
