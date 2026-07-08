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

BASE = Path("/Users/dm/Desktop/сайт")
DATA = json.loads((BASE / "data" / "catalog.json").read_text())

COLOR_ORDER = ["красный", "коричневый", "персиковый", "бежевый", "серый",
               "графит", "микс (бавария)", "зелёный", "разное"]
SWATCH_CLASS = {
    "красный": "sw-krasny", "коричневый": "sw-korichnevy",
    "персиковый": "sw-persik", "бежевый": "sw-bezh", "серый": "sw-sery",
    "графит": "sw-grafit", "микс (бавария)": "sw-miks", "зелёный": "sw-zeleny",
}

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
        "tagline": "Проверенная середина: дом, забор и цоколь из одной коллекции.",
    },
    "evropa": {
        "name": "Европа",
        "tagline": "Фактуры под старину — кроста, антик, руст. Для фасадов с характером.",
    },
    "formovka": {
        "name": "Ручная формовка",
        "tagline": "Премиум-кирпич: у каждого свой рисунок, как у кирпича столетней кладки.",
    },
}
COLL_ORDER = ["ekonom", "palitra", "klassika", "evropa", "formovka"]

FMT_SHORT = {
    "1НФ (одинарный)": "1НФ", "1,4НФ (полуторный)": "1,4НФ",
    "0,7НФ (евро)": "0,7НФ", "0,9НФ": "0,9НФ",
    "Ригель MF": "ригель", "Лонг LF": "лонг", "WDF": "WDF", "WMF": "WMF",
}

PRODUCTS = [p for p in DATA["products"] if p["category"] == "oblitsovochnyy"]
for p in PRODUCTS:
    p["_thumb"] = (BASE / "img" / "catalog" / f"{p['id']}.jpg").exists()


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


def card(p, feat_hidden=None):
    """feat_hidden: None — всегда видна (страница коллекции);
    True/False — категория, hidden если не featured."""
    alt = f"Кирпич «{p['name']}» — {p['color_group']}, {p['texture']}"
    if p["_thumb"]:
        img = (f'<img class="p-img" src="img/catalog/{p["id"]}.jpg?v=2" alt="{esc(alt)}" '
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
        price = '<a class="p-ask" href="index.html#lead">Узнать цену</a>'
    hidden = " hidden" if feat_hidden else ""
    fmt = FMT_SHORT.get(p["format"], p["format"])
    return (f'<article class="p-card" data-color="{esc(p["color_group"])}" '
            f'data-texture="{esc(p["texture"])}" data-format="{esc(fmt)}"{hidden}>'
            f'{img}<h3 class="p-name">{esc(p["name"])}</h3>'
            f'<p class="p-meta">{esc(p["texture"])} · {esc(fmt)}</p>{price}</article>')


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


# Липкая полоса связи (виден только на телефоне).
# TODO перед запуском: реальный номер и ссылки мессенджеров (wa.me/номер,
# t.me/имя_аккаунта, max.ru/имя_аккаунта).
CALLBAR = """
  <nav class="callbar" aria-label="Быстрая связь">
    <a class="callbar-item callbar-tel" href="tel:+79000000000">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
      <span>Позвонить</span></a>
    <a class="callbar-item" href="https://wa.me/79000000000?text=%D0%97%D0%B4%D1%80%D0%B0%D0%B2%D1%81%D1%82%D0%B2%D1%83%D0%B9%D1%82%D0%B5!%20%D0%9F%D0%B8%D1%88%D1%83%20%D1%81%20%D1%81%D0%B0%D0%B9%D1%82%D0%B0%20%D0%A1%D1%82%D1%80%D0%BE%D0%B9-%D0%A1%D0%B5%D0%B9%D0%BB" target="_blank" rel="noopener">
      <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z"/></svg>
      <span>WhatsApp</span></a>
    <a class="callbar-item" href="https://t.me/stroy_sale" target="_blank" rel="noopener">
      <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>
      <span>Telegram</span></a>
    <a class="callbar-item" href="https://max.ru/stroy_sale" target="_blank" rel="noopener">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/></svg>
      <span>MAX</span></a>
  </nav>"""


def page_shell(title, descr, body, extra_js=""):
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
  <link rel="stylesheet" href="styles.css?v=3">
</head>
<body>

  <header class="masthead">
    <div class="wrap masthead-in">
      <a class="wordmark" href="index.html">
        <strong>СТРОЙ-СЕЙЛ</strong>
        <span>Стройматериалы · Краснодар</span>
      </a>
      <nav class="masthead-nav" aria-label="Основное меню">
        <a href="index.html#catalog">Каталог</a>
        <a href="index.html#order">Доставка и оплата</a>
        <a href="index.html#lead">Контакты</a>
      </nav>
      <div class="masthead-contact">
        <a href="tel:+79000000000">+7 (900) 000-00-00</a>
        <small>Перезвоним за 5 минут</small>
      </div>
    </div>
  </header>

{body}

  <!-- Помощь с выбором -->
  <section class="section">
    <div class="wrap">
      <div class="cta-band">
        <div>
          <h2>Сомневаетесь, какой подойдёт?</h2>
          <p class="caption">Позвоните — подберём кирпич под вашу кровлю, цоколь
            и бюджет, посчитаем количество на дом.</p>
        </div>
        <div class="cta-band-btns">
          <a class="btn" href="tel:+79000000000">+7 (900) 000-00-00</a>
          <a class="btn btn-ghost" href="index.html#lead">Оставить заявку</a>
        </div>
      </div>
    </div>
  </section>

  <footer class="footer">
    <div class="wrap footer-in">
      <span class="tag">Строй-Сейл · Краснодар · 2026</span>
      <a href="tel:+79000000000">+7 (900) 000-00-00</a>
      <span class="caption">Работаем с частными застройщиками, прорабами и бригадами</span>
      <a class="footer-policy caption" href="policy.html">Политика конфиденциальности</a>
    </div>
  </footer>
{CALLBAR}
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
    swatches = ['<button class="swatch is-on" data-color="" aria-pressed="true">'
                '<span class="swatch-dot sw-all" aria-hidden="true"></span>'
                '<span class="swatch-name">Все цвета</span></button>']
    for color in COLOR_ORDER:
        if color not in SWATCH_CLASS or not color_counts.get(color):
            continue
        swatches.append(
            f'<button class="swatch" data-color="{esc(color)}" aria-pressed="false">'
            f'<span class="swatch-dot {SWATCH_CLASS[color]}" aria-hidden="true"></span>'
            f'<span class="swatch-name">{esc(color)}</span>'
            f'<span class="swatch-n">{color_counts[color]}</span></button>')

    lanes = []
    for slug in COLL_ORDER:
        items, lo = coll_stats(slug)
        meta = COLLECTIONS[slug]
        featured = pick_featured(items)
        feat_ids = {p["id"] for p in featured}
        items_sorted = sorted(items, key=sort_key)
        cards = "\n".join(card(p, feat_hidden=(p["id"] not in feat_ids))
                          for p in items_sorted)
        n = len(items)
        kinds = plural(n, "вид", "вида", "видов")
        price_note = f"от {rub(lo)} ₽/шт" if lo else "цена по запросу"
        btn_label = f"Вся коллекция — {n} {kinds}"
        lanes.append(f"""
      <section class="lane" data-page="collection-{slug}.html" aria-label="Коллекция «{esc(meta['name'])}»">
        <div class="lane-head">
          <div>
            <h2>Коллекция «{esc(meta['name'])}»</h2>
            <p class="caption lane-tag">{esc(meta['tagline'])}</p>
          </div>
          <p class="lane-price">{price_note}</p>
        </div>
        <div class="p-grid">
{cards}
        </div>
        <a class="btn btn-ghost lane-btn" href="collection-{slug}.html" data-label="{esc(btn_label)}">{esc(btn_label)}</a>
      </section>""")

    body = f"""
  <main>
    <section class="page-head">
      <div class="wrap">
        <nav class="crumbs" aria-label="Вы здесь"><a href="index.html">Главная</a>
          <span aria-hidden="true">/</span> <span>Облицовочный кирпич</span></nav>
        <h1>Облицовочный кирпич</h1>
        <p class="page-sub">{total} видов · 5 коллекций · от {rub(all_min)} ₽ за штуку.
          Привозим на объект по Краснодару и краю, оплата при получении.</p>
      </div>
    </section>

    <section class="section pick" aria-label="Подбор по цвету">
      <div class="wrap">
        <div class="section-head">
          <span class="tag">Подбор по цвету</span>
          <h2>Каким будет ваш дом?</h2>
          <p class="caption pick-hint">Выберите цвет — покажем всё, что есть,
            по коллекциям от эконома до премиума. Стили съёмки в коллекциях разные —
            поэтому не смешиваем их в одну витрину.</p>
        </div>
        <div class="swatches" role="group" aria-label="Цвета кирпича">
{chr(10).join(swatches)}
        </div>
        <p class="caption pick-note" id="pickNote" aria-live="polite"></p>
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
            <div class="line-calc-group">
              <span class="line-calc-label">Стены, м²</span>
              <div class="line-calc-input-wrap">
                <input class="line-calc-input" id="cWall" type="number" min="0" step="1" inputmode="decimal" placeholder="120">
              </div>
            </div>
            <div class="line-calc-divider"></div>
            <div class="line-calc-group">
              <span class="line-calc-label">Окна/двери, м²</span>
              <div class="line-calc-input-wrap">
                <input class="line-calc-input" id="cOpen" type="number" min="0" step="1" inputmode="decimal" placeholder="18">
              </div>
            </div>
            <div class="line-calc-divider"></div>
            <div class="line-calc-group">
              <span class="line-calc-label">Формат</span>
              <select id="cFmt">
                <option value="51.4">1НФ одинарный</option>
                <option value="51.4">0,7НФ евро</option>
                <option value="39.2">1,4НФ полуторный</option>
              </select>
            </div>
            <div class="line-calc-divider"></div>
            <div class="line-calc-block">
              <span class="line-calc-sub">Понадобится:</span>
              <strong class="line-calc-val val-accent" id="calcQty">—</strong>
            </div>
            <div class="line-calc-divider"></div>
            <a class="line-calc-btn btn" href="index.html#lead">
              Получить точный расчёт
            </a>
          </div>
        </div>
      </div>
    </section>
  </main>"""

    js = """
  <script>
    // Подбор по цвету: карточки уже в разметке, фильтруем показом/скрытием.
    // Результаты всегда группами по коллекциям — стили фото не смешиваем.
    var LIMIT = 8;
    var swatches = Array.prototype.slice.call(document.querySelectorAll('.swatch'));
    var lanes = Array.prototype.slice.call(document.querySelectorAll('.lane'));
    var note = document.getElementById('pickNote');

    function plural(n, one, few, many) {
      var m10 = n % 10, m100 = n % 100;
      if (m10 === 1 && m100 !== 11) return one;
      if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
      return many;
    }

    function apply(color) {
      var total = 0;
      lanes.forEach(function (lane) {
        var cards = Array.prototype.slice.call(lane.querySelectorAll('.p-card'));
        var btn = lane.querySelector('.lane-btn');
        var shown = 0, match = 0;
        cards.forEach(function (c) {
          if (!color) {
            c.hidden = c.dataset.feat === '0';
          } else {
            var ok = c.dataset.color === color;
            if (ok) match++;
            var show = ok && shown < LIMIT;
            c.hidden = !show;
            if (show) shown++;
          }
        });
        if (!color) {
          lane.hidden = false;
          btn.textContent = btn.dataset.label;
          btn.href = lane.dataset.page;
        } else {
          lane.hidden = match === 0;
          total += match;
          if (match > shown) {
            var rest = match - shown;
            btn.textContent = 'Ещё ' + rest + ' — в коллекции';
          } else {
            btn.textContent = btn.dataset.label;
          }
          btn.href = lane.dataset.page + '?color=' + encodeURIComponent(color);
        }
      });
      note.textContent = color
        ? 'Нашлось ' + total + ' ' + plural(total, 'вид', 'вида', 'видов') + ' — «' + color + '», по коллекциям:'
        : '';
    }

    // featured-карточки помечаем по стартовому состоянию разметки
    lanes.forEach(function (lane) {
      Array.prototype.slice.call(lane.querySelectorAll('.p-card')).forEach(function (c) {
        c.dataset.feat = c.hidden ? '0' : '1';
      });
    });

    swatches.forEach(function (s) {
      s.addEventListener('click', function () {
        swatches.forEach(function (x) {
          x.classList.toggle('is-on', x === s);
          x.setAttribute('aria-pressed', x === s ? 'true' : 'false');
        });
        apply(s.dataset.color);
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
        <p class="lane-price">{n} {kinds} · {price_note}</p>
      </div>
    </section>

    <section class="section coll" aria-label="Товары коллекции">
      <div class="wrap">
        <div class="filters">
{chr(10).join(filters)}
        </div>
        <p class="caption pick-note" id="countNote" aria-live="polite"></p>
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
    var chips = Array.prototype.slice.call(document.querySelectorAll('.chip'));
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
    p["_thumb"] = (BASE / "img" / "catalog" / f"{p['id']}.jpg").exists()

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
        img = (f'<img class="p-img" src="img/catalog/{p["id"]}.jpg?v=2" alt="{esc(alt)}" '
               f'width="640" height="480" loading="lazy">')
    else:
        img = ('<div class="p-img p-none" role="img" aria-label="Фото готовим">'
               '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
               'stroke-width="1.5" stroke-linecap="round" aria-hidden="true">'
               '<rect x="3" y="8" width="18" height="9"/>'
               '<path d="M7 11h.01M12 11h.01M17 11h.01"/></svg>'
               '<span>Фото пришлём по запросу</span></div>')
    return (f'<article class="p-card" data-task="{" ".join(tasks)}">'
            f'{img}<h3 class="p-name">{esc(name)}</h3>'
            f'<p class="p-meta">{esc(meta)}</p>'
            f'<a class="p-ask" href="index.html#lead">Узнать цену</a></article>')


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
          <div>
            <h2>{esc(lane_name)}</h2>
            <p class="caption lane-tag">{esc(tagline)}</p>
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

    <section class="section pick" aria-label="Подбор по задаче">
      <div class="wrap">
        <div class="section-head">
          <span class="tag">Подбор по задаче</span>
          <h2>Что будете строить?</h2>
          <p class="caption pick-hint">Выберите задачу — покажем кирпич,
            который для неё подходит по марке и структуре.</p>
        </div>
        <div class="filter-chips" role="group" aria-label="Задачи">
{chr(10).join(chips)}
        </div>
        <p class="caption pick-note" id="pickNote" aria-live="polite"></p>
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


if __name__ == "__main__":
    build_category()
    for slug in COLL_ORDER:
        build_collection(slug)
    build_zabutovka()
