#!/usr/bin/env python3
"""A one-file Stremio add-on for the Player P5 device pass: one catalog with one short film
("P5 Fixture Short Film", 150 s, served by scripts/device/range_server.py from iosApp/build/smoke)
and two streams for it: one carrying `behaviorHints.audioDelayMs` (N1, per-stream audio delay)
and one without. The short length makes the end-of-film post-play screen (B22) reachable in two
minutes on either engine. Permissive CORS.

    python3 scripts/device/range_server.py 8011 NuvioMobile/iosApp/build/smoke &
    python3 scripts/device/fixtures/audio-delay-addon.py [port] [media-base-url]
    -> http://<mac-lan-ip>:<port>/manifest.json   (default port 8767, media http://192.168.1.127:8011)
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8767
MEDIA = sys.argv[2] if len(sys.argv) > 2 else "http://192.168.1.127:8011"
ID = "zzp5-short"
POSTER = "https://images.metahub.space/poster/medium/tt1160419/img"

MANIFEST = {
    "id": "org.nuviotv.fixture.p5",
    "version": "1.0.0",
    "name": "P5 Fixture",
    "description": "Device-pass fixture: a 150 s film with an audioDelayMs stream hint.",
    "resources": ["catalog", "meta", "stream"],
    "types": ["movie"],
    "idPrefixes": ["zzp5"],
    "catalogs": [{"type": "movie", "id": "zzp5", "name": "P5 Fixture (fixture)"}],
}
META = {
    "id": ID, "type": "movie", "name": "P5 Fixture Short Film", "year": "2026",
    "description": "Test pattern with a 440 Hz tone, 150 seconds. Ends quickly on purpose.",
    "poster": POSTER, "background": "https://images.metahub.space/background/medium/tt1160419/img",
    "genres": ["Test"], "runtime": "3 min",
}
STREAMS = [
    {"url": f"{MEDIA}/fixture-short.mp4", "name": "P5 Fixture", "title": "Direct · audioDelayMs=1500 (N1 hint)",
     "behaviorHints": {"audioDelayMs": 1500}},
    {"url": f"{MEDIA}/fixture-short.mp4", "name": "P5 Fixture", "title": "Direct · no hint"},
]


class Handler(BaseHTTPRequestHandler):
    def _send(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/manifest.json":
            return self._send(MANIFEST)
        if path.startswith("/catalog/movie/zzp5"):
            return self._send({"metas": [META]})
        if path == f"/meta/movie/{ID}.json":
            return self._send({"meta": META})
        if path == f"/stream/movie/{ID}.json":
            return self._send({"streams": STREAMS})
        return self._send({"error": "not found"}, 404)

    def log_message(self, fmt, *args):
        sys.stderr.write("[p5-addon] " + (fmt % args) + "\n")


if __name__ == "__main__":
    print(f"[p5-addon] serving on 0.0.0.0:{PORT}, media {MEDIA}", flush=True)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
