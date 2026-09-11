from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from software.quant.ternary import absmax_act, absmean, i2s_pack, report


class TernaryTests(unittest.TestCase):
    def test_absmean_clamps(self):
        t, sc = absmean([0.01, 2.0, -2.0, 0.0])
        self.assertTrue(all(x in (-1, 0, 1) for x in t))
        self.assertGreater(sc, 0)

    def test_i2s_roundtrip_len(self):
        t, _ = absmean([1.0, -1.0, 0.2, 0.0] * 4)
        packed = i2s_pack(t)
        self.assertGreaterEqual(len(packed), 2)

    def test_absmax(self):
        q, s = absmax_act([1.0, -0.5])
        self.assertTrue(all(-127 <= x <= 127 for x in q))
        self.assertEqual(report([1.0, 0.0, -1.0]).method, "absmean")


if __name__ == "__main__":
    unittest.main(verbosity=2)
