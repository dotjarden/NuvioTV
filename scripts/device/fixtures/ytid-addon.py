#!/usr/bin/env python3
"""A one-file Stremio add-on that answers every stream request with ONE ytId-only stream.

Device fixture for Batch D U2 (upstream 94976222): install it in the Test profile, open any
title's Sources, and the "YouTube (ytId fixture)" row must resolve through the trailer extractor
and play. Serves manifest.json + /stream/{type}/{id}.json with permissive CORS; no catalogs.

    python3 scripts/device/fixtures/ytid-addon.py [port] [videoId]
    -> http://<mac-lan-ip>:<port>/manifest.json   (default port 8765, default video dQw4w9WgXcQ)
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
VIDEO_ID = sys.argv[2] if len(sys.argv) > 2 else "dQw4w9WgXcQ"

MANIFEST = {
    "id": "org.nuviotv.fixture.ytid",
    "version": "1.0.0",
    "name": "ytId fixture",
    "description": "Batch D U2 device fixture: one ytId-only stream for every title.",
    "resources": ["stream"],
    "types": ["movie", "series"],
    "idPrefixes": ["tt", "tmdb", "kitsu", "mal"],
    "catalogs": [],
    "behaviorHints": {"configurable": False, "configurationRequired": False},
}


class Handler(BaseHTTPRequestHandler):
    def _send(self, payload, status=200):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/manifest.json":
            return self._send(MANIFEST)
        if path.startswith("/stream/") and path.endswith(".json"):
            return self._send({"streams": [{
                "ytId": VIDEO_ID,
                "name": "YouTube (ytId fixture)",
                "title": "Resolved on the device through the trailer extractor",
            }]})
        return self._send({"error": "not found"}, 404)

    def log_message(self, fmt, *args):
        sys.stderr.write("[ytid-addon] " + (fmt % args) + "\n")


if __name__ == "__main__":
    print(f"[ytid-addon] serving on 0.0.0.0:{PORT}, videoId={VIDEO_ID}", flush=True)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
