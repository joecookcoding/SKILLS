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
    write_if_missing(path / ".gitignore", "__pycache__/\n*.tmp\n.DS_Store\nThumbs.db\n")

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


def start(args: argparse.Namespace) -> int:
    repo = resolve_repo_root()
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
    }
    save_json(map_dir / "generated" / "change-set.json", change_set)

    lines = [
        "# Session Brief", "",
        f"Generated: {change_set['generated_at']}",
        f"Repository: `{repo.name}`",
        f"Branch: `{git_info['branch']}`",
        f"Current commit: `{git_info['short_commit']}`",
        f"Last mapped commit: `{str(base)[:12] if base else 'unknown'}`",
        f"Working tree dirty: `{git_info['dirty']}`",
        f"Mesh: {mesh_status}", "",
        "## Changes requiring selective review", "",
    ]
    if not changes:
        lines.append("_No source changes detected since the last mapped state._")
    else:
        for item in changes:
            lines.append(f"- `{item.get('status', '?')}` `{item['path']}` → {', '.join(impacts_for(item['path']))}")
    lines.extend(["", "## Agent next steps", "", "1. Read local instructions, `.repo-map/hot.md`, and `.repo-map/index.md`.", "2. Inspect only task-relevant and changed source files.", "3. Refresh affected generated map sections with provenance.", "4. Retain missing prior records as unresolved rather than deleting them."])
    (map_dir / "generated" / "session-brief.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {map_dir / 'generated' / 'session-brief.md'}")
    print(f"Detected {len(changes)} relevant change(s); Mesh is {mesh_status}.")
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
        destination = Path(str(mesh_path)).expanduser().resolve() / "imports" / f"{payload['project_id']}.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(export_path, destination)
        print(f"Exported safe map metadata to {destination}")
    else:
        print(f"Wrote local export {export_path}; no available Mesh was updated.")
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
    print(f"Freshness: {'current' if fresh else 'review required'}")
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

    cmd = sub.add_parser("start", help="create an incremental session brief")
    cmd.set_defaults(func=start)

    cmd = sub.add_parser("export", help="write a safe local export and optionally update Mesh")
    cmd.set_defaults(func=export)

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
