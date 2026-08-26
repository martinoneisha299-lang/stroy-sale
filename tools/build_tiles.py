"""
Тротуарная плитка: витрина категории, страницы форм, товары и бордюры.

Собирает:
    trotuarnaya-plitka.html        — витрина всех расцветок с фильтрами
    plitka-<форма>.html × 7        — та же витрина внутри одной формы
    tovar/<форма>-<цвет>.html ×172 — страницы товара
    tovar/bordur-1.html, bordur-2.html — бордюры к плитке

Данные: _data/tiles.json (готовит tools/parse_tiles.py).
Фотографии: img/catalog/tile-*.jpg и tile-*-2/-3.jpg (готовит
tools/build_tile_images.py) — наличие проверяется по диску, а не по списку
в json; обложки форм, работы и видео — img/plitka/.

Поставщик один, поэтому коллекций у плитки нет: подкатегория — это ФОРМА
(«Новый город», «Брусчатка»), а цвет выбирают внутри неё или общим фильтром.

Оболочка, карточка и фильтры — общие модули shell_common и catalog_common;
здесь только то, что специфично для плитки.
"""

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_common import (fgroup, filters_drawer, filters_panel, fprice,
                            grid_shell, toolbar)
from shell_common import (BASE, ICON, PHONE_HREF, SITE_URL, TERMS_STOCK,
                          crumbs_html, esc, grid_cls, page_shell, plural,
                          price_split, product_card, rub, spec_dd, wa_link,
                          write_page)

DATA = json.loads((BASE / "_data" / "tiles.json").read_text())
CAT_IMG = BASE / "img" / "catalog"
IMG_V = 5          # версия кэша фотографий плитки

PRODUCTS = DATA["products"]
SHAPES = DATA["shapes"]
BORDERS = DATA["borders"]

# Отгрузка и расчёт — цифры из спеков завода, они одинаковы для всей плитки
PALLET_M2 = 15     # м² в поддоне
SPARE = 5          # % запаса на подрезку
CALC_AREA = 78     # площадь для примера в калькуляторе (обычный двор с дорожками)

# Порядок форм на витрине: сначала то, что берут чаще, дальше — крупный формат
SHAPE_ORDER = ["novyy-gorod", "staryy-gorod", "bruschatka", "pryamougolnik",
               "myunhen", "parket", "asgard"]

# Короткое «зачем эта форма» — читается под именем в плитке раздела
SHAPE_NOTE = {
    "novyy-gorod": "Три размера в одной раскладке — выбирают чаще всего",
    "staryy-gorod": "Рисунок старой мостовой, мягкая фаска",
    "bruschatka": "Классический «кирпичик» — дорожки и площадки",
    "pryamougolnik": "Строгая сетка — современные дворы",
    "myunhen": "Крупный модуль, меньше швов",
    "parket": "Узкая доска — укладка «ёлочкой»",
    "asgard": "Крупный формат, парадные площадки",
}

# «Применение» — на странице товара, простым языком, без укладочного жаргона
SHAPE_USE = {
    "novyy-gorod": "дорожки, двор и отмостка вокруг дома; три размера "
                   "в раскладке прощают подрезку у стен и клумб",
    "staryy-gorod": "дорожки и площадки «под старину» — к кирпичному дому "
                    "и саду; фаска не задерживает грязь в швах",
    "bruschatka": "садовые дорожки и площадки у дома; классический "
                  "«кирпичик» кладётся любым рисунком — ёлочкой, плетёнкой",
    "pryamougolnik": "современные дворы со строгой сеткой швов; хорошо "
                     "смотрится с газоном и бетонной архитектурой",
    "myunhen": "просторные дворы и зоны отдыха; крупный модуль укладывается "
               "быстрее мелкой плитки, швов меньше",
    "parket": "акцентные зоны — вход, терраса, патио; узкая доска ёлочкой "
              "смотрится как паркет под открытым небом",
    "asgard": "парадные площадки и зона у входа; самый крупный формат "
              "каталога, минимум швов",
}

# Что люди набирают в поиске — ссылки внизу витрины (приём Лемана и ВИ)
OFTEN = [("Плитка «Старый город»", "shape=staryy-gorod"),
         ("Брусчатка", "shape=bruschatka"),
         ("Плитка ёлочкой — «Паркет»", "shape=parket"),
         ("Однотонная плитка", "kind=mono"),
         ("Колормиксы", "kind=mix"),
         ("Плитка до 700 ₽/м²", "max=700"),
         ("Сначала недорогие", "sort=cheap")]

# У плитки нет ни новинок, ни коллекций — сортировку по новизне не показываем:
# кнопка без данных за ней сортировала бы «как получится».
SORTS = [("default", "По каталогу"), ("cheap", "Сначала дешевле"),
         ("exp", "Сначала дороже")]


# ---------------------------------------------------------------------------
# Подготовка
# ---------------------------------------------------------------------------
def _gallery(p):
    """Файлы галереи, которые РЕАЛЬНО лежат на диске (список в json бывает старым)."""
    out = []
    if (CAT_IMG / f"{p['id']}.jpg").exists():
        out.append(f"img/catalog/{p['id']}.jpg")
    for i in (2, 3):
        if (CAT_IMG / f"{p['id']}-{i}.jpg").exists():
            out.append(f"img/catalog/{p['id']}-{i}.jpg")
    return out


for _p in PRODUCTS:
    _p["_gal"] = _gallery(_p)
    _p["_url"] = f"tovar/{_p['slug']}.html"

ALL_MIN = min(p["price"] for p in PRODUCTS if p["price"])
ALL_MAX = max(p["price"] for p in PRODUCTS if p["price"])

# Расцветок в каталоге — 32, а позиций 172: одна расцветка идёт в семи формах.
# Число позиций «расцветками» называть нельзя — покупатель считает цвета.
ALL_COLORS = len({p["name"] for p in PRODUCTS})


def kind_of(p):
    return "mono" if p["mono"] else "mix"


def kind_ru(p):
    return "однотонная" if p["mono"] else "колормикс"


def shape_name(slug):
    return SHAPES[slug]["name"]


def nice_name(p):
    """«Плитка «Агат коричневый», Новый город» — имя цвета одно на семь форм,
    поэтому форма обязана стоять в названии: иначе в общей выдаче семь
    одинаковых «Агатов» подряд.

    Имя расцветки в кавычках: без них прилагательное сталкивается с родом
    («Плитка Оранжевый, Асгард»), а имена с уточнением («Хаски — Мрамор»)
    приносят в строку второе тире."""
    return f"Плитка «{p['name']}», {shape_name(p['shape'])}"


def alt_of(p):
    return f"Тротуарная плитка «{p['name']}», форма «{shape_name(p['shape'])}»"


def price_html(p):
    if not p.get("price"):
        return ""
    return price_split(p["price"], "м²")


def pallet_text(p):
    """Вторая цена — поддон: плитку возят поддонами, метром её никто не берёт."""
    if not p.get("price"):
        return ""
    return f"поддон {PALLET_M2} м² ≈ {rub(p['price'] * PALLET_M2)} ₽"


def sort_key(p):
    """Форма → колормиксы раньше однотонных → цена → имя.
    Колормиксы первыми осознанно: за ними приходят, однотонные ищут ценой."""
    si = SHAPE_ORDER.index(p["shape"]) if p["shape"] in SHAPE_ORDER else 99
    return (si, p["mono"], p["price"] or 0, p["name"])


def card_of(p, root="", eager=False, with_shape=True):
    img = f"{p['_gal'][0]}?v={IMG_V}" if p["_gal"] else None
    data = (f' data-shape="{esc(p["shape"])}"'
            f' data-kind="{kind_of(p)}"'
            f' data-price="{p.get("price") or ""}"')
    # Кнопка заявки есть и без цены — позиция уходит в тот же список
    add = {"id": p["id"], "name": nice_name(p), "price": p.get("price"), "unit": "м²",
           "img": p["_gal"][0] if p["_gal"] else ""}
    gal_urls = [f"{g}?v={IMG_V}" for g in p["_gal"]] if p.get("_gal") else None
    return product_card(
        href=p["_url"], name=nice_name(p) if with_shape else f"Плитка «{p['name']}»",
        img=img, alt=alt_of(p), price_html=price_html(p), m2=pallet_text(p),
        meta=shape_name(p["shape"]) if not with_shape else kind_ru(p),
        stock="Поставка с завода" if p.get("price") else "Под заказ",
        shots=len(p["_gal"]), gallery=gal_urls, data=data, root=root, add=add, eager=eager)


def border_card(b, root=""):
    """Бордюр в сетке. Фото снято на белом холсте целиком — обрезать его
    в квадрат нельзя, поэтому вписываем (img_contain)."""
    note = ("К дорожкам и парковкам — держит край мощения"
            if "дорожн" in b["name"].lower() else
            "К садовым дорожкам и клумбам")
    return product_card(
        href=f"tovar/{b['id']}.html", name=b["name"],
        img=f"img/catalog/{b['id']}.jpg?v={IMG_V}", alt=f"{b['name']} к тротуарной плитке",
        price_html=price_split(b["price"], "шт"),
        m2=note, root=root, img_contain=True, stock="Поставка с завода",
        add={"id": b["id"], "name": b["name"], "price": b["price"], "unit": "шт",
             "img": f"img/catalog/{b['id']}.jpg"})


# ---------------------------------------------------------------------------
# Фильтры и плитки форм
# ---------------------------------------------------------------------------
def tile_filters(items, *, with_shape=True):
    prices = [p["price"] for p in items if p.get("price")]
    groups = [fprice(rub(min(prices)) if prices else "0",
                     rub(max(prices)) if prices else "0", unit="₽/м²")]
    if with_shape:
        # Кружков-образцов у формы нет: мини-фото под свотч (cdot-*) build_tile_images
        # не делает, а обложка формы 600×600 в кружке 26px — это лишние 120 КБ.
        shapes = [(s, shape_name(s), sum(1 for p in items if p["shape"] == s))
                  for s in SHAPE_ORDER if any(p["shape"] == s for p in items)]
        groups.append(fgroup("Форма", "shape", shapes))
    kinds = [(k, t, sum(1 for p in items if kind_of(p) == k))
             for k, t in (("mix", "Колормикс"), ("mono", "Однотонная"))]
    groups.append(fgroup("Тип окраски", "kind", [k for k in kinds if k[2]]))
    return filters_panel("".join(groups))


def shape_tiles(active=None, *, borders_href="#borders"):
    """Плитки форм над выдачей — подкатегории, как у больших магазинов.
    Восьмая плитка — бордюры: без неё в сетке 4×2 зияет пустой слот.
    borders_href: на витрине категории секция бордюров своя (якорь),
    с остальных страниц ведём на неё же полной ссылкой."""
    out = []
    for slug in SHAPE_ORDER:
        m = SHAPES[slug]
        n = sum(1 for p in PRODUCTS if p["shape"] == slug)
        note = (f"{n} {plural(n, 'расцветка', 'расцветки', 'расцветок')}"
                f" · от {rub(m['min_price'])} ₽/м²")
        on = ' aria-current="page"' if slug == active else ""
        # Вторая строка — «зачем эта форма»: по одним именам («Мюнхен», «Асгард»)
        # покупатель, который выбирает плитку впервые, разницы не видит.
        out.append(f'<a class="tile" href="plitka-{slug}.html"{on}>'
                   f'<strong>{esc(m["name"])}<span>{esc(note)}</span>'
                   f'<span>{esc(SHAPE_NOTE[slug])}</span></strong>'
                   f'<img src="img/plitka/shape-{slug}.jpg" alt="" width="320" height="240" '
                   f'loading="lazy"></a>')
    b_min = min(b["price"] for b in BORDERS)
    out.append(f'<a class="tile" href="{borders_href}">'
               f'<strong>Бордюры<span>Дорожный и садовый · от {rub(b_min)} ₽/шт</span></strong>'
               f'<img src="img/plitka/shape-bordur.jpg" alt="" width="320" height="240" '
               f'loading="lazy"></a>')
    return f'<div class="tiles">{"".join(out)}</div>'


def often_html():
    links = "".join(f'<a class="chip" href="trotuarnaya-plitka.html?{q}">{esc(t)}</a>'
                    for t, q in OFTEN)
    return (f'<div class="section"><div class="wrap"><h2 class="section-head">Часто ищут</h2>'
            f'<div class="applied">{links}</div></div></div>')


# ---------------------------------------------------------------------------
# Калькулятор
#
# Площадь → метры с запасом → поддоны → деньги.
#
# Цифры примера считаются ЗДЕСЬ и печатаются в разметку: пока живого пересчёта
# нет, посетитель видит нормальный расчёт, а не прочерки. Пересчёт при вводе
# должен делать общий app.js — в нём модуля калькулятора ПОКА НЕТ (в новом
# styles.css раздел 12 уже есть, разметка под него). Хуки для модуля:
#   блок `.calc[data-calc]` с data-price / data-pallet / data-spare / data-area,
#   поля #calcArea и #calcShape (у опции формы своя data-price),
#   выводы #calcM2, #calcPallets, #calcSum.
# Тот же набор нужен калькулятору кровли — модуль стоит писать общим.
# ---------------------------------------------------------------------------
def calc_numbers(area, price):
    need = area * (1 + SPARE / 100)
    m2 = math.ceil(need)
    pallets = math.ceil(need / PALLET_M2)
    return m2, pallets, m2 * price


def calc_block(*, price, note, shape_pick=False):
    m2, pallets, total = calc_numbers(CALC_AREA, price)

    pick = ""
    if shape_pick:
        # В подписи опции только имя формы: поле узкое (max-width 12rem),
        # «Прямоугольник — от 650 ₽/м²» обрезается многоточием прямо в списке.
        opts = "".join(
            f'<option value="{s}" data-price="{SHAPES[s]["min_price"]}">'
            f'{esc(SHAPES[s]["name"])}</option>' for s in SHAPE_ORDER)
        pick = (f'<div class="calc-row"><label for="calcShape">Форма плитки</label>'
                f'<span class="calc-val"><select id="calcShape">{opts}</select></span></div>')

    return f"""
  <section class="section" id="calc"><div class="wrap">
    <div class="calc" data-calc data-price="{price}" data-pallet="{PALLET_M2}"
         data-spare="{SPARE}" data-area="{CALC_AREA}">
      <h2>Расчёт количества плитки</h2>
      <p class="calc-sub">Введите площадь двора и дорожек — калькулятор посчитает
        метры с запасом, число поддонов и примерную стоимость.</p>
      <div class="calc-rows">
        <div class="calc-row">
          <label for="calcArea">Площадь мощения, м²</label>
          <span class="calc-val"><input id="calcArea" type="number" inputmode="decimal"
            min="1" max="10000" step="1" value="{CALC_AREA}" aria-describedby="calcNote"></span>
        </div>
        {pick}
        <div class="calc-row">
          <span class="calc-key">С запасом {SPARE} % на подрезку</span>
          <span class="calc-val" id="calcM2">{m2} м²</span>
        </div>
        <div class="calc-row">
          <span class="calc-key">Поддонов по {PALLET_M2} м²</span>
          <span class="calc-val" id="calcPallets">{pallets} {plural(pallets, "поддон", "поддона", "поддонов")}</span>
        </div>
      </div>
      <p class="calc-out"><span>Примерная стоимость</span>
        <b id="calcSum">{rub(total)} ₽</b></p>
      <a class="btn btn--accent btn--wide" href="#lead">Заказать расчёт</a>
      <p class="calc-note" id="calcNote">{esc(note)}</p>
    </div>
  </div></section>"""


# ---------------------------------------------------------------------------
# Витрина категории
# ---------------------------------------------------------------------------
def works_section():
    """Объекты и видео с производства: плитка — покупка «глазами».
    Кадры сняты не нами, поэтому подписи говорят о самой плитке, а не
    о «наших работах» — присваивать чужие объекты нельзя."""
    works = "".join(
        f'<img src="img/plitka/work-{i:02d}.jpg" alt="Двор и дорожки, мощённые '
        f'этой плиткой — объект {i}" width="800" height="600" loading="lazy">'
        for i in range(1, 11))
    return f"""
  <section class="section" id="works"><div class="wrap">
    <div class="section-head"><h2>Объекты из этой плитки</h2>
      <a class="see-all" href="raboty.html">Все объекты</a></div>
    <div class="works">{works}</div>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="section-head"><h2>Производство плитки</h2></div>
    <video controls preload="none" poster="img/plitka/works-video-poster.jpg"
           width="360" height="640">
      <source src="img/plitka/works-video.mp4" type="video/mp4">
    </video>
    <p class="note">Съёмка с производственной линии. Плитку формуют вибропрессом
      из полусухой смеси: она плотнее литой, с ровными гранями и одинаковым швом.
      Прочность плитка набирает на выдержке у завода — до отгрузки.</p>
  </div></section>"""


def build_category():
    items = sorted(PRODUCTS, key=sort_key)
    cards = "".join(card_of(p, eager=(i < 4)) for i, p in enumerate(items))
    b_cards = "".join(border_card(b) for b in BORDERS)

    body = f"""
  <section class="page-head"><div class="wrap">
    {crumbs_html([("Главная", "index.html"), ("Каталог", "index.html#catalog"),
                  ("Тротуарная плитка", None)])}
    <h1>Тротуарная плитка<span class="h1-n">{ALL_COLORS} {plural(ALL_COLORS, "расцветка", "расцветки", "расцветок")} в {len(SHAPES)} формах</span></h1>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="section-head"><h2>Формы плитки</h2></div>
    {shape_tiles()}
  </div></section>

  <section class="section"><div class="wrap">
    {toolbar(len(items), sorts=SORTS)}
    <div class="catalog-body">
      {tile_filters(items)}
      {grid_shell(cards)}
    </div>
  </div></section>

  <section class="section" id="borders"><div class="wrap">
    <div class="section-head"><h2>Бордюры к плитке</h2></div>
    <p class="page-sub">Держат край мощения: без бордюра дорожка со временем
      расползается, а край крошится. Количество бордюра менеджер посчитает
      по плану участка.</p>
    <div class="p-grid{grid_cls(len(BORDERS))}">{b_cards}</div>
  </div></section>
{calc_block(price=SHAPES[SHAPE_ORDER[0]]["min_price"], shape_pick=True,
            note=f"Пример для {CALC_AREA} м² по цене «от» выбранной формы: "
                 f"колормиксы дороже однотонных. Точную смету с раскладкой, "
                 f"бордюром и доставкой посчитает менеджер.")}
{works_section()}
{often_html()}
{filters_drawer()}
"""
    write_page(BASE / "trotuarnaya-plitka.html", page_shell(
        f"Тротуарная плитка в Краснодаре — {ALL_COLORS} "
        f"{plural(ALL_COLORS, 'расцветка', 'расцветки', 'расцветок')} "
        f"в {len(SHAPE_ORDER)} формах, цены от {rub(ALL_MIN)} ₽/м²",
        f"Тротуарная плитка напрямую с завода: {ALL_COLORS} "
        f"{plural(ALL_COLORS, 'расцветка', 'расцветки', 'расцветок')} "
        f"в {len(SHAPE_ORDER)} формах, толщина 40 мм, F200. Цены от {rub(ALL_MIN)} ₽/м². "
        f"Доставка по Краснодару и краю, наличный и безналичный расчёт.",
        body, active="plitka"))


# ---------------------------------------------------------------------------
# Витрина одной формы
# ---------------------------------------------------------------------------
def build_shape(slug):
    m = SHAPES[slug]
    items = sorted([p for p in PRODUCTS if p["shape"] == slug], key=sort_key)
    if not items:
        return
    cards = "".join(card_of(p, eager=(i < 4), with_shape=False)
                    for i, p in enumerate(items))
    lo = rub(m["min_price"])

    body = f"""
  <section class="page-head"><div class="wrap">
    {crumbs_html([("Главная", "index.html"),
                  ("Тротуарная плитка", "trotuarnaya-plitka.html"),
                  (m["name"], None)])}
    <h1>Плитка «{esc(m["name"])}»</h1>
    <p class="page-sub">{esc(SHAPE_NOTE[slug])}.</p>
  </div></section>

  <section class="section"><div class="wrap">
    {toolbar(len(items), sorts=SORTS)}
    <div class="catalog-body">
      {tile_filters(items, with_shape=False)}
      {grid_shell(cards)}
    </div>
  </div></section>
{calc_block(price=m["min_price"],
            note=f"Пример для {CALC_AREA} м² по цене «от» этой формы: "
                 f"у колормиксов цена выше. Точную смету с раскладкой, бордюром "
                 f"и доставкой посчитает менеджер.")}

  <section class="section"><div class="wrap">
    <div class="section-head"><h2>Другие формы</h2>
      <a class="see-all" href="trotuarnaya-plitka.html">Вся плитка</a></div>
    {shape_tiles(active=slug, borders_href="trotuarnaya-plitka.html#borders")}
  </div></section>
{filters_drawer()}
"""
    write_page(BASE / f"plitka-{slug}.html", page_shell(
        f"Плитка «{m['name']}» — {len(items)} "
        f"{plural(len(items), 'расцветка', 'расцветки', 'расцветок')} от {lo} ₽/м², Краснодар",
        f"Тротуарная плитка «{m['name']}»: {len(items)} "
        f"{plural(len(items), 'расцветка', 'расцветки', 'расцветок')}, 40 мм, F200, В30, "
        f"от {lo} ₽/м². Доставка по Краснодару и краю, наличный и безналичный расчёт.",
        body, active="plitka"))


def dotted_specs_html(p):
    """Таблица характеристик тротуарной плитки с точечными направляющими."""
    m = SHAPES[p["shape"]]
    is_mix = not p["mono"]
    color_type = "Колормикс (градиентный перелив)" if is_mix else "Однотонная (монохром)"

    main_specs = [
        ("Форма плитки", m["name"]),
        ("Тип окраски", color_type),
        ("Расцветка", p["name"]),
        ("Толщина плитки", "40 мм (пешеходная, двор, отмостка)"),
        ("Класс прочности бетона", "В30 (М400) на сжатие"),
        ("Морозостойкость", "F200 (200 циклов)"),
        ("Водопоглощение", "не более 5 %"),
        ("Истираемость", "не более 0,7 г/см²"),
        ("Технология", "Полусухое вибропрессование"),
        ("ГОСТ", "ГОСТ 17608-2017"),
    ]

    trans_specs = [
        ("Площадь на поддоне", f"{PALLET_M2} м²"),
        ("Вес 1 м²", "≈ 90 кг"),
        ("Вес одного поддона", "≈ 1 350 кг (1,35 т)"),
        ("Расход песка на подушку", "≈ 0,1 м³ на 1 м²"),
        ("Загрузка манипулятора (10 т)", "7–8 поддонов (105–120 м²)"),
        ("Загрузка шаланды (20 т)", "14–15 поддонов (210–225 м²)"),
    ]

    def render_list(items):
        out = ['<ul class="dotted-list">']
        for k, v in items:
            if not v:
                continue
            out.append(f'<li class="dotted-item"><span class="dotted-name">{esc(k)}</span><span class="dotted-leader"></span><span class="dotted-val">{esc(str(v))}</span></li>')
        out.append('</ul>')
        return "".join(out)

    return f"""
    <div class="pd-specs-sheet">
      <div class="pd-specs-col">
        <h3>Основные характеристики</h3>
        {render_list(main_specs)}
      </div>
      <div class="pd-specs-col">
        <h3>Транспортировка и упаковка</h3>
        {render_list(trans_specs)}
      </div>
    </div>
    """


def cross_sell_html(root="../"):
    return f"""
    <section class="pd-cross-section">
      <div class="wrap">
        <div class="section-head">
          <h2>Сопутствующие товары для укладки плитки</h2>
        </div>
        <div class="pd-cross-grid">
          <article class="pd-cross-card">
            <img class="pd-cross-img" src="{root}img/catalog/bordur-1.jpg?v={IMG_V}" alt="Бордюр садовый" loading="lazy">
            <h4 class="pd-cross-title">Бордюр садовый 1000×200×80 мм (серый, графит, коричневый)</h4>
            <p class="pd-cross-price">от 290 ₽ / шт</p>
            <a class="pd-cross-btn" href="{root}zayavka.html">Добавить к заказу</a>
          </article>
          <article class="pd-cross-card">
            <img class="pd-cross-img" src="{root}img/catalog/pal-006.jpg?v={IMG_V}" alt="Геотекстиль дорожный" loading="lazy">
            <h4 class="pd-cross-title">Геотекстиль дорожный иглопробивной плотность 150 г/м²</h4>
            <p class="pd-cross-price">48 ₽ / м²</p>
            <a class="pd-cross-btn" href="{root}zayavka.html">Добавить к заказу</a>
          </article>
          <article class="pd-cross-card">
            <img class="pd-cross-img" src="{root}img/catalog/pal-007.jpg?v={IMG_V}" alt="Гидрофобизатор для плитки" loading="lazy">
            <h4 class="pd-cross-title">Гидрофобизатор с эффектом «Мокрый камень» для защиты брусчатки 10 л</h4>
            <p class="pd-cross-price">2 450 ₽ / канистра</p>
            <a class="pd-cross-btn" href="{root}zayavka.html">Добавить к заказу</a>
          </article>
        </div>
      </div>
    </section>
    """


def similar(p, k=4):
    """Соседние расцветки той же формы: сначала того же типа окраски."""
    pool = [q for q in PRODUCTS if q["shape"] == p["shape"] and q["id"] != p["id"]]
    pool.sort(key=lambda q: (q["mono"] != p["mono"],
                             abs((q["price"] or 0) - (p["price"] or 0)), q["name"]))
    return pool[:k]


def cross_shapes(p):
    """Тот же цвет в других формах — вторая ось выбора после цвета."""
    out = [q for q in PRODUCTS if q["name"] == p["name"] and q["shape"] != p["shape"]]
    out.sort(key=lambda q: SHAPE_ORDER.index(q["shape"]))
    return out


def build_product(p):
    root = "../"
    name = nice_name(p)
    m = SHAPES[p["shape"]]
    has_price = bool(p.get("price"))

    price_m2 = float(p.get("price") or 0)
    price_pal = round(price_m2 * PALLET_M2, 2)
    deliv_price = round(price_m2 + 120.0, 2)

    # ---- Галерея
    zoom_btn = (f'<button class="pd-zoom-trigger" id="pdZoom" type="button" '
                f'aria-label="Открыть фото крупно">{ICON["zoom"]}</button>')
    badges = ('<div class="pd-badges-bar">'
              '<span class="pd-badge pd-badge--hit">Хит</span>'
              '<span class="pd-badge pd-badge--factory">С завода</span>'
              '<span class="pd-badge pd-badge--gost">ГОСТ 17608-2017</span>'
              '</div>')
    main_img = (f'<div class="pd-main-card">{badges}'
                f'<img class="pd-main-img" id="pdMain" src="{root}{p["_gal"][0]}?v={IMG_V}" '
                f'alt="{esc(alt_of(p))}" width="1200" height="900" fetchpriority="high">{zoom_btn}</div>')
    thumbs_html = ""
    if len(p["_gal"]) > 1:
        thumbs_html = '<div class="pd-thumbs-strip">' + "".join(
            f'<button class="pd-thumb-btn{" is-on" if i == 0 else ""}" type="button" '
            f'data-src="{root}{g}?v={IMG_V}" aria-label="Фото {i + 1}">'
            f'<img src="{root}{g}?v={IMG_V}" alt="" width="74" height="74" loading="lazy">'
            f'</button>' for i, g in enumerate(p["_gal"])) + "</div>"
    
    wa_text = f"Здравствуйте! Пришлите, пожалуйста, фото и видео образца: {name}"
    wa_strip = (f'<div class="pd-wa-request">{ICON["wa"]}'
                f'<span>Оттенок на экране может отличаться от партии. '
                f'<a href="{wa_link(wa_text)}" target="_blank" rel="noopener">'
                f'Запросить фото и видео образца в WhatsApp</a></span></div>')
    gallery_html = f'<div class="pd-gallery-wrap">{main_img}{thumbs_html}{wa_strip}</div>'

    # ---- Карточки преимуществ под галереей
    trust_html = f"""
    <div class="pd-trust-cards">
      <div class="pd-trust-card">
        {ICON["calc"]}
        <div>
          <b>Бесплатный расчёт</b>
          <span>Посчитаем квадратуру двора, дорожек и бордюров</span>
        </div>
      </div>
      <div class="pd-trust-card">
        {ICON["truck"]}
        <div>
          <b>Удобная доставка</b>
          <span>Манипулятор 5–10 т, бережная выгрузка на участке</span>
        </div>
      </div>
      <div class="pd-trust-card">
        {ICON["doc"]}
        <div>
          <b>Скидки от 5 поддонов</b>
          <span>Спецусловия при заказе от 75 м²</span>
        </div>
      </div>
    </div>
    """

    # ---- Buy Box
    sku_val = esc(p["id"]).upper()
    color_type = "Колормикс" if not p["mono"] else "Однотонная"

    unit_tabs_html = """
    <div class="pd-unit-bar">
      <span class="pd-unit-label">Цена за:</span>
      <div class="pd-unit-tabs">
        <button class="pd-unit-btn is-active" type="button" data-unit="m2">м²</button>
        <button class="pd-unit-btn" type="button" data-unit="pal">поддон</button>
      </div>
    </div>
    """

    if has_price:
        price_cards_html = f"""
        <div class="pd-price-cards">
          <label class="pd-price-card is-selected" data-price-pcs="{price_m2}">
            <div class="pd-price-card-left">
              <input type="radio" name="priceRate" checked>
              <div>
                <span class="pd-price-card-title">Цена завода</span>
                <span class="pd-price-card-sub">Самовывоз или прямая отгрузка</span>
              </div>
            </div>
            <div class="pd-price-card-val">
              <b>{rub(price_m2)} ₽</b>
              <small>за 1 м²</small>
            </div>
          </label>
          <label class="pd-price-card" data-price-pcs="{deliv_price}">
            <div class="pd-price-card-left">
              <input type="radio" name="priceRate">
              <div>
                <span class="pd-price-card-title">С доставкой по Краснодару</span>
                <span class="pd-price-card-sub">Включая выгрузку манипулятором</span>
              </div>
            </div>
            <div class="pd-price-card-val">
              <b>~{rub(deliv_price)} ₽</b>
              <small>за 1 м²</small>
            </div>
          </label>
        </div>
        """
        initial_sum = rub(price_pal)
        total_html = f"""
        <div class="pd-total-summary">
          <span class="pd-total-summary-label">Итого на сумму:</span>
          <div class="pd-total-summary-val">
            <b>{initial_sum} ₽</b>
            <small>({PALLET_M2} м² · 1 поддон)</small>
          </div>
        </div>
        """
        action_btn = (f'<button class="pd-btn-main" type="button" data-add '
                      f'data-id="{esc(p["id"])}" data-name="{esc(name)}" data-price="{price_m2}" '
                      f'data-qty="{PALLET_M2}" data-unit="м²" data-img="{esc(p["_gal"][0] if p["_gal"] else "")}" '
                      f'data-url="{esc(p["_url"])}" data-root="{root}">'
                      f'{ICON["cart"]}<span>В заявку</span></button>')
    else:
        price_cards_html = """
        <div class="pd-price-cards">
          <div class="pd-price-card is-selected" style="cursor:default">
            <div>
              <span class="pd-price-card-title">Цена по запросу</span>
              <span class="pd-price-card-sub">Подтверждаем при заказе от объёма</span>
            </div>
            <div class="pd-price-card-val">
              <b>по запросу</b>
            </div>
          </div>
        </div>
        """
        total_html = ""
        action_btn = (f'<button class="pd-btn-main" type="button" data-add '
                      f'data-id="{esc(p["id"])}" data-name="{esc(name)}" data-price="" '
                      f'data-qty="{PALLET_M2}" data-unit="м²" data-img="{esc(p["_gal"][0] if p["_gal"] else "")}" '
                      f'data-url="{esc(p["_url"])}" data-root="{root}">'
                      f'{ICON["cart"]}<span>В заявку</span></button>')

    buybox_html = f"""
    <div class="pd-buybox" data-price="{price_m2}" data-per-m2="1" data-pallet="{PALLET_M2}" data-name="{esc(name)}">
      <div class="pd-box-meta">
        <span class="pd-sku">Артикул: {sku_val}</span>
        <span class="pd-stock-badge">В наличии на складе</span>
      </div>

      <dl class="pd-mini-specs">
        <dt>Форма:</dt><dd><a href="{root}plitka-{p['shape']}.html">{esc(m["name"])}</a></dd>
        <dt>Расцветка / Тип:</dt><dd>{esc(p["name"])} ({color_type})</dd>
        <dt>Толщина / Класс:</dt><dd>40 мм · Класс бетона В30 (F200)</dd>
      </dl>

      {unit_tabs_html if has_price else ""}
      {price_cards_html}

      <div class="pd-order-controls">
        <div class="pd-stepper-row">
          <div class="pd-qty-stepper">
            <button type="button" data-step="-{PALLET_M2}" aria-label="Меньше">−</button>
            <input type="text" inputmode="numeric" value="{PALLET_M2}" aria-label="Количество, м²">
            <button type="button" data-step="{PALLET_M2}" aria-label="Больше">+</button>
          </div>
          <div class="pd-pallet-hint">
            <b>кратно поддону {PALLET_M2} м²</b>
            <div>1 поддон ≈ 1 350 кг (~1,35 т)</div>
          </div>
        </div>

        <div class="pd-presets-row">
          <button class="pd-preset-chip" type="button" data-add-pallet="1">+1 поддон ({PALLET_M2} м²)</button>
          <button class="pd-preset-chip" type="button" data-add-pallet="3">+3 поддона ({PALLET_M2 * 3} м²)</button>
          <button class="pd-preset-chip" type="button" data-add-pallet="10">+10 поддонов ({PALLET_M2 * 10} м²)</button>
        </div>

        {total_html}
        {action_btn}

        <div class="pd-fast-actions">
          <a class="pd-fast-btn pd-fast-btn--wa" href="{wa_link('Здравствуйте! Хочу уточнить наличие и расчет плитки: ' + name)}" target="_blank" rel="noopener">
            {ICON["wa"]}<span>В WhatsApp</span>
          </a>
          <a class="pd-fast-btn pd-fast-btn--call" href="{PHONE_HREF}">
            {ICON["phone"]}<span>Позвонить</span>
          </a>
        </div>

        <div class="pd-oneclick-wrap">
          <div class="pd-oneclick-title">Купить в 1 клик без оформления</div>
          <form class="pd-oneclick-form" novalidate>
            <input class="pd-oneclick-input" type="tel" placeholder="+7 (___) ___-__-__" required>
            <button class="pd-oneclick-btn" type="submit">Купить в 1 клик</button>
          </form>
          <div class="pd-oneclick-note">
            Нажимая кнопку, вы соглашаетесь с <a href="{root}policy.html">политикой конфиденциальности</a>
          </div>
        </div>

        <div class="pd-price-guarantee">
          {ICON["check"]}
          <span><b>Прямые поставки с завода.</b> Заводское вибропрессование по ГОСТ 17608-2017.</span>
        </div>
      </div>
    </div>
    """

    # ---- Блок Вкладок (Tabs Section)
    tabs_html = f"""
    <section class="pd-tabs-section">
      <div class="wrap">
        <div class="pd-tabs-nav" role="tablist">
          <button class="pd-tab-btn is-active" type="button" role="tab" data-tab="tabSpecs">
            {ICON["doc"]}<span>Характеристики</span>
          </button>
          <button class="pd-tab-btn" type="button" role="tab" data-tab="tabCalc">
            {ICON["calc"]}<span>Калькулятор мощения</span>
          </button>
          <button class="pd-tab-btn" type="button" role="tab" data-tab="tabDelivery">
            {ICON["truck"]}<span>Доставка и разгрузка</span>
          </button>
          <button class="pd-tab-btn" type="button" role="tab" data-tab="tabPayment">
            {ICON["card"]}<span>Оплата</span>
          </button>
        </div>

        <div class="pd-tab-panel is-active" id="tabSpecs" role="tabpanel">
          {dotted_specs_html(p)}
        </div>

        <div class="pd-tab-panel" id="tabCalc" role="tabpanel">
          <div class="pd-calc-interactive">
            <div class="pd-calc-grid">
              <div class="pd-calc-fields">
                <h3>Параметры участка мощения</h3>
                <div class="pd-calc-field">
                  <label for="fcArea">Площадь двора и дорожек (м²):</label>
                  <input id="fcArea" type="number" step="any" value="75" placeholder="75">
                </div>
                <label class="pd-calc-check">
                  <input id="fcWaste" type="checkbox" checked>
                  <span>Добавить запас +5% на подрезку и стыки</span>
                </label>
              </div>

              <div class="pd-calc-results">
                <div>
                  <div class="pd-calc-results-title">Расчёт материалов</div>
                  <div class="pd-calc-results-list">
                    <div class="pd-calc-res-item">
                      <span>Квадратура с запасом:</span>
                      <b id="fcResBricks">79 м²</b>
                    </div>
                    <div class="pd-calc-res-item">
                      <span>Количество поддонов:</span>
                      <b id="fcResPallets">6 поддонов</b>
                    </div>
                    <div class="pd-calc-res-item">
                      <span>Садовый бордюр (периметр):</span>
                      <b id="fcResMortar">45 пог. м</b>
                    </div>
                    <div class="pd-calc-res-item">
                      <span>Общий вес партии:</span>
                      <b id="fcResWeight">7,1 т</b>
                    </div>
                  </div>
                </div>
                <div>
                  <div class="pd-calc-res-total">
                    <span>Ориентировочная сумма:</span>
                    <b id="fcResSum">{rub(round(79 * price_m2))} ₽</b>
                  </div>
                  <button class="pd-btn-main" id="fcAddBtn" type="button">
                    {ICON["cart"]}<span>Добавить расчёт в заявку</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="pd-tab-panel" id="tabDelivery" role="tabpanel">
          <div class="pd-delivery-info">
            <h3>Доставка тротуарной плитки с выгрузкой</h3>
            <p>Плитка доставляется автомобилями с краном-манипулятором грузоподъёмностью от 5 до 15 тонн. Водитель аккуратно выгружает поддоны на подготовленную площадку вашего участка без повреждения упаковки.</p>
            <table class="pd-delivery-table">
              <thead>
                <tr>
                  <th>Зона доставки</th>
                  <th>Манипулятор 5–10 т (до 8 поддонов)</th>
                  <th>Длинномер 20 т (до 15 поддонов)</th>
                  <th>Срок</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>По Краснодару (до 15 км)</td>
                  <td>от 3 500 ₽</td>
                  <td>от 7 500 ₽</td>
                  <td>1–2 дня</td>
                </tr>
                <tr>
                  <td>Пригород (Динская, Яблоновский, Елизаветинская)</td>
                  <td>от 4 500 ₽</td>
                  <td>от 9 000 ₽</td>
                  <td>1–2 дня</td>
                </tr>
                <tr>
                  <td>Краснодарский край и Адыгея (до 100 км)</td>
                  <td>от 8 000 ₽</td>
                  <td>от 15 000 ₽</td>
                  <td>2–3 дня</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="pd-tab-panel" id="tabPayment" role="tabpanel">
          <div class="pd-payment-info">
            <h3>Условия оплаты</h3>
            <div class="pd-payment-grid">
              <div class="pd-payment-card">
                <h4>Для частных покупателей</h4>
                <p>• Оплата водителю-экспедитору по факту доставки и проверки целостности поддонов.<br>• Оплата банковской картой или через СБП.<br>• Фиксация цены при бронировании партии с завода.</p>
              </div>
              <div class="pd-payment-card">
                <h4>Для строительных компаний и ИП</h4>
                <p>• Безналичный расчёт с НДС 20% или без НДС.<br>• Комплект закрывающих документов (УПД, паспорта качества завода, сертификаты ГОСТ 17608-2017).<br>• Договор поставки с гарантией сроков.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
    """

    # ---- похожие и та же расцветка в других формах
    sim = similar(p)
    sim_html = ""
    if sim:
        sim_html = f"""
  <section class="section"><div class="wrap">
    <div class="section-head"><h2>Другие расцветки «{esc(m["name"])}»</h2>
      <a class="see-all" href="{root}plitka-{p["shape"]}.html">Все расцветки</a></div>
    <div class="p-grid{grid_cls(len(sim))}">
      {"".join(card_of(q, root=root, with_shape=False) for q in sim)}</div>
  </div></section>"""

    cross = cross_shapes(p)
    cross_html = ""
    if cross:
        chips = "".join(
            f'<a class="chip" href="{root}{q["_url"]}">{esc(shape_name(q["shape"]))}'
            f'<small>{rub(q["price"])} ₽/м²</small></a>' if q["price"] else
            f'<a class="chip" href="{root}{q["_url"]}">{esc(shape_name(q["shape"]))}'
            f'<small>цена по запросу</small></a>' for q in cross)
        cross_html = f"""
  <section class="section"><div class="wrap">
    <div class="section-head"><h2>«{esc(p["name"])}» в других формах</h2></div>
    <p class="page-sub">Тот же цвет — другой рисунок мощения.</p>
    <div class="applied">{chips}</div>
  </div></section>"""

    body = f"""
  <section class="page-head">
    <div class="wrap">
      <div class="pd-header">
        <h1 class="pd-title">{esc(name)}</h1>
        {crumbs_html([
            ("Главная", f"{root}index.html"),
            ("Тротуарная плитка", f"{root}trotuarnaya-plitka.html"),
            (m["name"], f"{root}plitka-{p['shape']}.html"),
            (p["name"], None)])}
      </div>
    </div>
  </section>

  <section class="pd">
    <div class="wrap">
      <div class="pd-hero-grid">
        <div>
          {gallery_html}
          {trust_html}
        </div>
        <div>
          {buybox_html}
        </div>
      </div>
    </div>
  </section>

  {tabs_html}
  {cross_sell_html(root)}
  {sim_html}
  {cross_html}
"""
    ld = {"@context": "https://schema.org", "@type": "Product", "name": name,
          "sku": p["id"].upper(), "category": "Тротуарная плитка",
          "description": f"Тротуарная плитка «{p['name']}», форма «{m['name']}». "
                         f"Толщина 40 мм, морозостойкость F200, класс прочности В30, "
                         f"поддон {PALLET_M2} м².",
          "image": SITE_URL + p["_gal"][0],
          "offers": {"@type": "Offer", "price": p["price"], "priceCurrency": "RUB",
                     "url": SITE_URL + p["_url"]}}
    head = ('\n  <script type="application/ld+json">'
            + json.dumps(ld, ensure_ascii=False) + "</script>")

    write_page(BASE / "tovar" / f"{p['slug']}.html", page_shell(
        f"{name} · {rub(p['price'])} ₽/м² — купить в Краснодаре",
        f"{name}: {rub(p['price'])} ₽/м², {pallet_text(p)}. Толщина 40 мм, F200, В30. "
        f"Доставка по Краснодару и краю, наличный и безналичный расчёт.",
        body, root=root, active="plitka", extra_head=head))


# ---------------------------------------------------------------------------
# Бордюры
# ---------------------------------------------------------------------------
def build_border(b):
    root = "../"
    is_road = "дорожн" in b["name"].lower()
    use = ("держит край дорожки и парковки — мощение не расползается, "
           "край не крошится под колесом"
           if is_road else
           "аккуратный край садовых дорожек и клумб — ниже и легче дорожного, "
           "ставится вручную")
    img = f"img/catalog/{b['id']}.jpg?v={IMG_V}"
    terms_html = "".join(f"<li>{ICON[ic]}<span>{esc(t)}</span></li>" for ic, t in TERMS_STOCK)

    body = f"""
  <section class="page-head"><div class="wrap">{crumbs_html([
      ("Главная", f"{root}index.html"),
      ("Тротуарная плитка", f"{root}trotuarnaya-plitka.html"),
      (b["name"], None)])}</div></section>

  <section class="pd"><div class="wrap">
    <div class="pd-grid">
      <div class="pd-gallery">
        <div class="pd-main-wrap">
          <!-- Бордюр снят целиком на белом холсте: квадратный кроп .pd-main срезал бы
               ему торцы, поэтому вписываем кадр карточной .p-img--contain -->
          <img class="p-img p-img--contain" id="pdMain" src="{root}{img}"
            alt="{esc(b["name"])} к тротуарной плитке" width="1200" height="900"
            fetchpriority="high">
          <button class="pd-zoom" id="pdZoom" type="button"
            aria-label="Открыть фото крупно">{ICON["zoom"]}</button>
        </div>
      </div>
      <div class="pd-info">
        <p class="note">Артикул {esc(b["id"]).upper()}</p>
        <h1 class="pd-name">{esc(b["name"])}</h1>
        <p class="pd-meta">Бордюр к тротуарной плитке</p>
        <p class="pd-price"><b>{rub(b["price"])} ₽</b><span>/шт</span></p>
        <ul class="pd-terms">{terms_html}</ul>
        <div class="pd-bar">
          <button class="btn p-add" type="button" data-add
            data-id="{esc(b["id"])}" data-name="{esc(b["name"])}" data-price="{b["price"]}"
            data-unit="шт" data-img="img/catalog/{b["id"]}.jpg"
            data-url="tovar/{b["id"]}.html" data-root="{root}">В заявку</button>
          <a class="btn btn--call pd-bar-call" href="{PHONE_HREF}"
             aria-label="Позвонить">{ICON["phone"]}<span>Позвонить</span></a>
        </div>
        <p class="pd-note">Назначение: {esc(use)}.</p>
      </div>
    </div>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="section-head"><h2>Плитка к этому бордюру</h2>
      <a class="see-all" href="{root}trotuarnaya-plitka.html">Вся плитка</a></div>
    <div class="tiles">{"".join(
        f'<a class="tile" href="{root}plitka-{s}.html">'
        f'<strong>{esc(SHAPES[s]["name"])}<span>от {rub(SHAPES[s]["min_price"])} ₽/м²</span></strong>'
        f'<img src="{root}img/plitka/shape-{s}.jpg" alt="" width="320" height="240" '
        f'loading="lazy"></a>' for s in SHAPE_ORDER[:4])}</div>
  </div></section>
"""
    ld = {"@context": "https://schema.org", "@type": "Product", "name": b["name"],
          "sku": b["id"].upper(), "category": "Бордюры",
          "image": SITE_URL + f"img/catalog/{b['id']}.jpg",
          "offers": {"@type": "Offer", "price": b["price"], "priceCurrency": "RUB",
                     "url": SITE_URL + f"tovar/{b['id']}.html"}}
    head = ('\n  <script type="application/ld+json">'
            + json.dumps(ld, ensure_ascii=False) + "</script>")

    write_page(BASE / "tovar" / f"{b['id']}.html", page_shell(
        f"{b['name']} — {rub(b['price'])} ₽/шт, купить в Краснодаре",
        f"{b['name']}: {rub(b['price'])} ₽/шт. Отгружаем вместе с плиткой или отдельно; "
        f"количество посчитает менеджер по плану участка. Наличный и безналичный расчёт.",
        body, root=root, active="plitka", extra_head=head))


# ---------------------------------------------------------------------------
def main():
    build_category()
    for slug in SHAPE_ORDER:
        build_shape(slug)
    for p in PRODUCTS:
        build_product(p)
    for b in BORDERS:
        build_border(b)
    print(f"плитка: витрина + {len(SHAPE_ORDER)} форм + "
          f"{len(PRODUCTS)} товаров + {len(BORDERS)} бордюра")


if __name__ == "__main__":
    main()
