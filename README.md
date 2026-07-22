# FUSU — Futuro Sustentável (site estático)

Réplica estática do site do podcast **FuSu — Futuro Sustentável**, feita para ser hospedada em GitHub Pages com domínio próprio (sai do Wix).

HTML + CSS + JS puro. Sem build, sem dependências.

## Estrutura

```
index.html                     home (hero, sobre, episódios em destaque, time, blog, contato)
episodios.html                 todos os episódios + player/playlist
404.html                       página de erro
blog/index.html                lista de todos os posts        [gerado]
blog/<slug>.html               uma página por post            [gerado]
assets/
  css/style.css
  js/main.js                   menu, animações, scroll-spy
  js/player.js                 lista de episódios, filtros, player fixo
  data/episodes.json           episódios vindos do RSS        [gerado]
  data/posts.json              conteúdo do blog               [fonte da verdade]
  img/                         imagens do site (WebP)
  img/ep/                      capas dos episódios            [geradas]
scripts/build_episodes.py      lê o RSS do podcast e gera episodes.json + capas
scripts/build_blog.py          gera o blog, a home e sitemap.xml a partir de posts.json
sitemap.xml, robots.txt        [gerados]
.nojekyll                      impede processamento Jekyll no GitHub Pages
CNAME.exemplo                  domínio próprio — renomear para CNAME quando o DNS estiver pronto
```

## Publicar um episódio novo

Nada a fazer à mão — o episódio já está no RSS do podcast:

```bash
python3 scripts/build_episodes.py && git add -A && git commit -m "conteudo: novos episodios" && git push --no-thin origin main
```

## Publicar um post novo

1. Adicionar um objeto no início da lista `posts` em `assets/data/posts.json`
   (campos: `slug`, `title`, `date`, `dateLabel`, `author`, `readingTime`, `image`, `tags`, `excerpt`, `body`).
2. Colocar a imagem em `assets/img/` (de preferência `.webp`, 1000px de largura).
3. Rodar:

```bash
python3 scripts/build_blog.py && git add -A && git commit -m "conteudo: novo post" && git push --no-thin origin main
```

O script cria a página do post, atualiza a lista do blog, os 3 destaques da home e o `sitemap.xml`.

> Ao ativar o domínio próprio, trocar `SITE_URL` no topo de `scripts/build_blog.py` e rodar o script de novo
> (isso corrige canonical, JSON-LD e sitemap). Também trocar as tags `canonical` de `index.html` e `episodios.html`.

## No ar

- Repositório: https://github.com/jmanzolli/fusu-site
- Site: https://www.jonatasmanzolli.com/fusu-site/
- Domínio próprio `projetofusu.com`: **ainda apontando para o Wix** — ver seção abaixo

## Ver localmente

```bash
python3 -m http.server 8000
```

Depois abrir http://localhost:8000

## Atualizar o site

Editar os arquivos, depois:

```bash
git add -A && git commit -m "conteúdo: atualiza X" && git push --no-thin origin main
```

O GitHub Pages reconstrói sozinho em ~1 min.

> `--no-thin` é necessário nesta máquina: sem ele o push falha com `RPC falhou: HTTP 400`.

## Domínio próprio

O domínio `projetofusu.com` hoje aponta para o Wix. Enquanto isso, o custom domain fica **desligado** no Pages e o arquivo se chama `CNAME.exemplo` — assim o site fica visível em `www.jonatasmanzolli.com/fusu-site`.

Quando quiser migrar:

1. No registrador do domínio, criar os registros DNS abaixo (apagando os do Wix).
2. Renomear o arquivo e enviar:

```bash
git mv CNAME.exemplo CNAME && git commit -m "chore: ativa domínio próprio" && git push --no-thin origin main
```

Registros DNS:

**Domínio raiz (`projetofusu.com`) — 4 registros A:**

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

(opcional, IPv6 AAAA: `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153`)

**Subdomínio `www` — 1 registro CNAME:**

```
www  →  jmanzolli.github.io
```

3. No GitHub: **Settings → Pages → Custom domain** → escrever `projetofusu.com` → salvar → marcar **Enforce HTTPS** depois que o certificado for emitido (pode levar até 24h).

> Se o domínio atual `projetofusu.com` está registrado/gerido pelo Wix, é preciso apontar o DNS para o GitHub (passos acima) ou transferir o domínio antes. Enquanto o DNS apontar para o Wix, o site antigo continua no ar.

## Formulário de contato

Site estático não processa formulários. O `<form>` em `index.html` está apontado para o Formspree:

```html
<form action="https://formspree.io/f/SEU_ID_AQUI" method="POST">
```

Criar conta grátis em https://formspree.io, copiar o ID do formulário e substituir `SEU_ID_AQUI`.
Alternativas: Basin, Getform, Web3Forms. Ou trocar por `mailto:`.

## Editar conteúdo

- Textos e seções: `index.html`
- Cores, tipografia, espaçamento: variáveis no topo de `assets/css/style.css`
- Novo post: copiar um arquivo de `blog/`, editar, e adicionar um `.post-card` na seção `#blog` do `index.html`
- Episódios: embed do Spotify (`show/0nLbEuYuL0trgLPo5lUbRJ`) — atualiza sozinho a cada episódio novo

## Créditos

Conteúdo e imagens: Futuro Sustentável co. Apoio: Fundação EDP.
