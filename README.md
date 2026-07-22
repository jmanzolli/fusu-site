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
CNAME.exemplo                  domínio próprio — renomear para CNAME quando o DNS estiver pronto
```

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
