# MESH Command Card

Point a coding agent to `INSTALL.md`, then issue:

```text
MESH >> REPO .
```

This installs the generic skill, creates the non-destructive `.repo-map/`, maps the existing repository, and generates:

```text
.repo-map/generated/architecture.html
.repo-map/generated/architecture.json
```

For the complete mapping instructions, point the agent to `MAP.md`.

Refresh the complete local map:

```text
MESH >> MAP
```

Regenerate the HTML from the JSON:

```text
MESH >> VIEW
```

Create and connect the optional shared Mesh repository:

```text
MESH >> CREATE ../repo-mesh
MESH >> CONNECT ../repo-mesh
```

Rebuild the combined cross-repository graph:

```text
MESH >> GRAPH ../repo-mesh
```

Begin and finish sessions:

```text
MESH >> START
MESH >> END
```

The local Repo Map and visual architecture remain usable when the shared Mesh is absent or inaccessible.

## Task context

```text
MESH >> CONTEXT Add profile authentication fallback
MESH >> DEEP CONTEXT Trace profile authentication across every connected repo
```

`CONTEXT` builds an adaptive, bidirectional graph closure. `DEEP CONTEXT` also follows reference edges and opaque boundaries as far as available evidence allows. Neither command uses a hard token cutoff.
