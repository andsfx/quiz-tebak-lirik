#!/usr/bin/env python3
from __future__ import annotations

import gzip
import html
import json
import re
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"

LYRIC_HOSTS = (
    "azlyrics.com",
    "genius.com",
    "musixmatch.com",
    "lyrics.com",
    "songlyrics.com",
    "lirik.kapanlagi.com",
    "liriklaguindonesia.net",
    "sonora.id",
)

BAD_LINE_RE = re.compile(r"(cookie|privacy|copyright|embed|share|login|sign up|advert|iklan|ringtone|youtube|facebook|twitter|instagram|contributor|translation|verified|album|writer|composer|publisher|license)", re.I)
TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_RE = re.compile(r"<(script|style|noscript).*?</\1>", re.I | re.S)


def fetch(url: str, timeout: int = 12) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "id,en;q=0.8", "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read(1_500_000)
        if (r.headers.get("Content-Encoding") or "").lower() == "gzip":
            raw = gzip.decompress(raw)
        enc = r.headers.get_content_charset() or "utf-8"
        return raw.decode(enc, "replace")


def search_duckduckgo(query: str) -> list[str]:
    url = "https://duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    text = fetch(url)
    urls: list[str] = []
    for m in re.finditer(r'class="result__a"[^>]+href="([^"]+)"', text):
        href = html.unescape(m.group(1))
        if "uddg=" in href:
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
            href = qs.get("uddg", [href])[0]
        if href.startswith("http") and href not in urls:
            urls.append(href)
    return urls[:8]


def clean_text_from_html(raw: str) -> str:
    raw = SCRIPT_RE.sub("\n", raw)
    raw = re.sub(r"<br\s*/?>", "\n", raw, flags=re.I)
    raw = re.sub(r"</p>|</div>|</li>|</h\d>", "\n", raw, flags=re.I)
    raw = TAG_RE.sub(" ", raw)
    raw = html.unescape(raw)
    raw = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]+", " ", raw)
    raw = raw.replace("\r", "\n")
    raw = re.sub(r"[ \t]+", " ", raw)
    raw = re.sub(r"\n[ \t]+", "\n", raw)
    return raw


def score_line(line: str) -> bool:
    s = line.strip()
    if len(s) < 4 or len(s) > 90:
        return False
    if BAD_LINE_RE.search(s):
        return False
    if re.search(r"https?://|www\.", s):
        return False
    if sum(ch.isalpha() for ch in s) < 3:
        return False
    return True


def split_lyrics_text(text: str) -> list[str]:
    text = html.unescape(text)
    text = re.sub(r"(?<=[a-zA-ZÀ-ÿ])(?=[A-ZÀ-Ý])", "\n", text)
    text = re.sub(r" {2,}", "\n", text)
    return [re.sub(r"\s+", " ", ln).strip(" -\t") for ln in text.split("\n")]


def extract_lyrics(raw: str, title: str, artist: str) -> list[str]:
    m = re.search(r'"lyrics"\s*:\s*\{[^{}]*"text"\s*:\s*"((?:\\.|[^"\\])*)"', raw, re.S)
    if m:
        try:
            decoded = json.loads('"' + m.group(1) + '"')
            json_lines = [ln for ln in split_lyrics_text(decoded) if score_line(ln)]
            if len(json_lines) >= 4:
                return json_lines[:80]
        except Exception:
            pass
    text = clean_text_from_html(raw)
    lines = [re.sub(r"\s+", " ", ln).strip(" -\t") for ln in text.split("\n")]
    lines = [ln for ln in lines if score_line(ln)]

    # Remove repeated headers and site chrome around obvious title/artist noise.
    title_words = set(re.findall(r"\w+", title.lower()))
    artist_words = set(re.findall(r"\w+", artist.lower()))
    out: list[str] = []
    seen = set()
    for ln in lines:
        low = ln.lower()
        words = set(re.findall(r"\w+", low))
        if len(words & title_words) >= max(1, min(2, len(title_words))) and ("lirik" in low or "lyrics" in low):
            continue
        if len(words & artist_words) >= max(1, min(2, len(artist_words))) and len(ln) < 35:
            continue
        key = re.sub(r"\W+", "", low)
        if key in seen:
            continue
        seen.add(key)
        out.append(ln)

    # Pick longest contiguous lyric-like run.
    best: list[str] = []
    cur: list[str] = []
    for ln in out:
        if score_line(ln):
            cur.append(ln)
        else:
            if len(cur) > len(best):
                best = cur
            cur = []
    if len(cur) > len(best):
        best = cur
    return best[:80]


def make_quiz_from_lines(lines: list[str]) -> tuple[str, str]:
    usable = [ln for ln in lines if 8 <= len(ln) <= 70]
    if len(usable) < 4:
        return "", ""
    # Avoid first line if likely title. Take first clean 2+2 sequence.
    return "\n".join(usable[:2]), "\n".join(usable[2:4])


def find_lrclib(title: str, artist: str) -> dict | None:
    clean_title = title.replace("&", "dan")
    url = "https://lrclib.net/api/search?" + urllib.parse.urlencode({"track_name": clean_title, "artist_name": artist})
    try:
        data = json.loads(fetch(url))
    except Exception:
        return None
    title_l = title.lower(); artist_l = artist.lower()
    for item in data[:8]:
        plain = (item.get("plainLyrics") or "").strip()
        if not plain:
            continue
        if title_l.split()[0] not in (item.get("trackName") or "").lower():
            continue
        lines = [ln.strip() for ln in plain.splitlines() if score_line(ln.strip())]
        if len(lines) < 4:
            continue
        bait, answer = make_quiz_from_lines(lines)
        if bait and answer:
            return {"status":"verified","source":"https://lrclib.net","url":"https://lrclib.net","host":"lrclib.net","priority":True,"lineCount":len(lines),"lyrics":"\n".join(lines),"bait":bait,"answer":answer,"candidates":[]}
    return None


def find_lyrics(title: str, artist: str) -> dict:
    lrclib = find_lrclib(title, artist)
    if lrclib:
        return lrclib
    queries = [
        f'"{title}" "{artist}" lirik',
        f'"{title}" "{artist}" lyrics',
        f'{title} {artist} lirik lagu',
    ]
    candidates = []
    checked = []
    for q in queries:
        try:
            for url in search_duckduckgo(q):
                if url in checked:
                    continue
                checked.append(url)
                host = urllib.parse.urlparse(url).netloc.lower().replace("www.", "")
                priority = any(h in host for h in LYRIC_HOSTS)
                try:
                    raw = fetch(url)
                    lines = extract_lyrics(raw, title, artist)
                    if len(lines) >= 4:
                        bait, answer = make_quiz_from_lines(lines)
                        candidates.append({
                            "url": url,
                            "host": host,
                            "priority": priority,
                            "lineCount": len(lines),
                            "lyrics": "\n".join(lines),
                            "bait": bait,
                            "answer": answer,
                        })
                except Exception:
                    continue
        except Exception:
            continue
        if candidates:
            break
    candidates.sort(key=lambda c: (c["priority"], c["lineCount"]), reverse=True)
    if not candidates:
        return {"status": "missing", "sources": checked[:8], "lyrics": "", "bait": "", "answer": ""}
    best = candidates[0]
    # Conservative: only verified if two sources have similar opening lines.
    status = "unverified"
    if len(candidates) >= 2:
        a = re.sub(r"\W+", "", candidates[0]["lyrics"].lower()[:220])
        b = re.sub(r"\W+", "", candidates[1]["lyrics"].lower()[:220])
        if a and b and (a[:80] in b or b[:80] in a or len(set(a.split()) & set(b.split())) > 10):
            status = "verified"
        else:
            status = "needs_review"
    return {"status": status, "source": best["url"], "candidates": candidates[:3], **best}


