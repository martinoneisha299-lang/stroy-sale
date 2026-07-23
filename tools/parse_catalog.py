#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсер каталога «Строй-Сейл».
Читает ~/Desktop/фото (5 поставщиков) → data/catalog.json.

Принципы (см. КАТАЛОГ-ПЛАН.md):
- поставщик скрыт (поле supplier — только для менеджера);
- 1 поставщик = 1 коллекция;
- имена товаров чистим от заводского мусора;
- Тербунский: 4 файла-формата одного цвета склеиваются в 1 товар;
- Донской: дубли (разный поддон) склеиваются, флагуются.
"""

import json
import re
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path("/Users/dm/Desktop/фото")
OUT = Path("/Users/dm/Desktop/сайт/data/catalog.json")

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXT = {".mp4"}

# ─── Коллекции ────────────────────────────────────────────────────────────────
COLLECTIONS = {
    "ekonom": "Эконом",
    "palitra": "Палитра",
    "klassika": "Классика",
    "evropa": "Европа",
    "formovka": "Ручная формовка",
}

# ─── Цветовые группы (для «подбора по цвету») ────────────────────────────────
COLOR_GROUPS = [
    ("белый", ["белый", "слоновая кость", "белоснеж"]),
    # «скала»/«гранит» убраны из ключей: у Донского это ФАКТУРЫ
    # («Коричневый скала антик»), сам цвет берётся из поля «Цвет»
    ("серый", ["светло-сер", "серый", "серая", "грей", "платин", "мрамор"]),
    ("микс (бавария)", ["бавар", "флеш", "пестр", "пёстр"]),
    # «сахара» убрана из ключей (фактура Донского: «Красный сахара»);
    # песочный цвет «Сахара» Губского держит оверрайд по точному имени
    ("бежевый", ["бежев", "солома", "песочн", "песчаная", "каракум",
                  "пшениц", "золотист", "янтар", "саванн", "сафари",
                  "капучино", "латунь", "бронза", "жёлт", "желт", "светлый",
                  "соломенн"]),
    ("персиковый", ["персик", "абрикос", "розов", "коралл", "лосось"]),
    ("красный", ["красн", "терракот", "классик", "гранат", "рубин", "бордо",
                  "вишн", "черри", "магма", "коррида"]),
    ("коричневый", ["коричнев", "корица", "мокко", "mokko", "шоколад", "мускат",
                     "каштан", "кора кедра", "какао", "медь", "тархан"]),
    ("графит", ["графит", "черн", "чёрн", "тёмн", "темн", "габбро", "готик",
                 "вулкан", "лава", "феррум", "антрацит", "патина"]),
    ("зелёный", ["зелен", "зелён", "малахит", "хаки", "олив"]),
]


def color_group(*texts: str) -> str:
    blob = " ".join(t.lower() for t in texts if t)
    for group, keys in COLOR_GROUPS:
        for k in keys:
            if k in blob:
                return group
    return "разное"


# ─── Фактуры ─────────────────────────────────────────────────────────────────
TEXTURES = [
    ("ручная формовка", ["ручной формовки", "ручная формовка", "wdf ту"]),
    ("старый город", ["старый город", "старый  город"]),
    ("береста", ["береста"]),
    ("руст", ["руст"]),
    ("кроста", ["кроста"]),
    ("антик", ["антик"]),
    ("винтаж", ["винтаж"]),
    ("ретро", ["ретро"]),
    ("рельефный", ["рельеф"]),
    ("коралл", ["коралл"]),   # раньше «кора» — но фактура Донского другая
    ("сахара", ["сахара"]),   # «сахарная крошка» Донского (и Сахара Губского)
    ("кора", ["кора", "кедра"]),
    ("бриз", ["бриз"]),
    ("велюр", ["вельвет", "велюр"]),
    ("рифлёный", ["рифлен", "рифлён"]),
    ("фактурный", ["фактурн"]),  # завод не называет фактуру точнее
    ("гладкий", ["гладк"]),
]


def texture_of(*texts: str) -> str:
    blob = " ".join(t.lower() for t in texts if t)
    for tex, keys in TEXTURES:
        for k in keys:
            if k in blob:
                return tex
    return "гладкий"  # по умолчанию у кирпича гладкая поверхность


# ─── Форматы ─────────────────────────────────────────────────────────────────
def format_of(*texts: str) -> str:
    blob = " ".join(t.lower() for t in texts if t)
    if "0,5wdf" in blob or "0.5wdf" in blob:
        return "0,5 WDF"
    if "wdf" in blob:
        return "WDF"
    if "wmf" in blob:
        return "WMF"
    if "ригельный" in blob or " mf" in blob or "modf" in blob:
        return "Ригель MF"
    if "длинный" in blob or " lf" in blob or "long" in blob:
        return "Лонг LF"
    if "0,7" in blob or "0.7" in blob or "евро" in blob:
        return "0,7НФ (евро)"
    if "0,9" in blob or "0.9" in blob:
        return "0,9НФ"
    if "1,4" in blob or "1.4" in blob or "утолщен" in blob or "полуторн" in blob:
        return "1,4НФ (полуторный)"
    if "1нф" in blob or "1 нф" in blob or "одинарн" in blob:
        return "1НФ (одинарный)"
    return "1НФ (одинарный)"


# ─── Утилиты ─────────────────────────────────────────────────────────────────
def read_txt(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def parse_price(s: str):
    """'36,88 ₽ / шт.' | '142 руб./за шт. | 8095.5 руб./за м²' | 'по запросу'"""
    if not s:
        return None, None
    if "запрос" in s.lower():
        return None, None
    nums = re.findall(r"(\d[\d\s]*[.,]?\d*)\s*(?:₽|руб)", s)
    def to_f(x):
        return float(x.replace(" ", "").replace(",", "."))
    price = to_f(nums[0]) if nums else None
    price_m2 = to_f(nums[1]) if len(nums) > 1 and ("м²" in s or "м2" in s) else None
    return price, price_m2


def parse_kv_block(text: str, header: str) -> dict:
    """Блок '- Ключ: значение' (и вариант «ключ и значение на соседних строках»)."""
    out = {}
    m = re.search(rf"{header}.*?:\s*\n(.*?)(?:\n\s*\n|\Z)", text, re.S)
    if not m:
        return out
    lines = [l.strip().lstrip("-").strip() for l in m.group(1).splitlines()
             if l.strip().startswith("-")]
    pending_key = None
    for line in lines:
        if ":" in line:
            k, _, v = line.partition(":")
            k, v = k.strip(), v.strip()
            if v:
                out[k] = v
                pending_key = None
            else:
                pending_key = k
        elif pending_key:
            out[pending_key] = line
            pending_key = None
    return out


def field(text: str, name: str) -> str:
    m = re.search(rf"^{name}:\s*(.+)$", text, re.M)
    return m.group(1).strip() if m else ""


def description_of(text: str) -> str:
    m = re.search(r"^Описание:\s*\n(.*)", text, re.M | re.S)
    if not m:
        return ""
    d = m.group(1).strip()
    d = re.sub(r"\n{3,}", "\n\n", d)
    return d


def images_in(d: Path):
    return sorted([f.name for f in d.iterdir()
                   if f.suffix.lower() in IMG_EXT and not f.name.startswith(".")])


def videos_in(d: Path):
    return sorted([f.name for f in d.iterdir()
                   if f.suffix.lower() in VIDEO_EXT and not f.name.startswith(".")])


def nice_title(s: str) -> str:
    """'ВИШНЯ "БЕРЕСТА"' → 'Вишня Береста'"""
    s = re.sub(r'["«»„“”]', "", s)
    def cap(w):
        if any(ch.isdigit() for ch in w):   # 0,5WDF, MODF и т.п. — не трогаем регистр цифро-кодов
            return w.upper()
        return w if (len(w) <= 3 and w.isupper() and not w.isalpha()) else w.capitalize()
    return " ".join(cap(w) for w in s.split())


def mark_of(raw: str) -> str:
    """Марка прочности из заводского имени: 'М150'"""
    m = re.search(r"\bМ\s?(\d{2,3})\b", raw)
    return f"М{m.group(1)}" if m else ""


def consumption(specs: dict):
    for k, v in specs.items():
        if "расход" in k.lower() and "м2" in k.lower().replace("м²", "м2"):
            m = re.search(r"[\d.,]+", v.replace(" ", ""))
            if m:
                try:
                    return float(m.group(0).replace(",", "."))
                except ValueError:
                    return None
    return None


products = []
warnings = []


def add(p: dict):
    p.setdefault("flags", [])
    p.setdefault("photos", [])
    p.setdefault("video", None)
    p.setdefault("formats_prices", {})
    p.setdefault("price_m2", None)
    p.setdefault("description", "")
    p.setdefault("specs", {})
    p.setdefault("consumption_per_m2", None)
    if not p["photos"]:
        p["flags"].append("нет фото")
    if p.get("price") is None and not p["formats_prices"]:
        p["price_on_request"] = True
    else:
        p.setdefault("price_on_request", False)
    products.append(p)


# ─── 1. Губский → «Палитра» ──────────────────────────────────────────────────
def parse_gubskiy():
    base = ROOT / "Губский"
    lic = base / "Лицевой керамический кирпич"
    for d in sorted(p for p in lic.iterdir() if p.is_dir()):
        txts = list(d.glob("*.txt"))
        text = read_txt(txts[0]) if txts else ""
        specs = parse_kv_block(text, "Технические характеристики")
        # цены по форматам: '- 0.7 NF 34.00 ₽ / шт.'
        fmt_prices = {}
        m = re.search(r"Цены по форматам:\s*\n(.*?)(?:\n\s*\n|\Z)", text, re.S)
        if m:
            for line in m.group(1).splitlines():
                fm = re.search(r"([\d.,]+)\s*NF\s+([\d.,]+)", line)
                if fm:
                    key = format_of(fm.group(1) + "нф")
                    fmt_prices[key] = float(fm.group(2).replace(",", "."))
        price, _ = parse_price(field(text, "Цена"))
        name = nice_title(field(text, "Название") or d.name)
        add({
            "category": "oblitsovochnyy",
            "collection": "palitra",
            "supplier": "Губский",
            "name": name,
            "factory_name": d.name,
            "color_raw": specs.get("Цвет", ""),
            "color_group": color_group(specs.get("Цвет", ""), name),
            "texture": texture_of(name, text),
            "format": "1НФ (одинарный)",
            "formats_prices": fmt_prices,
            "price": price,
            "price_unit": "шт",
            "specs": specs,
            "consumption_per_m2": consumption(specs),
            "description": description_of(text),
            "dir": str(d.relative_to(ROOT)),
            "photos": images_in(d),
            "video": (videos_in(d) or [None])[0],
        })
    # рядовой + хозяйственный → категория «обычный кирпич»
    for sub in ("Кирпич рядовой керамический пустотелый",
                "Кирпич хозяйственный керамический пустотелый"):
        d = base / sub
        if not d.exists():
            continue
        text = read_txt(next(d.glob("*.txt")))
        fmt_prices = {}
        for fm in re.finditer(r"([\d.,]+)\s*NF\s*—\s*([\d.,]+)\s*₽", text):
            fmt_prices[format_of(fm.group(1) + "нф")] = float(fm.group(2).replace(",", "."))
        short = "Рядовой пустотелый" if "рядовой" in sub else "Хозяйственный пустотелый"
        add({
            "category": "obychnyy",
            "collection": None,
            "supplier": "Губский",
            "name": short,
            "factory_name": sub,
            "color_raw": "не регламентируется",
            "color_group": "разное",
            "texture": "гладкий",
            "format": "1НФ (одинарный)",
            "formats_prices": fmt_prices,
            "price": min(fmt_prices.values()) if fmt_prices else None,
            "price_unit": "шт",
            "specs": {},
            "description": description_of(text) or field(text, "Описание категории"),
            "dir": str(d.relative_to(ROOT)),
            "photos": images_in(d),
            "video": None,
        })


# ─── 2. Донской → «Классика» (+забутовочный → обычный) ──────────────────────
DON_CUT = re.compile(
    r"\s*(Лицевой|Рядовой|Одинарный|Утолщенный|УТОЛЩЕННЫЙ|Кирпич|пустотелый|"
    r"полнотелй|полнотелый|М\d{2,3}|\(F\d+|евро\b|с ФАСКОЙ).*$",
    re.I)


def don_name(raw: str) -> str:
    cut = DON_CUT.sub("", raw).strip(" ,.-")
    return nice_title(cut) if cut else nice_title(raw)


def parse_donskoy():
    base = ROOT / "Донской кирпич"
    seen = {}
    for cat_dir, category in (("лицевой", "oblitsovochnyy"),
                              ("забутовочный", "obychnyy")):
        for d in sorted(p for p in (base / cat_dir).iterdir() if p.is_dir()):
            txts = list(d.glob("*.txt"))
            if not txts:
                warnings.append(f"Донской: нет txt в {d.name}")
                continue
            text = read_txt(txts[0])
            brief = parse_kv_block(text, r"Характеристики \(кратко\)")
            price, _ = parse_price(field(text, "Цена"))
            raw = field(text, "Название") or d.name
            if category == "oblitsovochnyy":
                name = don_name(raw)
            else:
                # для рабочего кирпича имя = суть без хвостов упаковки
                name = re.sub(r"\s*\d+шт.*$", "", raw).strip(" ,.")
                name = re.sub(r"\s*упак.*$", "", name).strip(" ,.")
            texture = texture_of(brief.get("Поверхность", ""), raw)
            fmt = format_of(brief.get("Формат", ""), raw)
            mark = mark_of(raw)
            
            photos = images_in(d)
            p_dir = str(d.relative_to(ROOT))
            # нет фото — честная заглушка «Фото пришлём по запросу»

            key = (name.lower(), texture, fmt, mark, category)
            if key in seen:  # дубль: другой поддон/фасовка при той же марке
                seen[key]["flags"].append(f"вариант фасовки: {raw}")
                if not seen[key]["photos"] and photos:
                    seen[key]["photos"] = photos
                    seen[key]["dir"] = p_dir
                continue
            flags = []
            if "некондиц" in raw.lower():
                flags.append("некондиция (уценка)")
            p = {
                "flags": flags,
                "category": category,
                "collection": "klassika" if category == "oblitsovochnyy" else None,
                "supplier": "Донской",
                "name": name,
                "factory_name": raw,
                "color_raw": brief.get("Цвет", ""),
                "color_group": color_group(brief.get("Цвет", ""), name),
                "texture": texture,
                "format": fmt,
                "mark": mark,
                "price": price,
                "price_unit": "шт",
                "specs": parse_kv_block(text, "Технические характеристики") or brief,
                "description": description_of(text),
                "dir": p_dir,
                "photos": photos,
                "video": None,
            }
            add(p)
            seen[key] = p


# ─── 3. Славянский → «Европа» ────────────────────────────────────────────────
def parse_slavyanskiy():
    base = ROOT / "Славянский"
    all_files = [f for f in base.iterdir() if not f.name.startswith(".")]
    for txt in sorted(f for f in all_files if f.suffix == ".txt"):
        stem = txt.stem
        text = read_txt(txt)
        chars = parse_kv_block(text, "Характеристики")
        price, _ = parse_price(field(text, "Цена"))
        # фото: точное совпадение основы имени (не путать «КЛАССИК 1НФ» и «КЛАССИК 1НФ УС»)
        photos = sorted(
            f.name for f in all_files
            if f.suffix.lower() in IMG_EXT
            and re.fullmatch(re.escape(stem) + r"(?:_\d+)?", f.stem))
        # имя: до формата (границы слов, чтобы не резать «РУСТ» по «УС»)
        raw_disp = re.sub(r"\s+(1НФ|0,7НФ|Евро|УС|рф)\b.*$", "", stem).strip(" -")
        name = nice_title(raw_disp.replace("-", " "))
        flags = []
        if re.search(r"\bрф\b", stem.lower()):
            flags.append("уточнить: «рф» в заводском имени (ручная формовка?)")
        desc = description_of(text)
        p = {
            "category": "oblitsovochnyy",
            "collection": "evropa",
            "supplier": "Славянский",
            "name": name,
            "factory_name": stem,
            "color_raw": "",
            "color_group": color_group(name, desc[:300]),
            "texture": texture_of(stem),
            "format": format_of(chars.get("Формат", ""), stem),
            "price": price,
            "price_unit": "шт",
            "specs": chars,
            "description": description_of(text),
            "dir": "Славянский",
            "photos": photos,
            "video": None,
            "flags": flags,
        }
        add(p)


# ─── 4. Тандем → «Ручная формовка» ───────────────────────────────────────────
def parse_tandem():
    base = ROOT / "Тандем Кирпич"
    for sub in sorted(p for p in base.iterdir() if p.is_dir()):
        for txt in sorted(sub.glob("*.txt")):
            text = read_txt(txt)
            chars = parse_kv_block(text, "Характеристики")
            price, price_m2 = parse_price(field(text, "Цена"))
            name = nice_title(field(text, "Название") or txt.stem)
            # ИМЯ.jpg — основное фото; ИМЯ_2.jpg, ИМЯ_3.jpg… — доснимки
            # галереи с сайта завода (мерж 16.07). Разделитель «_» не
            # конфликтует с вариантами типа «ИМЯ 0,5WDF» (там пробел).
            photos = sorted(f.name for f in sub.iterdir()
                            if f.suffix.lower() in IMG_EXT
                            and (f.stem == txt.stem
                                 or f.stem.startswith(txt.stem + "_")))
            add({
                "category": "oblitsovochnyy",
                "collection": "formovka",
                "supplier": "Тандем",
                "name": name,
                "factory_name": txt.stem,
                "color_raw": chars.get("Цвет", ""),
                "color_group": color_group(chars.get("Цвет", ""), name),
                "texture": "ручная формовка",
                "format": format_of(chars.get("Формат", ""), sub.name),
                "price": price,
                "price_m2": price_m2,
                "price_unit": "шт",
                "specs": chars,
                "description": description_of(text),
                "dir": str(sub.relative_to(ROOT)),
                "photos": photos,
                "video": None,
            })


# ─── 5. Тербунский → «Эконом» (склейка форматов) ─────────────────────────────
def parse_terbunskiy():
    base = ROOT / "тербунский_гончар"
    type_names = {"Керамический": "керамический", "Клинкерный": "клинкерный",
                  "Полнотелый": "полнотелый"}
    for type_dir in sorted(p for p in base.iterdir() if p.is_dir()):
        t_ru = type_names.get(type_dir.name, type_dir.name.lower())
        fak = type_dir / "фактура"
        if not fak.exists():
            continue
        for tex_dir in sorted(p for p in fak.iterdir() if p.is_dir()):
            texture = tex_dir.name.strip().lower()
            for color_dir in sorted(p for p in tex_dir.iterdir() if p.is_dir()):
                color = color_dir.name.strip()
                fmt_prices, photos, spec_all, desc = {}, [], {}, ""
                base_price = None
                for txt in sorted(color_dir.glob("*.txt")):
                    text = read_txt(txt)
                    price, _ = parse_price(field(text, "Цена"))
                    fmt = format_of(txt.stem)
                    if price is not None:
                        fmt_prices[fmt] = price
                        if fmt.startswith("1НФ"):
                            base_price = price
                    spec_all.update(parse_kv_block(text, "Характеристики"))
                    desc = desc or description_of(text)
                    photos += [f.name for f in color_dir.iterdir()
                               if f.suffix.lower() in IMG_EXT and f.stem == txt.stem]
                if base_price is None and fmt_prices:
                    base_price = min(fmt_prices.values())

                # Sort photos so standard 1НФ (1.0 / одинарный) is first
                base_photos = []
                other_photos = []
                for ph in sorted(set(photos)):
                    ph_low = ph.lower()
                    if "1.0" in ph_low or "одинарн" in ph_low or "1нф" in ph_low:
                        base_photos.append(ph)
                    else:
                        other_photos.append(ph)
                sorted_photos = base_photos + other_photos

                p_name = nice_title(color)
                if type_dir.name == "Клинкерный":
                    p_name += " Клинкер"
                elif type_dir.name == "Полнотелый":
                    p_name += " Полнотелый"

                add({
                    "category": "oblitsovochnyy",
                    "collection": "ekonom",
                    "supplier": "Тербунский гончар",
                    "name": p_name,
                    "factory_name": f"{type_dir.name}/{texture}/{color}",
                    "kind": t_ru,  # керамический/клинкерный/полнотелый
                    "color_raw": color,
                    "color_group": color_group(color),
                    "texture": texture,
                    "format": "1НФ (одинарный)",
                    "formats_prices": fmt_prices,
                    "price": base_price,
                    "price_unit": "шт",
                    "specs": spec_all,
                    "description": desc,
                    "dir": str(color_dir.relative_to(ROOT)),
                    "photos": sorted_photos,
                    "video": None,
                })


# ─── Запуск ──────────────────────────────────────────────────────────────────
parse_gubskiy()
parse_donskoy()
parse_slavyanskiy()
parse_tandem()
parse_terbunskiy()

# Точечные поправки цвета по ТОЧНОМУ имени: у этих товаров слово-имя
# совпадает со словом-фактурой, общие ключи дают неверную группу.
NAME_COLOR_OVERRIDES = {
    "сахара": "бежевый",
    # «Графит» Губского размечался коричневым — свотч «графит» его не находил
    "графит": "графит",
    "старый город графит": "графит",
    # «Вена» была в группе «разное» (пустой свотч-клон кнопки «Все»);
    # по фото это тёплый персиковый микс
    "вена": "персиковый",
}
for p in products:
    ov = NAME_COLOR_OVERRIDES.get(p["name"].lower())
    if ov:
        p["color_group"] = ov

# Линейки «Палитры» (Губский): имя линейки и есть фактура, но разметка из
# прайса гуляла («Красный Бриз» — рельефный, «Черный Бриз» — руст и т.п.) —
# фильтр «Фактура» разбрасывал одну линейку по 4 значениям. Нормализуем.
for p in products:
    if p.get("collection") != "palitra":
        continue
    low = p["name"].lower()
    if "бриз" in low:
        p["texture"] = "бриз"
    elif "кора" in low and "коралл" not in low:
        p["texture"] = "кора"

# ─── «Без каши»: один цвет+фактура = одна карточка ───────────────────────────
# Донской («Классика»): форматы и марки одного цвета+фактуры сливаются
# в базовый товар, варианты уходят в formats_prices (как у Губского).
# Порядок как у самого завода: карточка = цвет+фактура, формат внутри.
from collections import defaultdict

FMT_RANK = {"1НФ (одинарный)": 0, "0,7НФ (евро)": 1, "0,9НФ": 2,
            "1,4НФ (полуторный)": 3}


def merge_klassika():
    groups = defaultdict(list)
    for p in products:
        if p["collection"] == "klassika":
            groups[(p["name"].lower(), p["texture"])].append(p)
    removed = []
    for grp in groups.values():
        if len(grp) < 2:
            continue
        # база: с фото → одинарный формат → дешевле
        grp.sort(key=lambda p: (not p["photos"],
                                FMT_RANK.get(p["format"], 9),
                                p["price"] or 10**9))
        base = grp[0]
        for v in grp[1:]:
            if v["price"]:
                if v["format"] != base["format"]:
                    label = v["format"]
                else:  # тот же формат, другая марка прочности
                    label = f'{v["format"]}, марка {v.get("mark") or "выше"}'
                # не затираем и не дублируем
                if label not in base["formats_prices"]:
                    base["formats_prices"][label] = v["price"]
            base["flags"].append(f"объединён вариант: {v['factory_name']}")
            removed.append(id(v))
    products[:] = [p for p in products if id(p) not in removed]


def merge_exact_twins():
    """Полные двойники (имя+фактура+формат): Славянский «Классик»/«Классик УС»,
    Тандем «Омега Modf» ×2 — покупателю различий не видно, оставляем один."""
    groups = defaultdict(list)
    for p in products:
        groups[(p["collection"], p["name"].lower(), p["texture"], p["format"])].append(p)
    removed = []
    for grp in groups.values():
        if len(grp) < 2:
            continue
        grp.sort(key=lambda p: (not p["photos"], p["price"] or 10**9,
                                len(p["factory_name"])))
        base = grp[0]
        for v in grp[1:]:
            if v["price"] and v["price"] != base["price"]:
                label = f'вариант ({v.get("mark") or v["factory_name"][:20]})'
                base["formats_prices"].setdefault(label, v["price"])
            base["flags"].append(f"объединён двойник: {v['factory_name']}")
            removed.append(id(v))
    products[:] = [p for p in products if id(p) not in removed]


# Имя карточки как у завода: цвет + фактура («Красный руст»),
# чтобы соседние карточки одного цвета не выглядели дублями.
# Делается ДО схлопывания, чтобы «Красный»+береста слился с «Красный Береста».
_TEX_STOP = ([t for t, _ in TEXTURES if t not in ("гладкий", "ручная формовка")]
             + [k for _, keys in TEXTURES for k in keys]
             + ["лава"])  # «Вулкан Лава» — заводское имя, не дописываем
for p in products:
    if p["collection"] == "klassika":
        tex = p["texture"]
        low = p["name"].lower()
        # «фактурный» — неконкретная фактура, в имя не дописываем
        if (tex not in ("гладкий", "ручная формовка", "фактурный")
                and not any(w in low for w in _TEX_STOP)):
            p["name"] = f'{p["name"]} {tex}'

merge_klassika()

# фасовки-двойники Донского: одно имя, формат и марка, но фактура в спеках
# распознана по-разному («Красный Рельефный» 416шт=береста / 480шт=рельефный)
_pack = defaultdict(list)
for p in products:
    if p["collection"] == "klassika":
        _pack[(p["name"].lower(), p["format"], p.get("mark"))].append(p)
for grp in _pack.values():
    if len(grp) > 1:
        grp.sort(key=lambda p: (not p["photos"], p["price"] or 10**9))
        base = grp[0]
        for v in grp[1:]:
            base["flags"].append(f"объединена фасовка: {v['factory_name']}")
            products.remove(v)

merge_exact_twins()

# Европа (Славянский, цены по запросу): один цвет в двух форматах —
# одна карточка, второй формат уходит в характеристики
_ev = defaultdict(list)
for p in products:
    if p["collection"] == "evropa":
        _ev[(p["name"].lower(), p["texture"])].append(p)
for grp in _ev.values():
    if len(grp) > 1:
        grp.sort(key=lambda p: (not p["photos"], FMT_RANK.get(p["format"], 9)))
        base = grp[0]
        others = ", ".join(v["format"] for v in grp[1:])
        base["specs"]["Форматы"] = f'{base["format"]}, также {others}'
        for v in grp[1:]:
            base["flags"].append(f"объединён формат: {v['factory_name']}")
            products.remove(v)

# id: коллекция-NNN, стабильно по сортировке
counters = {}
for p in sorted(products, key=lambda x: (x["collection"] or "z-obychnyy",
                                         x["supplier"], x["name"])):
    pref = (p["collection"] or "rab")[:3]
    counters[pref] = counters.get(pref, 0) + 1
    p["id"] = f"{pref}-{counters[pref]:03d}"

data = {
    "generated": str(date.today()),
    "source_root": str(ROOT),
    "collections": COLLECTIONS,
    "products": products,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

# ─── Отчёт ───────────────────────────────────────────────────────────────────
from collections import Counter
print(f"Всего товаров: {len(products)}")
print("\nПо коллекциям:")
for c, n in Counter(p["collection"] or "обычный кирпич" for p in products).most_common():
    name = COLLECTIONS.get(c, c)
    prices = [p["price"] for p in products if (p["collection"] or "обычный кирпич") == c and p["price"]]
    rng = f"{min(prices):.0f}–{max(prices):.0f} ₽" if prices else "цены по запросу"
    print(f"  {name:20s} {n:4d} тов.  {rng}")
print("\nПо цветовым группам (облицовочный):")
for c, n in Counter(p["color_group"] for p in products
                    if p["category"] == "oblitsovochnyy").most_common():
    print(f"  {c:15s} {n}")
no_photo = [p for p in products if not p["photos"]]
print(f"\nБез фото: {len(no_photo)}")
for p in no_photo[:15]:
    print(f"  [{p['supplier']}] {p['name']} ({p['factory_name'][:60]})")
if len(no_photo) > 15:
    print(f"  … и ещё {len(no_photo) - 15}")
on_req = [p for p in products if p["price_on_request"]]
print(f"\nЦена по запросу: {len(on_req)}")
flagged = [p for p in products if p["flags"] and p["photos"]]
print(f"Прочие флаги: {sum(1 for p in products if p['flags'])}")
if warnings:
    print("\nПРЕДУПРЕЖДЕНИЯ:")
    for w in warnings:
        print("  " + w)
print("\nOK →", OUT)
