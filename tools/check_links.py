# -*- coding: utf-8 -*-
"""Проверка всех страниц сайта: битые внутренние ссылки, картинки, якоря.
Запуск: python3 tools/check_links.py (из корня проекта)"""
import pathlib, re, sys
from urllib.parse import unquote, urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
pages = sorted(ROOT.rglob('*.html'))
pages = [p for p in pages if '__pycache__' not in str(p)]

# id-якоря каждой страницы
ids = {}
for p in pages:
    s = p.read_text('utf-8')
    ids[p] = set(re.findall(r'\bid="([^"]+)"', s))

bad_links, bad_assets, bad_anchors = [], [], []
LINK = re.compile(r'(?:href|src)="([^"]+)"')

for p in pages:
    s = p.read_text('utf-8')
    for raw in LINK.findall(s):
        if raw.startswith(('http://', 'https://', 'mailto:', 'tel:', 'data:', '//')):
            continue
        url = unquote(raw)
        if url.startswith('#'):
            frag = url[1:]
            if frag and frag not in ids[p]:
                bad_anchors.append(f'{p.relative_to(ROOT)} → {url}')
            continue
        path_part, _, frag = url.partition('#')
        path_part = path_part.partition('?')[0]   # отрезаем ?v=N кэш-версии
        if not path_part:
            continue
        target = (p.parent / path_part).resolve()
        if not target.exists():
            (bad_assets if target.suffix.lower() in
             {'.jpg', '.jpeg', '.png', '.webp', '.svg', '.mp4', '.css', '.js'}
             else bad_links).append(f'{p.relative_to(ROOT)} → {url}')
            continue
        if frag and target.suffix == '.html':
            if frag not in ids.get(target, set()):
                bad_anchors.append(f'{p.relative_to(ROOT)} → {url}')

print(f'страниц: {len(pages)}')
for name, lst in (('битых ссылок', bad_links), ('битых ассетов', bad_assets),
                  ('битых якорей', bad_anchors)):
    print(f'{name}: {len(lst)}')
    for x in lst[:15]:
        print('   ', x)
sys.exit(1 if (bad_links or bad_assets or bad_anchors) else 0)
