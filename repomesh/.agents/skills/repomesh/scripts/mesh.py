#!/usr/bin/env python3
"""Dependency-free RepoMesh bootstrap and freshness CLI."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SKILL_ROOT = SCRIPT.parents[1]
PACKAGE_ROOT = SCRIPT.parents[4]
MAP_DIRNAME = ".repo-map"
STATE_FILE = Path("state/sync-state.json")
SECRET_BASENAMES = {
    ".env", ".env.local", ".env.production", ".env.development",
    "id_rsa", "id_ed25519", "credentials.json", "secrets.yaml",
}
SKIP_DIRS = {".git", ".repo-map", "node_modules", ".venv", "venv", "dist", "build", "coverage", ".next"}
CONTEXT_POLICIES = {"required", "relevant", "reference"}


def today() -> str:
    return dt.date.today().isoformat()


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except FileNotFoundError as exc:
        return 127, "", str(exc)


def git(repo: Path, *args: str) -> str:
    code, out, _ = run(["git", "-C", str(repo), *args])
    return out if code == 0 else "unknown"


def git_available(repo: Path) -> bool:
    code, out, _ = run(["git", "-C", str(repo), "rev-parse", "--is-inside-work-tree"])
    return code == 0 and out == "true"


def git_state(repo: Path) -> dict[str, object]:
    status = git(repo, "status", "--porcelain")
    return {
        "branch": git(repo, "branch", "--show-current"),
        "commit": git(repo, "rev-parse", "HEAD"),
        "short_commit": git(repo, "rev-parse", "--short", "HEAD"),
        "remote": git(repo, "remote", "get-url", "origin"),
        "dirty": status not in ("", "unknown"),
    }


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return value.strip("-") or "project"


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def load_json(path: Path, default: object) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def save_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def default_architecture_data(repo: Path, state: dict[str, object] | None = None) -> dict[str, object]:
    state = state or {}
    project_id = slugify(repo.name)
    return {
        "schema_version": 1,
        "status": "scaffold",
        "project": {
            "id": project_id,
            "name": repo.name,
            "source_commit": state.get("commit", "unknown"),
            "generated_at": now_iso(),
        },
        "nodes": [
            {
                "id": "repository",
                "label": repo.name,
                "type": "repository",
                "group": "Repository",
                "description": "Initial scaffold. Replace with source-grounded architecture nodes during MESH >> MAP.",
                "path": ".",
                "status": "unmapped",
            }
        ],
        "edges": [],
        "flows": [
            {
                "id": "mapping-required",
                "name": "Initial architecture mapping",
                "description": "Analyze the repository and replace this scaffold with verified application flows.",
                "steps": [
                    {
                        "order": 1,
                        "nodeId": "repository",
                        "label": "Inspect repository",
                        "detail": "Read high-signal source, manifests, routes, schemas, tests, and deployment files.",
                        "path": ".",
                    }
                ],
            }
        ],
        "metadata": {
            "generator": "RepoMesh",
            "contains_source_code": False,
            "contains_secrets": False,
            "human_view": ".repo-map/generated/architecture.html",
            "agent_view": ".repo-map/generated/architecture.json",
        },
    }


def validate_architecture_data(data: object) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return ["architecture JSON root must be an object"], warnings

    nodes = data.get("nodes")
    edges = data.get("edges")
    flows = data.get("flows")
    if not isinstance(nodes, list):
        errors.append("architecture JSON `nodes` must be an array")
        nodes = []
    if not isinstance(edges, list):
        errors.append("architecture JSON `edges` must be an array")
        edges = []
    if not isinstance(flows, list):
        errors.append("architecture JSON `flows` must be an array")
        flows = []

    node_ids: set[str] = set()
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            errors.append(f"nodes[{index}] must be an object")
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id.strip():
            errors.append(f"nodes[{index}] requires a non-empty string id")
            continue
        if node_id in node_ids:
            errors.append(f"duplicate node id `{node_id}`")
        node_ids.add(node_id)
        if not node.get("label"):
            warnings.append(f"node `{node_id}` has no label")
        if not node.get("path") and not node.get("external"):
            warnings.append(f"node `{node_id}` has no source path or external marker")

    edge_ids: set[str] = set()
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            errors.append(f"edges[{index}] must be an object")
            continue
        edge_id = edge.get("id")
        if not isinstance(edge_id, str) or not edge_id.strip():
            errors.append(f"edges[{index}] requires a non-empty string id")
        elif edge_id in edge_ids:
            errors.append(f"duplicate edge id `{edge_id}`")
        else:
            edge_ids.add(edge_id)
        source = edge.get("source")
        target = edge.get("target")
        if source not in node_ids:
            errors.append(f"edge `{edge_id or index}` references unknown source `{source}`")
        if target not in node_ids:
            errors.append(f"edge `{edge_id or index}` references unknown target `{target}`")
        context_policy = edge.get("context") or edge.get("traversal")
        if context_policy is not None and context_policy not in CONTEXT_POLICIES:
            warnings.append(f"edge `{edge_id or index}` has unknown context policy `{context_policy}`")

    flow_ids: set[str] = set()
    for index, flow in enumerate(flows):
        if not isinstance(flow, dict):
            errors.append(f"flows[{index}] must be an object")
            continue
        flow_id = flow.get("id")
        if not isinstance(flow_id, str) or not flow_id.strip():
            errors.append(f"flows[{index}] requires a non-empty string id")
        elif flow_id in flow_ids:
            errors.append(f"duplicate flow id `{flow_id}`")
        else:
            flow_ids.add(flow_id)
        steps = flow.get("steps")
        if not isinstance(steps, list) or not steps:
            warnings.append(f"flow `{flow_id or index}` has no steps")
            continue
        for step_index, step in enumerate(steps):
            node_id = step if isinstance(step, str) else step.get("nodeId") if isinstance(step, dict) else None
            if node_id not in node_ids:
                errors.append(f"flow `{flow_id or index}` step {step_index + 1} references unknown node `{node_id}`")

    if not nodes:
        warnings.append("architecture graph has no nodes")
    return errors, warnings


ARCHITECTURE_HTML_TEMPLATE = r'''<!doctype html>
<html lang="en" class="dark">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>RepoMesh Architecture</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>tailwind.config = { darkMode: 'class' };</script>
  <style>
    html, body { min-height: 100%; background: #020617; }
    .node-shape { fill: #0f172a; stroke: #475569; stroke-width: 1.5; transition: .18s ease; }
    .node-group:hover .node-shape, .node-group.selected .node-shape { fill: #1e293b; stroke: #38bdf8; stroke-width: 2.5; }
    .node-group.flow-active .node-shape { fill: #172554; stroke: #60a5fa; stroke-width: 3; filter: drop-shadow(0 0 7px rgba(96,165,250,.45)); }
    .edge-path { fill: none; stroke: #334155; stroke-width: 1.7; opacity: .82; transition: .18s ease; }
    .edge-path.flow-active { stroke: #60a5fa; stroke-width: 3.2; opacity: 1; }
    .edge-label { fill: #94a3b8; font-size: 11px; pointer-events: none; }
    .node-label { fill: #f8fafc; font-size: 13px; font-weight: 650; pointer-events: none; }
    .node-type { fill: #94a3b8; font-size: 10px; pointer-events: none; }
    .group-label { fill: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; }
    #graph { min-width: 900px; }
    .glass { background: rgba(15,23,42,.78); backdrop-filter: blur(10px); }
  </style>
</head>
<body class="text-slate-100">
  <header class="border-b border-slate-800 bg-slate-950/90 sticky top-0 z-20">
    <div class="max-w-[1800px] mx-auto px-5 py-4 flex flex-col lg:flex-row lg:items-center gap-4 justify-between">
      <div>
        <div class="text-xs uppercase tracking-[.24em] text-sky-400 font-semibold">RepoMesh</div>
        <h1 id="projectTitle" class="text-2xl font-bold">Architecture Map</h1>
        <p id="projectMeta" class="text-sm text-slate-400 mt-1"></p>
      </div>
      <div class="flex flex-wrap gap-2 items-center">
        <input id="search" class="w-64 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-sky-500" placeholder="Search nodes, paths, descriptions" />
        <select id="flowSelect" class="min-w-64 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-sky-500"></select>
        <button id="reset" class="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm hover:border-sky-500">Reset</button>
      </div>
    </div>
  </header>

  <main class="max-w-[1800px] mx-auto p-5 space-y-5">
    <section class="grid grid-cols-2 md:grid-cols-4 gap-3" id="stats"></section>
    <section class="grid xl:grid-cols-[minmax(0,1fr)_380px] gap-5">
      <div class="rounded-2xl border border-slate-800 bg-slate-950 overflow-auto min-h-[720px]">
        <svg id="graph" role="img" aria-label="Interactive application architecture diagram"></svg>
      </div>
      <aside class="space-y-5">
        <section class="glass rounded-2xl border border-slate-800 p-5">
          <div class="text-xs uppercase tracking-widest text-slate-500 font-semibold">Selected component</div>
          <div id="nodeDetails" class="mt-3 text-sm text-slate-300">Select a node to inspect its purpose and source path.</div>
        </section>
        <section class="glass rounded-2xl border border-slate-800 p-5">
          <div class="text-xs uppercase tracking-widest text-slate-500 font-semibold">Interactive flow</div>
          <div id="flowDetails" class="mt-3 text-sm text-slate-300">Select a flow to highlight its complete path.</div>
        </section>
        <section class="glass rounded-2xl border border-slate-800 p-5">
          <div class="text-xs uppercase tracking-widest text-slate-500 font-semibold">Legend</div>
          <div id="legend" class="mt-3 flex flex-wrap gap-2"></div>
        </section>
      </aside>
    </section>
  </main>

  <script id="architecture-data" type="application/json">__ARCHITECTURE_DATA__</script>
  <script>
    const data = JSON.parse(document.getElementById('architecture-data').textContent);
    const nodes = Array.isArray(data.nodes) ? data.nodes : [];
    const edges = Array.isArray(data.edges) ? data.edges : [];
    const flows = Array.isArray(data.flows) ? data.flows : [];
    const nodeById = new Map(nodes.map(n => [n.id, n]));
    const graph = document.getElementById('graph');
    const NS = 'http://www.w3.org/2000/svg';
    let selectedNodeId = null;
    let selectedFlowId = null;
    let searchTerm = '';

    const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
    const project = data.project || {};
    document.getElementById('projectTitle').textContent = project.name || 'Architecture Map';
    document.getElementById('projectMeta').textContent = [project.id, project.source_commit ? `commit ${String(project.source_commit).slice(0, 12)}` : '', data.status].filter(Boolean).join(' · ');

    function statCard(label, value) {
      return `<div class="rounded-xl border border-slate-800 bg-slate-950 p-4"><div class="text-xs uppercase tracking-wider text-slate-500">${esc(label)}</div><div class="text-2xl font-bold mt-1">${esc(value)}</div></div>`;
    }
    const groups = [...new Set(nodes.map(n => n.group || n.type || 'Other'))];
    document.getElementById('stats').innerHTML = [statCard('Components', nodes.length), statCard('Relationships', edges.length), statCard('Flows', flows.length), statCard('Groups', groups.length)].join('');

    const flowSelect = document.getElementById('flowSelect');
    flowSelect.innerHTML = `<option value="">Select a flow…</option>` + flows.map(f => `<option value="${esc(f.id)}">${esc(f.name || f.id)}</option>`).join('');
    flowSelect.addEventListener('change', event => { selectedFlowId = event.target.value || null; render(); });
    document.getElementById('reset').addEventListener('click', () => { selectedNodeId = null; selectedFlowId = null; searchTerm = ''; flowSelect.value = ''; document.getElementById('search').value = ''; render(); });
    document.getElementById('search').addEventListener('input', event => { searchTerm = event.target.value.toLowerCase().trim(); render(); });

    const typeClasses = ['bg-sky-950 text-sky-300 border-sky-800','bg-indigo-950 text-indigo-300 border-indigo-800','bg-emerald-950 text-emerald-300 border-emerald-800','bg-amber-950 text-amber-300 border-amber-800','bg-rose-950 text-rose-300 border-rose-800','bg-violet-950 text-violet-300 border-violet-800'];
    function typeClass(type) {
      let hash = 0;
      for (const ch of String(type || 'other')) hash = ((hash << 5) - hash + ch.charCodeAt(0)) | 0;
      return typeClasses[Math.abs(hash) % typeClasses.length];
    }
    document.getElementById('legend').innerHTML = [...new Set(nodes.map(n => n.type || 'component'))].map(type => `<span class="rounded-full border px-2.5 py-1 text-xs ${typeClass(type)}">${esc(type)}</span>`).join('');

    function flowNodeIds(flow) {
      return (flow?.steps || []).map(s => typeof s === 'string' ? s : s.nodeId).filter(Boolean);
    }
    function flowEdgeIds(flow) {
      const explicit = new Set(flow?.edgeIds || []);
      const ids = flowNodeIds(flow);
      for (let i = 0; i < ids.length - 1; i++) {
        const match = edges.find(e => e.source === ids[i] && e.target === ids[i + 1]);
        if (match) explicit.add(match.id);
      }
      return explicit;
    }

    function layout() {
      const grouped = new Map();
      for (const node of nodes) {
        const group = node.group || node.type || 'Other';
        if (!grouped.has(group)) grouped.set(group, []);
        grouped.get(group).push(node);
      }
      const orderedGroups = [...grouped.keys()];
      const positions = new Map();
      const colWidth = 270, rowHeight = 120, top = 90, left = 70;
      let maxRows = 1;
      orderedGroups.forEach((group, col) => {
        const list = grouped.get(group);
        maxRows = Math.max(maxRows, list.length);
        list.forEach((node, row) => positions.set(node.id, { x: left + col * colWidth, y: top + row * rowHeight, group, col, row }));
      });
      return { positions, orderedGroups, width: Math.max(980, left * 2 + Math.max(1, orderedGroups.length) * colWidth), height: Math.max(720, top + maxRows * rowHeight + 80) };
    }

    function svgEl(name, attrs = {}) {
      const el = document.createElementNS(NS, name);
      Object.entries(attrs).forEach(([key, value]) => el.setAttribute(key, value));
      return el;
    }

    function renderNodeDetails(node) {
      const panel = document.getElementById('nodeDetails');
      if (!node) { panel.innerHTML = 'Select a node to inspect its purpose and source path.'; return; }
      panel.innerHTML = `<div class="flex items-center justify-between gap-3"><h2 class="text-lg font-semibold text-white">${esc(node.label || node.id)}</h2><span class="rounded-full border px-2 py-0.5 text-xs ${typeClass(node.type)}">${esc(node.type || 'component')}</span></div>
        <p class="mt-3 leading-6">${esc(node.description || 'No description supplied.')}</p>
        ${node.path ? `<div class="mt-3 rounded-lg bg-slate-950 border border-slate-800 p-3 font-mono text-xs text-sky-300 break-all">${esc(node.path)}</div>` : ''}
        <dl class="mt-4 grid grid-cols-[100px_1fr] gap-y-2 text-xs"><dt class="text-slate-500">ID</dt><dd>${esc(node.id)}</dd><dt class="text-slate-500">Group</dt><dd>${esc(node.group || 'Other')}</dd><dt class="text-slate-500">Status</dt><dd>${esc(node.status || 'unknown')}</dd></dl>`;
    }

    function renderFlowDetails(flow) {
      const panel = document.getElementById('flowDetails');
      if (!flow) { panel.innerHTML = 'Select a flow to highlight its complete path.'; return; }
      const steps = (flow.steps || []).map((step, index) => {
        const value = typeof step === 'string' ? { nodeId: step } : step;
        const node = nodeById.get(value.nodeId) || {};
        return `<li class="relative pl-9 pb-5 last:pb-0"><span class="absolute left-0 top-0 h-6 w-6 rounded-full bg-sky-500 text-slate-950 text-xs font-bold flex items-center justify-center">${esc(value.order || index + 1)}</span><div class="font-semibold text-white">${esc(value.label || node.label || value.nodeId)}</div><div class="text-xs leading-5 mt-1 text-slate-400">${esc(value.detail || node.description || '')}</div>${value.path || node.path ? `<div class="font-mono text-[11px] text-sky-300 mt-1 break-all">${esc(value.path || node.path)}</div>` : ''}</li>`;
      }).join('');
      panel.innerHTML = `<h2 class="text-lg font-semibold text-white">${esc(flow.name || flow.id)}</h2><p class="mt-2 leading-6">${esc(flow.description || '')}</p><ol class="mt-5">${steps}</ol>`;
    }

    function render() {
      graph.innerHTML = '';
      const { positions, orderedGroups, width, height } = layout();
      graph.setAttribute('viewBox', `0 0 ${width} ${height}`);
      graph.setAttribute('width', width);
      graph.setAttribute('height', height);

      const defs = svgEl('defs');
      const marker = svgEl('marker', { id: 'arrow', markerWidth: '10', markerHeight: '10', refX: '9', refY: '3', orient: 'auto', markerUnits: 'strokeWidth' });
      marker.appendChild(svgEl('path', { d: 'M0,0 L0,6 L9,3 z', fill: '#475569' }));
      defs.appendChild(marker);
      const activeMarker = svgEl('marker', { id: 'arrow-active', markerWidth: '10', markerHeight: '10', refX: '9', refY: '3', orient: 'auto', markerUnits: 'strokeWidth' });
      activeMarker.appendChild(svgEl('path', { d: 'M0,0 L0,6 L9,3 z', fill: '#60a5fa' }));
      defs.appendChild(activeMarker);
      graph.appendChild(defs);

      orderedGroups.forEach((group, col) => {
        const label = svgEl('text', { x: 70 + col * 270, y: 38, class: 'group-label' });
        label.textContent = group;
        graph.appendChild(label);
        graph.appendChild(svgEl('line', { x1: 70 + col * 270, y1: 50, x2: 270 + col * 270, y2: 50, stroke: '#1e293b', 'stroke-width': '2' }));
      });

      const activeFlow = flows.find(f => f.id === selectedFlowId);
      const activeNodes = new Set(flowNodeIds(activeFlow));
      const activeEdges = flowEdgeIds(activeFlow);

      for (const edge of edges) {
        const source = positions.get(edge.source), target = positions.get(edge.target);
        if (!source || !target) continue;
        const x1 = source.x + 190, y1 = source.y + 34, x2 = target.x, y2 = target.y + 34;
        const bend = Math.max(70, Math.abs(x2 - x1) * .45);
        const path = svgEl('path', { id: `edge-${edge.id}`, d: `M ${x1} ${y1} C ${x1 + bend} ${y1}, ${x2 - bend} ${y2}, ${x2} ${y2}`, class: `edge-path${activeEdges.has(edge.id) ? ' flow-active' : ''}`, 'marker-end': activeEdges.has(edge.id) ? 'url(#arrow-active)' : 'url(#arrow)' });
        graph.appendChild(path);
        if (edge.label) {
          const label = svgEl('text', { x: (x1 + x2) / 2, y: (y1 + y2) / 2 - 7, class: 'edge-label', 'text-anchor': 'middle' });
          label.textContent = edge.label;
          graph.appendChild(label);
        }
      }

      for (const node of nodes) {
        const pos = positions.get(node.id);
        const searchable = [node.id, node.label, node.type, node.group, node.description, node.path].filter(Boolean).join(' ').toLowerCase();
        const matches = !searchTerm || searchable.includes(searchTerm);
        const classes = ['node-group'];
        if (node.id === selectedNodeId) classes.push('selected');
        if (activeNodes.has(node.id)) classes.push('flow-active');
        const group = svgEl('g', { class: classes.join(' '), transform: `translate(${pos.x},${pos.y})`, role: 'button', tabindex: '0', opacity: matches ? '1' : '.18' });
        group.appendChild(svgEl('rect', { width: '190', height: '68', rx: '12', class: 'node-shape' }));
        const label = svgEl('text', { x: '14', y: '28', class: 'node-label' });
        label.textContent = String(node.label || node.id).slice(0, 25);
        group.appendChild(label);
        const type = svgEl('text', { x: '14', y: '49', class: 'node-type' });
        type.textContent = String(node.type || 'component');
        group.appendChild(type);
        group.addEventListener('click', () => { selectedNodeId = node.id; renderNodeDetails(node); document.querySelectorAll('.node-group.selected').forEach(el => el.classList.remove('selected')); group.classList.add('selected'); });
        group.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') group.dispatchEvent(new Event('click')); });
        graph.appendChild(group);
      }
      renderNodeDetails(selectedNodeId ? nodeById.get(selectedNodeId) : null);
      renderFlowDetails(activeFlow);
    }

    render();
  </script>
</body>
</html>
'''


def render_architecture_html(data: dict[str, object], output: Path) -> None:
    embedded = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(ARCHITECTURE_HTML_TEMPLATE.replace("__ARCHITECTURE_DATA__", embedded), encoding="utf-8")


def write_architecture_outputs(repo: Path, force_scaffold: bool = False) -> tuple[Path, Path]:
    map_dir = repo / MAP_DIRNAME
    json_path = map_dir / "generated" / "architecture.json"
    html_path = map_dir / "generated" / "architecture.html"
    if force_scaffold or not json_path.exists():
        state = git_state(repo) if git_available(repo) else {"commit": "unknown"}
        save_json(json_path, default_architecture_data(repo, state))
    data = load_json(json_path, {})
    errors, warnings = validate_architecture_data(data)
    if errors:
        raise ValueError("; ".join(errors))
    assert isinstance(data, dict)
    render_architecture_html(data, html_path)
    for warning in warnings:
        print(f"WARN: {warning}")
    return json_path, html_path


def aggregate_mesh(mesh: Path) -> tuple[Path, Path]:
    nodes: list[dict[str, object]] = []
    edges: list[dict[str, object]] = []
    flows: list[dict[str, object]] = []
    projects: list[dict[str, object]] = []

    for source in sorted((mesh / "imports").glob("*.architecture.json")):
        data = load_json(source, {})
        if not isinstance(data, dict):
            continue
        project = data.get("project") if isinstance(data.get("project"), dict) else {}
        project_id = slugify(str(project.get("id") or source.name.removesuffix(".architecture.json")))
        project_name = str(project.get("name") or project_id)
        projects.append({"id": project_id, "name": project_name, "source_commit": project.get("source_commit", "unknown")})
        source_nodes = data.get("nodes") if isinstance(data.get("nodes"), list) else []
        source_edges = data.get("edges") if isinstance(data.get("edges"), list) else []
        source_flows = data.get("flows") if isinstance(data.get("flows"), list) else []
        for node in source_nodes:
            if not isinstance(node, dict) or not node.get("id"):
                continue
            copied = dict(node)
            copied["id"] = f"{project_id}::{node['id']}"
            copied["label"] = f"{project_name}: {node.get('label', node['id'])}"
            copied["group"] = f"{project_name} / {node.get('group', node.get('type', 'Other'))}"
            copied["projectId"] = project_id
            nodes.append(copied)
        for edge in source_edges:
            if not isinstance(edge, dict) or not edge.get("source") or not edge.get("target"):
                continue
            copied = dict(edge)
            copied["id"] = f"{project_id}::{edge.get('id', len(edges))}"
            copied["source"] = f"{project_id}::{edge['source']}"
            copied["target"] = f"{project_id}::{edge['target']}"
            copied["projectId"] = project_id
            edges.append(copied)
        for flow in source_flows:
            if not isinstance(flow, dict):
                continue
            copied = dict(flow)
            copied["id"] = f"{project_id}::{flow.get('id', len(flows))}"
            copied["name"] = f"{project_name}: {flow.get('name', flow.get('id', 'Flow'))}"
            copied_steps: list[object] = []
            for step in flow.get("steps", []):
                if isinstance(step, str):
                    copied_steps.append(f"{project_id}::{step}")
                elif isinstance(step, dict):
                    step_copy = dict(step)
                    if step_copy.get("nodeId"):
                        step_copy["nodeId"] = f"{project_id}::{step_copy['nodeId']}"
                    copied_steps.append(step_copy)
            copied["steps"] = copied_steps
            copied["edgeIds"] = [f"{project_id}::{edge_id}" for edge_id in flow.get("edgeIds", [])]
            copied["projectId"] = project_id
            flows.append(copied)

    cross_path = mesh / "graph" / "cross-repo.json"
    cross = load_json(cross_path, {})
    if isinstance(cross, dict):
        for key, target in (("nodes", nodes), ("edges", edges), ("flows", flows)):
            values = cross.get(key)
            if isinstance(values, list):
                target.extend(item for item in values if isinstance(item, dict))

    data: dict[str, object] = {
        "schema_version": 1,
        "status": "compiled-mesh",
        "project": {"id": "repo-mesh", "name": "RepoMesh Cross-Repository Graph", "source_commit": git(mesh, "rev-parse", "HEAD"), "generated_at": now_iso()},
        "projects": projects,
        "nodes": nodes,
        "edges": edges,
        "flows": flows,
        "metadata": {"generator": "RepoMesh", "contains_source_code": False, "contains_secrets": False},
    }
    json_path = mesh / "graph" / "architecture.json"
    html_path = mesh / "graph" / "architecture.html"
    save_json(json_path, data)
    render_architecture_html(data, html_path)
    return json_path, html_path

def ensure_skill(target_repo: Path) -> None:
    target = target_repo / ".agents" / "skills" / "repomesh"
    if target.resolve() == SKILL_ROOT.resolve():
        return
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SKILL_ROOT, target)
        print(f"Installed skill at {target.relative_to(target_repo)}")
        return

    # Non-destructive refresh: add files that do not exist; never replace local edits.
    for source in SKILL_ROOT.rglob("*"):
        if not source.is_file() or "__pycache__" in source.parts:
            continue
        relative = source.relative_to(SKILL_ROOT)
        destination = target / relative
        if not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            print(f"Added missing skill file {destination.relative_to(target_repo)}")


def repo_manifest(repo: Path, state: dict[str, object]) -> str:
    name = repo.name
    slug = slugify(name)
    remote = state.get("remote") or "unknown"
    branch = state.get("branch") or "unknown"
    return f"""schema_version: 1
project:
  id: {slug}
  name: {name}
  type: unknown
repository:
  root: ..
  remote: {remote}
  default_branch: {branch}
ownership:
  team: unknown
mesh:
  enabled: auto
  failure_policy: continue-local
  path: null
  discovery:
    environment_variable: REPO_MESH_PATH
    sibling_directories:
      - ../repo-mesh
      - ../engineering-mesh
context:
  strategy: adaptive-graph-closure
  hard_token_cap: null
  token_warning_threshold: 32000
  traversal:
    directions:
      - upstream
      - downstream
    include_complete_flows: true
    include_required_edges: true
    include_relevant_edges: true
    include_reference_edges: on-demand
    stop_when: no-new-material-relationships
privacy:
  export:
    source_code: false
    secrets: false
    private_notes: false
    architecture: true
    interfaces: true
    dependencies: true
    decisions: reviewed-only
"""


def local_page(title: str, body: str) -> str:
    return f"""---
title: {title}
type: repository-map
status: draft
ownership: hybrid
source_commit: unknown
last_verified: {today()}
confidence: low
sources: []
---

# {title}

<!-- REPOMESH:GENERATED:START generated -->
{body}
<!-- REPOMESH:GENERATED:END generated -->

## Maintainer Notes

<!-- REPOMESH:HUMAN:START -->
<!-- Add durable human-maintained context here. -->
<!-- REPOMESH:HUMAN:END -->
"""


def init_repo(args: argparse.Namespace) -> int:
    repo = Path(args.path or ".").expanduser().resolve()
    if not repo.is_dir():
        print(f"error: repository path does not exist: {repo}", file=sys.stderr)
        return 2

    ensure_skill(repo)
    map_dir = repo / MAP_DIRNAME
    for directory in ("decisions", "modules", "workflows", "generated", "state"):
        (map_dir / directory).mkdir(parents=True, exist_ok=True)

    state = git_state(repo) if git_available(repo) else {
        "branch": "unknown", "commit": "unknown", "short_commit": "unknown", "remote": "unknown", "dirty": False
    }

    created: list[str] = []
    files = {
        map_dir / "manifest.yaml": repo_manifest(repo, state),
        map_dir / "index.md": "# Repo Map Index\n\n_Local navigation for this repository. Update generated links as the map grows._\n",
        map_dir / "hot.md": local_page("Recent Project Context", "_No session context has been compiled yet._"),
        map_dir / "architecture.md": local_page("Architecture", "_To be compiled from repository evidence._"),
        map_dir / "interfaces.md": local_page("Interfaces", "_To be compiled from repository evidence._"),
        map_dir / "dependencies.md": local_page("Dependencies", "_To be compiled from repository evidence._"),
        map_dir / "ownership.md": local_page("Ownership", "_To be compiled from repository evidence._"),
        map_dir / "generated" / "session-brief.md": "# Session Brief\n\n_Run `mesh.py start` to refresh._\n",
        map_dir / "generated" / "context-plan.json": json.dumps({
            "schema_version": 1,
            "strategy": "adaptive-graph-closure",
            "hard_token_cap": None,
            "nodes": [], "edges": [], "flows": [], "source_paths": [],
            "stopping_condition": "no-new-material-relationships",
        }, indent=2) + "\n",
    }
    for path, content in files.items():
        if write_if_missing(path, content):
            created.append(str(path.relative_to(repo)))

    sync_path = map_dir / STATE_FILE
    if not sync_path.exists():
        save_json(sync_path, {
            "schema_version": 1,
            "last_mapped_commit": state["commit"],
            "last_mapped_at": now_iso(),
            "last_seen_branch": state["branch"],
            "mesh_path": None,
        })
        created.append(str(sync_path.relative_to(repo)))

    architecture_json = map_dir / "generated" / "architecture.json"
    architecture_html = map_dir / "generated" / "architecture.html"
    json_existed = architecture_json.exists()
    html_existed = architecture_html.exists()
    write_architecture_outputs(repo)
    if not json_existed:
        created.append(str(architecture_json.relative_to(repo)))
    if not html_existed:
        created.append(str(architecture_html.relative_to(repo)))

    print(f"Repo Map ready: {map_dir}")
    if created:
        print("Created:")
        for item in created:
            print(f"- {item}")
    else:
        print("No existing map files were replaced.")
    print("Next: ask the agent to inspect the repository using the RepoMesh SKILL.md mapping protocol.")
    return 0


def init_mesh(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    for directory in (
        "registry", "imports", "graph/projects", "graph/services", "graph/interfaces",
        "graph/data-models", "graph/integrations", "contracts", "decisions", "patterns",
        "conflicts", "audits", "state",
    ):
        (path / directory).mkdir(parents=True, exist_ok=True)

    write_if_missing(path / "README.md", "# RepoMesh Repository\n\nOptional cross-repository graph compiled from safe Repo Map exports.\n")
    write_if_missing(path / "AGENTS.md", "# RepoMesh Instructions\n\nPreserve provenance, visibility, contradictions, and inaccessible nodes. Never require this repository for local source-repo development.\n")
    write_if_missing(path / "registry" / "README.md", "# Registry\n\nOne project registration record per connected repository.\n")
    write_if_missing(path / "imports" / "README.md", "# Imports\n\nNormalized safe exports from connected Repo Maps.\n")
    write_if_missing(path / "graph" / "index.md", "# Mesh Graph Index\n")
    if not (path / "graph" / "cross-repo.json").exists():
        save_json(path / "graph" / "cross-repo.json", {"schema_version": 1, "nodes": [], "edges": [], "flows": []})
    write_if_missing(path / ".gitignore", "__pycache__/\n*.tmp\n.DS_Store\nThumbs.db\n")
    aggregate_mesh(path)

    if not git_available(path):
        code, _, err = run(["git", "init"], cwd=path)
        if code != 0:
            print(f"WARN: could not initialize Git: {err}")
        else:
            print(f"Initialized Git repository at {path}")
    else:
        print(f"Using existing Git repository at {path}")
    print("No commit or push was performed.")
    return 0


def resolve_repo_root() -> Path:
    cwd = Path.cwd().resolve()
    root = git(cwd, "rev-parse", "--show-toplevel")
    return Path(root).resolve() if root != "unknown" else cwd


def connect(args: argparse.Namespace) -> int:
    repo = resolve_repo_root()
    map_dir = repo / MAP_DIRNAME
    if not map_dir.exists():
        print("error: no .repo-map found; run the repo command first", file=sys.stderr)
        return 2
    mesh = Path(args.path).expanduser().resolve()
    if not mesh.exists():
        print(f"WARN: Mesh path does not exist: {mesh}")
        print("Local Repo Map remains active; connection was not changed.")
        return 0

    state_path = map_dir / STATE_FILE
    state = load_json(state_path, {})
    assert isinstance(state, dict)
    state["mesh_path"] = str(mesh)
    state["mesh_connected_at"] = now_iso()
    save_json(state_path, state)

    project_id = slugify(repo.name)
    registry = mesh / "registry" / f"{project_id}.json"
    registry.parent.mkdir(parents=True, exist_ok=True)
    existing = load_json(registry, {})
    if not isinstance(existing, dict):
        existing = {}
    existing.update({
        "schema_version": 1,
        "project_id": project_id,
        "repo_path": str(repo),
        "remote": git_state(repo)["remote"],
        "connected_at": existing.get("connected_at", now_iso()),
        "last_seen_at": now_iso(),
        "status": "connected",
    })
    save_json(registry, existing)
    print(f"Connected {project_id} to Mesh at {mesh}")
    return 0


def parse_name_status(text: str) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        if status.startswith("R") and len(parts) >= 3:
            result.append({"status": "R", "old_path": parts[1], "path": parts[2]})
        elif len(parts) >= 2:
            result.append({"status": status[:1], "path": parts[1]})
    return result


def impacts_for(path: str) -> list[str]:
    lower = path.lower()
    impacts: set[str] = set()
    if any(x in lower for x in ("package.json", "pyproject.toml", "requirements", "cargo.toml", "go.mod", "pom.xml", "build.gradle")):
        impacts.update(("dependencies", "commands", "runtime"))
    if any(x in lower for x in ("route", "controller", "handler", "api/", "openapi", "swagger")):
        impacts.update(("interfaces", "workflows"))
    if any(x in lower for x in ("schema", "model", "migration", "prisma", "entity")):
        impacts.update(("data-models", "interfaces"))
    if any(x in lower for x in ("docker", "compose", "k8s", "kubernetes", "terraform", "helm", "deploy")):
        impacts.update(("deployment", "services"))
    if any(x in lower for x in ("test", "spec", "__tests__")):
        impacts.add("verification")
    if any(x in lower for x in (".github/workflows", "gitlab-ci", "jenkins")):
        impacts.update(("ci-cd", "commands"))
    if any(x in lower for x in ("readme", "agents.md", "claude.md", "docs/", "adr")):
        impacts.update(("documentation", "decisions"))
    if any(x in lower for x in (".env.example", "example.env", "config")):
        impacts.add("configuration")
    return sorted(impacts or {"module-map"})



CONTEXT_STOPWORDS = {
    "the", "and", "for", "with", "from", "into", "this", "that", "add", "change",
    "update", "fix", "create", "current", "task", "feature", "work", "repo", "repository",
}


def context_terms(value: object) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, (list, tuple, set)):
        combined = " ".join(str(item) for item in value)
    else:
        combined = str(value)
    return {
        token for token in re.findall(r"[a-zA-Z0-9_-]+", combined.lower())
        if len(token) >= 3 and token not in CONTEXT_STOPWORDS
    }


def node_paths(node: dict[str, object]) -> list[str]:
    paths: list[str] = []
    path = node.get("path")
    if isinstance(path, str) and path:
        paths.append(path)
    sources = node.get("sources")
    if isinstance(sources, list):
        for source in sources:
            if isinstance(source, str) and source:
                paths.append(source)
            elif isinstance(source, dict) and isinstance(source.get("path"), str):
                paths.append(str(source["path"]))
    return paths


def paths_related(left: str, right: str) -> bool:
    left = left.replace("\\", "/").strip("./")
    right = right.replace("\\", "/").strip("./")
    if not left or not right:
        return False
    if left == right or left.startswith(right + "/") or right.startswith(left + "/"):
        return True
    left_parent = left.rsplit("/", 1)[0] if "/" in left else ""
    right_parent = right.rsplit("/", 1)[0] if "/" in right else ""
    return bool(left_parent and left_parent == right_parent)


def build_context_plan(
    architecture_data: object,
    changes: list[dict[str, str]],
    task: str = "",
    deep: bool = False,
) -> dict[str, object]:
    """Build a deterministic, bidirectional task context closure without a token cutoff."""
    if not isinstance(architecture_data, dict):
        architecture_data = {}
    raw_nodes = architecture_data.get("nodes", [])
    raw_edges = architecture_data.get("edges", [])
    raw_flows = architecture_data.get("flows", [])
    nodes = [node for node in raw_nodes if isinstance(node, dict) and isinstance(node.get("id"), str)] if isinstance(raw_nodes, list) else []
    edges = [edge for edge in raw_edges if isinstance(edge, dict)] if isinstance(raw_edges, list) else []
    flows = [flow for flow in raw_flows if isinstance(flow, dict)] if isinstance(raw_flows, list) else []
    node_by_id = {str(node["id"]): node for node in nodes}
    changed_paths = sorted({item.get("path", "") for item in changes if item.get("path")})
    task_tokens = context_terms(task)

    selected: set[str] = set()
    reasons: dict[str, set[str]] = {}

    def select(node_id: str, reason: str) -> bool:
        if node_id not in node_by_id:
            return False
        was_new = node_id not in selected
        selected.add(node_id)
        reasons.setdefault(node_id, set()).add(reason)
        return was_new

    for node_id, node in node_by_id.items():
        for source_path in node_paths(node):
            if any(paths_related(source_path, changed_path) for changed_path in changed_paths):
                select(node_id, "changed-source")
                break
        searchable = " ".join(str(node.get(key, "")) for key in ("id", "label", "description", "type", "group"))
        searchable += " " + " ".join(node_paths(node))
        tags = node.get("tags", [])
        concerns = node.get("concerns", [])
        if isinstance(tags, list):
            searchable += " " + " ".join(str(item) for item in tags)
        if isinstance(concerns, list):
            searchable += " " + " ".join(str(item) for item in concerns)
        overlap = task_tokens & context_terms(searchable)
        if overlap:
            select(node_id, "task:" + ",".join(sorted(overlap)))

    if not selected and "repository" in node_by_id:
        select("repository", "repository-fallback")

    selected_edges: set[str] = set()
    selected_flows: set[str] = set()
    skipped_reference_edges: set[str] = set()

    def edge_identifier(edge: dict[str, object], index: int) -> str:
        value = edge.get("id")
        return str(value) if isinstance(value, str) and value else f"edge-{index}"

    # Repeat until no node, edge, or flow is added. This is closure, not a fixed depth.
    expanded = True
    while expanded:
        expanded = False
        for index, edge in enumerate(edges):
            source = str(edge.get("source", ""))
            target = str(edge.get("target", ""))
            if source not in node_by_id or target not in node_by_id:
                continue
            if source not in selected and target not in selected:
                continue
            policy = str(edge.get("context") or edge.get("traversal") or "relevant").lower()
            if policy not in CONTEXT_POLICIES:
                policy = "relevant"
            edge_search = " ".join(str(edge.get(key, "")) for key in ("id", "label", "type", "description"))
            reference_matches = bool(task_tokens & context_terms(edge_search))
            eid = edge_identifier(edge, index)
            if policy == "reference" and not (deep or reference_matches):
                skipped_reference_edges.add(eid)
                continue
            if eid not in selected_edges:
                selected_edges.add(eid)
                expanded = True
            if select(source, f"edge:{eid}"):
                expanded = True
            if select(target, f"edge:{eid}"):
                expanded = True

        # A flow is indivisible context: selecting one step selects every step and declared edge.
        for flow in flows:
            flow_id = str(flow.get("id") or "unnamed-flow")
            steps = flow.get("steps", []) if isinstance(flow.get("steps"), list) else []
            step_nodes = {
                str(step.get("nodeId")) for step in steps
                if isinstance(step, dict) and isinstance(step.get("nodeId"), str)
            }
            flow_search = " ".join(str(flow.get(key, "")) for key in ("id", "name", "description"))
            task_match = bool(task_tokens & context_terms(flow_search))
            if selected & step_nodes or task_match:
                if flow_id not in selected_flows:
                    selected_flows.add(flow_id)
                    expanded = True
                for node_id in step_nodes:
                    if select(node_id, f"flow:{flow_id}"):
                        expanded = True
                declared_edges = flow.get("edgeIds", [])
                if isinstance(declared_edges, list):
                    for eid in declared_edges:
                        if isinstance(eid, str) and eid not in selected_edges:
                            selected_edges.add(eid)
                            expanded = True

    selected_node_data = [node_by_id[node_id] for node_id in sorted(selected)]
    selected_edge_data = [edge for index, edge in enumerate(edges) if edge_identifier(edge, index) in selected_edges]
    selected_flow_data = [flow for flow in flows if str(flow.get("id") or "unnamed-flow") in selected_flows]
    source_paths = sorted({path for node in selected_node_data for path in node_paths(node)})
    serialized = json.dumps({"nodes": selected_node_data, "edges": selected_edge_data, "flows": selected_flow_data})
    estimated_graph_tokens = max(1, len(serialized) // 4)

    return {
        "schema_version": 1,
        "generated_at": now_iso(),
        "strategy": "adaptive-graph-closure",
        "task": task or None,
        "deep": deep,
        "hard_token_cap": None,
        "estimated_graph_tokens": estimated_graph_tokens,
        "changed_paths": changed_paths,
        "seed_nodes": [
            {
                "id": node_id,
                "reasons": sorted(reason for reason in node_reasons if not reason.startswith("edge:") and not reason.startswith("flow:")),
            }
            for node_id, node_reasons in sorted(reasons.items())
            if any(not reason.startswith("edge:") and not reason.startswith("flow:") for reason in node_reasons)
        ],
        "nodes": selected_node_data,
        "edges": selected_edge_data,
        "flows": selected_flow_data,
        "source_paths": source_paths,
        "node_reasons": {node_id: sorted(node_reasons) for node_id, node_reasons in sorted(reasons.items())},
        "skipped_reference_edges": sorted(skipped_reference_edges - selected_edges),
        "stopping_condition": "no-new-material-relationships",
        "completeness_note": "Token estimates are telemetry only. Required context was not truncated by a numeric budget.",
    }

def start(args: argparse.Namespace) -> int:
    repo = resolve_repo_root()
    task = str(getattr(args, "task", "") or "")
    deep = bool(getattr(args, "deep", False))
    map_dir = repo / MAP_DIRNAME
    if not map_dir.exists():
        print("error: no .repo-map found; run `mesh.py repo .` first", file=sys.stderr)
        return 2

    state_path = map_dir / STATE_FILE
    state = load_json(state_path, {})
    assert isinstance(state, dict)
    git_info = git_state(repo)
    base = str(state.get("last_mapped_commit") or "")

    committed: list[dict[str, str]] = []
    if base and base not in ("unknown", str(git_info["commit"])):
        code, out, _ = run(["git", "-C", str(repo), "diff", "--name-status", f"{base}..HEAD"])
        if code == 0:
            committed = parse_name_status(out)

    working: list[dict[str, str]] = []
    for cmd in (
        ["git", "-C", str(repo), "diff", "--name-status"],
        ["git", "-C", str(repo), "diff", "--cached", "--name-status"],
    ):
        code, out, _ = run(cmd)
        if code == 0:
            working.extend(parse_name_status(out))
    untracked = git(repo, "ls-files", "--others", "--exclude-standard")
    if untracked != "unknown":
        working.extend({"status": "U", "path": p} for p in untracked.splitlines() if p and not p.startswith(f"{MAP_DIRNAME}/"))

    changes = committed + working
    dedup: dict[tuple[str, str], dict[str, str]] = {}
    for item in changes:
        path = item.get("path", "")
        if not path or path.startswith(f"{MAP_DIRNAME}/"):
            continue
        dedup[(item.get("status", "?"), path)] = item
    changes = list(dedup.values())

    impact: dict[str, list[str]] = {}
    for item in changes:
        for category in impacts_for(item["path"]):
            impact.setdefault(category, []).append(item["path"])

    mesh_path = state.get("mesh_path") or os.environ.get("REPO_MESH_PATH")
    mesh_status = "not configured"
    if mesh_path:
        mesh_status = "available" if Path(str(mesh_path)).expanduser().exists() else "unavailable; continuing local-only"

    architecture_data = load_json(map_dir / "generated" / "architecture.json", {})
    architecture_project = architecture_data.get("project") if isinstance(architecture_data, dict) and isinstance(architecture_data.get("project"), dict) else {}
    architecture_commit = str(architecture_project.get("source_commit") or "unknown")
    architecture_status = str(architecture_data.get("status") if isinstance(architecture_data, dict) else "missing")
    if architecture_commit not in ("unknown", str(git_info["commit"])):
        architecture_status += "; refresh recommended"

    change_set = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "repository": str(repo),
        "branch": git_info["branch"],
        "current_commit": git_info["commit"],
        "last_mapped_commit": base or "unknown",
        "dirty": git_info["dirty"],
        "changes": changes,
        "impact": impact,
        "mesh_status": mesh_status,
        "architecture_status": architecture_status,
        "architecture_source_commit": architecture_commit,
    }
    save_json(map_dir / "generated" / "change-set.json", change_set)

    context_plan = build_context_plan(architecture_data, changes, task=task, deep=deep)
    save_json(map_dir / "generated" / "context-plan.json", context_plan)

    lines = [
        "# Session Brief", "",
        f"Generated: {change_set['generated_at']}",
        f"Repository: `{repo.name}`",
        f"Branch: `{git_info['branch']}`",
        f"Current commit: `{git_info['short_commit']}`",
        f"Last mapped commit: `{str(base)[:12] if base else 'unknown'}`",
        f"Working tree dirty: `{git_info['dirty']}`",
        f"Mesh: {mesh_status}",
        f"Architecture graph: {architecture_status} (source `{architecture_commit[:12]}`)",
        f"Task: {task or '_not supplied_'}",
        f"Context strategy: adaptive graph closure{' including reference edges' if deep else ''}",
        f"Context graph: {len(context_plan['nodes'])} node(s), {len(context_plan['edges'])} edge(s), {len(context_plan['flows'])} flow(s)",
        f"Estimated graph tokens: ~{context_plan['estimated_graph_tokens']} (telemetry only; no hard cap)", "",
        "## Changes requiring selective review", "",
    ]
    if not changes:
        lines.append("_No source changes detected since the last mapped state._")
    else:
        for item in changes:
            lines.append(f"- `{item.get('status', '?')}` `{item['path']}` → {', '.join(impacts_for(item['path']))}")
    lines.extend([
        "", "## Adaptive context closure", "",
        "Read `.repo-map/generated/context-plan.json` and inspect every listed source path needed to verify the task.",
        "Traverse selected relationships upstream and downstream. Include complete selected flows.",
        "Do not omit required context to satisfy an arbitrary token ceiling; summarize stable records when useful, but preserve material facts and source references.",
        "", "## Agent next steps", "",
        "1. Read local instructions, `.repo-map/hot.md`, `.repo-map/index.md`, and `context-plan.json`.",
        "2. Inspect changed files plus every source path in the selected graph closure that affects correctness.",
        "3. Expand the closure when live source reveals an unrecorded caller, consumer, provider, hook, context/state dependency, auth boundary, schema, test, or deployment relationship.",
        "4. Refresh affected generated map sections and `.repo-map/generated/architecture.json` with provenance.",
        "5. Run `mesh.py visualize` after changing the architecture JSON.",
        "6. Retain missing prior records as unresolved rather than deleting them.",
    ])
    (map_dir / "generated" / "session-brief.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {map_dir / 'generated' / 'session-brief.md'}")
    print(f"Wrote {map_dir / 'generated' / 'context-plan.json'}")
    print(f"Detected {len(changes)} relevant change(s); selected {len(context_plan['nodes'])} context node(s); Mesh is {mesh_status}.")
    return 0


def export(args: argparse.Namespace) -> int:
    repo = resolve_repo_root()
    map_dir = repo / MAP_DIRNAME
    if not map_dir.exists():
        print("error: no .repo-map found", file=sys.stderr)
        return 2
    state_path = map_dir / STATE_FILE
    state = load_json(state_path, {})
    assert isinstance(state, dict)
    git_info = git_state(repo)

    def digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    pages: list[dict[str, str]] = []
    for path in sorted(map_dir.rglob("*.md")):
        rel = path.relative_to(repo).as_posix()
        if rel.startswith(f"{MAP_DIRNAME}/generated/"):
            continue
        pages.append({"path": rel, "sha256": digest(path)})

    architecture_json, architecture_html = write_architecture_outputs(repo)
    architecture_data = load_json(architecture_json, {})
    assert isinstance(architecture_data, dict)
    architecture_project = architecture_data.get("project") if isinstance(architecture_data.get("project"), dict) else {}

    payload = {
        "schema_version": 1,
        "project_id": slugify(repo.name),
        "project_name": repo.name,
        "source_commit": git_info["commit"],
        "source_branch": git_info["branch"],
        "generated_at": now_iso(),
        "visibility": "project",
        "contains_source_code": False,
        "contains_secrets": False,
        "map_pages": pages,
        "architecture": {
            "json_path": architecture_json.relative_to(repo).as_posix(),
            "html_path": architecture_html.relative_to(repo).as_posix(),
            "sha256": digest(architecture_json),
            "status": architecture_data.get("status", "unknown"),
            "source_commit": architecture_project.get("source_commit", "unknown"),
            "node_count": len(architecture_data.get("nodes", [])),
            "edge_count": len(architecture_data.get("edges", [])),
            "flow_count": len(architecture_data.get("flows", [])),
        },
        "relationships": {
            "provided_interfaces": [], "consumed_interfaces": [], "services": [],
            "data_models": [], "integrations": [], "dependencies": [], "decisions": []
        },
    }
    export_path = map_dir / "generated" / "export.json"
    save_json(export_path, payload)

    state["last_mapped_commit"] = git_info["commit"]
    state["last_mapped_at"] = now_iso()
    state["last_seen_branch"] = git_info["branch"]
    save_json(state_path, state)

    mesh_path = state.get("mesh_path") or os.environ.get("REPO_MESH_PATH")
    if mesh_path and Path(str(mesh_path)).expanduser().exists():
        resolved_mesh = Path(str(mesh_path)).expanduser().resolve()
        destination = resolved_mesh / "imports" / f"{payload['project_id']}.json"
        architecture_destination = resolved_mesh / "imports" / f"{payload['project_id']}.architecture.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(export_path, destination)
        shutil.copy2(architecture_json, architecture_destination)
        mesh_json, mesh_html = aggregate_mesh(resolved_mesh)
        print(f"Exported safe map metadata to {destination}")
        print(f"Exported architecture graph to {architecture_destination}")
        print(f"Rebuilt Mesh graph: {mesh_json} and {mesh_html}")
    else:
        print(f"Wrote local export {export_path}; no available Mesh was updated.")
    return 0


def visualize(args: argparse.Namespace) -> int:
    repo = resolve_repo_root()
    map_dir = repo / MAP_DIRNAME
    if not map_dir.exists():
        print("error: no .repo-map found; run `mesh.py repo .` first", file=sys.stderr)
        return 2
    try:
        json_path, html_path = write_architecture_outputs(repo, force_scaffold=bool(getattr(args, "reset", False)))
    except ValueError as exc:
        print(f"error: invalid architecture graph: {exc}", file=sys.stderr)
        return 2
    print(f"Architecture JSON: {json_path}")
    print(f"Interactive HTML: {html_path}")
    return 0


def aggregate_command(args: argparse.Namespace) -> int:
    mesh = Path(args.path or ".").expanduser().resolve()
    if not (mesh / "imports").exists() or not (mesh / "graph").exists():
        print(f"error: path does not look like a RepoMesh repository: {mesh}", file=sys.stderr)
        return 2
    json_path, html_path = aggregate_mesh(mesh)
    print(f"Mesh architecture JSON: {json_path}")
    print(f"Mesh interactive HTML: {html_path}")
    return 0



def lint(args: argparse.Namespace) -> int:
    repo = resolve_repo_root()
    map_dir = repo / MAP_DIRNAME
    errors: list[str] = []
    warnings: list[str] = []
    required = ["manifest.yaml", "index.md", "hot.md", "architecture.md", "interfaces.md", "dependencies.md", "ownership.md"]
    if not map_dir.exists():
        errors.append(".repo-map is missing")
    else:
        for item in required:
            if not (map_dir / item).exists():
                errors.append(f".repo-map/{item} is missing")
        for path in map_dir.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            starts = text.count("<!-- REPOMESH:GENERATED:START")
            ends = text.count("<!-- REPOMESH:GENERATED:END")
            if starts != ends:
                errors.append(f"{path.relative_to(repo)} has unbalanced generated markers")
            human_starts = text.count("<!-- REPOMESH:HUMAN:START")
            human_ends = text.count("<!-- REPOMESH:HUMAN:END")
            if human_starts != human_ends:
                errors.append(f"{path.relative_to(repo)} has unbalanced human markers")

        architecture_json = map_dir / "generated" / "architecture.json"
        architecture_html = map_dir / "generated" / "architecture.html"
        if not architecture_json.exists():
            errors.append(".repo-map/generated/architecture.json is missing")
        else:
            architecture_data = load_json(architecture_json, None)
            graph_errors, graph_warnings = validate_architecture_data(architecture_data)
            errors.extend(f"architecture: {item}" for item in graph_errors)
            warnings.extend(f"architecture: {item}" for item in graph_warnings)
        if not architecture_html.exists():
            errors.append(".repo-map/generated/architecture.html is missing")
        elif architecture_html.stat().st_size < 1000:
            warnings.append("architecture HTML appears unexpectedly small")

    for secret in SECRET_BASENAMES:
        if (repo / secret).exists():
            warnings.append(f"sensitive file `{secret}` exists; RepoMesh must never read or export its values")

    for item in errors:
        print(f"ERROR {item}")
    for item in warnings:
        print(f"WARN  {item}")
    print(f"Lint complete: {len(errors)} error(s), {len(warnings)} warning(s).")
    return 1 if errors else 0


def status(args: argparse.Namespace) -> int:
    repo = resolve_repo_root()
    map_dir = repo / MAP_DIRNAME
    if not map_dir.exists():
        print("Repo Map: missing")
        return 1
    state = load_json(map_dir / STATE_FILE, {})
    assert isinstance(state, dict)
    current = git_state(repo)
    recorded = str(state.get("last_mapped_commit") or "unknown")
    fresh = current["commit"] == recorded
    mesh_path = state.get("mesh_path") or os.environ.get("REPO_MESH_PATH")
    mesh_status = "not configured"
    if mesh_path:
        mesh_status = "available" if Path(str(mesh_path)).expanduser().exists() else "unavailable"
    print(f"Repo Map: present")
    print(f"Current commit: {current['short_commit']}")
    print(f"Mapped commit: {recorded[:12]}")
    architecture_data = load_json(map_dir / "generated" / "architecture.json", {})
    if isinstance(architecture_data, dict):
        graph_status = architecture_data.get("status", "unknown")
        graph_nodes = len(architecture_data.get("nodes", [])) if isinstance(architecture_data.get("nodes"), list) else 0
        graph_edges = len(architecture_data.get("edges", [])) if isinstance(architecture_data.get("edges"), list) else 0
        graph_flows = len(architecture_data.get("flows", [])) if isinstance(architecture_data.get("flows"), list) else 0
    else:
        graph_status, graph_nodes, graph_edges, graph_flows = "invalid", 0, 0, 0
    print(f"Freshness: {'current' if fresh else 'review required'}")
    print(f"Architecture: {graph_status} ({graph_nodes} nodes, {graph_edges} edges, {graph_flows} flows)")
    print(f"Mesh: {mesh_status}")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="mesh", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    cmd = sub.add_parser("repo", help="install or initialize a local Repo Map")
    cmd.add_argument("path", nargs="?", default=".")
    cmd.set_defaults(func=init_repo)

    cmd = sub.add_parser("mesh", help="create an optional Mesh repository")
    cmd.add_argument("path")
    cmd.set_defaults(func=init_mesh)

    cmd = sub.add_parser("connect", help="connect current Repo Map to a Mesh")
    cmd.add_argument("path")
    cmd.set_defaults(func=connect)

    cmd = sub.add_parser("start", help="create an incremental session brief and adaptive context plan")
    cmd.add_argument("--task", default="", help="describe the coding or investigation task used to seed graph traversal")
    cmd.add_argument("--deep", action="store_true", help="also traverse reference edges")
    cmd.set_defaults(func=start)

    cmd = sub.add_parser("context", help="build a task-specific bidirectional graph closure")
    cmd.add_argument("task", help="coding or investigation task")
    cmd.add_argument("--deep", action="store_true", help="also traverse reference edges")
    cmd.set_defaults(func=start)

    cmd = sub.add_parser("export", help="write a safe local export and optionally update Mesh")
    cmd.set_defaults(func=export)

    cmd = sub.add_parser("visualize", help="validate architecture.json and regenerate interactive architecture.html")
    cmd.add_argument("--reset", action="store_true", help="replace architecture JSON with a new scaffold")
    cmd.set_defaults(func=visualize)

    cmd = sub.add_parser("aggregate", help="rebuild the interactive cross-repository Mesh graph")
    cmd.add_argument("path", nargs="?", default=".")
    cmd.set_defaults(func=aggregate_command)

    cmd = sub.add_parser("lint", help="validate local Repo Map structure")
    cmd.set_defaults(func=lint)

    cmd = sub.add_parser("status", help="show local freshness and Mesh availability")
    cmd.set_defaults(func=status)
    return p


def main() -> int:
    args = parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
