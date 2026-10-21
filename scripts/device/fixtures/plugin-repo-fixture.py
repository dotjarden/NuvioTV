#!/usr/bin/env python3
"""Device-pass fixture: a JS plugin REPOSITORY with four providers named out of A–Z order, for the
Settings › Sources › Plugins pane (BUG-197, GitHub #7: one row per provider, collapse, Remove alert).
    python3 scripts/device/fixtures/plugin-repo-fixture.py [port]
    -> http://<mac-lan-ip>:<port>/manifest.json   (default port 8768)
The scraper scripts are stubs that return no streams. Install through Settings › Sources › Plugins ›
the manifest URL field; remove the repository afterwards (it syncs to the account's profile).
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8768
SCRAPERS = [
    ("zeta", "Zeta Provider"), ("alpha", "alpha provider"), ("p10", "Provider 10"), ("p2", "Provider 2"),
]
MANIFEST = {
    "name": "Device-pass fixture repo",
    "version": "1.0.0",
    "description": "Four stub providers for the Plugins pane device pass.",
    "author": "nuviotv rig",
    "scrapers": [
        {"id": f"fixture-{sid}", "name": name, "description": "Stub, returns no streams.",
         "version": "1.0.0", "filename": f"{sid}.js", "supportedTypes": ["movie", "tv"], "enabled": True}
        for sid, name in SCRAPERS
    ],
}
STUB = "// device-pass stub provider\nasync function getStreams() { return []; }\n"


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?")[0] == "/manifest.json":
            body = json.dumps(MANIFEST).encode()
            ctype = "application/json"
        elif self.path.endswith(".js"):
            body = STUB.encode()
            ctype = "application/javascript"
        else:
            self.send_response(404); self.end_headers(); return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        sys.stderr.write("[plugin-fixture] " + (fmt % args) + "\n")


if __name__ == "__main__":
    print(f"serving plugin repository fixture on port {PORT}", flush=True)
    HTTPServer(("0.0.0.0", PORT), H).serve_forever()
