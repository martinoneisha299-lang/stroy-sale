"""
Каталог: панель управления, фильтры, сортировка, догрузка.

Один код на все разделы (кирпич, плитка, кровля). До редизайна у каждой
страницы была своя копия фильтрующего JS с чуть разным поведением.

Как это устроено
----------------
1. Каждая карточка витрины несёт data-атрибуты групп: data-color, data-texture,
   data-format, data-coll, data-shape, data-task, data-price, data-new.
2. Панель фильтров — ОДНА форма `#filters` в DOM. На узком экране JS ПЕРЕНОСИТ
   её в шторку и возвращает обратно при закрытии. Копии формы намеренно нет:
   две копии = два состояния, которые рано или поздно разъедутся.
3. Состояние живёт в адресе страницы (?color=красный&sort=cheap), поэтому
   ссылку на отфильтрованную выдачу можно отправить в WhatsApp, а «назад»
   в браузере возвращает туда же.
4. Показывается первые N карточек, остальные — по кнопке «Показать ещё».
"""

from shell_common import ICON, esc, plural, terms_line

# Ровно три пункта, как в каталоге референса. «Новинки» отсюда убраны
# 17.08.2026: это не порядок, а признак товара — он переехал в фильтры
# отдельным чекбоксом «Только новинки», где ему и место (и где его можно
# сочетать с цветом и заводом, а не выбирать вместо сортировки).
SORTS = [("default", "По каталогу"), ("cheap", "Сначала дешевле"),
         ("exp", "Сначала дороже"), ("factory", "По заводу (А → Я)")]

NO_PRICE_SORTS = [("default", "По каталогу"), ("factory", "По заводу (А → Я)")]


def toolbar(total, unit=("товар", "товара", "товаров"), sorts=None, filters=True,
            has_prices=True):
    """Строка над выдачей: «Фильтры», сортировка, счётчик найденного.

    has_prices=False убирает «сначала недорогие/дорогие»: на забутовке
    и кровле цены скрыты, и такая сортировка ничего не меняла.
    """
    if sorts is None and not has_prices:
        sorts = NO_PRICE_SORTS
    opts = "".join(
        f'<option value="{k}">{esc(t)}</option>'
        for k, t in (sorts or SORTS))
    fbtn = (f'<button class="tool-btn tool-filters" type="button" aria-controls="filtersDrawer">'
            f'{ICON["filter"]}Фильтры<b id="filtersOn" hidden>0</b></button>') if filters else ""
    sort_html = "" if len(sorts or SORTS) < 2 else (
        f'<span class="sort">{ICON["sort"]}'
        f'<select id="sortSel" aria-label="Сортировка">{opts}</select>{ICON["down"]}</span>')
    return f"""
      <div class="toolbar">
        {fbtn}
        {sort_html}
        <span class="toolbar-count" id="count" aria-live="polite">{total} {plural(total, *unit)}</span>
      </div>
      <div class="applied" id="applied"></div>
      {terms_line()}"""


def fgroup(title, group, opts, dots=None):
    """
    Группа чекбоксов панели фильтров.
    opts — список (значение, подпись, количество) или (значение, подпись).
    dots — {значение: css-цвет или путь к фото} для кружков-образцов.
    """
    rows = []
    for o in opts:
        val, label = o[0], o[1]
        n = o[2] if len(o) > 2 else None
        dot = ""
        if dots and val in dots:
            d = dots[val]
            style = (f"background-image:url({d})" if "/" in str(d) else f"background:{d}")
            dot = f'<span class="fopt-dot" style="{style}"></span>'
        cnt = f'<span class="fopt-n">{n}</span>' if n is not None else ""
        rows.append(
            f'<label class="fopt"><input type="checkbox" data-group="{group}" '
            f'value="{esc(val)}">{dot}<span class="fopt-label">{esc(label)}</span>{cnt}</label>')
    # Заголовок печатаем только если он есть: у группы из одного чекбокса
    # («Только новинки») подпись стоит на самом чекбоксе, а пустой <h3>
    # оставлял дырку в дереве доступности и фантомный отступ.
    head = f"<h3>{esc(title)}</h3>" if title else ""
    return (f'<div class="fgroup">{head}'
            f'<div class="fgroup-list">{"".join(rows)}</div></div>')


def fprice(lo, hi, unit="₽/шт"):
    return (f'<div class="fgroup"><h3>Цена, {esc(unit)}</h3><div class="frange">'
            f'<input type="text" id="pmin" inputmode="decimal" placeholder="от {lo}" aria-label="Цена от">'
            f'<input type="text" id="pmax" inputmode="decimal" placeholder="до {hi}" aria-label="Цена до">'
            f'</div></div>')


def filters_panel(groups_html):
    """Панель целиком: группы + кнопка применения (её видно только в шторке)."""
    return f"""
        <form class="filters" id="filters">
          {groups_html}
          <button class="btn btn--accent btn--wide filters-apply" type="button" data-close
                  id="applyBtn">Показать</button>
          <button class="filters-reset" type="button" data-reset>Сбросить всё</button>
        </form>"""


def filters_drawer():
    """Пустая шторка: форму фильтров JS переносит сюда на узком экране."""
    return f"""
  <div class="drawer" id="filtersDrawer" hidden>
    <div class="drawer-scrim" data-close></div>
    <div class="drawer-panel" role="dialog" aria-modal="true" aria-label="Фильтры">
      <div class="drawer-head">
        <strong>Фильтры</strong>
        <button class="drawer-close" type="button" data-close aria-label="Закрыть">{ICON["close"]}</button>
      </div>
      <div class="drawer-body" id="filtersSlot"></div>
    </div>
  </div>"""


def grid_shell(cards_html, page_size=40, empty_note="По выбранным параметрам товаров не найдено."):
    return f"""
        <div id="catalogWrap" data-page-size="{page_size}">
          <div class="p-grid" id="grid">{cards_html}</div>
          <div class="empty" id="empty" hidden>
            <p>{esc(empty_note)}</p>
            <button class="btn btn--ghost" type="button" data-reset>Сбросить фильтры</button>
          </div>
          <div class="more-row" id="moreRow" hidden>
            <p class="more-shown" id="shownNote"></p>
            <button class="btn btn--soft btn--lg" type="button" id="moreBtn">Показать ещё</button>
          </div>
        </div>"""
