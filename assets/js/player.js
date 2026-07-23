/* FuSu — episódios: destaque na home, lista com filtros e player/playlist */
(() => {
  const $ = (id) => document.getElementById(id);
  const DATA = 'assets/data/episodes.json';

  const isList = !!$('epList');          // episodios.html
  const isHome = !!$('epRows') || !!$('featured');

  if (!isList && !isHome) return;

  const state = {
    all: [], view: [], index: -1,
    kind: 'all', season: 'all', query: '', sort: 'new',
  };

  const fmtTime = (s) => {
    if (!isFinite(s)) return '0:00';
    const m = Math.floor(s / 60);
    return `${m}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
  };

  const clean = (txt, n) => {
    const t = (txt || '').replace(/\s+/g, ' ').trim();
    return t.length > n ? `${t.slice(0, n).replace(/\s\S*$/, '')}…` : t;
  };

  const kindLabel = (ep) => (ep.kind === 'pilula' ? 'Pílula' : 'Entrevista');
  const kindClass = (ep) => (ep.kind === 'pilula' ? 'chip chip--pill' : 'chip chip--talk');
  const pageUrl = (ep) => `episodios/${ep.id}.html`;

  fetch(DATA)
    .then((r) => r.json())
    .then((data) => {
      state.all = data.episodes || [];
      if (isHome) return renderHome();
      startList();
    })
    .catch(() => {
      const fallback = '<p class="lead">Não foi possível carregar os episódios agora. Ouça no <a href="https://open.spotify.com/show/0nLbEuYuL0trgLPo5lUbRJ">Spotify</a>.</p>';
      ['featured', 'epRows', 'epList'].forEach((id) => { if ($(id)) $(id).innerHTML = fallback; });
    });

  /* ================= HOME ================= */
  function renderHome() {
    const [latest] = state.all;
    if (!latest) return;

    // Cartão do último episódio no hero
    if ($('heroLatestTitle')) {
      $('heroLatestTitle').textContent = latest.title;
      $('heroLatestMeta').innerHTML =
        `<span class="${kindClass(latest)}">${kindLabel(latest)}</span>`
        + `<span>${latest.dateLabel}</span><span>${latest.duration}</span>`;
      $('heroLatestLink').href = pageUrl(latest);
      $('heroLatestLink').setAttribute('aria-label', `Ouvir ${latest.title}`);

      const cover = $('heroLatestCover');
      if (latest.cover) {
        cover.src = latest.cover;
        cover.alt = `Capa do episódio ${latest.title}`;
      }
    }

    // Números
    if ($('factEpisodes')) $('factEpisodes').firstChild.textContent = String(state.all.length);
    if ($('factHours')) {
      const hours = Math.round(state.all.reduce((a, e) => a + (e.seconds || 0), 0) / 3600);
      $('factHours').firstChild.textContent = String(hours);
    }

    // Episódio em destaque
    const featured = $('featured');
    if (featured) {
      featured.innerHTML = `
        <img class="featured__cover" src="${latest.cover}" alt="Capa do episódio ${latest.title}" width="400" height="400" loading="lazy">
        <div>
          <p class="meta">
            <span class="${kindClass(latest)}">${kindLabel(latest)}</span>
            <span>Temporada ${latest.season}</span>
            <span>${latest.dateLabel}</span>
            <span>${latest.duration}</span>
          </p>
          <h3 class="featured__title">${latest.title}</h3>
          <p class="featured__desc">${clean(latest.description, 260)}</p>
          <div class="featured__actions">
            <a class="btn btn--light" href="${pageUrl(latest)}">Ouvir episódio</a>
            <a class="btn btn--ghost" href="episodios.html">Ver todos</a>
          </div>
          <ul class="platforms">
            <li><a href="https://open.spotify.com/show/0nLbEuYuL0trgLPo5lUbRJ" target="_blank" rel="noopener">Spotify</a></li>
            <li><a href="https://podcasts.apple.com/us/podcast/futuro-sustent%C3%A1vel/id1704469234" target="_blank" rel="noopener">Apple Podcasts</a></li>
            <li><a href="https://www.deezer.com/en/show/1000211035" target="_blank" rel="noopener">Deezer</a></li>
          </ul>
        </div>`;
    }

    // Episódios recentes
    const rows = $('epRows');
    if (rows) {
      const limit = Number(rows.dataset.limit || 5);
      rows.innerHTML = state.all.slice(1, limit + 1).map((ep) => `
        <li class="ep-row">
          <img class="ep-row__cover" src="${ep.cover}" alt="" width="96" height="96" loading="lazy">
          <div>
            <p class="meta">
              <span class="${kindClass(ep)}">${kindLabel(ep)}</span>
              <span>${ep.dateLabel}</span>
              <span>${ep.duration}</span>
            </p>
            <h3 class="ep-row__title"><a href="${pageUrl(ep)}">${ep.title}</a></h3>
            <p class="ep-row__desc">${clean(ep.description, 150)}</p>
          </div>
          <a class="ep-row__play" href="${pageUrl(ep)}" aria-label="Ouvir ${ep.title}">▶</a>
        </li>`).join('');
    }
  }

  /* ================= PÁGINA DE EPISÓDIOS ================= */
  function startList() {
    const params = new URLSearchParams(location.search);
    const q = params.get('q');
    if (q) {
      state.query = q.toLowerCase();
      $('search').value = q;
    }

    renderStats();
    bindFilters();
    bindPlayer();
    applyFilters();
    restore();
  }

  function renderStats() {
    if (!$('statTotal')) return;
    const hours = state.all.reduce((a, e) => a + (e.seconds || 0), 0) / 3600;
    $('statTotal').textContent = state.all.length;
    $('statSeasons').textContent = new Set(state.all.map((e) => e.season)).size;
    $('statHours').textContent = Math.round(hours);
  }

  function bindFilters() {
    document.querySelectorAll('[data-kind]').forEach((btn) => {
      btn.addEventListener('click', () => {
        state.kind = btn.dataset.kind;
        document.querySelectorAll('[data-kind]').forEach((b) => {
          b.classList.toggle('is-on', b === btn);
          b.setAttribute('aria-pressed', String(b === btn));
        });
        applyFilters();
      });
    });

    document.querySelectorAll('[data-season]').forEach((btn) => {
      btn.addEventListener('click', () => {
        state.season = btn.dataset.season;
        document.querySelectorAll('[data-season]').forEach((b) => {
          b.classList.toggle('is-on', b === btn);
          b.setAttribute('aria-pressed', String(b === btn));
        });
        applyFilters();
      });
    });

    $('search').addEventListener('input', (e) => { state.query = e.target.value.toLowerCase(); applyFilters(); });
    $('sort').addEventListener('change', (e) => { state.sort = e.target.value; applyFilters(); });
    $('playAll').addEventListener('click', () => play(0));

    $('shuffle').addEventListener('click', () => {
      state.view = state.view.map((v) => [Math.random(), v]).sort((a, b) => a[0] - b[0]).map((p) => p[1]);
      renderList();
      play(0);
    });
  }

  function applyFilters() {
    let list = state.all.filter((ep) => {
      if (state.kind !== 'all' && ep.kind !== state.kind) return false;
      if (state.season !== 'all' && String(ep.season) !== state.season) return false;
      if (state.query && !`${ep.title} ${ep.description}`.toLowerCase().includes(state.query)) return false;
      return true;
    });

    list = list.sort({
      new: (a, b) => b.date.localeCompare(a.date),
      old: (a, b) => a.date.localeCompare(b.date),
      long: (a, b) => b.seconds - a.seconds,
      short: (a, b) => a.seconds - b.seconds,
    }[state.sort]);

    state.view = list;
    const current = $('audio').dataset.id;
    state.index = current ? list.findIndex((e) => e.id === current) : -1;
    renderList();
  }

  function renderList() {
    const list = $('epList');
    const currentId = $('audio').dataset.id;

    $('count').textContent = state.view.length
      ? `${state.view.length} episódio${state.view.length > 1 ? 's' : ''} nesta lista`
      : 'Nenhum episódio corresponde a estes filtros.';

    list.innerHTML = state.view.map((ep, i) => `
      <li class="ep-row${ep.id === currentId ? ' is-playing' : ''}" id="${ep.id}">
        <img class="ep-row__cover" src="${ep.cover}" alt="" width="96" height="96" loading="lazy">
        <div>
          <p class="meta">
            <span class="${kindClass(ep)}">${kindLabel(ep)}</span>
            <span>Temporada ${ep.season}</span>
            <span>${ep.dateLabel}</span>
            <span>${ep.duration}</span>
          </p>
          <h3 class="ep-row__title"><a href="${pageUrl(ep)}">${ep.title}</a></h3>
          <p class="ep-row__desc">${clean(ep.description, 190)}</p>
        </div>
        <button class="ep-row__play" data-i="${i}" aria-label="Tocar ${ep.title}">▶</button>
      </li>`).join('');

    list.querySelectorAll('.ep-row__play').forEach((btn) => {
      btn.addEventListener('click', () => play(Number(btn.dataset.i)));
    });
  }

  /* ---------- Player ---------- */
  function load(ep) {
    const audio = $('audio');
    audio.src = ep.audio;
    audio.dataset.id = ep.id;
    $('pbCover').src = ep.cover || 'assets/img/brand/globe.png';
    $('pbTitle').textContent = ep.title;
    $('pbSub').textContent = `${kindLabel(ep)} · Temporada ${ep.season} · ${ep.duration}`;
    $('pbLink').href = pageUrl(ep);
    $('playerBar').hidden = false;
    document.body.classList.add('player-open');

    if ('mediaSession' in navigator) {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: ep.title,
        artist: 'FuSu — Futuro Sustentável',
        artwork: [{ src: new URL(ep.cover, location.href).href, sizes: '400x400', type: 'image/jpeg' }],
      });
    }
  }

  function play(i) {
    const ep = state.view[i];
    if (!ep) return;
    state.index = i;
    if ($('audio').dataset.id !== ep.id) load(ep);
    $('audio').play().catch(() => {});
    save();
    renderList();
  }

  function bindPlayer() {
    const audio = $('audio');

    $('pbPlay').addEventListener('click', () => (audio.paused ? audio.play() : audio.pause()));
    $('pbPrev').addEventListener('click', () => play(Math.max(0, state.index - 1)));
    $('pbNext').addEventListener('click', () => play(Math.min(state.view.length - 1, state.index + 1)));
    $('pbBack').addEventListener('click', () => { audio.currentTime -= 15; });
    $('pbFwd').addEventListener('click', () => { audio.currentTime += 30; });

    $('pbRate').addEventListener('click', () => {
      const rates = [1, 1.25, 1.5, 1.75, 2, 0.75];
      const next = rates[(rates.indexOf(audio.playbackRate) + 1) % rates.length];
      audio.playbackRate = next;
      $('pbRate').textContent = `${next}×`;
    });

    $('pbClose').addEventListener('click', () => {
      audio.pause();
      $('playerBar').hidden = true;
      document.body.classList.remove('player-open');
    });

    audio.addEventListener('play', () => { $('pbPlay').textContent = '⏸'; $('pbPlay').setAttribute('aria-label', 'Pausar'); });
    audio.addEventListener('pause', () => { $('pbPlay').textContent = '▶'; $('pbPlay').setAttribute('aria-label', 'Tocar'); });
    audio.addEventListener('ended', () => { if (state.index + 1 < state.view.length) play(state.index + 1); });

    audio.addEventListener('timeupdate', () => {
      if (!audio.duration) return;
      $('pbRange').value = String((audio.currentTime / audio.duration) * 1000);
      $('pbCur').textContent = fmtTime(audio.currentTime);
      $('pbDur').textContent = fmtTime(audio.duration);
      if (Math.floor(audio.currentTime) % 5 === 0) save();
    });

    $('pbRange').addEventListener('input', (e) => {
      if (audio.duration) audio.currentTime = (Number(e.target.value) / 1000) * audio.duration;
    });

    document.addEventListener('keydown', (e) => {
      const tag = (e.target.tagName || '').toLowerCase();
      if (['input', 'select', 'textarea', 'button'].includes(tag)) return;
      if ($('playerBar').hidden) return;
      if (e.code === 'Space') { e.preventDefault(); audio.paused ? audio.play() : audio.pause(); }
      if (e.key === 'ArrowRight') audio.currentTime += 30;
      if (e.key === 'ArrowLeft') audio.currentTime -= 15;
    });
  }

  /* ---------- Retomar ---------- */
  function save() {
    const audio = $('audio');
    if (!audio.dataset.id) return;
    try {
      localStorage.setItem('fusu:last', JSON.stringify({ id: audio.dataset.id, t: audio.currentTime }));
    } catch (_) { /* modo privado */ }
  }

  function restore() {
    let saved = null;
    try { saved = JSON.parse(localStorage.getItem('fusu:last') || 'null'); } catch (_) { return; }

    const hash = decodeURIComponent(location.hash.slice(1));
    const target = hash || (saved && saved.id);
    if (!target) return;

    const i = state.view.findIndex((e) => e.id === target);
    if (i < 0) return;

    state.index = i;
    load(state.view[i]);
    renderList();

    if (!hash && saved && saved.t > 5) {
      const audio = $('audio');
      audio.addEventListener('loadedmetadata', () => { audio.currentTime = saved.t; }, { once: true });
      audio.load();
    }
    if (hash) document.getElementById(hash)?.scrollIntoView({ block: 'center' });
  }
})();
