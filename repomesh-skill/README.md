# RepoMesh

A generic, Git-backed knowledge system for software repositories.

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
          \                    /
           optional safe exports
                    ↓
              RepoMesh repo
        (its own Git history)
```

## First run

Give your coding agent [`INSTALL.md`](INSTALL.md), then use one of these commands:

```text
MESH >> REPO .
MESH >> CREATE ../repo-mesh
MESH >> CONNECT ../repo-mesh
MESH >> START
```

The corresponding shell CLI is:

```bash
python .agents/skills/repomesh/scripts/mesh.py repo .
python .agents/skills/repomesh/scripts/mesh.py mesh ../repo-mesh
python .agents/skills/repomesh/scripts/mesh.py connect ../repo-mesh
python .agents/skills/repomesh/scripts/mesh.py start
```

## Design guarantees

- Live code and reviewed repository documentation remain authoritative.
- Local Repo Maps work without the larger Mesh.
- Missing files and repositories are retained as unresolved records, not silently deleted.
- Human-owned sections are never replaced by generated updates.
- Cross-repository exports omit source code, secrets, credentials, and private datasets.
- Every generated claim should retain file and Git-commit provenance.
- Session startup is incremental: inspect changes since the last mapped commit instead of rereading everything.

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
│   ├── export.json
│   ├── change-set.json
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
├── graph/
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
