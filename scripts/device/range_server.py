#!/usr/bin/env python3
"""Minimal HTTP server with Range support and per-request logging (for feeding the Apple TV a fixture)."""
import os, re, sys, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

class H(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            self.send_error(404); return
        size = os.path.getsize(path); rng = self.headers.get("Range"); start, end = 0, size - 1; status = 200
        if rng:
            m = re.match(r"bytes=(\d*)-(\d*)", rng)
            if m:
                if m.group(1): start = int(m.group(1)); end = int(m.group(2)) if m.group(2) else size - 1
                else: start = max(0, size - int(m.group(2))); end = size - 1
                end = min(end, size - 1); status = 206
        self.send_response(status)
        self.send_header("Content-Type", "video/x-matroska"); self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        if status == 206: self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        sent = 0; t0 = time.time()
        try:
            with open(path, "rb") as f:
                f.seek(start); left = end - start + 1
                while left > 0:
                    chunk = f.read(min(65536, left))
                    if not chunk: break
                    self.wfile.write(chunk); sent += len(chunk); left -= len(chunk)
            how = "complete"
        except (BrokenPipeError, ConnectionResetError):
            how = "client-closed"
        sys.stderr.write(f"{time.strftime('%H:%M:%S')} {self.command} {self.path} range={rng} status={status} sent={sent} life={int((time.time()-t0)*1000)}ms end={how}\n"); sys.stderr.flush()
    def do_HEAD(self):
        path = self.translate_path(self.path)
        if not os.path.isfile(path): self.send_error(404); return
        self.send_response(200); self.send_header("Content-Type", "video/x-matroska"); self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(os.path.getsize(path))); self.end_headers()
    def log_message(self, *a): pass

os.chdir(sys.argv[2] if len(sys.argv) > 2 else ".")
ThreadingHTTPServer(("0.0.0.0", int(sys.argv[1])), H).serve_forever()
