#!/usr/bin/env node
// Cheap checks for the skills repo. Run from the repo root: node .github/scripts/validate-skills.mjs
// No dependencies; Node 18+. Exits 1 on any error, so CI fails; warnings never fail.
import { readFileSync, readdirSync, existsSync, statSync } from "node:fs";
import { join, relative, sep } from "node:path";
import { inflateRawSync } from "node:zlib";

const root = process.argv[2] ?? ".";
const errors = [];
const warnings = [];
const err = (where, msg) => errors.push(`${where}: ${msg}`);
const warn = (where, msg) => warnings.push(`${where}: ${msg}`);

const DESC_CAP = 1536; // Claude Code cuts description + when_to_use here in the skill listing
const NAME_RX = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const POINTER_RX = /(?<![\w/\\.-])((?:references|scripts|assets|prompts|templates|examples)\/[\w][\w.\-/]*)/g;
const MDLINK_RX = /\]\((?!https?:|#|mailto:)([^)\s]+?)(?:#[^)]*)?\)/g;

function walk(dir) {
  const out = [];
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    if (["node_modules", "__pycache__", ".git"].includes(e.name)) continue;
    const p = join(dir, e.name);
    if (e.isDirectory()) out.push(...walk(p));
    else out.push(p);
  }
  return out;
}

function frontmatter(text) {
  const m = text.replace(/\r\n/g, "\n").match(/^---\n([\s\S]*?)\n---\n/);
  if (!m) return null;
  const fields = {};
  const lines = m[1].split("\n");
  for (let i = 0; i < lines.length; i++) {
    const km = lines[i].match(/^([A-Za-z_-]+):[ \t]*(.*)$/);
    if (!km) continue;
    let [, key, raw] = km;
    // join folded continuation lines (indented) for block or plain multi-line values
    while (i + 1 < lines.length && /^\s+\S/.test(lines[i + 1]) && !/^\s+-\s/.test(lines[i + 1])) raw += " " + lines[++i].trim();
    fields[key] = raw.trim();
  }
  return fields;
}

function scalar(raw) {
  if (raw == null) return { value: null, style: "missing" };
  if (raw.startsWith('"') && raw.endsWith('"')) return { value: JSON.parse(raw), style: "double" };
  if (raw.startsWith("'") && raw.endsWith("'")) return { value: raw.slice(1, -1).replace(/''/g, "'"), style: "single" };
  if (/^[>|][-+]?$/.test(raw)) return { value: "", style: "block" };
  return { value: raw, style: "plain" };
}

// --- zip reader (central directory only; stored and deflated entries) ---
function readZip(path) {
  const buf = readFileSync(path);
  let eocd = -1;
  for (let i = buf.length - 22; i >= Math.max(0, buf.length - 65557); i--) {
    if (buf.readUInt32LE(i) === 0x06054b50) { eocd = i; break; }
  }
  if (eocd < 0) throw new Error("no end-of-central-directory record");
  const count = buf.readUInt16LE(eocd + 10);
  let p = buf.readUInt32LE(eocd + 16);
  const files = new Map();
  for (let n = 0; n < count; n++) {
    const method = buf.readUInt16LE(p + 10);
    const csize = buf.readUInt32LE(p + 20);
    const nameLen = buf.readUInt16LE(p + 28), extraLen = buf.readUInt16LE(p + 30), commentLen = buf.readUInt16LE(p + 32);
    const local = buf.readUInt32LE(p + 42);
    const name = buf.toString("utf8", p + 46, p + 46 + nameLen).replace(/\\/g, "/");
    p += 46 + nameLen + extraLen + commentLen;
    if (name.endsWith("/")) continue;
    const dataStart = local + 30 + buf.readUInt16LE(local + 26) + buf.readUInt16LE(local + 28);
    const raw = buf.subarray(dataStart, dataStart + csize);
    files.set(name, method === 0 ? raw : method === 8 ? inflateRawSync(raw) : null);
  }
  return files;
}
const norm = (b) => b.toString("utf8").replace(/\r\n/g, "\n");

// --- skills ---
const skillDirs = readdirSync(root, { withFileTypes: true })
  .filter((e) => e.isDirectory() && !e.name.startsWith(".") && existsSync(join(root, e.name, "SKILL.md")))
  .map((e) => e.name)
  .sort();

for (const name of skillDirs) {
  const dir = join(root, name);
  const text = readFileSync(join(dir, "SKILL.md"), "utf8");
  const fm = frontmatter(text);
  if (!fm) { err(name, "SKILL.md has no frontmatter block"); continue; }

  const n = scalar(fm.name);
  if (!n.value) err(name, "frontmatter has no name");
  else {
    if (n.value !== name) err(name, `name "${n.value}" does not match the folder`);
    if (!NAME_RX.test(n.value) || n.value.length > 64) err(name, "name must be lowercase words joined by hyphens, at most 64 characters");
  }

  const d = scalar(fm.description);
  if (!d.value && d.style !== "block") err(name, "frontmatter has no description");
  else {
    if (d.style === "plain" && (/:\s/.test(d.value) || /\s#/.test(d.value)))
      err(name, 'unquoted description contains ": " or " #" (invalid YAML outside Claude Code); wrap it in double quotes');
    const listing = d.value.length + (scalar(fm.when_to_use).value?.length ?? 0);
    if (listing > DESC_CAP) err(name, `description is ${listing} characters; the skill listing cuts it at ${DESC_CAP}`);
  }

  // every pointer and relative markdown link in SKILL.md resolves
  const body = text.replace(/```[\s\S]*?```/g, "");
  const targets = new Set([...body.matchAll(POINTER_RX)].map((m) => m[1].replace(/[.,;:)]+$/, "")));
  for (const m of body.matchAll(MDLINK_RX)) targets.add(m[1]);
  for (const t of targets) {
    if (/[*?<>{}]/.test(t)) continue;
    if (!existsSync(join(dir, t))) err(name, `SKILL.md points at ${t}, which does not exist`);
  }

  // evals
  const evalPath = join(dir, "evals", "evals.json");
  if (!existsSync(evalPath)) err(name, "no evals/evals.json");
  else {
    let ev;
    try { ev = JSON.parse(readFileSync(evalPath, "utf8")); } catch (e) { err(name, `evals.json does not parse: ${e.message}`); }
    if (ev) {
      if (ev.skill_name !== name) err(name, `evals.json skill_name is "${ev.skill_name}"`);
      if (!Array.isArray(ev.evals) || ev.evals.length === 0) err(name, "evals.json has no evals");
      else {
        const ids = new Set();
        for (const [i, c] of ev.evals.entries()) {
          const at = `${name} eval ${c.id ?? i}`;
          if (ids.has(c.id)) err(at, "duplicate id");
          ids.add(c.id);
          if (!c.prompt) err(at, "no prompt");
          if (!c.expected_output && !(c.assertions?.length)) err(at, "no expected_output or assertions");
          for (const f of c.files ?? []) if (!existsSync(join(dir, f))) warn(at, `fixture ${f} is not in the repo, so this eval can't run from a clone`);
        }
        if (ev.evals.length < 3) warn(name, `only ${ev.evals.length} eval(s)`);
      }
    }
  }
}

// --- README lists every skill ---
const readmePath = join(root, "README.md");
if (existsSync(readmePath)) {
  const readme = readFileSync(readmePath, "utf8");
  for (const name of skillDirs) if (!readme.includes(`](${name}/)`)) err("README.md", `no row links ${name}/`);
}

// --- dist zips match their skill folders (evals left out) ---
const distDir = join(root, "dist");
if (existsSync(distDir)) {
  for (const zipName of readdirSync(distDir).filter((f) => f.endsWith(".zip"))) {
    const skill = zipName.replace(/\.zip$/, "");
    const at = `dist/${zipName}`;
    if (!skillDirs.includes(skill)) { err(at, "no skill folder of that name"); continue; }
    let zip;
    try { zip = readZip(join(distDir, zipName)); } catch (e) { err(at, `unreadable: ${e.message}`); continue; }
    const prefix = [...zip.keys()].every((k) => k.startsWith(skill + "/")) ? skill + "/" : "";
    const source = new Map(
      walk(join(root, skill))
        .map((f) => relative(join(root, skill), f).split(sep).join("/"))
        .filter((r) => !r.startsWith("evals/"))
        .map((r) => [r, readFileSync(join(root, skill, r))]),
    );
    for (const [rel, data] of source) {
      const z = zip.get(prefix + rel);
      if (!z) err(at, `missing ${rel}; rebuild the zip`);
      else if (norm(z) !== norm(data)) err(at, `${rel} differs from the source; rebuild the zip`);
    }
    for (const k of zip.keys()) if (!source.has(k.slice(prefix.length))) err(at, `holds ${k}, which the source no longer has`);
  }
}

for (const w of warnings) console.log(`warning  ${w}`);
for (const e of errors) console.log(`error    ${e}`);
console.log(`\n${skillDirs.length} skills checked: ${errors.length} error(s), ${warnings.length} warning(s)`);
process.exit(errors.length ? 1 : 0);
