// Аудит пустот: вертикальные зазоры между соседними блоками + недозаполненные
// последние ряды сеток. Запуск: node scan_gaps.mjs <порт> [ширины]
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';

const PORT = process.argv[2] || '8765';
const WIDTHS = (process.argv[3] || '375,1280').split(',').map(Number);
const PAGES = [
  'index.html',
  'kirpich-oblitsovochnyy.html',
  'kirpich-ves.html',
  'collection-palitra.html',
  'kirpich-zabutovochnyy.html',
  'trotuarnaya-plitka.html',
  'plitka-bruschatka.html',
  'tovar/bruschatka-agat-korichnevyy.html',
  'tovar/kirpich-kla-001.html',
  'krovlya.html',
  'krovlya-profnastil.html',
  'krovlya-shtaketnik.html',
  'tovar/krovlya-prof-s8.html',
  'policy.html',
];

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=9455',
  '--user-data-dir=/tmp/gaps-chrome', '--no-first-run', '--disable-gpu',
  '--hide-scrollbars', 'about:blank'], { stdio: 'ignore' });
await sleep(2500);
const list = await (await fetch('http://localhost:9455/json/list')).json();
const target = list.find(t => t.type === 'page');
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise(r => { ws.onopen = r; });
let id = 0; const pend = new Map();
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
const send = (method, params = {}) => new Promise(res => { const i = ++id; pend.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });

const EXPR = (limit) => `(() => {
  const LIM = ${limit};
  const sel = el => el.tagName.toLowerCase() +
    (el.id ? '#' + el.id : '') +
    (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\\s+/).slice(0,2).join('.') : '');
  const vis = el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || cs.position === 'fixed' || cs.position === 'absolute') return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  const gaps = [];
  const walk = el => {
    const kids = [...el.children].filter(vis);
    for (let i = 0; i < kids.length - 1; i++) {
      const a = kids[i].getBoundingClientRect(), b = kids[i+1].getBoundingClientRect();
      const g = Math.round(b.top - a.bottom);
      if (g >= LIM && b.top > a.bottom) gaps.push({ in: sel(el), after: sel(kids[i]), before: sel(kids[i+1]), gap: g });
    }
    kids.forEach(walk);
  };
  walk(document.body);
  // недозаполненные последние ряды сеток
  const halfRows = [];
  document.querySelectorAll('*').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.display !== 'grid') return;
    const cols = cs.gridTemplateColumns.split(' ').filter(Boolean).length;
    const kids = [...el.children].filter(vis);
    if (cols < 2 || kids.length <= cols) return;
    const rest = kids.length % cols;
    if (rest && rest <= cols / 2) halfRows.push({ el: sel(el), cols, items: kids.length, lastRow: rest });
  });
  return JSON.stringify({ gaps: gaps.sort((x,y)=>y.gap-x.gap).slice(0, 8), halfRows: halfRows.slice(0, 6) });
})()`;

for (const w of WIDTHS) {
  const limit = w < 700 ? 34 : 56;
  console.log('\\n=== ширина ' + w + ' (порог ' + limit + 'px) ===');
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: 1200, deviceScaleFactor: 1, mobile: w < 700 });
  for (const p of PAGES) {
    await send('Page.navigate', { url: `http://localhost:${PORT}/${p}` });
    await sleep(800);
    const r = await send('Runtime.evaluate', { expression: EXPR(limit), returnByValue: true });
    const v = JSON.parse(r.result.result.value);
    if (v.gaps.length || v.halfRows.length) {
      console.log('· ' + p);
      v.gaps.forEach(g => console.log('   зазор ' + g.gap + 'px в ' + g.in + ': после ' + g.after + ' → ' + g.before));
      v.halfRows.forEach(h => console.log('   ряд: ' + h.el + ' — ' + h.items + ' шт в ' + h.cols + ' колонок, в последнем ряду ' + h.lastRow));
    }
  }
}
chrome.kill();
process.exit(0);
