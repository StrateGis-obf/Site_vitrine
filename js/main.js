(function () {
  'use strict';

  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia && matchMedia('(hover: hover) and (pointer: fine)').matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---------- Menu mobile ---------- */
  var nav = $('#nav');
  var toggle = $('#nav-toggle');
  var links = $('#nav-links');
  function closeMenu() {
    if (!toggle) return;
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Ouvrir le menu');
    links.classList.remove('open');
  }
  if (toggle && links) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      toggle.setAttribute('aria-label', open ? 'Ouvrir le menu' : 'Fermer le menu');
      links.classList.toggle('open', !open);
    });
    links.addEventListener('click', function (e) { if (e.target.closest('a')) closeMenu(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeMenu(); });
  }

  /* ---------- Titres découpés mot par mot ---------- */
  function splitWords(el) {
    var idx = 0;
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (p) {
            if (!p) return;
            if (/^\s+$/.test(p)) { frag.appendChild(document.createTextNode(' ')); return; }
            var w = document.createElement('span'); w.className = 'w';
            var s = document.createElement('span'); s.textContent = p; s.style.setProperty('--i', idx++);
            w.appendChild(s); frag.appendChild(w);
          });
          node.replaceChild(frag, n);
        } else if (n.nodeType === 1 && n.tagName !== 'BR') { walk(n); }
      });
    })(el);
  }
  function splitLetters(el) {
    var text = el.textContent;
    el.setAttribute('aria-label', text);
    el.textContent = '';
    text.split('').forEach(function (ch, i) {
      var s = document.createElement('span');
      s.className = 'l'; s.setAttribute('aria-hidden', 'true');
      s.style.setProperty('--i', i); s.textContent = ch;
      el.appendChild(s);
    });
  }

  var splits = $$('.split');
  var footLogo = $('#foot-logo');
  if (!reduce) {
    splits.forEach(splitWords);
    if (footLogo) splitLetters(footLogo);
  }

  /* ---------- Apparitions au défilement (avec cascade) ---------- */
  var groups = [
    ['.cards', '.card'], ['.steps', 'li'], ['.values', '.value'], ['.intents', 'li'],
    ['.faq-list', '.qa'], ['.form-wrap form', '.row, .field, .consent, .send']
  ];
  var targets = [];
  groups.forEach(function (g) {
    $$(g[0]).forEach(function (parent) {
      Array.prototype.filter.call(parent.children, function (c) { return c.matches(g[1]); }).forEach(function (el, i) {
        el.classList.add('rv');
        el.style.setProperty('--d', (i * 110) + 'ms');
        targets.push(el);
      });
    });
  });
  [
    ['.about-main', ''], ['.sv-head', ''], ['.story-fig', 'rv-left'], ['.story-text', 'rv-right'],
    ['.video-text', 'rv-left'], ['.video-panel', 'rv-scale'], ['.faq-intro', 'rv-left'],
    ['.contact-info', 'rv-left'], ['.form-title', ''], ['.s-about .rule', '']
  ].forEach(function (p) {
    $$(p[0]).forEach(function (el) {
      if (p[0] !== '.s-about .rule') el.classList.add('rv');
      if (p[1]) el.classList.add(p[1]);
      targets.push(el);
    });
  });
  targets = targets.concat(splits, footLogo ? [footLogo] : []);
  // Tout élément .rv non listé ci-dessus (stats, vitrine, bandeau…) doit aussi être révélé,
  // sinon il reste invisible (opacity:0)
  $$('.rv').forEach(function (el) { if (targets.indexOf(el) === -1) targets.push(el); });

  function reveal(el) {
    el.classList.add('in');
    var d = parseInt(el.style.getPropertyValue('--d'), 10) || 0;
    setTimeout(function () { el.classList.add('done'); }, 1600 + d);
  }
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { reveal(en.target); io.unobserve(en.target); }
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -6% 0px' });
    targets.forEach(function (el) { io.observe(el); });
  } else {
    targets.forEach(function (el) { el.classList.add('in', 'done'); });
  }
  // Titre principal : animation dès le chargement
  var heroTitle = $('#hero-title');
  if (heroTitle) setTimeout(function () { heroTitle.classList.add('in'); }, 250);

  /* ---------- Compteurs (section stats) ---------- */
  $$('.stat b[data-to]').forEach(function (b) {
    var to = parseFloat(b.getAttribute('data-to')) || 0;
    var suf = b.getAttribute('data-suf') || '';
    function set(v) { b.textContent = Math.round(v) + suf; }
    if (reduce || !('IntersectionObserver' in window)) { set(to); return; }
    var co = new IntersectionObserver(function (es) {
      if (!es[0].isIntersecting) return;
      co.disconnect();
      var t0 = performance.now(), dur = 1600;
      requestAnimationFrame(function step(t) {
        var p = Math.min(1, (t - t0) / dur);
        set(to * (1 - Math.pow(1 - p, 3)));
        if (p < 1) requestAnimationFrame(step);
      });
    }, { threshold: 0.5 });
    co.observe(b);
  });

  /* ---------- Agrandissement des images de la vitrine ---------- */
  $$('[data-zoom]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var img = $('img', btn);
      if (!img) return;
      var lb = document.createElement('div');
      lb.className = 'lb';
      lb.setAttribute('role', 'dialog');
      lb.setAttribute('aria-modal', 'true');
      lb.setAttribute('aria-label', img.alt || 'Image agrandie');
      var big = document.createElement('img');
      big.src = img.currentSrc || img.src;
      big.alt = img.alt;
      lb.appendChild(big);
      document.body.appendChild(lb);
      function onKey(e) { if (e.key === 'Escape') close(); }
      function close() { lb.remove(); document.removeEventListener('keydown', onKey); btn.focus(); }
      lb.addEventListener('click', close);
      document.addEventListener('keydown', onKey);
    });
  });

  /* ---------- Défilement : progression, navigation, parallaxe ---------- */
  var prog = $('#prog');
  var pars = $$('[data-par]');
  var lastY = window.pageYOffset;
  var ticking = false;

  function onScroll() {
    var y = window.pageYOffset;
    var h = document.documentElement.scrollHeight - window.innerHeight;
    if (prog) prog.style.transform = 'scaleX(' + (h > 0 ? Math.min(1, y / h) : 0).toFixed(4) + ')';

    if (nav) {
      nav.classList.toggle('compact', y > 140);
      var menuOpen = links && links.classList.contains('open');
      if (!menuOpen) {
        if (y > lastY + 6 && y > 520) nav.classList.add('hide');
        else if (y < lastY - 6 || y < 520) nav.classList.remove('hide');
      }
    }
    lastY = y;

    if (!reduce) {
      var vh = window.innerHeight;
      pars.forEach(function (el) {
        if (!el.isConnected || !el.parentElement) return; // image absente (retirée par onerror)
        var r = el.parentElement.getBoundingClientRect();
        if (r.bottom < -100 || r.top > vh + 100) return;
        var diff = (r.top + r.height / 2) - vh / 2;
        el.style.setProperty('--py', (diff * -parseFloat(el.dataset.par)).toFixed(1) + 'px');
      });
    }
    ticking = false;
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(onScroll); }
  }, { passive: true });
  window.addEventListener('resize', onScroll);
  onScroll();

  /* ---------- Lien actif dans le menu ---------- */
  var sections = ['a-propos', 'services', 'approche', 'faq'].map(function (id) { return document.getElementById(id); }).filter(Boolean);
  if ('IntersectionObserver' in window) {
    var so = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        $$('.nav-links > a:not(.btn)').forEach(function (a) {
          a.classList.toggle('on', a.getAttribute('href') === '#' + en.target.id);
        });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    sections.forEach(function (s) { so.observe(s); });
  }

  /* ---------- Effets souris (écrans avec souris uniquement) ---------- */
  if (finePointer && !reduce) {
    // Halo lumineux dans l'accueil
    var hero = $('.s-hero');
    if (hero) {
      hero.addEventListener('pointermove', function (e) {
        var r = hero.getBoundingClientRect();
        hero.style.setProperty('--mx', (e.clientX - r.left) + 'px');
        hero.style.setProperty('--my', (e.clientY - r.top) + 'px');
      });
    }
    // Cartes services : spot lumineux + déplacement de l'illustration
    $$('.card').forEach(function (card) {
      card.addEventListener('pointermove', function (e) {
        var r = card.getBoundingClientRect();
        var x = e.clientX - r.left, y = e.clientY - r.top;
        card.style.setProperty('--mx', x + 'px');
        card.style.setProperty('--my', y + 'px');
        card.style.setProperty('--ax', ((x / r.width) - 0.5).toFixed(3));
        card.style.setProperty('--ay', ((y / r.height) - 0.5).toFixed(3));
      });
      card.addEventListener('pointerleave', function () {
        card.style.setProperty('--ax', 0);
        card.style.setProperty('--ay', 0);
      });
    });
    // Boutons « magnétiques »
    $$('.btn, .to-top').forEach(function (b) {
      b.addEventListener('pointermove', function (e) {
        var r = b.getBoundingClientRect();
        var dx = (e.clientX - (r.left + r.width / 2)) * 0.18;
        var dy = (e.clientY - (r.top + r.height / 2)) * 0.28;
        b.style.transform = 'translate(' + dx.toFixed(1) + 'px,' + dy.toFixed(1) + 'px)';
      });
      b.addEventListener('pointerleave', function () { b.style.transform = ''; });
    });
  }

  /* ---------- FAQ (accordéon) ---------- */
  $$('.qa button').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var qa = btn.closest('.qa');
      var open = !qa.classList.contains('open');
      qa.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', String(open));
    });
  });

  /* ---------- Vidéo : bouton « Lancer la vidéo » ---------- */
  var video = $('#promo-video');
  var cta = $('#video-cta');
  if (video && cta) {
    cta.addEventListener('click', function () {
      video.scrollIntoView({ behavior: 'smooth', block: 'center' });
      var p = video.play();
      if (p && p.catch) p.catch(function () {});
    });
  }

  /* ---------- Cartes service → présélection du formulaire ---------- */
  var serviceSel = $('#service');
  $$('.card[data-service]').forEach(function (card) {
    card.addEventListener('click', function () {
      if (serviceSel) serviceSel.value = card.getAttribute('data-service');
    });
  });

  /* ---------- Formulaire de devis (Formspree) ---------- */
  var form = $('#devis-form');
  var status = $('#form-status');
  var submitBtn = $('#submit-btn');

  function setStatus(type, msg) {
    status.className = 'form-status';
    void status.offsetWidth; // relance l'animation
    status.className = 'form-status show ' + type;
    status.textContent = msg;
  }

  function validate() {
    var ok = true;
    $$('[required]', form).forEach(function (el) {
      var wrap = el.closest('.field') || el.closest('.consent');
      var valid = el.type === 'checkbox' ? el.checked : el.value.trim() !== '';
      if (valid && el.type === 'email') valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value.trim());
      if (wrap) {
        wrap.classList.remove('err');
        if (!valid) { void wrap.offsetWidth; wrap.classList.add('err'); }
      }
      if (!valid) ok = false;
    });
    return ok;
  }

  if (form) {
    form.addEventListener('input', function (e) {
      var wrap = e.target.closest('.field') || e.target.closest('.consent');
      if (wrap) wrap.classList.remove('err');
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!validate()) {
        setStatus('ko', 'Merci de compléter les champs obligatoires (*) avec des informations valides.');
        var first = $('.err input, .err select, .err textarea', form);
        if (first) first.focus();
        return;
      }
      submitBtn.disabled = true;
      var label = $('span', submitBtn);
      var old = label.textContent;
      label.textContent = 'Envoi en cours…';

      fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { Accept: 'application/json' }
      }).then(function (res) {
        if (res.ok) {
          setStatus('ok', 'Merci ! Votre demande a bien été envoyée. Nous revenons vers vous sous 24h.');
          form.reset();
        } else {
          throw new Error('http ' + res.status);
        }
      }).catch(function () {
        setStatus('ko', 'Une erreur est survenue. Réessayez ou écrivez-nous à strategisobf@gmail.com.');
      }).finally(function () {
        submitBtn.disabled = false;
        label.textContent = old;
      });
    });
  }
})();
