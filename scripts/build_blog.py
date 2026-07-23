#!/usr/bin/env python3
"""Gera o blog a partir de assets/data/posts.json.

Cria:
  blog/index.html        — lista de artigos (destaque + restantes)
  blog/<slug>.html       — uma página por artigo
  sitemap.xml, robots.txt (inclui as páginas de episódio)
  e reescreve o bloco de artigos em destaque da home (entre marcadores).

Uso:  python3 scripts/build_blog.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import template as T  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "assets", "data", "posts.json")
EPISODES = os.path.join(ROOT, "assets", "data", "episodes.json")
BLOG_DIR = os.path.join(ROOT, "blog")
HOME = os.path.join(ROOT, "index.html")

START = "<!-- posts:start -->"
END = "<!-- posts:end -->"


def featured_card(post: dict, prefix: str) -> str:
    tags = "".join(f'<span class="chip chip--soft">{t}</span>' for t in post.get("tags", []))
    return f"""      <a class="post-featured" href="{prefix}blog/{post['slug']}.html">
        <img src="{prefix}{post['image']}" alt="" width="900" height="506" loading="lazy">
        <div>
          <p class="chips">{tags}</p>
          <h3>{post['title']}</h3>
          <p>{post['excerpt']}</p>
          <p class="meta">{post['dateLabel']}<span>{post['readingTime']} de leitura</span></p>
        </div>
      </a>"""


def item_card(post: dict, prefix: str) -> str:
    tag = post.get("tags", ["Artigo"])[0]
    return f"""        <a class="post-item" href="{prefix}blog/{post['slug']}.html">
          <img src="{prefix}{post['image']}" alt="" width="600" height="338" loading="lazy">
          <p class="chips"><span class="chip chip--soft">{tag}</span></p>
          <h3>{post['title']}</h3>
          <p>{post['excerpt']}</p>
          <p class="meta">{post['dateLabel']}<span>{post['readingTime']}</span></p>
        </a>"""


def build_post(post: dict, newer: dict | None, older: dict | None) -> str:
    paragraphs = "\n        ".join(f"<p>{p}</p>" for p in post["body"])
    tags = "".join(f'<span class="chip chip--soft">{t}</span>' for t in post.get("tags", []))
    url = f"{T.SITE_URL}/blog/{post['slug']}.html"
    image_url = f"{T.SITE_URL}/{post['image']}"

    jsonld = json.dumps([
        {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": post["title"],
            "datePublished": post["date"],
            "author": {"@type": "Person", "name": post["author"]},
            "image": image_url,
            "description": post["excerpt"],
            "inLanguage": "pt",
            "mainEntityOfPage": url,
            "publisher": {"@type": "Organization", "name": "Futuro Sustentável co."},
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Início", "item": f"{T.SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{T.SITE_URL}/blog/"},
                {"@type": "ListItem", "position": 3, "name": post["title"], "item": url},
            ],
        },
    ], ensure_ascii=False, indent=1)

    pager = []
    if older:
        pager.append(f'<a class="pager__item" href="{older["slug"]}.html"><span>← Anterior</span>{older["title"]}</a>')
    if newer:
        pager.append(f'<a class="pager__item pager__item--next" href="{newer["slug"]}.html"><span>Seguinte →</span>{newer["title"]}</a>')
    pager_html = f'<nav class="pager" aria-label="Outros artigos">{"".join(pager)}</nav>' if pager else ""

    return f"""{T.head(post['title'] + ' | FuSu', post['excerpt'], image_url, '../', url, jsonld)}

{T.nav('../', 'blog')}

<main id="conteudo">
  <article>
    <header class="page-hero">
      <div class="wrap">
        <p class="crumbs"><a href="../index.html">Início</a> / <a href="index.html">Blog</a></p>
        <p class="chips" style="margin-bottom:16px">{tags}</p>
        <h1>{post['title']}</h1>
        <p class="meta">{post['author']}<span>{post['dateLabel']}</span><span>{post['readingTime']} de leitura</span></p>
      </div>
    </header>

    <div class="section">
      <div class="wrap">
        <div class="post-body">
          <img src="../{post['image']}" alt="" width="900" height="506">
          {paragraphs}
          <p style="margin-top:32px"><a class="btn btn--outline" href="../episodios.html">Ouvir os episódios</a></p>
          {pager_html}
          <p><a class="back-link" href="index.html">← Todos os artigos</a></p>
        </div>
      </div>
    </div>
  </article>
</main>

{T.support('../')}

{T.footer('../')}"""


def build_index(posts: list) -> str:
    featured = featured_card(posts[0], "../")
    rest = "\n".join(item_card(p, "../") for p in posts[1:])

    return f"""{T.head('Blog | FuSu — Futuro Sustentável',
                       'Bastidores das entrevistas, referências e contexto extra sobre clima, energia e economia.',
                       f'{T.SITE_URL}/{posts[0]["image"]}', '../', f'{T.SITE_URL}/blog/', '', 'website')}

{T.nav('../', 'blog')}

<main id="conteudo">
  <header class="page-hero">
    <div class="wrap">
      <p class="crumbs"><a href="../index.html">Início</a> / Blog</p>
      <h1>Blog</h1>
      <p class="lead">Bastidores das entrevistas, referências e contexto extra sobre os temas que aparecem no podcast — para quem quer ir além do áudio.</p>
    </div>
  </header>

  <section class="section">
    <div class="wrap">
{featured}

      <div class="post-list">
{rest}
      </div>
    </div>
  </section>
</main>

{T.support('../')}

{T.footer('../')}"""


def update_home(posts: list) -> None:
    with open(HOME, encoding="utf-8") as fh:
        html = fh.read()

    if START not in html or END not in html:
        print("  ! marcadores posts:start/posts:end não encontrados na home")
        return

    block = featured_card(posts[0], "") + "\n\n      <div class=\"post-list\">\n" \
        + "\n".join(item_card(p, "") for p in posts[1:3]) + "\n      </div>"

    before, after = html.split(START)[0], html.split(END)[1]
    with open(HOME, "w", encoding="utf-8") as fh:
        fh.write(f"{before}{START}\n{block}\n      {END}{after}")
    print("  home: destaque + 2 artigos atualizados")


def build_sitemap(posts: list) -> None:
    urls = [(f"{T.SITE_URL}/", "1.0"),
            (f"{T.SITE_URL}/episodios.html", "0.9"),
            (f"{T.SITE_URL}/blog/", "0.8")]
    urls += [(f"{T.SITE_URL}/blog/{p['slug']}.html", "0.6") for p in posts]

    if os.path.exists(EPISODES):
        with open(EPISODES, encoding="utf-8") as fh:
            urls += [(f"{T.SITE_URL}/episodios/{e['id']}.html", "0.7")
                     for e in json.load(fh)["episodes"]]

    body = "\n".join(f"  <url><loc>{loc}</loc><priority>{p}</priority></url>" for loc, p in urls)
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                 f"{body}\n</urlset>\n")

    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"User-agent: *\nAllow: /\n\nSitemap: {T.SITE_URL}/sitemap.xml\n")

    print(f"  sitemap.xml ({len(urls)} URLs) + robots.txt")


def main() -> None:
    with open(DATA, encoding="utf-8") as fh:
        posts = json.load(fh)["posts"]
    posts.sort(key=lambda p: p["date"], reverse=True)

    os.makedirs(BLOG_DIR, exist_ok=True)
    for i, post in enumerate(posts):
        newer = posts[i - 1] if i > 0 else None
        older = posts[i + 1] if i + 1 < len(posts) else None
        with open(os.path.join(BLOG_DIR, f"{post['slug']}.html"), "w", encoding="utf-8") as fh:
            fh.write(build_post(post, newer, older))

    with open(os.path.join(BLOG_DIR, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(build_index(posts))

    update_home(posts)
    build_sitemap(posts)
    print(f"OK — {len(posts)} artigos gerados")


if __name__ == "__main__":
    main()
