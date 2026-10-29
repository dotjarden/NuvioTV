#!/usr/bin/env python3
"""A one-file Stremio add-on that answers every stream request with a long, Torrentio-shaped list.

Device fixture for Wave 3c W3-16 (BUG-207, Steven's rc11 verdict: "stream selection page:
scrolling isn't smooth"). The Test profile has no real provider, so this stub gives the stream
picker 48 rows (default; `--rows N`) that look like a debrid provider's: a multi-line title
(release name, resolution, size, seeders, a language flag line), a `name` with a provider tag and
quality, and `behaviorHints` (bingeGroup, filename). Every stream points at the same local URL
(served by scripts/device/range_server.py, or any URL: the rows are for scrolling, not playing).
Measure with Animation Hitches over 30 Down + 30 Up at 0.35 s before and after the W3-16 change.
Permissive CORS; no catalogs.

    python3 scripts/device/fixtures/picker-rows-addon.py [port] [--rows N] [--media URL]
        [--id <manifest id>] [--name <display name>] [--manifest-delay <seconds>]
    -> http://<mac-lan-ip>:<port>/manifest.json   (default port 8769, 48 rows)

`--id` / `--name` let two instances run as two distinct add-ons (Add-ons hub H5 device pass:
install, reorder, remove); `--manifest-delay` holds the manifest response for N seconds so the
install sheet's Checking phase can be watched (Menu during Checking must not close the sheet).
"""
import json
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8769
ROWS = 48
MEDIA = "http://192.168.1.127:8011/fixture-short.mp4"
ADDON_ID = "org.nuviotv.fixture.pickerrows"
NAME = "Picker Rows fixture"
MANIFEST_DELAY = 0.0
args = sys.argv[1:]
if args and args[0].isdigit():
    PORT = int(args.pop(0))
while args:
    flag = args.pop(0)
    if flag == "--rows" and args:
        ROWS = int(args.pop(0))
    elif flag == "--media" and args:
        MEDIA = args.pop(0)
    elif flag == "--id" and args:
        ADDON_ID = args.pop(0)
    elif flag == "--name" and args:
        NAME = args.pop(0)
    elif flag == "--manifest-delay" and args:
        MANIFEST_DELAY = float(args.pop(0))

MANIFEST = {
    "id": ADDON_ID,
    "version": "1.0.0",
    "name": NAME,
    "description": f"W3-16 device fixture: {ROWS} Torrentio-shaped streams for every title.",
    "resources": ["stream"],
    "types": ["movie", "series"],
    "idPrefixes": ["tt", "tmdb", "kitsu", "mal"],
    "catalogs": [],
    "behaviorHints": {"configurable": False, "configurationRequired": False},
}

RESOLUTIONS = ["2160p", "1080p", "1080p", "720p", "2160p", "1080p"]
SOURCES = ["WEB-DL", "BluRay", "WEBRip", "BluRay REMUX", "HDTV", "WEB-DL"]
CODECS = ["x265 HDR DV", "x264", "x265", "HEVC 10bit", "AVC", "x265 HDR10+"]
GROUPS = ["FLUX", "SPARKS", "CMRG", "PSA", "RARBG", "YTS", "NTb", "DON", "EVO", "QxR"]
AUDIO = ["DDP5.1 Atmos", "DD5.1", "AAC2.0", "TrueHD 7.1", "DTS-HD MA", "EAC3"]
FLAGS = ["🇬🇧 🇫🇷", "🇬🇧", "🇬🇧 🇩🇪 🇫🇷 🇪🇸", "🇫🇷", "🇬🇧 🇮🇹", "Multi"]


def stream(i: int):
    res = RESOLUTIONS[i % len(RESOLUTIONS)]
    src = SOURCES[i % len(SOURCES)]
    codec = CODECS[i % len(CODECS)]
    group = GROUPS[i % len(GROUPS)]
    audio = AUDIO[i % len(AUDIO)]
    size_gb = round(1.4 + (i * 1.73) % 38.0, 2)
    seeders = 5 + (i * 37) % 900
    filename = f"Fixture.Title.2026.{res}.{src.replace(' ', '.')}.{audio.replace(' ', '.')}.{codec.replace(' ', '.')}-{group}.mkv"
    return {
        "url": MEDIA,
        "name": f"[RD+] Torrentio\n{res}",
        "title": f"{filename}\n👤 {seeders} 💾 {size_gb} GB ⚙️ {'ThePirateBay' if i % 2 else 'YTS'}\n{FLAGS[i % len(FLAGS)]}",
        "behaviorHints": {
            "bingeGroup": f"torrentio|{res}|{src}|{codec}",
            "filename": filename,
            "videoSize": int(size_gb * 1024 * 1024 * 1024),
        },
    }


STREAMS = {"streams": [stream(i) for i in range(ROWS)]}


class Handler(BaseHTTPRequestHandler):
    def _send(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/manifest.json":
            if MANIFEST_DELAY > 0:
                time.sleep(MANIFEST_DELAY)
            return self._send(MANIFEST)
        if path.startswith("/stream/") and path.endswith(".json"):
            return self._send(STREAMS)
        return self._send({"error": "not found"}, 404)

    def log_message(self, fmt, *args):
        sys.stderr.write("[picker-rows-addon] " + (fmt % args) + "\n")


if __name__ == "__main__":
    print(f"[picker-rows-addon] serving on 0.0.0.0:{PORT}, rows={ROWS}, media={MEDIA}, id={ADDON_ID}, "
          f"name={NAME!r}, manifest-delay={MANIFEST_DELAY}s", flush=True)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
