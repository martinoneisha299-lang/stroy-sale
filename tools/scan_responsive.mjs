// Сканер отзывчивости: ширины × масштаб шрифта. Ищет горизонтальный вылет,
// элементы за краем экрана, наезд текста друг на друга и обрезанный текст.
//
// Зачем: на телефонах с увеличенным системным шрифтом (Android «Размер шрифта»,
// iPhone «Размер текста») и с уменьшенным масштабом экрана (iPhone Display Zoom
// отдаёт вьюпорт 320px) вёрстка разъезжается. Скрипт эмулирует эти режимы.
//
// Запуск (сервер должен быть поднят, порт по умолчанию 8765):
//   node tools/scan_responsive.mjs 8765
//   node tools/scan_responsive.mjs 8765 "index.html,krovlya.html"
// Пустой отчёт [] = проблем нет.
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';

const PORT = process.argv[2] || '51455';
const BASE = `http://localhost:${PORT}/`;
const PAGES = process.argv[3] ? process.argv[3].split(',') : [
  'index.html',
  'kirpich-oblitsovochnyy.html',
  'kirpich-ves.html',
  'collection-palitra.html',
  'kirpich-zabutovochnyy.html',
  'trotuarnaya-plitka.html',
  'plitka-staryy-gorod.html',
  'tovar/asgard-agat-kofeynyy.html',
  'tovar/kirpich-eko-001.html',
  'krovlya.html',
  'krovlya-profnastil.html',
  'krovlya-shtaketnik.html',
  'tovar/krovlya-prof-mp20.html',
  'policy.html',
];
const WIDTHS = [280, 320, 360, 375, 390, 412, 430, 600, 768, 820, 1024, 1280, 1440];
const SCALES = [1, 1.25, 1.5, 2];

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PROFILE = '/tmp/scan-chrome-profile';
const chrome = spawn(CHROME, [
  '--headless=new', '--remote-debugging-port=9333', `--user-data-dir=${PROFILE}`,
  '--no-first-run', '--no-default-browser-check', '--disable-gpu', '--hide-scrollbars',
  'about:blank',
], { stdio: 'ignore' });

let wsUrl = null;
for (let i = 0; i < 60 && !wsUrl; i++) {
  await sleep(300);
  try {
    const r = await fetch('http://127.0.0.1:9333/json/new?about:blank', { method: 'PUT' });
    wsUrl = (await r.json()).webSocketDebuggerUrl;
  } catch {}
}
if (!wsUrl) { console.error('chrome не поднялся'); process.exit(1); }

const ws = new WebSocket(wsUrl);
await new Promise(res => ws.addEventListener('open', res));
let msgId = 0;
const pending = new Map();
const waiters = [];
ws.addEventListener('message', ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  if (m.method) for (let i = waiters.length - 1; i >= 0; i--) {
    if (waiters[i].method === m.method) { waiters[i].res(m.params); waiters.splice(i, 1); }
  }
});
const send = (method, params = {}, sessionId) => new Promise(res => {
  const id = ++msgId;
  pending.set(id, res);
  ws.send(JSON.stringify({ id, method, params, sessionId }));
});
const waitEvent = (method, ms = 15000) => new Promise(res => {
  const w = { method, res };
  waiters.push(w);
  setTimeout(() => { const i = waiters.indexOf(w); if (i >= 0) { waiters.splice(i, 1); res(null); } }, ms);
});

const cmd = (m, p) => send(m, p);
await cmd('Page.enable');
await cmd('Runtime.enable');

const PROBE = `(() => {
  const vw = window.innerWidth;
  const out = { overflow: Math.round(document.documentElement.scrollWidth - vw), off: [], overlap: [], clipped: [] };
  const label = el => {
    const id = el.id ? '#' + el.id : '';
    const cls = (el.className && typeof el.className === 'string') ? '.' + el.className.trim().split(/\\s+/).slice(0,2).join('.') : '';
    const t = (el.textContent || '').trim().replace(/\\s+/g, ' ').slice(0, 28);
    return el.tagName.toLowerCase() + id + cls + (t ? ' «' + t + '»' : '');
  };
  // намеренная карусель = предок с overflow-x auto/scroll (html/body не считаем — там clip страницы)
  const scrollable = el => {
    for (let p = el.parentElement; p && p !== document.body && p !== document.documentElement; p = p.parentElement) {
      if (/auto|scroll/.test(getComputedStyle(p).overflowX)) return true;
    }
    return false;
  };
  // задуманные приёмы: бегущая строка преимуществ и декоративное парящее фото
  const decor = el => el.closest('.benefits, .tile-hero-stage, .roof-hero-stage, .marquee') !== null;
  const pinned = el => {
    for (let p = el; p; p = p.parentElement) {
      const pos = getComputedStyle(p).position;
      if (pos === 'fixed' || pos === 'sticky' || pos === 'absolute') return true;
    }
    return false;
  };
  // один проход: собираем стиль+рект, дальше считаем по числам (без layout thrash)
  const items = [];
  for (const el of document.querySelectorAll('body *')) {
    const s = getComputedStyle(el);
    if (s.display === 'none' || s.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    // инлайн-элемент, разорванный на несколько строк, даёт «объединённый» прямоугольник —
    // сравнивать его с соседями бессмысленно
    const multiline = s.display.startsWith('inline') && el.getClientRects().length > 1;
    items.push({ el, s, r, pin: pinned(el), skipOverlap: multiline || decor(el),
      text: [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) });
    if ((r.right > vw + 1 || r.left < -1) && !scrollable(el) && !decor(el)) out.off.push({ el: label(el), left: Math.round(r.left), right: Math.round(r.right) });
    if (/hidden|clip/.test(s.overflowY) || /hidden|clip/.test(s.overflowX)) {
      if (el.scrollHeight > el.clientHeight + 2 && el.clientHeight > 0 && (el.textContent || '').trim() && el.clientHeight < 400)
        out.clipped.push({ el: label(el), need: el.scrollHeight, has: el.clientHeight });
    }
  }
  // наезд: текстовые блоки в обычном потоке перекрываются площадью
  const t = items.filter(i => i.text && i.r.height < 400 && !i.skipOverlap);
  t.sort((a, b) => a.r.top - b.r.top);
  for (let i = 0; i < t.length; i++) {
    for (let j = i + 1; j < t.length && t[j].r.top < t[i].r.bottom; j++) {
      const a = t[i], b = t[j];
      if (a.pin !== b.pin) continue; // фиксированная полоса поверх контента — это норма
      if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
      const ox = Math.min(a.r.right, b.r.right) - Math.max(a.r.left, b.r.left);
      const oy = Math.min(a.r.bottom, b.r.bottom) - Math.max(a.r.top, b.r.top);
      if (ox > 2 && oy > 2) {
        const area = ox * oy, small = Math.min(a.r.width * a.r.height, b.r.width * b.r.height);
        if (area / small > 0.2) out.overlap.push({ a: label(a.el), b: label(b.el), ox: Math.round(ox), oy: Math.round(oy) });
      }
    }
    if (out.overlap.length > 8) break;
  }
  out.off = out.off.slice(0, 12); out.overlap = out.overlap.slice(0, 8); out.clipped = out.clipped.slice(0, 8);
  return JSON.stringify(out);
})()`;

const report = [];
for (const page of PAGES) {
  for (const width of WIDTHS) {
    for (const scale of SCALES) {
      await cmd('Emulation.setDeviceMetricsOverride', {
        width, height: 900, deviceScaleFactor: 1, mobile: width < 900,
      });
      await cmd('Page.navigate', { url: BASE + page });
      await waitEvent('Page.loadEventFired', 12000);
      await cmd('Runtime.evaluate', {
        expression: `document.documentElement.style.fontSize='${(16 * scale).toFixed(1)}px';document.body.offsetHeight;`,
      });
      await sleep(120);
      const r = await cmd('Runtime.evaluate', { expression: PROBE, returnByValue: true });
      let data;
      try { data = JSON.parse(r.result.result.value); } catch { data = { error: JSON.stringify(r).slice(0, 300) }; }
      const bad = data.error || data.overflow > 1 || (data.off || []).length || (data.overlap || []).length || (data.clipped || []).length;
      if (bad) report.push({ page, width, scale, ...data });
    }
  }
  process.stderr.write('.');
}
process.stderr.write('\n');
console.log(JSON.stringify(report, null, 1));
ws.close();
chrome.kill();
process.exit(0);
