# -*- coding: utf-8 -*-
"""Шапка-обложка категории — общая для build_tiles / build_category / build_roof.

Макет «Обложка» (выбран пользователем 24.07.2026 из четырёх): фотография
во всю ширину без полей и скруглений, поверх неё — строка возврата
«← Каталог», имя категории и живые цифры; снизу — акция (этикетка,
заголовок, кнопка). Кадры сами меняются каждые 4 секунды, активный
медленно наезжает; под фото — полоска кирпичиков-прогресса.

Почему так: фотография и есть шапка (ДНК сайта — Petersen/Fireclay),
имя категории не тратит отдельную высоту, надпись читается за счёт
скрима сверху и снизу. Прежний «кирпичик» у h1 заменён на стрелку
возврата: это кнопка, а не украшение.

Механика: автолистание 4 с (и на телефоне тоже), пауза при наведении,
фокусе и уходе вкладки в фон, свайп пальцем, стрелки и счётчик на
десктопе, слайд с истёкшей data-until исчезает сам (как промо-полоса).
ВАЖНО: на страницах с обложкой промо-полосу .promo-bar не выводим
(promo=False в page_shell) — две акции друг над другом спорят.

Слайд — dict: eyebrow, title (HTML, акцент в <b>), sub, cta, href, img,
опционально until="ГГГГ-ММ-ДД".
"""

ARR_PREV = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M11 18l-6-6 6-6"/></svg>')
ARR_NEXT = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')
ARR_BACK = ('<svg width="17" height="17" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M11 18l-6-6 6-6"/></svg>')


def _frame(s, first, root=""):
    """Кадр — только фотография с вуалью. Лежит под строкой категории."""
    # первый кадр — LCP страницы: качаем сразу и с приоритетом
    load = ('loading="eager" fetchpriority="high"' if first else 'loading="lazy"')
    return f"""
        <div class="pb-frame">
          <img class="pb-photo" src="{root}{s['img']}" alt="" {load}>
          <div class="pb-veil"></div>
        </div>"""


def _slide(s):
    """Текст акции. Живёт во втором ряду сетки — под строкой категории,
    поэтому надписи не могут наехать друг на друга ни при каком шрифте."""
    until = f' data-until="{s["until"]}"' if s.get("until") else ""
    sub = f'\n            <p class="pb-sub">{s["sub"]}</p>' if s.get("sub") else ""
    return f"""
        <a class="pb-slide" href="{s['href']}"{until}><span class="wrap">
            <span class="pb-eyebrow">{s['eyebrow']}</span>
            <span class="pb-title">{s['title']}</span>{sub}
            <span class="pb-go">{s['cta']}</span>
        </span></a>"""


def banner(h1, facts, slides, root="", crumb=None):
    """Шапка-обложка категории. h1 — имя категории (HTML), facts — строка
    цифр (HTML, акцент в <b>), slides — список слайдов-акций."""
    crumb = crumb or h1
    frames_html = "".join(_frame(s, i == 0, root) for i, s in enumerate(slides))
    slides_html = "".join(_slide(s) for s in slides)
    return f"""
  <!-- Шапка-обложка: фото во всю ширину, акции сменяют друг друга (BANNER_JS) -->
  <section class="pb" aria-label="{crumb} — акции и предложения">
    <div class="pb-stage">
      <div class="pb-stack">{frames_html}
      </div>

      <div class="pb-head">
        <div class="wrap">
          <nav aria-label="Хлебные крошки">
            <a class="pb-back" href="{root}index.html#catalog">{ARR_BACK}Каталог</a>
          </nav>
          <h1>{h1}</h1>
          <p class="pb-facts">{facts}</p>
        </div>
      </div>

      <div class="pb-deck">{slides_html}
      </div>
    </div>

    <div class="pb-ui">
      <div class="wrap">
        <div class="pb-dots" aria-label="Переключение акций"></div>
        <span class="pb-count">01 / 0{len(slides)}</span>
        <button class="pb-arr pb-prev" type="button" aria-label="Предыдущая акция">{ARR_PREV}</button>
        <button class="pb-arr pb-next" type="button" aria-label="Следующая акция">{ARR_NEXT}</button>
      </div>
    </div>
  </section>"""


BANNER_JS = """
  <script>
    (function () {
      // Обложка категории: кадры меняются сами каждые 4 с — и на телефоне
      // тоже (просьба заказчика). Пауза при наведении, фокусе и когда
      // вкладка ушла в фон; палец листает свайпом. DUR держать равным
      // --pb-dur в styles.css — по нему заливается кирпичик-прогресс.
      var DUR = 4000;
      var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

      document.querySelectorAll('.pb').forEach(function (root) {
        var stack = root.querySelector('.pb-stack');
        var frames = Array.prototype.slice.call(root.querySelectorAll('.pb-frame'));
        var slides = Array.prototype.slice.call(root.querySelectorAll('.pb-slide'));
        var dotsWrap = root.querySelector('.pb-dots');
        var counter = root.querySelector('.pb-count');
        var ui = root.querySelector('.pb-ui');

        // акция с истёкшей датой убирается сама — вместе со своим кадром
        var now = new Date();
        for (var k = slides.length - 1; k >= 0; k--) {
          var till = slides[k].dataset.until;
          if (till && new Date(till + 'T23:59:59') < now) {
            slides[k].remove(); if (frames[k]) frames[k].remove();
            slides.splice(k, 1); frames.splice(k, 1);
          }
        }

        if (!slides.length) { if (stack) stack.hidden = true; if (ui) ui.hidden = true; return; }
        slides[0].classList.add('is-on');
        if (frames[0]) frames[0].classList.add('is-on');
        if (slides.length === 1) { if (ui) ui.hidden = true; return; }

        var i = 0, timer = null;
        var dots = slides.map(function (_, n) {
          var b = document.createElement('button');
          b.type = 'button'; b.className = 'pb-dot';
          b.setAttribute('aria-label', 'Акция ' + (n + 1) + ' из ' + slides.length);
          b.addEventListener('click', function () { go(n); start(); });
          dotsWrap.appendChild(b);
          return b;
        });

        function pad(n) { return (n < 10 ? '0' : '') + n; }
        function go(n) {
          slides[i].classList.remove('is-on'); dots[i].classList.remove('is-on');
          if (frames[i]) frames[i].classList.remove('is-on');
          i = (n + slides.length) % slides.length;
          slides[i].classList.add('is-on');
          if (frames[i]) frames[i].classList.add('is-on');
          // перезапуск заливки полоски: снять класс, дать браузеру
          // пересчитать элемент, вернуть — иначе анимация не стартует заново
          void dots[i].offsetWidth;
          dots[i].classList.add('is-on');
          if (counter) counter.textContent = pad(i + 1) + ' / ' + pad(slides.length);
        }
        function start() {
          if (reduced) return;
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

        // свайп пальцем: горизонтальный жест листает, вертикальный — скролл
        var stage = root.querySelector('.pb-stage');
        var x0 = null, y0 = null;
        stage.addEventListener('touchstart', function (e) {
          x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; stop();
        }, { passive: true });
        stage.addEventListener('touchend', function (e) {
          if (x0 === null) return;
          var dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
          if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) {
            e.preventDefault();
            go(i + (dx < 0 ? 1 : -1));
          }
          x0 = null; start();
        });

        dots[0].classList.add('is-on');
        if (counter) counter.textContent = '01 / ' + pad(slides.length);
        start();
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
