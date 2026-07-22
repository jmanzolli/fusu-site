#!/usr/bin/env python3
"""Gera o blog a partir de assets/data/posts.json.

Cria:
  blog/index.html          — lista de todos os posts
  blog/<slug>.html         — uma página por post
  e reescreve o bloco de destaques do blog em index.html (entre marcadores).

Uso:  python3 scripts/build_blog.py
"""

from __future__ import annotations

import json
import os

# URL pública do site — trocar quando o domínio próprio for ativado
SITE_URL = "https://www.jonatasmanzolli.com/fusu-site"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "assets", "data", "posts.json")
BLOG_DIR = os.path.join(ROOT, "blog")
HOME = os.path.join(ROOT, "index.html")

START = "<!-- posts:start -->"
END = "<!-- posts:end -->"


def nav(prefix: str, active: str = "") -> str:
    items = [
        ("FuSu", f"{prefix}index.html#fusu", "fusu"),
        ("Episódios", f"{prefix}episodios.html", "episodios"),
        ("Blog", f"{prefix}blog/index.html", "blog"),
        ("Quem Somos", f"{prefix}index.html#quem-somos", "quem-somos"),
        ("Contato", f"{prefix}index.html#contato", "contato"),
    ]
    def li(label: str, href: str, key: str) -> str:
        cls = ' class="is-active"' if key == active else ""
        return f'      <li><a href="{href}"{cls}>{label}</a></li>'

    lis = "\n".join(li(*item) for item in items)
    return f"""<header class="nav">
  <div class="nav__inner">
    <a class="brand" href="{prefix}index.html">
      <img src="{prefix}assets/img/logo.png" alt="Logótipo FuSu">
      <span>Futuro Sustentável</span>
    </a>
    <button class="nav__toggle" id="navToggle" aria-label="Abrir menu" aria-expanded="false" aria-controls="navLinks">☰</button>
    <ul class="nav__links" id="navLinks">
{lis}
    </ul>
  </div>
</header>"""


def head(title: str, description: str, image: str, prefix: str,
         canonical: str = "", jsonld: str = "") -> str:
    extra = ""
    if canonical:
        extra += f'\n<link rel="canonical" href="{canonical}">'
    if jsonld:
        extra += f'\n<script type="application/ld+json">\n{jsonld}\n</script>'
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{prefix}{image}">
<meta property="og:type" content="article">
<link rel="icon" href="{prefix}assets/img/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Gemunu+Libre:wght@600;700;800&family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/css/style.css">{extra}
</head>
<body>

<a class="skip-link" href="#conteudo">Ir para o conteúdo</a>"""


FOOTER = """<footer class="footer">
  <div class="wrap">
    <div class="footer__grid">
      <div>
        <h3>FuSu Podcast</h3>
        <p>Futuro Sustentável — sustentabilidade de um modo fácil, abrangente e descontraído.</p>
      </div>
      <div>
        <h3>Ouça</h3>
        <ul>
          <li><a href="{p}episodios.html">Todos os episódios</a></li>
          <li><a href="https://open.spotify.com/show/0nLbEuYuL0trgLPo5lUbRJ" target="_blank" rel="noopener">Spotify</a></li>
          <li><a href="https://podcasts.apple.com/us/podcast/futuro-sustent%C3%A1vel/id1704469234" target="_blank" rel="noopener">Apple Podcasts</a></li>
          <li><a href="https://www.deezer.com/en/show/1000211035" target="_blank" rel="noopener">Deezer</a></li>
        </ul>
      </div>
      <div>
        <h3>Siga</h3>
        <ul>
          <li><a href="https://www.instagram.com/fusupodcast/" target="_blank" rel="noopener">Instagram</a></li>
          <li><a href="https://www.linkedin.com/company/fusupodcast/" target="_blank" rel="noopener">LinkedIn</a></li>
        </ul>
        <h3 style="margin-top:24px">Apoio</h3>
        <p class="footer__support">
          <a href="https://www.fundacaoedp.pt/pt" target="_blank" rel="noopener">
            <img src="{p}assets/img/edp.png" alt="Fundação EDP" loading="lazy">
          </a>
          <small>Fundação EDP · Escola da Energia<br>Menção Honrosa 2025</small>
        </p>
      </div>
    </div>
    <div class="footer__bottom">
      <span>© 2025 by Futuro Sustentável co.</span>
      <span>FUSU PODCAST</span>
    </div>
  </div>
</footer>

<script src="{p}assets/js/main.js"></script>
</body>
</html>
"""


def card(post: dict, prefix: str) -> str:
    tags = "".join(f'<span class="chip">{t}</span>' for t in post.get("tags", []))
    return f"""        <a class="post-card" href="{prefix}blog/{post['slug']}.html">
          <img src="{prefix}{post['image']}" alt="{post['title']}" loading="lazy">
          <div class="post-card__body">
            <p class="post-card__meta">{post['dateLabel']} · {post['readingTime']} de leitura</p>
            <h3 class="post-card__title">{post['title']}</h3>
            <p class="post-card__excerpt">{post['excerpt']}</p>
            <p class="chips">{tags}</p>
          </div>
        </a>"""


def build_post(post: dict, prev: dict | None, nxt: dict | None) -> str:
    paras = "\n        ".join(f"<p>{p}</p>" for p in post["body"])
    tags = "".join(f'<span class="chip chip--light">{t}</span>' for t in post.get("tags", []))

    around = []
    if nxt:
        around.append(f'<a class="pager__item" href="{nxt["slug"]}.html"><span>← Anterior</span>{nxt["title"]}</a>')
    if prev:
        around.append(f'<a class="pager__item pager__item--next" href="{prev["slug"]}.html"><span>Seguinte →</span>{prev["title"]}</a>')
    pager = f'<nav class="pager">{"".join(around)}</nav>' if around else ""

    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post["title"],
        "datePublished": post["date"],
        "author": {"@type": "Person", "name": post["author"]},
        "image": f"{SITE_URL}/{post['image']}",
        "description": post["excerpt"],
        "inLanguage": "pt",
        "mainEntityOfPage": f"{SITE_URL}/blog/{post['slug']}.html",
        "publisher": {"@type": "Organization", "name": "Futuro Sustentável co."},
    }, ensure_ascii=False, indent=1)

    return f"""{head(post['title'] + ' | FuSu', post['excerpt'], post['image'], '../',
                     f"{SITE_URL}/blog/{post['slug']}.html", jsonld)}

{nav('../', 'blog')}

<main id="conteudo">
  <section class="post-hero">
    <div class="wrap">
      <p class="post-card__meta">{post['author']} · {post['dateLabel']} · {post['readingTime']} de leitura</p>
      <h1>{post['title']}</h1>
      <p class="chips">{tags}</p>
    </div>
  </section>

  <article class="section">
    <div class="wrap">
      <div class="post-body">
        <img src="../{post['image']}" alt="{post['title']}">
        {paras}
        <p><a class="btn btn--primary" href="../episodios.html">Ouvir os episódios</a></p>
        {pager}
        <a class="back-link" href="index.html">← Todos os posts</a>
      </div>
    </div>
  </article>
</main>

{FOOTER.format(p='../')}"""


def build_index(posts: list) -> str:
    cards = "\n".join(card(p, "../") for p in posts)
    return f"""{head('Blog | FuSu — Futuro Sustentável', 'Artigos, bastidores dos episódios e informações sobre os convidados do podcast FuSu.', 'assets/img/post-acv.webp', '../', f'{SITE_URL}/blog/')}

{nav('../', 'blog')}

<main id="conteudo">
  <section class="page-hero">
    <div class="wrap">
      <h1>Blog</h1>
      <p class="lead">Nosso blog oferece informações adicionais sobre os tópicos que abordamos em nosso podcast, com links para artigos, pesquisas e dicas práticas para uma vida mais consciente e sustentável. Encontre também bastidores de nossas entrevistas e informações adicionais sobre nossos convidados.</p>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="posts">
{cards}
      </div>
    </div>
  </section>
</main>

{FOOTER.format(p='../')}"""


def update_home(posts: list) -> None:
    with open(HOME, encoding="utf-8") as fh:
        html = fh.read()
    if START not in html or END not in html:
        print("  ! marcadores posts:start/posts:end não encontrados em index.html — homepage não atualizada")
        return
    cards = "\n".join(card(p, "") for p in posts[:3])
    before = html.split(START)[0]
    after = html.split(END)[1]
    with open(HOME, "w", encoding="utf-8") as fh:
        fh.write(f"{before}{START}\n{cards}\n      {END}{after}")
    print("  homepage: 3 posts em destaque atualizados")


def build_sitemap(posts: list) -> None:
    urls = [
        (f"{SITE_URL}/", "1.0"),
        (f"{SITE_URL}/episodios.html", "0.9"),
        (f"{SITE_URL}/blog/", "0.8"),
    ] + [(f"{SITE_URL}/blog/{p['slug']}.html", "0.6") for p in posts]

    body = "\n".join(
        f"  <url><loc>{loc}</loc><priority>{prio}</priority></url>" for loc, prio in urls
    )
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{body}
</urlset>
"""
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(xml)

    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")

    print(f"  sitemap.xml ({len(urls)} URLs) + robots.txt")


def main() -> None:
    with open(DATA, encoding="utf-8") as fh:
        posts = json.load(fh)["posts"]
    posts.sort(key=lambda p: p["date"], reverse=True)

    os.makedirs(BLOG_DIR, exist_ok=True)
    for i, post in enumerate(posts):
        prev = posts[i - 1] if i > 0 else None
        nxt = posts[i + 1] if i + 1 < len(posts) else None
        path = os.path.join(BLOG_DIR, f"{post['slug']}.html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(build_post(post, prev, nxt))
        print(f"  blog/{post['slug']}.html")

    with open(os.path.join(BLOG_DIR, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(build_index(posts))
    print("  blog/index.html")

    update_home(posts)
    build_sitemap(posts)
    print(f"OK — {len(posts)} posts gerados")


if __name__ == "__main__":
    main()
