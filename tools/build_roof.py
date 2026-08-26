"""
Кровля, фасад и забор: хаб раздела, витрины семейств и страницы товара.

Собирает:
    krovlya.html                    — хаб: четыре материала, палитра, калькулятор
    krovlya-<семейство>.html × 4    — витрина семейства (металлочерепица,
                                      профнастил, штакетник, сайдинг)
    tovar/krovlya-<id>.html × 16    — страницы товара

Товарная матрица и характеристики лежат ЗДЕСЬ, в коде: поставщик один, прайса
в машинном виде у нас нет, спеки выверены по его txt и заводскому прайсу.
Цены на сайт не выносим (наценка не утверждена) — везде «Цена по запросу»,
кнопка «В заявку» уходит с пустым data-price: позиция всё равно попадает
в список к менеджеру.

Фотографии и кружки цветов: _data/roof_images.json (готовит build_roof_images.py).
На части кадров профнастила, сайдинга и штакетника стоит водяной знак завода —
это временно и осознанно (решение заказчика), скриптом их не трогаем.

Оболочка, карточка и фильтры — общие модули shell_common и catalog_common;
здесь только то, что специфично для кровли.

Пересборка: build_roof_images.py → build_roof.py.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_common import (fgroup, filters_drawer, filters_panel, grid_shell,
                            toolbar)
from shell_common import (BASE, ICON, PHONE_HREF, SITE_URL, TERMS_ORDER,
                          crumbs_html, esc, grid_cls, page_shell, plural,
                          product_card, write_page)

IMG = json.loads((BASE / "_data" / "roof_images.json").read_text())
COLORS = IMG["colors"]            # slug → {label, code, series, sw}
P_COLORS = IMG["product_colors"]  # id товара → [slug цвета, …]
P_IMAGES = IMG["products"]        # id товара → {gallery: [файлы], scheme: файл|None}
IMG_V = 4                         # версия кэша картинок кровли

# ---------------------------------------------------------------------------
# Справочники
# ---------------------------------------------------------------------------
# Серии покрытий. Порядок — как в палитре поставщика: сначала ходовой глянец,
# потом матовое премиум-покрытие, потом рисунки под дерево, цинк последним.
SERIES = [
    ("polyester", "Полиэстер",
     "Стандартное глянцевое покрытие — самое распространённое на крышах "
     "и заборах. Срок службы покрытия по данным завода — до 10 лет."),
    ("granite", "Granite Deep Mat",
     "Плотное матовое покрытие 35 мкм: не бликует на солнце, дольше держит "
     "цвет. Срок службы покрытия по данным завода — до 15 лет."),
    ("printech", "Printech под дерево и камень",
     "Фотопечать структуры дерева, кирпича и камня: вблизи рисунок отличим "
     "от дерева, издалека — нет."),
    ("zink", "Цинк",
     "Оцинкованный лист без краски — для хозпостроек и черновых работ."),
]
SERIES_TITLE = {k: t for k, t, _ in SERIES}

# Названия цветов приходят из прайса поставщика вперемешку: где-то капс
# посреди фразы, где-то «е» вместо «ё». Чиним только написание — сам список
# цветов и их коды не трогаем.
LABEL_FIX = {
    "Вишня Темная": "Вишня тёмная",
    "Орех Темный": "Орех тёмный",
    "Береза Белая": "Берёза белая",
    "Ясень Светлый": "Ясень светлый",
    "Бельгийский Кирпич": "Бельгийский кирпич",
    "Античный Дуб двухсторонний": "Античный дуб двухсторонний",
    "Зеленый лист": "Зелёный лист",
    "Зелёный Мох": "Зелёный мох",
}

# Один и тот же код в прайсе записан двумя способами — «RR 32» и «Granite RR32».
# Оба образца видны на одном экране, поэтому приводим написание к общему виду.
CODE_FIX = {
    "Granite RR32": "Granite RR 32",
}

# Порядок кружков внутри серии берём из json — там он уже как у поставщика
SERIES_ORDER = {}
for _slug, _c in COLORS.items():
    SERIES_ORDER.setdefault(_c["series"], []).append(_slug)

# Назначение материала. Единственное реальное различие внутри семейства —
# по нему и фильтруем (у кирпича это цвет, у плитки форма, здесь — задача).
TASKS = [("roof", "Крыша"), ("fence", "Забор"), ("wall", "Стены и фасад"),
         ("span", "Навесы и перекрытия"), ("soffit", "Подшивка свесов")]
TASK_TITLE = dict(TASKS)

MCH = [
    dict(
        id="mch-monterrey", name="Супермонтеррей",
        kind="Металлочерепица",
        meta="классический профиль под черепицу",
        task=["roof"],
        blurb="Классика загородных крыш: профиль повторяет керамическую "
              "черепицу. Самый частый выбор для скатной кровли.",
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
        task=["roof"],
        blurb="Модули со сдвигом, как у настоящей черепицы, и скрытое "
              "крепление — саморезов на крыше не видно.",
        use="крыша дома, где важен внешний вид — стыки листов не заметны, "
            "скат выглядит монолитным; уклон от 35°",
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
        meta="базовый профиль для сплошного забора",
        task=["fence", "wall"],
        blurb="Базовый профиль для сплошных заборов и обшивки стен: широкий "
              "лист, меньше стыков на той же площади.",
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
        meta="для высоких заборов и обшивки стен",
        task=["fence", "wall"],
        blurb="Жёстче С-8 — для высоких заборов и обшивки, где нужен "
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
        task=["fence", "roof", "span"],
        blurb="Симметричный профиль, одинаково аккуратный с обеих сторон — "
              "для заборов, которые видно с улицы и со двора, и простых крыш.",
        use="забор, который виден с двух сторон; крыша гаража, навеса, "
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
        task=["roof", "fence", "wall"],
        blurb="Кровельный вариант (тип R) с капиллярной канавкой: отводит "
              "воду из стыка листов и не даёт ей попасть под кровлю.",
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
        task=["roof", "span"],
        blurb="Высокая трапеция с рёбрами жёсткости: выдерживает снеговую "
              "нагрузку и разрежённую обрешётку — для крыш и навесов.",
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
        task=["span"],
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
        task=["fence"],
        blurb="Плавная линия верха — самая мягкая форма из трёх.",
        use="забор и палисадник с просветом — ниже ветровая нагрузка, двор "
            "не затеняется",
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
        task=["fence"],
        blurb="Трапециевидный рез — строже круглого, с чётким ритмом планок.",
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
        task=["fence"],
        blurb="Ровный срез без фигурного верха — самая лаконичная форма.",
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
        task=["wall"],
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
        task=["wall"],
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
        task=["wall"],
        blurb="Имитация деревянного бруса: с покрытием Printech фасад "
              "повторяет рисунок сруба.",
        use="фасад с рисунком дерева — не гниёт, не рассыхается, "
            "не требует покраски",
        specs=[
            ("Ширина панели", "270 мм (полезная — 220 мм)"),
            ("Длина", "режем в размер от 0,3 до 6 м"),
            ("Покрытие", "чаще заказывают Printech под дерево"),
        ],
    ),
    dict(
        id="sid-brus-riflenyy", name="Евробрус Рифлёный", kind="Металлосайдинг",
        meta="под брус · рифлёная поверхность",
        task=["wall"],
        blurb="Тот же брус, но с рифлением — глубже тень, фактурнее фасад.",
        use="фасад под дерево с выраженной фактурой",
        specs=[
            ("Ширина панели", "267 мм (полезная — 240 мм)"),
            ("Длина", "режем в размер от 0,3 до 6 м"),
            ("Покрытие", "чаще заказывают Printech под дерево"),
        ],
    ),
    dict(
        id="sid-sofit", name="Софит перфорированный", kind="Металлосайдинг",
        meta="подшивка свесов · с вентиляцией",
        task=["soffit"],
        blurb="Панель для подшивки свесов крыши: перфорация проветривает "
              "подкровельное пространство.",
        use="подшивка карнизных и фронтонных свесов — подкровельное "
            "пространство проветривается, птицы и насекомые внутрь не попадают",
        specs=[
            ("Ширина панели", "267 мм (полезная — 240 мм)"),
            ("Длина", "режем в размер от 0,3 до 6 м"),
            ("Перфорация", "по всей панели"),
        ],
    ),
]

ALL_PRODUCTS = MCH + PROF + SHT + SID
BY_ID = {p["id"]: p for p in ALL_PRODUCTS}

# Две ключевые цифры на карточку витрины: покупатель сравнивает профили именно
# по полезной ширине и высоте волны, а не по названию.
CARD_LINE = {
    "mch-monterrey": "Полезная ширина 1,10 м · волна 24 мм",
    "mch-dyuna": "Полезная ширина 1,04 м · волна 25–35 мм",
    "prof-s8": "Полезная ширина 1,15 м · волна 8 мм",
    "prof-s10": "Полезная ширина 1,10 м · волна 10 мм",
    "prof-s21": "Полезная ширина 1,00 м · волна 21 мм",
    "prof-mp20": "Полезная ширина 1,10 м · волна 20 мм",
    "prof-ns35": "Полезная ширина 1,00 м · волна 35 мм",
    "prof-n60": "Полезная ширина 0,845 м · волна 60 мм",
    "sht-kruglyy": "Ширина планки 130 мм · профиль 19,5 мм",
    "sht-trapetsiya": "Ширина планки 120 мм · профиль 19,5 мм",
    "sht-pryamoy": "Ширина планки 130 мм · профиль 19,5 мм",
    "sid-korabelnaya": "Полезная ширина 226 мм · профиль 14 мм",
    "sid-korabelnaya-evro": "Полезная ширина 229 мм · профиль 14 мм",
    "sid-brus-klassik": "Полезная ширина 220 мм · длина до 6 м",
    "sid-brus-riflenyy": "Полезная ширина 240 мм · длина до 6 м",
    "sid-sofit": "Полезная ширина 240 мм · с перфорацией",
}

# Семейства = подкатегории раздела. Путь как у конкурентов и как в плитке:
# хаб → семейство → товар → цвет.
FAMILIES = [
    dict(
        slug="metallocherepitsa", title="Металлочерепица", short="Металлочерепица",
        unit=("профиль", "профиля", "профилей"),
        products=MCH, cover="cover-cat-mch.jpg",
        cover_alt="Красная глянцевая металлочерепица с каплями дождя",
        tile="для скатной крыши",
        sub="Купить металлочерепицу в Краснодаре: два профиля с завода — "
            "крыша собирается без горизонтальных стыков.",
        note="Сталь с полимерным покрытием, 0,4–0,5 мм — точная толщина "
             "зависит от профиля. Расчёт цены и раскроя — по вашим размерам "
             "или чертежу.",
    ),
    dict(
        slug="profnastil", title="Профнастил", short="Профнастил",
        unit=("профиль", "профиля", "профилей"),
        products=PROF, cover="cover-cat-prof.jpg",
        cover_alt="Профнастил серо-синего цвета крупным планом",
        tile="крыша, забор, навес",
        sub="Купить профнастил в Краснодаре: шесть профилей — от лёгкого "
            "заборного С-8 до несущего Н-60. В каждом товаре фото, чертёж "
            "волны и все размеры.",
        note="Подберём марку профиля под задачу и рассчитаем количество "
             "листов по вашим размерам.",
    ),
    dict(
        slug="shtaketnik", title="Штакетник", short="Штакетник",
        unit=("форма верха", "формы верха", "форм верха"),
        products=SHT, cover="cover-cat-sht.jpg",
        cover_alt="Планки графитового евроштакетника крупным планом",
        tile="для забора с просветом",
        sub="Купить металлический штакетник в Краснодаре: планки с просветом — "
            "двор проветривается, ниже ветровая нагрузка. Три формы верха, "
            "цвета и рисунки под дерево.",
        note="Кромки завальцованы — без острых краёв. Образец цвета покажем "
             "перед заказом.",
    ),
    dict(
        slug="sayding", title="Металлосайдинг и софиты", short="Металлосайдинг",
        unit=("профиль", "профиля", "профилей"),
        products=SID, cover="cover-cat-sid.jpg",
        cover_alt="Металлосайдинг с фотопечатью под серое дерево крупным планом",
        tile="фасад и подшивка свесов", printech=True,
        sub="Купить металлосайдинг и софиты в Краснодаре: обшивка, которую "
            "не надо красить и пропитывать — металл с рисунком дерева "
            "не гниёт и не рассыхается.",
        note="Рисунок дерева — фотопечать Printech на стали. По фото дома "
             "подберём профиль и рассчитаем площадь обшивки.",
    ),
]
FAMILY_OF = {p["id"]: f for f in FAMILIES for p in f["products"]}

# Доборные, водосток и безопасность своих страниц не имеют: их подбирает
# менеджер в цвет кровли, поштучно их не выбирают.
KIT = [
    ("Доборные элементы", "Подбираем в цвет кровли",
     ["Конёк фигурный", "Конёк полукруглый", "Конёк-ребро", "Заглушки конька",
      "Планка карнизная", "Планка ветровая", "Планка лобовая",
      "Ендова верхняя и нижняя", "Планки примыкания", "Планки углов",
      "Планка снегозадержателя", "Планка диагональная", "L-планка заборная"]),
    ("Водосточные системы", "Круглая и прямоугольная, с крепежом",
     ["Круглая «Оптима» 125/90 — желоба, трубы, углы, воронки",
      "Прямоугольная гофрированная — желоба, трубы, колена",
      "Крюки, крепления и заглушки подбираем к системе"]),
    ("Безопасность кровли", "Снегозадержание и ограждения",
     ["Снегозадержатели трубчатые длиной 1 и 3 м",
      "Кровельные ограждения высотой 650 и 900 мм"]),
]

# Что люди набирают в поиске — ссылки внизу хаба (приём Лемана и ВИ).
# Параметр ?task= подхватывает фильтр витрины: ссылка открывает готовую выдачу.
OFTEN = [
    ("Профнастил на забор", "krovlya-profnastil.html?task=fence"),
    ("Профнастил на крышу", "krovlya-profnastil.html?task=roof"),
    ("Металлочерепица", "krovlya-metallocherepitsa.html"),
    ("Штакетник под дерево", "krovlya-shtaketnik.html"),
    ("Сайдинг на фасад", "krovlya-sayding.html?task=wall"),
    ("Софиты для свесов", "krovlya-sayding.html?task=soffit"),
    ("Доборные и водосток", "krovlya.html#dobornye"),
    ("Расчёт площади крыши", "krovlya.html#calc"),
]


# ---------------------------------------------------------------------------
# Мелкие помощники
# ---------------------------------------------------------------------------
def src(name, root=""):
    return f"{root}img/roof/{name}?v={IMG_V}"


def full_name(p):
    """«Профнастил МП-20», но без дубля вида: «Евроштакетник круглый»,
    «Евробрус Классик» — имя уже говорит, что это за товар."""
    stems = ("штакетник", "софит", "доска", "брус")
    if any(s in p["name"].lower() for s in stems):
        return p["name"]
    return f'{p["kind"]} {p["name"]}'


def colors_of(p):
    return P_COLORS.get(p["id"], [])


def n_colors_text(n):
    return f'{n} {plural(n, "цвет", "цвета", "цветов")}'


# ---------------------------------------------------------------------------
# Кружки цветов
#
# Фотография образца — единственный способ показать матовый Granite и рисунок
# Printech: плоская заливка врёт. Путь к кадру приходит из данных, поэтому он
# и живёт в атрибуте style — так же, как кружки цвета в фильтрах (fgroup dots).
# Ссылки из кружка никуда нет: отдельной страницы у цвета не существует,
# поэтому это подписанная картинка, а не навигация.
# ---------------------------------------------------------------------------
def color_label(slug):
    c = COLORS[slug]
    return LABEL_FIX.get(c["label"], c["label"])


def color_code(slug):
    c = COLORS[slug]
    return CODE_FIX.get(c["code"], c["code"])


def swatch(slug, root=""):
    c = COLORS[slug]
    code = color_code(slug)
    label = color_label(slug) + (f" · {code}" if code else "")
    return (f'<a role="img" aria-label="Цвет: {esc(label)}" title="{esc(label)}" '
            f'style="background-image:url({src(c["sw"], root)})"></a>')


def colors_row(slugs, root="", cap=None, more_href=None):
    """
    Ряд кружков; если показываем не всё — следом пилюля «ещё N».

    Пилюля стоит СНАРУЖИ ряда осознанно: правило `.pd-colors a` задаёт ширину
    44px всем ссылкам внутри и сплющивает подпись — при крупном системном
    шрифте текст вылезал за экран.
    """
    shown = slugs[:cap] if cap else slugs
    dots = "".join(swatch(s, root) for s in shown)
    row = f'<div class="pd-colors">{dots}</div>'
    left = len(slugs) - len(shown)
    if left > 0 and more_href:
        row += (f'<p><a class="pd-colors-more" href="{more_href}">'
                f'Ещё {left} {plural(left, "цвет", "цвета", "цветов")}</a></p>')
    return row


def swatch_labeled(slug, root=""):
    """Образец с подписью: имя под кружком, код RAL — строкой ниже.
    Как в палитрах ИКЕА/Hornbach: искать цвет люди будут по имени,
    и на телефоне подсказка при наведении недоступна — подпись видима всегда."""
    c = COLORS[slug]
    code = f"<i>{esc(color_code(slug))}</i>" if c["code"] else ""
    return (f'<li><span role="img" aria-label="Цвет: {esc(color_label(slug))}" '
            f'style="background-image:url({src(c["sw"], root)})"></span>'
            f'<b>{esc(color_label(slug))}</b>{code}</li>')


def palette_sections(slugs, root=""):
    """
    Полная палитра, разбитая по сериям покрытий: сетка подписанных
    образцов вместо абзаца со всеми именами через «·».

    Каждая серия — отдельная секция: у заголовков и абзацев в этой вёрстке
    своих отступов нет, ритм задаёт только .section, иначе Granite слипается
    с полиэстером в одну простыню.
    """
    out = []
    for key, title, descr in SERIES:
        mine = [s for s in SERIES_ORDER.get(key, []) if s in slugs]
        if not mine:
            continue
        head = (f"{title} — {n_colors_text(len(mine))}" if key != "zink"
                else f"{title} — без покраски")
        cells = "".join(swatch_labeled(s, root) for s in mine)
        out.append(f'<h3>{esc(head)}</h3>'
                   f'<p class="note">{esc(descr)}</p>'
                   f'<ul class="swl">{cells}</ul>')
    return out


# ---------------------------------------------------------------------------
# Карточка витрины
# ---------------------------------------------------------------------------
def card_of(p, root="", eager=False):
    """Цен у кровли нет: карточка показывает «Цена по запросу» и ведёт
    в товар, где стоит кнопка «В заявку»."""
    entry = P_IMAGES[p["id"]]
    contain = False
    if entry["gallery"]:
        img, alt = entry["gallery"][0], full_name(p)
    elif entry["scheme"]:
        # Фото нет — показываем чертёж целиком, обрезать его нельзя
        img, alt = entry["scheme"], f'{full_name(p)} — чертёж профиля'
        contain = True
    else:
        img, alt = None, ""
    gal_urls = [src(g) for g in entry["gallery"]] if entry.get("gallery") else None
    return product_card(
        href=f"tovar/krovlya-{p['id']}.html", name=full_name(p),
        # ВАЖНО: путь без root — product_card подставит его сам,
        # иначе на страницах товара получается ../../img/…
        img=src(img) if img else None, alt=alt,
        price_html="", root=root,
        # Цен у кровли нет ни у одной позиции — но в заявку она кладётся так же,
        # как товар с ценой: список уходит менеджеру, он и называет стоимость.
        add={"id": p["id"], "name": full_name(p), "price": None, "unit": "шт",
             "img": src(img) if img else ""},
        img_contain=contain,
        meta=CARD_LINE[p["id"]],
        stock="Под заказ",
        shots=len(entry["gallery"]) + (1 if entry["scheme"] else 0),
        gallery=gal_urls,
        data=f' data-task="{"|".join(p["task"])}" data-price=""',
        eager=eager)


def task_filter(products):
    """Фильтр «Назначение» ставим только там, где задачи реально разные:
    у штакетника все три планки идут на забор — выбирать нечего."""
    cnt = {}
    for p in products:
        for t in p["task"]:
            cnt[t] = cnt.get(t, 0) + 1
    if len(cnt) < 2:
        return None
    opts = [(k, TASK_TITLE[k], cnt[k]) for k, _ in TASKS if k in cnt]
    return filters_panel(fgroup("Назначение", "task", opts))


# ---------------------------------------------------------------------------
# Хаб раздела
# ---------------------------------------------------------------------------
def family_tiles(active=None):
    out = []
    for f in FAMILIES:
        n = len(f["products"])
        note = f'{n} {plural(n, *f["unit"])} · {f["tile"]}'
        on = ' aria-current="page"' if f["slug"] == active else ""
        out.append(
            f'<a class="tile" href="krovlya-{f["slug"]}.html"{on}>'
            f'<strong>{esc(f["short"])}<span>{esc(note)}</span></strong>'
            f'<img src="{src(f["cover"])}" alt="{esc(f["cover_alt"])}" '
            f'width="320" height="240" loading="lazy"></a>')
    return f'<div class="tiles">{"".join(out)}</div>'


def kit_section():
    tiles, lists = [], []
    for title, short, items in KIT:
        tiles.append(f'<div class="tile"><strong>{esc(title)}'
                     f'<span>{esc(short)}</span></strong></div>')
        # В перечислении через запятую заглавные буквы посреди строки мешают,
        # но «L-планка» и «Оптима» так и остаются — строчной делаем только
        # первую букву и только если это обычное слово, а не аббревиатура
        low = [s[0].lower() + s[1:] if s[1:2].islower() else s for s in items]
        # Пункты склеиваем точкой с запятой: внутри пункта уже есть запятые
        # («желоба, трубы, углы»), и на запятой перечни сливались в один
        # нечитаемый список
        # Каждая группа — свой абзац: одной простынёй в три списка не читается
        lists.append(f'<p class="note"><b>{esc(title)}:</b> '
                     + esc("; ".join(low)) + ".</p>")
    return f"""
  <section class="section band" id="dobornye"><div class="wrap">
    <div class="section-head"><h2>Всё для крыши — сразу</h2>
      <a class="see-all" href="#lead">Рассчитать комплект</a></div>
    <div class="tiles">{"".join(tiles)}</div>
    {"".join(lists)}
  </div></section>"""


CALC_SECTION = f"""
  <section class="section" id="calc"><div class="wrap">
    <div class="calc">
      <h2>Предварительный расчёт площади крыши</h2>
      <p class="calc-sub">Оценка по габаритам дома — уклон и свесы учтены
        в расчёте.</p>
      <div class="calc-rows">
        <div class="calc-row">
          <label for="rcLen">Длина дома, м</label>
          <span class="calc-val"><input id="rcLen" type="number" inputmode="decimal"
            min="1" max="100" step="0.1" placeholder="10"></span>
        </div>
        <div class="calc-row">
          <label for="rcWid">Ширина дома, м</label>
          <span class="calc-val"><input id="rcWid" type="number" inputmode="decimal"
            min="1" max="100" step="0.1" placeholder="8"></span>
        </div>
        <div class="calc-row">
          <label for="rcType">Тип крыши</label>
          <span class="calc-val"><select id="rcType">
            <option value="1.4" selected>Двускатная</option>
            <option value="1.5">Вальмовая, четыре ската</option>
            <option value="1.15">Односкатная</option>
          </select></span>
        </div>
      </div>
      <p class="calc-out"><span class="calc-key">Площадь крыши</span>
        <b id="rcArea">—</b></p>
      <a class="btn btn--accent btn--wide" href="#lead">Заказать расчёт</a>
      <p class="calc-note">Расчёт предварительный: точный раскрой по листам,
        доборные и водосток менеджер рассчитает по вашим размерам или чертежу.</p>
    </div>
  </div></section>"""


def build_hub():
    n_prod = len(ALL_PRODUCTS)
    n_col = len(COLORS)

    body = f"""
  <section class="page-head"><div class="wrap">
    {crumbs_html([("Главная", "index.html"), ("Каталог", "index.html#catalog"),
                  ("Кровля, фасад и забор", None)])}
    <h1>Кровля, фасад и забор</h1>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="section-head"><h2>Выберите материал</h2></div>
    {family_tiles()}
    <p class="note">Режем листы в размер ската, доборные элементы подбираем
      в цвет кровли.</p>
  </div></section>

  <section class="section" id="tsveta"><div class="wrap">
    <div class="section-head"><h2>Один цвет — на всё</h2></div>
    <p class="page-sub">Лист, конёк, планки, водосток и саморезы — в одном
      тоне: кровля выглядит цельной.</p>
    {colors_row(list(COLORS))}
    <p class="note">Названия и коды цветов — в карточке профиля. На экране
      цвет передаётся неточно, перед заказом покажем образец.</p>
  </div></section>
{kit_section()}
{CALC_SECTION}

  <section class="section"><div class="wrap">
    <h2 class="section-head">Часто ищут</h2>
    <div class="applied">{"".join(f'<a class="chip" href="{h}">{esc(t)}</a>'
                                  for t, h in OFTEN)}</div>
  </div></section>
"""
    write_page(BASE / "krovlya.html", page_shell(
        "Кровля в Краснодаре — металлочерепица, профнастил, штакетник, сайдинг",
        f"Кровельные материалы, фасад и забор напрямую с заводов: {n_prod} "
        f"{plural(n_prod, 'профиль', 'профиля', 'профилей')} металлочерепицы, "
        f"профнастила, штакетника и металлосайдинга, {n_colors_text(n_col)}. "
        "Режем в размер, доборные в цвет. Доставка по Краснодару и краю, "
        "наличный и безналичный расчёт.",
        body, active="krovlya"))


# ---------------------------------------------------------------------------
# Витрина семейства
# ---------------------------------------------------------------------------
def build_family(f):
    items = f["products"]
    cards = "".join(card_of(p, eager=(i < 4)) for i, p in enumerate(items))
    filters = task_filter(items)
    slugs = colors_of(items[0])
    first = f"tovar/krovlya-{items[0]['id']}.html#tsveta"

    if filters:
        grid = (f'<div class="catalog-body">{filters}'
                f'{grid_shell(cards, page_size=24)}</div>')
    else:
        grid = grid_shell(cards, page_size=24)

    printech = ""
    if f.get("printech"):
        pics = "".join(
            f'<img src="{src(n)}" alt="Металлосайдинг с фотопечатью под дерево" '
            f'width="960" height="720" loading="lazy">'
            for n in IMG["printech_live"])
        printech = f"""
  <section class="section"><div class="wrap">
    <div class="section-head"><h2>Printech вживую</h2></div>
    <p class="page-sub">Так фотопечать под дерево выглядит на готовых панелях —
      рисунок не повторяется от планки к планке.</p>
    <div class="works">{pics}</div>
  </div></section>"""

    body = f"""
  <section class="page-head"><div class="wrap">
    {crumbs_html([("Главная", "index.html"), ("Кровля", "krovlya.html"),
                  (f["title"], None)])}
    <h1>{esc(f["title"])}</h1>
  </div></section>

  <section class="section"><div class="wrap">
    {toolbar(len(items), filters=bool(filters), has_prices=False)}
    {grid}
    <p class="note">{esc(f["note"])}</p>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="section-head"><h2>Цвета</h2>
      <a class="see-all" href="{first}">Вся палитра с названиями</a></div>
    <p class="page-sub">Доборные, планки и саморезы — в том же тоне.</p>
    {colors_row(slugs, cap=12, more_href=first)}
  </div></section>
{printech}
{filters_drawer() if filters else ""}
"""
    write_page(BASE / f"krovlya-{f['slug']}.html", page_shell(
        f"{f['title']} в Краснодаре — {len(items)} "
        f"{plural(len(items), *f['unit'])} с завода",
        f"{f['sub']} Режем в размер, {n_colors_text(len(slugs))}, доставка "
        "по Краснодару и краю, наличный и безналичный расчёт.",
        body, active="sayding" if f["slug"] == "sayding" else "krovlya"))


# ---------------------------------------------------------------------------
# Страница товара
# ---------------------------------------------------------------------------
def gallery_html(p, root):
    """Фото товара, чертёж профиля — последним кадром."""
    entry = P_IMAGES[p["id"]]
    shots = [(g, f"{full_name(p)} — фото {i}")
             for i, g in enumerate(entry["gallery"], 1)]
    if entry["scheme"]:
        shots.append((entry["scheme"],
                      f'{full_name(p)} — чертёж профиля с размерами'))
    if not shots:
        return (f'<div class="pd-main p-none">{ICON["photo-off"]}'
                f"<span>Фотографии пришлём по запросу</span></div>")

    main = (f'<div class="pd-main-wrap">'
            f'<img class="pd-main" id="pdMain" src="{src(shots[0][0], root)}" '
            f'alt="{esc(shots[0][1])}" width="960" height="720" fetchpriority="high">'
            f'<button class="pd-zoom" id="pdZoom" type="button" '
            f'aria-label="Открыть фото крупно">{ICON["zoom"]}</button></div>')
    thumbs = ""
    if len(shots) > 1:
        thumbs = '<div class="pd-thumbs">' + "".join(
            f'<button class="pd-thumb{" is-on" if i == 0 else ""}" type="button" '
            f'data-src="{src(g, root)}" aria-label="{esc(alt)}">'
            f'<img src="{src(g, root)}" alt="" width="76" height="76" loading="lazy">'
            f"</button>" for i, (g, alt) in enumerate(shots)) + "</div>"
    # Чертёж в квадратном кадре обрезается по краям — подписываем, что это
    # схема, иначе размеры на ней выглядят срезанными
    note = ""
    if entry["scheme"]:
        note = ('<p class="pd-note">Чертёж профиля с размерами — '
                "последний кадр галереи.</p>")
    return main + thumbs + note


def similar(p):
    """Соседи по семейству, а если их мало — ближайшие по задаче."""
    fam = FAMILY_OF[p["id"]]
    out = [q for q in fam["products"] if q["id"] != p["id"]]
    if len(out) < 4:
        same_task = [q for q in ALL_PRODUCTS
                     if q["id"] != p["id"] and q not in out
                     and set(q["task"]) & set(p["task"])]
        out += same_task
    return out[:4]


def build_product(p):
    root = "../"
    fam = FAMILY_OF[p["id"]]
    name = full_name(p)
    slugs = colors_of(p)
    n = len(slugs)
    entry = P_IMAGES[p["id"]]

    # «10–15» читалось как «не меньше десяти», хотя у полиэстера завод даёт
    # «до 10», а у цинка покрытия нет вовсе.
    terms = TERMS_ORDER + [
        # Диапазон, а не «до 15»: на этой же странице ниже написано, что
        # у полиэстера срок до 10 лет, и два числа спорили на одном экране.
        ("shield", "Срок службы покрытия по данным завода — от 10 до 15 лет "
                   "в зависимости от серии (см. «Цвета»)")]
    terms_html = ""
    for ic, t in terms:
        cls = ' class="is-wait"' if ic == "clock" else ""
        terms_html += f"<li{cls}>{ICON[ic]}<span>{esc(t)}</span></li>"

    specs = "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in p["specs"])

    add = (f'<button class="btn p-add" type="button" data-add '
           f'data-id="{esc(p["id"])}" data-name="{esc(name)}" data-price="" '
           f'data-unit="м²" data-img="{esc("img/roof/" + entry["gallery"][0]) if entry["gallery"] else ""}" '
           f'data-url="tovar/krovlya-{p["id"]}.html" data-root="{root}">В заявку</button>')

    sim = similar(p)
    sim_html = ""
    if sim:
        sim_html = f"""
  <section class="section"><div class="wrap">
    <div class="section-head"><h2>Смотрят вместе с этим</h2>
      <a class="see-all" href="{root}krovlya-{fam["slug"]}.html">В раздел «{esc(fam["short"])}»</a></div>
    <div class="p-grid{grid_cls(len(sim))}">
      {"".join(card_of(q, root=root) for q in sim)}</div>
  </div></section>"""

    printech = ""
    if p in SHT or p in SID:
        pics = "".join(
            f'<img src="{src(nm, root)}" alt="Покрытие Printech под дерево" '
            f'width="960" height="720" loading="lazy">'
            for nm in IMG["printech_live"])
        printech = f"""
  <section class="section"><div class="wrap">
    <div class="section-head"><h2>Printech вживую</h2></div>
    <p class="page-sub">Фотопечать под дерево на готовых панелях — рисунок
      не повторяется от планки к планке.</p>
    <div class="works">{pics}</div>
  </div></section>"""

    # Палитра: первая секция несёт заголовок, дальше по секции на серию,
    # закрывающая оговорка про оттенок — в последней
    blocks = palette_sections(slugs, root)
    palette = (f'\n  <section class="section" id="tsveta"><div class="wrap">'
               f'<div class="section-head"><h2>Цвета — {n} '
               f'{plural(n, "вариант", "варианта", "вариантов")}</h2></div>'
               f"{blocks[0]}</div></section>")
    for blk in blocks[1:]:
        palette += (f'\n  <section class="section"><div class="wrap">'
                    f"{blk}</div></section>")
    palette += ('\n  <section class="section"><div class="wrap">'
                '<p class="note">Фотография не передаёт оттенок точно. Перед '
                "заказом покажем образец цвета.</p></div></section>")

    # Под именем товара — целое предложение о профиле (blurb), а не короткий
    # ярлык meta: ярлык почти дословно повторял первую фразу описания
    # («Базовый профиль для сплошного забора» / «Базовый профиль для сплошных
    # заборов…»). Цифры ярлыка живут в CARD_LINE на витрине и в спеках ниже.
    body = f"""
  <section class="page-head"><div class="wrap">
    {crumbs_html([("Главная", f"{root}index.html"), ("Кровля", f"{root}krovlya.html"),
                  (fam["short"], f"{root}krovlya-{fam['slug']}.html"), (p["name"], None)])}
  </div></section>
  <section class="pd"><div class="wrap">
    <div class="pd-grid">
      <div class="pd-gallery">{gallery_html(p, root)}</div>
      <div class="pd-info">
        <p class="note">{esc(p["kind"])}</p>
        <h1 class="pd-name">{esc(name)}</h1>
        <p class="pd-meta">{esc(p["blurb"])}</p>
        <p class="pd-price"><b>Цена по запросу</b></p>
        <p class="pd-m2">Цена зависит от покрытия и толщины стали — рассчитаем
          по вашим размерам. Наличие и условия поставки подтверждаются
          при оформлении заказа.</p>
        <p class="pd-note">{n} {plural(n, "цвет", "цвета", "цветов")}
          и {plural(n, "рисунок", "рисунка", "рисунков")}. Доборные, планки
          и саморезы — в том же тоне.</p>
        {colors_row(slugs, root, cap=6, more_href="#tsveta")}
        <ul class="pd-terms">{terms_html}</ul>
        <div class="pd-bar">{add}
          <a class="btn btn--call pd-bar-call" href="{PHONE_HREF}"
             aria-label="Позвонить">{ICON["phone"]}<span>Позвонить</span></a>
        </div>
        <p class="pd-note">Область применения: {esc(p["use"])}.</p>
        <div class="pd-specs"><h2>Характеристики</h2><dl>{specs}</dl></div>
      </div>
    </div>
  </div></section>

{palette}
{printech}{sim_html}
"""
    ld = {"@context": "https://schema.org", "@type": "Product", "name": name,
          "description": f"{name}: {p['use']}.",
          "category": fam["title"],
          "brand": {"@type": "Brand", "name": "Стройсейл"}}
    if entry["gallery"]:
        ld["image"] = SITE_URL + "img/roof/" + entry["gallery"][0]
    head = ('\n  <script type="application/ld+json">'
            + json.dumps(ld, ensure_ascii=False) + "</script>")

    write_page(BASE / "tovar" / f"krovlya-{p['id']}.html", page_shell(
        f"{name} — купить в Краснодаре",
        f"{name}: {p['use']}. {n_colors_text(n)}, режем в размер. Цена "
        "по запросу, доставка по Краснодару и краю, наличный и безналичный "
        "расчёт.",
        body, root=root, extra_head=head,
        active="sayding" if fam["slug"] == "sayding" else "krovlya"))


# ---------------------------------------------------------------------------
def main():
    build_hub()
    for f in FAMILIES:
        build_family(f)
    for p in ALL_PRODUCTS:
        build_product(p)
    print(f"кровля: хаб + {len(FAMILIES)} семейств + {len(ALL_PRODUCTS)} товаров")


if __name__ == "__main__":
    main()
