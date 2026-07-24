#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Раздел «Кровля»: krovlya.html + tovar/krovlya-*.html × 16.

Данные: data/roof_images.json (собирает build_roof_images.py — галереи,
схемы, кружки цветов) + описания товаров здесь, руками, простым языком
(спеки выверены по txt поставщика и заводскому прайсу 16.07.2026).

Один поставщик, имя завода скрыто. Цены на сайт не выносим (наценка не
утверждена) — везде «Цена по запросу» и кнопки связи. Металлочерепица/
штакетник/сайдинг — чистые кадры из галереи завода. У профнастила чистых
фото на сайте поставщика нет вообще (только у этих 6 позиций — снято под
тайловым водяным знаком по всему кадру, не только у моделей на витрине);
по решению пользователя (17.07.2026) временно грузим фото КАК ЕСТЬ, со
знаком — до появления чистых снимков или замены на AI-фото. Плюс чертежи
профилей и кружки реальных текстур покрытий везде.

Пересборка: build_roof_images.py → build_roof.py.
"""

import html
import json
from urllib.parse import quote
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from banner_common import banner, BANNER_JS, SLIDE_SALE_TILE, SLIDE_DELIVERY

BASE = Path("/Users/dm/Desktop/сайт")

# Абсолютный адрес сайта — для JSON-LD (относительные пути из /tovar/ бьются)
SITE_URL = "https://martinoneisha299-lang.github.io/stroy-sale/"
TOVAR = BASE / "tovar"
TOVAR.mkdir(exist_ok=True)

IMG = json.loads((BASE / "data" / "roof_images.json").read_text())
COLORS = IMG["colors"]
P_COLORS = IMG["product_colors"]
P_IMAGES = IMG["products"]

STYLES_V = 34
IMG_V = 4


def esc(s):
    return html.escape(str(s), quote=True)


# ───────────────────────── каркас страницы (общий язык сайта) ──────────
WA_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z"/></svg>'
TG_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>'
PHONE_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>'
ARR_SVG = ('<svg class="arr" width="16" height="16" viewBox="0 0 24 24" fill="none" '
           'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
           'stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')


def callbar(root=""):
    wa = "https://wa.me/79000000000?text=" + quote("Здравствуйте! Пишу с сайта Строй-Сейл")
    return f"""
  <nav class="callbar" aria-label="Быстрая связь">
    <a class="callbar-item callbar-tel" href="tel:+79000000000">
      {PHONE_SVG}
      <span>Позвонить</span></a>
    <a class="callbar-item cb-wa" href="{wa}" target="_blank" rel="noopener">
      {WA_SVG}
      <span>WhatsApp</span></a>
    <a class="callbar-item cb-tg" href="https://t.me/stroy_sale" target="_blank" rel="noopener">
      {TG_SVG}
      <span>Telegram</span></a>
    <a class="callbar-item cb-max" href="https://max.ru/stroy_sale" target="_blank" rel="noopener">
      <img src="{root}img/max-icon.svg" alt="" width="24" height="24">
      <span>MAX</span></a>
  </nav>"""


def promo_bar(root=""):
    return (f'<a class="promo-bar" href="{root}plitka-staryy-gorod.html" data-until="2026-08-03" hidden>'
            f'<b>−15%</b> на плитку «Старый город» — до 3 августа'
            f'<span class="promo-bar-go"> · Выбрать</span></a>')


def msg_circles(root="", product="", label="Быстрый ответ в мессенджере:"):
    txt = (f"Здравствуйте! Интересует {product} (пишу с сайта Строй-Сейл)"
           if product else "Здравствуйте! Пишу с сайта Строй-Сейл")
    wa = "https://wa.me/79000000000?text=" + quote(txt)
    return f"""<p class="msg-row">
          <span class="msg-row-label">{label}</span>
          <a class="msg-circle mc-wa" href="{wa}" target="_blank" rel="noopener" aria-label="Написать в WhatsApp">{WA_SVG}</a>
          <a class="msg-circle mc-tg" href="https://t.me/stroy_sale" target="_blank" rel="noopener" aria-label="Написать в Telegram">{TG_SVG}</a>
          <a class="msg-circle mc-max" href="https://max.ru/stroy_sale" target="_blank" rel="noopener" aria-label="Написать в MAX"><img src="{root}img/max-icon-white.svg" alt="" width="22" height="22"></a>
        </p>"""


def order_btns():
    return """<div class="order-block">
          <div class="order-row">
            <a class="btn" href="tel:+79000000000">Позвонить</a>
            <a class="btn btn-ghost" href="#lead">Заказать звонок</a>
          </div>
        </div>"""


SHELL_JS = """
  <script>
    (function () {
      var f = document.getElementById('ctaForm');
      if (f) {
        f.addEventListener('submit', function (e) {
          e.preventDefault();
          var ph = document.getElementById('cfPhone');
          var err = document.getElementById('ctaErr');
          var digits = (ph.value.match(/\\d/g) || []).length;
          if (digits < 10) {
            if (err) { err.hidden = false; ph.setAttribute('aria-describedby', 'ctaErr'); }
            ph.focus();
            return;
          }
          if (err) err.hidden = true;
          f.hidden = true;
          document.getElementById('ctaOk').hidden = false;
        });
      }
      var promo = document.querySelector('.promo-bar');
      if (promo && promo.dataset.until) {
        var end = new Date(promo.dataset.until + 'T23:59:59');
        if (new Date() > end) { promo.remove(); } else { promo.hidden = false; }
      }
    })();
  </script>"""

GALLERY_JS = """
  <script>
    (function () {
      var main = document.getElementById('pdMain');
      var thumbs = Array.prototype.slice.call(document.querySelectorAll('.pd-thumb'));
      if (!main || !thumbs.length) return;
      thumbs.forEach(function (t) {
        t.addEventListener('click', function () {
          if (main.src === t.dataset.src) return;
          main.classList.add('is-fading');
          setTimeout(function () {
            main.src = t.dataset.src;
            main.alt = t.dataset.alt || main.alt;
            setTimeout(function () { main.classList.remove('is-fading'); }, 120);
          }, 120);
          thumbs.forEach(function (x) {
            x.classList.toggle('is-on', x === t);
            x.setAttribute('aria-pressed', x === t ? 'true' : 'false');
          });
        });
      });
    })();
  </script>"""


def page_shell(title, descr, body, cta_h2, cta_note, extra_js="", root="",
               extra_head="", product="", promo=True):
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{descr}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600;700;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{root}styles.css?v={STYLES_V}">{extra_head}
</head>
<body>

{promo_bar(root) if promo else ""}

  <header class="masthead">
    <div class="wrap masthead-in">
      <a class="wordmark" href="{root}index.html">
        <svg class="brand-mark" viewBox="0 0 100 88" aria-hidden="true"><path fill="var(--color-logo)" d="M50 4 L96 84 H70 L50 36 L30 84 H4 Z"/></svg>
        <span class="wordmark-text"><strong>СТРОЙСЕЙЛ</strong>
        <span><span class="wm-long">Стройматериалы · </span>Краснодар</span></span>
      </a>
      <nav class="masthead-nav" aria-label="Основное меню">
        <a href="{root}index.html#catalog">Каталог</a>
        <a href="{root}index.html#order">Доставка и оплата</a>
        <a href="{root}index.html#lead">Контакты</a>
      </nav>
      <div class="masthead-contact">
        <a href="tel:+79000000000">+7 (900) 000-00-00</a>
        <small>Перезвоним за 5 минут</small>
      </div>
    </div>
  </header>

{body}

  <section class="section" id="lead">
    <div class="wrap">
      <div class="cta-band">
        <div>
          <h2>{cta_h2}</h2>
          <p class="caption">{cta_note}</p>
        </div>
        <div class="cta-grid">
          <div class="cta-left">
            <a class="cta-phone" href="tel:+79000000000">+7 (900) 000-00-00
              <small>Перезвоним за 5 минут</small></a>
            {msg_circles(root, product, label="Или напишите:")}
          </div>
          <form class="cta-form" id="ctaForm" novalidate>
            <div class="field">
              <label for="cfName">Имя</label>
              <input id="cfName" name="name" type="text" autocomplete="name" placeholder="Как к вам обращаться">
            </div>
            <div class="field">
              <label for="cfPhone">Телефон</label>
              <input id="cfPhone" name="phone" type="tel" autocomplete="tel" inputmode="tel" placeholder="+7 (___) ___-__-__" required>
            </div>
            <button class="btn" type="submit">Оставить заявку</button>
            <p class="form-err" id="ctaErr" hidden>Проверьте номер — в нём не хватает цифр.</p>
            <p class="caption form-note">Нажимая кнопку, вы соглашаетесь с
              <a href="{root}policy.html">политикой конфиденциальности</a>.
              Номер не передаём третьим лицам.</p>
          </form>
          <p class="form-ok" id="ctaOk" role="status" hidden>Заявка принята — скоро перезвоним.</p>
        </div>
      </div>
    </div>
  </section>

  <footer class="footer">
    <div class="wrap footer-in">
      <span class="tag">Строй-Сейл · Краснодар · 2026</span>
      <a href="tel:+79000000000">+7 (900) 000-00-00</a>
      <span class="caption footer-addr">Краснодар, ул. Ореховая, 182</span>
      <span class="caption">Работаем с частными застройщиками, прорабами и бригадами</span>
      <span class="caption">Цены на сайте не являются публичной офертой</span>
      <a class="footer-policy caption" href="{root}policy.html">Политика конфиденциальности</a>
    </div>
  </footer>
{callbar(root)}{SHELL_JS}
{extra_js}
</body>
</html>
"""


# ───────────────────────────── данные раздела ──────────────────────────
SERIES = [
    ("polyester", "Полиэстер", "20 цветов",
     "Стандартное глянцевое покрытие — им красят большинство крыш и заборов. "
     "Сталь 0,4–0,5 мм, гарантия покрытия до 10 лет."),
    ("granite", "Granite Deep Mat", "7 цветов",
     "Плотное матовое покрытие 35 мкм: не бликует на солнце, дольше держит "
     "цвет. Гарантия до 15 лет."),
    ("printech", "Printech — под дерево и камень", "12 рисунков",
     "Фотопечать структуры дерева, кирпича и камня. Любимое покрытие для "
     "штакетника и сайдинга: издалека не отличить от дерева."),
    ("zink", "Цинк", "без покраски",
     "Оцинкованный лист без краски — рабочий вариант для хозпостроек "
     "и черновых работ."),
]

# порядок кружков внутри серии — как в палитре поставщика
SERIES_ORDER = {}
for _slug, _c in COLORS.items():
    SERIES_ORDER.setdefault(_c["series"], []).append(_slug)

MCH = [
    dict(
        id="mch-monterrey", name="Супермонтеррей",
        kind="Металлочерепица",
        meta="классический профиль под черепицу",
        blurb="Классика загородных крыш: профиль повторяет керамическую "
              "черепицу. Берут чаще всего.",
        use="крыша жилого дома, коттеджа, бани — любая скатная кровля "
            "с уклоном от 14°",
        specs=[
            ("Ширина листа", "1,18 м (полезная — 1,10 м)"),
            ("Высота волны", "24 мм, шаг 350 мм"),
            ("Длина листа", "режем в размер от 0,8 до 8 м"),
            ("Сталь", "0,4–0,5 мм, оцинковка + полимерное покрытие"),
            ("Уклон крыши", "от 14°"),
        ],
    ),
    dict(
        id="mch-dyuna", name="Испанская дюна",
        kind="Металлочерепица",
        meta="модульный профиль · скрытое крепление",
        blurb="Модули со сдвигом, как у настоящей черепицы, и скрытое "
              "крепление — саморезов на крыше не видно.",
        use="крыша дома, когда важен вид: стыки листов не заметны, крыша "
            "выглядит монолитной; уклон от 35°",
        specs=[
            ("Ширина листа", "1,17 м (полезная — 1,04 м)"),
            ("Высота волны", "25 или 35 мм, шаг 350 мм"),
            ("Длина листа", "режем в размер от 0,8 до 8 м"),
            ("Сталь", "0,45–0,5 мм, оцинковка + полимерное покрытие"),
            ("Крепление", "скрытое — без открытых саморезов"),
        ],
    ),
]

PROF = [
    dict(
        id="prof-s8", name="С-8", kind="Профнастил",
        meta="самый ходовой для сплошного забора",
        blurb="Самый ходовой для сплошных заборов и обшивки стен: широкий "
              "лист, перекрывает больше за те же деньги.",
        use="сплошной забор, обшивка стен, фронтонов и хозпостроек; на крышу "
            "— только с уклоном от 30°",
        specs=[
            ("Ширина листа", "1,20 м (полезная — 1,15 м)"),
            ("Высота волны", "8 мм"),
            ("Длина листа", "режем в размер от 0,3 до 12 м"),
            ("Сталь", "0,32–0,7 мм на выбор"),
        ],
    ),
    dict(
        id="prof-s10", name="С-10", kind="Профнастил",
        meta="для заборов повыше и обшивки стен",
        blurb="Чуть жёстче С-8 — для заборов повыше и обшивки, где нужен "
              "запас прочности.",
        use="заборы, обшивка стен и потолков, временные постройки; кровля — "
            "по сплошной обрешётке с уклоном от 30°",
        specs=[
            ("Ширина листа", "1,18 м (полезная — 1,10 м)"),
            ("Высота волны", "10 мм"),
            ("Длина листа", "режем в размер от 0,3 до 12 м"),
            ("Сталь", "0,32–0,7 мм на выбор"),
        ],
    ),
    dict(
        id="prof-s21", name="С-21", kind="Профнастил",
        meta="симметричный — аккуратен с двух сторон",
        blurb="Симметричный профиль, одинаково аккуратный с обеих сторон — "
              "любимец заборов «для соседей не стыдно» и простых крыш.",
        use="забор, который смотрят с двух сторон; крыша гаража, навеса, "
            "хозпостройки",
        specs=[
            ("Ширина листа", "1,05 м (полезная — 1,00 м)"),
            ("Высота волны", "21 мм, симметричная"),
            ("Длина листа", "режем в размер от 0,3 до 12 м"),
            ("Сталь", "0,4–0,7 мм на выбор"),
        ],
    ),
    dict(
        id="prof-mp20", name="МП-20", kind="Профнастил",
        meta="кровельный, с водоотводной канавкой",
        blurb="Кровельный вариант (тип R) с капиллярной канавкой: отводит "
              "воду из стыка листов — под кровлю не затекает.",
        use="крыша дома и построек (вариант R с канавкой), заборы и обшивка "
            "(варианты А и В)",
        specs=[
            ("Ширина листа", "1,15 м (полезная — 1,10 м)"),
            ("Высота волны", "20 мм"),
            ("Длина листа", "режем в размер от 0,3 до 12 м"),
            ("Особенность", "капиллярная канавка на кровельном варианте"),
        ],
    ),
    dict(
        id="prof-ns35", name="НС-35", kind="Профнастил",
        meta="жёсткий — для кровли и навесов",
        blurb="Высокая трапеция с рёбрами жёсткости: держит снег и редкую "
              "обрешётку — для крыш и навесов.",
        use="крыша дома, навесы и козырьки, каркасные постройки; выдерживает "
            "высокую снеговую нагрузку",
        specs=[
            ("Ширина листа", "1,06 м (полезная — 1,00 м)"),
            ("Высота волны", "35 мм + рёбра жёсткости"),
            ("Длина листа", "режем в размер от 0,3 до 12 м"),
            ("Сталь", "0,45–0,7 мм на выбор"),
        ],
    ),
    dict(
        id="prof-n60", name="Н-60", kind="Профнастил",
        meta="несущий — пролёты до 6 метров",
        blurb="Несущий лист для больших пролётов: перекрытия, козырьки, "
              "несъёмная опалубка — до 6 метров без прогиба.",
        use="перекрытия и пролёты до 6 м, промышленные кровли, несъёмная "
            "опалубка",
        specs=[
            ("Ширина листа", "0,90 м (полезная — 0,845 м)"),
            ("Высота волны", "60 мм + борозды жёсткости"),
            ("Длина листа", "режем в размер от 0,3 до 14 м"),
            ("Сталь", "0,5–0,7 мм"),
        ],
    ),
]

SHT = [
    dict(
        id="sht-kruglyy", name="Евроштакетник круглый", kind="Штакетник",
        meta="скруглённый верх · ширина 130 мм",
        blurb="Плавная линия верха — самый мягкий и «домашний» вариант.",
        use="забор и палисадник с просветом: не парусит на ветру, двор "
            "не в глухой тени",
        specs=[
            ("Ширина планки", "130 мм"),
            ("Высота профиля", "19,5 мм"),
            ("Длина", "режем в размер от 0,5 до 3 м"),
            ("Верх планки", "скруглённый, кромка завальцована"),
        ],
    ),
    dict(
        id="sht-trapetsiya", name="Евроштакетник трапеция", kind="Штакетник",
        meta="скошенный верх · ширина 120 мм",
        blurb="Трапециевидный рез — строже круглого, ритмичный «частокол».",
        use="забор с просветом в строгом стиле — к дому с чёткими линиями",
        specs=[
            ("Ширина планки", "120 мм"),
            ("Высота профиля", "19,5 мм"),
            ("Длина", "режем в размер от 0,5 до 3 м"),
            ("Верх планки", "трапеция"),
        ],
    ),
    dict(
        id="sht-pryamoy", name="Штакетник с прямым резом", kind="Штакетник",
        meta="прямой верх · ширина 130 мм",
        blurb="Ровный срез без фигурного верха — лаконично и дешевле "
              "фигурных.",
        use="строгое ограждение без лишних деталей; хорошо смотрится "
            "с современными домами",
        specs=[
            ("Ширина планки", "130 мм"),
            ("Высота профиля", "19,5 мм"),
            ("Длина", "режем в размер от 0,5 до 3 м"),
            ("Верх планки", "прямой рез"),
        ],
    ),
]

SID = [
    dict(
        id="sid-korabelnaya", name="Корабельная доска", kind="Металлосайдинг",
        meta="классика · панель 260 мм",
        blurb="Классический профиль «доска за доской» — самый привычный вид "
              "обшитого фасада.",
        use="обшивка фасада дома, фронтонов, хозпостроек",
        specs=[
            ("Ширина панели", "260 мм (полезная — 226 мм)"),
            ("Высота профиля", "14 мм"),
            ("Длина", "режем в размер от 0,5 до 6 м"),
        ],
    ),
    dict(
        id="sid-korabelnaya-evro", name="Корабельная доска Евро",
        kind="Металлосайдинг",
        meta="узкий шов · панель 260 мм",
        blurb="Та же доска, но с более узким швом — фасад выглядит ровнее.",
        use="обшивка фасада, когда хочется меньше заметных стыков",
        specs=[
            ("Ширина панели", "260 мм (полезная — 229 мм)"),
            ("Высота профиля", "14 мм"),
            ("Длина", "режем в размер от 0,5 до 6 м"),
        ],
    ),
    dict(
        id="sid-brus-klassik", name="Евробрус Классик", kind="Металлосайдинг",
        meta="под брус · панель 270 мм",
        blurb="Имитация деревянного бруса: с покрытием Printech фасад "
              "не отличить от сруба.",
        use="фасад «под дерево» без ухода за деревом — не гниёт, не горит, "
            "не надо красить",
        specs=[
            ("Ширина панели", "270 мм (полезная — 220 мм)"),
            ("Длина", "режем в размер от 0,3 до 6 м"),
            ("Покрытие", "чаще берут Printech под дерево"),
        ],
    ),
    dict(
        id="sid-brus-riflenyy", name="Евробрус Рифлёный", kind="Металлосайдинг",
        meta="под брус · рифлёная поверхность",
        blurb="Тот же брус, но с рифлением — глубже тень, фактурнее фасад.",
        use="фасад под дерево с выраженной фактурой",
        specs=[
            ("Ширина панели", "267 мм (полезная — 240 мм)"),
            ("Длина", "режем в размер от 0,3 до 6 м"),
            ("Покрытие", "чаще берут Printech под дерево"),
        ],
    ),
    dict(
        id="sid-sofit", name="Софит перфорированный", kind="Металлосайдинг",
        meta="подшивка свесов · с вентиляцией",
        blurb="Панель для подшивки свесов крыши: перфорация проветривает "
              "подкровельное пространство.",
        use="подшивка карнизных и фронтонных свесов — крыша «дышит», "
            "птицы и осы внутрь не попадают",
        specs=[
            ("Ширина панели", "267 мм (полезная — 240 мм)"),
            ("Длина", "режем в размер от 0,3 до 6 м"),
            ("Перфорация", "по всей панели"),
        ],
    ),
]

ALL_PRODUCTS = MCH + PROF + SHT + SID
BY_ID = {p["id"]: p for p in ALL_PRODUCTS}

# Две ключевые цифры на карточку сетки (как «ширина/высота» у конкурента) —
# карточка сразу говорит размер, а не только название.
CARD_SPECS = {
    "mch-monterrey": [("Полезная", "1,10 м"), ("Волна", "24 мм")],
    "mch-dyuna":     [("Полезная", "1,04 м"), ("Волна", "25–35 мм")],
    "prof-s8":       [("Полезная", "1,15 м"), ("Волна", "8 мм")],
    "prof-s10":      [("Полезная", "1,10 м"), ("Волна", "10 мм")],
    "prof-s21":      [("Полезная", "1,00 м"), ("Волна", "21 мм")],
    "prof-mp20":     [("Полезная", "1,10 м"), ("Волна", "20 мм")],
    "prof-ns35":     [("Полезная", "1,00 м"), ("Волна", "35 мм")],
    "prof-n60":      [("Полезная", "0,845 м"), ("Волна", "60 мм")],
}

# ── Семейства = «категории»: путь категория → товар → цвет (как у europrofil93
#    и как у нас в плитке). Сетка карточек для семейств с фото/чертежами,
#    фото+список (duo) для «бедных на фото» штакетника и сайдинга. ──────────
FAMILIES = [
    dict(
        slug="metallocherepitsa", title="Металлочерепица", short="Металлочерепица",
        kind="Металлочерепица", tag="Для крыши дома", layout="grid",
        products=MCH,
        sub="Два профиля — оба режем в размер ската, крыша собирается "
            "без горизонтальных стыков.",
        card="2 профиля · для скатной крыши",
        cover="cover-mch-monterrey.jpg", cover_scheme=False,
        cover_alt="Металлочерепица крупным планом",
        hub_cover="cover-cat-mch.jpg",
        hub_alt="Красная глянцевая металлочерепица с каплями дождя",
        note="Оба профиля — сталь 0,4–0,5 мм с полимерным покрытием, "
             "40 цветов. Цену и раскрой посчитаем по вашим размерам.",
        cta_h2="Посчитаем черепицу по вашей крыше",
        cta_note="Пришлите размеры или фото чертежа — вернём раскрой листов, "
                  "доборные и цену с доставкой.",
    ),
    dict(
        slug="profnastil", title="Профнастил", short="Профнастил",
        kind="Профнастил", tag="Крыша · забор · навес", layout="grid",
        products=PROF,
        sub="Шесть профилей — от лёгкого заборного С-8 до несущего Н-60. "
            "Внутри каждого — фото, чертёж волны и все размеры.",
        card="6 профилей · крыша, забор, навес",
        cover="roof-prof-s8.jpg", cover_scheme=False,
        cover_alt="Профнастил крупным планом",
        hub_cover="cover-cat-prof.jpg",
        hub_alt="Профнастил серо-синего цвета крупным планом",
        note="Не хотите разбираться в профилях? Назовите задачу — "
             "подберём марку и посчитаем количество.",
        cta_h2="Подберём профиль и посчитаем листы",
        cta_note="Скажите, что закрываете — крышу, забор или стены. "
                  "Подберём марку, цвет и цену с доставкой.",
    ),
    dict(
        slug="shtaketnik", title="Штакетник", short="Штакетник",
        kind="Штакетник", tag="Для забора", layout="grid",
        products=SHT,
        sub="Металлические планки с просветом: двор проветривается, "
            "забор не парусит. Три формы верха, 12 цветов и рисунки под дерево.",
        card="3 формы верха · для забора",
        cover="sec-shtaketnik.jpg", cover_scheme=False,
        cover_alt="Забор из графитового евроштакетника на фоне зелени",
        hub_cover="cover-cat-sht.jpg",
        hub_alt="Планки графитового евроштакетника крупным планом",
        note="Кромки завальцованы — без острых краёв. Не знаете, какой верх "
             "выбрать, — пришлём фото заборов в цвете и подскажем по вашему дому.",
        duo_note="Евроштакетник круглый в цвете «Графит». Кромки завальцованы — "
                 "без острых краёв.",
        cta_h2="Посчитаем забор по вашим метрам",
        cta_note="Пришлите длину забора и высоту — посчитаем планки, столбы "
                  "и цену с доставкой.",
    ),
    dict(
        slug="sayding", title="Металлосайдинг и софиты", short="Металлосайдинг",
        kind="Металлосайдинг", tag="Для фасада и свесов", layout="grid",
        products=SID, printech_live=True,
        sub="Обшивка, которую не надо красить и пропитывать: металл с рисунком "
            "дерева не гниёт, не выгорает и не боится огня.",
        card="5 профилей · для фасада и свесов",
        cover="sec-sayding.jpg", cover_scheme=False,
        cover_alt="Металлосайдинг с фотопечатью под тёмное дерево крупным планом",
        hub_cover="cover-cat-sid.jpg",
        hub_alt="Металлосайдинг с фотопечатью под серое дерево крупным планом",
        note="Рисунок дерева — фотопечать Printech на стали, не выгорает. "
             "Пришлите фото дома — подскажем профиль и посчитаем площадь.",
        duo_note="Покрытие Printech: рисунок дерева — фотопечать на стали.",
        cta_h2="Посчитаем фасад по вашим размерам",
        cta_note="Пришлите площадь стен или фото дома — подберём профиль, "
                  "цвет и цену с доставкой.",
    ),
]
FAMILY_BY_SLUG = {f["slug"]: f for f in FAMILIES}
FAMILY_OF = {p["id"]: f for f in FAMILIES for p in f["products"]}

# Компактная палитра-тизер «один цвет — на всё»: спред по всем сериям
ROOF_TEASER_COLORS = [
    "ral-1014-bezhevyi", "ral-3005-spelaya-vishnya", "ral-3011-krasno-korichnevyi",
    "ral-1018-zhe-ltyi", "ral-6002-zelenyi-list", "ral-6005-zele-nyi-moh",
    "ral-5002-ultramarin", "ral-7024-grafitovyi-seryi", "ral-8017-shokolad",
    "ral-9003-belyi", "granite-deep-mat-8004", "granite-deep-mat-9005",
    "granite-deep-mat-6020", "antichnyi-dub", "oreh-temnyi",
    "svetloe-derevo", "kirpich", "tsink",
]

# Доборные и водосток — без своих страниц: подбирает менеджер в цвет кровли
DOBORNYE = [
    "Конёк фигурный", "Конёк полукруглый", "Конёк-ребро",
    "Заглушки конька", "Планка карнизная", "Планка ветровая",
    "Планка лобовая", "Ендова верхняя и нижняя", "Планки примыкания",
    "Планки углов", "Планка снегозадержателя", "Планка диагональная",
    "L-планка заборная",
]
VODOSTOK = [
    "Круглая система «Оптима» 125/90 — желоба, трубы, углы, воронки",
    "Прямоугольная гофрированная система — желоба, трубы, колена",
    "Крюки, крепления, заглушки — весь крепёж в комплекте",
]
SAFETY = [
    "Снегозадержатели трубчатые, 1 м и 3 м",
    "Кровельные ограждения, высота 650 и 900 мм",
]


# ─────────────────────────────── куски разметки ────────────────────────
def gallery_html(pid, name, kind, root=""):
    """Галерея товара: чистые фото + чертёж; без визуала — честная заглушка."""
    entry = P_IMAGES[pid]
    items = []          # (src, alt, подпись-метка для миниатюры)
    for i, g in enumerate(entry["gallery"], 1):
        items.append((f"{root}img/roof/{g}?v={IMG_V}",
                      f"{kind} «{name}» — фото {i}", None))
    if entry["scheme"]:
        items.append((f"{root}img/roof/{entry['scheme']}?v={IMG_V}",
                      f"{kind} «{name}» — чертёж профиля с размерами", "Чертёж"))
    if not items:
        ph = ('<div class="pd-none" role="img" aria-label="Фото пришлём по запросу">'
              '<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
              'stroke-width="1.5" stroke-linecap="round" aria-hidden="true">'
              '<rect x="3" y="8" width="18" height="9"/>'
              '<path d="M7 11h.01M12 11h.01M17 11h.01"/></svg>'
              '<span>Фото пришлём по запросу</span></div>')
        return f'<div class="pd-gallery">{ph}</div>'
    main_src, main_alt, _ = items[0]
    out = [f'<div class="pd-gallery">',
           f'<div class="pd-main-wrap" id="pdMainWrap">'
           f'<img class="pd-main" id="pdMain" src="{main_src}" alt="{esc(main_alt)}" '
           f'width="960" height="720"></div>']
    if len(items) > 1:
        thumbs = []
        for i, (src, alt, label) in enumerate(items):
            on = " is-on" if i == 0 else ""
            pressed = "true" if i == 0 else "false"
            aria = label or f"Фото {i + 1}"
            tag = f'<span class="pd-thumb-tag">{esc(label)}</span>' if label else ""
            cls = "pd-thumb pd-thumb--scheme" if label else "pd-thumb"
            thumbs.append(
                f'<button class="{cls}{on}" type="button" data-src="{src}" '
                f'data-alt="{esc(alt)}" aria-pressed="{pressed}" aria-label="{esc(aria)}">'
                f'{tag}<img src="{src}" alt="" width="960" height="720" loading="lazy"></button>')
        out.append(f'<div class="pd-thumbs">{"".join(thumbs)}</div>')
    out.append("</div>")
    return "".join(out)


def palette_html(pid=None, root="", note=None):
    """Палитра покрытий: серии с кружками. pid — ограничить цветами товара."""
    allowed = set(P_COLORS[pid]) if pid else None
    blocks = []
    for skey, sname, scount, sdesc in SERIES:
        slugs = [s for s in SERIES_ORDER.get(skey, [])
                 if allowed is None or s in allowed]
        if not slugs:
            continue
        dots = []
        for s in slugs:
            c = COLORS[s]
            code = f'<small class="pal-code">{esc(c["code"])}</small>' if c["code"] else ""
            dots.append(
                f'<li><img class="pal-dot" src="{root}img/roof/{c["sw"]}?v={IMG_V}" '
                f'alt="" width="62" height="62" loading="lazy">'
                f'<span class="pal-name">{esc(c["label"])}{code}</span></li>')
        count = f"{len(slugs)} " + plural(len(slugs), "цвет", "цвета", "цветов") \
            if skey != "zink" else "без покраски"
        blocks.append(
            f'<div class="palette-block">'
            f'<div class="palette-head"><h3>{esc(sname)} <small>· {count}</small></h3>'
            f'<p class="caption">{esc(sdesc)}</p></div>'
            f'<ul class="palette-row">{"".join(dots)}</ul></div>')
    note_html = f'<p class="caption cats-note">{note}</p>' if note else ""
    return "".join(blocks) + note_html


def plural(n, one, few, many):
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many


def grid_cls(n):
    """Класс сетки товаров: подбирает число колонок так, чтобы в последнем
    ряду не оставалась одна сиротливая карточка (5 + 1 читается как дыра).
    Большие каталоги не трогаем — там ряды и так плотные."""
    if n <= 1 or n > 20:
        return ""
    for c in (5, 4, 3, 2):
        if n % c == 0:
            return f" p-grid--c{c}"
    for c in (5, 4, 3):
        if n % c != 1:
            return f" p-grid--c{c}"
    return ""


def swatch_preview(pid, root=""):
    """Кружки цветов сразу под товаром — клиент видит, что есть варианты,
    не листая до палитры. Показываем первые 7, ссылка ведёт к полной палитре."""
    slugs = P_COLORS[pid]
    if not slugs:
        return ""
    cap = 7
    dots = "".join(
        f'<img class="pd-sw-dot" src="{root}img/roof/{COLORS[s]["sw"]}?v={IMG_V}" '
        f'alt="{esc(COLORS[s]["label"])}" width="44" height="44" loading="lazy">'
        for s in slugs[:cap])
    n = len(slugs)
    more = (f'<span class="pd-sw-more">+{n - cap}</span>' if n > cap else "")
    return (f'<a class="pd-swatches" href="#tsveta">'
            f'<span class="pd-sw-row">{dots}{more}</span>'
            f'<span class="pd-sw-label">{n} {plural(n, "цвет", "цвета", "цветов")} '
            f'и рисунков — посмотреть все</span></a>')


def card_colors(pid, root=""):
    """Кластер реальных кружков-образцов + счётчик прямо на карточке в сетке —
    клиент сразу видит, что палитра большая, не открывая товар."""
    slugs = P_COLORS.get(pid, [])
    if not slugs:
        return ""
    cap = 5
    dots = "".join(
        f'<img class="cc-dot" src="{root}img/roof/{COLORS[s]["sw"]}?v={IMG_V}" '
        f'alt="" width="28" height="28" loading="lazy">'
        for s in slugs[:cap])
    n = len(slugs)
    return (f'<p class="cat-colors"><span class="cc-row">{dots}</span>'
            f'<span class="cc-label">{n} {plural(n, "цвет", "цвета", "цветов")}</span></p>')


def product_card(p, root="", rich=False):
    """Карточка товара в сетке — та же, что у кирпича и плитки.
    rich=True добавляет две ключевые цифры и кластер цветов (сетка семейства)."""
    entry = P_IMAGES[p["id"]]
    cls = "p-img"
    if entry["gallery"]:
        src = f'{root}img/roof/{entry["gallery"][0]}?v={IMG_V}'
        alt = f'{p["kind"]} «{p["name"]}»'
    elif entry["scheme"]:
        src = f'{root}img/roof/{entry["scheme"]}?v={IMG_V}'
        alt = f'{p["kind"]} {p["name"]} — чертёж профиля'
        cls = "p-img p-img-scheme"
    else:
        src = None
    if src:
        img = (f'<img class="{cls}" src="{src}" alt="{esc(alt)}" '
               f'width="960" height="720" loading="lazy">')
    else:
        img = ('<div class="p-img p-none" role="img" aria-label="Фото готовим">'
               '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
               'stroke-width="1.5" stroke-linecap="round" aria-hidden="true">'
               '<rect x="3" y="8" width="18" height="9"/>'
               '<path d="M7 11h.01M12 11h.01M17 11h.01"/></svg>'
               '<span>Фото пришлём по запросу</span></div>')
    extra = (card_specs_html(p["id"]) + card_colors(p["id"], root)) if rich else ""
    return (f'<a class="p-card" href="{root}tovar/krovlya-{p["id"]}.html">'
            f'{img}<h3 class="p-name">{esc(p["name"])}</h3>'
            f'<p class="p-meta">{esc(p["meta"])}</p>{extra}'
            f'<span class="p-ask">Узнать цену</span></a>')


def cat_img(src, alt, scheme=False, root=""):
    cls = "cat-img cat-img-scheme" if scheme else "cat-img"
    return (f'<img class="{cls}" src="{root}img/roof/{src}?v={IMG_V}" '
            f'alt="{esc(alt)}" width="600" height="600" loading="lazy">')


def cat_card(href, img, title, caption, price="Узнать цену", extra=""):
    """Единая карточка сетки (как формы в плитке): фото/чертёж + имя + подпись."""
    price_html = f'<p class="cat-price">{esc(price)}</p>' if price else ""
    return (f'<a class="cat" href="{href}">{img}'
            f'<div class="cat-row"><h3>{esc(title)}</h3>{ARR_SVG}</div>'
            f'<p class="caption">{esc(caption)}</p>{extra}{price_html}</a>')


def card_specs_html(pid):
    """Компактная строка из двух ключевых цифр под подписью карточки."""
    specs = CARD_SPECS.get(pid)
    if not specs:
        return ""
    lis = "".join(f'<li><span>{esc(k)}</span><b>{esc(v)}</b></li>' for k, v in specs)
    return f'<ul class="cat-specs">{lis}</ul>'


def duo_rows(products, root=""):
    lis = []
    for p in products:
        lis.append(
            f'<li><a class="duo-item" href="{root}tovar/krovlya-{p["id"]}.html">'
            f'<div><h3>{esc(p["name"])}</h3>'
            f'<p class="caption">{esc(p["blurb"])}</p></div>{ARR_SVG}</a></li>')
    return f'<ul class="duo-list">{"".join(lis)}</ul>'


def color_strip(root=""):
    dots = "".join(
        f'<img src="{root}img/roof/{COLORS[s]["sw"]}?v={IMG_V}" '
        f'alt="{esc(COLORS[s]["label"])}" width="52" height="52" loading="lazy">'
        for s in ROOF_TEASER_COLORS)
    return f'<div class="color-strip">{dots}</div>'


def color_section(root="", n=40,
                  series="глянцевый полиэстер, матовый Granite, Printech под дерево и цинк"):
    """Компактный тизер «один цвет — на всё». Полная палитра — в карточке товара.
    n и series — по семейству: у штакетника 12 цветов, у сайдинга 22, не 40."""
    return f"""
  <section class="section" id="tsveta">
    <div class="wrap">
      <div class="section-head">
        <span class="tag">Палитра</span>
        <h2>Один цвет — на&nbsp;всё</h2>
        <p class="caption">Лист, конёк, планки, водосток и саморезы красим в один тон —
          крыша выглядит целой. {n} {plural(n, "оттенок", "оттенка", "оттенков")}: {series}.</p>
      </div>
      {color_strip(root)}
      <p class="caption cats-note">Полную палитру под каждый материал показываем
        в карточке товара. Перед заказом привезём образец вживую.</p>
    </div>
  </section>"""


def printech_live_section(root=""):
    return f"""
  <section class="section" aria-label="Printech вживую">
    <div class="wrap">
      <div class="section-head">
        <h2>Printech вживую</h2>
        <p class="caption">Так фотопечать под дерево выглядит на готовых панелях —
          рисунок не повторяется от планки к планке.</p>
      </div>
      <div class="works-grid-4">
        <img src="{root}img/roof/printech-live-1.jpg?v={IMG_V}" alt="Металлосайдинг под античный дуб" width="960" height="720" loading="lazy">
        <img src="{root}img/roof/printech-live-2.jpg?v={IMG_V}" alt="Металлосайдинг под тёмный орех" width="960" height="720" loading="lazy">
        <img src="{root}img/roof/printech-live-3.jpg?v={IMG_V}" alt="Металлосайдинг под светлую сосну" width="960" height="720" loading="lazy">
        <img src="{root}img/roof/printech-live-4.jpg?v={IMG_V}" alt="Металлосайдинг под белёное дерево" width="960" height="720" loading="lazy">
      </div>
    </div>
  </section>"""


ROOF_CALC_JS = """
  <script>
    (function () {
      var len = document.getElementById('rcLen');
      var wid = document.getElementById('rcWid');
      var typ = document.getElementById('rcType');
      var area = document.getElementById('rcArea');
      if (!len) return;
      function recalc() {
        var l = parseFloat(len.value), w = parseFloat(wid.value);
        if (!l || !w || l <= 0 || w <= 0) { area.textContent = '—'; return; }
        var k = parseFloat(typ.value);
        area.textContent = Math.ceil(l * w * k) + ' м²';
      }
      len.addEventListener('input', recalc);
      wid.addEventListener('input', recalc);
      typ.addEventListener('change', recalc);
    })();
  </script>"""


# ─────────────────────────────── общие куски хаба ──────────────────────
def kit_columns():
    cols = []
    for h3, items, cap in [
        ("Доборные элементы", DOBORNYE,
         "Коньки, планки и ендовы гнём на своём оборудовании — "
         "в цвет кровли, длина 2 м."),
        ("Водосточные системы", VODOSTOK,
         "Комплект под вашу крышу соберёт менеджер: желоба, трубы, крюки — "
         "ничего не забудем."),
        ("Безопасность кровли", SAFETY,
         "Снег сходит порциями, а не лавиной — обязательная вещь над входом "
         "и дорожками."),
    ]:
        lis = "".join(f"<li>{esc(i)}</li>" for i in items)
        cols.append(
            f'<div class="kit-col">'
            f'<h3>{esc(h3)}</h3>'
            f'<p class="caption">{esc(cap)}</p><ul>{lis}</ul></div>')
    return "".join(cols)


CALC_SECTION = f"""
  <!-- Калькулятор -->
  <section class="section" id="calc" aria-label="Калькулятор кровли">
    <div class="wrap">
      <div class="section-head">
        <span class="tag">Калькулятор</span>
        <h2>Прикиньте площадь крыши</h2>
      </div>
      <div class="line-calc">
        <div class="line-calc-wrap">
          <label class="line-calc-group" for="rcLen">
            <span class="line-calc-label">Длина <br>дома</span>
            <span class="line-calc-input-wrap">
              <input class="line-calc-input" id="rcLen" type="number" inputmode="decimal" min="1" max="100" step="0.1" placeholder="10">
              <span class="line-calc-unit">м</span>
            </span>
          </label>
          <label class="line-calc-group" for="rcWid">
            <span class="line-calc-label">Ширина <br>дома</span>
            <span class="line-calc-input-wrap">
              <input class="line-calc-input" id="rcWid" type="number" inputmode="decimal" min="1" max="100" step="0.1" placeholder="8">
              <span class="line-calc-unit">м</span>
            </span>
          </label>
          <label class="line-calc-group" for="rcType">
            <span class="line-calc-label">Тип <br>крыши</span>
            <select id="rcType">
              <option value="1.4" selected>Двускатная</option>
              <option value="1.5">Вальмовая (четыре ската)</option>
              <option value="1.15">Односкатная</option>
            </select>
          </label>
          <div class="line-calc-outputs">
            <div class="line-calc-block">
              <span class="line-calc-sub">Площадь кровли</span>
              <span class="line-calc-val val-accent" id="rcArea">—</span>
            </div>
          </div>
          <a class="btn line-calc-btn" href="#lead">Получить расчёт
            {ARR_SVG}</a>
        </div>
        <p class="caption line-calc-note">Оценка по размерам дома со свесами —
          чтобы прикинуть бюджет. Точный раскрой по листам сделает менеджер
          по вашим размерам или чертежу — бесплатно.</p>
      </div>
    </div>
  </section>"""


# ─────────────────────────────── страница-хаб «Кровля» ─────────────────
def build_hub():
    cards = []
    for f in FAMILIES:
        img = cat_img(f.get("hub_cover", f["cover"]),
                      f.get("hub_alt", f["cover_alt"]), False)
        cards.append(cat_card(f'krovlya-{f["slug"]}.html', img,
                              f["short"], f["card"], price=None,
                              extra=card_colors(f["products"][0]["id"])))

    hero = banner(
        "Кровля: металлочерепица и&nbsp;профнастил",
        "<b>лист до 8 м</b> · 40 цветов · гарантия до 15 лет",
        [{"eyebrow": "Расчёт",
          "title": "Посчитаем крышу по размерам <b>за 10 минут</b>",
          "sub": "Раскрой листов до 8 м без стыков, доборные и цена с доставкой.",
          "cta": "Посчитать крышу", "href": "#calc",
          "img": f"img/roof/hero-roof.jpg?v={IMG_V}"},
         {"eyebrow": "Металлочерепица",
          "title": "Гарантия на покрытие <b>до 15 лет</b>",
          "sub": "Супермонтеррей и Испанская дюна — с завода, режем в размер.",
          "cta": "Выбрать черепицу", "href": "krovlya-metallocherepitsa.html",
          "img": f"img/roof/cover-mch-monterrey.jpg?v={IMG_V}"},
         {"eyebrow": "Один цвет — на всё",
          "title": "<b>40 цветов</b>: кровля, забор и фасад в тон",
          "sub": "Полиэстер, Granite и Printech — покрытие общее для всех материалов.",
          "cta": "Смотреть цвета", "href": "#tsveta",
          "img": f"img/roof/printech-live-1.jpg?v={IMG_V}"},
         dict(SLIDE_DELIVERY,
              sub="Листы до 8 м возим аккуратно, разгрузка на месте.",
              img=f"img/roof/cover-cat-prof.jpg?v={IMG_V}")],
        crumb="Кровля")

    body = f"""
{hero}

  <!-- Четыре материала = четыре категории -->
  <section class="section" id="materialy">
    <div class="wrap">
      <div class="section-head">
        <h2>Выберите материал</h2>
        <p class="caption">Купить кровлю в Краснодаре: четыре материала с одного завода, режем в размер до 8 м без стыков. Внутри — товары, все размеры и 40&nbsp;цветов.</p>
      </div>
      <div class="cats cats-roof">{''.join(cards)}</div>
    </div>
  </section>

  <!-- Доборные, водосток, безопасность -->
  <section class="section" id="dobornye">
    <div class="wrap">
      <div class="section-head">
        <span class="tag">К любой кровле</span>
        <h2>Всё для крыши — сразу</h2>
        <p class="caption">Доборные, водосток и снегозадержатели подберём
          в цвет кровли и посчитаем по вашим размерам — одним заказом.</p>
      </div>
      <div class="kit">{kit_columns()}</div>
    </div>
  </section>

{color_section()}
{CALC_SECTION}"""

    out = page_shell(
        "Кровля в Краснодаре: металлочерепица и профнастил с завода — Строй-Сейл",
        "Металлочерепица, профнастил, штакетник и сайдинг с завода в Краснодаре. "
        "Режем в размер крыши до 8 м, 40 цветов, доборные и водосток в цвет. "
        "Доставка на объект, оплата при получении.",
        body,
        cta_h2="Посчитаем крышу по вашим размерам",
        cta_note="Пришлите размеры дома или фото чертежа — вернём раскрой листов, "
                 "количество доборных и цену с доставкой.",
        extra_js=ROOF_CALC_JS + BANNER_JS,
        product="кровля", promo=False)
    (BASE / "krovlya.html").write_text(out)


# ─────────────────────────────── страницы семейств ─────────────────────
def build_family(f):
    slug = f["slug"]
    head = f"""
  <section class="page-head">
    <div class="wrap">
      <nav class="crumbs" aria-label="Хлебные крошки">
        <a href="index.html">Главная</a> <span aria-hidden="true">/</span>
        <a href="krovlya.html">Кровля</a> <span aria-hidden="true">/</span>
        <span>{esc(f['title'])}</span>
      </nav>
      <h1>{esc(f['title'])}</h1>
      <p class="page-sub">{esc(f['sub'])}</p>
    </div>
  </section>"""

    if f["layout"] == "grid":
        # карточки товара — ровно те же, что в кирпиче и плитке: один размер
        # и один визуальный язык на всём сайте
        cards = "".join(product_card(p, rich=True) for p in f["products"])
        main = f"""
  <section class="section">
    <div class="wrap">
      <div class="p-grid{grid_cls(len(f["products"]))}">{cards}</div>
      <p class="caption cats-note">{esc(f['note'])}</p>
    </div>
  </section>"""
    else:  # duo: одно хорошее фото + список вариантов (для «бедных на фото»)
        main = f"""
  <section class="section">
    <div class="wrap">
      <div class="duo">
        <figure class="duo-img">
          <img src="img/roof/{f['cover']}?v={IMG_V}" alt="{esc(f['cover_alt'])}" width="1100" height="820" loading="lazy">
          <figcaption class="caption">{esc(f['duo_note'])}</figcaption>
        </figure>
        {duo_rows(f['products'])}
      </div>
    </div>
  </section>"""

    live = printech_live_section() if f.get("printech_live") else ""
    # палитра честная по семейству: МЧ/профнастил 40, штакетник 12, сайдинг 22
    first_pid = f["products"][0]["id"] if f.get("products") else None
    n_col = len(P_COLORS.get(first_pid, [])) or 40
    col_series = ("глянцевый полиэстер, матовый Granite, Printech под дерево и цинк"
                  if n_col >= 40 else "глянцевые, матовые и Printech под дерево")
    body = head + main + live + color_section(n=n_col, series=col_series)

    out = page_shell(
        f"{f['title']} в Краснодаре — цена с завода | Строй-Сейл",
        f"{f['title']}: {f['sub']} Заводские цены, режем в размер, "
        "доставка по Краснодару и краю, оплата при получении.",
        body,
        cta_h2=f["cta_h2"],
        cta_note=f["cta_note"],
        product=f["title"].lower())
    (BASE / f"krovlya-{slug}.html").write_text(out)


# ─────────────────────────────── товарные страницы ─────────────────────
def similar_html(p, root=""):
    """Другие товары того же вида (и соседние для черепицы/профнастила)."""
    if p in MCH:
        pool = [x for x in MCH if x is not p] + [BY_ID["prof-mp20"], BY_ID["prof-ns35"]]
        h2 = "Смотрят вместе с этим"
    elif p in PROF:
        pool = [x for x in PROF if x is not p][:4]
        h2 = "Другие профили"
    elif p in SHT:
        pool = [x for x in SHT if x is not p] + [BY_ID["prof-s8"], BY_ID["prof-s21"]]
        pool = pool[:4]
        h2 = "Другие варианты для забора"
    else:
        pool = [x for x in SID if x is not p][:4]
        h2 = "Другой сайдинг"
    shown = pool[:4]
    cards = "".join(product_card(x, root) for x in shown)
    fam = FAMILY_OF[p["id"]]
    return f"""
  <section class="section" aria-label="{esc(h2)}">
    <div class="wrap">
      <div class="section-head">
        <h2>{esc(h2)}</h2>
      </div>
      <div class="p-grid{grid_cls(len(shown))}">{cards}</div>
      <div class="more">
        <a class="btn btn-ghost" href="{root}krovlya-{fam['slug']}.html">В раздел «{esc(fam['title'])}»</a>
      </div>
    </div>
  </section>"""


def full_name(p):
    """«Профнастил МП-20», но без дубля вида: «Штакетник с прямым резом»,
    «Евробрус Классик» — имя уже говорит, что это за товар."""
    stems = ("штакетник", "софит", "доска", "брус")
    if any(s in p["name"].lower() for s in stems):
        return p["name"]
    return f'{p["kind"]} {p["name"]}'


def build_product(p):
    root = "../"
    pid = p["id"]
    fam = FAMILY_OF[pid]
    specs = "".join(f"<div><dt>{esc(dt)}</dt><dd>{esc(dd)}</dd></div>"
                    for dt, dd in p["specs"])
    n_colors = len(P_COLORS[pid])
    live = ""
    if p in SHT or p in SID:
        live = f"""
  <section class="section" aria-label="Покрытие под дерево вживую">
    <div class="wrap">
      <div class="section-head">
        <h2>Printech вживую</h2>
        <p class="caption">Фотопечать под дерево на готовых панелях —
          рисунок не повторяется от планки к планке.</p>
      </div>
      <div class="works-grid-4">
        <img src="{root}img/roof/printech-live-1.jpg?v={IMG_V}" alt="Покрытие под античный дуб" width="960" height="720" loading="lazy">
        <img src="{root}img/roof/printech-live-2.jpg?v={IMG_V}" alt="Покрытие под тёмный орех" width="960" height="720" loading="lazy">
        <img src="{root}img/roof/printech-live-3.jpg?v={IMG_V}" alt="Покрытие под светлую сосну" width="960" height="720" loading="lazy">
        <img src="{root}img/roof/printech-live-4.jpg?v={IMG_V}" alt="Покрытие под белёное дерево" width="960" height="720" loading="lazy">
      </div>
    </div>
  </section>"""

    body = f"""
  <section class="page-head">
    <div class="wrap">
      <nav class="crumbs" aria-label="Хлебные крошки">
        <a href="{root}index.html">Главная</a> <span aria-hidden="true">/</span>
        <a href="{root}krovlya.html">Кровля</a> <span aria-hidden="true">/</span>
        <a href="{root}krovlya-{fam['slug']}.html">{esc(fam['short'])}</a> <span aria-hidden="true">/</span>
        <span>{esc(p['name'])}</span>
      </nav>
    </div>
  </section>

  <section class="section pd" aria-label="Карточка товара">
    <div class="wrap pd-grid">
      {gallery_html(pid, p['name'], p['kind'], root)}
      <div class="pd-info">
        <p class="tag">{esc(p['kind'])}</p>
        <h1 class="pd-name">{esc(p['name'])}</h1>
        <p class="p-meta">{esc(p['meta'])}</p>
        <p class="pd-price pd-price-ask">Цена по запросу</p>
        <p class="caption pd-price-note">Цена зависит от покрытия и толщины стали.
          Назовите размеры — посчитаем и пришлём в WhatsApp за 5 минут.</p>
        <p class="caption pd-m2">Гарантия на покрытие — до 15 лет, точный срок
          зависит от серии цвета.</p>
        {swatch_preview(pid, root)}
        {order_btns()}
        <dl class="pd-specs">{specs}</dl>
        <p class="caption pd-usage"><strong>Куда подходит:</strong> {esc(p['use'])}.</p>
      </div>
    </div>
  </section>

  <section class="section" id="tsveta" aria-label="Цвета">
    <div class="wrap">
      <div class="section-head">
        <h2>Цвета — {n_colors} {plural(n_colors, 'вариант', 'варианта', 'вариантов')}</h2>
        <p class="caption">Доборные, планки и саморезы покрасим в тот же цвет.</p>
      </div>
      {palette_html(pid, root, note="Оттенок на экране — ориентир. Перед заказом покажем образец вживую.")}
    </div>
  </section>
{live}{similar_html(p, root)}"""

    ld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": full_name(p),
        "description": f"{full_name(p)}: {p['use']}.",
        "brand": {"@type": "Brand", "name": "Строй-Сейл"},
    }
    entry = P_IMAGES[pid]
    if entry["gallery"]:
        ld["image"] = f"{SITE_URL}img/roof/{entry['gallery'][0]}"
    extra_head = ('\n  <script type="application/ld+json">'
                  + json.dumps(ld, ensure_ascii=False) + "</script>")

    out = page_shell(
        f"{full_name(p)} — цена с завода в Краснодаре | Строй-Сейл",
        f"{full_name(p)}: {p['use']}. {n_colors} цветов, режем в размер. "
        "Доставка по Краснодару и краю, оплата при получении.",
        body,
        cta_h2="Пришлём цену и раскрой за 5 минут",
        cta_note="Назовите размеры — посчитаем листы, доборные и водосток, "
                 "скажем цену с доставкой на ваш адрес.",
        extra_js=GALLERY_JS, root=root,
        product=f"{p['kind'].lower()} «{p['name']}»",
        extra_head=extra_head)
    (TOVAR / f"krovlya-{pid}.html").write_text(out)


build_hub()
for _f in FAMILIES:
    build_family(_f)
for _p in ALL_PRODUCTS:
    build_product(_p)
print(f"OK: krovlya.html + {len(FAMILIES)} семейств + "
      f"{len(ALL_PRODUCTS)} товарных страниц")
