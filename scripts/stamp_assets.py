#!/usr/bin/env python3
"""Carimba CSS e JS com um hash do conteúdo em todas as páginas.

Sem isso, quem já visitou o site continua a ver o CSS antigo até o cache expirar
(o GitHub Pages serve com max-age=600, mas o navegador costuma guardar por mais tempo).
Com o hash no endereço, qualquer alteração vira um arquivo novo para o navegador.

Uso:  python3 scripts/stamp_assets.py     (roda sozinho no fim dos outros scripts)
"""

from __future__ import annotations

import glob
import hashlib
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = ["assets/css/style.css", "assets/js/main.js", "assets/js/player.js"]


def short_hash(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha1(fh.read()).hexdigest()[:8]


def main() -> None:
    versions = {a: short_hash(os.path.join(ROOT, a)) for a in ASSETS}

    pages = (glob.glob(os.path.join(ROOT, "*.html"))
             + glob.glob(os.path.join(ROOT, "blog", "*.html"))
             + glob.glob(os.path.join(ROOT, "episodios", "*.html")))

    alterados = 0
    for page in pages:
        with open(page, encoding="utf-8") as fh:
            html = fh.read()
        antes = html

        for asset, versao in versions.items():
            nome = asset.split("/")[-1]
            # captura o caminho como está na página (../assets/…, /fusu-site/assets/…)
            html = re.sub(
                rf'((?:\.\./|/fusu-site/)?assets/(?:css|js)/{re.escape(nome)})(\?v=[a-f0-9]+)?',
                rf'\g<1>?v={versao}',
                html,
            )

        if html != antes:
            with open(page, "w", encoding="utf-8") as fh:
                fh.write(html)
            alterados += 1

    resumo = ", ".join(f"{a.split('/')[-1]}={v}" for a, v in versions.items())
    print(f"  versões: {resumo} ({alterados} páginas)")


if __name__ == "__main__":
    main()
