/* ============================================================================
   СТРОЙСЕЙЛ · весь клиентский код сайта.

   Один файл на все 495 страниц: браузер скачивает его один раз и дальше берёт
   из кэша. Раньше тот же код инлайнился в каждую страницу тремя копиями,
   которые успели разойтись между разделами.

   Модули включаются сами: каждый проверяет свою разметку и молча выходит,
   если её на странице нет.

     1 шторки            5 формы заявки
     2 заявка            6 полоса акции
     3 тост              7 фильтры каталога
     4 поиск             8 галерея товара
                         9 страница заявки
   ========================================================================== */
(function () {
  'use strict';

  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) {
    return Array.prototype.slice.call((ctx || document).querySelectorAll(sel));
  };

  function plural(n, a, b, c) {
    var m = Math.abs(n) % 100;
    if (m >= 11 && m <= 14) return c;
    m %= 10;
    return m === 1 ? a : (m >= 2 && m <= 4 ? b : c);
  }
  function money(v) {
    if (v === null || v === undefined || isNaN(v)) return '';
    var s = (Math.round(v * 100) / 100).toFixed(2).replace('.', ',');
    if (s.slice(-3) === ',00') s = s.slice(0, -3);
    return s.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  }
  function goods(n) { return n + ' ' + plural(n, 'товар', 'товара', 'товаров'); }

  /* =========================================================================
     1 · Шторки (каталог, фильтры)
     ====================================================================== */
  var openerOf = {};

  function openDrawer(d, opener) {
    d.hidden = false;
    document.body.classList.add('is-locked');
    openerOf[d.id] = opener || null;
    if (opener) opener.setAttribute('aria-expanded', 'true');
    var first = d.querySelector('.drawer-close');
    if (first) first.focus();
  }

  function closeDrawer(d) {
    d.hidden = true;
    if (!$('.drawer:not([hidden])')) document.body.classList.remove('is-locked');
    var op = openerOf[d.id];
    if (op) { op.setAttribute('aria-expanded', 'false'); op.focus(); }
  }

  document.addEventListener('click', function (e) {
    var opener = e.target.closest('[aria-controls]');
    if (opener) {
      var d = document.getElementById(opener.getAttribute('aria-controls'));
      if (d && d.classList.contains('drawer')) {
        e.preventDefault();
        openDrawer(d, opener);
        return;
      }
    }
    var closer = e.target.closest('[data-close]');
    if (closer) {
      var dd = closer.closest('.drawer');
      if (dd) closeDrawer(dd);
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var d = $('.drawer:not([hidden])');
    if (d) closeDrawer(d);
  });

  /* =========================================================================
     2 · Заявка — корзина без регистрации

     Хранится в localStorage: ни регистрации, ни сервера. Список уходит
     менеджеру, когда человек отправит форму на странице заявки.
     Схема значения: {n: количество, name, price, unit, img, url}
     ====================================================================== */
  var KEY = 'ss_cart_v1';

  function cartRead() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; }
  }
  function cartWrite(c) {
    try { localStorage.setItem(KEY, JSON.stringify(c)); } catch (e) { /* приватный режим */ }
    paintCount();
    document.dispatchEvent(new CustomEvent('cart:change'));
  }
  function cartCount(c) { return Object.keys(c || cartRead()).length; }

  function paintCount() {
    var n = cartCount();
    $$('[data-cart-count]').forEach(function (el) {
      el.textContent = n;
      el.hidden = n === 0;
    });
  }
  function paintAddButtons() {
    var c = cartRead();
    $$('[data-add]').forEach(function (b) {
      var inCart = !!c[b.dataset.id];
      b.classList.toggle('is-in', inCart);
      b.textContent = inCart ? 'В заявке' : 'В заявку';
    });
  }

  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-add]');
    if (!b) return;
    e.preventDefault();
    var c = cartRead();
    var id = b.dataset.id;
    if (c[id]) {
      delete c[id];
      cartWrite(c);
      paintAddButtons();
      toast('Убрали из заявки', b.dataset.root);
    } else {
      c[id] = {
        n: parseInt(b.dataset.qty, 10) || 1,
        name: b.dataset.name,
        price: parseFloat(b.dataset.price) || null,
        unit: b.dataset.unit || 'шт',
        img: b.dataset.img || '',
        url: b.dataset.url || ''
      };
      cartWrite(c);
      paintAddButtons();
      toast('Добавили в заявку', b.dataset.root);
    }
  });

  /* =========================================================================
     3 · Тост
     ====================================================================== */
  var toastTimer;

  function toast(text, root) {
    var old = $('.toast');
    if (old) old.remove();
    var t = document.createElement('div');
    t.className = 'toast';
    t.setAttribute('role', 'status');
    t.appendChild(document.createTextNode(text + ' '));
    var a = document.createElement('a');
    a.href = (root || '') + 'zayavka.html';
    a.textContent = 'Открыть заявку';
    t.appendChild(a);
    document.body.appendChild(t);
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.remove(); }, 4500);
  }

  /* =========================================================================
     4 · Поиск: индекс подтягивается при первом обращении к полю
     ====================================================================== */
  (function search() {
    var input = $('#q');
    var box = $('#sug');
    if (!input || !box) return;

    var root = input.dataset.root || '';
    var index = null;
    var loading = null;

    function load() {
      if (index) return Promise.resolve(index);
      if (loading) return loading;
      loading = fetch(root + 'data/search.json')
        .then(function (r) { return r.json(); })
        .then(function (j) { index = j; return j; })
        .catch(function () { index = []; return index; });
      return loading;
    }
    function norm(s) { return (s || '').toLowerCase().replace(/ё/g, 'е'); }

    function render(list) {
      if (!list.length) {
        box.innerHTML = '<p class="sug-empty">Ничего не нашли. Позвоните — подберём по описанию.</p>';
        box.hidden = false;
        return;
      }
      box.innerHTML = list.slice(0, 8).map(function (it) {
        var img = it.i ? '<img src="' + root + it.i + '" alt="" loading="lazy">' : '';
        var price = it.p ? '<b>' + it.p + '</b>' : '';
        return '<a href="' + root + it.u + '">' + img + '<span>' + it.n + '</span>' + price + '</a>';
      }).join('');
      box.hidden = false;
    }

    var timer;
    input.addEventListener('input', function () {
      clearTimeout(timer);
      var q = norm(input.value.trim());
      if (q.length < 2) { box.hidden = true; return; }
      timer = setTimeout(function () {
        load().then(function (list) {
          var words = q.split(/\s+/);
          render(list.filter(function (it) {
            var hay = norm(it.n + ' ' + (it.k || ''));
            return words.every(function (w) { return hay.indexOf(w) >= 0; });
          }));
        });
      }, 120);
    });
    input.addEventListener('focus', load);
    document.addEventListener('click', function (e) {
      if (!e.target.closest('.hdr-search')) box.hidden = true;
    });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { box.hidden = true; input.blur(); }
    });
  })();

  /* =========================================================================
     5 · Формы заявки

     Приёмника заявок (Telegram-бот, amoCRM) у сайта пока нет. Поэтому форма
     НЕ делает вид, что отправила: она проверяет телефон, собирает текст
     заявки и отдаёт человеку готовую кнопку «Отправить в WhatsApp» плюс
     телефон. Ничего не теряется, никто не ждёт звонка впустую.
     Когда приёмник появится — здесь добавится fetch, а текст подтверждения
     станет обычным «Заявка принята».
     ====================================================================== */
  var WA_BASE = 'https://wa.me/79000000000?text=';

  function cartText() {
    var c = cartRead(), ids = Object.keys(c);
    if (!ids.length) return '';
    return ids.map(function (id) {
      return '· ' + c[id].name + ' — ' + c[id].n + ' ' + c[id].unit;
    }).join('\n');
  }

  $$('form[data-lead]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var phone = form.querySelector('input[type="tel"]');
      var err = form.querySelector('.form-err');
      var digits = ((phone && phone.value) || '').replace(/\D/g, '').length;
      if (digits < 10) {
        if (err) err.hidden = false;
        if (phone) { phone.setAttribute('aria-invalid', 'true'); phone.focus(); }
        return;
      }
      if (err) err.hidden = true;
      if (phone) phone.removeAttribute('aria-invalid');

      var nameField = form.querySelector('input[type="text"]');
      var lines = ['Здравствуйте! Заявка с сайта Стройсейл.'];
      if (nameField && nameField.value.trim()) lines.push('Имя: ' + nameField.value.trim());
      lines.push('Телефон: ' + phone.value.trim());
      var items = form.dataset.clears === 'cart' ? cartText() : '';
      if (items) lines.push('Товары:', items);

      var ok = document.getElementById(form.dataset.lead);
      if (ok) {
        var link = ok.querySelector('[data-wa]');
        if (link) link.href = WA_BASE + encodeURIComponent(lines.join('\n'));
        ok.hidden = false;
        ok.focus && ok.focus();
      }
      form.hidden = true;
    });
  });

  /* =========================================================================
     6 · Полоса акции: показываем только до даты в data-until
     ====================================================================== */
  (function promo() {
    var bar = $('.promo-bar');
    if (!bar || !bar.dataset.until) return;
    if (new Date() > new Date(bar.dataset.until + 'T23:59:59')) bar.remove();
    else bar.hidden = false;
  })();

  /* =========================================================================
     7 · Фильтры каталога, сортировка, догрузка

     Панель фильтров одна на страницу: на узком экране JS переносит её
     в шторку и возвращает обратно. Две копии формы = два состояния,
     которые рано или поздно разъедутся.
     ====================================================================== */
  (function catalog() {
    var wrap = $('#catalogWrap');
    var grid = $('#grid');
    if (!wrap || !grid) return;

    var PAGE = parseInt(wrap.dataset.pageSize, 10) || 24;
    var cards = $$('.p-card', grid);
    var form = $('#filters');
    var sortSel = $('#sortSel');
    var countEl = $('#count');
    var appliedEl = $('#applied');
    var moreRow = $('#moreRow');
    var moreBtn = $('#moreBtn');
    var emptyEl = $('#empty');
    var applyBtn = $('#applyBtn');
    var onBadge = $('#filtersOn');
    var shown = PAGE;

    cards.forEach(function (c, i) {
      c._i = i;
      var p = parseFloat(c.dataset.price);
      c._price = isNaN(p) ? Infinity : p;   /* «по запросу» всегда в конце */
      c._new = c.dataset.new === '1';
    });

    function boxes() {
      return form ? $$('input[data-group]', form) : [];
    }
    function num(v) {
      v = (v || '').toString().replace(/\s/g, '').replace(',', '.').replace(/[^\d.]/g, '');
      var n = parseFloat(v);
      return isNaN(n) ? null : n;
    }
    function state() {
      var s = {};
      boxes().forEach(function (b) {
        if (!b.checked) return;
        (s[b.dataset.group] = s[b.dataset.group] || []).push(b.value);
      });
      var lo = num($('#pmin') && $('#pmin').value);
      var hi = num($('#pmax') && $('#pmax').value);
      if (lo !== null) s._min = lo;
      if (hi !== null) s._max = hi;
      return s;
    }
    function match(card, s) {
      for (var g in s) {
        if (g.charAt(0) === '_') continue;
        var have = (card.dataset[g] || '').split('|');
        var hit = s[g].some(function (v) { return have.indexOf(v) >= 0; });
        if (!hit) return false;
      }
      if (s._min !== undefined && card._price < s._min) return false;
      if (s._max !== undefined && card._price !== Infinity && card._price > s._max) return false;
      if (s._max !== undefined && card._price === Infinity) return false;
      return true;
    }
    function order(list) {
      var by = sortSel ? sortSel.value : 'default';
      var out = list.slice();
      if (by === 'cheap') {
        out.sort(function (a, b) { return a._price - b._price || a._i - b._i; });
      } else if (by === 'exp') {
        out.sort(function (a, b) {
          var ap = a._price === Infinity ? -1 : a._price;
          var bp = b._price === Infinity ? -1 : b._price;
          return bp - ap || a._i - b._i;
        });
      } else if (by === 'new') {
        out.sort(function (a, b) { return (b._new ? 1 : 0) - (a._new ? 1 : 0) || a._i - b._i; });
      } else {
        out.sort(function (a, b) { return a._i - b._i; });
      }
      return out;
    }

    function paintApplied(s) {
      if (!appliedEl) return;
      var x = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
              'stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>';
      var chips = [];
      boxes().forEach(function (b) {
        if (!b.checked) return;
        var label = b.parentNode.querySelector('.fopt-label');
        chips.push('<button class="applied-chip" type="button" data-off="' +
          b.dataset.group + '|' + b.value + '">' +
          (label ? label.textContent : b.value) + x + '</button>');
      });
      if (s._min !== undefined || s._max !== undefined) {
        var t = (s._min !== undefined ? 'от ' + money(s._min) : '') +
                (s._max !== undefined ? ' до ' + money(s._max) : '');
        chips.push('<button class="applied-chip" type="button" data-off="_price">' +
          t.trim() + ' ₽' + x + '</button>');
      }
      var n = chips.length;
      if (n > 1) chips.push('<button class="applied-reset" type="button" data-reset>Сбросить всё</button>');
      appliedEl.innerHTML = chips.join('');
      if (onBadge) { onBadge.textContent = n; onBadge.hidden = n === 0; }
    }

    var KEYS = { color: 'color', texture: 'tex', format: 'fmt', coll: 'coll',
                 shape: 'shape', task: 'task', kind: 'kind', material: 'mat' };

    function saveUrl(s) {
      var p = new URLSearchParams();
      Object.keys(KEYS).forEach(function (g) { if (s[g]) p.set(KEYS[g], s[g].join(',')); });
      if (s._min !== undefined) p.set('min', s._min);
      if (s._max !== undefined) p.set('max', s._max);
      if (sortSel && sortSel.value !== 'default') p.set('sort', sortSel.value);
      var q = p.toString();
      try {
        history.replaceState(null, '', q ? '?' + q : location.pathname);
      } catch (e) { /* file:// */ }
    }
    function loadUrl() {
      var p = new URLSearchParams(location.search);
      boxes().forEach(function (b) {
        var raw = p.get(KEYS[b.dataset.group] || b.dataset.group);
        if (raw) b.checked = raw.split(',').indexOf(b.value) >= 0;
      });
      var mn = $('#pmin'), mx = $('#pmax');
      if (mn && p.get('min')) mn.value = p.get('min');
      if (mx && p.get('max')) mx.value = p.get('max');
      if (sortSel && p.get('sort')) sortSel.value = p.get('sort');
    }

    function apply(resetPage) {
      var s = state();
      var hits = cards.filter(function (c) { return match(c, s); });
      if (resetPage !== false) shown = PAGE;

      var seq = order(hits);
      cards.forEach(function (c) { c.hidden = true; });
      seq.slice(0, shown).forEach(function (c) { c.hidden = false; grid.appendChild(c); });

      if (countEl) countEl.textContent = goods(hits.length);
      if (applyBtn) applyBtn.textContent = 'Показать ' + goods(hits.length);
      if (emptyEl) emptyEl.hidden = hits.length !== 0;
      if (moreRow) {
        moreRow.hidden = hits.length <= shown;
        if (moreBtn) moreBtn.textContent = 'Показать ещё ' + Math.min(hits.length - shown, PAGE);
      }
      paintApplied(s);
      saveUrl(s);
      paintAddButtons();
    }

    if (form) {
      form.addEventListener('change', function () { apply(); });
      form.addEventListener('input', function (e) {
        if (e.target.id === 'pmin' || e.target.id === 'pmax') apply();
      });
      form.addEventListener('submit', function (e) { e.preventDefault(); });
    }
    if (sortSel) sortSel.addEventListener('change', function () { apply(); });

    /* Кнопка «Показать N»: в шторке закрывает её (data-close), на широком
       экране — переносит взгляд к выдаче, чтобы не искать её глазами. */
    if (applyBtn) {
      applyBtn.addEventListener('click', function () {
        if (!$('.drawer:not([hidden])')) {
          grid.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    }
    if (moreBtn) {
      moreBtn.addEventListener('click', function () {
        shown += PAGE;
        apply(false);
      });
    }

    document.addEventListener('click', function (e) {
      var off = e.target.closest('[data-off]');
      if (off) {
        var v = off.dataset.off;
        if (v === '_price') {
          ['#pmin', '#pmax'].forEach(function (sel) { var el = $(sel); if (el) el.value = ''; });
        } else {
          var parts = v.split('|');
          boxes().forEach(function (b) {
            if (b.dataset.group === parts[0] && b.value === parts[1]) b.checked = false;
          });
        }
        apply();
        return;
      }
      if (e.target.closest('[data-reset]')) {
        boxes().forEach(function (b) { b.checked = false; });
        ['#pmin', '#pmax'].forEach(function (sel) { var el = $(sel); if (el) el.value = ''; });
        if (sortSel) sortSel.value = 'default';
        apply();
      }
    });

    /* Переезд панели в шторку и обратно */
    var slot = $('#filtersSlot');
    var drawer = $('#filtersDrawer');
    var home = form ? form.parentNode : null;
    if (drawer && form && slot && home) {
      new MutationObserver(function () {
        if (!drawer.hidden) slot.appendChild(form);
        else if (form.parentNode !== home) home.insertBefore(form, home.firstChild);
      }).observe(drawer, { attributes: true, attributeFilter: ['hidden'] });
    }

    loadUrl();
    apply();
  })();

  /* =========================================================================
     8 · Галерея товара и лайтбокс
     ====================================================================== */
  (function gallery() {
    var main = $('#pdMain');
    if (!main) return;

    var thumbs = $$('.pd-thumb');
    var srcs = thumbs.length ? thumbs.map(function (t) { return t.dataset.src; }) : [main.src];
    var cur = 0;
    var lb = null;

    function show(i) {
      cur = (i + srcs.length) % srcs.length;
      main.src = srcs[cur];
      thumbs.forEach(function (t, n) { t.classList.toggle('is-on', n === cur); });
      if (lb && !lb.hidden) lb.querySelector('img').src = srcs[cur];
    }
    thumbs.forEach(function (t, i) {
      t.addEventListener('click', function () { show(i); });
    });

    function build() {
      lb = document.createElement('div');
      lb.className = 'lightbox';
      var nav = srcs.length > 1
        ? '<button class="lb-prev" aria-label="Предыдущее фото"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M15 6l-6 6 6 6"/></svg></button>' +
          '<button class="lb-next" aria-label="Следующее фото"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M9 6l6 6-6 6"/></svg></button>'
        : '';
      lb.innerHTML = '<img alt="">' +
        '<button class="lb-close" aria-label="Закрыть"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg></button>' + nav;
      document.body.appendChild(lb);
      lb.addEventListener('click', function (e) {
        if (e.target.closest('.lb-next')) show(cur + 1);
        else if (e.target.closest('.lb-prev')) show(cur - 1);
        else if (e.target === lb || e.target.closest('.lb-close')) close();
      });
    }
    function open() {
      if (!lb) build();
      lb.querySelector('img').src = srcs[cur];
      lb.hidden = false;
      document.body.classList.add('is-locked');
      lb.querySelector('.lb-close').focus();
    }
    function close() {
      if (!lb) return;
      lb.hidden = true;
      document.body.classList.remove('is-locked');
    }

    var zoom = $('#pdZoom');
    if (zoom) zoom.addEventListener('click', open);

    document.addEventListener('keydown', function (e) {
      if (!lb || lb.hidden) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowRight') show(cur + 1);
      if (e.key === 'ArrowLeft') show(cur - 1);
    });
  })();

  /* =========================================================================
     9 · Страница заявки
     ====================================================================== */
  (function cartPage() {
    var list = $('#cartList');
    if (!list) return;

    var root = list.dataset.root || '';
    var emptyBox = $('#cartEmpty');
    var body = $('#cartBody');
    var totalEl = $('#cartTotal');
    var noteEl = $('#cartNote');
    var hidden = $('#cartPayload');

    function render() {
      var c = cartRead();
      var ids = Object.keys(c);
      if (emptyBox) emptyBox.hidden = ids.length !== 0;
      if (body) body.hidden = ids.length === 0;
      if (!ids.length) { if (hidden) hidden.value = ''; return; }

      list.innerHTML = ids.map(function (id) {
        var it = c[id];
        var img = it.img
          ? '<img src="' + root + it.img + '" alt="" width="84" height="84" loading="lazy">'
          : '<div class="p-img p-none" style="width:84px;height:84px;margin:0"></div>';
        var price = it.price
          ? '<p class="cart-price">' + money(it.price) + ' ₽<span class="p-unit">/' + it.unit + '</span></p>'
          : '<p class="cart-price">Цена по запросу</p>';
        var sum = it.price
          ? '<span class="muted">' + money(it.price * it.n) + ' ₽</span>'
          : '';
        return '<li class="cart-item" data-id="' + id + '">' + img +
          '<div><a class="cart-name" href="' + root + it.url + '">' + it.name + '</a>' + price +
          '<div class="cart-row"><span class="qty">' +
            '<button type="button" data-step="-1" aria-label="Меньше">−</button>' +
            '<input type="text" inputmode="numeric" value="' + it.n + '" aria-label="Количество, ' + it.unit + '">' +
            '<button type="button" data-step="1" aria-label="Больше">+</button></span>' +
            sum +
          '<button class="cart-drop" type="button" data-drop>Убрать</button></div></div></li>';
      }).join('');

      var total = 0, ask = 0;
      ids.forEach(function (id) {
        if (c[id].price) total += c[id].price * c[id].n;
        else ask++;
      });
      if (totalEl) totalEl.textContent = total ? money(total) + ' ₽' : '—';
      if (noteEl) {
        noteEl.textContent = ask
          ? 'В заявке ' + ask + ' ' + plural(ask, 'позиция', 'позиции', 'позиций') +
            ' без цены — назовём при звонке.'
          : 'Итог примерный: точную цену с доставкой назовёт менеджер.';
      }
      if (hidden) {
        hidden.value = ids.map(function (id) {
          return c[id].name + ' — ' + c[id].n + ' ' + c[id].unit;
        }).join('; ');
      }
    }

    list.addEventListener('click', function (e) {
      var li = e.target.closest('.cart-item');
      if (!li) return;
      var c = cartRead();
      var id = li.dataset.id;
      if (!c[id]) return;
      if (e.target.closest('[data-drop]')) {
        delete c[id];
        cartWrite(c);
        render();
        return;
      }
      var step = e.target.closest('[data-step]');
      if (step) {
        c[id].n = Math.max(1, c[id].n + parseInt(step.dataset.step, 10));
        cartWrite(c);
        render();
      }
    });
    list.addEventListener('change', function (e) {
      if (e.target.tagName !== 'INPUT') return;
      var li = e.target.closest('.cart-item');
      var c = cartRead();
      var n = parseInt(e.target.value, 10);
      c[li.dataset.id].n = isNaN(n) || n < 1 ? 1 : n;
      cartWrite(c);
      render();
    });

    document.addEventListener('cart:change', render);
    render();
  })();

  /* =========================================================================
     10 · Страница результатов поиска
     ====================================================================== */
  (function searchPage() {
    var box = $('#searchResults');
    if (!box) return;

    var root = box.dataset.root || '';
    var q = new URLSearchParams(location.search).get('q') || '';
    var field = $('#q');
    if (field && q) field.value = q;

    function norm(s) { return (s || '').toLowerCase().replace(/ё/g, 'е'); }

    if (!q.trim()) {
      box.innerHTML = '<p class="note">Введите запрос в строке поиска наверху.</p>';
      return;
    }

    fetch(root + 'data/search.json')
      .then(function (r) { return r.json(); })
      .then(function (list) {
        var words = norm(q.trim()).split(/\s+/);
        var hits = list.filter(function (it) {
          var hay = norm(it.n + ' ' + (it.k || ''));
          return words.every(function (w) { return hay.indexOf(w) >= 0; });
        });
        if (!hits.length) {
          box.innerHTML = '<div class="empty"><p>По запросу «' + q +
            '» ничего не нашли. Попробуйте короче: «кирпич красный», «плитка», «профнастил» — ' +
            'или позвоните, подберём по описанию.</p>' +
            '<a class="btn btn--accent" href="' + root + 'index.html#catalog">В каталог</a></div>';
          return;
        }
        box.innerHTML = '<p class="toolbar-count" style="margin:0 0 16px">' + goods(hits.length) +
          '</p><div class="p-grid">' + hits.slice(0, 60).map(function (it) {
            var img = it.i
              ? '<img class="p-img" src="' + root + it.i + '" alt="" width="640" height="640" loading="lazy">'
              : '<div class="p-img p-none"><span>Фото по запросу</span></div>';
            var price = it.p
              ? '<p class="p-price"><b>' + it.p + '</b></p>'
              : '<p class="p-ask">Цена по запросу</p>';
            return '<article class="p-card"><a href="' + root + it.u + '" tabindex="-1" aria-hidden="true">' +
              img + '</a><a class="p-name" href="' + root + it.u + '">' + it.n + '</a>' + price + '</article>';
          }).join('') + '</div>' +
          (hits.length > 60 ? '<p class="note" style="margin-top:16px">Показаны первые 60 — уточните запрос.</p>' : '');
      })
      .catch(function () {
        box.innerHTML = '<p class="note">Не удалось загрузить каталог. Обновите страницу или позвоните нам.</p>';
      });
  })();

  /* =========================================================================
     10a · Калькуляторы материала

     Три штуки, все по одной схеме: поля сверху, живой итог снизу. Считаем
     на клиенте — цифра меняется, пока человек печатает, без перезагрузки.
     Значения намеренно округляем ВВЕРХ: недовезти материал хуже, чем
     привезти лишний поддон.
     ====================================================================== */
  function numOf(el) {
    if (!el) return 0;
    var v = parseFloat((el.value || '').replace(',', '.'));
    return isNaN(v) || v < 0 ? 0 : v;
  }

  /* --- плитка: площадь → метры с запасом → поддоны → деньги -------------- */
  (function tileCalc() {
    var box = $('.calc[data-calc]');
    var area = $('#calcArea');
    if (!box || !area) return;

    var shape = $('#calcShape');
    var outM2 = $('#calcM2'), outPal = $('#calcPallets'), outSum = $('#calcSum');
    var pallet = parseFloat(box.dataset.pallet) || 15;
    var spare = parseFloat(box.dataset.spare) || 5;

    function price() {
      if (shape) {
        var opt = shape.options[shape.selectedIndex];
        var p = parseFloat(opt && (opt.dataset.price || opt.value));
        if (!isNaN(p)) return p;
      }
      return parseFloat(box.dataset.price) || 0;
    }
    function recalc() {
      var a = numOf(area);
      if (!a) {
        if (outM2) outM2.textContent = '—';
        if (outPal) outPal.textContent = '—';
        if (outSum) outSum.textContent = '—';
        return;
      }
      var m2 = Math.ceil(a * (1 + spare / 100));
      var pal = Math.ceil(m2 / pallet);
      if (outM2) outM2.textContent = m2 + ' м²';
      if (outPal) outPal.textContent = pal + ' ' + plural(pal, 'поддон', 'поддона', 'поддонов');
      if (outSum) outSum.textContent = price() ? money(m2 * price()) + ' ₽' : '—';
    }
    area.addEventListener('input', recalc);
    if (shape) shape.addEventListener('change', recalc);
    recalc();
  })();

  /* --- кровля: габариты дома × тип крыши → площадь ----------------------- */
  (function roofCalc() {
    var len = $('#rcLen'), wid = $('#rcWid'), type = $('#rcType'), out = $('#rcArea');
    if (!len || !wid || !type || !out) return;
    function recalc() {
      var l = numOf(len), w = numOf(wid);
      var k = parseFloat(type.value) || 1.4;
      out.textContent = (l && w) ? Math.ceil(l * w * k) + ' м²' : '—';
    }
    [len, wid].forEach(function (el) { el.addEventListener('input', recalc); });
    type.addEventListener('change', recalc);
    recalc();
  })();

  /* --- кирпич: стены минус проёмы → штуки --------------------------------
     Расход берём из выбранного формата (шт на м² кладки), запас 5 %,
     округляем до десятка — кирпич продают не поштучно. */
  (function brickCalc() {
    var wall = $('#bcWall'), open = $('#bcOpen'), fmt = $('#bcFmt');
    var outQty = $('#bcQty'), outArea = $('#bcArea');
    if (!wall || !fmt || !outQty) return;
    function recalc() {
      var a = Math.max(0, numOf(wall) - numOf(open));
      var per = parseFloat(fmt.value) || 51.4;
      if (!a) {
        outQty.textContent = '—';
        if (outArea) outArea.textContent = '—';
        return;
      }
      var qty = Math.ceil(a * per * 1.05 / 10) * 10;
      outQty.textContent = money(qty) + ' шт';
      if (outArea) outArea.textContent = Math.ceil(a) + ' м²';
    }
    [wall, open].forEach(function (el) { if (el) el.addEventListener('input', recalc); });
    fmt.addEventListener('change', recalc);
    recalc();
  })();

  /* =========================================================================
     11 · Реальная высота таб-бара

     В CSS она задана как 60px, но при системном увеличении шрифта таб-бар
     становится выше — и липкая панель товара («В заявку») пряталась под ним.
     Меряем один раз и на смену размера окна.
     ====================================================================== */
  (function tabbarHeight() {
    var bar = $('.tabbar');
    if (!bar) return;
    var timer;
    function sync() {
      var h = bar.getBoundingClientRect().height;
      if (h) document.documentElement.style.setProperty('--tabbar-h', Math.round(h) + 'px');
    }
    sync();
    /* ResizeObserver, а не событие resize: высота меняется и без смены размера
       окна — например когда система отдаёт более крупный шрифт или
       догружается веб-шрифт с другими метриками. */
    if (window.ResizeObserver) {
      /* Без задержки: ResizeObserver и так батчит вызовы, а отложенный sync
         не успевал за сменой системного шрифта — липкая панель товара
         на мгновение оказывалась под таб-баром. */
      new ResizeObserver(sync).observe(bar);
    } else {
      addEventListener('resize', function () {
        clearTimeout(timer);
        timer = setTimeout(sync, 120);
      });
    }
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(sync);
  })();

  /* --- первичная отрисовка счётчиков ------------------------------------ */
  paintCount();
  paintAddButtons();
})();
