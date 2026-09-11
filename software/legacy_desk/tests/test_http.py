from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from software.legacy_desk.server import Handler


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.httpd.server_address[1]
        cls.t = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.t.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def _get(self, path: str) -> dict:
        with urlopen(f"http://127.0.0.1:{self.port}{path}", timeout=2) as r:
            return json.loads(r.read().decode())

    def _post(self, path: str, body: dict) -> dict:
        req = Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=2) as r:
            return json.loads(r.read().decode())

    def test_health_and_draft(self):
        h = self._get("/health")
        self.assertEqual(h["bind"], "127.0.0.1:8766")
        d = self._post("/draft", {"sidecar": "TITLE: BRACKET\nHEIGHT: 8\nELEV"})
        self.assertIn("plain", d)
        self.assertIn("build", d["plain"])

    def test_fix_signed(self):
        with tempfile.TemporaryDirectory() as td:
            p = str(Path(td) / "fixes.jsonl")
            out = self._post(
                "/fix",
                {"field": "height", "value": "7.5", "by": "nico", "note": "tape", "path": p},
            )
            self.assertTrue(out["ok"])
            self.assertTrue(out["allow_extrude"])
            self.assertFalse(out["interp_hypothesis"])
            self.assertEqual(out["fix"]["by"], "nico")


if __name__ == "__main__":
    unittest.main(verbosity=2)
