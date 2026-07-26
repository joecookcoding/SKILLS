# Ingestion Protocol

## Initial map

1. Record Git state.
2. Read local agent instructions.
3. Inspect manifests, architecture docs, CI, deployment, schemas, routes, tests, and ownership files.
4. Build deterministic structure.
5. Produce semantic pages with provenance.
6. Create a safe Mesh export.

## Incremental map

1. Read the last mapped commit.
2. Calculate committed and working-tree changes.
3. Classify likely knowledge impact.
4. Refresh only affected generated pages.
5. Retain disappeared items as unresolved.
6. Rebuild indexes and export.
