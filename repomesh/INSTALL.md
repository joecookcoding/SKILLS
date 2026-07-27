# RepoMesh First-Run Installer

Give this file to a coding agent the first time RepoMesh is used in a repository.

## Natural commands

### `MESH >> REPO [PATH]`

Install or refresh RepoMesh inside an existing source repository. `PATH` defaults to the current directory.

The agent must:

1. Locate the RepoMesh skill bundled with this installer.
2. Copy `.agents/skills/repomesh/` into the target repository if it is missing.
3. Run:

   ```bash
   python .agents/skills/repomesh/scripts/mesh.py repo PATH
   ```

4. Perform the complete `MESH >> MAP` procedure below.
5. Preserve existing human notes, stable IDs, and unresolved historical records.
6. Commit nothing unless explicitly requested.

Example:

```text
MESH >> REPO .
```

### `MESH >> MAP`

Analyze the current codebase and compile its complete local Repo Map.

The agent must:

1. Read the repository instructions and RepoMesh `SKILL.md`.
2. Inspect Git state, manifests, source layout, routes, schemas, tests, CI, deployment files, existing docs, and ownership files.
3. Update the Markdown map under `.repo-map/` using source and Git-commit provenance.
4. Generate a complete `.repo-map/generated/architecture.json` containing:
   - `nodes`
   - `edges`
   - `flows`, each with ordered `steps`
5. Model meaningful components and application flows rather than listing every file.
6. Include repository-relative paths on nodes and flow steps whenever evidence exists.
7. Preserve stable node IDs and mark missing prior components `unresolved` instead of silently deleting them.
8. Set the graph's `project.source_commit`, `project.generated_at`, and `status`.
9. Run:

   ```bash
   python .agents/skills/repomesh/scripts/mesh.py visualize
   python .agents/skills/repomesh/scripts/mesh.py lint
   ```

The resulting files are:

- `.repo-map/generated/architecture.html` — interactive human view using Tailwind CDN and a dark theme.
- `.repo-map/generated/architecture.json` — machine-readable graph for the next coding agent.

The HTML must support searching, selecting components, selecting a flow, highlighting its path, and showing ordered flow steps. The HTML is generated from the JSON and must not be edited directly.

### `MESH >> VIEW`

Validate the architecture JSON and regenerate the interactive HTML without remapping the repository:

```bash
python .agents/skills/repomesh/scripts/mesh.py visualize
```

### `MESH >> CREATE [PATH]`

Create a new optional Mesh repository with its own Git history.

The agent must run:

```bash
python .agents/skills/repomesh/scripts/mesh.py mesh PATH
```

The command initializes Git only when `PATH` is not already inside a Git work tree. It also creates an empty cross-repository architecture JSON and HTML.

Example:

```text
MESH >> CREATE ../repo-mesh
```

### `MESH >> CONNECT [PATH]`

Connect the current repository's local Repo Map to an existing Mesh repository.

The agent must run from the source repository:

```bash
python .agents/skills/repomesh/scripts/mesh.py connect PATH
```

Connection is optional. If `PATH` is missing or unavailable, local operation continues normally.

Example:

```text
MESH >> CONNECT ../repo-mesh
```

### `MESH >> GRAPH [PATH]`

Rebuild the larger Mesh's combined JSON and interactive HTML from available repository architecture imports:

```bash
python .agents/skills/repomesh/scripts/mesh.py aggregate PATH
```

Optional cross-repository nodes, edges, and flows may be maintained in `graph/cross-repo.json`. Imported repository node IDs are namespaced so unrelated repos cannot collide.

### `MESH >> START`

Begin a coding session with incremental context ingestion.

The agent must:

1. Run `python .agents/skills/repomesh/scripts/mesh.py start`.
2. Read `.repo-map/generated/session-brief.md`.
3. Read `AGENTS.md`, relevant nested instructions, `.repo-map/hot.md`, and `.repo-map/index.md`.
4. Read `.repo-map/generated/architecture.json` when the task touches architecture, interfaces, or flows.
5. Inspect only changed or task-relevant files.
6. Load directly connected Mesh context when available.
7. Clearly label stale, unresolved, inaccessible, or inferred information.

### `MESH >> END`

Close a session and update durable project context.

The agent must:

1. Summarize verified changes, tests, decisions, contract impacts, and unfinished work.
2. Update affected Markdown map pages and architecture JSON.
3. Update only generated blocks or newly created generated pages.
4. Never overwrite protected human sections.
5. Run:

   ```bash
   python .agents/skills/repomesh/scripts/mesh.py visualize
   python .agents/skills/repomesh/scripts/mesh.py export
   python .agents/skills/repomesh/scripts/mesh.py lint
   ```

6. Update the connected Mesh only when permitted and available.

## Required safety behavior

- Never read or export secret values.
- Never place full source code in the architecture graph.
- Never delete local knowledge merely because a source disappeared.
- Mark missing evidence `unresolved` and retain its last verified commit.
- Never make Mesh availability a requirement for building, testing, or developing the source repository.
- Never automatically commit or push.

## Adaptive context rule

Never impose a low fixed token cap on RepoMesh retrieval. Start from the task and changed files, traverse upstream and downstream through required and relevant edges, include complete flows, and stop when no new material relationship appears. Token estimates may trigger a warning or summary layer, but may not remove context required for correctness.
