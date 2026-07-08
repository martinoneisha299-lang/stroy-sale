#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Фото плитки → img/catalog/tile-*.jpg + обложки форм + герой + бордюры.

Текстуры: водяной знак по центру кадра → берём чистый верхний левый угол
(40% высоты, пропорция 4:3) и растягиваем до 640×480. На типичной текстуре
900×900 это кроп 480×360 — запас качества достаточный.
"""

import json
from pathlib import Path
from PIL import Image, ImageOps

SRC = Path("/Users/dm/Desktop/фото/Тротурная плитка")
SITE = Path("/Users/dm/Desktop/сайт")
CAT = SITE / "img" / "catalog"
PLITKA = SITE / "img" / "plitka"
W, H = 640, 480
PAPER = (250, 249, 247)

CAT.mkdir(parents=True, exist_ok=True)
PLITKA.mkdir(parents=True, exist_ok=True)

DATA = json.loads((SITE / "data" / "tiles.json").read_text())


def save(img, dst, q=76):
    img.save(dst, "JPEG", quality=q, optimize=True, progressive=True)


def corner_crop(path):
    """Чистый верхний левый угол текстуры, 4:3."""
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    w, h = img.size
    ch = int(h * 0.40)
    cw = min(int(ch * 4 / 3), w)
    ch = int(cw * 3 / 4)
    return img.crop((0, 0, cw, ch)).resize((W, H), Image.LANCZOS)


def fit_on_paper(path):
    canvas = Image.new("RGB", (W, H), PAPER)
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGBA")
    img.thumbnail((int(W * 0.92), int(H * 0.92)), Image.LANCZOS)
    canvas.paste(img, ((W - img.width) // 2, (H - img.height) // 2), img)
    return canvas


def cover_crop(path, w=W, h=H):
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    return ImageOps.fit(img, (w, h), Image.LANCZOS)


def main():
    done = 0
    # карточки товаров: чистый угловой кроп текстуры
    for p in DATA["products"]:
        if not p["texture"]:
            continue
        save(corner_crop(SRC / p["texture"]), CAT / f"{p['id']}.jpg")
        done += 1

    # бордюры: белый фон → вписываем на подложку
    for b in DATA["borders"]:
        if b["photo"]:
            save(fit_on_paper(SRC / b["photo"]), CAT / f"{b['id']}.jpg")
            done += 1

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
    print(f"готово: {done} файлов, ~{total_kb} КБ")


if __name__ == "__main__":
    main()
