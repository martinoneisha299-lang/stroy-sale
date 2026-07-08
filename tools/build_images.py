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
    data = json.loads(Path("/Users/dm/Desktop/сайт/data/catalog.json").read_text())
    done = skipped = 0
    for p in data["products"]:
        if p["category"] not in ("oblitsovochnyy", "obychnyy") or not p["photos"]:
            continue
        src = ROOT / p["dir"] / p["photos"][0]
        dst = OUT / f"{p['id']}.jpg"
        if not src.exists():
            print("нет файла:", src)
            skipped += 1
            continue
        img = ImageOps.exif_transpose(Image.open(src))
        if p["dir"].startswith("Губский") and src.suffix.lower() in (".jpg", ".jpeg"):
            # кадры видео из папки Губского: внизу справа водяной знак
            # конвертера clideo — срезаем (независимо от того, чей товар)
            img = img.crop((0, 0, img.width, int(img.height * 0.86)))
        if has_alpha(img) or white_corners(img):
            out = fit_on_paper(img)
        else:
            out = cover_crop(img)
        out.save(dst, "JPEG", quality=92, optimize=True, progressive=True)
        done += 1
    total_kb = sum(f.stat().st_size for f in OUT.glob("*.jpg")) // 1024
    print(f"готово: {done}, пропущено: {skipped}, всего {total_kb} КБ")


if __name__ == "__main__":
    main()
