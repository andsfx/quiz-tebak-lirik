#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from audio_logic import find_audio_preview, open_preview
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

    def do_HEAD(self):
        return self.do_GET()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/api/lyrics", "/api/audio", "/api/preview"):
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
                if parsed.path == "/api/preview":
                    data, upstream = open_preview(title, artist)
                    with upstream:
                        self.send_response(206 if upstream.status == 206 else 200)
                        self.send_header("Content-Type", "audio/mp4")
                        self.send_header("Cache-Control", "public, max-age=3600")
                        self.send_header("X-Audio-Source", data.get("source", ""))
                        self.send_header("X-Audio-Title", data.get("matchedTitle", ""))
                        if upstream.headers.get("Content-Length"):
                            self.send_header("Content-Length", upstream.headers.get("Content-Length"))
                        if upstream.headers.get("Accept-Ranges"):
                            self.send_header("Accept-Ranges", upstream.headers.get("Accept-Ranges"))
                        if upstream.headers.get("Content-Range"):
                            self.send_header("Content-Range", upstream.headers.get("Content-Range"))
                        self.end_headers()
                        if self.command != "HEAD":
                            shutil.copyfileobj(upstream, self.wfile)
                    return
                data = find_lyrics(title, artist) if parsed.path == "/api/lyrics" else find_audio_preview(title, artist)
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
