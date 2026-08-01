"""
Индекс для поиска по сайту → data/search.json.

Читает УЖЕ СОБРАННЫЕ страницы, а не данные генераторов. Так индекс всегда
описывает то, что реально опубликовано: добавился раздел — он попал в поиск
сам, без правки этого скрипта.

Запускать последним, после всех build_*.py.
"""

import html as _html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from shell_common import BASE

RE_NAME = re.compile(r'<h1 class="pd-name">(.*?)</h1>', re.S)
RE_H1 = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
RE_MAIN = re.compile(r'<img class="pd-main"[^>]*src="\.\./([^"?]+)')
# Единицу («/м²», «/шт») забираем вместе с числом: без неё цена плитки
# в поиске выглядела как цена за штуку, хотя на витрине та же позиция
# подписана «за м²» — страницы противоречили друг другу по главному числу.
RE_PRICE = re.compile(r'<p class="pd-price"><b>(.*?)</b>(?:<span[^>]*>(.*?)</span>)?', re.S)
# Крошки берём ТОЛЬКО из блока .crumbs: тот же шаблон ссылки есть в футере,
# и без границы блока в ключи попадало всё меню сайта.
RE_CRUMBS_BLOCK = re.compile(r'<ol class="crumbs">(.*?)</ol>', re.S)
RE_CRUMB = re.compile(r"<li>(.*?)</li>", re.S)
RE_TAGS = re.compile(r"<[^>]+>")


def text(s):
    """Снять теги и раскодировать сущности — в индексе нужен чистый текст.

    Без unescape в имена попадали литералы «&nbsp;»: их расставляет nbsp.typo
    при записи страниц, и в JSON они выглядели бы как мусор.
    """
    return " ".join(_html.unescape(RE_TAGS.sub("", s)).split())


def build():
    items = []

    # ---- товары
    for f in sorted((BASE / "tovar").glob("*.html")):
        html = f.read_text(encoding="utf-8")
        m = RE_NAME.search(html)
        if not m:
            continue
        name = text(m.group(1))
        img = RE_MAIN.search(html)
        pm = RE_PRICE.search(html)
        price = text(pm.group(1)) if pm else ""
        unit = text(pm.group(2) or "") if pm else ""
        # крошки дают раздел и коллекцию — по ним тоже ищем.
        # Дедупликация обязательна: крошки встречаются и в шапке, и в блоке
        # «похожие», иначе ключи раздувают индекс втрое.
        seen, keys = set(), []
        block = RE_CRUMBS_BLOCK.search(html)
        crumbs = RE_CRUMB.findall(block.group(1))[1:-1] if block else []
        for c in crumbs:
            t = text(c)
            if t and t not in seen:
                seen.add(t)
                keys.append(t)
        rec = {"n": name, "u": f"tovar/{f.name}"}
        if img:
            rec["i"] = img.group(1)
        if price and "запрос" not in price.lower():
            rec["p"] = price          # символ ₽ уже внутри цены на странице
            if unit:
                rec["pu"] = unit      # «/м²» или «/шт» — вместе с косой чертой
        if keys:
            rec["k"] = " ".join(keys)
        items.append(rec)

    # ---- разделы: чтобы «плитка» находила саму витрину, а не только товары
    for f in sorted(BASE.glob("*.html")):
        if f.name in ("poisk.html", "zayavka.html", "policy.html", "index.html"):
            continue
        html = f.read_text(encoding="utf-8")
        m = RE_H1.search(html)
        if not m:
            continue
        items.append({"n": text(m.group(1)), "u": f.name, "k": "раздел каталог"})

    out = BASE / "data" / "search.json"
    out.write_text(json.dumps(items, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")
    kb = out.stat().st_size / 1024
    print(f"поиск: {len(items)} записей, {kb:.0f} КБ")


if __name__ == "__main__":
    build()
