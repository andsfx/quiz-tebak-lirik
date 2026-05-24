from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.load(r)


def tokens(text: str) -> list[str]:
    return [w for w in re.findall(r"[\wÀ-ÿ]+", text.lower().replace("&", " ")) if len(w) > 1 and w not in {"and", "the"}]


def score_text(title2: str, artist2: str, title: str, artist: str) -> int:
    text = f"{title2} {artist2}".lower()
    score = sum(w in text for w in tokens(title)) * 3 + sum(w in text for w in tokens(artist)) * 2
    if title2.lower().strip(" .") == title.lower().strip(" ."):
        score += 8
    if artist.lower().replace("and", "&") in artist2.lower().replace("and", "&"):
        score += 4
    return score


def find_itunes_preview(title: str, artist: str) -> dict:
    q = urllib.parse.urlencode({"term": f"{title} {artist}", "media": "music", "entity": "song", "limit": 25, "country": "ID"})
    data = fetch_json(f"https://itunes.apple.com/search?{q}")
    candidates = []
    for item in data.get("results", []):
        preview = item.get("previewUrl")
        if not preview:
            continue
        candidates.append({
            "preview": preview,
            "source": "itunes",
            "sourceUrl": item.get("trackViewUrl", ""),
            "matchedTitle": item.get("trackName", ""),
            "matchedArtist": item.get("artistName", ""),
            "score": score_text(item.get("trackName", ""), item.get("artistName", ""), title, artist),
            "previewSeconds": 30,
        })
    if not candidates:
        raise ValueError("itunes preview not found")
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[0]


def find_deezer_preview(title: str, artist: str) -> dict:
    q = urllib.parse.quote(f"{title} {artist}")
    data = fetch_json(f"https://api.deezer.com/search?q={q}")
    candidates = []
    for item in data.get("data", [])[:20]:
        preview = item.get("preview")
        if not preview:
            continue
        candidates.append({
            "preview": preview,
            "source": "deezer",
            "sourceUrl": item.get("link", ""),
            "matchedTitle": item.get("title", ""),
            "matchedArtist": item.get("artist", {}).get("name", ""),
            "score": score_text(item.get("title", ""), item.get("artist", {}).get("name", ""), title, artist),
            "previewSeconds": 30,
        })
    if not candidates:
        raise ValueError("deezer preview not found")
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[0]


def find_audio_preview(title: str, artist: str) -> dict:
    best = None
    errors = []
    for fn in (find_itunes_preview, find_deezer_preview):
        try:
            cand = fn(title, artist)
            if best is None or cand["score"] > best["score"]:
                best = cand
        except Exception as exc:
            errors.append(str(exc))
    if not best:
        raise ValueError("; ".join(errors) or "preview not found")
    return best


def open_preview(title: str, artist: str):
    data = find_audio_preview(title, artist)
    req = urllib.request.Request(data["preview"], headers={"User-Agent": UA})
    return data, urllib.request.urlopen(req, timeout=20)
