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

4. Inspect the repository according to `SKILL.md`.
5. Build the initial `.repo-map/` using direct repository evidence.
6. Preserve existing human notes and unknown historical records.
7. Commit nothing unless explicitly requested.

Example:

```text
MESH >> REPO .
```

### `MESH >> CREATE [PATH]`

Create a new optional Mesh repository with its own Git history.

The agent must run:

```bash
python .agents/skills/repomesh/scripts/mesh.py mesh PATH
```

The command initializes Git only when `PATH` is not already inside a Git work tree.

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

### `MESH >> START`

Begin a coding session with incremental context ingestion.

The agent must:

1. Run `python .agents/skills/repomesh/scripts/mesh.py start`.
2. Read `.repo-map/generated/session-brief.md`.
3. Read `AGENTS.md`, relevant nested instructions, `.repo-map/hot.md`, and `.repo-map/index.md`.
4. Inspect only changed or task-relevant files.
5. Load directly connected Mesh context when available.
6. Clearly label stale, unresolved, inaccessible, or inferred information.

### `MESH >> END`

Close a session and update durable project context.

The agent must:

1. Summarize verified changes, tests, decisions, contract impacts, and unfinished work.
2. Update only generated blocks or newly created generated pages.
3. Never overwrite protected human sections.
4. Run:

   ```bash
   python .agents/skills/repomesh/scripts/mesh.py export
   python .agents/skills/repomesh/scripts/mesh.py lint
   ```

5. Update the connected Mesh only when permitted and available.

## Required safety behavior

- Never read or export secret values.
- Never delete local knowledge merely because a source disappeared.
- Mark missing evidence `unresolved` and retain its last verified commit.
- Never make Mesh availability a requirement for building, testing, or developing the source repository.
- Never automatically commit or push.
