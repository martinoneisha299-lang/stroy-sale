// Проверка CSS-токенов. Ловит поломки, которые в этом проекте уже случались:
//   1. var(--чего-нет) — так было с --text-2xs/--text-xs и --text-md/--text-xl:
//      кегль падал в значение по умолчанию и рвал мобильную вёрстку;
//   2. объявление, съеденное сломанным комментарием (двойное */ в tokens.css) —
//      файл выглядит правильным, но в браузере токена НЕ СУЩЕСТВУЕТ,
//      радиусы падали в 0, а дропдауны теряли тень;
//   3. таблица стилей, не доехавшая до страницы (опечатка в ?v=N → 404);
//   4. мёртвые токены — объявлены, но нигде не используются.
//
// Запуск:  node tools/check_tokens.mjs
// Сервер поднимать НЕ нужно: скрипт раздаёт папку сам на свободном порту,
// поэтому «перепутал порт → сканер молча сказал 0 проблем» здесь невозможно.
// Пустой отчёт = всё в порядке. Код возврата 1, если найдены ошибки.
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { createServer } from 'node:http';
import { join, resolve, dirname, extname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const CSS = ['styles.css', 'tokens.css'].filter(f => existsSync(join(ROOT, f)));

// ── 1. разбор CSS ────────────────────────────────────────────────────────────
// Комментарии вырезаются вручную, а не регуляркой: попутно ловим лишний */,
// который закрывает то, что уже закрыто, — с этого места браузер съедает
// следующее объявление целиком.
function stripComments(text) {
  let out = '', stray = [], line = 1, i = 0, state = 'code', quote = '';
  while (i < text.length) {
    const c = text[i], n = text[i + 1];
    if (c === '\n') line++;
    if (state === 'comment') {
      if (c === '*' && n === '/') { state = 'code'; out += '  '; i += 2; continue; }
      out += c === '\n' ? '\n' : ' '; i++; continue;
    }
    if (state === 'str') {
      if (c === '\\') { out += '  '; i += 2; continue; }
      if (c === quote) state = 'code';
      out += c; i++; continue;
    }
    if (c === '/' && n === '*') { state = 'comment'; out += '  '; i += 2; continue; }
    if (c === '*' && n === '/') { stray.push(line); out += '  '; i += 2; continue; }
    if (c === '"' || c === "'") { state = 'str'; quote = c; }
    out += c; i++;
  }
  return { clean: out, stray };
}

// Объявления собираем со стеком фигурных скобок, чтобы знать селектор и то,
// лежит ли объявление внутри @media/@container (такие в покое пустые — это норма).
function collectDecls(clean, file) {
  const decls = [];
  const stack = [];
  let buf = '', line = 1, startLine = 1;
  const take = () => {
    const m = buf.trim().match(/^--([\w-]+)\s*:/);
    if (m) decls.push({
      name: m[1], file, line: startLine,
      sel: stack[stack.length - 1] || '',
      cond: stack.some(s => s.startsWith('@')),
    });
    buf = ''; startLine = line;
  };
  for (let i = 0; i < clean.length; i++) {
    const c = clean[i];
    if (c === '\n') line++;
    if (c === '{') { stack.push(buf.trim().replace(/\s+/g, ' ')); buf = ''; startLine = line; continue; }
    if (c === '}') { take(); stack.pop(); buf = ''; startLine = line; continue; }
    if (c === ';') { take(); continue; }
    if (!buf.trim()) startLine = line;
    buf += c;
  }
  return decls;
}

const decls = [];
const strays = [];
for (const f of CSS) {
  const { clean, stray } = stripComments(readFileSync(join(ROOT, f), 'utf8'));
  decls.push(...collectDecls(clean, f));
  stray.forEach(line => strays.push({ file: f, line }));
}

// ── 2. где токены используются ───────────────────────────────────────────────
const files = [
  ...CSS,
  ...(existsSync(join(ROOT, 'app.js')) ? ['app.js'] : []),
  ...readdirSync(join(ROOT, 'tools')).filter(f => f.endsWith('.py')).map(f => 'tools/' + f),
  ...readdirSync(ROOT).filter(f => f.endsWith('.html')),
  ...(existsSync(join(ROOT, 'tovar'))
    ? readdirSync(join(ROOT, 'tovar')).filter(f => f.endsWith('.html')).map(f => 'tovar/' + f)
    : []),
];

const uses = new Map();               // имя → { files:Set, fallback:boolean }
for (const rel of files) {
  const text = readFileSync(join(ROOT, rel), 'utf8');
  for (const m of text.matchAll(/var\(\s*--([\w-]+)\s*(,?)/g)) {
    const u = uses.get(m[1]) || { files: new Set(), fallback: false };
    u.files.add(rel);
    if (m[2] === ',') u.fallback = true;
    uses.set(m[1], u);
  }
  // токены, заданные из разметки и из JS, тоже считаются объявленными
  if (rel.endsWith('.html')) {
    for (const s of text.matchAll(/style="([^"]*)"/g))
      for (const d of s[1].matchAll(/--([\w-]+)\s*:/g))
        decls.push({ name: d[1], file: rel, line: 0, sel: 'style=""', cond: false, inline: true });
  }
  for (const m of text.matchAll(/setProperty\(\s*['"`]--([\w-]+)/g))
    decls.push({ name: m[1], file: rel, line: 0, sel: 'JS', cond: false, js: true });
}

const declared = new Set(decls.map(d => d.name));
const missing = [...uses.entries()].filter(([n]) => !declared.has(n));
const dead = [...declared].filter(n => !uses.has(n)).sort();

// ── 3. живая проверка в браузере ─────────────────────────────────────────────
// Статический разбор не видит бага со сломанным комментарием: в файле
// объявление есть, а до браузера оно не доезжает. Поэтому спрашиваем сам Chrome.
const MIME = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript',
  '.json': 'application/json', '.svg': 'image/svg+xml', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.mp4': 'video/mp4' };
const server = createServer((req, res) => {
  const path = decodeURIComponent(req.url.split('?')[0]);
  const file = join(ROOT, path === '/' ? 'index.html' : path);
  if (!file.startsWith(ROOT) || !existsSync(file)) { res.writeHead(404).end(); return; }
  res.writeHead(200, { 'content-type': MIME[extname(file)] || 'application/octet-stream' });
  res.end(readFileSync(file));
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const PORT = server.address().port;

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const CDP = 9700 + Math.floor(Math.random() * 200);
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${CDP}`,
  `--user-data-dir=/tmp/tokens-chrome-${CDP}`, '--no-first-run', '--no-default-browser-check',
  '--disable-gpu', '--hide-scrollbars', 'about:blank'], { stdio: 'ignore' });

let wsUrl = null;
for (let i = 0; i < 60 && !wsUrl; i++) {
  await sleep(300);
  try {
    const r = await fetch(`http://127.0.0.1:${CDP}/json/new?about:blank`, { method: 'PUT' });
    wsUrl = (await r.json()).webSocketDebuggerUrl;
  } catch {}
}
if (!wsUrl) { console.error('Chrome не поднялся'); process.exit(1); }
const ws = new WebSocket(wsUrl);
await new Promise(res => ws.addEventListener('open', res));
let msgId = 0;
const pending = new Map();
ws.addEventListener('message', ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
});
const send = (method, params = {}) => new Promise(res => {
  const id = ++msgId; pending.set(id, res);
  ws.send(JSON.stringify({ id, method, params }));
});
await send('Page.enable');
await send('Runtime.enable');
await send('Network.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });

// проверяем три типа страниц — у них разные ?v= у styles.css
const tovar = existsSync(join(ROOT, 'tovar'))
  ? readdirSync(join(ROOT, 'tovar')).filter(f => f.endsWith('.html'))[0] : null;
const PAGES = ['index.html', 'kirpich-oblitsovochnyy.html', tovar && 'tovar/' + tovar]
  .filter(p => p && existsSync(join(ROOT, p)));

// на :root без @-условия — те, что обязаны существовать всегда
const rootNames = [...new Set(decls
  .filter(d => !d.cond && !d.inline && /(^|,)\s*:root\s*(,|$)/.test(d.sel))
  .map(d => d.name))];

const live = [];
for (const page of PAGES) {
  await send('Page.navigate', { url: `http://127.0.0.1:${PORT}/${page}` });
  await sleep(1200);
  const expr = `(() => {
    const cs = getComputedStyle(document.documentElement);
    const empty = ${JSON.stringify(rootNames)}.filter(n => !cs.getPropertyValue('--' + n).trim());
    let rules = 0, sheets = 0;
    for (const s of document.styleSheets) { sheets++; try { rules += s.cssRules.length; } catch {} }
    return JSON.stringify({ empty, rules, sheets });
  })()`;
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  const v = JSON.parse(r.result.result.value);
  live.push({ page, ...v });
}
ws.close(); chrome.kill(); server.close();

// ── 4. отчёт ─────────────────────────────────────────────────────────────────
const err = [];
for (const s of strays) err.push(`СЛОМАН КОММЕНТАРИЙ  ${s.file}:${s.line} — лишний */ ; всё, что объявлено следом, браузер съест`);
for (const [n, u] of missing) err.push(`НЕТ ТОКЕНА  --${n}${u.fallback ? ' (есть запасное значение)' : ''} — используется в: ${[...u.files].slice(0, 3).join(', ')}${u.files.size > 3 ? ` и ещё ${u.files.size - 3}` : ''}`);
for (const l of live) {
  if (l.rules === 0) err.push(`НЕТ СТИЛЕЙ  ${l.page} — таблица стилей не загрузилась (проверьте ?v= у styles.css), подключено ${l.sheets}`);
  for (const n of l.empty) err.push(`ПУСТ В БРАУЗЕРЕ  --${n} на ${l.page} — в файле объявлен, но до браузера не доехал`);
}

console.log(`Токенов объявлено: ${declared.size}, используется: ${uses.size}. Проверено страниц: ${live.length} (правил CSS: ${live.map(l => l.rules).join(', ')}).`);
if (dead.length) console.log(`\nМёртвые (объявлены, нигде не используются), ${dead.length}: ${dead.map(n => '--' + n).join(', ')}`);
if (!err.length) { console.log('\nОшибок нет.'); process.exit(0); }
console.log(`\nОШИБКИ (${err.length}):`);
err.forEach(e => console.log('  ' + e));
process.exit(1);
