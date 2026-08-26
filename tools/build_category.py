"""
Кирпич: витрина категории, коллекции, забутовка и страницы товара.

Собирает:
    kirpich-oblitsovochnyy.html    — витрина всех облицовочных с фильтрами
    collection-<slug>.html × 5     — та же витрина внутри одной коллекции
    kirpich-zabutovochnyy.html     — забутовочный, фильтр по задаче
    tovar/kirpich-<id>.html × 282  — страницы товара

Данные: _data/catalog.json (готовит tools/parse_catalog.py).
Фотографии: img/catalog/<id>.jpg и <id>-2..7.jpg (готовит tools/build_images.py) —
наличие проверяется по диску, а не по списку в json.

Оболочка, карточка и фильтры — общие модули shell_common и catalog_common;
здесь только то, что специфично для кирпича.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_common import (fgroup, filters_drawer, filters_panel, fprice,
                            grid_shell, toolbar)
from shell_common import (BASE, ICON, PHONE_HREF, SITE_URL, TERMS_ORDER,
                          TERMS_STOCK, VIEWPORT, crumbs_html, esc, grid_cls,
                          page_shell, plural, price_split, product_card, rub,
                          spec_dd, wa_link, write_page)

DATA = json.loads((BASE / "_data" / "catalog.json").read_text())
CAT_IMG = BASE / "img" / "catalog"
IMG_V = 10          # версия кэша картинок каталога

# ---------------------------------------------------------------------------
# Справочники
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Заводы-производители.
#
# 17.08.2026, решение владельца: витрина показывает НАСТОЯЩИЕ имена заводов —
# так устроены все большие магазины стройматериалов (у Славдома это «Бренд»
# и «Завод российского кирпича», у Леманы — «Бренд»). Прежние выдуманные
# коллекции («Классика», «Палитра», «Европа», «Ручная формовка», «Эконом»)
# отменены: покупатель ищет «Тербунский гончар», а не «Эконом».
#
# КЛЮЧИ НЕ ТРОГАТЬ. Первые три буквы ключа — префикс id товара (kla-001,
# pal-014…), а id стоит в адресе всех 284 товарных страниц. Меняются только
# подписи (title/short/desc/use) и имена файлов страниц (slug).
# ---------------------------------------------------------------------------
# Описания — ТОЛЬКО то, что проверяется по нашей же базе (цвета, фактуры,
# форматы, цены считаются из catalog.json и видны покупателю в фильтре рядом).
# Аудит 17.08.2026 поймал в первой редакции три выдумки: «оборудование Hans
# Lingl» приписали Славянскому (в источниках Lingl упомянут у ГУБСКОГО —
# лаборатория, где мерили глину), фактуру «скала» — Донскому (её нет в базе
# вообще), и два взаимоисключающих «самый широкий выбор» на соседних плитках.
# Правило: если утверждение нельзя проверить по catalog.json — его тут нет.
COLLECTIONS = {
    "klassika": {"title": "Донской кирпич", "short": "Донской", "slug": "zavod-donskoy",
                 "desc": "47 видов: 6 цветов и 9 фактур — от гладкой до бересты, "
                         "антика и руста. Форматы одинарный, полуторный и длинный WDF.",
                 "use": "Применение: фасад дома и забор, когда нужен ровный предсказуемый результат."},
    "palitra": {"title": "Губский кирпичный завод", "short": "Губский", "slug": "zavod-gubskiy",
                "desc": "Краснодарский край. 65 видов, 8 цветов — от пшеничного "
                        "до графита; одинарный формат, фактуры от гладкой до коры.",
                "use": "Применение: фасады, где цвет задан проектом и нужен точный оттенок."},
    "formovka": {"title": "Тандем", "short": "Тандем", "slug": "zavod-tandem",
                 "desc": "Кирпич ручной формовки: неровная «живая» грань, как у старой "
                         "европейской кладки. 99 видов в длинных форматах WDF, WMF, "
                         "лонг и ригель.",
                 "use": "Применение: дома в европейском стиле, камины и входные группы."},
    "evropa": {"title": "Славянский кирпич", "short": "Славянский", "slug": "zavod-slavyanskiy",
               "desc": "Славянск-на-Кубани. 26 видов в одинарном и евроформате, "
                       "фактуры кроста, руст, антик и ретро.",
               "use": "Применение: современные фасады — длинный формат зрительно растягивает стену."},
    "ekonom": {"title": "Тербунский гончар", "short": "Тербунский", "slug": "zavod-terbunskiy",
               "desc": "Липецкая область. 27 видов, 6 цветов, гладкая фактура "
                       "и «старый город». Цена от 18,50 ₽/шт.",
               "use": "Применение: фасады жилых домов, коттеджей и заборов — высокая морозостойкость и прочность."},
}
COLL_ORDER = ["palitra", "evropa", "klassika", "ekonom", "formovka"]

# Старые адреса страниц. Сайт лежит на GitHub Pages — серверных редиректов там
# нет, поэтому на старых путях остаются страницы-заглушки с meta refresh.
OLD_COLL_PAGES = {s: f"collection-{s}.html" for s in COLL_ORDER}

# Имя завода по полю supplier из данных. Нужно забутовке: у неё collection
# не задан (подкатегория там — задача, а не производитель), но показать,
# чей это кирпич, всё равно надо.
SUPPLIER_TITLE = {
    "Донской": "Донской кирпич",
    "Губский": "Губский кирпичный завод",
    "Тандем": "Тандем",
    "Славянский": "Славянский кирпич",
    "Тербунский гончар": "Тербунский гончар",
}

COLOR_ORDER = ["красный", "коричневый", "бежевый", "персиковый", "серый",
               "графит", "микс (бавария)", "зелёный"]
COLOR_LABEL = {"микс (бавария)": "Баварская кладка"}

# Фактура. Сверху то, что понятно частному застройщику, ниже — торговые
# названия рельефа у заводов (береста, кроста, бриз): по непонятному слову
# не кликают, поэтому оно не должно стоять первым.
TEX_ORDER = ["гладкий", "ручная формовка", "рельефный", "фактурный", "руст",
             "старый город", "антик", "ретро", "винтаж"]
# «Ручная формовка» — ещё и имя коллекции. В фильтре уточняем, что здесь
# речь о поверхности, иначе на одном экране два разных числа под одним словом.
TEX_LABEL = {"ручная формовка": "Ручная формовка (поверхность)"}

# Формат: «1НФ» знают прорабы, «одинарный» — частные застройщики.
# В фильтре даём оба слова, в имени товара — человеческое.
FMT_FILTER = {
    "1НФ (одинарный)": "Одинарный 1НФ",
    "1,4НФ (полуторный)": "Полуторный 1,4НФ",
    "0,7НФ (евро)": "Евро 0,7НФ",
    "0,9НФ": "Утолщённый 0,9НФ",
    "WDF": "Длинный WDF",
    "WMF": "Длинный WMF",
    "Лонг LF": "Лонг LF",
    "Ригель MF": "Ригель MF",
}
FMT_NAME = {
    "1НФ (одинарный)": "одинарный",
    "1,4НФ (полуторный)": "полуторный",
    "0,7НФ (евро)": "евро",
    "0,9НФ": "0,9НФ",
    "WDF": "WDF",
    "WMF": "WMF",
    "Лонг LF": "лонг",
    "Ригель MF": "ригель",
}

# Новинки заводов. Флага в данных нет, список ведём руками — ключ по имени.
NOVINKI = {
    "Баварский классик", "Баварский светлый", "Булат", "Винтаж лайт", "Винтаж премиум",
    "Коричневый сахара", "Красный сахара", "Солома сахара", "Коричневый скала антик",
    "Красный скала антик", "Светлый береста", "Светлый крафт", "Светлый терра",
    "Тёмно-коричневый", "СС-УС-01", "СС-УС-02", "СС-УС-03", "СС-УС-04", "СС-УС-05",
    "СС-УС-06", "УС-01.04", "Арес", "Марс 01", "Марс 02", "Марс 03",
}

# Что люди набирают в поиске — ссылки внизу витрины (приём Лемана и ВИ)
# Подпись чипа = имя фильтра, на который он ведёт. «Под старину» вело на одну
# фактуру из трёх (антик, старый город, ретро) — покупатель видел 6 позиций
# вместо 21 и решал, что выбора нет.
OFTEN = [("Баварская кладка", "color=микс (бавария)"), ("Графитовый", "color=графит"),
         ("Бежевый", "color=бежевый"), ("Красный", "color=красный"),
         ("Кирпич ручной формовки", "tex=ручная формовка"), ("Длинный кирпич", "fmt=WDF"),
         ("Гладкий", "tex=гладкий"), ("Антик", "tex=антик"),
         ("Старый город", "tex=старый город")]

PRODUCTS = [p for p in DATA["products"] if p["category"] == "oblitsovochnyy"]
RAB = [p for p in DATA["products"] if p["category"] == "obychnyy"]

# Забутовка: заводские имена нечитаемы («Одинарный полнотелый М150 (F25…) 480шт
# упак. лентой»), поэтому имя/пояснение/задачи ведём руками. Ключ — factory_name:
# id сдвигаются при добавлении товаров, имя завода — нет.
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


TASKS = [("fund", "Фундамент и цоколь"), ("walls", "Несущие стены"),
         ("inner", "Перегородки и хозпостройки")]


# ---------------------------------------------------------------------------
# Подготовка
# ---------------------------------------------------------------------------
def _gallery(p):
    """Файлы галереи, которые РЕАЛЬНО лежат на диске (список в json бывает старым)."""
    out = []
    if (CAT_IMG / f"{p['id']}.jpg").exists():
        out.append(f"img/catalog/{p['id']}.jpg")
    for i in range(2, 8):
        if (CAT_IMG / f"{p['id']}-{i}.jpg").exists():
            out.append(f"img/catalog/{p['id']}-{i}.jpg")
    return out


for _p in DATA["products"]:
    _p["_gal"] = _gallery(_p)
    # Габариты у поставщиков записаны по-разному: «250×120×65 мм», «250×120×65 см»
    # (у Донского «см» — описка завода, на деле миллиметры) и просто числами.
    # Приводим к голым числам, единицу дописываем сами при выводе.
    _dims = (_p.get("specs") or {}).get("Габариты", "")
    for _u in (" мм", " см", "мм", "см"):
        _dims = _dims.replace(_u, "")
    _p["_dims"] = _dims.strip()


def nice_name(p):
    """«Кирпич Абрикос гладкий, одинарный 250×120×65» — как на витринах."""
    parts = ["Кирпич", p["name"]]
    tex = (p.get("texture") or "").strip()
    if tex and tex.lower() not in p["name"].lower() and tex != "ручная формовка":
        parts.append(tex)
    head = " ".join(parts)
    tail = FMT_NAME.get(p.get("format"), p.get("format") or "")
    # У «Абрамцево 0,5WDF» формат уже назван в самом имени — второй раз
    # в хвосте он читается как заикание («Абрамцево 0,5WDF, WDF»).
    if tail and tail.lower() in p["name"].lower():
        return f"{head}, {p['_dims']}" if p.get("_dims") else head
    if tail and p.get("_dims"):
        return f"{head}, {tail} {p['_dims']}"
    return f"{head}, {tail}" if tail else head


# Ложковая грань стандартных российских форматов (длина × высота, мм).
# Только они закреплены ГОСТ 530-2012 и одинаковы у всех заводов.
# Европейские WDF / WMF / лонг / ригель сюда НЕ входят: у каждого завода
# свой размер, а в наших данных его нет — значит, ₽/м² для них не печатаем.
FORMAT_FACE = {
    "1НФ (одинарный)": (250, 65),
    "1,4НФ (полуторный)": (250, 88),
    "0,7НФ (евро)": (250, 65),
    "0,9НФ": (250, 60),
}


def per_m2(p):
    """
    Сколько кирпичей уходит на м² кладки.

    Берём из спецификации завода, если она есть. Если нет — СЧИТАЕМ
    по габаритам: на м² укладывается 1 / ((длина + шов) × (высота + шов)),
    шов 10 мм. Для одинарного 250×120×65 формула даёт 51,3 — ровно то,
    что пишут заводы.

    Раньше здесь стояла константа 51,4 для всего, кроме полуторного.
    Для длинных европейских форматов (WDF, лонг, ригель — 105 товаров)
    это было ПРОСТО НЕВЕРНО: у ригеля 290×40 расход почти 67 шт/м².
    Такую цифру человек проверяет первой, и ошибка в ней — ошибка в смете.
    """
    per = p.get("consumption_per_m2")
    if per:
        return per
    dims = (p.get("_dims") or "").split("×")
    face = None
    if len(dims) == 3:
        try:
            face = (float(dims[0].replace(",", ".")), float(dims[2].replace(",", ".")))
        except ValueError:
            face = None
    if face is None:
        face = FORMAT_FACE.get(p.get("format"))
    if not face or not all(face):
        return None      # размеров нет — молчим, а не выдумываем
    return round(1 / (((face[0] + 10) / 1000) * ((face[1] + 10) / 1000)), 1)


def pallet_qty(p):
    """
    Сколько штук в поддоне у ЭТОГО товара.

    Заводы записывают это тремя разными способами:
      · «На поддоне»: 480            — прямое число (Тандем);
      · «Штук на поддоне»: 352       — то же другими словами;
      · «Количество на поддоне (1.4НФ, 1НФ, 0,9НФ, 0.7НФ), (шт)»: «352, 480, 484, 660»
        — Губский пишет ОДНОЙ графой числа сразу для четырёх форматов, в том
        порядке, в каком форматы перечислены в названии графы.
    Из последней берём число, соответствующее формату товара; если формат
    в перечне не нашёлся — молчим, а не подставляем первое попавшееся.
    """
    specs = p.get("specs") or {}
    for key in ("На поддоне", "Штук на поддоне"):
        v = str(specs.get(key, "")).strip()
        if v.isdigit():
            return int(v)
    for key, val in specs.items():
        if not key.startswith("Количество на поддоне"):
            continue
        fmts = [float(x.replace(",", ".")) for x in re.findall(r"(\d+[.,]?\d*)\s*НФ", key)]
        nums = [x.strip() for x in str(val).split(",")]
        if len(fmts) != len(nums) or not all(n.isdigit() for n in nums):
            return None
        m = re.match(r"(\d+[.,]?\d*)\s*НФ", p.get("format") or "")
        if not m:
            return None
        want = float(m.group(1).replace(",", "."))
        for f, n in zip(fmts, nums):
            if abs(f - want) < 1e-6:
                return int(n)
    return None


def qty_block(p, unit="шт"):
    """
    Счётчик количества над кнопкой заказа (макет заказчика, блок 4d).

    Человек редко покупает одну штуку: он покупает стену. Поэтому рядом со
    счётчиком идут две подсказки — сколько штук в поддоне (из спецификации
    завода, если она там есть) и во сколько квадратов кладки это выльется.
    Второе считает app.js по data-per: цифра меняется вместе с количеством.
    """
    per = per_m2(p)
    pallet = pallet_qty(p)
    pal, start = "", 1
    if pallet:
        start = pallet                            # кирпич возят поддонами
        pal = f" · на поддоне {rub(pallet)} шт"
    out = '<span data-qty-out></span>' if per else ""
    data_per = f' data-per="{per}"' if per else ""
    return f"""<div class="pd-buy">
          <span class="qty" data-qty-box{data_per}>
            <button type="button" data-step="-1" aria-label="Меньше">−</button>
            <input type="text" inputmode="numeric" value="{start}" aria-label="Количество, {unit}">
            <button type="button" data-step="1" aria-label="Больше">+</button>
          </span>
          <p class="pd-qty-note"><b>{unit}{pal}</b>{out}</p>
        </div>"""


def m2_price(p):
    """Цена за м² кладки — то, чем кирпич считают на самом деле."""
    per = per_m2(p)
    if not p.get("price") or not per:
        return None
    return round(p["price"] * per / 10) * 10


def price_html(p):
    if not p.get("price"):
        return ""
    return price_split(p["price"], "шт")


def m2_text(p):
    v = m2_price(p)
    return f"= {rub(v)} ₽/м² кладки" if v else ""


def zavod_line(p, root=""):
    """Строка «Завод: …» под именем товара.

    У облицовочного завод = коллекция и ведёт на его страницу. У забутовки
    коллекции нет (подкатегория там — задача), но производителя показать надо:
    берём его из поля supplier. Без этого рядовой кирпич был единственным
    разделом, где покупатель не видел, чей товар.
    """
    coll = p.get("collection")
    if coll:
        c = COLLECTIONS[coll]
        return (f'<a class="pd-zavod" href="{root}{c["slug"]}.html">'
                f'Завод: <i>{esc(c["title"])}</i></a>')
    title = SUPPLIER_TITLE.get(p.get("supplier"))
    return f'<span class="pd-zavod">Завод: <i>{esc(title)}</i></span>' if title else ""


def stock_text(p):
    """Честная строка срока. Остатков у нас нет (менеджер их не дал), поэтому
    обещаем только то, что знаем точно: цена есть — возим постоянно, цены нет —
    позиция под заказ. Когда появятся реальные остатки, править ЗДЕСЬ."""
    return "Поставка с завода" if p.get("price") else "Под заказ"


def sort_key(p):
    """Цвет → популярные заводы перед ручной формовкой → цена по возрастанию."""
    ci = COLOR_ORDER.index(p["color_group"]) if p["color_group"] in COLOR_ORDER else 99
    is_premium = 1 if p.get("collection") == "formovka" else 0
    price_val = p.get("price") or 9999
    return (ci, is_premium, price_val, p["name"].lower())


def card_of(p, root="", eager=False):
    img = f"{p['_gal'][0]}?v={IMG_V}" if p["_gal"] else None
    data = (f' data-color="{esc(p["color_group"])}"'
            f' data-texture="{esc(p.get("texture") or "")}"'
            f' data-format="{esc(p.get("format") or "")}"'
            f' data-coll="{esc(p.get("collection") or "")}"'
            f' data-price="{p.get("price") or ""}"')
    if p["name"] in NOVINKI:
        data += ' data-new="1"'
    # Кнопка заявки есть и у позиций БЕЗ цены: «узнайте цену отдельно» —
    # это тупик, из которого не возвращаются. Такая позиция попадает
    # в тот же список к менеджеру, просто с пустым data-price.
    add = {"id": p["id"], "name": nice_name(p), "price": p.get("price"), "unit": "шт",
           "img": p["_gal"][0] if p["_gal"] else ""}
    # Второй кадр для наведения — только если он реально есть на диске.
    alt_img = f"{p['_gal'][1]}?v={IMG_V}" if len(p["_gal"]) > 1 else None
    coll = p.get("collection")
    gal_urls = [f"{g}?v={IMG_V}" for g in p["_gal"]] if p.get("_gal") else None
    return product_card(
        href=f"tovar/kirpich-{p['id']}.html", name=nice_name(p), img=img,
        alt=nice_name(p), price_html=price_html(p), m2=m2_text(p),
        badge="Новинка" if p["name"] in NOVINKI else None,
        meta=COLLECTIONS[coll]["title"] if coll else "",
        stock=stock_text(p), shots=len(p["_gal"]), gallery=gal_urls,
        data=data, root=root, add=add, eager=eager, alt_img=alt_img)


# ---------------------------------------------------------------------------
# Фильтры
# ---------------------------------------------------------------------------
def color_dots(items):
    """Кружок цвета — настоящая фотография кирпича, а не плоская заливка."""
    out = {}
    for p in items:
        g = p["color_group"]
        if g not in out and (CAT_IMG / f"cdot-{p['id']}.jpg").exists():
            out[g] = f"img/catalog/cdot-{p['id']}.jpg?v={IMG_V}"
    return out


def facet(items, key, order=None, label=None):
    """Значения фасета с количествами — счётчик у фильтра сильно помогает выбирать."""
    cnt = {}
    for p in items:
        v = p.get(key)
        if v:
            cnt[v] = cnt.get(v, 0) + 1
    keys = ([k for k in order if k in cnt]
            + sorted([k for k in cnt if k not in order], key=lambda k: -cnt[k])
            if order else sorted(cnt, key=lambda k: -cnt[k]))
    lab = label or {}
    return [(k, lab.get(k, k[:1].upper() + k[1:]), cnt[k]) for k in keys]


def brick_filters(items, *, with_coll=True):
    prices = [p["price"] for p in items if p.get("price")]
    groups = []
    if with_coll:
        coll = [(s, COLLECTIONS[s]["title"],
                 sum(1 for p in items if p.get("collection") == s))
                for s in COLL_ORDER if any(p.get("collection") == s for p in items)]
        groups.append(fgroup("Производитель (завод)", "coll", coll))
    groups.append(fprice(rub(min(prices)) if prices else "0",
                         rub(max(prices)) if prices else "0"))
    groups.append(fgroup("Цвет", "color",
                         facet(items, "color_group", COLOR_ORDER, COLOR_LABEL),
                         dots=color_dots(items)))
    groups.append(fgroup("Фактура", "texture",
                         facet(items, "texture", TEX_ORDER, TEX_LABEL)))
    groups.append(fgroup("Формат", "format", facet(items, "format", label=FMT_FILTER)))
    if any(p["name"] in NOVINKI for p in items):
        groups.append(fgroup("", "new", [("1", "Только новинки",
                                          sum(1 for p in items if p["name"] in NOVINKI))]))
    return filters_panel("".join(groups))


def coll_tiles(active=None):
    """Лента заводов над выдачей.

    Компактная строка «фото + имя + сколько видов», как ряд подкатегорий
    у Леманы: она помещается над выдачей целиком и не отодвигает товар вниз.
    Прежние большие плитки занимали пол-экрана и повторяли то же самое.
    """
    out = []
    for slug in COLL_ORDER:
        items = [p for p in PRODUCTS if p.get("collection") == slug]
        if not items:
            continue
        c = COLLECTIONS[slug]
        prices = [p["price"] for p in items if p.get("price")]
        note = (f"{len(items)} {plural(len(items), 'вид', 'вида', 'видов')}"
                + (f" · от {rub(min(prices))} ₽" if prices else ""))
        pic = next((f"img/catalog/cdot-{p['id']}.jpg" for p in items
                    if (CAT_IMG / f"cdot-{p['id']}.jpg").exists()), None)
        img = (f'<img src="{pic}?v={IMG_V}" alt="" width="56" height="56" loading="lazy">'
               if pic else '<span class="zv-none"></span>')
        on = ' aria-current="page"' if slug == active else ""
        out.append(f'<a class="zv" href="{c["slug"]}.html"{on}>{img}'
                   f'<span><b>{esc(c["title"])}</b><small>{note}</small></span></a>')
    return f'<div class="zv-row">{"".join(out)}</div>'


def often_html(base="kirpich-oblitsovochnyy.html"):
    links = "".join(f'<a class="chip" href="{base}?{q}">{esc(t)}</a>' for t, q in OFTEN)
    return (f'<div class="section"><div class="wrap"><h2 class="section-head">Часто ищут</h2>'
            f'<div class="applied">{links}</div></div></div>')



# Расход кирпича на м² кладки. 51,4 — из спецификации завода (одинарный),
# остальные посчитаны по габаритам и толщине шва 10 мм. Длинные европейские
# форматы в калькулятор не выносим: их кладут по-разному, считает менеджер.
CALC_FORMATS = [("51.4", "Одинарный 1НФ — 250×120×65"),
                ("39.2", "Полуторный 1,4НФ — 250×120×88"),
                ("51.4", "Евро 0,7НФ — 250×85×65")]


def calc_block():
    """Калькулятор кирпича: площадь стен минус проёмы → штуки.

    Разметку читает модуль brickCalc в app.js по id полей.
    """
    opts = "".join(f'<option value="{v}">{esc(t)}</option>' for v, t in CALC_FORMATS)
    return f"""
  <section class="section" id="calc"><div class="wrap">
    <div class="calc">
      <h2>Сколько нужно кирпича</h2>
      <p class="calc-sub">Считаем по площади стен: проёмы вычитаем,
        5&nbsp;% добавляем на подрезку и бой.</p>
      <div class="calc-rows">
        <div class="calc-row">
          <label for="bcWall">Площадь стен, м²</label>
          <span class="calc-val"><input id="bcWall" type="number" inputmode="decimal"
            min="1" max="10000" step="1" value="120"></span>
        </div>
        <div class="calc-row">
          <label for="bcOpen">Окна и двери, м²</label>
          <span class="calc-val"><input id="bcOpen" type="number" inputmode="decimal"
            min="0" max="10000" step="1" value="18"></span>
        </div>
        <div class="calc-row">
          <label for="bcFmt">Формат кирпича</label>
          <span class="calc-val"><select id="bcFmt">{opts}</select></span>
        </div>
        <div class="calc-row">
          <span class="calc-key">Чистая площадь кладки</span>
          <span class="calc-val" id="bcArea">—</span>
        </div>
      </div>
      <p class="calc-out"><span class="calc-key">Нужно кирпича</span>
        <b id="bcQty">—</b></p>
      <a class="btn btn--accent btn--wide" href="#lead">Заказать расчёт</a>
      <p class="calc-note">Это ориентир: фактический расход зависит от толщины
        шва, перевязки и сложности фасада. Точное количество по проекту
        посчитает менеджер.</p>
    </div>
  </div></section>"""


# ---------------------------------------------------------------------------
# Витрина категории и коллекций
# ---------------------------------------------------------------------------
def build_category():
    items = sorted(PRODUCTS, key=sort_key)
    cards = "".join(card_of(p, eager=(i < 4)) for i, p in enumerate(items))
    prices = [p["price"] for p in items if p.get("price")]
    lo = rub(min(prices))

    body = f"""
  <section class="page-head"><div class="wrap">
    {crumbs_html([("Главная", "index.html"), ("Каталог", "index.html#catalog"),
                  ("Облицовочный кирпич", None)])}
    <h1>Облицовочный кирпич<span class="h1-n">{len(items)} {plural(len(items), 'вид', 'вида', 'видов')}</span></h1>
    {coll_tiles()}
  </div></section>

  <section class="section"><div class="wrap">
    {toolbar(len(items))}
    <div class="catalog-body">
      {brick_filters(items)}
      {grid_shell(cards)}
    </div>
  </div></section>
{calc_block()}
{often_html()}
{filters_drawer()}
"""
    write_page(BASE / "kirpich-oblitsovochnyy.html", page_shell(
        f"Облицовочный кирпич в Краснодаре — {len(items)} "
        f"{plural(len(items), 'вид', 'вида', 'видов')}, цены от {lo} ₽",
        f"Облицовочный кирпич напрямую с заводов: {len(items)} {plural(len(items), 'вид', 'вида', 'видов')} "
        f"от 5 заводов, цены от {lo} ₽/шт. Доставка по Краснодару и краю, "
        f"наличный и безналичный расчёт.",
        body, active="oblic"))


def build_collection(slug):
    """Страница завода: та же витрина, отфильтрованная по производителю."""
    items = sorted([p for p in PRODUCTS if p.get("collection") == slug], key=sort_key)
    if not items:
        return
    c = COLLECTIONS[slug]
    cards = "".join(card_of(p, eager=(i < 4)) for i, p in enumerate(items))
    prices = [p["price"] for p in items if p.get("price")]
    note = f"от {rub(min(prices))} ₽/шт" if prices else "цена по запросу"

    body = f"""
  <section class="page-head"><div class="wrap">
    {crumbs_html([("Главная", "index.html"),
                  ("Облицовочный кирпич", "kirpich-oblitsovochnyy.html"),
                  (c["title"], None)])}
    <h1>{esc(c["title"])}<span class="h1-n">{len(items)} {plural(len(items), 'вид', 'вида', 'видов')}</span></h1>
    <p class="page-sub">{esc(c["desc"])}</p>
  </div></section>

  <section class="section"><div class="wrap">
    {toolbar(len(items))}
    <div class="catalog-body">
      {brick_filters(items, with_coll=False)}
      {grid_shell(cards)}
    </div>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="section-head"><h2>Другие заводы</h2>
      <a class="see-all" href="kirpich-oblitsovochnyy.html">Весь облицовочный кирпич</a></div>
    {coll_tiles(active=slug)}
  </div></section>
{filters_drawer()}
"""
    write_page(BASE / f"{c['slug']}.html", page_shell(
        f"{c['title']} — облицовочный кирпич, {len(items)} "
        f"{plural(len(items), 'вид', 'вида', 'видов')}, Краснодар",
        f"{c['title']}: {len(items)} "
        f"{plural(len(items), 'вид', 'вида', 'видов')} облицовочного кирпича, {note}. "
        f"Доставка по Краснодару и краю, наличный и безналичный расчёт.",
        body, active="oblic"))
    build_redirect(OLD_COLL_PAGES[slug], f"{c['slug']}.html", c["title"])


def build_redirect(old, new, title):
    """Заглушка на старом адресе страницы.

    Страницы коллекций переименованы в страницы заводов, а сайт лежит на
    GitHub Pages — серверных 301 там нет. Заглушка уводит и человека,
    и поисковик: canonical + refresh + видимая ссылка, если скрипты выключены.
    """
    write_page(BASE / old, f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  {VIEWPORT}
  <title>{esc(title)} — страница переехала</title>
  <meta name="robots" content="noindex, follow">
  <link rel="canonical" href="{SITE_URL}{new}">
  <meta http-equiv="refresh" content="0; url={new}">
</head>
<body>
  <p>Страница переехала: <a href="{new}">{esc(title)}</a></p>
</body>
</html>
""")


# ---------------------------------------------------------------------------
# Забутовочный
# ---------------------------------------------------------------------------
def rab_view(p):
    """Имя, пояснение и задачи забутовки. Новинку завода не роняем — предупреждаем."""
    v = RAB_VIEW.get(p["factory_name"])
    if v is None:
        print(f"  !! RAB_VIEW: нет записи для «{p['factory_name']}» — беру сырое имя")
        mark = p.get("mark") or ""
        v = (p["name"], mark, ["fund", "walls"] if mark in ("М150", "М175", "М250")
             else ["walls", "inner"])
    return v


def build_zabutovka():
    items = [p for p in RAB if p["factory_name"] not in RAB_SKIP]
    cards = []
    for i, p in enumerate(items):
        name, meta, tasks = rab_view(p)
        full = f"Кирпич забутовочный {name}" + (f", {meta}" if meta else "")
        cards.append(product_card(
            href=f"tovar/kirpich-{p['id']}.html", name=full,
            img=f"{p['_gal'][0]}?v={IMG_V}" if p["_gal"] else None, alt=name,
            price_html="", m2="",   # цены рядового заказчик пока скрывает
            meta=SUPPLIER_TITLE.get(p.get("supplier"), ""),
            stock="Под заказ", shots=len(p["_gal"]),
            # Позиция без цены всё равно кладётся в ту же заявку: тупик
            # «узнайте цену отдельно» терял бы половину обращений.
            add={"id": p["id"], "name": full, "price": None, "unit": "шт",
                 "img": p["_gal"][0] if p["_gal"] else ""},
            data=f' data-task="{"|".join(tasks)}" data-price=""', eager=(i < 4)))

    body = f"""
  <section class="page-head"><div class="wrap">
    {crumbs_html([("Главная", "index.html"), ("Каталог", "index.html#catalog"),
                  ("Забутовочный кирпич", None)])}
    <h1>Забутовочный кирпич<span class="h1-n">{len(items)} {plural(len(items), "вид", "вида", "видов")}</span></h1>
  </div></section>

  <section class="section"><div class="wrap">
    {toolbar(len(items), has_prices=False)}
    <div class="catalog-body">
      {filters_panel(fgroup("Назначение", "task", TASKS))}
      {grid_shell("".join(cards), page_size=24)}
    </div>
  </div></section>
{filters_drawer()}
"""
    write_page(BASE / "kirpich-zabutovochnyy.html", page_shell(
        "Забутовочный кирпич в Краснодаре — фундамент, стены, перегородки",
        "Забутовочный (рядовой) кирпич напрямую с заводов: полнотелый и пустотелый, "
        "марки М100–М175. Доставка по Краснодару и краю, условия оплаты согласуем при заказе.",
        body, active="zabut"))


# ---------------------------------------------------------------------------
# Страница товара
# ---------------------------------------------------------------------------
# «Расход на 1 м²» здесь намеренно НЕТ: он печатается строкой под ценой,
# рядом с «≈ ₽/м² кладки», — там его ищут, а не среди морозостойкости.
SPEC_ORDER = ["Марка прочности", "Марка морозостойкости", "Структура", "Вес",
              "Водопоглощение (%)", "Тип", "Назначение"]
SPEC_RENAME = {
    "Расход на 1м2 (шт)": "Расход на 1 м² кладки",
    "Марка прочности": "Прочность",
    "Марка морозостойкости": "Морозостойкость",
    "Водопоглощение (%)": "Водопоглощение",
}
# Числовые графы: их значения в прайсах записаны как попало («кг 1,9-2,0»,
# «7, 8», «2.4 кг»), а строку без единого числа («упаковки» — обрывок,
# у которого при парсинге потерялась цифра) печатать нельзя вовсе.
NUM_SPECS = {"Вес", "Расход на 1м2 (шт)", "Водопоглощение (%)"}


def tidy_num(v):
    """«кг 1,9-2,0» → «1,9–2,0 кг», «7, 8» → «7,8», «2.4» → «2,4», «51,40» → «51,4»."""
    v = re.sub(r"(\d),\s+(\d)", r"\1,\2", v)          # «7, 8» — пробел рвёт число
    v = re.sub(r"(?<=\d)\.(?=\d)", ",", v)            # точка в дроби — латинская запись
    v = re.sub(r"(?<=\d)\s*-\s*(?=\d)", "–", v)       # диапазон через тире
    v = re.sub(r"(\d,\d+?)0+(?!\d)", r"\1", v)        # хвостовой ноль: «51,40» → «51,4»
    m = re.match(r"^(кг|шт|мм|т)\s+(.+)$", v)         # единица впереди числа
    if m:
        v = f"{m.group(2)} {m.group(1)}"
    return v.strip()


def tidy_color(v):
    """Цвет из прайса: регистр вразнобой, «е» вместо «ё», внутренние коды."""
    v = (v or "").strip()
    if not v:
        return None
    low = v.lower()
    if low.startswith("не регламент"):
        return None                  # формулировка ГОСТа, покупателю ни о чём
    if low in COLOR_LABEL or low == "баварская кладка":
        return COLOR_LABEL.get(low, "Баварская кладка")
    for bad, good in (("желт", "жёлт"), ("зелен", "зелён"), ("черн", "чёрн")):
        low = low.replace(bad, good)
    return low[:1].upper() + low[1:]


def spec_rows(p):
    src = dict(p.get("specs") or {})
    rows, seen = [], set()

    def add(key, val):
        if not val or key in seen:
            return
        seen.add(key)
        rows.append(f"<dt>{esc(key)}</dt>" + spec_dd(val))

    add("Цвет", tidy_color((p.get("color_raw") or "").strip() or src.get("Цвет")))
    add("Фактура", (p.get("texture") or "").capitalize())
    add("Формат", FMT_FILTER.get(p.get("format"), p.get("format")))
    add("Габариты", f"{p['_dims']} мм" if p.get("_dims") else None)
    for k in SPEC_ORDER:
        v = str(src.get(k) or "").strip()
        if not v:
            continue
        if k in NUM_SPECS:
            v = tidy_num(v)
            if not re.search(r"\d", v):
                continue          # числа не осталось — графа бессмысленна
        if k == "Водопоглощение (%)" and "%" not in v:
            v += " %"
        if k == "Расход на 1м2 (шт)":
            v += " шт"
        # У пяти позиций в графе «Тип» стоит не материал, а назначение
        # («лицевой»); показываем его в своей графе и одним словом —
        # тем же, каким назван раздел сайта.
        if k == "Тип" and v.lower() == "лицевой":
            add("Назначение", "Облицовочный")
            continue
        if k == "Назначение" and v.lower() in ("лицевой", "облицовочный"):
            v = "Облицовочный"
        add(SPEC_RENAME.get(k, k), v)
    return "".join(rows)


def similar(p, k=4):
    """Похожие: тот же цвет в той же коллекции, дальше — просто тот же цвет."""
    pool = [q for q in PRODUCTS if q["id"] != p["id"]]
    ranked = ([q for q in pool if q["color_group"] == p["color_group"]
               and q.get("collection") == p.get("collection")]
              + [q for q in pool if q["color_group"] == p["color_group"]]
              + [q for q in pool if q.get("collection") == p.get("collection")])
    out, seen = [], set()
    for q in ranked:
        if q["id"] in seen:
            continue
        seen.add(q["id"])
        out.append(q)
    # Заглушки «фото по запросу» и «цена по запросу» не должны открывать блок:
    # иначе «Похожие» встречают посетителя двумя серыми прямоугольниками.
    out.sort(key=lambda q: (not q["_gal"], not q.get("price")))
    return out[:k]


def dotted_specs_html(p):
    """Таблица характеристик с точечными направляющими в стиле Kirpich.ru."""
    src = dict(p.get("specs") or {})
    color = tidy_color((p.get("color_raw") or "").strip() or src.get("Цвет"))
    texture = (p.get("texture") or "").capitalize()
    fmt = FMT_FILTER.get(p.get("format"), p.get("format"))
    dims = f"{p['_dims']} мм" if p.get("_dims") else None
    supplier = SUPPLIER_TITLE.get(p.get("supplier"), p.get("supplier") or "Завод-производитель")

    main_specs = [
        ("Цвет", color),
        ("Поверхность", texture or "Гладкая"),
        ("Формат", fmt),
        ("Габариты (Д×Ш×В)", dims),
        ("Марка прочности", src.get("Марка прочности") or "М150"),
        ("Морозостойкость", src.get("Марка морозостойкости") or "F75"),
        ("Водопоглощение", (src.get("Водопоглощение (%)") or "10").replace("%", "").strip() + " %"),
        ("Теплопроводность", (src.get("Теплопроводность (Вт/м,°С)") or "0,334").strip() + " Вт/(м·°C)"),
        ("Структура", src.get("Структура") or "Пустотелый (щелевой)"),
        ("Тип материала", src.get("Тип") or "Керамический"),
        ("Назначение", "Облицовочный"),
        ("Производитель", supplier),
    ]

    per = per_m2(p) or 51.4
    pal_qty = pallet_qty(p) or 480
    weight_unit = src.get("Вес") or "2,4 кг"
    pal_weight = src.get("Вес одного поддона (кг)") or "1 100 кг"
    if pal_weight and not str(pal_weight).endswith("кг") and not str(pal_weight).endswith("т"):
        pal_weight = f"{pal_weight} кг"
    truck_load = pal_qty * 18 if pal_qty else 8640

    trans_specs = [
        ("Расход на 1 м² кладки", f"{tidy_num(rub(per))} шт"),
        ("Количество на поддоне", f"{pal_qty} шт"),
        ("Вес 1 шт", weight_unit),
        ("Вес одного поддона", f"{pal_weight}"),
        ("Расход кладочного раствора", "60 кг на 1 м² кладки"),
        ("Загрузка машины (шаланда)", f"{truck_load:,} шт (18 поддонов)".replace(",", " ")),
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
          <h2>Сопутствующие товары для кладки</h2>
        </div>
        <div class="pd-cross-grid">
          <article class="pd-cross-card">
            <img class="pd-cross-img" src="{root}img/catalog/pal-002.jpg?v={IMG_V}" alt="Цветная кладочная смесь" loading="lazy">
            <h4 class="pd-cross-title">Цветная кладочная смесь для кирпича (Белая, Графит, Беж) 25 кг</h4>
            <p class="pd-cross-price">от 485 ₽ / мешок</p>
            <a class="pd-cross-btn" href="{root}zayavka.html">Добавить к заказу</a>
          </article>
          <article class="pd-cross-card">
            <img class="pd-cross-img" src="{root}img/catalog/pal-006.jpg?v={IMG_V}" alt="Кладочная базальтовая сетка" loading="lazy">
            <h4 class="pd-cross-title">Кладочная базальтовая сетка 50×50 мм (рулон 50 м)</h4>
            <p class="pd-cross-price">1 850 ₽ / рулон</p>
            <a class="pd-cross-btn" href="{root}zayavka.html">Добавить к заказу</a>
          </article>
          <article class="pd-cross-card">
            <img class="pd-cross-img" src="{root}img/catalog/pal-007.jpg?v={IMG_V}" alt="Гидрофобизатор фасадный" loading="lazy">
            <h4 class="pd-cross-title">Гидрофобизатор фасадный для кирпича (защита от высолов) 10 л</h4>
            <p class="pd-cross-price">2 150 ₽ / канистра</p>
            <a class="pd-cross-btn" href="{root}zayavka.html">Добавить к заказу</a>
          </article>
        </div>
      </div>
    </section>
    """


def build_product(p):
    is_rab = p["category"] == "obychnyy"
    if is_rab:
        _n, _m, _ = rab_view(p)
        name = f"Кирпич забутовочный {_n}" + (f", {_m}" if _m else "")
    else:
        name = nice_name(p)
    coll = p.get("collection")
    root = "../"
    has_price = bool(p.get("price")) and not is_rab

    per = per_m2(p) or 51.4
    pal_qty = pallet_qty(p) or 480
    price_val = float(p.get("price") or 0)
    price_m2_val = round(price_val * per, 2) if price_val else 0
    price_pal_val = round(price_val * pal_qty, 2) if price_val else 0
    deliv_price_val = round(price_val + 5.0, 2) if price_val else 0

    # ---- Галерея и медиа-блок
    if p["_gal"]:
        zoom_btn = (f'<button class="pd-zoom-trigger" id="pdZoom" type="button" '
                    f'aria-label="Открыть фото крупно">{ICON["zoom"]}</button>')
        badges = ('<div class="pd-badges-bar">'
                  '<span class="pd-badge pd-badge--hit">Хит</span>'
                  '<span class="pd-badge pd-badge--factory">С завода</span>'
                  '<span class="pd-badge pd-badge--gost">ГОСТ 530-2012</span>'
                  '</div>')
        main_img = (f'<div class="pd-main-card">{badges}'
                    f'<img class="pd-main-img" id="pdMain" src="{root}{p["_gal"][0]}?v={IMG_V}" '
                    f'alt="{esc(name)}" width="1200" height="900" fetchpriority="high">{zoom_btn}</div>')
        thumbs_html = ""
        if len(p["_gal"]) > 1:
            thumbs_html = '<div class="pd-thumbs-strip">' + "".join(
                f'<button class="pd-thumb-btn{" is-on" if i == 0 else ""}" type="button" '
                f'data-src="{root}{g}?v={IMG_V}" aria-label="Фото {i + 1}">'
                f'<img src="{root}{g}?v={IMG_V}" alt="" width="74" height="74" loading="lazy">'
                f'</button>' for i, g in enumerate(p["_gal"])) + "</div>"
        
        wa_text = f"Здравствуйте! Пришлите, пожалуйста, фото и видео образца: {name}"
        wa_strip = (f'<div class="pd-wa-request">{ICON["wa"]}'
                    f'<span>Цвет на экране может отличаться от партии. '
                    f'<a href="{wa_link(wa_text)}" target="_blank" rel="noopener">'
                    f'Запросить фото и видео образца в WhatsApp</a></span></div>')
        gallery_html = f'<div class="pd-gallery-wrap">{main_img}{thumbs_html}{wa_strip}</div>'
    else:
        gallery_html = (f'<div class="pd-main-card p-none" style="aspect-ratio:4/3;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:12px">'
                        f'{ICON["photo-off"]}<span>Фотографии пришлём по запросу</span></div>')

    # ---- Плашки доверия под галереей
    trust_html = f"""
    <div class="pd-trust-cards">
      <div class="pd-trust-card">
        {ICON["calc"]}
        <div>
          <b>Бесплатный расчёт</b>
          <span>Посчитаем объём стен и швов по вашему проекту</span>
        </div>
      </div>
      <div class="pd-trust-card">
        {ICON["truck"]}
        <div>
          <b>Удобная доставка</b>
          <span>Манипуляторы и длинномеры, выгрузка на объекте</span>
        </div>
      </div>
      <div class="pd-trust-card">
        {ICON["doc"]}
        <div>
          <b>Скидки от 5 поддонов</b>
          <span>Спецусловия для строителей и бригад</span>
        </div>
      </div>
    </div>
    """

    # ---- Buy Box (Правая колонка)
    sku_val = esc(p["id"]).upper()
    supplier_val = SUPPLIER_TITLE.get(p.get("supplier"), p.get("supplier") or "Завод-производитель")
    dims_val = f"{p['_dims']} мм" if p.get("_dims") else "250×120×65 мм"
    color_val = tidy_color((p.get("color_raw") or "").strip()) or "Красный"
    texture_val = (p.get("texture") or "Гладкий").capitalize()
    fmt_val = FMT_FILTER.get(p.get("format"), p.get("format") or "1НФ (одинарный)")

    unit_tabs_html = f"""
    <div class="pd-unit-bar">
      <span class="pd-unit-label">Цена за:</span>
      <div class="pd-unit-tabs">
        <button class="pd-unit-btn is-active" type="button" data-unit="pcs">шт</button>
        <button class="pd-unit-btn" type="button" data-unit="m2">м²</button>
        <button class="pd-unit-btn" type="button" data-unit="pal">поддон</button>
      </div>
    </div>
    """

    if has_price:
        price_cards_html = f"""
        <div class="pd-price-cards">
          <label class="pd-price-card is-selected" data-price-pcs="{price_val}">
            <div class="pd-price-card-left">
              <input type="radio" name="priceRate" checked>
              <div>
                <span class="pd-price-card-title">Цена завода</span>
                <span class="pd-price-card-sub">Самовывоз или прямая отгрузка</span>
              </div>
            </div>
            <div class="pd-price-card-val">
              <b>{rub(price_val)} ₽</b>
              <small>за 1 шт</small>
            </div>
          </label>
          <label class="pd-price-card" data-price-pcs="{deliv_price_val}">
            <div class="pd-price-card-left">
              <input type="radio" name="priceRate">
              <div>
                <span class="pd-price-card-title">С доставкой по Краснодару</span>
                <span class="pd-price-card-sub">Включая выгрузку манипулятором</span>
              </div>
            </div>
            <div class="pd-price-card-val">
              <b>~{rub(deliv_price_val)} ₽</b>
              <small>за 1 шт</small>
            </div>
          </label>
        </div>
        """
        initial_sum = rub(price_pal_val)
        initial_m2 = tidy_num(rub(round(pal_qty / per, 1)))
        total_html = f"""
        <div class="pd-total-summary">
          <span class="pd-total-summary-label">Итого на сумму:</span>
          <div class="pd-total-summary-val">
            <b>{initial_sum} ₽</b>
            <small>({pal_qty} шт · {initial_m2} м² · 1 подд.)</small>
          </div>
        </div>
        """
        action_btn = (f'<button class="pd-btn-main" type="button" data-add '
                      f'data-id="{esc(p["id"])}" data-name="{esc(name)}" data-price="{price_val}" '
                      f'data-qty="{pal_qty}" data-unit="шт" data-img="{esc(p["_gal"][0] if p["_gal"] else "")}" '
                      f'data-url="tovar/kirpich-{p["id"]}.html" data-root="{root}">'
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
                      f'data-qty="{pal_qty}" data-unit="шт" data-img="{esc(p["_gal"][0] if p["_gal"] else "")}" '
                      f'data-url="tovar/kirpich-{p["id"]}.html" data-root="{root}">'
                      f'{ICON["cart"]}<span>В заявку</span></button>')

    buybox_html = f"""
    <div class="pd-buybox" data-price="{price_val}" data-per-m2="{per}" data-pallet="{pal_qty}" data-name="{esc(name)}">
      <div class="pd-box-meta">
        <span class="pd-sku">Артикул: {sku_val}</span>
        <span class="pd-stock-badge">В наличии на складе</span>
      </div>

      <dl class="pd-mini-specs">
        <dt>Завод:</dt><dd><a href="{root}{COLLECTIONS[coll]['slug'] if coll else 'kirpich-oblitsovochnyy'}.html">{esc(supplier_val)}</a></dd>
        <dt>Формат / Габариты:</dt><dd>{esc(fmt_val)} ({esc(dims_val)})</dd>
        <dt>Цвет / Поверхность:</dt><dd>{esc(color_val)} · {esc(texture_val)}</dd>
      </dl>

      {unit_tabs_html if has_price else ""}
      {price_cards_html}

      <div class="pd-order-controls">
        <div class="pd-stepper-row">
          <div class="pd-qty-stepper">
            <button type="button" data-step="-1" aria-label="Меньше">−</button>
            <input type="text" inputmode="numeric" value="{pal_qty}" aria-label="Количество, шт">
            <button type="button" data-step="1" aria-label="Больше">+</button>
          </div>
          <div class="pd-pallet-hint">
            <b>кратно поддону {pal_qty} шт</b>
            <div>1 поддон ≈ {tidy_num(rub(round(pal_qty / per, 1)))} м² кладки</div>
          </div>
        </div>

        <div class="pd-presets-row">
          <button class="pd-preset-chip" type="button" data-add-pallet="1">+1 поддон ({pal_qty})</button>
          <button class="pd-preset-chip" type="button" data-add-pallet="5">+5 поддонов ({pal_qty * 5})</button>
          <button class="pd-preset-chip" type="button" data-add-pallet="18">+18 (шаланда {pal_qty * 18})</button>
        </div>

        {total_html}
        {action_btn}

        <div class="pd-fast-actions">
          <a class="pd-fast-btn pd-fast-btn--wa" href="{wa_link('Здравствуйте! Хочу уточнить наличие и расчет: ' + name)}" target="_blank" rel="noopener">
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
          <span><b>Прямые поставки с завода.</b> Честная заводская цена без наценок и переплат.</span>
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
            {ICON["calc"]}<span>Калькулятор кладки</span>
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
                <h3>Параметры фасада и кладки</h3>
                <div class="pd-calc-field">
                  <label for="fcArea">Площадь стен фасада (м²):</label>
                  <input id="fcArea" type="number" step="any" value="100" placeholder="100">
                </div>
                <div class="pd-calc-row">
                  <div class="pd-calc-field">
                    <label for="fcLen">Или длина стен (м):</label>
                    <input id="fcLen" type="number" step="any" placeholder="Например, 40">
                  </div>
                  <div class="pd-calc-field">
                    <label for="fcHeight">Высота стен (м):</label>
                    <input id="fcHeight" type="number" step="any" placeholder="Например, 3">
                  </div>
                </div>
                <div class="pd-calc-field">
                  <label for="fcThick">Толщина кладки:</label>
                  <select id="fcThick">
                    <option value="1" selected>Облицовка в 0,5 кирпича (120 мм)</option>
                    <option value="2">Стена в 1 кирпич (250 мм)</option>
                    <option value="3">Стена в 1,5 кирпича (380 мм)</option>
                  </select>
                </div>
                <label class="pd-calc-check">
                  <input id="fcWaste" type="checkbox" checked>
                  <span>Добавить запас +5% на подрезку и бой</span>
                </label>
              </div>

              <div class="pd-calc-results">
                <div>
                  <div class="pd-calc-results-title">Расчёт материалов</div>
                  <div class="pd-calc-results-list">
                    <div class="pd-calc-res-item">
                      <span>Количество кирпича:</span>
                      <b id="fcResBricks">5 397 шт</b>
                    </div>
                    <div class="pd-calc-res-item">
                      <span>Количество поддонов:</span>
                      <b id="fcResPallets">12 поддонов</b>
                    </div>
                    <div class="pd-calc-res-item">
                      <span>Кладочный раствор:</span>
                      <b id="fcResMortar">240 мешков (25 кг)</b>
                    </div>
                    <div class="pd-calc-res-item">
                      <span>Общий вес партии:</span>
                      <b id="fcResWeight">13,0 т</b>
                    </div>
                  </div>
                </div>
                <div>
                  <div class="pd-calc-res-total">
                    <span>Ориентировочная сумма:</span>
                    <b id="fcResSum">142 913 ₽</b>
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
            <h3>Доставка и разгрузка по Краснодару и ЮФО</h3>
            <p>Мы доставляем кирпич напрямую с завода собственным транспортом разной грузоподъёмности (от 5 до 20 тонн), оборудованным краном-манипулятором для аккуратной выгрузки на вашем участке.</p>
            <table class="pd-delivery-table">
              <thead>
                <tr>
                  <th>Зона доставки</th>
                  <th>Манипулятор 5–10 т</th>
                  <th>Длинномер (шаланда 20 т)</th>
                  <th>Срок доставки</th>
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
                  <td>Пригород (до 30 км: Динская, Елизаветинская, Яблоновский)</td>
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
                <p>• Оплата водителю-экспедитору наличными или переводом по факту доставки и проверки товара.<br>• Оплата банковской картой или через СБП.<br>• Предоплата при заказе индивидуальных заказных позиций завода.</p>
              </div>
              <div class="pd-payment-card">
                <h4>Для строительных компаний и ИП</h4>
                <p>• Безналичный расчёт по счёту с НДС 20% или без НДС.<br>• Полный комплект закрывающих документов (УПД, паспорта качества, сертификаты ГОСТ).<br>• Договор поставки и фиксация цен на объём.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
    """

    crumbs = [("Главная", f"{root}index.html")]
    if is_rab:
        crumbs.append(("Забутовочный кирпич", f"{root}kirpich-zabutovochnyy.html"))
    else:
        crumbs.append(("Облицовочный кирпич", f"{root}kirpich-oblitsovochnyy.html"))
        if coll:
            crumbs.append((COLLECTIONS[coll]["title"], f"{root}{COLLECTIONS[coll]['slug']}.html"))
    crumbs.append(((f"{_n}, {_m}" if _m else _n) if is_rab else p["name"], None))

    sim = [] if is_rab else similar(p)
    sim_html = ""
    if sim:
        sim_html = f"""
  <section class="section"><div class="wrap">
    <div class="section-head"><h2>Похожие по цвету</h2>
      <a class="see-all" href="{root}kirpich-oblitsovochnyy.html">Весь облицовочный кирпич</a></div>
    <div class="p-grid{grid_cls(len(sim))}">{"".join(card_of(q, root=root) for q in sim)}</div>
  </div></section>"""

    body = f"""
  <section class="page-head">
    <div class="wrap">
      <div class="pd-header">
        <h1 class="pd-title">{esc(name)}</h1>
        {crumbs_html(crumbs)}
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
"""
    ld = {"@context": "https://schema.org", "@type": "Product", "name": name,
          "sku": p["id"].upper(),
          "category": "Забутовочный кирпич" if is_rab else "Облицовочный кирпич"}
    if p["_gal"]:
        ld["image"] = SITE_URL + p["_gal"][0]
    if has_price:
        ld["offers"] = {"@type": "Offer", "price": p["price"], "priceCurrency": "RUB",
                        "url": SITE_URL + f"tovar/kirpich-{p['id']}.html"}
    head = ('\n  <script type="application/ld+json">'
            + json.dumps(ld, ensure_ascii=False) + "</script>")

    m2d = m2_text(p)
    descr = (f"{name}: {rub(p['price'])} ₽/шт{', ' + m2d if m2d else ''}. "
             f"Доставка по Краснодару и краю, наличный и безналичный расчёт." if has_price else
             f"{name}. Цена по запросу. Доставка по Краснодару и краю.")

    title = f"{name}. Купить в Краснодаре" if "—" in name else f"{name} — купить в Краснодаре"

    write_page(BASE / "tovar" / f"kirpich-{p['id']}.html", page_shell(
        title, descr, body, root=root,
        active="zabut" if is_rab else "oblic", extra_head=head))


# ---------------------------------------------------------------------------
def main():
    build_category()

    for slug in COLL_ORDER:
        build_collection(slug)
    build_zabutovka()
    n = 0
    for p in PRODUCTS:
        build_product(p)
        n += 1
    for p in RAB:
        if p["factory_name"] not in RAB_SKIP:
            build_product(p)
            n += 1
    print(f"кирпич: витрина + {len(COLL_ORDER)} коллекций + забутовка + {n} товаров")


if __name__ == "__main__":
    main()
