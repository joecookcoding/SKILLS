# Release Notes

## 1.2.0 — Adaptive Context Closure

- Replaced fixed-budget guidance with task-rooted, bidirectional graph closure.
- Added `MESH >> CONTEXT <task>` and `MESH >> DEEP CONTEXT <task>`.
- Added deterministic `.repo-map/generated/context-plan.json`.
- Added task and changed-file seeds, upstream/downstream traversal, complete-flow inclusion, and optional reference-edge traversal.
- Added context-policy metadata to edges and concerns/tags to nodes.
- Added token estimates as telemetry with no hard correctness cutoff.
- Added RepoMesh philosophy and Joe's principle: tokens should fund discovery, not repeated rediscovery.

# RepoMesh 1.1.0

## Added

- Repository-local `architecture.json` for AI agents.
- Generated interactive `architecture.html` for developers.
- Searchable SVG architecture diagram with selectable nodes.
- Selectable flows with highlighted graph paths and ordered step details.
- Architecture graph validation for node, edge, and flow references.
- `MESH >> MAP`, `MESH >> VIEW`, and `MESH >> GRAPH` natural commands.
- `visualize` and `aggregate` CLI commands.
- Cross-repository graph aggregation with namespaced project IDs.
- Optional `graph/cross-repo.json` for shared contracts and cross-repo flows.
- `MAP.md` as a reusable complete mapping prompt.

## Preserved guarantees

- Local-only operation when the shared Mesh is missing.
- Non-destructive installation and updates.
- Protected human sections.
- Missing records become unresolved rather than disappearing.
- No automatic commit or push.
- No source code or secrets in Mesh exports.
