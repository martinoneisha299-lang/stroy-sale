#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tiles.json → страницы тротуарной плитки.

Генерирует:
- trotuarnaya-plitka.html — категория: герой с «живой» плиткой, 7 форм +
  плитка «Бордюры», бордюры, калькулятор, галерея работ + видео;
- plitka-<форма>.html × 7 — сетка цветов с фильтром, карточки → страницы товара;
- tovar/<форма>-<цвет>.html × 172 — карточка товара: галерея, цена,
  характеристики простым языком, калькулятор, другие расцветки.

Один поставщик → без лент коллекций: форма = страница. Имя завода скрыто.
"""

import html
import json
import re
from urllib.parse import quote
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from nbsp import typo
from banner_common import banner, BANNER_JS, SLIDE_SALE_TILE, SLIDE_NEW_BRICK, SLIDE_DELIVERY

BASE = Path("/Users/dm/Desktop/сайт")

# Абсолютный адрес сайта — для JSON-LD (относительные пути из /tovar/ бьются)
SITE_URL = "https://martinoneisha299-lang.github.io/stroy-sale/"
TOVAR = BASE / "tovar"
TOVAR.mkdir(exist_ok=True)
DATA = json.loads((BASE / "data" / "tiles.json").read_text())

PRODUCTS = DATA["products"]
SHAPES = DATA["shapes"]
BORDERS = DATA["borders"]
CAT_IMG = BASE / "img" / "catalog"
for p in PRODUCTS:
    p["_gallery"] = [f"img/catalog/{p['id']}.jpg"] + [
        f"img/catalog/{p['id']}-{i}.jpg" for i in (2, 3)
        if (CAT_IMG / f"{p['id']}-{i}.jpg").exists()]
    p["_thumb"] = (CAT_IMG / f"{p['id']}.jpg").exists()
    p["_url"] = f"tovar/{p['slug']}.html"

SHAPE_ORDER = ["novyy-gorod", "staryy-gorod", "bruschatka", "pryamougolnik",
               "myunhen", "parket", "asgard"]

# короткое «зачем эта форма» — по фото раскладок
SHAPE_NOTE = {
    "novyy-gorod": "Три размера в одной раскладке — берут чаще всего",
    "staryy-gorod": "Рисунок старой мостовой, мягкая фаска",
    "bruschatka": "Классический «кирпичик» — дорожки и парковки",
    "pryamougolnik": "Строгая сетка — современные дворы",
    "myunhen": "Крупный модуль, выглядит дорого",
    "parket": "Узкая доска — укладка «ёлочкой»",
    "asgard": "Крупный формат, парадные площадки",
}

# «куда берут» — для карточки товара, простым языком
SHAPE_USE = {
    "novyy-gorod": "дорожки, двор и отмостка вокруг дома; три размера "
                   "в раскладке прощают подрезку у стен и клумб",
    "staryy-gorod": "дорожки и площадки «под старину» — к кирпичному дому "
                    "и саду; мягкая фаска не собирает грязь в швах",
    "bruschatka": "садовые дорожки и стоянка легковой машины; классический "
                  "«кирпичик» кладётся любым рисунком — ёлочкой, плетёнкой",
    "pryamougolnik": "современные дворы со строгой сеткой швов; хорошо "
                     "смотрится с газоном и бетонной архитектурой",
    "myunhen": "просторные дворы и зоны отдыха; крупный модуль выглядит "
               "дорого и кладётся быстрее мелкой плитки",
    "parket": "акцентные зоны — вход, терраса, патио; узкая доска ёлочкой "
              "смотрится как паркет под открытым небом",
    "asgard": "парадные площадки и подъезд к дому; самый крупный формат "
              "каталога, минимум швов",
}

PALLET_M2 = 15  # м² в поддоне (из спеков)


def rub(v):
    return f"{v:,}".replace(",", " ")


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


def esc(s):
    return html.escape(str(s), quote=True)


# Глифы мессенджеров (simple-icons, CC0) — полоса связи и кнопки заказа
WA_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z"/></svg>'
TG_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>'
PHONE_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>'

WA_LINK = ("https://wa.me/79000000000?text=" +
           quote("Здравствуйте! Пишу с сайта Строй-Сейл"))


# Липкая полоса связи (видна только на телефоне).
# TODO перед запуском: реальный номер и ссылки мессенджеров.
def callbar(root=""):
    return f"""
  <nav class="callbar" aria-label="Быстрая связь">
    <a class="callbar-item callbar-tel" href="tel:+79000000000">
      {PHONE_SVG}
      <span>Позвонить</span></a>
    <a class="callbar-item cb-wa" href="{WA_LINK}" target="_blank" rel="noopener">
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
    """Сезонное предложение: тонкая полоска над шапкой. data-until — дата
    окончания; после неё полоска скрывается сама (скрипт в page_shell)."""
    return (f'<a class="promo-bar" href="{root}plitka-staryy-gorod.html" data-until="2026-08-03" hidden>'
            f'<b>−15%</b> на плитку «Старый город» — до 3 августа'
            f'<span class="promo-bar-go"> · Выбрать</span></a>')


def msg_circles(root="", product="", label="Быстрый ответ в мессенджере:"):
    """Тихий ряд мессенджеров: подпись + три фирменных кружка."""
    txt = (f"Здравствуйте! Интересует {product} (пишу с сайта Строй-Сейл)"
           if product else "Здравствуйте! Пишу с сайта Строй-Сейл")
    wa = "https://wa.me/79000000000?text=" + quote(txt)
    return f"""<p class="msg-row">
          <span class="msg-row-label">{label}</span>
          <a class="msg-circle mc-wa" href="{wa}" target="_blank" rel="noopener" aria-label="Написать в WhatsApp">{WA_SVG}</a>
          <a class="msg-circle mc-tg" href="https://t.me/stroy_sale" target="_blank" rel="noopener" aria-label="Написать в Telegram">{TG_SVG}</a>
          <a class="msg-circle mc-max" href="https://max.ru/stroy_sale" target="_blank" rel="noopener" aria-label="Написать в MAX"><img src="{root}img/max-icon-white.svg" alt="" width="22" height="22"></a>
        </p>"""


def order_btns(root="", product=""):
    """Блок заказа на карточке товара: одно главное действие + запасное.
    Мессенджеры здесь не дублируем — они в липкой полосе (мобайл) и в CTA-блоке."""
    return f"""<div class="order-block">
          <div class="order-row">
            <a class="btn" href="tel:+79000000000">Позвонить</a>
            <a class="btn btn-ghost" href="#lead">Заказать звонок</a>
          </div>
        </div>"""


# Скрипты каркаса: форма заявки (приём заявок подключается по ТЗ: Telegram + amoCRM)
# + промо-полоска (показывается только до даты data-until)
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


# Плавающая видео-миниатюра «производство» — только на странице категории.
# Лёгкий беззвучный клип (150 КБ) крутится в углу; тап — поп-ап с полным
# видео со звуком и кнопкой к калькулятору. Крестик прячет до конца визита.
X_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
         'stroke-width="2" stroke-linecap="round" aria-hidden="true">'
         '<path d="M18 6 6 18M6 6l12 12"/></svg>')

VIDEO_BUBBLE = f"""
  <div class="vb" id="vb">
    <button class="vb-mini" id="vbMini" type="button"
      aria-label="Смотреть видео с нашего производства">
      <video id="vbClip" data-src="img/plitka/works-video-mini.mp4"
        poster="img/plitka/works-video-mini-poster.jpg"
        muted loop playsinline preload="none" width="270" height="480"></video>
      <span class="vb-live" aria-hidden="true"><i></i>видео</span>
      <span class="vb-play" aria-hidden="true"><svg width="14" height="14" viewBox="0 0 24 24"
        fill="currentColor"><path d="M8 5v14l11-7z"/></svg></span>
      <span class="vb-cap" aria-hidden="true">Наше производство</span>
    </button>
    <button class="vb-hide" id="vbHide" type="button" aria-label="Скрыть видео">{X_SVG}</button>
  </div>
  <div class="vb-pop" id="vbPop" hidden>
    <button class="vb-back" id="vbBack" type="button" tabindex="-1" aria-hidden="true"></button>
    <figure class="vb-pop-body">
      <video id="vbFull" data-src="img/plitka/works-video.mp4"
        poster="img/plitka/works-video-poster.jpg"
        playsinline controls preload="none" width="360" height="640"></video>
      <a class="btn vb-cta" id="vbCta" href="#calc">Рассчитать плитку</a>
    </figure>
    <button class="vb-close" id="vbClose" type="button" aria-label="Закрыть видео">{X_SVG}</button>
  </div>"""

VIDEO_BUBBLE_JS = """
  <script>
    (function () {
      var vb = document.getElementById('vb'), pop = document.getElementById('vbPop');
      if (!vb) return;
      if (sessionStorage.getItem('vbOff')) { vb.remove(); pop.remove(); return; }
      var clip = document.getElementById('vbClip'),
          full = document.getElementById('vbFull'),
          mobile = window.matchMedia('(max-width: 899px)'),
          still = window.matchMedia('(prefers-reduced-motion: reduce)');
      if (!mobile.matches) { vb.remove(); pop.remove(); return; }

      // мягкое появление; при reduced motion — постер с кнопкой play вместо автоплея
      setTimeout(function () {
        vb.classList.add('vb-on');
        if (still.matches) { vb.classList.add('vb-rm'); return; }
        clip.src = clip.dataset.src;
        clip.play().catch(function () { vb.classList.add('vb-rm'); });
      }, 900);

      // доскроллил до видео-секции на странице — миниатюра прячется (дубль не нужен)
      var section = document.querySelector('.works-video');
      if (section && 'IntersectionObserver' in window) {
        new IntersectionObserver(function (es) {
          vb.classList.toggle('vb-away', es[0].isIntersecting);
        }, { threshold: 0.15 }).observe(section);
      }

      function open() {
        pop.hidden = false;
        requestAnimationFrame(function () { pop.classList.add('vb-pop-on'); });
        document.body.style.overflow = 'hidden';
        clip.pause();
        if (!full.src) full.src = full.dataset.src;
        full.currentTime = 0;
        full.muted = false;
        full.play().catch(function () {});
        document.getElementById('vbClose').focus();
      }
      function close() {
        pop.classList.remove('vb-pop-on');
        pop.hidden = true;
        document.body.style.overflow = '';
        full.pause();
        if (!still.matches && !vb.classList.contains('vb-rm')) clip.play().catch(function () {});
      }

      document.getElementById('vbMini').addEventListener('click', open);
      document.getElementById('vbClose').addEventListener('click', close);
      document.getElementById('vbBack').addEventListener('click', close);
      document.getElementById('vbCta').addEventListener('click', close);
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && !pop.hidden) close();
      });
      full.addEventListener('ended', close);
      document.getElementById('vbHide').addEventListener('click', function () {
        sessionStorage.setItem('vbOff', '1');
        vb.classList.remove('vb-on');
        setTimeout(function () { vb.remove(); pop.remove(); }, 400);
      });
    })();
  </script>"""


def page_shell(title, descr, body, cta_h2, cta_note, extra_js="", root="",
               extra_head="", product="", promo=True):
    """Каркас страницы. root = префикс относительных ссылок ('' или '../')."""
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
  <link rel="stylesheet" href="{root}styles.css?v=34">{extra_head}
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

  <!-- Помощь с выбором; id=lead — сюда скроллит кнопка калькулятора -->
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


def tile_card(p, root=""):
    """Карточка товара в сетке — вся карточка это ссылка на страницу товара."""
    alt = f"Тротуарная плитка «{p['name']}» — {SHAPES[p['shape']]['name']}"
    if p["_thumb"]:
        img = (f'<img class="p-img" src="{root}{p["_gallery"][0]}?v=4" alt="{esc(alt)}" '
               f'width="640" height="480" loading="lazy">')
    else:
        img = ('<div class="p-img p-none" role="img" aria-label="Фото готовим">'
               '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
               'stroke-width="1.5" stroke-linecap="round" aria-hidden="true">'
               '<rect x="3" y="8" width="18" height="9"/>'
               '<path d="M7 11h.01M12 11h.01M17 11h.01"/></svg>'
               '<span>Фото пришлём по запросу</span></div>')
    kind = "mono" if p["mono"] else "mix"
    kind_ru = "однотонная" if p["mono"] else "колормикс"
    price = (f'<p class="p-price">{rub(p["price"])} ₽/м²</p>' if p["price"]
             else '<span class="p-ask">Узнать цену</span>')
    return (f'<a class="p-card" data-kind="{kind}" href="{root}{p["_url"]}">'
            f'{img}<h3 class="p-name">{esc(p["name"])}</h3>'
            f'<p class="p-meta">{kind_ru}</p>{price}</a>')


CALC_JS = """
  <script>
    (function () {
      var container = document.getElementById('calcContainer');
      var area = document.getElementById('cArea');
      var shape = document.getElementById('cShape');
      var qty = document.getElementById('calcQty');
      var pallets = document.getElementById('calcPallets');
      var price = document.getElementById('calcPrice');
      var priceBlock = document.getElementById('calcPriceBlock');
      var priceDivider = document.getElementById('calcPriceDivider');
      
      if (!area) return;
      
      var basePrice = container ? parseInt(container.dataset.price, 10) : 0;
      var palletSize = 15;
      
      function recalc() {
        var a = parseFloat(area.value);
        if (!a || a <= 0) {
          qty.textContent = '—';
          pallets.textContent = '—';
          if (price) price.textContent = '—';
          return;
        }
        var activePrice = basePrice || (shape ? parseInt(shape.value, 10) : 0);
        var need = a * 1.05;
        var m2 = Math.ceil(need);
        var pCount = Math.ceil(need / palletSize);
        
        qty.textContent = m2 + '\u00A0м²';
        
        var palletsText = pCount + ' ' +
          (pCount % 10 === 1 && pCount % 100 !== 11 ? 'поддон' :
           (pCount % 10 >= 2 && pCount % 10 <= 4 && (pCount % 100 < 12 || pCount % 100 > 14) ? 'поддона' : 'поддонов'));
        pallets.textContent = palletsText;
        
        if (activePrice) {
          if (priceBlock) priceBlock.style.display = '';
          if (priceDivider) priceDivider.style.display = '';
          if (price) price.textContent = 'от\u00A0' + (m2 * activePrice).toLocaleString('ru-RU') + '\u00A0₽';
        } else {
          if (priceBlock) priceBlock.style.display = 'none';
          if (priceDivider) priceDivider.style.display = 'none';
        }
      }
      area.addEventListener('input', recalc);
      if (shape) shape.addEventListener('change', recalc);
      recalc();
    })();
  </script>"""

GALLERY_JS = """
  <script>
    (function () {
      var main = document.getElementById('pdMain');
      var mainWrap = document.getElementById('pdMainWrap');
      var thumbs = Array.prototype.slice.call(document.querySelectorAll('.pd-thumb'));
      
      if (!main) return;
      
      // Смена изображений с плавным затуханием (fade)
      function switchMain(src, activeThumb) {
        if (main.src === new URL(src, location.href).href) return;
        main.classList.add('is-fading');
        setTimeout(function() {
          main.src = src;
          // Убираем fading после загрузки картинки
          var tempImg = new Image();
          tempImg.src = src;
          tempImg.onload = function() {
            main.classList.remove('is-fading');
          };
          // Резервный сброс, если событие onload не сработает
          setTimeout(function() {
            main.classList.remove('is-fading');
          }, 250);
        }, 150);
        
        thumbs.forEach(function (x) {
          x.classList.toggle('is-on', x === activeThumb);
          x.setAttribute('aria-pressed', x === activeThumb ? 'true' : 'false');
        });
      }
      
      thumbs.forEach(function (t) {
        t.addEventListener('click', function () {
          switchMain(t.dataset.src, t);
        });
      });
      
      // Динамическое добавление премиум-лайтбокса
      var lightbox = document.createElement('div');
      lightbox.className = 'pd-lightbox';
      lightbox.innerHTML = '<button class="pd-lightbox-close" aria-label="Закрыть"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg></button>' +
        '<button class="pd-lightbox-nav pd-lightbox-prev" aria-label="Предыдущее фото"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg></button>' +
        '<button class="pd-lightbox-nav pd-lightbox-next" aria-label="Следующее фото"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg></button>' +
        '<div class="pd-lightbox-content"><img class="pd-lightbox-img" src="" alt="Увеличенное фото"></div>';
      document.body.appendChild(lightbox);
      
      var lbImg = lightbox.querySelector('.pd-lightbox-img');
      var lbClose = lightbox.querySelector('.pd-lightbox-close');
      var lbPrev = lightbox.querySelector('.pd-lightbox-prev');
      var lbNext = lightbox.querySelector('.pd-lightbox-next');
      
      var currentIdx = 0;
      var galleryUrls = thumbs.map(function(t) { return t.dataset.src; });
      if (galleryUrls.length === 0) {
        galleryUrls = [main.src];
      }
      
      // Защита от пикселизации мелких картинок в лайтбоксе
      lbImg.addEventListener('load', function() {
        var naturalW = lbImg.naturalWidth;
        if (naturalW && naturalW < 800) {
          lbImg.style.maxWidth = naturalW + 'px';
        } else {
          lbImg.style.maxWidth = '90vw';
        }
      });
      
      function openLightbox(idx) {
        currentIdx = idx;
        lbImg.src = galleryUrls[currentIdx];
        lightbox.classList.add('is-open');
        document.body.style.overflow = 'hidden';
        updateNav();
      }
      
      function closeLightbox() {
        lightbox.classList.remove('is-open');
        document.body.style.overflow = '';
      }
      
      function updateNav() {
        if (galleryUrls.length <= 1) {
          lbPrev.style.display = 'none';
          lbNext.style.display = 'none';
        } else {
          lbPrev.style.display = '';
          lbNext.style.display = '';
        }
      }
      
      function showPrev() {
        currentIdx = (currentIdx - 1 + galleryUrls.length) % galleryUrls.length;
        lbImg.src = galleryUrls[currentIdx];
      }
      
      function showNext() {
        currentIdx = (currentIdx + 1) % galleryUrls.length;
        lbImg.src = galleryUrls[currentIdx];
      }
      
      // Открытие лайтбокса при клике на основную картинку
      if (mainWrap) {
        mainWrap.addEventListener('click', function(e) {
          if (e.target.closest('.pd-zoom-trigger')) return;
          var activeThumb = document.querySelector('.pd-thumb.is-on');
          var idx = activeThumb ? thumbs.indexOf(activeThumb) : 0;
          openLightbox(idx >= 0 ? idx : 0);
        });
      }
      
      var zoomTrigger = document.getElementById('pdZoomTrigger');
      if (zoomTrigger) {
        zoomTrigger.addEventListener('click', function(e) {
          e.stopPropagation();
          var activeThumb = document.querySelector('.pd-thumb.is-on');
          var idx = activeThumb ? thumbs.indexOf(activeThumb) : 0;
          openLightbox(idx >= 0 ? idx : 0);
        });
      }
      
      lbClose.addEventListener('click', closeLightbox);
      lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox || e.target.classList.contains('pd-lightbox-content')) {
          closeLightbox();
        }
      });
      
      lbPrev.addEventListener('click', function(e) { e.stopPropagation(); showPrev(); });
      lbNext.addEventListener('click', function(e) { e.stopPropagation(); showNext(); });
      
      document.addEventListener('keydown', function(e) {
        if (!lightbox.classList.contains('is-open')) return;
        if (e.key === 'Escape') closeLightbox();
        if (e.key === 'ArrowLeft') showPrev();
        if (e.key === 'ArrowRight') showNext();
      });
    })();
  </script>"""


def calc_block(shape_select=None, root="",
               note="Точный расчёт с раскладкой и доставкой сделает менеджер.",
               price=0):
    """Калькулятор площади. shape_select: HTML select или None (тогда цена фиксированная в data-price)."""
    fields = f"""
        <label class="line-calc-group" for="cArea">
          <span class="line-calc-label">Площадь <br>под плитку</span>
          <span class="line-calc-input-wrap">
            <input class="line-calc-input" id="cArea" type="number" inputmode="decimal" min="1" max="10000" placeholder="0" value="78">
            <span class="line-calc-unit">м²</span>
          </span>
        </label>"""
    if shape_select:
        fields += f"""
        <div class="line-calc-group">
          <span class="line-calc-label">Форма <br>плитки</span>
          {shape_select}
        </div>"""

    return f"""
    <div class="line-calc" id="calcContainer" data-price="{price}">
      <div class="line-calc-wrap">
        {fields}
        <div class="line-calc-outputs">
          <div class="line-calc-block">
            <span class="line-calc-sub">С запасом 5%</span>
            <strong class="line-calc-val" id="calcQty">—</strong>
          </div>
          <div class="line-calc-block">
            <span class="line-calc-sub">Отгрузка</span>
            <strong class="line-calc-val" id="calcPallets">—</strong>
          </div>
          <div class="line-calc-block" id="calcPriceBlock">
            <span class="line-calc-sub">Стоимость</span>
            <strong class="line-calc-val val-accent" id="calcPrice">—</strong>
          </div>
        </div>
        <a class="btn line-calc-btn" href="#lead">
          Получить расчёт
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" width="16" height="16" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
        </a>
      </div>
      <p class="caption line-calc-note">{note}</p>
    </div>"""


# ── Категория: trotuarnaya-plitka.html ───────────────────────────────────────

def build_category():
    total = len(PRODUCTS)
    all_min = min(p["price"] for p in PRODUCTS if p["price"])

    shape_cards = []
    for slug in SHAPE_ORDER:
        m = SHAPES[slug]
        colors = plural(m["count"], "цвет", "цвета", "цветов")
        shape_cards.append(f"""
        <a class="cat" href="plitka-{slug}.html">
          <img class="cat-img" src="img/plitka/shape-{slug}.jpg" alt="Тротуарная плитка «{esc(m['name'])}» — фактура" width="600" height="600" loading="lazy">
          <div class="cat-row"><h3>{esc(m['name'])}</h3>
            <svg class="arr" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
          </div>
          <p class="caption">{m['count']} {colors} · {esc(SHAPE_NOTE[slug])}</p>
          <p class="cat-price">от {rub(m['min_price'])} ₽/м²</p>
        </a>""")

    # восьмая плитка сетки — бордюры (иначе в сетке 4×2 пустой слот)
    b_min = min(b["price"] for b in BORDERS)
    shape_cards.append(f"""
        <a class="cat" href="#borders">
          <img class="cat-img cat-img-fit" src="img/plitka/shape-bordur.jpg" alt="Бордюры к тротуарной плитке" width="600" height="600" loading="lazy">
          <div class="cat-row"><h3>Бордюры</h3>
            <svg class="arr" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14M6 13l6 6 6-6"/></svg>
          </div>
          <p class="caption">Дорожный и садовый — держат край полотна</p>
          <p class="cat-price">от {rub(b_min)} ₽/шт</p>
        </a>""")

    border_cards = []
    for b in BORDERS:
        note = ("К дорожкам и парковкам — держит край полотна" if "дорожн" in b["name"].lower()
                else "К садовым дорожкам и клумбам")
        border_cards.append(f"""
        <a class="p-card" href="tovar/{b['id']}.html">
          <img class="p-img p-img-line" src="img/catalog/{b['id']}.jpg" alt="{esc(b['name'])}" width="640" height="480" loading="lazy">
          <h3 class="p-name">{esc(b['name'])}</h3>
          <p class="p-meta">{note}</p>
          <p class="p-price">{rub(b['price'])} ₽/шт</p>
        </a>""")

    works = "\n".join(
        f'<img src="img/plitka/work-{i:02d}.jpg" alt="Уложенная тротуарная плитка — наш объект, фото {i}" '
        f'width="800" height="600" loading="lazy">'
        for i in range(1, 11))

    shape_options = "\n".join(
        f'            <option value="{SHAPES[s]["min_price"]}">{esc(SHAPES[s]["name"])} — от {rub(SHAPES[s]["min_price"])} ₽/м²</option>'
        for s in SHAPE_ORDER)
    shape_select = f"""
          <div class="field">
            <label for="cShape">Форма плитки</label>
            <select id="cShape">
{shape_options}
            </select>
          </div>"""

    hero = banner(
        "Тротуарная плитка",
        f"<b>{total} {plural(total, 'вариант', 'варианта', 'вариантов')}</b> · 7 форм · от {rub(all_min)} ₽/м²",
        [SLIDE_SALE_TILE,
         {"eyebrow": "Расчёт",
          "title": "Посчитаем плитку по плану двора <b>за 10 минут</b>",
          "sub": "Пришлите размеры — посчитаем метры, поддоны и доставку.",
          "cta": "Получить расчёт", "href": "#calc",
          "img": "img/plitka/work-03.jpg"},
         SLIDE_NEW_BRICK,
         dict(SLIDE_DELIVERY, img="img/plitka/work-07.jpg")])

    body = f"""
{hero}

  <!-- Формы -->
  <section class="section" id="shapes" aria-label="Формы плитки">
    <div class="wrap">
      <div class="section-head">
        <h2>Выберите форму</h2>
        <p class="caption">Купить тротуарную плитку в Краснодаре: {total} {plural(total, "вариант", "варианта", "вариантов")} в 7 формах с завода-производителя. Цвет подберёте внутри формы.</p>
        <ul class="page-facts">
          <li><b>40 мм</b> <span>толщина</span></li>
          <li><b>F200</b> <span>200 зим</span></li>
          <li><b>B30</b> <span>держит машину</span></li>
          <li><b>~24</b> <span>цвета в форме</span></li>
        </ul>
      </div>
      <div class="cats cats-tiles">
{"".join(shape_cards)}
      </div>
      <p class="caption cats-note">Цены — заводские «от», зависят от расцветки.
        Однотонные дешевле, колормиксы — дороже.</p>
    </div>
  </section>

  <!-- Бордюры -->
  <section class="section" id="borders" aria-label="Бордюры">
    <div class="wrap">
      <div class="section-head">
        <h2>Бордюры — сразу к плитке</h2>
        <p class="caption">Продукция сертифицирована. Посчитаем метраж по вашему плану — просто пришлите размеры.</p>
      </div>
      <div class="p-grid{grid_cls(len(border_cards))}">
{"".join(border_cards)}
      </div>
    </div>
  </section>
  <section class="section" id="calc" aria-label="Калькулятор плитки">
    <div class="wrap">
      {calc_block(shape_select)}
    </div>
  </section>
  <!-- Наши работы -->
  <section class="section" id="works" aria-label="Наши работы">
    <div class="wrap">
      <div class="section-head">
        <h2>Наши работы</h2>
        <p class="caption">Реальные объекты: дворы, дорожки, парковки — плитка из этого каталога.</p>
      </div>
      <div class="works-grid">
{works}
      </div>
      <div class="works-video">
        <video controls preload="none" poster="img/plitka/works-video-poster.jpg" width="360">
          <source src="img/plitka/works-video.mp4" type="video/mp4">
        </video>
        <div class="works-video-txt">
          <h3>Плитку прессуем на собственной линии</h3>
          <p class="caption">30 секунд с производства — почему у нас заводская цена
            и ровная геометрия.</p>
          <ul class="wv-facts">
            <li><strong>Вибропресс</strong> — плитка плотнее литой, не боится мороза</li>
            <li><strong>Полусухая смесь</strong> — точные размеры, ровные швы при укладке</li>
            <li><strong>Камера выдержки</strong> — прочность набрана ещё до отгрузки</li>
          </ul>
        </div>
      </div>
    </div>
  </section>"""

    out = page_shell(
        "Тротуарная плитка от производителя — от 650 ₽/м² | Строй-Сейл Краснодар",
        f"Тротуарная плитка в Краснодаре: {total} {plural(total, 'вариант', 'варианта', 'вариантов')}, "
        "7 форм, 40 мм, F200. Заводские цены, доставка на объект, оплата при получении.",
        body + VIDEO_BUBBLE,
        "Не знаете, какую форму выбрать?",
        "Позвоните — подберём форму и цвет под дом, посчитаем площадь по плану участка и скажем точную цену с доставкой.",
        CALC_JS + VIDEO_BUBBLE_JS + BANNER_JS, promo=False)
    (BASE / "trotuarnaya-plitka.html").write_text(typo(out))
    print(f"trotuarnaya-plitka.html: {total} товаров, 7 форм, от {all_min} ₽/м²")


# ── Страницы форм: plitka-<slug>.html ────────────────────────────────────────

def build_shape(slug):
    m = SHAPES[slug]
    items = sorted([p for p in PRODUCTS if p["shape"] == slug],
                   key=lambda p: (not p["_thumb"] and not p["price"],
                                  p["mono"], p["price"] or 0, p["name"]))
    n = len(items)
    n_mono = sum(1 for p in items if p["mono"])
    n_mix = n - n_mono
    cards = "\n".join(tile_card(p) for p in items)

    others = " ".join(
        f'<a href="plitka-{s}.html">{esc(SHAPES[s]["name"])}</a>'
        for s in SHAPE_ORDER if s != slug)

    # факты о плитке: цифра выделена, пояснение простыми словами рядом.
    # Раньше это была одна серая строка через «·» — её не читали.
    spec_bits = [("40 мм", "толщина"), ("F200", "200 зим"),
                 ("B30", "держит машину"), (f"{PALLET_M2} м²", "в поддоне")]
    facts_html = "\n".join(
        f"        <li><b>{esc(a)}</b> <span>{esc(b)}</span></li>"
        for a, b in spec_bits)

    filter_html = ""
    filter_js = ""
    if n_mono and n_mix:
        filter_html = f"""
      <div class="filters" aria-label="Фильтр по типу окраски">
        <div class="pick-row">
          <div class="pick-scroll pick-scroll--slide" id="kindChips" role="group" aria-label="Тип окраски">
            <button class="chip is-on" data-kind="" aria-pressed="true">Все · {n}</button>
            <button class="chip" data-kind="mix" aria-pressed="false">Колормиксы · {n_mix}</button>
            <button class="chip" data-kind="mono" aria-pressed="false">Однотонные · {n_mono} — от {rub(m['min_price'])} ₽</button>
          </div>
        </div>
        <p class="pick-count" id="shownNote">Показано {n} из {n}</p>
      </div>"""
        filter_js = """
  <script>
    (function () {
      var chips = Array.prototype.slice.call(document.querySelectorAll('#kindChips .chip'));
      var cards = Array.prototype.slice.call(document.querySelectorAll('.p-card'));
      var note = document.getElementById('shownNote');
      chips.forEach(function (c) {
        c.addEventListener('click', function () {
          chips.forEach(function (x) {
            x.classList.toggle('is-on', x === c);
            x.setAttribute('aria-pressed', x === c ? 'true' : 'false');
          });
          var kind = c.dataset.kind;
          var shown = 0;
          cards.forEach(function (card) {
            var ok = !kind || card.dataset.kind === kind;
            card.hidden = !ok;
            if (ok) shown++;
          });
          note.textContent = 'Показано\u00A0' + shown + ' из\u00A0' + cards.length;
        });
      });
    })();
  </script>"""

    body = f"""
  <section class="page-head">
    <div class="wrap">
      <nav class="crumbs" aria-label="Хлебные крошки">
        <a href="index.html">Главная</a> <span aria-hidden="true">/</span>
        <a href="trotuarnaya-plitka.html">Тротуарная плитка</a> <span aria-hidden="true">/</span>
        <span>{esc(m['name'])}</span>
      </nav>
      <h1>Плитка «{esc(m['name'])}»</h1>
      <p class="page-sub">{esc(SHAPE_NOTE[slug])}. {n} {plural(n, 'расцветка', 'расцветки', 'расцветок')},
        от {rub(m['min_price'])} ₽/м² с завода.</p>
      <ul class="page-facts">
{facts_html}
      </ul>
    </div>
  </section>

  <section class="section" aria-label="Расцветки">
    <div class="wrap">
{filter_html}
      <div class="p-grid">
{cards}
      </div>
      <p class="caption cats-note">Фото передают рисунок, оттенок на живой плитке
        может отличаться — пришлём фото готовых партий в мессенджер.</p>
      <div class="more">
        <span class="more-label">Другие формы</span>
        <div class="more-list">{others}</div>
      </div>
    </div>
  </section>
  <section class="section" id="calc" aria-label="Калькулятор плитки">
    <div class="wrap">
      {calc_block(note=f"Стоимость — от {rub(m['min_price'])} ₽/м² по этой форме. Точный расчёт сделает менеджер.", price=m['min_price'])}
    </div>
  </section>"""

    # калькулятор формы: цена подставляется скрытым полем
    body = body.replace('<div class="calc-fields">', f"""<div class="calc-fields">
          <input type="hidden" id="cShape" value="{m['min_price']}">""")

    out = page_shell(
        f"Плитка «{m['name']}» — {n} {plural(n, 'расцветка', 'расцветки', 'расцветок')} от {rub(m['min_price'])} ₽/м² | Строй-Сейл",
        f"Тротуарная плитка «{m['name']}» в Краснодаре: {n} {plural(n, 'расцветка', 'расцветки', 'расцветок')}, 40 мм, F200, "
        f"от {rub(m['min_price'])} ₽/м². Доставка, оплата при получении.",
        body,
        "Поможем выбрать расцветку",
        "Пришлём живые фото плитки в мессенджер, посчитаем количество и скажем цену с доставкой до вашего участка.",
        CALC_JS + filter_js)
    (BASE / f"plitka-{slug}.html").write_text(typo(out))
    print(f"plitka-{slug}.html: {n} расцветок (моно {n_mono} / микс {n_mix})")


# ── Карточка товара: tovar/<форма>-<цвет>.html ───────────────────────────────

def related_products(p, k=4):
    """Соседние расцветки той же формы: похожая цена, разнообразие вида."""
    pool = [q for q in PRODUCTS if q["shape"] == p["shape"] and q["id"] != p["id"]]
    pool.sort(key=lambda q: (q["mono"] != p["mono"],
                             abs((q["price"] or 0) - (p["price"] or 0)),
                             q["name"]))
    return pool[:k]


def build_product(p):
    root = "../"
    m = SHAPES[p["shape"]]
    kind_ru = "однотонная окраска" if p["mono"] else "колормикс — несколько оттенков в замесе"
    name = esc(p["name"])
    shape_name = esc(m["name"])

    # та же расцветка в других формах — быстрый переход
    cross = [q for q in PRODUCTS if q["name"] == p["name"] and q["shape"] != p["shape"]]
    cross.sort(key=lambda q: SHAPE_ORDER.index(q["shape"]))
    cross_form_html = ""
    if cross:
        chips = "".join(
            f'<a href="{root}tovar/{q["slug"]}.html"><span>{esc(SHAPES[q["shape"]]["name"])}</span>'
            f'<small>{rub(q["price"]) + " ₽/м²" if q["price"] else "цена по запросу"}</small></a>'
            for q in cross)
        cross_form_html = f"""
  <section class="section" aria-label="Эта расцветка в других формах">
    <div class="wrap">
      <div class="section-head">
        <h2>«{name}» в других формах</h2>
        <p class="caption">Тот же цвет — другой рисунок мощения.</p>
      </div>
      <nav class="chip-links">{chips}</nav>
    </div>
  </section>"""

    # галерея
    thumbs = ""
    if len(p["_gallery"]) > 1:
        btns = []
        for i, src in enumerate(p["_gallery"]):
            on = " is-on" if i == 0 else ""
            pressed = "true" if i == 0 else "false"
            btns.append(
                f'<button class="pd-thumb{on}" type="button" data-src="{root}{src}?v=4" '
                f'aria-pressed="{pressed}" aria-label="Фото {i + 1}">'
                f'<img src="{root}{src}?v=4" alt="" width="640" height="480" loading="lazy"></button>')
        thumbs = f'\n      <div class="pd-thumbs">{"".join(btns)}</div>'

    # поддон 15 м² — вторая цена (паттерн Bradstone: юнит-экономика без калькулятора)
    pallet_line = ""
    if p["price"]:
        sp = p.get("specs") or {}
        pm = re.search(r"([\d,.]+)", str(sp.get("pallet_m2", "")))
        if pm:
            try:
                pallet_m2 = float(pm.group(1).replace(",", "."))
                pallet_rub = round(p["price"] * pallet_m2 / 100) * 100
                pallet_line = (f'<p class="caption pd-m2">поддон {pm.group(1)} м² '
                               f'≈ {rub(pallet_rub)} ₽</p>')
            except ValueError:
                pass
    price_html = (f'<p class="pd-price">{rub(p["price"])} ₽<span class="pd-price-unit">/м²</span></p>{pallet_line}'
                  if p["price"] else
                  f'<p class="pd-price pd-price-ask">Цена по запросу</p>')

    body = f"""
  <section class="page-head">
    <div class="wrap">
      <nav class="crumbs" aria-label="Хлебные крошки">
        <a href="{root}index.html">Главная</a> <span aria-hidden="true">/</span>
        <a href="{root}trotuarnaya-plitka.html">Тротуарная плитка</a> <span aria-hidden="true">/</span>
        <a href="{root}plitka-{p['shape']}.html">{shape_name}</a> <span aria-hidden="true">/</span>
        <span>{name}</span>
      </nav>
    </div>
  </section>

  <section class="section pd" aria-label="Карточка товара">
    <div class="wrap pd-grid">
      <div class="pd-gallery">
        <div class="pd-main-wrap" id="pdMainWrap">
          <img class="pd-main" id="pdMain" src="{root}{p['_gallery'][0]}?v=4"
            alt="Тротуарная плитка «{name}», форма «{shape_name}» — фактура укладки"
            width="640" height="480">
          <button class="pd-zoom-trigger" id="pdZoomTrigger" type="button" aria-label="Открыть во весь экран">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>
          </button>
        </div>{thumbs}
      </div>
      <div class="pd-info">
        <p class="tag">Тротуарная плитка · {shape_name}</p>
        <h1 class="pd-name">{name}</h1>
        <p class="p-meta">{kind_ru} · толщина 40 мм</p>
        {price_html}
        <p class="caption pd-price-note">Заводская цена. Отгрузка поддонами
          по {PALLET_M2} м², обычно за 3–5 дней.</p>
        <div class="pd-cta">
          {order_btns(root, f"плитка «{p['name']}» ({m['name']})")}
        </div>
        <dl class="pd-specs">
          <div><dt>Толщина</dt><dd>40 мм — дорожки, двор, легковая машина</dd></div>
          <div><dt>Морозостойкость</dt><dd>F200 — двести циклов заморозки</dd></div>
          <div><dt>Прочность</dt><dd>B30 — бетон дорожного класса</dd></div>
          <div><dt>Поддон</dt><dd>{PALLET_M2} м² · около 1,4 тонны</dd></div>
          <div><dt>Фура</dt><dd>225 м² за один рейс</dd></div>
        </dl>
        <p class="caption pd-usage"><strong>Куда берут:</strong> {SHAPE_USE[p['shape']]}.</p>
      </div>
      <div class="pd-calc-row">
        {calc_block(root=root, note=f"Стоимость по цене этой расцветки. Точный расчёт с раскладкой и доставкой сделает менеджер.", price=p['price'])}
      </div>
    </div>
  </section>
  <section class="section" aria-label="Другие расцветки">
    <div class="wrap">
      <div class="section-head">
        <h2>Другие расцветки «{shape_name}»</h2>
        <p class="caption">Та же форма и характеристики — другой рисунок.</p>
      </div>
      <div class="p-grid{grid_cls(len(related_products(p)))}">
{"".join(tile_card(q, root) for q in related_products(p))}
      </div>
      <div class="more">
        <span class="more-label">Вся форма</span>
        <div class="more-list"><a href="{root}plitka-{p['shape']}.html">{shape_name} — все {m['count']} {plural(m['count'], 'расцветка', 'расцветки', 'расцветок')}</a></div>
      </div>
    </div>
  </section>{cross_form_html}"""

    body = body.replace('<div class="calc-fields">', f"""<div class="calc-fields">
          <input type="hidden" id="cShape" value="{p['price'] or 0}">""")

    ld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": f"Тротуарная плитка «{p['name']}» ({m['name']})",
        "image": SITE_URL + p["_gallery"][0],
        "description": f"Тротуарная плитка «{p['name']}», форма «{m['name']}». "
                       "Толщина 40 мм, морозостойкость F200, прочность B30.",
        "offers": {
            "@type": "Offer",
            "priceCurrency": "RUB",
            "price": p["price"],
            "availability": "https://schema.org/InStock",
        },
    }
    extra_head = ('\n  <script type="application/ld+json">'
                  + json.dumps(ld, ensure_ascii=False) + "</script>")

    out = page_shell(
        f"Плитка «{p['name']}» ({m['name']}) — {rub(p['price'])} ₽/м² | Строй-Сейл",
        f"Тротуарная плитка «{p['name']}», форма «{m['name']}»: {rub(p['price'])} ₽/м², "
        "40 мм, F200, B30. Поддон 15 м². Доставка по Краснодару и краю, оплата при получении.",
        body,
        "Возьмём подбор на себя",
        "Пришлём живые фото этой расцветки, посчитаем количество по вашему плану и скажем цену с доставкой.",
        CALC_JS + GALLERY_JS, root=root, extra_head=extra_head,
        product=f"плитка «{p['name']}» ({m['name']})")
    (TOVAR / f"{p['slug']}.html").write_text(typo(out))


def build_border(b):
    """Страница бордюра: фото, цена, зачем нужен, заказ."""
    root = "../"
    is_road = "дорожн" in b["name"].lower()
    use = ("Держит край дорожки и парковки: полотно не расползается, край не крошится."
           if is_road else
           "Аккуратный край садовых дорожек и клумб — ниже и легче дорожного.")
    name = esc(b["name"])
    body = f"""
  <section class="page-head">
    <div class="wrap">
      <nav class="crumbs" aria-label="Хлебные крошки">
        <a href="{root}index.html">Главная</a> <span aria-hidden="true">/</span>
        <a href="{root}trotuarnaya-plitka.html">Тротуарная плитка</a> <span aria-hidden="true">/</span>
        <span>{name}</span>
      </nav>
    </div>
  </section>

  <section class="section pd" aria-label="Карточка товара">
    <div class="wrap pd-grid">
      <div class="pd-gallery">
        <div class="pd-main-wrap">
          <img class="pd-main" src="{root}img/catalog/{b['id']}.jpg?v=4"
            alt="{name} к тротуарной плитке" width="640" height="480">
        </div>
      </div>
      <div class="pd-info">
        <p class="tag">Бордюры</p>
        <h1 class="pd-name">{name}</h1>
        <p class="pd-price">{rub(b['price'])} ₽<span class="pd-price-unit">/шт</span></p>
        <p class="caption pd-price-note">Заводская цена. Обычно берут вместе с плиткой —
          посчитаем метраж по плану участка.</p>
        <div class="pd-cta">
          {order_btns(root, b["name"].lower())}
        </div>
        <p class="caption pd-usage"><strong>Зачем нужен:</strong> {use}</p>
      </div>
    </div>
  </section>"""

    out = page_shell(
        f"{b['name']} — {rub(b['price'])} ₽/шт | Строй-Сейл Краснодар",
        f"{b['name']}: {rub(b['price'])} ₽/шт, к тротуарной плитке. "
        "Посчитаем метраж, привезём вместе с плиткой. Оплата при получении.",
        body,
        "Посчитаем бордюр вместе с плиткой",
        "Пришлите план или размеры участка — скажем, сколько нужно бордюра и плитки, и назовём цену с доставкой.",
        root=root, product=b["name"].lower())
    (TOVAR / f"{b['id']}.html").write_text(typo(out))


if __name__ == "__main__":
    build_category()
    for slug in SHAPE_ORDER:
        build_shape(slug)
    for p in PRODUCTS:
        build_product(p)
    for b in BORDERS:
        build_border(b)
    print(f"tovar/: {len(PRODUCTS) + len(BORDERS)} страниц товара")
