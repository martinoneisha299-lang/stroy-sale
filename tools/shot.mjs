// Скриншот страницы в headless Chrome. node shot.mjs <порт> <страница> <ширина> <y> [высота]
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import { writeFileSync } from 'node:fs';

const [PORT, PAGE, W = '1280', Y = '0', H = '900'] = process.argv.slice(2);
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=9466',
  '--user-data-dir=/tmp/shot-chrome', '--no-first-run', '--disable-gpu',
  '--hide-scrollbars', 'about:blank'], { stdio: 'ignore' });
await sleep(2500);
const list = await (await fetch('http://localhost:9466/json/list')).json();
const target = list.find(t => t.type === 'page');
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise(r => { ws.onopen = r; });
let id = 0; const pend = new Map();
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
const send = (method, params = {}) => new Promise(res => { const i = ++id; pend.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });

await send('Emulation.setDeviceMetricsOverride', { width: +W, height: +H, deviceScaleFactor: 1, mobile: +W < 700 });
await send('Page.navigate', { url: `http://localhost:${PORT}/${PAGE}` });
await sleep(1800);
if (+Y > 0) { await send('Runtime.evaluate', { expression: `window.scrollTo({top:${Y},behavior:'instant'})` }); await sleep(600); }
const r = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
writeFileSync(process.env.OUT || '/tmp/shot.png', Buffer.from(r.result.data, 'base64'));
console.log('ok');
chrome.kill();
process.exit(0);
