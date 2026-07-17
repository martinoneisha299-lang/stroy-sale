#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Фото раздела «Кровля» → img/roof/ + data/roof_images.json.

Источники:
- ~/Desktop/фото/кровля/<раздел>/<товар>/ — фото поставщика (ВСЕ продуктовые
  кадры под тайловым водяным знаком → на сайт НЕ идут, берём только чистые
  _схема.* и папки «Цвета»);
- ~/Desktop/фото/кровля/_с-сайта-17.07/галерея-изделий — 14 чистых студийных
  кадров из галереи сайта поставщика (без знака, проверены глазами);
- ~/Desktop/фото/кровля/_с-сайта-17.07/текстуры-покрытий — большие текстуры
  цветов со страницы «Коллекция» + collection_map.json (серия → цвет → файл).

Выход (img/roof/ — своя папка, чтобы не задевать img/catalog кирпича/плитки):
- hero-roof.jpg — герой категории;
- cover-<id>.jpg 900×900 — обложки карточек (металлочерепица, секции);
- roof-<id>.jpg / roof-<id>-N.jpg 960×720 — галереи товарных страниц;
- roof-<id>-scheme.jpg — чертёж профиля, вписанный в 960×720 на белом;
- sw-<slug>.jpg 124×124 — кружки цветов; tex-<slug>.jpg 880×560 — большой образец.
"""

import json
import re
import unicodedata
from pathlib import Path

from PIL import Image, ImageOps

BASE = Path("/Users/dm/Desktop/сайт")
SRC = Path("/Users/dm/Desktop/фото/кровля")
GAL = SRC / "_с-сайта-17.07" / "галерея-изделий"
TEX = SRC / "_с-сайта-17.07" / "текстуры-покрытий"
PROF_GAL = SRC / "_с-сайта-17.07" / "профнастил-фото"
OUT = BASE / "img" / "roof"
OUT.mkdir(parents=True, exist_ok=True)

WHITE = (255, 255, 255)

TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def slugify(name):
    s = unicodedata.normalize("NFKD", name.lower())
    out = []
    for ch in s:
        if ch in TRANSLIT:
            out.append(TRANSLIT[ch])
        elif ch.isalnum() and ch.isascii():
            out.append(ch)
        else:
            out.append("-")
    slug = re.sub(r"-+", "-", "".join(out)).strip("-")
    return slug


def cover_crop(im, w, h):
    return ImageOps.fit(im.convert("RGB"), (w, h), Image.LANCZOS, centering=(0.5, 0.5))


def save(im, path, q=82):
    im.save(path, "JPEG", quality=q, optimize=True, progressive=True)


def photo(src, dest, w=960, h=720, q=82, centering=(0.5, 0.5)):
    im = Image.open(src).convert("RGB")
    im = ImageOps.fit(im, (w, h), Image.LANCZOS, centering=centering)
    save(im, OUT / dest, q)
    return dest


def scheme(src, dest, w=960, h=720):
    """Чертёж: автокроп белых полей, вписать на белый холст с воздухом."""
    im = Image.open(src).convert("RGB")
    gray = im.convert("L")
    # маска «не-белого» с запасом на антиалиасинг
    bbox = gray.point(lambda p: 0 if p > 246 else 255).getbbox()
    if bbox:
        pad = 8
        bbox = (max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad))
        im = im.crop(bbox)
    margin = 0.10
    box_w, box_h = int(w * (1 - margin * 2)), int(h * (1 - margin * 2))
    im.thumbnail((box_w, box_h), Image.LANCZOS)
    canvas = Image.new("RGB", (w, h), WHITE)
    canvas.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    save(canvas, OUT / dest, 88)
    return dest


# ---------------------------------------------------------------- галерея
# Чистые кадры из галереи сайта: hash → как используем (проверено глазами).
G = {
    "33f4807fff49220050108b907a785524": "supermonterrey-wet",     # тёмно-серая, капли
    "c487802bce4e18ad0efed288e066b10a": "supermonterrey-graphite",
    "e10ff3a6a673126142ff39caa83ff535": "supermonterrey-green",
    "5d622f5ff6154e284418b27b83ed9890": "dyuna-brown",            # смещённые модули
    "f61a6713eac3e0fc8852e32ecbeb56ec": "dyuna-terracotta",
    "b5a97e522851e752ebf5bef87459ebeb": "shtaketnik-chocolate",
    "be3d177640c99dc485660d3e0979e7df": "shtaketnik-graphite",    # на фоне зелени
    "b9894d18845f3db3b037f11f529e992c": "shtaketnik-cherry",      # printech вишня
    "e26ee5cfb7f5d8e12b99f8a0dc39f9ed": "shtaketnik-pine",
    "4376c97fe177dd808e95fc6b056ffdd3": "sayding-dark",
    "ec61408e4b082de81716159fe1874387": "sayding-oak",
    "9651a03097a25fb6584b83900f8e71b1": "sayding-walnut",
    "785b0c2939070dc4c053ac47f51adca6": "sayding-light",
    "eec25d69d4439529d2fc1dddf1170a06": "sayding-white",
}
gal = {}
for h, key in G.items():
    p = GAL / f"{h}.jpg"
    if p.exists():
        gal[key] = p
    else:
        print(f"!! нет кадра галереи {key} ({h})")

# Профнастил: фото ЕСТЬ ТОЛЬКО у поставщика, все под тайловым водяным знаком
# по всему кадру (кроп не спасает — проверено). По решению пользователя
# (17.07.2026) грузим как есть — временная мера, до появления чистых фото.
PROF_G = {
    "09adc01207b89d00c24ede84fab8a5ef": "s8-1",
    "f45fd7ce52023363a8a814356e064d41": "s8-2",
    "778098753bd9d089adb99b3a84506c86": "s8-3",
    "1d0c1365aeb94edfd7109b16a9b8b7cc": "s10-1",
    "320c8e7b4416bad26cc276e90911a148": "s10-2",
    "263811f395be29e805823c252face073": "mp20-1",
    "5c16994910d84e2b105f1d3197e75b3d": "mp20-2",
    "83c032aa81cd4b1a94c7663a54a2fb58": "s21-1",
    "df9a4cc8bb8d85620d2f0bda390ee24c": "s21-2",
    "0eb15032566317244de9d7f65613515a": "ns35-1",
    "a1a9b10c1b22082e5a44ec8368ac6a34": "ns35-2",
    "39cc75ff369c64e640be135bdd125f2f": "n60-1",
    "7f06db8bd26aeb4173d9f145f3d41a13": "n60-2",
}
prof_gal = {}
for h, key in PROF_G.items():
    p = PROF_GAL / f"{h}.jpg"
    if p.exists():
        prof_gal[key] = p
    else:
        print(f"!! нет фото профнастила {key} ({h})")

manifest = {"products": {}, "colors": {}, "sections": {}}

# герой: мокрая тёмная металлочерепица (16:9 для десктопного hero)
im = Image.open(gal["supermonterrey-wet"]).convert("RGB")
save(cover_crop(im, 1200, 800), OUT / "hero-roof.jpg", 84)

# ------------------------------------------------------------- товары
# Галереи товарных страниц: чистые фото + схема из папки товара.
PRODUCTS = [
    # id, папка поставщика, [фото из галереи]
    ("mch-monterrey", "Металлочерепица/Супермонтеррей",
     ["supermonterrey-graphite", "supermonterrey-wet", "supermonterrey-green"]),
    ("mch-dyuna", "Металлочерепица/Испанская дюна",
     ["dyuna-brown", "dyuna-terracotta"]),
    ("prof-s8", "Профнастил/Профилированный лист С-8",
     ["s8-1", "s8-2", "s8-3"]),
    ("prof-s10", "Профнастил/Профилированный лист С-10",
     ["s10-1", "s10-2"]),
    ("prof-s21", "Профнастил/Профилированный лист С-21",
     ["s21-1", "s21-2"]),
    ("prof-mp20", "Профнастил/Профилированный лист МП-20",
     ["mp20-1", "mp20-2"]),
    ("prof-ns35", "Профнастил/Профилированный лист НС-35",
     ["ns35-1", "ns35-2"]),
    ("prof-n60", "Профнастил/Профилированный лист Н-60",
     ["n60-1", "n60-2"]),
    ("sht-kruglyy", "Штакетник/EURO-штакетник круглый",
     ["shtaketnik-chocolate", "shtaketnik-graphite", "shtaketnik-cherry",
      "shtaketnik-pine"]),
    ("sht-trapetsiya", "Штакетник/EURO-штакетник трапеция", []),
    ("sht-pryamoy", "Штакетник/ШТАКЕТНИК С ПРЯМЫМ РЕЗОМ", []),
    ("sid-korabelnaya", "Сайдинг и доборные элементы/Корабельная доска", []),
    ("sid-korabelnaya-evro", "Сайдинг и доборные элементы/Корабельная доска EURO", []),
    ("sid-brus-klassik", "Сайдинг и доборные элементы/Сайдинг EURO-Брус Классик", []),
    ("sid-brus-riflenyy", "Сайдинг и доборные элементы/Сайдинг EURO-Брус Рифленый", []),
    ("sid-sofit", "Сайдинг и доборные элементы/Софит EURO-Брус перфорированный", []),
]

for pid, rel, photos in PRODUCTS:
    pdir = SRC / rel
    entry = {"gallery": [], "scheme": None}
    for i, key in enumerate(photos):
        name = f"roof-{pid}.jpg" if i == 0 else f"roof-{pid}-{i + 1}.jpg"
        photo(gal.get(key) or prof_gal[key], name)
        entry["gallery"].append(name)
    schemes = [f for f in pdir.iterdir()
               if "_схема" in f.name and f.suffix.lower() in (".jpg", ".jpeg", ".png")]
    if schemes:
        entry["scheme"] = scheme(schemes[0], f"roof-{pid}-scheme.jpg")
    manifest["products"][pid] = entry

# обложки карточек металлочерепицы и секций на странице категории
save(cover_crop(Image.open(gal["supermonterrey-graphite"]), 900, 900),
     OUT / "cover-mch-monterrey.jpg")
save(cover_crop(Image.open(gal["dyuna-brown"]), 900, 900),
     OUT / "cover-mch-dyuna.jpg")
save(cover_crop(Image.open(gal["shtaketnik-graphite"]), 1100, 820),
     OUT / "sec-shtaketnik.jpg")
save(cover_crop(Image.open(gal["sayding-dark"]), 1100, 820),
     OUT / "sec-sayding.jpg")
manifest["sections"] = {
    "shtaketnik": "sec-shtaketnik.jpg",
    "sayding": "sec-sayding.jpg",
}

# примеры покрытия Printech вживую (для страниц сайдинга/штакетника)
PRINTECH_LIVE = ["sayding-oak", "sayding-walnut", "sayding-light", "sayding-white"]
manifest["printech_live"] = []
for i, key in enumerate(PRINTECH_LIVE, 1):
    name = f"printech-live-{i}.jpg"
    photo(gal[key], name)
    manifest["printech_live"].append(name)

# ------------------------------------------------------------- цвета
# Серии покрытий: большие текстуры со страницы «Коллекция» (map),
# фолбэк — локальные миниатюрки из папок «Цвета».
cmap = json.loads((TEX / "collection_map.json").read_text())

SERIES_RU = {"Полиэстер": "polyester", "Granite® Deep Mat": "granite",
             "Printech": "printech", "Цинк": "zink"}

# Человеческие подписи для кодовых имён
RAL_RU = {
    "3009": "Красная окись", "6020": "Тёмная зелень", "7024": "Графит",
    "8004": "Терракота", "8017": "Шоколад", "9005": "Чёрный",
    "RR32": "Тёмный шоколад",
}

# У Printech-текстур тайловый водяной знак — для кружка берём размеченную
# глазами чистую зону (доли ширины/высоты кадра). По умолчанию — центр.
PRINTECH_CROPS = {
    "Античный дуб": (0.51, 0.35, 0.73, 0.64),
    "Вишня Темная": (0.02, 0.02, 0.24, 0.31),
    "Бельгийский Кирпич": (0.02, 0.02, 0.24, 0.31),
    "Береза Белая": (0.02, 0.02, 0.24, 0.31),
    "Орех Темный": (0.51, 0.36, 0.71, 0.62),
    "Дикий камень": (0.52, 0.70, 0.74, 0.97),
    "Кирпич": (0.27, 0.35, 0.49, 0.64),
    "Античный Дуб двухсторонний": (0.14, 0.68, 0.30, 0.82),
    "Светлое дерево": (0.13, 0.35, 0.28, 0.49),
    "Сосна светлая": (0.02, 0.36, 0.23, 0.64),
    "Ясень Светлый": (0.02, 0.36, 0.23, 0.64),
    "Каштан": (0.02, 0.74, 0.23, 0.99),
}


def norm(s):
    return re.sub(r"[^\wа-яё]+", " ", s.lower().replace("ё", "е")).strip()


tex_by_name = {}
for ser in cmap:
    for c in ser["colors"]:
        big = (c.get("big") or c["thumb"]).split("/")[-1]
        tex_by_name[norm(c["name"])] = (ser["series"], big)

colors = {}
for ser in cmap:
    skey = SERIES_RU[ser["series"]]
    for c in ser["colors"]:
        name = c["name"].replace("®", "").strip()
        slug = slugify(name)
        big = (c.get("big") or c["thumb"]).split("/")[-1]
        src = TEX / big
        if not src.exists():
            print(f"!! нет текстуры {name} ({big})")
            continue
        im = Image.open(src).convert("RGB")
        # кружок: чистая зона (Printech со знаком) или центральный квадрат
        crop = PRINTECH_CROPS.get(name)
        if crop:
            w, h = im.size
            im = im.crop((int(crop[0] * w), int(crop[1] * h),
                          int(crop[2] * w), int(crop[3] * h)))
        sw = ImageOps.fit(im, (124, 124), Image.LANCZOS)
        save(sw, OUT / f"sw-{slug}.jpg", 86)

        # подпись: «Шоколад» + код
        label, code = name, ""
        m = re.match(r"RAL\s+NL\s*805\s*(.*)", name)
        if m:
            label, code = m.group(1).strip() or "Шоколад глянец", "RAL NL 805"
        else:
            m = re.match(r"RAL\s+(\d{4})\s*(.*)", name)
            if m:
                code, label = f"RAL {m.group(1)}", m.group(2).strip() or m.group(1)
            elif name.startswith("RR 32"):
                code, label = "RR 32", "Тёмный шоколад"
            elif "Deep Mat" in name:
                c2 = name.split()[-1]
                code = f"Granite {c2}"
                label = RAL_RU.get(c2, c2)
        colors[slug] = {
            "name": name, "label": label, "code": code, "series": skey,
            "sw": f"sw-{slug}.jpg",
        }
manifest["colors"] = colors

# --------------------------------------------- цвета по товарам (из папок)
def product_colors(pdir):
    cd = pdir / "Цвета"
    if not cd.exists():
        return []
    got = []
    for f in sorted(cd.iterdir()):
        if f.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            continue
        n = norm(f.stem.replace("®", ""))
        slug = None
        for s, c in colors.items():
            if norm(c["name"]) == n:
                slug = s
                break
        if slug:
            got.append(slug)
        else:
            print(f"!! цвет без текстуры: {f.stem} ({pdir.name})")
    return got


manifest["product_colors"] = {}
for pid, rel, _ in PRODUCTS:
    manifest["product_colors"][pid] = product_colors(SRC / rel)

(BASE / "data" / "roof_images.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=1))

n_files = len(list(OUT.glob("*.jpg")))
print(f"OK: {n_files} файлов в img/roof/, {len(colors)} цветов, "
      f"{len(manifest['products'])} товаров")
