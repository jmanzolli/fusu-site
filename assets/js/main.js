/* FuSu — comportamento base: menu, revelação, ano, formulário */
(() => {
  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

  /* ---------- Menu ---------- */
  const toggle = $('#navToggle');
  const links = $('#navLinks');

  if (toggle && links) {
    const setOpen = (open) => {
      links.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
    };

    toggle.addEventListener('click', () => setOpen(!links.classList.contains('is-open')));
    links.addEventListener('click', (e) => { if (e.target.tagName === 'A') setOpen(false); });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && links.classList.contains('is-open')) {
        setOpen(false);
        toggle.focus();
      }
    });

    // Fecha ao voltar para desktop
    window.matchMedia('(min-width: 781px)').addEventListener('change', (e) => {
      if (e.matches) setOpen(false);
    });
  }

  /* ---------- Sombra da navegação ao rolar ---------- */
  const nav = $('#nav') || $('.nav');
  if (nav) {
    const onScroll = () => nav.classList.toggle('is-scrolled', window.scrollY > 8);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ---------- Ano do copyright ---------- */
  $$('[data-year]').forEach((el) => { el.textContent = String(new Date().getFullYear()); });

  /* ---------- Revelação suave ---------- */
  const revealables = $$('.reveal');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (reduced || !('IntersectionObserver' in window)) {
    revealables.forEach((el) => el.classList.add('is-visible'));
  } else {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      });
    }, { threshold: 0.1 });
    revealables.forEach((el) => io.observe(el));
  }

  /* ---------- Link ativo conforme a secção ---------- */
  const sections = $$('main section[id]');
  const anchors = $$('.nav__links a[href^="#"]');

  if (sections.length && anchors.length && 'IntersectionObserver' in window) {
    const spy = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        anchors.forEach((a) => a.classList.toggle('is-active', a.getAttribute('href') === `#${entry.target.id}`));
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    sections.forEach((s) => spy.observe(s));
  }

  /* ---------- Formulário de contato ---------- */
  const form = $('#contactForm');
  if (!form) return;

  const status = $('#formStatus');
  const fields = $$('input, select, textarea', form);

  const messages = {
    nome: 'Escreva o seu nome.',
    email: 'Escreva um e-mail válido.',
    assunto: 'Escolha um assunto.',
    mensagem: 'Escreva a sua mensagem.',
  };

  const setStatus = (text, state) => {
    if (!status) return;
    status.textContent = text;
    if (state) status.dataset.state = state; else delete status.dataset.state;
  };

  const validate = (field) => {
    const error = $(`#erro-${field.name}`);
    const ok = field.checkValidity();
    field.setAttribute('aria-invalid', String(!ok));
    if (error) error.textContent = ok ? '' : (messages[field.name] || 'Campo obrigatório.');
    return ok;
  };

  fields.forEach((field) => {
    field.addEventListener('blur', () => validate(field));
    field.addEventListener('input', () => {
      if (field.getAttribute('aria-invalid') === 'true') validate(field);
    });
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const invalid = fields.filter((f) => !validate(f));
    if (invalid.length) {
      setStatus('Falta preencher alguns campos — veja as mensagens abaixo.', 'error');
      invalid[0].focus();
      return;
    }

    if (form.action.includes('SEU_ID_AQUI')) {
      setStatus('O formulário ainda não está ligado a um serviço de envio. Escreva para o FuSu pelo Instagram ou LinkedIn enquanto isso.', 'error');
      return;
    }

    setStatus('A enviar…', 'loading');
    const submit = $('button[type="submit"]', form);
    if (submit) submit.disabled = true;

    try {
      const response = await fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { Accept: 'application/json' },
      });

      if (!response.ok) throw new Error('falha no envio');

      form.reset();
      fields.forEach((f) => f.removeAttribute('aria-invalid'));
      setStatus('Mensagem enviada. Obrigado — respondemos em breve!', 'ok');
    } catch (_) {
      setStatus('Não foi possível enviar agora. Tente de novo em instantes ou fale com a gente pelas redes sociais.', 'error');
    } finally {
      if (submit) submit.disabled = false;
    }
  });
})();
