from __future__ import annotations

import json
import shutil
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from audio_logic import open_preview


class handler(BaseHTTPRequestHandler):
    def _json(self, status: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_HEAD(self):
        return self._serve(head_only=True)

    def do_GET(self):
        return self._serve(head_only=False)

    def _serve(self, head_only: bool):
        qs = parse_qs(urlparse(self.path).query)
        title = (qs.get("title") or [""])[0].strip()
        artist = (qs.get("artist") or [""])[0].strip()
        if not title or not artist:
            return self._json(400, {"error": "title and artist required"})
        try:
            data, upstream = open_preview(title, artist)
            with upstream:
                self.send_response(206 if upstream.status == 206 else 200)
                self.send_header("Content-Type", "audio/mp4")
                self.send_header("Access-Control-Allow-Origin", "*")
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
                if not head_only:
                    shutil.copyfileobj(upstream, self.wfile)
        except Exception as exc:
            return self._json(404, {"error": str(exc)})
