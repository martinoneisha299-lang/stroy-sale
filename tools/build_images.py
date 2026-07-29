#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Фото товаров → img/catalog/{id}.jpg, единый кадр 4:3 640×480.

Правила кадра:
- PNG с прозрачностью (вырезанный кирпич) → вписываем на светлую подложку;
- фото с белым фоном (стопки Тандема, студийные PNG) → тоже вписываем;
- «живые» кадры (стенды Губского) → кроп по центру до 4:3.
"""

import json
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path("/Users/dm/Desktop/фото")
OUT = Path("/Users/dm/Desktop/сайт/img/catalog")
W, H = 1200, 900
PAPER = (250, 249, 247)
PAD = 0.92  # доля кадра под товар в режиме «вписать»

OUT.mkdir(parents=True, exist_ok=True)


def has_alpha(img):
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        a = img.convert("RGBA").getchannel("A")
        return a.getextrema()[0] < 250
    return False


def white_corners(img):
    rgb = img.convert("RGB")
    w, h = rgb.size
    pts = [(3, 3), (w - 4, 3), (3, h - 4), (w - 4, h - 4)]
    return all(min(rgb.getpixel(p)) > 232 for p in pts)


def white_share(img):
    """Доля почти-белых пикселей. У студийного кадра «кирпич на белом» она
    большая, у кадра кладки во всю рамку — маленькая."""
    small = img.convert("RGB").resize((64, 64), Image.BILINEAR)
    px = list(small.getdata())
    return sum(1 for r, g, b in px if r > 238 and g > 238 and b > 238) / len(px)


def is_studio(img):
    """Кадр «объект на белом фоне» (студийный) против полнокадрового.

    Полнокадровый кадр — кладка или текстура во всю рамку — это то, чем товар
    выбирают на самом деле (так показывает кирпич Brickhunter). Студийный
    кирпич в пустом поле и есть главная причина «дешёвого» вида карточки.
    """
    if has_alpha(img):
        return True
    # Белые углы сами по себе не приговор: у части кадров «Палитры» белый фон
    # запечён в файл узкими полосами сверху и снизу, а сам кадр — кладка.
    # Решает доля белого по всему кадру, а не четыре угловые точки.
    return white_corners(img) and white_share(img) > 0.34


def trim_white(img, tol=238):
    """Срезать запечённые белые поля по краям (у «Палитры» они в файле).

    Без этого даже верный кадр кладки даёт белые полосы сверху и снизу,
    когда карточка кадрирует его под 4:3.
    """
    rgb = img.convert("RGB")
    mask = rgb.point(lambda v: 255 if v < tol else 0).convert("L")
    box = mask.getbbox()
    if not box:
        return img
    x0, y0, x1, y1 = box
    # Страховка от съедания кадра целиком. Порог низкий (40%): у панелей
    # «Палитры» белые поля занимают до половины высоты, и при пороге 66%
    # обрезка откатывалась назад — полосы оставались в карточке.
    w, h = rgb.size
    if (x1 - x0) < w * 0.40 or (y1 - y0) < h * 0.40:
        return rgb
    return rgb.crop((x0, y0, x1, y1))


def fit_on_paper(img):
    canvas = Image.new("RGB", (W, H), PAPER)
    img = img.convert("RGBA")
    img.thumbnail((int(W * PAD), int(H * PAD)), Image.LANCZOS)
    pos = ((W - img.width) // 2, (H - img.height) // 2)
    canvas.paste(img, pos, img)
    return canvas


def cover_crop(img):
    return ImageOps.fit(img.convert("RGB"), (W, H), Image.LANCZOS)


def main():
    data = json.loads(Path("/Users/dm/Desktop/сайт/_data/catalog.json").read_text())
    done = skipped = 0
    # Clean stale gallery extras ТОЛЬКО для id кирпича (эта папка img/catalog
    # общая с плиткой/бордюрами — их трогать нельзя, те собирает другой скрипт).
    # Иначе после уменьшения кол-ва фото на диске останутся файлы -4.jpg/-5.jpg
    # от прошлой сборки, и build_category.py подхватит их как «существующие».
    brick_ids = {p["id"] for p in data["products"]
                 if p["category"] in ("oblitsovochnyy", "obychnyy")}
    # Чистим и базовый {id}.jpg: при добавлении товаров id сдвигаются, и
    # товар без фото иначе унаследует «чужой» кадр со старого номера.
    for pid in brick_ids:
        for f in ([OUT / f"{pid}.jpg", OUT / f"cdot-{pid}.jpg"]
                  + [OUT / f"{pid}-{s}.jpg" for s in (2, 3, 4, 5)]):
            if f.exists():
                f.unlink()

    promoted = 0
    main_kind = {}
    for p in data["products"]:
        if p["category"] not in ("oblitsovochnyy", "obychnyy") or not p["photos"]:
            continue

        # --- выбор ГЛАВНОГО кадра -------------------------------------
        # Раньше главным всегда становился первый файл из папки — а это, как
        # правило, студийный кирпич на белом. Теперь вперёд выходит первый
        # полнокадровый кадр (кладка/текстура), студийный уходит вторым и
        # показывается по наведению. Ищем только среди первых четырёх: дальше
        # в папках поставщиков начинается всякое (сертификаты, кадры видео).
        loaded = []
        for name in p["photos"][:5]:
            src = ROOT / p["dir"] / name
            if not src.exists():
                print("нет файла:", src)
                continue
            img = ImageOps.exif_transpose(Image.open(src))
            if p["dir"].startswith("Губский") and src.suffix.lower() in (".jpg", ".jpeg"):
                # кадры видео из папки Губского: внизу справа водяной знак
                # конвертера clideo — срезаем (независимо от того, чей товар)
                img = img.crop((0, 0, img.width, int(img.height * 0.86)))
            loaded.append((name, img, is_studio(img)))

        if not loaded:
            skipped += 1
            continue

        wall_at = next((i for i, (_, _, studio) in enumerate(loaded[:4]) if not studio), None)
        if wall_at not in (None, 0):
            loaded.insert(0, loaded.pop(wall_at))
            promoted += 1

        main_kind[p["id"]] = "studio" if loaded[0][2] else "wall"
        for idx, (photo_name, img, studio) in enumerate(loaded):
            dst = OUT / (f"{p['id']}.jpg" if idx == 0 else f"{p['id']}-{idx + 1}.jpg")
            if studio:
                out = fit_on_paper(img)
            else:
                out = cover_crop(trim_white(img))
            out.save(dst, "JPEG", quality=80, optimize=True, progressive=True)
            if idx == 0:
                # мини-кружок 68×68 для .cdot/свотчей: кружок 34px не должен
                # тянуть полноразмерный кадр (это давало ~3 МБ на категорию)
                w, h = out.size
                side = min(w, h)
                sq = out.crop(((w - side) // 2, (h - side) // 2,
                               (w + side) // 2, (h + side) // 2))
                sq = sq.resize((68, 68), Image.LANCZOS)
                sq.save(OUT / f"cdot-{p['id']}.jpg", "JPEG",
                        quality=82, optimize=True)
            done += 1
    # Тип главного кадра — в данные: подборки на главной должны показывать
    # товар кладкой, а не одиноким кирпичом на белом.
    Path("/Users/dm/Desktop/сайт/_data/main_frames.json").write_text(
        json.dumps(main_kind, ensure_ascii=False, indent=1), encoding="utf-8")
    walls = sum(1 for v in main_kind.values() if v == "wall")
    total_kb = sum(f.stat().st_size for f in OUT.glob("*.jpg")) // 1024
    print(f"готово: {done}, пропущено: {skipped}, всего {total_kb} КБ")
    print(f"кладка поднята главным кадром у {promoted} товаров")
    print(f"главный кадр — кладка/текстура у {walls} из {len(main_kind)} товаров")


if __name__ == "__main__":
    main()
