# -*- coding: utf-8 -*-
"""Шапка-кинолента категории — общая для build_tiles / build_category / build_roof.

Тёмная лента = шапка категории: сверху статичная строка (крошки, h1
с терракотовым «кирпичиком», живые цифры), ниже крутятся акции.
Механика: автолистание 5 с, пауза при наведении/касании, свайп на телефоне,
стрелки на десктопе, слайд с истёкшей data-until исчезает сам (как промо-полоса).
ВАЖНО: на страницах с лентой промо-полосу .promo-bar не выводим (promo=False
в page_shell) — две акции друг над другом спорят.

Слайд — dict: eyebrow, title (HTML, акцент в <b>), sub, cta, href, img,
опционально until="ГГГГ-ММ-ДД".
"""

ARR_PREV = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M11 18l-6-6 6-6"/></svg>')
ARR_NEXT = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')


def _slide(s, first, root=""):
    until = f' data-until="{s["until"]}"' if s.get("until") else ""
    sub = f'\n              <p class="pbH-sub">{s["sub"]}</p>' if s.get("sub") else ""
    # первый слайд — LCP страницы: качаем сразу и с приоритетом
    load = ('loading="eager" fetchpriority="high"' if first else 'loading="lazy"')
    return f"""
          <a class="pb-slide" href="{s['href']}"{until}>
            <div class="pbH-copy">
              <p class="pbH-eyebrow">{s['eyebrow']}</p>
              <p class="pbH-title">{s['title']}</p>{sub}
              <span class="pbH-go">{s['cta']}</span>
            </div>
            <div class="pbH-media"><img src="{root}{s['img']}" alt="" {load}></div>
          </a>"""


def banner(h1, facts, slides, root="", crumb=None):
    """Лента-шапка категории. h1 — имя категории (HTML), facts — строка
    цифр (HTML, акцент в <b>), slides — список слайдов-акций."""
    crumb = crumb or h1
    slides_html = "".join(_slide(s, i == 0, root) for i, s in enumerate(slides))
    return f"""
  <!-- Шапка-кинолента: имя категории статично, акции крутятся (BANNER_JS) -->
  <section class="pb pbH" aria-label="{crumb} — акции и предложения">
    <div class="pbH-top">
      <div class="wrap">
        <div class="pbH-name">
          <nav class="pbH-crumbs" aria-label="Хлебные крошки"><a href="{root}index.html">Главная</a> / {crumb}</nav>
          <h1>{h1}</h1>
        </div>
        <p class="pbH-facts">{facts}</p>
      </div>
    </div>

    <div class="wrap">
      <div class="pb-stack">{slides_html}
      </div>
    </div>

    <div class="pbH-ui">
      <div class="wrap">
        <div class="pb-dots" role="tablist" aria-label="Переключение акций"></div>
        <span class="pb-count">01 / 0{len(slides)}</span>
        <button class="pb-arr pb-prev" type="button" aria-label="Предыдущая акция">{ARR_PREV}</button>
        <button class="pb-arr pb-next" type="button" aria-label="Следующая акция">{ARR_NEXT}</button>
      </div>
    </div>
  </section>"""


BANNER_JS = """
  <script>
    (function () {
      // Два режима (разведка WB/Ozon/ЯМаркет + Baymard):
      // десктоп — fade на месте с автолистанием 5 с (пауза при наведении);
      // мобайл — полка-карусель со scroll-snap, БЕЗ автолистания (на таче
      // слайд уезжает из-под пальца), точки синхронятся со скроллом.
      var DUR = 5000;
      var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
      var mq = matchMedia('(max-width: 45em)');

      document.querySelectorAll('.pb').forEach(function (root) {
        var now = new Date();
        root.querySelectorAll('.pb-slide[data-until]').forEach(function (s) {
          if (new Date(s.dataset.until + 'T23:59:59') < now) s.remove();
        });
        var stack = root.querySelector('.pb-stack');
        var slides = Array.prototype.slice.call(root.querySelectorAll('.pb-slide'));
        var dotsWrap = root.querySelector('.pb-dots');
        var counter = root.querySelector('.pb-count');
        var ui = root.querySelector('.pbH-ui');
        if (!slides.length) { stack.hidden = true; if (ui) ui.hidden = true; return; }
        if (slides.length === 1) { slides[0].classList.add('is-on'); if (ui) ui.hidden = true; return; }

        var i = 0, timer = null;
        var dots = slides.map(function (_, n) {
          var b = document.createElement('button');
          b.type = 'button'; b.className = 'pb-dot';
          b.setAttribute('aria-label', 'Акция ' + (n + 1) + ' из ' + slides.length);
          b.addEventListener('click', function () {
            if (mq.matches) {
              slides[n].scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'start' });
            } else { go(n); start(); }
          });
          dotsWrap.appendChild(b);
          return b;
        });

        function pad(n) { return (n < 10 ? '0' : '') + n; }
        function mark(n) {
          slides[i].classList.remove('is-on'); dots[i].classList.remove('is-on');
          i = (n + slides.length) % slides.length;
          slides[i].classList.add('is-on'); dots[i].classList.add('is-on');
          if (counter) counter.textContent = pad(i + 1) + ' / ' + pad(slides.length);
        }
        function go(n) { mark(n); }
        function start() {
          if (reduced || mq.matches) return;
          stop(); timer = setInterval(function () { go(i + 1); }, DUR);
          root.classList.add('is-play');
        }
        function stop() { clearInterval(timer); timer = null; root.classList.remove('is-play'); }

        var prev = root.querySelector('.pb-prev'), next = root.querySelector('.pb-next');
        if (prev) prev.addEventListener('click', function () { go(i - 1); start(); });
        if (next) next.addEventListener('click', function () { go(i + 1); start(); });

        root.addEventListener('mouseenter', stop);
        root.addEventListener('mouseleave', start);
        root.addEventListener('focusin', stop);
        root.addEventListener('focusout', start);
        document.addEventListener('visibilitychange', function () { document.hidden ? stop() : start(); });

        // мобайл: активная точка = карта, ближайшая к центру видимой области
        // (троттлинг на setTimeout, не rAF — rAF замирает в вебвью/фоне)
        var pending = null;
        stack.addEventListener('scroll', function () {
          if (!mq.matches || pending) return;
          pending = setTimeout(function () {
            pending = null;
            var pad0 = parseFloat(getComputedStyle(stack).paddingLeft) || 0;
            var base = slides[0].offsetLeft;
            var mid = stack.scrollLeft + stack.clientWidth / 2;
            var best = 0, bd = Infinity;
            slides.forEach(function (s, n) {
              var c = s.offsetLeft - base + pad0 + s.offsetWidth / 2;
              var d = Math.abs(c - mid);
              if (d < bd) { bd = d; best = n; }
            });
            if (best !== i) mark(best);
          }, 120);
        }, { passive: true });

        mq.addEventListener('change', function () {
          if (mq.matches) { stop(); } else { start(); }
        });

        mark(0); start();
      });
    })();
  </script>"""


# ——— Наборы слайдов по категориям ———
# Даты акций: data-until. При смене акции править ЗДЕСЬ и перезапускать
# генераторы (build_tiles, build_category, build_roof).

SLIDE_SALE_TILE = {
    "eyebrow": "Акция · до 3 августа",
    "title": "<b>−15&nbsp;%</b> на плитку «Старый город»",
    "sub": "Все 24 расцветки формы. Привезём на объект, оплата при получении.",
    "cta": "Выбрать плитку",
    "href": "plitka-staryy-gorod.html",
    "img": "img/plitka/shape-staryy-gorod.jpg",
    "until": "2026-08-03",
}

SLIDE_NEW_BRICK = {
    "eyebrow": "Новинки завода",
    "title": "<b>25 новых цветов</b> облицовочного кирпича",
    "sub": "Баварская кладка, сахара, скала антик — уже в каталоге.",
    "cta": "Смотреть новинки",
    "href": "kirpich-ves.html",
    "img": "img/cat-oblic.jpg",
}

SLIDE_DELIVERY = {
    "eyebrow": "Доставка",
    "title": "Доставим на объект — <b>оплата при получении</b>",
    "sub": "Разгрузка манипулятором. Фото и видео товара — в WhatsApp до отправки.",
    "cta": "Как заказать",
    "href": "#lead",
    "img": "img/plitka/work-05.jpg",
}
