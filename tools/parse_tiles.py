#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Тротуарная плитка (Легион) → data/tiles.json.

Источник: ~/Desktop/фото/Тротурная плитка/ — 7 форм × ~24 цвета + 2 бордюра.
Имя поставщика на сайт НЕ выводим (принцип коллекций).

Классификация фото по углам кадра:
- белые углы → рендер-плашка (водяной знак по центру, в кроп не годится);
- углы с текстурой → плоская текстура (чистый угловой кроп для карточки).
"""

import json
import re
from datetime import date
from pathlib import Path
from PIL import Image

SRC = Path("/Users/dm/Desktop/фото/Тротурная плитка")
OUT = Path("/Users/dm/Desktop/сайт/data/tiles.json")

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


def clean_name(raw):
    n = re.sub(r"\s*\((А|Б|П)\)\s*$", "", raw.strip())
    n = n.replace("Инь ян", "Инь и Ян").replace("Инь и ян", "Инь и Ян")
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
    """Белые (или прозрачные) углы → рендер-плашка на белом фоне."""
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    pts = [(4, 4), (w - 5, 4), (4, h - 5), (w - 5, h - 5)]
    return sum(1 for p in pts if min(img.getpixel(p)) > 228) >= 3


def main():
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
            texture = render = None
            for f in sorted(prod_dir.rglob("*.webp")):
                rel = str(f.relative_to(SRC))
                if is_render(f):
                    render = render or rel
                else:
                    texture = texture or rel
            idx += 1
            products.append({
                "id": f"tile-{idx:03d}",
                "shape": slug,
                "name": name,
                "mono": name.startswith("Моно"),
                "price": price,
                "specs": specs,
                "texture": texture,
                "render": render,
            })

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
        price, _ = parse_txt(txt)
        photo = next((f for f in sorted(d.glob("*.webp"))
                      if not f.name.startswith("sert")), None)
        borders.append({
            "id": f"bordur-{i}",
            "name": bname,
            "price": price,
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

    n_tex = sum(1 for p in products if p["texture"])
    n_only_render = sum(1 for p in products if not p["texture"] and p["render"])
    n_none = sum(1 for p in products if not p["texture"] and not p["render"])
    print(f"товаров: {len(products)} · с текстурой: {n_tex} · "
          f"только рендер: {n_only_render} · без фото: {n_none}")
    for slug, m in shapes_meta.items():
        print(f"  {m['name']}: {m['count']} шт, от {m['min_price']} ₽/м²")
    print("бордюры:", [(b["name"], b["price"]) for b in borders])


if __name__ == "__main__":
    main()
