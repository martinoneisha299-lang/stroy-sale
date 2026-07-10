#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""catalog.json → страницы каталога облицовочного кирпича.

Генерирует:
- kirpich-oblitsovochnyy.html — категория: подбор по цвету + 5 лент коллекций;
- collection-<slug>.html × 5 — полная сетка коллекции с фильтрами.

Принцип «коллекций»: фото разных поставщиков никогда не смешиваются в одной
сетке — даже при фильтре по цвету результаты идут группами по коллекциям.
"""

import html
import json
from pathlib import Path
from urllib.parse import quote

BASE = Path("/Users/dm/Desktop/сайт")
DATA = json.loads((BASE / "data" / "catalog.json").read_text())

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
    """Кнопка-образец цвета: кирпичик-образец + подпись.
    dot_class=None — текстовая кнопка «Все» (не псевдо-свотч)."""
    on = ' is-on' if is_on else ''
    pressed = 'true' if is_on else 'false'
    aria_attr = f' aria-label="{aria}"' if aria else ''
    if dot_class is None:
        return (f'<button class="swatch sw-text{on}" {attrs} '
                f'aria-pressed="{pressed}"{aria_attr}>{label}</button>')
    return (f'<button class="swatch{on}" {attrs} aria-pressed="{pressed}"{aria_attr}>'
            f'<span class="swatch-dot {dot_class}" aria-hidden="true"></span>'
            f'<span class="sw-name">{label}</span></button>')

COLLECTIONS = {
    "ekonom": {
        "name": "Эконом",
        "tagline": "Когда важна цена: заборы, хозпостройки и большие объёмы — без потери вида.",
    },
    "palitra": {
        "name": "Палитра",
        "tagline": "54 цвета — от белого до графита. Если ищете «тот самый» оттенок, он здесь.",
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


def esc(s):
    return html.escape(str(s), quote=True)


def sort_key(p):
    return (COLOR_ORDER.index(p["color_group"]), p["name"])


def card(p, feat_hidden=None, root=""):
    """Карточка кирпича — вся карточка ссылка на страницу товара.
    feat_hidden: None — всегда видна (страница коллекции);
    True/False — лента категории, hidden если не featured."""
    alt = f"Кирпич «{p['name']}» — {p['color_group']}, {p['texture']}"
    if p["_thumb"]:
        img = (f'<img class="p-img" src="{root}img/catalog/{p["id"]}.jpg?v=3" alt="{esc(alt)}" '
               f'width="640" height="480" loading="lazy">')
    else:
        img = ('<div class="p-img p-none" role="img" aria-label="Фото готовим">'
               '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
               'stroke-width="1.5" stroke-linecap="round" aria-hidden="true">'
               '<rect x="3" y="8" width="18" height="9"/>'
               '<path d="M7 11h.01M12 11h.01M17 11h.01"/></svg>'
               '<span>Фото пришлём по запросу</span></div>')
    if p.get("price"):
        price = f'<p class="p-price">{rub(p["price"])} ₽/шт</p>'
    else:
        price = '<span class="p-ask">Узнать цену</span>'
    hidden = " hidden" if feat_hidden else ""
    fmt = FMT_SHORT.get(p["format"], p["format"])
    attrs = (f'data-color="{esc(p["color_group"])}" '
             f'data-texture="{esc(p["texture"])}" data-format="{esc(fmt)}"{hidden}')
    
    meta_parts = []
    if p.get("kind"):
        meta_parts.append(p["kind"])
    meta_parts.append(p["texture"])
    meta_parts.append(fmt)
    meta_text = " · ".join(meta_parts)
    
    inner = (f'{img}<h3 class="p-name">{esc(p["name"])}</h3>'
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
    """Сезонное предложение: тонкая полоска над шапкой. data-until — дата
    окончания; после неё полоска скрывается сама (скрипт в page_shell)."""
    return (f'<a class="promo-bar" href="{root}plitka-staryy-gorod.html" data-until="2026-07-20">'
            f'<b>−15%</b> на плитку «Старый город» — до 20 июля'
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


# Скрипты каркаса: форма заявки (демо) + срок промо-полоски
SHELL_JS = """
  <script>
    (function () {
      var f = document.getElementById('ctaForm');
      if (f) {
        f.addEventListener('submit', function (e) {
          e.preventDefault();
          var ph = document.getElementById('cfPhone');
          if (!ph.value.trim()) { ph.focus(); return; }
          f.hidden = true;
          document.getElementById('ctaOk').hidden = false;
        });
      }
      var promo = document.querySelector('.promo-bar');
      if (promo && promo.dataset.until) {
        var end = new Date(promo.dataset.until + 'T23:59:59');
        if (new Date() > end) promo.remove();
      }
    })();
  </script>"""


def page_shell(title, descr, body, extra_js="", root="",
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
  <link rel="stylesheet" href="{root}styles.css?v=11">{extra_head}
</head>
<body>

{promo_bar(root)}

  <header class="masthead">
    <div class="wrap masthead-in">
      <a class="wordmark" href="{root}index.html">
        <svg class="brand-mark" viewBox="0 0 100 88" aria-hidden="true"><path fill="var(--color-logo)" d="M50 4 L96 84 H70 L50 36 L30 84 H4 Z"/></svg>
        <span class="wordmark-text"><strong>СТРОЙСЕЙЛ</strong>
        <span>Стройматериалы · Краснодар</span></span>
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
            <p class="caption form-note">Нажимая кнопку, вы соглашаетесь с
              <a href="{root}policy.html">политикой конфиденциальности</a>.
              Номер не передаём третьим лицам.</p>
          </form>
          <p class="form-ok" id="ctaOk" hidden>Заявка принята — скоро перезвоним (демо)</p>
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

def build_category():
    total = len(PRODUCTS)
    all_min = min(p["price"] for p in PRODUCTS if p.get("price"))

    # свотчи цветов
    color_counts = {}
    for p in PRODUCTS:
        color_counts[p["color_group"]] = color_counts.get(p["color_group"], 0) + 1
    swatches = [swatch_btn("Все", None, 'data-color=""',
                           is_on=True, aria="Все цвета")]
    for color in COLOR_ORDER:
        if color not in SWATCH_CLASS or not color_counts.get(color):
            continue
        n = color_counts[color]
        swatches.append(swatch_btn(
            esc(SW_LABEL.get(color, color)), SWATCH_CLASS[color],
            f'data-color="{esc(color)}"',
            aria=f"{esc(color)} — {n} {plural(n, 'вид', 'вида', 'видов')}"))

    # ленты в порядке цены: дешёвые первыми, «цена по запросу» в конце
    lane_order = sorted(COLL_ORDER,
                        key=lambda sl: coll_stats(sl)[1] or 10**9)

    # чипы бюджета — фильтр по коллекции (кнопки, не якоря)
    budget_chips = ['<button class="budget-chip is-on" data-coll="" aria-pressed="true">Все</button>']
    for slug in lane_order:
        items, lo = coll_stats(slug)
        meta = COLLECTIONS[slug]
        tail = f"<small>от {rub(lo)} ₽</small>" if lo else "<small>по запросу</small>"
        budget_chips.append(
            f'<button class="budget-chip" data-coll="{slug}" aria-pressed="false">'
            f'{esc(meta["name"])} {tail}</button>')

    lanes = []
    for slug in lane_order:
        items, lo = coll_stats(slug)
        meta = COLLECTIONS[slug]
        featured = pick_featured(items)
        feat_ids = {p["id"] for p in featured}
        items_sorted = sorted(items, key=sort_key)
        cards = "\n".join(
            card(p, feat_hidden=(p["id"] not in feat_ids))
            for p in items_sorted)
        n = len(items)
        kinds = plural(n, "вид", "вида", "видов")
        price_note = f"от {rub(lo)} ₽/шт" if lo else "цена по запросу"
        lanes.append(f"""
      <section class="lane" id="lane-{slug}" data-coll="{slug}" data-page="collection-{slug}.html" aria-label="Коллекция «{esc(meta['name'])}»">
        <div class="lane-head">
          <div class="lane-head-main">
            <h2>{esc(meta['name'])}</h2>
            <p class="lane-meta">{n} {kinds} · {price_note}</p>
          </div>
          <a class="lane-all" href="collection-{slug}.html">Смотреть все {n}&nbsp;→</a>
        </div>
        <div class="p-grid">
{cards}
        </div>
      </section>""")

    body = f"""
  <main>
    <section class="page-head">
      <div class="wrap">
        <nav class="crumbs" aria-label="Вы здесь"><a href="index.html">Главная</a>
          <span aria-hidden="true">/</span> <span>Облицовочный кирпич</span></nav>
        <h1>Облицовочный кирпич</h1>
        <p class="page-sub">{total} видов, от {rub(all_min)} ₽/шт. Доставка на объект, оплата при получении.</p>
      </div>
    </section>

    <!-- Фильтр-бар: цвет и бюджет работают вместе -->
    <section class="pick-bar" aria-label="Подбор кирпича">
      <div class="wrap">
        <div class="pick-row">
          <span class="pick-row-label">Цвет</span>
          <div class="pick-scroll" role="group" aria-label="Цвет кирпича">
{chr(10).join(swatches)}
          </div>
        </div>
        <div class="pick-row">
          <span class="pick-row-label">Бюджет</span>
          <div class="pick-scroll pick-scroll--slide" role="group" aria-label="Коллекция по цене">
            {"".join(budget_chips)}
          </div>
        </div>
        <p class="pick-count" id="pickNote" aria-live="polite"></p>
      </div>
    </section>

    <div class="wrap lanes" id="lanes">
{chr(10).join(lanes)}
    </div>

    <!-- Калькулятор: расход 51,4 шт/м² — из спеков каталога (1НФ, 250×65,
         шов 10 мм); 1,4НФ — по габаритам ГОСТ из тех же спеков -->
    <section class="section" id="calc" aria-label="Калькулятор кирпича">
      <div class="wrap">
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
              <span class="line-calc-label">Окна<br>и двери</span>
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
              Получить точный расчёт
            </a>
          </div>
          <p class="caption line-calc-note">Считаем с запасом 5% на бой и подрезку. Раскладку и доставку посчитает менеджер.</p>
        </div>
      </div>
    </section>
  </main>"""

    js = """
  <script>
    // Фильтр каталога: цвет и бюджет работают вместе. Карточки уже в DOM,
    // фильтруем показом/скрытием. Результат всегда группами по коллекциям —
    // стили фото разных заводов не смешиваем. Инлайн-лимит на ленту, полный
    // список — по ссылке «Смотреть все N».
    var LANE_LIMIT = 8;
    var swatches = Array.prototype.slice.call(document.querySelectorAll('.swatch'));
    var chips = Array.prototype.slice.call(document.querySelectorAll('.budget-chip'));
    var lanes = Array.prototype.slice.call(document.querySelectorAll('.lane'));
    var note = document.getElementById('pickNote');
    var state = { color: '', coll: '' };

    function plural(n, one, few, many) {
      var m10 = n % 10, m100 = n % 100;
      if (m10 === 1 && m100 !== 11) return one;
      if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
      return many;
    }

    // featured-карточки помечаем по стартовому состоянию разметки
    lanes.forEach(function (lane) {
      Array.prototype.slice.call(lane.querySelectorAll('.p-card')).forEach(function (c) {
        c.dataset.feat = c.hidden ? '0' : '1';
      });
    });

    function apply() {
      var filtered = !!(state.color || state.coll);
      var totalMatch = 0;
      lanes.forEach(function (lane) {
        // фильтр коллекции: показываем только выбранную ленту
        if (state.coll && lane.dataset.coll !== state.coll) {
          lane.hidden = true;
          return;
        }
        var cards = Array.prototype.slice.call(lane.querySelectorAll('.p-card'));
        var shown = 0, match = 0;
        cards.forEach(function (c) {
          var colorOk = !state.color || c.dataset.color === state.color;
          if (colorOk) match++;
          var show = filtered ? (colorOk && shown < LANE_LIMIT) : (c.dataset.feat === '1');
          c.hidden = !show;
          if (show) shown++;
        });
        var hide = filtered && match === 0;
        lane.hidden = hide;
        if (!hide) totalMatch += match;
        var all = lane.querySelector('.lane-all');
        if (all) {
          all.href = lane.dataset.page +
            (state.color ? '?color=' + encodeURIComponent(state.color) : '');
        }
      });
      if (!state.color) { note.textContent = ''; return; }
      note.textContent = totalMatch
        ? 'Нашлось ' + totalMatch + ' ' + plural(totalMatch, 'вид', 'вида', 'видов') + ' — ' + state.color
        : 'Такого цвета сейчас нет — сбросьте фильтр';
    }

    swatches.forEach(function (s) {
      s.addEventListener('click', function () {
        state.color = s.dataset.color;
        swatches.forEach(function (x) {
          var on = x === s;
          x.classList.toggle('is-on', on);
          x.setAttribute('aria-pressed', on ? 'true' : 'false');
        });
        apply();
      });
    });

    chips.forEach(function (ch) {
      ch.addEventListener('click', function () {
        state.coll = ch.dataset.coll;
        chips.forEach(function (x) {
          var on = x === ch;
          x.classList.toggle('is-on', on);
          x.setAttribute('aria-pressed', on ? 'true' : 'false');
        });
        apply();
        if (state.coll) {
          var lane = document.getElementById('lane-' + state.coll);
          if (lane) lane.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });

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
        f"Облицовочный кирпич в Краснодаре: {total} видов, от {rub(all_min)} ₽/шт. "
        "Подбор по цвету, доставка на объект, оплата при получении.",
        body, js)
    (BASE / "kirpich-oblitsovochnyy.html").write_text(out)
    print("kirpich-oblitsovochnyy.html:", total, "товаров")


# ── Страницы коллекций ───────────────────────────────────────────────────────

def chip_row(label, values, group):
    if group == "color":
        # цвет — кирпичики-образцы, единый язык со страницей категории
        chips = [swatch_btn("Все", None, f'data-group="{group}" data-val=""',
                            is_on=True, aria="Все цвета")]
        for v in values:
            chips.append(swatch_btn(
                esc(SW_LABEL.get(v, v)), SWATCH_CLASS.get(v, "sw-all"),
                f'data-group="{group}" data-val="{esc(v)}"', aria=esc(v)))
    else:
        chips = [f'<button class="chip is-on" data-group="{group}" data-val="" aria-pressed="true">Все</button>']
        for v in values:
            chips.append(f'<button class="chip" data-group="{group}" data-val="{esc(v)}" '
                         f'aria-pressed="false">{esc(v)}</button>')
    return (f'<div class="filter-row"><span class="tag filter-label">{label}</span>'
            f'<div class="filter-chips">{"".join(chips)}</div></div>')


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

    <section class="section coll" aria-label="Товары коллекции">
      <div class="wrap">
        <div class="filters">
{chr(10).join(filters)}
        </div>
        <p class="pick-count" id="countNote" aria-live="polite"></p>
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
  </script>"""

    out = page_shell(
        f"Облицовочный кирпич «{meta['name']}» — {n} {kinds} | Строй-Сейл Краснодар",
        f"Коллекция «{meta['name']}»: {meta['tagline']} {n} {kinds}, {price_note}.",
        body, js)
    (BASE / f"collection-{slug}.html").write_text(out)
    print(f"collection-{slug}.html:", n, "товаров |", price_note)


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
RAB_SKIP = {"rab-007", "rab-009"}

RAB_VIEW = {
    # id: (имя на сайте, мета, задачи)
    "rab-001": ("Рядовой пустотелый", "1НФ", ["inner", "walls"]),
    "rab-002": ("Хозяйственный пустотелый", "1НФ", ["inner"]),
    "rab-003": ("Камень керамический М175", "F75", ["walls"]),
    "rab-004": ("Красный одинарный", "1НФ · некондиция — уценка", ["inner"]),
    "rab-005": ("Красный одинарный М125", "1НФ · F50", ["walls"]),
    "rab-006": ("Пустотелый М100", "1НФ · F25", ["inner"]),
    "rab-008": ("Пустотелый М150", "1НФ · F25", ["walls", "inner"]),
    "rab-010": ("Полнотелый М150", "1НФ · F25", ["fund", "walls"]),
    "rab-011": ("Полнотелый М150", "1НФ · F35 — для цоколя", ["fund", "walls"]),
    "rab-012": ("Полнотелый", "1НФ · некондиция — уценка", ["inner"]),
    "rab-013": ("Полнотелый сплошной М100", "1НФ · F25", ["inner", "walls"]),
    "rab-014": ("Полнотелый сплошной М150", "1НФ · F25", ["fund", "walls"]),
    "rab-015": ("Полнотелый сплошной М150", "1НФ · F35 — для цоколя", ["fund", "walls"]),
    "rab-016": ("Утолщённый полнотелый М150", "1,4НФ · F25", ["fund", "walls"]),
    "rab-017": ("Утолщённый сплошной М150", "1,4НФ · F25", ["fund", "walls"]),
}

RAB_LANES = [
    ("Донской", "Классика — рабочая серия",
     "Полнотелый и пустотелый под фундамент, стены и цоколь."),
    ("Губский", "Палитра — рядовая серия",
     "Рядовой и хозяйственный — на перегородки и постройки во дворе."),
]


def card_z(p):
    name, meta, tasks = RAB_VIEW[p["id"]]
    alt = f"Забутовочный кирпич: {name}"
    if p["_thumb"]:
        img = (f'<img class="p-img" src="img/catalog/{p["id"]}.jpg?v=3" alt="{esc(alt)}" '
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
    items = [p for p in RAB if p["id"] not in RAB_SKIP]
    n = len(items)

    chips = ['<button class="chip is-on" data-task="" aria-pressed="true">Все задачи</button>']
    for slug, label in TASKS:
        chips.append(f'<button class="chip" data-task="{slug}" aria-pressed="false">{esc(label)}</button>')

    lanes = []
    for supplier, lane_name, tagline in RAB_LANES:
        sub = [p for p in items if p["supplier"] == supplier]
        sub.sort(key=lambda p: (not p["_thumb"], RAB_VIEW[p["id"]][0]))
        cards = "\n".join(card_z(p) for p in sub)
        lanes.append(f"""
      <section class="lane" aria-label="{esc(lane_name)}">
        <div class="lane-head">
          <div class="lane-head-main">
            <h2>{esc(lane_name)}</h2>
            <p class="lane-meta">{esc(tagline)}</p>
          </div>
        </div>
        <div class="p-grid">
{cards}
        </div>
      </section>""")

    body = f"""
  <main>
    <section class="page-head">
      <div class="wrap">
        <nav class="crumbs" aria-label="Вы здесь"><a href="index.html">Главная</a>
          <span aria-hidden="true">/</span> <span>Забутовочный кирпич</span></nav>
        <h1>Забутовочный кирпич</h1>
        <p class="page-sub">Рабочий кирпич, который прячется под облицовкой
          и штукатуркой. Главное в нём — марка прочности, а не красота.
          {n} видов, с заводов Юга.</p>
      </div>
    </section>

    <section class="pick-bar" aria-label="Подбор по задаче">
      <div class="wrap">
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
        f"Забутовочный (рабочий) кирпич в Краснодаре: {n} видов под фундамент, "
        "стены и перегородки. Доставка на объект, оплата при получении.",
        body, js)
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
    size = sp.get("Габариты", "").replace(" см", "").replace("х", "×").strip()
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
        w = w.replace("-", "–")
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
        disp_name, disp_meta, _tasks = RAB_VIEW[p["id"]]
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
        if (main.src === src) return;
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
        disp_name, disp_meta, _tasks = RAB_VIEW[p["id"]]
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
                f'<button class="pd-thumb{on}" type="button" data-src="{root}{src}?v=4" '
                f'aria-pressed="{pressed}" aria-label="Фото {i + 1}">'
                f'<img src="{root}{src}?v=4" alt="" width="640" height="480" loading="lazy"></button>')
        thumbs = f'\n      <div class="pd-thumbs">{"".join(btns)}</div>'

    if p["_thumb"]:
        photo = (f'<div class="pd-main-wrap" id="pdMainWrap">'
                 f'<img class="pd-main" id="pdMain" src="{root}{p["_gallery"][0]}?v=4" '
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

    # цена: базовая + цены форматов, либо «по запросу»
    if p.get("price"):
        price_html = f'<p class="pd-price">{rub(p["price"])} ₽<span class="pd-price-unit">/шт</span></p>'
        fmts = p.get("formats_prices") or {}
        fmt_lines = []
        for f_name, f_price in fmts.items():
            if f_name == p["format"]:
                continue  # базовый формат уже показан большой ценой
            short = FMT_SHORT.get(f_name, f_name)
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
      <div class="p-grid">
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
        ld["image"] = f"img/catalog/{p['id']}.jpg"
    if p.get("price"):
        ld["offers"] = {"@type": "Offer", "priceCurrency": "RUB",
                        "price": p["price"],
                        "availability": "https://schema.org/InStock"}
    extra_head = ('\n  <script type="application/ld+json">'
                  + json.dumps(ld, ensure_ascii=False) + "</script>")

    price_str = f"{rub(p['price'])} ₽/шт" if p.get("price") else "цена по запросу"
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
        if p["id"] in RAB_SKIP:
            continue
        build_brick_product(p, is_rab=True)
        n += 1
    print(f"tovar/kirpich-*.html: {n} страниц")


if __name__ == "__main__":
    build_category()
    for slug in COLL_ORDER:
        build_collection(slug)
    build_zabutovka()
    build_brick_products()
