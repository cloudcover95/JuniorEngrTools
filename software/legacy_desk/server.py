"""Loopback JSON API. No 0.0.0.0."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from software.legacy_desk.endpoints import draft, fix, health, interp, quant_dims, verify_routes
from software.legacy_desk.fixes import list_fixes


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: dict) -> None:
        raw = json.dumps(body, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/health"):
            self._send(200, health())
            return
        if self.path.startswith("/verify"):
            self._send(200, verify_routes())
            return
        if self.path.startswith("/fixes"):
            self._send(200, {"fixes": list_fixes()})
            return
        self._send(404, {"error": "not_found", "plain": "Unknown route. Try /health."})

    def do_POST(self) -> None:  # noqa: N802
        n = int(self.headers.get("Content-Length") or 0)
        payload = json.loads(self.rfile.read(n) or b"{}")
        if self.path.startswith("/draft"):
            self._send(200, draft(str(payload.get("sidecar") or ""), str(payload.get("profile") or ""), str(payload.get("misc") or "")))
            return
        if self.path.startswith("/interp"):
            self._send(200, interp(str(payload.get("profile") or ""), str(payload.get("misc") or ""), str(payload.get("sidecar") or "")))
            return
        if self.path.startswith("/quant"):
            vals = [float(x) for x in payload.get("values") or []]
            self._send(200, quant_dims(vals, str(payload.get("method") or "absmean")))
            return
        if self.path.startswith("/fix"):
            try:
                self._send(
                    200,
                    fix(
                        str(payload.get("field") or ""),
                        str(payload.get("value") or ""),
                        str(payload.get("by") or ""),
                        str(payload.get("note") or ""),
                        str(payload.get("was") or ""),
                        Path(payload["path"]) if payload.get("path") else None,
                    ),
                )
            except ValueError as exc:
                self._send(400, {"error": str(exc), "plain": "Need field, value, and your name."})
            return
        self._send(404, {"error": "not_found"})

    def log_message(self, fmt: str, *args) -> None:
        return


def serve(host: str = "127.0.0.1", port: int = 8766) -> int:
    if host != "127.0.0.1":
        raise RuntimeError("loopback only")
    print(f"legacy desk http://{host}:{port}/health")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
    return 0
