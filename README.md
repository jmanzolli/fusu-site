# FUSU — Futuro Sustentável (site estático)

Réplica estática do site do podcast **FuSu — Futuro Sustentável**, feita para ser hospedada em GitHub Pages com domínio próprio (sai do Wix).

HTML + CSS + JS puro. Sem build, sem dependências.

## Estrutura

```
index.html                     página única (FuSu, Episódios, Blog, Quem Somos, Contato)
blog/
  avaliacao-do-ciclo-de-vida.html
  economia-do-bem-estar.html
assets/
  css/style.css
  js/main.js
  img/                         imagens (hero, time, cartaz, posts, logo, apoio)
.nojekyll                      impede processamento Jekyll no GitHub Pages
CNAME                          domínio próprio (editar antes de publicar)
```

## Ver localmente

```bash
python3 -m http.server 8000
```

Depois abrir http://localhost:8000

## Publicar no GitHub Pages

1. Criar repositório no GitHub (ex.: `fusu-site`).
2. Na pasta do projeto:

```bash
git init && git add -A && git commit -m "feat: site estático FuSu" && git branch -M main
```

3. Ligar ao remoto e enviar (trocar `SEU-USUARIO`):

```bash
git remote add origin https://github.com/SEU-USUARIO/fusu-site.git && git push -u origin main
```

4. No GitHub: **Settings → Pages → Source: Deploy from a branch → Branch: `main` / `(root)`**.
5. Em ~1 min o site fica em `https://SEU-USUARIO.github.io/fusu-site/`.

## Domínio próprio

1. Editar o arquivo `CNAME` e deixar só o domínio, sem `https://`. Ex.: `projetofusu.com`
2. No registrador do domínio, criar os registros DNS:

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
www  →  SEU-USUARIO.github.io
```

3. No GitHub: **Settings → Pages → Custom domain** → escrever o domínio → salvar → marcar **Enforce HTTPS** depois que o certificado for emitido (pode levar até 24h).

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
