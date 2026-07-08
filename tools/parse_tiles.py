#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Тротуарная плитка (Легион) → data/tiles.json.

Источник: ~/Desktop/фото/Тротурная плитка/ — 7 форм × ~24 цвета + 2 бордюра.
Имя поставщика на сайт НЕ выводим (принцип коллекций).

Фото в папках товара (включая «Схемы раскладки») бывают трёх видов:
- рендер — 3D-поддон на белом фоне, логотип по центру → на сайт не берём;
- текстура с водяным знаком по центру → берём чистые полосы сверху/снизу;
- чистая текстура (без знака) → берём целиком.
Чистые размечены вручную по контактным листам → tools/clean_textures.json.
"""

import json
import re
from datetime import date
from pathlib import Path
from PIL import Image
import numpy as np

SRC = Path("/Users/dm/Desktop/фото/Тротурная плитка")
BASE = Path("/Users/dm/Desktop/сайт")
OUT = BASE / "data" / "tiles.json"
CLEAN_LIST = BASE / "tools" / "clean_textures.json"

IMG_EXTS = {".webp", ".jpg", ".jpeg", ".png"}

# порядок форм на странице: ходовые первыми
SHAPES = [
    ("novyy-gorod", "Новый город"),
    ("staryy-gorod", "Старый город"),
    ("bruschatka", "Брусчатка"),
    ("pryamougolnik", "Прямоугольник"),
    ("myunhen", "Мюнхен"),
    ("parket", "Паркет"),
    ("asgard", "Асгард"),
]

SPEC_KEYS = {
    "Высота": "height",
    "Количество в поддоне": "pallet_m2",
    "Вес поддона": "pallet_weight",
    "Количество м² в фуре": "truck_m2",
    "Класс по прочности": "strength",
    "Морозостойкость": "frost",
}

TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def slugify(name):
    s = "".join(TRANSLIT.get(c, c) for c in name.lower())
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def clean_name(raw):
    n = re.sub(r"\s*\((А|Б|П)\)\s*$", "", raw.strip())
    n = n.replace("Инь ян", "Инь и Ян").replace("Инь и ян", "Инь и Ян")
    n = n.replace("Темный", "Тёмный")
    return n


def parse_txt(path):
    text = path.read_text(encoding="utf-8")
    price = None
    m = re.search(r"Цена:\s*([\d\s]+)\s*₽", text)
    if m:
        price = int(m.group(1).replace(" ", ""))
    specs = {}
    for label, key in SPEC_KEYS.items():
        m = re.search(rf"- {re.escape(label)}:\s*(.+)", text)
        if m:
            specs[key] = m.group(1).strip()
    return price, specs


def is_render(img_path):
    """Рендер = сплошной белый фон по периметру (без тёмных швов).

    Углы недостаточно: у белой плитки углы тоже белые. Смотрим весь
    периметр: у текстуры его пересекают тёмные швы, у рендера — нет.
    """
    img = Image.open(img_path).convert("L")
    a = np.asarray(img, dtype=np.uint8)
    h, w = a.shape
    t = max(3, h // 50)
    border = np.concatenate([
        a[:t, :].ravel(), a[-t:, :].ravel(),
        a[:, :t].ravel(), a[:, -t:].ravel(),
    ])
    dark_frac = (border < 200).mean()
    return dark_frac < 0.005


def main():
    clean_set = set(json.loads(CLEAN_LIST.read_text()))
    products, idx = [], 0
    for slug, shape_name in SHAPES:
        shape_dir = SRC / shape_name
        for prod_dir in sorted(shape_dir.iterdir()):
            if not prod_dir.is_dir():
                continue
            txts = list(prod_dir.glob("*.txt"))
            if not txts:
                print("нет txt:", prod_dir)
                continue
            price, specs = parse_txt(txts[0])
            name = clean_name(prod_dir.name)

            textures, render = [], None
            files = sorted(f for f in prod_dir.rglob("*")
                           if f.suffix.lower() in IMG_EXTS)
            for f in files:
                rel = str(f.relative_to(SRC))
                if is_render(f):
                    # у рендеров поставщика логотип LEGION по центру — не «чистые»
                    render = render or rel
                    textures.append({"path": rel, "clean": rel in clean_set, "is_render": True})
                else:
                    textures.append({"path": rel, "clean": rel in clean_set, "is_render": False})
            # Сортировка: сначала чистые текстуры, затем текстуры с водяным знаком, затем рендеры
            textures.sort(key=lambda t: (t.get("is_render", False), not t["clean"]))

            idx += 1
            products.append({
                "id": f"tile-{idx:03d}",
                "shape": slug,
                "slug": f"{slug}-{slugify(name)}",
                "name": name,
                "mono": name.startswith("Моно"),
                "price": price,
                "specs": specs,
                "images": textures,
                "texture": textures[0]["path"] if textures else None,
                "render": render,
            })

    # проверка уникальности слогов (имена цветов повторяются между формами)
    slugs = [p["slug"] for p in products]
    assert len(slugs) == len(set(slugs)), "дубль слога: " + str(
        sorted({s for s in slugs if slugs.count(s) > 1}))

    shapes_meta = {}
    for slug, shape_name in SHAPES:
        items = [p for p in products if p["shape"] == slug]
        prices = [p["price"] for p in items if p["price"]]
        shapes_meta[slug] = {
            "name": shape_name,
            "count": len(items),
            "min_price": min(prices) if prices else None,
            "cover": f"Категории/{shape_name}.webp",
        }

    borders = []
    for i, (dname, bname) in enumerate(
            [("Бордюр дорожный", "Бордюр дорожный"),
             ("Бордюр садовый", "Бордюр садовый")], 1):
        d = SRC / dname
        txt = next(d.glob("*.txt"))
        price, bspecs = parse_txt(txt)
        photo = next((f for f in sorted(d.glob("*.webp"))
                      if not f.name.startswith("sert")), None)
        borders.append({
            "id": f"bordur-{i}",
            "name": bname,
            "price": price,
            "specs": bspecs,
            "photo": str(photo.relative_to(SRC)) if photo else None,
            "serts": [str(f.relative_to(SRC)) for f in sorted(d.glob("sert*.webp"))],
        })

    data = {
        "generated": date.today().isoformat(),
        "shapes": shapes_meta,
        "products": products,
        "borders": borders,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1))

    n_clean = sum(1 for p in products if p["images"] and p["images"][0]["clean"])
    n_wm = sum(1 for p in products if p["images"] and not p["images"][0]["clean"])
    n_none = sum(1 for p in products if not p["images"])
    print(f"товаров: {len(products)} · главное фото чистое: {n_clean} · "
          f"из полосы текстуры: {n_wm} · без фото: {n_none}")
    for slug, m in shapes_meta.items():
        print(f"  {m['name']}: {m['count']} шт, от {m['min_price']} ₽/м²")
    print("бордюры:", [(b["name"], b["price"]) for b in borders])
    if n_none:
        for p in products:
            if not p["images"]:
                print("  БЕЗ ФОТО:", p["shape"], p["name"], "| рендер:", bool(p["render"]))


if __name__ == "__main__":
    main()
