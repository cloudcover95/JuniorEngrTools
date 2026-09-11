from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from software.legacy_desk.endpoints import draft, health


class DeskTests(unittest.TestCase):
    def test_health(self):
        h = health()
        self.assertEqual(h["bind"], "127.0.0.1:8766")
        self.assertEqual(h["port"], "JuniorBitNetDraft")

    def test_draft_local(self):
        d = draft("TITLE: BRACKET\nELEV FRONT\nHEIGHT: 8")
        self.assertTrue(d["port"].startswith("JuniorBitNetDraft"))
        self.assertIn("rec", d)


if __name__ == "__main__":
    unittest.main(verbosity=2)
