#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""catalog.json → страницы каталога облицовочного кирпича.

Генерирует:
- kirpich-oblitsovochnyy.html — категория: подбор по цвету + плитки-мозаики
  коллекций (3 фото + «+N», кружки цветов, цена) — макет утверждён 17.07;
- kirpich-ves.html — весь кирпич одной сеткой (фильтры цвет/бюджет/фактура);
- collection-<slug>.html × 5 — полная сетка коллекции с фильтрами и сортировкой.

Принцип «коллекций»: фото разных поставщиков никогда не смешиваются в одной
сетке — по умолчанию результаты идут группами по коллекциям (сортировка по
цене смешивает группы, но это осознанный выбор пользователя).
"""

import html
import json
import re
from pathlib import Path
from urllib.parse import quote

import sys
sys.path.insert(0, str(Path(__file__).parent))
from banner_common import banner, BANNER_JS, SLIDE_SALE_TILE, SLIDE_NEW_BRICK, SLIDE_DELIVERY

BASE = Path("/Users/dm/Desktop/сайт")
DATA = json.loads((BASE / "data" / "catalog.json").read_text())

# Абсолютный адрес сайта — для JSON-LD (относительные пути из /tovar/ бьются)
SITE_URL = "https://martinoneisha299-lang.github.io/stroy-sale/"

COLOR_ORDER = ["красный", "коричневый", "персиковый", "бежевый", "серый",
               "графит", "микс (бавария)", "зелёный", "разное"]
SWATCH_CLASS = {
    "красный": "sw-krasny", "коричневый": "sw-korichnevy",
    "персиковый": "sw-persik", "бежевый": "sw-bezh", "серый": "sw-sery",
    "графит": "sw-grafit", "микс (бавария)": "sw-miks", "зелёный": "sw-zeleny",
}
# короткая подпись под кружком-образцом (полное имя — в aria-label и статусе)
SW_LABEL = {"микс (бавария)": "бавария"}


def swatch_btn(label, dot_class, attrs, is_on=False, aria=""):
    """Кнопка-образец цвета: круг-образец + подпись.
    dot_class=None — «Все»: круг-образец с текстом внутри, без подписи снизу."""
    on = ' is-on' if is_on else ''
    pressed = 'true' if is_on else 'false'
    aria_attr = f' aria-label="{aria}"' if aria else ''
    if dot_class is None:
        return (f'<button class="swatch sw-all-btn{on}" {attrs} '
                f'aria-pressed="{pressed}"{aria_attr}>'
                f'<span class="swatch-dot sw-all">{label}</span></button>')
    return (f'<button class="swatch{on}" {attrs} aria-pressed="{pressed}"{aria_attr}>'
            f'<span class="swatch-dot {dot_class}" aria-hidden="true"></span>'
            f'<span class="sw-name">{label}</span></button>')


# стрелка-чеврон для карусели образцов
CHEVRON = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" '
           'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
           'stroke-linejoin="round" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>')


def color_track(swatches_html, aria="Цвет кирпича"):
    """Ряд образцов цвета: одна прокручиваемая строка + стрелка «ещё» справа."""
    return (
        '<div class="pick-track">\n'
        f'          <div class="pick-scroll pick-scroll--swatch" data-carousel role="group" aria-label="{aria}">\n'
        f'{swatches_html}\n'
        '          </div>\n'
        '          <button class="pick-next" type="button" aria-label="Показать ещё цвета" hidden>'
        f'{CHEVRON}</button>\n'
        '        </div>')


# инициализация каруселей образцов (стрелка листает, прячется в конце ряда)
CAROUSEL_JS = """
    // Круги-цвета: одна прокручиваемая строка; стрелка листает и прячется в конце
    Array.prototype.forEach.call(document.querySelectorAll('.pick-track'), function (track) {
      var scroll = track.querySelector('[data-carousel]');
      var next = track.querySelector('.pick-next');
      if (!scroll || !next) return;
      function sync() {
        next.hidden = (scroll.scrollWidth - scroll.clientWidth - scroll.scrollLeft) < 8;
      }
      next.addEventListener('click', function () {
        scroll.scrollBy({ left: scroll.clientWidth * 0.8, behavior: 'smooth' });
      });
      scroll.addEventListener('scroll', sync);
      window.addEventListener('resize', sync);
      sync();
    });
"""

COLLECTIONS = {
    "ekonom": {
        "name": "Эконом",
        "tagline": "Когда важна цена: заборы, хозпостройки и большие объёмы — без потери вида.",
    },
    "palitra": {
        "name": "Палитра",
        "tagline": "Самая широкая палитра оттенков — от абрикоса до тёмного шоколада. Если ищете «тот самый», он здесь.",
    },
    "klassika": {
        "name": "Классика",
        "tagline": "Золотая середина по цене: дом, забор и цоколь из одной коллекции.",
    },
    "evropa": {
        "name": "Европа",
        "tagline": "Кирпич «под старину» с рельефной поверхностью — для фасадов с характером.",
    },
    "formovka": {
        "name": "Ручная формовка",
        "tagline": "Премиум-кирпич: у каждого свой рисунок, как у кирпича столетней кладки.",
    },
}
COLL_ORDER = ["ekonom", "palitra", "klassika", "evropa", "formovka"]

# ── Плитки-мозаики на странице категории (макет утверждён 17.07) ────────────
# Описание в подписи плитки — продающее, простым языком (таглайны коллекций
# остались на страницах коллекций).
TILE_DESC = {
    "ekonom": "Гладкий керамический без переплаты за фактуру — дом, забор, хозпостройки.",
    "klassika": "Фактуры под старину — береста, сахара, скала антик. Самая большая линейка фактур.",
    "palitra": "Самая широкая гамма: 7 цветов от абрикоса до графита, баварская кладка.",
    "evropa": "Узкий длинный кирпич европейских форматов — фасад как в Амстердаме.",
    "formovka": "Премиум: каждый кирпич со своим лицом, кладка выглядит столетней.",
}
# Тройка фото мозаики — подобраны глазами, чтобы не сливались по цвету.
# КЛЮЧИ — name (не id: id сдвигаются при добавлении товаров).
TILE_PICKS = {
    "ekonom": ["Корица", "Золотистый", "Персик"],
    "klassika": ["Вишня", "Баварский Классик береста", "Светлосерый"],
    "palitra": ["Абрикос", "Грей", "Бежевая Кора"],
    "evropa": ["Бостон", "Готик Руст", "Mokko Вт Руст"],
    "formovka": ["Астра Modf", "Петерсен Modf", "Тиволи Modf"],
}
# подпись цвета в кружке/тайтле: «микс (бавария)» человеку не говорим
DOT_LABEL = {"микс (бавария)": "Бавария (микс)"}

# Новинки заводов 17.07.2026 — метка на карточке и чип «Новинки» в сортировке.
# КЛЮЧИ — name (стабильны, как RAB_VIEW по factory_name).
NOVINKI = {
    # Донской, «Классика»
    "Баварский Классик береста", "Баварский Светлый береста", "Булат",
    "Винтаж Лайт", "Винтаж Премиум", "Коричневый Сахара",
    "Коричневый Скала Антик", "Красный Сахара", "Красный Скала Антик",
    "Светлый Береста", "Светлый Крафт", "Светлый Терра", "Солома Сахара",
    "Темно-коричневый",
    # Губский, «Палитра»
    "СС-УС-01", "СС-УС-02", "СС-УС-03.2", "СС-УС-04", "СС-УС-05", "СС-УС-06",
    "УС-01.04", "Арес", "Марс 01", "Марс 02", "Марс 03",
}

# подписи форматов простым языком: частник не обязан знать «1НФ»
FMT_SHORT = {
    "1НФ (одинарный)": "одинарный", "1,4НФ (полуторный)": "полуторный",
    "0,7НФ (евро)": "узкий (евро)", "0,9НФ": "формат 0,9НФ",
    "Ригель MF": "ригель (длинный)", "Лонг LF": "лонг (длинный)",
    "WDF": "WDF", "WMF": "WMF",
}

PRODUCTS = [p for p in DATA["products"] if p["category"] == "oblitsovochnyy"]
CAT_IMG = BASE / "img" / "catalog"
for p in PRODUCTS:
    p["_gallery"] = [f"img/catalog/{p['id']}.jpg"] + [
        f"img/catalog/{p['id']}-{i}.jpg" for i in (2, 3, 4, 5)
        if (CAT_IMG / f"{p['id']}-{i}.jpg").exists()]
    p["_thumb"] = (CAT_IMG / f"{p['id']}.jpg").exists()


def rub(v):
    s = f"{v:,.2f}".replace(",", " ").replace(".", ",")
    return s[:-3] if s.endswith(",00") else s


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


FMT_RANK = {"1НФ (одинарный)": 0, "0,7НФ (евро)": 1, "0,9НФ": 2,
            "1,4НФ (полуторный)": 3}


def sort_key(p):
    # цветовая семья → имя → гладкие первыми → формат (как на сайте завода)
    return (COLOR_ORDER.index(p["color_group"]), p["name"],
            p["texture"] != "гладкий", p["texture"],
            FMT_RANK.get(p["format"], 9))


def m2_price(p):
    """≈ цена за м² кладки: цена/шт × расход шт/м² (паттерн Славдом/Кирпич.ру —
    прораб сравнивает форматы без калькулятора). Округление до 10 ₽."""
    if not p.get("price"):
        return None
    cons = p.get("consumption_per_m2")
    if cons:
        try:
            cons = float(str(cons).replace(",", "."))
        except ValueError:
            cons = None
    if not cons:
        f = p.get("format") or ""
        if "1,4НФ" in f:
            cons = 39.2
        elif "1НФ" in f or "0,7НФ" in f:
            cons = 51.4
    if not cons:
        return None
    return round(p["price"] * cons / 10) * 10


def card(p, feat_hidden=None, root=""):
    """Карточка кирпича — вся карточка ссылка на страницу товара.
    feat_hidden: None — всегда видна (страница коллекции);
    True/False — лента категории, hidden если не featured."""
    alt = f"Кирпич «{p['name']}» — {p['color_group']}, {p['texture']}"
    if p["_thumb"]:
        img = (f'<img class="p-img" src="{root}img/catalog/{p["id"]}.jpg?v=8" alt="{esc(alt)}" '
               f'width="640" height="480" loading="lazy">')
    else:
        img = ('<div class="p-img p-none" role="img" aria-label="Фото готовим">'
               '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
               'stroke-width="1.5" stroke-linecap="round" aria-hidden="true">'
               '<rect x="3" y="8" width="18" height="9"/>'
               '<path d="M7 11h.01M12 11h.01M17 11h.01"/></svg>'
               '<span>Фото пришлём по запросу</span></div>')
    if p.get("price"):
        m2 = m2_price(p)
        m2_html = f' <span class="p-m2">≈ {rub(m2)} ₽/м²</span>' if m2 else ""
        price = f'<p class="p-price">{rub(p["price"])} ₽/шт{m2_html}</p>'
    else:
        price = '<span class="p-ask">Узнать цену</span>'
    hidden = " hidden" if feat_hidden else ""
    fmt = FMT_SHORT.get(p["format"], p["format"])
    is_new = p["name"] in NOVINKI
    new_attr = ' data-new="1"' if is_new else ""
    attrs = (f'data-color="{esc(p["color_group"])}" '
             f'data-texture="{esc(p["texture"])}" data-format="{esc(fmt)}" '
             f'data-coll="{esc(p.get("collection") or "")}" '
             f'data-price="{p["price"] if p.get("price") else ""}"'
             f'{new_attr}{hidden}')
    badge = '<span class="p-new" aria-label="Новинка завода">Новинка</span>' if is_new else ""

    meta_parts = []
    if p.get("kind"):
        meta_parts.append(p["kind"])
    meta_parts.append(p["texture"])
    meta_parts.append(fmt)
    meta_text = " · ".join(meta_parts)

    inner = (f'{badge}{img}<h3 class="p-name">{esc(p["name"])}</h3>'
             f'<p class="p-meta">{esc(meta_text)}</p>{price}')
    return f'<a class="p-card" href="{root}tovar/kirpich-{p["id"]}.html" {attrs}>{inner}</a>'



def pick_featured(items, n=4):
    """Разные цвета, с фото, с ценой (если в коллекции цены есть)."""
    priced = [p for p in items if p["_thumb"] and p.get("price")]
    pool = priced or [p for p in items if p["_thumb"]]
    out, used = [], set()
    for color in COLOR_ORDER:
        for p in pool:
            if p["color_group"] == color and color not in used:
                out.append(p)
                used.add(color)
                break
        if len(out) == n:
            return out
    for p in pool:
        if p not in out:
            out.append(p)
        if len(out) == n:
            break
    return out


# Глифы мессенджеров (simple-icons, CC0) — используются в полосе связи и кнопках заказа
WA_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z"/></svg>'
TG_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>'
PHONE_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>'

WA_LINK = ("https://wa.me/79000000000?text=" +
           quote("Здравствуйте! Пишу с сайта Строй-Сейл"))


# Липкая полоса связи (видна только на телефоне).
# TODO перед запуском: реальный номер и ссылки мессенджеров (wa.me/номер,
# t.me/имя_аккаунта, max.ru/имя_аккаунта).
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
    """Сезонное предложение: тонкая полоска над шапкой. Скрыта по умолчанию
    (hidden) — скрипт в page_shell ПОКАЗЫВАЕТ её только до даты data-until,
    так просроченная акция не мигает даже на медленной сети и не видна роботам."""
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


def page_shell(title, descr, body, extra_js="", root="",
               promo=True,
               cta_h2="Сомневаетесь, какой подойдёт?",
               cta_note="Напишите в любой мессенджер или оставьте номер — подберём кирпич под дом и бюджет, посчитаем количество.",
               product="", extra_head=""):
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
  <link rel="stylesheet" href="{root}styles.css?v=33">{extra_head}
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


def coll_stats(slug):
    items = [p for p in PRODUCTS if p["collection"] == slug]
    prices = [p["price"] for p in items if p.get("price")]
    return items, (min(prices) if prices else None)


# ── Категория: kirpich-oblitsovochnyy.html ───────────────────────────────────

ARROW = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" '
         'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
         'stroke-linejoin="round" aria-hidden="true">'
         '<path d="M5 12h14M13 6l6 6-6 6"/></svg>')


def swatch_link(label, dot_class, href, aria=""):
    """Круг-образец как ссылка (страница категории — там свотч не фильтр,
    а вход в общую сетку с пресетом цвета)."""
    aria_attr = f' aria-label="{aria}"' if aria else ''
    if dot_class is None:
        return (f'<a class="swatch sw-all-btn" href="{href}"{aria_attr}>'
                f'<span class="swatch-dot sw-all">{label}</span></a>')
    return (f'<a class="swatch" href="{href}"{aria_attr}>'
            f'<span class="swatch-dot {dot_class}" aria-hidden="true"></span>'
            f'<span class="sw-name">{label}</span></a>')


def mosaic_tile(slug, eager=False):
    """Плитка-мозаика коллекции: 3 фото + «+N», подпись, кружки цветов, цена.
    eager=True — для первой плитки страницы (LCP): без lazy, с приоритетом."""
    items, lo = coll_stats(slug)
    meta = COLLECTIONS[slug]
    items_sorted = sorted(items, key=sort_key)
    n = len(items)
    kinds = plural(n, "вид", "вида", "видов")

    # тройка фото: подобранные глазами имена, фолбэк — pick_featured
    by_name = {p["name"]: p for p in items if p["_thumb"]}
    picks = [by_name[nm] for nm in TILE_PICKS.get(slug, []) if nm in by_name]
    if len(picks) < 3:
        for p in pick_featured(items, 3):
            if p not in picks:
                picks.append(p)
            if len(picks) == 3:
                break
    load_attr = ('loading="eager" fetchpriority="high"' if eager
                 else 'loading="lazy"')
    cells = "\n".join(
        f'          <span class="cell"><img src="img/catalog/{p["id"]}.jpg?v=8" '
        f'alt="{esc(p["name"])}" width="640" height="480" {load_attr}></span>'
        for p in picks[:3])

    # кружки цветов: реальное фото первого товара цвета; тап = коллекция
    # с включённым фильтром этого цвета (?color= уже работает)
    dots = []
    colors_here = [c for c in COLOR_ORDER
                   if any(p["color_group"] == c for p in items)]
    for color in colors_here[:7]:  # максимум один ряд, редкие цвета не теряются — плитка ведёт в коллекцию целиком
        with_photo = [p for p in items_sorted
                      if p["color_group"] == color and p["_thumb"]]
        if not with_photo:
            continue
        cn = sum(1 for p in items if p["color_group"] == color)
        lbl = DOT_LABEL.get(color, color.capitalize())
        tip = f"{lbl} — {cn} {plural(cn, 'вид', 'вида', 'видов')}"
        dots.append(
            f'<a class="cdot" href="collection-{slug}.html?color={quote(color)}" '
            f'title="{esc(tip)}" aria-label="{esc(tip)}">'
            f'<img src="img/catalog/cdot-{with_photo[0]["id"]}.jpg?v=8" alt="" '
            f'width="34" height="34" loading="lazy"></a>')
    nc = len(colors_here)
    dots_html = ""
    if len(dots) > 1:
        dots_html = (f'\n      <div class="cdots" aria-label="Цвета коллекции «{esc(meta["name"])}»">'
                     f'{"".join(dots)}'
                     f'<span class="cdot-tip">{nc} {plural(nc, "цвет", "цвета", "цветов")}</span></div>')

    head_meta = (f"{n} {kinds} · от {rub(lo)} ₽/шт" if lo
                 else f"{n} {kinds} · цена по запросу")
    return f"""
      <div class="tile">
        <a class="t-head" href="collection-{slug}.html">
          <h3>{esc(meta['name'])}</h3>
          <span class="t-head-meta">{head_meta}</span>
        </a>
        <a class="t-main" href="collection-{slug}.html" aria-label="Коллекция «{esc(meta['name'])}» — все {n} {kinds}">
          <span class="mosaic">
{cells}
          <span class="more"><span class="plus">+{n - len(picks[:3])}</span><span class="all">все {n} {kinds}</span></span>
          </span>
          <div class="cap">
            <span class="desc">{esc(TILE_DESC[slug])}</span>
          </div>
        </a>{dots_html}
        <a class="t-meta" href="collection-{slug}.html" aria-label="Открыть коллекцию «{esc(meta['name'])}»">
          <span class="cnt">Смотреть все {n} {kinds}</span>{ARROW}
        </a>
      </div>"""


def build_category():
    total = len(PRODUCTS)
    all_min = min(p["price"] for p in PRODUCTS if p.get("price"))

    # свотчи цветов — ссылки в общую сетку с пресетом цвета
    color_counts = {}
    for p in PRODUCTS:
        color_counts[p["color_group"]] = color_counts.get(p["color_group"], 0) + 1
    swatches = [swatch_link("Все", None, "kirpich-ves.html",
                            aria="Весь кирпич одной сеткой")]
    for color in COLOR_ORDER:
        if color not in SWATCH_CLASS or not color_counts.get(color):
            continue
        n = color_counts[color]
        swatches.append(swatch_link(
            esc(SW_LABEL.get(color, color)), SWATCH_CLASS[color],
            f"kirpich-ves.html?color={quote(color)}",
            aria=f"{esc(color)} — {n} {plural(n, 'вид', 'вида', 'видов')} во всех коллекциях"))

    # плитки в порядке цены: дешёвые первыми, «цена по запросу» в конце
    lane_order = sorted(COLL_ORDER,
                        key=lambda sl: coll_stats(sl)[1] or 10**9)

    # чипы бюджета — ссылки в коллекции (та же цель, что плитки: быстрый ход
    # с телефона, пока плитки ниже экрана)
    budget_chips = [f'<a class="budget-chip" href="kirpich-ves.html">Все '
                    f'<small>{total} {plural(total, "вид", "вида", "видов")}</small></a>']
    for slug in lane_order:
        items, lo = coll_stats(slug)
        meta = COLLECTIONS[slug]
        tail = f"<small>от {rub(lo)} ₽</small>" if lo else "<small>по запросу</small>"
        budget_chips.append(
            f'<a class="budget-chip" href="collection-{slug}.html">'
            f'{esc(meta["name"])} {tail}</a>')

    tiles = [mosaic_tile(slug, eager=(i == 0))
             for i, slug in enumerate(lane_order)]
    tiles.append(f"""
      <a class="tile-all" href="kirpich-ves.html">
        <span class="t-eyebrow">Не хочется выбирать коллекцию?</span>
        <span class="t-title">Весь кирпич одной сеткой — {total} {plural(total, 'вид', 'вида', 'видов')}</span>
        <span class="t-note">Фильтры по цвету, бюджету и фактуре, как на маркетплейсе.</span>
        <span class="go">Показать всё {ARROW}</span>
      </a>""")

    hero = banner(
        "Облицовочный кирпич",
        f"<b>{total} {plural(total, 'вид', 'вида', 'видов')}</b> · {len(COLL_ORDER)} коллекций · от {rub(all_min)} ₽/шт",
        [SLIDE_NEW_BRICK,
         {"eyebrow": "Расчёт",
          "title": "Посчитаем кирпич на дом <b>за 10 минут</b>",
          "sub": "Площадь стен минус проёмы, запас на бой — и цена с доставкой.",
          "cta": "Посчитать кирпич", "href": "#calc",
          "img": "img/cat-brick.jpg"},
         SLIDE_SALE_TILE,
         SLIDE_DELIVERY])

    body = f"""
  <main>
{hero}

    <!-- Подбор: свотч цвета и чип бюджета — входы в сетку/коллекцию, не фильтры -->
    <section class="pick-bar" aria-label="Подбор кирпича">
      <div class="wrap">
        <p class="caption pick-intro">Купить облицовочный кирпич в Краснодаре: {total} {plural(total, "вид", "вида", "видов")} от {rub(all_min)} ₽/шт с заводов Юга. Доставка на объект, оплата при получении.</p>
        <div class="pick-row pick-row--color">
          <span class="pick-row-label">Цвет</span>
          {color_track(chr(10).join(swatches))}
        </div>
        <div class="pick-row">
          <span class="pick-row-label">Бюджет</span>
          <div class="pick-scroll pick-scroll--slide" role="group" aria-label="Коллекция по цене">
            {"".join(budget_chips)}
          </div>
        </div>
        <p class="caption often">Часто ищут:
          <a href="kirpich-ves.html?color={quote("микс (бавария)")}">баварская кладка</a> ·
          <a href="kirpich-ves.html?color={quote("графит")}">графит</a> ·
          <a href="kirpich-ves.html?color={quote("бежевый")}">слоновая кость</a> ·
          <a href="kirpich-ves.html?color={quote("красный")}">красный</a></p>
      </div>
    </section>

    <!-- Коллекции плитками-мозаиками: 3 фото + «+N», кружки цветов, цена -->
    <section class="section" aria-label="Коллекции кирпича">
      <div class="wrap tiles">
{chr(10).join(tiles)}
      </div>
    </section>

    <!-- Калькулятор: расход 51,4 шт/м² — из спеков каталога (1НФ, 250×65,
         шов 10 мм); 1,4НФ — по габаритам ГОСТ из тех же спеков -->
    <section class="section" id="calc" aria-label="Калькулятор кирпича">
      <div class="wrap">
        <div class="section-head">
          <span class="tag">Калькулятор</span>
          <h2>Сколько кирпича понадобится?</h2>
          <p class="caption">Введите площадь стен — посчитаем количество со&nbsp;складским запасом.</p>
        </div>
        <div class="line-calc" id="calcContainer">
          <div class="line-calc-wrap">
            <label class="line-calc-group" for="cWall">
              <span class="line-calc-label">Стены</span>
              <span class="line-calc-input-wrap">
                <input class="line-calc-input" id="cWall" type="number" min="0" step="1" inputmode="decimal" placeholder="0" value="120">
                <span class="line-calc-unit">м²</span>
              </span>
            </label>
            <label class="line-calc-group" for="cOpen">
              <span class="line-calc-label">Окна <br>и двери</span>
              <span class="line-calc-input-wrap">
                <input class="line-calc-input" id="cOpen" type="number" min="0" step="1" inputmode="decimal" placeholder="0" value="18">
                <span class="line-calc-unit">м²</span>
              </span>
            </label>
            <div class="line-calc-group">
              <span class="line-calc-label">Формат</span>
              <select id="cFmt">
                <option value="51.4">1НФ одинарный</option>
                <option value="51.4">0,7НФ евро</option>
                <option value="39.2">1,4НФ полуторный</option>
              </select>
            </div>
            <div class="line-calc-outputs">
              <div class="line-calc-block">
                <span class="line-calc-sub">Понадобится</span>
                <strong class="line-calc-val val-accent" id="calcQty">—</strong>
              </div>
            </div>
            <a class="btn line-calc-btn" href="#lead">
              Получить расчёт
            </a>
          </div>
          <p class="caption line-calc-note">Считаем с запасом 5% на бой и подрезку. Раскладку и доставку посчитает менеджер.</p>
        </div>
      </div>
    </section>
  </main>"""

    js = """
  <script>
    // Свотчи и чипы на этой странице — ссылки (в общую сетку и коллекции),
    // фильтровать здесь нечего: коллекции показаны плитками целиком.
""" + CAROUSEL_JS + """
    // Калькулятор: площадь × расход, запас 5%, округление до десятка
    var cWall = document.getElementById('cWall');
    var cOpen = document.getElementById('cOpen');
    var cFmt = document.getElementById('cFmt');
    var calcQty = document.getElementById('calcQty');

    function recalc() {
      var w = parseFloat(cWall.value) || 0;
      var o = parseFloat(cOpen.value) || 0;
      var area = w - o;
      if (w <= 0 || area <= 0) {
        calcQty.textContent = '—';
        return;
      }
      var rate = parseFloat(cFmt.value);
      var rawQty = Math.ceil(area * rate);
      var reserve = Math.ceil(rawQty * 0.05);
      var totalQty = Math.ceil((rawQty + reserve) / 10) * 10;
      
      calcQty.textContent = totalQty.toLocaleString('ru-RU') + ' шт';
    }

    [cWall, cOpen, cFmt].forEach(function (el) {
      if (el) {
        el.addEventListener('input', recalc);
        el.addEventListener('change', recalc);
      }
    });
    recalc();
  </script>"""

    out = page_shell(
        "Облицовочный кирпич — 5 коллекций, подбор по цвету | Строй-Сейл Краснодар",
        f"Купить облицовочный кирпич в Краснодаре: {total} {plural(total, 'вид', 'вида', 'видов')} от {rub(all_min)} ₽/шт с заводов Юга. "
        "Подбор по цвету, доставка на объект, оплата при получении.",
        body, js + BANNER_JS, promo=False)
    (BASE / "kirpich-oblitsovochnyy.html").write_text(out)
    print("kirpich-oblitsovochnyy.html:", total, "товаров")


# ── Страницы коллекций ───────────────────────────────────────────────────────

# первая пилюля ряда описывает сам ряд — ярлыки-колонки не нужны
CHIP_ALL = {"Фактура": "Любая фактура", "Формат": "Любой формат"}


def sort_row(has_new, default_label="По цвету"):
    """Ряд чипов сортировки (макет утверждён 17.07): не выпадашка — выбор
    виден сразу, один тап. «Узнать цену» при сортировке по цене — в конце."""
    chips = [
        f'<button class="chip is-on" data-sort="default" aria-pressed="true">{default_label}</button>',
        '<button class="chip" data-sort="cheap" aria-pressed="false">Сначала недорогие</button>',
        '<button class="chip" data-sort="exp" aria-pressed="false">Сначала дорогие</button>',
    ]
    if has_new:
        chips.append('<button class="chip" data-sort="new" aria-pressed="false">Новинки</button>')
    return ('<div class="pick-row pick-row--sort"><span class="pick-row-label">Сортировка</span>'
            '<div class="pick-scroll pick-scroll--slide" role="group" '
            f'aria-label="Сортировка">{"".join(chips)}</div></div>')


# сортировка карточек в сетке; initial — порядок вёрстки (наш ручной)
SORT_JS = """
    // Сортировка: перекладываем карточки в #grid; фильтры (hidden) не трогаем
    var grid = document.getElementById('grid');
    var initial = Array.prototype.slice.call(grid.querySelectorAll('.p-card'));
    function priceOf(c) {
      var v = parseFloat(c.dataset.price);
      return isNaN(v) ? Infinity : v; // «Узнать цену» — всегда в конце
    }
    var sorts = {
      cheap: function (a, b) {
        return priceOf(a) - priceOf(b) || initial.indexOf(a) - initial.indexOf(b);
      },
      exp: function (a, b) {
        var pa = priceOf(a), pb = priceOf(b);
        if (pa === Infinity && pb === Infinity) return initial.indexOf(a) - initial.indexOf(b);
        if (pa === Infinity) return 1;
        if (pb === Infinity) return -1;
        return pb - pa;
      },
      new: function (a, b) {
        return (b.dataset.new ? 1 : 0) - (a.dataset.new ? 1 : 0) ||
               initial.indexOf(a) - initial.indexOf(b);
      }
    };
    var sortChips = Array.prototype.slice.call(document.querySelectorAll('.chip[data-sort]'));
    sortChips.forEach(function (ch) {
      ch.addEventListener('click', function () {
        sortChips.forEach(function (x) {
          var on = x === ch;
          x.classList.toggle('is-on', on);
          x.setAttribute('aria-pressed', on ? 'true' : 'false');
        });
        var mode = ch.dataset.sort;
        var order = mode === 'default' ? initial : initial.slice().sort(sorts[mode]);
        order.forEach(function (c) { grid.appendChild(c); });
      });
    });
"""


def chip_row(label, values, group):
    if group == "color":
        # цвет — круги-образцы в одну прокручиваемую строку со стрелкой,
        # единый язык со страницей категории
        chips = [swatch_btn("Все", None, f'data-group="{group}" data-val=""',
                            is_on=True, aria="Все цвета")]
        for v in values:
            chips.append(swatch_btn(
                esc(SW_LABEL.get(v, v)), SWATCH_CLASS.get(v, "sw-all"),
                f'data-group="{group}" data-val="{esc(v)}"', aria=esc(v)))
        return (f'<div class="pick-row pick-row--color">'
                f'<span class="pick-row-label">{label}</span>'
                f'{color_track(chr(10).join(chips))}</div>')
    all_label = CHIP_ALL.get(label, "Все")
    chips = [f'<button class="chip is-on" data-group="{group}" data-val="" '
             f'aria-pressed="true">{all_label}</button>']
    for v in values:
        chips.append(f'<button class="chip" data-group="{group}" data-val="{esc(v)}" '
                     f'aria-pressed="false">{esc(v)}</button>')
    return (f'<div class="pick-row"><span class="pick-row-label">{label}</span>'
            f'<div class="pick-scroll pick-scroll--slide" role="group" '
            f'aria-label="{label}">{"".join(chips)}</div></div>')


def build_collection(slug):
    items, lo = coll_stats(slug)
    meta = COLLECTIONS[slug]
    items_sorted = sorted(items, key=sort_key)
    n = len(items)
    kinds = plural(n, "вид", "вида", "видов")
    price_note = f"от {rub(lo)} ₽/шт" if lo else "цена по запросу"

    colors = [c for c in COLOR_ORDER if any(p["color_group"] == c for p in items)]
    textures = sorted({p["texture"] for p in items})
    formats = []
    for p in items_sorted:
        f = FMT_SHORT.get(p["format"], p["format"])
        if f not in formats:
            formats.append(f)

    filters = []
    if len(colors) > 1:
        filters.append(chip_row("Цвет", colors, "color"))
    if len(textures) > 1:
        filters.append(chip_row("Фактура", textures, "texture"))
    if len(formats) > 1:
        filters.append(chip_row("Формат", formats, "format"))
    filters.append(sort_row(has_new=any(p["name"] in NOVINKI for p in items)))

    cards = "\n".join(card(p) for p in items_sorted)

    body = f"""
  <main>
    <section class="page-head">
      <div class="wrap">
        <nav class="crumbs" aria-label="Вы здесь"><a href="index.html">Главная</a>
          <span aria-hidden="true">/</span> <a href="kirpich-oblitsovochnyy.html">Облицовочный кирпич</a>
          <span aria-hidden="true">/</span> <span>«{esc(meta['name'])}»</span></nav>
        <h1>Коллекция «{esc(meta['name'])}»</h1>
        <p class="page-sub">{esc(meta['tagline'])}</p>
        <p class="lane-meta">{n} {kinds} · {price_note}</p>
      </div>
    </section>

    <!-- Фильтр-бар: тот же язык, что на странице категории -->
    <section class="pick-bar" aria-label="Подбор в коллекции">
      <div class="wrap">
{chr(10).join(filters)}
        <p class="pick-count" id="countNote" aria-live="polite"></p>
      </div>
    </section>

    <section class="section coll" aria-label="Товары коллекции">
      <div class="wrap">
        <div class="p-grid" id="grid">
{cards}
        </div>
        <div class="empty-note" id="emptyNote" hidden>
          <p>С такими фильтрами ничего не нашлось — снимите один из них.</p>
          <button class="btn btn-ghost" id="resetBtn" type="button">Сбросить фильтры</button>
        </div>
      </div>
    </section>
  </main>"""

    js = """
  <script>
    var state = { color: '', texture: '', format: '' };
    var chips = Array.prototype.slice.call(document.querySelectorAll('.chip[data-group], .swatch[data-group]'));
    var cards = Array.prototype.slice.call(document.querySelectorAll('.p-card'));
    var note = document.getElementById('countNote');
    var empty = document.getElementById('emptyNote');

    function plural(n, one, few, many) {
      var m10 = n % 10, m100 = n % 100;
      if (m10 === 1 && m100 !== 11) return one;
      if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
      return many;
    }

    function paint() {
      chips.forEach(function (c) {
        var on = state[c.dataset.group] === c.dataset.val;
        c.classList.toggle('is-on', on);
        c.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
      var shown = 0;
      cards.forEach(function (c) {
        var ok = (!state.color || c.dataset.color === state.color) &&
                 (!state.texture || c.dataset.texture === state.texture) &&
                 (!state.format || c.dataset.format === state.format);
        c.hidden = !ok;
        if (ok) shown++;
      });
      var active = state.color || state.texture || state.format;
      note.textContent = active
        ? 'Показано ' + shown + ' из ' + cards.length + ' ' + plural(cards.length, 'вида', 'видов', 'видов')
        : '';
      empty.hidden = shown !== 0;
    }

    chips.forEach(function (c) {
      c.addEventListener('click', function () {
        var g = c.dataset.group;
        state[g] = (state[g] === c.dataset.val) ? '' : c.dataset.val;
        paint();
      });
    });
    document.getElementById('resetBtn').addEventListener('click', function () {
      state = { color: '', texture: '', format: '' };
      paint();
    });

    // предустановка цвета из ссылки «Ещё N этого цвета» на странице категории
    var pre = new URLSearchParams(location.search).get('color');
    if (pre && cards.some(function (c) { return c.dataset.color === pre; })) {
      state.color = pre;
    }
    paint();
""" + SORT_JS + CAROUSEL_JS + """
  </script>"""

    out = page_shell(
        f"Облицовочный кирпич «{meta['name']}» — {n} {kinds} | Строй-Сейл Краснодар",
        f"Коллекция «{meta['name']}»: {meta['tagline']} {n} {kinds}, {price_note}.",
        body, js)
    (BASE / f"collection-{slug}.html").write_text(out)
    print(f"collection-{slug}.html:", n, "товаров |", price_note)


# ── Весь облицовочный одной сеткой: kirpich-ves.html ─────────────────────────
# Дорожка «показать всё» по Baymard: примерно половина покупателей не хочет
# выбирать коллекцию. По умолчанию карточки идут ГРУППАМИ по коллекциям
# (принцип «фото разных заводов не смешиваются»); сортировка по цене смешивает
# группы — но это осознанное действие пользователя.

def build_ves():
    lane_order = sorted(COLL_ORDER,
                        key=lambda sl: coll_stats(sl)[1] or 10**9)
    items_sorted = []
    for slug in lane_order:
        items, _ = coll_stats(slug)
        items_sorted += sorted(items, key=sort_key)
    total = len(items_sorted)
    all_min = min(p["price"] for p in items_sorted if p.get("price"))
    kinds = plural(total, "вид", "вида", "видов")

    colors = [c for c in COLOR_ORDER
              if any(p["color_group"] == c for p in items_sorted)]
    textures = sorted({p["texture"] for p in items_sorted})

    coll_chips = [f'<button class="budget-chip is-on" data-group="coll" data-val="" '
                  f'aria-pressed="true">Все <small>{total} {kinds}</small></button>']
    for slug in lane_order:
        items, lo = coll_stats(slug)
        meta = COLLECTIONS[slug]
        tail = f"<small>от {rub(lo)} ₽</small>" if lo else "<small>по запросу</small>"
        coll_chips.append(
            f'<button class="budget-chip" data-group="coll" data-val="{slug}" '
            f'aria-pressed="false">{esc(meta["name"])} {tail}</button>')

    filters = [
        chip_row("Цвет", colors, "color"),
        ('<div class="pick-row"><span class="pick-row-label">Бюджет</span>'
         '<div class="pick-scroll pick-scroll--slide" role="group" '
         f'aria-label="Коллекция по цене">{"".join(coll_chips)}</div></div>'),
        chip_row("Фактура", textures, "texture"),
        sort_row(has_new=True, default_label="По коллекциям"),
    ]

    cards = "\n".join(card(p) for p in items_sorted)

    body = f"""
  <main>
    <section class="page-head">
      <div class="wrap">
        <nav class="crumbs" aria-label="Вы здесь"><a href="index.html">Главная</a>
          <span aria-hidden="true">/</span> <a href="kirpich-oblitsovochnyy.html">Облицовочный кирпич</a>
          <span aria-hidden="true">/</span> <span>Вся сетка</span></nav>
        <h1>Весь облицовочный кирпич</h1>
        <p class="page-sub">{total} {kinds} из 5 коллекций, от {rub(all_min)} ₽/шт.
          Удобно сравнивать один цвет между коллекциями.</p>
      </div>
    </section>

    <section class="pick-bar" aria-label="Подбор кирпича">
      <div class="wrap">
{chr(10).join(filters)}
        <p class="pick-count" id="countNote" aria-live="polite"></p>
      </div>
    </section>

    <section class="section coll" aria-label="Все товары">
      <div class="wrap">
        <div class="p-grid" id="grid">
{cards}
        </div>
        <div class="empty-note" id="emptyNote" hidden>
          <p>С такими фильтрами ничего не нашлось — снимите один из них.</p>
          <button class="btn btn-ghost" id="resetBtn" type="button">Сбросить фильтры</button>
        </div>
      </div>
    </section>
  </main>"""

    js = """
  <script>
    var state = { color: '', coll: '', texture: '' };
    var chips = Array.prototype.slice.call(document.querySelectorAll('[data-group]'));
    var cards = Array.prototype.slice.call(document.querySelectorAll('.p-card'));
    var note = document.getElementById('countNote');
    var empty = document.getElementById('emptyNote');

    function plural(n, one, few, many) {
      var m10 = n % 10, m100 = n % 100;
      if (m10 === 1 && m100 !== 11) return one;
      if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
      return many;
    }

    function paint() {
      chips.forEach(function (c) {
        var on = state[c.dataset.group] === c.dataset.val;
        c.classList.toggle('is-on', on);
        c.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
      var shown = 0;
      cards.forEach(function (c) {
        var ok = (!state.color || c.dataset.color === state.color) &&
                 (!state.coll || c.dataset.coll === state.coll) &&
                 (!state.texture || c.dataset.texture === state.texture);
        c.hidden = !ok;
        if (ok) shown++;
      });
      var active = state.color || state.coll || state.texture;
      note.textContent = active
        ? 'Показано ' + shown + ' из ' + cards.length + ' ' + plural(cards.length, 'вида', 'видов', 'видов')
        : '';
      empty.hidden = shown !== 0;
    }

    chips.forEach(function (c) {
      c.addEventListener('click', function () {
        var g = c.dataset.group;
        state[g] = (state[g] === c.dataset.val) ? '' : c.dataset.val;
        paint();
      });
    });
    document.getElementById('resetBtn').addEventListener('click', function () {
      state = { color: '', coll: '', texture: '' };
      paint();
    });

    // предустановки из ссылок страницы категории (свотч цвета / чип «Все»)
    var qs = new URLSearchParams(location.search);
    var preColor = qs.get('color');
    if (preColor && cards.some(function (c) { return c.dataset.color === preColor; })) {
      state.color = preColor;
    }
    var preColl = qs.get('coll');
    if (preColl && cards.some(function (c) { return c.dataset.coll === preColl; })) {
      state.coll = preColl;
    }
    paint();
""" + SORT_JS + CAROUSEL_JS + """
  </script>"""

    out = page_shell(
        f"Весь облицовочный кирпич — {total} {kinds} в одной сетке | Строй-Сейл Краснодар",
        f"Весь облицовочный кирпич без деления на коллекции: {total} {kinds}, "
        f"от {rub(all_min)} ₽/шт. Фильтры по цвету, бюджету и фактуре.",
        body, js)
    (BASE / "kirpich-ves.html").write_text(out)
    print(f"kirpich-ves.html: {total} товаров")


# ── Забутовочный кирпич: подбор по задаче, пока без цен ─────────────────────

RAB = [p for p in DATA["products"] if p["category"] == "obychnyy"]
for p in RAB:
    p["_gallery"] = [f"img/catalog/{p['id']}.jpg"] + [
        f"img/catalog/{p['id']}-{i}.jpg" for i in (2, 3, 4, 5)
        if (CAT_IMG / f"{p['id']}-{i}.jpg").exists()]
    p["_thumb"] = (CAT_IMG / f"{p['id']}.jpg").exists()

TASKS = [
    ("fund", "Фундамент и цоколь"),
    ("walls", "Несущие стены"),
    ("inner", "Перегородки и хозпостройки"),
]

# скрываем дубли-фасовки (та же марка и структура, другая упаковка, без фото)
# КЛЮЧИ — factory_name (не id!): при добавлении товаров id сдвигаются.
RAB_SKIP = {
    "Одинарный М100 (F25 пустот. 13%, 11 сквозных отверстий) 448шт",
    "Одинарный М150 (F25 пустот. 13%, 11 сквозных отверстий) 448шт",
}

RAB_VIEW = {
    # factory_name: (имя на сайте, мета, задачи)
    "Кирпич рядовой керамический пустотелый":
        ("Рядовой пустотелый", "1НФ", ["inner", "walls"]),
    "Кирпич хозяйственный керамический пустотелый":
        ("Хозяйственный пустотелый", "1НФ", ["inner"]),
    "КАМЕНЬ M175 (F75) 192шт упак. пленкой":
        ("Камень керамический М175", "F75", ["walls"]),
    "КРАСНЫЙ Одинарный некондиционный 416шт упак. лентой":
        ("Красный одинарный", "1НФ · некондиция — уценка", ["inner"]),
    "Красный Одинарный М125 (F50) 416шт упак. пленкой и лентой":
        ("Красный одинарный М125", "1НФ · F50", ["walls"]),
    "Одинарный М100 (F25 пустот. 12%, 8 конусных углублений) 448шт":
        ("Пустотелый М100", "1НФ · F25", ["inner"]),
    "Одинарный М150 (F25 пустот. 12%, 8 конусных углублений) 448шт":
        ("Пустотелый М150", "1НФ · F25", ["walls", "inner"]),
    "Одинарный полнотелый М150 (F25 пустот. 12%, 3 скв.отв) 480шт упак. лентой":
        ("Полнотелый М150", "1НФ · F25", ["fund", "walls"]),
    "Одинарный полнотелый М150 (F35 пустот. 12%, 3 скв.отв) 480шт упак. лентой":
        ("Полнотелый М150", "1НФ · F35 — для цоколя", ["fund", "walls"]),
    "Одинарный полнотелый СВАР / некондиция":
        ("Полнотелый", "1НФ · некондиция — уценка", ["inner"]),
    "Одинарный полнотелый сплошной М100 (F25) 420шт упак. лентой":
        ("Полнотелый сплошной М100", "1НФ · F25", ["inner", "walls"]),
    "Одинарный полнотелый сплошной М150 (F25) 420шт упак. лентой":
        ("Полнотелый сплошной М150", "1НФ · F25", ["fund", "walls"]),
    "Одинарный полнотелый сплошной М150 (F35) 420шт упак. лентой":
        ("Полнотелый сплошной М150", "1НФ · F35 — для цоколя", ["fund", "walls"]),
    "Утолщенный полнотелый М150 (F25 пустот. 12%, 3 скв.отв) 352шт упак. лентой":
        ("Утолщённый полнотелый М150", "1,4НФ · F25", ["fund", "walls"]),
    "Утолщенный полнотелый М150 сплошной (F25) 308шт упак. лентой":
        ("Утолщённый сплошной М150", "1,4НФ · F25", ["fund", "walls"]),
    # новинки завода 17.07 — рядовые с лицевой фактурой
    "БЕЛЫЕ НОЧИ Рядовой Одинарный М150 (F50) 416шт упак. пленкой":
        ("Белые ночи М150 — белый", "1НФ · F50", ["walls", "inner"]),
    "БЕЛЫЕ НОЧИ БЕРЕСТА Рядовой Одинарный М150 (F50) 416шт упак. пленкой":
        ("Белые ночи береста М150 — белый", "1НФ · F50", ["walls", "inner"]),
    "БАВАРСКИЙ СВЕТЛЫЙ ВЕЛЬВЕТ Рядовой Одинарный М175 (F75) 416шт упак. пленкой":
        ("Баварский светлый вельвет М175", "1НФ · F75", ["walls"]),
}


def rab_view(p):
    """Имя/мета/задачи забутовки; не роняем сборку на будущей новинке."""
    v = RAB_VIEW.get(p["factory_name"])
    if v is None:
        print(f"  !! RAB_VIEW: нет записи для «{p['factory_name']}» — "
              f"показываю сырое имя")
        v = (p["name"], p.get("mark") or "", ["walls"])
    return v

RAB_LANES = [
    ("Донской", "Классика — рабочая серия",
     "Полнотелый и пустотелый под фундамент, стены и цоколь."),
    ("Губский", "Палитра — рядовая серия",
     "Рядовой и хозяйственный — на перегородки и постройки во дворе."),
]


def card_z(p):
    name, meta, tasks = rab_view(p)
    alt = f"Забутовочный кирпич: {name}"
    if p["_thumb"]:
        img = (f'<img class="p-img" src="img/catalog/{p["id"]}.jpg?v=8" alt="{esc(alt)}" '
               f'width="640" height="480" loading="lazy">')
    else:
        img = ('<div class="p-img p-none" role="img" aria-label="Фото готовим">'
               '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
               'stroke-width="1.5" stroke-linecap="round" aria-hidden="true">'
               '<rect x="3" y="8" width="18" height="9"/>'
               '<path d="M7 11h.01M12 11h.01M17 11h.01"/></svg>'
               '<span>Фото пришлём по запросу</span></div>')
    return (f'<a class="p-card" href="tovar/kirpich-{p["id"]}.html" data-task="{" ".join(tasks)}">'
            f'{img}<h3 class="p-name">{esc(name)}</h3>'
            f'<p class="p-meta">{esc(meta)}</p>'
            f'<span class="p-ask">Узнать цену</span></a>')


def build_zabutovka():
    items = [p for p in RAB if p["factory_name"] not in RAB_SKIP]
    n = len(items)

    chips = ['<button class="chip is-on" data-task="" aria-pressed="true">Все задачи</button>']
    for slug, label in TASKS:
        chips.append(f'<button class="chip" data-task="{slug}" aria-pressed="false">{esc(label)}</button>')

    lanes = []
    for supplier, lane_name, tagline in RAB_LANES:
        sub = [p for p in items if p["supplier"] == supplier]
        sub.sort(key=lambda p: (not p["_thumb"], rab_view(p)[0]))
        cards = "\n".join(card_z(p) for p in sub)
        lane_grid = grid_cls(len(sub))
        lanes.append(f"""
      <section class="lane" aria-label="{esc(lane_name)}">
        <div class="lane-head">
          <div class="lane-head-main">
            <h2>{esc(lane_name)}</h2>
            <p class="lane-meta">{esc(tagline)}</p>
          </div>
        </div>
        <div class="p-grid{lane_grid}">
{cards}
        </div>
      </section>""")

    hero = banner(
        "Забутовочный кирпич",
        f"<b>{n} {plural(n, 'вид', 'вида', 'видов')}</b> · полнотелый и пустотелый · под фундамент и стены",
        [{"eyebrow": "Подбор",
          "title": "Подберём марку под задачу <b>за 5 минут</b>",
          "sub": "Фундамент, несущие стены или перегородки — скажите, что строите.",
          "cta": "Получить подбор", "href": "#lead",
          "img": "img/cat-brick.jpg"},
         SLIDE_NEW_BRICK,
         SLIDE_SALE_TILE,
         SLIDE_DELIVERY])

    body = f"""
  <main>
{hero}

    <section class="pick-bar" aria-label="Подбор по задаче">
      <div class="wrap">
        <p class="caption pick-intro">Купить забутовочный кирпич в Краснодаре — {n} {plural(n, "вид", "вида", "видов")} с заводов Юга.
          Рабочий кирпич прячется под облицовкой и штукатуркой: главное в нём — марка прочности, а не красота.</p>
        <div class="pick-row">
          <span class="pick-row-label">Задача</span>
          <div class="pick-scroll pick-scroll--slide" role="group" aria-label="Что будете строить">
{chr(10).join(chips)}
          </div>
        </div>
        <p class="pick-count" id="pickNote" aria-live="polite"></p>
      </div>
    </section>

    <div class="wrap lanes">
{chr(10).join(lanes)}
    </div>

    <section class="section">
      <div class="wrap">
        <p class="caption cats-note">Прайс на забутовочный кирпич обновляется —
          цену с доставкой на ваш адрес назовёт менеджер. Перезвоним за 5 минут.</p>
      </div>
    </section>
  </main>"""

    js = """
  <script>
    var chips = Array.prototype.slice.call(document.querySelectorAll('.chip'));
    var lanes = Array.prototype.slice.call(document.querySelectorAll('.lane'));
    var note = document.getElementById('pickNote');

    function plural(n, one, few, many) {
      var m10 = n % 10, m100 = n % 100;
      if (m10 === 1 && m100 !== 11) return one;
      if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
      return many;
    }

    function apply(task) {
      var total = 0;
      lanes.forEach(function (lane) {
        var shown = 0;
        Array.prototype.slice.call(lane.querySelectorAll('.p-card')).forEach(function (c) {
          var ok = !task || c.dataset.task.split(' ').indexOf(task) !== -1;
          c.hidden = !ok;
          if (ok) shown++;
        });
        lane.hidden = shown === 0;
        total += shown;
      });
      note.textContent = task
        ? 'Подходит ' + total + ' ' + plural(total, 'вид', 'вида', 'видов') + ':'
        : '';
    }

    chips.forEach(function (c) {
      c.addEventListener('click', function () {
        chips.forEach(function (x) {
          x.classList.toggle('is-on', x === c);
          x.setAttribute('aria-pressed', x === c ? 'true' : 'false');
        });
        apply(c.dataset.task);
      });
    });
  </script>"""

    out = page_shell(
        f"Забутовочный кирпич — подбор по задаче | Строй-Сейл Краснодар",
        f"Купить забутовочный (рабочий) кирпич в Краснодаре: {n} {plural(n, 'вид', 'вида', 'видов')} под фундамент, "
        "стены и перегородки. Доставка на объект, оплата при получении.",
        body, js + BANNER_JS, promo=False)
    (BASE / "kirpich-zabutovochnyy.html").write_text(out)
    print(f"kirpich-zabutovochnyy.html: {n} товаров (цены скрыты)")


# ── Карточка товара: tovar/kirpich-<id>.html ────────────────────────────────

# человеческие размеры по формату (мм) — если в спеках нет габаритов
FMT_MM = {
    "1НФ (одинарный)": "250×120×65", "1,4НФ (полуторный)": "250×120×88",
    "0,7НФ (евро)": "250×85×65", "0,9НФ": "250×108×65",
    "Ригель MF": "290×90×40", "Лонг LF": "490×90×40",
    "WDF": "215×102×65", "WMF": "210×100×50",
}

COLL_USE = {
    "ekonom": "Забор, хозпостройки, большие объёмы — там, где важна цена.",
    "palitra": "Фасад дома и забор — когда ищете точный оттенок.",
    "klassika": "Дом, забор и цоколь из одной коллекции.",
    "evropa": "Фасады «под старину» — рельефная поверхность с характером.",
    "formovka": "Премиальные фасады: у каждого кирпича свой рисунок.",
}


def brick_specs_rows(p):
    """Характеристики простым языком: только то, что есть в данных."""
    sp = p.get("specs") or {}
    fmt = FMT_SHORT.get(p["format"], p["format"])
    # срезаем любую единицу из данных (у Донских « см», у Губских « мм») —
    # « мм» дописывается ниже один раз; латинскую x приводим к «×»
    size = re.sub(r"\s*(мм|см)\s*$", "", sp.get("Габариты", "").strip())
    size = size.replace("х", "×").replace("x", "×").strip()
    if not size:
        size = FMT_MM.get(p["format"], "")
    rows = []
    if size:
        rows.append(("Размер", f"{size} мм"))
    rows.append(("Формат", fmt))
    strength = sp.get("Марка прочности")
    if strength:
        rows.append(("Прочность", f"{strength} — с запасом на два этажа"))
    frost = sp.get("Марка морозостойкости")
    if frost:
        rows.append(("Морозостойкость", f"{frost} — {str(frost).lstrip('F')} циклов зима-лето"))
    struct = sp.get("Структура") or sp.get("Пустотность (%)")
    if sp.get("Структура"):
        rows.append(("Структура", sp["Структура"].lower()))
    w = sp.get("Вес")
    if w:
        w = str(w).strip()
        if w.lower().startswith("кг"):  # у поставщика «кг 2,6-2,7»
            w = w[2:].strip() + " кг"
        w = w.replace("-", "–").replace(".", ",")
        # у 16 товаров «Европы» в данных обрезок «упаковки» — мусор без цифр не выводим
        if any(ch.isdigit() for ch in w):
            rows.append(("Вес штуки", w))
    cons = p.get("consumption_per_m2")
    if cons:
        rows.append(("Расход", f"{str(cons).replace('.', ',')} шт на 1 м² кладки"))
    return rows


def similar_bricks(p, k=4):
    """Похожие: та же коллекция, сперва тот же цвет, только с фото."""
    pool = [q for q in PRODUCTS
            if q["collection"] == p["collection"] and q["id"] != p["id"] and q["_thumb"]]
    pool.sort(key=lambda q: (q["color_group"] != p["color_group"],
                             q["texture"] != p["texture"], q["name"]))
    return pool[:k]


def build_brick_product(p, is_rab=False):
    root = "../"
    if is_rab:
        disp_name, disp_meta, _tasks = rab_view(p)
        crumb_cat = ("kirpich-zabutovochnyy.html", "Забутовочный кирпич")
        crumb_coll = None
        use_note = "Рабочая кладка: фундамент, несущие стены, перегородки — всё, что прячется под облицовкой."
        title_kind = "Забутовочный кирпич"
    else:
        disp_name = p["name"]
        disp_meta = None
        meta = COLLECTIONS[p["collection"]]
        crumb_cat = ("kirpich-oblitsovochnyy.html", "Облицовочный кирпич")
        crumb_coll = (f"collection-{p['collection']}.html", f"«{meta['name']}»")
        use_note = COLL_USE[p["collection"]]
        title_kind = "Облицовочный кирпич"

GALLERY_JS = """
  <script>
    (function () {
      var main = document.getElementById('pdMain');
      var mainWrap = document.getElementById('pdMainWrap');
      var thumbs = Array.prototype.slice.call(document.querySelectorAll('.pd-thumb'));
      
      if (!main) return;
      
      // Смена изображений с плавным затуханием (fade)
      function switchMain(src, activeThumb) {
        // сравниваем абсолютные URL: main.src всегда абсолютный, data-src — относительный
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


def build_brick_product(p, is_rab=False):
    root = "../"
    if is_rab:
        disp_name, disp_meta, _tasks = rab_view(p)
        crumb_cat = ("kirpich-zabutovochnyy.html", "Забутовочный кирпич")
        crumb_coll = None
        use_note = "Рабочая кладка: фундамент, несущие стены, перегородки — всё, что прячется под облицовкой."
        title_kind = "Забутовочный кирпич"
    else:
        disp_name = p["name"]
        disp_meta = None
        meta = COLLECTIONS[p["collection"]]
        crumb_cat = ("kirpich-oblitsovochnyy.html", "Облицовочный кирпич")
        crumb_coll = (f"collection-{p['collection']}.html", f"«{meta['name']}»")
        use_note = COLL_USE[p["collection"]]
        title_kind = "Облицовочный кирпич"

    name = esc(disp_name)
    alt = f"{title_kind} «{disp_name}»"
    
    thumbs = ""
    if len(p["_gallery"]) > 1:
        btns = []
        for i, src in enumerate(p["_gallery"]):
            on = " is-on" if i == 0 else ""
            pressed = "true" if i == 0 else "false"
            btns.append(
                f'<button class="pd-thumb{on}" type="button" data-src="{root}{src}?v=7" '
                f'aria-pressed="{pressed}" aria-label="Фото {i + 1}">'
                f'<img src="{root}{src}?v=7" alt="" width="640" height="480" loading="lazy"></button>')
        thumbs = f'\n      <div class="pd-thumbs">{"".join(btns)}</div>'

    if p["_thumb"]:
        photo = (f'<div class="pd-main-wrap" id="pdMainWrap">'
                 f'<img class="pd-main" id="pdMain" src="{root}{p["_gallery"][0]}?v=7" '
                 f'alt="{esc(alt)}" width="640" height="480">'
                 f'<button class="pd-zoom-trigger" id="pdZoomTrigger" type="button" aria-label="Открыть во весь экран">'
                 f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>'
                 f'</button></div>{thumbs}')
    else:
        photo = ('<div class="pd-main p-none" role="img" aria-label="Фото готовим">'
                 '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                 'stroke-width="1.5" stroke-linecap="round" aria-hidden="true">'
                 '<rect x="3" y="8" width="18" height="9"/>'
                 '<path d="M7 11h.01M12 11h.01M17 11h.01"/></svg>'
                 '<span>Пришлём живые фото в мессенджер — напишите нам</span></div>')

    # Честный дисклеймер + действие (паттерн Randers/Wienerberger: наш аналог
    # «заказать образец» — живые фото в WhatsApp). Только у товаров с фото.
    if p["_thumb"]:
        wa_tone = ("https://wa.me/79000000000?text=" + quote(
            f"Здравствуйте! Пришлите живые фото кирпича «{disp_name}» (пишу с сайта Строй-Сейл)"))
        tone_note = (f'<p class="caption pd-tone-note">Оттенок на экране может отличаться — '
                     f'<a href="{wa_tone}" target="_blank" rel="noopener">пришлём живые фото и видео в WhatsApp</a>.</p>')
    else:
        tone_note = ""

    # цена: базовая + цены форматов, либо «по запросу».
    # Забутовка (is_rab): цены скрыты по решению пользователя до нового прайса —
    # каталог показывает «Узнать цену», карточка не должна их светить.
    if p.get("price") and not is_rab:
        m2 = m2_price(p)
        m2_line = (f'<p class="caption pd-m2">≈ {rub(m2)} ₽ за м² кладки</p>'
                   if m2 else "")
        price_html = (f'<p class="pd-price">{rub(p["price"])} ₽<span class="pd-price-unit">/шт</span></p>'
                      + m2_line)
        fmts = p.get("formats_prices") or {}
        fmt_lines = []
        for f_name, f_price in fmts.items():
            if f_name == p["format"]:
                continue  # базовый формат уже показан большой ценой
            short = FMT_SHORT.get(f_name)
            if short is None:
                # составная метка («1НФ (одинарный), марка М175») —
                # переводим известную часть на простой язык
                short = f_name
                for full, s in FMT_SHORT.items():
                    short = short.replace(full, s)
            fmt_lines.append(f"{esc(short)} — {rub(f_price)} ₽")
        fmt_note = (f'<p class="caption pd-price-note">Другие форматы: {" · ".join(fmt_lines)}.</p>'
                    if fmt_lines else "")
        price_note = (fmt_note +
                      '<p class="caption pd-price-note">Заводская цена. Точную цену с доставкой на ваш адрес назовёт менеджер.</p>')
    else:
        price_html = '<p class="pd-price pd-price-ask">Цена по запросу</p>'
        price_note = ('<p class="caption pd-price-note">Пришлём прайс за 5 минут — '
                      'напишите в любой мессенджер или оставьте номер.</p>')

    specs = "\n".join(
        f'          <div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>'
        for k, v in brick_specs_rows(p))

    crumb_mid = (f'<a href="{root}{crumb_coll[0]}">{esc(crumb_coll[1])}</a> <span aria-hidden="true">/</span>'
                 if crumb_coll else "")

    sim = similar_bricks(p)
    similar_html = ""
    if sim:
        sim_cards = "\n".join(card(q, root=root) for q in sim)
        similar_html = f"""
  <section class="section" aria-label="Похожие кирпичи">
    <div class="wrap">
      <div class="section-head">
        <h2>Похожие по цвету и коллекции</h2>
      </div>
      <div class="p-grid{grid_cls(len(sim))}">
{sim_cards}
      </div>
      <div class="more">
        <a class="btn btn-ghost" href="{root}{crumb_cat[0] if is_rab else crumb_coll[0]}">Вся {"категория" if is_rab else "коллекция"}</a>
      </div>
    </div>
  </section>"""

    fmt_short = FMT_SHORT.get(p["format"], p["format"])
    meta_parts = []
    if p.get("kind"):
        meta_parts.append(p["kind"])
    meta_parts.append(p["texture"])
    meta_parts.append(fmt_short)
    meta_text = " · ".join(meta_parts)
    
    meta_line = esc(disp_meta) if is_rab else esc(meta_text)

    body = f"""
  <section class="page-head">
    <div class="wrap">
      <nav class="crumbs" aria-label="Хлебные крошки">
        <a href="{root}index.html">Главная</a> <span aria-hidden="true">/</span>
        <a href="{root}{crumb_cat[0]}">{crumb_cat[1]}</a> <span aria-hidden="true">/</span>
        {crumb_mid}
        <span>{name}</span>
      </nav>
    </div>
  </section>

  <section class="section pd" aria-label="Карточка товара">
    <div class="wrap pd-grid">
      <div class="pd-gallery">
        {photo}
        {tone_note}
      </div>
      <div class="pd-info">
        <p class="tag">{title_kind}</p>
        <h1 class="pd-name">{name}</h1>
        <p class="p-meta">{meta_line}</p>
        {price_html}
        {price_note}
        {order_btns(root, f"кирпич «{disp_name}»")}
        <dl class="pd-specs">
{specs}
        </dl>
        <p class="caption pd-usage"><strong>Куда подходит:</strong> {esc(use_note)}</p>
      </div>
    </div>
  </section>
{similar_html}"""

    ld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": f"{title_kind} «{disp_name}»",
        "description": f"{title_kind} «{disp_name}». {use_note}",
    }
    if p["_thumb"]:
        ld["image"] = f"{SITE_URL}img/catalog/{p['id']}.jpg"
    if p.get("price") and not is_rab:
        ld["offers"] = {"@type": "Offer", "priceCurrency": "RUB",
                        "price": p["price"],
                        "availability": "https://schema.org/InStock"}
    extra_head = ('\n  <script type="application/ld+json">'
                  + json.dumps(ld, ensure_ascii=False) + "</script>")

    price_str = (f"{rub(p['price'])} ₽/шт"
                 if p.get("price") and not is_rab else "цена по запросу")
    out = page_shell(
        f"{title_kind} «{disp_name}» — {price_str} | Строй-Сейл Краснодар",
        f"{title_kind} «{disp_name}»: {price_str}. {use_note} "
        "Доставка по Краснодару и краю, оплата при получении.",
        body, extra_js=GALLERY_JS, root=root,
        cta_h2="Возьмём подбор на себя",
        cta_note="Пришлём живые фото этого кирпича, посчитаем количество на дом и скажем цену с доставкой.",
        product=f"кирпич «{disp_name}»",
        extra_head=extra_head)
    (BASE / "tovar" / f"kirpich-{p['id']}.html").write_text(out)


def build_brick_products():
    (BASE / "tovar").mkdir(exist_ok=True)
    n = 0
    for p in PRODUCTS:
        build_brick_product(p)
        n += 1
    for p in RAB:
        if p["factory_name"] in RAB_SKIP:
            continue
        build_brick_product(p, is_rab=True)
        n += 1
    print(f"tovar/kirpich-*.html: {n} страниц")


if __name__ == "__main__":
    build_category()
    build_ves()
    for slug in COLL_ORDER:
        build_collection(slug)
    build_zabutovka()
    build_brick_products()
