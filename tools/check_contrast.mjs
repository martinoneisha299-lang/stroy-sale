// Контраст ВСЕГО видимого текста на странице — по WCAG AA (4.5:1, крупный 3:1).
//
// Цвет берём КАНВАСОМ, а не разбором строки: Chrome отдаёт computed-цвет
// в oklch(), и regex по цифрам врёт (ловили в аудите 24.07). Фон ищем вверх
// по дереву до первого непрозрачного, полупрозрачные слои смешиваем.
//
// Запуск (сервер должен быть поднят):  node tools/check_contrast.mjs 8877
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';

const PORT = process.argv[2] || '8877';
const PAGES = (process.argv[3] || [
  'index.html', 'kirpich-oblitsovochnyy.html', 'zavod-donskoy.html',
  'kirpich-zabutovochnyy.html', 'trotuarnaya-plitka.html', 'plitka-bruschatka.html',
  'krovlya.html', 'krovlya-profnastil.html', 'tovar/kirpich-kla-002.html',
  'tovar/bruschatka-agat-korichnevyy.html', 'tovar/krovlya-prof-s8.html',
  'zayavka.html', 'poisk.html', 'akcii.html', 'dostavka.html', 'raboty.html',
  'policy.html',
].join(',')).split(',');

const CDP = 9400 + Math.floor(Math.random() * 500);
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${CDP}`,
  `--user-data-dir=/tmp/contrast-${CDP}`, '--no-first-run', '--disable-gpu',
  '--hide-scrollbars', 'about:blank'], { stdio: 'ignore' });
await sleep(2500);

const list = await (await fetch(`http://localhost:${CDP}/json/list`)).json();
const target = list.find(t => t.type === 'page');
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise(r => { ws.onopen = r; });
let id = 0; const pend = new Map();
ws.onmessage = e => {
  const m = JSON.parse(e.data);
  if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
};
const send = (method, params = {}) => new Promise(res => {
  const i = ++id; pend.set(i, res);
  ws.send(JSON.stringify({ id: i, method, params }));
});

const PROBE = `(() => {
  const cv = document.createElement('canvas'); cv.width = cv.height = 1;
  const cx = cv.getContext('2d', { willReadFrequently: true });
  const parse = (col) => {
    cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000';
    cx.fillStyle = col; cx.fillRect(0, 0, 1, 1);
    const d = cx.getImageData(0, 0, 1, 1).data;
    return [d[0], d[1], d[2], d[3] / 255];
  };
  const lum = (c) => {
    const f = (v) => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); };
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2]);
  };
  const mix = (fg, bg) => fg.map((v, i) => i < 3 ? v * fg[3] + bg[i] * (1 - fg[3]) : 1);
  const bgOf = (el) => {
    let node = el, acc = null;
    while (node && node.nodeType === 1) {
      const s = getComputedStyle(node);
      const c = parse(s.backgroundColor);
      if (c[3] > 0) { acc = acc ? mix(acc, c) : c; if (acc[3] >= .999) return acc; }
      if (s.backgroundImage && s.backgroundImage !== 'none') return null; // фото — не судим
      node = node.parentElement;
    }
    return acc || [255, 255, 255, 1];
  };
  const out = [];
  document.querySelectorAll('*').forEach((el) => {
    const hasText = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (!hasText) return;
    const s = getComputedStyle(el);
    if (s.visibility === 'hidden' || s.display === 'none' || +s.opacity === 0) return;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) return;
    const bg = bgOf(el);
    if (!bg) return;
    const fg = mix(parse(s.color), bg);
    const L1 = lum(fg), L2 = lum(bg);
    const ratio = (Math.max(L1, L2) + .05) / (Math.min(L1, L2) + .05);
    const px = parseFloat(s.fontSize);
    const bold = +s.fontWeight >= 700;
    const need = (px >= 24 || (px >= 18.66 && bold)) ? 3 : 4.5;
    if (ratio < need - .01) {
      out.push({
        sel: el.tagName.toLowerCase() + (el.className && typeof el.className === 'string'
          ? '.' + el.className.trim().split(/\\s+/).slice(0, 2).join('.') : ''),
        text: (el.textContent || '').trim().slice(0, 40),
        ratio: +ratio.toFixed(2), need,
        fg: 'rgb(' + fg.slice(0, 3).map(Math.round) + ')',
        bg: 'rgb(' + bg.slice(0, 3).map(Math.round) + ')',
        px,
      });
    }
  });
  const seen = new Set();
  return JSON.stringify(out.filter(o => {
    const k = o.sel + o.ratio; if (seen.has(k)) return false; seen.add(k); return true;
  }));
})()`;

await send('Emulation.setDeviceMetricsOverride',
  { width: 1280, height: 1000, deviceScaleFactor: 1, mobile: false });
await send('Network.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });

let total = 0;
for (const page of PAGES) {
  await send('Page.navigate', { url: `http://localhost:${PORT}/${page}` });
  await sleep(1500);
  const r = await send('Runtime.evaluate', { expression: PROBE, returnByValue: true });
  const found = JSON.parse(r.result.result.value || '[]');
  if (found.length) {
    console.log(`\n· ${page}`);
    found.forEach(f => console.log(
      `   ${f.ratio}:1 (нужно ${f.need}) ${f.sel} ${f.px}px  ${f.fg} на ${f.bg}  «${f.text}»`));
    total += found.length;
  }
}
console.log(total ? `\nНАРУШЕНИЙ: ${total}` : 'Контраст: нарушений нет.');
chrome.kill();
process.exit(0);
