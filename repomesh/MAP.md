# RepoMesh Architecture Mapping Prompt

Use this when a repository already contains the RepoMesh skill:

```text
MESH >> MAP

Analyze this entire codebase using `.agents/skills/repomesh/SKILL.md`.

Update the repository-local `.repo-map/` non-destructively. Preserve human-owned sections, stable graph IDs, prior decisions, contradictions, and unresolved historical information.

Generate or update both complete architecture outputs:

1. `.repo-map/generated/architecture.json`
   - Valid JSON with `{nodes, edges, flows}`.
   - Nodes represent meaningful architectural components, modules, services, interfaces, storage, jobs, deployments, and external systems.
   - Edges represent verified relationships between nodes and should declare `context: required|relevant|reference` when useful.
   - Flows contain ordered `steps` that reference node IDs and explain important user, data, authentication, event, background-job, and deployment paths.
   - Include repository-relative source paths, concerns/tags such as auth, hooks, state, context, configuration, persistence, tests, and the observed Git commit.
   - Do not include source code, secrets, credentials, or private data.

2. `.repo-map/generated/architecture.html`
   - Generate it from the JSON with the RepoMesh CLI.
   - Use the built-in single-page dark-theme Tailwind CDN viewer.
   - It must support node search, selectable components, selectable flows, path highlighting, and ordered flow-step details.
   - Do not hand-edit the HTML.

Inspect live code and tests whenever implementation freshness matters. Mark missing prior components `unresolved` rather than deleting them solely because their source cannot currently be found.

After mapping, run:

python .agents/skills/repomesh/scripts/mesh.py visualize
python .agents/skills/repomesh/scripts/mesh.py lint

Report:
- files and subsystems inspected
- map pages created or updated
- node, edge, and flow counts
- contradictions or unresolved items
- likely cross-repository impacts
- exact output paths
```

## Context completeness requirement

The graph must support bidirectional impact traversal. Map callers and callees, providers and consumers, upstream and downstream data movement, hooks and state/context providers, authentication and authorization boundaries, schemas, persistence, configuration, tests, jobs, deployment, and cross-repository contracts wherever they materially affect a component or flow. Do not optimize node count at the expense of missing impact paths.
