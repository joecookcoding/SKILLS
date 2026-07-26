---
name: repomesh
description: Build and maintain a non-destructive repository-local knowledge map, optionally connect it to a separate cross-repository Mesh, and begin coding sessions with incremental source-grounded context. Use for mapping existing repos, preserving architecture and decisions, coordinating frontend/backend contracts, session start/end ingestion, cross-repo queries, and freshness checks.
license: MIT
metadata:
  version: 1.0.0
  category: engineering-knowledge
---

# RepoMesh

RepoMesh has two layers:

- **Repo Map:** `.repo-map/` inside the current repository. This is mandatory and self-sufficient.
- **Mesh:** an optional separate Git repository that imports safe summaries and relationships from multiple Repo Maps.

## Authority order

1. Current live code and tests
2. Reviewed repository-local documentation and explicit human decisions
3. Generated local Repo Map with matching provenance
4. Connected Mesh records
5. Conversation or model inference

Never let a lower layer silently override a higher layer.

## First-run commands

Interpret the natural commands in the package `INSTALL.md`:

```text
MESH >> REPO .
MESH >> CREATE ../repo-mesh
MESH >> CONNECT ../repo-mesh
MESH >> START
MESH >> END
```

## Read order at session start

1. Root and relevant nested `AGENTS.md` or equivalent instructions
2. `.repo-map/manifest.yaml`
3. `.repo-map/generated/session-brief.md`
4. `.repo-map/hot.md`
5. `.repo-map/index.md`
6. Task-relevant local pages
7. Directly connected Mesh records, when available
8. Changed or task-relevant live source files

Do not load every map page or every repository file by default.

## Mapping an existing repository

1. Run the `repo` CLI command to create missing structure without replacing existing content.
2. Inspect Git metadata and high-signal files first:
   - repository instructions
   - README and architecture docs
   - package/build manifests
   - CI workflows
   - compose, deployment, and infrastructure files
   - schemas, migrations, routes, interfaces, and tests
3. Extract deterministic structure before semantic summaries.
4. Create or update local pages with file and commit provenance.
5. Use one concept, module, workflow, contract, or decision per page.
6. Update generated blocks only.
7. Mark missing prior sources unresolved rather than deleting their records.
8. Export approved metadata for the optional Mesh.

## Session start

Run:

```bash
python .agents/skills/repomesh/scripts/mesh.py start
```

Then use the generated change set to perform selective ingestion:

1. Compare current `HEAD`, branch, and working tree to the last mapped commit.
2. Classify added, modified, deleted, renamed, and untracked files.
3. Determine which architecture, module, interface, dependency, workflow, and decision pages may be affected.
4. Verify only those pages and files relevant to the current task.
5. If the connected Mesh is unavailable, state that cross-repo context may be incomplete and continue locally.

## Session end

Capture only durable, source-grounded outcomes:

- changed architecture or ownership boundaries
- tests and build results
- new or changed interfaces
- decisions and rationale
- discovered constraints or gotchas
- unfinished work and cross-repo impact

Do not promote speculative conversation statements into established architecture.

Run:

```bash
python .agents/skills/repomesh/scripts/mesh.py export
python .agents/skills/repomesh/scripts/mesh.py lint
```

## Non-destructive editing

Files or sections have one of three ownership classes:

- `human`: read-only to the generator
- `generated`: may be regenerated from evidence
- `hybrid`: only generated marker blocks may be replaced

Protected markers:

```markdown
<!-- REPOMESH:GENERATED:START section-name -->
Generated content
<!-- REPOMESH:GENERATED:END section-name -->

<!-- REPOMESH:HUMAN:START -->
Human-maintained content
<!-- REPOMESH:HUMAN:END -->
```

Never replace content outside an explicitly generated block in a hybrid file.

## Missing data

When a file, repository, interface, or source disappears:

- retain the existing knowledge
- change its status to `unresolved`
- preserve the last verified path and commit
- record the reason and first observed missing date
- request human review before deletion

A missing Mesh is not an error. A missing peer repository is represented as an inaccessible or opaque node.

## Cross-repository Mesh

Export only normalized summaries and references. Do not export source code or secret values.

The Mesh may connect:

- projects and ownership
- provided and consumed APIs
- schemas and data models
- events and queues
- services and deployments
- shared packages
- decisions and reusable patterns

Each imported record must retain its source project, source commit, generated date, and visibility.

## Query protocol

For a question:

1. Read the smallest sufficient local context.
2. Inspect live source whenever freshness or implementation detail matters.
3. Read Mesh records only for relevant direct relationships.
4. Label claims as `verified-current`, `compiled-local`, `compiled-mesh`, `inference`, or `unknown`.
5. Cite repository-relative paths and commits.

## Never do these

- Never require the Mesh for local development.
- Never silently delete missing or superseded information.
- Never claim generated context is current when its source commit differs.
- Never export secrets, credentials, private data, or full source files.
- Never overwrite human-owned content.
- Never automatically commit or push.
