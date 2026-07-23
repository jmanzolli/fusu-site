#!/usr/bin/env python3
"""Lê o RSS do podcast e gera:

  assets/data/episodes.json   — dados usados pela home e pela lista de episódios
  assets/img/ep/<slug>.jpg    — capas
  episodios/<slug>.html       — uma página por episódio (com player e dados estruturados)

Uso:  python3 scripts/build_episodes.py
"""

from __future__ import annotations

import html
import json
import os
import re
import subprocess
import sys
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import template as T  # noqa: E402

FEED = T.RSS
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "data", "episodes.json")
IMG_DIR = os.path.join(ROOT, "assets", "img", "ep")
PAGE_DIR = os.path.join(ROOT, "episodios")
NS = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}

MESES = ["jan", "fev", "mar", "abr", "mai", "jun",
         "jul", "ago", "set", "out", "nov", "dez"]


# --- Normalização pt-PT -> pt-BR das descrições vindas do RSS -----------------
# Só grafia e vocabulário: nenhum fato, nome ou número é alterado.
# Prefixo europeu -> prefixo brasileiro. Uma passagem só, com fronteira de palavra,
# para não reescrever uma substituição já feita.
PTBR_STEMS = {
    "prémio": "prêmio",
    "económ": "econôm",
    "autónom": "autônom",
    "anónim": "anônim",
    "sinónim": "sinônim",
    "fenómen": "fenômen",
    "eletrónic": "eletrônic",
    "electrónic": "eletrônic",
    "polémic": "polêmic",
    "académ": "acadêm",
    "génio": "gênio",
    "ténue": "tênue",
    "cómod": "cômod",
    "facto": "fato",
    "factos": "fatos",
    "contacto": "contato",
    "contactos": "contatos",
    "óptim": "ótim",
    "partilhar": "compartilhar",
    "partilhando": "compartilhando",
    "partilhado": "compartilhado",
    "partilhada": "compartilhada",
    "partilhamos": "compartilhamos",
    "partilham": "compartilham",
    "partilha": "compartilha",
    "sector": "setor",
    "sectores": "setores",
    "objectivo": "objetivo",
    "objectivos": "objetivos",
    "acção": "ação",
    "acções": "ações",
    "equipa": "equipe",
    "connosco": "conosco",
    "utilizador": "usuário",
    "ecrã": "tela",
    "telemóvel": "celular",
    "autocarro": "ônibus",
    "comboio": "trem",
}

STEM_RE = re.compile(
    r"\b(" + "|".join(sorted(PTBR_STEMS, key=len, reverse=True)) + r")",
    re.IGNORECASE,
)


def _swap_stem(match: re.Match) -> str:
    found = match.group(1)
    novo = PTBR_STEMS[found.lower()]
    return novo.capitalize() if found[0].isupper() else novo

# "está a transformar" -> "está transformando"
PROGRESSIVE = re.compile(
    r"\b(est(?:á|ão|ava|avam|ivera[m]?|arão|aria[m]?)|"
    r"continua|continuam|continuava|continuavam|"
    r"anda|andam|segue|seguem)\s+a\s+([a-zçãáéíóúâêôõà]+?)(ar|er|ir)\b",
    re.IGNORECASE,
)

GERUND = {"ar": "ando", "er": "endo", "ir": "indo"}


def to_ptbr(text: str) -> str:
    """Passa a grafia europeia para a brasileira, preservando o conteúdo."""
    text = STEM_RE.sub(_swap_stem, text)
    return PROGRESSIVE.sub(lambda m: f"{m.group(1)} {m.group(2)}{GERUND[m.group(3).lower()]}", text)


# O feed repete um rodapé de redes sociais em cada episódio — corta-se na geração.
FEED_FOOTER = re.compile(r"\n\s*--\s*\n.*$", re.S)


def strip_html(raw: str) -> str:
    txt = re.sub(r"<br\s*/?>", "\n", raw or "")
    txt = re.sub(r"</p>", "\n\n", txt)
    txt = re.sub(r"<[^>]+>", "", txt)
    txt = html.unescape(txt)
    for ch in ("⁠", "⁩", "⁦", "​"):
        txt = txt.replace(ch, "")
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = FEED_FOOTER.sub("", txt)
    return re.sub(r"\n{3,}", "\n\n", txt).strip()


def slugify(text: str) -> str:
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()[:60]


def fmt_duration(d: str) -> str:
    if not d:
        return ""
    parts = [int(p) for p in d.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    h, m, _ = parts
    return f"{h}h{m:02d}" if h else f"{m} min"


def duration_seconds(d: str) -> int:
    if not d:
        return 0
    parts = [int(p) for p in d.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def iso_duration(seconds: int) -> str:
    return f"PT{seconds // 60}M{seconds % 60}S"


def download_cover(url: str, slug: str) -> str:
    if not url:
        return ""
    os.makedirs(IMG_DIR, exist_ok=True)
    path = os.path.join(IMG_DIR, f"{slug}.jpg")
    rel = f"assets/img/ep/{slug}.jpg"
    if os.path.exists(path):
        return rel
    try:
        urllib.request.urlretrieve(url, path)
        subprocess.run(["sips", "-Z", "500", path], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return rel
    except Exception as exc:  # noqa: BLE001
        print(f"  ! capa falhou ({slug}): {exc}")
        return ""


def kind_label(ep: dict) -> str:
    return "Pílula" if ep["kind"] == "pilula" else "Entrevista"


def build_page(ep: dict, newer: dict | None, older: dict | None) -> str:
    label = kind_label(ep)
    summary = re.sub(r"\s+", " ", ep["description"])[:200].strip()
    paragraphs = "\n        ".join(
        f"<p>{html.escape(p)}</p>" for p in ep["description"].split("\n\n") if p.strip()
    ) or "<p>Episódio disponível nas plataformas de áudio.</p>"

    url = f"{T.SITE_URL}/episodios/{ep['id']}.html"
    cover_url = f"{T.SITE_URL}/{ep['cover']}" if ep["cover"] else f"{T.SITE_URL}/assets/img/fusu-poster.webp"

    jsonld = json.dumps([
        {
            "@context": "https://schema.org",
            "@type": "PodcastEpisode",
            "url": url,
            "name": ep["title"],
            "datePublished": ep["date"],
            "timeRequired": iso_duration(ep["seconds"]),
            "description": summary,
            "image": cover_url,
            "inLanguage": "pt",
            "associatedMedia": {"@type": "MediaObject", "contentUrl": ep["audio"]},
            "partOfSeries": {
                "@type": "PodcastSeries",
                "name": "FuSu — Futuro Sustentável",
                "url": f"{T.SITE_URL}/",
            },
            "partOfSeason": {"@type": "PodcastSeason", "seasonNumber": ep["season"]},
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Início", "item": f"{T.SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Episódios", "item": f"{T.SITE_URL}/episodios.html"},
                {"@type": "ListItem", "position": 3, "name": ep["title"], "item": url},
            ],
        },
    ], ensure_ascii=False, indent=1)

    pager = []
    if older:
        pager.append(f'<a class="pager__item" href="{older["id"]}.html"><span>← Anterior</span>{html.escape(older["title"])}</a>')
    if newer:
        pager.append(f'<a class="pager__item pager__item--next" href="{newer["id"]}.html"><span>Seguinte →</span>{html.escape(newer["title"])}</a>')
    pager_html = f'<nav class="pager" aria-label="Outros episódios">{"".join(pager)}</nav>' if pager else ""

    chip_class = "chip chip--pill" if ep["kind"] == "pilula" else "chip chip--talk"

    cover_img = (f'<img class="featured__cover" src="../{ep["cover"]}" alt="Capa do episódio {html.escape(ep["title"])}" '
                 f'width="400" height="400">') if ep["cover"] else ""

    return f"""{T.head(f"{ep['title']} | FuSu", summary, cover_url, '../', url, jsonld)}

{T.nav('../', 'episodios')}

<main id="conteudo">
  <article>
    <header class="page-hero">
      <div class="wrap">
        <p class="crumbs"><a href="../index.html">Início</a> / <a href="../episodios.html">Episódios</a></p>
        <div class="featured">
          {cover_img}
          <div>
            <p class="chips" style="margin-bottom:16px">
              <span class="{chip_class}">{label}</span>
              <span class="chip chip--soft">Temporada {ep['season']}</span>
            </p>
            <h1>{html.escape(ep['title'])}</h1>
            <p class="meta" style="margin-top:16px">{ep['dateLabel']}<span>{ep['duration']}</span></p>

            <audio controls preload="none" src="{ep['audio']}" style="width:100%;margin-top:28px">
              O seu navegador não reproduz áudio. <a href="{ep['link']}">Ouça no Spotify</a>.
            </audio>

            <ul class="platforms" style="margin-top:24px">
              <li><a href="{ep['link']}" target="_blank" rel="noopener">Abrir no Spotify</a></li>
              <li><a href="{T.APPLE}" target="_blank" rel="noopener">Apple Podcasts</a></li>
              <li><a href="{T.DEEZER}" target="_blank" rel="noopener">Deezer</a></li>
            </ul>
          </div>
        </div>
      </div>
    </header>

    <div class="section">
      <div class="wrap">
        <div class="post-body">
          {paragraphs}
          <p style="margin-top:32px"><a class="btn btn--outline" href="../episodios.html">Ver todos os episódios</a></p>
          {pager_html}
        </div>
      </div>
    </div>
  </article>
</main>

{T.support('../')}

{T.footer('../')}"""


def main() -> None:
    print(f"A ler {FEED} …")
    with urllib.request.urlopen(FEED) as resp:
        root = ET.fromstring(resp.read())

    episodes = []
    for item in root.find("channel").findall("item"):
        title = (item.findtext("title") or "").strip()
        pub = item.findtext("pubDate")
        dt = parsedate_to_datetime(pub) if pub else datetime.now()
        enclosure = item.find("enclosure")
        img_el = item.find("itunes:image", NS)
        raw_duration = item.findtext("itunes:duration", default="", namespaces=NS)

        season = item.findtext("itunes:season", default="", namespaces=NS)
        if not season:
            season = "2" if dt.year >= 2025 else "1"

        slug = slugify(title)
        episodes.append({
            "id": slug,
            "title": title,
            "kind": "pilula" if title.lower().startswith("pílula") else "episodio",
            "season": int(season),
            "number": item.findtext("itunes:episode", default="", namespaces=NS),
            "date": dt.strftime("%Y-%m-%d"),
            "dateLabel": f"{dt.day} {MESES[dt.month - 1]} {dt.year}",
            "duration": fmt_duration(raw_duration),
            "seconds": duration_seconds(raw_duration),
            "audio": enclosure.get("url") if enclosure is not None else "",
            "link": item.findtext("link") or "",
            "cover": download_cover(img_el.get("href") if img_el is not None else "", slug),
            "description": to_ptbr(strip_html(item.findtext("description") or "")),
        })

    episodes.sort(key=lambda e: e["date"], reverse=True)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({
            "updated": datetime.now().strftime("%Y-%m-%d"),
            "count": len(episodes),
            "episodes": episodes,
        }, fh, ensure_ascii=False, indent=1)

    os.makedirs(PAGE_DIR, exist_ok=True)
    for i, ep in enumerate(episodes):
        newer = episodes[i - 1] if i > 0 else None
        older = episodes[i + 1] if i + 1 < len(episodes) else None
        with open(os.path.join(PAGE_DIR, f"{ep['id']}.html"), "w", encoding="utf-8") as fh:
            fh.write(build_page(ep, newer, older))

    print(f"OK — {len(episodes)} episódios: dados, capas e páginas em episodios/")


if __name__ == "__main__":
    main()
