#!/usr/bin/env node
// Before-and-after screenshots of real pages, through headless Chrome's
// DevTools protocol. Needs Node 22+ (built-in fetch and WebSocket) and an
// installed Chrome or Edge; no npm packages.
//
//   node shot.mjs --base https://staging.example.com --out shots/before \
//        --width 1440 --theme light / /pricing /signup
//
// For each path it writes <name>-<theme>-<width>-fold.png (the first
// viewport) and <name>-<theme>-<width>-full.png (the whole page).
//
// --width   viewport width in px; under 600 is treated as a phone (390 x 844).
// --theme   a label for the file name. To make the page use it, also pass
//           --cookie name=value and/or --attr data-theme=dark (set on <html>).
// --chrome  path to the browser, when it is not in a usual place.
// --wait    ms to wait after load before the picture (default 3500).
//
// In Git Bash on Windows, export MSYS_NO_PATHCONV=1 first, or "/" and
// "/pricing" are rewritten to C:/Program Files/Git/... before Node sees them.
// Tested on Windows with Chrome; the macOS and Linux paths are the usual
// install locations and have not been run.
import { spawn } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const args = process.argv.slice(2);
const opts = { width: "1440", theme: "light", wait: "3500" };
const paths = [];
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a.startsWith("--")) opts[a.slice(2)] = args[++i];
  else paths.push(a);
}
if (!opts.base || !opts.out || paths.length === 0) {
  console.error(
    "usage: node shot.mjs --base <origin> --out <dir> [--width 1440] [--theme light] [--cookie k=v] [--attr k=v] <path...>",
  );
  process.exit(2);
}

const candidates = [
  opts.chrome,
  process.env.CHROME_PATH,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
  "/usr/bin/chromium-browser",
].filter(Boolean);
const browser = candidates.find((p) => existsSync(p));
if (!browser) {
  console.error("No Chrome or Edge found. Pass --chrome <path>.");
  process.exit(2);
}

mkdirSync(opts.out, { recursive: true });
const width = Number(opts.width);
const phone = width < 600;
const port = 9300 + Math.floor(Math.random() * 600);
const child = spawn(
  browser,
  [
    "--headless=new",
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${mkdtempSync(join(tmpdir(), "ui-craft-shot-"))}`,
    "--hide-scrollbars",
    "--no-first-run",
    "about:blank",
  ],
  { stdio: "ignore" },
);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let target;
for (let i = 0; i < 50 && !target; i++) {
  await sleep(200);
  try {
    const list = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
    target = list.find((t) => t.type === "page");
  } catch {
    // the browser is still starting
  }
}
if (!target) {
  console.error("The browser did not open a DevTools port.");
  child.kill();
  process.exit(1);
}

const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => (ws.onopen = r));
let id = 0;
const pending = new Map();
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) {
    pending.get(m.id)(m.result ?? m);
    pending.delete(m.id);
  }
};
const send = (method, params = {}) =>
  new Promise((r) => {
    pending.set(++id, r);
    ws.send(JSON.stringify({ id, method, params }));
  });

await send("Page.enable");
await send("Network.enable");
if (opts.cookie) {
  const [name, ...rest] = opts.cookie.split("=");
  await send("Network.setCookie", {
    name,
    value: rest.join("="),
    domain: new URL(opts.base).hostname,
    path: "/",
  });
}
await send("Emulation.setDeviceMetricsOverride", {
  width,
  height: phone ? 844 : 900,
  deviceScaleFactor: 1,
  mobile: phone,
});

for (const p of paths) {
  await send("Page.navigate", { url: opts.base + p });
  await sleep(Number(opts.wait));
  // Lazy images below the fold would otherwise be blank in the full picture.
  let script =
    "document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager');";
  if (opts.attr) {
    const [k, ...v] = opts.attr.split("=");
    script += `document.documentElement.setAttribute(${JSON.stringify(k)},${JSON.stringify(v.join("="))});`;
  }
  await send("Runtime.evaluate", { expression: script });
  await sleep(1500);
  const slug =
    p === "/" ? "home" : p.replace(/^\//, "").replace(/[/#?=&]/g, "-");
  const name = `${slug}-${opts.theme}-${width}`;
  const fold = await send("Page.captureScreenshot", { format: "png" });
  writeFileSync(
    join(opts.out, `${name}-fold.png`),
    Buffer.from(fold.data, "base64"),
  );
  const full = await send("Page.captureScreenshot", {
    format: "png",
    captureBeyondViewport: true,
  });
  writeFileSync(
    join(opts.out, `${name}-full.png`),
    Buffer.from(full.data, "base64"),
  );
  console.log(join(opts.out, name));
}
ws.close();
child.kill();
