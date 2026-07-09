#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Фото плитки → img/catalog/tile-*.jpg (+ галерея), обложки форм, герой, бордюры.

Каждому товару — до 3 кадров 640×480:
- чистая текстура (без водяного знака) → целиком + приближенный фрагмент;
- текстура со знаком по центру → верхняя и нижняя чистые полосы
  (знак занимает ~44–58% высоты, полосы 0–40% и 62–100% безопасны).
Главный кадр = tile-XXX.jpg (карточки), доп. кадры = tile-XXX-2/-3.jpg
(галерея на странице товара). Рендеры с логотипом на сайт не идут.
"""

import json
from pathlib import Path
from PIL import Image, ImageOps

SRC = Path("/Users/dm/Desktop/фото/Тротурная плитка")
SITE = Path("/Users/dm/Desktop/сайт")
CAT = SITE / "img" / "catalog"
PLITKA = SITE / "img" / "plitka"
W, H = 1200, 900

CAT.mkdir(parents=True, exist_ok=True)
PLITKA.mkdir(parents=True, exist_ok=True)

DATA = json.loads((SITE / "data" / "tiles.json").read_text())


def save(img, dst, q=92):
    img.save(dst, "JPEG", quality=q, optimize=True, progressive=True)


def load(path):
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")


def band_crop(img, y0, y1):
    """Горизонтальная полоса кадра → 4:3, по центру ширины."""
    w, h = img.size
    ch = int(h * (y1 - y0))
    cw = min(int(ch * 4 / 3), w)
    ch = int(cw * 3 / 4)
    x = (w - cw) // 2
    top = int(h * y0)
    return img.crop((x, top, x + cw, top + ch)).resize((W, H), Image.LANCZOS)


def zoom_crop(img):
    """Приближенный фрагмент — деталь фактуры (верхняя левая треть кадра)."""
    w, h = img.size
    cw, ch = int(w * 0.58), int(w * 0.58 * 3 / 4)
    return img.crop((int(w * 0.04), int(h * 0.05),
                     int(w * 0.04) + cw, int(h * 0.05) + ch)) \
              .resize((W, H), Image.LANCZOS)


def cover_crop(path, w=W, h=H):
    return ImageOps.fit(load(path), (w, h), Image.LANCZOS)


def fit_on_white(path, w=W, h=H, pad=0.92):
    canvas = Image.new("RGB", (w, h), (255, 255, 255))
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGBA")
    img.thumbnail((int(w * pad), int(h * pad)), Image.LANCZOS)
    canvas.paste(img, ((w - img.width) // 2, (h - img.height) // 2), img)
    return canvas


def product_shots(p):
    """До 3 кадров товара без водяного знака поставщика.

    Рендеры и текстуры со знаком LEGION по центру целиком не публикуем:
    чистая текстура → весь кадр + зум, текстура со знаком → верхняя
    и нижняя чистые полосы (знак занимает ~44–58% высоты).
    """
    shots = []
    for im in p["images"]:
        if im.get("is_render", False) and not im.get("clean", False):
            continue
        img = load(SRC / im["path"])
        if im.get("clean", False):
            shots.append(ImageOps.fit(img, (W, H), Image.LANCZOS))
            if not im.get("is_render", False):
                shots.append(zoom_crop(img))
        else:
            shots.append(band_crop(img, 0.0, 0.40))
            shots.append(band_crop(img, 0.62, 1.0))
        if len(shots) >= 3:
            break
    return shots[:3]


def main():
    done = 0
    # старые кадры галереи чистим (набор мог поменяться)
    for f in CAT.glob("tile-*-*.jpg"):
        f.unlink()

    n_multi = 0
    for p in DATA["products"]:
        shots = product_shots(p)
        if not shots:
            continue
        save(shots[0], CAT / f"{p['id']}.jpg")
        for i, img in enumerate(shots[1:], 2):
            save(img, CAT / f"{p['id']}-{i}.jpg")
        p["_n"] = len(shots)
        n_multi += len(shots) > 1
        done += len(shots)

    # бордюры: белый фон → вписываем на белый холст
    for b in DATA["borders"]:
        if b["photo"]:
            save(fit_on_white(SRC / b["photo"]), CAT / f"{b['id']}.jpg")
            done += 1
    # квадратная обложка «Бордюры» для сетки форм
    save(fit_on_white(SRC / DATA["borders"][0]["photo"], 600, 600, pad=0.82),
         PLITKA / "shape-bordur.jpg", q=80)

    # обложки форм (исходники квадратные 500×500 — оставляем квадрат)
    for slug, m in DATA["shapes"].items():
        save(cover_crop(SRC / m["cover"], 600, 600),
             PLITKA / f"shape-{slug}.jpg", q=80)
        done += 1

    # герой: чистые рендеры без знака, с прозрачностью → webp
    for src_name, dst_name in [("plitka.webp", "hero-tiles-red.webp"),
                               ("plitka2.webp", "hero-tiles-grey.webp")]:
        img = Image.open(SRC / src_name).convert("RGBA")
        img.thumbnail((1100, 1100), Image.LANCZOS)
        img.save(PLITKA / dst_name, "WEBP", quality=82, method=6)
        done += 1

    # галерея «Наши работы»: отобраны вручную по контактному листу —
    # без штампов камеры, разные цвета и сюжеты (дом, бассейн, узор, дорожки)
    works = [
        "photo_2024-10-31_23-13-14.jpg",    # чёрно-белый микс, ёлка, небо
        "photo_2024-10-31_23-13-19.jpg",    # дом: кирпич + плитка вместе
        "photo_2024-10-31_23-13-23.jpg",    # двор с кованым забором
        "photo_2024-10-31_23-13-28.jpg",    # красно-чёрная у дома с садом
        "photo_2024-10-31_23-13-32.jpg",    # красная дорожка вдоль газона
        "photo_2024-10-31_23-13-52.jpg",    # современный дом, серая плитка
        "photo_2024-10-31_23-13-55.jpg",    # греческий узор жёлтым
        "photo_2024-10-31_23-13-56-2.jpg",  # бордовая плитка у бассейна
        "photo_2024-10-31_23-13-59-2.jpg",  # красно-жёлтая шахматка
        "photo_2024-10-31_23-14-02.jpg",    # двор частного дома
    ]
    for i, name in enumerate(works, 1):
        save(cover_crop(SRC / "Наши работы" / name, 800, 600),
             PLITKA / f"work-{i:02d}.jpg", q=78)
        done += 1

    # видео с укладки — в галерею работ
    video_dst = PLITKA / "works-video.mp4"
    if not video_dst.exists():
        video_dst.write_bytes((SRC / "IMG_3673_видео.mp4").read_bytes())

    total_kb = (sum(f.stat().st_size for f in CAT.glob("tile-*.jpg"))
                + sum(f.stat().st_size for f in PLITKA.iterdir())) // 1024
    print(f"готово: {done} файлов, ~{total_kb} КБ, "
          f"товаров с галереей 2+: {n_multi} из {len(DATA['products'])}")


if __name__ == "__main__":
    main()
