#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Русская микротипографика: неразрывные пробелы в готовом HTML.

Правило (жалоба пользователя 24.07.2026): предлог не должен «висеть» в конце
строки — «расчёт с / доставкой», «кирпич под / дом», «от абрикоса до / графита».
Такое решается только неразрывным пробелом, CSS тут не помогает.

Что делает typo():
1. после коротких предлогов и союзов (в, с, на, от, до, для, под, и, а, но…)
   ставит &nbsp; — слово уезжает на новую строку вместе с предлогом;
2. перед частицами (же, ли, бы, б) — они не должны начинать строку;
3. склеивает число с тем, что за ним: «5 минут», «40 мм», «650 ₽», «1 105 ₽»;
4. склеивает сокращения с именем: «ул. Ореховая»;
5. привязывает тире к предыдущему слову — «дорожки, двор и парковка&nbsp;—»,
   чтобы длинное тире не начинало строку.

Чего НЕ трогает: теги и их атрибуты, комментарии, <script>, <style>, <title>.
Функция идемпотентна — повторный прогон ничего не меняет.

Использование:
    from nbsp import typo
    path.write_text(typo(html))          # в генераторах
    python3 tools/nbsp.py [файлы…]       # разово для страниц, собранных руками
"""

import re
import sys
from pathlib import Path

NBSP = "&nbsp;"

# куски, внутрь которых лезть нельзя (порядок важен: комментарий раньше тега)
OPAQUE = re.compile(
    r"(<!--.*?-->"
    r"|<script\b[^>]*>.*?</script>"
    r"|<style\b[^>]*>.*?</style>"
    r"|<title\b[^>]*>.*?</title>"
    r"|<[^>]*>)",
    re.S | re.I,
)

# Предлоги, союзы и отрицания: их нельзя отрывать от следующего слова.
# Только короткие (1–3 буквы) — правило русской типографики.
AFTER = [
    "а", "и", "но", "да", "или", "то", "как", "что", "чем",
    "не", "ни", "в", "во", "к", "ко", "с", "со", "о", "об", "обо",
    "у", "из", "изо", "от", "ото", "до", "за", "на", "по",
    "над", "под", "при", "про", "для", "без", "безо",
]
RE_AFTER = re.compile(
    r"(?<![\w\-])(" + "|".join(sorted(AFTER, key=len, reverse=True)) + r")(\s+)(?![\s<]|&nbsp;)",
    re.I,
)

# Частицы: не должны начинать строку — приклеиваем к предыдущему слову.
RE_BEFORE = re.compile(r"(\s+)(же|ли|ль|бы|б)(?![\w\-])", re.I)

# Число + следующее слово («5 минут», «40 мм», «650 ₽», «470+ товаров»).
RE_NUM = re.compile(r"(\d[+]?)(\s+)(?=([\w₽%°²³]+))", re.U)
MAX_UNIT = 14  # слишком длинное слово к числу не клеим — распирает узкие карточки

# Разряды числа: «1 105 ₽» — пробел внутри числа неразрывный всегда.
RE_DIGITS = re.compile(r"(\d)(\s+)(?=\d)")

# Сокращение + имя собственное: «ул. Ореховая», «г. Краснодар».
RE_ABBR = re.compile(r"(?<![\w\-])(ул|г|д|стр|обл|кв|им|т|стр)\.(\s+)(?=[^\s<&])", re.I)

# Тире не начинает строку — прилипает к предыдущему слову, но только если это
# слово короткое: «хозяйственный&nbsp;—» распирает узкие карточки при системном
# шрифте 200% (проверено сканером на 280px — заголовок вылезал за экран).
RE_DASH = re.compile(r"(\s+)(—|–)(?=\s)")
DASH_MAX_WORD = 6


def _num_repl(m: re.Match) -> str:
    word = m.group(3)
    return m.group(1) + (NBSP if len(word) <= MAX_UNIT else m.group(2))


def _dash_repl(m: re.Match) -> str:
    tail = m.string[:m.start()]
    word = re.split(r"[\s>]", tail)[-1] if tail else ""
    keep = 0 < len(word) <= DASH_MAX_WORD
    return (NBSP if keep else m.group(1)) + m.group(2)


def _fix_text(text: str) -> str:
    if not text.strip():
        return text
    text = RE_AFTER.sub(lambda m: m.group(1) + NBSP, text)
    text = RE_BEFORE.sub(lambda m: NBSP + m.group(2), text)
    text = RE_DIGITS.sub(lambda m: m.group(1) + NBSP, text)
    text = RE_NUM.sub(_num_repl, text)
    text = RE_ABBR.sub(lambda m: m.group(1) + "." + NBSP, text)
    text = RE_DASH.sub(_dash_repl, text)
    return text


# Предлог перед началом ссылки склеивается с ней («соглашаетесь с&nbsp;<a>политикой»),
# а вот перед закрывающим тегом и <br> неразрывный пробел не нужен — он там висит впустую.
RE_TAIL = re.compile(r"&nbsp;(?=</|<br)", re.I)


def typo(html_text: str) -> str:
    """Расставить неразрывные пробелы в тексте страницы."""
    parts = OPAQUE.split(html_text)
    for i in range(0, len(parts), 2):  # чётные индексы — текст между тегами
        parts[i] = _fix_text(parts[i])
    return RE_TAIL.sub(" ", "".join(parts))


def _plain(s: str) -> str:
    """Текст без учёта вида пробелов — для проверки, что смысл не изменился."""
    return re.sub(r"\s+", " ", s.replace(NBSP, " ").replace(" ", " "))


def main(argv: list[str]) -> int:
    base = Path(__file__).resolve().parent.parent
    if argv:
        files = [Path(a) for a in argv]
    else:
        files = sorted(base.glob("*.html")) + sorted((base / "tovar").glob("*.html"))
    changed = 0
    for f in files:
        src = f.read_text()
        out = typo(src)
        if _plain(src) != _plain(out):  # страховка: текст должен остаться прежним
            print(f"ОШИБКА: {f.name} — текст изменился, файл не тронут")
            continue
        if out != src:
            f.write_text(out)
            changed += 1
    print(f"Обработано файлов: {len(files)}, изменено: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
