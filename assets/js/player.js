/* Lista de episódios + player/playlist do FuSu */
(() => {
  const isHome = !!document.getElementById('epTeaser');
  const dataUrl = 'assets/data/episodes.json';

  const state = {
    all: [],
    view: [],      // lista filtrada = playlist atual
    index: -1,     // posição na playlist
    kind: 'all',
    season: 'all',
    query: '',
    sort: 'new',
  };

  const $ = (id) => document.getElementById(id);
  const fmt = (s) => {
    if (!isFinite(s)) return '0:00';
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${String(sec).padStart(2, '0')}`;
  };

  const shorten = (txt, n = 190) => {
    const clean = (txt || '').replace(/\s+/g, ' ').trim();
    return clean.length > n ? clean.slice(0, n).replace(/\s\S*$/, '') + '…' : clean;
  };

  // ---------- carregamento ----------
  fetch(dataUrl)
    .then((r) => r.json())
    .then((data) => {
      state.all = data.episodes || [];
      if (isHome) return renderTeaser();
      renderStats();
      bindFilters();
      bindPlayer();
      applyFilters();
      restore();
    })
    .catch(() => {
      const list = $('epList') || $('epTeaser');
      if (list) list.innerHTML = '<p class="lead">Não foi possível carregar os episódios. Ouça no <a href="https://open.spotify.com/show/0nLbEuYuL0trgLPo5lUbRJ">Spotify</a>.</p>';
    });

  // ---------- destaque na home ----------
  function renderTeaser() {
    const box = $('epTeaser');
    const limit = Number(box.dataset.limit || 4);
    box.innerHTML = state.all.slice(0, limit).map((ep) => `
      <a class="ep-mini" href="episodios.html#${ep.id}">
        <img src="${ep.cover || 'assets/img/logo.png'}" alt="" loading="lazy">
        <span class="ep-mini__body">
          <span class="ep-mini__kind">${ep.kind === 'pilula' ? 'Pílula' : 'Episódio'} · ${ep.duration}</span>
          <span class="ep-mini__title">${ep.title}</span>
          <span class="ep-mini__date">${ep.dateLabel}</span>
        </span>
      </a>`).join('');
  }

  // ---------- estatísticas ----------
  function renderStats() {
    const hours = state.all.reduce((a, e) => a + (e.seconds || 0), 0) / 3600;
    $('statTotal').textContent = state.all.length;
    $('statSeasons').textContent = new Set(state.all.map((e) => e.season)).size;
    $('statHours').textContent = Math.round(hours);
  }

  // ---------- filtros ----------
  function bindFilters() {
    document.querySelectorAll('[data-kind]').forEach((btn) => {
      btn.addEventListener('click', () => {
        state.kind = btn.dataset.kind;
        document.querySelectorAll('[data-kind]').forEach((b) => b.classList.toggle('is-on', b === btn));
        applyFilters();
      });
    });

    document.querySelectorAll('[data-season]').forEach((btn) => {
      btn.addEventListener('click', () => {
        state.season = btn.dataset.season;
        document.querySelectorAll('[data-season]').forEach((b) => b.classList.toggle('is-on', b === btn));
        applyFilters();
      });
    });

    $('search').addEventListener('input', (e) => {
      state.query = e.target.value.toLowerCase();
      applyFilters();
    });

    $('sort').addEventListener('change', (e) => {
      state.sort = e.target.value;
      applyFilters();
    });

    $('playAll').addEventListener('click', () => play(0));

    $('shuffle').addEventListener('click', () => {
      state.view = state.view
        .map((v) => [Math.random(), v])
        .sort((a, b) => a[0] - b[0])
        .map((pair) => pair[1]);
      renderList();
      play(0);
    });
  }

  function applyFilters() {
    let list = state.all.filter((ep) => {
      if (state.kind !== 'all' && ep.kind !== state.kind) return false;
      if (state.season !== 'all' && String(ep.season) !== state.season) return false;
      if (state.query) {
        const hay = (ep.title + ' ' + ep.description).toLowerCase();
        if (!hay.includes(state.query)) return false;
      }
      return true;
    });

    const cmp = {
      new: (a, b) => b.date.localeCompare(a.date),
      old: (a, b) => a.date.localeCompare(b.date),
      long: (a, b) => b.seconds - a.seconds,
      short: (a, b) => a.seconds - b.seconds,
    }[state.sort];

    list = list.sort(cmp);
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
      : 'Nenhum episódio encontrado com esses filtros.';

    list.innerHTML = state.view.map((ep, i) => `
      <li class="ep${ep.id === currentId ? ' is-playing' : ''}" id="${ep.id}" data-i="${i}">
        <button class="ep__play" data-i="${i}" aria-label="Tocar ${ep.title}">▶</button>
        <img class="ep__cover" src="${ep.cover || 'assets/img/logo.png'}" alt="" loading="lazy">
        <div class="ep__body">
          <p class="ep__meta">
            <span class="chip ${ep.kind === 'pilula' ? 'chip--pill' : ''}">${ep.kind === 'pilula' ? 'Pílula' : `Temporada ${ep.season}`}</span>
            <span>${ep.dateLabel}</span>
            <span>·</span>
            <span>${ep.duration}</span>
          </p>
          <h2 class="ep__title">${ep.title}</h2>
          <p class="ep__desc">${shorten(ep.description)}</p>
          <p class="ep__links">
            <a href="${ep.link}" target="_blank" rel="noopener">Abrir no Spotify ↗</a>
          </p>
        </div>
      </li>`).join('');

    list.querySelectorAll('.ep__play').forEach((btn) => {
      btn.addEventListener('click', () => play(Number(btn.dataset.i)));
    });
  }

  // ---------- player ----------
  function play(i) {
    const ep = state.view[i];
    if (!ep) return;
    const audio = $('audio');
    state.index = i;

    if (audio.dataset.id !== ep.id) {
      audio.src = ep.audio;
      audio.dataset.id = ep.id;
      $('pbCover').src = ep.cover || 'assets/img/logo.png';
      $('pbTitle').textContent = ep.title;
      $('pbSub').textContent = `${ep.kind === 'pilula' ? 'Pílula' : 'Temporada ' + ep.season} · ${ep.dateLabel} · ${ep.duration}`;
      $('pbLink').href = ep.link;
      $('playerBar').hidden = false;
      document.body.classList.add('player-open');
      if ('mediaSession' in navigator) {
        navigator.mediaSession.metadata = new MediaMetadata({
          title: ep.title,
          artist: 'FuSu — Futuro Sustentável',
          artwork: [{ src: new URL(ep.cover || 'assets/img/logo.png', location.href).href, sizes: '400x400', type: 'image/jpeg' }],
        });
      }
    }

    audio.play().catch(() => {});
    save();
    renderList();
  }

  function bindPlayer() {
    const audio = $('audio');

    $('pbPlay').addEventListener('click', () => (audio.paused ? audio.play() : audio.pause()));
    $('pbPrev').addEventListener('click', () => play(Math.max(0, state.index - 1)));
    $('pbNext').addEventListener('click', () => play(Math.min(state.view.length - 1, state.index + 1)));
    $('pbBack').addEventListener('click', () => (audio.currentTime -= 15));
    $('pbFwd').addEventListener('click', () => (audio.currentTime += 30));

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

    audio.addEventListener('play', () => ($('pbPlay').textContent = '⏸'));
    audio.addEventListener('pause', () => ($('pbPlay').textContent = '▶'));
    audio.addEventListener('ended', () => {
      if (state.index + 1 < state.view.length) play(state.index + 1);
    });

    audio.addEventListener('timeupdate', () => {
      if (!audio.duration) return;
      $('pbRange').value = String((audio.currentTime / audio.duration) * 1000);
      $('pbCur').textContent = fmt(audio.currentTime);
      $('pbDur').textContent = fmt(audio.duration);
      if (Math.floor(audio.currentTime) % 5 === 0) save();
    });

    $('pbRange').addEventListener('input', (e) => {
      if (audio.duration) audio.currentTime = (Number(e.target.value) / 1000) * audio.duration;
    });

    document.addEventListener('keydown', (e) => {
      const tag = (e.target.tagName || '').toLowerCase();
      if (tag === 'input' || tag === 'select' || tag === 'textarea') return;
      if (e.code === 'Space' && !$('playerBar').hidden) {
        e.preventDefault();
        audio.paused ? audio.play() : audio.pause();
      }
      if (e.key === 'ArrowRight') audio.currentTime += 30;
      if (e.key === 'ArrowLeft') audio.currentTime -= 15;
    });
  }

  // ---------- retomar de onde parou ----------
  function save() {
    const audio = $('audio');
    if (!audio.dataset.id) return;
    try {
      localStorage.setItem('fusu:last', JSON.stringify({ id: audio.dataset.id, t: audio.currentTime }));
    } catch (_) { /* modo privado */ }
  }

  function restore() {
    let saved;
    try {
      saved = JSON.parse(localStorage.getItem('fusu:last') || 'null');
    } catch (_) { return; }

    const hash = location.hash.slice(1);
    const target = hash || (saved && saved.id);
    if (!target) return;

    const i = state.view.findIndex((e) => e.id === target);
    if (i < 0) return;

    const ep = state.view[i];
    const audio = $('audio');
    state.index = i;
    audio.src = ep.audio;
    audio.dataset.id = ep.id;
    $('pbCover').src = ep.cover || 'assets/img/logo.png';
    $('pbTitle').textContent = ep.title;
    $('pbSub').textContent = `${ep.kind === 'pilula' ? 'Pílula' : 'Temporada ' + ep.season} · ${ep.dateLabel} · ${ep.duration}`;
    $('pbLink').href = ep.link;
    $('playerBar').hidden = false;
    document.body.classList.add('player-open');
    renderList();

    if (!hash && saved && saved.t > 5) {
      audio.addEventListener('loadedmetadata', () => { audio.currentTime = saved.t; }, { once: true });
      audio.load();
    }
    if (hash) document.getElementById(hash)?.scrollIntoView({ block: 'center' });
  }
})();
