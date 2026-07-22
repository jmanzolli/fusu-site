#!/usr/bin/env python3
"""Gera assets/data/episodes.json a partir do feed RSS do podcast.

Uso:  python3 scripts/build_episodes.py
Depois:  git add -A && git commit -m "conteudo: atualiza episodios" && git push --no-thin origin main
"""

import html
import json
import os
import re
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

FEED = "https://anchor.fm/s/e7f23af4/podcast/rss"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "data", "episodes.json")
IMG_DIR = os.path.join(ROOT, "assets", "img", "ep")
NS = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}

MESES = ["jan", "fev", "mar", "abr", "mai", "jun",
         "jul", "ago", "set", "out", "nov", "dez"]


def strip_html(raw: str) -> str:
    txt = re.sub(r"<br\s*/?>", "\n", raw or "")
    txt = re.sub(r"</p>", "\n\n", txt)
    txt = re.sub(r"<[^>]+>", "", txt)
    txt = html.unescape(txt)
    txt = txt.replace("⁠", "").replace("⁩", "").replace("⁦", "")
    txt = re.sub(r"[ \t]+", " ", txt)
    return re.sub(r"\n{3,}", "\n\n", txt).strip()


def slugify(text: str) -> str:
    import unicodedata
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t[:60]


def fmt_duration(d: str) -> str:
    if not d:
        return ""
    parts = [int(p) for p in d.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    h, m, s = parts
    return f"{h}h{m:02d}" if h else f"{m} min"


def duration_seconds(d: str) -> int:
    if not d:
        return 0
    parts = [int(p) for p in d.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def download_cover(url: str, slug: str) -> str:
    """Baixa a capa do episódio e reduz para 400px (sips, macOS)."""
    if not url:
        return ""
    os.makedirs(IMG_DIR, exist_ok=True)
    ext = ".jpg"
    path = os.path.join(IMG_DIR, slug + ext)
    rel = f"assets/img/ep/{slug}{ext}"
    if os.path.exists(path):
        return rel
    try:
        urllib.request.urlretrieve(url, path)
        subprocess.run(["sips", "-Z", "400", path], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return rel
    except Exception as exc:  # noqa: BLE001
        print(f"  ! capa falhou ({slug}): {exc}")
        return ""


def main() -> None:
    print(f"A ler {FEED} ...")
    with urllib.request.urlopen(FEED) as resp:
        root = ET.fromstring(resp.read())

    channel = root.find("channel")
    episodes = []

    for item in channel.findall("item"):
        title = (item.findtext("title") or "").strip()
        pub = item.findtext("pubDate")
        dt = parsedate_to_datetime(pub) if pub else datetime.now()
        enclosure = item.find("enclosure")
        img_el = item.find("itunes:image", NS)

        slug = slugify(title)
        kind = "pilula" if title.lower().startswith("pílula") else "episodio"
        season = item.findtext("itunes:season", default="", namespaces=NS)

        # Pílulas antigas não trazem temporada: inferir pela data.
        if not season:
            season = "2" if dt.year >= 2025 else "1"

        episodes.append({
            "id": slug,
            "title": title,
            "kind": kind,
            "season": int(season),
            "number": item.findtext("itunes:episode", default="", namespaces=NS),
            "date": dt.strftime("%Y-%m-%d"),
            "dateLabel": f"{dt.day} {MESES[dt.month - 1]} {dt.year}",
            "duration": fmt_duration(item.findtext("itunes:duration", default="", namespaces=NS)),
            "seconds": duration_seconds(item.findtext("itunes:duration", default="", namespaces=NS)),
            "audio": enclosure.get("url") if enclosure is not None else "",
            "link": item.findtext("link") or "",
            "cover": download_cover(img_el.get("href") if img_el is not None else "", slug),
            "description": strip_html(item.findtext("description") or ""),
        })

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({
            "updated": datetime.now().strftime("%Y-%m-%d"),
            "count": len(episodes),
            "episodes": episodes,
        }, fh, ensure_ascii=False, indent=1)

    print(f"OK — {len(episodes)} episódios em {OUT}")


if __name__ == "__main__":
    main()
