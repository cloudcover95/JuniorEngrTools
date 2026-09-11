"""Loopback JSON API. No 0.0.0.0."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from software.legacy_desk.endpoints import draft, health


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: dict) -> None:
        raw = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/health"):
            self._send(200, health())
            return
        self._send(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        n = int(self.headers.get("Content-Length") or 0)
        payload = json.loads(self.rfile.read(n) or b"{}")
        if self.path.startswith("/draft"):
            self._send(200, draft(str(payload.get("sidecar") or "")))
            return
        self._send(404, {"error": "not_found"})

    def log_message(self, fmt: str, *args) -> None:
        return


def serve(host: str = "127.0.0.1", port: int = 8766) -> int:
    if host != "127.0.0.1":
        raise RuntimeError("loopback only")
    print(json_dumps := f"legacy desk http://{host}:{port}/health")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
    return 0
