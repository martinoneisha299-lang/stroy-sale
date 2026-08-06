"""
Общая оболочка всех страниц сайта «Стройсейл».

До редизайна 29.07.2026 шапка, футер, полоса связи и общий JS были СКОПИРОВАНЫ
в build_category.py, build_tiles.py и build_roof.py — три копии расходились,
и правка в одном месте не долетала до двух других. Теперь это один модуль:

    from shell_common import page_shell, product_card, ICON, rub, plural

Кто им пользуется: build_category.py (кирпич), build_tiles.py (плитка),
build_roof.py (кровля), build_site.py (главная и служебные страницы).

Что здесь лежит:
    · контакты и адрес                    · шапка, меню разделов, футер
    · набор SVG-иконок (стиль Lucide)     · нижний таб-бар и шторка каталога
    · карточка товара                     · JS: заявка, поиск, шторки, форма
"""

from pathlib import Path

from nbsp import typo

BASE = Path(__file__).resolve().parent.parent
SITE_URL = "https://martinoneisha299-lang.github.io/stroy-sale/"

# Версии кэша. Поднимать при ЛЮБОЙ правке styles.css / tokens.css / app.js —
# иначе у посетителя останется старый файл и вёрстка «поедет».
STYLES_V = 59
APP_V = 9

# viewport-fit=cover обязателен: без него env(safe-area-inset-*) всегда 0, и во
# встроенных браузерах (Telegram, Instagram), где страница занимает экран
# целиком, нижние пункты таб-бара оказываются под «домашней» чертой iPhone —
# по ним просто не попасть пальцем. Зум НЕ отключаем (никаких maximum-scale).
VIEWPORT = ('<meta name="viewport" '
            'content="width=device-width, initial-scale=1, viewport-fit=cover">')

# ---------------------------------------------------------------------------
# Контакты. Телефон и юзернеймы — заглушки, заказчик пришлёт настоящие.
# ---------------------------------------------------------------------------
PHONE = "+7 (900) 000-00-00"
PHONE_HREF = "tel:+79000000000"
PHONE_NOTE = "Перезвоним за 5 минут"
CITY = "Краснодар"
ADDRESS = "Краснодар, ул. Ореховая, 182"
WORK_HOURS = "с 8:00 до 20:00, без выходных"

WA_URL = "https://wa.me/79000000000"
TG_URL = "https://t.me/stroy_sale"
MAX_URL = "https://max.ru/stroy_sale"


def wa_link(text="Здравствуйте! Пишу с сайта Стройсейл"):
    """Ссылка в WhatsApp с заранее набранным сообщением."""
    from urllib.parse import quote
    return f"{WA_URL}?text={quote(text)}"


# ---------------------------------------------------------------------------
# Наличие и сроки.
#
# ВНИМАНИЕ. В макете у каждого товара стоят строки «Со склада в Краснодаре» и
# «Доставим завтра». Реальных остатков и сроков у нас НЕТ, а это обещание
# покупателю. Решение заказчика 29.07.2026: «пока не знаю, напомни позже».
# До тех пор держим осторожные формулировки. Когда появятся данные об остатках —
# менять ЗДЕСЬ, в одном месте, и пересобрать все четыре генератора.
#
# «Оплата при получении» убрана по требованию заказчика: условия оплаты у
# компании каждый раз разные, обещать их на витрине нельзя. Возвращать нельзя.
# ---------------------------------------------------------------------------
# Оплата описана ровно двумя фразами — короткой и полной. До этого по сайту
# гуляли шесть вариантов одного условия, различавшихся одним словом.
PAY_SHORT = "Наличный и безналичный расчёт"
PAY_FULL = ("Наличный и безналичный расчёт, для организаций — по счёту; "
            "условия согласуем при оформлении заказа")

AVAIL_STOCK = [("truck", "Доставка по Краснодару и краю"),
               ("card", PAY_SHORT)]
AVAIL_ORDER = [("clock", "Под заказ"),
               ("card", PAY_SHORT)]

# Развёрнутые формулировки для страницы товара, где место есть
TERMS_STOCK = [("truck", "Доставка по Краснодару и краю, разгрузка манипулятором"),
               ("card", PAY_FULL),
               ("calc", "Количество и стоимость посчитаем бесплатно")]
TERMS_ORDER = [("clock", "Под заказ — срок поставки уточняет менеджер"),
               ("truck", "Доставка по Краснодару и краю"),
               ("card", PAY_FULL)]

# ---------------------------------------------------------------------------
# Разделы. Порядок — как в меню; ключ используется для подсветки активного.
# ---------------------------------------------------------------------------
SECTIONS = [
    {"key": "oblic", "title": "Облицовочный кирпич", "url": "kirpich-oblitsovochnyy.html",
     "img": "img/cat-oblic.jpg", "note": "264 вида, от 18,50 ₽/шт"},
    {"key": "zabut", "title": "Забутовочный кирпич", "url": "kirpich-zabutovochnyy.html",
     "img": "img/cat-brick.jpg", "note": "Фундамент, стены, перегородки"},
    # 172 — это позиции (7 форм × расцветки), а самих расцветок 32: карточки
    # форм на странице плитки пишут «24 расцветки», «29 расцветок».
    {"key": "plitka", "title": "Тротуарная плитка", "url": "trotuarnaya-plitka.html",
     "img": "img/cat-tile.jpg", "note": "32 расцветки в 7 формах, от 650 ₽/м²"},
    {"key": "krovlya", "title": "Кровля и фасад", "url": "krovlya.html",
     "img": "img/cat-roof.jpg", "note": "Металлочерепица, профнастил, штакетник, сайдинг"},
    # Пункт ведёт на страницу металлосайдинга, поэтому и называется так же:
    # штакетник живёт на своей странице и заявлен в разделе «Кровля».
    {"key": "sayding", "title": "Металлосайдинг", "url": "krovlya-sayding.html",
     "img": "img/roof/cover-cat-sid.jpg", "note": "Фасад и софиты, 22 цвета"},
]

# Ссылки, которые уходят вправо в меню десктопа
SECONDARY = [
    {"key": "dostavka", "title": "Доставка и оплата", "url": "dostavka.html"},
    {"key": "raboty", "title": "Наши работы", "url": "raboty.html"},
]

# ---------------------------------------------------------------------------
# Иконки. Обводка 1.8–2, скруглённые концы — один визуальный язык на весь сайт.
# ---------------------------------------------------------------------------
_S = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="%s" '
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>')

ICON = {
    "menu": _S % ("2.4", '<path d="M4 7h16M4 12h16M4 17h16"/>'),
    "search": _S % ("2", '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4.3-4.3"/>'),
    "right": _S % ("2", '<path d="M9 6l6 6-6 6"/>'),
    "left": _S % ("2", '<path d="M15 6l-6 6 6 6"/>'),
    "down": _S % ("2.5", '<path d="M6 9l6 6 6-6"/>'),
    "arrow": _S % ("2", '<path d="M5 12h14M13 6l6 6-6 6"/>'),
    "close": _S % ("2", '<path d="M6 6l12 12M18 6L6 18"/>'),
    "home": _S % ("1.9", '<path d="M4 11l8-6.5 8 6.5v8a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z"/>'),
    "grid": _S % ("1.9", '<rect x="3.5" y="3.5" width="7" height="7" rx="1.5"/>'
                         '<rect x="13.5" y="3.5" width="7" height="7" rx="1.5"/>'
                         '<rect x="3.5" y="13.5" width="7" height="7" rx="1.5"/>'
                         '<rect x="13.5" y="13.5" width="7" height="7" rx="1.5"/>'),
    "list": _S % ("1.9", '<path d="M8 6h11M8 12h11M8 18h11"/><circle cx="4" cy="6" r="1.2"/>'
                         '<circle cx="4" cy="12" r="1.2"/><circle cx="4" cy="18" r="1.2"/>'),
    "phone": _S % ("1.85", '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6'
                           'A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8'
                           'a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7'
                           'a2 2 0 0 1 1.7 2z"/>'),
    "chat": _S % ("1.85", '<path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 9 9 0 0 1-3.4-.6L3 21l1.8-4.8'
                          'A8.3 8.3 0 0 1 12 3.1a8.4 8.4 0 0 1 9 8.4z"/>'),
    "bookmark": _S % ("1.8", '<path d="M6 3h12v18l-6-4-6 4z"/>'),
    "truck": _S % ("1.9", '<path d="M3 7h11v8H3zM14 10h4l3 3v2h-7z"/>'
                          '<circle cx="7" cy="18" r="1.7"/><circle cx="17.5" cy="18" r="1.7"/>'),
    "warehouse": _S % ("1.95", '<path d="M4 20V9l8-5 8 5v11"/><path d="M9 20v-6h6v6"/>'),
    "clock": _S % ("1.9", '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/>'),
    "card": _S % ("1.9", '<rect x="2.5" y="5.5" width="19" height="13" rx="2.5"/><path d="M2.5 10h19"/>'),
    "shield": _S % ("1.9", '<path d="M12 3l7 3v6c0 4.2-2.9 7.7-7 9-4.1-1.3-7-4.8-7-9V6z"/>'
                           '<path d="M9.2 12.2l2 2 3.6-3.8"/>'),
    "calc": _S % ("1.85", '<rect x="4.5" y="2.5" width="15" height="19" rx="2.5"/>'
                          '<path d="M8 7h8M8.5 12h.01M12 12h.01M15.5 12h.01M8.5 16h.01M12 16h.01M15.5 16h.01"/>'),
    "photo-off": _S % ("1.8", '<rect x="3" y="5" width="18" height="14" rx="2.5"/>'
                              '<path d="M3 16l4.5-4.5 3 3M14 13l3-2.5 4 4M3.5 4.5l17 15"/>'),
    "zoom": _S % ("1.9", '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4.3-4.3M11 8.5v5M8.5 11h5"/>'),
    "pin": _S % ("1.9", '<path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11z"/>'
                        '<circle cx="12" cy="10" r="2.6"/>'),
    "check": _S % ("2.2", '<path d="M4.5 12.5l5 5 10-11"/>'),
    "filter": _S % ("2", '<path d="M4 6h16M7 12h10M10 18h4"/>'),
    # Рядом со словом «Акции» стоит знак процента — так это подписано в любом
    # магазине. Солнце, которое было здесь раньше, не значило ничего.
    "percent": _S % ("1.9", '<path d="M19 5L5 19"/><circle cx="6.8" cy="6.8" r="2.3"/>'
                            '<circle cx="17.2" cy="17.2" r="2.3"/>'),
}

# Мессенджеры — фирменные заливки, обводкой их рисовать нельзя
WA_SVG = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z"/></svg>')
TG_SVG = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>')


# ---------------------------------------------------------------------------
# Мелкие утилиты (раньше жили в каждом генераторе своей копией)
# ---------------------------------------------------------------------------
def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def rub(v):
    """36.88 → «36,88», 1900.0 → «1 900»."""
    if v is None:
        return ""
    s = f"{v:,.2f}".replace(",", " ").replace(".", ",")
    return s[:-3] if s.endswith(",00") else s


def plural(n, one, few, many):
    n = abs(int(n)) % 100
    if 11 <= n <= 14:
        return many
    n %= 10
    if n == 1:
        return one
    if 2 <= n <= 4:
        return few
    return many


def grid_cls(n):
    """Не оставлять одинокую карточку в последнем ряду при малых наборах."""
    if n < 2 or n > 20:
        return ""
    for cols in (5, 4, 3, 2):
        if n % cols == 0 and n // cols >= 1:
            return f" p-grid--c{cols}"
    return ""


def write_page(path, html):
    """Единственная точка записи: неразрывные пробелы ставятся здесь."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(typo(html), encoding="utf-8")


# ---------------------------------------------------------------------------
# Кусочки оболочки
# ---------------------------------------------------------------------------
def crumbs_html(items):
    """items: [(«Главная», «index.html»), …, («Текущая», None)]"""
    li = []
    for title, href in items:
        inner = f'<a href="{href}">{esc(title)}</a>' if href else f"<span>{esc(title)}</span>"
        li.append(f"<li>{inner}</li>")
    return ('<nav aria-label="Вы здесь"><ol class="crumbs">'
            + "".join(li) + "</ol></nav>")


def header_html(root="", active="", lead=True):
    secs = []
    for s in SECTIONS:
        on = ' class="is-on" aria-current="page"' if s["key"] == active else ""
        secs.append(f'<a href="{root}{s["url"]}"{on}>{esc(s["title"])}</a>')
    lead_href = "#lead" if lead else f"{root}index.html#lead"
    for i, s in enumerate(SECONDARY):
        on = ' aria-current="page"' if s["key"] == active else ""
        style = ' class="subnav-right"' if i == 0 else ""
        secs.append(f'<a href="{root}{s["url"]}"{on}{style}>{esc(s["title"])}</a>')

    return f"""
  <header class="hdr">
    <div class="wrap hdr-top">
      <a class="logo" href="{root}index.html" aria-label="Стройсейл — на главную">
        <svg viewBox="0 0 100 88" aria-hidden="true"><path fill="var(--accent)" d="M50 4 L96 84 H70 L50 36 L30 84 H4 Z"/></svg>
        <span><b>СТРОЙ</b><b>СЕЙЛ</b></span>
      </a>
      <div class="hdr-tools">
        <button class="hdr-cat" type="button" id="catBtn" aria-expanded="false" aria-controls="catDrawer">
          {ICON["menu"]}<span>Каталог</span>
        </button>
        <form class="hdr-search" role="search" action="{root}poisk.html" method="get">
          {ICON["search"]}
          <input type="search" name="q" id="q" placeholder="Поиск: кирпич, плитка, профнастил"
                 aria-label="Поиск по каталогу" autocomplete="off" data-root="{root}">
          <div class="sug" id="sug" hidden></div>
        </form>
      </div>
      <div class="hdr-city">
        <span>Город</span>
        <a href="{root}dostavka.html">{CITY}</a>
      </div>
      <div class="hdr-contact">
        <a class="hdr-tel" href="{PHONE_HREF}">{PHONE}</a>
        <small>{PHONE_NOTE}</small>
      </div>
      <a class="btn hdr-cta" href="{lead_href}">Заказать звонок</a>
      <a class="hdr-cart" href="{root}zayavka.html" aria-label="Заявка">
        {ICON["list"]}<span class="cart-count" data-cart-count hidden>0</span>
      </a>
    </div>
    <nav class="subnav" aria-label="Разделы каталога">
      <div class="wrap subnav-in">
        <a class="subnav-sale" href="{root}akcii.html">{ICON["percent"]}Акции</a>
        {"".join(secs)}
      </div>
    </nav>
  </header>
"""


def catalog_drawer(root=""):
    items = []
    for s in SECTIONS:
        items.append(
            f'<li><a href="{root}{s["url"]}">'
            f'<img src="{root}{s["img"]}" alt="" width="48" height="48" loading="lazy">'
            f'<span>{esc(s["title"])}<small>{esc(s["note"])}</small></span>'
            f'<span class="arr">{ICON["right"]}</span></a></li>')
    extra = [("Акции и предложения", f"{root}akcii.html"),
             ("Доставка и оплата", f"{root}dostavka.html"),
             ("Наши работы", f"{root}raboty.html"),
             ("Моя заявка", f"{root}zayavka.html")]
    for title, href in extra:
        items.append(f'<li><a href="{href}"><span>{esc(title)}</span>'
                     f'<span class="arr">{ICON["right"]}</span></a></li>')
    return f"""
  <div class="drawer drawer--left" id="catDrawer" hidden>
    <div class="drawer-scrim" data-close></div>
    <div class="drawer-panel" role="dialog" aria-modal="true" aria-label="Каталог">
      <div class="drawer-head">
        <strong>Каталог</strong>
        <button class="drawer-close" type="button" data-close aria-label="Закрыть">{ICON["close"]}</button>
      </div>
      <div class="drawer-body">
        <ul class="drawer-nav">{"".join(items)}</ul>
      </div>
    </div>
  </div>
"""


def tabbar(root="", active=""):
    def item(key, href, icon, label, badge=False):
        on = ' class="is-on" aria-current="page"' if key == active else ""
        b = '<span class="tab-badge" data-cart-count hidden>0</span>' if badge else ""
        return f'<a href="{href}"{on}>{icon}<span>{label}</span>{b}</a>'

    return f"""
  <nav class="tabbar" aria-label="Основное меню">
    {item("home", f"{root}index.html", ICON["home"], "Главная")}
    <button type="button" id="catBtn2" aria-controls="catDrawer" aria-expanded="false">
      {ICON["grid"]}<span>Каталог</span></button>
    {item("cart", f"{root}zayavka.html", ICON["bookmark"], "Заявка", badge=True)}
    <a href="{PHONE_HREF}">{ICON["phone"]}<span>Позвонить</span></a>
    <a href="{wa_link()}" target="_blank" rel="noopener">{ICON["chat"]}<span>Написать</span></a>
  </nav>
"""


def promo_bar(root=""):
    """Тонкая полоса акции. Скрыта по умолчанию — JS показывает её только до даты."""
    # Процент скидки заказчик не подтвердил — пока полоса зовёт на бесплатный
    # расчёт: это мы точно делаем. Когда акция будет согласована, вернуть
    # сюда «−15% … до <дата>» вместе с data-until.
    return (f'<a class="promo-bar" href="{root}index.html#lead" hidden data-until="2026-12-31">'
            f'<b>Бесплатный расчёт</b> материала по вашим размерам</a>')


def msg_circles(product="", label="Или напишите:"):
    txt = f"Здравствуйте! Интересует {product}" if product else "Здравствуйте! Пишу с сайта Стройсейл"
    return f"""<p class="msg-row"><span>{label}</span>
      <a class="msg-circle mc-wa" href="{wa_link(txt)}" target="_blank" rel="noopener" aria-label="Написать в WhatsApp">{WA_SVG}</a>
      <a class="msg-circle mc-tg" href="{TG_URL}" target="_blank" rel="noopener" aria-label="Написать в Telegram">{TG_SVG}</a>
      <a class="msg-circle mc-max" href="{MAX_URL}" target="_blank" rel="noopener" aria-label="Написать в MAX"><img src="{{root}}img/max-icon-white.svg" alt="" width="22" height="22"></a></p>"""


def lead_block(root="", h2="Расчёт материала и стоимости",
               note="Оставьте номер — менеджер уточнит размеры, посчитает "
                    "объём и пришлёт расчёт с условиями доставки."):
    circles = msg_circles().replace("{root}", root)
    return f"""
  <section class="section" id="lead">
    <div class="wrap">
      <div class="lead">
        <div>
          <h2>{esc(h2)}</h2>
          <p class="page-sub">{esc(note)}</p>
          <a class="lead-phone" href="{PHONE_HREF}">{PHONE}
            <small>Приём звонков {WORK_HOURS}</small></a>
          {circles}
        </div>
        <form class="lead-form" data-lead="lfOk" novalidate>
          <div class="field">
            <label for="lfName">Ваше имя</label>
            <input id="lfName" name="name" type="text" autocomplete="name" placeholder="Иван">
          </div>
          <div class="field">
            <label for="lfPhone">Телефон</label>
            <input id="lfPhone" name="phone" type="tel" autocomplete="tel" inputmode="tel"
                   placeholder="+7 (___) ___-__-__" required aria-describedby="lfErr">
            <p class="form-err" id="lfErr" hidden>В номере не хватает цифр — проверьте, пожалуйста.</p>
          </div>
          <button class="btn btn--accent btn--wide" type="submit">Получить расчёт</button>
          <p class="form-note">Нажимая кнопку, вы даёте согласие на обработку персональных данных
            и принимаете <a href="{root}policy.html">политику конфиденциальности</a>.
            Номер используем только для связи по вашей заявке.</p>
        </form>
        <p class="form-ok" id="lfOk" role="status" tabindex="-1" hidden>
          Заявка готова. Отправьте её в WhatsApp или позвоните — так менеджер
          получит её сразу и назовёт цену с доставкой:
          <span class="form-ok-row">
            <a class="btn btn--accent" data-wa href="{wa_link()}" target="_blank" rel="noopener">Отправить в WhatsApp</a>
            <a class="btn btn--ghost" href="{PHONE_HREF}">Позвонить {PHONE}</a>
          </span>
        </p>
      </div>
    </div>
  </section>
"""


def footer_html(root=""):
    secs = "".join(f'<li><a href="{root}{s["url"]}">{esc(s["title"])}</a></li>' for s in SECTIONS)
    return f"""
  <footer class="footer">
    <div class="wrap footer-in">
      <div>
        <a class="logo" href="{root}index.html" aria-label="Стройсейл">
          <svg viewBox="0 0 100 88" aria-hidden="true"><path fill="var(--accent)" d="M50 4 L96 84 H70 L50 36 L30 84 H4 Z"/></svg>
          <span><b>СТРОЙ</b><b>СЕЙЛ</b></span>
        </a>
        <p class="footer-about">Кирпич, тротуарная плитка, кровля и фасадные
          материалы — напрямую с заводов. Работаем с частными покупателями,
          подрядчиками и организациями: наличный и безналичный расчёт.</p>
      </div>
      <div>
        <h3>Каталог</h3>
        <ul>{secs}</ul>
      </div>
      <div>
        <h3>Покупателю</h3>
        <ul>
          <li><a href="{root}dostavka.html">Доставка и оплата</a></li>
          <li><a href="{root}akcii.html">Акции</a></li>
          <li><a href="{root}raboty.html">Наши работы</a></li>
          <li><a href="{root}zayavka.html">Моя заявка</a></li>
          <li><a href="{root}policy.html">Политика конфиденциальности</a></li>
        </ul>
      </div>
      <div>
        <h3>Контакты</h3>
        <a class="footer-tel" href="{PHONE_HREF}">{PHONE}</a>
        <p class="footer-hours">Приём звонков: {WORK_HOURS}</p>
        <p class="footer-addr">{ADDRESS}</p>
        {msg_circles(label="Напишите:").replace("{root}", root)}
      </div>
      <p class="footer-legal">
        Стройсейл · {CITY} · 2026. Информация на сайте носит справочный характер
        и не является публичной офертой. Наличие, цена и условия поставки
        подтверждаются отдельно.
      </p>
    </div>
  </footer>
"""


# ---------------------------------------------------------------------------
# Карточка товара — одна на весь сайт (кирпич, плитка, кровля)
# ---------------------------------------------------------------------------
def terms_line():
    """Условия одной строкой над выдачей — вместо повтора в каждой карточке."""
    rows = "".join(f'<li>{ICON[ic]}<span>{esc(t)}</span></li>' for ic, t in AVAIL_STOCK)
    return f'<ul class="terms-line">{rows}</ul>'


def product_card(*, href, name, img=None, alt="", price_html="", m2="", badge=None,
                 in_stock=True, data="", root="", add=None, img_contain=False,
                 specs="", eager=False, alt_img=None):
    """
    Универсальная карточка витрины.

    href       — ссылка на товар
    price_html — уже собранная цена («31,40 ₽» + единица) либо "" → «Цена по запросу»
    add        — dict для кнопки «В заявку»: {id, name, price, unit, img}
    data       — готовая строка data-атрибутов для фильтров и сортировки
    alt_img    — второй кадр: сам товар крупно, всплывает по наведению.
                 Главный кадр — кладка («как это выглядит на доме»), второй —
                 штучный товар («что именно приедет»). Передавать ТОЛЬКО если
                 такой кадр реально есть: иначе по наведению будет пустая плашка.
    """
    if img:
        load = ('loading="eager" fetchpriority="high"' if eager else 'loading="lazy"')
        cls = "p-img p-img--contain" if img_contain else "p-img"
        pic = (f'<img class="{cls}" src="{root}{img}" alt="{esc(alt)}" '
               f'width="640" height="480" {load}>')
        if alt_img:
            pic += (f'<span class="p-alt" aria-hidden="true">'
                    f'<img src="{root}{alt_img}" alt="" width="640" height="480" '
                    f'loading="lazy"></span>')
    else:
        pic = (f'<div class="p-img p-none">{ICON["photo-off"]}'
               f'<span>Фотографии пришлём по запросу</span></div>')

    badge_html = ""
    if badge:
        mod = " p-badge--new" if badge == "Новинка" else ""
        badge_html = f'<span class="p-badge{mod}">{esc(badge)}</span>'

    if price_html:
        price = f'<p class="p-price">{price_html}</p>'
        # Строку «≈ ₽/м²» печатаем ВСЕГДА, даже пустой: у форматов без известной
        # ложковой грани её нет, и без пустого слота цена с кнопкой в соседних
        # карточках стояли на разной высоте (высоту держит CSS min-height).
        price += f'<p class="p-m2">{esc(m2)}</p>'
    else:
        price = '<p class="p-ask">Цена по запросу</p>'

    if add:
        # data-root обязателен: по нему тост строит ссылку «Открыть заявку».
        # Без него на страницах в tovar/ она уводила на tovar/zayavka.html — 404.
        btn = (f'<button class="btn p-add" type="button" data-add '
               f'data-id="{esc(add["id"])}" data-name="{esc(add["name"])}" '
               f'data-price="{add.get("price") or ""}" data-unit="{esc(add.get("unit", "шт"))}" '
               f'data-img="{esc(add.get("img", ""))}" data-url="{esc(href)}" '
               f'data-root="{root}">В заявку</button>')
    else:
        # Кнопка ведёт на карточку товара, а не запрашивает цену, — поэтому
        # и называется тем, что делает. «Запросить цену» обещало действие,
        # которого не выполняло, и спорило с «В заявку» в соседнем разделе.
        btn = f'<a class="btn btn--outline" href="{root}{href}">Подробнее</a>'

    return f"""<article class="p-card"{data}>{badge_html}
  <a class="p-shot" href="{root}{href}" tabindex="-1" aria-hidden="true">{pic}</a>
  <a class="p-name" href="{root}{href}">{esc(name)}</a>
  {specs}{price}
  <div class="p-actions">{btn}</div>
</article>"""


# ---------------------------------------------------------------------------
# Общий JS: шторки, заявка, поиск, форма, полоса акции
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Сборка страницы целиком
# ---------------------------------------------------------------------------
def page_shell(title, descr, body, *, root="", active="", extra_js="", extra_head="",
               promo=True, lead=True, tab=""):
    """
    title/descr — <title> и meta description
    body        — готовая разметка страницы (между шапкой и футером)
    root        — «» для корня, «../» для страниц в tovar/
    active      — ключ раздела для подсветки в меню
    tab         — ключ активного пункта таб-бара (home/cart)
    """
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  {VIEWPORT}
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(descr)}">
  <link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{root}styles.css?v={STYLES_V}">{extra_head}
</head>
<body>
  <a class="skip" href="#main">К содержанию</a>
{promo_bar(root) if promo else ""}
{header_html(root, active, lead)}
  <main id="main">
{body}
  </main>
{lead_block(root) if lead else ""}
{footer_html(root)}
{catalog_drawer(root)}
{tabbar(root, tab)}
  <script src="{root}app.js?v={APP_V}" defer></script>
{extra_js}
</body>
</html>
"""
