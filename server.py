#!/usr/bin/env python3
from __future__ import annotations

import json
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from lyric_logic import find_lyrics

PORT = 8777
HOST = "0.0.0.0"


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/lyrics":
            qs = urllib.parse.parse_qs(parsed.query)
            title = (qs.get("title") or [""])[0].strip()
            artist = (qs.get("artist") or [""])[0].strip()
            if not title or not artist:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "title and artist required"}).encode())
                return
            try:
                data = find_lyrics(title, artist)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return
        return super().do_GET()


if __name__ == "__main__":
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
