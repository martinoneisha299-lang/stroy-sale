"""
Главная и служебные страницы: index, заявка, поиск, акции, доставка, работы,
политика конфиденциальности.

Раньше index.html и policy.html правились руками и отставали от остального
сайта: шапка и футер там жили своей жизнью. Теперь они собираются той же
оболочкой, что и каталог, — расхождение невозможно.

Запуск: python3 tools/build_site.py (после build_category/build_tiles/build_roof —
главная берёт с них живые цены и количества).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from shell_common import (ADDRESS, BASE, CITY, ICON, PHONE, PHONE_HREF, PHONE_NOTE,
                          SECTIONS, WORK_HOURS, crumbs_html, esc, msg_circles,
                          page_shell, plural, product_card, rub, write_page)

CAT = json.loads((BASE / "_data" / "catalog.json").read_text())["products"]
TILES = json.loads((BASE / "_data" / "tiles.json").read_text())

BRICK = [p for p in CAT if p["category"] == "oblitsovochnyy" and p.get("price")]
TILE = [p for p in TILES["products"] if p.get("price")]

IMG_V = 9


# ---------------------------------------------------------------------------
# Акции. Срок жизни у каждой свой: после даты акция исчезает сама
# (data-until читает app.js). Менять здесь — попадёт и на главную, и в /akcii.
# ---------------------------------------------------------------------------
PROMOS = [
    # ВНИМАНИЕ: процент скидки заказчик пока не подтвердил, и на страницах
    # плитки старой цены нет. Пока обещаем только то, что можем выполнить.
    {"title": "Плитка «Старый город»",
     "sub": "Классическая форма — 24 расцветки от 650 ₽/м²",
     "url": "plitka-staryy-gorod.html", "until": None,
     "img": "img/plitka/shape-staryy-gorod.jpg", "accent": True},
    # Фото у промо теперь ФОН всей плитки, поэтому нужен кадр, который держит
    # текст: работа или кладка, а не студийный кирпич на белом.
    {"title": "Посчитаем материал",
     "sub": "Пришлите размеры — вернём расчёт за 5 минут. Бесплатно",
     "url": "#lead", "until": None, "img": "img/plitka/work-06.jpg"},
    {"title": "Новинки заводов",
     "sub": "25 новых цветов кирпича этим летом",
     "url": "kirpich-oblitsovochnyy.html?sort=new", "until": None,
     "img": "img/catalog/kla-003.jpg"},
]


def promo_card(p, root=""):
    until = f' data-until="{p["until"]}"' if p.get("until") else ""
    cls = "promo promo--accent" if p.get("accent") else "promo"
    img = (f'<img src="{root}{p["img"]}?v={IMG_V}" alt="" width="380" height="285" loading="lazy">'
           if p.get("img") else "")
    return (f'<a class="{cls}" href="{root}{p["url"]}"{until}>'
            f'<strong>{esc(p["title"])}</strong><p>{esc(p["sub"])}</p>'
            f'<span class="go">Подробнее</span>{img}</a>')


def promo_row(root=""):
    return f'<div class="promo-row">{"".join(promo_card(p, root) for p in PROMOS)}</div>'


# ---------------------------------------------------------------------------
# Главная
# ---------------------------------------------------------------------------
def section_tiles():
    """Разделы каталога плитками — главный вход в магазин."""
    out = []
    for s in SECTIONS:
        out.append(f'<a class="tile" href="{s["url"]}">'
                   f'<strong>{esc(s["title"])}<span>{esc(s["note"])}</span></strong>'
                   f'<img src="{s["img"]}?v={IMG_V}" alt="" width="320" height="240" loading="lazy"></a>')
    return f'<div class="tiles">{"".join(out)}</div>'


def popular_cards():
    """Недорогие позиции, у которых есть НАСТОЯЩИЙ кадр кладки.

    Раньше брались просто восемь самых дешёвых — и подряд вставали четыре
    одинаковые серые «Моно 1» по 650 ₽, а кирпич показывался одинокой штукой
    на белом. Теперь: только товар с полнокадровым фото (кладка/текстура),
    не больше одного на коллекцию и на форму плитки.
    """
    kinds = {}
    kf = BASE / "_data" / "main_frames.json"
    if kf.exists():
        kinds = json.loads(kf.read_text())

    def has_wall(pid):
        return kinds.get(pid) == "wall"

    picks, seen_coll = [], set()
    for p in sorted(BRICK, key=lambda x: x["price"]):
        coll = p.get("collection")
        if coll in seen_coll or not has_wall(p["id"]):
            continue
        if not (BASE / "img" / "catalog" / f"{p['id']}.jpg").exists():
            continue
        seen_coll.add(coll)
        picks.append(("brick", p))
        if len(picks) >= 4:
            break

    seen_shape = set()
    for t in sorted(TILE, key=lambda x: x["price"]):
        if t["shape"] in seen_shape:
            continue
        if not (BASE / "img" / "catalog" / f"{t['id']}.jpg").exists():
            continue
        seen_shape.add(t["shape"])
        picks.append(("tile", t))
        if len(picks) >= 8:
            break

    cards = []
    for kind, p in picks:
        if kind == "brick":
            per = p.get("consumption_per_m2") or 51.4
            m2 = f"≈ {rub(round(p['price'] * per / 10) * 10)} ₽/м² кладки"
            name = f"Кирпич {p['name']}"
            href = f"tovar/kirpich-{p['id']}.html"
            img = f"img/catalog/{p['id']}.jpg?v={IMG_V}"
            unit = "шт"
        else:
            m2 = f"поддон 15 м² ≈ {rub(p['price'] * 15)} ₽"
            name = f"Плитка {TILES['shapes'][p['shape']]['name']} {p['name']}"
            href = f"tovar/{p['slug']}.html"
            img = f"img/catalog/{p['id']}.jpg?v=4"
            unit = "м²"
        cards.append(product_card(
            href=href, name=name, img=img, alt=name,
            price_html=f'<b>{rub(p["price"])} ₽</b><span class="p-unit">/{unit}</span>',
            m2=m2, add={"id": p["id"], "name": name, "price": p["price"],
                        "unit": unit, "img": img.split("?")[0]}))
    return f'<div class="p-grid">{"".join(cards)}</div>'


STEPS = [
    ("Выбираете товар", "В каталоге или по телефону — поможем подобрать под дом и бюджет."),
    ("Перезваниваем за 5 минут", "Уточняем объём, считаем количество и называем цену с доставкой."),
    ("Привозим на объект", "Своя доставка по Краснодару и краю, разгрузка манипулятором."),
    ("Платите при получении", "Наличными или картой, когда материал уже у вас на участке."),
]

TERMS = ["Перезвоним за 5 минут", "Доставка на объект", "Оплата при получении",
         "С заводов Юга напрямую"]


def build_index():
    lo_brick = rub(min(p["price"] for p in BRICK))
    lo_tile = rub(min(p["price"] for p in TILE))
    steps = "".join(
        f'<div class="step"><span class="step-n">{i + 1}</span>'
        f'<h3>{esc(t)}</h3><p>{esc(d)}</p></div>'
        for i, (t, d) in enumerate(STEPS))
    terms = "".join(f'<li class="brick-mark">{esc(t)}</li>' for t in TERMS)
    works = "".join(
        f'<img src="img/plitka/work-{n:02d}.jpg" alt="Двор и дорожки, выложенные плиткой из каталога" '
        f'width="800" height="600" loading="lazy">' for n in (2, 4, 6, 8))

    body = f"""
  <section class="hero">
    <picture>
      <source media="(max-width: 47.9375em)" srcset="img/hero-home-mobile.jpg?v={IMG_V}">
      <img class="hero-photo" src="img/hero-home.jpg?v={IMG_V}"
           alt="Дом, облицованный кирпичом из каталога"
           width="1900" height="1010" fetchpriority="high">
    </picture>
    <div class="wrap hero-in"><div class="hero-copy">
      <span class="hero-eyebrow">{CITY} и край</span>
      <h1>Кирпич, плитка и кровля прямо с заводов Юга</h1>
      <p>Подберём материал под дом и бюджет, посчитаем количество
         и привезём на объект. Без посредников и предоплаты.</p>
      <div class="hero-facts">
        <div><b>470+</b><span>товаров в наличии</span></div>
        <div><b>5 минут</b><span>на расчёт по вашим размерам</span></div>
        <div><b>от {lo_brick} ₽</b><span>кирпич за штуку</span></div>
        <div><b>Оплата</b><span>при получении</span></div>
      </div>
      <div class="hero-cta">
        <a class="btn" href="kirpich-oblitsovochnyy.html">Смотреть каталог</a>
        <a class="hero-ghost" href="#lead">Бесплатный расчёт</a>
      </div>
    </div></div>
  </section>

  <section class="section" id="catalog"><div class="wrap">
    <div class="section-head"><h2>Каталог</h2></div>
    {section_tiles()}
    <p class="note mt">Также возим газоблок, песок и щебень —
      скажите объём, посчитаем и привезём вместе с основным заказом.</p>
  </div></section>

  <section class="section"><div class="wrap">{promo_row()}</div></section>

  <section class="band"><div class="wrap">
    <ul class="terms-strip">{terms}</ul>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="section-head"><h2>Часто заказывают</h2>
      <a class="see-all" href="kirpich-oblitsovochnyy.html">Весь каталог</a></div>
    {popular_cards()}
  </div></section>

  <section class="section"><div class="wrap">
    <div class="section-head"><h2>Наши работы</h2>
      <a class="see-all" href="raboty.html">Смотреть все</a></div>
    <div class="works">{works}</div>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="section-head"><h2>Как заказать</h2></div>
    <div class="steps">{steps}</div>
  </div></section>
"""
    write_page(BASE / "index.html", page_shell(
        f"Стройсейл — кирпич, плитка и кровля с доставкой, {CITY}",
        f"Кирпич, тротуарная плитка и кровля с заводов Юга: 470+ товаров "
        f"с доставкой по {CITY}у и краю. Перезвоним за 5 минут, оплата при получении.",
        body, tab="home"))


# ---------------------------------------------------------------------------
# Заявка
# ---------------------------------------------------------------------------
def build_zayavka():
    body = f"""
  <section class="page-head"><div class="wrap">
    {crumbs_html([("Главная", "index.html"), ("Заявка", None)])}
    <h1>Моя заявка</h1>
    <p class="page-sub">Список товаров, которые вы отложили. Отправьте его —
      перезвоним, уточним объём и назовём цену с доставкой. Предоплаты нет,
      регистрация не нужна.</p>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="empty" id="cartEmpty" hidden>
      <p>Заявка пока пустая. Отложите товары кнопкой «В заявку» — соберём их здесь.</p>
      <a class="btn btn--accent" href="index.html#catalog">Перейти в каталог</a>
    </div>

    <div class="cart-grid" id="cartBody" hidden>
      <div>
        <ul id="cartList" data-root=""></ul>
      </div>
      <aside class="cart-side">
        <div class="cart-total"><span>Примерно</span><b id="cartTotal">—</b></div>
        <p class="note" id="cartNote"></p>
        <form class="lead-form cart-form" data-lead="czOk" data-clears="cart" novalidate>
          <div class="field">
            <label for="czName">Как к вам обращаться</label>
            <input id="czName" name="name" type="text" autocomplete="name" placeholder="Имя">
          </div>
          <div class="field">
            <label for="czPhone">Телефон</label>
            <input id="czPhone" name="phone" type="tel" inputmode="tel" autocomplete="tel"
                   placeholder="+7 (___) ___-__-__" required aria-describedby="czErr">
            <p class="form-err" id="czErr" hidden>В номере не хватает цифр — проверьте, пожалуйста.</p>
          </div>
          <input type="hidden" name="items" id="cartPayload">
          <button class="btn btn--accent btn--wide" type="submit">Отправить заявку</button>
          <p class="form-note">Нажимая кнопку, вы соглашаетесь с
            <a href="policy.html">политикой конфиденциальности</a>.</p>
        </form>
        <p class="form-ok" id="czOk" role="status" tabindex="-1" hidden>
          Список готов. Отправьте его в мессенджер или позвоните — подтвердим
          наличие и назовём цену с доставкой. Заявка сохранена: если закроете
          страницу, список останется.
          <span class="form-ok-row">
            <a class="btn btn--accent" data-wa href="#" target="_blank" rel="noopener">Отправить в WhatsApp</a>
            <a class="btn btn--ghost" href="{PHONE_HREF}">Позвонить</a>
          </span>
        </p>
      </aside>
    </div>
  </div></section>
"""
    write_page(BASE / "zayavka.html", page_shell(
        "Моя заявка — Стройсейл",
        "Список отложенных товаров. Отправьте заявку — перезвоним за 5 минут, "
        "уточним объём и назовём цену с доставкой.",
        body, active="", tab="cart", lead=False))


# ---------------------------------------------------------------------------
# Поиск
# ---------------------------------------------------------------------------
def build_poisk():
    body = """
  <section class="page-head"><div class="wrap">
    <h1>Поиск по каталогу</h1>
    <p class="page-sub">Введите название материала, цвет или размер — например
      «кирпич бежевый», «плитка старый город», «профнастил С-8».</p>
  </div></section>

  <section class="section"><div class="wrap">
    <div id="searchResults" data-root="">
      <p class="note">Загружаем каталог…</p>
    </div>
  </div></section>
"""
    write_page(BASE / "poisk.html", page_shell(
        "Поиск по каталогу — Стройсейл",
        "Поиск материалов по каталогу Стройсейл: кирпич, тротуарная плитка, кровля.",
        body, lead=False))


# ---------------------------------------------------------------------------
# Акции
# ---------------------------------------------------------------------------
def build_akcii():
    cards = "".join(promo_card(p) for p in PROMOS)
    body = f"""
  <section class="page-head"><div class="wrap">
    {crumbs_html([("Главная", "index.html"), ("Акции", None)])}
    <h1>Акции и предложения</h1>
    <p class="page-sub">Действующие скидки и бесплатные услуги. Предложение
      пропадает со страницы, когда заканчивается срок, — того, чего уже нет,
      вы здесь не увидите.</p>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="promo-row promo-row--wrap">{cards}</div>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="section-head"><h2>Что ещё сэкономит деньги</h2></div>
    <ul class="pd-terms">
      <li>{ICON["calc"]}<span>Бесплатный расчёт количества: пришлите размеры дома,
        забора или двора — посчитаем материал и запас.</span></li>
      <li>{ICON["truck"]}<span>Одна доставка на несколько позиций: кирпич, плитку
        и кровлю привозим вместе, платить за две машины не нужно.</span></li>
      <li>{ICON["shield"]}<span>Остатки со склада поставщика — иногда есть партии
        по цене ниже прайса. Спросите при звонке, что доступно сейчас.</span></li>
    </ul>
  </div></section>
"""
    write_page(BASE / "akcii.html", page_shell(
        "Акции на стройматериалы — Стройсейл, " + CITY,
        "Действующие акции и скидки на кирпич, тротуарную плитку и кровлю "
        f"в {CITY}е. Бесплатный расчёт материала.",
        body))


# ---------------------------------------------------------------------------
# Доставка и оплата
# ---------------------------------------------------------------------------
def build_dostavka():
    body = f"""
  <section class="page-head"><div class="wrap">
    {crumbs_html([("Главная", "index.html"), ("Доставка и оплата", None)])}
    <h1>Доставка и оплата</h1>
    <p class="page-sub">Возим по {CITY}у и краю. Оплата — когда материал
      уже у вас на участке.</p>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="steps">
      <div class="step"><span class="step-n">1</span>
        <h3>Считаем доставку по адресу</h3>
        <p>Стоимость зависит от объёма и расстояния — называем её сразу при звонке,
          до того как вы что-то подтвердите.</p></div>
      <div class="step"><span class="step-n">2</span>
        <h3>Привозим на объект</h3>
        <p>Кирпич и плитку — на поддонах, разгрузка манипулятором прямо к месту
          кладки. Длинномер для кровли до 8 метров.</p></div>
      <div class="step"><span class="step-n">3</span>
        <h3>Проверяете при получении</h3>
        <p>Пересчитываем и осматриваем материал вместе с вами, прежде чем
          вы за него заплатите.</p></div>
      <div class="step"><span class="step-n">4</span>
        <h3>Платите</h3>
        <p>Наличными или картой водителю, безналичный расчёт — для организаций
          по счёту.</p></div>
    </div>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="section-head"><h2>Частые вопросы</h2></div>
    <ul class="pd-terms">
      <li>{ICON["truck"]}<span><b>Можно забрать самому?</b> Спросите менеджера:
        по части позиций это возможно, по части — материал едет прямо с завода.</span></li>
      <li>{ICON["clock"]}<span><b>Как быстро привезёте?</b> Срок зависит
        от позиции и объёма: часть материалов едет со склада, часть — с завода.
        Точный срок называем при подтверждении заказа.</span></li>
      <li>{ICON["card"]}<span><b>Нужна ли предоплата?</b> Нет. Оплата при получении;
        предоплату просим только на позиции, которые везём под заказ с завода.</span></li>
      <li>{ICON["shield"]}<span><b>А если что-то побилось?</b> Пересчитываем
        и осматриваем при приёмке — спорные позиции решаем на месте,
        до оплаты.</span></li>
    </ul>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="section-head"><h2>Где мы</h2></div>
    <p class="page-sub">{ADDRESS} · {WORK_HOURS}</p>
    <iframe class="map" loading="lazy" title="Стройсейл на карте — {ADDRESS}"
      src="https://yandex.ru/map-widget/v1/?ll=38.940651%2C45.105281&amp;z=17&amp;l=map&amp;pt=38.940651%2C45.105281%2Cpm2rdm"></iframe>
  </div></section>
"""
    write_page(BASE / "dostavka.html", page_shell(
        f"Доставка и оплата — Стройсейл, {CITY}",
        f"Доставка стройматериалов по {CITY}у и краю, разгрузка манипулятором, "
        "оплата при получении. Самовывоз со склада.",
        body, active="dostavka"))


# ---------------------------------------------------------------------------
# Наши работы
# ---------------------------------------------------------------------------
def build_raboty():
    shots = "".join(
        f'<img src="img/plitka/work-{n:02d}.jpg" width="800" height="600" loading="lazy" '
        f'alt="Двор и дорожки, выложенные плиткой из нашего каталога">'
        for n in range(1, 11))
    body = f"""
  <section class="page-head"><div class="wrap">
    {crumbs_html([("Главная", "index.html"), ("Наши работы", None)])}
    <h1>Наши работы</h1>
    <p class="page-sub">Дворы и дорожки, выложенные плиткой из нашего каталога.
      Фотографии от производителя и наших покупателей — не рендеры.</p>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="works">{shots}</div>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="section-head"><h2>Хотите так же?</h2></div>
    <p class="page-sub">Пришлите фото участка или размеры — подберём материал,
      посчитаем количество и назовём цену с доставкой. Расчёт бесплатный.</p>
  </div></section>
"""
    write_page(BASE / "raboty.html", page_shell(
        f"Наши работы — объекты из наших материалов, {CITY}",
        f"Фотографии реальных объектов в {CITY}е и крае: дворы, дорожки и фасады "
        "из кирпича и тротуарной плитки Стройсейл.",
        body, active="raboty"))


# ---------------------------------------------------------------------------
# Политика конфиденциальности
# ---------------------------------------------------------------------------
def build_policy():
    body = f"""
  <section class="page-head"><div class="wrap">
    {crumbs_html([("Главная", "index.html"), ("Политика конфиденциальности", None)])}
    <h1>Политика конфиденциальности</h1>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="page-sub prose">
      <p>Оставляя имя и телефон в форме на сайте, вы даёте
        согласие на обработку персональных данных в соответствии с Федеральным законом
        от 27.07.2006 №&nbsp;152-ФЗ «О персональных данных».</p>
      <p><b>Какие данные собираем.</b> Имя и номер телефона,
        которые вы указали сами, и состав заявки — чтобы перезвонить, посчитать материал
        и договориться о доставке.</p>
      <p><b>Зачем.</b> Только для связи по вашему обращению.
        Рассылок не делаем, третьим лицам данные не передаём и не продаём.</p>
      <p><b>Сколько храним.</b> До завершения работы
        по обращению или до вашего отзыва согласия — по звонку на {PHONE}.</p>
      <p><b>Аналитика.</b> Сайт использует обезличенную
        статистику посещений (файлы cookie) для оценки удобства страниц.
        Эти данные не позволяют вас идентифицировать.</p>
      <p><b>Контакты.</b> {ADDRESS}, телефон {PHONE}, {WORK_HOURS}.</p>
    </div>
  </div></section>
"""
    write_page(BASE / "policy.html", page_shell(
        "Политика конфиденциальности — Стройсейл",
        "Как Стройсейл обрабатывает имя и телефон, оставленные в форме на сайте.",
        body, lead=False))


def main():
    build_index()
    build_zayavka()
    build_poisk()
    build_akcii()
    build_dostavka()
    build_raboty()
    build_policy()
    print("страницы сайта: главная, заявка, поиск, акции, доставка, работы, политика")


if __name__ == "__main__":
    main()
