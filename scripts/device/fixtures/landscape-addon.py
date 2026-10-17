#!/usr/bin/env python3
"""A one-file Stremio add-on whose single catalog is a row of LANDSCAPE cards (posterShape).

Device fixture for Batch B B4 (BUG-162 + BUG-163, Steven's rc4 verdict): install it in the Test
profile, set Poster Size to Medium+ and look at the "Landscape Row (fixture)" row on Home: the 16:9
cards must be as tall as the portrait cards one row up, the heading right above them, and the
focused card's in-row trailer must show a picture (not audio only). Serves manifest.json, the
catalog (`/catalog/movie/zzland.json`, with or without extras) and one meta per id
(`/meta/movie/<id>.json`) with a YouTube trailer, so the inline trailer has something to play.
Posters are metahub's 16:9 backdrops of well-known titles; the ids carry the fixture's own prefix
so Cinemeta never answers for them. Permissive CORS; no streams.

    python3 scripts/device/fixtures/landscape-addon.py [port]
    -> http://<mac-lan-ip>:<port>/manifest.json   (default port 8766)
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
PREFIX = "zzland"

# (slug, name, imdb id for metahub art, year, YouTube trailer id, genres)
TITLES = [
    ("dune", "Dune: Part One", "tt1160419", "2021", "n9xhJrPXop4", ["Science Fiction", "Adventure"]),
    ("oppenheimer", "Oppenheimer", "tt15398776", "2023", "uYPbbksJxIg", ["Drama", "History"]),
    ("interstellar", "Interstellar", "tt0816692", "2014", "zSWdZVtXT7E", ["Science Fiction", "Drama"]),
    ("bladerunner", "Blade Runner 2049", "tt1856101", "2017", "gCcx85zbxz4", ["Science Fiction", "Thriller"]),
    ("maverick", "Top Gun: Maverick", "tt1745960", "2022", "giXco2jaZ_4", ["Action", "Drama"]),
    ("inception", "Inception", "tt1375666", "2010", "YoHD9XEInc0", ["Action", "Science Fiction"]),
    ("darkknight", "The Dark Knight", "tt0468569", "2008", "EXeTwQWrcwY", ["Action", "Crime"]),
    ("nowayhome", "Spider-Man: No Way Home", "tt10872600", "2021", "JfVOs4VSpmA", ["Action", "Adventure"]),
]


def meta(slug, name, imdb, year, yt, genres):
    return {
        "id": f"{PREFIX}-{slug}",
        "type": "movie",
        "name": name,
        "posterShape": "landscape",
        # 16:9 art in the poster slot: that is what makes a shape-landscape row (BUG-157/162).
        "poster": f"https://images.metahub.space/background/medium/{imdb}/img",
        "background": f"https://images.metahub.space/background/large/{imdb}/img",
        "logo": f"https://images.metahub.space/logo/medium/{imdb}/img",
        "releaseInfo": year,
        "year": int(year),
        "genres": genres,
        "description": f"{name} ({year}). Batch B B4 landscape-row fixture; the trailer is the title's own.",
        "trailers": [{"source": yt, "type": "Trailer"}],
    }


METAS = [meta(*t) for t in TITLES]
BY_ID = {m["id"]: m for m in METAS}

MANIFEST = {
    "id": "org.nuviotv.fixture.landscape",
    "version": "1.0.0",
    "name": "Landscape fixture",
    "description": "Batch B B4 device fixture: one catalog of posterShape landscape cards with trailers.",
    "resources": ["catalog", "meta"],
    "types": ["movie"],
    "idPrefixes": [PREFIX],
    "catalogs": [{"type": "movie", "id": PREFIX, "name": "Landscape Row (fixture)"}],
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
        # /catalog/movie/zzland.json and /catalog/movie/zzland/skip=0.json (extras) alike
        if path.startswith(f"/catalog/movie/{PREFIX}") and path.endswith(".json"):
            return self._send({"metas": METAS})
        if path.startswith("/meta/movie/") and path.endswith(".json"):
            item_id = path[len("/meta/movie/"):-len(".json")]
            if item_id in BY_ID:
                return self._send({"meta": BY_ID[item_id]})
        return self._send({"error": "not found"}, 404)

    def log_message(self, fmt, *args):
        sys.stderr.write("[landscape-addon] " + (fmt % args) + "\n")


if __name__ == "__main__":
    print(f"[landscape-addon] serving on 0.0.0.0:{PORT}, {len(METAS)} landscape metas", flush=True)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
