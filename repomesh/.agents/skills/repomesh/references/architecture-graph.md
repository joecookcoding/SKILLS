# Architecture Graph Contract

The machine-readable graph is `.repo-map/generated/architecture.json`. The interactive human view is generated from it at `.repo-map/generated/architecture.html`.

## Required root shape

```json
{
  "schema_version": 1,
  "status": "verified-current",
  "project": {
    "id": "project-id",
    "name": "Project Name",
    "source_commit": "full-git-commit",
    "generated_at": "ISO-8601 timestamp"
  },
  "nodes": [],
  "edges": [],
  "flows": []
}
```

## Node

```json
{
  "id": "auth-service",
  "label": "Authentication Service",
  "type": "service",
  "group": "Backend",
  "description": "Creates and validates application sessions.",
  "path": "src/auth/session.ts",
  "status": "verified-current",
  "source_commit": "full-git-commit",
  "concerns": ["auth", "session", "configuration"],
  "tags": ["security-boundary"]
}
```

Use stable, semantic IDs. Do not use line numbers, hashes, or temporary filenames as IDs.

## Edge

```json
{
  "id": "login-page-calls-auth-api",
  "source": "login-page",
  "target": "auth-api",
  "label": "POST /api/login",
  "type": "calls",
  "status": "verified-current",
  "context": "required"
}
```

Every source and target must refer to an existing node.

## Flow

```json
{
  "id": "user-login",
  "name": "User login",
  "description": "From credential submission through session creation.",
  "steps": [
    {
      "order": 1,
      "nodeId": "login-page",
      "label": "Submit credentials",
      "detail": "The form validates input and calls the login API.",
      "path": "src/app/login/page.tsx"
    }
  ],
  "edgeIds": ["login-page-calls-auth-api"]
}
```

Flows should cover important user journeys, data paths, authentication, events, background jobs, deployments, or operational sequences. Do not invent a flow solely to connect unrelated nodes.

## Mapping level

Prefer meaningful architecture components:

- entry points and user surfaces
- modules and bounded contexts
- APIs and services
- workers, queues, scheduled tasks, and events
- databases and external systems
- deployment and observability components
- shared packages and cross-repository contracts

Do not create one node for every source file unless the repository is very small and each file is architecturally meaningful.

## Provenance and staleness

- `project.source_commit` identifies the commit the graph was verified against.
- Nodes may additionally carry their own `source_commit`, `sources`, or `last_verified`.
- Preserve stable IDs through refactors when the conceptual component survives.
- A missing prior component becomes `unresolved` before deletion.
- The generated HTML is never edited directly.

## Adaptive context semantics

RepoMesh context is built by graph closure, not by a fixed token budget.

- `required`: always traverse when either endpoint enters task context.
- `relevant`: traverse during normal closure unless evidence makes it immaterial.
- `reference`: traverse on task match, selected-flow inclusion, or deep-context request.

Traversal is bidirectional. Selecting a node considers callers and callees, providers and consumers, and upstream and downstream data paths. Selecting any step of a flow selects the complete flow. Use `concerns` and `tags` for hooks, context/state, auth, authorization, schemas, configuration, persistence, queues, tests, deployment, and observability.

Token estimates are telemetry only and may not truncate required context.
