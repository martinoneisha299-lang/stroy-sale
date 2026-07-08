#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""catalog.json → КАТАЛОГ-ТАБЛИЦА.xlsx: проверочная таблица для пользователя."""

import json
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

DATA = json.loads(Path("/Users/dm/Desktop/сайт/data/catalog.json").read_text())
OUT = "/Users/dm/Desktop/сайт/КАТАЛОГ-ТАБЛИЦА.xlsx"

products = DATA["products"]
CAT_RU = {"oblitsovochnyy": "Облицовочный", "obychnyy": "Забутовочный"}
COLL_RU = DATA["collections"]

HEAD = ["ID", "Коллекция", "Категория", "Название на сайте", "Цвет (завод)",
        "Группа цвета", "Фактура", "Формат", "Цена ₽/шт", "Цена ₽/м²",
        "Цены по форматам", "Расход шт/м²", "Фото, шт", "Видео",
        "Проверить", "Заводское название", "Поставщик (на сайт НЕ выводим)"]

wb = Workbook()

# ── Лист «Каталог» ────────────────────────────────────────────────────────────
ws = wb.active
ws.title = "Каталог"
ws.append(HEAD)

header_fill = PatternFill("solid", start_color="21201C")
warn_fill = PatternFill("solid", start_color="FFF3C4")
nophoto_fill = PatternFill("solid", start_color="FBE0DC")
thin = Border(bottom=Side(style="thin", color="DDDDDD"))

for c in range(1, len(HEAD) + 1):
    cell = ws.cell(row=1, column=c)
    cell.font = Font(name="Arial", bold=True, color="FFFFFF", size=10)
    cell.fill = header_fill
    cell.alignment = Alignment(vertical="center", wrap_text=True)

for p in sorted(products, key=lambda x: (x["category"], x["collection"] or "я",
                                         x["name"])):
    fp = "; ".join(f"{k}: {v:.2f} ₽" for k, v in p["formats_prices"].items())
    ws.append([
        p["id"],
        COLL_RU.get(p["collection"], "—") if p["collection"] else "—",
        CAT_RU[p["category"]],
        p["name"],
        p["color_raw"] or "",
        p["color_group"],
        p["texture"],
        p["format"],
        p["price"],
        p.get("price_m2"),
        fp,
        p.get("consumption_per_m2"),
        len(p["photos"]),
        "да" if p.get("video") else "",
        "; ".join(p["flags"]),
        p["factory_name"],
        p["supplier"],
    ])

last = ws.max_row
for r in range(2, last + 1):
    for c in range(1, len(HEAD) + 1):
        cell = ws.cell(row=r, column=c)
        cell.font = Font(name="Arial", size=10)
        cell.border = thin
    if ws.cell(row=r, column=15).value:                      # флаги
        ws.cell(row=r, column=15).fill = warn_fill
    if ws.cell(row=r, column=13).value == 0:                 # нет фото
        ws.cell(row=r, column=13).fill = nophoto_fill
    ws.cell(row=r, column=9).number_format = "#,##0.00"
    ws.cell(row=r, column=10).number_format = "#,##0.00"

widths = [9, 16, 17, 26, 14, 14, 15, 18, 10, 10, 42, 11, 8, 6, 34, 46, 24]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = "E2"
ws.auto_filter.ref = f"A1:{get_column_letter(len(HEAD))}{last}"

# ── Лист «Сводка» ─────────────────────────────────────────────────────────────
sv = wb.create_sheet("Сводка")
sv["A1"] = "Сводка каталога «Строй-Сейл»"
sv["A1"].font = Font(name="Arial", bold=True, size=14)
sv["A2"] = f"Собрано автоматически из папки фото · {DATA['generated']}"
sv["A2"].font = Font(name="Arial", size=9, color="777777")

rows = [
    ("", ""),
    ("Всего товаров", f"=COUNTA(Каталог!A2:A{last})"),
    ("Облицовочный кирпич", f'=COUNTIF(Каталог!C2:C{last},"Облицовочный")'),
    ("Забутовочный", f'=COUNTIF(Каталог!C2:C{last},"Забутовочный")'),
    ("Без фото (докрасим/уточним)", f"=COUNTIF(Каталог!M2:M{last},0)"),
    ("Цена по запросу", f"=COUNTBLANK(Каталог!I2:I{last})"),
    ("С видео", f'=COUNTIF(Каталог!N2:N{last},"да")'),
    ("", ""),
]
r = 3
for label, formula in rows:
    sv.cell(row=r, column=1, value=label).font = Font(name="Arial", size=10)
    if formula:
        c = sv.cell(row=r, column=2, value=formula)
        c.font = Font(name="Arial", size=10, bold=True)
    r += 1

sv.cell(row=r, column=1, value="По коллекциям").font = Font(name="Arial", bold=True, size=11)
r += 1
for slug, name in COLL_RU.items():
    sv.cell(row=r, column=1, value=name).font = Font(name="Arial", size=10)
    sv.cell(row=r, column=2,
            value=f'=COUNTIF(Каталог!B2:B{last},"{name}")').font = Font(name="Arial", size=10, bold=True)
    sv.cell(row=r, column=3,
            value=f'=MINIFS(Каталог!I2:I{last},Каталог!B2:B{last},"{name}")').number_format = "#,##0.00"
    sv.cell(row=r, column=4,
            value=f'=MAXIFS(Каталог!I2:I{last},Каталог!B2:B{last},"{name}")').number_format = "#,##0.00"
    sv.cell(row=r, column=3).font = Font(name="Arial", size=10)
    sv.cell(row=r, column=4).font = Font(name="Arial", size=10)
    r += 1
sv.cell(row=r - len(COLL_RU) - 1, column=3, value="мин. ₽").font = Font(name="Arial", size=9, color="777777")
sv.cell(row=r - len(COLL_RU) - 1, column=4, value="макс. ₽").font = Font(name="Arial", size=9, color="777777")

r += 1
sv.cell(row=r, column=1, value="По цветам (облицовочный)").font = Font(name="Arial", bold=True, size=11)
r += 1
colors = sorted({p["color_group"] for p in products if p["category"] == "oblitsovochnyy"})
for col in colors:
    sv.cell(row=r, column=1, value=col).font = Font(name="Arial", size=10)
    sv.cell(row=r, column=2,
            value=(f'=COUNTIFS(Каталог!F2:F{last},"{col}",'
                   f'Каталог!C2:C{last},"Облицовочный")')).font = Font(name="Arial", size=10, bold=True)
    r += 1

for i, w in enumerate([30, 12, 10, 10], 1):
    sv.column_dimensions[get_column_letter(i)].width = w

wb.save(OUT)
print("OK →", OUT)
