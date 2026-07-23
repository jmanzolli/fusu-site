"""Blocos de HTML partilhados pelos geradores (blog e episódios)."""

SITE_URL = "https://www.jonatasmanzolli.com/fusu-site"
SPOTIFY = "https://open.spotify.com/show/0nLbEuYuL0trgLPo5lUbRJ"
APPLE = "https://podcasts.apple.com/us/podcast/futuro-sustent%C3%A1vel/id1704469234"
DEEZER = "https://www.deezer.com/en/show/1000211035"
RSS = "https://anchor.fm/s/e7f23af4/podcast/rss"
EDP = "https://www.fundacaoedp.pt/pt"


def head(title: str, description: str, image_url: str, prefix: str,
         canonical: str = "", jsonld: str = "", og_type: str = "article") -> str:
    """<head> completo + skip link. `image_url` deve ser absoluto."""
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
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="FuSu — Futuro Sustentável">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{image_url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{image_url}">
<link rel="icon" href="{prefix}assets/img/brand/globe.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Gemunu+Libre:wght@600;700;800&family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/css/style.css">{extra}
</head>
<body>

<a class="skip-link" href="#conteudo">Ir para o conteúdo</a>"""


def nav(prefix: str, active: str = "") -> str:
    items = [
        ("O FuSu", f"{prefix}index.html#fusu", "fusu"),
        ("Episódios", f"{prefix}episodios.html", "episodios"),
        ("Blog", f"{prefix}blog/index.html", "blog"),
        ("Quem somos", f"{prefix}index.html#quem-somos", "quem-somos"),
        ("Contato", f"{prefix}index.html#contato", "contato"),
    ]

    def li(label: str, href: str, key: str) -> str:
        cls = ' class="is-active"' if key == active else ""
        return f'        <li><a href="{href}"{cls}>{label}</a></li>'

    lis = "\n".join(li(*item) for item in items)

    return f"""<header class="nav" id="nav">
  <div class="nav__inner">
    <a class="brand" href="{prefix}index.html">
      <img src="{prefix}assets/img/brand/globe.png" alt="" width="34" height="34">
      <span>FuSu</span>
    </a>

    <nav aria-label="Principal">
      <ul class="nav__links" id="navLinks">
{lis}
      </ul>
    </nav>

    <div class="nav__cta">
      <a class="btn btn--light btn--sm" href="{prefix}episodios.html">Ouvir agora</a>
    </div>

    <button class="nav__toggle" id="navToggle" aria-label="Abrir menu" aria-expanded="false" aria-controls="navLinks">
      <span></span>
    </button>
  </div>
</header>"""


def support(prefix: str) -> str:
    return f"""<section class="support" aria-labelledby="apoio-h">
  <div class="wrap support__inner">
    <a class="support__logo" href="{EDP}" target="_blank" rel="noopener">
      <img src="{prefix}assets/img/edp.png" alt="Fundação EDP" width="400" height="209" loading="lazy">
    </a>
    <div>
      <p class="eyebrow">Apoio institucional</p>
      <h2 class="support__title" id="apoio-h">Fundação EDP · Escola da Energia</h2>
      <p class="support__text">O FuSu recebeu uma <strong>Menção Honrosa</strong> no prêmio Escola da Energia da Fundação EDP, em 2025. O apoio ajuda a sustentar a produção da segunda temporada.</p>
      <p class="support__note">A pauta e as opiniões dos episódios são de responsabilidade exclusiva da equipe do FuSu.</p>
      <p class="support__links">
        <a class="btn btn--ghost btn--sm" href="{EDP}" target="_blank" rel="noopener">Site da Fundação EDP</a>
      </p>
    </div>
  </div>
</section>"""


def footer(prefix: str, scripts: str = "") -> str:
    return f"""<footer class="footer">
  <div class="wrap">
    <div class="footer__grid">
      <div>
        <img class="footer__logo" src="{prefix}assets/img/brand/logo-full.png" alt="FuSu — Futuro Sustentável Podcast" width="520" height="587" loading="lazy">
        <p class="footer__about">Podcast sobre clima, energia e economia, com conversas de quem pesquisa e pratica sustentabilidade.</p>
      </div>
      <div>
        <h2>Ouvir</h2>
        <ul>
          <li><a href="{prefix}episodios.html">Todos os episódios</a></li>
          <li><a href="{SPOTIFY}" target="_blank" rel="noopener">Spotify</a></li>
          <li><a href="{APPLE}" target="_blank" rel="noopener">Apple Podcasts</a></li>
          <li><a href="{DEEZER}" target="_blank" rel="noopener">Deezer</a></li>
          <li><a href="{RSS}" target="_blank" rel="noopener">Feed RSS</a></li>
        </ul>
      </div>
      <div>
        <h2>Navegar</h2>
        <ul>
          <li><a href="{prefix}index.html#fusu">O projeto</a></li>
          <li><a href="{prefix}index.html#quem-somos">Quem somos</a></li>
          <li><a href="{prefix}blog/index.html">Blog</a></li>
          <li><a href="{prefix}index.html#contato">Contato</a></li>
        </ul>
      </div>
      <div>
        <h2>Seguir</h2>
        <ul>
          <li><a href="https://www.instagram.com/fusupodcast/" target="_blank" rel="noopener">Instagram</a></li>
          <li><a href="https://www.linkedin.com/company/fusupodcast/" target="_blank" rel="noopener">LinkedIn</a></li>
          <li><a href="{EDP}" target="_blank" rel="noopener">Apoio: Fundação EDP</a></li>
        </ul>
      </div>
    </div>

    <div class="footer__bottom">
      <span>© <span data-year>2025</span> Futuro Sustentável co.</span>
      <span>Feito em HTML, CSS e um microfone.</span>
    </div>
  </div>
</footer>

<script src="{prefix}assets/js/main.js"></script>{scripts}
</body>
</html>
"""
