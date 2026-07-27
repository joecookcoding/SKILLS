---
name: repomesh
description: Build and maintain a non-destructive repository-local knowledge map, optionally connect it to a separate cross-repository Mesh, and begin coding sessions with incremental source-grounded context. Use for mapping existing repos, preserving architecture and decisions, coordinating frontend/backend contracts, session start/end ingestion, cross-repo queries, and freshness checks.
license: MIT
metadata:
  version: 1.2.0
  category: engineering-knowledge
---

# RepoMesh

RepoMesh has two layers:

- **Repo Map:** `.repo-map/` inside the current repository. This is mandatory and self-sufficient.
- **Mesh:** an optional separate Git repository that imports safe summaries and relationships from multiple Repo Maps.

## Joe's principle

> If your application depends on agents repeatedly burning tokens to rediscover the same solution through nondeterministic reasoning, you are being fleeced by the AI companies.
>
> Agents should handle uncertainty, exploration, and exceptions. Once a behavior becomes understood and repeatable, capture it in deterministic code, APIs/CLIs, tools, or workflows.
>
> The goal is not to eliminate agents. It is to stop paying for the same cognition over and over again.
>
> Tokens should fund discovery, not rent-seeking on already-solved problems.
>
> — Joe

RepoMesh spends model reasoning on discovery and ambiguity, then compiles stable findings into versioned graphs, commands, contracts, and workflows that future sessions retrieve deterministically.

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
MESH >> MAP
MESH >> VIEW
MESH >> START
MESH >> END
```

## Read order at session start

1. Root and relevant nested `AGENTS.md` or equivalent instructions
2. `.repo-map/manifest.yaml`
3. `.repo-map/generated/session-brief.md`
4. `.repo-map/generated/context-plan.json`
5. `.repo-map/hot.md`
6. `.repo-map/index.md`
7. Task-relevant graph nodes, edges, and complete connected flows
8. Directly connected Mesh records, when available
9. Every live source file required to verify the selected dependency closure

Do not load every map page or repository file blindly. Do not stop at an arbitrary token ceiling either. Build the smallest **complete** context for the task by traversing material graph relationships in both directions until the dependency frontier closes.

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
8. Generate `.repo-map/generated/architecture.json` as the machine-readable architecture contract.
9. Run `mesh.py visualize` to regenerate `.repo-map/generated/architecture.html`.
10. Export approved metadata for the optional Mesh.

## Architecture graph outputs

Each mapped repository must maintain two synchronized outputs:

- `.repo-map/generated/architecture.json` — authoritative machine-readable graph for agents.
- `.repo-map/generated/architecture.html` — interactive dark-theme human viewer generated from the JSON.

The JSON must contain:

```json
{
  "nodes": [],
  "edges": [],
  "flows": [
    { "id": "flow-id", "name": "Flow name", "steps": [] }
  ]
}
```

Nodes represent meaningful architectural components, not every file. Edges represent verified relationships. Flows describe ordered user, data, authentication, deployment, or background-processing paths. Each node and flow step should include repository-relative source paths when available.

When updating architecture:

1. Analyze live source and current map pages.
2. Preserve stable node IDs whenever the component still exists.
3. Mark missing components unresolved before removing them.
4. Update `project.source_commit`, `project.generated_at`, and `status`.
5. Validate and render with:

```bash
python .agents/skills/repomesh/scripts/mesh.py visualize
```

The HTML must not become an independent source of truth; never hand-edit it.

## Session start and adaptive context

Run:

```bash
python .agents/skills/repomesh/scripts/mesh.py start --task "describe the current task"
```

Or use:

```text
MESH >> CONTEXT <task>
```

RepoMesh generates both `change-set.json` and `context-plan.json`. The plan is task-rooted but **not token-capped**:

1. Seed context from the task, changed files, named flows, and explicit targets.
2. Traverse graph edges upstream and downstream.
3. Pull complete flows and materially connected hooks, context/state, auth, schemas, configuration, callers, consumers, providers, persistence, queues, deployment, and tests.
4. Continue until no new required or relevant relationship is discovered.
5. Treat estimated token size as telemetry. Never omit a required component solely to satisfy a numeric budget.
6. Inspect live source for every implementation claim that affects the edit.
7. Continue locally when the Mesh is unavailable and label cross-repo context incomplete.

Edges may be `required`, `relevant`, or `reference`. Required and relevant edges participate in normal closure. Reference edges are followed on semantic match, flow inclusion, or a deep-context request.

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
python .agents/skills/repomesh/scripts/mesh.py visualize
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

Each imported record must retain its source project, source commit, generated date, and visibility. Local architecture JSON files are copied into Mesh imports, namespaced by project, and compiled into `graph/architecture.json` plus `graph/architecture.html`. Optional cross-repository edges and flows live in `graph/cross-repo.json`.

## Query protocol

For a question or coding task:

1. Build the smallest **complete** context, not the smallest numerical context.
2. Seed from the task, current changes, and relevant flows.
3. Traverse material relationships in both directions until closure.
4. Inspect live source whenever freshness or implementation detail matters.
5. Read connected Mesh records for every materially affected cross-repository contract, including deeper traversal when required.
6. Label claims as `verified-current`, `compiled-local`, `compiled-mesh`, `inference`, or `unknown`.
7. Cite repository-relative paths and commits.

## Never do these

- Never require the Mesh for local development.
- Never silently delete missing or superseded information.
- Never claim generated context is current when its source commit differs.
- Never export secrets, credentials, private data, or full source files.
- Never overwrite human-owned content.
- Never automatically commit or push.
