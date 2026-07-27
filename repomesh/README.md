# RepoMesh

**Version 1.2.0 — Adaptive Context Closure**

A generic, Git-backed knowledge and architecture-mapping system for software repositories.

RepoMesh has two independent layers:

1. **Repo Map** — baked into each source repository under `.repo-map/`.
2. **Mesh repository** — an optional, separate Git repository that connects approved exports from multiple Repo Maps.

A repository remains fully useful when the Mesh is absent, inaccessible, private, moved, or stale.

```text
source repo A                source repo B
├── code                     ├── code
├── AGENTS.md                ├── AGENTS.md
├── .agents/skills/repomesh  ├── .agents/skills/repomesh
└── .repo-map/               └── .repo-map/
    ├── knowledge                ├── knowledge
    ├── architecture.json        ├── architecture.json
    └── architecture.html        └── architecture.html
          \                    /
           optional safe exports
                    ↓
              RepoMesh repo
        (its own Git history and
         combined JSON + HTML graph)
```

## Core principle

> If your application depends on agents repeatedly burning tokens to rediscover the same solution through nondeterministic reasoning, you are being fleeced by the AI companies.
>
> Agents should handle uncertainty, exploration, and exceptions. Once a behavior becomes understood and repeatable, capture it in deterministic code, APIs/CLIs, tools, or workflows.
>
> The goal is not to eliminate agents. It is to stop paying for the same cognition over and over again.
>
> Tokens should fund discovery, not rent-seeking on already-solved problems.
>
> — Joe

RepoMesh turns discovered architecture into deterministic, Git-versioned project memory. The graph does not impose a hard context limit. It computes a task-specific dependency closure and uses token estimates only to expose cost.

## First run

Give your coding agent [`INSTALL.md`](INSTALL.md), then say:

```text
MESH >> REPO .
```

Additional natural commands:

```text
MESH >> MAP
MESH >> VIEW
MESH >> CONTEXT <task>
MESH >> DEEP CONTEXT <task>
MESH >> CREATE ../repo-mesh
MESH >> CONNECT ../repo-mesh
MESH >> GRAPH ../repo-mesh
MESH >> START
MESH >> END
```

The reusable complete mapping prompt is in [`MAP.md`](MAP.md).

The corresponding shell CLI is:

```bash
python .agents/skills/repomesh/scripts/mesh.py repo .
python .agents/skills/repomesh/scripts/mesh.py visualize
python .agents/skills/repomesh/scripts/mesh.py mesh ../repo-mesh
python .agents/skills/repomesh/scripts/mesh.py connect ../repo-mesh
python .agents/skills/repomesh/scripts/mesh.py aggregate ../repo-mesh
python .agents/skills/repomesh/scripts/mesh.py start --task "describe the task"
python .agents/skills/repomesh/scripts/mesh.py context "describe the task"
python .agents/skills/repomesh/scripts/mesh.py context "describe the task" --deep
python .agents/skills/repomesh/scripts/mesh.py export
```

## Self-explaining architecture

Every mapped repo produces two synchronized files:

- **`architecture.html` for people:** one dark-theme interactive page with searchable components, selectable nodes, selectable flows, highlighted paths, and ordered flow steps.
- **`architecture.json` for agents:** a stable `{nodes, edges, flows}` contract with source paths and Git provenance.

The JSON is the source of truth. The HTML is regenerated deterministically with `mesh.py visualize`.

## Design guarantees

- Live code and reviewed repository documentation remain authoritative.
- Local Repo Maps work without the larger Mesh.
- Missing files and repositories are retained as unresolved records, not silently deleted.
- Human-owned sections are never replaced by generated updates.
- Cross-repository exports omit source code, secrets, credentials, and private datasets.
- Every generated claim should retain file and Git-commit provenance.
- Session startup is incremental: inspect changes since the last mapped commit instead of rereading everything.
- Context retrieval is adaptive: traverse required and relevant relationships in both directions until closure.
- No hard token ceiling may truncate materially required context; estimates are warnings and telemetry only.
- Stable graph IDs are preserved when components continue to exist.
- The HTML is never an independent editable knowledge source.

## Repository-local layout

```text
.repo-map/
├── manifest.yaml
├── index.md
├── hot.md
├── architecture.md
├── interfaces.md
├── dependencies.md
├── ownership.md
├── decisions/
├── modules/
├── workflows/
├── generated/
│   ├── architecture.json
│   ├── architecture.html
│   ├── export.json
│   ├── change-set.json
│   ├── context-plan.json
│   └── session-brief.md
└── state/
    ├── sync-state.json
    └── file-hashes.json
```

## Mesh layout

```text
repo-mesh/
├── AGENTS.md
├── registry/
├── imports/
│   ├── project-a.json
│   ├── project-a.architecture.json
│   └── project-b.architecture.json
├── graph/
│   ├── architecture.json
│   ├── architecture.html
│   ├── cross-repo.json
│   ├── projects/
│   ├── services/
│   ├── interfaces/
│   ├── data-models/
│   └── integrations/
├── contracts/
├── decisions/
├── patterns/
├── conflicts/
├── audits/
└── state/
```

## Portable skill

The complete skill is in `.agents/skills/repomesh/`. Copy that directory into any repository, or retain this package as the source template.

## Testing

```bash
python -m unittest discover -s tests -v
```

## License

MIT.
